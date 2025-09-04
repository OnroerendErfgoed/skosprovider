from test_providers import geo
from test_providers import larch
from test_providers import trees

from skosprovider.jsonld import CONTEXT
from skosprovider.jsonld import jsonld_c_dumper
from skosprovider.jsonld import jsonld_conceptscheme_dumper
from skosprovider.jsonld import jsonld_dumper


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
