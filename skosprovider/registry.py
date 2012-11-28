# -*- coding: utf-8 -*-

'''This module provides a registry for skos providers.

This registry helps us find providers during runtime. We can also apply some
operations to all or several providers at the same time.
'''


class Registry:
    '''This registry collects all vocab providers.
    '''

    def __init__(self):
        self.providers = []

    def register_provider(self, provider):
        self.providers.append(provider)

    def get_providers(self, **kwargs):
        '''Get all providers registered.

        If keyword ids is present, get only the providers with this id.
        '''
        if not 'ids' in kwargs:
            return self.providers
        else:
            return [p for p in self.providers
                    if p.get_vocabulary_id() in kwargs['ids']]

    def find(self, query, **kwargs):
        '''Launch a query across all or a selection of providers.

        If the keyword providers is present, it should be a list of
        skos provider id's. The query will then only be passed to these providers.

        Returns a list of dicts. Each dict has two keys: id and concepts.
        '''
        if not 'providers' in kwargs:
            providers = self.get_providers()
        else:
            providers = self.get_providers(ids=kwargs['providers'])
        return [{'id': p.get_vocabulary_id(), 'concepts': p.find(query)}
                for p in providers]

    def get_all(self):
        '''Get all concepts from all providers.

        Returns a list of dicts. Each dict has two keys: id and concepts.
        '''
        return [{'id': p.get_vocabulary_id(), 'concepts': p.get_all()}
                for p in self.providers]
