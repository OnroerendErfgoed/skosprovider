"""
Loaders and dumpers for the extra_data of skos objects in RDF.

A loader receives the graph of a single concept scheme, concept or
collection, or of a source, SKOS-XL label or note with a uri, read by a
:class:`~skosprovider.rdf.provider.RDFProvider`, and the skos object built
from it, and returns a :class:`rdflib.Graph` or `None`. The graph of an object
is the Concise Bounded Description of its node: the triples about the node
and, recursively, about the blank nodes it points to.

A dumper receives a skos object and returns a :class:`rdflib.Graph` that the
dumpers in :mod:`skosprovider.rdf.dumper` merge into the dump, or `None`.

The loader :func:`from_unmapped` reads the triples RDFProvider does not turn
into attributes, the dumper :func:`to_graph` writes the whole extra_data.
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
from rdflib.term import URIRef

from skosprovider.extra_data import SkosObject
from skosprovider.rdf.provider import SKOSXL
from skosprovider.rdf.provider import SKOS_THES
from skosprovider.skos import Collection
from skosprovider.skos import Concept
from skosprovider.skos import ConceptScheme
from skosprovider.skos import Label
from skosprovider.skos import Note
from skosprovider.skos import Source

_DESCRIBED = frozenset(
    [
        *(SKOS[type_] for type_ in ("prefLabel", "altLabel", "hiddenLabel")),
        *(SKOSXL[type_] for type_ in ("prefLabel", "altLabel", "hiddenLabel")),
        *(SKOS[type_] for type_ in Note.valid_types),
        DCTERMS.source,
        # Derived by the dumpers from the label and the metadata of the provider.
        RDFS.label,
        VOID.inDataset,
    ]
)
"""Predicates of a concept scheme, concept and collection alike."""

_IN_SCHEME = frozenset(
    [SKOS.inScheme, SKOS.topConceptOf, DCTERMS.identifier, DC.identifier]
)
"""Predicates of a concept and a collection alike."""

# which properties we store for each object
# this is important so we can store the remainder as extra_data
_MAPPED = {
    ConceptScheme: _DESCRIBED
    | {
        DCTERMS.language,
        DC.language,
        # Derived by the dumpers from the provider.
        DCTERMS.identifier,
        SKOS.hasTopConcept,
    },
    Concept: _DESCRIBED
    | _IN_SCHEME
    | {
        SKOS.broader,
        SKOS.narrower,
        SKOS.related,
        SKOS_THES.subordinateArray,
        *(SKOS[match_type + "Match"] for match_type in Concept.matchtypes),
    },
    Collection: _DESCRIBED | _IN_SCHEME | {SKOS.member, SKOS_THES.superOrdinate},
    Label: frozenset([SKOSXL.literalForm, DCTERMS.type]),
    Note: frozenset([RDF.value]),
    Source: frozenset([DCTERMS.bibliographicCitation, RDF.value]),
}
"""
Predicates that RDFProvider turns into attributes, or that the dumpers derive
from them, per type of skos object.
"""

_RDF_TYPES = {
    ConceptScheme: SKOS.ConceptScheme,
    Concept: SKOS.Concept,
    Collection: SKOS.Collection,
    Label: SKOSXL.Label,
    Source: DCTERMS.BibliographicResource,
}
"""The rdf:type that RDFProvider reads or the dumpers write, per type of object."""


def from_unmapped(graph: Graph, skos_object: SkosObject) -> Graph | None:
    """
    Load the triples about an object that RDFProvider does not turn into
    attributes, eg. a skos:notation or a dct:creator.

    Which predicates are mapped depends on the type of the skos object, eg. a
    dct:language is mapped for a concept scheme, but not for a source.

    The triples of the object itself are filtered on their predicate. Blank
    nodes they point to are followed and copied entirely, like in a
    Concise Bounded Description.

    :returns: A graph, or `None` when there are no such triples.
    """
    subject = URIRef(skos_object.uri)
    mapped = _MAPPED[type(skos_object)]
    rdf_type = _RDF_TYPES.get(type(skos_object))
    extra_data = Graph()
    for prefix, namespace in graph.namespaces():
        extra_data.bind(prefix, namespace, override=False)
    blank_nodes = []
    for predicate, object_ in graph.predicate_objects(subject):
        if predicate in mapped or (predicate == RDF.type and object_ == rdf_type):
            continue
        extra_data.add((subject, predicate, object_))
        if isinstance(object_, BNode):
            blank_nodes.append(object_)
    seen = set()
    while blank_nodes:
        blank_node = blank_nodes.pop()
        if blank_node in seen:
            continue
        seen.add(blank_node)
        for predicate, object_ in graph.predicate_objects(blank_node):
            extra_data.add((blank_node, predicate, object_))
            if isinstance(object_, BNode):
                blank_nodes.append(object_)
    return extra_data if len(extra_data) else None


def to_graph(obj: SkosObject) -> Graph | None:
    """
    Dump the extra_data of a skos object unchanged, so it is merged into the
    RDF dump.

    :returns: The extra_data of the object.
    """
    return obj.extra_data
