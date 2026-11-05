import pytest
from rdflib import BNode
from rdflib import Graph
from rdflib import Literal
from rdflib import URIRef
from rdflib.compare import isomorphic
from rdflib.namespace import DCTERMS
from rdflib.namespace import SKOS

from skosprovider.exceptions import ExtraDataException
from skosprovider.rdf import utils
from skosprovider.rdf.extra_data import merge_graph
from skosprovider.rdf.extra_data import unmapped_triples
from skosprovider.rdf.providers import RDFProvider

TREES = """
@prefix skos: <http://www.w3.org/2004/02/skos/core#> .
@prefix dct: <http://purl.org/dc/terms/> .
@prefix ex: <http://example.org/> .

<http://id.trees.org> a skos:ConceptScheme ;
    skos:prefLabel "Trees"@en ;
    dct:creator "Jane Doe" .

<http://id.trees.org/1> a skos:Concept, ex:Tree ;
    skos:inScheme <http://id.trees.org> ;
    dct:identifier "1" ;
    skos:prefLabel "The Larch"@en ;
    skos:definition "A type of tree."@en ;
    skos:broader <http://id.trees.org/2> ;
    skos:exactMatch <http://example.org/larch> ;
    skos:notation "L" ;
    ex:height [ ex:value 30 ; ex:unit [ ex:name "metre" ] ] ;
    dct:source [
        a dct:BibliographicResource ;
        dct:bibliographicCitation "Anonymous source." ;
        dct:creator "John Doe"
    ] , <http://id.trees.org/source/1> .

<http://id.trees.org/source/1>
    dct:bibliographicCitation "Source with a uri." ;
    dct:date "2024" .

<http://id.trees.org/2> a skos:Concept ;
    skos:inScheme <http://id.trees.org> ;
    dct:identifier "2" ;
    skos:prefLabel "Trees"@en ;
    skos:narrower <http://id.trees.org/1> .

<http://id.trees.org/3> a skos:Collection ;
    skos:inScheme <http://id.trees.org> ;
    dct:identifier "3" ;
    skos:prefLabel "Trees by species"@en ;
    skos:member <http://id.trees.org/1> ;
    dct:creator "Jane Doe" .
"""

EX = "http://example.org/"
LARCH = URIRef("http://id.trees.org/1")
PLACEHOLDER = URIRef("urn:x-skosprovider:blank-node")


@pytest.fixture
def graph():
    return Graph().parse(data=TREES, format="turtle")


@pytest.fixture
def provider(graph):
    return RDFProvider({"id": "TREES"}, graph, extra_data_loader=unmapped_triples)


def _source(provider, uri):
    return next(
        source for source in provider.get_by_id("1").sources if source.uri == uri
    )


class TestLoading:
    def test_ignore_by_default(self, graph):
        provider = RDFProvider({"id": "TREES"}, graph)
        assert provider.concept_scheme.extra_data is None
        assert provider.get_by_id("1").extra_data is None
        assert provider.get_by_id("3").extra_data is None
        assert all(
            source.extra_data is None for source in provider.get_by_id("1").sources
        )

    def test_concept_unmapped_triples(self, provider):
        expected = Graph().parse(
            data="""
            @prefix skos: <http://www.w3.org/2004/02/skos/core#> .
            @prefix ex: <http://example.org/> .
            <http://id.trees.org/1> a ex:Tree ;
                skos:notation "L" ;
                ex:height [ ex:value 30 ; ex:unit [ ex:name "metre" ] ] .
            """,
            format="turtle",
        )
        assert isomorphic(provider.get_by_id("1").extra_data, expected)

    def test_concept_without_unmapped_triples(self, provider):
        assert provider.get_by_id("2").extra_data is None

    def test_collection_unmapped_triples(self, provider):
        assert set(provider.get_by_id("3").extra_data) == {
            (URIRef("http://id.trees.org/3"), DCTERMS.creator, Literal("Jane Doe"))
        }

    def test_concept_scheme_unmapped_triples(self, provider):
        assert set(provider.concept_scheme.extra_data) == {
            (URIRef("http://id.trees.org"), DCTERMS.creator, Literal("Jane Doe"))
        }

    def test_blank_node_source_uses_placeholder(self, provider):
        source = _source(provider, None)
        assert set(source.extra_data) == {
            (PLACEHOLDER, DCTERMS.creator, Literal("John Doe"))
        }

    def test_uri_source(self, provider):
        source = _source(provider, "http://id.trees.org/source/1")
        assert set(source.extra_data) == {
            (URIRef("http://id.trees.org/source/1"), DCTERMS.date, Literal("2024"))
        }

    def test_loader_receives_graph_and_node(self, graph):
        calls = []

        def loader(loader_graph, node):
            calls.append((loader_graph, node))

        RDFProvider({"id": "TREES"}, graph, extra_data_loader=loader)
        assert all(loader_graph is graph for loader_graph, _ in calls)
        nodes = [node for _, node in calls]
        assert URIRef("http://id.trees.org") in nodes
        assert LARCH in nodes
        assert URIRef("http://id.trees.org/3") in nodes
        assert URIRef("http://id.trees.org/source/1") in nodes
        assert any(isinstance(node, BNode) for node in nodes)

    def test_loader_error(self, graph):
        def loader(_graph, node):
            if node == LARCH:
                raise ValueError("boom")

        with pytest.raises(ExtraDataException) as excinfo:
            RDFProvider({"id": "TREES"}, graph, extra_data_loader=loader)
        assert excinfo.value.message == "Failed to load extra_data: boom"
        assert excinfo.value.__notes__ == ["while processing concept '1'"]

    def test_source_loader_error(self, graph):
        def loader(_graph, node):
            if node == URIRef("http://id.trees.org/source/1"):
                raise ValueError("boom")

        with pytest.raises(ExtraDataException) as excinfo:
            RDFProvider({"id": "TREES"}, graph, extra_data_loader=loader)
        assert excinfo.value.__notes__ == [
            (
                "while processing Source('Source with a uri.', "
                "'http://id.trees.org/source/1')"
            ),
            "while processing concept '1'",
        ]


