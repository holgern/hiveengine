from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
import sys
from datetime import datetime, timedelta, date
import time
import json
import requests
from timeit import default_timer as timer
import logging
from .rpc import RPC


class Api(object):
    """ Access the hive-engine API
    """
    def __init__(self, url=None, rpcurl=None, user=None, password=None, **kwargs):
        if url is None:
            self.url = 'https://api.hive-engine.com/'
        else:
            self.url = url
        if url is not None and rpcurl is None:
            self.rpc = RPC(url=url)
        else:
            self.rpc = RPC(url=rpcurl)

    def get_history(self, account, symbol, limit=1000, offset=0):
        """"Get the transaction history for an account and a token"""
        response = requests.get("https://history.hive-engine.com/accountHistory?account=%s&limit=%d&offset=%d&symbol=%s" % (account, limit, offset, symbol))
        cnt2 = 0
        while response.status_code != 200 and cnt2 < 10:
            response = requests.get("https://history.hive-engine.com/accountHistory?account=%s&limit=%d&offset=%d&symbol=%s" % (account, limit, offset, symbol))
            cnt2 += 1
        return response.json()

    def get_latest_block_info(self):
        """get the latest block of the sidechain"""
        ret = self.rpc.getLatestBlockInfo(endpoint="blockchain")
        if isinstance(ret, list) and len(ret) == 1:
            return ret[0]
        else:
            return ret

    def get_status(self):
        """gets the status of the sidechain"""
        ret = self.rpc.getStatus(endpoint="blockchain")
        if isinstance(ret, list) and len(ret) == 1:
            return ret[0]
        else:
            return ret

    def get_block_info(self, blocknumber):
        """get the block with the specified block number of the sidechain"""
        ret = self.rpc.getBlockInfo({"blockNumber": blocknumber}, endpoint="blockchain")
        if isinstance(ret, list) and len(ret) == 1:
            return ret[0]
        else:
            return ret

    def get_transaction_info(self, txid):
        """Retrieve the specified transaction info of the sidechain"""
        ret = self.rpc.getTransactionInfo({"txid": txid}, endpoint="blockchain")
        if isinstance(ret, list) and len(ret) == 1:
            return ret[0]
        else:
            return ret

    def get_contract(self, contract_name):
        """ Get the contract specified from the database"""
        ret = self.rpc.getContract({"name": contract_name}, endpoint="contracts")
        if isinstance(ret, list) and len(ret) == 1:
            return ret[0]
        else:
            return ret

    def find_one(self, contract_name, table_name, query = {}):
        """Get the object that matches the query from the table of the specified contract"""
        ret = self.rpc.findOne({"contract": contract_name, "table": table_name, "query": query}, endpoint="contracts")
        return ret

    def find(self, contract_name, table_name, query = {}, limit=1000, offset=0, indexes=[]):
        """Get an array of objects that match the query from the table of the specified contract"""
        ret = self.rpc.find({"contract": contract_name, "table": table_name, "query": query,
                             "limit": limit, "offset": offset, "indexes": indexes}, endpoint="contracts")
        if isinstance(ret, list) and len(ret) == 1:
            return ret[0]
        else:
            return ret

