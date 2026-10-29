from rdflib import Graph
from rdflib import Literal
from rdflib import Namespace
from rdflib import URIRef
from rdflib.namespace import XSD
from test_providers import geo
from test_providers import larch
from test_providers import trees

from skosprovider.jsonld import CONTEXT
from skosprovider.jsonld import DumpContext
from skosprovider.jsonld import to_jsonld
from skosprovider.providers import DictionaryProvider
from skosprovider.skos import ConceptScheme
from skosprovider.skos import Label
from skosprovider.skos import Note
from skosprovider.skos import Source


class TestDumperTrees:

    def test_dump_larch(self):
        doc = to_jsonld(trees.get_by_id(1), DumpContext(provider=trees, language="nl"))
        assert doc["dct:identifier"] == "1"
        assert doc["@id"] == "http://id.trees.org/1"
        assert doc["@type"] == "skos:Concept"
        assert doc["rdfs:label"] == "De Lariks"
        assert len(doc["skos:prefLabel"]) == 2
        assert {"@language": "en", "@value": "The Larch"} in doc["skos:prefLabel"]
        assert len(doc["skos:definition"]) == 1
        assert {
            "rdf:value": {"@value": "A type of tree.", "@language": "en"}
        } in doc["skos:definition"]
        assert len(doc["dct:source"]) == len(larch["sources"])
        assert {
            "@type": "dct:BibliographicResource",
            "dct:bibliographicCitation": [
                {
                    "@value": "Monthy Python. Episode Three: How to recognise different"
                    " types of trees from quite a long way away."
                }
            ],
        } in doc["dct:source"]
        assert len(doc["@reverse"]["skos:member"]) == 1
        assert {"@id": "http://id.python.org/different/types/of/trees/nr/1/the/larch"} in doc[
            "skos:exactMatch"
        ]
        assert doc["skos:inScheme"] == {
            "@id": "http://id.trees.org",
            "@type": "skos:ConceptScheme",
            "rdfs:label": "Soorten",
        }
        assert doc["void:inDataset"] == {"@id": "http://id.trees.org/dataset"}
        assert "skosxl:prefLabel" in doc
        assert len(doc["skosxl:prefLabel"]) == 1
        assert doc["skosxl:prefLabel"][0]["@type"] == "skosxl:Label"
        assert doc["skosxl:prefLabel"][0]["@id"] == "http://id.trees.org/labels/lariks-nl"
        assert doc["skosxl:prefLabel"][0]["skosxl:literalForm"] == {
            "@language": "nl",
            "@value": "De Lariks",
        }
        assert doc["skosxl:prefLabel"][0]["dct:type"] == [
            {"@id": "http://publications.europa.eu/resource/authority/label-type/STANDARDLABEL"}
        ]

    def test_dump_larch_label_en(self):
        doc = to_jsonld(trees.get_by_id(1), DumpContext(provider=trees, language="en"))
        assert doc["rdfs:label"] == "The Larch"

    def test_dump_larch_label_nl(self):
        doc = to_jsonld(trees.get_by_id(1), DumpContext(provider=trees, language="nl"))
        assert doc["rdfs:label"] == "De Lariks"

    def test_dump_larch_member_of_partial(self):
        doc = to_jsonld(trees.get_by_id(1), DumpContext(provider=trees, language="en"))
        assert doc["@reverse"]["skos:member"] == [
            {
                "dct:identifier": 3,
                "@id": "http://id.trees.org/3",
                "@type": "skos:Collection",
                "rdfs:label": "Trees by species",
            }
        ]
        assert doc["skos:inScheme"] == {
            "@id": "http://id.trees.org",
            "@type": "skos:ConceptScheme",
            "rdfs:label": "Species",
        }

    def test_dump_chestnut(self):
        doc = to_jsonld(trees.get_by_id(2), DumpContext(provider=trees, language="en"))
        assert doc["dct:identifier"] == "2"
        assert doc["@id"] == "http://id.trees.org/2"
        assert doc["@type"] == "skos:Concept"
        assert doc["rdfs:label"] == "The Chestnut"
        assert len(doc["skos:prefLabel"]) == 1
        assert {"@language": "en", "@value": "The Chestnut"} in doc["skos:prefLabel"]
        assert len(doc["skos:altLabel"]) == 2
        assert "skosxl:prefLabel" not in doc
        assert len(doc["skos:definition"]) == 1
        assert {
            "rdf:value": {"@value": "A different type of tree.", "@language": "en"}
        } in doc["skos:definition"]
        assert len(doc["@reverse"]["skos:member"]) == 1
        assert len(doc["skos:relatedMatch"]) == 1
        assert doc["skos:inScheme"] == {
            "@id": "http://id.trees.org",
            "@type": "skos:ConceptScheme",
            "rdfs:label": "Species",
        }
        assert doc["void:inDataset"] == {"@id": "http://id.trees.org/dataset"}

    def test_dump_species(self):
        doc = to_jsonld(trees.get_by_id(3), DumpContext(provider=trees, language="en"))
        assert doc["dct:identifier"] == 3
        assert doc["@id"] == "http://id.trees.org/3"
        assert doc["@type"] == "skos:Collection"
        assert doc["rdfs:label"] == "Trees by species"
        assert len(doc["skos:prefLabel"]) == 2
        assert {"@language": "en", "@value": "Trees by species"} in doc["skos:prefLabel"]
        assert len(doc["skos:hiddenLabel"]) == 1
        assert "skosxl:prefLabel" not in doc
        assert len(doc["skos:editorialNote"]) == 1
        assert {
            "rdf:value": {
                "@value": '<div xml:lang="en">As seen in <em>How to Recognise '
                "Different Types of Trees from Quite a Long Way Away</em>.</div>",
                "@type": "rdf:HTML",
            }
        } in doc["skos:editorialNote"]
        assert "dct:source" not in doc
        assert len(doc["skos:member"]) == 2
        assert {
            "dct:identifier": "2",
            "@id": "http://id.trees.org/2",
            "@type": "skos:Concept",
            "rdfs:label": "The Chestnut",
        } in doc["skos:member"]
        assert "skos:exactMatch" not in doc
        assert doc["skos:inScheme"] == {
            "@id": "http://id.trees.org",
            "@type": "skos:ConceptScheme",
            "rdfs:label": "Species",
        }
        assert doc["void:inDataset"] == {"@id": "http://id.trees.org/dataset"}

    def test_dump_trees_cs_nl(self):
        doc = to_jsonld(trees.concept_scheme, DumpContext(provider=trees, language="nl"))
        assert doc["@id"] == "http://id.trees.org"
        assert doc["@type"] == "skos:ConceptScheme"
        assert doc["dct:identifier"] == "TREES"
        assert doc["rdfs:label"] == "Soorten"
        assert len(doc["skos:hasTopConcept"]) == 2
        assert len(doc["skos:prefLabel"]) == 2
        assert len(doc["skosxl:prefLabel"]) == 1
        assert "dct:source" not in doc
        assert "skos:definition" not in doc
        assert doc["void:inDataset"] == {"@id": "http://id.trees.org/dataset"}

    def test_dump_trees_cs_top_concepts_partial(self):
        doc = to_jsonld(trees.concept_scheme, DumpContext(provider=trees, language="nl"))
        assert len(doc["skos:hasTopConcept"]) == 2
        assert {
            "dct:identifier": "2",
            "@id": "http://id.trees.org/2",
            "@type": "skos:Concept",
            "rdfs:label": "De Paardekastanje",
        } in doc["skos:hasTopConcept"]

    def test_dump_trees_cs_xllabel(self):
        doc = to_jsonld(trees.concept_scheme, DumpContext(provider=trees, language="en"))
        assert doc["rdfs:label"] == "Species"
        assert "skosxl:prefLabel" in doc
        assert len(doc["skosxl:prefLabel"]) == 1
        assert doc["skosxl:prefLabel"][0]["@type"] == "skosxl:Label"
        assert doc["skosxl:prefLabel"][0]["@id"] == "http://id.trees.org/labels/soorten-nl"
        assert doc["skosxl:prefLabel"][0]["skosxl:literalForm"] == {
            "@language": "nl",
            "@value": "Soorten",
        }
        assert {"@language": "nl", "@value": "Soorten"} in doc["skos:prefLabel"]

    def test_dump_trees(self):
        doc = to_jsonld(trees)
        assert "@graph" in doc
        assert len(doc["@graph"]) == 4

    def test_dump_trees_inline_context(self):
        doc = to_jsonld(trees, DumpContext(provider=trees, context=CONTEXT))
        assert "@graph" in doc
        assert len(doc["@graph"]) == 4
        assert "@context" in doc
        assert doc["@context"] == CONTEXT

    def test_dump_trees_url_context(self):
        context_uri = "https://atramhasis.org/context/atramhasis.jsonld"
        doc = to_jsonld(trees, DumpContext(provider=trees, context=context_uri))
        assert "@graph" in doc
        assert len(doc["@graph"]) == 4
        assert "@context" in doc
        assert doc["@context"] == context_uri


