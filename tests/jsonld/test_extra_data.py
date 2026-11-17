from rdflib import BNode
from rdflib import Graph
from rdflib import Literal
from rdflib import URIRef
from rdflib.compare import isomorphic
from rdflib.namespace import DCTERMS

from skosprovider.jsonld.extra_data import from_unmapped
from skosprovider.jsonld.extra_data import graph_to_jsonld
from skosprovider.jsonld.extra_data import jsonld_to_graph
from skosprovider.jsonld.extra_data import to_jsonld
from skosprovider.skos import Concept
from skosprovider.skos import Source

LARCH = URIRef("http://id.trees.org/1")


def _larch_graph():
    return Graph().parse(
        data="""
        @prefix dct: <http://purl.org/dc/terms/> .
        @prefix ex: <http://example.org/> .
        <http://id.trees.org/1> dct:creator "Jane Doe" ;
            ex:height [ ex:value 30 ; ex:unit [ ex:name "metre" ] ] .
        <http://id.trees.org/2> dct:creator "John Doe" .
        """,
        format="turtle",
    )


class TestGraphToJsonLd:
    def test_node_with_other_nodes_included(self):
        node = graph_to_jsonld(_larch_graph(), "http://id.trees.org/1")
        assert node["@id"] == "http://id.trees.org/1"
        assert node["http://purl.org/dc/terms/creator"] == [{"@value": "Jane Doe"}]
        [height] = node["http://example.org/height"]
        assert set(height) == {"@id"}
        included_ids = {included["@id"] for included in node["@included"]}
        assert height["@id"] in included_ids
        assert "http://id.trees.org/2" in included_ids
        assert len(included_ids) == 3

    def test_no_triple_is_lost(self):
        graph = _larch_graph()
        node = graph_to_jsonld(graph, "http://id.trees.org/1")
        assert isomorphic(jsonld_to_graph(node), graph)

    def test_without_other_nodes(self):
        graph = Graph()
        graph.add((LARCH, DCTERMS.creator, Literal("Jane Doe")))
        assert graph_to_jsonld(graph, "http://id.trees.org/1") == {
            "@id": "http://id.trees.org/1",
            "http://purl.org/dc/terms/creator": [{"@value": "Jane Doe"}],
        }

    def test_unknown_node(self):
        node = graph_to_jsonld(_larch_graph(), "http://id.trees.org/3")
        assert set(node) == {"@id", "@included"}
        assert node["@id"] == "http://id.trees.org/3"

    def test_empty_graph(self):
        assert graph_to_jsonld(Graph(), "http://id.trees.org/1") == {}


class TestFromUnmapped:
    def test_skips_mapped_properties(self):
        node = {
            "@context": {
                "skos": "http://www.w3.org/2004/02/skos/core#",
                "dct": "http://purl.org/dc/terms/",
                "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
                "ex": "http://example.org/",
            },
            "@id": "http://id.trees.org/1",
            "@type": ["skos:Concept", "ex:Tree"],
            "dct:identifier": "1",
            "skos:prefLabel": {"@value": "The Larch", "@language": "en"},
            "skos:definition": {"rdf:value": "A type of tree."},
            "dct:creator": "Jane Doe",
            "ex:height": {"ex:value": 30, "ex:unit": "metre"},
        }
        expected = Graph().parse(
            data="""
            @prefix dct: <http://purl.org/dc/terms/> .
            @prefix ex: <http://example.org/> .
            <http://id.trees.org/1> a ex:Tree ;
                dct:creator "Jane Doe" ;
                ex:height [ ex:value 30 ; ex:unit "metre" ] .
            """,
            format="turtle",
        )
        actual = from_unmapped(node, Concept(1, uri="http://id.trees.org/1"))
        assert isomorphic(actual, expected)

    def test_only_mapped_properties(self):
        node = {
            "@id": "http://id.trees.org/1",
            "@type": "http://www.w3.org/2004/02/skos/core#Concept",
        }
        assert from_unmapped(node, Concept(1, uri="http://id.trees.org/1")) is None


class TestToJsonLd:
    def test_without_extra_data(self):
        assert to_jsonld(Concept(1, uri=str(LARCH))) is None

    def test_dumps_the_whole_graph(self):
        graph = _larch_graph()
        properties = to_jsonld(Concept(1, uri=str(LARCH), extra_data=graph))
        assert "@id" not in properties
        assert properties["http://purl.org/dc/terms/creator"] == [
            {"@value": "Jane Doe"}
        ]
        actual = jsonld_to_graph({**properties, "@id": str(LARCH)})
        assert isomorphic(actual, graph)

    def test_object_without_uri(self):
        graph = Graph()
        graph.add((BNode(), DCTERMS.creator, Literal("Jane Doe")))
        assert to_jsonld(Source("A book.", extra_data=graph)) is None

    def test_uri_node_is_included(self):
        graph = Graph().parse(
            data="""
            @prefix dct: <http://purl.org/dc/terms/> .
            @prefix foaf: <http://xmlns.com/foaf/0.1/> .
            <http://id.trees.org/1> dct:contributor <http://example.org/piet> .
            <http://example.org/piet> foaf:name "Piet" .
            """,
            format="turtle",
        )
        assert to_jsonld(Concept(1, uri=str(LARCH), extra_data=graph)) == {
            "http://purl.org/dc/terms/contributor": [
                {"@id": "http://example.org/piet"}
            ],
            "@included": [
                {
                    "@id": "http://example.org/piet",
                    "http://xmlns.com/foaf/0.1/name": [{"@value": "Piet"}],
                }
            ],
        }

    def test_nothing_about_the_object(self):
        graph = Graph()
        graph.add((URIRef("http://id.trees.org/2"), DCTERMS.creator, Literal("x")))
        assert to_jsonld(Concept(1, uri=str(LARCH), extra_data=graph)) == {
            "@included": [
                {
                    "@id": "http://id.trees.org/2",
                    "http://purl.org/dc/terms/creator": [{"@value": "x"}],
                }
            ],
        }

    def test_empty_graph(self):
        assert to_jsonld(Concept(1, uri=str(LARCH), extra_data=Graph())) is None
