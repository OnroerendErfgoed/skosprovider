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
        '''Returns all concepts and collections in this provider.

        Returns a list of concepts and collections. For each an
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

            * `label`: Search for something with this label value. An empty \
                label is equal to searching for all concepts.
            * `type`: Limit the search to certain SKOS elements. If not \
                present `all` is assumed:

                * `concept`: Only return :class:`skosprovider.skos.Concept` \
                    instances.
                * `collection`: Only return \
                    :class:`skosprovider.skos.Collection` instances.
                * `all`: Return both :class:`skosprovider.skos.Concept` and \
                    :class:`skosprovider.skos.Collection` instances.
            * `collection`: Search only for concepts belonging to a certain \
                collection. This argument should be a dict with two keys:

                * `id`: The id of a collection. Required.
                * `depth`: Can be `members` or `all`. Optional. If not \
                    present, `members` is assumed, meaning only concepts or \
                    collections that are a direct member of the collection \
                    should be considered. When set to `all`, this method \
                    should return concepts and collections that are a member \
                    of the collection or are a narrower concept of a member \
                    of the collection.

        :returns: A list of concepts that match the query. For each concept an
            id is present and a label. The label is determined by looking at
            the `**kwargs` parameter, the default language of the provider
            and falls back to `en` if nothing is present.
        :rtype: A list of dicts. Each dict contains at least an `id` and a
            `label` key.
        '''

    def expand_concept(self, id):
        '''Expand a concept to the concept itself and all it's narrower
        concepts.

        .. deprecated:: 0.2.0
            This method has been deprectad, please use :meth:`expand`.

        :param id: A concept id.
        :rtype: A list of id's or `False` if the concept doesn't exist.
        '''
        warnings.warn(
            'expand_concept has been deprecated, please use expand',
            DeprecationWarning
        )
        return self.expand(id)

    @abc.abstractmethod
    def expand(self, id):
        '''Expand a concept or collection to all it's narrower
        concepts.

        This method should recurse and also return narrower concepts
        of narrower concepts.

        If the id passed belongs to a :class:`skosprovider.skos.Concept`,
        the id of the concept itself should be include in the return value.

        If the id passed belongs to a :class:`skosprovider.skos.Collection`,
        the id of the collection itself must not be present in the return value
        In this case the return value includes all the member concepts and
        their narrower concepts.

        :param id: A concept or collection id.
        :rtype: A list of id's or `False` if the concept or collection doesn't
            exist.
        '''


class MemoryProvider(VocabularyProvider):
    '''
    An provider that keeps everything in memory.

    The data is passed in the constructor of this provider as a list of
    :class:`skosprovider.skos.Concept` and :class:`skosprovider.skos.Collection`
    instances.
    '''

    case_insensitive = True
    '''
    Is searching for labels case insensitive?

    By default a search for a label is done case insensitive. Older versions of 
    this provider were case sensitive. If this behaviour is decided, this can 
    be triggered by providing a `case_insensitive` keyword to the constructor.
    '''

    def __init__(self, metadata, list, **kwargs):
        '''
        :param dict metadata: A dictionary with keywords like language.
        :param list list: A list of :class:`skosprovider.skos.Concept` and 
            :class:`skosprovider.skos.Collection` instances.
        :param Boolean case_insensitive: Should searching for labels be done 
            case-insensitive?
        '''
        super(MemoryProvider, self).__init__(metadata)
        self.list = list
        if 'case_insensitive' in kwargs:
            self.case_insensitive = kwargs['case_insensitive']

    def get_by_id(self, id):
        id = str(id)
        for c in self.list:
            if str(c.id) == id:
                return c
        return False

    def find(self, query, **kwargs):
        ret = []
        for c in self.list:
            include = True
            if include and 'type' in query and query['type'] != 'all':
                if query['type'] == 'concept' and not isinstance(c, Concept):
                    include = False
                elif query['type'] == 'collection' and not isinstance(c, Collection):
                    include = False
            if include and 'label' in query:
                if not self.case_insensitive:
                    finder = lambda l, query: l['label'].find(query['label'])
                else:
                    finder = lambda l, query: l['label'].upper().find(query['label'].upper())
                if not any([finder(l, query) >= 0 for l in c.labels]):
                    include = False
            if include and 'collection' in query:
                coll = self.get_by_id(query['collection']['id'])
                if not coll or not isinstance(coll, Collection):
                    raise ValueError(
                        'You are searching for items in an unexisting collection.'
                    )
                else:
                    if 'depth' in query['collection'] and query['collection']['depth'] == 'all':
                        members = self.expand(coll.id)
                    else:
                        members = coll.members
                    members = [str(id) for id in members]
                    if not str(c.id) in members:
                        include = False
            if include:
                ret.append(self._get_find_dict(c, **kwargs))
        return ret

    def _get_find_dict(self, c, **kwargs):
        '''
        Return a dict that can be used in the return list of the :meth:`find` 
        method.

        :param c: A :class:`skosprovider.skos.Concept` or 
            :class:`skosprovider.skos.Collection`.
        :rtype: dict
        '''
        language = self._get_language(**kwargs)
        return {'id': c.id, 'label': c.label(language).label}

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


class DictionaryProvider(MemoryProvider):
    '''A simple vocab provider that use a python list of dicts.

    The provider expects a list with elements that are dicts that represent
    the concepts.
    '''

    def __init__(self, metadata, list, **kwargs):
        list = [self._from_dict(c) for c in list]
        super(DictionaryProvider, self).__init__(metadata, list, **kwargs)

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


class SimpleCsvProvider(MemoryProvider):
    '''
    A provider that reads a simple csv format into memory.

    The supported csv format looks like this:
    <id>,<preflabel>,<note>

    .. versionadded:: 0.2.0
    '''

    def __init__(self, metadata, reader):
        '''
        :param metadata: A metadata dictionary.
        :param reader: A csv reader.
        '''
        list = [self._from_row(row) for row in reader]
        super(SimpleCsvProvider, self).__init__(metadata, list)

    def _from_row(self, row):
        id = row[0]
        labels = [{'label': row[1], 'type':'prefLabel'}]
        if row[2]:
            notes = [{'note': row[2], 'type':'note'}]
        else:
            notes = []
        return Concept(
            id=id,
            labels=labels,
            notes=notes
        )


class FlatDictionaryProvider(DictionaryProvider):
    '''
    A provider that uses a list of dicts.

    .. deprecated:: 0.2.0
        This provider has been deprecated and will be removed in 
        version 0.3.0. Please use :class:`DictionaryProvider`.
    '''
    def __init__(self, metadata, list):
        warnings.warn(
            'FlatDictionaryProvider has been deprecated, \
            please use DictionaryProvider',
            DeprecationWarning
        )
        super(FlatDictionaryProvider, self).__init__(metadata, list)


class TreeDictionaryProvider(DictionaryProvider):
    '''
    A provider that uses a list of dicts and supports hierarchies.

    .. deprecated:: 0.2.0
        This provider has been deprecated and will be removed in 
        version 0.3.0. Please use :class:`DictionaryProvider`.
    '''

    def __init__(self, metadata, list):
        warnings.warn(
            'TreeDictionaryProvider has been deprecated, \
            please use DictionaryProvider',
            DeprecationWarning
        )
        super(TreeDictionaryProvider, self).__init__(metadata, list)
