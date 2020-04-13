from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
import sys
from datetime import datetime, timedelta, date
import time
import json
from timeit import default_timer as timer
import logging
import decimal
from hiveengine.api import Api
from hiveengine.tokens import Tokens
from hiveengine.tokenobject import Token
from hiveengine.wallet import Wallet
from hiveengine.exceptions import (TokenDoesNotExists, TokenNotInWallet, InsufficientTokenAmount, InvalidTokenAmount)
from beem.instance import shared_steem_instance
from beem.account import Account


class Market(list):
    """ Access the hive-engine market

        :param Steem steem_instance: Steem
               instance
    """
    def __init__(self, api=None, steem_instance=None):
        if api is None:
            self.api = Api()
        else:
            self.api = api        
        self.steem = steem_instance or shared_steem_instance()
        self.tokens = Tokens(api=self.api)
        self.ssc_id = "ssc-mainnet-hive"
        self.refresh()

    def refresh(self):
        super(Market, self).__init__(self.get_metrics())

    def set_id(self, ssc_id):
        """Sets the ssc id (default is ssc-mainnet-hive)"""
        self.ssc_id = ssc_id

    def get_metrics(self):
        """Returns all token within the wallet as list"""
        metrics = self.api.find("market", "metrics", query={})
        return metrics

    def get_buy_book(self, symbol, account=None, limit=100, offset=0):
        """Returns the buy book for a given symbol. When account is set,
            the order book from the given account is shown.
        """
        if self.tokens.get_token(symbol) is None:
            raise TokenDoesNotExists("%s does not exists" % symbol)
        if account is None:
            buy_book = self.api.find("market", "buyBook", query={"symbol": symbol.upper()}, limit=limit, offset=offset)
        else:
            buy_book = self.api.find("market", "buyBook", query={"symbol": symbol.upper(), "account": account}, limit=limit, offset=offset)
        return buy_book

    def get_sell_book(self, symbol, account=None, limit=100, offset=0):
        """Returns the sell book for a given symbol. When account is set,
            the order book from the given account is shown.
        """        
        if self.tokens.get_token(symbol) is None:
            raise TokenDoesNotExists("%s does not exists" % symbol)
        if account is None:
            sell_book = self.api.find("market", "sellBook", query={"symbol": symbol.upper()}, limit=limit, offset=offset)
        else:
            sell_book = self.api.find("market", "sellBook", query={"symbol": symbol.upper(), "account": account}, limit=limit, offset=offset)
        return sell_book

    def get_trades_history(self, symbol, account=None, limit=30, offset=0):
        """Returns the trade history for a given symbol. When account is set,
            the trade history from the given account is shown.
        """        
        if self.tokens.get_token(symbol) is None:
            raise TokenDoesNotExists("%s does not exists" % symbol)
        if account is None:
            trades_history = self.api.find("market", "tradesHistory", query={"symbol": symbol.upper()}, limit=limit, offset=offset)
        else:
            trades_history = self.api.find("market", "tradesHistory", query={"symbol": symbol.upper(), "account": account}, limit=limit, offset=offset)
        return trades_history

    def withdraw(self, account, amount):
        """Widthdraw SWAP.HIVE to account as HIVE.

            :param str account: account name
            :param float amount: Amount to withdraw

            Withdraw example:

            .. code-block:: python

                from hiveengine.market import Market
                from beem import Steem
                active_wif = "5xxxx"
                stm = Steem(keys=[active_wif])
                market = Market(steem_instance=stm)
                market.withdraw("test", 1)
        """
        wallet = Wallet(account, api=self.api, steem_instance=self.steem)
        token_in_wallet = wallet.get_token("SWAP.HIVE")
        if token_in_wallet is None:
            raise TokenNotInWallet("%s is not in wallet." % "SWAP.HIVE")
        if float(token_in_wallet["balance"]) < float(amount):
            raise InsufficientTokenAmount("Only %.3f in wallet" % float(token_in_wallet["balance"]))
        token = Token("SWAP.HIVE", api=self.api)
        quant_amount = token.quantize(amount)
        if quant_amount <= decimal.Decimal("0"):
            raise InvalidTokenAmount("Amount to transfer is below token precision of %d" % token["precision"])        
        contract_payload = {"quantity":str(quant_amount)}
        json_data = {"contractName":"hivepegged","contractAction":"withdraw",
                     "contractPayload":contract_payload}
        assert self.steem.is_hive
        tx = self.steem.custom_json(self.ssc_id, json_data, required_auths=[account])
        return tx

    def deposit(self, account, amount):
        """Deposit HIVE to market in exchange for SWAP.HIVE.

            :param str account: account name
            :param float amount: Amount to deposit

            Deposit example:

            .. code-block:: python

                from hiveengine.market import Market
                from beem import Steem
                active_wif = "5xxxx"
                stm = Steem(keys=[active_wif])
                market = Market(steem_instance=stm)
                market.deposit("test", 1)
        """
        acc = Account(account, steem_instance=self.steem)
        steem_balance = acc.get_balance("available", "HIVE")
        if float(steem_balance) < float(amount):
            raise InsufficientTokenAmount("Only %.3f in wallet" % float(steem_balance))
        json_data = '{"id":"' + self.ssc_id + '","json":{"contractName":"hivepegged","contractAction":"buy","contractPayload":{}}}'
        tx = acc.transfer("honey-swap", amount, "HIVE", memo=json_data)
        return tx

    def buy(self, account, amount, symbol, price):
        """Buy token for given price.

            :param str account: account name
            :param float amount: Amount to withdraw
            :param str symbol: symbol
            :param float price: price

            Buy example:

            .. code-block:: python

                from hiveengine.market import Market
                from beem import Steem
                active_wif = "5xxxx"
                stm = Steem(keys=[active_wif])
                market = Market(steem_instance=stm)
                market.buy("test", 1, "BEE", 0.95)
        """
        wallet = Wallet(account, api=self.api, steem_instance=self.steem)
        token_in_wallet = wallet.get_token("SWAP.HIVE")
        if token_in_wallet is None:
            raise TokenNotInWallet("%s is not in wallet." % "SWAP.HIVE")
        if float(token_in_wallet["balance"]) < float(amount) * float(price):
            raise InsufficientTokenAmount("Only %.3f in wallet" % float(token_in_wallet["balance"]))

        token = Token(symbol, api=self.api)
        quant_amount = token.quantize(amount)
        if quant_amount <= decimal.Decimal("0"):
            raise InvalidTokenAmount("Amount to transfer is below token precision of %d" % token["precision"])           
        contract_payload = {"symbol": symbol.upper(), "quantity":str(quant_amount), "price": str(price)}
        json_data = {"contractName":"market","contractAction":"buy",
                     "contractPayload":contract_payload}
        assert self.steem.is_hive
        tx = self.steem.custom_json(self.ssc_id, json_data, required_auths=[account])
        return tx

    def sell(self, account, amount, symbol, price):
        """Sell token for given price.

            :param str account: account name
            :param float amount: Amount to withdraw
            :param str symbol: symbol
            :param float price: price

            Sell example:

            .. code-block:: python

                from hiveengine.market import Market
                from beem import Steem
                active_wif = "5xxxx"
                stm = Steem(keys=[active_wif])
                market = Market(steem_instance=stm)
                market.sell("test", 1, "BEE", 0.95)
        """
        wallet = Wallet(account, api=self.api, steem_instance=self.steem)
        token_in_wallet = wallet.get_token(symbol)
        if token_in_wallet is None:
            raise TokenNotInWallet("%s is not in wallet." % symbol)
        if float(token_in_wallet["balance"]) < float(amount):
            raise InsufficientTokenAmount("Only %.3f in wallet" % float(token_in_wallet["balance"]))
        
        token = Token(symbol, api=self.api)
        quant_amount = token.quantize(amount)
        if quant_amount <= decimal.Decimal("0"):
            raise InvalidTokenAmount("Amount to transfer is below token precision of %d" % token["precision"])        
        contract_payload = {"symbol": symbol.upper(), "quantity":str(quant_amount), "price": str(price)}
        json_data = {"contractName":"market","contractAction":"sell",
                     "contractPayload":contract_payload}
        assert self.steem.is_hive
        tx = self.steem.custom_json(self.ssc_id, json_data, required_auths=[account])
        return tx

    def cancel(self, account, order_type, order_id):
        """Cancel buy/sell order.

            :param str account: account name
            :param str order_type: sell or buy
            :param int order_id: order id

            Cancel example:

            .. code-block:: python

                from hiveengine.market import Market
                from beem import Steem
                active_wif = "5xxxx"
                stm = Steem(keys=[active_wif])
                market = Market(steem_instance=stm)
                market.sell("test", "sell", 12)
        """

        contract_payload = {"type": order_type, "id": order_id}
        json_data = {"contractName":"market","contractAction":"cancel",
                     "contractPayload":contract_payload}
        assert self.steem.is_hive
        tx = self.steem.custom_json(self.ssc_id, json_data, required_auths=[account])
        return tx
