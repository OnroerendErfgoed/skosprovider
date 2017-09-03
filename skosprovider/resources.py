# -*- coding: utf-8 -*-

'''This module provides support for handling resources.

Resources are things like database connections or request sessions that are

.. versionadded:: 0.7.0
'''

from zope.interface import Interface

class IResource(Interface):
    '''
    Basic interface all resourcekeys should inherit from.
    '''
    pass

