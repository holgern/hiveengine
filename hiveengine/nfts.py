from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
from hiveengine.api import Api
from hiveengine.nft import Nft


class Nfts(list):
    """ Access the Hive-engine Nfts
    """
    def __init__(self, api=None, **kwargs):
        if api is None:
            self.api = Api()
        else:
            self.api = api        
        self.refresh()

    def refresh(self):
        super(Nfts, self).__init__(self.get_nft_list())

    def get_nft_list(self):
        """Returns all available nft as list"""
        tokens = self.api.find_all("nft", "nfts", query={})
        return tokens

    def get_nft_params(self):
        """Returns all available nft as list"""
        tokens = self.api.find_one("nft", "params", query={})
        if isinstance(tokens, list) and len(tokens) > 0:
            tokens = tokens[0]
        return tokens

    def get_symbol_list(self):
        symbols = []
        for nft in self:
            symbols.append(nft["symbol"])
        return symbols

    def get_nft(self, nft):
        """Returns Token from given nft symbol. Is None
            when nft does not exists.
        """
        for t in self:
            if t["symbol"].lower() == nft.lower():
                return Nft(t, api=self.api)
        return None

