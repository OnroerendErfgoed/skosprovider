# -*- coding: utf-8 -*-

import unittest

import pytest

from skosprovider.skos import Collection
from skosprovider.skos import Concept
from skosprovider.skos import ConceptScheme
from skosprovider.skos import Label
from skosprovider.skos import Note
from skosprovider.skos import Source
from skosprovider.skos import dict_to_label
from skosprovider.skos import dict_to_note
from skosprovider.skos import dict_to_source
from skosprovider.skos import filter_labels_by_language
from skosprovider.skos import find_best_label_for_type
from skosprovider.skos import label


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

    def testConstructorInvalidLanguage(self):
        with self.assertRaises(ValueError):
            l = Label('Knokke-Heist', type="prefLabel", language='nederlands')
        l = Label('Knokke-Heist', type='prefLabel', language=None)
        assert l.language == 'und'

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

    def testConstructorInvalidLanguage(self):
        with self.assertRaises(ValueError):
            n = Note(
                'Een gemeente in West-Vlaanderen.',
                type="note",
                language='nederlands'
            )
        n = Note(
            'Een gemeente in West-Vlaanderen.',
            type="note",
            language=None
        )
        assert n.language == 'und'

    def testConstructorInvalidMarkup(self):
        with self.assertRaises(ValueError):
            n = Note(
                'Een gemeente in West-Vlaanderen.',
                type="note",
                language='nl',
                markup='markdown'
            )

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

    def testConstructorWithHTML(self):
        citation = 'Van Daele, K; Meganck, L. & Mortier, S. 2015. <em>Data-driven systems and system-driven data: the story of the Flanders Heritage Inventory (1995-2015)</em>'
        s = Source(
            citation,
            markup='HTML'
        )
        self.assertEqual(citation, s.citation)
        self.assertEqual('HTML', s.markup)

    def testIsValidMarkup(self):
        self.assertTrue(Source.is_valid_markup('HTML'))
        self.assertFalse(Source.is_valid_markup('markdown'))
        citation = 'Van Daele, K; Meganck, L. & Mortier, S. 2015. Data-driven systems and system-driven data: the story of the Flanders Heritage Inventory (1995-2015)'
        s = Source(
            citation
        )
        self.assertTrue(s.is_valid_markup(None))

    def testConstructorInvalidMarkup(self):
        with self.assertRaises(ValueError):
            citation = 'Van Daele, K; Meganck, L. & Mortier, S. 2015. <em>Data-driven systems and system-driven data: the story of the Flanders Heritage Inventory (1995-2015)</em>'
            s = Source(
                citation,
                markup='markdown'
            )


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
        self.assertEqual("ConceptScheme('urn:x-skosprovider:gemeenten')", cs.__repr__())

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
        self.assertEqual(cs.languages, ['nl', 'en', 'und'])

    def testSource(self):
        cs = ConceptScheme(
            uri='urn:x-skosprovider:gemeenten',
            sources=[{'citation': 'My citation'}]
        )
        self.assertEqual(1, len(cs.sources))
        self.assertIsInstance(cs.sources[0], Source)
        self.assertEqual('My citation', cs.sources[0].citation)

    def testEmptyUri(self):
        with pytest.raises(ValueError):
            cs = ConceptScheme(uri=None)


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
        self.assertEqual("Concept('1')", c.__repr__())

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
        self.assertEqual("Collection('1')", c.__repr__())

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

    def testnferConceptRelations(self):
        coll = Collection(
            id=1,
        )
        self.assertTrue(coll.infer_concept_relations)
        coll = Collection(
            id=1,
            infer_concept_relations=False
        )
        self.assertFalse(coll.infer_concept_relations)


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

    def testDictToSourceWithDictWithMarkup(self):
        citation = '<strong>Van Daele, K; Meganck, L. & Mortier, S.</strong> 2015. Data-driven systems and system-driven data: the story of the Flanders Heritage Inventory (1995-2015)'
        s = dict_to_source({'citation': citation, 'markup': 'HTML'})
        self.assertEqual(citation, s.citation)
        self.assertEqual('HTML', s.markup)

    def testDictToSourceWithSource(self):
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
        self.assertEqual(None, label([], ['nl-BE']))

    def test_label_pref(self):
        kh = self._get_knokke_heist_nl()
        labels = [kh]
        self.assertEqual(kh, label(labels))
        self.assertEqual(kh, label(labels, 'nl-BE'))
        self.assertEqual(kh, label(labels, ['nl-BE']))
        self.assertEqual(kh, label(labels, 'en-GB'))
        self.assertEqual(kh, label(labels, ['en-GB']))
        self.assertEqual(kh, label(labels, None))

    def test_label_pref_und(self):
        und = self._get_und()
        labels = [und]
        assert label(labels) is not None
        self.assertEqual(und, label(labels))
        self.assertEqual(und, label(labels, 'nl-BE'))
        self.assertEqual(und, label(labels, ['nl-BE']))
        self.assertEqual(und, label(labels, 'en-GB'))
        self.assertEqual(und, label(labels, 'und'))
        self.assertEqual(und, label(labels, ['und']))
        self.assertEqual(und, label(labels, 'any'))
        self.assertEqual(und, label(labels, ['any']))
        self.assertEqual(und, label(labels, None))

    def test_label_pref_nl_and_en(self):
        kh = self._get_knokke_heist_nl()
        khen = self._get_knokke_heist_en()
        labels = [kh, khen]
        self.assertIn(label(labels), [kh, khen])
        self.assertEqual(kh, label(labels, 'nl-BE'))
        self.assertEqual(kh, label(labels, ['nl-BE', 'en-GB']))
        self.assertEqual(khen, label(labels, 'en-GB'))
        self.assertEqual(khen, label(labels, ['fr', 'en-GB']))
        self.assertIn(label(labels, None), [kh, khen])

    def test_label_inexact_language_match(self):
        kh = self._get_knokke_heist_nl()
        ch = self._get_cnocke_heyst_nl()
        khen = self._get_knokke_heist_en()
        labels = [kh, ch, khen]
        assert khen == label(labels, ['en', 'nl'])
        assert khen == label(labels, 'en')
        assert kh == label(labels, ['nl'])
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
        assert khnlbe == label(labels, ['nl-BE'])
        assert khnl == label(labels, 'nl')
        assert label(labels, 'en-US') in [khen, khengb]

    def test_label_alt(self):
        ch = self._get_cnocke_heyst_nl()
        labels = [ch]
        self.assertEqual(ch, label(labels))
        self.assertEqual(ch, label(labels, 'nl-BE'))
        self.assertEqual(ch, label(labels, ['nl-BE']))
        self.assertEqual(ch, label(labels, 'en-GB'))
        self.assertEqual(ch, label(labels, ['en-GB']))
        self.assertEqual(ch, label(labels, None))

    def test_pref_precedes_alt(self):
        kh = self._get_knokke_heist_nl()
        ch = self._get_cnocke_heyst_nl()
        labels = [kh, ch]
        self.assertEqual(kh, label(labels))
        self.assertEqual(kh, label(labels, 'nl-BE'))
        self.assertEqual(kh, label(labels, ['nl-BE']))
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
        self.assertEqual(kh, label(labels, ['nl-BE']))
        self.assertEqual(kh, label(labels, 'en-GB'))
        self.assertEqual(kh, label(labels, None))

    def test_sortlabel_broader(self):
        '''
        Test that a broader sortlabel gets picked up for a regional sort.
        '''
        kh = self._get_knokke_heist_nl()
        ch = self._get_cnocke_heyst_nl()
        sl = Label('Eerst', type='sortLabel', language='nl')
        labels = [kh, ch, sl]
        assert sl == label(labels, 'nl-BE', True)
        assert sl == label(labels, ['nl-BE'], True)

    def test_dict_pref(self):
        kh = self._get_knokke_heist_nl()
        khd = kh.__dict__
        labels = [khd]
        self.assertEqual(kh, label(labels))
        self.assertEqual(kh, label(labels, 'nl-BE'))
        self.assertEqual(kh, label(labels, 'en-GB'))
        self.assertEqual(kh, label(labels, None))

    def test_find_best_label_for_type(self):
        kh = self._get_knokke_heist_nl()
        ch = self._get_cnocke_heyst_nl()
        khen = self._get_knokke_heist_en()
        labels = [kh, ch, khen]
        assert khen == find_best_label_for_type(labels, 'en', 'prefLabel')
        assert not find_best_label_for_type(labels, 'en', 'sortLabel')
        assert ch == find_best_label_for_type(labels, 'nl', 'altLabel')

    def test_filter_labels_by_language(self):
        kh = self._get_knokke_heist_nl()
        ch = self._get_cnocke_heyst_nl()
        khen = self._get_knokke_heist_en()
        labels = [kh, ch, khen]
        assert [kh, ch] == filter_labels_by_language(labels, 'nl-BE')
        assert [] == filter_labels_by_language(labels, 'nl')
        assert [kh, ch] == filter_labels_by_language(labels, 'nl', True)
        assert labels == filter_labels_by_language(labels, 'any')
