import json
import os

import pytest
from rdflib import Graph

from skosprovider.providers import DictionaryProvider
from skosprovider.rdf.providers import RDFProvider
from skosprovider.skos import ConceptScheme
from skosprovider.skos import Label
from skosprovider.skos import Note
from skosprovider.uri import UriPatternGenerator

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'data')


@pytest.fixture(scope='module')
def products_provider():
    products_graph = Graph()
    products_graph.parse(os.path.join(DATA_DIR, 'simple_turtle_products'), format='turtle')
    return RDFProvider({'id': 'PRODUCTS'}, products_graph)


@pytest.fixture(scope='module')
def trees_provider():
    trees_graph = Graph()
    trees_graph.parse(os.path.join(DATA_DIR, 'trees.xml'), format='application/rdf+xml')
    return RDFProvider({'id': 'TREES'}, trees_graph)


@pytest.fixture(scope='module')
def materials_provider():
    materials_data = json.load(open(os.path.join(DATA_DIR, 'materiaal.txt')))['materiaal']
    return DictionaryProvider(
        {'id': 'Materials'},
        materials_data,
        uri_generator=UriPatternGenerator('https://id.erfgoed.net/thesauri/materialen/%s'),
        concept_scheme=ConceptScheme(
            uri='https://id.erfgoed.net/thesauri/materialen',
            labels=[Label(type='prefLabel', language='nl', label='Materialen')],
            notes=[Note(
                type='scopeNote',
                language='nl',
                note='Materialen zijn grondstoffen of halfafgewerkte producten die vaak een rol spelen bij onroerend erfgoed.'
            )]
        )
    )
