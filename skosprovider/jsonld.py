"""
This module contains functions dealing with jsonld reading and writing.

.. versionadded:: 0.7.0
"""

import json
import logging
from functools import singledispatch
from typing import Any

from attr import dataclass
from pyld import jsonld as pyld_jsonld
from rdflib import Graph

from skosprovider import skos
from skosprovider.providers import SkosRef
from skosprovider.providers import VocabularyProvider
from skosprovider.utils import add_lang_to_html
from skosprovider.utils import extract_language

LOG = logging.getLogger(__name__)
TYPE_TO_SKOS = {"concept": "skos:Concept", "collection": "skos:Collection"}
MATCH_TYPE_TO_SKOS = {
    "exact": "skos:exactMatch",
    "close": "skos:closeMatch",
    "broad": "skos:broadMatch",
    "narrow": "skos:narrowMatch",
    "related": "skos:relatedMatch",
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
}


@dataclass
class DumpContext:
    provider: VocabularyProvider
    all_data_by_id: dict[str, SkosRef] | None = None
    """
    Because concepts are often interlinked with relations to each other
    this essentially serves as a cache. Highly suggested to use when
    dumping an entire provider to prevent many provider calls to fetch single
    concepts by id.
    """
    language: str = "en"
    context: dict | str | None = CONTEXT


def _plain_label(lbl: "skos.Label") -> dict:
    return {"@language": extract_language(lbl.language), "@value": lbl.label}


# ---------------------------
# The to_jsonld registrations
# ---------------------------


@singledispatch
def to_jsonld(obj, dump_context: DumpContext, **kwargs) -> dict[str, Any]:
    raise TypeError(f"Unsupported type: {type(obj)}")


@to_jsonld.register(VocabularyProvider)
def _(
    provider: VocabularyProvider, dump_context: DumpContext | None = None, **kwargs
) -> dict[str, Any]:
    """
    Dump a provider to a JSON-LD serialisable dictionary.

    :param skosprovider.providers.VocabularyProvider provider: The provider
        that wil be turned into a JSON-LD `dict`.
    :param DumpContext dump_context: Context for the dump operation. If None,
        a default DumpContext will be created from the provider's metadata.

    :rtype: A `dict`
    """
    all_data = provider.get_all()
    if dump_context is None:
        language = provider.metadata.get("default_language", "en")
        dump_context = DumpContext(
            provider=provider,
            language=language,
            all_data_by_id={item["id"]: item for item in all_data},
        )
    if not dump_context.context:
        dump_context.context = CONTEXT

    doc: dict[str, Any] = {
        "@graph": [to_jsonld(provider.concept_scheme, dump_context)],
        "@context": dump_context.context,
    }
    for concept_or_collection in all_data:
        obj = provider.get_by_id(concept_or_collection["id"])
        if obj is not False:
            doc["@graph"].append(to_jsonld(obj, dump_context))
    return doc


@to_jsonld.register(skos.Label)
def _(label: skos.Label, dump_context: DumpContext, **kwargs) -> dict:
    lang = extract_language(label.language)

    if label.is_xl():
        rendered = {
            "@id": label.uri,
            "@type": "skosxl:Label",
            "skosxl:literalForm": {"@language": lang, "@value": label.label},
        }
        if label.label_types:
            rendered["dct:type"] = [{"@id": lt} for lt in label.label_types]
        if label.extra_data is not None:
            rendered.update(_extra_data_to_props(label.extra_data))
        return rendered
    else:
        return {"@language": lang, "@value": label.label}


