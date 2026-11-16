"""
This example demonstrates a round trip of the extra_data of a note and a
source through a JsonLdProvider.

The note and the source have a uri, so they can have extra_data. Next to the
properties JsonLdProvider turns into attributes (rdf:value and
dct:bibliographicCitation), they have properties of their own, some of them
nested blank nodes. The `from_unmapped` loader keeps them as extra_data, the
`to_jsonld` dumper writes them to the dump again.

The loader only sees the triples about the object itself and the blank nodes
behind them. `@included` in the input has no meaning in RDF: the nodes in it
belong to the document, not to the object, so they are not loaded as
extra_data. When extra_data holds more than the object, eg. because another
loader set it, the dumper writes those other nodes in `@included`, so no
triple is lost in the dump.
"""

import json

from rdflib import Graph
from rdflib.compare import isomorphic
from rdflib.namespace import DCTERMS
from rdflib.namespace import RDF

from skosprovider.jsonld import extra_data
from skosprovider.jsonld.dumper import CONTEXT
from skosprovider.jsonld.dumper import DumpContext
from skosprovider.jsonld.dumper import to_jsonld
from skosprovider.jsonld.extra_data import from_unmapped
from skosprovider.jsonld.provider import JsonLdProvider

context = {
    **CONTEXT,
    "ex": "http://example.org/",
    "foaf": "http://xmlns.com/foaf/0.1/",
    "xsd": "http://www.w3.org/2001/XMLSchema#",
}

document = {
    "@context": context,
    "@graph": [
        {
            "@id": "http://id.trees.org",
            "@type": "skos:ConceptScheme",
            "skos:prefLabel": {"@value": "Trees", "@language": "en"},
        },
        {
            "@id": "http://id.trees.org/1",
            "@type": "skos:Concept",
            "skos:inScheme": {"@id": "http://id.trees.org"},
            "dct:identifier": "1",
            "skos:prefLabel": {"@value": "The Larch", "@language": "en"},
            "skos:definition": {
                "@id": "http://id.trees.org/notes/1",
                "rdf:value": {"@value": "A type of tree.", "@language": "en"},
                "dct:created": {"@value": "2020-03-01", "@type": "xsd:date"},
                "dct:creator": {
                    "foaf:name": "John Doe",
                    "foaf:mbox": {"@id": "mailto:john@example.org"},
                },
                "ex:reviewedBy": [
                    {"foaf:name": "Jane Doe"},
                    {"foaf:name": "Piet Pieters"},
                ],
            },
            "dct:source": {
                "@id": "http://id.trees.org/sources/1",
                "dct:bibliographicCitation": "Monthy Python's Flying Circus.",
                "dct:date": "1970",
                "dct:language": "en",
                "dct:publisher": {
                    "foaf:name": "BBC",
                    "ex:address": {"ex:city": "London", "ex:country": "UK"},
                },
                "ex:pages": 42,
            },
        },
    ],
}

metadata = {"id": "TREES"}
dump_context = {"context": context, "extra_data_dumper": extra_data.to_jsonld}


def note_and_source(provider):
    larch = provider.get_by_id("1")
    return {"note": larch.notes[0], "source": larch.sources[0]}


# 1. Load the document, keeping the unmapped properties as extra_data.
original = JsonLdProvider(metadata, document, extra_data_loader=from_unmapped)
for name, obj in note_and_source(original).items():
    print(f"--- extra_data of the {name}")
    print(obj.extra_data.serialize(format="turtle"))

# 2. Dump the provider, merging the extra_data into the nodes of the dump. The
#    blank nodes are written flat: a property refers to them by their @id and
#    they are in the @included of the object.
dumped = to_jsonld(original, DumpContext(provider=original, **dump_context))
larch = next(node for node in dumped["@graph"] if node["@id"].endswith("/1"))
print("--- dumped note")
print(json.dumps(larch["skos:definition"], indent=2))
print("--- dumped source")
print(json.dumps(larch["dct:source"], indent=2))

# 3. Load the dump again and compare the extra_data. Blank nodes get new ids
#    on every parse, so the graphs are compared with `isomorphic`.
reloaded = JsonLdProvider(metadata, dumped, extra_data_loader=from_unmapped)
reloaded_objects = note_and_source(reloaded)
for name, obj in note_and_source(original).items():
    same = isomorphic(obj.extra_data, reloaded_objects[name].extra_data)
    print(f"{name}: {len(obj.extra_data)} triples, round trip ok: {same}")

# 4. extra_data can hold more than the object, eg. when another loader set
#    it. Here the source gets triples about its publisher that has a uri, and
#    about a review that refers to the source. Neither is reachable from the
#    source, so the dumper writes them in @included.
source = note_and_source(original)["source"]
source.extra_data += Graph().parse(
    data="""
    @prefix dct: <http://purl.org/dc/terms/> .
    @prefix ex: <http://example.org/> .
    @prefix foaf: <http://xmlns.com/foaf/0.1/> .
    <http://example.org/bbc> foaf:name "BBC" ;
        foaf:homepage <https://www.bbc.co.uk> .
    <http://example.org/reviews/1> dct:subject <http://id.trees.org/sources/1> ;
        ex:rating 5 .
    """,
    format="turtle",
)
dumped_source = to_jsonld(source, DumpContext(provider=original, **dump_context))
print("--- dumped source with more than the source in its extra_data")
print(json.dumps(dumped_source["@included"], indent=2))

# 5. All triples are in the dump: the dumped source, without the triples of
#    its attributes, is the extra_data again. Loading the dump with
#    `from_unmapped` would keep only the triples about the source itself and
#    its blank nodes.
source_graph = Graph().parse(
    data=json.dumps({"@context": context, **dumped_source}), format="json-ld"
)
source_graph.remove((None, DCTERMS.bibliographicCitation, None))
source_graph.remove((None, RDF.type, DCTERMS.BibliographicResource))
in_dump = isomorphic(source_graph, source.extra_data)
print(f"source: {len(source.extra_data)} triples, all in the dump: {in_dump}")
