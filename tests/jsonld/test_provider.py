import json

import pytest
from fixtures_data import geo
from fixtures_data import trees
from rdflib.compare import isomorphic

from skosprovider.jsonld.dumper import to_jsonld
from skosprovider.jsonld.extra_data import from_unmapped
from skosprovider.jsonld.extra_data import to_unmapped
from skosprovider.jsonld.provider import JsonLdProvider

CONTEXT = {
    "skos": "http://www.w3.org/2004/02/skos/core#",
    "skosxl": "http://www.w3.org/2008/05/skos-xl#",
    "dct": "http://purl.org/dc/terms/",
    "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
    "ex": "http://example.org/",
}

LARCH = {
    "@id": "http://id.trees.org/1",
    "@type": ["skos:Concept", "ex:Tree"],
    "skos:inScheme": {"@id": "http://id.trees.org"},
    "dct:identifier": "1",
    "skos:notation": "L",
    "ex:height": {"ex:value": 30, "ex:unit": {"ex:name": "metre"}},
    "skos:prefLabel": {"@value": "The Larch", "@language": "en"},
    "skosxl:altLabel": {
        "@id": "http://id.trees.org/labels/1",
        "@type": "skosxl:Label",
        "skosxl:literalForm": {"@value": "Lariks", "@language": "nl"},
        "dct:created": "2020",
    },
    "skos:definition": {
        "@id": "http://id.trees.org/notes/1",
        "rdf:value": {"@value": "A type of tree.", "@language": "en"},
        "dct:creator": "John Doe",
    },
    "dct:source": {
        "@id": "http://id.trees.org/sources/1",
        "dct:bibliographicCitation": "A book.",
        "dct:date": "1970",
    },
}

DOCUMENT = {
    "@context": CONTEXT,
    "@graph": [
        {
            "@id": "http://id.trees.org",
            "@type": "skos:ConceptScheme",
            "dct:creator": "Jane Doe",
        },
        LARCH,
    ],
}


def _dump(provider, **kwargs):
    return json.loads(json.dumps(to_jsonld(provider, **kwargs)))


def _all_extra_data(provider):
    larch = provider.get_by_id("1")
    return [
        provider.concept_scheme.extra_data,
        larch.extra_data,
        next(label for label in larch.labels if label.uri).extra_data,
        larch.notes[0].extra_data,
        larch.sources[0].extra_data,
    ]


class TestReadDump:
    @pytest.mark.parametrize("provider", [trees, geo])
    def test_same_concepts_and_collections(self, provider):
        reloaded = JsonLdProvider(provider.metadata, _dump(provider))
        assert sorted(item["uri"] for item in reloaded.get_all()) == sorted(
            item["uri"] for item in provider.get_all()
        )

    def test_concept(self):
        larch = JsonLdProvider(trees.metadata, _dump(trees)).get_by_id("1")
        original = trees.get_by_id("1")
        assert larch.uri == original.uri
        assert larch.concept_scheme.uri == original.concept_scheme.uri
        assert sorted(larch.labels, key=repr) == sorted(original.labels, key=repr)
        assert larch.notes == original.notes
        assert larch.sources == original.sources
        assert larch.member_of == original.member_of
        assert larch.matches == original.matches

    def test_xl_label(self):
        larch = JsonLdProvider(trees.metadata, _dump(trees)).get_by_id("1")
        xl_label = next(label for label in larch.labels if label.uri)
        assert xl_label.uri == "http://id.trees.org/labels/lariks-nl"
        assert xl_label.label_types == [
            "http://publications.europa.eu/resource/authority/label-type/STANDARDLABEL"
        ]

    def test_collection_relations(self):
        reloaded = JsonLdProvider(geo.metadata, _dump(geo))
        for id_ in ("333", "358", "359"):
            collection = reloaded.get_by_id(id_)
            original = geo.get_by_id(int(id_))
            assert sorted(collection.members) == sorted(map(str, original.members))
            assert collection.superordinates == list(map(str, original.superordinates))


class TestExtraData:
    def test_ignore_by_default(self):
        provider = JsonLdProvider({"id": "TREES"}, DOCUMENT)
        assert _all_extra_data(provider) == [None] * 5

    def test_loader_receives_compact_jsonld(self):
        received = []

        def loader(data):
            received.append(data)

        JsonLdProvider({"id": "TREES"}, DOCUMENT, extra_data_loader=loader)
        larch = next(data for data in received if data["@id"] == LARCH["@id"])
        assert "@context" in larch
        assert set(larch) - {"@context", "@id"} == {
            "@type",
            "skos:notation",
            "http://example.org/height",
        }
        assert larch["@type"] == "http://example.org/Tree"

    def test_loader_not_called_without_unmapped_properties(self):
        document = {
            "@context": CONTEXT,
            "@graph": [{"@id": "http://id.trees.org", "@type": "skos:ConceptScheme"}],
        }
        JsonLdProvider(
            {"id": "TREES"},
            document,
            extra_data_loader=lambda data: pytest.fail("loader called"),
        )

    def test_blank_note_and_source_get_no_extra_data(self):
        larch = {
            **LARCH,
            "skos:definition": {
                "rdf:value": {"@value": "A type of tree.", "@language": "en"},
                "dct:creator": "John Doe",
            },
            "dct:source": {"dct:bibliographicCitation": "A book.", "dct:date": "1970"},
        }
        provider = JsonLdProvider(
            {"id": "TREES"},
            {"@context": CONTEXT, "@graph": [larch]},
            extra_data_loader=from_unmapped,
        )
        concept = provider.get_by_id("1")
        assert concept.notes[0].extra_data is None
        assert concept.sources[0].extra_data is None

    def test_round_trip(self):
        original = JsonLdProvider(
            {"id": "TREES"}, DOCUMENT, extra_data_loader=from_unmapped
        )
        reloaded = JsonLdProvider(
            {"id": "TREES"},
            _dump(original, extra_data_dumper=to_unmapped),
            extra_data_loader=from_unmapped,
        )
        for actual, expected in zip(
            _all_extra_data(reloaded), _all_extra_data(original), strict=True
        ):
            assert expected is not None
            assert isomorphic(actual, expected)

    def test_dump_ignores_extra_data_by_default(self):
        original = JsonLdProvider(
            {"id": "TREES"}, DOCUMENT, extra_data_loader=from_unmapped
        )
        reloaded = JsonLdProvider(
            {"id": "TREES"}, _dump(original), extra_data_loader=from_unmapped
        )
        assert _all_extra_data(reloaded) == [None] * 5
