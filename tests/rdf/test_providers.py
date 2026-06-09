import os

import pytest
import rdflib
from rdflib import Graph
from rdflib import Literal
from rdflib import URIRef
from rdflib.namespace import SKOS
from skosprovider.skos import Collection
from skosprovider.skos import ConceptScheme
from skosprovider.skos import Note
from skosprovider.utils import dict_dumper

from skosprovider.rdf.providers import RDFProvider

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'data')


class TestRDFProviderProducts:

    def test_get_vocabulary_id(self, products_provider):
        assert 'PRODUCTS' == products_provider.get_vocabulary_id()

    def test_conceptscheme(self, products_provider):
        cs = products_provider.concept_scheme

        assert cs.uri == 'http://www.products.com/Scheme'
        assert cs.label('en') is not None
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
        with pytest.raises(ValueError):
            products_provider._create_label("literal", "nonexistinglabeltype")

    def test_createNote(self, products_provider):
        with pytest.raises(ValueError):
            products_provider._create_note("literal", "nonexistingnotetype")

    def test_get_concept_by_uri_equals_id(self, products_provider):
        u_product = "http://www.products.com/Product"
        cona = products_provider.get_by_id(u_product)
        conb = products_provider.get_by_uri(u_product)
        assert cona == conb

    def test_get_unexisting_by_uri(self, products_provider):
        con = products_provider.get_by_uri('http://www.products.com/Thingy')
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
        all = products_provider.find({'type': 'all'})
        assert len(all) == 4

    def test_find_type_concept(self, products_provider):
        all = products_provider.find({'type': 'concept'})
        assert len(all) == 3

    def test_find_type_collection(self, products_provider):
        all = products_provider.find({'type': 'collection'})
        assert len(all) == 1

    def test_find_label_perfume(self, products_provider):
        all = products_provider.find({'label': 'Perfume'})
        assert len(all) == 1

    def test_find_label_perfume_type_concept(self, products_provider):
        all = products_provider.find({'label': 'Perfume', 'type': 'concept'})
        assert len(all) == 1

    def test_find_collection_unexisting(self, products_provider):
        with pytest.raises(ValueError):
            products_provider.find({'collection': {'id': 404}})

    def test_find_collection_stuff_no_depth(self, products_provider):
        u_stuff = "http://www.products.com/Stuff"
        all = products_provider.find({'collection': {'id': u_stuff}})
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

    def test_concept_extra_data(self, products_provider):
        u_product = "http://www.products.com/Product"
        con = products_provider.get_by_id(u_product)
        assert isinstance(con.extra_data, rdflib.Graph)
        assert (URIRef(u_product), SKOS.notation, Literal("PROD-001")) in con.extra_data
        assert (
            URIRef(u_product),
            URIRef("http://www.products.com/properties/internalCode"),
            Literal("P1"),
        ) in con.extra_data

    def test_concept_without_extra_data(self, products_provider):
        u_perfume = "http://www.products.com/Perfume"
        con = products_provider.get_by_id(u_perfume)
        assert con.extra_data is None


class TestMultipleConceptschemes:

    def test_pick_one_conceptscheme(self):
        wb_graph = Graph()
        wb_graph.parse(os.path.join(DATA_DIR, 'waarde_en_besluit_types.ttl'), format='turtle')
        wb_provider = RDFProvider(
            {'id': 'WAARDETYPES'},
            wb_graph,
            concept_scheme_uri='https://id.erfgoed.net/thesauri/waardetypes'
        )
        assert 'https://id.erfgoed.net/thesauri/waardetypes' == wb_provider.concept_scheme.uri
        assert len(wb_provider.get_all()) == 21

    def test_set_a_conceptscheme_manually(self):
        wb_graph = Graph()
        wb_graph.parse(os.path.join(DATA_DIR, 'waarde_en_besluit_types.ttl'), format='turtle')
        wb_provider = RDFProvider(
            {'id': 'WAARDETYPES'},
            wb_graph,
            concept_scheme=ConceptScheme('https://id.erfgoed.net/thesauri/besluittypes')
        )
        assert 'https://id.erfgoed.net/thesauri/besluittypes' == wb_provider.concept_scheme.uri
        assert len(wb_provider.get_all()) == 24

    def test_pick_wrong_conceptscheme(self):
        wb_graph = Graph()
        wb_graph.parse(os.path.join(DATA_DIR, 'waarde_en_besluit_types.ttl'), format='turtle')
        with pytest.raises(RuntimeError) as exc:
            RDFProvider(
                {'id': 'WAARTYPES'},
                wb_graph,
                concept_scheme_uri='https://id.erfgoed.net/thesauri/waartypes'
            )
        assert 'https://id.erfgoed.net/thesauri/waardetypes' in str(exc.value)
        assert 'https://id.erfgoed.net/thesauri/besluittypes' in str(exc.value)

    def test_too_many_conceptscheme(self):
        toepassingen_graph = Graph()
        toepassingen_graph.parse(os.path.join(DATA_DIR, 'schemes.xml'), format='application/rdf+xml')
        with pytest.raises(RuntimeError) as exc:
            RDFProvider({'id': 'TOEPASSINGEN'}, toepassingen_graph)
        assert 'https://id.erfgoed.net/toepassingen' in str(exc.value)
        assert 'https://id.erfgoed.net/applicaties' in str(exc.value)

    def test_concept_extra_data(self):
        wb_graph = Graph()
        wb_graph.parse(os.path.join(DATA_DIR, 'waarde_en_besluit_types.ttl'), format='turtle')
        wb_provider = RDFProvider(
            {'id': 'WAARDETYPES'},
            wb_graph,
            concept_scheme_uri='https://id.erfgoed.net/thesauri/waardetypes'
        )
        u_arch = 'https://id.erfgoed.net/thesauri/waardetypes/38'
        arch = wb_provider.get_by_uri(u_arch)
        assert isinstance(arch.extra_data, rdflib.Graph)
        assert (URIRef(u_arch), SKOS.notation, Literal("OE-38")) in arch.extra_data

    def test_concept_without_extra_data(self):
        wb_graph = Graph()
        wb_graph.parse(os.path.join(DATA_DIR, 'waarde_en_besluit_types.ttl'), format='turtle')
        wb_provider = RDFProvider(
            {'id': 'WAARDETYPES'},
            wb_graph,
            concept_scheme_uri='https://id.erfgoed.net/thesauri/waardetypes'
        )
        u_arch = 'https://id.erfgoed.net/thesauri/waardetypes/39'
        arch = wb_provider.get_by_uri(u_arch)
        assert arch.extra_data is None


