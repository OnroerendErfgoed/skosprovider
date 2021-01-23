# -*- coding: utf-8 -*-
'''
This module contains functions dealing with jsonld reading and writing.

.. versionadded:: 0.7.0
'''

from skosprovider.skos import (
    Concept,
    Collection,
    ConceptScheme,
    label
)

from skosprovider.utils import (
    extract_language,
    add_lang_to_html
)

import logging
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
    "concept_scheme": {
        "@id": "skos:inScheme",
        "@type": "@id"
    },
    "in_dataset": {
        "@id": "void:inDataset",
        "@type": "@id"
    },
    "top_concepts": {
        "@id": "skos:hasTopConcept",
        "@type": "@id"
    },
    "labels": "@nest",
    "notes": "@nest",
    "matches": "@nest",
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
    "editorial_notes": {
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
    "exact_matches": {
      "@id": "skos:exactMatch",
      "@type": "@id",
      "@container": "@set"
    },
    "close_matches": {
      "@id": "skos:closeMatch",
      "@type": "@id",
      "@container": "@set"
    },
    "broad_matches": {
      "@id": "skos:broadMatch",
      "@type": "@id",
      "@container": "@set"
    },
    "narrow_matches": {
      "@id": "skos:narrowMatch",
      "@type": "@id",
      "@container": "@set"
    },
    "related_matches": {
      "@id": "skos:relatedMatch",
      "@type": "@id",
      "@container": "@set"
    },
    "member_of": {
        "@reverse": "skos:member",
        "@type": "@id",
        "@container": "@set"
    },
    "members": {
        "@id": "skos:member",
        "@type": "@id",
        "@container": "@set"
    },
    "subordinate_arrays": {
        "@id": "iso-thes:subordinateArray",
        "@type": "@id",
        "@container": "@set"
    },
    "broader": {
        "@id": "skos:broader",
        "@type": "@id",
        "@container": "@set"
    },
    "narrower": {
        "@id": "skos:narrower",
        "@type": "@id",
        "@container": "@set"
    },
    "related": {
        "@id": "skos:related",
        "@type": "@id",
        "@container": "@set"
    },
    "languages": {
        "@id": "dct:language",
        "@type": "@id",
        "@container": "@set"
    }
}

def jsonld_dumper(provider, context = None, language = None):
    '''
    Dump a provider to a JSON-LD serialisable dictionary.

    :param skosprovider.providers.VocabularyProvider provider: The provider
        that wil be turned into a JSON-LD `dict`.
    :param str or dict context: Context as a dict or link to context file.
    :param string language: Language to render a single label in.

    :rtype: A `dict`
    '''
    if not language:
        language = provider.metadata.get('default_language', 'en')
    doc = {
        '@graph': []
    }
    if context:
        doc['@context'] = context
    doc['@graph'].append(jsonld_conceptscheme_dumper(
        provider, None,
        relations_profile = 'uri', language = language
        ))
    for c in provider.get_all():
        doc['@graph'].append(jsonld_c_dumper(
            provider, c['id'], None,
            relations_profile = 'uri', language = language
        ))
    return doc

def jsonld_c_dumper(provider, id, context = None, relations_profile =
        'partial', language = 'en'):
    '''
    Dump a concept or collection to a JSON-LD serialisable dictionary.

    :param skosprovider.providers.VocabularyProvider provider: The provider
        that contains the concept or collection.
    :param str or int id: Identifier of the concept to dump.
    :param str or dict context: Context as a dict or link to context file.
    :param str relations_profile: Either `partial` or `uri` to render links to
        other resources with some information or just a :term:`URI`.
    :param string language: Language to render a single label in.

    :rtype: A `dict`
    '''
    c = provider.get_by_id(id)
    doc = _jsonld_c_basic_renderer(c, language)
    if context:
        doc['@context'] = context
    if relations_profile == 'partial':
        doc['concept_scheme'] = _jsonld_cs_basic_renderer(c.concept_scheme, language)
    else:
        doc['concept_scheme'] = c.concept_scheme.uri
    dataset_uri = provider.get_metadata().get('dataset', {}).get('uri', None)
    if dataset_uri:
        doc['in_dataset'] = dataset_uri
    doc.update(_jsonld_labels_renderer(c))
    doc.update(_jsonld_notes_renderer(c))
    doc.update(_jsonld_sources_renderer(c))
    doc.update(_jsonld_member_of_renderer(c, provider, relations_profile, language))
    if c.type == 'concept':
        doc.update(_jsonld_matches_renderer(c))
        doc.update(_jsonld_broader_renderer(c, provider, relations_profile, language))
        doc.update(_jsonld_narrower_renderer(c, provider, relations_profile, language))
        doc.update(_jsonld_related_renderer(c, provider, relations_profile, language))
        doc.update(_jsonld_subordinate_arrays_renderer(c, provider, relations_profile, language))
    elif c.type == 'collection':
        doc['infer_concept_relations'] = True
        doc.update(_jsonld_members_renderer(c, provider, relations_profile, language))
        doc.update(_jsonld_superordinates_renderer(c, provider, relations_profile, language))
    return doc

