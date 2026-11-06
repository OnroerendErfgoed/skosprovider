"""
This example demonstrates a round trip of extra_data through an RDFProvider.

The graph contains triples that RDFProvider does not turn into attributes, eg.
a skos:notation or a dct:creator. The `from_unmapped` loader keeps them as
extra_data, the `to_unmapped` dumper writes them to the dump again. The dump is
loaded a second time and its extra_data is compared with the original.
"""

from rdflib import Graph
from rdflib.compare import isomorphic

from skosprovider.rdf.dumper import rdf_dumper
from skosprovider.rdf.extra_data import from_unmapped
from skosprovider.rdf.extra_data import to_unmapped
from skosprovider.rdf.provider import RDFProvider

TREES = """
@prefix skos: <http://www.w3.org/2004/02/skos/core#> .
@prefix dct: <http://purl.org/dc/terms/> .
@prefix ex: <http://example.org/> .

<http://id.trees.org> a skos:ConceptScheme ;
    skos:prefLabel "Trees"@en ;
    dct:creator "Jane Doe" .

<http://id.trees.org/1> a skos:Concept ;
    skos:inScheme <http://id.trees.org> ;
    dct:identifier "1" ;
    skos:prefLabel "The Larch"@en ;
    skos:notation "L" ;
    ex:height [ ex:value 30 ; ex:unit "metre" ] ;
    dct:source [
        dct:bibliographicCitation "Monthy Python's Flying Circus." ;
        dct:date "1970"
    ] .

<http://id.trees.org/2> a skos:Collection ;
    skos:inScheme <http://id.trees.org> ;
    dct:identifier "2" ;
    skos:prefLabel "Trees by species"@en ;
    skos:member <http://id.trees.org/1> ;
    dct:created "2021-06-15" .
"""

metadata = {"id": "TREES"}
graph = Graph().parse(data=TREES, format="turtle")
# 1. Load the graph, keeping the unmapped triples as extra_data.
original = RDFProvider(metadata, graph, extra_data_loader=from_unmapped)

# 2. Dump the provider, merging the extra_data into the dump.
dumped = rdf_dumper(original, extra_data_dumper=to_unmapped)
print(dumped.serialize(format="turtle"))

# 3. Load the dump again.
reloaded = RDFProvider(metadata, dumped, extra_data_loader=from_unmapped)


# 4. Compare the extra_data of every object. Blank nodes get new ids on every
#    parse, so the graphs are compared with `isomorphic`.
def all_extra_data(provider):
    larch = provider.get_by_id("1")
    return {
        "concept scheme": provider.concept_scheme.extra_data,
        "concept": larch.extra_data,
        "source": larch.sources[0].extra_data,
        "collection": provider.get_by_id("2").extra_data,
    }


reloaded_extra_data = all_extra_data(reloaded)
for name, graph in all_extra_data(original).items():
    same = isomorphic(graph, reloaded_extra_data[name])
    print(f"{name}: {len(graph)} triples, round trip ok: {same}")
