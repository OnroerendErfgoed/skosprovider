from rdflib import Graph
from rdflib import Literal
from rdflib import Namespace
from rdflib import URIRef
from rdflib.namespace import XSD
from test_providers import geo
from test_providers import larch
from test_providers import trees

from skosprovider.jsonld import CONTEXT
from skosprovider.jsonld import jsonld_c_dumper
from skosprovider.jsonld import jsonld_conceptscheme_dumper
from skosprovider.jsonld import jsonld_dumper
from skosprovider.providers import DictionaryProvider
from skosprovider.skos import ConceptScheme
from skosprovider.skos import Label
from skosprovider.skos import Note
from skosprovider.skos import Source


class TestDumperTrees:

    def test_dump_larch(self):
        doc = jsonld_c_dumper(trees, 1, language="nl")
        assert doc["id"] == "1"
        assert doc["uri"] == "http://id.trees.org/1"
        assert doc["type"] == "concept"
        assert doc["label"] == "De Lariks"
        assert len(doc["labels"]["pref_labels"]) == 2
        assert {"language": "en", "@language": "en", "lbl": "The Larch"} in doc[
            "labels"
        ]["pref_labels"]
        assert len(doc["notes"]["definitions"]) == 1
        assert {
            "language": "en",
            "@language": "en",
            "nt": "A type of tree.",
        } in doc[
            "notes"
        ]["definitions"]
        assert len(doc["sources"]) == len(larch["sources"])
        assert {
            "type": "dct:BibliographicResource",
            "citations": [
                {
                    "ct": "Monthy Python. Episode Three: How to recognise different"
                    " types of trees from quite a long way away."
                }
            ],
        } in doc["sources"]
        assert len(doc["member_of"]) == 1
        assert (
            "http://id.python.org/different/types/of/trees/nr/1/the/larch"
            in doc["matches"]["exact_matches"]
        )
        assert doc["concept_scheme"] == {
            "uri": "http://id.trees.org",
            "type": "skos:ConceptScheme",
            "label": "Soorten",
        }
        assert doc["in_dataset"] == "http://id.trees.org/dataset"
        assert "pref_labels_xl" in doc["labels_xl"]
        assert len(doc["labels_xl"]["pref_labels_xl"]) == 1
        assert doc["labels_xl"]["pref_labels_xl"][0]["type"] == "skosxl:Label"
        assert (
            doc["labels_xl"]["pref_labels_xl"][0]["uri"]
            == "http://id.trees.org/labels/lariks-nl"
        )
        assert doc["labels_xl"]["pref_labels_xl"][0]["skosxl:literalForm"] == {
            "@language": "nl",
            "lbl": "De Lariks",
        }
        assert doc["labels_xl"]["pref_labels_xl"][0]["label_types"] == [
            "http://publications.europa.eu/resource/authority/label-type/STANDARDLABEL"
        ]

    def test_dump_larch_uri_profile(self):
        doc = jsonld_c_dumper(trees, 1, relations_profile="uri")
        assert doc["member_of"] == ["http://id.trees.org/3"]
        assert doc["concept_scheme"] == "http://id.trees.org"

    def test_dump_larch_label_en(self):
        doc = jsonld_c_dumper(trees, 1, language="en")
        assert doc["label"] == "The Larch"

    def test_dump_larch_label_nl(self):
        doc = jsonld_c_dumper(trees, 1, language="nl")
        assert doc["label"] == "De Lariks"

    def test_dump_larch_partial_profile_en(self):
        doc = jsonld_c_dumper(trees, 1, relations_profile="partial", language="en")
        assert doc["member_of"] == [
            {
                "id": 3,
                "uri": "http://id.trees.org/3",
                "type": "collection",
                "label": "Trees by species",
            }
        ]
        assert doc["concept_scheme"] == {
            "uri": "http://id.trees.org",
            "type": "skos:ConceptScheme",
            "label": "Species",
        }

    def test_dump_larch_inline_context(self):
        doc = jsonld_c_dumper(trees, 1, CONTEXT)
        assert "@context" in doc
        assert doc["@context"] == CONTEXT

    def test_dump_chestnut(self):
        doc = jsonld_c_dumper(trees, 2)
        assert doc["id"] == "2"
        assert doc["uri"] == "http://id.trees.org/2"
        assert doc["type"] == "concept"
        assert doc["label"] == "The Chestnut"
        assert len(doc["labels"]["pref_labels"]) == 1
        assert {"language": "en", "@language": "en", "lbl": "The Chestnut"} in doc[
            "labels"
        ]["pref_labels"]
        assert len(doc["labels"]["alt_labels"]) == 2
        assert "labels_xl" not in doc
        assert len(doc["notes"]["definitions"]) == 1
        assert {
            "language": "en",
            "@language": "en",
            "nt": "A different type of tree.",
        } in doc["notes"]["definitions"]
        assert len(doc["member_of"]) == 1
        assert len(doc["matches"]["related_matches"]) == 1
        assert doc["concept_scheme"] == {
            "uri": "http://id.trees.org",
            "type": "skos:ConceptScheme",
            "label": "Species",
        }
        assert doc["in_dataset"] == "http://id.trees.org/dataset"

    def test_dump_species(self):
        doc = jsonld_c_dumper(trees, 3)
        assert doc["id"] == 3
        assert doc["uri"] == "http://id.trees.org/3"
        assert doc["type"] == "collection"
        assert doc["label"] == "Trees by species"
        assert len(doc["labels"]["pref_labels"]) == 2
        assert {"language": "en", "@language": "en", "lbl": "Trees by species"} in doc[
            "labels"
        ]["pref_labels"]
        assert len(doc["labels"]["hidden_labels"]) == 1
        assert "labels_xl" not in doc
        assert len(doc["notes"]["editorial_notes"]) == 1
        assert {
            "language": "en",
            "nt": '<div xml:lang="en">As seen in <em>How to Recognise '
            "Different Types of Trees from Quite a Long Way Away</em>.</div>",
            "@type": "HTML",
        } in doc["notes"]["editorial_notes"]
        assert "sources" not in doc
        assert len(doc["members"]) == 2
        assert {
            "id": "2",
            "uri": "http://id.trees.org/2",
            "type": "concept",
            "label": "The Chestnut",
        } in doc["members"]
        assert "matches" not in doc
        assert doc["concept_scheme"] == {
            "uri": "http://id.trees.org",
            "type": "skos:ConceptScheme",
            "label": "Species",
        }
        assert doc["in_dataset"] == "http://id.trees.org/dataset"

    def test_dump_trees_cs_nl(self):
        doc = jsonld_conceptscheme_dumper(trees, language="nl")
        assert doc["uri"] == "http://id.trees.org"
        assert doc["type"] == "skos:ConceptScheme"
        assert doc["id"] == "TREES"
        assert doc["label"] == "Soorten"
        assert len(doc["top_concepts"]) == 2
        assert len(doc["labels"]["pref_labels"]) == 2
        assert len(doc["labels_xl"]["pref_labels_xl"]) == 1
        assert "sources" not in doc
        assert "notes" not in doc
        assert doc["in_dataset"] == "http://id.trees.org/dataset"

    def test_dump_trees_cs_partial_profile(self):
        doc = jsonld_conceptscheme_dumper(
            trees, relations_profile="partial", language="nl"
        )
        assert len(doc["top_concepts"]) == 2
        assert {
            "id": "2",
            "uri": "http://id.trees.org/2",
            "type": "concept",
            "label": "De Paardekastanje",
        } in doc["top_concepts"]

    def test_dump_trees_cs_uri_profile(self):
        doc = jsonld_conceptscheme_dumper(trees, relations_profile="uri")
        assert len(doc["top_concepts"]) == 2
        assert "http://id.trees.org/1" in doc["top_concepts"]
        assert "http://id.trees.org/2" in doc["top_concepts"]

    def test_dump_trees_cs_inline_context(self):
        doc = jsonld_conceptscheme_dumper(trees, CONTEXT)
        assert doc["uri"] == "http://id.trees.org"
        assert doc["type"] == "skos:ConceptScheme"
        assert "@context" in doc
        assert doc["@context"] == CONTEXT

    def test_dump_trees_cs_url_context(self):
        context_uri = "https://atramhasis.org/context/atramhasis.jsonld"
        doc = jsonld_conceptscheme_dumper(trees, context_uri)
        assert doc["uri"] == "http://id.trees.org"
        assert doc["type"] == "skos:ConceptScheme"
        assert "@context" in doc
        assert doc["@context"] == context_uri

    def test_dump_trees_cs_xllabel(self):
        doc = jsonld_conceptscheme_dumper(trees)
        assert doc["label"] == "Species"
        assert "labels_xl" in doc
        assert "pref_labels_xl" in doc["labels_xl"]
        assert len(doc["labels_xl"]["pref_labels_xl"]) == 1
        assert doc["labels_xl"]["pref_labels_xl"][0]["type"] == "skosxl:Label"
        assert (
            doc["labels_xl"]["pref_labels_xl"][0]["uri"]
            == "http://id.trees.org/labels/soorten-nl"
        )
        assert doc["labels_xl"]["pref_labels_xl"][0]["skosxl:literalForm"] == {
            "@language": "nl",
            "lbl": "Soorten",
        }
        assert {"language": "nl", "@language": "nl", "lbl": "Soorten"} in doc["labels"][
            "pref_labels"
        ]

    def test_dump_trees(self):
        doc = jsonld_dumper(trees)
        assert "@graph" in doc
        assert len(doc["@graph"]) == 4

    def test_dump_trees_inline_context(self):
        doc = jsonld_dumper(trees, CONTEXT)
        assert "@graph" in doc
        assert len(doc["@graph"]) == 4
        assert "@context" in doc
        assert doc["@context"] == CONTEXT

    def test_dump_trees_url_context(self):
        context_uri = "https://atramhasis.org/context/atramhasis.jsonld"
        doc = jsonld_dumper(trees, context_uri)
        assert "@graph" in doc
        assert len(doc["@graph"]) == 4
        assert "@context" in doc
        assert doc["@context"] == context_uri


