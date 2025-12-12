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
            div.ownerDocument = html
            div.setAttribute("xml:lang", lang)
            div.childNodes = [node]
            html.childNodes = [div]
        else:
            node.setAttribute("xml:lang", lang)
    else:
        # add a single encompassing div
        div = Element("div")
        div.ownerDocument = html
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
