# -*- coding: utf-8 -*-

import unittest

import os
import sys
sys.path.insert(0, os.path.abspath('..'))

from skosprovider.providers import (
    FlatDictionaryProvider,
    TreeDictionaryProvider
)

larch = {
    'id': 1,
    'labels': [
        {'type': 'pref', 'lang': 'en', 'label': 'The Larch'},
        {'type': 'pref', 'lang': 'nl', 'label': 'De Lariks'}
    ],
    'notes': [
        {'type': 'definition', 'lang': 'en', 'note': 'A type of tree.'}
    ]
}

chestnut = {
    'id': 2,
    'labels': [
        {'type': 'pref', 'lang': 'en', 'label': 'The Chestnut'},
        {'type': 'alt', 'lang': 'nl', 'label': 'De Paardekastanje'}
    ],
    'notes': [
        {
            'type': 'definition', 'lang': 'en',
            'note': 'A different type of tree.'
        }
    ]
}

trees = FlatDictionaryProvider(
    {'id': 'TREES', 'default_language': 'nl'},
    [larch, chestnut]
)

world = {
    'id': 1,
    'labels': [
        {'type': 'pref', 'lang': 'en', 'label': 'World'}
    ],
    'narrower': [2, 3]
}

geo = TreeDictionaryProvider(
    {'id': 'GEOGRAPHY'},
    [
        world,
        {
            'id': 2,
            'labels': [{'type': 'pref', 'lang': 'en', 'label': 'Europe'}],
            'narrower': [4, 5], 'broader': [1]
        }, {
            'id': 3,
            'labels': [
                {'type': 'pref', 'lang': 'en', 'label': 'North-America'}
            ],
            'narrower': [6], 'broader': [1]
        }, {
            'id': 4,
            'labels': [
                {'type': 'pref', 'lang': 'en', 'label': 'Belgium'}
            ],
            'narrower': [7, 8, 9], 'broader': [2]
        }, {
            'id': 5,
            'labels': [
                {'type': 'pref', 'lang': 'en', 'label': 'United Kingdom'}
            ],
            'broader': [2]
        }, {
            'id': 6,
            'labels': [
                {
                    'type': 'pref', 'lang': 'en',
                    'label': 'United States of America'
                }
            ],
            'broader': [3]
        }, {
            'id': 7,
            'labels': [
                {'type': 'pref', 'lang': 'en', 'label': 'Flanders'}
            ],
            'broader': [4]
        }, {
            'id': 8,
            'labels': [
                {'type': 'pref', 'lang': 'en', 'label': 'Brussels'}
            ],
            'broader': [4]
        }, {
            'id': 9,
            'labels': [
                {'type': 'pref', 'lang': 'en', 'label': 'Wallonie'}
            ],
            'broader': [4]
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
        self.assertEquals(larch, trees.get_by_id(1))

    def test_get_unexisting_by_id(self):
        self.assertEquals(False, trees.get_by_id(987654321))

    def test_expand_concept(self):
        self.assertEquals([1], trees.expand_concept(1))

    def test_expand_unexisting_concept(self):
        self.assertEquals(False, trees.expand_concept(987654321))

    def test_get_all(self):
        self.assertEquals(trees.get_all(),
                          [{'id': 1, 'label': 'De Lariks'},
                           {'id': 2, 'label': 'De Paardekastanje'}])

    def test_get_all_default_language(self):
        trees = FlatDictionaryProvider(
            {'id': 'TREES'},
            [larch]
        )
        self.assertEquals(trees.get_all(),
                          [{'id': 1, 'label': 'The Larch'}])

    def test_get_all_english(self):
        self.assertEquals(trees.get_all(language='en'),
                          [{'id': 1, 'label': 'The Larch'},
                           {'id': 2, 'label': 'The Chestnut'}])


class TreeDictionaryProviderTests(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_get_vocabulary_id(self):
        self.assertEquals('GEOGRAPHY', geo.get_vocabulary_id())

    def test_get_metadata(self):
        self.assertEquals({'id': 'GEOGRAPHY'}, geo.get_metadata())

    def test_get_by_id(self):
        self.assertEquals(world, geo.get_by_id(1))

    def test_expand_concept(self):
        self.assertEquals([4, 7, 8, 9], geo.expand_concept(4))

    def test_expand_unexisting_concept(self):
        self.assertEquals(False, geo.expand_concept(987654321))
