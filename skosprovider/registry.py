# -*- coding: utf-8 -*-

'''This module provides a registry for skos providers.

This registry helps us find providers during runtime. We can also apply some
operations to all or several providers at the same time.
'''

from __future__ import unicode_literals


class RegistryException(Exception):
    pass


class Registry:
    '''
    This registry collects all skos providers.
    '''

    def __init__(self):
        self.providers = {}

    def register_provider(self, provider):
        '''
        Register a :class:`skosprovider.providers.VocabularyProvider`.

        :param skosprovider.providers.VocabularyProvider provider: The provider
            to register.
        '''
        if provider.get_vocabulary_id() in self.providers:
            raise RegistryException(
                'A provider with this id has already been registered.')
        self.providers[provider.get_vocabulary_id()] = provider

    def remove_provider(self, id):
        '''
        Remove the provider with the given id.

        :param str id: The identifier for the provider.
        :returns: A :class:`skosprovider.providers.VocabularyProvider` or
            False if the id is unknown.
        '''
        if id in self.providers:
            p = self.providers.get(id, False)
            del self.providers[id]
            return p
        else:
            return False

    def get_provider(self, id):
        '''
        Get a provider by id.

        :param str id: The identifier for the provider.
        :returns: A :class:`skosprovider.providers.VocabularyProvider`
            or False if the id is unknown.
        '''
        return self.providers.get(id, False)

    def get_providers(self, **kwargs):
        '''Get all providers registered.

        If keyword ids is present, get only the providers with this id.
        '''
        if not 'ids' in kwargs:
            return list(self.providers.values())
        else:
            return [self.providers[k] for k in self.providers.keys()
                    if k in kwargs['ids']]

    def find(self, query, **kwargs):
        '''Launch a query across all or a selection of providers.

        .. code-block:: python

            # Find anything that has a label of church in any provider.
            registry.find({'label': 'church'})

            # Find anything that has a label of church the BUILDINGS provider.
            registry.find({'label': 'church'}, providers=['BUILIDINGS'])

        :param list providers: Optional. If present, it should be a list of
            skosprovider id's. The query will then only be passed to
            these providers.
        :param dict query: The query parameters that will be passed on to each
            :meth:`~skosprovider.providers.VocabularyProvider.find` method of
            the selected.
            :class:`providers <skosprovider.providers.VocabularyProvider>`.
        :returns: a list of :class:`dict`.
            Each dict has two keys: id and concepts.
        '''
        if not 'providers' in kwargs:
            providers = self.get_providers()
        else:
            providers = self.get_providers(ids=kwargs['providers'])
        return [{'id': p.get_vocabulary_id(), 'concepts': p.find(query)}
                for p in providers]

    def get_all(self):
        '''Get all concepts from all providers.

        :returns: a list of :class:`dict`.
            Each dict has two keys: id and concepts.
        '''
        return [{'id': p.get_vocabulary_id(), 'concepts': p.get_all()}
                for p in self.providers.values()]

    def get_by_uri(self, uri):
        '''Get a concept or collection by its uri.

        Returns a single concept or collection if one exists with this uri.
        Returns False otherwise.

        :param string uri: The uri to find a concept or collection for.
        :rtype: :class:`skosprovider.skos.Concept` or
            :class:`skosprovider.skos.Collection`
        '''
        for p in self.providers.values():
            c = p.get_by_uri(uri)
            if c:
                return c
        return False
