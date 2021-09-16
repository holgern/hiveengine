from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
import unittest
from hiveengine.api import Api


class Testcases(unittest.TestCase):
    def test_api(self):
        api = Api()
        result = api.get_latest_block_info()
        self.assertTrue(len(result) > 0)

        result = api.get_block_info(1910)
        self.assertTrue(len(result) > 0)

        result = api.get_transaction_info("78aea60cdc4477cdf9437d8224e34c6033499169")
        self.assertTrue(len(result) > 0)

        result = api.get_contract("tokens")
        self.assertTrue(len(result) > 0)

        result = api.find("tokens", "tokens")
        self.assertTrue(len(result) > 0)

        result = api.find_one("tokens", "tokens")
        self.assertTrue(len(result) > 0)

        result = api.get_history("holger80", "FOODIE")
        self.assertTrue(len(result) > 0)
