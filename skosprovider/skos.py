# -*- coding: utf-8 -*-

import collections


class ConceptScheme:
    pass


class Concept(collections.Mapping):
    
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
    pass
