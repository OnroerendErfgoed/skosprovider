import pytest
from test_providers import geo
from test_providers import larch
from test_providers import trees

from skosprovider.providers import DictionaryProvider
from skosprovider.utils import add_lang_to_html
from skosprovider.utils import dict_dumper
from skosprovider.utils import extract_language


class TestDictDumper:

    @pytest.fixture
    def larch_dump(self):
        return {
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
                    "label_types": [
                        "http://publications.europa.eu/resource/authority/label-type/STANDARDLABEL"
                    ],
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

    @pytest.fixture
    def chestnut_dump(self):
        return {
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

    @pytest.fixture
    def species_dump(self):
        return {
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

    @pytest.fixture
    def world_dump(self):
        return {
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

    def _get_flat_provider(self, dictionary):
        return DictionaryProvider({"id": "TEST"}, dictionary)

    def _get_tree_provider(self, dictionary):
        return DictionaryProvider({"id": "TEST"}, dictionary)

    def test_empty_provider(self):
        pv = self._get_flat_provider([])
        assert [] == dict_dumper(pv)

    def test_one_element_provider(self, larch_dump):
        pv = self._get_flat_provider([larch])
        assert [larch_dump] == dict_dumper(pv)

    def test_flat_provider(self, larch_dump, chestnut_dump, species_dump):
        assert dict_dumper(trees) == [
            larch_dump,
            chestnut_dump,
            species_dump,
        ]

    def test_empty_tree_provider(self):
        provider = self._get_tree_provider([])
        assert [] == dict_dumper(provider)

    def test_tree_provider(self, world_dump):
        dump = dict_dumper(geo)
        assert isinstance(dump, list)
        for concept_or_collection in dump:
            assert isinstance(concept_or_collection, dict)
            assert "type" in concept_or_collection
            assert "id" in concept_or_collection
        assert world_dump in dump

    def test_flat_provider_round_trip(self):
        dump = dict_dumper(trees)
        dump2 = dict_dumper(self._get_flat_provider(dict_dumper(trees)))
        assert dump == dump2

    def test_tree_provider_round_trip(self):
        dump = dict_dumper(geo)
        dump2 = dict_dumper(self._get_tree_provider(dict_dumper(geo)))
        assert dump == dump2


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
