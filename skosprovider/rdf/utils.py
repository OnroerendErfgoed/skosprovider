"""
This module contains utility functions for dealing with skos providers.
"""

from collections.abc import Iterable
from collections.abc import Iterator

from rdflib import Graph
from rdflib import Literal
from rdflib.namespace import DCTERMS
from rdflib.namespace import RDF
from rdflib.namespace import SKOS
from rdflib.namespace import VOID
from rdflib.term import BNode
from rdflib.term import Node
from rdflib.term import URIRef
from skosprovider.exceptions import NotFoundException
from skosprovider.providers import VocabularyProvider
from skosprovider.rdf.providers import SKOS_THES
from skosprovider.skos import Collection
from skosprovider.skos import Concept
from skosprovider.skos import ConceptScheme
from skosprovider.utils import add_lang_to_html
from skosprovider.utils import extract_language


def rdf_dumper(provider: VocabularyProvider) -> Graph:
    """
    Dump a provider to a format that can be passed to a
    :class:`skosprovider.rdf.providers.RDFProvider`.

    :param skosprovider.providers.VocabularyProvider provider: The provider
        that wil be turned into an :class:`rdflib.graph.Graph`.

    :rtype: :class:`rdflib.graph.Graph`
    """
    graph = rdf_conceptscheme_dumper(provider)
    for concept_or_collection in provider.get_all():
        _add_concept_or_collection(graph, provider, concept_or_collection["id"])
    return graph


def rdf_concept_or_collection_dumper(
    provider: VocabularyProvider, id_: str | int
) -> Graph:
    """
    Dump one concept or collection from a provider to a format that can be passed to a
    :class:`skosprovider.rdf.providers.RDFProvider`.

    :param skosprovider.providers.VocabularyProvider provider: The provider
        that contains the concept or collection.
    :param id_: The id of the concept or collection to dump.

    :raises skosprovider.exceptions.NotFoundException: If the provider
        has no concept or collection with this id.
    :rtype: :class:`rdflib.graph.Graph`
    """
    graph = _create_concept_scheme_graph(provider)
    _add_concept_or_collection(graph, provider, id_)
    return graph


def rdf_conceptscheme_dumper(provider: VocabularyProvider) -> Graph:
    """
    Dump all information of the conceptscheme of a provider to a format that can be passed to a
    :class:`skosprovider.rdf.providers.RDFProvider`.

    :param skosprovider.providers.VocabularyProvider provider: The provider
        that wil be turned into an :class:`rdflib.graph.Graph`.

    :rtype: :class:`rdflib.graph.Graph`
    """
    graph = _create_concept_scheme_graph(provider)
    concept_scheme = URIRef(provider.concept_scheme.uri)
    for top_concept in provider.get_top_concepts():
        graph.add((concept_scheme, SKOS.hasTopConcept, URIRef(top_concept["uri"])))
    return graph


def _create_concept_scheme_graph(provider: VocabularyProvider) -> Graph:
    """
    Create a graph with the conceptscheme of a provider, without its top concepts.
    """
    graph = Graph()
    graph.namespace_manager.bind("skos", SKOS)
    graph.namespace_manager.bind("dcterms", DCTERMS)
    graph.namespace_manager.bind("skos-thes", SKOS_THES)
    graph.namespace_manager.bind("void", VOID)
    concept_scheme = provider.concept_scheme
    subject = URIRef(concept_scheme.uri)
    _add_in_dataset(graph, subject, provider)
    graph.add((subject, RDF.type, SKOS.ConceptScheme))
    graph.add((subject, DCTERMS.identifier, Literal(provider.metadata["id"])))
    _add_labels(graph, concept_scheme, subject)
    _add_notes(graph, concept_scheme, subject)
    _add_sources(graph, concept_scheme, subject)
    _add_languages(graph, concept_scheme, subject)
    return graph


