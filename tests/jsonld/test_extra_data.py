from rdflib import BNode
from rdflib import Graph
from rdflib import Literal
from rdflib import URIRef
from rdflib.compare import isomorphic
from rdflib.namespace import DCTERMS

from skosprovider.jsonld.extra_data import from_unmapped
from skosprovider.jsonld.extra_data import node_to_jsonld
from skosprovider.jsonld.extra_data import to_unmapped
from skosprovider.skos import Concept
from skosprovider.skos import Source

LARCH = URIRef("http://id.trees.org/1")
EX = "http://example.org/"


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


class TestNodeToJsonLd:
    def test_embeds_blank_nodes(self):
        assert node_to_jsonld(_larch_graph(), LARCH) == {
            "@id": "http://id.trees.org/1",
            "http://purl.org/dc/terms/creator": [{"@value": "Jane Doe"}],
            EX
            + "height": [
                {
                    EX
                    + "value": [
                        {
                            "@type": "http://www.w3.org/2001/XMLSchema#integer",
                            "@value": 30,
                        }
                    ],
                    EX + "unit": [{EX + "name": [{"@value": "metre"}]}],
                }
            ],
        }

    def test_compacts_with_context(self):
        context = {"dct": "http://purl.org/dc/terms/"}
        graph = Graph()
        graph.add((LARCH, DCTERMS.creator, Literal("Jane Doe")))
        assert node_to_jsonld(graph, LARCH, context) == {
            "@context": {"dct": "http://purl.org/dc/terms/"},
            "@id": "http://id.trees.org/1",
            "dct:creator": "Jane Doe",
        }

    def test_unknown_node(self):
        assert node_to_jsonld(_larch_graph(), URIRef("http://id.trees.org/3")) == {}


class TestFromUnmapped:
    def test_round_trip_with_node_to_jsonld(self):
        graph = _larch_graph()
        graph.remove((URIRef("http://id.trees.org/2"), None, None))
        data = node_to_jsonld(graph, LARCH, {"dct": "http://purl.org/dc/terms/"})
        assert isomorphic(from_unmapped(data), graph)

    def test_no_triples(self):
        assert from_unmapped({"@id": "http://id.trees.org/1"}) is None


class TestToUnmapped:
    def test_without_extra_data(self):
        assert to_unmapped(Concept(1, uri=str(LARCH))) is None

    def test_only_dumps_the_object_itself(self):
        concept = Concept(1, uri=str(LARCH), extra_data=_larch_graph())
        assert to_unmapped(concept) == {
            "http://purl.org/dc/terms/creator": [{"@value": "Jane Doe"}],
            EX
            + "height": [
                {
                    EX
                    + "value": [
                        {
                            "@type": "http://www.w3.org/2001/XMLSchema#integer",
                            "@value": 30,
                        }
                    ],
                    EX + "unit": [{EX + "name": [{"@value": "metre"}]}],
                }
            ],
        }

    def test_object_without_uri(self):
        graph = Graph()
        graph.add((BNode(), DCTERMS.creator, Literal("Jane Doe")))
        assert to_unmapped(Source("A book.", extra_data=graph)) is None

    def test_uri_node_stays_a_reference(self):
        graph = Graph().parse(
            data="""
            @prefix dct: <http://purl.org/dc/terms/> .
            @prefix foaf: <http://xmlns.com/foaf/0.1/> .
            <http://id.trees.org/1> dct:contributor <http://example.org/piet> .
            <http://example.org/piet> foaf:name "Piet" .
            """,
            format="turtle",
        )
        concept = Concept(1, uri=str(LARCH), extra_data=graph)
        assert to_unmapped(concept) == {
            "http://purl.org/dc/terms/contributor": [
                {"@id": "http://example.org/piet"}
            ],
        }

    def test_nothing_about_the_object(self):
        graph = Graph()
        graph.add((URIRef("http://id.trees.org/2"), DCTERMS.creator, Literal("x")))
        assert to_unmapped(Concept(1, uri=str(LARCH), extra_data=graph)) is None
