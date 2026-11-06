"""
Loaders and dumpers for the extra_data of skos objects in dicts.

A loader receives the dict of a single concept, collection, label, note or
source passed to a :class:`~skosprovider.dictionary.provider.DictionaryProvider`
and returns a :class:`rdflib.Graph` or `None`.

A dumper receives a skos object and returns a dict that
:func:`~skosprovider.dictionary.dumper.dict_dumper` merges into the dump of that
object, or `None`.

The loaders :func:`from_turtle`, :func:`from_jsonld` and :func:`from_graph`
read the `extra_data` key, the dumpers :func:`to_turtle`, :func:`to_jsonld`
and :func:`to_graph` write it. :func:`skosprovider.extra_data.ignore` can be
used as both a loader and a dumper and is the default everywhere.
"""

import json
from collections.abc import Callable
from typing import Any

from rdflib import Graph
from rdflib import Literal
from rdflib import URIRef

from skosprovider.exceptions import ExtraDataException
from skosprovider.extra_data import SkosObject

ExtraDataDumper = Callable[[SkosObject], dict[str, Any] | None]


def from_turtle(data: dict[str, Any]) -> Graph | None:
    """
    Load a turtle string under `extra_data` into a :class:`rdflib.Graph`.

    :returns: A graph, or `None` when `extra_data` is missing or `None`.
    """
    value = data.get("extra_data")
    if value is None:
        return None
    return Graph().parse(data=value, format="turtle")


def from_jsonld(data: dict[str, Any]) -> Graph | None:
    """
    Load a JSON-LD dict under `extra_data` into a :class:`rdflib.Graph`.

    The dict is expected to contain its own `@context`. Both compact and
    expanded JSON-LD are supported.

    :returns: A graph, or `None` when `extra_data` is missing or `None`.
    """
    value = data.get("extra_data")
    if value is None:
        return None
    return Graph().parse(data=json.dumps(value), format="json-ld")


def from_graph(data: dict[str, Any]) -> Graph | None:
    """
    Pass a :class:`rdflib.Graph` under `extra_data` through unchanged.

    :returns: The graph, or `None` when `extra_data` is missing.
    """
    return data.get("extra_data")


def to_turtle(obj: SkosObject) -> dict[str, str] | None:
    """
    Dump the extra_data of a skos object as a turtle string under `extra_data`.

    :returns: A dict, or `None` when the object has no extra_data.
    """
    if obj.extra_data is None:
        return None
    return {"extra_data": obj.extra_data.serialize(format="turtle")}


def to_jsonld(obj: SkosObject) -> dict[str, Any] | None:
    """
    Dump the extra_data of a skos object as a compact JSON-LD dict under
    `extra_data`.

    The context is built from the namespace bindings of the graph, limited to
    the namespaces that are used by an IRI or datatype in the graph.

    :returns: A dict, or `None` when the object has no extra_data.
    """
    if obj.extra_data is None:
        return None
    # rdflib offers little help in building a sensible JSON-LD context. Its
    # `auto_compact` option puts every namespace bound to the graph in the
    # context, including the ~30 namespaces rdflib binds by default. So we
    # build the context ourselves, keeping only the namespaces actually used
    # by an IRI or datatype in the graph.
    # See https://github.com/RDFLib/rdflib/issues/1679
    # Note that compacting with any context makes rdflib drop an explicit
    # xsd:string datatype, so "x"^^xsd:string comes back as the plain
    # literal "x" (equal in RDF 1.1, but a different term to rdflib).
    iris = set()
    for triple in obj.extra_data:
        for term in triple:
            if isinstance(term, URIRef):
                iris.add(str(term))
            elif isinstance(term, Literal) and term.datatype:
                iris.add(str(term.datatype))
    context = {
        prefix: str(namespace)
        for prefix, namespace in obj.extra_data.namespaces()
        if prefix and any(iri.startswith(str(namespace)) for iri in iris)
    }
    return {
        "extra_data": json.loads(
            obj.extra_data.serialize(format="json-ld", context=context)
        )
    }


def to_graph(obj: SkosObject) -> dict[str, Graph] | None:
    """
    Dump the extra_data of a skos object unchanged under `extra_data`.

    :returns: A dict, or `None` when the object has no extra_data.
    """
    if obj.extra_data is None:
        return None
    return {"extra_data": obj.extra_data}


def dump_extra_data(dumper: ExtraDataDumper, obj: SkosObject) -> dict[str, Any]:
    """
    Call a dumper and wrap any error in an :class:`ExtraDataException`.

    Use :func:`~skosprovider.extra_data.exception_context` to describe which object was being dumped.

    :returns: A dict, empty when the dumper returned `None`.
    """
    try:
        return dumper(obj) or {}
    except Exception as err:
        raise ExtraDataException(f"Failed to dump extra_data: {err}") from err
