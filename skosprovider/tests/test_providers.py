# -*- coding: utf-8 -*-

import unittest

import warnings

from skosprovider.providers import (
    FlatDictionaryProvider,
    TreeDictionaryProvider
)

larch = {
    'id': '1',
    'labels': [
        {'type': 'prefLabel', 'language': 'en', 'label': 'The Larch'},
        {'type': 'prefLabel', 'language': 'nl', 'label': 'De Lariks'}
    ],
    'notes': [
        {'type': 'definition', 'language': 'en', 'note': 'A type of tree.'}
    ]
}

chestnut = {
    'id': '2',
    'labels': [
        {'type': 'prefLabel', 'language': 'en', 'label': 'The Chestnut'},
        {'type': 'altLabel', 'language': 'nl', 'label': 'De Paardekastanje'}
    ],
    'notes': [
        {
            'type': 'definition', 'language': 'en',
            'note': 'A different type of tree.'
        }
    ]
}

species = {
    'id': 3,
    'labels': [
        {'type': 'prefLabel', 'language': 'en', 'label': 'Trees by species'},
        {'type': 'prefLabel', 'language': 'nl', 'label': 'Bomen per soort'}
    ],
    'type': 'collection',
    'members': ['1', '2']
}

trees = FlatDictionaryProvider(
    {'id': 'TREES', 'default_language': 'nl'},
    [larch, chestnut, species]
)

world = {
    'id': '1',
    'labels': [
        {'type': 'prefLabel', 'language': 'en', 'label': 'World'}
    ],
    'narrower': [2, 3]
}

geo = TreeDictionaryProvider(
    {'id': 'GEOGRAPHY'},
    [
        world,
        {
            'id': 2,
            'labels': [{'type': 'prefLabel', 'language': 'en', 'label': 'Europe'}],
            'narrower': [4, 5], 'broader': [1]
        }, {
            'id': 3,
            'labels': [
                {'type': 'prefLabel', 'language': 'en', 'label': 'North-America'}
            ],
            'narrower': [6], 'broader': [1]
        }, {
            'id': 4,
            'labels': [
                {'type': 'prefLabel', 'language': 'en', 'label': 'Belgium'}
            ],
            'narrower': [7, 8, 9], 'broader': [2]
        }, {
            'id': 5,
            'labels': [
                {'type': 'prefLabel', 'language': 'en', 'label': 'United Kingdom'}
            ],
            'broader': [2]
        }, {
            'id': 6,
            'labels': [
                {
                    'type': 'prefLabel', 'language': 'en',
                    'label': 'United States of America'
                }
            ],
            'broader': [3]
        }, {
            'id': 7,
            'labels': [
                {'type': 'prefLabel', 'language': 'en', 'label': 'Flanders'}
            ],
            'broader': [4]
        }, {
            'id': 8,
            'labels': [
                {'type': 'prefLabel', 'language': 'en', 'label': 'Brussels'}
            ],
            'broader': [4]
        }, {
            'id': 9,
            'labels': [
                {'type': 'prefLabel', 'language': 'en', 'label': 'Wallonie'}
            ],
            'broader': [4]
        }, {
            'id': '333',
            'type': 'collection',
            'labels': [
                {'type': 'prefLabel', 'language': 'en', 'label': 'Places where dutch is spoken'}
            ],
            'members': ['4', '7', '8']
        }
    ]
)


class FlatDictionaryProviderTests(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_get_vocabulary_id(self):
        self.assertEquals('TREES', trees.get_vocabulary_id())

    def test_get_metadata(self):
        self.assertEquals(
            {'id': 'TREES', 'default_language': 'nl'},
            trees.get_metadata()
        )

    def test_get_by_id(self):
        lariks = trees.get_by_id(1)
        self.assertEqual(larch['id'], lariks['id'])
        self.assertEqual(larch['labels'], lariks['labels'])
        self.assertEqual(larch['notes'], lariks['notes'])

    def test_get_by_id_string(self):
        lariks = trees.get_by_id('1')
        self.assertEqual(larch['id'], lariks['id'])
        self.assertEqual(larch['labels'], lariks['labels'])
        self.assertEqual(larch['notes'], lariks['notes'])

    def test_get_by_id_is_type_agnostic(self):
        self.assertEqual(trees.get_by_id(1), trees.get_by_id('1'))

    def test_get_unexisting_by_id(self):
        self.assertEquals(False, trees.get_by_id(987654321))

    def test_expand_concept_deprecated(self):
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter('always')
            trees.expand_concept(1)
            self.assertEqual(1, len(w))
            self.assertEqual(w[-1].category, DeprecationWarning)

    def test_expand_concept(self):
        self.assertEquals(['1'], trees.expand(1))

    def test_expand_unexisting(self):
        self.assertEquals(False, trees.expand(987654321))

    def test_expand_collection(self):
        self.assertEquals(['1', '2'], trees.expand(3))

    def test_get_all(self):
        self.assertEquals(trees.get_all(),
                          [{'id': '1', 'label': 'De Lariks'},
                           {'id': '2', 'label': 'De Paardekastanje'},
                           {'id': 3, 'label': 'Bomen per soort'}])

    def test_get_all_default_language(self):
        trees = FlatDictionaryProvider(
            {'id': 'TREES'},
            [larch]
        )
        self.assertEquals(trees.get_all(),
                          [{'id': '1', 'label': 'The Larch'}])

    def test_get_all_english(self):
        self.assertEquals(trees.get_all(language='en'),
                          [{'id': '1', 'label': 'The Larch'},
                           {'id': '2', 'label': 'The Chestnut'},
                           {'id': 3, 'label': 'Trees by species'}])

    def test_find_larch(self):
        self.assertEqual(
            trees.find({'label': 'The Larch'}),
            [{'id': '1', 'label': 'De Lariks'}]
        )

    def test_find_lar(self):
        self.assertEqual(
            trees.find({'label': 'The Lar'}),
            [{'id': '1', 'label': 'De Lariks'}]
        )

    def test_find_empty_label(self):
        self.assertEqual(
            trees.find({'label': ''}),
            []
        )

    def test_find_all(self):
        self.assertEqual(
            trees.find({}),
            trees.get_all()
        )


class TreeDictionaryProviderTests(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_get_vocabulary_id(self):
        self.assertEqual('GEOGRAPHY', geo.get_vocabulary_id())

    def test_get_metadata(self):
        self.assertEqual({'id': 'GEOGRAPHY'}, geo.get_metadata())

    def test_get_by_id(self):
        wereld = geo.get_by_id(1)
        self.assertEqual(world['id'], wereld['id'])
        self.assertEqual(world['labels'], wereld['labels'])
        self.assertEqual(world['narrower'], wereld['narrower'])

    def test_get_colletion_by_id(self):
        dutch_speaking = geo.get_by_id(333)
        self.assertEqual('333', dutch_speaking.id)
        self.assertEqual(['4', '7', '8'], dutch_speaking.members)

    def test_expand(self):
        self.assertTrue(set([4, 7, 8, 9]), set(geo.expand(4)))

    def test_expand_string(self):
        self.assertTrue(set([4, 7, 8, 9]), set(geo.expand('4')))

    def test_expand_unexisting(self):
        self.assertEqual(False, geo.expand(987654321))

    def test_expand_collection(self):
        self.assertTrue(set([4, 7, 8, 9]), set(geo.expand(333)))
