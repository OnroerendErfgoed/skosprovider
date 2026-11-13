"""
This module provides a provider that reads a list of dicts into memory.
"""

from collections.abc import Callable
from typing import Any

from skosprovider.extra_data import ExtraDataLoader
from skosprovider.extra_data import exception_context
from skosprovider.extra_data import ignore
from skosprovider.extra_data import load_extra_data
from skosprovider.provider import MemoryProvider
from skosprovider.skos import Collection
from skosprovider.skos import Concept
from skosprovider.skos import Label
from skosprovider.skos import Note
from skosprovider.skos import Source
from skosprovider.skos import dict_to_label
from skosprovider.skos import dict_to_note
from skosprovider.skos import dict_to_source


class DictionaryProvider(MemoryProvider):
    """A simple vocab provider that use a python list of dicts.

    The provider expects a list with elements that are dicts that represent
    the concepts.
    """

    def __init__(
        self,
        metadata: dict[str, Any],
        list: list[dict[str, Any] | Concept | Collection],
        *,
        extra_data_loader: ExtraDataLoader = ignore,
        **kwargs: Any,
    ) -> None:
        """
        :param extra_data_loader: A callable that receives the dict of a
            single concept, collection, label, note or source and returns a
            :class:`rdflib.Graph` or `None`. See
            :mod:`skosprovider.dictionary.extra_data` for the available
            loaders. Defaults to :func:`~skosprovider.extra_data.ignore`.
            Labels, notes and sources passed as objects keep their own
            extra_data.
        """
        super().__init__(metadata, [], **kwargs)
        self.extra_data_loader = extra_data_loader
        self.list = [
            self._from_dict(concept_or_collection) for concept_or_collection in list
        ]

    def _from_dict(
        self, data: dict[str, Any] | Concept | Collection
    ) -> Concept | Collection:
        if isinstance(data, (Concept, Collection)):
            return data
        if "type" in data and data["type"] == "collection":
            uri = data.get("uri") or self.uri_generator.generate(
                type="collection", id=data["id"]
            )
            with exception_context(f"collection {data['id']!r}"):
                return Collection(
                    id=data["id"],
                    uri=uri,
                    concept_scheme=self.concept_scheme,
                    labels=self._from_list(data.get("labels", []), dict_to_label),
                    notes=self._from_list(data.get("notes", []), dict_to_note),
                    sources=self._from_list(data.get("sources", []), dict_to_source),
                    members=data.get("members", []),
                    member_of=data.get("member_of", []),
                    superordinates=data.get("superordinates", []),
                    infer_concept_relations=data.get("infer_concept_relations", True),
                    extra_data=load_extra_data(self.extra_data_loader, data),
                )
        else:
            uri = data.get("uri") or self.uri_generator.generate(
                type="concept", id=data["id"]
            )
            with exception_context(f"concept {data['id']!r}"):
                return Concept(
                    id=data["id"],
                    uri=uri,
                    concept_scheme=self.concept_scheme,
                    labels=self._from_list(data.get("labels", []), dict_to_label),
                    notes=self._from_list(data.get("notes", []), dict_to_note),
                    sources=self._from_list(data.get("sources", []), dict_to_source),
                    broader=data.get("broader", []),
                    narrower=data.get("narrower", []),
                    related=data.get("related", []),
                    member_of=data.get("member_of", []),
                    subordinate_arrays=data.get("subordinate_arrays", []),
                    matches=data.get("matches", {}),
                    extra_data=load_extra_data(self.extra_data_loader, data),
                )

    def _from_list(
        self,
        items: list[dict[str, Any] | Label | Note | Source],
        to_object: Callable[[Any], Label | Note | Source],
    ) -> list[Label | Note | Source]:
        """
        Turn the dicts of labels, notes or sources into objects and load their
        extra_data. Objects are left untouched.
        """
        ret = []
        for item in items:
            obj = to_object(item)
            if isinstance(item, dict) and obj is not item:
                with exception_context(repr(obj)):
                    obj.extra_data = load_extra_data(self.extra_data_loader, item)
            ret.append(obj)
        return ret
