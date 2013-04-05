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

    @staticmethod
    def is_valid_type(type):
        '''
        Check if the argument is a valid SKOS label type.
        '''
        return type in ['prefLabel', 'altLabel', 'hiddenLabel']


class ConceptScheme:
    '''
    A SKOS ConceptScheme.
    '''
    pass


class Concept(collections.Mapping):
    '''
    A SKOS Concept.
    '''
    
    def __init__(self, id, labels=[], notes=[], broader=[], narrower=[]):
        self.id = id
        self.labels = labels
        self.notes = notes
        self.broader = broader
        self.narrower = narrower

    def __getitem__(self, item):
        if item in self.__dict__.keys():
            return self.__dict__[item]

    def __iter__(self):
        return iter(self.__dict__)

    def __len__(self):
        return len(self.__dict__)


class Collection:
    '''
    A SKOS Collection.
    '''
    pass
