"""
This module contains functions dealing with jsonld reading and writing.

.. versionadded:: 0.7.0
"""

import logging
from typing import Callable
from typing import Literal
from typing import TypeAlias

from skosprovider.providers import VocabularyProvider
from skosprovider.skos import Collection
from skosprovider.skos import Concept
from skosprovider.skos import ConceptScheme
from skosprovider.skos import SkosObject
from skosprovider.utils import add_lang_to_html
from skosprovider.utils import extract_language

log = logging.getLogger(__name__)

Serializer: TypeAlias = Callable[[dict, SkosObject], None] | None
"""A callable that receives the output :class:`dict` and a SKOS object, and
mutates the dict directly to add extra data.  Called only when the object's
:attr:`extra_data` is not :obj:`None`.

Example usage with an rdflib Graph as extra_data::

    import json
    from rdflib import Graph

    def my_serializer(doc, obj):
        if isinstance(obj.extra_data, Graph):
            doc.update(json.loads(obj.extra_data.serialize(format="json-ld")))

    result = jsonld_dumper(provider, extra_data_serializer=my_serializer)
"""

MINI_CONTEXT = {
    "@version": 1.1,
    "dct": "http://purl.org/dc/terms/",
    "skos": "http://www.w3.org/2004/02/skos/core#",
    "iso-thes": "http://purl.org/iso25964/skos-thes#",
    "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
    "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
    "void": "http://rdfs.org/ns/void#",
    "uri": "@id",
    "type": "@type",
    "id": "dct:identifier",
    "label": "rdfs:label",
    "concept": "skos:Concept",
    "collection": "skos:Collection",
}

CONTEXT = {
    "@version": 1.1,
    "dct": "http://purl.org/dc/terms/",
    "skos": "http://www.w3.org/2004/02/skos/core#",
    "skosxl": "http://www.w3.org/2008/05/skos-xl#",
    "iso-thes": "http://purl.org/iso25964/skos-thes#",
    "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
    "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
    "void": "http://rdfs.org/ns/void#",
    "uri": "@id",
    "type": "@type",
    "id": "dct:identifier",
    "label": "rdfs:label",
    "concept": "skos:Concept",
    "collection": "skos:Collection",
    "lbl": "@value",
    "nt": "@value",
    "ct": "@value",
    "HTML": "rdf:HTML",
    "concept_scheme": {"@id": "skos:inScheme", "@type": "@id"},
    "in_dataset": {"@id": "void:inDataset", "@type": "@id"},
    "top_concepts": {"@id": "skos:hasTopConcept", "@type": "@id"},
    "labels": "@nest",
    "labels_xl": "@nest",
    "notes": "@nest",
    "matches": "@nest",
    "sources": {"@id": "dct:source", "@container": "@set"},
    "citations": {"@id": "dct:bibliographicCitation", "@container": "@set"},
    "pref_labels": {"@nest": "labels", "@id": "skos:prefLabel", "@container": "@set"},
    "alt_labels": {"@nest": "labels", "@id": "skos:altLabel", "@container": "@set"},
    "hidden_labels": {
        "@nest": "labels",
        "@id": "skos:hiddenLabel",
        "@container": "@set",
    },
    "pref_labels_xl": {
        "@nest": "labels_xl",
        "@id": "skosxl:prefLabel",
        "@container": "@set",
    },
    "alt_labels_xl": {
        "@nest": "labels_xl",
        "@id": "skosxl:altLabel",
        "@container": "@set",
    },
    "hidden_labels_xl": {
        "@nest": "labels_xl",
        "@id": "skosxl:hiddenLabel",
        "@container": "@set",
    },
    "general_notes": {"@nest": "notes", "@id": "skos:note", "@container": "@set"},
    "scope_notes": {"@nest": "notes", "@id": "skos:scopeNote", "@container": "@set"},
    "definitions": {"@nest": "notes", "@id": "skos:definition", "@container": "@set"},
    "history_notes": {
        "@nest": "notes",
        "@id": "skos:historyNote",
        "@container": "@set",
    },
    "editorial_notes": {
        "@nest": "notes",
        "@id": "skos:editorialNote",
        "@container": "@set",
    },
    "change_notes": {"@nest": "notes", "@id": "skos:changeNote", "@container": "@set"},
    "examples": {"@nest": "notes", "@id": "skos:example", "@container": "@set"},
    "exact_matches": {"@id": "skos:exactMatch", "@type": "@id", "@container": "@set"},
    "close_matches": {"@id": "skos:closeMatch", "@type": "@id", "@container": "@set"},
    "broad_matches": {"@id": "skos:broadMatch", "@type": "@id", "@container": "@set"},
    "narrow_matches": {"@id": "skos:narrowMatch", "@type": "@id", "@container": "@set"},
    "related_matches": {
        "@id": "skos:relatedMatch",
        "@type": "@id",
        "@container": "@set",
    },
    "member_of": {"@reverse": "skos:member", "@type": "@id", "@container": "@set"},
    "members": {"@id": "skos:member", "@type": "@id", "@container": "@set"},
    "subordinate_arrays": {
        "@id": "iso-thes:subordinateArray",
        "@type": "@id",
        "@container": "@set",
    },
    "broader": {"@id": "skos:broader", "@type": "@id", "@container": "@set"},
    "narrower": {"@id": "skos:narrower", "@type": "@id", "@container": "@set"},
    "related": {"@id": "skos:related", "@type": "@id", "@container": "@set"},
    "languages": {"@id": "dct:language", "@type": "@id", "@container": "@set"},
    "label_types": {"@id": "dct:type", "@type": "@id", "@container": "@set"},
}

