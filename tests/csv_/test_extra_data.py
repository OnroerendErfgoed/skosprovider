import json

import pytest
from rdflib import Graph
from rdflib import Literal
from rdflib import URIRef

from skosprovider.csv.extra_data import concept_from_jsonld
from skosprovider.csv.extra_data import concept_from_turtle
from skosprovider.csv.extra_data import label_from_jsonld
from skosprovider.csv.extra_data import label_from_turtle
from skosprovider.csv.extra_data import note_from_jsonld
from skosprovider.csv.extra_data import note_from_turtle
from skosprovider.csv.extra_data import source_from_jsonld
from skosprovider.csv.extra_data import source_from_turtle
from skosprovider.csv.extra_data import to_jsonld
from skosprovider.csv.extra_data import to_turtle
from skosprovider.csv.provider import SimpleCsvProvider
from skosprovider.exceptions import ExtraDataException
from skosprovider.skos import Label


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
            {"id": "CSV"}, [["1", "Larch", "A tree."]], concept_extra_data_loader=loader
        )
        assert received == [["1", "Larch", "A tree."]]
        assert provider.get_by_id("1").extra_data is graph

    def test_failing_loader_raises(self):
        def loader(row):
            raise ValueError("boom")

        with pytest.raises(ExtraDataException) as excinfo:
            SimpleCsvProvider(
                {"id": "CSV"}, [["1", "Larch"]], concept_extra_data_loader=loader
            )
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
            concept_extra_data_loader=column_loader(4),
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


TURTLE = '<http://id.trees.org/1> <http://purl.org/dc/terms/creator> "Jane Doe" .'
JSONLD = json.dumps(
    {
        "@id": "http://id.trees.org/1",
        "http://purl.org/dc/terms/creator": "Jane Doe",
    }
)
EXPECTED = {
    (
        URIRef("http://id.trees.org/1"),
        URIRef("http://purl.org/dc/terms/creator"),
        Literal("Jane Doe"),
    )
}


class TestLoaders:
    @pytest.mark.parametrize(
        "loader, index",
        [
            (concept_from_turtle, 4),
            (label_from_turtle, 5),
            (note_from_turtle, 6),
            (source_from_turtle, 7),
        ],
    )
    def test_turtle_column(self, loader, index):
        row = ["1", "Larch", "", "", "", "", "", ""]
        row[index] = TURTLE
        assert set(loader(row)) == EXPECTED

    @pytest.mark.parametrize(
        "loader, index",
        [
            (concept_from_jsonld, 4),
            (label_from_jsonld, 5),
            (note_from_jsonld, 6),
            (source_from_jsonld, 7),
        ],
    )
    def test_jsonld_column(self, loader, index):
        row = ["1", "Larch", "", "", "", "", "", ""]
        row[index] = JSONLD
        assert set(loader(row)) == EXPECTED

    @pytest.mark.parametrize("loader", [concept_from_turtle, source_from_jsonld])
    @pytest.mark.parametrize(
        "row", [["1", "Larch"], ["1", "Larch", "", "", "", "", "", ""]]
    )
    def test_missing_or_empty_column(self, loader, row):
        assert loader(row) is None


class TestDumpers:
    @pytest.mark.parametrize("dumper", [to_turtle, to_jsonld])
    def test_without_extra_data(self, dumper):
        assert dumper(Label("Larch")) is None

    def test_to_turtle(self):
        graph = Graph().parse(data=TURTLE, format="turtle")
        assert (
            set(
                concept_from_turtle(
                    ["1", "", "", "", to_turtle(Label("Larch", extra_data=graph))]
                )
            )
            == EXPECTED
        )

    def test_to_jsonld(self):
        graph = Graph().parse(data=TURTLE, format="turtle")
        dumped = to_jsonld(Label("Larch", extra_data=graph))
        assert isinstance(dumped, str)
        assert set(concept_from_jsonld(["1", "", "", "", dumped])) == EXPECTED
