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
from skosprovider.skos import Source
from skosprovider.utils import add_lang_to_html
from skosprovider.utils import extract_language

SkosObject: TypeAlias = Concept | Collection | ConceptScheme | Label | Note | Source

RdfSerializer: TypeAlias = Callable[[Graph, URIRef, SkosObject], None] | None
"""A callable that receives a graph, a subject URIRef and a SKOS object, and
adds extra triples to the graph.  Called only when the object's
:attr:`extra_data` is not :obj:`None`.

Example::

    from rdflib.namespace import SKOS
    from rdflib import Literal

    def my_serializer(graph, subject, obj):
        if isinstance(obj.extra_data, dict):
            for notation in obj.extra_data.get("notation", []):
                graph.add((subject, SKOS.notation, Literal(notation)))

    result = rdf_dumper(provider, extra_data_serializer=my_serializer)
"""

SKOS_THES = Namespace("http://purl.org/iso25964/skos-thes#")
log = logging.getLogger(__name__)


def rdf_dumper(provider, extra_data_serializer: RdfSerializer = None):
    """
    Dump a provider to a format that can be passed to a
    :class:`skosprovider.providers.RDFProvider`.

    :param skosprovider.providers.VocabularyProvider provider: The provider
        that wil be turned into an :class:`rdflib.graph.Graph`.

    :param extra_data_serializer: Optional :data:`RdfSerializer` callable that
        receives ``(graph, subject, skos_object)`` and adds extra triples for
        objects that carry :attr:`~skosprovider.skos.Concept.extra_data`.

    :rtype: :class:`rdflib.graph.Graph`
    """
    return _rdf_dumper(provider, None, extra_data_serializer)


def rdf_c_dumper(provider, c, extra_data_serializer: RdfSerializer = None):
    """
    Dump one concept or collection from a provider to a format that can be passed to a
    :class:`skosprovider.providers.RDFProvider`.

    :param skosprovider.providers.VocabularyProvider provider: The provider
        that wil be turned into an :class:`rdflib.graph.Graph`.

    :param String c: identifier

    :param extra_data_serializer: Optional :data:`RdfSerializer` callable.
        See :func:`rdf_dumper`.

    :rtype: :class:`rdflib.graph.Graph`
    """
    return _rdf_dumper(provider, [c], extra_data_serializer)


def _rdf_dumper(provider, id_list=None, extra_data_serializer: RdfSerializer = None):
    """
    Dump a provider to a format that can be passed to a
    :class:`skosprovider.providers.RDFProvider`.

    :param skosprovider.providers.VocabularyProvider provider: The provider
        that wil be turned into an :class:`rdflib.graph.Graph`.

    :param List id_list: List of id's of the data to dump.

    :param extra_data_serializer: Optional :data:`RdfSerializer` callable.
        See :func:`rdf_dumper`.

    :rtype: :class:`rdflib.graph.Graph`
    """
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
        extra_data_serializer(graph, conceptscheme, provider.concept_scheme)
    # Add triples using store's add method.
    if not id_list:
        id_list = [x["id"] for x in provider.get_all()]
        for c in provider.get_top_concepts():
            graph.add((conceptscheme, SKOS.hasTopConcept, URIRef(c["uri"])))
    for id in id_list:
        _add_c(graph, provider, id, extra_data_serializer)

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
        extra_data_serializer(graph, conceptscheme, provider.concept_scheme)
    for c in provider.get_top_concepts():
        graph.add((conceptscheme, SKOS.hasTopConcept, URIRef(c["uri"])))

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


