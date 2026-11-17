"""
Concepts, collections and providers shared by the tests.
"""

from skosprovider.dictionary.provider import DictionaryProvider
from skosprovider.skos import ConceptScheme

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
