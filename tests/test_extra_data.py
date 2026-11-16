import pytest
from rdflib import BNode
from rdflib import Graph
from rdflib import Literal
from rdflib import Namespace
from rdflib import URIRef
from rdflib.compare import isomorphic
from rdflib.namespace import XSD

from skosprovider.exceptions import ExtraDataException
from skosprovider.exceptions import ProviderUnavailableException
from skosprovider.exceptions import SkosproviderException
from skosprovider.extra_data import from_graph
from skosprovider.extra_data import from_jsonld
from skosprovider.extra_data import from_turtle
from skosprovider.extra_data import ignore
from skosprovider.extra_data import to_graph
from skosprovider.extra_data import to_jsonld
from skosprovider.extra_data import to_turtle
from skosprovider.providers import DictionaryProvider
from skosprovider.providers import SimpleCsvProvider
from skosprovider.skos import Label
from skosprovider.skos import Note
from skosprovider.utils import dict_dumper

DCT = Namespace("http://purl.org/dc/terms/")


def _graph(subject, value):
    graph = Graph()
    graph.bind("dct", DCT)
    node = BNode()
    graph.add((URIRef(subject), DCT.creator, node))
    graph.add((node, DCT.title, Literal(value)))
    return graph


def _provider(data, **kwargs):
    return DictionaryProvider({"id": "TREES"}, data, **kwargs)


def _concept_dict(extra_data):
    return {
        "id": "1",
        "uri": "http://id.trees.org/1",
        "labels": [
            {
                "label": "Larch",
                "type": "prefLabel",
                "language": "en",
                "extra_data": extra_data("http://id.trees.org/1/label", "label"),
            },
        ],
        "notes": [
            {
                "note": "A tree.",
                "type": "note",
                "language": "en",
                "extra_data": extra_data("http://id.trees.org/1/note", "note"),
            },
        ],
        "sources": [
            {
                "citation": "A book.",
                "extra_data": extra_data("http://id.trees.org/1/source", "source"),
            },
        ],
        "extra_data": extra_data("http://id.trees.org/1", "concept"),
    }


def _collection_dict(extra_data):
    return {
        "id": "2",
        "uri": "http://id.trees.org/2",
        "type": "collection",
        "labels": [
            {
                "label": "Trees",
                "type": "prefLabel",
                "language": "en",
                "extra_data": extra_data("http://id.trees.org/2/label", "label"),
            },
        ],
        "members": ["1"],
        "extra_data": extra_data("http://id.trees.org/2", "collection"),
    }


def _all_extra_data(provider):
    concept = provider.get_by_id("1")
    collection = provider.get_by_id("2")
    return [
        concept.extra_data,
        concept.labels[0].extra_data,
        concept.notes[0].extra_data,
        concept.sources[0].extra_data,
        collection.extra_data,
        collection.labels[0].extra_data,
    ]