_LABEL_TYPE_MAP = {
    "prefLabel": "pref_labels",
    "altLabel": "alt_labels",
    "hiddenLabel": "hidden_labels",
    "sortLabel": "hidden_labels",
}

_LABEL_XL_TYPE_MAP = {
    "prefLabel": "pref_labels_xl",
    "altLabel": "alt_labels_xl",
    "hiddenLabel": "hidden_labels_xl",
    "sortLabel": "hidden_labels_xl",
}

_NOTE_TYPE_MAP = {
    "note": "general_notes",
    "scopeNote": "scope_notes",
    "definition": "definitions",
    "historyNote": "history_notes",
    "editorialNote": "editorial_notes",
    "changeNote": "change_notes",
    "example": "examples",
}

_CONCEPT_RELATIONS = ("broader", "narrower", "related", "subordinate_arrays")
_COLLECTION_RELATIONS = ("members", "superordinates")


def jsonld_dumper(
    provider: VocabularyProvider,
    context: str | dict | None = None,
    language: str | None = None,
    extra_data_serializer: Serializer = None,
) -> dict:
    """
    Dump a provider to a JSON-LD serialisable dictionary.

    :param skosprovider.providers.VocabularyProvider provider: The provider
        that wil be turned into a JSON-LD `dict`.
    :param str or dict context: Context as a dict or link to context file.
    :param string language: Language to render a single label in.
    :param extra_data_serializer: Optional :data:`Serializer` callable that
        receives the output dict and a SKOS object, and mutates the dict to
        add extra data.

    :rtype: A `dict`
    """
    if not language:
        language = provider.metadata.get("default_language", "en")
    doc = {"@graph": []}
    if context:
        doc["@context"] = context
    doc["@graph"].append(
        jsonld_conceptscheme_dumper(
            provider,
            None,
            relations_profile="uri",
            language=language,
            extra_data_serializer=extra_data_serializer,
        )
    )
    for concept_or_collection in provider.get_all():
        doc["@graph"].append(
            jsonld_c_dumper(
                provider,
                concept_or_collection["id"],
                None,
                relations_profile="uri",
                language=language,
                extra_data_serializer=extra_data_serializer,
            )
        )
    return doc