def _jsonld_c_basic_renderer(c, language = 'en'):
    doc = {
        'id': c.id,
        'uri': c.uri,
        'type': c.type
    }
    label = c.label(language)
    if label:
        doc['label'] = label.label
    return doc

def _jsonld_cs_basic_renderer(cs, language = 'en'):
    doc = {
        'uri': cs.uri,
        'type': 'skos:ConceptScheme'
    }
    label = cs.label(language)
    if label:
        doc['label'] = label.label
    return doc

def _jsonld_labels_renderer(c):
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

def _jsonld_notes_renderer(c):
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
            note['nt'] = add_lang_to_html(note['nt'], language)
            note['@type'] = n.markup
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

def _jsonld_sources_renderer(c):
    doc = {
        'sources': []
    }
    def s_renderer(s):
        source = {
            'type': 'dct:BibliographicResource',
            'citations': [{
                'ct': s.citation
            }]
        }
        if s.markup is not None:
            source['citations'][0]['@type'] = s.markup
        return source
    for s in c.sources:
        doc['sources'].append(s_renderer(s))
    return doc

def _jsonld_matches_renderer(c):
    doc = {
        'matches': {}
    }
    for k,v in c.matches.items():
        doc['matches'].setdefault('%s_matches' % k, []).extend(v)
    return doc

def _jsonld_superordinates_renderer(c, provider, profile = 'partial', language = 'en'):
    return _jsonld_relation_renderer(c, provider, 'superordinates', profile, language)

def _jsonld_members_renderer(c, provider, profile = 'partial', language = 'en'):
    return _jsonld_relation_renderer(c, provider, 'members', profile, language)

def _jsonld_member_of_renderer(c, provider, profile = 'partial', language = 'en'):
    return _jsonld_relation_renderer(c, provider, 'member_of', profile, language)

def _jsonld_broader_renderer(c, provider, profile = 'partial', language = 'en'):
    return _jsonld_relation_renderer(c, provider, 'broader', profile, language)

def _jsonld_narrower_renderer(c, provider, profile = 'partial', language = 'en'):
    return _jsonld_relation_renderer(c, provider, 'narrower', profile, language)

def _jsonld_related_renderer(c, provider, profile = 'partial', language = 'en'):
    return _jsonld_relation_renderer(c, provider, 'related', profile, language)

def _jsonld_subordinate_arrays_renderer(c, provider, profile = 'partial', language = 'en'):
    return _jsonld_relation_renderer(c, provider, 'subordinate_arrays', profile, language)

def _jsonld_relation_renderer(c, provider, relation, profile = 'partial', language = 'en'):
    doc = {
        relation: []
    }
    for m in getattr(c, relation):
        relc = provider.get_by_id(m)
        if profile == 'partial':
            doc[relation].append(_jsonld_c_basic_renderer(relc, language))
        else:
            doc[relation].append(relc.uri)
    return doc

def _jsonld_topconcepts_renderer(provider, profile = 'partial'):
    doc = {
        'top_concepts': []
    }
    for c in provider.get_top_concepts():
        if profile == 'partial':
            doc['top_concepts'].append(c)
        else:
            doc['top_concepts'].append(c['uri'])
    return doc

def _jsonld_cs_languages_renderer(cs):
    doc = {
        'languages': []
    }
    for l in cs.languages:
        doc['languages'].append(l)
    return doc

def jsonld_conceptscheme_dumper(provider, context = None,
        relations_profile = 'partial', language = 'en'):
    '''
    Dump a conceptscheme to a JSON-LD serialisable dictionary.

    :param skosprovider.providers.VocabularyProvider provider: The provider
        that contains the conceptscheme.
    :param str or dict context: Context as a dict or link to context file.
    :param str relations_profile: Either `partial` or `uri` to render links to
        other resources with some information or just a :term:`URI`.
    :param string language: Language to render a single label in.

    :rtype: A `dict`
    '''
    cs = provider.concept_scheme
    doc = _jsonld_cs_basic_renderer(cs)
    if context:
        doc['@context'] = context
    dataset_uri = provider.get_metadata().get('dataset', {}).get('uri', None)
    if dataset_uri:
        doc['in_dataset'] = dataset_uri
    doc['id'] = provider.get_metadata()['id']
    doc.update(_jsonld_labels_renderer(cs))
    doc.update(_jsonld_notes_renderer(cs))
    doc.update(_jsonld_sources_renderer(cs))
    doc.update(_jsonld_cs_languages_renderer(cs))
    doc.update(_jsonld_topconcepts_renderer(provider, relations_profile))
    return doc
