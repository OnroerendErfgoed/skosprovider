"""
This example round trips the extra_data of an RDFProvider with a loader and a
dumper of its own.

The loader only keeps the dct:creator of a SKOS-XL label and ignores
everything else. The dumper writes the creator back and adds a dct:publisher
that was not in the input.

The provider only reads the concept scheme passed as `concept_scheme_uri`,
which is needed when a graph holds more than one concept scheme.
"""

from pathlib import Path

from rdflib import Graph
from rdflib import Literal
from rdflib import URIRef
from rdflib.namespace import DCTERMS

from skosprovider.extra_data import SkosObject
from skosprovider.rdf import RDFProvider
from skosprovider.rdf import rdf_dumper
from skosprovider.skos import Label


def load_creator(graph: Graph, skos_object: SkosObject) -> Graph | None:
    """Load only the creator of a label."""
    if not isinstance(skos_object, Label):
        return None
    creators = Graph()
    for triple in graph.triples((None, DCTERMS.creator, None)):
        creators.add(triple)
    return creators if len(creators) else None


def dump_creator(obj: SkosObject) -> Graph | None:
    """Dump the creator and add a fixed publisher."""
    if obj.extra_data is None or not obj.uri:
        return None
    graph = Graph() + obj.extra_data
    graph.add((URIRef(obj.uri), DCTERMS.publisher, Literal("Tree Society")))
    return graph


graph = Graph().parse(Path(__file__).parents[1] / "data" / "trees.ttl")
provider = RDFProvider(
    {"id": "TREES"},
    graph,
    concept_scheme_uri="http://id.trees.org",
    extra_data_loader=load_creator,
)

dump = rdf_dumper(provider, extra_data_dumper=dump_creator)
print(dump.serialize(format="turtle"))
