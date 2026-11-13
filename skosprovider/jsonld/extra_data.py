"""
Loaders and dumpers for the extra_data of skos objects in JSON-LD.

A JSON-LD loader receives a JSON-LD dict with the properties of a single
concept scheme, concept or collection, or of a source, SKOS-XL label or note
with a uri, that :class:`~skosprovider.jsonld.provider.JsonLdProvider` does
not turn into attributes, and returns a :class:`rdflib.Graph` or `None`. The
dict is built by :func:`node_to_jsonld`. It is only called when there are such
properties.

A JSON-LD dumper receives the concept scheme, a concept or collection, or a
source, SKOS-XL label or note with a uri, and returns a dict of JSON-LD
properties that :func:`~skosprovider.jsonld.dumper.to_jsonld` merges into the
node of that object, or `None`. The properties are expanded, so they do not
depend on the context of the dump.

Together, :func:`from_unmapped` and :func:`to_unmapped` let the properties
that JsonLdProvider does not turn into attributes survive a round trip
through JsonLdProvider and :func:`~skosprovider.jsonld.dumper.to_jsonld`.

:func:`skosprovider.extra_data.ignore` can be used as both a loader and a
dumper and is the default everywhere.
"""

import json
from collections.abc import Callable
from typing import Any

from pyld import jsonld as pyld_jsonld
from rdflib import Graph
from rdflib.term import Node
from rdflib.term import URIRef

from skosprovider.extra_data import SkosObject
from skosprovider.skos import ConceptScheme

JsonLdExtraDataLoader = Callable[[dict[str, Any]], Graph | None]
JsonLdExtraDataDumper = Callable[[SkosObject | ConceptScheme], dict[str, Any] | None]


def node_to_jsonld(
    graph: Graph, node: Node, context: dict[str, Any] | None = None
) -> dict[str, Any]:
    """
    Describe a node of a graph as a single JSON-LD node object.

    The blank nodes the node points to are embedded, so the result holds all
    triples of the node and its blank nodes.

    :param context: When given, the node is compacted with this context and
        the result contains it as `@context`. Otherwise the node is expanded.
    :returns: A JSON-LD node object, `{}` when the graph says nothing about
        the node.
    """
    by_id = {
        item["@id"]: item
        for item in json.loads(graph.serialize(format="json-ld"))
        if "@id" in item
    }
    expanded = _embed(by_id, by_id.get(str(node), {}), set())
    if context is None or not expanded:
        return expanded
    return pyld_jsonld.compact(expanded, context)


def _embed(
    by_id: dict[str, dict[str, Any]], item: dict[str, Any], seen: set[str]
) -> dict[str, Any]:
    """
    Replace the references to blank nodes in a node object by the blank nodes
    themselves.
    """
    embedded = {}
    for key, values in item.items():
        if not isinstance(values, list):
            embedded[key] = values
            continue
        embedded[key] = [
            _embed_value(by_id, value, seen) if isinstance(value, dict) else value
            for value in values
        ]
    return embedded


def _embed_value(
    by_id: dict[str, dict[str, Any]], value: dict[str, Any], seen: set[str]
) -> dict[str, Any]:
    id_ = value.get("@id")
    if set(value) != {"@id"} or not id_.startswith("_:") or id_ in seen:
        return value
    blank_node = _embed(by_id, by_id.get(id_, {}), seen | {id_})
    blank_node.pop("@id", None)
    return blank_node


def from_unmapped(data: dict[str, Any]) -> Graph | None:
    """
    Load the JSON-LD dict built by :func:`node_to_jsonld` into a
    :class:`rdflib.Graph`.

    :returns: A graph, or `None` when the dict holds no triples.
    """
    graph = Graph().parse(data=json.dumps(data), format="json-ld")
    return graph if len(graph) else None


def to_unmapped(obj: SkosObject | ConceptScheme) -> dict[str, Any] | None:
    """
    Dump the extra_data of a skos object as expanded JSON-LD properties of its
    node. The counterpart of :func:`from_unmapped`.

    Only the triples with the uri of the object as subject are dumped. Blank
    nodes they point to are embedded.

    :returns: A dict, or `None` when the object has no such extra_data.
    """
    if obj.extra_data is None or not obj.uri:
        return None
    properties = node_to_jsonld(obj.extra_data, URIRef(obj.uri))
    properties.pop("@id", None)
    return properties or None
