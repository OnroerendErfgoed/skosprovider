"""
Loaders and dumpers for the extra_data of skos objects in JSON-LD.

A loader receives the node of a single concept scheme, concept or collection,
or of a source, SKOS-XL label or note with a uri, read by a
:class:`~skosprovider.jsonld.provider.JsonLdProvider`, and the skos object
built from it, and returns a :class:`rdflib.Graph` or `None`. The node is an
expanded JSON-LD dict with all triples about the object, and the blank nodes
behind them in `@included`.

A dumper receives a skos object and returns a dict of JSON-LD properties that
:func:`~skosprovider.jsonld.dumper.to_jsonld` compacts with the context of the
dump and merges into the node of that object, or `None`.

The loader :func:`from_unmapped` reads the properties JsonLdProvider does not
turn into attributes, the dumper :func:`to_jsonld` writes the whole
extra_data. :func:`skosprovider.extra_data.ignore` can be used as both a
loader and a dumper and is the default everywhere.
"""

import json
from typing import Any

from rdflib import Graph

from skosprovider.extra_data import SkosObject
from skosprovider.rdf.extra_data import from_unmapped as rdf_from_unmapped

# ---- Default extra_data loader and dumper


def from_unmapped(node: dict[str, Any], skos_object: SkosObject) -> Graph | None:
    """
    Load the properties of a JSON-LD node that JsonLdProvider does not turn
    into attributes, eg. a skos:notation or a dct:creator.

    The properties are filtered like
    :func:`skosprovider.rdf.extra_data.from_unmapped` does: blank nodes
    behind an unmapped property are kept entirely.

    :returns: A graph, or `None` when there are no such properties.
    """
    return rdf_from_unmapped(jsonld_to_graph(node), skos_object)


def to_jsonld(obj: SkosObject) -> dict[str, Any] | None:
    """
    Dump the whole extra_data of a skos object as expanded JSON-LD properties
    of its node. All other nodes of the extra_data, eg. blank nodes or nodes
    that are not linked to the object, are put in `@included`, so no triple
    is lost. :func:`~skosprovider.jsonld.dumper.to_jsonld` compacts the
    properties with the context of the dump.

    :returns: A dict, or `None` when the object has no uri or no extra_data.
    """
    if obj.extra_data is None or not obj.uri:
        return None
    properties = graph_to_jsonld(obj.extra_data, obj.uri)
    properties.pop("@id", None)
    return properties or None


# ---- utils


def graph_to_jsonld(graph: Graph, uri: str) -> dict[str, Any]:
    """
    Describe a graph as the expanded JSON-LD node with the given uri, with all
    other nodes of the graph in `@included`.

    :returns: A JSON-LD node object, `{}` when the graph is empty.
    """
    if not len(graph):
        return {}
    nodes = json.loads(graph.serialize(format="json-ld"))
    root = next((node for node in nodes if node["@id"] == uri), {"@id": uri})
    included = [node for node in nodes if node is not root]
    if included:
        root["@included"] = included
    return root


def jsonld_to_graph(node: dict[str, Any]) -> Graph:
    """
    Read a JSON-LD node object into a :class:`rdflib.Graph`.
    """
    return Graph().parse(data=json.dumps(node), format="json-ld")
