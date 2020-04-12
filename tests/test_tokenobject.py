from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
import unittest
from hiveengine.tokenobject import Token


class Testcases(unittest.TestCase):
    def test_token(self):
        eng = Token("BEE")
        self.assertTrue(eng is not None)
        self.assertTrue(eng["symbol"] == "BEE")
