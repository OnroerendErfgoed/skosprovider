# -*- coding: utf-8 -*-
import unittest
from skosprovider.exceptions import ProviderUnavailableException


class ExceptionsTest(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_provider_unavailable_exception(self):
        exc = ProviderUnavailableException("test error")
        self.assertEqual("test error", repr(exc))