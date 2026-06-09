import unittest

import pytest


class DBTestCase(unittest.TestCase):
    @pytest.fixture(autouse=True)
    def init(self, session_maker, engine):
        self.session_maker = session_maker
        self.engine = engine