class TestDumperGeo:

    def test_dump_geo(self):
        doc = jsonld_dumper(geo, CONTEXT)
        assert "@graph" in doc
        assert len(doc["@graph"]) == 20
        assert "@context" in doc
        assert doc["@context"] == CONTEXT

    def test_dump_Belgium(self):
        doc = jsonld_c_dumper(geo, 4, CONTEXT)
        assert len(doc["subordinate_arrays"]) == 2
        assert "matches" not in doc


DCT = Namespace("http://purl.org/dc/terms/")

_note_uri = URIRef("http://id.trees.org/notes/larch-change-1999")
_note_graph = Graph()
_note_graph.add((_note_uri, DCT.creator, URIRef("http://id.trees.org/persons/HoraceGray")))
_note_graph.add((_note_uri, DCT.date, Literal("1999-01-23", datatype=XSD.date)))

_source_uri = URIRef("http://id.trees.org/sources/larch-monograph")
_source_graph = Graph()
_source_graph.add((_source_uri, DCT.creator, URIRef("http://id.trees.org/persons/JohnDoe")))
_source_graph.add((_source_uri, DCT.date, Literal("2005", datatype=XSD.gYear)))

_larch_extra = {
    "id": "1",
    "uri": "http://id.trees.org/1",
    "labels": [{"type": "prefLabel", "language": "en", "label": "The Larch"}],
    "notes": [
        Note(
            "Moved from 'conifers' to 'deciduous'",
            type="changeNote",
            language="en",
            uri=str(_note_uri),
            extra_data=_note_graph,
        ),
    ],
    "sources": [
        Source(
            "The Larch: A Complete Monograph",
            uri=str(_source_uri),
            extra_data=_source_graph,
        ),
    ],
    "member_of": [],
}

