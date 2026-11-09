"""
This script demonstrates dumping a
:class:`skosprovider.providers.SimpleCsvProvider` as a RDF Graph. In this
case, `n3` serialisation is used, other serialisations are available through
:mod:`rdflib`.
"""

import csv
import os

from skosprovider.providers import SimpleCsvProvider
from skosprovider.rdf.dumper import rdf_dumper
from skosprovider.skos import ConceptScheme
from skosprovider.skos import Label
from skosprovider.skos import Note
from skosprovider.skos import Source
from skosprovider.uri import UriPatternGenerator

with open(os.path.join(os.path.dirname(__file__), "data", "menu.csv")) as ifile:
    csvprovider = SimpleCsvProvider(
        {"id": "MENU"},
        csv.reader(ifile),
        uri_generator=UriPatternGenerator("http://id.python.org/menu/%s"),
        concept_scheme=ConceptScheme(
            uri="http://id.python.org/menu",
            labels=[
                Label(type="prefLabel", language="en", label="A pythonesque menu.")
            ],
            notes=[
                Note(
                    type="changeNote",
                    language="en",
                    note="<strong>We didn't need no change notes when I was younger.</strong>",
                    markup="HTML",
                )
            ],
            sources=[Source("Monthy Python's Flying Circus, 1970. Spam.")],
        ),
    )

graph = rdf_dumper(csvprovider)

print(graph.serialize(format="n3"))
