# -*- coding: utf-8 -*-

try:
    import unittest2 as unittest
except ImportError:  # pragma NO COVER
    import unittest  # noqa

from skosprovider.utils import (
    dict_dumper
)

from skosprovider.providers import (
    FlatDictionaryProvider,
    TreeDictionaryProvider
)

from test_providers import (
    larch,
    chestnut,
    species,
    trees,
    geo
)

class DictDumperTest(unittest.TestCase):

    def setUp(self):
        self.larch_dump = {
            'id': '1',
            'type': 'concept',
            'labels': [
                {'type': 'prefLabel', 'language': 'en', 'label': 'The Larch'},
                {'type': 'prefLabel', 'language': 'nl', 'label': 'De Lariks'}
            ],
            'notes': [
                {'type': 'definition', 'language': 'en', 'note': 'A type of tree.'}
            ],
            'narrower': [],
            'broader': [],
            'related': []
        }

        self.chestnut_dump = {
            'id': '2',
            'type': 'concept',
            'labels': [
                {'type': 'prefLabel', 'language': 'en', 'label': 'The Chestnut'},
                {'type': 'altLabel', 'language': 'nl', 'label': 'De Paardekastanje'}
            ],
            'notes': [
                {
                    'type': 'definition', 'language': 'en',
                    'note': 'A different type of tree.'
                }
            ],
            'narrower': [],
            'broader': [],
            'related': []
        }
        self.world_dump = {
            'id': '1',
            'type': 'concept',
            'labels': [
                {'type': 'prefLabel', 'language': 'en', 'label': 'World'}
            ],
            'notes': [
            ],
            'narrower': [2, 3],
            'broader': [],
            'related': []
        }
            

    def tearDown(self):
        del self.larch_dump
        del self.chestnut_dump
        del self.world_dump

    def _get_flat_provider(self, dictionary):
        return FlatDictionaryProvider({'id': 'TEST'}, dictionary)

    def _get_tree_provider(self, dictionary):
        return TreeDictionaryProvider({'id': 'TEST'}, dictionary)

    def testEmptyProvider(self):
        pv = self._get_flat_provider([])
        self.assertEqual([], dict_dumper(pv))

    def testOneElementProvider(self):
        pv = self._get_flat_provider([larch])
        self.assertEqual([self.larch_dump],dict_dumper(pv))

    def testFlatProvider(self):
        self.assertEqual(
            [self.larch_dump, self.chestnut_dump, species],
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
