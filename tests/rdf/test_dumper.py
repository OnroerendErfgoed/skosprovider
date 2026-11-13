import pytest
from rdflib import Namespace
from rdflib.compare import isomorphic
from rdflib.namespace import DC
from rdflib.namespace import DCTERMS
from rdflib.namespace import RDF
from rdflib.namespace import SKOS
from rdflib.term import Literal
from rdflib.term import URIRef

from skosprovider.dictionary.provider import DictionaryProvider
from skosprovider.exceptions import NotFoundException
from skosprovider.rdf.dumper import rdf_concept_or_collection_dumper
from skosprovider.rdf.dumper import rdf_conceptscheme_dumper
from skosprovider.rdf.dumper import rdf_dumper
from skosprovider.rdf.provider import RDFProvider
from skosprovider.skos import Collection
from skosprovider.skos import Concept
from skosprovider.skos import ConceptScheme
from skosprovider.skos import Label
from skosprovider.skos import Note

SKOS_THES = Namespace("http://purl.org/iso25964/skos-thes#")
SKOSXL = Namespace("http://www.w3.org/2008/05/skos-xl#")
TREE_METADATA = {"id": "TREE", "dataset": {"uri": "https://id.trees.org/dataset"}}


@pytest.fixture(scope="module")
def tree_provider():
    larch = {
        "id": "1",
        "uri": "http://id.trees.org/1",
        "type": "concept",
        "labels": [
            {"type": "prefLabel", "language": "en", "label": "The Larch"},
            {"type": "prefLabel", "language": "nl", "label": "De Lariks"},
        ],
        "notes": [
            {"type": "definition", "language": "en", "note": "A type of tree."},
            {
                "type": "definition",
                "language": "nl",
                "note": "<p>Een soort <srong>b</strong>oom.</p>",
                "markup": "HTML",
            },
        ],
        "narrower": [],
        "broader": [],
        "related": [],
        "member_of": ["3"],
        "sources": [
            {
                "citation": (
                    "Monthy Python. Episode Three: How to recognise different "
                    "types of trees from quite a long way away."
                )
            }
        ],
    }

    chestnut = {
        "id": "2",
        "uri": "http://id.trees.org/2",
        "type": "concept",
        "labels": [
            {"type": "prefLabel", "language": "en", "label": "The Chestnut"},
            {"type": "altLabel", "language": "nl", "label": "De Paardekastanje"},
            {"type": "altLabel", "language": "fr", "label": "la châtaigne"},
            {"type": "sortLabel", "language": "nl", "label": "aaa"},
        ],
        "notes": [
            {
                "type": "definition",
                "language": "en",
                "note": "A different type of tree.",
            }
        ],
        "narrower": [],
        "broader": [],
        "related": [],
        "member_of": ["3"],
        "subordinate_arrays": [],
        "sources": [
            {
                "citation": (
                    "<strong>Monthy Python.</strong> Episode Three: How to "
                    "recognise different types of trees from quite a long way "
                    "away."
                ),
                "markup": "HTML",
            }
        ],
    }

    oak = {
        "id": "4",
        "uri": "http://id.trees.org/4",
        "type": "concept",
        "labels": [
            {"type": "prefLabel", "language": "en", "label": "The Oak"},
            {"type": "altLabel", "language": "nl", "label": "De Eik"},
            {"type": "altLabel", "language": "fr", "label": "le chêne"},
        ],
        "notes": [
            {
                "type": "definition",
                "language": "en",
                "note": "An even differenter type of tree.",
            }
        ],
        "narrower": [],
        "broader": [],
        "related": [],
        "member_of": [],
        "subordinate_arrays": [],
        "matches": {"exact": ["https://id.erfgoed.net/thesauri/soorten/297"]},
    }

    species = {
        "id": 3,
        "uri": "http://id.trees.org/3",
        "labels": [
            {"type": "prefLabel", "language": "en", "label": "Trees by species"},
            {"type": "prefLabel", "language": "nl", "label": "Bomen per soort"},
        ],
        "type": "collection",
        "members": ["1", "2", "4"],
        "member_of": [],
        "superordinates": [],
    }

    tree_provider = DictionaryProvider(
        TREE_METADATA,
        [larch, chestnut, oak, species],
        concept_scheme=ConceptScheme(
            uri="http://id.trees.org",
            labels=[
                Label("Pythonic trees.", type="prefLabel", language="en"),
                Label("Pythonische bomen.", type="prefLabel", language=None),
            ],
            notes=[
                Note(
                    "<p>Trees as used by Monthy Python.</p>",
                    type="definition",
                    language="en",
                    markup="HTML",
                )
            ],
        ),
    )

    return tree_provider


