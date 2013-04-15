# -*- coding: utf-8 -*-

'''This module provides an abstraction of controlled vocabularies.

This abstraction allows our application to work with both local and remote
vocabs (be they SOAP, REST, XML-RPC or something else).

The basic idea is that we have skos providers. Each provider is an instance
of a VocabularyProvider. The same class can thus be reused with different
configurations to handle different vocabs.
'''

import abc

from .skos import (
    Concept
)


class VocabularyProvider:
    '''An interface that all vocabulary providers must follow.
    '''

    __metaclass__ = abc.ABCMeta

    def __init__(self, metadata):
        '''Create a new provider and register some metadata.

        Expected metadata:
         * id: A unique identifier for the vocabulary. Required.
         * default_language: Used to determine what language to use when
           returning labels if no language is specified.
        '''
        self.metadata = metadata

    def _get_language(self, **kwargs):
        '''Determine what language to render labels in.
        '''
        if 'language' in kwargs:
            return kwargs.get('language')
        else:
            if 'default_language' in self.metadata:
                return self.metadata.get('default_language')
            else:
                return 'en'

    def get_vocabulary_id(self):
        '''Get an identifier for the vocabulary.

        Returns a string or number.
        '''
        return self.metadata.get('id')

    def get_metadata(self):
        '''Get some metadata on the provider or the vocab it represents.

        Returns a dict.
        '''
        return self.metadata

    @abc.abstractmethod
    def get_by_id(self, id):
        '''Get all information on a concept, based on id.

        Providers should assume that all id's passed are strings. If a provider 
        knows that internally it uses numeric identifiers, it's up to the 
        provider to do the typecasting. Generally, this should not be done by
        changing the id's themselves (eg. from int to str), but by doing the
        id comparisons in a type agnostic way.

        Returns a :class:`skosprovider.skos.Concept` or `False` if the concept 
        is unknown to the provider.
        '''

    @abc.abstractmethod
    def get_all(self, **kwargs):
        '''Returns all concepts in this provider.

        Returns a list of all concepts. For each concept an
        id is present and a label. The label is determined by looking at the
        `**kwargs` parameter, the default language of the provider and falls
        back to `en` if nothing is present.
        '''

    @abc.abstractmethod
    def find(self, query, **kwargs):
        '''Find concepts that match a certain query.

        Currently query is expected to be a dict, so that complex queries can
        be passed. Currently only searching on label (eg. {'label': 'tree'}) is
        expected.

        Returns a list of concepts that match the query. For each concept an
        id is present and a label. The label is determined by looking at the
        `**kwargs` parameter, the default language of the provider and falls
        back to `en` if nothing is present.
        '''

    def expand_concept(self, id):
        '''Expand a concept to the concept itself and all it's narrower
        concepts.

        This method should recurse and also return narrower concepts
        of narrower concepts.

        Returns a list of all id's that are narrower concepts or the concept
        itself.
        '''


class FlatDictionaryProvider(VocabularyProvider):
    '''A simple vocab provider that use a python list of dicts.

    The provider expects a list with elements that are dicts that represent
    the concepts. This provider assumeis there is no hierarchy
    (broader/narrower) or relations between concepts.
    '''

    def __init__(self, metadata, list):
        super(FlatDictionaryProvider, self).__init__(metadata)
        self.list = [self._concept_from_dict(c) for c in list]

    def _concept_from_dict(self, data):
        return Concept(
            data['id'],
            data['labels'] if 'labels' in data else [],
            data['notes'] if 'notes' in data else []
        )

    def get_by_id(self, id):
        id = str(id)
        for c in self.list:
            if str(c['id']) == id:
                return c
        return False

    def find(self, query, **kwargs):
        if 'label' not in query:
            return self.get_all(**kwargs)
        if query['label'] == '':
            return []
        language = self._get_language(**kwargs)
        ret = []
        for c in self.list:
            if any(
                [l['label'].find(query['label']) >= 0 for l in c['labels']]
            ):
                ret.append({'id': c['id'], 'label': c.label(language).label})
        return ret

    def get_all(self, **kwargs):
        language = self._get_language(**kwargs)
        ret = []
        for c in self.list:
            ret.append({'id': c['id'], 'label': c.label(language).label})
        return ret

    def expand_concept(self, id):
        id = str(id)
        for c in self.list:
            if str(c['id']) == id:
                return [c['id']]
        return False


class TreeDictionaryProvider(FlatDictionaryProvider):
    '''An extension of the :class:`FlatDictionaryProvider` that can handle 
    hierarchical data.

    This provider can check if a concept has narrower concepts and use that to
    expand a certain concept.
    '''

    def _concept_from_dict(self, data):
        return Concept(
            data['id'],
            data['labels'] if 'labels' in data else [],
            data['notes'] if 'notes' in data else [],
            data['broader'] if 'broader' in data else [],
            data['narrower'] if 'narrower' in data else [],
            data['related'] if 'related' in data else [],
        )

    def expand_concept(self, id):
        id = str(id)
        for c in self.list:
            if str(c['id']) == id:
                ret = [c['id']]
                if 'narrower' in c:
                    for cid in c['narrower']:
                        ret = ret + self.expand_concept(cid)
                return ret
        return False
