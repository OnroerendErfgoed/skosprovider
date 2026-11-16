"""
Loaders and dumpers for the extra_data of skos objects in JSON-LD.

In the skos model, extra_data is a :class:`rdflib.Graph`. Loaders for JSON-LD
read a JSON-LD dict and return a graph, dumpers for JSON-LD turn the graph into
a JSON-LD dict.

A JSON-LD loader receives the node of a single concept scheme, concept or
collection, or of a source, SKOS-XL label or note with a uri, as an expanded
JSON-LD dict: keys and types are full IRIs and every value is a list. Use a
JSON-LD library to read it, eg. compact it with a context of your own with
:func:`pyld.jsonld.compact` to get fixed keys, whatever prefixes the document
used. The node holds all triples about the object, including the ones that
:class:`~skosprovider.jsonld.provider.JsonLdProvider` turns into attributes,
gathered from wherever the document describes the object. The blank nodes
behind them are in `@included`, other nodes are references by their `@id`.

The loader receives triples, not the text of the document: how the document
wrote them, eg. its prefixes, nesting or `@included`, is not kept. A node in
`@included` is not part of the object it is written in, it is part of the
document, so the loader does not receive it.

The loader also receives the skos object built from the node, so it can
tell what kind of object it loads. Like every extra_data loader, it returns a
:class:`rdflib.Graph` or `None`. :func:`jsonld_to_graph` reads a JSON-LD dict
into a graph.

A JSON-LD dumper receives the concept scheme, a concept or collection, or a
source, SKOS-XL label or note with a uri, and returns a dict of JSON-LD
properties that :func:`~skosprovider.jsonld.dumper.to_jsonld` merges into the
node of that object, or `None`. The dict may have its own `@context`, use the
prefixes of the context of the dump or use full IRIs: the properties are
compacted with the context of the dump before they are merged, see
:attr:`~skosprovider.jsonld.dumper.DumpContext.extra_data_dumper`.

Together, :func:`from_unmapped` and :func:`to_jsonld` let the properties that
JsonLdProvider does not turn into attributes survive a round trip through
JsonLdProvider and :func:`skosprovider.jsonld.dumper.to_jsonld`.

:func:`skosprovider.extra_data.ignore` can be used as both a loader and a
dumper and is the default everywhere.
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
