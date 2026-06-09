import logging

import pytest
from rdflib import Graph
from rdflib import Namespace
from rdflib.namespace import DC
from rdflib.namespace import DCTERMS
from rdflib.namespace import RDF
from rdflib.namespace import SKOS
from rdflib.term import Literal
from rdflib.term import URIRef

from skosprovider.providers import DictionaryProvider
from skosprovider.rdf.providers import RDFProvider
from skosprovider.rdf import utils
from skosprovider.skos import ConceptScheme
from skosprovider.skos import Label
from skosprovider.skos import Note

SKOS_THES = Namespace('http://purl.org/iso25964/skos-thes#')

log = logging.getLogger(__name__)


@pytest.fixture(scope='module')
def tree_provider():
    larch = {
        'id': '1',
        'uri': 'http://id.trees.org/1',
        'type': 'concept',
        'labels': [
            {'type': 'prefLabel', 'language': 'en', 'label': 'The Larch'},
            {'type': 'prefLabel', 'language': 'nl', 'label': 'De Lariks'}
        ],
        'notes': [
            {'type': 'definition', 'language': 'en', 'note': 'A type of tree.'},
            {'type': 'definition', 'language': 'nl', 'note': '<p>Een soort <strong>b</strong>oom.</p>', 'markup': 'HTML'}
        ],
        'narrower': [],
        'broader': [],
        'related': [],
        'member_of': ['3'],
        'sources': [
            {'citation': 'Monthy Python. Episode Three: How to recognise different types of trees from quite a long way away.'}
        ]
    }

    chestnut = {
        'id': '2',
        'uri': 'http://id.trees.org/2',
        'type': 'concept',
        'labels': [
            {'type': 'prefLabel', 'language': 'en', 'label': 'The Chestnut'},
            {'type': 'altLabel', 'language': 'nl', 'label': 'De Paardekastanje'},
            {'type': 'altLabel', 'language': 'fr', 'label': 'la châtaigne'},
            {'type': 'sortLabel', 'language': 'nl', 'label': 'aaa'}
        ],
        'notes': [
            {'type': 'definition', 'language': 'en', 'note': 'A different type of tree.'}
        ],
        'narrower': [],
        'broader': [],
        'related': [],
        'member_of': ['3'],
        'subordinate_arrays': [],
        'sources': [
            {
                'citation': '<strong>Monthy Python.</strong> Episode Three: How to recognise different types of trees from quite a long way away.',
                'markup': 'HTML'
            }
        ]
    }

    oak = {
        'id': '4',
        'uri': 'http://id.trees.org/4',
        'type': 'concept',
        'labels': [
            {'type': 'prefLabel', 'language': 'en', 'label': 'The Oak'},
            {'type': 'altLabel', 'language': 'nl', 'label': 'De Eik'},
            {'type': 'altLabel', 'language': 'fr', 'label': 'le chêne'}
        ],
        'notes': [
            {'type': 'definition', 'language': 'en', 'note': 'An even differenter type of tree.'}
        ],
        'narrower': [],
        'broader': [],
        'related': [],
        'member_of': [],
        'subordinate_arrays': [],
        'matches': {
            'exact': ['https://id.erfgoed.net/thesauri/soorten/297']
        }
    }

    species = {
        'id': 3,
        'uri': 'http://id.trees.org/3',
        'labels': [
            {'type': 'prefLabel', 'language': 'en', 'label': 'Trees by species'},
            {'type': 'prefLabel', 'language': 'nl', 'label': 'Bomen per soort'}
        ],
        'type': 'collection',
        'members': ['1', '2', '4'],
        'member_of': [],
        'superordinates': []
    }

    return DictionaryProvider(
        {'id': 'TREE', 'dataset': {'uri': 'https://id.trees.org/dataset'}},
        [larch, chestnut, oak, species],
        concept_scheme=ConceptScheme(
            uri='http://id.trees.org',
            labels=[
                Label('Pythonic trees.', type='prefLabel', language='en'),
                Label('Pythonische bomen.', type='prefLabel', language=None)
            ],
            notes=[
                Note('<p>Trees as used by Monthy Python.</p>', type='definition', language='en', markup='HTML')
            ]
        )
    )


