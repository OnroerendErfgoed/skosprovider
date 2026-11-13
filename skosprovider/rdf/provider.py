"""
This module contains an RDFProvider, an implementation of the
:class:`skosprovider.provider.VocabularyProvider` interface that uses a
:class:`rdflib.graph.Graph` as input.
"""

import logging
import re
from collections.abc import Callable
from functools import partial
from typing import Any

import rdflib
from langcodes import tag_is_valid
from rdflib import Graph
from rdflib.namespace import DC
from rdflib.namespace import DCTERMS
from rdflib.namespace import RDF
from rdflib.namespace import SKOS
from rdflib.paths import AlternativePath
from rdflib.term import Literal
from rdflib.term import Node
from rdflib.term import URIRef

from skosprovider.exceptions import ConceptSchemeException
from skosprovider.exceptions import InvalidDataException
from skosprovider.extra_data import exception_context
from skosprovider.extra_data import ignore
from skosprovider.extra_data import load_extra_data
from skosprovider.provider import MemoryProvider
from skosprovider.skos import Collection
from skosprovider.skos import Concept
from skosprovider.skos import ConceptScheme
from skosprovider.skos import Label
from skosprovider.skos import Note
from skosprovider.skos import Source
from skosprovider.uri import DefaultConceptSchemeUrnGenerator

log = logging.getLogger(__name__)

SKOS_THES = rdflib.Namespace("http://purl.org/iso25964/skos-thes#")
SKOSXL = rdflib.Namespace("http://www.w3.org/2008/05/skos-xl#")

RdfExtraDataLoader = Callable[[Graph, Node], Graph | None]


