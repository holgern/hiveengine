from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
from hiveengine.api import Api
from hiveengine.exceptions import TokenDoesNotExists
import decimal


class Token(dict):
    """ hive-engine token dict

        :param str token: Name of the token
    """
    def __init__(self, symbol, api=None):
        if api is None:
            self.api = Api()
        else:
            self.api = api
        if isinstance(symbol, dict):
            self.symbol = symbol["symbol"]
            super(Token, self).__init__(symbol)
        else:
            self.symbol = symbol.upper()
            self.refresh()

    def refresh(self):
        info = self.get_info()
        if info is None:
            raise TokenDoesNotExists("Token %s does not exists!" % self.symbol)
        super(Token, self).__init__(info)

    def quantize(self, amount):
        """Round down a amount using the token precision and returns a Decimal object"""
        amount = decimal.Decimal(amount)
        places = decimal.Decimal(10) ** (-self["precision"])
        return amount.quantize(places, rounding=decimal.ROUND_DOWN)

    def get_info(self):
        """Returns information about the token"""
        token = self.api.find_one("tokens", "tokens", query={"symbol": self.symbol})
        if len(token) > 0:
            return token[0]
        else:
            return token

    def get_holder(self, limit=1000, offset=0):
        """Returns all token holders"""
        holder = self.api.find("tokens", "balances", query={"symbol": self.symbol}, limit=limit, offset=offset)
        return holder

    def get_market_info(self):
        """Returns market information"""
        metrics = self.api.find_one("market", "metrics", query={"symbol": self.symbol})
        if len(metrics) > 0:
            return metrics[0]
        else:
            return metrics

    def get_buy_book(self, limit=100, offset=0):
        """Returns the buy book"""
        holder = self.api.find("market", "buyBook", query={"symbol": self.symbol}, limit=limit, offset=offset)
        return holder

    def get_sell_book(self, limit=100, offset=0):
        """Returns the sell book"""
        holder = self.api.find("market", "sellBook", query={"symbol": self.symbol}, limit=limit, offset=offset)
        return holder