class TestRDFDumperMaterials:

    def test_dump_dictionary_to_rdf(self, materials_provider):
        graph_dump = utils.rdf_dumper(materials_provider)
        lith_mat = URIRef('https://id.erfgoed.net/thesauri/materialen/42')
        tienkwarts = URIRef('https://id.erfgoed.net/thesauri/materialen/44')
        womkwarts = URIRef('https://id.erfgoed.net/thesauri/materialen/45')
        assert (lith_mat, SKOS.narrower, tienkwarts) in graph_dump
        assert (lith_mat, SKOS.narrower, womkwarts) in graph_dump
        assert (womkwarts, SKOS.broader, lith_mat) in graph_dump
        assert (tienkwarts, SKOS.broader, lith_mat) in graph_dump
        assert not materials_provider.get_by_id(13).infer_concept_relations
        koper = URIRef('https://id.erfgoed.net/thesauri/materialen/12')
        legeringen = URIRef('https://id.erfgoed.net/thesauri/materialen/13')
        brons = URIRef('https://id.erfgoed.net/thesauri/materialen/14')
        messing = URIRef('https://id.erfgoed.net/thesauri/materialen/15')
        assert (koper, SKOS_THES.subordinateArray, legeringen) in graph_dump
        assert (legeringen, SKOS_THES.superOrdinate, koper) in graph_dump
        assert (legeringen, SKOS.member, brons) in graph_dump
        assert (legeringen, SKOS.member, messing) in graph_dump
        assert (koper, SKOS.narrower, brons) not in graph_dump
        assert (koper, SKOS.narrower, messing) not in graph_dump
        xml = graph_dump.serialize(format='xml', encoding="UTF-8")
        if isinstance(xml, bytes):
            xml = xml.decode("UTF-8")
        assert '<?xml' == xml[:5]
        bont_skos_definition = '<skos:definition xml:lang="nl-BE">Bont is een gelooide dierlijke huid, dicht bezet met haren. Het wordt voornamelijk gebruikt voor het maken van kleding.</skos:definition>'
        dcterms_id_skos_definition = '<dcterms:identifier rdf:datatype="http://www.w3.org/2001/XMLSchema#integer">9</dcterms:identifier>'
        assert bont_skos_definition in xml
        assert dcterms_id_skos_definition in xml

    def test_dump_collections_roundtrip(self, materials_provider, caplog):
        caplog.set_level(logging.DEBUG)
        graph_dump = utils.rdf_dumper(materials_provider)
        provider = RDFProvider({'id': 'ImportMateriaal'}, graph_dump)
        kwarts_mat = provider.get_by_id(43)
        assert kwarts_mat.type == 'collection'
        assert kwarts_mat.infer_concept_relations is True
        legeringen = provider.get_by_id(13)
        assert legeringen.type == 'collection'
        assert legeringen.infer_concept_relations is False
        bet_nr_vs = provider.get_by_id(68)
        assert bet_nr_vs.type == 'collection'
        assert bet_nr_vs.infer_concept_relations is True
        assert set(provider.expand(68)) == {'39', '70'}

    def test_dump_concept_with_superordinates(self, materials_provider, caplog):
        caplog.set_level(logging.DEBUG)
        graph_dump = utils.rdf_c_dumper(materials_provider, 44)

        assert isinstance(graph_dump, Graph)
        assert (
            URIRef('https://id.erfgoed.net/thesauri/materialen/43'),
            SKOS.member,
            URIRef('https://id.erfgoed.net/thesauri/materialen/44')
        ) in graph_dump
        assert (
            URIRef('https://id.erfgoed.net/thesauri/materialen/44'),
            SKOS.broader,
            URIRef('https://id.erfgoed.net/thesauri/materialen/42')
        ) in graph_dump


