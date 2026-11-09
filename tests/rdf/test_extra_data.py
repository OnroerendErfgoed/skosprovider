import pytest
from rdflib import BNode
from rdflib import Graph
from rdflib import Literal
from rdflib import Namespace
from rdflib import URIRef
from rdflib.compare import isomorphic
from rdflib.namespace import DCTERMS
from rdflib.namespace import RDF
from rdflib.namespace import SKOS

from skosprovider.exceptions import ExtraDataException
from skosprovider.rdf.dumper import rdf_concept_or_collection_dumper
from skosprovider.rdf.dumper import rdf_conceptscheme_dumper
from skosprovider.rdf.dumper import rdf_dumper
from skosprovider.rdf.providers import RDFProvider

TREES = """
@prefix skos: <http://www.w3.org/2004/02/skos/core#> .
@prefix skosxl: <http://www.w3.org/2008/05/skos-xl#> .
@prefix dct: <http://purl.org/dc/terms/> .
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
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
    skosxl:altLabel [
        a skosxl:Label ;
        skosxl:literalForm "Bomen"@nl ;
        dct:creator "Jan"
    ] , <http://id.trees.org/labels/1> ;
    skos:note [ rdf:value "A blank note."@en ; dct:creator "Piet" ] ,
        <http://id.trees.org/notes/1> ;
    skos:narrower <http://id.trees.org/1> .

<http://id.trees.org/labels/1> a skosxl:Label ;
    skosxl:literalForm "Boom"@nl ;
    dct:date "2025" .

<http://id.trees.org/notes/1>
    rdf:value "A note with a uri."@en ;
    dct:date "2026" .

<http://id.trees.org/3> a skos:Collection ;
    skos:inScheme <http://id.trees.org> ;
    dct:identifier "3" ;
    skos:prefLabel "Trees by species"@en ;
    skos:member <http://id.trees.org/1> ;
    dct:creator "Jane Doe" .
"""

SKOSXL = Namespace("http://www.w3.org/2008/05/skos-xl#")
EX = "http://example.org/"
LARCH = URIRef("http://id.trees.org/1")
TREE = URIRef("http://id.trees.org/2")


@pytest.fixture
def graph():
    return Graph().parse(data=TREES, format="turtle")


def loader(graph, node):
    """Load the dct:creator, dct:date and skos:notation of a node."""
    extra_data = Graph()
    extra_data.bind("ex", EX)
    for predicate in (DCTERMS.creator, DCTERMS.date, SKOS.notation):
        for object_ in graph.objects(node, predicate):
            extra_data.add((node, predicate, object_))
    return extra_data if len(extra_data) else None


def merge_graph(obj):
    return obj.extra_data


@pytest.fixture
def provider(graph):
    return RDFProvider({"id": "TREES"}, graph, extra_data_loader=loader)


def _source(provider, uri):
    return next(
        source for source in provider.get_by_id("1").sources if source.uri == uri
    )


def _label(provider, text):
    return next(
        label for label in provider.get_by_id("2").labels if label.label == text
    )


def _note(provider, text):
    return next(note for note in provider.get_by_id("2").notes if note.note == text)