class TestDictionaryProviderExtraData:

    def test_default_ignores_extra_data(self):
        provider = _provider([_concept_dict(_graph), _collection_dict(_graph)])
        assert _all_extra_data(provider) == [None] * 6

    def test_from_graph_on_all_object_types(self):
        provider = _provider(
            [_concept_dict(_graph), _collection_dict(_graph)],
            extra_data_loader=from_graph,
        )
        expected = [
            _graph("http://id.trees.org/1", "concept"),
            _graph("http://id.trees.org/1/label", "label"),
            _graph("http://id.trees.org/1/note", "note"),
            _graph("http://id.trees.org/1/source", "source"),
            _graph("http://id.trees.org/2", "collection"),
            _graph("http://id.trees.org/2/label", "label"),
        ]
        for actual, graph in zip(_all_extra_data(provider), expected):
            assert isomorphic(actual, graph)

    def test_loader_receives_full_dict(self):
        received = []

        def loader(data):
            received.append(data)

        concept = _concept_dict(lambda *_: None)
        _provider([concept], extra_data_loader=loader)
        assert received == [
            concept["labels"][0],
            concept["notes"][0],
            concept["sources"][0],
            concept,
        ]

    def test_objects_keep_their_extra_data(self):
        graph = _graph("http://id.trees.org/1/label", "label")
        provider = _provider(
            [
                {
                    "id": "1",
                    "labels": [Label("Larch", extra_data=graph)],
                    "notes": [Note("A tree.", extra_data=graph)],
                }
            ],
            extra_data_loader=from_graph,
        )
        concept = provider.get_by_id("1")
        assert concept.extra_data is None
        assert concept.labels[0].extra_data is graph
        assert concept.notes[0].extra_data is graph

    def test_custom_keys(self):
        def loader(data):
            if "extra1" not in data:
                return None
            graph = Graph()
            graph.add((URIRef("urn:x"), DCT.identifier, Literal(data["extra1"])))
            return graph

        provider = _provider(
            [{"id": "1", "labels": [{"label": "Kerk", "extra1": 1}]}],
            extra_data_loader=loader,
        )
        concept = provider.get_by_id("1")
        assert concept.extra_data is None
        assert len(concept.labels[0].extra_data) == 1

    def test_wrong_format_raises(self):
        with pytest.raises(ExtraDataException) as excinfo:
            _provider([_concept_dict(_graph)], extra_data_loader=from_turtle)
        assert str(excinfo.value).startswith("Failed to load extra_data: ")
        assert excinfo.value.__notes__ == [
            "while processing Label('Larch', 'prefLabel', 'en')",
            "while processing concept '1'",
        ]
        assert excinfo.value.__cause__ is not None

    def test_failing_custom_loader_raises(self):
        error = ValueError("boom")

        def loader(data):
            raise error

        with pytest.raises(ExtraDataException) as excinfo:
            _provider([{"id": "2", "type": "collection"}], extra_data_loader=loader)
        assert str(excinfo.value) == "Failed to load extra_data: boom"
        assert excinfo.value.__notes__ == ["while processing collection '2'"]
        assert excinfo.value.__cause__ is error


class TestSimpleCsvProviderExtraData:

    def test_default_ignores_extra_data(self):
        provider = SimpleCsvProvider({"id": "CSV"}, [["1", "Larch"]])
        assert provider.get_by_id("1").extra_data is None

    def test_loader_receives_row(self):
        graph = Graph()
        received = []

        def loader(row):
            received.append(row)
            return graph

        provider = SimpleCsvProvider(
            {"id": "CSV"}, [["1", "Larch", "A tree."]], extra_data_loader=loader
        )
        assert received == [["1", "Larch", "A tree."]]
        assert provider.get_by_id("1").extra_data is graph

    def test_failing_loader_raises(self):
        def loader(row):
            raise ValueError("boom")

        with pytest.raises(ExtraDataException) as excinfo:
            SimpleCsvProvider({"id": "CSV"}, [["1", "Larch"]], extra_data_loader=loader)
        assert str(excinfo.value) == "Failed to load extra_data: boom"
        assert excinfo.value.__notes__ == ["while processing concept '1'"]

    def test_default_ignores_nested_extra_data(self):
        provider = SimpleCsvProvider(
            {"id": "CSV"}, [["1", "Larch", "A tree.", "A book."]]
        )
        concept = provider.get_by_id("1")
        assert concept.labels[0].extra_data is None
        assert concept.notes[0].extra_data is None
        assert concept.sources[0].extra_data is None

    def test_loader_per_object_type(self):
        row = ["1", "Larch", "A tree.", "A book.", "c", "l", "n", "s"]
        graphs = {column: Graph() for column in "clns"}

        def column_loader(index):
            return lambda row: graphs[row[index]]

        provider = SimpleCsvProvider(
            {"id": "CSV"},
            [row],
            extra_data_loader=column_loader(4),
            label_extra_data_loader=column_loader(5),
            note_extra_data_loader=column_loader(6),
            source_extra_data_loader=column_loader(7),
        )
        concept = provider.get_by_id("1")
        assert concept.extra_data is graphs["c"]
        assert concept.labels[0].extra_data is graphs["l"]
        assert concept.notes[0].extra_data is graphs["n"]
        assert concept.sources[0].extra_data is graphs["s"]

    def test_nested_loader_not_called_without_object(self):
        provider = SimpleCsvProvider(
            {"id": "CSV"},
            [["1", "Larch", ""]],
            note_extra_data_loader=lambda row: pytest.fail("note loader called"),
            source_extra_data_loader=lambda row: pytest.fail("source loader called"),
        )
        concept = provider.get_by_id("1")
        assert concept.notes == []
        assert concept.sources == []

    def test_failing_nested_loader_raises(self):
        def loader(row):
            raise ValueError("boom")

        with pytest.raises(ExtraDataException) as excinfo:
            SimpleCsvProvider(
                {"id": "CSV"},
                [["1", "Larch", "", "A book."]],
                source_extra_data_loader=loader,
            )
        assert str(excinfo.value) == "Failed to load extra_data: boom"
        assert excinfo.value.__notes__ == [
            "while processing Source('A book.')",
            "while processing concept '1'",
        ]