_trees_extra = DictionaryProvider(
    {"id": "TREES_EXTRA", "dataset": {"uri": "http://id.trees.org/dataset"}},
    [_larch_extra],
    concept_scheme=ConceptScheme("http://id.trees.org"),
)


_larch_object_notes = {
    "id": "1",
    "uri": "http://id.trees.org/1",
    "labels": [{"type": "prefLabel", "language": "en", "label": "The Larch"}],
    "notes": [
        Note(
            "Moved from 'conifers' to 'deciduous'",
            type="changeNote",
            language="en",
            uri="http://id.trees.org/notes/larch-change-1",
        ),
        Note(
            "<p>A <em>historical</em> note.</p>",
            type="historyNote",
            language="en",
            markup="HTML",
            uri="http://id.trees.org/notes/larch-history-1",
        ),
    ],
    "sources": [
        Source(
            "The Larch: A Complete Monograph",
            uri="http://id.trees.org/sources/larch-monograph",
        ),
        Source(
            "<em>Trees</em>, vol. 1",
            markup="HTML",
            uri="http://id.trees.org/sources/trees-vol1",
        ),
    ],
    "member_of": [],
}

_trees_object_notes = DictionaryProvider(
    {"id": "TREES_OBJ", "dataset": {"uri": "http://id.trees.org/dataset"}},
    [_larch_object_notes],
    concept_scheme=ConceptScheme("http://id.trees.org"),
)


