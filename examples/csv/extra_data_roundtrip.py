"""
This example demonstrates a round trip of extra_data through a
SimpleCsvProvider.

The rows carry the extra_data of the concept, label, note and source as turtle
strings in the fifth to eighth column. They are loaded with the
`*_from_turtle` loaders, dumped with `csv_dumper` and the `to_turtle` dumper,
written to csv and read again, and finally compared with the original graphs.
"""

import csv
import io

from rdflib.compare import isomorphic

from skosprovider.csv.dumper import csv_dumper
from skosprovider.csv.extra_data import concept_from_turtle
from skosprovider.csv.extra_data import label_from_turtle
from skosprovider.csv.extra_data import note_from_turtle
from skosprovider.csv.extra_data import source_from_turtle
from skosprovider.csv.extra_data import to_turtle
from skosprovider.csv.provider import SimpleCsvProvider

PREFIXES = "@prefix dct: <http://purl.org/dc/terms/> .\n"

rows = [
    [
        "1",
        "Egg and Bacon",
        "A breakfast.",
        "Monthy Python, Episode Twenty-five.",
        PREFIXES + '<urn:menu:1> dct:created "1970" .',
        PREFIXES + '<urn:menu:1:label> dct:creator "Terry Jones" .',
        PREFIXES + '<urn:menu:1:note> dct:creator "Michael Palin" .',
        PREFIXES + '<urn:menu:1:source> dct:title "Spam" .',
    ],
    ["2", "Egg and Spam"],
]

loaders = {
    "concept_extra_data_loader": concept_from_turtle,
    "label_extra_data_loader": label_from_turtle,
    "note_extra_data_loader": note_from_turtle,
    "source_extra_data_loader": source_from_turtle,
}
metadata = {"id": "MENU"}

# 1. Load the rows, turning the turtle strings into rdflib graphs.
original = SimpleCsvProvider(metadata, rows, **loaders)

# 2. Dump the provider to rows, turning the graphs into turtle strings again,
#    and write them as csv.
file = io.StringIO()
csv.writer(file).writerows(csv_dumper(original, extra_data_dumper=to_turtle))
print(file.getvalue())

# 3. Read the csv and load it again.
file.seek(0)
reloaded = SimpleCsvProvider(metadata, csv.reader(file), **loaders)


# 4. Compare the extra_data of every object. Blank nodes get new ids on every
#    parse, so the graphs are compared with `isomorphic`.
def all_extra_data(provider):
    egg_and_bacon = provider.get_by_id("1")
    return {
        "concept": egg_and_bacon.extra_data,
        "label": egg_and_bacon.labels[0].extra_data,
        "note": egg_and_bacon.notes[0].extra_data,
        "source": egg_and_bacon.sources[0].extra_data,
    }


reloaded_extra_data = all_extra_data(reloaded)
for name, graph in all_extra_data(original).items():
    same = isomorphic(graph, reloaded_extra_data[name])
    print(f"{name}: {len(graph)} triples, round trip ok: {same}")
