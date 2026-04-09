import pytest
from test_providers import chestnut
from test_providers import larch
from test_providers import species

from skosprovider.registry import Registry
from skosprovider.registry import RegistryException


class TestRegistry:

    def test_default_metadata_is_dict(self, registry):
        assert isinstance(registry.get_metadata(), dict)

    def test_passed_metadata_is_dict(self):
        reg = Registry(metadata={"catalog": {"uri": "http://my.data.org"}})
        assert "catalog" in reg.get_metadata()
        assert "uri" in reg.get_metadata().get("catalog")

    def test_set_instance_scope(self):
        reg = Registry(instance_scope="threaded_global")
        assert reg.instance_scope == "threaded_global"

    def test_set_invalid_instance_scope(self):
        with pytest.raises(ValueError):
            Registry(instance_scope="bad_scope")

    def test_empty_register_provider(self, registry, trees_provider):
        registry.register_provider(trees_provider)
        assert registry.get_provider("TREES") == trees_provider

    def test_empty_register_removeProvider(self, registry):
        assert not registry.remove_provider("TREES")

    def test_empty_getProviders(self, registry):
        assert registry.get_providers() == []
        assert registry.get_providers(ids=[]) == []

    def test_empty_getProviderById(self, registry):
        assert not registry.get_provider("TREES")
        assert not registry.get_provider("http://id.trees.org")

    def test_empty_findConcepts(self, registry):
        assert registry.find({}) == []

    def test_empty_getAllConcepts(self, registry):
        assert registry.get_all() == []

    def test_one_provider_register_provider(
        self, registry, trees_provider, geo_provider
    ):
        registry.register_provider(trees_provider)
        assert registry.get_provider("TREES") == trees_provider
        assert registry.get_provider("http://id.trees.org") == trees_provider
        registry.register_provider(geo_provider)
        assert registry.get_provider("GEOGRAPHY") == geo_provider
        assert registry.get_provider("urn:x-skosprovider:geography") == geo_provider

    def test_one_provider_register_double_provider(self, registry, trees_provider):
        registry.register_provider(trees_provider)
        assert registry.get_provider("TREES") == trees_provider
        with pytest.raises(RegistryException):
            registry.register_provider(trees_provider)
        # Change the id, but keep identical URIs
        trees_provider.metadata["id"] = "TREESTOO"
        with pytest.raises(RegistryException):
            registry.register_provider(trees_provider)
        trees_provider.metadata["id"] = "TREES"

    def test_register_provider_wrong_scope(self, registry):
        from skosprovider.skos import ConceptScheme
        from skosprovider.providers import DictionaryProvider

        t = DictionaryProvider(
            {"id": "TREES", "default_language": "nl"},
            [larch, chestnut, species],
            concept_scheme=ConceptScheme("urn:something"),
            allowed_instance_scopes=["threaded_thread"],
        )
        with pytest.raises(RegistryException):
            registry.register_provider(t)

    def test_one_provider_removeProvider(self, registry, trees_provider):
        registry.register_provider(trees_provider)
        assert registry.get_provider("TREES") == trees_provider
        registry.remove_provider("TREES")
        assert not registry.get_provider("TREES")

    def test_one_provider_removeProviderWithUri(self, registry, trees_provider):
        registry.register_provider(trees_provider)
        assert registry.get_provider("TREES") == trees_provider
        registry.remove_provider("http://id.trees.org")
        assert not registry.get_provider("TREES")

    def test_one_provider_getProviders(self, registry, trees_provider):
        registry.register_provider(trees_provider)
        assert registry.get_providers() == [trees_provider]
        assert registry.get_providers(ids=["TREES"]) == [trees_provider]

    def test_one_provider_getProvidersWithIds(self, registry, trees_provider):
        registry.register_provider(trees_provider)
        assert registry.get_providers(ids=["TREES"]) == [trees_provider]
        assert registry.get_providers() == [trees_provider]
        assert registry.get_providers(ids=["GEOGRAPHY"]) == []

    def test_one_provider_getProvidersWithUris(self, registry, trees_provider):
        registry.register_provider(trees_provider)
        assert registry.get_providers(ids=["http://id.trees.org"]) == [trees_provider]
        assert registry.get_providers() == [trees_provider]
        assert registry.get_providers(ids=["urn:x-skosprovider:geography"]) == []

    def test_one_provider_getProvidersWithSubject(self, registry, trees_provider):
        registry.register_provider(trees_provider)
        assert registry.get_providers(subject="something") == []
        assert registry.get_providers(subject="biology") == [trees_provider]

    def test_one_provider_getPoviderWithId(self, registry, trees_provider):
        registry.register_provider(trees_provider)
        assert registry.get_provider("TREES") == trees_provider

    def test_one_provider_getPoviderWithUri(self, registry, trees_provider):
        registry.register_provider(trees_provider)
        assert registry.get_provider("http://id.trees.org") == trees_provider

    def test_one_provider_findConcepts(self, registry, trees_provider):
        registry.register_provider(trees_provider)
        assert registry.find({"label": "The Larch"}) == [
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
        ]

    def test_one_provider_getConceptByUri(self, registry, trees_provider):
        registry.register_provider(trees_provider)
        c = registry.get_by_uri("http://id.trees.org/1")
        assert c.id == "1"
        assert c.uri == "http://id.trees.org/1"

    def test_one_provider_getConceptByUriDifferentFromConceptScheme(self, registry):
        from skosprovider.skos import ConceptScheme
        from skosprovider.providers import DictionaryProvider

        t = DictionaryProvider(
            {"id": "TREES", "default_language": "nl"},
            [larch, chestnut, species],
            concept_scheme=ConceptScheme("urn:something"),
        )
        registry.register_provider(t)
        c = registry.get_by_uri("http://id.trees.org/1")
        assert c.id == "1"
        assert c.uri == "http://id.trees.org/1"

    def test_one_provider_getConceptByUnexistingUri(self, registry, trees_provider):
        registry.register_provider(trees_provider)
        c = registry.get_by_uri("http://id.thingy.com/123456")
        assert not c

    def test_get_by_invalid_uri(self, registry):
        with pytest.raises(ValueError):
            registry.get_by_uri(None)

    def test_one_provider_findConceptsWithProviderid(self, registry, trees_provider):
        registry.register_provider(trees_provider)
        assert registry.find({"label": "The Larch"}, providers=["TREES"]) == [
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
        ]
        assert registry.find({"label": "The Larch"}, providers=[]) == []

    def test_one_provider_getAllConcepts(self, registry, trees_provider):
        registry.register_provider(trees_provider)
        assert registry.get_all() == [
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
        ]

    def test_one_provider_getAllConceptsDifferentLanguage(
        self, registry, trees_provider
    ):
        registry.register_provider(trees_provider)
        assert registry.get_all(language="en") == [
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
        ]

    def test_two_providers_findConceptsWithProviderIdAndUri(
        self, registry, trees_provider, geo_provider
    ):
        registry.register_provider(geo_provider)
        registry.register_provider(trees_provider)
        assert registry.find(
            {"label": "The Larch"}, providers=["TREES"]
        ) == registry.find({"label": "The Larch"}, providers=["http://id.trees.org"])

    def test_two_providers_findConceptsProvidersDictionarySyntax(
        self, registry, trees_provider, geo_provider
    ):
        registry.register_provider(geo_provider)
        registry.register_provider(trees_provider)
        assert registry.find(
            {"label": "The Larch"}, providers=["TREES"]
        ) == registry.find(
            {"label": "The Larch"}, providers={"ids": ["http://id.trees.org"]}
        )

    def test_one_provider_findConceptsWithSubject(self, registry, trees_provider):
        registry.register_provider(trees_provider)
        provs = registry.get_providers(subject="biology")
        res = [{"id": p.get_vocabulary_id(), "concepts": p.find({})} for p in provs]
        assert res == registry.find({}, subject="biology")

    def test_one_provider_findConceptsWithSubject_language_en(
        self, registry, trees_provider
    ):
        registry.register_provider(trees_provider)
        provs = registry.get_providers(subject="biology")
        res = [
            {"id": p.get_vocabulary_id(), "concepts": p.find({}, language="en")}
            for p in provs
        ]
        assert res == registry.find({}, subject="biology", language="en")

    def test_one_provider_findConceptsWithSubject_language_nl(
        self, registry, trees_provider
    ):
        registry.register_provider(trees_provider)
        provs = registry.get_providers(subject="biology")
        res = [{"id": p.get_vocabulary_id(), "concepts": p.find({})} for p in provs]
        assert res == registry.find({}, subject="biology", language="nl")
