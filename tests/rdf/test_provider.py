import os

import pytest
from rdflib import Graph
from rdflib import Literal
from rdflib import URIRef
from rdflib.namespace import RDF
from rdflib.namespace import SKOS

from skosprovider.dictionary.dumper import dict_dumper
from skosprovider.exceptions import ConceptSchemeException
from skosprovider.exceptions import InvalidDataException
from skosprovider.rdf.provider import RDFProvider
from skosprovider.skos import Collection
from skosprovider.skos import ConceptScheme
from skosprovider.skos import Note

from . import TEST_DIR


class TestRDFProviderProducts:
    def test_get_vocabulary_id(self, products_provider):
        assert "PRODUCTS" == products_provider.get_vocabulary_id()

    def test_conceptscheme(self, products_provider):
        cs = products_provider.concept_scheme

        assert cs.uri == "http://www.products.com/Scheme"
        assert cs.label("en") is not None
        assert len(cs.languages) == 3

    def test_get_concept_by_id(self, products_provider):
        u_jewellery = "http://www.products.com/Jewellery"
        u_perfume = "http://www.products.com/Perfume"
        from skosprovider.skos import Concept

        con = products_provider.get_by_id(u_jewellery)
        assert isinstance(con, Concept)
        assert u_jewellery == con.id
        assert u_jewellery == con.uri
        assert u_perfume in con.related

    def test_get_unexisting_by_id(self, products_provider):
        con = products_provider.get_by_id(404)
        assert not con

    def test_createLabel(self, products_provider):
        with pytest.raises(InvalidDataException):
            products_provider._create_label("literal", "nonexistinglabeltype")

    def test_createNote(self, products_provider):
        with pytest.raises(InvalidDataException):
            products_provider._create_note("literal", "nonexistingnotetype")

    def test_get_concept_by_uri_equals_id(self, products_provider):
        u_product = "http://www.products.com/Product"
        cona = products_provider.get_by_id(u_product)
        conb = products_provider.get_by_uri(u_product)
        assert cona == conb

    def test_get_unexisting_by_uri(self, products_provider):
        con = products_provider.get_by_uri("http://www.products.com/Thingy")
        assert not con

    def test_concept_has_correct_note(self, products_provider):
        u_jewellery = "http://www.products.com/Jewellery"
        con = products_provider.get_by_id(u_jewellery)
        assert len(con.notes) == 2
        assert isinstance(con.notes[0], Note)

    def test_get_collection_by_id(self, products_provider):
        u_stuff = "http://www.products.com/Stuff"
        u_product = "http://www.products.com/Product"
        col = products_provider.get_by_id(u_stuff)
        assert isinstance(col, Collection)
        assert u_stuff == col.id
        assert u_product in col.members
        for m in col.members:
            m = products_provider.get_by_id(m)
            assert col.id in m.member_of

    def test_get_collection_by_uri_equals_id(self, products_provider):
        u_stuff = "http://www.products.com/Stuff"
        cola = products_provider.get_by_id(u_stuff)
        colb = products_provider.get_by_uri(u_stuff)
        assert cola.id == colb.id
        assert cola.uri == colb.uri

    def test_get_all(self, products_provider):
        all = products_provider.get_all()
        assert len(all) == 4

    def test_get_top_concepts(self, products_provider):
        all = products_provider.get_top_concepts()
        assert len(all) == 1

    def test_get_top_display(self, products_provider):
        all = products_provider.get_top_display()
        assert len(all) == 1

    def test_get_children_display_unexisting(self, products_provider):
        assert not products_provider.get_children_display(700)

    def test_get_children_display_collection(self, products_provider):
        u_stuff = "http://www.products.com/Stuff"
        children = products_provider.get_children_display(u_stuff)
        assert len(children) == 3

    def test_get_children_display_concept(self, products_provider):
        u_product = "http://www.products.com/Product"
        children = products_provider.get_children_display(u_product)
        assert len(children) == 2

    def test_find_all(self, products_provider):
        all = products_provider.find({})
        assert len(all) == 4

    def test_find_type_all(self, products_provider):
        all = products_provider.find({"type": "all"})
        assert len(all) == 4

    def test_find_type_concept(self, products_provider):
        all = products_provider.find({"type": "concept"})
        assert len(all) == 3

    def test_find_type_collection(self, products_provider):
        all = products_provider.find({"type": "collection"})
        assert len(all) == 1

    def test_find_label_perfume(self, products_provider):
        all = products_provider.find({"label": "Perfume"})
        assert len(all) == 1

    def test_find_label_perfume_type_concept(self, products_provider):
        all = products_provider.find({"label": "Perfume", "type": "concept"})
        assert len(all) == 1

    def test_find_collection_unexisting(self, products_provider):
        with pytest.raises(ValueError):
            products_provider.find({"collection": {"id": 404}})

    def test_find_collection_stuff_no_depth(self, products_provider):
        u_stuff = "http://www.products.com/Stuff"
        all = products_provider.find({"collection": {"id": u_stuff}})
        assert len(all) == 3

    def test_expand_concept(self, products_provider):
        u_product = "http://www.products.com/Product"
        u_perfume = "http://www.products.com/Perfume"
        ids = products_provider.expand(u_product)
        assert u_perfume in ids

    def test_expand_collection(self, products_provider):
        u_stuff = "http://www.products.com/Stuff"
        u_perfume = "http://www.products.com/Perfume"
        ids = products_provider.expand(u_stuff)
        assert u_perfume in ids

    def test_expand_unexisting(self, products_provider):
        ids = products_provider.expand(404)
        assert not ids

    def test_no_literal(self, products_provider):
        assert products_provider._get_language_from_literal("test") is None


