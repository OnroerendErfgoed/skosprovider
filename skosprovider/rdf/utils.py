"""
This module contains utility functions for dealing with skos providers.
"""

import logging
from typing import Callable
from typing import TypeAlias

from rdflib import Graph
from rdflib import Literal
from rdflib import Namespace
from rdflib.namespace import DCTERMS
from rdflib.namespace import RDF
from rdflib.namespace import SKOS
from rdflib.namespace import VOID
from rdflib.term import BNode
from rdflib.term import URIRef

from skosprovider.skos import Collection
from skosprovider.skos import Concept
from skosprovider.skos import ConceptScheme
from skosprovider.skos import Label
from skosprovider.skos import Note
from skosprovider.skos import SkosObject
from skosprovider.skos import Source
from skosprovider.utils import add_lang_to_html
from skosprovider.utils import extract_language

RdfSerializer: TypeAlias = Callable[[Graph, SkosObject], None] | None
"""A callable that receives a graph and a SKOS object, and adds extra triples
to the graph.  Called only when the object's :attr:`extra_data` is not
:obj:`None`.  The subject URIRef is available as ``URIRef(obj.uri)``.

Example::

    from rdflib.namespace import SKOS
    from rdflib import Literal, URIRef

    def my_serializer(graph, obj):
        if isinstance(obj.extra_data, dict):
            subject = URIRef(obj.uri)
            for notation in obj.extra_data.get("notation", []):
                graph.add((subject, SKOS.notation, Literal(notation)))

    result = rdf_dumper(provider, extra_data_serializer=my_serializer)
"""

SKOS_THES = Namespace("http://purl.org/iso25964/skos-thes#")
log = logging.getLogger(__name__)


def _init_graph(provider, extra_data_serializer: RdfSerializer = None):
    """Build a graph with conceptscheme triples, return (graph, conceptscheme URIRef)."""
    graph = Graph()
    graph.namespace_manager.bind("skos", SKOS)
    graph.namespace_manager.bind("dcterms", DCTERMS)
    graph.namespace_manager.bind("skos-thes", SKOS_THES)
    graph.namespace_manager.bind("void", VOID)
    conceptscheme = URIRef(provider.concept_scheme.uri)
    _add_in_dataset(graph, conceptscheme, provider)
    graph.add((conceptscheme, RDF.type, SKOS.ConceptScheme))
    graph.add((conceptscheme, DCTERMS.identifier, Literal(provider.metadata["id"])))
    _add_labels(graph, provider.concept_scheme, conceptscheme)
    _add_notes(graph, provider.concept_scheme, conceptscheme)
    _add_sources(graph, provider.concept_scheme, conceptscheme)
    _add_languages(graph, provider.concept_scheme, conceptscheme)
    if extra_data_serializer is not None and provider.concept_scheme.extra_data is not None:
        extra_data_serializer(graph, provider.concept_scheme)
    return graph, conceptscheme


def rdf_dumper(provider, extra_data_serializer: RdfSerializer = None):
    """
    Dump a provider to a format that can be passed to a
    :class:`skosprovider.providers.RDFProvider`.

    :param skosprovider.providers.VocabularyProvider provider: The provider
        that wil be turned into an :class:`rdflib.graph.Graph`.

    :param extra_data_serializer: Optional :data:`RdfSerializer` callable that
        receives ``(graph, skos_object)`` and adds extra triples for
        objects that carry :attr:`~skosprovider.skos.Concept.extra_data`.

    :rtype: :class:`rdflib.graph.Graph`
    """
    graph, conceptscheme = _init_graph(provider, extra_data_serializer)
    for top_concept in provider.get_top_concepts():
        graph.add((conceptscheme, SKOS.hasTopConcept, URIRef(top_concept["uri"])))
    for concept_id in [x["id"] for x in provider.get_all()]:
        _add_c(graph, provider, concept_id, extra_data_serializer)
    return graph


