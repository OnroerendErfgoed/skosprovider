# -*- coding: utf-8 -*-

'''This module provides an abstraction of controlled vocabularies.

This abstraction allows our application to work with both local and remote
vocabs (be they SOAP, REST, XML-RPC or something else).

The basic idea is that we have skos providers. Each provider is an instance
of a VocabularyProvider. The same class can thus be reused with different
configurations to handle different vocabs.
'''

import abc

import warnings

from .skos import (
    Concept,
    Collection
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

        :rtype: String or number.
        '''
        return self.metadata.get('id')

    def get_metadata(self):
        '''Get some metadata on the provider or the vocab it represents.

        :rtype: Dict.
        '''
        return self.metadata

    @abc.abstractmethod
    def get_by_id(self, id):
        '''Get all information on a concept or collection, based on id.

        Providers should assume that all id's passed are strings. If a provider 
        knows that internally it uses numeric identifiers, it's up to the 
        provider to do the typecasting. Generally, this should not be done by
        changing the id's themselves (eg. from int to str), but by doing the
        id comparisons in a type agnostic way.

        Since this method could be used to find both concepts and collections,
        it's assumed that there are no id collisions between concepts and 
        collections.

        :rtype: :class:`skosprovider.skos.Concept` or 
            :class:`skosprovider.skos.Collection` or `False` if the concept or
            collection is unknown to the provider.
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

        :param query: A dict that can be used to express a query. The following 
            keys are permitted:

            * `label`: Search for something with this label value.
            * `type`: Limit the search to certain SKOS elements. If not present
                `all` is assumed:
            
                * `concept`: Only return :class:`skosprovider.skos.Concept` instances.
                * `collection`: Only return :class:`skosprovider.skos.Collection` instances.
                * `all`: Return both :class:`skosprovider.skos.Concept` and
                    :class:`skosprovider.skos.Collection` instances.

        :returns: A list of concepts that match the query. For each concept an
            id is present and a label. The label is determined by looking at the
            `**kwargs` parameter, the default language of the provider and falls
            back to `en` if nothing is present.
        :rtype: A list of dicts. Each dict contains at least an `id` and a 
            `label` key.
        '''

    def expand_concept(self, id):
        '''Expand a concept to the concept itself and all it's narrower
        concepts.

        This method has been deprectad, please use :meth:`expand`.

        :param id: A concept id.
        :rtype: A list of id's or `False` if the concept doesn't exist.
        '''
        warnings.warn(
            'expand_concept has been deprecated, please use expand',
            DeprecationWarning
        )
        return self.expand(id)

    def expand(self, id):
        '''Expand a concept or collection to all it's narrower
        concepts.

        This method should recurse and also return narrower concepts
        of narrower concepts.

        If the id passed belongs to a :class:`skosprovider.skos.Concept`, 
        the id of the concept itself should be include in the return value. 

        If the id passed belongs to a :class:`skosprovider.skos.Collection`,
        the id of the collection itself must not be present in the return value.
        In this case the return value includes all the member concepts and their
        narrower concepts.

        :param id: A concept or collection id.
        :rtype: A list of id's or `False` if the concept or collection doesn't 
            exist.
        '''


class FlatDictionaryProvider(VocabularyProvider):
    '''A simple vocab provider that use a python list of dicts.

    The provider expects a list with elements that are dicts that represent
    the concepts. This provider assumes there is no hierarchy
    (broader/narrower) or relations between concepts.
    '''

    def __init__(self, metadata, list):
        super(FlatDictionaryProvider, self).__init__(metadata)
        self.list = [self._from_dict(c) for c in list]

    def _from_dict(self, data):
        if 'type' in data and data['type'] == 'collection':
            return Collection(
                data['id'],
                data['labels'] if 'labels' in data else [],
                data['members'] if 'members' in data else []
            )
        else:
            return Concept(
                data['id'],
                data['labels'] if 'labels' in data else [],
                data['notes'] if 'notes' in data else []
            )

    def get_by_id(self, id):
        id = str(id)
        for c in self.list:
            if str(c.id) == id:
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
                [l['label'].find(query['label']) >= 0 for l in c.labels]
            ):
                ret.append({'id': c['id'], 'label': c.label(language).label})
        return ret

    def get_all(self, **kwargs):
        language = self._get_language(**kwargs)
        ret = []
        for c in self.list:
            ret.append({'id': c.id, 'label': c.label(language).label})
        return ret

    def expand(self, id):
        id = str(id)
        for c in self.list:
            if str(c.id) == id: 
                if isinstance(c, Concept):
                    return [c.id]
                elif isinstance(c, Collection):
                    return c.members
        return False


class TreeDictionaryProvider(FlatDictionaryProvider):
    '''An extension of the :class:`FlatDictionaryProvider` that can handle 
    hierarchical data.

    This provider can check if a concept has narrower concepts and use that to
    expand a certain concept.
    '''

    def _from_dict(self, data):
        if 'type' in data and data['type'] == 'collection':
            return Collection(
                data['id'],
                data['labels'] if 'labels' in data else [],
                data['members'] if 'members' in data else []
            )
        else:
            return Concept(
                data['id'],
                data['labels'] if 'labels' in data else [],
                data['notes'] if 'notes' in data else [],
                data['broader'] if 'broader' in data else [],
                data['narrower'] if 'narrower' in data else [],
                data['related'] if 'related' in data else [],
            )

    def expand(self, id):
        id = str(id)
        for c in self.list:
            if str(c.id) == id:
                if isinstance(c, Concept):
                    ret = set([c.id])
                    if 'narrower' in c:
                        for cid in c['narrower']:
                            ret |= set(self.expand(cid))
                    return list(ret)
                elif isinstance(c, Collection):
                    ret = set([])
                    for m in c.members:
                        ret |= set(self.expand(m))
                    return list(ret)
        return False
