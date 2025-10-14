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


class TestLabel:

    def testConstructor(self):
        label = Label("Knokke-Heist", type="prefLabel", language="nl-BE")
        assert label.label == "Knokke-Heist"
        assert label.type == "prefLabel"
        assert label.language == "nl-BE"
        assert label.uri is None

    def testConstructorInvalidLanguage(self):
        with pytest.raises(ValueError):
            Label("Knokke-Heist", type="prefLabel", language="nederlands")
        label = Label("Knokke-Heist", type="prefLabel", language=None)
        assert label.language == "und"

    def testConstructorOptionalFields(self):
        label = Label(
            "Knokke-Heist",
            type="prefLabel",
            language="nl-BE",
            uri="urn:x-skosprovider:gemeenten:knokke-heist:nl-BE",
        )
        assert label.uri == "urn:x-skosprovider:gemeenten:knokke-heist:nl-BE"
        label = Label(
            "Knokke-Heist", uri="urn:x-skosprovider:gemeenten:knokke-heist:nl-BE"
        )
        assert label.uri == "urn:x-skosprovider:gemeenten:knokke-heist:nl-BE"

    def testRepr(self):
        label = Label("Knokke-Heist", type="prefLabel", language="nl-BE")
        assert repr(label) == "Label('Knokke-Heist', 'prefLabel', 'nl-BE')"
        label = Label(
            "Knokke-Heist",
            type="prefLabel",
            language="nl-BE",
            uri="urn:x-skosp:gem:KH:nl-Be",
        )
        assert (
            repr(label)
            == "Label('Knokke-Heist', 'prefLabel', 'nl-BE', 'urn:x-skosp:gem:KH:nl-Be')"
        )

    def testIsValidType(self):
        assert Label.is_valid_type("prefLabel")
        assert not Label.is_valid_type("voorkeursLabel")
        label = Label("Knokke-Heist")
        assert label.is_valid_type("prefLabel")

    def testEquality(self):
        label1 = Label("Knokke-Heist")
        label2 = Label("Knokke-Heist", "prefLabel", "und")
        assert label1 == label2

    def testInequality(self):
        label1 = Label("Knokke-Heist")
        label2 = Label("Knokke", "altLabel")
        assert label1 != label2

    def testDictEquality(self):
        label1 = Label("Knokke-Heist")
        label2 = {"label": "Knokke-Heist", "type": "prefLabel", "language": "und"}
        assert label1 == label2

    def testDictInequality(self):
        label1 = Label("Knokke-Heist")
        label2 = {"label": "Knokke", "type": "altLabel", "language": None}
        assert label1 != label2

    def testUriEquality(self):
        label1 = Label(
            "Knokke-Heist", uri="urn:x-skosprovider:gemeenten:Knokke-Heist:nl-BE"
        )
        label2 = Label(
            "Knokke-Heist", uri="urn:x-skosprovider:gemeenten:Knokke-Heist:nl"
        )
        label3 = Label(
            "Cnocke-Heyst",
            type="altLabel",
            language="vls",
            uri="urn:x-skosprovider:gemeenten:Knokke-Heist:nl-BE",
        )
        assert label1 != label2
        assert label1 == label3

    def testUriDictEquality(self):
        label1 = Label(
            "Knokke-Heist", uri="urn:x-skosprovider:gemeenten:Knokke-Heist:und"
        )
        label2 = {
            "label": "Knokke-Heist",
            "type": "prefLabel",
            "language": "und",
            "uri": "urn:x-skosprovider:gemeenten:Knokke-Heist:und",
        }
        assert label1 == label2

    def testUriDictInequality(self):
        label1 = Label(
            "Knokke-Heist", uri="urn:x-skosprovider:gemeenten:Knokke-Heist:nl-BE"
        )
        label2 = {"label": "Knokke-Heist", "type": "prefLabel", "language": "und"}
        assert label1 != label2