def _add_in_dataset(
    graph: Graph, subject: URIRef, provider: VocabularyProvider
) -> None:
    """
    Checks if the provider says something about a dataset and if so adds
    void.inDataset statements.

    :param rdflib.graph.Graph graph: The graph to add statements to.
    :param rdflib.term.URIRef subject: The subject to add an inDataset statement to.
    :param skosprovider.providers.VocabularyProvider provider:
    """
    dataset_uri = provider.get_metadata().get("dataset", {}).get("uri")
    if dataset_uri:
        graph.add((subject, VOID.inDataset, URIRef(dataset_uri)))


def _get_by_ids(
    provider: VocabularyProvider, ids: Iterable[str | int]
) -> Iterator[Concept | Collection]:
    """
    Get the concepts and collections for some ids, skipping unknown ids.
    """
    for id_ in ids:
        concept_or_collection = provider.get_by_id(id_)
        if concept_or_collection:
            yield concept_or_collection


def _get_collections_by_ids(
    provider: VocabularyProvider, ids: Iterable[str | int]
) -> Iterator[Collection]:
    """
    Get the collections for some ids, skipping unknown ids and concepts.
    """
    for concept_or_collection in _get_by_ids(provider, ids):
        if isinstance(concept_or_collection, Collection):
            yield concept_or_collection


def _add_relations(
    graph: Graph,
    provider: VocabularyProvider,
    subject: URIRef,
    predicate: URIRef,
    ids: Iterable[str | int],
) -> None:
    """
    Add a relation from the subject to every known concept or collection in ids.
    """
    for related in _get_by_ids(provider, ids):
        graph.add((subject, predicate, URIRef(related.uri)))


def _add_concept_or_collection(
    graph: Graph, provider: VocabularyProvider, id_: str | int
) -> None:
    """
    Adds a concept or collection to the graph.

    :param rdflib.graph.Graph graph: The graph to add statements to.
    :param skosprovider.providers.VocabularyProvider provider: Provider
    :param id_: The id of a concept or collection.
    """
    concept_or_collection = provider.get_by_id(id_)
    if not concept_or_collection:
        raise NotFoundException(f"No concept or collection found with id {id_}.")
    subject = URIRef(concept_or_collection.uri)
    _add_in_dataset(graph, subject, provider)
    if concept_or_collection.id != concept_or_collection.uri:
        graph.add((subject, DCTERMS.identifier, Literal(concept_or_collection.id)))
    concept_scheme = URIRef(provider.concept_scheme.uri)
    graph.add((subject, SKOS.inScheme, concept_scheme))
    _add_labels(graph, concept_or_collection, subject)
    _add_notes(graph, concept_or_collection, subject)
    _add_sources(graph, concept_or_collection, subject)
    if isinstance(concept_or_collection, Concept):
        concept = concept_or_collection
        graph.add((subject, RDF.type, SKOS.Concept))
        _add_relations(graph, provider, subject, SKOS.broader, concept.broader)
        _add_relations(graph, provider, subject, SKOS.narrower, concept.narrower)
        _add_relations(graph, provider, subject, SKOS.related, concept.related)
        for subordinate_array in _get_collections_by_ids(
            provider, concept.subordinate_arrays
        ):
            graph.add(
                (subject, SKOS_THES.subordinateArray, URIRef(subordinate_array.uri))
            )
            if subordinate_array.infer_concept_relations:
                _add_members_as_narrower(
                    graph, provider, subject, subordinate_array.members
                )
        for collection in _get_collections_by_ids(provider, concept.member_of):
            collection_uri = URIRef(collection.uri)
            graph.add((collection_uri, SKOS.member, subject))
            graph.add((collection_uri, RDF.type, SKOS.Collection))
            graph.add((collection_uri, SKOS.inScheme, concept_scheme))
            graph.add((collection_uri, DCTERMS.identifier, Literal(collection.id)))
            _add_superordinates_as_broader(graph, provider, subject, collection)
        for match_type, uris in concept.matches.items():
            predicate = URIRef(SKOS[match_type + "Match"])
            for uri in uris:
                graph.add((subject, predicate, URIRef(uri)))
    elif isinstance(concept_or_collection, Collection):
        collection = concept_or_collection
        graph.add((subject, RDF.type, SKOS.Collection))
        _add_relations(graph, provider, subject, SKOS.member, collection.members)
        _add_relations(
            graph, provider, subject, SKOS_THES.superOrdinate, collection.superordinates
        )