class TestDumperObjectNotes:

    def test_object_note_renders_uri_and_rdf_value(self):
        doc = jsonld_c_dumper(_trees_object_notes, "1", CONTEXT)
        change_note = doc["notes"]["change_notes"][0]
        assert change_note["uri"] == "http://id.trees.org/notes/larch-change-1"
        assert change_note["rdf:value"] == {
            "@value": "Moved from 'conifers' to 'deciduous'",
            "@language": "en",
        }
        assert "nt" not in change_note
        assert "@language" not in change_note

    def test_object_note_with_markup_uses_type_in_rdf_value(self):
        doc = jsonld_c_dumper(_trees_object_notes, "1", CONTEXT)
        history_note = doc["notes"]["history_notes"][0]
        assert history_note["uri"] == "http://id.trees.org/notes/larch-history-1"
        assert history_note["rdf:value"]["@type"] == "HTML"
        assert "@language" not in history_note["rdf:value"]

    def test_object_source_renders_uri_and_rdf_value(self):
        doc = jsonld_c_dumper(_trees_object_notes, "1", CONTEXT)
        source = doc["sources"][0]
        assert source["uri"] == "http://id.trees.org/sources/larch-monograph"
        assert source["rdf:value"] == {"@value": "The Larch: A Complete Monograph"}
        assert "citations" not in source

    def test_object_source_with_markup_uses_type_in_rdf_value(self):
        doc = jsonld_c_dumper(_trees_object_notes, "1", CONTEXT)
        source = doc["sources"][1]
        assert source["uri"] == "http://id.trees.org/sources/trees-vol1"
        assert source["rdf:value"]["@type"] == "HTML"
        assert "citations" not in source


class TestDumperExtraData:

    def test_note_extra_data_includes_expanded_props(self):
        doc = jsonld_c_dumper(_trees_extra, "1", CONTEXT)
        change_note = doc["notes"]["change_notes"][0]
        assert change_note["uri"] == str(_note_uri)
        dct_creator = "http://purl.org/dc/terms/creator"
        dct_date = "http://purl.org/dc/terms/date"
        assert dct_creator in change_note
        assert change_note[dct_creator] == [{"@id": "http://id.trees.org/persons/HoraceGray"}]
        assert dct_date in change_note
        assert change_note[dct_date] == [
            {"@type": "http://www.w3.org/2001/XMLSchema#date", "@value": "1999-01-23"}
        ]

    def test_note_extra_data_no_context_leak(self):
        doc = jsonld_c_dumper(_trees_extra, "1", CONTEXT)
        change_note = doc["notes"]["change_notes"][0]
        assert "@context" not in change_note

    def test_source_extra_data_includes_expanded_props(self):
        doc = jsonld_c_dumper(_trees_extra, "1", CONTEXT)
        source = doc["sources"][0]
        assert source["uri"] == str(_source_uri)
        dct_creator = "http://purl.org/dc/terms/creator"
        dct_date = "http://purl.org/dc/terms/date"
        assert dct_creator in source
        assert source[dct_creator] == [{"@id": "http://id.trees.org/persons/JohnDoe"}]
        assert dct_date in source
        assert source[dct_date] == [
            {"@type": "http://www.w3.org/2001/XMLSchema#gYear", "@value": "2005"}
        ]

    def test_source_extra_data_no_context_leak(self):
        doc = jsonld_c_dumper(_trees_extra, "1", CONTEXT)
        source = doc["sources"][0]
        assert "@context" not in source


DCT2 = Namespace("http://purl.org/dc/terms/")

_concept_uri = URIRef("http://id.trees.org/1")
_concept_graph = Graph()
_concept_graph.add((_concept_uri, DCT2.created, Literal("2010-01-15", datatype=XSD.date)))
_concept_graph.add((_concept_uri, DCT2.modified, Literal("2020-06-01", datatype=XSD.date)))

_collection_uri = URIRef("http://id.trees.org/3")
_collection_graph = Graph()
_collection_graph.add((_collection_uri, DCT2.created, Literal("2010-01-15", datatype=XSD.date)))

