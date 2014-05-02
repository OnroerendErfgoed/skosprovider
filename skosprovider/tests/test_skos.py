# -*- coding: utf-8 -*-

from __future__ import unicode_literals

try:
    import unittest2 as unittest
except ImportError:  # pragma NO COVER
    import unittest  # noqa

from skosprovider.skos import (
    Label,
    Note,
    ConceptScheme,
    Concept,
    Collection,
    label,
    dict_to_label,
    dict_to_note
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

    def testEquality(self):
        l1 = Label('Knokke-Heist')
        l2 = Label('Knokke-Heist', 'prefLabel', None)
        self.assertEqual(l1, l2)

    def testInequality(self):
        l1 = Label('Knokke-Heist')
        l2 = Label('Knokke', 'altLabel')
        self.assertNotEqual(l1, l2)

    def testDictEquality(self):
        l1 = Label('Knokke-Heist')
        l2 = {'label': 'Knokke-Heist', 'type': 'prefLabel', 'language': None}
        self.assertEqual(l1, l2)

    def testDictInequality(self):
        l1 = Label('Knokke-Heist')
        l2 = {'label': 'Knokke', 'type': 'altLabel', 'language': None}
        self.assertNotEqual(l1, l2)


class NoteTest(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def testConstructor(self):
        n = Note(
            'Een gemeente in West-Vlaanderen.',
            type="note",
            language='nl-BE'
        )
        self.assertEqual('Een gemeente in West-Vlaanderen.', n.note)
        self.assertEqual('note', n.type)
        self.assertEqual('nl-BE', n.language)

    def testEquality(self):
        n1 = Note('A note.')
        n2 = Note('A note.', 'note', None)
        self.assertEqual(n1, n2)

    def testInEquality(self):
        n1 = Note('A note.')
        n2 = Note('A note.', 'definition')
        self.assertNotEqual(n1, n2)

    def testDictEquality(self):
        n1 = Note('A note.')
        n2 = {'note': 'A note.', 'type': 'note', 'language': None}
        self.assertEqual(n1, n2)

    def testDictInequality(self):
        n1 = Note('A note.')
        n2 = {'note': 'A note.', 'type': 'definition', 'language': None}
        self.assertNotEqual(n1, n2)

    def testIsValidType(self):
        self.assertTrue(Note.is_valid_type('note'))
        self.assertFalse(Label.is_valid_type('notitie'))
        n = Note('A community in West-Flanders.', 'definition', 'en')
        self.assertTrue(n.is_valid_type('definition'))


class ConceptSchemeTest(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def _get_gemeenten_nl(self):
        return Label('Gemeenten', type="prefLabel", language='nl-BE')

    def _get_fusiegemeenten_nl(self):
        return Label('Fusiegemeenten', type="altLabel", language='nl-BE')

    def _get_communities_en(self):
        return Label('Communities', type="prefLabel", language='en')

    def _get_labels(self):
        return [
            self._get_gemeenten_nl(),
            self._get_fusiegemeenten_nl(),
            self._get_communities_en()
        ]

    def testLabel(self):
        labels = self._get_labels()
        cs = ConceptScheme(
            uri='urn:x-skosprovider:gemeenten',
            labels=labels
        )
        self.assertEqual(label(labels), cs.label())
        self.assertEqual(label(labels, 'nl'), cs.label('nl'))
        self.assertEqual(label(labels, 'en'), cs.label('en'))
        self.assertEqual(label(labels, None), cs.label(None))


class ConceptTest(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def _get_knokke_heist_nl(self):
        return Label('Knokke-Heist', type="prefLabel", language='nl-BE')

    def _get_cnocke_heyst_nl(self):
        return Label('Cnock-Heyst', type="altLabel", language='nl-BE')

    def _get_knokke_heist_en(self):
        return Label('Knocke-Heyst', type="prefLabel", language='en')

    def _get_labels(self):
        return [
            self._get_knokke_heist_nl(),
            self._get_cnocke_heyst_nl(),
            self._get_knokke_heist_en()
        ]

    def testIn(self):
        c = Concept(1)
        self.assertIn('id', c)
        self.assertIn('uri', c)
        self.assertIn('labels', c)
        self.assertIn('notes', c)
        self.assertIn('broader', c)
        self.assertIn('narrower', c)
        self.assertIn('related', c)

    def testIter(self):
        c = Concept(1)
        keys = [
            'id', 'uri', 'labels', 'notes', 'broader', 'narrower', 'related'
        ]
        for k in c.keys():
            self.assertIn(k, keys)

    def testLen(self):
        c = Concept(1)
        self.assertEqual(7, len(c))

    def testLabel(self):
        labels = self._get_labels()
        c = Concept(1, labels=labels)
        self.assertEqual(label(labels), c.label())
        self.assertEqual(label(labels, 'nl'), c.label('nl'))
        self.assertEqual(label(labels, 'en'), c.label('en'))
        self.assertEqual(label(labels, None), c.label(None))

    def testUri(self):
        c = Concept(1, uri='urn:x-skosprovider:gemeenten:1')
        self.assertEqual(1, c.id)
        self.assertEqual('urn:x-skosprovider:gemeenten:1', c.uri)


class CollectionTest(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def _get_deelgemeenten_nl(self):
        return Label('Deelgemeenten', type="prefLabel", language='nl-BE')

    def _get_prefusiegemeenten_nl(self):
        return Label('Prefusiegemeenten', type="altLabel", language='nl-BE')

    def _get_labels(self):
        return [
            self._get_deelgemeenten_nl(),
            self._get_prefusiegemeenten_nl(),
        ]

    def testId(self):
        coll = Collection(350)
        self.assertEqual(350, coll.id)

    def testUri(self):
        c = Collection(350, uri='urn:x-skosprovider:gemeenten:350')
        self.assertEqual(350, c.id)
        self.assertEqual('urn:x-skosprovider:gemeenten:350', c.uri)

    def testLabel(self):
        labels = self._get_labels()
        coll = Collection(350, labels=labels)
        self.assertEqual(label(labels), coll.label())
        self.assertEqual(label(labels, 'nl'), coll.label('nl'))
        self.assertEqual(label(labels, 'en'), coll.label('en'))
        self.assertEqual(label(labels, None), coll.label(None))

    def testEmptyMembers(self):
        labels = self._get_labels()
        coll = Collection(
            350,
            labels=labels,
            members=[]
        )
        self.assertEqual([], coll.members)

    def testMembers(self):
        labels = self._get_labels()
        coll = Collection(
            id=350,
            labels=labels,
            members=[1, 2]
        )
        self.assertTrue(set([1, 2]), set(coll.members))


class DictToNoteFunctionTest(unittest.TestCase):

    def testDictToNodeWithDict(self):
        d = dict_to_note({'note': 'A note.', 'type': 'note'})
        self.assertEqual('A note.', d.note)
        self.assertEqual('note', d.type)

    def testDictToNodeWithNote(self):
        d = dict_to_note(Note('A note.', 'note'))
        self.assertEqual('A note.', d.note)
        self.assertEqual('note', d.type)


class DictToLabelFunctionTest(unittest.TestCase):

    def testDictToLabelWithDict(self):
        l = dict_to_label({'label': 'A label.', 'type': 'prefLabel'})
        self.assertEqual('A label.', l.label)
        self.assertEqual('prefLabel', l.type)

    def testDictToLabelWithlabel(self):
        l = dict_to_label(Label('A label.', 'prefLabel'))
        self.assertEqual('A label.', l.label)
        self.assertEqual('prefLabel', l.type)


class LabelFunctionTest(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def _get_knokke_heist_nl(self):
        return Label('Knokke-Heist', type="prefLabel", language='nl-BE')

    def _get_cnocke_heyst_nl(self):
        return Label('Cnock-Heyst', type="altLabel", language='nl-BE')

    def _get_knokke_heist_en(self):
        return Label('Knocke-Heyst', type="prefLabel", language='en')

    def test_label_empty(self):
        self.assertEqual(None, label([]))
        self.assertEqual(None, label([], 'nl-BE'))
        self.assertEqual(None, label([], None))

    def test_label_pref(self):
        kh = self._get_knokke_heist_nl()
        labels = [kh]
        self.assertEqual(kh, label(labels))
        self.assertEqual(kh, label(labels, 'nl-BE'))
        self.assertEqual(kh, label(labels, 'en'))
        self.assertEqual(kh, label(labels, None))

    def test_label_pref_nl_and_en(self):
        kh = self._get_knokke_heist_nl()
        khen = self._get_knokke_heist_en()
        labels = [kh, khen]
        self.assertIn(label(labels), [kh, khen])
        self.assertEqual(kh, label(labels, 'nl-BE'))
        self.assertEqual(khen, label(labels, 'en'))
        self.assertIn(label(labels, None), [kh, khen])

    def test_label_alt(self):
        ch = self._get_cnocke_heyst_nl()
        labels = [ch]
        self.assertEqual(ch, label(labels))
        self.assertEqual(ch, label(labels, 'nl-BE'))
        self.assertEqual(ch, label(labels, 'en'))
        self.assertEqual(ch, label(labels, None))

    def test_pref_precedes_alt(self):
        kh = self._get_knokke_heist_nl()
        ch = self._get_cnocke_heyst_nl()
        labels = [kh, ch]
        self.assertEqual(kh, label(labels))
        self.assertEqual(kh, label(labels, 'nl-BE'))
        self.assertEqual(kh, label(labels, 'en'))
        self.assertEqual(kh, label(labels, None))

    def test_dict_pref(self):
        kh = self._get_knokke_heist_nl()
        khd = kh.__dict__
        labels = [khd]
        self.assertEqual(kh, label(labels))
        self.assertEqual(kh, label(labels, 'nl-BE'))
        self.assertEqual(kh, label(labels, 'en'))
        self.assertEqual(kh, label(labels, None))
