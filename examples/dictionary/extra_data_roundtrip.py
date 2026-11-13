"""
This example demonstrates a round trip of extra_data through a
DictionaryProvider.

The input dicts carry their extra_data as turtle strings. They are loaded with
the `from_turtle` loader, dumped again as compact JSON-LD with `to_jsonld`,
loaded a second time with `from_jsonld` and finally compared with the
original graphs.
"""

import json

from rdflib.compare import isomorphic

from skosprovider.dictionary.dumper import dict_dumper
from skosprovider.dictionary.extra_data import from_jsonld
from skosprovider.dictionary.extra_data import from_turtle
from skosprovider.dictionary.extra_data import to_jsonld
from skosprovider.dictionary.provider import DictionaryProvider
from skosprovider.uri import UriPatternGenerator

PREFIXES = """
@prefix dct: <http://purl.org/dc/terms/> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
"""

larch = {
    "id": "1",
    "uri": "http://id.trees.org/1",
    "labels": [
        {
            "type": "prefLabel",
            "language": "en",
            "label": "The Larch",
            "extra_data": PREFIXES
            + """
            <http://id.trees.org/1> dct:creator "Jane Doe" .
            """,
        },
    ],
    "notes": [
        {
            "type": "definition",
            "language": "en",
            "note": "A type of tree.",
            "extra_data": PREFIXES
            + """
            <http://id.trees.org/1> dct:modified "2024-05-01"^^xsd:date .
            """,
        },
    ],
    "sources": [
        {
            "citation": "Monthy Python. Episode Three: How to recognise "
            "different types of trees from quite a long way away.",
            "extra_data": PREFIXES
            + """
            <http://id.trees.org/1> dct:source [ dct:title "Flying Circus" ] .
            """,
        },
    ],
    "member_of": ["2"],
    "extra_data": PREFIXES
    + """
    <http://id.trees.org/1> dct:created "2020-01-01"^^xsd:date ;
        dct:creator [ dct:title "Tree Society" ] .
    """,
}

species = {
    "id": "2",
    "uri": "http://id.trees.org/2",
    "type": "collection",
    "labels": [{"type": "prefLabel", "language": "en", "label": "Trees by species"}],
    "members": ["1"],
    "extra_data": PREFIXES
    + """
    <http://id.trees.org/2> dct:created "2021-06-15"^^xsd:date .
    """,
}

metadata = {"id": "TREES"}
uri_generator = UriPatternGenerator("http://id.trees.org/%s")

# 1. Load the dicts, turning the turtle strings into rdflib graphs.
original = DictionaryProvider(
    metadata,
    [larch, species],
    uri_generator=uri_generator,
    extra_data_loader=from_turtle,
)

# 2. Dump the provider, turning the graphs into compact JSON-LD dicts.
dumped = dict_dumper(original, extra_data_dumper=to_jsonld)
print(json.dumps(dumped, indent=2))

# 3. Load the dump again, this time reading JSON-LD.
reloaded = DictionaryProvider(
    metadata,
    dumped,
    uri_generator=uri_generator,
    extra_data_loader=from_jsonld,
)


# 4. Compare the extra_data of every object. Blank nodes get new ids on every
#    parse, so the graphs are compared with `isomorphic`.
def all_extra_data(provider):
    larch = provider.get_by_id("1")
    species = provider.get_by_id("2")
    return {
        "concept": larch.extra_data,
        "label": larch.labels[0].extra_data,
        "note": larch.notes[0].extra_data,
        "source": larch.sources[0].extra_data,
        "collection": species.extra_data,
    }


reloaded_extra_data = all_extra_data(reloaded)
for name, graph in all_extra_data(original).items():
    same = isomorphic(graph, reloaded_extra_data[name])
    print(f"{name}: {len(graph)} triples, round trip ok: {same}")