class TestDumping:
    def test_ignore_by_default(self, provider, graph):
        dump = utils.rdf_dumper(provider)
        assert (LARCH, SKOS.notation, Literal("L")) not in dump
        assert isomorphic(dump, utils.rdf_dumper(RDFProvider({"id": "TREES"}, graph)))

    def test_merge_graph(self, provider):
        dump = utils.rdf_dumper(provider, extra_data_dumper=merge_graph)
        assert (LARCH, SKOS.notation, Literal("L")) in dump
        assert (
            URIRef("http://id.trees.org"),
            DCTERMS.creator,
            Literal("Jane Doe"),
        ) in dump
        assert (
            URIRef("http://id.trees.org/source/1"),
            DCTERMS.date,
            Literal("2024"),
        ) in dump
        assert not any(PLACEHOLDER in triple for triple in dump)

    def test_blank_node_source_is_linked(self, provider):
        dump = utils.rdf_dumper(provider, extra_data_dumper=merge_graph)
        source_node = dump.value(
            predicate=DCTERMS.bibliographicCitation,
            object=Literal("Anonymous source."),
        )
        assert isinstance(source_node, BNode)
        assert (LARCH, DCTERMS.source, source_node) in dump
        assert (source_node, DCTERMS.creator, Literal("John Doe")) in dump

    def test_round_trip(self, provider):
        dump = utils.rdf_dumper(provider, extra_data_dumper=merge_graph)
        reloaded = RDFProvider(
            {"id": "TREES"}, dump, extra_data_loader=unmapped_triples
        )
        for id_ in ("1", "3"):
            assert isomorphic(
                reloaded.get_by_id(id_).extra_data, provider.get_by_id(id_).extra_data
            )
        assert isomorphic(
            reloaded.concept_scheme.extra_data, provider.concept_scheme.extra_data
        )
        for uri in (None, "http://id.trees.org/source/1"):
            assert isomorphic(
                _source(reloaded, uri).extra_data, _source(provider, uri).extra_data
            )

    def test_concept_or_collection_dumper(self, provider):
        dump = utils.rdf_concept_or_collection_dumper(
            provider, "1", extra_data_dumper=merge_graph
        )
        assert (LARCH, SKOS.notation, Literal("L")) in dump
        assert (
            URIRef("http://id.trees.org"),
            DCTERMS.creator,
            Literal("Jane Doe"),
        ) in dump

    def test_conceptscheme_dumper(self, provider):
        dump = utils.rdf_conceptscheme_dumper(provider, extra_data_dumper=merge_graph)
        assert (
            URIRef("http://id.trees.org"),
            DCTERMS.creator,
            Literal("Jane Doe"),
        ) in dump
        assert (LARCH, SKOS.notation, Literal("L")) not in dump

    def test_dumper_keeps_prefixes(self, provider):
        dump = utils.rdf_dumper(provider, extra_data_dumper=merge_graph)
        assert ("ex", URIRef(EX)) in set(dump.namespaces())

    def test_dumper_error(self, provider):
        def dumper(obj):
            if getattr(obj, "id", None) == "1":
                raise ValueError("boom")

        with pytest.raises(ExtraDataException) as excinfo:
            utils.rdf_dumper(provider, extra_data_dumper=dumper)
        assert excinfo.value.message == "Failed to dump extra_data: boom"
        assert excinfo.value.__notes__ == ["while processing concept '1'"]