class TestDumperGeo:

    def test_dump_geo(self):
        doc = to_jsonld(geo, DumpContext(provider=geo, context=CONTEXT))
        assert "@graph" in doc
        assert len(doc["@graph"]) == 20
        assert "@context" in doc
        assert doc["@context"] == CONTEXT

    def test_dump_Belgium(self):
        doc = to_jsonld(geo.get_by_id(4), DumpContext(provider=geo))
        assert len(doc["iso-thes:subordinateArray"]) == 2
        assert "skos:exactMatch" not in doc


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
        doc = to_jsonld(
            _trees_object_notes.get_by_id("1"),
            DumpContext(provider=_trees_object_notes),
        )
        change_note = doc["skos:changeNote"][0]
        assert change_note["@id"] == "http://id.trees.org/notes/larch-change-1"
        assert change_note["rdf:value"] == {
            "@value": "Moved from 'conifers' to 'deciduous'",
            "@language": "en",
        }
        assert "@language" not in change_note

    def test_object_note_with_markup_uses_type_in_rdf_value(self):
        doc = to_jsonld(
            _trees_object_notes.get_by_id("1"),
            DumpContext(provider=_trees_object_notes),
        )
        history_note = doc["skos:historyNote"][0]
        assert history_note["@id"] == "http://id.trees.org/notes/larch-history-1"
        assert history_note["rdf:value"]["@type"] == "rdf:HTML"
        assert "@language" not in history_note["rdf:value"]

    def test_object_source_renders_uri_and_rdf_value(self):
        doc = to_jsonld(
            _trees_object_notes.get_by_id("1"),
            DumpContext(provider=_trees_object_notes),
        )
        source = doc["dct:source"][0]
        assert source["@id"] == "http://id.trees.org/sources/larch-monograph"
        assert source["rdf:value"] == {"@value": "The Larch: A Complete Monograph"}
        assert "dct:bibliographicCitation" not in source

    def test_object_source_with_markup_uses_type_in_rdf_value(self):
        doc = to_jsonld(
            _trees_object_notes.get_by_id("1"),
            DumpContext(provider=_trees_object_notes),
        )
        source = doc["dct:source"][1]
        assert source["@id"] == "http://id.trees.org/sources/trees-vol1"
        assert source["rdf:value"]["@type"] == "rdf:HTML"
        assert "dct:bibliographicCitation" not in source


