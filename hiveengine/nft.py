from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
from hiveengine.api import Api
from hiveengine.tokenobject import Token
from hiveengine.exceptions import (NftDoesNotExists)


class Nft(dict):
    """ Access the hive-engine Nfts
    """
    def __init__(self, symbol, api=None):
        if api is None:
            self.api = Api()
        else:
            self.api = api
        if isinstance(symbol, dict):
            self.symbol = symbol["symbol"]
            super(Nft, self).__init__(symbol)
        else:
            self.symbol = symbol.upper()
            self.refresh()

    def refresh(self):
        info = self.get_info()
        if info is None:
            raise NftDoesNotExists("Nft %s does not exists!" % self.symbol)
        super(Nft, self).__init__(info)

    def get_info(self):
        """Returns information about the nft"""
        token = self.api.find_one("nft", "nfts", query={"symbol": self.symbol})
        if len(token) > 0:
            return token[0]
        else:
            return token

    @property
    def properties(self):
        return list(self["properties"].keys())

    @property
    def issuer(self):
        return self["issuer"]

    def get_property(self, property_name):
        """Returns all token properties"""
        return self.api.find_all("nft", "%sinstances" % self.symbol, query={"properties.name": property_name})

    def get_collection(self, account):
        """ Get NFT collection"""
        tokens = self.api.find_all("nft", "%sinstances" % self.symbol, query={"account": account})
        return tokens

    def get_id(self, _id):
        """ Get info about a token"""
        tokens = self.api.find_one("nft", "%sinstances" % self.symbol, query={"_id": _id})
        if len(tokens) > 0:
            return tokens[0]
        return tokens

    def get_trade_history(self, query={}, limit=-1, offset=0):
        """Returns market information
           :param dict query: can be priceSymbol, timestamp
        """
        if limit < 0 or limit > 1000:
            return self.api.find_all("nftmarket", "%stradesHistory" % self.symbol, query=query)
        else:
            return self.api.find("nftmarket", "%stradesHistory" % self.symbol, query=query, limit=limit, offset=offset)

    def get_open_interest(self, query={}, limit=-1, offset=0):
        """Returns open interests
           :param dict query: side, priceSymbol, grouping
        """
        if limit < 0 or limit > 1000:
            return self.api.find_all("nftmarket", "%sopenInterest" % self.symbol, query=query)
        else:
            return self.api.find("nftmarket", "%sopenInterest" % self.symbol, query=query, limit=limit, offset=offset)

    def get_sell_book(self, query={}, limit=-1, offset=0):
        """Returns the sell book
           :param dict query: can be ownedBy, account, nftId, grouping, priceSymbol 
        """
        if limit < 0 or limit > 1000:
            return self.api.find_all("nftmarket", "%ssellBook" % self.symbol, query=query)
        else:
            return self.api.find("nftmarket", "%ssellBook" % self.symbol, query=query, limit=limit, offset=offset)
