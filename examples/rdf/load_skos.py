import os

from rdflib import Graph

from skosprovider.rdf.provider import RDFProvider

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