_cs_uri_extra = URIRef("http://id.trees.org")
_cs_graph_extra = Graph()
_cs_graph_extra.add((_cs_uri_extra, DCT2.created, Literal("2009-12-01", datatype=XSD.date)))

_cs_with_extra = ConceptScheme("http://id.trees.org", extra_data=_cs_graph_extra)

_larch_with_extra = {
    "id": "1",
    "uri": "http://id.trees.org/1",
    "labels": [{"type": "prefLabel", "language": "en", "label": "The Larch"}],
    "notes": [],
    "member_of": ["3"],
    "extra_data": _concept_graph,
}

_species_with_extra = {
    "id": "3",
    "uri": "http://id.trees.org/3",
    "labels": [{"type": "prefLabel", "language": "en", "label": "Trees by species"}],
    "type": "collection",
    "members": ["1"],
    "member_of": [],
    "extra_data": _collection_graph,
}

_trees_concept_extra = DictionaryProvider(
    {"id": "TREES_CONCEPT_EXTRA", "dataset": {"uri": "http://id.trees.org/dataset"}},
    [_larch_with_extra, _species_with_extra],
    concept_scheme=_cs_with_extra,
)


class TestDumperConceptExtraData:

    def test_concept_extra_data_includes_expanded_props(self):
        doc = jsonld_c_dumper(_trees_concept_extra, "1", CONTEXT)
        dct_created = "http://purl.org/dc/terms/created"
        dct_modified = "http://purl.org/dc/terms/modified"
        assert dct_created in doc
        assert doc[dct_created] == [
            {"@type": "http://www.w3.org/2001/XMLSchema#date", "@value": "2010-01-15"}
        ]
        assert dct_modified in doc
        assert doc[dct_modified] == [
            {"@type": "http://www.w3.org/2001/XMLSchema#date", "@value": "2020-06-01"}
        ]

    def test_concept_extra_data_no_context_leak(self):
        doc = jsonld_c_dumper(_trees_concept_extra, "1")
        assert "@context" not in doc

    def test_collection_extra_data_includes_expanded_props(self):
        doc = jsonld_c_dumper(_trees_concept_extra, "3", CONTEXT)
        dct_created = "http://purl.org/dc/terms/created"
        assert dct_created in doc
        assert doc[dct_created] == [
            {"@type": "http://www.w3.org/2001/XMLSchema#date", "@value": "2010-01-15"}
        ]

    def test_collection_extra_data_no_context_leak(self):
        doc = jsonld_c_dumper(_trees_concept_extra, "3")
        assert "@context" not in doc

    def test_conceptscheme_extra_data_includes_expanded_props(self):
        doc = jsonld_conceptscheme_dumper(_trees_concept_extra)
        dct_created = "http://purl.org/dc/terms/created"
        assert dct_created in doc
        assert doc[dct_created] == [
            {"@type": "http://www.w3.org/2001/XMLSchema#date", "@value": "2009-12-01"}
        ]

    def test_conceptscheme_extra_data_no_context_leak(self):
        doc = jsonld_conceptscheme_dumper(_trees_concept_extra)
        assert "@context" not in doc

    def test_label_extra_data_includes_expanded_props(self):
        _label_uri = URIRef("http://id.trees.org/labels/larch-en")
        _label_graph = Graph()
        _label_graph.add((_label_uri, DCT2.created, Literal("2010-01-15", datatype=XSD.date)))
        larch_with_xl_extra = {
            "id": "10",
            "uri": "http://id.trees.org/10",
            "labels": [
                Label(
                    "The Larch",
                    type="prefLabel",
                    language="en",
                    uri="http://id.trees.org/labels/larch-en",
                    extra_data=_label_graph,
                )
            ],
            "member_of": [],
        }
        provider = DictionaryProvider(
            {"id": "LARCH_LABEL_EXTRA"},
            [larch_with_xl_extra],
            concept_scheme=ConceptScheme("http://id.trees.org"),
        )
        doc = jsonld_c_dumper(provider, "10", CONTEXT)
        xl_label = doc["labels_xl"]["pref_labels_xl"][0]
        dct_created = "http://purl.org/dc/terms/created"
        assert dct_created in xl_label
        assert xl_label[dct_created] == [
            {"@type": "http://www.w3.org/2001/XMLSchema#date", "@value": "2010-01-15"}
        ]
