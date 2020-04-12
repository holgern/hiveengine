from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
import unittest
from hiveengine.tokens import Tokens


class Testcases(unittest.TestCase):
    def test_tokens(self):
        tokens = Tokens()
        self.assertTrue(tokens is not None)
        self.assertTrue(len(tokens) > 0)
