from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
import sys
from datetime import datetime, timedelta
import time
import io
import logging
from beem import Steem
from hiveengine.wallet import Wallet
from beembase import transactions, operations
log = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


if __name__ == "__main__":
    stm = Steem()
    stm.wallet.unlock(pwd="wallet_pass")
    wallet = Wallet("beembot", steem_instance=stm)
    dragon_token = wallet.get_token("DRAGON")
    if dragon_token is not None and float(dragon_token["balance"]) >= 0.01:
        print("balance %.2f" % float(dragon_token["balance"]))
        print(wallet.transfer("holger80", 0.01, "DRAGON", "test"))
    else:
        print("Could not sent")
    time.sleep(15)
    wallet.refresh()
    dragon_token = wallet.get_token("DRAGON")
    print("new balance %.2f" % float(dragon_token["balance"]))

    