class TestDictDumperExtraData:

    def test_default_ignores_extra_data(self):
        provider = _provider(
            [_concept_dict(_graph), _collection_dict(_graph)],
            extra_data_loader=from_graph,
        )
        dump = dict_dumper(provider)
        concept, collection = dump
        assert "extra_data" not in concept
        assert "extra_data" not in concept["labels"][0]
        assert "extra_data" not in concept["notes"][0]
        assert "extra_data" not in concept["sources"][0]
        assert "extra_data" not in collection

    def test_dumper_result_is_merged_and_overwrites(self):
        provider = _provider([{"id": "1", "labels": [{"label": "Kerk"}]}])

        def dumper(obj):
            if isinstance(obj, Label):
                return {"label": "Church", "extra1": 1}
            return None

        concept = dict_dumper(provider, extra_data_dumper=dumper)[0]
        assert concept["labels"][0]["label"] == "Church"
        assert concept["labels"][0]["extra1"] == 1
        assert "extra1" not in concept

    def test_failing_dumper_raises(self):
        provider = _provider([{"id": "1", "notes": [{"note": "A tree."}]}])
        error = ValueError("boom")

        def dumper(obj):
            if isinstance(obj, Note):
                raise error

        with pytest.raises(ExtraDataException) as excinfo:
            dict_dumper(provider, extra_data_dumper=dumper)
        assert str(excinfo.value) == "Failed to dump extra_data: boom"
        assert excinfo.value.__notes__ == [
            "while processing Note('A tree.', 'note', 'und')",
            "while processing concept '1'",
        ]
        assert excinfo.value.__cause__ is error


class TestLoadersAndDumpers:

    @pytest.mark.parametrize("loader", [from_turtle, from_jsonld, from_graph])
    @pytest.mark.parametrize("data", [{}, {"extra_data": None}])
    def test_loader_without_extra_data(self, loader, data):
        assert loader(data) is None

    @pytest.mark.parametrize("dumper", [to_turtle, to_jsonld, to_graph, ignore])
    def test_dumper_without_extra_data(self, dumper):
        assert dumper(Label("Larch")) is None

    def test_ignore(self):
        assert ignore({"extra_data": Graph()}) is None

    def test_to_jsonld_context_only_has_used_namespaces(self):
        graph = Graph()
        graph.bind("dct", DCT)
        graph.bind("unused", Namespace("http://example.org/unused#"))
        graph.add(
            (
                URIRef("http://id.trees.org/1"),
                DCT.created,
                Literal("2020-01-01", datatype=XSD.date),
            )
        )
        dumped = to_jsonld(Label("Larch", extra_data=graph))
        assert dumped["extra_data"]["@context"] == {
            "dct": "http://purl.org/dc/terms/",
            "xsd": "http://www.w3.org/2001/XMLSchema#",
        }

    @pytest.mark.parametrize(
        "loader, dumper",
        [(from_turtle, to_turtle), (from_jsonld, to_jsonld), (from_graph, to_graph)],
    )
    def test_round_trip(self, loader, dumper):
        original = _provider(
            [_concept_dict(_graph), _collection_dict(_graph)],
            extra_data_loader=from_graph,
        )
        dump = dict_dumper(original, extra_data_dumper=dumper)
        reloaded = _provider(dump, extra_data_loader=loader)
        for actual, expected in zip(
            _all_extra_data(reloaded), _all_extra_data(original)
        ):
            assert isomorphic(actual, expected)


def test_exception_hierarchy():
    assert issubclass(ExtraDataException, SkosproviderException)
    assert issubclass(ProviderUnavailableException, SkosproviderException)
