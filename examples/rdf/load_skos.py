import json
import os

import rdflib
from rdflib import Graph
from skosprovider.jsonld import jsonld_dumper
from skosprovider.rdf.providers import RDFProvider

graph = Graph()

file = os.path.join(
    os.path.dirname(__file__), "..", "..", "tests", "data", "simple_turtle_products"
)
graph.parse(file, format="turtle")

provider = RDFProvider({"id": "PRODUCTS"}, graph)

print("provider.get_all()")
print("------------------")
print(provider.get_all())
print("")

print("provider.find({'label': 'jewelry'})")
print("-----------------------------------")
print(provider.find({"label": "jewelry"}))
print("")


print("provider.get_by_id('http://wwww.products.com/Jewellery')")
print("--------------------------------------------------------")
print(provider.get_by_id("http://www.products.com/Jewellery"))
print("")

print("provider.get_by_uri('http://wwww.products.com/Jewellery')")
print("---------------------------------------------------------")
print(provider.get_by_uri("http://www.products.com/Jewellery"))
print("")

print("extra_data per concept/collection")
print("----------------------------------")
for item in provider.get_all():
    obj = provider.get_by_uri(item["uri"])
    if obj is False:
        continue

    if obj.extra_data is not None:
        print(f"{item['uri']}:")
        print(obj.extra_data.serialize(format="n3"))
    else:
        print(f"{item['uri']}: no extra_data")

    print("=======")


def extra_data_serializer(obj):
    """Convert extra_data sub-graph to a dict of JSON-LD properties."""
    if not isinstance(obj.extra_data, rdflib.Graph):
        return None
    nodes = json.loads(obj.extra_data.serialize(format="json-ld"))
    for node in nodes:
        if node.get("@id") == obj.uri:
            result = {k: v for k, v in node.items() if k != "@id"}
            return result or None
    return None


print("jsonld_dumper with extra_data")
print("------------------------------")
doc = jsonld_dumper(provider, extra_data_serializer=extra_data_serializer)
print(json.dumps(doc, indent=2))
