"""
Loaders and dumpers for the extra_data of skos objects in RDF.

An RDF loader receives the graph passed to a
:class:`~skosprovider.rdf.provider.RDFProvider` and the node of a single
concept scheme, concept, collection, source, SKOS-XL label or note node, and
returns a :class:`rdflib.Graph` or `None`.

An RDF dumper receives a skos object and returns a :class:`rdflib.Graph` that
the dumpers in :mod:`skosprovider.rdf.dumper` merge into the dump, or `None`.

Plain SKOS labels and notes are literals in RDF, so they get no extra_data. A
SKOS-XL label and a note written as a node with rdf:value do.

A source or a note node is usually a blank node, which has no identity outside
the graph it was read from. So :func:`from_unmapped` replaces a blank node
object by :data:`BLANK_NODE_PLACEHOLDER` in its extra_data, and the dumpers
replace the placeholder by the node of the dumped object again.

Together, :func:`from_unmapped` and :func:`to_unmapped` let the triples that
RDFProvider does not turn into attributes survive a round trip through
RDFProvider and :func:`~skosprovider.rdf.dumper.rdf_dumper`.

:func:`skosprovider.extra_data.ignore` can be used as both a loader and a
dumper and is the default everywhere.
"""

from rdflib import Graph
from rdflib.namespace import DC
from rdflib.namespace import DCTERMS
from rdflib.namespace import RDF
from rdflib.namespace import RDFS
from rdflib.namespace import SKOS
from rdflib.namespace import VOID
from rdflib.term import BNode
from rdflib.term import Node
from rdflib.term import URIRef

from skosprovider.extra_data import SkosObject
from skosprovider.rdf.provider import SKOSXL
from skosprovider.rdf.provider import SKOS_THES
from skosprovider.skos import Concept
from skosprovider.skos import ConceptScheme
from skosprovider.skos import Note

BLANK_NODE_PLACEHOLDER = URIRef("urn:x-skosprovider:blank-node")
"""Stands for the node of a blank node object in its extra_data."""

_MAPPED_PREDICATES = frozenset(
    [
        SKOS.prefLabel,
        SKOS.altLabel,
        SKOS.hiddenLabel,
        SKOSXL.prefLabel,
        SKOSXL.altLabel,
        SKOSXL.hiddenLabel,
        SKOSXL.literalForm,
        *(SKOS[type_] for type_ in Note.valid_types),
        RDF.value,
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
        # Derived by the dumpers from the label and the metadata of the provider.
        RDFS.label,
        VOID.inDataset,
    ]
)
"""
Predicates of an object that RDFProvider turns into attributes, or that the
dumpers derive from them.
"""

_MAPPED_TYPES = frozenset(
    [
        SKOS.ConceptScheme,
        SKOS.Concept,
        SKOS.Collection,
        DCTERMS.BibliographicResource,
        SKOSXL.Label,
    ]
)
"""Values of rdf:type of an object that RDFProvider turns into an object."""


def from_unmapped(graph: Graph, subject: Node) -> Graph | None:
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
    is_xl_label = (subject, RDF.type, SKOSXL.Label) in graph
    for predicate, object_ in graph.predicate_objects(subject):
        if (
            predicate in _MAPPED_PREDICATES
            or (predicate == RDF.type and object_ in _MAPPED_TYPES)
            # The dct:type of a SKOS-XL label holds its label_types.
            or (is_xl_label and predicate == DCTERMS.type)
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


def to_unmapped(obj: SkosObject | ConceptScheme) -> Graph | None:
    """
    Dump the extra_data of a skos object unchanged, so it is merged into the
    RDF dump. The counterpart of :func:`from_unmapped`.

    :returns: The extra_data of the object.
    """
    return obj.extra_data
