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

    def test_label_empty(self):
        c = Concept(1)
        self.assertEqual(None, c.label())
        self.assertEqual(None, c.label('nl-BE'))
        self.assertEqual(None, c.label(None))

    def _get_knokke_heist_nl(self):
        return Label('Knokke-Heist', type="prefLabel", language='nl-BE')

    def _get_cnocke_heyst_nl(self):
        return Label('Cnock-Heyst', type="altLabel", language='nl-BE')

    def _get_knokke_heist_en(self):
        return Label('Knocke-Heyst', type="prefLabel", language='en')

    def test_label_pref(self):
        kh = self._get_knokke_heist_nl()
        c = Concept(1, labels=[kh])
        self.assertEqual(kh, c.label())
        self.assertEqual(kh, c.label('nl-BE'))
        self.assertEqual(kh, c.label('en'))
        self.assertEqual(kh, c.label(None))

    def test_label_pref_nl_and_en(self):
        kh = self._get_knokke_heist_nl()
        khen = self._get_knokke_heist_en()
        c = Concept(1, labels=[kh, khen])
        self.assertIn(c.label(), [kh, khen])
        self.assertEqual(kh, c.label('nl-BE'))
        self.assertEqual(khen, c.label('en'))
        self.assertIn(c.label(None), [kh, khen])

    def test_label_alt(self):
        ch = self._get_cnocke_heyst_nl()
        c = Concept(1, labels=[ch])
        self.assertEqual(ch, c.label())
        self.assertEqual(ch, c.label('nl-BE'))
        self.assertEqual(ch, c.label('en'))
        self.assertEqual(ch, c.label(None))

    def test_pref_precedes_alt(self):
        kh = self._get_knokke_heist_nl()
        ch = self._get_cnocke_heyst_nl()
        c = Concept(1, labels=[kh, ch])
        self.assertEqual(kh, c.label())
        self.assertEqual(kh, c.label('nl-BE'))
        self.assertEqual(kh, c.label('en'))
        self.assertEqual(kh, c.label(None))
