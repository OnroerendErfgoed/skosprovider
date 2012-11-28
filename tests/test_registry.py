# -*- coding: utf-8 -*-

import unittest

import os
import sys
sys.path.insert(0, os.path.abspath('..'))

from test_providers import trees

from skosprovider.registry import (
    Registry
    )

class RegistryTests(unittest.TestCase):
    def setUp(self):
        self.reg = Registry()
        self.prov = trees

    def tearDown(self):
        self.reg = None
        self.prov = None

    def test_empty_getProviders(self):
        self.assertEquals(self.reg.get_providers(),[])
        self.assertEquals(self.reg.get_providers(ids=[]),[])

    def test_empty_findConcepts(self):
        self.assertEquals(self.reg.find({}),[])

    def test_empty_getAllConcepts(self):
        self.assertEquals(self.reg.get_all(),[])

    def test_one_provider_getProviders(self):
        self.reg.register_provider(self.prov)
        self.assertEquals(self.reg.get_providers(),[self.prov])
        self.assertEquals(self.reg.get_providers(ids=['TREES']),[self.prov])

    def test_one_provider_getProvidersWithIds(self):
        self.reg.register_provider(self.prov)
        self.assertEquals(self.reg.get_providers(ids=['TREES']),[self.prov])
        self.assertEquals(self.reg.get_providers(),[self.prov])
        self.assertEquals(self.reg.get_providers(ids=['GEOGRAPHY']),[])


    def test_one_provider_findConcepts(self):
        self.reg.register_provider(self.prov)
        self.assertEquals(self.reg.find({'label': 'The Larch'}),
                          [{'id': 'TREES', 
                            'concepts': [{'id':1, 'label': 'De Lariks'}]}])

    def test_one_provider_findConceptsWithProviderid(self):
        self.reg.register_provider(self.prov)
        self.assertEquals(self.reg.find({'label': 'The Larch'},
                                                providers= ['TREES']),
                          [{'id': 'TREES', 
                              'concepts': [{'id': 1, 'label': 'De Lariks'}]}])
        self.assertEquals(self.reg.find({'label': 'The Larch'},
                                                providers= []),
                          [])

    def test_one_provider_getAllConcepts(self):
        self.reg.register_provider(self.prov)
        self.assertEquals(self.reg.get_all(),
                          [{'id': 'TREES', 
                              'concepts': [{'id': 1, 'label': 'De Lariks'},
                                           {'id': 2, 'label': 'De Paardekastanje'}]}])