class TestRDFProviderExtraData:

    def _build_graph(self):
        from rdflib.namespace import DCTERMS, RDF, SKOS
        from rdflib import Literal, URIRef, Graph

        g = Graph()
        CS = URIRef("http://id.test.org")
        CONCEPT = URIRef("http://id.test.org/1")
        COLLECTION = URIRef("http://id.test.org/col")
        CUSTOM = URIRef("http://example.org/custom#")

        g.add((CS, RDF.type, SKOS.ConceptScheme))
        g.add((CS, DCTERMS.identifier, Literal("TEST")))
        g.add((CS, SKOS.prefLabel, Literal("Test", lang="en")))
        g.add((CS, URIRef(CUSTOM + "schemeVersion"), Literal("2")))

        g.add((CONCEPT, RDF.type, SKOS.Concept))
        g.add((CONCEPT, SKOS.inScheme, CS))
        g.add((CONCEPT, DCTERMS.identifier, Literal("1")))
        g.add((CONCEPT, SKOS.prefLabel, Literal("Concept One", lang="en")))
        g.add((CONCEPT, SKOS.notation, Literal("C-001")))

        g.add((COLLECTION, RDF.type, SKOS.Collection))
        g.add((COLLECTION, SKOS.inScheme, CS))
        g.add((COLLECTION, DCTERMS.identifier, Literal("col")))
        g.add((COLLECTION, SKOS.prefLabel, Literal("Collection", lang="en")))
        g.add((COLLECTION, SKOS.member, CONCEPT))
        g.add((COLLECTION, URIRef(CUSTOM + "collectionCode"), Literal("COL-001")))

        return g

    def test_concept_extra_data_graph(self):
        provider = RDFProvider({"id": "TEST"}, self._build_graph())
        concept = provider.get_by_uri("http://id.test.org/1")
        assert isinstance(concept.extra_data, rdflib.Graph)
        assert (
            URIRef("http://id.test.org/1"),
            SKOS.notation,
            Literal("C-001"),
        ) in concept.extra_data

    def test_collection_extra_data_graph(self):
        provider = RDFProvider({"id": "TEST"}, self._build_graph())
        col = provider.get_by_uri("http://id.test.org/col")
        assert isinstance(col.extra_data, rdflib.Graph)
        assert (
            URIRef("http://id.test.org/col"),
            URIRef("http://example.org/custom#collectionCode"),
            Literal("COL-001"),
        ) in col.extra_data

    def test_conceptscheme_extra_data_graph(self):
        provider = RDFProvider({"id": "TEST"}, self._build_graph())
        cs = provider.concept_scheme
        assert isinstance(cs.extra_data, rdflib.Graph)
        assert (
            URIRef("http://id.test.org"),
            URIRef("http://example.org/custom#schemeVersion"),
            Literal("2"),
        ) in cs.extra_data

    def test_known_predicates_not_in_extra_data(self):
        provider = RDFProvider({"id": "TEST"}, self._build_graph())
        concept = provider.get_by_uri("http://id.test.org/1")
        assert concept.extra_data is not None
        assert (URIRef("http://id.test.org/1"), SKOS.prefLabel, None) not in [
            (s, p, o) for s, p, o in concept.extra_data
        ]

    def test_no_extra_predicates_returns_none(self):
        from rdflib.namespace import DCTERMS, RDF, SKOS
        from rdflib import Literal, URIRef, Graph

        g = Graph()
        CS = URIRef("http://id.test.org")
        CONCEPT = URIRef("http://id.test.org/1")
        g.add((CS, RDF.type, SKOS.ConceptScheme))
        g.add((CS, DCTERMS.identifier, Literal("TEST")))
        g.add((CONCEPT, RDF.type, SKOS.Concept))
        g.add((CONCEPT, SKOS.inScheme, CS))
        g.add((CONCEPT, SKOS.prefLabel, Literal("Plain", lang="en")))

        provider = RDFProvider({"id": "TEST"}, g)
        concept = provider.get_by_uri("http://id.test.org/1")
        assert concept.extra_data is None

    def test_round_trip_extra_data_preserved(self):
        from skosprovider.rdf import utils as rdf_utils

        graph = self._build_graph()
        provider = RDFProvider({"id": "TEST"}, graph)

        def reinjector(out_graph, subject, obj):
            if isinstance(obj.extra_data, rdflib.Graph):
                for s, p, o in obj.extra_data.triples((subject, None, None)):
                    out_graph.add((s, p, o))

        dumped = rdf_utils.rdf_dumper(provider, extra_data_serializer=reinjector)
        assert (
            URIRef("http://id.test.org/1"),
            SKOS.notation,
            Literal("C-001"),
        ) in dumped


