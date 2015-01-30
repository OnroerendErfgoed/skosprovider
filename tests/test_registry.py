# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import unittest

from test_providers import (
    larch,
    chestnut,
    species,
    trees,
    geo
)

from skosprovider.registry import (
    Registry,
    RegistryException
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
        self.assertFalse(self.reg.get_provider('http://id.trees.org'))

    def test_empty_findConcepts(self):
        self.assertEquals(self.reg.find({}), [])

    def test_empty_getAllConcepts(self):
        self.assertEquals(self.reg.get_all(), [])

    def test_one_provider_register_provider(self):
        self.reg.register_provider(self.prov)
        self.assertEquals(self.reg.get_provider('TREES'), self.prov)
        self.assertEquals(
            self.reg.get_provider('http://id.trees.org'),
            self.prov
        )
        self.reg.register_provider(self.prov2)
        self.assertEquals(self.reg.get_provider('GEOGRAPHY'), self.prov2)
        self.assertEquals(
            self.reg.get_provider('urn:x-skosprovider:geography'),
            self.prov2
        )

    def test_one_provider_register_double_provider(self):
        self.reg.register_provider(self.prov)
        self.assertEquals(self.reg.get_provider('TREES'), self.prov)
        self.assertRaises(
            RegistryException,
            self.reg.register_provider,
            self.prov
        )

    def test_one_provider_removeProvider(self):
        self.reg.register_provider(self.prov)
        self.assertEquals(self.reg.get_provider('TREES'), self.prov)
        self.reg.remove_provider('TREES')
        self.assertFalse(self.reg.get_provider('TREES'))

    def test_one_provider_removeProviderWithUri(self):
        self.reg.register_provider(self.prov)
        self.assertEquals(self.reg.get_provider('TREES'), self.prov)
        self.reg.remove_provider('http://id.trees.org')
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

    def test_one_provider_getProvidersWithUris(self):
        self.reg.register_provider(self.prov)
        self.assertEquals(self.reg.get_providers(ids=['http://id.trees.org']), [self.prov])
        self.assertEquals(self.reg.get_providers(), [self.prov])
        self.assertEquals(self.reg.get_providers(ids=['urn:x-skosprovider:geography']), [])

    def test_one_provider_getProvidersWithSubject(self):
        self.reg.register_provider(self.prov)
        self.assertEquals(self.reg.get_providers(subject='something'), [])
        self.assertEquals(self.reg.get_providers(subject='biology'), [self.prov])

    def test_one_provider_getPoviderWithId(self):
        self.reg.register_provider(self.prov)
        self.assertEquals(self.reg.get_provider('TREES'), self.prov)

    def test_one_provider_getPoviderWithUri(self):
        self.reg.register_provider(self.prov)
        self.assertEquals(self.reg.get_provider('http://id.trees.org'), self.prov)

    def test_one_provider_findConcepts(self):
        self.reg.register_provider(self.prov)
        self.assertEquals(
            self.reg.find({'label': 'The Larch'}),
            [
                {
                    'id': 'TREES',
                    'concepts': [
                        {
                            'id': '1',
                            'uri': 'http://id.trees.org/1',
                            'type': 'concept',
                            'label': 'De Lariks'
                        }
                    ]
                }
            ]
        )

    def test_one_provider_getConceptByUri(self):
        self.reg.register_provider(self.prov)
        c = self.reg.get_by_uri('http://id.trees.org/1')
        self.assertEqual(c.id, '1')
        self.assertEqual(c.uri, 'http://id.trees.org/1')

    def test_one_provider_getConceptByUriDifferentFromConceptScheme(self):
        from skosprovider.skos import ConceptScheme
        from skosprovider.providers import DictionaryProvider
        trees = DictionaryProvider(
            {'id': 'TREES', 'default_language': 'nl'},
            [larch, chestnut, species],
            concept_scheme=ConceptScheme('urn:something')
        )
        self.reg.register_provider(trees)
        c = self.reg.get_by_uri('http://id.trees.org/1')
        self.assertEqual(c.id, '1')
        self.assertEqual(c.uri, 'http://id.trees.org/1')

    def test_one_provider_getConceptByUnexistingUri(self):
        self.reg.register_provider(self.prov)
        c = self.reg.get_by_uri('http://id.thingy.com/123456')
        self.assertFalse(c)

    def test_one_provider_findConceptsWithProviderid(self):
        self.reg.register_provider(self.prov)
        self.assertEquals(
            self.reg.find({'label': 'The Larch'}, providers=['TREES']),
            [
                {
                    'id': 'TREES',
                    'concepts': [
                        {
                            'id': '1',
                            'uri': 'http://id.trees.org/1',
                            'type': 'concept',
                            'label': 'De Lariks'
                        }
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
                        {
                            'id': '1',
                            'uri': 'http://id.trees.org/1',
                            'type': 'concept',
                            'label': 'De Lariks'
                        }, {
                            'id': '2',
                            'uri': 'http://id.trees.org/2',
                            'type': 'concept',
                            'label': 'De Paardekastanje'
                        }, {
                            'id': 3,
                            'uri': 'http://id.trees.org/3',
                            'type': 'collection',
                            'label': 'Bomen per soort'
                        }
                    ]
                }
            ]
        )

    def test_two_providers_findConceptsWithProviderIdAndUri(self):
        self.reg.register_provider(self.prov2)
        self.reg.register_provider(self.prov)
        self.assertEquals(
            self.reg.find({'label': 'The Larch'}, providers=['TREES']),
            self.reg.find({'label': 'The Larch'}, providers=['http://id.trees.org']),
        )

    def test_two_providers_findConceptsProvidersDictionarySyntax(self):
        self.reg.register_provider(self.prov2)
        self.reg.register_provider(self.prov)
        self.assertEquals(
            self.reg.find({'label': 'The Larch'}, providers=['TREES']),
            self.reg.find({'label': 'The Larch'}, providers={'ids': ['http://id.trees.org']}),
        )

    def test_two_providers_findConceptsProvidersDictionarySyntax(self):
        self.reg.register_provider(self.prov2)
        self.reg.register_provider(self.prov)
        self.assertEquals(
            self.reg.find({'label': 'The Larch'}, providers=['TREES']),
            self.reg.find({'label': 'The Larch'}, providers={'ids': ['http://id.trees.org']}),
        )

    def test_one_provider_findConceptsWithSubject(self):
        self.reg.register_provider(self.prov)
        provs = self.reg.get_providers(subject='biology')
        res = [{'id': p.get_vocabulary_id(), 'concepts': p.find({})} for p in provs]
        self.assertEquals(
            res,
            self.reg.find({},subject='biology')
        )

    def test_one_provider_findConceptsWithSubject_language_en(self):
        self.reg.register_provider(self.prov)
        provs = self.reg.get_providers(subject='biology')
        res = [{'id': p.get_vocabulary_id(), 'concepts': p.find({}, language='en')} for p in provs]
        self.assertEquals(
            res,
            self.reg.find({},subject='biology', language='en')
        )

    def test_one_provider_findConceptsWithSubject_language_nl(self):
        self.reg.register_provider(self.prov)
        provs = self.reg.get_providers(subject='biology')
        res = [{'id': p.get_vocabulary_id(), 'concepts': p.find({})} for p in provs]
        self.assertEquals(
            res,
            self.reg.find({},subject='biology', language='nl')
        )