@to_jsonld.register(skos.Concept)
def _(concept: skos.Concept, dump_context: DumpContext, **kwargs):
    language = dump_context.language
    dataset_uri = dump_context.provider.get_metadata().get("dataset", {}).get("uri")
    best_label = concept.label(language)

    def render_list(objs):
        return [to_jsonld(obj, dump_context, **kwargs) for obj in objs]

    def relation(r):
        return id_to_relation_jsonld(r, dump_context, **kwargs)

    pref_labels_xl = (lbl for lbl in concept.pref_labels if lbl.is_xl())
    alt_labels_xl = (lbl for lbl in concept.alt_labels if lbl.is_xl())
    hidden_labels_xl = (lbl for lbl in concept.hidden_labels if lbl.is_xl())
    concept_jsonld = {
        "@id": concept.uri,
        "@type": "skos:Concept",
        "dct:identifier": concept.id,
        "skos:inScheme": (
            _cs_ref(concept.concept_scheme, language)
            if concept.concept_scheme
            else None
        ),
        "void:inDataset": {"@id": dataset_uri} if dataset_uri else None,
        "rdfs:label": best_label.label if best_label else None,
        # plain labels as literals (XL labels also appear in skosxl:* below)
        "skos:prefLabel": [_plain_label(lbl) for lbl in concept.pref_labels],
        "skos:altLabel": [_plain_label(lbl) for lbl in concept.alt_labels],
        "skos:hiddenLabel": [
            _plain_label(lbl) for lbl in concept.hidden_labels + concept.sort_labels
        ],
        # XL labels
        "skosxl:prefLabel": render_list(pref_labels_xl),
        "skosxl:altLabel": render_list(alt_labels_xl),
        "skosxl:hiddenLabel": render_list(hidden_labels_xl),
        # notes
        "skos:note": render_list(concept.general_notes),
        "skos:scopeNote": render_list(concept.scope_notes),
        "skos:definition": render_list(concept.definitions),
        "skos:historyNote": render_list(concept.history_notes),
        "skos:editorialNote": render_list(concept.editorial_notes),
        "skos:changeNote": render_list(concept.change_notes),
        "skos:example": render_list(concept.examples),
        # sources
        "dct:source": render_list(concept.sources),
        # relations
        "@reverse": (
            {"skos:member": [relation(r) for r in concept.member_of]}
            if concept.member_of
            else None
        ),
        "skos:broader": [relation(r) for r in concept.broader],
        "skos:narrower": [relation(r) for r in concept.narrower],
        "skos:related": [relation(r) for r in concept.related],
        "iso-thes:subordinateArray": [relation(r) for r in concept.subordinate_arrays],
        # matches
        "skos:exactMatch": [{"@id": m} for m in concept.matches.get("exact", [])],
        "skos:closeMatch": [{"@id": m} for m in concept.matches.get("close", [])],
        "skos:broadMatch": [{"@id": m} for m in concept.matches.get("broad", [])],
        "skos:narrowMatch": [{"@id": m} for m in concept.matches.get("narrow", [])],
        "skos:relatedMatch": [{"@id": m} for m in concept.matches.get("related", [])],
    }
    concept_jsonld = _filter_optional_keys(concept_jsonld)
    if concept.extra_data is not None:
        concept_jsonld.update(_extra_data_to_props(concept.extra_data))
    return concept_jsonld