def jsonld_conceptscheme_dumper(
    provider: VocabularyProvider,
    context: str | dict | None = None,
    relations_profile: Literal["partial", "uri"] = "partial",
    language: str = "en",
    extra_data_serializer: Serializer = None,
) -> dict:
    """
    Dump a conceptscheme to a JSON-LD serialisable dictionary.

    :param skosprovider.providers.VocabularyProvider provider: The provider
        that contains the conceptscheme.
    :param str or dict context: Context as a dict or link to context file.
    :param str relations_profile: Either `partial` or `uri` to render links to
        other resources with some information or just a :term:`URI`.
    :param string language: Language to render a single label in.
    :param extra_data_serializer: Optional :data:`Serializer` callable that
        receives the output dict and a SKOS object, and mutates the dict to
        add extra data.

    :rtype: A `dict`
    """
    cs = provider.concept_scheme
    doc = _render_cs_basic(cs, language)
    if context:
        doc["@context"] = context
    if dataset_uri := provider.get_metadata().get("dataset", {}).get("uri"):
        doc["in_dataset"] = dataset_uri
    doc["id"] = provider.get_metadata()["id"]
    doc.update(_render_labels(cs, extra_data_serializer))
    doc.update(_render_labels_xl(cs, extra_data_serializer))
    doc.update(_render_notes(cs, extra_data_serializer))
    doc.update(_render_sources(cs, extra_data_serializer))
    doc["languages"] = list(cs.languages)
    top = list(provider.get_top_concepts())
    doc["top_concepts"] = [tc["uri"] for tc in top] if relations_profile == "uri" else top
    if extra_data_serializer is not None and cs.extra_data is not None:
        extra_data_serializer(doc, cs)
    return doc


def jsonld_c_dumper(
    provider: VocabularyProvider,
    id: str | int,
    context: str | dict | None = None,
    relations_profile: Literal["partial", "uri"] = "partial",
    language: str = "en",
    extra_data_serializer: Serializer = None,
) -> dict:
    """
    Dump a concept or collection to a JSON-LD serialisable dictionary.

    :param skosprovider.providers.VocabularyProvider provider: The provider
        that contains the concept or collection.
    :param str or int id: Identifier of the concept to dump.
    :param str or dict context: Context as a dict or link to context file.
    :param str relations_profile: Either `partial` or `uri` to render links to
        other resources with some information or just a :term:`URI`.
    :param string language: Language to render a single label in.
    :param extra_data_serializer: Optional :data:`Serializer` callable that
        receives the output dict and a SKOS object, and mutates the dict to
        add extra data.

    :rtype: A `dict`
    """
    obj = provider.get_by_id(id)
    if obj is False:
        raise ValueError(f"id {id} was not found in the provider.")
    doc = _render_c_basic(obj, language)
    if context:
        doc["@context"] = context
    doc["concept_scheme"] = (
        _render_cs_basic(obj.concept_scheme, language)
        if relations_profile == "partial"
        else obj.concept_scheme.uri
    )
    if dataset_uri := provider.get_metadata().get("dataset", {}).get("uri"):
        doc["in_dataset"] = dataset_uri
    doc.update(_render_labels(obj, extra_data_serializer))
    doc.update(_render_labels_xl(obj, extra_data_serializer))
    doc.update(_render_notes(obj, extra_data_serializer))
    doc.update(_render_sources(obj, extra_data_serializer))
    doc.update(_render_relation(obj, provider, "member_of", relations_profile, language))
    if obj.type == "concept":
        doc.update(_render_matches(obj))
        for rel in _CONCEPT_RELATIONS:
            doc.update(_render_relation(obj, provider, rel, relations_profile, language))
    elif obj.type == "collection":
        doc["infer_concept_relations"] = True
        for rel in _COLLECTION_RELATIONS:
            doc.update(_render_relation(obj, provider, rel, relations_profile, language))
    if extra_data_serializer is not None and obj.extra_data is not None:
        extra_data_serializer(doc, obj)
    return doc


