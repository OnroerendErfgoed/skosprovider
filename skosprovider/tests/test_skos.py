# -*- coding: utf-8 -*-

try:
    import unittest2 as unittest
except ImportError:  # pragma NO COVER
    import unittest  # noqa

from skosprovider.skos import (
    Label,
    ConceptScheme,
    Concept,
    Collection
)

class LabelTest(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def testConstructor(self):
        l = Label('Knokke-Heist', type="prefLabel", language='nl-BE')
        self.assertEqual('Knokke-Heist', l.label)
        self.assertEqual('prefLabel', l.type)
        self.assertEqual('nl-BE', l.language)

    def testIsValidType(self):
        self.assertTrue(Label.is_valid_type('prefLabel'))
        self.assertFalse(Label.is_valid_type('voorkeursLabel'))
        l = Label('Knokke-Heist')
        self.assertTrue(l.is_valid_type('prefLabel'))

class ConceptTest(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def testIn(self):
        c = Concept(1)
        self.assertIn('id', c)
        self.assertIn('labels', c)
        self.assertIn('notes', c)
        self.assertIn('broader', c)
        self.assertIn('narrower', c)

    def testIter(self):
        c = Concept(1)
        keys = ['id', 'labels', 'notes', 'broader', 'narrower']
        for k in c.keys():
            self.assertIn(k, keys)

    def testLen(self):
        c = Concept(1)
        self.assertEqual(5, len(c))
