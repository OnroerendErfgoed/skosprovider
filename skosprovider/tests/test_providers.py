# -*- coding: utf-8 -*-

try:
    import unittest2 as unittest
except ImportError:  # pragma NO COVER
    import unittest  # noqa

import warnings

import os
import csv

from skosprovider.providers import (
    DictionaryProvider,
    SimpleCsvProvider
)

from skosprovider.skos import (
    Concept,
    Collection,
    Note
)

larch = {
    'id': '1',
    'uri': 'http://id.trees.org/1',
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
    'uri': 'http://id.trees.org/2',
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
    'uri': 'http://id.trees.org/3',
    'labels': [
        {'type': 'prefLabel', 'language': 'en', 'label': 'Trees by species'},
        {'type': 'prefLabel', 'language': 'nl', 'label': 'Bomen per soort'}
    ],
    'type': 'collection',
    'members': ['1', '2']
}

trees = DictionaryProvider(
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

geo = DictionaryProvider(
    {'id': 'GEOGRAPHY'},
    [
        world,
        {
            'id': 2,
            'labels': [
                {'type': 'prefLabel', 'language': 'en', 'label': 'Europe'}
            ],
            'narrower': [4, 5], 'broader': [1]
        }, {
            'id': 3,
            'labels': [
                {
                    'type': 'prefLabel', 'language': 'en',
                    'label': 'North-America'
                }
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
                {
                    'type': 'prefLabel', 'language': 'en',
                    'label': 'United Kingdom'
                }
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
                {
                    'type': 'prefLabel', 'language': 'en',
                    'label': 'Places where dutch is spoken'
                }
            ],
            'members': ['4', '7', '8']
        }
    ]
)


class TreesDictionaryProviderTests(unittest.TestCase):
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
        self.assertEqual(larch['uri'], lariks['uri'])
        self.assertEqual(larch['labels'], lariks['labels'])
        self.assertEqual(larch['notes'], lariks['notes'])

    def test_get_by_uri(self):
        lariks = trees.get_by_uri('http://id.trees.org/1')
        self.assertEqual('http://id.trees.org/1', lariks.uri)

    def test_get_by_id_string(self):
        lariks = trees.get_by_id('1')
        self.assertEqual(larch['id'], lariks['id'])
        self.assertEqual(larch['uri'], lariks['uri'])
        self.assertEqual(larch['labels'], lariks['labels'])
        self.assertEqual(larch['notes'], lariks['notes'])

    def test_get_by_id_is_type_agnostic(self):
        self.assertEqual(trees.get_by_id(1), trees.get_by_id('1'))

    def test_get_unexisting_by_id(self):
        self.assertFalse(trees.get_by_id(987654321))

    def test_get_unexisting_by_uri(self):
        self.assertFalse(trees.get_by_uri('urn:x-skosprovider:987654321'))

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
        trees = DictionaryProvider(
            {'id': 'TREES'},
            [larch]
        )
        self.assertEquals(trees.get_all(),
                          [{'id': '1', 'label': 'The Larch'}])

    def test_get_top_concepts_default_language(self):
        self.assertEquals(trees.get_top_concepts(),
                          [{'id': '1', 'label': 'De Lariks'},
                           {'id': '2', 'label': 'De Paardekastanje'}])

    def test_get_all_english(self):
        self.assertEquals(trees.get_all(language='en'),
                          [{'id': '1', 'label': 'The Larch'},
                           {'id': '2', 'label': 'The Chestnut'},
                           {'id': 3, 'label': 'Trees by species'}])

    def test_find_all(self):
        c = trees.find({'type': 'all'})
        self.assertEqual(3, len(c))

    def test_find_concepts(self):
        c = trees.find({'type': 'concept'})
        self.assertEqual(2, len(c))

    def test_find_collections(self):
        c = trees.find({'type': 'collection'})
        self.assertEqual(1, len(c))

    def test_find_larch(self):
        self.assertEqual(
            trees.find({'label': 'The Larch'}),
            [{'id': '1', 'label': 'De Lariks'}]
        )

    def test_find_The_Lar(self):
        self.assertEqual(
            trees.find({'label': 'The Lar'}),
            [{'id': '1', 'label': 'De Lariks'}]
        )

    def test_find_case_sensitive(self):
        trees = DictionaryProvider(
            {'id': 'TREES', 'default_language': 'nl'},
            [larch, chestnut, species],
            case_insensitive=False
        )
        self.assertEqual(
            trees.find({'label': 'The Lar'}),
            [{'id': '1', 'label': 'De Lariks'}]
        )
        self.assertEqual(
            trees.find({'label': 'lar'}),
            []
        )

    def test_find_empty_label(self):
        c = trees.find({'label': ''})
        self.assertEqual(3, len(c))

    def test_find_lar(self):
        self.assertEqual(
            trees.find({'label': 'lar'}),
            [{'id': '1', 'label': 'De Lariks'}]
        )

    def test_find_es(self):
        c = trees.find({'label': 'es'})
        self.assertEqual(2, len(c))

    def test_find_all_es(self):
        c = trees.find({'label': 'es', 'type': 'all'})
        self.assertEqual(2, len(c))

    def test_find_concepts_es(self):
        c = trees.find({'label': 'es', 'type': 'concept'})
        self.assertEqual(1, len(c))
        for cc in c:
            self.assertIsInstance(trees.get_by_id(cc['id']), Concept)

    def test_find_collections_es(self):
        c = trees.find({'label': 'es', 'type': 'collection'})
        self.assertEqual(1, len(c))
        for cc in c:
            self.assertIsInstance(trees.get_by_id(cc['id']), Collection)

    def test_find_no_arguments(self):
        self.assertEqual(
            trees.find({}),
            trees.get_all()
        )

    def test_find_in_collection(self):
        c = trees.find({'collection': {'id': 3}})
        self.assertEqual(2, len(c))
        for cc in c:
            self.assertIsInstance(trees.get_by_id(cc['id']), Concept)

    def test_find_in_collection_es(self):
        c = trees.find({'collection': {'id': 3}, 'label': 'es'})
        self.assertEqual(1, len(c))
        for cc in c:
            self.assertIsInstance(trees.get_by_id(cc['id']), Concept)

    def test_find_in_unexisting_collection(self):
        self.assertRaises(ValueError, trees.find, {'collection': {'id': 404}})

    def test_get_display_top(self):
        self.assertEqual(trees.get_top_concepts(), trees.get_top_display())

    def test_get_display_children_unexisting_concept(self):
        self.assertFalse(trees.get_children_display(404))

    def test_get_display_children_concept(self):
        self.assertEqual([],trees.get_children_display(1))
        self.assertEqual([],trees.get_children_display(2))

    def test_get_display_children_collection(self):
        self.assertEqual(
            [{'id': '1', 'label': 'De Lariks'},
             {'id': '2', 'label': 'De Paardekastanje'}],
            trees.get_children_display(3)
        )


class GeoDictionaryProviderTests(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_get_vocabulary_id(self):
        self.assertEqual('GEOGRAPHY', geo.get_vocabulary_id())

    def test_get_metadata(self):
        self.assertEqual({'id': 'GEOGRAPHY'}, geo.get_metadata())

    def test_get_top_concepts(self):
        top = geo.get_top_concepts()
        self.assertEqual(1, len(top))
        self.assertEqual([{'id': '1', 'label': 'World'}], top)

    def test_get_by_id(self):
        wereld = geo.get_by_id(1)
        self.assertEqual(world['id'], wereld['id'])
        self.assertEqual(world['labels'], wereld['labels'])
        self.assertEqual(world['narrower'], wereld['narrower'])

    def test_get_by_uri(self):
        wereld = geo.get_by_uri('urn:x-skosprovider:geography:1')
        self.assertEqual(world['id'], wereld['id'])
        self.assertEqual(world['labels'], wereld['labels'])
        self.assertEqual(world['narrower'], wereld['narrower'])

    def test_get_colletion_by_id(self):
        dutch_speaking = geo.get_by_id(333)
        self.assertEqual('333', dutch_speaking.id)
        self.assertEqual(['4', '7', '8'], dutch_speaking.members)

    def test_get_colletion_by_uri(self):
        dutch_speaking = geo.get_by_uri('urn:x-skosprovider:geography:333')
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

    def test_find_in_collection(self):
        c = geo.find({'collection': {'id': 333}})
        self.assertEqual(3, len(c))
        for cc in c:
            self.assertIsInstance(geo.get_by_id(cc['id']), Concept)

    def test_find_in_collection_depth_all(self):
        c = geo.find({
            'collection': {'id': 333, 'depth': 'all'}
        })
        self.assertEqual(4, len(c))
        for cc in c:
            self.assertIsInstance(geo.get_by_id(cc['id']), Concept)

    def test_find_in_collection_depth_all_wallon(self):
        c = geo.find({
            'collection': {'id': '333', 'depth': 'all'},
            'label': 'Wallon'
        })
        self.assertEqual(1, len(c))
        for cc in c:
            self.assertIsInstance(geo.get_by_id(cc['id']), Concept)

    def test_get_display_top(self):
        self.assertEqual(geo.get_top_concepts(), geo.get_top_display())

    def test_get_display_children_unexisting_concept(self):
        self.assertFalse(geo.get_children_display(404))

    def test_get_display_children_concept(self):
        self.assertEqual(
            [{'id': 2, 'label': 'Europe'}, {'id': 3, 'label': 'North-America'}],
            geo.get_children_display(1)
        )

    def test_get_display_children_collection(self):
        self.assertEqual(
            [
                {'id': 4, 'label': 'Belgium'},
                {'id': 7, 'label': 'Flanders'},
                {'id': 8, 'label': 'Brussels'}
            ],
            geo.get_children_display(333)
        )


class SimpleCsvProviderTests(unittest.TestCase):

    def setUp(self):
        from skosprovider.uri import UriPatternGenerator
        self.ifile = open(
            os.path.join(os.path.dirname(__file__), 'data', 'menu.csv'),
            "r"
        )
        reader = csv.reader(self.ifile)
        self.csvprovider = SimpleCsvProvider(
            {'id': 'MENU'},
            reader,
            uri_generator=UriPatternGenerator('http://id.python.org/menu/%s')
        )

    def tearDown(self):
        self.ifile.close()
        del self.csvprovider

    def testCount(self):
        self.assertEqual(11, len(self.csvprovider.get_all()))

    def testGetEggAndBacon(self):
        eb = self.csvprovider.get_by_id(1)
        self.assertIsInstance(eb, Concept)
        self.assertEqual('1', eb.id)
        self.assertEqual('http://id.python.org/menu/1', eb.uri)
        self.assertEqual('Egg and Bacon', eb.label().label)
        self.assertEqual('prefLabel', eb.label().type)
        self.assertEqual([], eb.notes)

    def testGetEggAndSpamByUri(self):
        eb = self.csvprovider.get_by_uri('http://id.python.org/menu/3')
        self.assertIsInstance(eb, Concept)
        self.assertEqual('3', eb.id)
        self.assertEqual('http://id.python.org/menu/3', eb.uri)

    def testFindSpam(self):
        spam = self.csvprovider.find({'label': 'Spam'})
        self.assertEqual(8, len(spam))

    def testGetLobster(self):
        eb = self.csvprovider.get_by_id(11)
        self.assertIsInstance(eb, Concept)
        self.assertEqual('11', eb.id)
        self.assertEqual('Lobster Thermidor', eb.label().label)
        self.assertIsInstance(eb.notes[0], Note)
        self.assertIn('Mornay', eb.notes[0].note)
        self.assertEqual('note', eb.notes[0].type)

    def testFindSausageCaseInsensitive(self):
        sausages = self.csvprovider.find({'label': 'sausage'})
        self.assertEqual(4, len(sausages))

    def testFindSausageCaseSensitive(self):
        self.csvprovider.case_insensitive = False
        sausages = self.csvprovider.find({'label': 'Sausage'})
        self.assertEqual(1, len(sausages))
