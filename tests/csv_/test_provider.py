import csv
import os

import pytest

from skosprovider.csv.provider import SimpleCsvProvider
from skosprovider.skos import Concept
from skosprovider.skos import ConceptScheme
from skosprovider.skos import Note


class TestSimpleCsvProvider:

    @pytest.fixture
    def csv_file(self):
        data_dir = os.path.join(os.path.dirname(__file__), os.pardir, "data")
        ifile = open(os.path.join(data_dir, "menu.csv"))
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