@to_jsonld.register(skos.ConceptScheme)
def _(conceptscheme: skos.ConceptScheme, dump_context: DumpContext, **kwargs):
    language = dump_context.language
    provider = dump_context.provider
    dataset_uri = provider.get_metadata().get("dataset", {}).get("uri")
    best_label = conceptscheme.label(language)

    def render_list(objs):
        return [to_jsonld(obj, dump_context, **kwargs) for obj in objs]

    pref_labels_xl = (lbl for lbl in conceptscheme.pref_labels if lbl.is_xl())
    alt_labels_xl = (lbl for lbl in conceptscheme.alt_labels if lbl.is_xl())
    hidden_labels_xl = (lbl for lbl in conceptscheme.hidden_labels if lbl.is_xl())
    concept_scheme_jsonld = {
        "@id": conceptscheme.uri,
        "@type": "skos:ConceptScheme",
        "dct:identifier": provider.get_metadata()["id"],
        "void:inDataset": {"@id": dataset_uri} if dataset_uri else None,
        "rdfs:label": best_label.label if best_label else None,
        # plain labels as literals (XL labels also appear in skosxl:* below)
        "skos:prefLabel": [_plain_label(lbl) for lbl in conceptscheme.pref_labels],
        "skos:altLabel": [_plain_label(lbl) for lbl in conceptscheme.alt_labels],
        "skos:hiddenLabel": [
            _plain_label(lbl)
            for lbl in conceptscheme.hidden_labels + conceptscheme.sort_labels
        ],
        # XL labels
        "skosxl:prefLabel": render_list(pref_labels_xl),
        "skosxl:altLabel": render_list(alt_labels_xl),
        "skosxl:hiddenLabel": render_list(hidden_labels_xl),
        # notes
        "skos:note": render_list(conceptscheme.general_notes),
        "skos:scopeNote": render_list(conceptscheme.scope_notes),
        "skos:definition": render_list(conceptscheme.definitions),
        "skos:historyNote": render_list(conceptscheme.history_notes),
        "skos:editorialNote": render_list(conceptscheme.editorial_notes),
        "skos:changeNote": render_list(conceptscheme.change_notes),
        "skos:example": render_list(conceptscheme.examples),
        # sources
        "dct:source": render_list(conceptscheme.sources),
        # top concepts
        "skos:hasTopConcept": [
            {
                "@id": tc["uri"],
                "@type": TYPE_TO_SKOS[tc["type"]],
                "dct:identifier": tc["id"],
                "rdfs:label": tc["label"],
            }
            for tc in provider.get_top_concepts(language=language)
        ],
        # languages
        "dct:language": [{"@value": lang} for lang in conceptscheme.languages],
    }
    concept_scheme_jsonld = _filter_optional_keys(concept_scheme_jsonld)
    if conceptscheme.extra_data is not None:
        concept_scheme_jsonld.update(_extra_data_to_props(conceptscheme.extra_data))
    return concept_scheme_jsonld


@to_jsonld.register(skos.Collection)
def _(collection: skos.Collection, dump_context: DumpContext, **kwargs):
    language = dump_context.language
    dataset_uri = dump_context.provider.get_metadata().get("dataset", {}).get("uri")
    best_label = collection.label(language)

    def render_list(objs):
        return [to_jsonld(obj, dump_context, **kwargs) for obj in objs]

    def relation(r):
        return id_to_relation_jsonld(r, dump_context)

    pref_labels_xl = (lbl for lbl in collection.pref_labels if lbl.is_xl())
    alt_labels_xl = (lbl for lbl in collection.alt_labels if lbl.is_xl())
    hidden_labels_xl = (lbl for lbl in collection.hidden_labels if lbl.is_xl())
    collection_jsonld = {
        "@id": collection.uri,
        "@type": "skos:Collection",
        "dct:identifier": collection.id,
        "skos:inScheme": _cs_ref(collection.concept_scheme, language),
        "void:inDataset": {"@id": dataset_uri} if dataset_uri else None,
        "rdfs:label": best_label.label if best_label else None,
        # plain labels as literals (XL labels also appear in skosxl:* below)
        "skos:prefLabel": [_plain_label(lbl) for lbl in collection.pref_labels],
        "skos:altLabel": [_plain_label(lbl) for lbl in collection.alt_labels],
        "skos:hiddenLabel": [
            _plain_label(lbl)
            for lbl in collection.hidden_labels + collection.sort_labels
        ],
        # XL labels
        "skosxl:prefLabel": render_list(pref_labels_xl),
        "skosxl:altLabel": render_list(alt_labels_xl),
        "skosxl:hiddenLabel": render_list(hidden_labels_xl),
        # notes
        "skos:note": render_list(collection.general_notes),
        "skos:scopeNote": render_list(collection.scope_notes),
        "skos:definition": render_list(collection.definitions),
        "skos:historyNote": render_list(collection.history_notes),
        "skos:editorialNote": render_list(collection.editorial_notes),
        "skos:changeNote": render_list(collection.change_notes),
        "skos:example": render_list(collection.examples),
        # sources
        "dct:source": render_list(collection.sources),
        # members
        "skos:member": [relation(r) for r in collection.members],
        "@reverse": (
            {"skos:member": [relation(r) for r in collection.member_of]}
            if collection.member_of
            else None
        ),
    }
    collection_jsonld = _filter_optional_keys(collection_jsonld)
    if collection.extra_data is not None:
        collection_jsonld.update(_extra_data_to_props(collection.extra_data))
    return collection_jsonld


