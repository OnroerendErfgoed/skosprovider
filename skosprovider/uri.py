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
    def generate(self, id):
        '''
        Generate a :term:`URI` for this id.

        :param id: An id.
        '''

class UriPatternGenerator(UriGenerator):
    '''
    Generate a :term:`URI` based on a simple pattern.
    '''

    def __init__(self, pattern):
        self.pattern = pattern

    def generate(self, id):
        return self.pattern % id


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

    def generate(self, id):
        return (self.pattern % (self.vocabulary_id, id)).lower()
