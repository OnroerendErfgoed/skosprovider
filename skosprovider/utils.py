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
        c = provider.get_by_id(stuff["id"])
        labels = []
        for label in c.labels:
            ldict = {
                "language": label.language,
                "type": label.type,
                "label": label.label,
            }
            if label.uri:
                ldict["uri"] = label.uri
                if len(label.label_types):
                    ldict["label_types"] = label.label_types
            labels.append(ldict)
        notes = [
            {
                "note": note.note,
                "type": note.type,
                "language": note.language,
                "markup": note.markup,
            }
            for note in c.notes
        ]
        sources = [
            {"citation": source.citation, "markup": source.markup}
            for source in c.sources
        ]
        if isinstance(c, Concept):
            ret.append(
                {
                    "id": c.id,
                    "uri": c.uri,
                    "type": c.type,
                    "labels": labels,
                    "notes": notes,
                    "sources": sources,
                    "narrower": c.narrower,
                    "broader": c.broader,
                    "related": c.related,
                    "member_of": c.member_of,
                    "subordinate_arrays": c.subordinate_arrays,
                    "matches": c.matches,
                }
            )
        elif isinstance(c, Collection):
            ret.append(
                {
                    "id": c.id,
                    "uri": c.uri,
                    "type": c.type,
                    "labels": labels,
                    "notes": notes,
                    "sources": sources,
                    "members": c.members,
                    "member_of": c.member_of,
                    "superordinates": c.superordinates,
                    "infer_concept_relations": c.infer_concept_relations,
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
