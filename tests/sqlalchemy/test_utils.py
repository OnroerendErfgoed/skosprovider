import csv
import os

from skosprovider.sqlalchemy.models import Base
from skosprovider.sqlalchemy.models import Initialiser
from skosprovider.sqlalchemy.utils import VisitationCalculator
from skosprovider.sqlalchemy.utils import import_provider
from tests.sqlalchemy import DBTestCase

from sqlalchemy import select
from sqlalchemy.orm import session


def _get_menu():
    from skosprovider.providers import SimpleCsvProvider

    ifile = open(os.path.join(os.path.dirname(__file__), "data", "menu.csv"))
    reader = csv.reader(ifile)
    csvprovider = SimpleCsvProvider({"id": "MENU"}, reader)
    ifile.close()
    return csvprovider


def _get_geo():
    from skosprovider.providers import DictionaryProvider

    geo = DictionaryProvider(
        {"id": "GEOGRAPHY"},
        [
            {
                "id": "1",
                "labels": [{"type": "prefLabel", "language": "en", "label": "World"}],
                "narrower": [2, 3],
            },
            {
                "id": 2,
                "labels": [{"type": "prefLabel", "language": "en", "label": "Europe"}],
                "narrower": [4, 5, 10],
                "broader": [1],
            },
            {
                "id": 3,
                "labels": [
                    {"type": "prefLabel", "language": "en", "label": "North-America"}
                ],
                "narrower": [6],
                "broader": [1],
            },
            {
                "id": 4,
                "labels": [{"type": "prefLabel", "language": "en", "label": "Belgium"}],
                "narrower": [7, 8, 9],
                "broader": [2],
                "related": [10],
            },
            {
                "id": 5,
                "labels": [
                    {"type": "prefLabel", "language": "en", "label": "United Kingdom"}
                ],
                "broader": [2],
            },
            {
                "id": 6,
                "labels": [
                    {
                        "type": "prefLabel",
                        "language": "en",
                        "label": "United States of America",
                    }
                ],
                "broader": [3],
            },
            {
                "id": 7,
                "labels": [
                    {"type": "prefLabel", "language": "en", "label": "Flanders"},
                    {"type": "prefLabel", "language": "nl-BE", "label": "Vlaanderen"},
                ],
                "broader": [4],
            },
            {
                "id": 8,
                "labels": [
                    {"type": "prefLabel", "language": "en", "label": "Brussels"}
                ],
                "broader": [4],
            },
            {
                "id": 9,
                "labels": [
                    {"type": "prefLabel", "language": "en", "label": "Wallonie"}
                ],
                "broader": [4],
            },
            {
                "id": 10,
                "labels": [
                    {"type": "prefLabel", "language": "nl", "label": "Nederland"}
                ],
                "related": [4],
            },
            {
                "id": "333",
                "type": "collection",
                "labels": [
                    {
                        "type": "prefLabel",
                        "language": "en",
                        "label": "Places where dutch is spoken",
                    }
                ],
                "members": ["4", "7", 8, 10],
            },
        ],
    )
    return geo


def _get_buildings():
    from skosprovider.providers import DictionaryProvider
    from skosprovider.skos import ConceptScheme
    from skosprovider.uri import UriPatternGenerator

    buildings = DictionaryProvider(
        {"id": "BUILDINGS"},
        [
            {
                "id": "1",
                "labels": [
                    {"type": "prefLabel", "language": "en", "label": "Fortifications"}
                ],
                "narrower": [2],
                "matches": {"exact": ["http://vocab.getty.edu/aat/300006888"]},
            },
            {
                "id": "2",
                "labels": [{"type": "prefLabel", "language": "en", "label": "Castle"}],
                "broader": [1, 3],
                "matches": {"broad": ["http://vocab.getty.edu/aat/300006888"]},
            },
            {
                "id": "3",
                "labels": [
                    {"type": "prefLabel", "language": "en", "label": "Habitations"}
                ],
                "narrower": [2, 4],
                "matches": {"close": ["http://vocab.getty.edu/aat/300005425"]},
            },
            {
                "id": "4",
                "labels": [
                    {"type": "prefLabel", "language": "en", "label": "Huts"},
                    {"type": "prefLabel", "language": None, "label": "Hutten"},
                ],
                "broader": [3],
                "matches": {"exact": ["http://vocab.getty.edu/aat/300004824"]},
            },
        ],
        concept_scheme=ConceptScheme(uri="https://id.buildings.org"),
        uri_generator=UriPatternGenerator("https://id.buildings.org/%s"),
    )
    return buildings