class RDFProvider(MemoryProvider):
    """
    A simple vocabulary provider that use an :class:`rdflib.graph.Graph`
    as input. The provider expects a RDF graph with elements that represent
    the SKOS concepts and collections.

    Please be aware that this provider needs to load the entire graph in memory.

    When a concept scheme is passed or picked with `concept_scheme_uri`,
    `check_in_scheme` is set and the provider only takes concepts and
    collections into account that are explicitly linked to that concept scheme.
    """

    def __init__(
        self,
        metadata: dict[str, Any],
        graph: Graph,
        *,
        extra_data_loader: RdfExtraDataLoader = ignore,
        **kwargs: Any,
    ) -> None:
        """
        :param extra_data_loader: A callable that receives the graph and the
            node of a single concept scheme, concept or collection, or of a
            source, SKOS-XL label or note with a uri, and returns a
            :class:`rdflib.Graph` or `None`. A source, label or note that is a
            blank node gets no extra_data. See :mod:`skosprovider.rdf.extra_data`
            for the available loaders. Defaults to
            :func:`~skosprovider.extra_data.ignore`. A concept scheme passed as
            `concept_scheme` keeps its own extra_data.
        """
        self.extra_data_loader = extra_data_loader
        self.check_in_scheme = False
        if "concept_scheme" not in kwargs:
            kwargs["concept_scheme"] = self._concept_scheme_from_graph(
                graph, metadata, kwargs.get("concept_scheme_uri")
            )
        else:
            self.check_in_scheme = True
        super().__init__(metadata, [], **kwargs)
        self.list = self._from_graph(graph)

    def _concept_scheme_from_graph(
        self, graph: Graph, metadata: dict[str, Any], concept_scheme_uri: str | None
    ) -> ConceptScheme:
        """
        Pick the concept scheme of the provider from the graph.

        Only the picked concept scheme is created, so the extra_data loader
        is not called for the others.
        """
        subjects = list(graph.subjects(RDF.type, SKOS.ConceptScheme))
        found_uris = ", ".join(self.to_text(subject) for subject in subjects)
        if concept_scheme_uri is not None:
            for subject in subjects:
                if self.to_text(subject) == concept_scheme_uri:
                    self.check_in_scheme = True
                    return self._create_concept_scheme(graph, subject)
            raise ConceptSchemeException(
                "This RDF file does not contain the ConceptScheme "
                f"{concept_scheme_uri}. "
                f"The following schemes were found: {found_uris or 'none'}"
            )
        if not subjects:
            return ConceptScheme(
                uri=DefaultConceptSchemeUrnGenerator().generate(id=metadata.get("id"))
            )
        if len(subjects) > 1:
            raise ConceptSchemeException(
                "This RDF file contains more than one ConceptScheme. "
                "Please specify one. "
                f"The following schemes were found: {found_uris}"
            )
        return self._create_concept_scheme(graph, subjects[0])

    def _create_concept_scheme(self, graph: Graph, subject: Node) -> ConceptScheme:
        uri = self.to_text(subject)
        with exception_context(f"concept scheme {uri!r}"):
            return ConceptScheme(
                uri=uri,
                labels=self._create_labels(graph, subject),
                notes=self._create_notes(graph, subject),
                sources=self._create_sources(graph, subject),
                languages=self._create_languages(graph, subject),
                extra_data=self._load_extra_data(graph, subject),
            )

    def _load_extra_data(self, graph: Graph, subject: Node) -> Graph | None:
        return load_extra_data(partial(self.extra_data_loader, graph), subject)

    def _from_graph(self, graph: Graph) -> list[Concept | Collection]:
        concepts_and_collections: list[Concept | Collection] = [
            self._create_concept(graph, subject)
            for subject in self._subjects_of_type(graph, SKOS.Concept)
        ]
        concepts_and_collections.extend(
            self._create_collection(graph, subject)
            for subject in self._subjects_of_type(graph, SKOS.Collection)
        )
        by_id = {
            concept_or_collection.id: concept_or_collection
            for concept_or_collection in concepts_and_collections
        }
        collections = [
            concept_or_collection
            for concept_or_collection in concepts_and_collections
            if isinstance(concept_or_collection, Collection)
        ]
        self._fill_member_of(collections, by_id)
        self._set_infer_concept_relations(collections, by_id)
        return concepts_and_collections

    def _subjects_of_type(self, graph: Graph, rdf_type: URIRef) -> list[Node]:
        """
        Get all subjects of a type, limited to the concept scheme of this
        provider if `check_in_scheme` is set.
        """
        return [
            subject
            for subject in graph.subjects(RDF.type, rdf_type)
            if not self.check_in_scheme
            or self._get_in_scheme(graph, subject) == self.concept_scheme.uri
        ]

    def _create_concept(self, graph: Graph, subject: Node) -> Concept:
        uri = self.to_text(subject)
        id_ = self._get_id_for_subject(graph, subject, uri)
        with exception_context(f"concept {id_!r}"):
            return Concept(
                id=id_,
                uri=uri,
                concept_scheme=self.concept_scheme,
                labels=self._create_labels(graph, subject),
                notes=self._create_notes(graph, subject),
                sources=self._create_sources(graph, subject),
                broader=self._create_from_subject_predicate(
                    graph, subject, SKOS.broader
                ),
                narrower=self._create_from_subject_predicate(
                    graph, subject, SKOS.narrower
                ),
                related=self._create_from_subject_predicate(
                    graph, subject, SKOS.related
                ),
                member_of=[],
                subordinate_arrays=self._create_from_subject_predicate(
                    graph, subject, SKOS_THES.subordinateArray
                ),
                matches={
                    match_type: self._create_from_subject_predicate(
                        graph, subject, URIRef(SKOS[match_type + "Match"])
                    )
                    for match_type in Concept.matchtypes
                },
                extra_data=self._load_extra_data(graph, subject),
            )

    def _create_collection(self, graph: Graph, subject: Node) -> Collection:
        uri = self.to_text(subject)
        id_ = self._get_id_for_subject(graph, subject, uri)
        with exception_context(f"collection {id_!r}"):
            return Collection(
                id=id_,
                uri=uri,
                concept_scheme=self.concept_scheme,
                labels=self._create_labels(graph, subject),
                notes=self._create_notes(graph, subject),
                sources=self._create_sources(graph, subject),
                members=self._create_from_subject_predicate(
                    graph, subject, SKOS.member
                ),
                member_of=[],
                superordinates=self._create_from_subject_predicate(
                    graph, subject, SKOS_THES.superOrdinate
                ),
                extra_data=self._load_extra_data(graph, subject),
            )

    def _get_in_scheme(self, graph: Graph, subject: Node) -> str | None:
        """
        Determine if a subject is part of a scheme.

        :param graph: Graph to look up the scheme in.
        :param subject: Subject to get the scheme for.
        :returns: A URI for the scheme a subject is part of or None if
            it's not part of a scheme.
        """
        scheme = graph.value(subject, SKOS.inScheme) or graph.value(
            subject, SKOS.topConceptOf
        )
        return self.to_text(scheme) if scheme else None

    @staticmethod
    def _fill_member_of(
        collections: list[Collection],
        by_id: dict[str, Concept | Collection],
    ) -> None:
        for collection in collections:
            for member_id in dict.fromkeys(collection.members):
                member = by_id.get(member_id)
                if member:
                    member.member_of.append(collection.id)

    def _set_infer_concept_relations(
        self,
        collections: list[Collection],
        by_id: dict[str, Concept | Collection],
    ) -> None:
        for collection in collections:
            collection.infer_concept_relations = bool(
                collection.superordinates
                and self._collect_broader(collection, by_id).intersection(
                    collection.superordinates
                )
            )

    def _collect_broader(
        self,
        collection: Collection,
        by_id: dict[str, Concept | Collection],
        seen: set[str] | None = None,
    ) -> set[str]:
        """
        Collect all broader concepts of members of a collection or
        their (recursive) members.

        :param seen: The ids of the collections already visited, so cyclic
            members are only visited once.
        """
        seen = set() if seen is None else seen
        seen.add(collection.id)
        broader: set[str] = set()
        for member_id in collection.members:
            member = by_id.get(member_id)
            if isinstance(member, Concept):
                broader.update(member.broader)
            elif isinstance(member, Collection) and member.id not in seen:
                broader.update(self._collect_broader(member, by_id, seen))
        return broader

    def _create_labels(self, graph: Graph, subject: Node) -> list[Label]:
        """
        Create the labels of a subject, both plain SKOS labels and SKOS-XL
        labels.

        A plain label with the same text and language as a SKOS-XL label of the
        same type is skipped, since it is the same label written twice.
        """
        labels = []
        for type_ in self._scrub_label_types():
            xl_labels = [
                label
                for node in graph.objects(subject, SKOSXL[type_])
                if (label := self._create_xl_label(graph, node, type_))
            ]
            xl_texts = {(label.label, label.language) for label in xl_labels}
            for literal in graph.objects(subject, SKOS[type_]):
                label = self._create_label(literal, type_)
                if (label.label, label.language) not in xl_texts:
                    labels.append(label)
            labels.extend(xl_labels)
        return labels

    def _create_xl_label(self, graph: Graph, node: Node, type_: str) -> Label | None:
        """
        Create a label from a skosxl:Label node.

        A blank node becomes a plain label without a uri, so it gets no
        extra_data.

        :returns: A label, or `None` when the node has no skosxl:literalForm.
        """
        literal = graph.value(node, SKOSXL.literalForm)
        if literal is None:
            log.warning("Skipping a skosxl:Label without literalForm: %s", node)
            return None
        label = Label(
            self.to_text(literal),
            type_,
            self._get_language_from_literal(literal),
            uri=self.to_text(node) if isinstance(node, URIRef) else None,
            label_types=[
                self.to_text(label_type)
                for label_type in graph.objects(node, DCTERMS.type)
            ],
        )
        if label.is_xl():
            with exception_context(repr(label)):
                label.extra_data = self._load_extra_data(graph, node)
        return label

    def _create_notes(self, graph: Graph, subject: Node) -> list[Note]:
        """
        Create the notes of a subject.

        A note is either a literal or a node with the text under rdf:value.
        Only a note node with a uri can have extra_data.
        """
        notes = []
        for type_ in Note.valid_types:
            for object_ in graph.objects(subject, SKOS[type_]):
                if isinstance(object_, Literal):
                    notes.append(self._create_note(object_, type_))
                elif note := self._create_note_from_node(graph, object_, type_):
                    notes.append(note)
        return notes

    def _get_id_for_subject(self, graph: Graph, subject: Node, uri: str) -> str:
        identifier = graph.value(subject, DCTERMS.identifier, any=False)
        if identifier is None:
            identifier = graph.value(subject, DC.identifier, any=False)
        return uri if identifier is None else self.to_text(identifier)

    def _create_from_subject_predicate(
        self, graph: Graph, subject: Node, predicate: URIRef
    ) -> list[str]:
        """
        Get the ids of the concepts or collections a subject points to.
        """
        return [
            self._get_id_for_subject(graph, node, self.to_text(node))
            for node in graph.objects(subject, predicate)
        ]

    def _create_label(self, literal: Node, type_: str) -> Label:
        if not Label.is_valid_type(type_):
            raise InvalidDataException("Type of Label is not valid.")
        return Label(
            self.to_text(literal), type_, self._get_language_from_literal(literal)
        )

    def _read_markupped_literal(
        self, literal: Literal
    ) -> tuple[str | Literal, str | None, str | None]:
        """
        Read the text, language and markup of a literal.

        :returns: A tuple of text, language and markup.
        """
        if literal.datatype != RDF.HTML:
            return (literal, self._get_language_from_literal(literal), None)
        if literal.value is None:
            # Since rdflib 7, malformed HTML makes the literal ill-typed
            # and leaves it without a value. Keep the raw text instead.
            return self._read_ill_typed_html(str(literal))
        fragment = literal.value.cloneNode(True)
        first_child = fragment.firstChild
        if (
            first_child
            and first_child.attributes
            and "xml:lang" in first_child.attributes
        ):
            language = self._scrub_language(
                first_child.attributes.get("xml:lang").value
            )
            del first_child.attributes["xml:lang"]
        else:
            language = "und"
        html = "".join(child.toxml() for child in fragment.childNodes)
        return (html, language, "HTML")

    def _read_ill_typed_html(self, text: str) -> tuple[str, str, str]:
        """
        Read the language of a piece of HTML that could not be parsed.

        Without a DOM, a regex looks for an `xml:lang` attribute on the
        first tag, the same place :meth:`_read_markupped_literal` looks for
        it in the DOM. The attribute is removed, the rest of the HTML is
        kept as is.
        """
        first_tag = re.match(r"<[a-zA-Z][^\s>/]*([^>]*)>", text)
        if first_tag:
            lang_attr = re.search(
                r"""\s+xml:lang\s*=\s*(?:"([^"]*)"|'([^']*)')""",
                first_tag.group(1),
                re.IGNORECASE,
            )
            if lang_attr:
                language = self._scrub_language(
                    lang_attr.group(1) or lang_attr.group(2)
                )
                start = first_tag.start(1) + lang_attr.start()
                end = first_tag.start(1) + lang_attr.end()
                return (text[:start] + text[end:], language, "HTML")
        return (text, "und", "HTML")

    def _create_note(self, literal: Literal, type_: str) -> Note:
        if not Note.is_valid_type(type_):
            raise InvalidDataException("Type of Note is not valid.")
        text, language, markup = self._read_markupped_literal(literal)
        return Note(self.to_text(text), type_, language, markup)

    def _create_note_from_node(
        self, graph: Graph, node: Node, type_: str
    ) -> Note | None:
        """
        Create a note from a node with the text of the note under rdf:value.

        A blank node becomes a note without a uri, so it gets no extra_data.

        :returns: A note, or `None` when the node has no rdf:value.
        """
        literal = graph.value(node, RDF.value)
        if not isinstance(literal, Literal):
            log.warning("Skipping a note without rdf:value: %s", node)
            return None
        text, language, markup = self._read_markupped_literal(literal)
        note = Note(
            self.to_text(text),
            type_,
            language,
            markup,
            uri=self.to_text(node) if isinstance(node, URIRef) else None,
        )
        if note.is_object():
            with exception_context(repr(note)):
                note.extra_data = self._load_extra_data(graph, node)
        return note

    def _create_sources(self, graph: Graph, subject: Node) -> list[Source]:
        """
        Create the sources for this subject.

        Only a source with a uri gets extra_data.

        :param graph: Graph to look up the sources in.
        :param subject: Subject to get the sources for.
        :returns: A :class:`list` of :class:`skosprovider.skos.Source` objects.
        """
        sources = []
        for source_node in graph.objects(subject, DCTERMS.source):
            for citation in graph.objects(
                source_node,
                AlternativePath(DCTERMS.bibliographicCitation, RDF.value),
            ):
                source = Source(
                    self.to_text(citation),
                    "HTML" if citation.datatype == RDF.HTML else None,
                    uri=(
                        self.to_text(source_node)
                        if isinstance(source_node, URIRef)
                        else None
                    ),
                )
                if source.is_object():
                    with exception_context(repr(source)):
                        source.extra_data = self._load_extra_data(graph, source_node)
                sources.append(source)
        return sources

    def _create_languages(self, graph: Graph, subject: Node) -> set[str]:
        """
        Create the languages for this subject.

        :param graph: Graph to look up the languages in.
        :param subject: Subject to get the languages for.
        :returns: A :class:`set` of IANA language tags.
        """
        return {
            self._scrub_language(self.to_text(language))
            for language in graph.objects(
                subject, AlternativePath(DCTERMS.language, DC.language)
            )
        }

    @staticmethod
    def _scrub_language(language: str) -> str:
        if tag_is_valid(language):
            return language
        log.warning(
            'Encountered an invalid language %s. Falling back to "und".', language
        )
        return "und"

    @staticmethod
    def _scrub_label_types() -> list[str]:
        return [type_ for type_ in Label.valid_types if type_ != "sortLabel"]

    def _get_language_from_literal(self, literal: Any) -> str | None:
        language = getattr(literal, "language", None)
        if language is None:
            return None
        return self.to_text(self._scrub_language(language))

    def to_text(self, data: Any) -> str:
        """
        Convert data of binary type or literal type to text.

        :param data: The data to convert.
        :return: text representation of the data
        """
        return str(data)
