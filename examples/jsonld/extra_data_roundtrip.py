"""
This example demonstrates a round trip of extra_data through a JsonLdProvider.

The document contains properties that JsonLdProvider does not turn into
attributes, eg. a skos:notation or a dct:creator. The `from_unmapped` loader
keeps them as extra_data, the `extra_data.to_jsonld` dumper writes them to the
dump again. The dump uses a context with the `ex` prefix of the document, so
the extra properties look like they did in the input. The dump is loaded a
second time and its extra_data is compared with the original. Only a note,
source or SKOS-XL label with a uri can have extra_data: a blank node has no
identity outside the document it was read from.
"""

import json

from rdflib import Graph
from rdflib.compare import isomorphic

from skosprovider.jsonld import extra_data
from skosprovider.jsonld.dumper import CONTEXT
from skosprovider.jsonld.dumper import DumpContext
from skosprovider.jsonld.dumper import to_jsonld
from skosprovider.jsonld.extra_data import from_unmapped
from skosprovider.jsonld.provider import JsonLdProvider

document = {
    "@context": {
        "skos": "http://www.w3.org/2004/02/skos/core#",
        "skosxl": "http://www.w3.org/2008/05/skos-xl#",
        "dct": "http://purl.org/dc/terms/",
        "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
        "ex": "http://example.org/",
    },
    "@graph": [
        {
            "@id": "http://id.trees.org",
            "@type": "skos:ConceptScheme",
            "skos:prefLabel": {"@value": "Trees", "@language": "en"},
            "dct:creator": "Jane Doe",
        },
        {
            "@id": "http://id.trees.org/1",
            "@type": "skos:Concept",
            "skos:inScheme": {"@id": "http://id.trees.org"},
            "dct:identifier": "1",
            "skos:prefLabel": {"@value": "The Larch", "@language": "en"},
            "skos:notation": "L",
            "ex:height": {"ex:value": 30, "ex:unit": "metre"},
            "skosxl:altLabel": {
                "@id": "http://id.trees.org/labels/1",
                "@type": "skosxl:Label",
                "skosxl:literalForm": {"@value": "Lariks", "@language": "nl"},
                "dct:created": "2020",
            },
            "skos:definition": {
                "@id": "http://id.trees.org/notes/1",
                "rdf:value": {"@value": "A type of tree.", "@language": "en"},
                "dct:creator": "John Doe",
            },
            "dct:source": {
                "@id": "http://id.trees.org/sources/1",
                "dct:bibliographicCitation": "Monthy Python's Flying Circus.",
                "dct:date": "1970",
            },
        },
    ],
}

metadata = {"id": "TREES"}

# 1. Load the document, keeping the unmapped properties as extra_data.
original = JsonLdProvider(metadata, document, extra_data_loader=from_unmapped)

# 2. Dump the provider, merging the extra_data into the nodes of the dump.
context = {**CONTEXT, "ex": "http://example.org/"}
dumped = to_jsonld(
    original,
    DumpContext(
        provider=original,
        context=context,
        extra_data_dumper=extra_data.to_jsonld,
    ),
)
print(json.dumps(dumped, indent=2))

# 3. Load the dump again.
reloaded = JsonLdProvider(metadata, dumped, extra_data_loader=from_unmapped)


# 4. Compare the extra_data of every object. Blank nodes get new ids on every
#    parse, so the graphs are compared with `isomorphic`.
def all_extra_data(provider):
    larch = provider.get_by_id("1")
    return {
        "concept scheme": provider.concept_scheme.extra_data,
        "concept": larch.extra_data,
        "xl label": next(label for label in larch.labels if label.uri).extra_data,
        "note": larch.notes[0].extra_data,
        "source": larch.sources[0].extra_data,
    }


reloaded_extra_data = all_extra_data(reloaded)
for name, graph in all_extra_data(original).items():
    same = isomorphic(graph, reloaded_extra_data[name])
    print(f"{name}: {len(graph)} triples, round trip ok: {same}")


# 5. extra_data can hold more than the object itself, eg. when a loader other
#    than `from_unmapped` set it. The nodes that are not the object, linked to
#    it or not, are dumped in `@included`, so no triple is lost.
larch = original.get_by_id("1")
label = next(label for label in larch.labels if label.uri)
label.extra_data = Graph().parse(
    data="""
    @prefix dct: <http://purl.org/dc/terms/> .
    @prefix foaf: <http://xmlns.com/foaf/0.1/> .
    <http://id.trees.org/labels/1> dct:creator <http://example.org/jane> .
    <http://example.org/jane> foaf:name "Jane Doe" .
    <http://example.org/john> foaf:name "John Doe" ;
        foaf:knows <http://example.org/jane> .
    """,
    format="turtle",
)
dumped_larch = to_jsonld(
    larch,
    DumpContext(
        provider=original, context=context, extra_data_dumper=extra_data.to_jsonld
    ),
)
print(json.dumps(dumped_larch["skosxl:altLabel"], indent=2))

dumped_graph = Graph().parse(
    data=json.dumps({"@context": context, **dumped_larch}), format="json-ld"
)
kept = all(triple in dumped_graph for triple in label.extra_data)
print(f"label: {len(label.extra_data)} triples, all in the dump: {kept}")
