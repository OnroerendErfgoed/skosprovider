"""
This module contains utility functions for dealing with skos providers.
"""

from xml.dom.minidom import DocumentFragment
from xml.dom.minidom import Element
from xml.dom.minidom import Node

import html5lib

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


def add_lang_to_html(htmltext, lang):
    """
    Take a piece of HTML and add an xml:lang attribute to it.

    .. versionadded:: 0.7.0
    """
    if lang == "und":
        return htmltext
    parser = html5lib.HTMLParser(tree=html5lib.treebuilders.getTreeBuilder("dom"))
    html = parser.parseFragment(htmltext)
    html.normalize()
    if len(html.childNodes) == 0:
        return f'<div xml:lang="{lang}"></div>'
    elif len(html.childNodes) == 1:
        node = html.firstChild
        if node.nodeType == Node.TEXT_NODE:
            div = Element("div")
            div.ownerDocument = html.ownerDocument
            div.setAttribute("xml:lang", lang)
            div.childNodes = [node]
            html.childNodes = [div]
        else:
            node.setAttribute("xml:lang", lang)
    else:
        # add a single encompassing div
        div = Element("div")
        div.ownerDocument = html.ownerDocument
        div.setAttribute("xml:lang", lang)
        div.childNodes = html.childNodes
        html.childNodes = [div]
    return html.toxml()


def _df_writexml(self, writer, indent="", addindent="", newl=""):
    """
    Monkeypatch method for unexisting `writexml` in
    :class:`xml.dom.minidom.DocumentFragment`.

    .. versionadded:: 0.7.0
    """
    # indent = current indentation
    # addindent = indentation to add to higher levels
    # newl = newline string
    if self.childNodes:
        if len(self.childNodes) == 1 and self.childNodes[0].nodeType == Node.TEXT_NODE:
            self.childNodes[0].writexml(writer, "", "", "")
        else:
            for node in self.childNodes:
                node.writexml(writer, indent + addindent, addindent, newl)


DocumentFragment.writexml = _df_writexml