class TestRDFDumperProducts:

    def test_dump_rdf_to_rdf(self, products_provider):
        graph_dump = utils.rdf_dumper(products_provider)
        xml = graph_dump.serialize(format='xml', encoding="UTF-8")
        if isinstance(xml, bytes):
            xml = xml.decode("UTF-8")
        assert '<?xml' == xml[:5]

        assert 'http://www.products.com/' in xml
        assert 'http://www.products.com/Jewellery' in xml
        assert 'http://www.products.com/Perfume' in xml
        assert 'http://www.products.com/Product' in xml
        assert 'http://www.products.com/Stuff' in xml

    def test_dump_rdf_compare_type(self, products_provider):
        graph_dump = utils.rdf_dumper(products_provider)
        assert isinstance(graph_dump, Graph)

    def test_dump_rdf_no_uri_as_local_identifier(self, products_provider, caplog):
        caplog.set_level(logging.DEBUG)
        graph_dump = utils.rdf_dumper(products_provider)

        prod_uri = 'http://www.prodcuts.com/Product'
        jewel_uri = 'http://www.products.com/Jewellery'
        perfume_uri = 'http://www.products.com/Perfume'

        prod = URIRef(prod_uri)
        jewel = URIRef(jewel_uri)
        perfume = URIRef(perfume_uri)

        log.debug(graph_dump.serialize(format='turtle'))

        assert (prod, DCTERMS.identifier, Literal(prod_uri)) not in graph_dump
        assert (prod, DC.identifier, Literal(prod_uri)) not in graph_dump
        assert (jewel, DCTERMS.identifier, Literal(jewel_uri)) not in graph_dump
        assert (jewel, DC.identifier, Literal(jewel_uri)) not in graph_dump
        assert (perfume, DCTERMS.identifier, Literal(perfume_uri)) not in graph_dump
        assert (perfume, DC.identifier, Literal(perfume_uri)) not in graph_dump


class TestRDFDumperTrees:

    def test_dump_tree_to_rdf(self, tree_provider):
        graph_dump = utils.rdf_dumper(tree_provider)
        xml = graph_dump.serialize(format='xml', encoding="UTF-8")
        if isinstance(xml, bytes):
            xml = xml.decode("UTF-8")
        assert '<?xml' == xml[:5]

    def test_dump_larch_to_rdf(self, tree_provider):
        graph_dump = utils.rdf_c_dumper(tree_provider, 1)
        cs = URIRef('http://id.trees.org')
        assert (cs, RDF.type, SKOS.ConceptScheme) in graph_dump
        definitions = list(graph_dump.objects(cs, SKOS.definition))
        assert any('Trees as used by Monthy Python.' in str(d) for d in definitions)
        assert (cs, SKOS.prefLabel, Literal('Pythonic trees.', lang='en')) in graph_dump
        xml = graph_dump.serialize(format='xml', encoding="UTF-8")
        if isinstance(xml, bytes):
            xml = xml.decode("UTF-8")
        assert '<?xml' == xml[:5]

    def test_dump_chestnut_to_rdf(self, tree_provider):
        graph_dump = utils.rdf_c_dumper(tree_provider, 2)

        chestnut = URIRef('http://id.trees.org/2')
        assert (chestnut, SKOS.hiddenLabel, Literal('aaa', lang='nl')) in graph_dump
        assert (chestnut, SKOS.altLabel, Literal('De Paardekastanje', lang='nl')) in graph_dump
        assert (chestnut, SKOS.prefLabel, Literal('The Chestnut', lang='en')) in graph_dump
        assert (chestnut, SKOS.altLabel, Literal('la châtaigne', lang='fr')) in graph_dump
        assert (chestnut, SKOS.definition, Literal('A different type of tree.', lang='en')) in graph_dump

        citations = list(graph_dump.objects(predicate=DCTERMS.bibliographicCitation))
        assert citations[0] == Literal(
            '<strong>Monthy Python.</strong> Episode Three: How to recognise different types of trees from quite a long way away.',
            datatype=RDF.HTML
        )

    def test_dump_oak_to_rdf(self, tree_provider):
        graph_dump = utils.rdf_c_dumper(tree_provider, 4)
        oak = URIRef('http://id.trees.org/4')
        eik = URIRef('https://id.erfgoed.net/thesauri/soorten/297')
        assert (oak, SKOS.exactMatch, eik) in graph_dump

    def test_dump_one_id_to_rdf_and_reload(self, tree_provider, caplog):
        caplog.set_level(logging.DEBUG)
        graph_dump1 = utils.rdf_c_dumper(tree_provider, 1)
        provider = RDFProvider(
            {'id': 'Number1', 'dataset': {'uri': 'http://id.trees.org/dataset'}},
            graph_dump1
        )
        graph_dump2 = utils.rdf_c_dumper(provider, 1)
        graph_full_dump2 = utils.rdf_dumper(provider)
        assert provider.get_by_id(1)
        assert provider.get_by_id(3)
        assert len(graph_dump1) == len(graph_dump2)
        assert len(graph_full_dump2) > len(graph_dump2)

    def test_dump_conceptscheme_tree_to_rdf(self, tree_provider):
        graph_dump = utils.rdf_conceptscheme_dumper(tree_provider)
        cs = URIRef('http://id.trees.org')
        assert (cs, RDF.type, SKOS.ConceptScheme) in graph_dump
        definitions = list(graph_dump.objects(cs, SKOS.definition))
        assert any('Trees as used by Monthy Python.' in str(d) for d in definitions)
        assert (cs, SKOS.prefLabel, Literal('Pythonic trees.', lang='en')) in graph_dump