class TestNote:

    def testConstructor(self):
        note = Note("Een gemeente in West-Vlaanderen.", type="note", language="nl-BE")
        assert "Een gemeente in West-Vlaanderen." == note.note
        assert "note" == note.type
        assert "nl-BE" == note.language

    def testConstructorInvalidLanguage(self):
        with pytest.raises(ValueError):
            Note("Een gemeente in West-Vlaanderen.", type="note", language="nederlands")
        note = Note("Een gemeente in West-Vlaanderen.", type="note", language=None)
        assert note.language == "und"

    def testConstructorInvalidMarkup(self):
        with pytest.raises(ValueError):
            Note(
                "Een gemeente in West-Vlaanderen.",
                type="note",
                language="nl",
                markup="markdown",
            )

    def testEquality(self):
        note1 = Note("A note.")
        note2 = Note("A note.", "note", "und")
        assert note1 == note2

    def testInEquality(self):
        note1 = Note("A note.")
        note2 = Note("A note.", "definition", "und")
        assert note1 != note2

    def testDictEquality(self):
        note1 = Note("A note.")
        note2 = {"note": "A note.", "type": "note", "language": "und", "markup": None}
        assert note1 == note2

    def testDictInequality(self):
        note1 = Note("A note.")
        note2 = {
            "note": "A note.",
            "type": "definition",
            "language": "und",
            "markup": None,
        }
        assert note1 != note2

    def testConstructorWithHTML(self):
        note = Note(
            "<p>Een gemeente in <em>West-Vlaanderen</em>.</p>",
            type="note",
            language="nl-BE",
            markup="HTML",
        )
        assert "<p>Een gemeente in <em>West-Vlaanderen</em>.</p>" == note.note
        assert "note" == note.type
        assert "nl-BE" == note.language
        assert "HTML" == note.markup

    def testIsValidType(self):
        assert Note.is_valid_type("note")
        assert not Note.is_valid_type("notitie")
        note = Note("A community in West-Flanders.", "definition", "en")
        assert note.is_valid_type("definition")

    def testIsValidMarkup(self):
        assert Note.is_valid_markup("HTML")
        assert not Note.is_valid_markup("markdown")
        note = Note("A community in West-Flanders.", "definition", "en", None)
        assert note.is_valid_markup(None)


class TestSource:

    def testConstructor(self):
        citation = "Van Daele, K; Meganck, L. & Mortier, S. 2015. "
        "Data-driven systems and system-driven data: the story of the "
        "Flanders Heritage Inventory (1995-2015)"
        source = Source(citation)
        assert citation == source.citation

    def testConstructorWithHTML(self):
        citation = "Van Daele, K; Meganck, L. & Mortier, S. 2015. "
        "<em>Data-driven systems and system-driven data: the story of the "
        "Flanders Heritage Inventory (1995-2015)</em>"
        source = Source(citation, markup="HTML")
        assert citation == source.citation
        assert "HTML" == source.markup

    def testIsValidMarkup(self):
        assert Source.is_valid_markup("HTML")
        assert not Source.is_valid_markup("markdown")
        citation = "Van Daele, K; Meganck, L. & Mortier, S. 2015. "
        "Data-driven systems and system-driven data: the story of the "
        "Flanders Heritage Inventory (1995-2015)"
        source = Source(citation)
        assert source.is_valid_markup(None)

    def testConstructorInvalidMarkup(self):
        with pytest.raises(ValueError):
            citation = "Van Daele, K; Meganck, L. & Mortier, S. 2015. "
            "<em>Data-driven systems and system-driven data: the story of the "
            "Flanders Heritage Inventory (1995-2015)</em>"
            Source(citation, markup="markdown")


