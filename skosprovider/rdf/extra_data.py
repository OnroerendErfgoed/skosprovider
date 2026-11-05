"""
Loaders and dumpers for the extra_data of skos objects in RDF.

An RDF loader receives the graph passed to a
:class:`~skosprovider.rdf.providers.RDFProvider` and the node of a single
concept scheme, concept, collection or source, and returns a
:class:`rdflib.Graph` or `None`.

An RDF dumper receives a skos object and returns a :class:`rdflib.Graph` that
the dumpers in :mod:`skosprovider.rdf.utils` merge into the dump, or `None`.

Labels and notes are literals in RDF, so they get no extra_data.

A source is usually a blank node, which has no identity outside the graph it
was read from. So :func:`unmapped_triples` replaces a blank node object by
:data:`BLANK_NODE_PLACEHOLDER` in its extra_data, and the dumpers replace the
placeholder by the node of the dumped object again.

:func:`skosprovider.extra_data.ignore` can be used as both a loader and a
dumper and is the default everywhere.
"""

from collections.abc import Callable

from rdflib import Graph
from rdflib.namespace import DC
from rdflib.namespace import DCTERMS
from rdflib.namespace import RDF
from rdflib.namespace import SKOS
from rdflib.term import BNode
from rdflib.term import Node
from rdflib.term import URIRef

from skosprovider.exceptions import ExtraDataException
from skosprovider.extra_data import SkosObject
from skosprovider.rdf.providers import SKOS_THES
from skosprovider.skos import Concept
from skosprovider.skos import ConceptScheme
from skosprovider.skos import Note

RdfExtraDataDumper = Callable[[SkosObject | ConceptScheme], Graph | None]

BLANK_NODE_PLACEHOLDER = URIRef("urn:x-skosprovider:blank-node")
"""Stands for the node of a blank node object in its extra_data."""

_MAPPED_PREDICATES = frozenset(
    [
        SKOS.prefLabel,
        SKOS.altLabel,
        SKOS.hiddenLabel,
        *(SKOS[type_] for type_ in Note.valid_types),
        SKOS.broader,
        SKOS.narrower,
        SKOS.related,
        SKOS.member,
        *(SKOS[match_type + "Match"] for match_type in Concept.matchtypes),
        SKOS.inScheme,
        SKOS.topConceptOf,
        SKOS.hasTopConcept,
        SKOS_THES.subordinateArray,
        SKOS_THES.superOrdinate,
        DCTERMS.identifier,
        DC.identifier,
        DCTERMS.source,
        DCTERMS.bibliographicCitation,
        DCTERMS.language,
        DC.language,
    ]
)
"""Predicates of an object that RDFProvider turns into attributes."""

_MAPPED_TYPES = frozenset(
    [SKOS.ConceptScheme, SKOS.Concept, SKOS.Collection, DCTERMS.BibliographicResource]
)
"""Values of rdf:type of an object that RDFProvider turns into an object."""


def unmapped_triples(graph: Graph, subject: Node) -> Graph | None:
    """
    Load the triples about an object that RDFProvider does not turn into
    attributes, eg. a skos:notation or a dct:creator.

    The triples of the object itself are filtered on their predicate. Blank
    nodes they point to are followed and copied entirely, like in a
    Concise Bounded Description. When the object is a blank node, it is
    replaced by :data:`BLANK_NODE_PLACEHOLDER`.

    :returns: A graph, or `None` when there are no such triples.
    """
    extra_data = Graph()
    for prefix, namespace in graph.namespaces():
        extra_data.bind(prefix, namespace, override=False)
    root = BLANK_NODE_PLACEHOLDER if isinstance(subject, BNode) else subject
    blank_nodes = []
    for predicate, object_ in graph.predicate_objects(subject):
        if predicate in _MAPPED_PREDICATES or (
            predicate == RDF.type and object_ in _MAPPED_TYPES
        ):
            continue
        extra_data.add((root, predicate, object_))
        if isinstance(object_, BNode):
            blank_nodes.append(object_)
    seen = set()
    while blank_nodes:
        blank_node = blank_nodes.pop()
        if blank_node in seen or blank_node == subject:
            continue
        seen.add(blank_node)
        for predicate, object_ in graph.predicate_objects(blank_node):
            extra_data.add((blank_node, predicate, object_))
            if isinstance(object_, BNode):
                blank_nodes.append(object_)
    return extra_data if len(extra_data) else None


def merge_graph(obj: SkosObject | ConceptScheme) -> Graph | None:
    """
    Dump the extra_data of a skos object unchanged, so it is merged into the
    RDF dump.

    :returns: The extra_data of the object.
    """
    return obj.extra_data


def dump_extra_data_graph(
    dumper: RdfExtraDataDumper, obj: SkosObject | ConceptScheme, node: Node
) -> Graph:
    """
    Call an RDF dumper and wrap any error in an :class:`ExtraDataException`.

    Use :func:`~skosprovider.extra_data.exception_context` to describe which
    object was being dumped.

    :param node: The node of the object in the dump. It replaces
        :data:`BLANK_NODE_PLACEHOLDER`.
    :returns: A graph, empty when the dumper returned `None`.
    """
    try:
        extra_data = dumper(obj)
    except Exception as err:
        raise ExtraDataException(f"Failed to dump extra_data: {err}") from err
    dumped = Graph()
    if extra_data is None:
        return dumped
    for prefix, namespace in extra_data.namespaces():
        dumped.bind(prefix, namespace, override=False)
    for triple in extra_data:
        dumped.add(
            tuple(node if term == BLANK_NODE_PLACEHOLDER else term for term in triple)
        )
    return dumped