class TestRDFDumperExtraData:

    @pytest.fixture
    def provider_with_notation(self):
        from skosprovider.uri import UriPatternGenerator
        larch = {
            'id': '1',
            'uri': 'http://id.trees.org/1',
            'labels': [{'type': 'prefLabel', 'language': 'en', 'label': 'The Larch'}],
            'notation': ['larch-001'],
        }
        chestnut = {
            'id': '2',
            'uri': 'http://id.trees.org/2',
            'labels': [{'type': 'prefLabel', 'language': 'en', 'label': 'The Chestnut'}],
        }
        return DictionaryProvider(
            {'id': 'TREES'},
            [larch, chestnut],
            uri_generator=UriPatternGenerator('http://id.trees.org/%s'),
            concept_scheme=ConceptScheme('http://id.trees.org'),
        )

    @pytest.fixture
    def notation_serializer(self):
        def serializer(graph, subject, obj):
            if isinstance(obj.extra_data, dict):
                for notation in obj.extra_data.get('notation', []):
                    graph.add((subject, SKOS.notation, Literal(notation)))
        return serializer

    def test_rdf_dumper_without_serializer_no_notation(self, provider_with_notation):
        graph = utils.rdf_dumper(provider_with_notation)
        larch = URIRef('http://id.trees.org/1')
        assert (larch, SKOS.notation, Literal('larch-001')) not in graph

    def test_rdf_dumper_with_serializer_adds_notation(self, provider_with_notation, notation_serializer):
        graph = utils.rdf_dumper(provider_with_notation, extra_data_serializer=notation_serializer)
        larch = URIRef('http://id.trees.org/1')
        assert (larch, SKOS.notation, Literal('larch-001')) in graph

    def test_rdf_dumper_serializer_only_called_for_extra_data(self, provider_with_notation, notation_serializer):
        graph = utils.rdf_dumper(provider_with_notation, extra_data_serializer=notation_serializer)
        chestnut = URIRef('http://id.trees.org/2')
        assert list(graph.objects(chestnut, SKOS.notation)) == []

    def test_rdf_c_dumper_with_serializer(self, provider_with_notation, notation_serializer):
        graph = utils.rdf_c_dumper(provider_with_notation, '1', extra_data_serializer=notation_serializer)
        larch = URIRef('http://id.trees.org/1')
        assert (larch, SKOS.notation, Literal('larch-001')) in graph

    def test_rdf_conceptscheme_dumper_with_serializer(self):
        DCTERMS_CREATED = URIRef('http://purl.org/dc/terms/created')
        cs = ConceptScheme('http://id.trees.org', extra_data={'created': '2024-01-01'})
        provider = DictionaryProvider({'id': 'TREES'}, [], concept_scheme=cs)

        def serializer(graph, subject, obj):
            if isinstance(obj.extra_data, dict) and 'created' in obj.extra_data:
                graph.add((subject, DCTERMS_CREATED, Literal(obj.extra_data['created'])))

        graph = utils.rdf_conceptscheme_dumper(provider, extra_data_serializer=serializer)
        cs_ref = URIRef('http://id.trees.org')
        assert (cs_ref, DCTERMS_CREATED, Literal('2024-01-01')) in graph

    def test_rdf_dumper_round_trip_extra_data(self, provider_with_notation, notation_serializer):
        import rdflib
        graph = utils.rdf_dumper(provider_with_notation, extra_data_serializer=notation_serializer)
        rdf_provider = RDFProvider({'id': 'TREES'}, graph)
        larch = rdf_provider.get_by_uri('http://id.trees.org/1')
        assert isinstance(larch.extra_data, rdflib.Graph)
        assert (URIRef('http://id.trees.org/1'), SKOS.notation, Literal('larch-001')) in larch.extra_data

    def test_rdf_dumper_round_trip_no_extra_data(self, provider_with_notation, notation_serializer):
        graph = utils.rdf_dumper(provider_with_notation, extra_data_serializer=notation_serializer)
        rdf_provider = RDFProvider({'id': 'TREES'}, graph)
        chestnut = rdf_provider.get_by_uri('http://id.trees.org/2')
        assert chestnut.extra_data is None
