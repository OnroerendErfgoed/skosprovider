"""
This example loads a turtle file into an RDFProvider and dumps the provider
to turtle again.
"""

from pathlib import Path

from rdflib import Graph

from skosprovider.rdf import RDFProvider
from skosprovider.rdf import rdf_dumper

graph = Graph().parse(Path(__file__).parents[1] / "data" / "trees.ttl")
provider = RDFProvider({"id": "TREES"}, graph)

dump = rdf_dumper(provider)
print(dump.serialize(format="turtle"))
