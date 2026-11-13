"""
This example demonstrates a round trip of extra_data through an RDFProvider.

Every object in the graph has a dct:creator, a triple that RDFProvider does not
turn into an attribute. The `from_unmapped` loader keeps it as the extra_data of
the object and the `to_unmapped` dumper writes it back. Extra data is only
supported for the concept scheme, concepts, collections and for SKOS-XL
labels, notes and sources with a URI. A blank node has no identity outside the
graph it was read from, so a blank label, note or source gets no extra_data.
"""

from rdflib import Graph
from rdflib.compare import isomorphic

from skosprovider.rdf import RDFProvider
from skosprovider.rdf import rdf_dumper
from skosprovider.rdf.extra_data import from_unmapped
from skosprovider.rdf.extra_data import to_unmapped

TREES = """
@prefix skos: <http://www.w3.org/2004/02/skos/core#> .
@prefix skosxl: <http://www.w3.org/2008/05/skos-xl#> .
@prefix dct: <http://purl.org/dc/terms/> .
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .

<http://id.trees.org> a skos:ConceptScheme ;
    dct:creator "Scheme creator" .

<http://id.trees.org/1> a skos:Concept ;
    skos:inScheme <http://id.trees.org> ;
    dct:identifier "1" ;
    dct:creator "Concept creator" ;
    skosxl:prefLabel <http://id.trees.org/labels/1> , [
        a skosxl:Label ;
        skosxl:literalForm "Lork"@nl ;
        dct:creator "Blank label creator"
    ] ;
    skos:definition <http://id.trees.org/notes/1> , [
        rdf:value "Een soort boom."@nl ;
        dct:creator "Blank note creator"
    ] ;
    dct:source <http://id.trees.org/sources/1> , [
        dct:bibliographicCitation "An anonymous source." ;
        dct:creator "Blank source creator"
    ] .

<http://id.trees.org/labels/1> a skosxl:Label ;
    skosxl:literalForm "The Larch"@en ;
    dct:creator "Label creator" .

<http://id.trees.org/notes/1>
    rdf:value "A type of tree."@en ;
    dct:creator "Note creator" .

<http://id.trees.org/sources/1>
    dct:bibliographicCitation "A source with a uri." ;
    dct:creator "Source creator" .
"""


def creators(obj):
    if obj.extra_data is None:
        return None
    return sorted(str(creator) for creator in obj.extra_data.objects())


graph = Graph().parse(data=TREES, format="turtle")
provider = RDFProvider({"id": "TREES"}, graph, extra_data_loader=from_unmapped)
larch = provider.get_by_id("1")

print("Loaded extra_data")
print("-----------------")
print(f"{provider.concept_scheme!r}: {creators(provider.concept_scheme)}")
print(f"{larch!r}: {creators(larch)}")
for obj in [*larch.labels, *larch.notes, *larch.sources]:
    print(f"{obj!r}: {creators(obj)}")
print("")

dump = rdf_dumper(provider, extra_data_dumper=to_unmapped)

print("Dump")
print("----")
print(dump.serialize(format="turtle"))

reloaded = RDFProvider({"id": "TREES"}, dump, extra_data_loader=from_unmapped)
reloaded_larch = reloaded.get_by_id("1")

copies = {
    repr(obj): obj
    for obj in [
        reloaded_larch,
        *reloaded_larch.labels,
        *reloaded_larch.notes,
        *reloaded_larch.sources,
    ]
}

print("Round trip")
print("----------")
for original in [larch, *larch.labels, *larch.notes, *larch.sources]:
    copy = copies[repr(original)]
    if original.extra_data is None:
        same = copy.extra_data is None
    else:
        same = isomorphic(original.extra_data, copy.extra_data)
    print(f"{original!r}: {'unchanged' if same else 'CHANGED'}")