def _get_materials():
    from skosprovider.providers import DictionaryProvider
    from skosprovider.skos import ConceptScheme
    from skosprovider.uri import UriPatternGenerator

    materials = DictionaryProvider(
        {"id": "MATERIALS"},
        [
            {
                "id": "1",
                "labels": [
                    {"type": "prefLabel", "language": "en", "label": "Cardboard"}
                ],
                "narrower": [2],
                "related": [3],
                "subordinate_arrays": [56],
            },
            {
                "id": "789",
                "type": "collection",
                "labels": [
                    {"type": "prefLabel", "language": "en", "label": "Wood by Tree"}
                ],
                "members": [654],
            },
        ],
        concept_scheme=ConceptScheme(uri="https://id.materials.org"),
        uri_generator=UriPatternGenerator("https://id.materials.org/%s"),
    )
    return materials


def _get_heritage_types():
    import json

    with open(os.path.join(os.path.dirname(__file__), "data", "typologie.js")) as f:
        typology_data = json.load(f)["typologie"]
    from skosprovider.providers import DictionaryProvider
    from skosprovider.skos import ConceptScheme
    from skosprovider.uri import UriPatternGenerator

    heritage_types = DictionaryProvider(
        {"id": "HERITAGE_TYPES"},
        typology_data,
        uri_generator=UriPatternGenerator(
            "https://id.erfgoed.net/thesauri/erfgoedtypes/%s"
        ),
        concept_scheme=ConceptScheme(
            uri="https://id.erfgoed.net/thesauri/erfgoedtypes",
            labels=[
                {"label": "Erfgoedtypes", "type": "prefLabel", "language": "nl-BE"},
                {"label": "Heritagetypes", "type": "prefLabel", "language": "en"},
            ],
            notes=[
                {
                    "note": "Different types of heritage.",
                    "type": "definition",
                    "language": "en",
                },
                {
                    "note": "Verschillende types van erfgoed.",
                    "type": "definition",
                    "language": "nl",
                },
            ],
            languages=["nl", "en"],
        ),
    )
    return heritage_types


def _get_event_types():
    import json

    with open(os.path.join(os.path.dirname(__file__), "data", "gebeurtenis.json")) as f:
        event_data = json.load(f)["gebeurtenis"]
    from skosprovider.providers import DictionaryProvider
    from skosprovider.uri import UriPatternGenerator

    event_types = DictionaryProvider(
        {"id": "EVENT_TYPES"},
        event_data,
        uri_generator=UriPatternGenerator(
            "https://id.erfgoed.net/thesauri/gebeurtenistypes/%s"
        ),
    )
    return event_types


