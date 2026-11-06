"""
This module contains a JsonLdProvider, an implementation of the
:class:`skosprovider.provider.VocabularyProvider` interface that uses a
JSON-LD document as input.
"""

import json
from typing import Any

from rdflib import Graph
from rdflib.term import Node

from skosprovider.extra_data import ignore
from skosprovider.jsonld.dumper import CONTEXT
from skosprovider.jsonld.extra_data import JsonLdExtraDataLoader
from skosprovider.jsonld.extra_data import node_to_jsonld
from skosprovider.rdf.extra_data import from_unmapped
from skosprovider.rdf.provider import RDFProvider


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
        :param extra_data_loader: A callable that receives a JSON-LD dict with
            the properties of a single concept scheme, concept, collection,
            source, SKOS-XL label or note node that are not turned into
            attributes, and returns a :class:`rdflib.Graph` or `None`. It is
            only called when there are such properties. See
            :mod:`skosprovider.jsonld.extra_data` for the available loaders.
            Defaults to :func:`~skosprovider.extra_data.ignore`.
        """
        self.jsonld_extra_data_loader = extra_data_loader
        graph = Graph().parse(data=json.dumps(document), format="json-ld")
        super().__init__(
            metadata, graph, extra_data_loader=self._load_jsonld_extra_data, **kwargs
        )

    def _load_jsonld_extra_data(self, graph: Graph, node: Node) -> Graph | None:
        if self.jsonld_extra_data_loader is ignore:
            return None
        unmapped = from_unmapped(graph, node)
        if unmapped is None:
            return None
        return self.jsonld_extra_data_loader(node_to_jsonld(unmapped, node, CONTEXT))