class TestRDFDumperMaterials:
    def test_dump_dictionary_to_rdf(self, materials_provider):
        graph_dump = rdf_dumper(materials_provider)
        lith_mat = URIRef("https://id.erfgoed.net/thesauri/materialen/42")
        tienkwarts = URIRef("https://id.erfgoed.net/thesauri/materialen/44")
        womkwarts = URIRef("https://id.erfgoed.net/thesauri/materialen/45")
        assert (lith_mat, SKOS.narrower, tienkwarts) in graph_dump
        assert (lith_mat, SKOS.narrower, womkwarts) in graph_dump
        assert (womkwarts, SKOS.broader, lith_mat) in graph_dump
        assert (tienkwarts, SKOS.broader, lith_mat) in graph_dump
        assert not materials_provider.get_by_id(13).infer_concept_relations
        koper = URIRef("https://id.erfgoed.net/thesauri/materialen/12")
        legeringen = URIRef("https://id.erfgoed.net/thesauri/materialen/13")
        brons = URIRef("https://id.erfgoed.net/thesauri/materialen/14")
        messing = URIRef("https://id.erfgoed.net/thesauri/materialen/15")
        assert (koper, SKOS_THES.subordinateArray, legeringen) in graph_dump
        assert (legeringen, SKOS_THES.superOrdinate, koper) in graph_dump
        assert (legeringen, SKOS.member, brons) in graph_dump
        assert (legeringen, SKOS.member, messing) in graph_dump
        assert (koper, SKOS.narrower, brons) not in graph_dump
        assert (koper, SKOS.narrower, messing) not in graph_dump
        xml = graph_dump.serialize(format="xml", encoding="UTF-8")
        if isinstance(xml, bytes):
            xml = xml.decode("UTF-8")
        assert "<?xml" == xml[:5]
        bont_skos_definition = (
            '<skos:definition xml:lang="nl-BE">Bont is een gelooide dierlijke '
            "huid, dicht bezet met haren. Het wordt voornamelijk gebruikt voor "
            "het maken van kleding.</skos:definition>"
        )
        dcterms_id_skos_definition = (
            "<dcterms:identifier "
            'rdf:datatype="http://www.w3.org/2001/XMLSchema#integer">'
            "9</dcterms:identifier>"
        )
        assert bont_skos_definition in xml
        assert dcterms_id_skos_definition in xml

    def test_dump_collections_roundtrip(self, materials_provider):
        graph_dump = rdf_dumper(materials_provider)
        provider = RDFProvider({"id": "ImportMateriaal"}, graph_dump)
        kwarts_mat = provider.get_by_id(43)
        assert kwarts_mat.type == "collection"
        assert kwarts_mat.infer_concept_relations is True
        legeringen = provider.get_by_id(13)
        assert legeringen.type == "collection"
        assert legeringen.infer_concept_relations is False
        bet_nr_vs = provider.get_by_id(68)
        assert bet_nr_vs.type == "collection"
        assert bet_nr_vs.infer_concept_relations is True
        assert set(provider.expand(68)) == {"39", "70"}

    def test_dump_concept_with_superordinates(self, materials_provider):
        graph_dump = rdf_concept_or_collection_dumper(materials_provider, 44)

        assert (
            URIRef("https://id.erfgoed.net/thesauri/materialen/43"),
            SKOS.member,
            URIRef("https://id.erfgoed.net/thesauri/materialen/44"),
        ) in graph_dump
        assert (
            URIRef("https://id.erfgoed.net/thesauri/materialen/44"),
            SKOS.broader,
            URIRef("https://id.erfgoed.net/thesauri/materialen/42"),
        ) in graph_dump


