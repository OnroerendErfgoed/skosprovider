# -*- coding: utf-8 -*-

'''This module provides a registry for skos providers.

This registry helps us find providers during runtime. We can also apply some
operations to all or several providers at the same time.
'''
import logging

log = logging.getLogger(__name__)

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

    metadata = {}
    '''
    Dictionary containing metadata about this registry.
    '''

    instance_scope = 'single'
    '''
    Indicates how the registry is being used. Options:
        - single: The registry is part of a script or a single process. It can
          be assumed to be operational for the entire duration of the process
          and there are no threads involved.
        - threaded_global: The registry is part of a program that uses threads,
          such as a typical web application. It's attached to the global process
          and duplicated to threads, making it not thread safe. Proceed carefully
          with certain providers. Should generally only be used with
          applications that only use read-only providers that load all data in
          memory at startup and use no database connections or other kinds of
          sessions.
        - threaded_thread: The registry is part of a program that uses threads,
          such as a typical web application. It's attached to a thread, such as
          a web request. The registry is instantiated for this thread/request and
          dies with this thread/request. This is needed for providers such
          as the SQLAlchemyProvider. Providers that use database connections or
          other session handling code generally require this.
    '''

    def __init__(self, instance_scope='single', metadata={}):
        '''
        :param str instance_scope: Indicates how the registry was instantiated.
            Possible values: single, threaded_global, threaded_thread.
        :param dict metadata: Metadata essential to this registry. Possible
            metadata:

                * `catalog`: A :class:`dict` detailing the catalog all \
                    conceptschemes are part of. \
                    Currently the contents of the dictionary are undefined \
                    except for a :term:`uri` attribute that must be present.
                * `dataset`: A :class:`dict` detailing the dataset all \
                    conceptschemes are part of. \
                    Currently the contents of the dictionary are undefined \
                    except for a :term:`uri` attribute that must be present.
        '''
        self.providers = {}
        self.concept_scheme_uri_map = {}
        self.metadata = metadata
        if instance_scope not in ['single', 'threaded_global', 'threaded_thread']:
            raise ValueError('Invalid instance_scope.')
        self.instance_scope = instance_scope

    def get_metadata(self):
        '''Get some metadata on the registry it represents.

        :rtype: Dict.
        '''
        return self.metadata

    def register_provider(self, provider):
        '''
        Register a :class:`skosprovider.providers.VocabularyProvider`.

        :param skosprovider.providers.VocabularyProvider provider: The provider
            to register.
        :raises RegistryException: A provider with this id or uri has already
            been registered.
        '''
        if (
            provider.allowed_instance_scopes
            and self.instance_scope not in provider.allowed_instance_scopes
        ):
            raise RegistryException(
                'This provider does not support instance_scope %s' % self.instance_scope
            )
        if provider.get_vocabulary_id() in self.providers:
            raise RegistryException(
                'A provider with this id has already been registered.'
            )
        self.providers[provider.get_vocabulary_id()] = provider
        try:
            cs_uri = provider.get_vocabulary_uri()
        except AttributeError as e:
            log.error(e)
            # For providers not compatible with skosprovider >= 0.8.0
            log.warning(
                'New versions of skosprovider (>=0.8.0) require your provider '
                'to have a get_vocabulary_uri method. This fallback mechanism '
                'will be removed in version 2.0.0.'
            )
            cs_uri = provider.concept_scheme.uri
        if cs_uri in self.concept_scheme_uri_map:
            raise RegistryException(
                'A provider with URI %s has already been registered.' % cs_uri
            )
        self.concept_scheme_uri_map[cs_uri] = provider.get_vocabulary_id()

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
            try:
                cs_uri = p.get_vocabulary_uri()
            except AttributeError as e:
                log.error(e)
                # For providers not compatible with skosprovider >= 0.8.0
                log.warning(
                    'New versions of skosprovider (>=0.8.0) require your provider '
                    'to have a get_vocabulary_uri method. This fallback mechanism '
                    'will be removed in version 2.0.0.'
                )
                # For providers not compatible with skosprovider >= 0.8.0
                cs_uri = p.concept_scheme.uri
            del self.concept_scheme_uri_map[cs_uri]
            return p
        elif id in self.concept_scheme_uri_map:
            id = self.concept_scheme_uri_map[id]
            return self.remove_provider(id)
        else:
            return False

    def get_provider(self, id):
        '''
        Get a provider by id or :term:`URI`.

        :param str id: The identifier for the provider. This can either be the
            id with which it was registered or the :term:`URI` of the conceptscheme
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

        :param list ids: Only return providers with one of the Ids or :term:`URIs <URI>`.
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

            # Find anything that has a match with an external concept
            # If possible, display the results with a Dutch label.
            registry.find({
                'matches': {
                    'uri': 'http://id.python.org/different/types/of/trees/nr/1/the/larch'
                }}, language='nl')

            # Find anything that has a label of lariks with a close match to an external concept
            # If possible, display the results with a Dutch label.
            provider.find({
                'matches': {
                    'label': 'lariks',
                    'type': 'close',
                    'uri': 'http://id.python.org/different/types/of/trees/nr/1/the/larch'
                }}, language='nl')

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