class TestImportProviderTests(DBTestCase):
    def setUp(self):
        Base.metadata.create_all(self.engine)
        self.session = self.session_maker()
        Initialiser(self.session).init_all()

    def tearDown(self):
        self.session.rollback()
        session.close_all_sessions()
        Base.metadata.drop_all(self.engine)

    def _get_cs(self):
        from skosprovider.sqlalchemy.models import ConceptScheme as ConceptSchemeModel

        return ConceptSchemeModel(id=68, uri="urn:x-skosprovider:cs:68")

    def test_empty_provider(self):
        from skosprovider.providers import DictionaryProvider
        from skosprovider.sqlalchemy.models import ConceptScheme as ConceptSchemeModel

        p = DictionaryProvider({"id": "EMPTY"}, [])
        cs = self._get_cs()
        self.session.add(cs)
        import_provider(p, self.session, cs)
        scheme = self.session.get(ConceptSchemeModel, 68)
        assert scheme == cs

    def test_string_concept_id_provider(self):
        from skosprovider.providers import DictionaryProvider
        from skosprovider.sqlalchemy.models import ConceptScheme as ConceptSchemeModel

        p = DictionaryProvider(
            {"id": "EMPTY"},
            [{"id": "manual-1", "uri": "urn:x-skosprovider:manual/manual-1"}],
        )
        cs = self._get_cs()
        self.session.add(cs)
        import_provider(p, self.session, cs)
        scheme = self.session.get(ConceptSchemeModel, 68)
        assert scheme == cs
        assert len(scheme.concepts) == 1
        assert scheme.concepts[0].concept_id == "manual-1"

    def test_menu(self):
        from skosprovider.sqlalchemy.models import Concept as ConceptModel

        csvprovider = _get_menu()
        cs = self._get_cs()
        self.session.add(cs)
        import_provider(csvprovider, self.session, cs)
        lobster = self.session.execute(
            select(ConceptModel).filter(
                ConceptModel.conceptscheme == cs, ConceptModel.concept_id == "11"
            )
        ).scalar_one()
        assert "11" == lobster.concept_id
        assert "urn:x-skosprovider:menu:11" == lobster.uri
        assert "Lobster Thermidor" == lobster.label().label
        assert 1 == len(lobster.notes)

    def test_geo(self):
        from skosprovider.sqlalchemy.models import Collection as CollectionModel
        from skosprovider.sqlalchemy.models import Concept as ConceptModel

        geoprovider = _get_geo()
        cs = self._get_cs()
        self.session.add(cs)
        import_provider(geoprovider, self.session, cs)
        self.session.flush()
        self.session.expire_all()
        world = self.session.execute(
            select(ConceptModel).filter(
                ConceptModel.conceptscheme == cs, ConceptModel.concept_id == "1"
            )
        ).scalar_one()
        assert world.concept_id == "1"
        assert "urn:x-skosprovider:geography:1" == world.uri
        assert "World" == world.label("en").label
        assert 1 == len(world.labels)
        assert 2 == len(world.narrower_concepts)

        dutch = self.session.execute(
            select(CollectionModel).filter(
                CollectionModel.conceptscheme == cs, CollectionModel.concept_id == "333"
            )
        ).scalar_one()
        assert "333" == dutch.concept_id
        assert "urn:x-skosprovider:geography:333" == dutch.uri
        assert "collection" == dutch.type
        assert 1 == len(dutch.labels)
        assert 4 == len(dutch.members)

        netherlands = self.session.execute(
            select(ConceptModel).filter(
                ConceptModel.conceptscheme == cs,
                ConceptModel.concept_id == "10",
            )
        ).scalar_one()
        assert "10" == netherlands.concept_id
        assert "concept" == netherlands.type
        assert 1 == len(netherlands.labels)
        assert "2" == netherlands.broader_concepts.pop().concept_id
        assert 1 == len(netherlands.related_concepts)

    def test_buildings(self):
        from skosprovider.sqlalchemy.models import Concept as ConceptModel

        buildingprovider = _get_buildings()
        cs = self._get_cs()
        self.session.add(cs)
        import_provider(buildingprovider, self.session, cs)
        castle = self.session.execute(
            select(ConceptModel).filter(
                ConceptModel.conceptscheme == cs, ConceptModel.concept_id == "2"
            )
        ).scalar_one()
        assert 2 == len(castle.broader_concepts)
        hut = self.session.execute(
            select(ConceptModel).filter(
                ConceptModel.conceptscheme == cs, ConceptModel.concept_id == "4"
            )
        ).scalar_one()
        assert 1 == len(hut.broader_concepts)
        assert 1 == len(hut.matches)
        assert "exactMatch" == hut.matches[0].matchtype_id
        assert "http://vocab.getty.edu/aat/300004824" == hut.matches[0].uri

    def test_conceptscheme_is_optional(self):
        from skosprovider.sqlalchemy.models import Concept as ConceptModel

        buildingprovider = _get_buildings()
        cs = import_provider(buildingprovider, self.session)
        assert "https://id.buildings.org" == cs.uri

        castle = self.session.execute(
            select(ConceptModel).filter(
                ConceptModel.conceptscheme == cs, ConceptModel.concept_id == "2"
            )
        ).scalar_one()
        assert 2 == len(castle.broader_concepts)

    def test_heritage_types(self):
        from skosprovider.sqlalchemy.models import Concept as ConceptModel

        heritagetypesprovider = _get_heritage_types()
        cs = self._get_cs()
        self.session.add(cs)
        import_provider(heritagetypesprovider, self.session, cs)
        bomen = self.session.execute(
            select(ConceptModel).filter(
                ConceptModel.conceptscheme == cs, ConceptModel.concept_id == "72"
            )
        ).scalar_one()
        assert 2 == len(bomen.narrower_collections)
        assert 2 == len(cs.labels)
        assert "Erfgoedtypes" == cs.label("nl").label
        assert 2 == len(cs.notes)
        assert 2 == len(cs.languages)

    def test_event_types(self):
        from skosprovider.sqlalchemy.models import Concept as ConceptModel

        eventtypesprovider = _get_event_types()
        cs = self._get_cs()
        self.session.add(cs)
        import_provider(eventtypesprovider, self.session, cs)
        archeologische_opgravingen = self.session.execute(
            select(ConceptModel).filter(
                ConceptModel.conceptscheme == cs, ConceptModel.concept_id == "38"
            )
        ).scalar_one()
        assert 3 == len(archeologische_opgravingen.narrower_collections)

    def test_materials(self):
        from skosprovider.sqlalchemy.models import Thing as ThingModel

        materialsprovider = _get_materials()
        cs = self._get_cs()
        self.session.add(cs)
        import_provider(materialsprovider, self.session, cs)
        materials = (
            self.session.execute(
                select(ThingModel).filter(ThingModel.conceptscheme == cs)
            )
            .scalars()
            .all()
        )
        assert 2 == len(materials)

    def test_materials_cs_is_created(self):
        materialsprovider = _get_materials()
        cs = self._get_cs()
        self.session.add(cs)
        cs = import_provider(materialsprovider, self.session, cs)

        materialsprovider = _get_materials()
        cs_from_provider = import_provider(materialsprovider, self.session)

        assert cs_from_provider.id != cs.id


