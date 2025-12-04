import csv
import os
import unittest

from skosprovider.providers import DictionaryProvider
from skosprovider.providers import SimpleCsvProvider
from skosprovider.skos import Collection
from skosprovider.skos import Concept
from skosprovider.skos import ConceptScheme
from skosprovider.skos import Note

larch = {
    "id": "1",
    "uri": "http://id.trees.org/1",
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
            "citation": "Monthy Python. Episode Three: How to recognise different "
            "types of trees from quite a long way away."
        }
    ],
    "member_of": ["3"],
    "matches": {
        "exact": ["http://id.python.org/different/types/of/trees/nr/1/the/larch"]
    },
}

chestnut = {
    "id": "2",
    "uri": "http://id.trees.org/2",
    "labels": [
        {"type": "prefLabel", "language": "en", "label": "The Chestnut"},
        {"type": "altLabel", "language": "nl", "label": "De Paardekastanje"},
        {"type": "altLabel", "language": "fr", "label": "la châtaigne"},
    ],
    "notes": [
        {"type": "definition", "language": "en", "note": "A different type of tree."}
    ],
    "sources": [
        {"citation": '<span class="author">Bicycle repair man</span>', "markup": "HTML"}
    ],
    "member_of": ["3"],
    "matches": {
        "related": [
            "http://id.python.org/different/types/of/trees/nr/17/the/other/chestnut"
        ]
    },
}

species = {
    "id": 3,
    "uri": "http://id.trees.org/3",
    "labels": [
        {"type": "prefLabel", "language": "en", "label": "Trees by species"},
        {"type": "prefLabel", "language": "nl", "label": "Bomen per soort"},
        {"type": "sortLabel", "language": "nl", "label": "aaa"},
    ],
    "type": "collection",
    "members": ["1", "2"],
    "notes": [
        {
            "type": "editorialNote",
            "language": "en",
            "note": "As seen in <em>How to Recognise Different Types of Trees "
            "from Quite a Long Way Away</em>.",
            "markup": "HTML",
        }
    ],
    "infer_concept_relations": False,
}

trees = DictionaryProvider(
    {
        "id": "TREES",
        "default_language": "nl",
        "subject": ["biology"],
        "dataset": {"uri": "http://id.trees.org/dataset"},
    },
    [larch, chestnut, species],
    concept_scheme=ConceptScheme(
        "http://id.trees.org",
        labels=[
            {
                "uri": "http://id.trees.org/labels/soorten-nl",
                "type": "prefLabel",
                "language": "nl",
                "label": "Soorten",
            },
            {"type": "prefLabel", "language": "en", "label": "Species"},
        ],
        languages=["nl", "en"],
    ),
)

world = {
    "id": "1",
    "uri": None,
    "labels": [{"type": "prefLabel", "language": "en", "label": "World"}],
    "narrower": [2, 3],
}

