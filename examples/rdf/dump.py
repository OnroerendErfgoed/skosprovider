'''
This script demonstrates dumping a
:class:`skosprovider.providers.SimpleCsvProvider` as a RDF Graph. In this
case, `n3` serialisation is used, other serialisations are available through
:mod:`rdflib`.
'''
>
import os
import csv

from skosprovider.providers import SimpleCsvProvider

from skosprovider.uri import UriPatternGenerator

from skosprovider.skos import ConceptScheme, Label, Note, Source

from skosprovider.rdf.utils import rdf_dumper

ifile = open(
    os.path.join(os.path.dirname(__file__), 'data', 'menu.csv'))

reader = csv.reader(ifile)

csvprovider = SimpleCsvProvider(
    {'id': 'MENU'},
    reader,
    uri_generator=UriPatternGenerator('http://id.python.org/menu/%s'),
    concept_scheme=ConceptScheme(
        uri='http://id.python.org/menu',
        labels=[
            Label(type='prefLabel', language='en', label='A pythonesque menu.')
        ],
        notes=[
            Note(
                type='changeNote',
                language='en',
                note="<strong>We didn't need no change notes when I was younger.</strong>",
                markup='HTML'
            )
        ],
        sources=[
            Source("Monthy Python's Flying Circus, 1970. Spam.")
        ]
    )
)

graph = rdf_dumper(csvprovider)

print(graph.serialize(format='n3'))
