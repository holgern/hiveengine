from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
import sys
from datetime import datetime, timedelta, date
import time
import io
import json
import requests
from timeit import default_timer as timer
import logging
import decimal
from hiveengine.api import Api
from hiveengine.tokenobject import Token
from hiveengine.exceptions import (TokenDoesNotExists, TokenNotInWallet, InsufficientTokenAmount, TokenIssueNotPermitted, MaxSupplyReached, InvalidTokenAmount)
from beem.instance import shared_blockchain_instance
from beem.account import Account


class Wallet(list):
    """ Access the steem-engine wallet

        :param str account: Name of the account
        :param Hive blockchain_instance: Hive
               instance
               
        Wallet example:

            .. code-block:: python

                from hiveengine.wallet import Wallet
                wallet = Wallet("test")
                print(wallet)

    """
    def __init__(self, account, api=None, blockchain_instance=None, steem_instance=None):
        if api is None:
            self.api = Api()
        else:
            self.api = api
        self.ssc_id = "ssc-mainnet-hive"
        self.blockchain = blockchain_instance or steem_instance or shared_blockchain_instance()
        check_account = Account(account, blockchain_instance=self.blockchain)
        self.account = check_account["name"]
        self.refresh()

    def refresh(self):
        super(Wallet, self).__init__(self.get_balances())

    def set_id(self, ssc_id):
        """Sets the ssc id (default is ssc-mainnet-hive)"""
        self.ssc_id = ssc_id

    def get_balances(self):
        """Returns all token within the wallet as list"""
        balances = self.api.find("tokens", "balances", query={"account": self.account})
        return balances

    def change_account(self, account):
        """Changes the wallet account"""
        check_account = Account(account, blockchain_instance=self.blockchain)
        self.account = check_account["name"]
        self.refresh()

    def get_token(self, symbol):
        """Returns a token from the wallet. Is None when not available."""
        for token in self:
            if token["symbol"].lower() == symbol.lower():
                return token
        return None

    def transfer(self, to, amount, symbol, memo=""):
        """Transfer a token to another account.

            :param str to: Recipient
            :param float amount: Amount to transfer
            :param str symbol: Token to transfer
            :param str memo: (optional) Memo


            Transfer example:

            .. code-block:: python

                from hiveengine.wallet import Wallet
                from beem import Steem
                active_wif = "5xxxx"
                stm = Steem(keys=[active_wif])
                wallet = Wallet("test", blockchain_instance=stm)
                wallet.transfer("test1", 1, "BEE", "test")
        """
        token_in_wallet = self.get_token(symbol)
        if token_in_wallet is None:
            raise TokenNotInWallet("%s is not in wallet." % symbol)
        if float(token_in_wallet["balance"]) < float(amount):
            raise InsufficientTokenAmount("Only %.3f in wallet" % float(token_in_wallet["balance"]))
        token = Token(symbol, api=self.api)
        quant_amount = token.quantize(amount)
        if quant_amount <= decimal.Decimal("0"):
            raise InvalidTokenAmount("Amount to transfer is below token precision of %d" % token["precision"])
        check_to = Account(to, blockchain_instance=self.blockchain)
        contract_payload = {"symbol":symbol.upper(),"to":to,"quantity":str(quant_amount),"memo":memo}
        json_data = {"contractName":"tokens","contractAction":"transfer",
                     "contractPayload":contract_payload}
        assert self.blockchain.is_hive
        tx = self.blockchain.custom_json(self.ssc_id, json_data, required_auths=[self.account])
        return tx

    def stake(self, amount, symbol, receiver=None):
        """Stake a token.

            :param float amount: Amount to stake
            :param str symbol: Token to stake

            Stake example:

            .. code-block:: python

                from hiveengine.wallet import Wallet
                from beem import Steem
                active_wif = "5xxxx"
                stm = Steem(keys=[active_wif])
                wallet = Wallet("test", blockchain_instance=stm)
                wallet.stake(1, "BEE")
        """
        token_in_wallet = self.get_token(symbol)
        if token_in_wallet is None:
            raise TokenNotInWallet("%s is not in wallet." % symbol)
        if float(token_in_wallet["balance"]) < float(amount):
            raise InsufficientTokenAmount("Only %.3f in wallet" % float(token_in_wallet["balance"]))
        token = Token(symbol, api=self.api)
        quant_amount = token.quantize(amount)
        if quant_amount <= decimal.Decimal("0"):
            raise InvalidTokenAmount("Amount to stake is below token precision of %d" % token["precision"])
        if receiver is None:
            receiver = self.account
        else:
            _ = Account(receiver, blockchain_instance=self.blockchain)
        contract_payload = {"symbol":symbol.upper(),"to": receiver, "quantity":str(quant_amount)}
        json_data = {"contractName":"tokens","contractAction":"stake",
                     "contractPayload":contract_payload}
        assert self.blockchain.is_hive
        tx = self.blockchain.custom_json(self.ssc_id, json_data, required_auths=[self.account])
        return tx

    def unstake(self, amount, symbol):
        """Unstake a token.

            :param float amount: Amount to unstake
            :param str symbol: Token to unstake

            Unstake example:

            .. code-block:: python

                from hiveengine.wallet import Wallet
                from beem import Steem
                active_wif = "5xxxx"
                stm = Steem(keys=[active_wif])
                wallet = Wallet("test", blockchain_instance=stm)
                wallet.unstake(1, "BEE")
        """
        token_in_wallet = self.get_token(symbol)
        if token_in_wallet is None:
            raise TokenNotInWallet("%s is not in wallet." % symbol)
        if "stake" not in token_in_wallet:
            raise InsufficientTokenAmount("Token cannot be unstaked")
        if float(token_in_wallet["stake"]) < float(amount):
            raise InsufficientTokenAmount("Only %.3f are staked in the wallet" % float(token_in_wallet["stake"]))
        token = Token(symbol, api=self.api)
        quant_amount = token.quantize(amount)
        if quant_amount <= decimal.Decimal("0"):
            raise InvalidTokenAmount("Amount to stake is below token precision of %d" % token["precision"])
        contract_payload = {"symbol":symbol.upper(),"quantity":str(quant_amount)}
        json_data = {"contractName":"tokens","contractAction":"unstake",
                     "contractPayload":contract_payload}
        assert self.blockchain.is_hive
        tx = self.blockchain.custom_json(self.ssc_id, json_data, required_auths=[self.account])
        return tx

    def cancel_unstake(self, trx_id):
        """Cancel unstaking a token.

            :param str trx_id: transaction id in which the tokan was unstaked

            Cancel unstake example:

            .. code-block:: python

                from hiveengine.wallet import Wallet
                from beem import Steem
                active_wif = "5xxxx"
                stm = Steem(keys=[active_wif])
                wallet = Wallet("test", blockchain_instance=stm)
                wallet.stake("cf39ecb8b846f1efffb8db526fada21a5fcf41c3")
        """
        contract_payload = {"txID":trx_id}
        json_data = {"contractName":"tokens","contractAction":"cancelUnstake",
                     "contractPayload":contract_payload}
        assert self.blockchain.is_hive
        tx = self.blockchain.custom_json(self.ssc_id, json_data, required_auths=[self.account])
        return tx

    def issue(self, to, amount, symbol):
        """Issues a specific token amount.

            :param str to: Recipient
            :param float amount: Amount to issue
            :param str symbol: Token to issue


            Issue example:

            .. code-block:: python

                from hiveengine.wallet import Wallet
                from beem import Steem
                active_wif = "5xxxx"
                stm = Steem(keys=[active_wif])
                wallet = Wallet("test", blockchain_instance=stm)
                wallet.issue(1, "my_token")
        """
        token = Token(symbol, api=self.api)
        if token["issuer"] != self.account:
            raise TokenIssueNotPermitted("%s is not the issuer of token %s" % (self.account, symbol))
        
        if token["maxSupply"] == token["supply"]:
            raise MaxSupplyReached("%s has reached is maximum supply of %d" % (symbol, token["maxSupply"]))
        quant_amount = token.quantize(amount)
        if quant_amount <= decimal.Decimal("0"):
            raise InvalidTokenAmount("Amount to issue is below token precision of %d" % token["precision"])        
        check_to = Account(to, blockchain_instance=self.blockchain)
        contract_payload = {"symbol":symbol.upper(),"to":to,"quantity":str(quant_amount)}
        json_data = {"contractName":"tokens","contractAction":"issue",
                     "contractPayload":contract_payload}
        assert self.blockchain.is_hive
        tx = self.blockchain.custom_json(self.ssc_id, json_data, required_auths=[self.account])
        return tx

    def get_history(self, symbol, limit=1000, offset=0):
        """Returns the transfer history of a token"""
        return self.api.get_history(self.account, symbol, limit, offset)

    def get_buy_book(self, symbol=None, limit=100, offset=0):
        """Returns the buy book for the wallet account. When symbol is set,
            the order book from the given token is shown.
        """
        if symbol is None:
            buy_book = self.api.find("market", "buyBook", query={"account": self.account}, limit=limit, offset=offset)
        else:
            buy_book = self.api.find("market", "buyBook", query={"symbol": symbol, "account": self.account}, limit=limit, offset=offset)
        return buy_book

    def get_sell_book(self, symbol=None, limit=100, offset=0):
        """Returns the sell book for the wallet account. When symbol is set,
            the order book from the given token is shown.
        """        
        if symbol is None:
            sell_book = self.api.find("market", "sellBook", query={"account": self.account}, limit=limit, offset=offset)
        else:
            sell_book = self.api.find("market", "sellBook", query={"symbol": symbol, "account": self.account}, limit=limit, offset=offset)
        return sell_book
