"""
This script demonstrates how :class:`~skosprovider.rdf.providers.RDFProvider`
captures unknown RDF predicates as ``extra_data`` and how
:func:`~skosprovider.rdf.utils.rdf_dumper` can round-trip them back via a
custom :data:`~skosprovider.rdf.utils.RdfSerializer`.

The input graph contains a ``skos:notation`` triple for the larch concept.
``skos:notation`` is not a predicate the provider extracts explicitly, so it
ends up in ``extra_data`` as a sub-graph.  The serializer re-injects those
triples when dumping so no information is lost.
"""

import json

import rdflib
from rdflib import Graph
from rdflib import Literal
from rdflib.namespace import DCTERMS
from rdflib.namespace import RDF
from rdflib.namespace import SKOS
from rdflib.term import URIRef
from skosprovider.jsonld import CONTEXT
from skosprovider.jsonld import jsonld_dumper
from skosprovider.rdf.providers import RDFProvider
from skosprovider.rdf.utils import rdf_dumper
from skosprovider.skos import SkosObject

# Build an RDF graph by hand, including a skos:notation triple that the
# provider does not handle natively.
source_graph = Graph()
source_graph.namespace_manager.bind("skos", SKOS)
source_graph.namespace_manager.bind("dcterms", DCTERMS)

CS = URIRef("http://id.trees.org")
LARCH = URIRef("http://id.trees.org/1")
CHESTNUT = URIRef("http://id.trees.org/2")
SPECIES = URIRef("http://id.trees.org/3")

source_graph.add((CS, RDF.type, SKOS.ConceptScheme))
source_graph.add((CS, DCTERMS.identifier, Literal("TREES")))
source_graph.add((CS, SKOS.prefLabel, Literal("Trees", lang="en")))
source_graph.add((CS, SKOS.prefLabel, Literal("Bomen", lang="nl")))

source_graph.add((LARCH, RDF.type, SKOS.Concept))
source_graph.add((LARCH, SKOS.inScheme, CS))
source_graph.add((LARCH, DCTERMS.identifier, Literal("1")))
source_graph.add((LARCH, SKOS.prefLabel, Literal("The Larch", lang="en")))
source_graph.add((LARCH, SKOS.prefLabel, Literal("De Lariks", lang="nl")))
source_graph.add((LARCH, SKOS.definition, Literal("A type of tree.", lang="en")))
source_graph.add((LARCH, SKOS.notation, Literal("larch-001")))  # extra predicate

source_graph.add((CHESTNUT, RDF.type, SKOS.Concept))
source_graph.add((CHESTNUT, SKOS.inScheme, CS))
source_graph.add((CHESTNUT, DCTERMS.identifier, Literal("2")))
source_graph.add((CHESTNUT, SKOS.prefLabel, Literal("The Chestnut", lang="en")))
source_graph.add((CHESTNUT, SKOS.altLabel, Literal("De Paardekastanje", lang="nl")))
source_graph.add(
    (CHESTNUT, SKOS.definition, Literal("A different type of tree.", lang="en"))
)

source_graph.add((SPECIES, RDF.type, SKOS.Collection))
source_graph.add((SPECIES, SKOS.inScheme, CS))
source_graph.add((SPECIES, DCTERMS.identifier, Literal("3")))
source_graph.add((SPECIES, SKOS.prefLabel, Literal("Trees by species", lang="en")))
source_graph.add((SPECIES, SKOS.prefLabel, Literal("Bomen per soort", lang="nl")))
source_graph.add((SPECIES, SKOS.member, LARCH))
source_graph.add((SPECIES, SKOS.member, CHESTNUT))

# --- Load via RDFProvider ---
# skos:notation is not in _KNOWN_CONCEPT_PREDICATES, so it lands in
# extra_data as a sub-graph containing the leftover triple(s).
provider = RDFProvider({"id": "TREES"}, source_graph)

larch = provider.get_by_uri("http://id.trees.org/1")
assert larch, "Larch tree not found"

msg = "Larch extra_data (sub-graph with skos:notation)"
print(msg)
print(len(msg) * "=")
if larch.extra_data is not None:
    print(larch.extra_data.serialize(format="n3"))
else:
    print("None")

chestnut = provider.get_by_uri("http://id.trees.org/2")
assert chestnut, "Chestnut tree not found"
msg = "Chestnut extra_data (no unknown predicates → None)"
print(msg)
print(len(msg) * "=")
print(chestnut.extra_data)


def extra_data_rdf_serializer(graph: Graph, obj: SkosObject) -> None:
    """Re-inject the extra_data sub-graph triples into the output graph."""
    if not isinstance(obj.extra_data, rdflib.Graph):
        return
    graph += obj.extra_data


# --- Dump back to RDF, re-injecting extra_data triples ---
dumped = rdf_dumper(provider, extra_data_serializer=extra_data_rdf_serializer)
msg = "Round-tripped graph (skos:notation preserved)"
print(msg)
print(len(msg) * "=")
print(dumped.serialize(format="n3"))


def extra_data_jsonld_serializer(doc: dict, obj: SkosObject) -> None:
    """Merge extra_data sub-graph triples into the JSON-LD concept document."""
    if not isinstance(obj.extra_data, rdflib.Graph):
        return

    nodes = json.loads(obj.extra_data.serialize(format="json-ld"))
    if not nodes:
        return
    node = nodes[0]
    node.pop("@id", None)
    doc.update(node)


# --- Dump to JSON-LD, re-injecting extra_data triples ---
doc = jsonld_dumper(
    provider, context=CONTEXT, extra_data_serializer=extra_data_jsonld_serializer
)
msg = "JSON-LD dump (skos:notation preserved in extra_data)"
print(msg)
print(len(msg) * "=")
print(json.dumps(doc, indent=2, ensure_ascii=False))
