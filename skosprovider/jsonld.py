"""
This module contains functions dealing with jsonld reading and writing.

.. versionadded:: 0.7.0
"""

import logging

from skosprovider.utils import add_lang_to_html
from skosprovider.utils import extract_language

log = logging.getLogger(__name__)

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


def jsonld_dumper(provider, context=None, language=None):
    """
    Dump a provider to a JSON-LD serialisable dictionary.

    :param skosprovider.providers.VocabularyProvider provider: The provider
        that wil be turned into a JSON-LD `dict`.
    :param str or dict context: Context as a dict or link to context file.
    :param string language: Language to render a single label in.

    :rtype: A `dict`
    """
    if not language:
        language = provider.metadata.get("default_language", "en")
    doc = {"@graph": []}
    if context:
        doc["@context"] = context
    doc["@graph"].append(
        jsonld_conceptscheme_dumper(
            provider, None, relations_profile="uri", language=language
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
            )
        )
    return doc


def jsonld_c_dumper(
    provider, id, context=None, relations_profile="partial", language="en"
):
    """
    Dump a concept or collection to a JSON-LD serialisable dictionary.

    :param skosprovider.providers.VocabularyProvider provider: The provider
        that contains the concept or collection.
    :param str or int id: Identifier of the concept to dump.
    :param str or dict context: Context as a dict or link to context file.
    :param str relations_profile: Either `partial` or `uri` to render links to
        other resources with some information or just a :term:`URI`.
    :param string language: Language to render a single label in.

    :rtype: A `dict`
    """
    concept_or_collection = provider.get_by_id(id)
    doc = _jsonld_c_basic_renderer(concept_or_collection, language)
    if context:
        doc["@context"] = context
    if relations_profile == "partial":
        doc["concept_scheme"] = _jsonld_cs_basic_renderer(
            concept_or_collection.concept_scheme, language
        )
    else:
        doc["concept_scheme"] = concept_or_collection.concept_scheme.uri
    dataset_uri = provider.get_metadata().get("dataset", {}).get("uri", None)
    if dataset_uri:
        doc["in_dataset"] = dataset_uri
    doc.update(_jsonld_labels_renderer(concept_or_collection))
    doc.update(_jsonld_labels_xl_renderer(concept_or_collection))
    doc.update(_jsonld_notes_renderer(concept_or_collection))
    doc.update(_jsonld_sources_renderer(concept_or_collection))
    doc.update(
        _jsonld_member_of_renderer(
            concept_or_collection, provider, relations_profile, language
        )
    )
    if concept_or_collection.type == "concept":
        doc.update(_jsonld_matches_renderer(concept_or_collection))
        doc.update(
            _jsonld_broader_renderer(
                concept_or_collection, provider, relations_profile, language
            )
        )
        doc.update(
            _jsonld_narrower_renderer(
                concept_or_collection, provider, relations_profile, language
            )
        )
        doc.update(
            _jsonld_related_renderer(
                concept_or_collection, provider, relations_profile, language
            )
        )
        doc.update(
            _jsonld_subordinate_arrays_renderer(
                concept_or_collection, provider, relations_profile, language
            )
        )
    elif concept_or_collection.type == "collection":
        doc["infer_concept_relations"] = True
        doc.update(
            _jsonld_members_renderer(
                concept_or_collection, provider, relations_profile, language
            )
        )
        doc.update(
            _jsonld_superordinates_renderer(
                concept_or_collection, provider, relations_profile, language
            )
        )
    return doc


def _jsonld_c_basic_renderer(concept_or_collection, language="en"):
    doc = {
        "id": concept_or_collection.id,
        "uri": concept_or_collection.uri,
        "type": concept_or_collection.type,
    }
    label = concept_or_collection.label(language)
    if label:
        doc["label"] = label.label
    return doc


def _jsonld_cs_basic_renderer(concept_scheme, language="en"):
    doc = {"uri": concept_scheme.uri, "type": "skos:ConceptScheme"}
    label = concept_scheme.label(language)
    if label:
        doc["label"] = label.label
    return doc


def _jsonld_labels_renderer(concept_or_collection):
    if not len(concept_or_collection.labels):
        return {}
    doc = {"labels": {}}

    def label_renderer(label):
        language = extract_language(label.language)
        return {"language": language, "@language": language, "lbl": label.label}

    label_type_map = {
        "prefLabel": "pref_labels",
        "altLabel": "alt_labels",
        "hiddenLabel": "hidden_labels",
        "sortLabel": "hidden_labels",
    }
    for label in concept_or_collection.labels:
        doc["labels"].setdefault(label_type_map[label.type], []).append(
            label_renderer(label)
        )
    return doc


def _jsonld_labels_xl_renderer(concept_or_collection):
    if not len([label for label in concept_or_collection.labels if label.is_xl()]):
        return {}
    doc = {"labels_xl": {}}

    def label_xl_renderer(label):
        language = extract_language(label.language)
        rendered_label = {
            "uri": label.uri,
            "type": "skosxl:Label",
            "skosxl:literalForm": {"@language": language, "lbl": label.label},
        }
        if len(label.label_types):
            rendered_label["label_types"] = label.label_types
        return rendered_label

    label_type_map = {
        "prefLabel": "pref_labels_xl",
        "altLabel": "alt_labels_xl",
        "hiddenLabel": "hidden_labels_xl",
        "sortLabel": "hidden_labels_xl",
    }
    for label in concept_or_collection.labels:
        if label.is_xl():
            doc["labels_xl"].setdefault(label_type_map[label.type], []).append(
                label_xl_renderer(label)
            )
    return doc


