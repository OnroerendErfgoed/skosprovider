# -*- coding: utf-8 -*-
'''
This module provides utilities for working with :term:`URIS <URI>`.

.. versionadded:: 0.3.0
'''

import abc


class UriGenerator(object):
    '''
    An abstract class for generating URIs.
    '''

    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def generate(self, **kwargs):
        '''
        Generate a :term:`URI` based on parameters passed.
        '''


class UriPatternGenerator(UriGenerator):
    '''
    Generate a :term:`URI` based on a simple pattern.
    '''

    def __init__(self, pattern):
        self.pattern = pattern

    def generate(self, **kwargs):
        '''
        Generate a :term:`URI` based on parameters passed.

        :param id: The id of the concept or collection.
        :rtype: string
        '''
        return self.pattern % kwargs['id']


class DefaultUrnGenerator(UriGenerator):
    '''
    Generate a :term:`URN` specific to skosprovider.

    Used for providers that do not implement a specific :class:`UriGenerator`.

    :param vocabulary_id: An identifier for the vocabulary we're generating
        URIs for.
    '''

    pattern = 'urn:x-skosprovider:%s:%s'

    def __init__(self, vocabulary_id):
        self.vocabulary_id = vocabulary_id

    def generate(self, **kwargs):
        '''
        Generate a :term:`URI` based on parameters passed.

        :param id: The id of the concept or collection.
        :rtype: string
        '''
        return (self.pattern % (self.vocabulary_id, kwargs['id'])).lower()


class TypedUrnGenerator(DefaultUrnGenerator):
    '''
    Generate a :term:`URN` specific to skosprovider that contains a type.

    :param vocabulary_id: An identifier for the vocabulary we're generating
        URIs for.
    '''

    pattern = 'urn:x-skosprovider:%s:%s:%s'

    def __init__(self, vocabulary_id):
        self.vocabulary_id = vocabulary_id

    def generate(self, **kwargs):
        '''
        Generate a :term:`URI` based on parameters passed.

        :param id: The id of the concept or collection.
        :param type: What we're generating a :term:`URI` for: `concept`
            or `collection`.
        :rtype: string
        '''
        if kwargs['type'] not in ['concept', 'collection']:
            raise ValueError('Type %s is invalid' % kwargs['type'])
        return (
            self.pattern % (self.vocabulary_id, kwargs['type'], kwargs['id'])
        ).lower()