class TestConceptScheme:

    def _get_gemeenten_nl(self):
        return Label("Gemeenten", type="prefLabel", language="nl-BE")

    def _get_fusiegemeenten_nl(self):
        return Label("Fusiegemeenten", type="altLabel", language="nl-BE")

    def _get_communities_en(self):
        return Label("Communities", type="prefLabel", language="en")

    def _get_labels(self):
        return [
            self._get_gemeenten_nl(),
            self._get_fusiegemeenten_nl(),
            self._get_communities_en(),
        ]

    def testRepr(self):
        conceptscheme = ConceptScheme(uri="urn:x-skosprovider:gemeenten")
        assert "ConceptScheme('urn:x-skosprovider:gemeenten')" == repr(conceptscheme)

    def testLabel(self):
        labels = self._get_labels()
        conceptscheme = ConceptScheme(uri="urn:x-skosprovider:gemeenten", labels=labels)
        assert label(labels) == conceptscheme.label()
        assert label(labels, "nl") == conceptscheme.label("nl")
        assert label(labels, "en") == conceptscheme.label("en")
        assert label(labels, None) == conceptscheme.label(None)

    def testSortKey(self):
        labels = self._get_labels()
        sortlabel = Label("allereerste", type="sortLabel", language="nl-BE")
        labels.append(sortlabel)
        conceptscheme = ConceptScheme(uri="urn:x-skosprovider:gemeenten", labels=labels)
        assert "allereerste" == conceptscheme._sortkey("sortlabel")
        assert "allereerste", conceptscheme._sortkey("sortlabel", "nl")
        assert "communities", conceptscheme._sortkey("sortlabel", "en")
        assert "urn:x-skosprovider:gemeenten", conceptscheme._sortkey("uri")

    def testLanguages(self):
        labels = self._get_labels()
        conceptscheme = ConceptScheme(
            uri="urn:x-skosprovider:gemeenten",
            labels=labels,
            languages=["nl", "en", "und"],
        )
        assert conceptscheme.languages == ["nl", "en", "und"]

    def testSource(self):
        conceptscheme = ConceptScheme(
            uri="urn:x-skosprovider:gemeenten", sources=[{"citation": "My citation"}]
        )
        assert 1 == len(conceptscheme.sources)
        assert "My citation" == conceptscheme.sources[0].citation

    def testEmptyUri(self):
        with pytest.raises(ValueError):
            ConceptScheme(uri=None)


class TestConcept:

    def _get_knokke_heist_nl(self):
        return Label("Knokke-Heist", type="prefLabel", language="nl-BE")

    def _get_cnocke_heyst_nl(self):
        return Label("Cnock-Heyst", type="altLabel", language="nl-BE")

    def _get_knokke_heist_en(self):
        return Label("Knocke-Heyst", type="prefLabel", language="en")

    def _get_labels(self):
        return [
            self._get_knokke_heist_nl(),
            self._get_cnocke_heyst_nl(),
            self._get_knokke_heist_en(),
        ]

    def testRepr(self):
        concept = Concept(1)
        assert "Concept('1')" == repr(concept)

    def testIn(self):
        c = Concept(1)
        assert hasattr(c, "id")
        assert hasattr(c, "uri")
        assert hasattr(c, "labels")
        assert hasattr(c, "notes")
        assert hasattr(c, "broader")
        assert hasattr(c, "narrower")
        assert hasattr(c, "related")
        assert hasattr(c, "member_of")

    def testLabel(self):
        labels = self._get_labels()
        c = Concept(1, labels=labels)
        assert label(labels) == c.label()
        assert label(labels, "nl") == c.label("nl")
        assert label(labels, "en") == c.label("en")
        assert label(labels, None) == c.label(None)

    def testSortKey(self):
        labels = self._get_labels()
        sl = Label("allereerste", type="sortLabel", language="nl-BE")
        labels.append(sl)
        c = Concept(1, labels=labels)
        assert "allereerste" == c._sortkey("sortlabel")
        assert "allereerste" == c._sortkey("sortlabel", "nl")
        assert "knocke-heyst" == c._sortkey("sortlabel", "en")
        assert "" == c._sortkey("uri")

    def testUri(self):
        c = Concept(1, uri="urn:x-skosprovider:gemeenten:1")
        assert 1 == c.id
        assert "urn:x-skosprovider:gemeenten:1" == c.uri

    def testMemberOf(self):
        c = Concept(1, uri="urn:x-skosprovider:gemeenten:1", member_of=[15])
        assert {15} == set(c.member_of)

    def testMatches(self):
        c = Concept(
            1,
            uri="urn:x-skosprovider:gemeenten:1",
            matches={"broad": ["http://id.something.org/provincies/1"]},
        )
        assert "close" in c.matches
        assert "exact" in c.matches
        assert "broad" in c.matches
        assert "narrow" in c.matches
        assert "related" in c.matches
        assert ["http://id.something.org/provincies/1"] == c.matches["broad"]

    def testSource(self):
        c = Concept(id=1, sources=[{"citation": "My citation"}])
        assert 1 == len(c.sources)
        assert "My citation" == c.sources[0].citation