geo = DictionaryProvider(
    {"id": "GEOGRAPHY"},
    [
        world,
        {
            "id": 2,
            "labels": [{"type": "prefLabel", "language": "en", "label": "Europe"}],
            "narrower": [4, 5],
            "broader": [1],
        },
        {
            "id": 3,
            "labels": [
                {"type": "prefLabel", "language": "en", "label": "North-America"}
            ],
            "narrower": [6],
            "broader": [1],
        },
        {
            "id": 4,
            "labels": [{"type": "prefLabel", "language": "en", "label": "Belgium"}],
            "broader": [2],
            "narrower": [16],
            "member_of": ["333"],
            "subordinate_arrays": ["358", "359"],
        },
        {
            "id": 5,
            "labels": [
                {"type": "prefLabel", "language": "en", "label": "United Kingdom"},
                {"type": "prefLabel", "language": "und", "label": "Brittannia"},
            ],
            "narrower": [10, 11, 12],
            "broader": [2],
        },
        {
            "id": 6,
            "labels": [
                {
                    "type": "prefLabel",
                    "language": "en",
                    "label": "United States of America",
                }
            ],
            "broader": [3],
        },
        {
            "id": 7,
            "labels": [{"type": "prefLabel", "language": "en", "label": "Flanders"}],
            "member_of": ["333", "358"],
        },
        {
            "id": 8,
            "labels": [{"type": "prefLabel", "language": "en", "label": "Brussels"}],
            "member_of": ["333", "358"],
        },
        {
            "id": 9,
            "labels": [{"type": "prefLabel", "language": "en", "label": "Wallonie"}],
            "member_of": [358],
        },
        {
            "id": 10,
            "labels": [{"type": "prefLabel", "language": "en", "label": "Scotland"}],
            "broader": [5],
        },
        {
            "id": 11,
            "labels": [{"type": "prefLabel", "language": "en", "label": "England"}],
            "broader": [5],
        },
        {
            "id": 12,
            "labels": [{"type": "prefLabel", "language": "en", "label": "Wales"}],
            "broader": [5],
        },
        {
            "id": 13,
            "labels": [{"type": "prefLabel", "language": "en", "label": "French"}],
            "member_of": [359],
        },
        {
            "id": 14,
            "labels": [{"type": "prefLabel", "language": "en", "label": "Dutch"}],
            "member_of": [359],
        },
        {
            "id": 15,
            "labels": [{"type": "prefLabel", "language": "en", "label": "German"}],
            "member_of": [359],
        },
        {
            "id": 16,
            "labels": [{"type": "prefLabel", "language": "en", "label": "The coast"}],
            "broader": [4],
        },
        {
            "id": "333",
            "type": "collection",
            "labels": [
                {
                    "type": "prefLabel",
                    "language": "en",
                    "label": "Places where dutch is spoken",
                }
            ],
            "members": ["4", "7", "8"],
            "infer_concept_relations": False,
        },
        {
            "id": "358",
            "type": "collection",
            "labels": [
                {"type": "prefLabel", "language": "en", "label": "Gewesten of Belgium"}
            ],
            "members": ["7", "8", "9"],
            "superordinates": ["4"],
            "infer_concept_relations": True,
        },
        {
            "id": 359,
            "type": "collection",
            "labels": [
                {"type": "prefLabel", "language": "en", "label": "Languages of Belgium"}
            ],
            "members": [13, 14, 15],
            "superordinates": [4],
            "infer_concept_relations": False,
        },
    ],
)