def _jsonld_notes_renderer(concept_or_collection):
    if not len(concept_or_collection.notes):
        return {}
    doc = {"notes": {}}

    def note_renderer(note):
        language = extract_language(note.language)
        rendered_note = {
            "language": language,
            "@language": language,
            "nt": note.note,
        }
        if note.markup is not None:
            del rendered_note["@language"]
            rendered_note["nt"] = add_lang_to_html(rendered_note["nt"], language)
            rendered_note["@type"] = note.markup
        return rendered_note

    note_type_map = {
        "note": "general_notes",
        "scopeNote": "scope_notes",
        "definition": "definitions",
        "historyNote": "history_notes",
        "editorialNote": "editorial_notes",
        "changeNote": "change_notes",
        "example": "examples",
    }
    for note in concept_or_collection.notes:
        doc["notes"].setdefault(note_type_map[note.type], []).append(
            note_renderer(note)
        )
    return doc


def _jsonld_sources_renderer(concept_or_collection):
    if not len(concept_or_collection.sources):
        return {}
    doc = {"sources": []}

    def source_renderer(source):
        rendered_source = {
            "type": "dct:BibliographicResource",
            "citations": [{"ct": source.citation}],
        }
        if source.markup is not None:
            rendered_source["citations"][0]["@type"] = source.markup
        return rendered_source

    for source in concept_or_collection.sources:
        doc["sources"].append(source_renderer(source))
    return doc


def _jsonld_matches_renderer(concept_or_collection):
    if not any([len(matches) for matches in concept_or_collection.matches.values()]):
        return {}
    doc = {"matches": {}}
    for matchtype, matches in concept_or_collection.matches.items():
        if len(matches):
            doc["matches"].setdefault(f"{matchtype}_matches", []).extend(matches)
    return doc


def _jsonld_superordinates_renderer(
    concept_or_collection, provider, profile="partial", language="en"
):
    return _jsonld_relation_renderer(
        concept_or_collection, provider, "superordinates", profile, language
    )


def _jsonld_members_renderer(
    concept_or_collection, provider, profile="partial", language="en"
):
    return _jsonld_relation_renderer(
        concept_or_collection, provider, "members", profile, language
    )


def _jsonld_member_of_renderer(
    concept_or_collection, provider, profile="partial", language="en"
):
    return _jsonld_relation_renderer(
        concept_or_collection, provider, "member_of", profile, language
    )


def _jsonld_broader_renderer(
    concept_or_collection, provider, profile="partial", language="en"
):
    return _jsonld_relation_renderer(
        concept_or_collection, provider, "broader", profile, language
    )


def _jsonld_narrower_renderer(
    concept_or_collection, provider, profile="partial", language="en"
):
    return _jsonld_relation_renderer(
        concept_or_collection, provider, "narrower", profile, language
    )


def _jsonld_related_renderer(
    concept_or_collection, provider, profile="partial", language="en"
):
    return _jsonld_relation_renderer(
        concept_or_collection, provider, "related", profile, language
    )


def _jsonld_subordinate_arrays_renderer(
    concept_or_collection, provider, profile="partial", language="en"
):
    return _jsonld_relation_renderer(
        concept_or_collection, provider, "subordinate_arrays", profile, language
    )


def _jsonld_relation_renderer(
    concept_or_collection, provider, relation, profile="partial", language="en"
):
    doc = {relation: []}
    for member_id in getattr(concept_or_collection, relation):
        related_concept = provider.get_by_id(member_id)
        if profile == "partial":
            doc[relation].append(_jsonld_c_basic_renderer(related_concept, language))
        else:
            doc[relation].append(related_concept.uri)
    return doc


def _jsonld_topconcepts_renderer(provider, profile="partial"):
    doc = {"top_concepts": []}
    for top_concept in provider.get_top_concepts():
        if profile == "partial":
            doc["top_concepts"].append(top_concept)
        else:
            doc["top_concepts"].append(top_concept["uri"])
    return doc


def _jsonld_cs_languages_renderer(cs):
    doc = {"languages": []}
    for language in cs.languages:
        doc["languages"].append(language)
    return doc


def jsonld_conceptscheme_dumper(
    provider, context=None, relations_profile="partial", language="en"
):
    """
    Dump a conceptscheme to a JSON-LD serialisable dictionary.

    :param skosprovider.providers.VocabularyProvider provider: The provider
        that contains the conceptscheme.
    :param str or dict context: Context as a dict or link to context file.
    :param str relations_profile: Either `partial` or `uri` to render links to
        other resources with some information or just a :term:`URI`.
    :param string language: Language to render a single label in.

    :rtype: A `dict`
    """
    conceptscheme = provider.concept_scheme
    doc = _jsonld_cs_basic_renderer(conceptscheme, language)
    if context:
        doc["@context"] = context
    dataset_uri = provider.get_metadata().get("dataset", {}).get("uri", None)
    if dataset_uri:
        doc["in_dataset"] = dataset_uri
    doc["id"] = provider.get_metadata()["id"]
    doc.update(_jsonld_labels_renderer(conceptscheme))
    doc.update(_jsonld_labels_xl_renderer(conceptscheme))
    doc.update(_jsonld_notes_renderer(conceptscheme))
    doc.update(_jsonld_sources_renderer(conceptscheme))
    doc.update(_jsonld_cs_languages_renderer(conceptscheme))
    doc.update(_jsonld_topconcepts_renderer(provider, relations_profile))
    return doc