class TestCollection:

    def _get_deelgemeenten_nl(self):
        return Label("Deelgemeenten", type="prefLabel", language="nl-BE")

    def _get_prefusiegemeenten_nl(self):
        return Label("Prefusiegemeenten", type="altLabel", language="nl-BE")

    def _get_labels(self):
        return [
            self._get_deelgemeenten_nl(),
            self._get_prefusiegemeenten_nl(),
        ]

    def testRepr(self):
        collection = Collection(1)
        assert "Collection('1')" == repr(collection)

    def testId(self):
        coll = Collection(350)
        assert 350 == coll.id

    def testUri(self):
        collection = Collection(350, uri="urn:x-skosprovider:gemeenten:350")
        assert 350 == collection.id
        assert "urn:x-skosprovider:gemeenten:350" == collection.uri

    def testLabel(self):
        labels = self._get_labels()
        coll = Collection(350, labels=labels)
        assert label(labels) == coll.label()
        assert label(labels, "nl") == coll.label("nl")
        assert label(labels, "en") == coll.label("en")
        assert label(labels, None) == coll.label(None)

    def testSortkey(self):
        labels = self._get_labels()
        sortlabel = Label("allereerste", type="sortLabel", language="nl-BE")
        labels.append(sortlabel)
        coll = Collection(350, labels=labels)
        assert "allereerste" == coll._sortkey("sortlabel")
        assert "allereerste" == coll._sortkey("sortlabel", "nl")
        assert "allereerste" == coll._sortkey("sortlabel", "en")
        assert "deelgemeenten" == coll._sortkey("label", "nl")
        assert "" == coll._sortkey("uri")

    def testEmptyMembers(self):
        labels = self._get_labels()
        coll = Collection(350, labels=labels, members=[])
        assert [] == coll.members

    def testMembers(self):
        labels = self._get_labels()
        coll = Collection(id=350, labels=labels, members=[1, 2])
        assert {1, 2} == set(coll.members)

    def testMemberOf(self):
        coll = Collection(id=1, member_of=[350])
        assert {350} == set(coll.member_of)

    def testSource(self):
        coll = Collection(id=1, sources=[{"citation": "My citation"}])
        assert 1 == len(coll.sources)
        assert "My citation" == coll.sources[0].citation

    def testnferConceptRelations(self):
        coll = Collection(
            id=1,
        )
        assert coll.infer_concept_relations
        coll = Collection(id=1, infer_concept_relations=False)
        assert not coll.infer_concept_relations


class TestDictToNoteFunction:

    def testDictToNodeWithDict(self):
        note = dict_to_note({"note": "A note.", "type": "note"})
        assert "A note." == note.note
        assert "note" == note.type
        assert "und" == note.language

    def testDictToNodeWithNote(self):
        note = dict_to_note(Note("A note.", "note"))
        assert "A note." == note.note
        assert "note" == note.type
        assert "und" == note.language


