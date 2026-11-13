"""
This module contains utility functions for dealing with skos providers.
"""

import re

_DIV_TAG_RE = re.compile(r"<(/?)div\b([^>]*)>", re.IGNORECASE)
_XML_LANG_ATTR_RE = re.compile(
    r"""\s+xml:lang\s*=\s*(?:"[^"]*"|'[^']*')""", re.IGNORECASE
)


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
