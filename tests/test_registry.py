import unittest
from unittest.mock import MagicMock
from unittest.mock import Mock

import pytest
from test_providers import chestnut
from test_providers import geo
from test_providers import larch
from test_providers import species
from test_providers import trees

from skosprovider.registry import Registry
from skosprovider.registry import RegistryException


class RegistryTests(unittest.TestCase):
    def setUp(self):
        self.reg = Registry()
        self.prov = trees
        self.prov2 = geo

    def tearDown(self):
        self.reg = None
        self.prov = None
        self.prov2 = None

    def test_default_metadata_is_dict(self):
        self.assertIsInstance(self.reg.get_metadata(), dict)

    def test_passed_metadata_is_dict(self):
        self.reg = Registry(metadata={"catalog": {"uri": "http://my.data.org"}})
        assert "catalog" in self.reg.get_metadata()
        assert "uri" in self.reg.get_metadata().get("catalog")

    def test_set_instance_scope(self):
        self.reg = Registry(instance_scope="threaded_global")
        assert self.reg.instance_scope == "threaded_global"

    def test_set_invalid_instance_scope(self):
        with pytest.raises(ValueError):
            Registry(instance_scope="bad_scope")

    def test_empty_register_provider(self):
        self.reg.register_provider(self.prov)
        self.assertEqual(self.reg.get_provider("TREES"), self.prov)

    def test_empty_register_removeProvider(self):
        self.assertFalse(self.reg.remove_provider("TREES"))

    def test_empty_getProviders(self):
        self.assertEqual(self.reg.get_providers(), [])
        self.assertEqual(self.reg.get_providers(ids=[]), [])

    def test_empty_getProviderById(self):
        self.assertFalse(self.reg.get_provider("TREES"))
        self.assertFalse(self.reg.get_provider("http://id.trees.org"))

    def test_empty_findConcepts(self):
        self.assertEqual(self.reg.find({}), [])

    def test_empty_getAllConcepts(self):
        self.assertEqual(self.reg.get_all(), [])

    def test_one_provider_register_provider(self):
        self.reg.register_provider(self.prov)
        self.assertEqual(self.reg.get_provider("TREES"), self.prov)
        self.assertEqual(self.reg.get_provider("http://id.trees.org"), self.prov)
        self.reg.register_provider(self.prov2)
        self.assertEqual(self.reg.get_provider("GEOGRAPHY"), self.prov2)
        self.assertEqual(
            self.reg.get_provider("urn:x-skosprovider:geography"), self.prov2
        )

    def test_one_provider_register_double_provider(self):
        self.reg.register_provider(self.prov)
        self.assertEqual(self.reg.get_provider("TREES"), self.prov)
        self.assertRaises(RegistryException, self.reg.register_provider, self.prov)
        # Change the id, but keep identical URIs
        self.prov.metadata["id"] = "TREESTOO"
        self.assertRaises(RegistryException, self.reg.register_provider, self.prov)
        self.prov.metadata["id"] = "TREES"

    def test_register_provider_wrong_scope(self):
        from skosprovider.skos import ConceptScheme
        from skosprovider.providers import DictionaryProvider

        trees = DictionaryProvider(
            {"id": "TREES", "default_language": "nl"},
            [larch, chestnut, species],
            concept_scheme=ConceptScheme("urn:something"),
            allowed_instance_scopes=["threaded_thread"],
        )
        with pytest.raises(RegistryException):
            self.reg.register_provider(trees)

    def test_register_provider_no_uri(self):
        p = Mock()
        p.allowed_instance_scopes = ["single"]
        p.get_vocabulary_id = MagicMock(return_value="MYID")
        del p.get_vocabulary_uri
        p.concept_scheme = MagicMock()
        p.concept_scheme.uri = "http://my.id.org"
        self.reg.register_provider(p)
        assert p == self.reg.get_provider("MYID")
        assert p == self.reg.get_provider("http://my.id.org")

    def test_remove_provider_no_uri(self):
        provider = Mock()
        provider.allowed_instance_scopes = ["single"]
        provider.get_vocabulary_id = MagicMock(return_value="MYID")
        del provider.get_vocabulary_uri
        provider.concept_scheme = MagicMock()
        provider.concept_scheme.uri = "http://my.id.org"
        self.reg.register_provider(provider)
        assert provider == self.reg.get_provider("MYID")
        assert provider == self.reg.get_provider("http://my.id.org")
        self.reg.remove_provider("http://my.id.org")
        assert not self.reg.get_provider("MYID")

    def test_one_provider_removeProvider(self):
        self.reg.register_provider(self.prov)
        self.assertEqual(self.reg.get_provider("TREES"), self.prov)
        self.reg.remove_provider("TREES")
        self.assertFalse(self.reg.get_provider("TREES"))

    def test_one_provider_removeProviderWithUri(self):
        self.reg.register_provider(self.prov)
        self.assertEqual(self.reg.get_provider("TREES"), self.prov)
        self.reg.remove_provider("http://id.trees.org")
        self.assertFalse(self.reg.get_provider("TREES"))

    def test_one_provider_getProviders(self):
        self.reg.register_provider(self.prov)
        self.assertEqual(self.reg.get_providers(), [self.prov])
        self.assertEqual(self.reg.get_providers(ids=["TREES"]), [self.prov])

    def test_one_provider_getProvidersWithIds(self):
        self.reg.register_provider(self.prov)
        self.assertEqual(self.reg.get_providers(ids=["TREES"]), [self.prov])
        self.assertEqual(self.reg.get_providers(), [self.prov])
        self.assertEqual(self.reg.get_providers(ids=["GEOGRAPHY"]), [])

    def test_one_provider_getProvidersWithUris(self):
        self.reg.register_provider(self.prov)
        assert self.reg.get_providers(ids=["http://id.trees.org"]) == [self.prov]
        assert self.reg.get_providers() == [self.prov]
        assert self.reg.get_providers(ids=["urn:x-skosprovider:geography"]) == []

    def test_one_provider_getProvidersWithSubject(self):
        self.reg.register_provider(self.prov)
        self.assertEqual(self.reg.get_providers(subject="something"), [])
        self.assertEqual(self.reg.get_providers(subject="biology"), [self.prov])

    def test_one_provider_getPoviderWithId(self):
        self.reg.register_provider(self.prov)
        self.assertEqual(self.reg.get_provider("TREES"), self.prov)

    def test_one_provider_getPoviderWithUri(self):
        self.reg.register_provider(self.prov)
        self.assertEqual(self.reg.get_provider("http://id.trees.org"), self.prov)

    def test_one_provider_findConcepts(self):
        self.reg.register_provider(self.prov)
        self.assertEqual(
            self.reg.find({"label": "The Larch"}),
            [
                {
                    "id": "TREES",
                    "concepts": [
                        {
                            "id": "1",
                            "uri": "http://id.trees.org/1",
                            "type": "concept",
                            "label": "De Lariks",
                        }
                    ],
                }
            ],
        )

    def test_one_provider_getConceptByUri(self):
        self.reg.register_provider(self.prov)
        c = self.reg.get_by_uri("http://id.trees.org/1")
        self.assertEqual(c.id, "1")
        self.assertEqual(c.uri, "http://id.trees.org/1")

    def test_one_provider_getConceptByUriDifferentFromConceptScheme(self):
        from skosprovider.skos import ConceptScheme
        from skosprovider.providers import DictionaryProvider

        trees = DictionaryProvider(
            {"id": "TREES", "default_language": "nl"},
            [larch, chestnut, species],
            concept_scheme=ConceptScheme("urn:something"),
        )
        self.reg.register_provider(trees)
        c = self.reg.get_by_uri("http://id.trees.org/1")
        self.assertEqual(c.id, "1")
        self.assertEqual(c.uri, "http://id.trees.org/1")

    def test_one_provider_getConceptByUnexistingUri(self):
        self.reg.register_provider(self.prov)
        c = self.reg.get_by_uri("http://id.thingy.com/123456")
        self.assertFalse(c)

    def test_get_by_invalid_uri(self):
        self.assertRaises(ValueError, self.reg.get_by_uri, None)

    def test_one_provider_findConceptsWithProviderid(self):
        self.reg.register_provider(self.prov)
        self.assertEqual(
            self.reg.find({"label": "The Larch"}, providers=["TREES"]),
            [
                {
                    "id": "TREES",
                    "concepts": [
                        {
                            "id": "1",
                            "uri": "http://id.trees.org/1",
                            "type": "concept",
                            "label": "De Lariks",
                        }
                    ],
                }
            ],
        )
        self.assertEqual(self.reg.find({"label": "The Larch"}, providers=[]), [])

    def test_one_provider_getAllConcepts(self):
        self.reg.register_provider(self.prov)
        self.assertEqual(
            self.reg.get_all(),
            [
                {
                    "id": "TREES",
                    "concepts": [
                        {
                            "id": "1",
                            "uri": "http://id.trees.org/1",
                            "type": "concept",
                            "label": "De Lariks",
                        },
                        {
                            "id": "2",
                            "uri": "http://id.trees.org/2",
                            "type": "concept",
                            "label": "De Paardekastanje",
                        },
                        {
                            "id": 3,
                            "uri": "http://id.trees.org/3",
                            "type": "collection",
                            "label": "Bomen per soort",
                        },
                    ],
                }
            ],
        )

    def test_one_provider_getAllConceptsDifferentLanguage(self):
        self.reg.register_provider(self.prov)
        self.assertEqual(
            self.reg.get_all(language="en"),
            [
                {
                    "id": "TREES",
                    "concepts": [
                        {
                            "id": "1",
                            "uri": "http://id.trees.org/1",
                            "type": "concept",
                            "label": "The Larch",
                        },
                        {
                            "id": "2",
                            "uri": "http://id.trees.org/2",
                            "type": "concept",
                            "label": "The Chestnut",
                        },
                        {
                            "id": 3,
                            "uri": "http://id.trees.org/3",
                            "type": "collection",
                            "label": "Trees by species",
                        },
                    ],
                }
            ],
        )

    def test_two_providers_findConceptsWithProviderIdAndUri(self):
        self.reg.register_provider(self.prov2)
        self.reg.register_provider(self.prov)
        self.assertEqual(
            self.reg.find({"label": "The Larch"}, providers=["TREES"]),
            self.reg.find({"label": "The Larch"}, providers=["http://id.trees.org"]),
        )

    def test_two_providers_findConceptsProvidersDictionarySyntax(self):
        self.reg.register_provider(self.prov2)
        self.reg.register_provider(self.prov)
        self.assertEqual(
            self.reg.find({"label": "The Larch"}, providers=["TREES"]),
            self.reg.find(
                {"label": "The Larch"}, providers={"ids": ["http://id.trees.org"]}
            ),
        )

    def test_one_provider_findConceptsWithSubject(self):
        self.reg.register_provider(self.prov)
        provs = self.reg.get_providers(subject="biology")
        res = [{"id": p.get_vocabulary_id(), "concepts": p.find({})} for p in provs]
        self.assertEqual(res, self.reg.find({}, subject="biology"))

    def test_one_provider_findConceptsWithSubject_language_en(self):
        self.reg.register_provider(self.prov)
        provs = self.reg.get_providers(subject="biology")
        res = [
            {"id": p.get_vocabulary_id(), "concepts": p.find({}, language="en")}
            for p in provs
        ]
        self.assertEqual(res, self.reg.find({}, subject="biology", language="en"))

    def test_one_provider_findConceptsWithSubject_language_nl(self):
        self.reg.register_provider(self.prov)
        provs = self.reg.get_providers(subject="biology")
        res = [{"id": p.get_vocabulary_id(), "concepts": p.find({})} for p in provs]
        self.assertEqual(res, self.reg.find({}, subject="biology", language="nl"))