class TestRDFDumperProducts:
    def test_dump_rdf_to_rdf(self, products_provider):
        graph_dump = rdf_dumper(products_provider)
        xml = graph_dump.serialize(format="xml", encoding="UTF-8")
        if isinstance(xml, bytes):
            xml = xml.decode("UTF-8")
        assert "<?xml" == xml[:5]

        assert "http://www.products.com/" in xml
        assert "http://www.products.com/Jewellery" in xml
        assert "http://www.products.com/Perfume" in xml
        assert "http://www.products.com/Product" in xml
        assert "http://www.products.com/Stuff" in xml

    def test_dump_rdf_no_uri_as_local_identifier(self, products_provider):
        graph_dump = rdf_dumper(products_provider)
        for uri in (
            "http://www.products.com/Product",
            "http://www.products.com/Jewellery",
            "http://www.products.com/Perfume",
        ):
            assert (URIRef(uri), RDF.type, SKOS.Concept) in graph_dump
            assert graph_dump.value(URIRef(uri), DCTERMS.identifier) is None
            assert graph_dump.value(URIRef(uri), DC.identifier) is None

    def test_dump_rdf_and_reload(self, products_provider):
        graph_dump1 = rdf_dumper(products_provider)
        graph_dump2 = rdf_dumper(RDFProvider({"id": "PRODUCTS"}, graph_dump1))
        assert isomorphic(graph_dump1, graph_dump2)


class TestRDFDumperTrees:
    def test_dump_tree_to_rdf_and_reload(self, tree_provider):
        graph_dump1 = rdf_dumper(tree_provider)
        graph_dump2 = rdf_dumper(RDFProvider(TREE_METADATA, graph_dump1))
        # The tree provider has an integer id for the collection,
        # RDFProvider reads it back as a string.
        graph_dump1.set(
            (URIRef("http://id.trees.org/3"), DCTERMS.identifier, Literal("3"))
        )
        assert isomorphic(graph_dump1, graph_dump2)

    def test_dump_larch_to_rdf(self, tree_provider):
        graph_dump = rdf_concept_or_collection_dumper(tree_provider, 1)
        cs = URIRef("http://id.trees.org")
        assert (cs, RDF.type, SKOS.ConceptScheme) in graph_dump
        assert (
            cs,
            SKOS.definition,
            Literal(
                '<div xml:lang="en"><p>Trees as used by Monthy Python.</p></div>',
                datatype=RDF.HTML,
                normalize=False,
            ),
        ) in graph_dump
        assert (cs, SKOS.prefLabel, Literal("Pythonic trees.", lang="en")) in graph_dump
        xml = graph_dump.serialize(format="xml", encoding="UTF-8")
        if isinstance(xml, bytes):
            xml = xml.decode("UTF-8")
        assert "<?xml" == xml[:5]

    def test_dump_chestnut_to_rdf(self, tree_provider):
        graph_dump = rdf_concept_or_collection_dumper(tree_provider, 2)

        chestnut = URIRef("http://id.trees.org/2")
        assert (chestnut, SKOS.hiddenLabel, Literal("aaa", lang="nl")) in graph_dump
        assert (
            chestnut,
            SKOS.altLabel,
            Literal("De Paardekastanje", lang="nl"),
        ) in graph_dump
        assert (
            chestnut,
            SKOS.prefLabel,
            Literal("The Chestnut", lang="en"),
        ) in graph_dump
        assert (
            chestnut,
            SKOS.altLabel,
            Literal("la châtaigne", lang="fr"),
        ) in graph_dump

        assert (
            chestnut,
            SKOS.definition,
            Literal("A different type of tree.", lang="en"),
        ) in graph_dump

        citations = list(graph_dump.objects(predicate=DCTERMS.bibliographicCitation))
        assert citations[0] == Literal(
            "<strong>Monthy Python.</strong> Episode Three: How to recognise "
            "different types of trees from quite a long way away.",
            datatype=RDF.HTML,
        )

    def test_dump_oak_to_rdf(self, tree_provider):
        graph_dump = rdf_concept_or_collection_dumper(tree_provider, 4)
        oak = URIRef("http://id.trees.org/4")
        eik = URIRef("https://id.erfgoed.net/thesauri/soorten/297")
        assert (oak, SKOS.exactMatch, eik) in graph_dump

    def test_dump_unexisting_id(self, tree_provider):
        with pytest.raises(NotFoundException):
            rdf_concept_or_collection_dumper(tree_provider, 404)

    def test_dump_one_id_to_rdf_and_reload(self, tree_provider):
        graph_dump1 = rdf_concept_or_collection_dumper(tree_provider, 1)
        provider = RDFProvider(TREE_METADATA, graph_dump1)
        graph_dump2 = rdf_concept_or_collection_dumper(provider, 1)
        assert provider.get_by_id(1)
        assert provider.get_by_id(3)
        # The tree provider has an integer id for the collection,
        # RDFProvider reads it back as a string.
        graph_dump1.set(
            (URIRef("http://id.trees.org/3"), DCTERMS.identifier, Literal("3"))
        )
        assert isomorphic(graph_dump1, graph_dump2)

    def test_dump_html_keeps_text(self, tree_provider):
        graph_dump = rdf_conceptscheme_dumper(tree_provider)
        definition = graph_dump.value(URIRef("http://id.trees.org"), SKOS.definition)
        assert (
            str(definition)
            == '<div xml:lang="en"><p>Trees as used by Monthy Python.</p></div>'
        )
        assert (
            '"<div xml:lang=\\"en\\"><p>Trees as used by Monthy Python.</p></div>"'
            in graph_dump.serialize(format="turtle")
        )

    def test_dump_conceptscheme_tree_to_rdf(self, tree_provider):
        graph_dump = rdf_conceptscheme_dumper(tree_provider)
        cs = URIRef("http://id.trees.org")
        assert (cs, RDF.type, SKOS.ConceptScheme) in graph_dump
        assert (
            cs,
            SKOS.definition,
            Literal(
                '<div xml:lang="en"><p>Trees as used by Monthy Python.</p></div>',
                datatype=RDF.HTML,
                normalize=False,
            ),
        ) in graph_dump
        assert (cs, SKOS.prefLabel, Literal("Pythonic trees.", lang="en")) in graph_dump


