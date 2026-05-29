import csv
import os

import pytest

from skosprovider.providers import DictionaryProvider
from skosprovider.providers import SimpleCsvProvider
from skosprovider.skos import Collection
from skosprovider.skos import Concept
from skosprovider.skos import ConceptScheme
from skosprovider.skos import Note
from skosprovider.skos import dict_to_label
from skosprovider.skos import dict_to_note

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


class TestTreesDictionaryProvider:

    def test_get_vocabulary_id(self):
        assert "TREES" == trees.get_vocabulary_id()

    def test_get_vocabulary_uri(self):
        assert trees.get_vocabulary_uri() == trees.concept_scheme.uri

    def test_override_get_vocabulary_uri(self):
        provider = DictionaryProvider(
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
        assert "http://id.trees.org" == provider.get_vocabulary_uri()
        assert "http://idtoo.trees.org" == provider.concept_scheme.uri

    def test_override_get_vocabulary_uri_generates_cs(self):
        provider = DictionaryProvider(
            {
                "id": "TREES",
                "uri": "http://id.trees.org",
                "default_language": "nl",
                "subject": ["biology"],
                "dataset": {"uri": "http://id.trees.org/dataset"},
            },
            [larch, chestnut, species],
        )
        assert "http://id.trees.org" == provider.get_vocabulary_uri()
        assert "http://id.trees.org" == provider.concept_scheme.uri

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
        provider = DictionaryProvider(
            {"id": "TREES"}, [larch], allowed_instance_scopes=["single"]
        )
        assert provider.allowed_instance_scopes == ["single"]

    def test_get_by_id(self):
        lariks = trees.get_by_id(1)
        assert larch["id"] == lariks.id
        assert larch["uri"] == lariks.uri
        assert [dict_to_label(label) for label in larch["labels"]] == lariks.labels
        assert [dict_to_note(note) for note in larch["notes"]] == lariks.notes
        assert len(larch["sources"]) == len(lariks.sources)
        assert larch["sources"][0]["citation"] == lariks.sources[0].citation

    def test_concept_has_scheme(self):
        lariks = trees.get_by_id(1)
        assert isinstance(lariks.concept_scheme, ConceptScheme)
        assert "http://id.trees.org" == lariks.concept_scheme.uri

    def test_collection_has_scheme(self):
        coll = trees.get_by_id(3)
        assert isinstance(coll.concept_scheme, ConceptScheme)
        assert "http://id.trees.org" == coll.concept_scheme.uri

    def test_get_by_uri(self):
        lariks = trees.get_by_uri("http://id.trees.org/1")
        assert "http://id.trees.org/1" == lariks.uri

    def test_get_by_id_string(self):
        lariks = trees.get_by_id("1")
        assert larch["id"] == lariks.id
        assert larch["uri"] == lariks.uri
        assert [dict_to_label(label) for label in larch["labels"]] == lariks.labels
        assert [dict_to_note(note) for note in larch["notes"]] == lariks.notes
        assert larch["member_of"] == lariks.member_of
        assert "concept" == lariks.type
        assert 5 == len(lariks.matches)
        assert 1 == len(lariks.matches["exact"])
        assert larch["matches"]["exact"] == lariks.matches["exact"]
        assert [] == lariks.matches["related"]

    def test_get_by_id_is_type_agnostic(self):
        assert trees.get_by_id(1) == trees.get_by_id("1")

    def test_get_unexisting_by_id(self):
        assert not trees.get_by_id(987654321)

    def test_get_unexisting_by_uri(self):
        assert not trees.get_by_uri("urn:x-skosprovider:987654321")

    def test_expand_concept(self):
        assert ["1"] == trees.expand(1)

    def test_expand_unexisting(self):
        assert trees.expand(987654321) is False

    def test_expand_collection(self):
        assert {"1", "2"} == set(trees.expand(3))

    def test_get_all(self):
        assert trees.get_all() == [
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
        ]

    def test_get_all_default_language(self):
        provider = DictionaryProvider({"id": "TREES"}, [larch])
        assert provider.get_all() == [
            {
                "id": "1",
                "uri": "http://id.trees.org/1",
                "type": "concept",
                "label": "The Larch",
            }
        ]

    def test_get_all_sort_label(self):
        assert trees.get_all(sort="label") == [
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
        ]

    def test_get_all_sort_id(self):
        assert trees.get_all(sort="id", sort_order="asc") == [
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
        ]

    def test_get_all_sort_id_reverse(self):
        assert trees.get_all(sort="id", sort_order="desc") == [
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
        ]

    def test_get_top_concepts_default_language(self):
        assert trees.get_top_concepts() == [
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
        ]

    def test_get_top_concepts_sorted_by_id(self):
        assert trees.get_top_concepts(sort="id") == [
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
        ]

    def test_get_all_english(self):
        assert trees.get_all(language="en") == [
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
        ]

    def test_get_all_english_sorted_by_label(self):
        assert trees.get_all(language="en", sort="label") == [
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
        ]

    def test_get_all_french(self):
        la_chataigne = {
            "id": "2",
            "uri": "http://id.trees.org/2",
            "type": "concept",
            "label": "la châtaigne",
        }
        assert la_chataigne in trees.get_all(language="fr")

    def test_find_all(self):
        concepts = trees.find({"type": "all"})
        assert 3 == len(concepts)

    def test_find_all_sort(self):
        concepts = trees.find({"type": "all"}, sort="id", sort_order="desc")
        assert [3, "2", "1"] == [concept["id"] for concept in concepts]
        concepts = trees.find({"type": "all"}, sort="sortlabel", sort_order="asc")
        assert [3, "1", "2"] == [concept["id"] for concept in concepts]
        concepts = trees.find({"type": "all"}, sort="sortlabel", sort_order="desc")
        assert ["2", "1", 3] == [concept["id"] for concept in concepts]

    def test_find_concepts(self):
        concepts = trees.find({"type": "concept"})
        assert 2 == len(concepts)

    def test_find_collections(self):
        concepts = trees.find({"type": "collection"})
        assert 1 == len(concepts)

    def test_find_type_None(self):
        concepts = trees.find({"type": None})
        assert len(concepts) == 3

    def test_find_larch(self):
        assert trees.find({"label": "The Larch"}) == [
            {
                "id": "1",
                "uri": "http://id.trees.org/1",
                "type": "concept",
                "label": "De Lariks",
            }
        ]

    def test_find_The_Lar(self):
        assert trees.find({"label": "The Lar"}) == [
            {
                "id": "1",
                "uri": "http://id.trees.org/1",
                "type": "concept",
                "label": "De Lariks",
            }
        ]

    def test_find_case_sensitive(self):
        provider = DictionaryProvider(
            {"id": "TREES", "default_language": "nl"},
            [larch, chestnut, species],
            case_insensitive=False,
        )
        assert provider.find({"label": "The Lar"}) == [
            {
                "id": "1",
                "uri": "http://id.trees.org/1",
                "type": "concept",
                "label": "De Lariks",
            }
        ]
        assert provider.find({"label": "lar"}) == []

    def test_find_kastanje(self):
        provider = DictionaryProvider(
            {"id": "TREES", "default_language": "nl"}, [larch, chestnut, species]
        )
        concepts = provider.find({"label": "De Paardekastanje"})
        assert len(concepts) == 1

    def test_find_empty_label(self):
        concepts = trees.find({"label": ""})
        assert 3 == len(concepts)

    def test_find_lar(self):
        assert trees.find({"label": "lar"}) == [
            {
                "id": "1",
                "uri": "http://id.trees.org/1",
                "type": "concept",
                "label": "De Lariks",
            }
        ]

    def test_find_es(self):
        concepts = trees.find({"label": "es"})
        assert 2 == len(concepts)

    def test_find_all_es(self):
        concepts = trees.find({"label": "es", "type": "all"})
        assert 2 == len(concepts)

    def test_find_concepts_es(self):
        concepts = trees.find({"label": "es", "type": "concept"})
        assert 1 == len(concepts)
        for concept in concepts:
            assert isinstance(trees.get_by_id(concept["id"]), Concept)

    def test_find_collections_es(self):
        concepts = trees.find({"label": "es", "type": "collection"})
        assert 1 == len(concepts)
        for concept in concepts:
            assert isinstance(trees.get_by_id(concept["id"]), Collection)

    def test_find_no_arguments(self):
        assert trees.find({}) == trees.get_all()

    def test_find_in_collection(self):
        concepts = trees.find({"collection": {"id": 3}})
        assert 2 == len(concepts)
        for concept in concepts:
            assert isinstance(trees.get_by_id(concept["id"]), Concept)

    def test_find_in_collection_es(self):
        concepts = trees.find({"collection": {"id": 3}, "label": "es"})
        assert 1 == len(concepts)
        for concept in concepts:
            assert isinstance(trees.get_by_id(concept["id"]), Concept)

    def test_find_in_unexisting_collection(self):
        with pytest.raises(ValueError):
            trees.find({"collection": {"id": 404}})

    def test_find_matches_without_uri(self):
        with pytest.raises(ValueError):
            trees.find({"matches": {"type": "close"}})

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
        concepts = trees.find(
            {
                "matches": {
                    "uri": "http://id.python.org/different/"
                    "types/of/trees/nr/1/the/larch",
                    "type": "close",
                }
            }
        )
        assert 1 == len(concepts)

    def test_find_matches_uri_and_wrong_type(self):
        concepts = trees.find(
            {
                "matches": {
                    "uri": "http://id.python.org/different/"
                    "types/of/trees/nr/1/the/larch",
                    "type": "related",
                }
            }
        )
        assert 0 == len(concepts)

    def test_get_display_top(self):
        top = trees.get_top_display()
        assert 1 == len(top)
        assert {
            "id": 3,
            "type": "collection",
            "label": "Bomen per soort",
            "uri": "http://id.trees.org/3",
        } in top

    def test_get_display_top_sorted_label(self):
        top = trees.get_top_display(sort="label", language="nl")
        assert 1 == len(top)
        assert {
            "id": 3,
            "type": "collection",
            "label": "Bomen per soort",
            "uri": "http://id.trees.org/3",
        } in top

    def test_get_display_children_unexisting_concept(self):
        assert not trees.get_children_display(404)

    def test_get_display_children_concept(self):
        assert [] == trees.get_children_display(1)
        assert [] == trees.get_children_display(2)

    def test_get_display_children_collection(self):
        assert trees.get_children_display(3) == [
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
        ]

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


class TestDictionaryProviderExtraData:

    def test_concept_extra_data_from_dict(self):
        provider = DictionaryProvider(
            {"id": "TEST"},
            [
                {
                    "id": "1",
                    "uri": "http://example.com/1",
                    "labels": [{"type": "prefLabel", "language": "en", "label": "One"}],
                    "custom_field": "my_value",
                    "nested": {"key": "val"},
                }
            ],
        )
        concept = provider.get_by_id("1")
        assert concept.extra_data == {"custom_field": "my_value", "nested": {"key": "val"}}

    def test_concept_no_extra_data(self):
        provider = DictionaryProvider(
            {"id": "TEST"},
            [
                {
                    "id": "1",
                    "uri": "http://example.com/1",
                    "labels": [{"type": "prefLabel", "language": "en", "label": "One"}],
                }
            ],
        )
        concept = provider.get_by_id("1")
        assert concept.extra_data == {}

    def test_collection_extra_data_from_dict(self):
        provider = DictionaryProvider(
            {"id": "TEST"},
            [
                {
                    "id": "1",
                    "uri": "http://example.com/coll/1",
                    "type": "collection",
                    "labels": [{"type": "prefLabel", "language": "en", "label": "Coll"}],
                    "theme": "nature",
                }
            ],
        )
        coll = provider.get_by_id("1")
        assert coll.extra_data == {"theme": "nature"}

    def test_label_extra_data_from_dict(self):
        provider = DictionaryProvider(
            {"id": "TEST"},
            [
                {
                    "id": "1",
                    "uri": "http://example.com/1",
                    "labels": [
                        {
                            "type": "prefLabel",
                            "language": "en",
                            "label": "One",
                            "label_extra": "extra_val",
                        }
                    ],
                }
            ],
        )
        concept = provider.get_by_id("1")
        assert concept.labels[0].extra_data == {"label_extra": "extra_val"}

    def test_note_extra_data_from_dict(self):
        provider = DictionaryProvider(
            {"id": "TEST"},
            [
                {
                    "id": "1",
                    "uri": "http://example.com/1",
                    "labels": [{"type": "prefLabel", "language": "en", "label": "One"}],
                    "notes": [
                        {
                            "type": "note",
                            "language": "en",
                            "note": "A note.",
                            "note_meta": "something",
                        }
                    ],
                }
            ],
        )
        concept = provider.get_by_id("1")
        assert concept.notes[0].extra_data == {"note_meta": "something"}


class TestGeoDictionaryProvider:

    def test_get_vocabulary_id(self):
        assert "GEOGRAPHY" == geo.get_vocabulary_id()

    def test_get_metadata(self):
        assert {"id": "GEOGRAPHY", "subject": []} == geo.get_metadata()

    def test_concept_has_scheme(self):
        con = geo.get_by_id(1)
        assert isinstance(con.concept_scheme, ConceptScheme)
        assert "urn:x-skosprovider:geography" == con.concept_scheme.uri

    def test_collection_has_scheme(self):
        coll = geo.get_by_id(333)
        assert isinstance(coll.concept_scheme, ConceptScheme)
        assert "urn:x-skosprovider:geography" == coll.concept_scheme.uri

    def test_get_top_concepts(self):
        top = geo.get_top_concepts()
        assert 4 == len(top)
        assert {
            "id": "1",
            "uri": "urn:x-skosprovider:geography:1",
            "type": "concept",
            "label": "World",
        } in top
        assert {
            "id": 15,
            "uri": "urn:x-skosprovider:geography:15",
            "type": "concept",
            "label": "German",
        } in top

    def test_get_by_id(self):
        wereld = geo.get_by_id(1)
        assert world["id"] == wereld.id
        assert wereld.uri is not None
        assert [dict_to_label(label) for label in world["labels"]] == wereld.labels
        assert world["narrower"] == wereld.narrower

    def test_get_belgium_by_id(self):
        belgium = geo.get_by_id(4)
        assert 4 == belgium.id
        assert {"333"} == set(belgium.member_of)

    def test_get_by_uri(self):
        wereld = geo.get_by_uri("urn:x-skosprovider:geography:1")
        assert world["id"] == wereld.id
        assert [dict_to_label(label) for label in world["labels"]] == wereld.labels
        assert world["narrower"] == wereld.narrower

    def test_get_collection_by_id(self):
        dutch_speaking = geo.get_by_id(333)
        assert "333" == dutch_speaking.id
        assert ["4", "7", "8"] == dutch_speaking.members

    def test_get_collection_by_uri(self):
        dutch_speaking = geo.get_by_uri("urn:x-skosprovider:geography:333")
        assert "333" == dutch_speaking.id
        assert ["4", "7", "8"] == dutch_speaking.members

    def test_expand_Belgium(self):
        assert {4, 7, 8, 9, 16} == set(geo.expand(4))

    def test_expand_UK(self):
        assert {5, 10, 11, 12} == set(geo.expand(5))

    def test_expand_string(self):
        assert {4, 7, 8, 9, 16} == set(geo.expand("4"))

    def test_expand_unexisting(self):
        assert geo.expand(987654321) is False

    def test_expand_collection(self):
        assert {4, 7, 8, 9, 16} == set(geo.expand(333))

    def test_find_in_collection(self):
        concepts = geo.find({"collection": {"id": 333}})
        assert 3 == len(concepts)
        for concept in concepts:
            assert isinstance(geo.get_by_id(concept["id"]), Concept)

    def test_find_in_collection_depth_all(self):
        concepts = geo.find({"collection": {"id": 333, "depth": "all"}})
        assert 5 == len(concepts)
        for concept in concepts:
            assert isinstance(geo.get_by_id(concept["id"]), Concept)

    def test_find_in_collection_depth_all_wallon(self):
        concepts = geo.find(
            {"collection": {"id": "333", "depth": "all"}, "label": "Wallon"}
        )
        assert 1 == len(concepts)
        for concept in concepts:
            assert isinstance(geo.get_by_id(concept["id"]), Concept)

    def test_get_display_top(self):
        top = geo.get_top_display()
        assert 2 == len(top)
        assert {
            "id": "1",
            "uri": "urn:x-skosprovider:geography:1",
            "type": "concept",
            "label": "World",
        } in top

    def test_get_display_children_unexisting_concept(self):
        assert not geo.get_children_display(404)

    def test_get_display_children_concept(self):
        assert geo.get_children_display(1) == [
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
        ]

    def test_get_display_children_collection(self):
        assert [
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
        ] == geo.get_children_display(333)

    def test_get_display_children_concept_with_thesaurus_array(self):
        children = geo.get_children_display(4)
        assert 3 == len(children)
        assert {
            "id": "358",
            "uri": "urn:x-skosprovider:geography:358",
            "type": "collection",
            "label": "Gewesten of Belgium",
        } in children
        assert {
            "id": 359,
            "uri": "urn:x-skosprovider:geography:359",
            "type": "collection",
            "label": "Languages of Belgium",
        } in children
        assert {
            "id": 16,
            "uri": "urn:x-skosprovider:geography:16",
            "type": "concept",
            "label": "The coast",
        } in children


class TestSimpleCsvProvider:

    @pytest.fixture
    def csv_file(self):
        ifile = open(os.path.join(os.path.dirname(__file__), "data", "menu.csv"))
        yield ifile
        ifile.close()

    @pytest.fixture
    def csv_provider(self, csv_file):
        from skosprovider.uri import UriPatternGenerator

        reader = csv.reader(csv_file)
        return SimpleCsvProvider(
            {"id": "MENU"},
            reader,
            uri_generator=UriPatternGenerator("http://id.python.org/menu/%s"),
            concept_scheme=ConceptScheme("http://id.python.org/menu"),
        )

    def test_count(self, csv_provider):
        assert 11 == len(csv_provider.get_all())

    def test_get_egg_and_bacon(self, csv_provider):
        concept = csv_provider.get_by_id(1)
        assert isinstance(concept, Concept)
        assert "1" == concept.id
        assert "http://id.python.org/menu/1" == concept.uri
        assert "Egg and Bacon" == concept.label().label
        assert "prefLabel" == concept.label().type
        assert [] == concept.notes
        assert 1 == len(concept.sources)
        assert "Monthy Python, Episode Twenty-five." == concept.sources[0].citation

    def test_get_egg_and_spam_by_uri(self, csv_provider):
        concept = csv_provider.get_by_uri("http://id.python.org/menu/3")
        assert isinstance(concept, Concept)
        assert "3" == concept.id
        assert "http://id.python.org/menu/3" == concept.uri

    def test_find_spam(self, csv_provider):
        spam = csv_provider.find({"label": "Spam"})
        assert 8 == len(spam)

    def test_get_lobster(self, csv_provider):
        concept = csv_provider.get_by_id(11)
        assert isinstance(concept, Concept)
        assert "11" == concept.id
        assert "Lobster Thermidor" == concept.label().label
        assert isinstance(concept.notes[0], Note)
        assert "Mornay" in concept.notes[0].note
        assert "note" == concept.notes[0].type

    def test_find_sausage_case_insensitive(self, csv_provider):
        sausages = csv_provider.find({"label": "sausage"})
        assert 4 == len(sausages)

    def test_find_sausage_case_sensitive(self, csv_provider):
        csv_provider.case_insensitive = False
        sausages = csv_provider.find({"label": "Sausage"})
        assert 1 == len(sausages)
