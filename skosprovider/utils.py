"""
This module contains utility functions for dealing with skos providers.
"""

from skosprovider.skos import Collection
from skosprovider.skos import Concept


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


def add_lang_to_html(htmltext, lang):
    """
    Wrap a piece of HTML in a ``<div>`` carrying an ``xml:lang`` attribute.

    .. versionadded:: 0.7.0
    """
    if lang == "und":
        return htmltext
    return f'<div xml:lang="{lang}">{htmltext}</div>'
