import pytest

from skosprovider.atramhasis.utils import dict_to_thing
from skosprovider.skos import Collection
from skosprovider.skos import Concept


@pytest.fixture
def concept():
    return {
        "subordinate_arrays": [],
        "matches": {
            "related": [
                "http://id.python.org/different/types/of/trees/nr/17/the/other/chestnut"
            ]
        },
        "labels": [
            {"type": "prefLabel", "language": "en", "label": "The Chestnut"},
            {"type": "altLabel", "language": "nl", "label": "De Paardekastanje"},
            {"type": "altLabel", "language": "fr", "label": "la châtaigne"},
        ],
        "narrower": [],
        "related": [],
        "broader": [],
        "id": 2,
        "member_of": [
            {
                "labels": [
                    {
                        "type": "prefLabel",
                        "language": "en",
                        "label": "Trees by species",
                    },
                    {
                        "type": "prefLabel",
                        "language": "nl",
                        "label": "Bomen per soort",
                    },
                ],
                "label": "Bomen per soort",
                "type": "collection",
                "id": 3,
                "uri": "urn:x-skosprovider:trees/3",
            }
        ],
        "notes": [
            {
                "note": "A different type of tree.",
                "type": "definition",
                "language": "en",
            }
        ],
        "uri": "urn:x-skosprovider:trees/2",
        "label": "The Chestnut",
        "type": "concept",
    }


@pytest.fixture
def collection():
    return {
        "labels": [
            {"type": "prefLabel", "language": "en", "label": "Trees by species"},
            {"type": "prefLabel", "language": "nl", "label": "Bomen per soort"},
        ],
        "members": [
            {
                "labels": [
                    {
                        "type": "prefLabel",
                        "language": "en",
                        "label": "The Chestnut",
                    },
                    {
                        "type": "altLabel",
                        "language": "nl",
                        "label": "De Paardekastanje",
                    },
                    {"type": "altLabel", "language": "fr", "label": "la châtaigne"},
                ],
                "label": "The Chestnut",
                "type": "concept",
                "id": 2,
                "uri": "urn:x-skosprovider:trees/2",
            },
            {
                "labels": [
                    {"type": "prefLabel", "language": "en", "label": "The Larch"},
                    {"type": "prefLabel", "language": "nl", "label": "De Lariks"},
                ],
                "label": "De Lariks",
                "type": "concept",
                "id": 1,
                "uri": "urn:x-skosprovider:trees/1",
            },
        ],
        "member_of": [],
        "superordinates": [],
        "label": "Bomen per soort",
        "type": "collection",
        "id": 3,
        "uri": "urn:x-skosprovider:trees/3",
        "sources": [{"citation": "citation about trees"}],
    }


def test_dict_to_thing_concept(concept):
    result = dict_to_thing(concept)
    assert isinstance(result, Concept)
    assert result.id == concept["id"]
    assert result.type == "concept"
    assert result.uri == concept["uri"]


def test_dict_to_thing_concept_can_still_call_label(concept):
    result = dict_to_thing(concept)
    assert result.label().label == "The Chestnut"


def test_dict_to_thing_concept_return():
    c = Concept("uri", "scheme")
    assert dict_to_thing(c) == c


def test_dict_to_thing_collection(collection):
    result = dict_to_thing(collection)
    assert isinstance(result, Collection)
    assert result.id == collection["id"]
    assert result.type == "collection"
    assert result.uri == collection["uri"]


def test_dict_to_thing_invalid():
    with pytest.raises(ValueError):
        dict_to_thing({})
    with pytest.raises(ValueError):
        dict_to_thing({"id": 2})
    with pytest.raises(ValueError):
        dict_to_thing({"id": 2, "type": "blabla"})
