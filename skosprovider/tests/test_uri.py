# -*- coding: utf-8 -*-

try:
    import unittest2 as unittest
except ImportError:  # pragma NO COVER
    import unittest  # noqa

from skosprovider.uri import (
    UriPatternGenerator,
    DefaultUrnGenerator,
    DefaultConceptSchemeUrnGenerator,
    TypedUrnGenerator
)


class UriPatternGeneratorTest(unittest.TestCase):

    def test_simple(self):
        urigen = UriPatternGenerator('http://id.example.com/%s')
        self.assertEqual(
            'http://id.example.com/1',
            urigen.generate(id=1)
        )


class DefaultUrnGeneratorTest(unittest.TestCase):

    def setUp(self):
        self.urigen = DefaultUrnGenerator('typologie')

    def tearDown(self):
        del self.urigen

    def test_simple(self):
        self.assertEqual(
            'urn:x-skosprovider:typologie:1',
            self.urigen.generate(id=1)
        )

    def test_missing_argument(self):
        self.assertRaises(KeyError, self.urigen.generate, type='set')


class DefaultConceptSchemeUrnGeneratorTest(unittest.TestCase):

    def setUp(self):
        self.urigen = DefaultConceptSchemeUrnGenerator()

    def tearDown(self):
        del self.urigen

    def test_simple(self):
        self.assertEqual(
            'urn:x-skosprovider:typologie',
            self.urigen.generate(id='TYPOLOGIE')
        )

    def test_missing_argument(self):
        self.assertRaises(KeyError, self.urigen.generate)


class TypedUrnGeneratorTest(unittest.TestCase):

    def setUp(self):
        self.urigen = TypedUrnGenerator('typologie')

    def tearDown(self):
        del self.urigen

    def test_concept(self):
        self.assertEqual(
            'urn:x-skosprovider:typologie:concept:1',
            self.urigen.generate(type='concept', id=1)
        )

    def test_collection(self):
        self.urigen = TypedUrnGenerator('typologie')
        self.assertEqual(
            'urn:x-skosprovider:typologie:collection:7000',
            self.urigen.generate(type='collection', id=7000)
        )

    def test_invalid_type(self):
        self.assertRaises(ValueError, self.urigen.generate, type='set', id=1)
