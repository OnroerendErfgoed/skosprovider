"""
This module contains an RDFProvider, an implementation of the
:class:`skosprovider.providers.VocabularyProvider` interface that uses a
:class:`rdflib.graph.Graph` as input.
"""

import logging
import re

import rdflib
from langcodes import tag_is_valid
from rdflib.namespace import DC
from rdflib.namespace import DCTERMS
from rdflib.namespace import RDF
from rdflib.namespace import SKOS
from rdflib.term import URIRef
from skosprovider.providers import MemoryProvider
from skosprovider.skos import Collection
from skosprovider.skos import Concept
from skosprovider.skos import ConceptScheme
from skosprovider.skos import Label
from skosprovider.skos import Note
from skosprovider.skos import Source
from skosprovider.uri import DefaultConceptSchemeUrnGenerator

log = logging.getLogger(__name__)

SKOS_THES = rdflib.Namespace("http://purl.org/iso25964/skos-thes#")


class RDFProvider(MemoryProvider):
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

    def __init__(self, metadata, graph, **kwargs):
        self.graph = graph
        self.check_in_scheme = False
        if "concept_scheme" not in kwargs:
            kwargs["concept_scheme"] = self._cs_from_graph(metadata, **kwargs)
        else:
            self.check_in_scheme = True
        super().__init__(metadata, [], **kwargs)
        self.list = self._from_graph()

    def _cs_from_graph(self, metadata, **kwargs):
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
            )
            cslist.append(cs)
        if len(cslist) == 0:
            return ConceptScheme(
                uri=DefaultConceptSchemeUrnGenerator().generate(id=metadata.get("id"))
            )
        elif len(cslist) == 1:
            return cslist[0]
        else:
            if "concept_scheme_uri" not in kwargs:
                raise RuntimeError(
                    "This RDF file contains more than one ConceptScheme. \
                    Please specify one. The following schemes were found: \
                    %s" % (", ".join([str(cs.uri) for cs in cslist]))
                )
            else:
                self.check_in_scheme = True
                csuri = kwargs["concept_scheme_uri"]
                filteredcslist = [cs for cs in cslist if cs.uri == csuri]
                if len(filteredcslist) == 0:
                    raise RuntimeError(
                        "This RDF file contains more than one ConceptScheme. \
                        You specified an unexisting one. The following schemes \
                        were found: %s" % (", ".join([str(cs.uri) for cs in cslist]))
                    )
                else:
                    return filteredcslist[0]

    def _from_graph(self):
        clist = []
        for sub, pred, obj in self.graph.triples((None, RDF.type, SKOS.Concept)):
            if (
                self.check_in_scheme
                and self._get_in_scheme(sub) != self.concept_scheme.uri
            ):
                continue
            uri = self.to_text(sub)
            matches = {}
            for k in Concept.matchtypes:
                matches[k] = self._create_from_subject_predicate(
                    sub, URIRef(SKOS[k + "Match"])
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
            )
            clist.append(con)

        for sub, pred, obj in self.graph.triples((None, RDF.type, SKOS.Collection)):
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
            )
            clist.append(col)
        self._fill_member_of(clist)
        self._set_infer_concept_relations(clist)
        return clist

    def _get_in_scheme(self, subject):
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

    def _fill_member_of(self, clist):
        collections = list({c for c in clist if isinstance(c, Collection)})
        for col in collections:
            for c in clist:
                if c.id in col.members:
                    c.member_of.append(col.id)
        return

    def _set_infer_concept_relations(self, clist):
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
                members = list({c for c in clist if c.id in collection.members})
                broader = []
                for m in members:
                    if m.type == "concept":
                        broader.extend(m.broader)
                    elif m.type == "collection":
                        broader.extend(_collect_broader(m, clist))
                return broader

            broader = _collect_broader(col, clist)
            col.infer_concept_relations = (
                len(set(broader).intersection(col.superordinates)) > 0
            )

    def _create_from_subject_typelist(self, subject, typelist):
        list = []
        for p in typelist:
            term = SKOS.__getitem__(p)
            list.extend(self._create_from_subject_predicate(subject, term))
        return list

    def _get_id_for_subject(self, subject, uri):
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

    def _create_from_subject_predicate(self, subject, predicate):
        list = []
        for s, p, o in self.graph.triples((subject, predicate, None)):
            type = predicate.split("#")[-1]
            if Label.is_valid_type(type):
                o = self._create_label(o, type)
            elif Note.is_valid_type(type):
                o = self._create_note(o, type)
            else:
                o = self._get_id_for_subject(o, self.to_text(o))
            list.append(o)
        return list

    def _create_label(self, literal, type):
        if not Label.is_valid_type(type):
            raise ValueError("Type of Label is not valid.")
        return Label(
            self.to_text(literal), type, self._get_language_from_literal(literal)
        )

    def _read_markupped_literal(self, literal):
        if literal.datatype == RDF.HTML:
            if literal.value is None:
                # Since rdflib 7, malformed HTML makes the literal ill-typed
                # and leaves it without a value. Keep the raw text instead.
                return self._read_ill_typed_html(str(literal))
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

    def _read_ill_typed_html(self, text):
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
                lang = self._scrub_language(lang_attr.group(1) or lang_attr.group(2))
                start = first_tag.start(1) + lang_attr.start()
                end = first_tag.start(1) + lang_attr.end()
                return (text[:start] + text[end:], lang, "HTML")
        return (text, "und", "HTML")

    def _create_note(self, literal, type):
        if not Note.is_valid_type(type):
            raise ValueError("Type of Note is not valid.")
        markup_literal = self._read_markupped_literal(literal)
        return Note(
            self.to_text(markup_literal[0]), type, markup_literal[1], markup_literal[2]
        )

    def _create_sources(self, subject):
        """
        Create the sources for this subject.

        :param subject: Subject to get the sources for.
        :returns: A :class:`list` of :class:`skosprovider.skos.Source` objects.
        """
        ret = []
        for s, p, o in self.graph.triples((subject, DCTERMS.source, None)):
            for si, pi, oi in self.graph.triples(
                (o, DCTERMS.bibliographicCitation, None)
            ):
                ret.append(
                    Source(
                        self.to_text(oi), "HTML" if oi.datatype == RDF.HTML else None
                    )
                )
        return ret

    def _create_languages(self, subject):
        """
        Create the languages for this subject.

        :param subject: Subject to get the sources for.
        :returns: A :class:`list` of IANA language tags.
        """
        ret = set()
        for s, p, o in self.graph.triples((subject, DCTERMS.language, None)):
            ret.add(self.to_text(self._scrub_language(o)))
        for s, p, o in self.graph.triples((subject, DC.language, None)):
            ret.add(self.to_text(self._scrub_language(o)))
        return ret

    def _scrub_language(self, language):
        if tag_is_valid(language):
            return language
        else:
            log.warning(
                'Encountered an invalid language %s. Falling back to "und".' % language
            )
            return "und"

    def _scrub_label_types(self):
        valid_label_types = Label.valid_types[:]
        if "sortLabel" in valid_label_types:
            valid_label_types.remove("sortLabel")
        return valid_label_types

    def _get_language_from_literal(self, data):
        if not hasattr(data, "language") or data.language is None:
            return None
        return self.to_text(self._scrub_language(data.language))

    def to_text(self, data):
        """
        data of binary type or literal type that needs to be converted to text.
        :param data
        :return: text representation of the data
        """
        return str(data)
