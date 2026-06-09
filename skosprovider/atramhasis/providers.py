"""
This module implements a :class:`skosprovider.providers.VocabularyProvider`
for Atramhasis.
"""

import logging

import requests
from dogpile.cache import make_region
from requests.exceptions import ConnectionError
from requests.exceptions import Timeout

from skosprovider.atramhasis.cache_utils import _cache_on_arguments
from skosprovider.atramhasis.utils import dict_to_thing
from skosprovider.exceptions import ProviderUnavailableException
from skosprovider.providers import VocabularyProvider
from skosprovider.skos import ConceptScheme
from skosprovider.skos import Label
from skosprovider.skos import Note
from skosprovider.skos import dict_to_source

log = logging.getLogger(__name__)


class AtramhasisProvider(VocabularyProvider):
    """A provider that can work with the Atramhasis REST services"""

    base_url = None
    """Base URL of an Atramhasis instance."""

    scheme_id = None
    """Identifier of the ConceptScheme this provider is managing."""

    session = None
    """
    The :class:`requests.Session` being used to make HTTP requests.
    """

    timeout = 10
    """Timeout in seconds for HTTP requests. Can be a float or a (connect, read) tuple."""

    # noinspection PyMissingConstructor
    # intentionally does not call super.
    def __init__(self, metadata, **kwargs):
        """Create a new AtramhasisProvider

        :param (dict) metadata: metadata of the provider
        :param kwargs: arguments defining the provider.
            * `base_url` and `scheme_id` are required.
            * `session` is optional and can be used to pass a custom
                :class:`requests.Session`, eg. to configure caching strategies.
            * `cache_config` is an optional dict. Only keys starting with
                "cache." are relevant.
            * `timeout` is optional. Timeout in seconds for HTTP requests.
                Can be a float or a (connect, read) tuple. Defaults to 10.
        """
        if "subject" not in metadata:
            metadata["subject"] = []
        if "uri" not in metadata:
            log.warning(
                "AtramhasisProvider: 'uri' is not present in the metadata. "
                "This will result in a http call to fetch the conceptscheme "
                "and extract the uri."
            )
        self.metadata = metadata
        self._conceptscheme = None
        self.allowed_instance_scopes = kwargs.get(
            "allowed_instance_scopes", ["single", "threaded_thread"]
        )
        if "base_url" in kwargs:
            self.base_url = kwargs["base_url"]
        else:
            raise ValueError("Please provide a base_url for the provider")
        if "scheme_id" in kwargs:
            self.scheme_id = kwargs["scheme_id"]
        else:
            raise ValueError("Please provide a scheme_id for the provider")

        if "session" in kwargs:
            self.session = kwargs["session"]
        else:
            self.session = requests.Session()

        self.timeout = kwargs.get("timeout", 10)

        self.caches = {"cache": make_region()}
        if not self.caches["cache"].is_configured:
            self.caches["cache"].configure_from_config(
                kwargs.get("cache_config", {"cache.backend": "dogpile.cache.null"}),
                prefix="cache.",
            )

    @property
    def concept_scheme(self):
        if self._conceptscheme is None:
            self._conceptscheme = self._get_concept_scheme()
        return self._conceptscheme

    def _get_concept_scheme(self):
        request = f"{self.base_url}/conceptschemes/{self.scheme_id}"
        response = self._request(request, {"Accept": "application/json"})
        if response.status_code == 404:
            raise ProviderUnavailableException(
                "Conceptscheme %s not found. Check your configuration." % request
            )
        cs = response.json()
        return ConceptScheme(
            cs["uri"],
            labels=[
                Label(
                    label.get("label", "<no label>"),
                    label.get("type", "prefLabel"),
                    label.get("language", "und"),
                )
                for label in cs["labels"]
            ],
            notes=[
                Note(
                    note.get("note", "<no note>"),
                    note.get("type", "note"),
                    note.get("language", "und"),
                    note.get("markup"),
                )
                for note in cs["notes"]
            ],
            sources=[dict_to_source(s) for s in cs["sources"]],
            languages=cs["languages"],
        )

    @_cache_on_arguments(cache_name="cache")
    def get_by_id(self, id_):
        request = f"{self.base_url}/conceptschemes/{self.scheme_id}/c/{id_}"
        response = self._request(request, {"Accept": "application/json"})
        if response.status_code == 404:
            return False
        answer = dict_to_thing(response.json())
        return answer

    @_cache_on_arguments(cache_name="cache")
    def get_by_uri(self, uri):
        request = f"{self.base_url}/uris"
        params = {"uri": uri}
        response = self._request(request, {"Accept": "application/json"}, params)
        if response.status_code == 404:
            return False
        if response.json()["concept_scheme"]["id"] != self.scheme_id:
            return False
        return self.get_by_id(response.json()["id"])

    @_cache_on_arguments(cache_name="cache")
    def find(self, query, **kwargs):
        params = {"language": self._get_language(**kwargs)}
        params.update(self._get_sort_params(**kwargs))

        if "label" in query:
            params["label"] = query["label"]

        if "type" in query and query["type"] in ["concept", "collection"]:
            params["type"] = query["type"]

        if "collection" in query:
            collection = query["collection"]
            if "id" not in collection:
                raise ValueError(
                    "collection: 'id' is required key if a collection-dictionary is given"
                )
            params["collection"] = collection["id"]
            if "depth" in collection and collection["depth"] != "all":
                raise ValueError(
                    "collection - 'depth': only 'all' is supported by Atramhasis"
                )

        if "matches" in query:
            match_uri = query["matches"].get("uri", None)
            if not match_uri:
                raise ValueError("Please provide a URI to match with.")
            else:
                params["match"] = match_uri
            match_type = query["matches"].get("type", None)
            if match_type:
                params["match_type"] = match_type

        search_url = f"{self.base_url}/conceptschemes/{self.scheme_id}/c/"
        response = self._request(search_url, {"Accept": "application/json"}, params)
        if response.status_code == 404:
            return False
        return response.json()

    @_cache_on_arguments(cache_name="cache")
    def get_all(self, **kwargs):
        request = f"{self.base_url}/conceptschemes/{self.scheme_id}/c/"
        params = {"language": self._get_language(**kwargs)}
        params.update(self._get_sort_params(**kwargs))
        response = self._request(request, {"Accept": "application/json"}, params)
        if response.status_code == 404:
            return False
        return response.json()

    @_cache_on_arguments(cache_name="cache")
    def get_top_concepts(self, **kwargs):
        request = f"{self.base_url}/conceptschemes/{self.scheme_id}/topconcepts"
        params = {"language": self._get_language(**kwargs)}
        params.update(self._get_sort_params(**kwargs))
        response = self._request(request, {"Accept": "application/json"}, params)
        if response.status_code == 404:
            return False
        return response.json()

    @_cache_on_arguments(cache_name="cache")
    def get_top_display(self, **kwargs):
        request = f"{self.base_url}/conceptschemes/{self.scheme_id}/displaytop"
        params = {"language": self._get_language(**kwargs)}
        params.update(self._get_sort_params(**kwargs))
        response = self._request(request, {"Accept": "application/json"}, params)
        if response.status_code == 404:
            return False
        return response.json()

    @_cache_on_arguments(cache_name="cache")
    def get_children_display(self, id_, **kwargs):
        request = (
            f"{self.base_url}/conceptschemes/{self.scheme_id}/c/{id_}/displaychildren"
        )
        params = dict()
        params["language"] = self._get_language(**kwargs)
        params.update(self._get_sort_params(**kwargs))
        response = self._request(request, {"Accept": "application/json"}, params)
        if response.status_code == 404:
            return False
        return response.json()

    @_cache_on_arguments(cache_name="cache")
    def expand(self, id_):
        request = f"{self.base_url}/conceptschemes/{self.scheme_id}/c/{id_}/expand"
        response = self._request(request, {"Accept": "application/json"})
        if response.status_code != 200:
            return False
        return response.json()

    def _get_sort_params(self, **kwargs):
        if "sort" in kwargs:
            sort = kwargs.get("sort")
            if kwargs.get("sort_order", "asc") == "desc":
                sort = "-" + sort
            return {"sort": sort}
        return {}

    def _request(self, request, headers=None, params=None):
        response = None
        for _ in range(5):
            try:
                response = self.session.get(
                    request, headers=headers, params=params, timeout=self.timeout
                )
            except (ConnectionError, Timeout) as e:
                log.debug(f"Failed to execute request {request}: {e}")
                continue
            if response.status_code >= 500:
                log.debug(f"Failed to execute request {request}: {response}")
                continue
            return response
        raise ProviderUnavailableException(
            f"Request could not be rexecuted - "
            f"Request: {request} - Response: {response}"
        )
