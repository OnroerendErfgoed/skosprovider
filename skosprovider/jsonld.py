# -*- coding: utf-8 -*-
'''
This module contains functions dealing with jsonld reading and writing.
'''

from __future__ import unicode_literals

from skosprovider.skos import (
    Concept,
    Collection,
    label
)

from skosprovider.utils import (
    extract_language,
    add_lang_to_html
)

context = {
    "@version": 1.1,
    "dct": "http://purl.org/dc/terms/",
    "skos": "http://www.w3.org/2004/02/skos/core#",
    "iso-thes": "http://purl.org/iso25964/skos-thes#",
    "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
    "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
    "label": "rdfs:label",
    "uri": "@id",
    "type": "@type",
    "concept": "skos:Concept",
    "collection": "skos:Collection",
    "lbl": "@value",
    "nt": "@value",
    "ct": "@value",
    "markup": "@type",
    "HTML": "rdf:HTML",
    "id": "dct:identifier",
    "labels": "@nest",
    "notes": "@nest",
    "sources": {
        "@id": "dct:source",
        "@container": "@set"
    },
    "citations": {
      "@id": "dct:bibliographicCitation",
      "@container": "@set"
    },
    "pref_labels": {
      "@nest": "labels",
      "@id": "skos:prefLabel",
      "@container": "@set"
    },
    "alt_labels": {
      "@nest": "labels",
      "@id": "skos:altLabel",
      "@container": "@set"
    },
    "hidden_labels": {
      "@nest": "labels",
      "@id": "skos:hiddenLabel",
      "@container": "@set"
    },
    "general_notes": {
        "@nest": "notes",
        "@id": "skos:note",
        "@container": "@set"
    },
    "scope_notes": {
        "@nest": "notes",
        "@id": "skos:scopeNote",
        "@container": "@set"
    },
    "definitions": {
        "@nest": "notes",
        "@id": "skos:definition",
        "@container": "@set"
    },
    "history_notes": {
        "@nest": "notes",
        "@id": "skos:historyNote",
        "@container": "@set"
    },
    "editioral_notes": {
        "@nest": "notes",
        "@id": "skos:editorialNote",
        "@container": "@set"
    },
    "change_notes": {
        "@nest": "notes",
        "@id": "skos:changeNote",
        "@container": "@set"
    },
    "examples": {
        "@nest": "notes",
        "@id": "skos:example",
        "@container": "@set"
    },
    "member_of": {
        "@reverse": "skos:member"
    },
    "members": "skos:member",
    "subordinate_arrays": "iso-thes:subordinateArray",
    "broader": "skos:broader",
    "narrower": "skos:narrower",
    "related": "skos:related",
}

def jsonld_dumper(provider):
    pass

def jsonld_c_dumper(provider, id):
    c = provider.get_by_id(id)
    doc = _jsonld_c_basic_renderer(c)
    doc.update(_jsonld_label_renderer(c))
    doc.update(_jsonld_note_renderer(c))
    doc.update(_jsonld_source_renderer(c))
    return doc

def _jsonld_c_basic_renderer(c):
    doc = {
        'id': c.id,
        'uri': c.uri,
    }
    label = c.label()
    if label:
        doc['label'] = label.label
    if isinstance(c, Concept):
        doc['type'] = 'concept'
    elif isinstance(c, Collection):
        doc['type'] = 'collection'
    return doc

def _jsonld_label_renderer(c):
    doc = {
        'labels': {}
    }
    def lbl_renderer(l):
        language = extract_language(l.language)
        return {
            'language': language,
            '@language': language,
            'lbl': l.label
        }
    ltypemap = {
        'prefLabel': 'pref_labels',
        'altLabel': 'alt_labels',
        'hiddenLabel': 'hidden_labels',
        'sortLabel': 'hidden_labels'
    }
    for l in c.labels:
        doc['labels'].setdefault(ltypemap[l.type], []).append(lbl_renderer(l))
    return doc

def _jsonld_note_renderer(c):
    doc = {
        'notes': {}
    }
    def nt_renderer(n):
        language = extract_language(n.language)
        note = {
            'language': language,
            '@language': language,
            'nt': n.note
        }
        if n.markup is not None:
            del note['@language']
            note['markup'] = n.markup
        return note
    ntypemap = {
        'note': 'general_notes',
        'scopeNote': 'scope_notes',
        'definition': 'definitions',
        'historyNote': 'history_notes',
        'editorialNote': 'editorial_notes',
        'changeNote': 'change_notes',
        'example': 'examples'
    }
    for n in c.notes:
        doc['notes'].setdefault(ntypemap[n.type], []).append(nt_renderer(n))
    return doc

def _jsonld_source_renderer(c):
    doc = {
        'sources': []
    }
    def s_renderer(s):
        source = {
            'type': 'dct:BibliographicResource'
            'citations': [{
                'ct': s.citation
            }]
        }
        if s.markup is not None:
            source['citations'][0]['markup'] = s.markup
        return source
    for s in c.sources:
        doc['sources'].append(s_renderer(s))
    return doc

def jsonld_conceptscheme_dumper(provider):
    pass