@to_jsonld.register(skos.Note)
def _(note: skos.Note, dump_context: DumpContext, **kwargs) -> dict:
    lang = extract_language(note.language)
    rdf_value = (
        {"@value": add_lang_to_html(note.note, lang), "@type": "rdf:HTML"}
        if note.markup is not None
        else {"@value": note.note, "@language": lang}
    )
    rendered = {"rdf:value": rdf_value}
    if note.is_object():
        rendered["@id"] = note.uri
        if note.extra_data is not None:
            rendered.update(_extra_data_to_props(note.extra_data))
    return rendered


@to_jsonld.register(skos.Source)
def _(source: skos.Source, dump_context: DumpContext, **kwargs) -> dict:
    rdf_value = (
        {"@value": source.citation, "@type": "rdf:HTML"}
        if source.markup is not None
        else {"@value": source.citation}
    )
    if source.is_object():
        rendered = {
            "@type": "dct:BibliographicResource",
            "@id": source.uri,
            "rdf:value": rdf_value,
        }
        if source.extra_data is not None:
            rendered.update(_extra_data_to_props(source.extra_data))
    else:
        rendered = {
            "@type": "dct:BibliographicResource",
            "dct:bibliographicCitation": [rdf_value],
        }
    return rendered


# -----------------------------------
# End of main to_jsonld registrations
# -----------------------------------


def _filter_optional_keys(full_jsonld: dict) -> dict:
    optional = {
        "void:inDataset",
        "dct:source",
        "@reverse",
        # labels
        "rdfs:label",
        "skos:prefLabel",
        "skos:altLabel",
        "skos:hiddenLabel",
        "skosxl:prefLabel",
        "skosxl:altLabel",
        "skosxl:hiddenLabel",
        # notes
        "skos:note",
        "skos:scopeNote",
        "skos:definition",
        "skos:historyNote",
        "skos:editorialNote",
        "skos:changeNote",
        "skos:example",
        # matches
        "skos:exactMatch",
        "skos:closeMatch",
        "skos:broadMatch",
        "skos:narrowMatch",
        "skos:relatedMatch",
        # concept scheme
        "skos:hasTopConcept",
        "dct:language",
        # collection
        "skos:member",
    }
    return {k: v for k, v in full_jsonld.items() if k not in optional or v}


def _extra_data_to_props(extra_data: Graph):
    """Extract properties from an extra_data Graph for merging into a rendered dict."""
    serialized = json.loads(extra_data.serialize(format="json-ld"))
    expanded = pyld_jsonld.expand(serialized)
    if not expanded:
        return {}
    return {k: v for k, v in expanded[0].items() if k != "@id"}


def id_to_relation_jsonld(skos_id: str, dump_context: DumpContext):
    if dump_context.all_data_by_id is not None:
        relation_data = dump_context.all_data_by_id.get(skos_id)
        if relation_data:
            return {
                "@id": relation_data["id"],
                "@type": TYPE_TO_SKOS[relation_data["type"]],
                "dct:identifier": relation_data["id"],
                "rdfs:label": relation_data["label"],
            }

    concept_or_collection = dump_context.provider.get_by_id(skos_id)
    if concept_or_collection is False:
        return {"@id": skos_id}

    best = concept_or_collection.label(language=dump_context.language)
    return {
        "@id": concept_or_collection.uri,
        "@type": TYPE_TO_SKOS[concept_or_collection.type],
        "dct:identifier": concept_or_collection.id,
        "rdfs:label": best.label if best else None,
    }


def _cs_ref(cs: "skos.ConceptScheme", language: str) -> dict:
    ref: dict = {"@id": cs.uri, "@type": "skos:ConceptScheme"}
    best = cs.label(language)
    if best:
        ref["rdfs:label"] = best.label
    return ref