class TestRDFDumperSources:
    def test_dump_source_uri(self):
        provider = DictionaryProvider(
            {"id": "TREES"},
            [
                {
                    "id": "1",
                    "uri": "http://id.trees.org/1",
                    "sources": [
                        {
                            "citation": "Source with a uri.",
                            "uri": "http://id.trees.org/source/1",
                        },
                        {"citation": "Anonymous source."},
                    ],
                }
            ],
        )
        graph = rdf_dumper(provider)
        source_nodes = set(
            graph.objects(URIRef("http://id.trees.org/1"), DCTERMS.source)
        )
        assert URIRef("http://id.trees.org/source/1") in source_nodes
        assert len(source_nodes) == 2
        assert (
            URIRef("http://id.trees.org/source/1"),
            DCTERMS.bibliographicCitation,
            Literal("Source with a uri."),
        ) in graph


class TestRDFDumperLabelsAndNotes:
    @pytest.fixture
    def provider(self):
        return DictionaryProvider(
            {"id": "TREES"},
            [
                {
                    "id": "1",
                    "uri": "http://id.trees.org/1",
                    "labels": [
                        {"type": "prefLabel", "language": "en", "label": "The Larch"},
                        {
                            "type": "altLabel",
                            "language": "nl",
                            "label": "Lork",
                            "uri": "http://id.trees.org/labels/1",
                            "label_types": ["http://example.org/label-type"],
                        },
                    ],
                    "notes": [
                        {"type": "note", "language": "en", "note": "A literal note."},
                        {
                            "type": "definition",
                            "language": "en",
                            "note": "A note with a uri.",
                            "uri": "http://id.trees.org/notes/1",
                        },
                    ],
                }
            ],
        )

    def test_plain_label_and_note_are_literals(self, provider):
        graph = rdf_dumper(provider)
        larch = URIRef("http://id.trees.org/1")
        assert (larch, SKOS.prefLabel, Literal("The Larch", lang="en")) in graph
        assert (larch, SKOS.note, Literal("A literal note.", lang="en")) in graph
        assert graph.value(larch, SKOSXL.prefLabel) is None

    def test_label_with_uri_is_xl_label(self, provider):
        graph = rdf_dumper(provider)
        larch = URIRef("http://id.trees.org/1")
        label = URIRef("http://id.trees.org/labels/1")
        lork = Literal("Lork", lang="nl")
        assert (larch, SKOS.altLabel, lork) not in graph
        assert (larch, SKOSXL.altLabel, label) in graph
        assert (label, RDF.type, SKOSXL.Label) in graph
        assert (label, SKOSXL.literalForm, lork) in graph
        assert (label, DCTERMS.type, URIRef("http://example.org/label-type")) in graph

    def test_note_with_uri_is_node(self, provider):
        graph = rdf_dumper(provider)
        larch = URIRef("http://id.trees.org/1")
        note = URIRef("http://id.trees.org/notes/1")
        assert (larch, SKOS.definition, note) in graph
        assert (note, RDF.value, Literal("A note with a uri.", lang="en")) in graph

    def test_extra_data_only_dumped_with_uri(self, provider):
        calls = []

        def dumper(obj):
            calls.append(obj)

        rdf_dumper(provider, extra_data_dumper=dumper)
        assert Label("The Larch", "prefLabel", "en") not in calls
        assert Label("Lork", "altLabel", "nl", uri="http://id.trees.org/labels/1") in (
            calls
        )
        assert Note("A literal note.", "note", "en") not in calls
        note = Note(
            "A note with a uri.", "definition", "en", uri="http://id.trees.org/notes/1"
        )
        assert note in calls

    def test_round_trip(self, provider):
        reloaded = RDFProvider({"id": "TREES"}, rdf_dumper(provider))
        larch = reloaded.get_by_uri("http://id.trees.org/1")
        assert sorted(
            (label.label, label.type, label.language, label.uri, label.label_types)
            for label in larch.labels
        ) == [
            (
                "Lork",
                "altLabel",
                "nl",
                "http://id.trees.org/labels/1",
                ["http://example.org/label-type"],
            ),
            ("The Larch", "prefLabel", "en", None, []),
        ]
        assert sorted(
            (note.note, note.type, note.language, note.uri) for note in larch.notes
        ) == [
            ("A literal note.", "note", "en", None),
            (
                "A note with a uri.",
                "definition",
                "en",
                "http://id.trees.org/notes/1",
            ),
        ]


