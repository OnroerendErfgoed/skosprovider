# -*- coding: utf-8 -*-

'''This module provides custom exceptions for skos providers.

.. versionadded:: 0.5.0
'''


class ProviderUnavailableException(Exception):
    '''
    This exception can be raised by a provider if it's unable to provide
    the thesaurus. This can occur when an underlying resource is unavailable
    (database connection, webservice, ...). The message should contain some
    more information about the problem.
    '''

    def __init__(self, message):
        '''
        :param message: More information about the exception.
        '''
        self.message = message

    def __repr__(self):
        return self.message