class TreesDictionaryProviderTests(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_get_vocabulary_id(self):
        self.assertEqual("TREES", trees.get_vocabulary_id())

    def test_get_vocabulary_uri(self):
        assert trees.get_vocabulary_uri() == trees.concept_scheme.uri

    def test_override_get_vocabulary_uri(self):
        trees = DictionaryProvider(
            {
                "id": "TREES",
                "uri": "http://id.trees.org",
                "default_language": "nl",
                "subject": ["biology"],
                "dataset": {"uri": "http://id.trees.org/dataset"},
            },
            [larch, chestnut, species],
            concept_scheme=ConceptScheme(
                "http://idtoo.trees.org",
                labels=[{"type": "prefLabel", "language": "nl", "label": "Soorten"}],
                languages=["nl", "en"],
            ),
        )
        assert "http://id.trees.org" == trees.get_vocabulary_uri()
        assert "http://idtoo.trees.org" == trees.concept_scheme.uri

    def test_override_get_vocabulary_uri_generates_cs(self):
        trees = DictionaryProvider(
            {
                "id": "TREES",
                "uri": "http://id.trees.org",
                "default_language": "nl",
                "subject": ["biology"],
                "dataset": {"uri": "http://id.trees.org/dataset"},
            },
            [larch, chestnut, species],
        )
        assert "http://id.trees.org" == trees.get_vocabulary_uri()
        assert "http://id.trees.org" == trees.concept_scheme.uri

    def test_get_metadata(self):
        assert trees.get_metadata() == {
            "id": "TREES",
            "default_language": "nl",
            "subject": ["biology"],
            "dataset": {"uri": "http://id.trees.org/dataset"},
        }

    def test_allowed_instance_scopes(self):
        assert trees.allowed_instance_scopes == [
            "single",
            "threaded_thread",
            "threaded_global",
        ]

    def test_override_instance_scopes(self):
        trees = DictionaryProvider(
            {"id": "TREES"}, [larch], allowed_instance_scopes=["single"]
        )
        assert trees.allowed_instance_scopes == ["single"]

    def test_get_by_id(self):
        lariks = trees.get_by_id(1)
        assert larch["id"] == lariks.id
        assert larch["uri"] == lariks.uri
        assert larch["labels"] == lariks.labels
        assert larch["notes"] == lariks.notes
        assert len(larch["sources"]) == len(lariks.sources)
        assert larch["sources"][0]["citation"] == lariks.sources[0].citation

    def test_concept_has_scheme(self):
        lariks = trees.get_by_id(1)
        self.assertIsInstance(lariks.concept_scheme, ConceptScheme)
        self.assertEqual("http://id.trees.org", lariks.concept_scheme.uri)

    def test_collection_has_scheme(self):
        coll = trees.get_by_id(3)
        self.assertIsInstance(coll.concept_scheme, ConceptScheme)
        self.assertEqual("http://id.trees.org", coll.concept_scheme.uri)

    def test_get_by_uri(self):
        lariks = trees.get_by_uri("http://id.trees.org/1")
        assert "http://id.trees.org/1" == lariks.uri

    def test_get_by_id_string(self):
        lariks = trees.get_by_id("1")
        self.assertEqual(larch["id"], lariks.id)
        self.assertEqual(larch["uri"], lariks.uri)
        self.assertEqual(larch["labels"], lariks.labels)
        self.assertEqual(larch["notes"], lariks.notes)
        self.assertEqual(larch["member_of"], lariks.member_of)
        self.assertEqual("concept", lariks.type)
        assert 5 == len(lariks.matches)
        assert 1 == len(lariks.matches["exact"])
        assert larch["matches"]["exact"] == lariks.matches["exact"]
        assert [] == lariks.matches["related"]

    def test_get_by_id_is_type_agnostic(self):
        self.assertEqual(trees.get_by_id(1), trees.get_by_id("1"))

    def test_get_unexisting_by_id(self):
        self.assertFalse(trees.get_by_id(987654321))

    def test_get_unexisting_by_uri(self):
        self.assertFalse(trees.get_by_uri("urn:x-skosprovider:987654321"))

    def test_expand_concept(self):
        self.assertEqual(["1"], trees.expand(1))

    def test_expand_unexisting(self):
        self.assertEqual(False, trees.expand(987654321))

    def test_expand_collection(self):
        self.assertEqual({"1", "2"}, set(trees.expand(3)))

    def test_get_all(self):
        self.assertEqual(
            trees.get_all(),
            [
                {
                    "id": "1",
                    "uri": "http://id.trees.org/1",
                    "type": "concept",
                    "label": "De Lariks",
                },
                {
                    "id": "2",
                    "uri": "http://id.trees.org/2",
                    "type": "concept",
                    "label": "De Paardekastanje",
                },
                {
                    "id": 3,
                    "uri": "http://id.trees.org/3",
                    "type": "collection",
                    "label": "Bomen per soort",
                },
            ],
        )

    def test_get_all_default_language(self):
        trees = DictionaryProvider({"id": "TREES"}, [larch])
        self.assertEqual(
            trees.get_all(),
            [
                {
                    "id": "1",
                    "uri": "http://id.trees.org/1",
                    "type": "concept",
                    "label": "The Larch",
                }
            ],
        )

    def test_get_all_sort_label(self):
        self.assertEqual(
            trees.get_all(sort="label"),
            [
                {
                    "id": 3,
                    "uri": "http://id.trees.org/3",
                    "type": "collection",
                    "label": "Bomen per soort",
                },
                {
                    "id": "1",
                    "uri": "http://id.trees.org/1",
                    "type": "concept",
                    "label": "De Lariks",
                },
                {
                    "id": "2",
                    "uri": "http://id.trees.org/2",
                    "type": "concept",
                    "label": "De Paardekastanje",
                },
            ],
        )

    def test_get_all_sort_id(self):
        self.assertEqual(
            trees.get_all(sort="id", sort_order="asc"),
            [
                {
                    "id": "1",
                    "uri": "http://id.trees.org/1",
                    "type": "concept",
                    "label": "De Lariks",
                },
                {
                    "id": "2",
                    "uri": "http://id.trees.org/2",
                    "type": "concept",
                    "label": "De Paardekastanje",
                },
                {
                    "id": 3,
                    "uri": "http://id.trees.org/3",
                    "type": "collection",
                    "label": "Bomen per soort",
                },
            ],
        )

    def test_get_all_sort_id_reverse(self):
        self.assertEqual(
            trees.get_all(sort="id", sort_order="desc"),
            [
                {
                    "id": 3,
                    "uri": "http://id.trees.org/3",
                    "type": "collection",
                    "label": "Bomen per soort",
                },
                {
                    "id": "2",
                    "uri": "http://id.trees.org/2",
                    "type": "concept",
                    "label": "De Paardekastanje",
                },
                {
                    "id": "1",
                    "uri": "http://id.trees.org/1",
                    "type": "concept",
                    "label": "De Lariks",
                },
            ],
        )

    def test_get_top_concepts_default_language(self):
        self.assertEqual(
            trees.get_top_concepts(),
            [
                {
                    "id": "1",
                    "uri": "http://id.trees.org/1",
                    "type": "concept",
                    "label": "De Lariks",
                },
                {
                    "id": "2",
                    "uri": "http://id.trees.org/2",
                    "type": "concept",
                    "label": "De Paardekastanje",
                },
            ],
        )

    def test_get_top_concepts_sorted_by_id(self):
        self.assertEqual(
            trees.get_top_concepts(sort="id"),
            [
                {
                    "id": "1",
                    "uri": "http://id.trees.org/1",
                    "type": "concept",
                    "label": "De Lariks",
                },
                {
                    "id": "2",
                    "uri": "http://id.trees.org/2",
                    "type": "concept",
                    "label": "De Paardekastanje",
                },
            ],
        )

    def test_get_all_english(self):
        self.assertEqual(
            trees.get_all(language="en"),
            [
                {
                    "id": "1",
                    "uri": "http://id.trees.org/1",
                    "type": "concept",
                    "label": "The Larch",
                },
                {
                    "id": "2",
                    "uri": "http://id.trees.org/2",
                    "type": "concept",
                    "label": "The Chestnut",
                },
                {
                    "id": 3,
                    "uri": "http://id.trees.org/3",
                    "type": "collection",
                    "label": "Trees by species",
                },
            ],
        )

    def test_get_all_english_sorted_by_label(self):
        self.assertEqual(
            trees.get_all(language="en", sort="label"),
            [
                {
                    "id": "2",
                    "uri": "http://id.trees.org/2",
                    "type": "concept",
                    "label": "The Chestnut",
                },
                {
                    "id": "1",
                    "uri": "http://id.trees.org/1",
                    "type": "concept",
                    "label": "The Larch",
                },
                {
                    "id": 3,
                    "uri": "http://id.trees.org/3",
                    "type": "collection",
                    "label": "Trees by species",
                },
            ],
        )

    def test_get_all_french(self):
        la_chataigne = {
            "id": "2",
            "uri": "http://id.trees.org/2",
            "type": "concept",
            "label": "la châtaigne",
        }
        assert la_chataigne in trees.get_all(language="fr")

    def test_find_all(self):
        c = trees.find({"type": "all"})
        self.assertEqual(3, len(c))

    def test_find_all_sort(self):
        c = trees.find({"type": "all"}, sort="id", sort_order="desc")
        self.assertEqual([3, "2", "1"], [cc["id"] for cc in c])
        c = trees.find({"type": "all"}, sort="sortlabel", sort_order="asc")
        self.assertEqual([3, "1", "2"], [cc["id"] for cc in c])
        c = trees.find({"type": "all"}, sort="sortlabel", sort_order="desc")
        self.assertEqual(["2", "1", 3], [cc["id"] for cc in c])

    def test_find_concepts(self):
        c = trees.find({"type": "concept"})
        self.assertEqual(2, len(c))

    def test_find_collections(self):
        c = trees.find({"type": "collection"})
        self.assertEqual(1, len(c))

    def test_find_type_None(self):
        c = trees.find({"type": None})
        assert len(c) == 3

    def test_find_larch(self):
        self.assertEqual(
            trees.find({"label": "The Larch"}),
            [
                {
                    "id": "1",
                    "uri": "http://id.trees.org/1",
                    "type": "concept",
                    "label": "De Lariks",
                }
            ],
        )

    def test_find_The_Lar(self):
        self.assertEqual(
            trees.find({"label": "The Lar"}),
            [
                {
                    "id": "1",
                    "uri": "http://id.trees.org/1",
                    "type": "concept",
                    "label": "De Lariks",
                }
            ],
        )

    def test_find_case_sensitive(self):
        trees = DictionaryProvider(
            {"id": "TREES", "default_language": "nl"},
            [larch, chestnut, species],
            case_insensitive=False,
        )
        self.assertEqual(
            trees.find({"label": "The Lar"}),
            [
                {
                    "id": "1",
                    "uri": "http://id.trees.org/1",
                    "type": "concept",
                    "label": "De Lariks",
                }
            ],
        )
        self.assertEqual(trees.find({"label": "lar"}), [])

    def test_find_kastanje(self):
        trees = DictionaryProvider(
            {"id": "TREES", "default_language": "nl"}, [larch, chestnut, species]
        )
        concepts = trees.find({"label": "De Paardekastanje"})
        assert len(concepts) == 1

    def test_find_empty_label(self):
        c = trees.find({"label": ""})
        self.assertEqual(3, len(c))

    def test_find_lar(self):
        self.assertEqual(
            trees.find({"label": "lar"}),
            [
                {
                    "id": "1",
                    "uri": "http://id.trees.org/1",
                    "type": "concept",
                    "label": "De Lariks",
                }
            ],
        )

    def test_find_es(self):
        c = trees.find({"label": "es"})
        self.assertEqual(2, len(c))

    def test_find_all_es(self):
        c = trees.find({"label": "es", "type": "all"})
        self.assertEqual(2, len(c))

    def test_find_concepts_es(self):
        c = trees.find({"label": "es", "type": "concept"})
        self.assertEqual(1, len(c))
        for cc in c:
            self.assertIsInstance(trees.get_by_id(cc["id"]), Concept)

    def test_find_collections_es(self):
        c = trees.find({"label": "es", "type": "collection"})
        self.assertEqual(1, len(c))
        for cc in c:
            self.assertIsInstance(trees.get_by_id(cc["id"]), Collection)

    def test_find_no_arguments(self):
        self.assertEqual(trees.find({}), trees.get_all())

    def test_find_in_collection(self):
        c = trees.find({"collection": {"id": 3}})
        self.assertEqual(2, len(c))
        for cc in c:
            self.assertIsInstance(trees.get_by_id(cc["id"]), Concept)

    def test_find_in_collection_es(self):
        c = trees.find({"collection": {"id": 3}, "label": "es"})
        self.assertEqual(1, len(c))
        for cc in c:
            self.assertIsInstance(trees.get_by_id(cc["id"]), Concept)

    def test_find_in_unexisting_collection(self):
        self.assertRaises(ValueError, trees.find, {"collection": {"id": 404}})

    def test_find_matches_without_uri(self):
        self.assertRaises(ValueError, trees.find, {"matches": {"type": "close"}})

    def test_find_matches_uri_not_present(self):
        concepts = trees.find(
            {"matches": {"uri": "https://id.erfgoed.net/thesauri/soorten/1"}}
        )
        assert 0 == len(concepts)

    def test_find_matches_uri_present(self):
        concepts = trees.find(
            {
                "matches": {
                    "uri": "http://id.python.org/different/"
                    "types/of/trees/nr/1/the/larch"
                }
            }
        )
        assert 1 == len(concepts)

    def test_find_matches_uri_and_type_present(self):
        concepts = trees.find(
            {
                "matches": {
                    "uri": "http://id.python.org/different/"
                    "types/of/trees/nr/1/the/larch",
                    "type": "exact",
                }
            }
        )
        assert 1 == len(concepts)

    def test_find_matches_uri_and_type_inheritance_present(self):
        c = trees.find(
            {
                "matches": {
                    "uri": "http://id.python.org/different/"
                    "types/of/trees/nr/1/the/larch",
                    "type": "close",
                }
            }
        )
        self.assertEqual(1, len(c))

    def test_find_matches_uri_and_wrong_type(self):
        c = trees.find(
            {
                "matches": {
                    "uri": "http://id.python.org/different/"
                    "types/of/trees/nr/1/the/larch",
                    "type": "related",
                }
            }
        )
        self.assertEqual(0, len(c))

    def test_get_display_top(self):
        top = trees.get_top_display()
        self.assertEqual(1, len(top))
        self.assertIn(
            {
                "id": 3,
                "type": "collection",
                "label": "Bomen per soort",
                "uri": "http://id.trees.org/3",
            },
            top,
        )

    def test_get_display_top_sorted_label(self):
        top = trees.get_top_display(sort="label", language="nl")
        self.assertEqual(1, len(top))
        self.assertIn(
            {
                "id": 3,
                "type": "collection",
                "label": "Bomen per soort",
                "uri": "http://id.trees.org/3",
            },
            top,
        )

    def test_get_display_children_unexisting_concept(self):
        self.assertFalse(trees.get_children_display(404))

    def test_get_display_children_concept(self):
        self.assertEqual([], trees.get_children_display(1))
        self.assertEqual([], trees.get_children_display(2))

    def test_get_display_children_collection(self):
        self.assertEqual(
            trees.get_children_display(3),
            [
                {
                    "id": "1",
                    "uri": "http://id.trees.org/1",
                    "type": "concept",
                    "label": "De Lariks",
                },
                {
                    "id": "2",
                    "uri": "http://id.trees.org/2",
                    "type": "concept",
                    "label": "De Paardekastanje",
                },
            ],
        )

    def test_get_display_children_collection_sort_custom(self):
        assert trees.get_children_display(
            3, language="nl", sort="sortlabel", sort_order="desc"
        ) == [
            {
                "id": "2",
                "uri": "http://id.trees.org/2",
                "type": "concept",
                "label": "De Paardekastanje",
            },
            {
                "id": "1",
                "uri": "http://id.trees.org/1",
                "type": "concept",
                "label": "De Lariks",
            },
        ]


class GeoDictionaryProviderTests(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_get_vocabulary_id(self):
        self.assertEqual("GEOGRAPHY", geo.get_vocabulary_id())

    def test_get_metadata(self):
        self.assertEqual({"id": "GEOGRAPHY", "subject": []}, geo.get_metadata())

    def test_concept_has_scheme(self):
        con = geo.get_by_id(1)
        self.assertIsInstance(con.concept_scheme, ConceptScheme)
        self.assertEqual("urn:x-skosprovider:geography", con.concept_scheme.uri)

    def test_collection_has_scheme(self):
        coll = geo.get_by_id(333)
        self.assertIsInstance(coll.concept_scheme, ConceptScheme)
        self.assertEqual("urn:x-skosprovider:geography", coll.concept_scheme.uri)

    def test_get_top_concepts(self):
        top = geo.get_top_concepts()
        self.assertEqual(4, len(top))
        self.assertIn(
            {
                "id": "1",
                "uri": "urn:x-skosprovider:geography:1",
                "type": "concept",
                "label": "World",
            },
            top,
        )
        self.assertIn(
            {
                "id": 15,
                "uri": "urn:x-skosprovider:geography:15",
                "type": "concept",
                "label": "German",
            },
            top,
        )

    def test_get_by_id(self):
        wereld = geo.get_by_id(1)
        self.assertEqual(world["id"], wereld.id)
        self.assertIsNotNone(wereld.uri)
        self.assertEqual(world["labels"], wereld.labels)
        self.assertEqual(world["narrower"], wereld.narrower)

    def test_get_belgium_by_id(self):
        belgium = geo.get_by_id(4)
        self.assertEqual(4, belgium.id)
        self.assertEqual({"333"}, set(belgium.member_of))

    def test_get_by_uri(self):
        wereld = geo.get_by_uri("urn:x-skosprovider:geography:1")
        self.assertEqual(world["id"], wereld.id)
        self.assertEqual(world["labels"], wereld.labels)
        self.assertEqual(world["narrower"], wereld.narrower)

    def test_get_collection_by_id(self):
        dutch_speaking = geo.get_by_id(333)
        self.assertEqual("333", dutch_speaking.id)
        self.assertEqual(["4", "7", "8"], dutch_speaking.members)

    def test_get_collection_by_uri(self):
        dutch_speaking = geo.get_by_uri("urn:x-skosprovider:geography:333")
        self.assertEqual("333", dutch_speaking.id)
        self.assertEqual(["4", "7", "8"], dutch_speaking.members)

    def test_expand_Belgium(self):
        self.assertEqual({4, 7, 8, 9, 16}, set(geo.expand(4)))

    def test_expand_UK(self):
        self.assertEqual({5, 10, 11, 12}, set(geo.expand(5)))

    def test_expand_string(self):
        self.assertEqual({4, 7, 8, 9, 16}, set(geo.expand("4")))

    def test_expand_unexisting(self):
        self.assertEqual(False, geo.expand(987654321))

    def test_expand_collection(self):
        self.assertEqual({4, 7, 8, 9, 16}, set(geo.expand(333)))

    def test_find_in_collection(self):
        c = geo.find({"collection": {"id": 333}})
        self.assertEqual(3, len(c))
        for cc in c:
            self.assertIsInstance(geo.get_by_id(cc["id"]), Concept)

    def test_find_in_collection_depth_all(self):
        c = geo.find({"collection": {"id": 333, "depth": "all"}})
        self.assertEqual(5, len(c))
        for cc in c:
            self.assertIsInstance(geo.get_by_id(cc["id"]), Concept)

    def test_find_in_collection_depth_all_wallon(self):
        c = geo.find({"collection": {"id": "333", "depth": "all"}, "label": "Wallon"})
        self.assertEqual(1, len(c))
        for cc in c:
            self.assertIsInstance(geo.get_by_id(cc["id"]), Concept)

    def test_get_display_top(self):
        top = geo.get_top_display()
        self.assertEqual(2, len(top))
        self.assertIn(
            {
                "id": "1",
                "uri": "urn:x-skosprovider:geography:1",
                "type": "concept",
                "label": "World",
            },
            top,
        )

    def test_get_display_children_unexisting_concept(self):
        self.assertFalse(geo.get_children_display(404))

    def test_get_display_children_concept(self):
        self.assertEqual(
            geo.get_children_display(1),
            [
                {
                    "id": 2,
                    "uri": "urn:x-skosprovider:geography:2",
                    "type": "concept",
                    "label": "Europe",
                },
                {
                    "id": 3,
                    "type": "concept",
                    "uri": "urn:x-skosprovider:geography:3",
                    "label": "North-America",
                },
            ],
        )

    def test_get_display_children_collection(self):
        self.assertEqual(
            [
                {
                    "id": 4,
                    "uri": "urn:x-skosprovider:geography:4",
                    "type": "concept",
                    "label": "Belgium",
                },
                {
                    "id": 7,
                    "uri": "urn:x-skosprovider:geography:7",
                    "type": "concept",
                    "label": "Flanders",
                },
                {
                    "id": 8,
                    "uri": "urn:x-skosprovider:geography:8",
                    "type": "concept",
                    "label": "Brussels",
                },
            ],
            geo.get_children_display(333),
        )

    def test_get_display_children_concept_with_thesaurus_array(self):
        children = geo.get_children_display(4)
        self.assertEqual(3, len(children))
        self.assertIn(
            {
                "id": "358",
                "uri": "urn:x-skosprovider:geography:358",
                "type": "collection",
                "label": "Gewesten of Belgium",
            },
            children,
        )
        self.assertIn(
            {
                "id": 359,
                "uri": "urn:x-skosprovider:geography:359",
                "type": "collection",
                "label": "Languages of Belgium",
            },
            children,
        )
        self.assertIn(
            {
                "id": 16,
                "uri": "urn:x-skosprovider:geography:16",
                "type": "concept",
                "label": "The coast",
            },
            children,
        )


class SimpleCsvProviderTests(unittest.TestCase):

    def setUp(self):
        from skosprovider.uri import UriPatternGenerator

        self.ifile = open(os.path.join(os.path.dirname(__file__), "data", "menu.csv"))
        reader = csv.reader(self.ifile)
        self.csvprovider = SimpleCsvProvider(
            {"id": "MENU"},
            reader,
            uri_generator=UriPatternGenerator("http://id.python.org/menu/%s"),
            concept_scheme=ConceptScheme("http://id.python.org/menu"),
        )

    def tearDown(self):
        self.ifile.close()
        del self.csvprovider

    def testCount(self):
        self.assertEqual(11, len(self.csvprovider.get_all()))

    def testGetEggAndBacon(self):
        eb = self.csvprovider.get_by_id(1)
        self.assertIsInstance(eb, Concept)
        self.assertEqual("1", eb.id)
        self.assertEqual("http://id.python.org/menu/1", eb.uri)
        self.assertEqual("Egg and Bacon", eb.label().label)
        self.assertEqual("prefLabel", eb.label().type)
        self.assertEqual([], eb.notes)
        assert 1 == len(eb.sources)
        assert "Monthy Python, Episode Twenty-five." == eb.sources[0].citation

    def testGetEggAndSpamByUri(self):
        eb = self.csvprovider.get_by_uri("http://id.python.org/menu/3")
        self.assertIsInstance(eb, Concept)
        self.assertEqual("3", eb.id)
        self.assertEqual("http://id.python.org/menu/3", eb.uri)

    def testFindSpam(self):
        spam = self.csvprovider.find({"label": "Spam"})
        self.assertEqual(8, len(spam))

    def testGetLobster(self):
        eb = self.csvprovider.get_by_id(11)
        self.assertIsInstance(eb, Concept)
        self.assertEqual("11", eb.id)
        self.assertEqual("Lobster Thermidor", eb.label().label)
        self.assertIsInstance(eb.notes[0], Note)
        self.assertIn("Mornay", eb.notes[0].note)
        self.assertEqual("note", eb.notes[0].type)

    def testFindSausageCaseInsensitive(self):
        sausages = self.csvprovider.find({"label": "sausage"})
        self.assertEqual(4, len(sausages))

    def testFindSausageCaseSensitive(self):
        self.csvprovider.case_insensitive = False
        sausages = self.csvprovider.find({"label": "Sausage"})
        self.assertEqual(1, len(sausages))