class TestRDFDumperCyclicCollections:
    @pytest.fixture
    def provider(self):
        concept_scheme = ConceptScheme("http://id.trees.org")
        provider = DictionaryProvider(
            {"id": "TREES"}, [], concept_scheme=concept_scheme
        )
        provider.list = [
            Concept("1", uri="http://id.trees.org/1", subordinate_arrays=["2"]),
            Collection(
                "2",
                uri="http://id.trees.org/2",
                members=["3", "4"],
                member_of=["3"],
                superordinates=["1"],
                infer_concept_relations=True,
            ),
            Collection(
                "3",
                uri="http://id.trees.org/3",
                members=["2"],
                member_of=["2"],
                infer_concept_relations=True,
            ),
            Concept("4", uri="http://id.trees.org/4", member_of=["2"]),
        ]
        return provider

    def test_members_as_narrower(self, provider):
        graph = rdf_concept_or_collection_dumper(provider, "1")
        concept = URIRef("http://id.trees.org/1")
        assert (concept, SKOS.narrower, URIRef("http://id.trees.org/4")) in graph

    def test_superordinates_as_broader(self, provider):
        graph = rdf_concept_or_collection_dumper(provider, "4")
        concept = URIRef("http://id.trees.org/4")
        assert (concept, SKOS.broader, URIRef("http://id.trees.org/1")) in graph
