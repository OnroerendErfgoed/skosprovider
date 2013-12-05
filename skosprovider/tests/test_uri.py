# -*- coding: utf-8 -*-

try:
    import unittest2 as unittest
except ImportError:  # pragma NO COVER
    import unittest  # noqa

from skosprovider.uri import (
    UriPatternGenerator,
    DefaultUrnGenerator
)


class UriPatternGeneratorTest(unittest.TestCase):

    def test_simple(self):
        urigen = UriPatternGenerator('http://id.example.com/%s')
        self.assertEqual(
            'http://id.example.com/1',
            urigen.generate(1)
        )

class DefaultUrnGeneratorTest(unittest.TestCase):

    def test_simple(self):
        urigen = DefaultUrnGenerator('typologie')
        self.assertEqual(
            'urn:x-skosprovider:typologie:1',
            urigen.generate(1)
        )