def rdf_c_dumper(provider, concept_id, extra_data_serializer: RdfSerializer = None):
    """
    Dump one concept or collection from a provider to a format that can be passed to a
    :class:`skosprovider.providers.RDFProvider`.

    :param skosprovider.providers.VocabularyProvider provider: The provider
        that wil be turned into an :class:`rdflib.graph.Graph`.

    :param concept_id: identifier

    :param extra_data_serializer: Optional :data:`RdfSerializer` callable.
        See :func:`rdf_dumper`.

    :rtype: :class:`rdflib.graph.Graph`
    """
    graph, _ = _init_graph(provider, extra_data_serializer)
    _add_c(graph, provider, concept_id, extra_data_serializer)
    return graph


def rdf_conceptscheme_dumper(provider, extra_data_serializer: RdfSerializer = None):
    """
    Dump all information of the conceptscheme of a provider to a format that can be passed to a
    :class:`skosprovider.providers.RDFProvider`.

    :param skosprovider.providers.VocabularyProvider provider: The provider
        that wil be turned into an :class:`rdflib.graph.Graph`.

    :param extra_data_serializer: Optional :data:`RdfSerializer` callable.
        See :func:`rdf_dumper`.

    :rtype: :class:`rdflib.graph.Graph`
    """
    graph, conceptscheme = _init_graph(provider, extra_data_serializer)
    for top_concept in provider.get_top_concepts():
        graph.add((conceptscheme, SKOS.hasTopConcept, URIRef(top_concept["uri"])))
    return graph


def _add_in_dataset(graph, subject, provider):
    """
    Checks if the provider says something about a dataset and if so adds
    void.inDataset statements.

    :param rdflib.graph.Graph graph: The graph to add statements to.
    :param rdflib.term.URIRef subject: The subject to add an inDataset statement to.
    :param skosprovider.providers.VocabularyProvider provider:
    """

    duri = provider.get_metadata().get("dataset", {}).get("uri", None)
    if duri:
        graph.add((subject, VOID.inDataset, URIRef(duri)))


def _add_c(graph, provider, concept_id, extra_data_serializer: RdfSerializer = None):
    """
    Adds a concept or collection to the graph.

    :param rdflib.graph.Graph graph: The graph to add statements to.
    :param skosprovider.providers.VocabularyProvider provider: Provider
    :param concept_id: The id of a concept or collection.
    :param extra_data_serializer: Optional :data:`RdfSerializer` callable.
    """

    skos_obj = provider.get_by_id(concept_id)
    subject = URIRef(skos_obj.uri)
    _add_in_dataset(graph, subject, provider)
    if skos_obj.id != skos_obj.uri:
        graph.add((subject, DCTERMS.identifier, Literal(skos_obj.id)))
    conceptscheme = URIRef(provider.concept_scheme.uri)
    graph.add((subject, SKOS.inScheme, conceptscheme))
    _add_labels(graph, skos_obj, subject)
    _add_notes(graph, skos_obj, subject)
    _add_sources(graph, skos_obj, subject)
    if extra_data_serializer is not None and skos_obj.extra_data is not None:
        extra_data_serializer(graph, skos_obj)
    if isinstance(skos_obj, Concept):
        graph.add((subject, RDF.type, SKOS.Concept))
        for broader_id in skos_obj.broader:
            broader = provider.get_by_id(broader_id)
            if broader:
                graph.add((subject, SKOS.broader, URIRef(broader.uri)))
        for narrower_id in skos_obj.narrower:
            narrower = provider.get_by_id(narrower_id)
            if narrower:
                graph.add((subject, SKOS.narrower, URIRef(narrower.uri)))
        for related_id in skos_obj.related:
            related = provider.get_by_id(related_id)
            if related:
                graph.add((subject, SKOS.related, URIRef(related.uri)))
        for subordinate_id in skos_obj.subordinate_arrays:
            subordinate_array = provider.get_by_id(subordinate_id)
            if subordinate_array:
                graph.add(
                    (subject, SKOS_THES.subordinateArray, URIRef(subordinate_array.uri))
                )
                if subordinate_array.infer_concept_relations:

                    def _add_coll_members_to_superordinate(so, members):
                        """
                        Recursively create broader/narrower relations between
                        collection members and the superordinate concept
                        """
                        for member_id in members:
                            member = provider.get_by_id(member_id)
                            if member.type == "concept":
                                graph.add((so, SKOS.narrower, URIRef(member.uri)))
                                graph.add((URIRef(member.uri), SKOS.broader, so))
                            elif member.type == "collection":
                                _add_coll_members_to_superordinate(so, member.members)

                    _add_coll_members_to_superordinate(
                        subject, subordinate_array.members
                    )
        for member_of_id in skos_obj.member_of:
            collection = provider.get_by_id(member_of_id)
            if collection:
                graph.add((URIRef(collection.uri), SKOS.member, subject))
                graph.add((URIRef(collection.uri), RDF.type, SKOS.Collection))
                graph.add((URIRef(collection.uri), SKOS.inScheme, conceptscheme))
                graph.add(
                    (URIRef(collection.uri), DCTERMS.identifier, Literal(collection.id))
                )

                def _add_coll_superordinates_as_broader(member, coll):
                    """
                    Recursively create broader relations between
                    a collection member and the superordinate concepts
                    """
                    if coll.infer_concept_relations:
                        for superordinate_id in coll.superordinates:
                            superordinate = provider.get_by_id(superordinate_id)
                            graph.add(
                                (
                                    URIRef(member.uri),
                                    SKOS.broader,
                                    URIRef(superordinate.uri),
                                )
                            )
                        for parent_coll_id in coll.member_of:
                            parent_collection = provider.get_by_id(parent_coll_id)
                            _add_coll_superordinates_as_broader(
                                member, parent_collection
                            )

                _add_coll_superordinates_as_broader(skos_obj, collection)
        for match_type in skos_obj.matches.keys():
            for match_uri in skos_obj.matches[match_type]:
                graph.add((subject, URIRef(SKOS[match_type + "Match"]), URIRef(match_uri)))
    elif isinstance(skos_obj, Collection):
        graph.add((subject, RDF.type, SKOS.Collection))
        for member_id in skos_obj.members:
            member = provider.get_by_id(member_id)
            if member:
                graph.add((subject, SKOS.member, URIRef(member.uri)))
        for superordinate_id in skos_obj.superordinates:
            superordinate = provider.get_by_id(superordinate_id)
            if superordinate:
                graph.add((subject, SKOS_THES.superOrdinate, URIRef(superordinate.uri)))


