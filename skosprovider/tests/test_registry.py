# -*- coding: utf-8 -*-

import unittest

from test_providers import (
    trees,
    geo
)

from skosprovider.registry import (
    Registry
)


class RegistryTests(unittest.TestCase):
    def setUp(self):
        self.reg = Registry()
        self.prov = trees
        self.prov2 = geo

    def tearDown(self):
        self.reg = None
        self.prov = None
        self.prov2 = None

    def test_empty_register_provider(self):
        self.reg.register_provider(self.prov)
        self.assertEquals(self.reg.get_provider('TREES'), self.prov)

    def test_empty_register_removeProvider(self):
        self.assertFalse(self.reg.remove_provider('TREES'))

    def test_empty_getProviders(self):
        self.assertEquals(self.reg.get_providers(), [])
        self.assertEquals(self.reg.get_providers(ids=[]), [])

    def test_empty_getProviderById(self):
        self.assertFalse(self.reg.get_provider('TREES'))

    def test_empty_findConcepts(self):
        self.assertEquals(self.reg.find({}), [])

    def test_empty_getAllConcepts(self):
        self.assertEquals(self.reg.get_all(), [])

    def test_one_provider_register_provider(self):
        self.reg.register_provider(self.prov)
        self.assertEquals(self.reg.get_provider('TREES'), self.prov)
        self.reg.register_provider(self.prov2)
        self.assertEquals(self.reg.get_provider('GEOGRAPHY'), self.prov2)

    def test_one_provider_register_double_provider(self):
        self.reg.register_provider(self.prov)
        self.assertEquals(self.reg.get_provider('TREES'), self.prov)
        self.assertRaises(Exception, self.reg.register_provider, self.prov)

    def test_one_provider_removeProvider(self):
        self.reg.register_provider(self.prov)
        self.assertEquals(self.reg.get_provider('TREES'), self.prov)
        self.reg.remove_provider('TREES')
        self.assertFalse(self.reg.get_provider('TREES'))

    def test_one_provider_getProviders(self):
        self.reg.register_provider(self.prov)
        self.assertEquals(self.reg.get_providers(), [self.prov])
        self.assertEquals(self.reg.get_providers(ids=['TREES']), [self.prov])

    def test_one_provider_getProvidersWithIds(self):
        self.reg.register_provider(self.prov)
        self.assertEquals(self.reg.get_providers(ids=['TREES']), [self.prov])
        self.assertEquals(self.reg.get_providers(), [self.prov])
        self.assertEquals(self.reg.get_providers(ids=['GEOGRAPHY']), [])

    def test_one_provider_getPoviderWithId(self):
        self.reg.register_provider(self.prov)
        self.assertEquals(self.reg.get_provider('TREES'), self.prov)

    def test_one_provider_findConcepts(self):
        self.reg.register_provider(self.prov)
        self.assertEquals(self.reg.find({'label': 'The Larch'}),
                          [{'id': 'TREES',
                            'concepts': [{'id':1, 'label': 'De Lariks'}]}])

    def test_one_provider_findConceptsWithProviderid(self):
        self.reg.register_provider(self.prov)
        self.assertEquals(
            self.reg.find({'label': 'The Larch'}, providers=['TREES']),
            [
                {
                    'id': 'TREES',
                    'concepts': [
                        {'id': 1, 'label': 'De Lariks'}
                    ]
                }
            ]
        )
        self.assertEquals(
            self.reg.find({'label': 'The Larch'}, providers=[]),
            []
        )

    def test_one_provider_getAllConcepts(self):
        self.reg.register_provider(self.prov)
        self.assertEquals(
            self.reg.get_all(),
            [
                {
                    'id': 'TREES',
                    'concepts': [
                        {'id': 1, 'label': 'De Lariks'},
                        {'id': 2, 'label': 'De Paardekastanje'}
                    ]
                }
            ]
        )
