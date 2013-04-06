# -*- coding: utf-8 -*-

import collections

class Label:
    '''
    A SKOS Label.
    '''

    def __init__(self, label, type="prefLabel", language = None):
        self.label = label
        self.type = type
        self.language = language

    def __eq__(self, other):
        return self.__dict__ == other.__dict__ 

    def __ne__(self, other):
        return not self == other

    @staticmethod
    def is_valid_type(type):
        '''
        Check if the argument is a valid SKOS label type.
        '''
        return type in ['prefLabel', 'altLabel', 'hiddenLabel']


class Note:
    '''
    A SKOS Note.
    '''

    def __init__(self, note, type="note", language = None):
        self.note = note
        self.type = type
        self.language = language

    def __eq__(self, other):
        return self.__dict__ == other.__dict__ 

    def __ne__(self, other):
        return not self == other

    @staticmethod
    def is_valid_type(type):
        '''
        Check if the argument is a valid SKOS note type.
        '''
        return type in [
            'note', 
            'changeNote', 
            'definition',
            'editorialNote',
            'example',
            'historyNote',
            'scopeNote'
        ]


class ConceptScheme:
    '''
    A SKOS ConceptScheme.
    '''
    
    def __init__(self, id, labels = []):
        self.id = id
        self.labels = labels

    def label(self, language = 'any'):
        return label(self.labels, language)


class Concept(collections.Mapping):
    '''
    A SKOS Concept.
    '''
    
    def __init__(
            self, id, 
            labels=[], notes=[], 
            broader=[], narrower=[], related=[]
        ):
        self.id = id
        self.labels = labels
        self.notes = notes
        self.broader = broader
        self.narrower = narrower
        self.related = related

    def __getitem__(self, item):
        if item in self.__dict__.keys():
            return self.__dict__[item]

    def __iter__(self):
        return iter(self.__dict__)

    def __len__(self):
        return len(self.__dict__)

    def label(self, language = 'any'):
        return label(self.labels, language)

class Collection:
    '''
    A SKOS Collection.
    '''
    
    def __init__(self, id, labels = []):
        self.id = id
        self.labels = labels

    def label(self, language = 'any'):
        return label(self.labels, language)


def label(labels = [], language = 'any'):
    '''
    Provide a label for this concept.

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