class TestDumperExtraData:

    def test_note_extra_data_includes_expanded_props(self):
        doc = to_jsonld(
            _trees_extra.get_by_id("1"), DumpContext(provider=_trees_extra)
        )
        change_note = doc["skos:changeNote"][0]
        assert change_note["@id"] == str(_note_uri)
        dct_creator = "http://purl.org/dc/terms/creator"
        dct_date = "http://purl.org/dc/terms/date"
        assert dct_creator in change_note
        assert change_note[dct_creator] == [{"@id": "http://id.trees.org/persons/HoraceGray"}]
        assert dct_date in change_note
        assert change_note[dct_date] == [
            {"@type": "http://www.w3.org/2001/XMLSchema#date", "@value": "1999-01-23"}
        ]

    def test_note_extra_data_no_context_leak(self):
        doc = to_jsonld(
            _trees_extra.get_by_id("1"), DumpContext(provider=_trees_extra)
        )
        change_note = doc["skos:changeNote"][0]
        assert "@context" not in change_note

    def test_source_extra_data_includes_expanded_props(self):
        doc = to_jsonld(
            _trees_extra.get_by_id("1"), DumpContext(provider=_trees_extra)
        )
        source = doc["dct:source"][0]
        assert source["@id"] == str(_source_uri)
        dct_creator = "http://purl.org/dc/terms/creator"
        dct_date = "http://purl.org/dc/terms/date"
        assert dct_creator in source
        assert source[dct_creator] == [{"@id": "http://id.trees.org/persons/JohnDoe"}]
        assert dct_date in source
        assert source[dct_date] == [
            {"@type": "http://www.w3.org/2001/XMLSchema#gYear", "@value": "2005"}
        ]

    def test_source_extra_data_no_context_leak(self):
        doc = to_jsonld(
            _trees_extra.get_by_id("1"), DumpContext(provider=_trees_extra)
        )
        source = doc["dct:source"][0]
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
        doc = to_jsonld(
            _trees_concept_extra.get_by_id("1"),
            DumpContext(provider=_trees_concept_extra),
        )
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
        doc = to_jsonld(
            _trees_concept_extra.get_by_id("1"),
            DumpContext(provider=_trees_concept_extra),
        )
        assert "@context" not in doc

    def test_collection_extra_data_includes_expanded_props(self):
        doc = to_jsonld(
            _trees_concept_extra.get_by_id("3"),
            DumpContext(provider=_trees_concept_extra),
        )
        dct_created = "http://purl.org/dc/terms/created"
        assert dct_created in doc
        assert doc[dct_created] == [
            {"@type": "http://www.w3.org/2001/XMLSchema#date", "@value": "2010-01-15"}
        ]

    def test_collection_extra_data_no_context_leak(self):
        doc = to_jsonld(
            _trees_concept_extra.get_by_id("3"),
            DumpContext(provider=_trees_concept_extra),
        )
        assert "@context" not in doc

    def test_conceptscheme_extra_data_includes_expanded_props(self):
        doc = to_jsonld(
            _trees_concept_extra.concept_scheme,
            DumpContext(provider=_trees_concept_extra),
        )
        dct_created = "http://purl.org/dc/terms/created"
        assert dct_created in doc
        assert doc[dct_created] == [
            {"@type": "http://www.w3.org/2001/XMLSchema#date", "@value": "2009-12-01"}
        ]

    def test_conceptscheme_extra_data_no_context_leak(self):
        doc = to_jsonld(
            _trees_concept_extra.concept_scheme,
            DumpContext(provider=_trees_concept_extra),
        )
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
        doc = to_jsonld(provider.get_by_id("10"), DumpContext(provider=provider))
        xl_label = doc["skosxl:prefLabel"][0]
        dct_created = "http://purl.org/dc/terms/created"
        assert dct_created in xl_label
        assert xl_label[dct_created] == [
            {"@type": "http://www.w3.org/2001/XMLSchema#date", "@value": "2010-01-15"}
        ]