def _render_c_basic(obj: Concept | Collection, language: str = "en") -> dict:
    doc = {"id": obj.id, "uri": obj.uri, "type": obj.type}
    if label := obj.label(language):
        doc["label"] = label.label
    return doc


def _render_cs_basic(cs: ConceptScheme, language: str = "en") -> dict:
    doc = {"uri": cs.uri, "type": "skos:ConceptScheme"}
    if label := cs.label(language):
        doc["label"] = label.label
    return doc


def _render_labels(
    obj: Concept | Collection | ConceptScheme,
    extra_data_serializer: Serializer = None,
) -> dict:
    if not obj.labels:
        return {}
    doc: dict = {"labels": {}}
    for label in obj.labels:
        language = extract_language(label.language)
        rendered = {"language": language, "@language": language, "lbl": label.label}
        if extra_data_serializer is not None and label.extra_data is not None:
            extra_data_serializer(rendered, label)
        doc["labels"].setdefault(_LABEL_TYPE_MAP[label.type], []).append(rendered)
    return doc


def _render_labels_xl(
    obj: Concept | Collection | ConceptScheme,
    extra_data_serializer: Serializer = None,
) -> dict:
    xl_labels = [lbl for lbl in obj.labels if lbl.is_xl()]
    if not xl_labels:
        return {}
    doc: dict = {"labels_xl": {}}
    for label in xl_labels:
        language = extract_language(label.language)
        rendered = {
            "uri": label.uri,
            "type": "skosxl:Label",
            "skosxl:literalForm": {"@language": language, "lbl": label.label},
        }
        if label.label_types:
            rendered["label_types"] = label.label_types
        if extra_data_serializer is not None and label.extra_data is not None:
            extra_data_serializer(rendered, label)
        doc["labels_xl"].setdefault(_LABEL_XL_TYPE_MAP[label.type], []).append(rendered)
    return doc


def _render_notes(
    obj: Concept | Collection | ConceptScheme,
    extra_data_serializer: Serializer = None,
) -> dict:
    if not obj.notes:
        return {}
    doc: dict = {"notes": {}}
    for note in obj.notes:
        language = extract_language(note.language)
        rendered = {"language": language, "@language": language, "nt": note.note}
        if note.markup is not None:
            del rendered["@language"]
            rendered["nt"] = add_lang_to_html(rendered["nt"], language)
            rendered["@type"] = note.markup
        if extra_data_serializer is not None and note.extra_data is not None:
            extra_data_serializer(rendered, note)
        doc["notes"].setdefault(_NOTE_TYPE_MAP[note.type], []).append(rendered)
    return doc


def _render_sources(
    obj: Concept | Collection | ConceptScheme,
    extra_data_serializer: Serializer = None,
) -> dict:
    if not obj.sources:
        return {}
    doc: dict = {"sources": []}
    for source in obj.sources:
        rendered: dict = {
            "type": "dct:BibliographicResource",
            "citations": [{"ct": source.citation}],
        }
        if source.markup is not None:
            rendered["citations"][0]["@type"] = source.markup
        if extra_data_serializer is not None and source.extra_data is not None:
            extra_data_serializer(rendered, source)
        doc["sources"].append(rendered)
    return doc


def _render_matches(concept: Concept) -> dict:
    if not any(concept.matches.values()):
        return {}
    doc: dict = {"matches": {}}
    for matchtype, matches in concept.matches.items():
        if matches:
            doc["matches"].setdefault(f"{matchtype}_matches", []).extend(matches)
    return doc


def _render_relation(
    obj: Concept | Collection,
    provider: VocabularyProvider,
    relation: str,
    profile: Literal["partial", "uri"] = "partial",
    language: str = "en",
) -> dict:
    doc: dict = {relation: []}
    for member_id in getattr(obj, relation):
        related = provider.get_by_id(member_id)
        if profile == "partial":
            doc[relation].append(_render_c_basic(related, language))
        else:
            doc[relation].append(related.uri)
    return doc
