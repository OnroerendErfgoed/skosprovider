# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import unittest

from skosprovider.skos import (
    Label,
    Note,
    Source,
    ConceptScheme,
    Concept,
    Collection,
    label,
    dict_to_label,
    dict_to_note,
    dict_to_source
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

    def testRepr(self):
        l = Label('Knokke-Heist', type="prefLabel", language='nl-BE')
        self.assertEqual("Label('Knokke-Heist', 'prefLabel', 'nl-BE')", l.__repr__())

    def testIsValidType(self):
        self.assertTrue(Label.is_valid_type('prefLabel'))
        self.assertFalse(Label.is_valid_type('voorkeursLabel'))
        l = Label('Knokke-Heist')
        self.assertTrue(l.is_valid_type('prefLabel'))

    def testEquality(self):
        l1 = Label('Knokke-Heist')
        l2 = Label('Knokke-Heist', 'prefLabel', 'und')
        self.assertEqual(l1, l2)

    def testInequality(self):
        l1 = Label('Knokke-Heist')
        l2 = Label('Knokke', 'altLabel')
        self.assertNotEqual(l1, l2)

    def testDictEquality(self):
        l1 = Label('Knokke-Heist')
        l2 = {'label': 'Knokke-Heist', 'type': 'prefLabel', 'language': 'und'}
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
        n2 = Note('A note.', 'note', 'und')
        self.assertEqual(n1, n2)

    def testInEquality(self):
        n1 = Note('A note.')
        n2 = Note('A note.', 'definition', 'und')
        self.assertNotEqual(n1, n2)

    def testDictEquality(self):
        n1 = Note('A note.')
        n2 = {'note': 'A note.', 'type': 'note', 'language': 'und', 'markup': None}
        self.assertEqual(n1, n2)

    def testDictInequality(self):
        n1 = Note('A note.')
        n2 = {'note': 'A note.', 'type': 'definition', 'language': 'und', 'markup': None}
        self.assertNotEqual(n1, n2)

    def testConstructorWithHTML(self):
        n = Note(
            '<p>Een gemeente in <em>West-Vlaanderen</em>.</p>',
            type="note",
            language='nl-BE',
            markup='HTML'
        )
        self.assertEqual('<p>Een gemeente in <em>West-Vlaanderen</em>.</p>', n.note)
        self.assertEqual('note', n.type)
        self.assertEqual('nl-BE', n.language)
        self.assertEqual('HTML', n.markup)

    def testIsValidType(self):
        self.assertTrue(Note.is_valid_type('note'))
        self.assertFalse(Note.is_valid_type('notitie'))
        n = Note('A community in West-Flanders.', 'definition', 'en')
        self.assertTrue(n.is_valid_type('definition'))

    def testIsValidMarkup(self):
        self.assertTrue(Note.is_valid_markup('HTML'))
        self.assertFalse(Note.is_valid_markup('markdown'))
        n = Note('A community in West-Flanders.', 'definition', 'en', None)
        self.assertTrue(n.is_valid_markup(None))


class SourceTest(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def testConstructor(self):
        citation = 'Van Daele, K; Meganck, L. & Mortier, S. 2015. Data-driven systems and system-driven data: the story of the Flanders Heritage Inventory (1995-2015)'
        s = Source(
            citation
        )
        self.assertEqual(citation, s.citation)


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

    def testRepr(self):
        cs = ConceptScheme(
            uri='urn:x-skosprovider:gemeenten'
        )
        self.assertEquals("ConceptScheme('urn:x-skosprovider:gemeenten')", cs.__repr__())

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

    def testSortKey(self):
        labels = self._get_labels()
        sl = Label('allereerste', type='sortLabel', language='nl-BE')
        labels.append(sl)
        cs = ConceptScheme(
            uri='urn:x-skosprovider:gemeenten',
            labels=labels
        )
        self.assertEqual('allereerste', cs._sortkey('sortlabel'))
        self.assertEqual('allereerste', cs._sortkey('sortlabel', 'nl'))
        self.assertEqual('communities', cs._sortkey('sortlabel', 'en'))
        self.assertEqual('urn:x-skosprovider:gemeenten', cs._sortkey('uri'))

    def testLanguages(self):
        labels = self._get_labels()
        cs = ConceptScheme(
            uri='urn:x-skosprovider:gemeenten',
            labels=labels,
            languages=['nl', 'en', 'und']
        )
        self.assertEquals(cs.languages, ['nl', 'en', 'und'])

    def testSource(self):
        cs = ConceptScheme(
            uri='urn:x-skosprovider:gemeenten',
            sources=[{'citation': 'My citation'}]
        )
        self.assertEqual(1, len(cs.sources))
        self.assertIsInstance(cs.sources[0], Source)
        self.assertEqual('My citation', cs.sources[0].citation)


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

    def testRepr(self):
        c = Concept(1)
        self.assertEquals("Concept('1')", c.__repr__())

    def testIn(self):
        c = Concept(1)
        assert hasattr(c, 'id')
        assert hasattr(c, 'uri')
        assert hasattr(c, 'labels')
        assert hasattr(c, 'notes')
        assert hasattr(c, 'broader')
        assert hasattr(c, 'narrower')
        assert hasattr(c, 'related')
        assert hasattr(c, 'member_of')

    def testLabel(self):
        labels = self._get_labels()
        c = Concept(1, labels=labels)
        self.assertEqual(label(labels), c.label())
        self.assertEqual(label(labels, 'nl'), c.label('nl'))
        self.assertEqual(label(labels, 'en'), c.label('en'))
        self.assertEqual(label(labels, None), c.label(None))

    def testSortKey(self):
        labels = self._get_labels()
        sl = Label('allereerste', type='sortLabel', language='nl-BE')
        labels.append(sl)
        c = Concept(1, labels=labels)
        self.assertEqual('allereerste', c._sortkey('sortlabel'))
        self.assertEqual('allereerste', c._sortkey('sortlabel', 'nl'))
        self.assertEqual('knocke-heyst', c._sortkey('sortlabel', 'en'))
        self.assertEqual('', c._sortkey('uri'))

    def testUri(self):
        c = Concept(1, uri='urn:x-skosprovider:gemeenten:1')
        self.assertEqual(1, c.id)
        self.assertEqual('urn:x-skosprovider:gemeenten:1', c.uri)

    def testMemberOf(self):
        c = Concept(
            1,
            uri='urn:x-skosprovider:gemeenten:1',
            member_of=[15])
        self.assertEqual(set([15]), set(c.member_of))

    def testMatches(self):
        c = Concept(
            1,
            uri='urn:x-skosprovider:gemeenten:1',
            matches={
                'broad': ['http://id.something.org/provincies/1']
            }
        )
        assert 'close' in c.matches
        assert 'exact' in c.matches
        assert 'broad' in c.matches
        assert 'narrow' in c.matches
        assert 'related' in c.matches
        assert ['http://id.something.org/provincies/1'] == c.matches['broad']

    def testSource(self):
        c = Concept(
            id=1,
            sources=[{'citation': 'My citation'}]
        )
        self.assertEqual(1, len(c.sources))
        self.assertIsInstance(c.sources[0], Source)
        self.assertEqual('My citation', c.sources[0].citation)


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

    def testRepr(self):
        c = Collection(1)
        self.assertEquals("Collection('1')", c.__repr__())

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

    def testSortkey(self):
        labels = self._get_labels()
        sl = Label('allereerste', type='sortLabel', language='nl-BE')
        labels.append(sl)
        coll = Collection(350, labels=labels)
        self.assertEqual('allereerste', coll._sortkey('sortlabel'))
        self.assertEqual('allereerste', coll._sortkey('sortlabel', 'nl'))
        self.assertEqual('allereerste', coll._sortkey('sortlabel', 'en'))
        self.assertEqual('deelgemeenten', coll._sortkey('label', 'nl'))
        self.assertEqual('', coll._sortkey('uri'))

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

    def testMemberOf(self):
        coll = Collection(
            id=1,
            member_of=[350]
        )
        self.assertTrue(set([350]), set(coll.member_of))

    def testSource(self):
        coll = Collection(
            id=1,
            sources=[{'citation': 'My citation'}]
        )
        self.assertEqual(1, len(coll.sources))
        self.assertIsInstance(coll.sources[0], Source)
        self.assertEqual('My citation', coll.sources[0].citation)


class DictToNoteFunctionTest(unittest.TestCase):

    def testDictToNodeWithDict(self):
        d = dict_to_note({'note': 'A note.', 'type': 'note'})
        self.assertEqual('A note.', d.note)
        self.assertEqual('note', d.type)
        self.assertEqual('und', d.language)

    def testDictToNodeWithNote(self):
        d = dict_to_note(Note('A note.', 'note'))
        self.assertEqual('A note.', d.note)
        self.assertEqual('note', d.type)
        self.assertEqual('und', d.language)


class DictToLabelFunctionTest(unittest.TestCase):

    def testDictToLabelWithDict(self):
        l = dict_to_label({'label': 'A label.', 'type': 'prefLabel'})
        self.assertEqual('A label.', l.label)
        self.assertEqual('prefLabel', l.type)
        self.assertEqual('und', l.language)

    def testDictToLabelWithlabel(self):
        l = dict_to_label(Label('A label.', 'prefLabel'))
        self.assertEqual('A label.', l.label)
        self.assertEqual('prefLabel', l.type)
        self.assertEqual('und', l.language)


class DictToSourceFunctionTest(unittest.TestCase):

    def testDictToSourceWithDict(self):
        citation = 'Van Daele, K; Meganck, L. & Mortier, S. 2015. Data-driven systems and system-driven data: the story of the Flanders Heritage Inventory (1995-2015)'
        s = dict_to_source({'citation': citation})
        self.assertEqual(citation, s.citation)

    def testDictToLabelWithlabel(self):
        citation = 'Van Daele, K; Meganck, L. & Mortier, S. 2015. Data-driven systems and system-driven data: the story of the Flanders Heritage Inventory (1995-2015)'
        s = dict_to_source(Source(citation))
        self.assertEqual(citation, s.citation)


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
        return Label('Knocke-Heyst', type="prefLabel", language='en-GB')

    def _get_und(self):
        return Label('nokke-eist', type='prefLabel', language='und')

    def _get_sortlabel(self):
        return Label('allereerste', type='sortLabel', language='nl-BE')

    def test_label_empty(self):
        self.assertEqual(None, label([]))
        self.assertEqual(None, label([], 'nl-BE'))
        self.assertEqual(None, label([], None))
        self.assertEqual(None, label([], 'und'))

    def test_label_pref(self):
        kh = self._get_knokke_heist_nl()
        labels = [kh]
        self.assertEqual(kh, label(labels))
        self.assertEqual(kh, label(labels, 'nl-BE'))
        self.assertEqual(kh, label(labels, 'en-GB'))
        self.assertEqual(kh, label(labels, None))

    def test_label_pref_und(self):
        und = self._get_und()
        labels = [und]
        assert label(labels) is not None
        self.assertEqual(und, label(labels))
        self.assertEqual(und, label(labels, 'nl-BE'))
        self.assertEqual(und, label(labels, 'en-GB'))
        self.assertEqual(und, label(labels, 'und'))
        self.assertEqual(und, label(labels, 'any'))
        self.assertEqual(und, label(labels, None))

    def test_label_pref_nl_and_en(self):
        kh = self._get_knokke_heist_nl()
        khen = self._get_knokke_heist_en()
        labels = [kh, khen]
        self.assertIn(label(labels), [kh, khen])
        self.assertEqual(kh, label(labels, 'nl-BE'))
        self.assertEqual(khen, label(labels, 'en-GB'))
        self.assertIn(label(labels, None), [kh, khen])

    def test_label_inexact_language_match(self):
        kh = self._get_knokke_heist_nl()
        ch = self._get_cnocke_heyst_nl()
        khen = self._get_knokke_heist_en()
        labels = [kh, ch, khen]
        assert khen == label(labels, 'en')
        assert kh == label(labels, 'nl')
        assert label(labels, None) in [kh, khen]

    def test_exact_precedes_inexact_match(self):
        khnl = Label('Knokke-Heist', type="prefLabel", language='nl')
        chnl = Label('Cnock-Heyst', type="altLabel", language='nl')
        khen = Label('Knocke-Heyst', type="prefLabel", language='en')
        khnlbe = self._get_knokke_heist_nl()
        chnlbe = self._get_cnocke_heyst_nl()
        khengb = self._get_knokke_heist_en()
        labels = [chnl, khen, khnlbe, khnl, chnlbe, khengb]
        assert khnlbe == label(labels, 'nl-BE')
        assert khnl == label(labels, 'nl')
        assert label(labels, 'en-US') in [khen, khengb]

    def test_label_alt(self):
        ch = self._get_cnocke_heyst_nl()
        labels = [ch]
        self.assertEqual(ch, label(labels))
        self.assertEqual(ch, label(labels, 'nl-BE'))
        self.assertEqual(ch, label(labels, 'en-GB'))
        self.assertEqual(ch, label(labels, None))

    def test_pref_precedes_alt(self):
        kh = self._get_knokke_heist_nl()
        ch = self._get_cnocke_heyst_nl()
        labels = [kh, ch]
        self.assertEqual(kh, label(labels))
        self.assertEqual(kh, label(labels, 'nl-BE'))
        self.assertEqual(kh, label(labels, 'en-GB'))
        self.assertEqual(kh, label(labels, None))

    def test_sortlabel_unused(self):
        kh = self._get_knokke_heist_nl()
        ch = self._get_cnocke_heyst_nl()
        sl = self._get_sortlabel()
        labels = [kh, ch, sl]
        self.assertEqual(kh, label(labels))
        self.assertEqual(kh, label(labels, sortLabel=False))
        self.assertEqual(kh, label(labels, 'nl-BE'))
        self.assertEqual(kh, label(labels, 'en-GB'))
        self.assertEqual(kh, label(labels, None))

    def test_dict_pref(self):
        kh = self._get_knokke_heist_nl()
        khd = kh.__dict__
        labels = [khd]
        self.assertEqual(kh, label(labels))
        self.assertEqual(kh, label(labels, 'nl-BE'))
        self.assertEqual(kh, label(labels, 'en-GB'))
        self.assertEqual(kh, label(labels, None))