def _add_members_as_narrower(
    graph: Graph,
    provider: VocabularyProvider,
    superordinate: URIRef,
    member_ids: Iterable[str | int],
) -> None:
    """
    Recursively create broader/narrower relations between
    collection members and the superordinate concept.
    """
    for member in _get_by_ids(provider, member_ids):
        if isinstance(member, Concept):
            member_uri = URIRef(member.uri)
            graph.add((superordinate, SKOS.narrower, member_uri))
            graph.add((member_uri, SKOS.broader, superordinate))
        elif isinstance(member, Collection):
            _add_members_as_narrower(graph, provider, superordinate, member.members)


def _add_superordinates_as_broader(
    graph: Graph,
    provider: VocabularyProvider,
    member: URIRef,
    collection: Collection,
) -> None:
    """
    Recursively create broader relations between
    a collection member and the superordinate concepts.
    """
    if not collection.infer_concept_relations:
        return
    _add_relations(graph, provider, member, SKOS.broader, collection.superordinates)
    for parent_collection in _get_collections_by_ids(provider, collection.member_of):
        _add_superordinates_as_broader(graph, provider, member, parent_collection)


def _add_labels(
    graph: Graph, item: ConceptScheme | Concept | Collection, subject: Node
) -> None:
    for label in item.labels:
        label_type = (
            label.type
            if label.type in ("prefLabel", "altLabel", "hiddenLabel")
            else "hiddenLabel"
        )
        language = extract_language(label.language)
        graph.add((subject, SKOS[label_type], Literal(label.label, lang=language)))


def _add_notes(
    graph: Graph, item: ConceptScheme | Concept | Collection, subject: Node
) -> None:
    for note in item.notes:
        predicate = SKOS[note.type]
        language = extract_language(note.language)
        if note.markup is None:
            literal = Literal(note.note, lang=language)
        else:
            # rdflib normalises HTML literals by reserializing them, which
            # drops optional tags such as </p>. Keep our text as is.
            literal = Literal(
                add_lang_to_html(note.note, language),
                datatype=RDF.HTML,
                normalize=False,
            )
        graph.add((subject, predicate, literal))


def _add_sources(
    graph: Graph, item: ConceptScheme | Concept | Collection, subject: Node
) -> None:
    """
    Add sources to the RDF graph.

    :param rdflib.graph.Graph graph: An RDF Graph.
    :param item: A :class:`skosprovider.skos.ConceptScheme`,
        :class:`skosprovider.skos.Concept` or :class:`skosprovider.skos.Collection`
    :param subject: The RDF subject to add the sources to.
    """
    for source in item.sources:
        source_node = BNode()
        graph.add((source_node, RDF.type, DCTERMS.BibliographicResource))
        if source.markup is None:
            citation = Literal(source.citation)
        else:
            citation = Literal(source.citation, datatype=RDF.HTML, normalize=False)
        graph.add((source_node, DCTERMS.bibliographicCitation, citation))
        graph.add((subject, DCTERMS.source, source_node))


def _add_languages(graph: Graph, concept_scheme: ConceptScheme, subject: Node) -> None:
    """
    Add languages to the RDF graph.

    :param rdflib.graph.Graph graph: An RDF Graph.
    :param concept_scheme: A :class:`skosprovider.skos.ConceptScheme`.
    :param subject: The RDF subject to add the languages to.
    """
    for language in concept_scheme.languages:
        graph.add((subject, DCTERMS.language, Literal(language)))