class TestDictToLabelFunction:

    def testDictToLabelWithDict(self):
        label = dict_to_label({"label": "A label.", "type": "prefLabel"})
        assert "A label." == label.label
        assert "prefLabel" == label.type
        assert "und" == label.language

    def testDictToLabelWithlabel(self):
        label = dict_to_label(Label("A label.", "prefLabel"))
        assert "A label." == label.label
        assert "prefLabel" == label.type
        assert "und" == label.language


class TestDictToSourceFunction:

    def testDictToSourceWithDict(self):
        citation = "Van Daele, K; Meganck, L. & Mortier, S. 2015. "
        "Data-driven systems and system-driven data: the story of the "
        "Flanders Heritage Inventory (1995-2015)"
        source = dict_to_source({"citation": citation})
        assert citation == source.citation

    def testDictToSourceWithDictWithMarkup(self):
        citation = "<strong>Van Daele, K; Meganck, L. & Mortier, S.</strong> 2015. "
        "Data-driven systems and system-driven data: the story of the "
        "Flanders Heritage Inventory (1995-2015)"
        source = dict_to_source({"citation": citation, "markup": "HTML"})
        assert citation == source.citation
        assert "HTML" == source.markup

    def testDictToSourceWithSource(self):
        citation = "Van Daele, K; Meganck, L. & Mortier, S. 2015. "
        "Data-driven systems and system-driven data: the story of the "
        "Flanders Heritage Inventory (1995-2015)"
        source = dict_to_source(Source(citation))
        assert citation == source.citation


