from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
from builtins import range
from builtins import super
import unittest
from hiveengine.rpc import RPC


class Testcases(unittest.TestCase):
    def test_rpc_blockchain(self):
        rpc = RPC()
        result = rpc.getLatestBlockInfo(endpoint="blockchain")
        self.assertTrue(len(result) > 0)

    def test_rpc_contract(self):
        rpc = RPC()
        result = rpc.getContract({"name": "token"}, endpoint="contracts")
        self.assertTrue(len(result) > 0)
