# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import unittest

from skosprovider.utils import (
    dict_dumper
)

from skosprovider.providers import (
    DictionaryProvider,
)

from test_providers import (
    larch,
    species,
    trees,
    geo
)


class DictDumperTest(unittest.TestCase):

    def setUp(self):
        self.larch_dump = {
            'id': '1',
            'uri': 'http://id.trees.org/1',
            'type': 'concept',
            'labels': [
                {'type': 'prefLabel', 'language': 'en', 'label': 'The Larch'},
                {'type': 'prefLabel', 'language': 'nl', 'label': 'De Lariks'}
            ],
            'notes': [
                {'type': 'definition',
                 'language': 'en',
                 'note': 'A type of tree.',
                 'markup': None}
            ],
            'narrower': [],
            'broader': [],
            'related': [],
            'member_of': ['3'],
            'subordinate_arrays': [],
            'matches': {
                'close': [
                    'http://id.python.org/different/types/of/trees/nr/1/the/larch'
                ],
                'exact': [],
                'related': [],
                'narrow': [],
                'broad': []
            }
        }
        self.chestnut_dump = {
            'id': '2',
            'uri': 'http://id.trees.org/2',
            'type': 'concept',
            'labels': [
                {'type': 'prefLabel',
                 'language': 'en',
                 'label': 'The Chestnut'},
                {'type': 'altLabel',
                 'language': 'nl',
                 'label': 'De Paardekastanje'},
                {'type': 'altLabel',
                 'language': 'fr',
                 'label': 'la châtaigne'}
            ],
            'notes': [
                {
                    'type': 'definition', 'language': 'en',
                    'note': 'A different type of tree.', 'markup': None
                }
            ],
            'narrower': [],
            'broader': [],
            'related': [],
            'member_of': ['3'],
            'subordinate_arrays': [],
            'matches': {
                'close': [],
                'exact': [],
                'related': [
                    'http://id.python.org/different/types/of/trees/nr/17/the/other/chestnut'
                ],
                'narrow': [],
                'broad': []
            }
        }
        self.species_dump = {
            'id': 3,
            'uri': 'http://id.trees.org/3',
            'labels': [
                {'type': 'prefLabel', 'language': 'en', 'label': 'Trees by species'},
                {'type': 'prefLabel', 'language': 'nl', 'label': 'Bomen per soort'}
            ],
            'type': 'collection',
            'notes': [
                {
                    'type': 'editorialNote',
                    'language': 'en',
                    'note': 'As seen in <em>How to Recognise Different Types of Trees from Quite a Long Way Away</em>.',
                    'markup': 'HTML'
                }
            ],
            'members': ['1', '2'],
            'member_of': [],
            'superordinates': []
        }
        self.world_dump = {
            'id': '1',
            'uri': 'urn:x-skosprovider:geography:1',
            'type': 'concept',
            'labels': [
                {'type': 'prefLabel', 'language': 'en', 'label': 'World'}
            ],
            'notes': [
            ],
            'narrower': [2, 3],
            'broader': [],
            'related': [],
            'member_of': [],
            'matches': {
                'close': [],
                'exact': [],
                'related': [],
                'narrow': [],
                'broad': []
            },
            'subordinate_arrays': []
        }

    def tearDown(self):
        del self.larch_dump
        del self.chestnut_dump
        del self.world_dump

    def _get_flat_provider(self, dictionary):
        return DictionaryProvider({'id': 'TEST'}, dictionary)

    def _get_tree_provider(self, dictionary):
        return DictionaryProvider({'id': 'TEST'}, dictionary)

    def testEmptyProvider(self):
        pv = self._get_flat_provider([])
        self.assertEqual([], dict_dumper(pv))

    def testOneElementProvider(self):
        pv = self._get_flat_provider([larch])
        self.assertEqual([self.larch_dump], dict_dumper(pv))

    def testFlatProvider(self):
        self.assertEqual(
            [self.larch_dump, self.chestnut_dump, self.species_dump],
            dict_dumper(trees)
        )

    def testEmptyTreeprovider(self):
        pv = self._get_tree_provider([])
        self.assertEqual(
            [],
            dict_dumper(pv)
        )

    def testTreeProvider(self):
        dump = dict_dumper(geo)
        self.assertIsInstance(dump, list)
        for c in dump:
            self.assertIsInstance(c, dict)
            self.assertIn('type', c)
            self.assertIn('id', c)
        self.assertIn(
            self.world_dump,
            dump
        )

    def testFlatProviderRoundTrip(self):
        dump = dict_dumper(trees)
        dump2 = dict_dumper(self._get_flat_provider(dict_dumper(trees)))
        self.assertEqual(dump, dump2)

    def testTreeProviderRoundTrip(self):
        dump = dict_dumper(geo)
        dump2 = dict_dumper(self._get_tree_provider(dict_dumper(geo)))
        self.assertEqual(dump, dump2)