class TestLoading:
    def test_ignore_by_default(self, graph):
        provider = RDFProvider({"id": "TREES"}, graph)
        assert provider.concept_scheme.extra_data is None
        assert provider.get_by_id("1").extra_data is None
        assert provider.get_by_id("3").extra_data is None
        assert all(
            source.extra_data is None for source in provider.get_by_id("1").sources
        )

    def test_loader_result_is_extra_data(self, provider):
        assert set(provider.get_by_id("1").extra_data) == {
            (LARCH, SKOS.notation, Literal("L"))
        }
        assert provider.get_by_id("2").extra_data is None
        assert set(provider.get_by_id("3").extra_data) == {
            (URIRef("http://id.trees.org/3"), DCTERMS.creator, Literal("Jane Doe"))
        }
        assert set(provider.concept_scheme.extra_data) == {
            (URIRef("http://id.trees.org"), DCTERMS.creator, Literal("Jane Doe"))
        }
        assert set(_source(provider, "http://id.trees.org/source/1").extra_data) == {
            (URIRef("http://id.trees.org/source/1"), DCTERMS.date, Literal("2024"))
        }
        assert set(_label(provider, "Boom").extra_data) == {
            (URIRef("http://id.trees.org/labels/1"), DCTERMS.date, Literal("2025"))
        }
        assert set(_note(provider, "A note with a uri.").extra_data) == {
            (URIRef("http://id.trees.org/notes/1"), DCTERMS.date, Literal("2026"))
        }

    def test_blank_source_has_no_extra_data(self, provider):
        assert _source(provider, None).extra_data is None

    def test_blank_xl_label_is_plain_label_without_extra_data(self, provider):
        label = _label(provider, "Bomen")
        assert label.uri is None
        assert label.extra_data is None

    def test_blank_note_node_has_no_extra_data(self, provider):
        note = _note(provider, "A blank note.")
        assert note.uri is None
        assert note.extra_data is None

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
        assert URIRef("http://id.trees.org/labels/1") in nodes
        assert URIRef("http://id.trees.org/notes/1") in nodes
        assert not any(isinstance(node, BNode) for node in nodes)

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
        dump = rdf_dumper(provider)
        assert (LARCH, SKOS.notation, Literal("L")) not in dump
        assert isomorphic(dump, rdf_dumper(RDFProvider({"id": "TREES"}, graph)))

    def test_blank_xl_label_is_dumped_as_plain_label(self, provider):
        dump = rdf_dumper(provider, extra_data_dumper=merge_graph)
        bomen = Literal("Bomen", lang="nl")
        assert (TREE, SKOS.altLabel, bomen) in dump
        assert dump.value(predicate=SKOSXL.literalForm, object=bomen) is None

    def test_blank_note_node_is_dumped_as_literal(self, provider):
        dump = rdf_dumper(provider, extra_data_dumper=merge_graph)
        assert (TREE, SKOS.note, Literal("A blank note.", lang="en")) in dump
        assert (None, DCTERMS.creator, Literal("Piet")) not in dump

    def test_merge_graph(self, provider):
        dump = rdf_dumper(provider, extra_data_dumper=merge_graph)
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

    def test_blank_source_is_dumped_without_extra_data(self, provider):
        dump = rdf_dumper(provider, extra_data_dumper=merge_graph)
        source = dump.value(
            predicate=DCTERMS.bibliographicCitation, object=Literal("Anonymous source.")
        )
        assert isinstance(source, BNode)
        assert (LARCH, DCTERMS.source, source) in dump
        assert (None, DCTERMS.creator, Literal("John Doe")) not in dump

    def test_note_with_uri(self, provider):
        dump = rdf_dumper(provider, extra_data_dumper=merge_graph)
        note = URIRef("http://id.trees.org/notes/1")
        assert (TREE, SKOS.note, note) in dump
        assert (note, RDF.value, Literal("A note with a uri.", lang="en")) in dump
        assert (note, DCTERMS.date, Literal("2026")) in dump

    def test_round_trip(self, provider):
        dump = rdf_dumper(provider, extra_data_dumper=merge_graph)
        reloaded = RDFProvider({"id": "TREES"}, dump, extra_data_loader=loader)
        for get_object in (
            lambda provider: provider.concept_scheme,
            lambda provider: provider.get_by_id("1"),
            lambda provider: provider.get_by_id("3"),
            lambda provider: _source(provider, "http://id.trees.org/source/1"),
            lambda provider: _label(provider, "Boom"),
            lambda provider: _note(provider, "A note with a uri."),
        ):
            assert isomorphic(
                get_object(reloaded).extra_data, get_object(provider).extra_data
            )

    def test_concept_or_collection_dumper(self, provider):
        dump = rdf_concept_or_collection_dumper(
            provider, "1", extra_data_dumper=merge_graph
        )
        assert (LARCH, SKOS.notation, Literal("L")) in dump
        assert (
            URIRef("http://id.trees.org"),
            DCTERMS.creator,
            Literal("Jane Doe"),
        ) in dump

    def test_conceptscheme_dumper(self, provider):
        dump = rdf_conceptscheme_dumper(provider, extra_data_dumper=merge_graph)
        assert (
            URIRef("http://id.trees.org"),
            DCTERMS.creator,
            Literal("Jane Doe"),
        ) in dump
        assert (LARCH, SKOS.notation, Literal("L")) not in dump

    def test_dumper_keeps_prefixes(self, provider):
        dump = rdf_dumper(provider, extra_data_dumper=merge_graph)
        assert ("ex", URIRef(EX)) in set(dump.namespaces())

    def test_dumper_error(self, provider):
        def dumper(obj):
            if getattr(obj, "id", None) == "1":
                raise ValueError("boom")

        with pytest.raises(ExtraDataException) as excinfo:
            rdf_dumper(provider, extra_data_dumper=dumper)
        assert excinfo.value.message == "Failed to dump extra_data: boom"
        assert excinfo.value.__notes__ == ["while processing concept '1'"]

    def test_label_dumper_error(self, provider):
        def dumper(obj):
            if getattr(obj, "label", None) == "Boom":
                raise ValueError("boom")

        with pytest.raises(ExtraDataException) as excinfo:
            rdf_dumper(provider, extra_data_dumper=dumper)
        assert excinfo.value.__notes__ == [
            (
                "while processing Label('Boom', 'altLabel', 'nl', "
                "'http://id.trees.org/labels/1')"
            ),
            "while processing concept '2'",
        ]
