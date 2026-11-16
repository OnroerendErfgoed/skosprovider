"""
This module contains a JsonLdProvider, an implementation of the
:class:`skosprovider.provider.VocabularyProvider` interface that uses a
JSON-LD document as input.
"""

import json
from collections.abc import Callable
from typing import Any

from rdflib import Graph

from skosprovider.extra_data import SkosObject
from skosprovider.extra_data import ignore
from skosprovider.jsonld.extra_data import graph_to_jsonld
from skosprovider.rdf.provider import RDFProvider

JsonLdExtraDataLoader = Callable[[dict[str, Any], SkosObject], Graph | None]


class JsonLdProvider(RDFProvider):
    """
    A vocabulary provider that reads a JSON-LD document, eg. one dumped by
    :func:`~skosprovider.jsonld.dumper.to_jsonld`.

    The document is parsed into an :class:`rdflib.graph.Graph` that is read
    like an :class:`~skosprovider.rdf.provider.RDFProvider` does.
    """

    def __init__(
        self,
        metadata: dict[str, Any],
        document: dict[str, Any] | list[Any],
        *,
        extra_data_loader: JsonLdExtraDataLoader = ignore,
        **kwargs: Any,
    ) -> None:
        """
        :param document: A JSON-LD document, as returned by :func:`json.load`.
        :param extra_data_loader: A callable that receives the node of a
            single concept scheme, concept or collection, or of a source,
            SKOS-XL label or note with a uri, as an expanded JSON-LD dict, and
            the skos object built from it, and returns a :class:`rdflib.Graph`
            or `None`.
            See :mod:`skosprovider.jsonld.extra_data` for what the node holds
            and for the available loaders. Defaults to
            :func:`~skosprovider.extra_data.ignore`.
        """
        self.jsonld_extra_data_loader = extra_data_loader
        graph = Graph().parse(data=json.dumps(document), format="json-ld")
        super().__init__(
            metadata, graph, extra_data_loader=self._load_jsonld_extra_data, **kwargs
        )

    def _load_jsonld_extra_data(
        self, graph: Graph, skos_object: SkosObject
    ) -> Graph | None:
        if self.jsonld_extra_data_loader is ignore:
            return None
        node = graph_to_jsonld(graph, skos_object.uri)
        if not node:
            return None
        return self.jsonld_extra_data_loader(node, skos_object)