def _add_c(graph, provider, id, extra_data_serializer: RdfSerializer = None):
    """
    Adds a concept or collection to the graph.

    :param rdflib.graph.Graph graph: The graph to add statements to.
    :param skosprovider.providers.VocabularyProvider provider: Provider
    :param c: The id of a concept or collection.
    :param extra_data_serializer: Optional :data:`RdfSerializer` callable.
    """

    c = provider.get_by_id(id)
    subject = URIRef(c.uri)
    _add_in_dataset(graph, subject, provider)
    if c.id != c.uri:
        graph.add((subject, DCTERMS.identifier, Literal(c.id)))
    conceptscheme = URIRef(provider.concept_scheme.uri)
    graph.add((subject, SKOS.inScheme, conceptscheme))
    _add_labels(graph, c, subject)
    _add_notes(graph, c, subject)
    _add_sources(graph, c, subject)
    if extra_data_serializer is not None and c.extra_data is not None:
        extra_data_serializer(graph, subject, c)
    if isinstance(c, Concept):
        graph.add((subject, RDF.type, SKOS.Concept))
        for b in c.broader:
            broader = provider.get_by_id(b)
            if broader:
                graph.add((subject, SKOS.broader, URIRef(broader.uri)))
        for n in c.narrower:
            narrower = provider.get_by_id(n)
            if narrower:
                graph.add((subject, SKOS.narrower, URIRef(narrower.uri)))
        for r in c.related:
            related = provider.get_by_id(r)
            if related:
                graph.add((subject, SKOS.related, URIRef(related.uri)))
        for s in c.subordinate_arrays:
            subordinate_array = provider.get_by_id(s)
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
                        for m in members:
                            member = provider.get_by_id(m)
                            if member.type == "concept":
                                graph.add((so, SKOS.narrower, URIRef(member.uri)))
                                graph.add((URIRef(member.uri), SKOS.broader, so))
                            elif member.type == "collection":
                                _add_coll_members_to_superordinate(so, member.members)

                    _add_coll_members_to_superordinate(
                        subject, subordinate_array.members
                    )
        for coll in c.member_of:
            collection = provider.get_by_id(coll)
            if collection:
                graph.add((URIRef(collection.uri), SKOS.member, subject))
                graph.add((URIRef(collection.uri), RDF.type, SKOS.Collection))
                graph.add((URIRef(collection.uri), SKOS.inScheme, conceptscheme))
                graph.add(
                    (URIRef(collection.uri), DCTERMS.identifier, Literal(collection.id))
                )

                def _add_coll_superordinates_as_broader(member, collection):
                    """
                    Recursively create broader relations between
                    a collection member and the superordinate concepts
                    """
                    if collection.infer_concept_relations:
                        for so in collection.superordinates:
                            superordinate = provider.get_by_id(so)
                            graph.add(
                                (
                                    URIRef(member.uri),
                                    SKOS.broader,
                                    URIRef(superordinate.uri),
                                )
                            )
                        for pc in collection.member_of:
                            parent_collection = provider.get_by_id(pc)
                            _add_coll_superordinates_as_broader(
                                member, parent_collection
                            )

                _add_coll_superordinates_as_broader(c, collection)
        for k in c.matches.keys():
            for uri in c.matches[k]:
                graph.add((subject, URIRef(SKOS[k + "Match"]), URIRef(uri)))
    elif isinstance(c, Collection):
        graph.add((subject, RDF.type, SKOS.Collection))
        for m in c.members:
            member = provider.get_by_id(m)
            if member:
                graph.add((subject, SKOS.member, URIRef(member.uri)))
        for s in c.superordinates:
            superordinate = provider.get_by_id(s)
            if superordinate:
                graph.add((subject, SKOS_THES.superOrdinate, URIRef(superordinate.uri)))


def _add_labels(graph, c, subject):
    for l in c.labels:
        labeltype = (
            l.type
            if l.type in ["prefLabel", "altLabel", "hiddenLabel"]
            else "hiddenLabel"
        )
        predicate = URIRef(SKOS[labeltype])
        lang = extract_language(l.language)
        graph.add((subject, predicate, Literal(l.label, lang=lang)))


def _add_notes(graph, c, subject):
    for n in c.notes:
        predicate = URIRef(SKOS[n.type])
        lang = extract_language(n.language)
        if n.markup is None:
            graph.add((subject, predicate, Literal(n.note, lang=lang)))
        else:
            html = add_lang_to_html(n.note, lang)
            graph.add((subject, predicate, Literal(html, datatype=RDF.HTML)))


def _add_sources(graph, c, subject):
    """
    Add sources to the RDF graph.

    :param rdflib.graph.Graph graph: An RDF Graph.
    :param c: A :class:`skosprovider.skos.ConceptScheme`,
        :class:`skosprovider.skos.Concept` or :class:`skosprovider.skos.Collection`
    :param subject: The RDF subject to add the sources to.
    """
    for s in c.sources:
        source = BNode()
        graph.add((source, RDF.type, DCTERMS.BibliographicResource))
        if s.markup is None:
            graph.add((source, DCTERMS.bibliographicCitation, Literal(s.citation)))
        else:
            graph.add(
                (
                    source,
                    DCTERMS.bibliographicCitation,
                    Literal(s.citation, datatype=RDF.HTML),
                )
            )
        graph.add((subject, DCTERMS.source, source))


def _add_languages(graph, c, subject):
    """
    Add languages to the RDF graph.

    :param rdflib.graph.Graph graph: An RDF Graph.
    :param c: A :class:`skosprovider.skos.ConceptScheme`.
    :param subject: The RDF subject to add the sources to.
    """
    for l in c.languages:
        lang = extract_language(l)
        graph.add((subject, DCTERMS.language, Literal(l)))


def text_(s, encoding="latin-1", errors="strict"):
    """If ``s`` is an instance of ``bytes``, return
    ``s.decode(encoding, errors)``, otherwise return ``s``"""
    if isinstance(s, bytes):
        return s.decode(encoding, errors)
    return s