class TestLabelFunction:

    def _get_knokke_heist_nl(self):
        return Label("Knokke-Heist", type="prefLabel", language="nl-BE")

    def _get_cnocke_heyst_nl(self):
        return Label("Cnock-Heyst", type="altLabel", language="nl-BE")

    def _get_knokke_heist_en(self):
        return Label("Knocke-Heyst", type="prefLabel", language="en-GB")

    def _get_und(self):
        return Label("nokke-eist", type="prefLabel", language="und")

    def _get_sortlabel(self):
        return Label("allereerste", type="sortLabel", language="nl-BE")

    def test_label_empty(self):
        assert label([]) is None
        assert label([], "nl-BE") is None
        assert label([], None) is None
        assert label([], "und") is None
        assert label([], ["nl-BE"]) is None

    def test_label_pref(self):
        kh = self._get_knokke_heist_nl()
        labels = [kh]
        assert kh == label(labels)
        assert kh == label(labels, "nl-BE")
        assert kh == label(labels, ["nl-BE"])
        assert kh == label(labels, "en-GB")
        assert kh == label(labels, ["en-GB"])
        assert kh == label(labels, None)

    def test_label_pref_und(self):
        und = self._get_und()
        labels = [und]
        assert label(labels) is not None
        assert und == label(labels)
        assert und == label(labels, "nl-BE")
        assert und == label(labels, ["nl-BE"])
        assert und == label(labels, "en-GB")
        assert und == label(labels, "und")
        assert und == label(labels, ["und"])
        assert und == label(labels, "any")
        assert und == label(labels, ["any"])
        assert und == label(labels, None)

    def test_label_pref_nl_and_en(self):
        kh = self._get_knokke_heist_nl()
        khen = self._get_knokke_heist_en()
        labels = [kh, khen]
        assert label(labels) in [kh, khen]
        assert kh == label(labels, "nl-BE")
        assert kh == label(labels, ["nl-BE", "en-GB"])
        assert khen == label(labels, "en-GB")
        assert khen == label(labels, ["fr", "en-GB"])
        assert label(labels, None) in [kh, khen]

    def test_label_inexact_language_match(self):
        kh = self._get_knokke_heist_nl()
        ch = self._get_cnocke_heyst_nl()
        khen = self._get_knokke_heist_en()
        labels = [kh, ch, khen]
        assert khen == label(labels, ["en", "nl"])
        assert khen == label(labels, "en")
        assert kh == label(labels, ["nl"])
        assert kh == label(labels, "nl")
        assert label(labels, None) in [kh, khen]

    def test_exact_precedes_inexact_match(self):
        khnl = Label("Knokke-Heist", type="prefLabel", language="nl")
        chnl = Label("Cnock-Heyst", type="altLabel", language="nl")
        khen = Label("Knocke-Heyst", type="prefLabel", language="en")
        khnlbe = self._get_knokke_heist_nl()
        chnlbe = self._get_cnocke_heyst_nl()
        khengb = self._get_knokke_heist_en()
        labels = [chnl, khen, khnlbe, khnl, chnlbe, khengb]
        assert khnlbe == label(labels, "nl-BE")
        assert khnlbe == label(labels, ["nl-BE"])
        assert khnl == label(labels, "nl")
        assert label(labels, "en-US") in [khen, khengb]

    def test_label_alt(self):
        ch = self._get_cnocke_heyst_nl()
        labels = [ch]
        assert ch == label(labels)
        assert ch == label(labels, "nl-BE")
        assert ch == label(labels, ["nl-BE"])
        assert ch == label(labels, "en-GB")
        assert ch == label(labels, ["en-GB"])
        assert ch == label(labels, None)

    def test_pref_precedes_alt(self):
        kh = self._get_knokke_heist_nl()
        ch = self._get_cnocke_heyst_nl()
        labels = [kh, ch]
        assert kh, label(labels)
        assert kh, label(labels, "nl-BE")
        assert kh, label(labels, ["nl-BE"])
        assert kh, label(labels, "en-GB")
        assert kh, label(labels, None)

    def test_sortlabel_unused(self):
        kh = self._get_knokke_heist_nl()
        ch = self._get_cnocke_heyst_nl()
        sl = self._get_sortlabel()
        labels = [kh, ch, sl]
        assert kh == label(labels)
        assert kh == label(labels, sortLabel=False)
        assert kh == label(labels, "nl-BE")
        assert kh == label(labels, ["nl-BE"])
        assert kh == label(labels, "en-GB")
        assert kh == label(labels, None)

    def test_sortlabel_broader(self):
        """
        Test that a broader sortlabel gets picked up for a regional sort.
        """
        kh = self._get_knokke_heist_nl()
        ch = self._get_cnocke_heyst_nl()
        sl = Label("Eerst", type="sortLabel", language="nl")
        labels = [kh, ch, sl]
        assert sl == label(labels, "nl-BE", True)
        assert sl == label(labels, ["nl-BE"], True)

    def test_dict_pref(self):
        kh = self._get_knokke_heist_nl()
        khd = kh.__dict__
        labels = [khd]
        assert kh == label(labels)
        assert kh == label(labels, "nl-BE")
        assert kh == label(labels, "en-GB")
        assert kh == label(labels, None)

    def test_find_best_label_for_type(self):
        kh = self._get_knokke_heist_nl()
        ch = self._get_cnocke_heyst_nl()
        khen = self._get_knokke_heist_en()
        labels = [kh, ch, khen]
        assert khen == find_best_label_for_type(labels, "en", "prefLabel")
        assert not find_best_label_for_type(labels, "en", "sortLabel")
        assert ch == find_best_label_for_type(labels, "nl", "altLabel")

    def test_filter_labels_by_language(self):
        kh = self._get_knokke_heist_nl()
        ch = self._get_cnocke_heyst_nl()
        khen = self._get_knokke_heist_en()
        labels = [kh, ch, khen]
        assert [kh, ch] == filter_labels_by_language(labels, "nl-BE")
        assert [] == filter_labels_by_language(labels, "nl")
        assert [kh, ch] == filter_labels_by_language(labels, "nl", True)
        assert labels == filter_labels_by_language(labels, "any")

    def test_filter_labels_by_language_unexisting(self):
        kh = self._get_knokke_heist_nl()
        ch = self._get_cnocke_heyst_nl()
        khen = self._get_knokke_heist_en()
        labels = [kh, ch, khen]
        assert label(labels, "tomatensoep") is not None
        assert label(labels, "") is not None