class TestVisitationCalculator(DBTestCase):
    def setUp(self):
        Base.metadata.create_all(self.engine)
        self.session = self.session_maker()
        Initialiser(self.session).init_all()

    def tearDown(self):
        self.session.rollback()
        session.close_all_sessions()
        Base.metadata.drop_all(self.engine)

    def _get_cs(self):
        from skosprovider.sqlalchemy.models import ConceptScheme as ConceptSchemeModel

        return ConceptSchemeModel(id=1, uri="urn:x-skosprovider:cs:1")

    def test_empty_provider(self):
        from skosprovider.providers import DictionaryProvider

        p = DictionaryProvider({"id": "EMPTY"}, [])
        cs = self._get_cs()
        self.session.add(cs)
        import_provider(p, self.session, cs)
        vc = VisitationCalculator(self.session)
        v = vc.visit(cs)
        assert 0 == len(v)

    def test_provider_invalid_language(self):
        from skosprovider.providers import DictionaryProvider

        with self.assertRaises(ValueError):
            p = DictionaryProvider(
                {"id": "EMPTY"},
                [
                    {
                        "id": "1",
                        "labels": [
                            {
                                "type": "prefLabel",
                                "language": "nederlands",
                                "label": "Versterkingen",
                            }
                        ],
                    }
                ],
            )
            cs = self._get_cs()
            self.session.add(cs)
            import_provider(p, self.session, cs)

    def test_menu(self):
        csvprovider = _get_menu()
        cs = self._get_cs()
        self.session.add(cs)
        import_provider(csvprovider, self.session, cs)
        vc = VisitationCalculator(self.session)
        visit = vc.visit(cs)
        assert 11 == len(visit)
        for v in visit:
            assert v["lft"] + 1 == v["rght"]
            assert 1 == v["depth"]

    def test_menu_sorted(self):
        csvprovider = _get_menu()
        cs = self._get_cs()
        self.session.add(cs)
        import_provider(csvprovider, self.session, cs)
        vc = VisitationCalculator(self.session)
        visit = vc.visit(cs)
        assert 11 == len(visit)
        left = 1
        for v in visit:
            assert v["lft"] == left
            left += 2

    def test_geo(self):
        from skosprovider.sqlalchemy.models import Concept as ConceptModel

        geoprovider = _get_geo()
        cs = self._get_cs()
        self.session.add(cs)
        import_provider(geoprovider, self.session, cs)
        vc = VisitationCalculator(self.session)
        visit = vc.visit(cs)
        assert 10 == len(visit)
        world = visit[0]
        assert self.session.get(ConceptModel, world["id"]).concept_id == "1"
        assert 1 == world["lft"]
        assert 20 == world["rght"]
        assert 1 == world["depth"]
        for v in visit:
            if v["id"] == 3:
                assert v["lft"] + 3 == v["rght"]
                assert 2 == v["depth"]
            if v["id"] == 6:
                assert v["lft"] + 1 == v["rght"]
                assert 3 == v["depth"]

    def test_buildings(self):
        from skosprovider.sqlalchemy.models import Concept as ConceptModel

        buildingprovider = _get_buildings()
        cs = self._get_cs()
        self.session.add(cs)
        import_provider(buildingprovider, self.session, cs)
        vc = VisitationCalculator(self.session)
        visit = vc.visit(cs)
        assert len(visit) == 5
        ids = [self.session.get(ConceptModel, v["id"]).concept_id for v in visit]
        assert ids.count("2") == 2
        for v in visit:
            if v["id"] == 1:
                assert v["lft"] + 3 == v["rght"]
                assert 1 == v["depth"]
            if v["id"] == 3:
                assert v["lft"] + 5 == v["rght"]
                assert 1 == v["depth"]
            if v["id"] == 2:
                assert v["lft"] + 1 == v["rght"]
                assert 2 == v["depth"]
