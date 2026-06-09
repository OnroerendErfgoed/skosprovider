'''
This examples fetches only one conceptscheme from a turtle file containing two.
'''

import os

from rdflib import Graph

from skosprovider.rdf.providers import RDFProvider

graph = Graph()

file = os.path.join(os.path.dirname(__file__), '..', '..', 'tests', 'data', 'waarde_en_besluit_types.ttl')
graph.parse(file, format="turtle")

provider = RDFProvider(
    {'id': 'WAARDETYPES'},
    graph,
    concept_scheme_uri = 'https://id.erfgoed.net/thesauri/waardetypes'
)

print("provider.get_all()")
print("------------------")
print(provider.get_all())
print("")

print("provider.find({'label': 'esthetische waarde'})")
print("-----------------------------------")
print(provider.find({'label': 'esthetische waarde'}))
print("")


print("provider.get_by_id(46)")
print("--------------------------------------------------------")
print(provider.get_by_id('46'))
print("")

print("provider.get_by_uri('https://id.erfgoed.net/thesauri/waardetypes/46')")
print("---------------------------------------------------------")
print(provider.get_by_uri('https://id.erfgoed.net/thesauri/waardetypes/46'))
print("")
