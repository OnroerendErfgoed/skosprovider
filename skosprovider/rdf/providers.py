"""
This module contains an RDFProvider, an implementation of the
:class:`skosprovider.providers.VocabularyProvider` interface that uses a
:class:`rdflib.graph.Graph` as input.
"""

import itertools
import logging

from typing import Any

import rdflib
from language_tags import tags
from rdflib.namespace import DC
from rdflib.namespace import DCTERMS
from rdflib.namespace import RDF
from rdflib.namespace import SKOS
from rdflib.namespace import VOID
from rdflib.term import Literal as RdfLiteral
from rdflib.term import URIRef

from skosprovider.providers import MemoryProvider
from skosprovider.skos import Collection
from skosprovider.skos import Concept
from skosprovider.skos import ConceptScheme
from skosprovider.skos import Label
from skosprovider.skos import Note
from skosprovider.skos import Source
from skosprovider.uri import DefaultConceptSchemeUrnGenerator
from skosprovider.uri import UriGenerator

log = logging.getLogger(__name__)

SKOS_THES = rdflib.Namespace("http://purl.org/iso25964/skos-thes#")


def _skos_term(name: str) -> URIRef:
    return URIRef("http://www.w3.org/2004/02/skos/core#" + name)


_KNOWN_CONCEPT_PREDICATES: frozenset = frozenset(
    [
        RDF.type,
        SKOS.inScheme,
        SKOS.topConceptOf,
        DCTERMS.identifier,
        DC.identifier,
        DCTERMS.source,
        SKOS.broader,
        SKOS.narrower,
        SKOS.related,
        SKOS_THES.subordinateArray,
        VOID.inDataset,
    ]
    + [_skos_term(t) for t in Label.valid_types]
    + [_skos_term(t) for t in Note.valid_types]
    + [_skos_term(k + "Match") for k in Concept.matchtypes]
)

_KNOWN_COLLECTION_PREDICATES: frozenset = frozenset(
    [
        RDF.type,
        SKOS.inScheme,
        DCTERMS.identifier,
        DC.identifier,
        DCTERMS.source,
        SKOS.member,
        SKOS_THES.superOrdinate,
        VOID.inDataset,
    ]
    + [_skos_term(t) for t in Label.valid_types]
    + [_skos_term(t) for t in Note.valid_types]
)

_KNOWN_CONCEPTSCHEME_PREDICATES: frozenset = frozenset(
    [
        RDF.type,
        DCTERMS.identifier,
        DC.identifier,
        DCTERMS.source,
        DCTERMS.language,
        DC.language,
        SKOS.hasTopConcept,
        VOID.inDataset,
    ]
    + [_skos_term(t) for t in Label.valid_types]
    + [_skos_term(t) for t in Note.valid_types]
)