class TestTreeProvider:

    def test_parse_without_conceptscheme_generates_default_uri(self, trees_provider):
        assert 'urn:x-skosprovider:trees' == trees_provider.concept_scheme.uri

    def test_parse_identifier(self, trees_provider):
        larch = trees_provider.get_by_id('1')
        assert larch.id == '1'

        chestnut = trees_provider.get_by_id('2')
        assert chestnut.id == '2'

        species = trees_provider.get_by_id(3)
        assert species.id == '3'

        assert not trees_provider.get_by_id('http://id.trees.org/1')
        assert not trees_provider.get_by_id('http://id.trees.org/2')
        assert not trees_provider.get_by_id('http://id.trees.org/3')

    def test_rdf_provider_list(self, trees_provider):
        dump = dict_dumper(trees_provider)

        assert len(dump) == 3
        chestnut = [item for item in dump if item['uri'] == 'http://id.trees.org/2'][0]
        assert chestnut['broader'] == []
        assert chestnut['id'] == '2'
        assert chestnut['member_of'] == ['3']
        assert chestnut['narrower'] == []
        label_en = [label for label in chestnut['labels'] if label['language'] == 'en'][0]
        assert label_en == {'label': 'The Chestnut', 'language': 'en', 'type': 'prefLabel'}
        label_nl = [label for label in chestnut['labels'] if label['language'] == 'nl'][0]
        assert label_nl == {'label': 'De Paardekastanje', 'language': 'nl', 'type': 'altLabel'}
        label_fr = [label for label in chestnut['labels'] if label['language'] == 'fr'][0]
        assert type(label_fr['label']) == str
        assert label_fr == {'label': 'la châtaigne', 'language': 'fr', 'type': 'altLabel'}
        assert {
            'language': 'en',
            'note': '<p>A different type of tree.</p>',
            'type': 'definition',
            'markup': 'HTML'
        } in chestnut['notes']
        assert {
            'language': 'und',
            'note': 'Een ander soort boom.',
            'type': 'definition',
            'markup': 'HTML'
        } in chestnut['notes']
        assert {
            'markup': 'HTML',
            'citation': '<strong>Monthy Python.</strong> Episode Three: How to recognise different types of trees from quite a long way away.'
        } in chestnut['sources']
        larch = [item for item in dump if item['uri'] == 'http://id.trees.org/1'][0]
        assert {
            'citation': 'Monthy Python. Episode Three: How to recognise different types of trees from quite a long way away.',
            'markup': None
        } in larch['sources']
        assert {
            'language': 'en',
            'note': 'A type of tree.',
            'type': 'definition',
            'markup': None
        } in larch['notes']
        assert {
            'language': 'nl',
            'note': '<p>Een soort boom.</p>',
            'type': 'definition',
            'markup': 'HTML'
        } in larch['notes']

    def test_find_matches_kastanjes(self, trees_provider):
        kastanjes = trees_provider.find({
            'matches': {'uri': 'https://id.erfgoed.net/thesauri/soorten/85'}
        })
        assert len(kastanjes) == 1

    def test_find_matches_no_related_larches(self, trees_provider):
        no_related_larches = trees_provider.find({
            'matches': {
                'uri': 'https://id.erfgoed.net/thesauri/soorten/666',
                'type': 'related'
            }
        })
        assert len(no_related_larches) == 0

    def test_find_matches_close_larches(self, trees_provider):
        close_larches = trees_provider.find({
            'matches': {
                'uri': 'https://id.erfgoed.net/thesauri/soorten/666',
                'type': 'close'
            }
        })
        assert len(close_larches) == 1
