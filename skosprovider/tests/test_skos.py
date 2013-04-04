# -*- coding: utf-8 -*-

import unittest

from skosprovider.skos import (
    ConceptScheme,
    Concept,
    Collection
)

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
