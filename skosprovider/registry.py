# -*- coding: utf-8 -*-

'''This module provides a registry for skos providers.

This registry helps us find providers during runtime. We can also apply some
operations to all or several providers at the same time.
'''

from __future__ import unicode_literals

from .uri import is_uri


class RegistryException(Exception):
    pass


class Registry:
    '''
    This registry collects all skos providers.
    '''

    providers = {}
    '''
    Dictionary containing all providers, keyed by id.
    '''

    concept_scheme_uri_map = {}
    '''
    Dictionary mapping concept scheme uri's to vocabulary id's.
    '''

    def __init__(self):
        self.providers = {}
        self.concept_scheme_uri_map = {}

    def register_provider(self, provider):
        '''
        Register a :class:`skosprovider.providers.VocabularyProvider`.

        :param skosprovider.providers.VocabularyProvider provider: The provider
            to register.
        :raises RegistryException: A provider with this id or uri has already 
            been registered.
        '''
        if provider.get_vocabulary_id() in self.providers:
            raise RegistryException(
                'A provider with this id has already been registered.'
            )
        self.providers[provider.get_vocabulary_id()] = provider
        if provider.concept_scheme.uri in self.concept_scheme_uri_map:
            raise RegistryException(
                'A provider with URI %s has already been registered.' % provider.concept_scheme.uri
            )
        self.concept_scheme_uri_map[provider.concept_scheme.uri] = provider.get_vocabulary_id()

    def remove_provider(self, id):
        '''
        Remove the provider with the given id or :term:`URI`.

        :param str id: The identifier for the provider.
        :returns: A :class:`skosprovider.providers.VocabularyProvider` or
            `False` if the id is unknown.
        '''
        if id in self.providers:
            p = self.providers.get(id, False)
            del self.providers[id]
            del self.concept_scheme_uri_map[p.concept_scheme.uri]
            return p
        elif id in self.concept_scheme_uri_map:
            id = self.concept_scheme_uri_map[id]
            return self.remove_provider(id)
        else:
            return False

    def get_provider(self, id):
        '''
        Get a provider by id or :term:`uri`.

        :param str id: The identifier for the provider. This can either be the
            id with which it was registered or the :term:`uri` of the conceptscheme
            that the provider services.
        :returns: A :class:`skosprovider.providers.VocabularyProvider`
            or `False` if the id or uri is unknown.
        '''
        if id in self.providers:
            return self.providers.get(id, False)
        elif is_uri(id) and id in self.concept_scheme_uri_map:
            return self.providers.get(self.concept_scheme_uri_map[id], False)
        return False

    def get_providers(self, **kwargs):
        '''Get all providers registered.

        If keyword `ids` is present, get only the providers with these ids.

        If keys `subject` is present, get only the providers that have this subject.

        .. code-block:: python

           # Get all providers with subject 'biology'
           registry.get_providers(subject='biology')

           # Get all providers with id 1 or 2
           registry.get_providers(ids=[1,2])

           # Get all providers with id 1 or 2 and subject 'biology'
           registry.get_providers(ids=[1,2], subject='biology']

        :param list ids: Only return providers with one of the Ids or :term:`URIs <uri>`.
        :param str subject: Only return providers with this subject.
        :returns: A list of :class:`providers <skosprovider.providers.VocabularyProvider>`
        '''
        if 'ids' in kwargs:
            ids = [self.concept_scheme_uri_map.get(id, id) for id in kwargs['ids']]
            providers = [
                self.providers[k] for k in self.providers.keys() if k in ids
            ]
        else:
            providers = list(self.providers.values())
        if 'subject' in kwargs:
            providers = [p for p in providers if kwargs['subject'] in p.metadata['subject']]
        return providers

    def find(self, query, **kwargs):
        '''Launch a query across all or a selection of providers.

        .. code-block:: python

            # Find anything that has a label of church in any provider.
            registry.find({'label': 'church'})

            # Find anything that has a label of church with the BUILDINGS provider.
            # Attention, this syntax was deprecated in version 0.3.0
            registry.find({'label': 'church'}, providers=['BUILDINGS'])

            # Find anything that has a label of church with the BUILDINGS provider.
            registry.find({'label': 'church'}, providers={'ids': ['BUILDINGS']})

            # Find anything that has a label of church with a provider
            # marked with the subject 'architecture'.
            registry.find({'label': 'church'}, providers={'subject': 'architecture'})

            # Find anything that has a label of church in any provider.
            # If possible, display the results with a Dutch label.
            registry.find({'label': 'church'}, language='nl')

        :param dict query: The query parameters that will be passed on to each
            :meth:`~skosprovider.providers.VocabularyProvider.find` method of
            the selected.
            :class:`providers <skosprovider.providers.VocabularyProvider>`.
        :param dict providers: Optional. If present, it should be a dictionary.
            This dictionary can contain any of the keyword arguments available
            to the :meth:`get_providers` method. The query will then only
            be passed to the providers confirming to these arguments.
        :param string language: Optional. If present, it should be a
            :term:`language-tag`. This language-tag is passed on to the
            underlying providers and used when selecting the label to display
            for each concept.
        :returns: a list of :class:`dict`.
            Each dict has two keys: id and concepts.
        '''
        if 'providers' not in kwargs:
            providers = self.get_providers()
        else:
            pargs = kwargs['providers']
            if isinstance(pargs, list):
                providers = self.get_providers(ids=pargs)
            else:
                providers = self.get_providers(**pargs)
        kwarguments = {}
        if 'language' in kwargs:
            kwarguments['language'] = kwargs['language']
        return [{'id': p.get_vocabulary_id(), 'concepts': p.find(query, **kwarguments)}
                for p in providers]

    def get_all(self, **kwargs):
        '''Get all concepts from all providers.

        .. code-block:: python

            # get all concepts in all providers.
            registry.get_all()

            # get all concepts in all providers.
            # If possible, display the results with a Dutch label.
            registry.get_all(language='nl')

        :param string language: Optional. If present, it should be a
            :term:`language-tag`. This language-tag is passed on to the
            underlying providers and used when selecting the label to display
            for each concept.

        :returns: a list of :class:`dict`.
            Each dict has two keys: id and concepts.
        '''
        kwarguments = {}
        if 'language' in kwargs:
            kwarguments['language'] = kwargs['language']
        return [{'id': p.get_vocabulary_id(), 'concepts': p.get_all(**kwarguments)}
                for p in self.providers.values()]

    def get_by_uri(self, uri):
        '''Get a concept or collection by its uri.

        Returns a single concept or collection if one exists with this uri.
        Returns False otherwise.

        :param string uri: The uri to find a concept or collection for.
        :raises ValueError: The uri is invalid.
        :rtype: :class:`skosprovider.skos.Concept` or
            :class:`skosprovider.skos.Collection`
        '''
        if not is_uri(uri):
            raise ValueError('%s is not a valid URI.' % uri)
        # Check if there's a provider that's more likely to have the URI
        csuris = [csuri for csuri in self.concept_scheme_uri_map.keys() if uri.startswith(csuri)]
        for csuri in csuris:
            c = self.get_provider(csuri).get_by_uri(uri)
            if c:
                return c
        # Check all providers
        for p in self.providers.values():
            c = p.get_by_uri(uri)
            if c:
                return c
        return False
