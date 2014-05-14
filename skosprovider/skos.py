# -*- coding: utf-8 -*-

'''
This module contains a read-only model of the :term:`SKOS` specification.

.. versionadded:: 0.2.0
'''

from __future__ import unicode_literals

import collections


class Label:
    '''
    A :term:`SKOS` Label.
    '''

    label = None
    '''
    The label itself (eg. `churches`, `trees`, `Spitfires`, ...)
    '''

    type = "prefLabel"
    '''
    The type of this label ( `prefLabel`, `altLabel`, `hiddenLabel`).
    '''

    language = None
    '''
    The language the label is in (eg. `en`, `en-US`, `nl`, `nl-BE`).
    '''

    valid_types=['prefLabel', 'altLabel', 'hiddenLabel']
    '''
    The valid types for a label
    '''

    def __init__(self, label, type="prefLabel", language=None):
        self.label = label
        self.type = type
        self.language = language

    def __eq__(self, other):
        return self.__dict__ == (other if type(other) == dict else other.__dict__)

    def __ne__(self, other):
        return not self == other

    def __getitem__(self, item):
        if item in self.__dict__.keys():
            return self.__dict__[item]

    @staticmethod
    def is_valid_type(type):
        '''
        Check if the argument is a valid SKOS label type.

        :param string type: The type to be checked.
        '''
        return type in Label.valid_types


class Note:
    '''
    A :term:`SKOS` Note.
    '''

    note = None
    '''The note itself'''

    type = "note"
    '''
    The type of this note ( `note`, `definition`, `scopeNote`, ...).
    '''

    language = None
    '''
    The language the label is in (eg. `en`, `en-US`, `nl`, `nl-BE`).
    '''

    valid_types=[
            'note',
            'changeNote',
            'definition',
            'editorialNote',
            'example',
            'historyNote',
            'scopeNote'
        ]
    '''
    The valid types for a note
    '''

    def __init__(self, note, type="note", language=None):
        self.note = note
        self.type = type
        self.language = language

    def __eq__(self, other):
        return self.__dict__ == (other if type(other) == dict else other.__dict__)

    def __ne__(self, other):
        return not self == other

    @staticmethod
    def is_valid_type(type):
        '''
        Check if the argument is a valid SKOS note type.

        :param string type: The type to be checked.
        '''
        return type in Note.valid_types


class ConceptScheme:
    '''
    A :term:`SKOS` ConceptScheme.

    :param string uri: A :term:`URI` for this conceptscheme.
    :param list labels: A list of :class:`skosprovider.skos.Label` instances.
    '''

    uri = None
    '''A :term:`URI` for this conceptscheme.'''

    labels = []
    '''A list of labels for this conceptscheme.'''

    def __init__(self, uri, labels=[]):
        self.uri = uri
        self.labels = labels

    def label(self, language='any'):
        '''
        Provide a single label for this conceptscheme.

        This uses the :func:`label` function to determine which label to
        return.

        :param string language: The preferred language to receive the label in.
        :rtype: :class:`skosprovider.skos.Label` or False if no labels was found.
        '''
        return label(self.labels, language)


class Concept(collections.Mapping):
    '''
    A :term:`SKOS` Concept.
    '''

    id = None
    '''An id for this Concept within a vocabulary

    eg. 12345
    '''

    uri = None
    '''A proper uri for this Concept

    eg. `http://id.example.com/skos/trees/1`
    '''

    type = 'concept'
    '''The type of this concept or collection.

    eg. 'concept'
    '''

    def __init__(self, id, uri=None,
                 labels=[], notes=[],
                 broader=[], narrower=[], related=[],
                 member_of=[]):
        self.id = id
        self.uri = uri
        self.type = 'concept'
        self.labels = [dict_to_label(l) for l in labels]
        self.notes = [dict_to_note(n) for n in notes]
        self.broader = broader
        self.narrower = narrower
        self.related = related
        self.member_of = member_of

    def __getitem__(self, item):
        if item in self.__dict__.keys():
            return self.__dict__[item]

    def __iter__(self):
        return iter(self.__dict__)

    def __len__(self):
        return len(self.__dict__)

    def label(self, language='any'):
        '''
        Provide a single label for this concept.

        This uses the :func:`label` function to determine which label to return.

        :param string language: The preferred language to receive the label in.
        :rtype: :class:`skosprovider.skos.Label` or False if no labels was found.
        '''
        return label(self.labels, language)


class Collection:
    '''
    A :term:`SKOS` Collection.
    '''

    id = None
    '''An id for this Collection within a vocabulary'''

    uri = None
    '''A proper uri for this Collection'''

    type = 'collection'
    '''The type of this concept or collection.

    eg. 'collection'
    '''

    labels = []
    '''A :class:`lst` of :class:`skosprovider.skos.label` instances.'''

    members = []
    '''A :class:`lst` of concept ids.'''

    member_of = []
    '''A :class:`lst` of concept or collection ids.'''

    def __init__(self, id, uri=None, labels=[], members=[], member_of=[]):
        self.id = id
        self.uri = uri
        self.type = 'collection'
        self.labels = [dict_to_label(l) for l in labels]
        self.members = members
        self.member_of = member_of

    def label(self, language='any'):
        '''
        Provide a single label for this collection.

        This uses the :func:`label` function to determine which label to return.

        :param string language: The preferred language to receive the label in.µ
        :rtype: :class:`skosprovider.skos.Label` or False if no labels was found.
        '''
        return label(self.labels, language)


def label(labels=[], language='any'):
    '''
    Provide a label for a list of labels.

    The items in the list of labels are assumed to be either instances of
    :class:`Label`, or dicts with at least the key `label` in them. These will
    be passed to the :func:`dict_to_label` function.

    This method tries to find a label by looking if there's
    a pref label for the specified language. If there's no pref label,
    it looks for an alt label. It disregards hidden labels.

    If language 'any' was specified, all labels will be considered,
    regardless of language.

    To find a label without a specified language, pass `None` as language.

    If a language or None was specified, and no label could be found, this
    method will automatically try to find a label in some other language.

    Finally, if no label could be found, None is returned.
    '''
    alt = None
    for l in labels:
        l = dict_to_label(l)
        if language == 'any' or l.language == language:
            if l.type == 'prefLabel':
                return l
            if alt is None and l.type == 'altLabel':
                alt = l
    if alt is not None:
        return alt
    elif language != 'any':
        return label(labels, 'any')
    else:
        return None


def dict_to_label(dict):
    '''
    Transform a dict with keys `label`, `type` and `language` into a
    :class:`Label`.

    If the argument passed is already a :class:`Label`, this method just
    returns the argument.
    '''
    if isinstance(dict, Label):
        return dict
    else:
        return Label(
            dict['label'],
            dict['type'] if 'type' in dict else 'prefLabel',
            dict['language'] if 'language' in dict else None
        )


def dict_to_note(dict):
    '''
    Transform a dict with keys `note`, `type` and `language` into a
    :class:`Note`.

    If the argument passed is already a :class:`Note`, this method just returns
    the argument.
    '''
    if isinstance(dict, Note):
        return dict
    else:
        return Note(
            dict['note'],
            dict['type'] if 'type' in dict else 'note',
            dict['language'] if 'language' in dict else None
        )
