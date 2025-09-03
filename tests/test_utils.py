import unittest

from test_providers import geo
from test_providers import larch
from test_providers import trees


from skosprovider.providers import DictionaryProvider
from skosprovider.utils import add_lang_to_html
from skosprovider.utils import dict_dumper
from skosprovider.utils import extract_language


class DictDumperTest(unittest.TestCase):

    def setUp(self):
        self.larch_dump = {
            "id": "1",
            "uri": "http://id.trees.org/1",
            "type": "concept",
            "labels": [
                {"type": "prefLabel", "language": "en", "label": "The Larch"},
                {
                    "uri": "http://id.trees.org/labels/lariks-nl",
                    "type": "prefLabel",
                    "language": "nl",
                    "label": "De Lariks",
                },
            ],
            "notes": [
                {
                    "type": "definition",
                    "language": "en",
                    "note": "A type of tree.",
                    "markup": None,
                }
            ],
            "sources": [
                {
                    "citation": "Monthy Python. Episode Three: How to recognise "
                    "different types of trees from quite a long way away.",
                    "markup": None,
                }
            ],
            "narrower": [],
            "broader": [],
            "related": [],
            "member_of": ["3"],
            "subordinate_arrays": [],
            "matches": {
                "close": [],
                "exact": [
                    "http://id.python.org/different/types/of/trees/nr/1/the/larch"
                ],
                "related": [],
                "narrow": [],
                "broad": [],
            },
        }
        self.chestnut_dump = {
            "id": "2",
            "uri": "http://id.trees.org/2",
            "type": "concept",
            "labels": [
                {"type": "prefLabel", "language": "en", "label": "The Chestnut"},
                {"type": "altLabel", "language": "nl", "label": "De Paardekastanje"},
                {"type": "altLabel", "language": "fr", "label": "la châtaigne"},
            ],
            "notes": [
                {
                    "type": "definition",
                    "language": "en",
                    "note": "A different type of tree.",
                    "markup": None,
                }
            ],
            "sources": [
                {
                    "citation": '<span class="author">Bicycle repair man</span>',
                    "markup": "HTML",
                }
            ],
            "narrower": [],
            "broader": [],
            "related": [],
            "member_of": ["3"],
            "subordinate_arrays": [],
            "matches": {
                "close": [],
                "exact": [],
                "related": [
                    "http://id.python.org/different/types/of/trees/nr/17/the/other/chestnut"
                ],
                "narrow": [],
                "broad": [],
            },
        }
        self.species_dump = {
            "id": 3,
            "uri": "http://id.trees.org/3",
            "labels": [
                {"type": "prefLabel", "language": "en", "label": "Trees by species"},
                {"type": "prefLabel", "language": "nl", "label": "Bomen per soort"},
                {"type": "sortLabel", "language": "nl", "label": "aaa"},
            ],
            "type": "collection",
            "notes": [
                {
                    "type": "editorialNote",
                    "language": "en",
                    "note": "As seen in <em>How to Recognise Different Types "
                    "of Trees from Quite a Long Way Away</em>.",
                    "markup": "HTML",
                }
            ],
            "sources": [],
            "members": ["1", "2"],
            "member_of": [],
            "superordinates": [],
            "infer_concept_relations": False,
        }
        self.world_dump = {
            "id": "1",
            "uri": "urn:x-skosprovider:geography:1",
            "type": "concept",
            "labels": [{"type": "prefLabel", "language": "en", "label": "World"}],
            "notes": [],
            "sources": [],
            "narrower": [2, 3],
            "broader": [],
            "related": [],
            "member_of": [],
            "matches": {
                "close": [],
                "exact": [],
                "related": [],
                "narrow": [],
                "broad": [],
            },
            "subordinate_arrays": [],
        }

    def tearDown(self):
        del self.larch_dump
        del self.chestnut_dump
        del self.world_dump

    def _get_flat_provider(self, dictionary):
        return DictionaryProvider({"id": "TEST"}, dictionary)

    def _get_tree_provider(self, dictionary):
        return DictionaryProvider({"id": "TEST"}, dictionary)

    def testEmptyProvider(self):
        pv = self._get_flat_provider([])
        self.assertEqual([], dict_dumper(pv))

    def testOneElementProvider(self):
        pv = self._get_flat_provider([larch])
        assert [self.larch_dump] == dict_dumper(pv)

    def testFlatProvider(self):
        assert dict_dumper(trees) == [
            self.larch_dump,
            self.chestnut_dump,
            self.species_dump,
        ]

    def testEmptyTreeprovider(self):
        pv = self._get_tree_provider([])
        self.assertEqual([], dict_dumper(pv))

    def testTreeProvider(self):
        dump = dict_dumper(geo)
        self.assertIsInstance(dump, list)
        for c in dump:
            self.assertIsInstance(c, dict)
            self.assertIn("type", c)
            self.assertIn("id", c)
        self.assertIn(self.world_dump, dump)

    def testFlatProviderRoundTrip(self):
        dump = dict_dumper(trees)
        dump2 = dict_dumper(self._get_flat_provider(dict_dumper(trees)))
        self.assertEqual(dump, dump2)

    def testTreeProviderRoundTrip(self):
        dump = dict_dumper(geo)
        dump2 = dict_dumper(self._get_tree_provider(dict_dumper(geo)))
        self.assertEqual(dump, dump2)


class TestExtractLanguage:

    def test_extract_language_nlBE(self):
        assert "nl-BE" == extract_language("nl-BE")

    def test_extract_language_None(self):
        assert "und" == extract_language(None)


class TestHtml:

    def test_lang_und(self):
        assert "" == add_lang_to_html("", "und")
        assert "<p></p>" == add_lang_to_html("<p></p>", "und")

    def test_lang_no_html(self):
        assert '<div xml:lang="en"></div>' == add_lang_to_html("", "en")

    def test_no_single_child(self):
        html = "<p>Paragraph 1</p><p>Paragraph2</p>"
        assert (
            '<div xml:lang="en"><p>Paragraph 1</p><p>Paragraph2</p></div>'
            == add_lang_to_html(html, "en")
        )

    def test_text_node(self):
        html = "Something"
        assert '<div xml:lang="en">Something</div>' == add_lang_to_html(html, "en")

    def test_single_child_no_attributes(self):
        html = "<p>Paragraph 1</p>"
        assert '<p xml:lang="en">Paragraph 1</p>' == add_lang_to_html(html, "en")

    def test_single_child_already_has_langs(self):
        html = '<p xml:lang="en">Paragraph 1</p>'
        assert '<p xml:lang="en">Paragraph 1</p>' == add_lang_to_html(html, "en")

    def test_single_child_other_attributes(self):
        html = '<p class="something">Paragraph 1</p>'
        assert '<p class="something" xml:lang="en">Paragraph 1</p>' == add_lang_to_html(
            html, "en"
        )
