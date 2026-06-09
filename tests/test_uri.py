import pytest

from skosprovider.uri import DefaultConceptSchemeUrnGenerator
from skosprovider.uri import DefaultUrnGenerator
from skosprovider.uri import TypedUrnGenerator
from skosprovider.uri import UriPatternGenerator
from skosprovider.uri import is_uri


class TestIsUri:

    def test_None(self):
        assert not is_uri(None)

    def test_url(self):
        assert is_uri("https://id.erfgoed.net/thesauri/erfgoedtypes/1")
        assert is_uri("https://thesaurus.erfgoed.net/conceptschemes/erfgoedtypes/1")

    def test_urn(self):
        assert is_uri("urn:x-skosprovider:typologie")
        assert is_uri("urn:x-skosprovider:typologie:1")


class TestUriPatternGenerator:

    def test_simple(self):
        urigen = UriPatternGenerator("http://id.example.com/%s")
        assert "http://id.example.com/1" == urigen.generate(concept_id=1)

    def test_pattern_none(self):
        with pytest.raises(ValueError):
            UriPatternGenerator(None)

    def test_pattern_no_placeholder(self):
        with pytest.raises(ValueError):
            UriPatternGenerator("http://id.example.com/")

    def test_pattern_multiple_placeholders(self):
        with pytest.raises(ValueError):
            UriPatternGenerator("http://id.example.com/%s/%s")

    def test_pattern_escaped_placeholder(self):
        UriPatternGenerator("http://id.example.com/%%s/%s")
        # No exception should be raised


class TestDefaultUrnGenerator:

    @pytest.fixture
    def urn_generator(self):
        return DefaultUrnGenerator("typologie")

    def test_simple(self, urn_generator):
        assert "urn:x-skosprovider:typologie:1" == urn_generator.generate(concept_id=1)

    def test_missing_argument(self, urn_generator):
        with pytest.raises(TypeError):
            urn_generator.generate(uri_type="set")


class TestDefaultConceptSchemeUrnGenerator:

    @pytest.fixture
    def urn_generator(self):
        return DefaultConceptSchemeUrnGenerator()

    def test_simple(self, urn_generator):
        assert "urn:x-skosprovider:typologie" == urn_generator.generate(concept_id="TYPOLOGIE")

    def test_missing_argument(self, urn_generator):
        with pytest.raises(TypeError):
            urn_generator.generate()


class TestTypedUrnGenerator:

    @pytest.fixture
    def urn_generator(self):
        return TypedUrnGenerator("typologie")

    def test_concept(self, urn_generator):
        assert "urn:x-skosprovider:typologie:concept:1" == urn_generator.generate(
            uri_type="concept", concept_id=1
        )

    def test_collection(self, urn_generator):
        assert "urn:x-skosprovider:typologie:collection:7000" == urn_generator.generate(
            uri_type="collection", concept_id=7000
        )

    def test_invalid_type(self, urn_generator):
        with pytest.raises(ValueError):
            urn_generator.generate(uri_type="set", concept_id=1)
