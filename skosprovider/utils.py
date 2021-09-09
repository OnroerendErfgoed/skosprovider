# -*- coding: utf-8 -*-
'''
This module contains utility functions for dealing with skos providers.
'''

import sys

from skosprovider.skos import (
    Concept,
    Collection
)

from xml.dom.minidom import Node, Element
import html5lib

PY3 = sys.version_info[0] == 3

if PY3:  # pragma: no cover
    binary_type = bytes
else:  # pragma: no cover
    binary_type = str


def dict_dumper(provider):
    '''
    Dump a provider to a format that can be passed to a
    :class:`skosprovider.providers.DictionaryProvider`.

    :param skosprovider.providers.VocabularyProvider provider: The provider
        that wil be turned into a `dict`.
    :rtype: A list of dicts.

    .. versionadded:: 0.2.0
    '''
    ret = []
    for stuff in provider.get_all():
        c = provider.get_by_id(stuff['id'])
        labels = [l.__dict__ for l in c.labels]
        notes = [n.__dict__ for n in c.notes]
        sources = [s.__dict__ for s in c.sources]
        if isinstance(c, Concept):
            ret.append({
                'id': c.id,
                'uri': c.uri,
                'type': c.type,
                'labels': labels,
                'notes': notes,
                'sources': sources,
                'narrower': c.narrower,
                'broader': c.broader,
                'related': c.related,
                'member_of': c.member_of,
                'subordinate_arrays': c.subordinate_arrays,
                'matches': c.matches
            })
        elif isinstance(c, Collection):
            ret.append({
                'id': c.id,
                'uri': c.uri,
                'type': c.type,
                'labels': labels,
                'notes': notes,
                'sources': sources,
                'members': c.members,
                'member_of': c.member_of,
                'superordinates': c.superordinates,
                'infer_concept_relations': c.infer_concept_relations
            })
    return ret


def extract_language(lang):
    '''
    Turn a language in our domain model into a IANA tag.

    .. versionadded:: 0.7.0
    '''
    if lang is None:
        lang = 'und'  # return undefined code when no language
    else:
        lang = text_(lang, encoding="UTF-8")
    return lang


def text_(s, encoding='latin-1', errors='strict'):
    """ If ``s`` is an instance of ``binary_type``, return
    ``s.decode(encoding, errors)``, otherwise return ``s``"""
    if isinstance(s, binary_type):
        return s.decode(encoding, errors)
    return s


def add_lang_to_html(htmltext, lang):
    '''
    Take a piece of HTML and add an xml:lang attribute to it.

    .. versionadded:: 0.7.0
    '''
    if lang == 'und':
        return htmltext
    parser = html5lib.HTMLParser(
        tree=html5lib.treebuilders.getTreeBuilder("dom")
    )
    html = parser.parseFragment(htmltext)
    html.normalize()
    if len(html.childNodes) == 0:
        return '<div xml:lang="%s"></div>' % lang
    elif len(html.childNodes) == 1:
        node = html.firstChild
        if node.nodeType == Node.TEXT_NODE:
            div = Element('div')
            div.ownerDocument = html
            div.setAttribute('xml:lang', lang)
            div.childNodes = [node]
            html.childNodes = [div]
        else:
            node.setAttribute('xml:lang', lang)
    else:
        #add a single encompassing div
        div = Element('div')
        div.ownerDocument = html
        div.setAttribute('xml:lang', lang)
        div.childNodes = html.childNodes
        html.childNodes = [div]
    return html.toxml()


def _df_writexml(self, writer, indent="", addindent="", newl=""):
    '''
    Monkeypatch method for unexisting `writexml` in
    :class:`xml.dom.minidom.DocumentFragment`.

    .. versionadded:: 0.7.0
    '''
    # indent = current indentation
    # addindent = indentation to add to higher levels
    # newl = newline string
    if self.childNodes:
        if (len(self.childNodes) == 1 and
            self.childNodes[0].nodeType == Node.TEXT_NODE):
            self.childNodes[0].writexml(writer, '', '', '')
        else:
            for node in self.childNodes:
                node.writexml(writer, indent+addindent, addindent, newl)

from xml.dom.minidom import DocumentFragment
DocumentFragment.writexml = _df_writexml
