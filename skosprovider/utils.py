"""
This module contains utility functions for dealing with skos providers.
"""

import re

from skosprovider.skos import Collection
from skosprovider.skos import Concept

_DIV_TAG_RE = re.compile(r"<(/?)div\b([^>]*)>", re.IGNORECASE)
_XML_LANG_ATTR_RE = re.compile(
    r"""\s+xml:lang\s*=\s*(?:"[^"]*"|'[^']*')""", re.IGNORECASE
)


def dict_dumper(provider):
    """
    Dump a provider to a format that can be passed to a
    :class:`skosprovider.providers.DictionaryProvider`.

    :param skosprovider.providers.VocabularyProvider provider: The provider
        that wil be turned into a `dict`.
    :rtype: A list of dicts.

    .. versionadded:: 0.2.0
    """
    ret = []
    for stuff in provider.get_all():
        concept_or_collection = provider.get_by_id(stuff["id"])
        labels = []
        for label in concept_or_collection.labels:
            label_dict = {
                "language": label.language,
                "type": label.type,
                "label": label.label,
            }
            if label.uri:
                label_dict["uri"] = label.uri
                if len(label.label_types):
                    label_dict["label_types"] = label.label_types
            labels.append(label_dict)
        notes = [
            {
                "note": note.note,
                "type": note.type,
                "language": note.language,
                "markup": note.markup,
            }
            for note in concept_or_collection.notes
        ]
        sources = [
            {"citation": source.citation, "markup": source.markup}
            for source in concept_or_collection.sources
        ]
        if isinstance(concept_or_collection, Concept):
            ret.append(
                {
                    "id": concept_or_collection.id,
                    "uri": concept_or_collection.uri,
                    "type": concept_or_collection.type,
                    "labels": labels,
                    "notes": notes,
                    "sources": sources,
                    "narrower": concept_or_collection.narrower,
                    "broader": concept_or_collection.broader,
                    "related": concept_or_collection.related,
                    "member_of": concept_or_collection.member_of,
                    "subordinate_arrays": concept_or_collection.subordinate_arrays,
                    "matches": concept_or_collection.matches,
                }
            )
        elif isinstance(concept_or_collection, Collection):
            ret.append(
                {
                    "id": concept_or_collection.id,
                    "uri": concept_or_collection.uri,
                    "type": concept_or_collection.type,
                    "labels": labels,
                    "notes": notes,
                    "sources": sources,
                    "members": concept_or_collection.members,
                    "member_of": concept_or_collection.member_of,
                    "superordinates": concept_or_collection.superordinates,
                    "infer_concept_relations": concept_or_collection.infer_concept_relations,  # NoQa: B950
                }
            )
    return ret


def extract_language(lang):
    """
    Turn a language in our domain model into a IANA tag.

    .. versionadded:: 0.7.0
    """
    return "und" if lang is None else lang


def _single_div_wrapper(text):
    """
    If ``text`` is a single ``<div>...</div>`` element wrapping the entire
    content (nested divs inside are allowed), return ``(attrs, inner)`` —
    the outer div's attribute string and the HTML between the tags.
    Otherwise return ``None``.
    """
    first = _DIV_TAG_RE.match(text)
    if not first or first.group(1):
        return None
    depth = 0
    for m in _DIV_TAG_RE.finditer(text):
        depth += -1 if m.group(1) else 1
        if depth == 0:
            if m.end() != len(text):
                return None
            return first.group(2), text[first.end() : m.start()]
    return None


def add_lang_to_html(htmltext, lang):
    """
    Wrap a piece of HTML in a ``<div>`` carrying an ``xml:lang`` attribute.

    If ``htmltext`` already consists of a single root ``<div>``, the
    ``xml:lang`` attribute is merged into that existing element instead of
    adding another wrapper. This keeps the function idempotent under
    export/import round-trips where an importer may strip ``xml:lang`` but
    leave the wrapping div behind.

    .. versionadded:: 0.7.0
    """
    if lang == "und":
        return htmltext
    wrapper = _single_div_wrapper(htmltext)
    if wrapper is not None:
        attrs, inner = wrapper
        attrs = _XML_LANG_ATTR_RE.sub("", attrs).strip()
        attr_part = (" " + attrs) if attrs else ""
        return f'<div xml:lang="{lang}"{attr_part}>{inner}</div>'
    return f'<div xml:lang="{lang}">{htmltext}</div>'
