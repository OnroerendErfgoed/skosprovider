import json

import pytest
from rdflib import Graph
from rdflib import Literal
from rdflib import URIRef

from skosprovider.csv.extra_data import from_jsonld
from skosprovider.csv.extra_data import from_turtle
from skosprovider.csv.extra_data import to_jsonld
from skosprovider.csv.extra_data import to_turtle
from skosprovider.csv.provider import SimpleCsvProvider
from skosprovider.exceptions import ExtraDataException
from skosprovider.skos import Concept
from skosprovider.skos import Label
from skosprovider.skos import Note
from skosprovider.skos import Source


class TestSimpleCsvProviderExtraData:
    def test_default_ignores_extra_data(self):
        provider = SimpleCsvProvider({"id": "CSV"}, [["1", "Larch"]])
        assert provider.get_by_id("1").extra_data is None

    def test_loader_receives_row_and_skos_object(self):
        graph = Graph()
        received = []

        def loader(row, skos_object):
            received.append((row, skos_object))
            return graph if isinstance(skos_object, Concept) else None

        provider = SimpleCsvProvider(
            {"id": "CSV"}, [["1", "Larch", "A tree."]], extra_data_loader=loader
        )
        concept = provider.get_by_id("1")
        assert received == [
            (["1", "Larch", "A tree."], concept.labels[0]),
            (["1", "Larch", "A tree."], concept.notes[0]),
            (["1", "Larch", "A tree."], concept),
        ]
        assert concept.extra_data is graph

    def test_failing_loader_raises(self):
        def loader(row, skos_object):
            if isinstance(skos_object, Concept):
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
        columns = {Concept: 4, Label: 5, Note: 6, Source: 7}

        def loader(row, skos_object):
            return graphs[row[columns[type(skos_object)]]]

        provider = SimpleCsvProvider({"id": "CSV"}, [row], extra_data_loader=loader)
        concept = provider.get_by_id("1")
        assert concept.extra_data is graphs["c"]
        assert concept.labels[0].extra_data is graphs["l"]
        assert concept.notes[0].extra_data is graphs["n"]
        assert concept.sources[0].extra_data is graphs["s"]

    def test_nested_loader_not_called_without_object(self):
        def loader(row, skos_object):
            if isinstance(skos_object, (Note, Source)):
                pytest.fail(f"loader called for {skos_object!r}")

        provider = SimpleCsvProvider(
            {"id": "CSV"}, [["1", "Larch", ""]], extra_data_loader=loader
        )
        concept = provider.get_by_id("1")
        assert concept.notes == []
        assert concept.sources == []

    def test_failing_nested_loader_raises(self):
        def loader(row, skos_object):
            if isinstance(skos_object, Source):
                raise ValueError("boom")

        with pytest.raises(ExtraDataException) as excinfo:
            SimpleCsvProvider(
                {"id": "CSV"},
                [["1", "Larch", "", "A book."]],
                extra_data_loader=loader,
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
        "skos_object, index",
        [
            (Concept(1), 4),
            (Label("Larch"), 5),
            (Note("A tree."), 6),
            (Source("A book."), 7),
        ],
    )
    @pytest.mark.parametrize(
        "loader, cell", [(from_turtle, TURTLE), (from_jsonld, JSONLD)]
    )
    def test_column_of_the_type_of_object(self, loader, cell, skos_object, index):
        row = ["1", "Larch", "", "", "", "", "", ""]
        row[index] = cell
        assert set(loader(row, skos_object)) == EXPECTED

    @pytest.mark.parametrize("loader", [from_turtle, from_jsonld])
    @pytest.mark.parametrize(
        "row", [["1", "Larch"], ["1", "Larch", "", "", "", "", "", ""]]
    )
    def test_missing_or_empty_column(self, loader, row):
        assert loader(row, Concept(1)) is None


class TestDumpers:
    @pytest.mark.parametrize("dumper", [to_turtle, to_jsonld])
    def test_without_extra_data(self, dumper):
        assert dumper(Label("Larch")) is None

    def test_to_turtle(self):
        graph = Graph().parse(data=TURTLE, format="turtle")
        assert (
            set(
                from_turtle(
                    ["1", "", "", "", to_turtle(Label("Larch", extra_data=graph))],
                    Concept(1),
                )
            )
            == EXPECTED
        )

    def test_to_jsonld(self):
        graph = Graph().parse(data=TURTLE, format="turtle")
        dumped = to_jsonld(Label("Larch", extra_data=graph))
        assert isinstance(dumped, str)
        assert set(from_jsonld(["1", "", "", "", dumped], Concept(1))) == EXPECTED
