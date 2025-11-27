import unittest

from skosprovider.uri import DefaultConceptSchemeUrnGenerator
from skosprovider.uri import DefaultUrnGenerator
from skosprovider.uri import TypedUrnGenerator
from skosprovider.uri import UriPatternGenerator
from skosprovider.uri import is_uri


class IsUriTest(unittest.TestCase):
    def test_None(self):
        assert not is_uri(None)

    def test_url(self):
        assert is_uri("https://id.erfgoed.net/thesauri/erfgoedtypes/1")
        assert is_uri("https://thesaurus.erfgoed.net/conceptschemes/erfgoedtypes/1")

    def test_urn(self):
        assert is_uri("urn:x-skosprovider:typologie")
        assert is_uri("urn:x-skosprovider:typologie:1")


class UriPatternGeneratorTest(unittest.TestCase):
    def test_simple(self):
        urigen = UriPatternGenerator("http://id.example.com/%s")
        self.assertEqual("http://id.example.com/1", urigen.generate(id=1))

    def test_pattern_none(self):
        with self.assertRaises(ValueError):
            UriPatternGenerator(None)

    def test_pattern_no_placeholder(self):
        with self.assertRaises(ValueError):
            UriPatternGenerator("http://id.example.com/")

    def test_pattern_multiple_placeholders(self):
        with self.assertRaises(ValueError):
            UriPatternGenerator("http://id.example.com/%s/%s")

    def test_pattern_escaped_placeholder(self):
        UriPatternGenerator("http://id.example.com/%%s/%s")
        # No exception should be raised


class DefaultUrnGeneratorTest(unittest.TestCase):
    def setUp(self):
        self.urigen = DefaultUrnGenerator("typologie")

    def tearDown(self):
        del self.urigen

    def test_simple(self):
        self.assertEqual("urn:x-skosprovider:typologie:1", self.urigen.generate(id=1))

    def test_missing_argument(self):
        self.assertRaises(KeyError, self.urigen.generate, type="set")


class DefaultConceptSchemeUrnGeneratorTest(unittest.TestCase):
    def setUp(self):
        self.urigen = DefaultConceptSchemeUrnGenerator()

    def tearDown(self):
        del self.urigen

    def test_simple(self):
        self.assertEqual(
            "urn:x-skosprovider:typologie", self.urigen.generate(id="TYPOLOGIE")
        )

    def test_missing_argument(self):
        self.assertRaises(KeyError, self.urigen.generate)


class TypedUrnGeneratorTest(unittest.TestCase):
    def setUp(self):
        self.urigen = TypedUrnGenerator("typologie")

    def tearDown(self):
        del self.urigen

    def test_concept(self):
        self.assertEqual(
            "urn:x-skosprovider:typologie:concept:1",
            self.urigen.generate(type="concept", id=1),
        )

    def test_collection(self):
        self.urigen = TypedUrnGenerator("typologie")
        self.assertEqual(
            "urn:x-skosprovider:typologie:collection:7000",
            self.urigen.generate(type="collection", id=7000),
        )

    def test_invalid_type(self):
        self.assertRaises(ValueError, self.urigen.generate, type="set", id=1)