class TestMultipleConceptschemes:
    def test_pick_one_conceptscheme(self):
        wb_graph = Graph()
        abspath = os.path.abspath(TEST_DIR + "/data/waarde_en_besluit_types.ttl")
        wb_graph.parse(abspath, format="turtle")
        wb_provider = RDFProvider(
            {"id": "WAARDETYPES"},
            wb_graph,
            concept_scheme_uri="https://id.erfgoed.net/thesauri/waardetypes",
        )
        assert (
            "https://id.erfgoed.net/thesauri/waardetypes"
            == wb_provider.concept_scheme.uri
        )
        assert len(wb_provider.get_all()) == 21

    def test_set_a_conceptscheme_manually(self):
        wb_graph = Graph()
        abspath = os.path.abspath(TEST_DIR + "/data/waarde_en_besluit_types.ttl")
        wb_graph.parse(abspath, format="turtle")
        wb_provider = RDFProvider(
            {"id": "WAARDETYPES"},
            wb_graph,
            concept_scheme=ConceptScheme(
                "https://id.erfgoed.net/thesauri/besluittypes"
            ),
        )
        assert (
            "https://id.erfgoed.net/thesauri/besluittypes"
            == wb_provider.concept_scheme.uri
        )
        assert len(wb_provider.get_all()) == 24

    def test_pick_wrong_conceptscheme(self):
        wb_graph = Graph()
        abspath = os.path.abspath(TEST_DIR + "/data/waarde_en_besluit_types.ttl")
        wb_graph.parse(abspath, format="turtle")
        with pytest.raises(ConceptSchemeException) as exc:
            RDFProvider(
                {"id": "WAARTYPES"},
                wb_graph,
                concept_scheme_uri="https://id.erfgoed.net/thesauri/waartypes",
            )
        assert "https://id.erfgoed.net/thesauri/waardetypes" in str(exc.value)
        assert "https://id.erfgoed.net/thesauri/besluittypes" in str(exc.value)

    def test_too_many_conceptscheme(self):
        toepassingen_graph = Graph()
        abspath = os.path.abspath(TEST_DIR + "/data/schemes.xml")
        toepassingen_graph.parse(abspath, format="application/rdf+xml")
        with pytest.raises(ConceptSchemeException) as exc:
            RDFProvider({"id": "TOEPASSINGEN"}, toepassingen_graph)
        assert "https://id.erfgoed.net/toepassingen" in str(exc.value)
        assert "https://id.erfgoed.net/applicaties" in str(exc.value)