def _add_labels(graph, skos_obj, subject):
    for lbl in skos_obj.labels:
        labeltype = (
            lbl.type
            if lbl.type in ["prefLabel", "altLabel", "hiddenLabel"]
            else "hiddenLabel"
        )
        predicate = URIRef(SKOS[labeltype])
        lang = extract_language(lbl.language)
        graph.add((subject, predicate, Literal(lbl.label, lang=lang)))


def _add_notes(graph, skos_obj, subject):
    for note in skos_obj.notes:
        predicate = URIRef(SKOS[note.type])
        lang = extract_language(note.language)
        if note.markup is None:
            graph.add((subject, predicate, Literal(note.note, lang=lang)))
        else:
            html = add_lang_to_html(note.note, lang)
            graph.add((subject, predicate, Literal(html, datatype=RDF.HTML)))


def _add_sources(graph, skos_obj, subject):
    """
    Add sources to the RDF graph.

    :param rdflib.graph.Graph graph: An RDF Graph.
    :param skos_obj: A :class:`skosprovider.skos.ConceptScheme`,
        :class:`skosprovider.skos.Concept` or :class:`skosprovider.skos.Collection`
    :param subject: The RDF subject to add the sources to.
    """
    for src in skos_obj.sources:
        source = BNode()
        graph.add((source, RDF.type, DCTERMS.BibliographicResource))
        if src.markup is None:
            graph.add((source, DCTERMS.bibliographicCitation, Literal(src.citation)))
        else:
            graph.add(
                (
                    source,
                    DCTERMS.bibliographicCitation,
                    Literal(src.citation, datatype=RDF.HTML),
                )
            )
        graph.add((subject, DCTERMS.source, source))


def _add_languages(graph, skos_obj, subject):
    """
    Add languages to the RDF graph.

    :param rdflib.graph.Graph graph: An RDF Graph.
    :param skos_obj: A :class:`skosprovider.skos.ConceptScheme`.
    :param subject: The RDF subject to add the sources to.
    """
    for lang_tag in skos_obj.languages:
        graph.add((subject, DCTERMS.language, Literal(lang_tag)))