class RDFProvider(MemoryProvider[rdflib.Graph]):
    """
    Should the provider only take concepts into account explicitly linked
    to the conceptscheme?
    """

    check_in_scheme = False

    """
    A simple vocabulary provider that use an :class:`rdflib.graph.Graph`
    as input. The provider expects a RDF graph with elements that represent
    the SKOS concepts and collections.

    Please be aware that this provider needs to load the entire graph in memory.
    """

    def __init__(
        self,
        metadata: dict,
        graph: rdflib.Graph,
        uri_generator: UriGenerator | None = None,
        concept_scheme: ConceptScheme | None = None,
        concept_scheme_uri: str | None = None,
        allowed_instance_scopes: list[str] | None = None,
        case_insensitive: bool = True,
    ) -> None:
        self.graph = graph
        self.check_in_scheme = False
        if concept_scheme is None:
            concept_scheme = self._cs_from_graph(metadata, concept_scheme_uri=concept_scheme_uri)
        else:
            self.check_in_scheme = True
        super().__init__(metadata, [], uri_generator=uri_generator, concept_scheme=concept_scheme, allowed_instance_scopes=allowed_instance_scopes, case_insensitive=case_insensitive)
        self.list = self._from_graph()

    def _cs_from_graph(self, metadata: dict, concept_scheme_uri: str | None = None) -> ConceptScheme:
        cslist = []
        for sub in self.graph.subjects(RDF.type, SKOS.ConceptScheme):
            uri = self.to_text(sub)
            cs = ConceptScheme(
                uri=uri,
                labels=self._create_from_subject_typelist(
                    sub, self._scrub_label_types()
                ),
                notes=self._create_from_subject_typelist(sub, Note.valid_types),
                sources=self._create_sources(sub),
                languages=self._create_languages(sub),
                extra_data=self._create_extra_data(
                    sub, _KNOWN_CONCEPTSCHEME_PREDICATES
                ),
            )
            cslist.append(cs)
        if len(cslist) == 0:
            return ConceptScheme(
                uri=DefaultConceptSchemeUrnGenerator().generate(concept_id=metadata.get("id"))
            )
        elif len(cslist) == 1:
            return cslist[0]
        else:
            if concept_scheme_uri is None:
                raise RuntimeError(
                    "This RDF file contains more than one ConceptScheme. \
                    Please specify one. The following schemes were found: \
                    %s"
                    % (", ".join([str(cs.uri) for cs in cslist]))
                )
            else:
                self.check_in_scheme = True
                csuri = concept_scheme_uri
                filteredcslist = [cs for cs in cslist if cs.uri == csuri]
                if len(filteredcslist) == 0:
                    raise RuntimeError(
                        "This RDF file contains more than one ConceptScheme. \
                        You specified an unexisting one. The following schemes \
                        were found: %s"
                        % (", ".join([str(cs.uri) for cs in cslist]))
                    )
                else:
                    return filteredcslist[0]

    def _from_graph(self) -> list[Concept | Collection]:
        clist = []
        for sub in self.graph.subjects(RDF.type, SKOS.Concept):
            if (
                self.check_in_scheme
                and self._get_in_scheme(sub) != self.concept_scheme.uri
            ):
                continue
            uri = self.to_text(sub)
            matches = {}
            for match_type in Concept.matchtypes:
                matches[match_type] = self._create_from_subject_predicate(
                    sub, URIRef(SKOS[match_type + "Match"])
                )
            con = Concept(
                id=self._get_id_for_subject(sub, uri),
                uri=uri,
                concept_scheme=self.concept_scheme,
                labels=self._create_from_subject_typelist(
                    sub, self._scrub_label_types()
                ),
                notes=self._create_from_subject_typelist(sub, Note.valid_types),
                sources=self._create_sources(sub),
                broader=self._create_from_subject_predicate(sub, SKOS.broader),
                narrower=self._create_from_subject_predicate(sub, SKOS.narrower),
                related=self._create_from_subject_predicate(sub, SKOS.related),
                member_of=[],
                subordinate_arrays=self._create_from_subject_predicate(
                    sub, SKOS_THES.subordinateArray
                ),
                matches=matches,
                extra_data=self._create_extra_data(sub, _KNOWN_CONCEPT_PREDICATES),
            )
            clist.append(con)

        for sub in self.graph.subjects(RDF.type, SKOS.Collection):
            if (
                self.check_in_scheme
                and self._get_in_scheme(sub) != self.concept_scheme.uri
            ):
                continue
            uri = self.to_text(sub)
            col = Collection(
                id=self._get_id_for_subject(sub, uri),
                uri=uri,
                concept_scheme=self.concept_scheme,
                labels=self._create_from_subject_typelist(
                    sub, self._scrub_label_types()
                ),
                notes=self._create_from_subject_typelist(sub, (Note.valid_types)),
                sources=self._create_sources(sub),
                members=self._create_from_subject_predicate(sub, SKOS.member),
                member_of=[],
                superordinates=self._create_from_subject_predicate(
                    sub, SKOS_THES.superOrdinate
                ),
                extra_data=self._create_extra_data(sub, _KNOWN_COLLECTION_PREDICATES),
            )
            clist.append(col)
        self._fill_member_of(clist)
        self._set_infer_concept_relations(clist)
        return clist

    def _get_in_scheme(self, subject: URIRef) -> str | None:
        """
        Determine if a subject is part of a scheme.

        :param subject: Subject to get the sources for.
        :returns: A URI for the scheme a subject is part of or None if
            it's not part of a scheme.
        """
        scheme = None
        scheme = self.graph.value(subject, SKOS.inScheme)
        if not scheme:
            scheme = self.graph.value(subject, SKOS.topConceptOf)
        return self.to_text(scheme) if scheme else None

    def _fill_member_of(self, clist: list[Concept | Collection]) -> None:
        collections = list(
            {skos_obj for skos_obj in clist if isinstance(skos_obj, Collection)}
        )
        for col in collections:
            for skos_obj in clist:
                if skos_obj.id in col.members:
                    skos_obj.member_of.append(col.id)
        return

    def _set_infer_concept_relations(self, clist: list[Concept | Collection]) -> None:
        collections = list({c for c in clist if isinstance(c, Collection)})
        for col in collections:
            if not col.superordinates:
                col.infer_concept_relations = False
                continue

            def _collect_broader(collection, clist):
                """
                Collect all broader concepts of members of a collection or
                their (recursive) members.
                """
                members = list(
                    {
                        skos_obj
                        for skos_obj in clist
                        if skos_obj.id in collection.members
                    }
                )
                broader = []
                for member in members:
                    if member.type == "concept":
                        broader.extend(member.broader)
                    elif member.type == "collection":
                        broader.extend(_collect_broader(member, clist))
                return broader

            broader = _collect_broader(col, clist)
            col.infer_concept_relations = (
                len(set(broader).intersection(col.superordinates)) > 0
            )

    def _create_extra_data(
        self, subject: URIRef, known_predicates: frozenset
    ) -> rdflib.Graph | None:
        """Return a Graph of triples for subject whose predicate is not in known_predicates."""
        g = rdflib.Graph()
        for triple in self.graph.triples((subject, None, None)):
            if triple[1] not in known_predicates:
                g.add(triple)
        return g if len(g) > 0 else None

    def _create_from_subject_typelist(
        self, subject: URIRef, typelist: list[str]
    ) -> list[Label | Note]:
        result = []
        for p in typelist:
            result.extend(self._create_from_subject_predicate(subject, SKOS[p]))
        return result

    def _get_id_for_subject(self, subject: URIRef, uri: str) -> str:
        if (subject, DCTERMS.identifier, None) in self.graph:
            return self.to_text(
                self.graph.value(
                    subject=subject, predicate=DCTERMS.identifier, any=False
                )
            )
        elif (subject, DC.identifier, None) in self.graph:
            return self.to_text(
                self.graph.value(subject=subject, predicate=DC.identifier, any=False)
            )
        else:
            return uri

    def _create_from_subject_predicate(self, subject: URIRef, predicate: URIRef) -> list[Label | Note | str]:
        items = []
        predicate_type = predicate.split("#")[-1]
        for rdf_obj in self.graph.objects(subject, predicate):
            if Label.is_valid_type(predicate_type):
                rdf_obj = self._create_label(rdf_obj, predicate_type)
            elif Note.is_valid_type(predicate_type):
                rdf_obj = self._create_note(rdf_obj, predicate_type)
            else:
                rdf_obj = self._get_id_for_subject(rdf_obj, self.to_text(rdf_obj))
            items.append(rdf_obj)
        return items

    def _create_label(self, literal: RdfLiteral, label_type: str) -> Label:
        if not Label.is_valid_type(label_type):
            raise ValueError("Type of Label is not valid.")
        return Label(
            self.to_text(literal), label_type, self._get_language_from_literal(literal)
        )

    def _read_markupped_literal(self, literal: RdfLiteral) -> tuple[str, str, str | None]:
        if literal.datatype == RDF.HTML:
            df = literal.value.cloneNode(True)
            if (
                df.firstChild
                and df.firstChild.attributes
                and "xml:lang" in df.firstChild.attributes.keys()
            ):
                lang = self._scrub_language(
                    df.firstChild.attributes.get("xml:lang").value
                )
                del df.firstChild.attributes["xml:lang"]
            else:
                lang = "und"
            return ("".join(child.toxml() for child in df.childNodes), lang, "HTML")
        else:
            return (literal, self._get_language_from_literal(literal), None)

    def _create_note(self, literal: RdfLiteral, note_type: str) -> Note:
        if not Note.is_valid_type(note_type):
            raise ValueError("Type of Note is not valid.")
        text, language, markup = self._read_markupped_literal(literal)
        return Note(self.to_text(text), note_type, language, markup)

    def _create_sources(self, subject: URIRef) -> list[Source]:
        """
        Create the sources for this subject.

        :param subject: Subject to get the sources for.
        :returns: A :class:`list` of :class:`skosprovider.skos.Source` objects.
        """
        ret = []
        for source in self.graph.objects(subject, DCTERMS.source):
            for citation in self.graph.objects(source, DCTERMS.bibliographicCitation):
                ret.append(
                    Source(
                        self.to_text(citation),
                        "HTML" if citation.datatype == RDF.HTML else None,
                    )
                )
        return ret

    def _create_languages(self, subject: URIRef) -> set[str]:
        """
        Create the languages for this subject.

        :param subject: Subject to get the sources for.
        :returns: A :class:`list` of IANA language tags.
        """
        ret = set()
        languages = itertools.chain(
            self.graph.objects(subject, DCTERMS.language),
            self.graph.objects(subject, DC.language),
        )
        for language in languages:
            ret.add(self.to_text(self._scrub_language(language)))
        return ret

    def _scrub_language(self, language: str | RdfLiteral) -> str:
        if tags.check(language):
            return language
        else:
            log.warning(
                'Encountered an invalid language %s. Falling back to "und".' % language
            )
            return "und"

    def _scrub_label_types(self) -> list[str]:
        valid_label_types = Label.valid_types[:]
        if "sortLabel" in valid_label_types:
            valid_label_types.remove("sortLabel")
        return valid_label_types

    def _get_language_from_literal(self, data: RdfLiteral) -> str | None:
        if not hasattr(data, "language") or data.language is None:
            return None
        return self.to_text(self._scrub_language(data.language))

    def to_text(self, data: Any) -> str:
        return str(data)