class TestTreeProvider:
    def test_parse_without_conceptscheme_generates_default_uri(self, trees_provider):
        assert "urn:x-skosprovider:trees" == trees_provider.concept_scheme.uri

    def test_parse_identifier(self, trees_provider):
        larch = trees_provider.get_by_id("1")
        assert larch.id == "1"

        chestnut = trees_provider.get_by_id("2")
        assert chestnut.id == "2"

        species = trees_provider.get_by_id(3)
        assert species.id == "3"

        assert not trees_provider.get_by_id("http://id.trees.org/1")
        assert not trees_provider.get_by_id("http://id.trees.org/2")
        assert not trees_provider.get_by_id("http://id.trees.org/3")

    def test_rdf_provider_list(self, trees_provider):
        dump = dict_dumper(trees_provider)

        assert len(dump) == 3
        chestnut = [item for item in dump if item["uri"] == "http://id.trees.org/2"][0]
        assert chestnut["broader"] == []
        assert chestnut["id"] == "2"
        assert chestnut["member_of"] == ["3"]
        assert chestnut["narrower"] == []
        label_en = [label for label in chestnut["labels"] if label["language"] == "en"][
            0
        ]
        assert label_en == {
            "label": "The Chestnut",
            "language": "en",
            "type": "prefLabel",
        }
        label_nl = [label for label in chestnut["labels"] if label["language"] == "nl"][
            0
        ]
        assert label_nl == {
            "label": "De Paardekastanje",
            "language": "nl",
            "type": "altLabel",
        }
        label_fr = [label for label in chestnut["labels"] if label["language"] == "fr"][
            0
        ]
        assert isinstance(label_fr["label"], str)
        assert label_fr == {
            "label": "la châtaigne",
            "language": "fr",
            "type": "altLabel",
        }
        assert {
            "language": "en",
            "note": "<p>A different type of tree.</p>",
            "type": "definition",
            "markup": "HTML",
        } in chestnut["notes"]
        assert {
            "language": "und",
            "note": "Een ander soort boom.",
            "type": "definition",
            "markup": "HTML",
        } in chestnut["notes"]
        assert {
            "markup": "HTML",
            "citation": "<strong>Monthy Python.</strong> Episode Three: How to recognise different types of trees from quite a long way away.",
        } in chestnut["sources"]
        larch = [item for item in dump if item["uri"] == "http://id.trees.org/1"][0]
        assert {
            "citation": "Monthy Python. Episode Three: How to recognise different types of trees from quite a long way away.",
            "markup": None,
        } in larch["sources"]
        assert {
            "language": "en",
            "note": "A type of tree.",
            "type": "definition",
            "markup": None,
        } in larch["notes"]
        assert {
            "language": "nl",
            "note": "<p>Een soort boom.</p>",
            "type": "definition",
            "markup": "HTML",
        } in larch["notes"]

    def test_find_matches_kastanjes(self, trees_provider):
        kastanjes = trees_provider.find(
            {"matches": {"uri": "https://id.erfgoed.net/thesauri/soorten/85"}}
        )
        assert len(kastanjes) == 1

    def test_find_matches_no_related_larches(self, trees_provider):
        no_related_larches = trees_provider.find(
            {
                "matches": {
                    "uri": "https://id.erfgoed.net/thesauri/soorten/666",
                    "type": "related",
                }
            }
        )
        assert len(no_related_larches) == 0

    def test_find_matches_close_larches(self, trees_provider):
        close_larches = trees_provider.find(
            {
                "matches": {
                    "uri": "https://id.erfgoed.net/thesauri/soorten/666",
                    "type": "close",
                }
            }
        )
        assert len(close_larches) == 1


class TestMalformedHtml:
    @pytest.mark.parametrize(
        "html, note_text, language",
        [
            (
                '<div xml:lang="nl"><p>Een <srong>b</strong>oom.</p></div>',
                "<div><p>Een <srong>b</strong>oom.</p></div>",
                "nl",
            ),
            (
                "<p xml:lang='en' class='x'>A <srong>t</strong>ree.</p>",
                "<p class='x'>A <srong>t</strong>ree.</p>",
                "en",
            ),
            (
                '<p class="x">Een <srong>b</strong>oom.</p>',
                '<p class="x">Een <srong>b</strong>oom.</p>',
                "und",
            ),
            ("<body>", "<body>", "und"),
        ],
    )
    def test_malformed_html_note(self, html, note_text, language):
        graph = Graph()
        concept = URIRef("http://id.trees.org/1")
        graph.add((concept, RDF.type, SKOS.Concept))
        graph.add((concept, SKOS.definition, Literal(html, datatype=RDF.HTML)))
        provider = RDFProvider({"id": "TREES"}, graph)

        note = provider.get_by_uri("http://id.trees.org/1").notes[0]
        assert note.note == note_text
        assert note.language == language
        assert note.markup == "HTML"


