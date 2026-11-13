import csv
import io
import os

import pytest
from rdflib import Graph
from rdflib.compare import isomorphic

from skosprovider.csv.dumper import csv_dumper
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
from skosprovider.dictionary.dumper import dict_dumper
from skosprovider.dictionary.extra_data import from_graph
from skosprovider.dictionary.provider import DictionaryProvider
from skosprovider.exceptions import ExtraDataException
from skosprovider.skos import Label
from skosprovider.skos import Note
from skosprovider.skos import Source


def _graph(subject):
    return Graph().parse(
        data=f'<{subject}> <http://purl.org/dc/terms/creator> "Jane Doe" .',
        format="turtle",
    )


def _write_and_read(rows):
    file = io.StringIO()
    csv.writer(file).writerows(rows)
    file.seek(0)
    return list(csv.reader(file))


@pytest.fixture
def menu():
    data_dir = os.path.join(os.path.dirname(__file__), os.pardir, "data")
    with open(os.path.join(data_dir, "menu.csv")) as file:
        return list(csv.reader(file))


@pytest.fixture
def larch():
    return DictionaryProvider(
        {"id": "TREES", "default_language": "nl"},
        [
            {
                "id": "1",
                "uri": "http://id.trees.org/1",
                "labels": [
                    Label("The Larch", "prefLabel", "en"),
                    Label("De Lariks", "prefLabel", "nl", extra_data=_graph("urn:l")),
                ],
                "notes": [
                    Note("A definition.", "definition", "en"),
                    Note("A tree.", "note", "en", extra_data=_graph("urn:n")),
                ],
                "sources": [Source("A book.", extra_data=_graph("urn:s"))],
                "extra_data": _graph("http://id.trees.org/1"),
            },
            {"id": "2", "type": "collection", "members": ["1"]},
        ],
        extra_data_loader=from_graph,
    )


class TestCsvDumper:
    def test_round_trip_menu(self, menu):
        provider = SimpleCsvProvider({"id": "MENU"}, menu)
        reloaded = SimpleCsvProvider({"id": "MENU"}, csv_dumper(provider))
        assert dict_dumper(reloaded) == dict_dumper(provider)

    def test_row(self, larch):
        assert csv_dumper(larch) == [["1", "De Lariks", "A tree.", "A book."]]

    def test_language(self, larch):
        assert csv_dumper(larch, language="en")[0][1] == "The Larch"

    def test_trailing_empty_cells_are_left_out(self):
        provider = DictionaryProvider(
            {"id": "TREES"},
            [{"id": "1", "labels": [{"type": "prefLabel", "label": "Larch"}]}],
        )
        assert csv_dumper(provider) == [["1", "Larch"]]

    def test_extra_data_columns(self, larch):
        row = csv_dumper(larch, extra_data_dumper=to_turtle)[0]
        assert len(row) == 8
        assert isomorphic(
            Graph().parse(data=row[4], format="turtle"),
            _graph("http://id.trees.org/1"),
        )
        for index, subject in ((5, "urn:l"), (6, "urn:n"), (7, "urn:s")):
            assert isomorphic(
                Graph().parse(data=row[index], format="turtle"), _graph(subject)
            )

    @pytest.mark.parametrize(
        "dumper, loaders",
        [
            (
                to_turtle,
                (
                    concept_from_turtle,
                    label_from_turtle,
                    note_from_turtle,
                    source_from_turtle,
                ),
            ),
            (
                to_jsonld,
                (
                    concept_from_jsonld,
                    label_from_jsonld,
                    note_from_jsonld,
                    source_from_jsonld,
                ),
            ),
        ],
    )
    def test_extra_data_round_trip(self, larch, dumper, loaders):
        rows = _write_and_read(csv_dumper(larch, extra_data_dumper=dumper))
        concept_loader, label_loader, note_loader, source_loader = loaders
        reloaded = SimpleCsvProvider(
            {"id": "TREES"},
            rows,
            concept_extra_data_loader=concept_loader,
            label_extra_data_loader=label_loader,
            note_extra_data_loader=note_loader,
            source_extra_data_loader=source_loader,
        ).get_by_id("1")
        assert isomorphic(reloaded.extra_data, _graph("http://id.trees.org/1"))
        assert isomorphic(reloaded.labels[0].extra_data, _graph("urn:l"))
        assert isomorphic(reloaded.notes[0].extra_data, _graph("urn:n"))
        assert isomorphic(reloaded.sources[0].extra_data, _graph("urn:s"))

    def test_dumper_error(self, larch):
        def dumper(obj):
            if getattr(obj, "citation", None) == "A book.":
                raise ValueError("boom")

        with pytest.raises(ExtraDataException) as excinfo:
            csv_dumper(larch, extra_data_dumper=dumper)
        assert excinfo.value.message == "Failed to dump extra_data: boom"
        assert excinfo.value.__notes__ == [
            "while processing Source('A book.')",
            "while processing concept '1'",
        ]
