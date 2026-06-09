import pytest
from tests.test_providers import chestnut
from tests.test_providers import geo
from tests.test_providers import larch
from tests.test_providers import species

from skosprovider.providers import DictionaryProvider
from skosprovider.registry import Registry
from skosprovider.skos import ConceptScheme


@pytest.fixture
def trees_provider():
    """Create a fresh DictionaryProvider for trees.

    Returns a new instance each time to avoid test pollution from
    tests that mutate provider metadata.
    """
    return DictionaryProvider(
        {
            "id": "TREES",
            "default_language": "nl",
            "subject": ["biology"],
            "dataset": {"uri": "http://id.trees.org/dataset"},
        },
        [larch, chestnut, species],
        concept_scheme=ConceptScheme(
            "http://id.trees.org",
            labels=[
                {
                    "uri": "http://id.trees.org/labels/soorten-nl",
                    "type": "prefLabel",
                    "language": "nl",
                    "label": "Soorten",
                },
                {"type": "prefLabel", "language": "en", "label": "Species"},
            ],
            languages=["nl", "en"],
        ),
    )


@pytest.fixture
def geo_provider():
    """Return the module-level geo provider.

    No test mutates geo's metadata, so sharing the instance is safe.
    """
    return geo


@pytest.fixture
def registry():
    return Registry()