class TestSources:
    def test_source_uri(self):
        graph = Graph().parse(
            data="""
            @prefix skos: <http://www.w3.org/2004/02/skos/core#> .
            @prefix dct: <http://purl.org/dc/terms/> .
            <http://id.trees.org/1> a skos:Concept ;
                dct:source <http://id.trees.org/source/1> , [
                    dct:bibliographicCitation "Anonymous source."
                ] .
            <http://id.trees.org/source/1>
                dct:bibliographicCitation "Source with a uri." .
            """,
            format="turtle",
        )
        provider = RDFProvider({"id": "TREES"}, graph)
        sources = provider.get_by_id("http://id.trees.org/1").sources
        assert sorted((s.citation, s.uri) for s in sources) == [
            ("Anonymous source.", None),
            ("Source with a uri.", "http://id.trees.org/source/1"),
        ]

    def test_source_with_rdf_value(self):
        graph = Graph().parse(
            data="""
            @prefix skos: <http://www.w3.org/2004/02/skos/core#> .
            @prefix dct: <http://purl.org/dc/terms/> .
            @prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
            <http://id.trees.org/1> a skos:Concept ;
                dct:source <http://id.trees.org/source/1> .
            <http://id.trees.org/source/1> rdf:value "Source with a uri." .
            """,
            format="turtle",
        )
        provider = RDFProvider({"id": "TREES"}, graph)
        source = provider.get_by_id("http://id.trees.org/1").sources[0]
        assert (source.citation, source.uri) == (
            "Source with a uri.",
            "http://id.trees.org/source/1",
        )


NODES = """
@prefix skos: <http://www.w3.org/2004/02/skos/core#> .
@prefix skosxl: <http://www.w3.org/2008/05/skos-xl#> .
@prefix dct: <http://purl.org/dc/terms/> .
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .

<http://id.trees.org/1> a skos:Concept ;
    skos:prefLabel "The Larch"@en , "De Lariks"@nl ;
    skosxl:prefLabel <http://id.trees.org/labels/1> ;
    skosxl:altLabel [ a skosxl:Label ; skosxl:literalForm "Lork"@nl ] ,
        [ a skosxl:Label ] ;
    skos:definition "A type of tree."@en ;
    skos:note <http://id.trees.org/notes/1> , [ rdf:value "A blank note."@en ] ,
        [ dct:creator "John Doe" ] .

<http://id.trees.org/labels/1> a skosxl:Label ;
    skosxl:literalForm "De Lariks"@nl ;
    dct:type <http://example.org/label-type/standard> .

<http://id.trees.org/notes/1>
    rdf:value "<p>A note with a uri.</p>"^^rdf:HTML .
"""


class TestNodes:
    @pytest.fixture
    def larch(self):
        graph = Graph().parse(data=NODES, format="turtle")
        return RDFProvider({"id": "TREES"}, graph).get_by_id("http://id.trees.org/1")

    def test_xl_labels(self, larch):
        assert sorted(
            (label.label, label.type, label.language, label.uri, label.label_types)
            for label in larch.labels
        ) == [
            (
                "De Lariks",
                "prefLabel",
                "nl",
                "http://id.trees.org/labels/1",
                ["http://example.org/label-type/standard"],
            ),
            ("Lork", "altLabel", "nl", None, []),
            ("The Larch", "prefLabel", "en", None, []),
        ]

    def test_note_nodes(self, larch):
        assert sorted(
            (note.note, note.type, note.language, note.markup, note.uri)
            for note in larch.notes
        ) == [
            (
                "<p>A note with a uri.</p>",
                "note",
                "und",
                "HTML",
                "http://id.trees.org/notes/1",
            ),
            ("A blank note.", "note", "en", None, None),
            ("A type of tree.", "definition", "en", None, None),
        ]

    def test_loader_receives_xl_label_and_note_nodes(self):
        graph = Graph().parse(data=NODES, format="turtle")
        nodes = []

        def loader(_graph, node):
            nodes.append(node)

        RDFProvider({"id": "TREES"}, graph, extra_data_loader=loader)
        assert URIRef("http://id.trees.org/labels/1") in nodes
        assert URIRef("http://id.trees.org/notes/1") in nodes
        assert len(nodes) == 5
