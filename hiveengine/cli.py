# This Python file uses the following encoding: utf-8
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
from builtins import bytes, int, str
from beem import Steem
from beem.account import Account
from beem.nodelist import NodeList
from beem.utils import formatTimeString, addTzInfo
from beem.blockchain import Blockchain
from hiveengine.api import Api
from hiveengine.tokens import Tokens
from hiveengine.tokenobject import Token
from hiveengine.market import Market
from hiveengine.wallet import Wallet
from prettytable import PrettyTable
import time
import json
import click
from click_shell import shell
import logging
import sys
import os
import io
import argparse
import re
import six
from beem.instance import set_shared_steem_instance, shared_steem_instance
from hiveengine.version import version as __version__
click.disable_unicode_literals_warning = True
log = logging.getLogger(__name__)
try:
    import keyring
    if not isinstance(keyring.get_keyring(), keyring.backends.fail.Keyring):
        KEYRING_AVAILABLE = True
    else:
        KEYRING_AVAILABLE = False
except ImportError:
    KEYRING_AVAILABLE = False


def unlock_wallet(stm, password=None):
    if stm.unsigned and stm.nobroadcast:
        return True
    password_storage = stm.config["password_storage"]
    if not password and KEYRING_AVAILABLE and password_storage == "keyring":
        password = keyring.get_password("beem", "wallet")
    if not password and password_storage == "environment" and "UNLOCK" in os.environ:
        password = os.environ.get("UNLOCK")
    if bool(password):
        stm.wallet.unlock(password)
    else:
        password = click.prompt("Password to unlock wallet", confirmation_prompt=False, hide_input=True)
        stm.wallet.unlock(password)

    if stm.wallet.locked():
        if password_storage == "keyring" or password_storage == "environment":
            print("Wallet could not be unlocked with %s!" % password_storage)
            password = click.prompt("Password to unlock wallet", confirmation_prompt=False, hide_input=True)
            if bool(password):
                unlock_wallet(stm, password=password)
                if not stm.wallet.locked():
                    return True
        else:
            print("Wallet could not be unlocked!")
        return False
    else:
        print("Wallet Unlocked!")
        return True

@shell(prompt='hiveengine> ', intro='Starting hiveengine... (use help to list all commands)', chain=True)
# click.group(chain=True)
@click.option(
    '--verbose', '-v', default=3, help='Verbosity')
@click.version_option(version=__version__)
def cli(verbose):
    # Logging
    log = logging.getLogger(__name__)
    verbosity = ["critical", "error", "warn", "info", "debug"][int(
        min(verbose, 4))]
    log.setLevel(getattr(logging, verbosity.upper()))
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ch = logging.StreamHandler()
    ch.setLevel(getattr(logging, verbosity.upper()))
    ch.setFormatter(formatter)
    log.addHandler(ch)
    debug = verbose > 0
    pass


@cli.command()
@click.argument('objects', nargs=-1)
def info(objects):
    """ Show basic blockchain info

        General information about hive-engine, a block, an account, a token,
        and a transaction id
    """
    stm = None   
    api = Api()

    if not objects:
        latest_block = api.get_latest_block_info()
        tokens = Tokens()
        t = PrettyTable(["Key", "Value"])
        t.align = "l"
        t.add_row(["latest block number", latest_block["blockNumber"]])
        t.add_row(["latest hive block", latest_block["refHiveBlockNumber"]])
        t.add_row(["latest timestamp", latest_block["timestamp"]])
        t.add_row(["Number of created tokens", len(tokens)])
        print(t.get_string())
    for obj in objects:
        if re.match("^[0-9-]*$", obj):
            block_info = api.get_block_info(int(obj))
            print("Block info: %d" % (int(obj)))
            trx_nr = 0
            for trx in block_info["transactions"]:
                trx_nr += 1
                t = PrettyTable(["Key", "Value"])
                t.align = "l"
                t.add_row(["trx_nr", str(trx_nr)])
                t.add_row(["action", trx["action"]])
                t.add_row(["contract", trx["contract"]])
                t.add_row(["logs", json.dumps(json.loads(trx["logs"]), indent=4)])
                t.add_row(["payload", json.dumps(json.loads(trx["payload"]), indent=4)])
                t.add_row(["refHiveBlockNumber", trx["refHiveBlockNumber"]])
                t.add_row(["timestamp", block_info["timestamp"]])
                t.add_row(["sender", trx["sender"]])
                t.add_row(["transactionId", trx["transactionId"]])
                print(t.get_string())
        elif re.match("^[A-Z0-9\-\._]{1,16}$", obj):
            print("Token: %s" % obj)
            tokens = Tokens()
            token = tokens.get_token(obj)
            if token is None:
                print("Could not found token %s" % obj)
                return
            t = PrettyTable(["Key", "Value"])
            t.align = "l"
            metadata = json.loads(token["metadata"])
            for key in token:
                if key == "metadata":
                    if "url" in metadata:
                        t.add_row(["metadata_url", metadata["url"]])
                    if "icon" in metadata:
                        t.add_row(["metadata_icon", metadata["icon"]])
                    if "desc" in metadata:
                        t.add_row(["metadata_desc", metadata["desc"]])            
                else:
                    t.add_row([key, token[key]])
            market_info = token.get_market_info()
            if market_info is not None:
                for key in market_info:
                    if key in ["_id", "symbol"]:
                        continue
                    t.add_row([key, market_info[key]])
            print(t.get_string())
        elif re.match("^[a-zA-Z0-9\-\._]{2,16}$", obj):
            print("Token Wallet: %s" % obj)
            if stm is None:
                nodelist = NodeList()
                nodelist.update_nodes()
                stm = Steem(node=nodelist.get_hive_nodes())                
            wallet = Wallet(obj, steem_instance=stm)
            t = PrettyTable(["id", "symbol", "balance", "stake", "pendingUnstake", "delegationsIn", "delegationsOut", "pendingUndelegations"])
            t.align = "l"
            for token in wallet:
                if "stake" in token:
                    stake = token["stake"]
                else:
                    stake = "-"
                if "pendingUnstake" in token:
                    pendingUnstake = token["pendingUnstake"]
                else:
                    pendingUnstake = "-"
                t.add_row([token["_id"], token["symbol"], token["balance"], stake, pendingUnstake, token["delegationsIn"],
                           token["delegationsOut"], token["pendingUndelegations"]])
            print(t.get_string(sortby="id"))
        elif len(obj) == 40:
            print("Transaction Id: %s" % obj)
            trx = api.get_transaction_info(obj)
            if trx is None:
                print("trx_id: %s is not a valid hive-engine trx_id!" % obj)
                return
            payload = json.loads(trx["payload"])
            logs = json.loads(trx["logs"])
            t = PrettyTable(["Key", "Value"])
            t.align = "l"
            t.add_row(["blockNumber", str(trx["blockNumber"])])
            t.add_row(["action", trx["action"]])
            t.add_row(["contract", trx["contract"]])
            t.add_row(["logs", json.dumps(logs, indent=4)])
            t.add_row(["payload", json.dumps(payload, indent=4)])
            t.add_row(["refHiveBlockNumber", trx["refHiveBlockNumber"]])
            t.add_row(["sender", trx["sender"]])
            t.add_row(["transactionId", trx["transactionId"]])
            print(t.get_string())            


@cli.command()
@click.argument('symbol', nargs=1)
@click.option('--top', '-t', help='Show only the top n accounts', default=50)
def richlist(symbol, top):
    """ Shows the richlist of a token

    """
    token = Token(symbol)
    holder = token.get_holder()
    market_info = token.get_market_info()
    last_price = float(market_info["lastPrice"])
    sorted_holder = sorted(holder, key=lambda account: float(account["balance"]), reverse=True)
    t = PrettyTable(["Balance", "Account", "Value [HIVE]"])
    t.align = "l"
    for balance in sorted_holder[:int(top)]:
        t.add_row([balance["balance"], balance["account"], "%.3f" % (float(balance["balance"]) * last_price)])
    print(t.get_string())


@cli.command()
@click.argument('to', nargs=1)
@click.argument('amount', nargs=1)
@click.argument('token', nargs=1)
@click.argument('memo', nargs=1, required=False)
@click.option('--account', '-a', help='Transfer from this account')
def transfer(to, amount, token, memo, account):
    """Transfer a token"""
    stm = shared_steem_instance()
    if stm.rpc is not None:
        stm.rpc.rpcconnect()
    if not account:
        account = stm.config["default_account"]
    if not bool(memo):
        memo = ''
    if not unlock_wallet(stm):
        return
    wallet = Wallet(account, steem_instance=stm)
    tx = wallet.transfer(to, amount, token, memo)
    tx = json.dumps(tx, indent=4)
    print(tx)


@cli.command()
@click.argument('to', nargs=1)
@click.argument('amount', nargs=1)
@click.argument('token', nargs=1)
@click.option('--account', '-a', help='Transfer from this account')
def issue(to, amount, token, account):
    """Issue a token"""
    stm = shared_steem_instance()
    if stm.rpc is not None:
        stm.rpc.rpcconnect()
    if not account:
        account = stm.config["default_account"]
    if not unlock_wallet(stm):
        return
    wallet = Wallet(account, steem_instance=stm)
    tx = wallet.issue(to, amount, token)
    tx = json.dumps(tx, indent=4)
    print(tx)


@cli.command()
@click.argument('amount', nargs=1)
@click.argument('token', nargs=1)
@click.option('--account', '-a', help='Transfer from this account')
def stake(amount, token, account):
    """stake a token"""
    stm = shared_steem_instance()
    if stm.rpc is not None:
        stm.rpc.rpcconnect()
    if not account:
        account = stm.config["default_account"]
    if not unlock_wallet(stm):
        return
    wallet = Wallet(account, steem_instance=stm)
    tx = wallet.stake(amount, token)
    tx = json.dumps(tx, indent=4)
    print(tx)


@cli.command()
@click.argument('amount', nargs=1)
@click.argument('token', nargs=1)
@click.option('--account', '-a', help='Transfer from this account')
def unstake(amount, token, account):
    """unstake a token"""
    stm = shared_steem_instance()
    if stm.rpc is not None:
        stm.rpc.rpcconnect()
    if not account:
        account = stm.config["default_account"]
    if not unlock_wallet(stm):
        return
    wallet = Wallet(account, steem_instance=stm)
    tx = wallet.unstake(amount, token)
    tx = json.dumps(tx, indent=4)
    print(tx)


@cli.command()
@click.argument('trx_id', nargs=1)
@click.option('--account', '-a', help='Transfer from this account')
def cancel_unstake(amount, trx_id):
    """unstake a token"""
    stm = shared_steem_instance()
    if stm.rpc is not None:
        stm.rpc.rpcconnect()
    if not account:
        account = stm.config["default_account"]
    if not unlock_wallet(stm):
        return
    wallet = Wallet(account, steem_instance=stm)
    tx = wallet.cancel_unstake(trx_id)
    tx = json.dumps(tx, indent=4)
    print(tx)


@cli.command()
@click.argument('amount', nargs=1)
@click.option('--account', '-a', help='withdraw from this account')
def withdraw(amount, account):
    """Widthdraw SWAP.HIVE to account as HIVE."""
    stm = shared_steem_instance()
    if stm.rpc is not None:
        stm.rpc.rpcconnect()
    if not account:
        account = stm.config["default_account"]
    if not unlock_wallet(stm):
        return
    market = Market(steem_instance=stm)
    tx = market.withdraw(account, amount)
    tx = json.dumps(tx, indent=4)
    print(tx)


@cli.command()
@click.argument('amount', nargs=1)
@click.option('--account', '-a', help='withdraw from this account')
def deposit(amount, account):
    """Deposit HIVE to market in exchange for SWAP.HIVE."""
    stm = shared_steem_instance()
    if stm.rpc is not None:
        stm.rpc.rpcconnect()
    if not account:
        account = stm.config["default_account"]
    if not unlock_wallet(stm):
        return
    market = Market(steem_instance=stm)
    tx = market.deposit(account, amount)
    tx = json.dumps(tx, indent=4)
    print(tx)


@cli.command()
@click.argument('amount', nargs=1)
@click.argument('token', nargs=1)
@click.argument('price', nargs=1)
@click.option('--account', '-a', help='Buy with this account (defaults to "default_account")')
def buy(amount, token, price, account):
    """Put a buy-order for a token to the hive-engine market

    """
    stm = shared_steem_instance()
    if stm.rpc is not None:
        stm.rpc.rpcconnect()
    if account is None:
        account = stm.config["default_account"]
    market = Market(steem_instance=stm)
    if not unlock_wallet(stm):
        return
    tx = market.buy(account, amount, token, price)
    tx = json.dumps(tx, indent=4)
    print(tx)


@cli.command()
@click.argument('amount', nargs=1)
@click.argument('token', nargs=1)
@click.argument('price', nargs=1)
@click.option('--account', '-a', help='Buy with this account (defaults to "default_account")')
def sell(amount, token, price, account):
    """Put a sell-order for a token to the hive-engine market

    """
    stm = shared_steem_instance()
    if stm.rpc is not None:
        stm.rpc.rpcconnect()
    if account is None:
        account = stm.config["default_account"]
    market = Market(steem_instance=stm)
    if not unlock_wallet(stm):
        return
    tx = market.sell(account, amount, token, price)
    tx = json.dumps(tx, indent=4)
    print(tx)


@cli.command()
@click.argument('order_type', nargs=1)
@click.argument('order_id', nargs=1)
@click.option('--account', '-a', help='Buy with this account (defaults to "default_account")')
def cancel(order_type, order_id, account):
    """Cancel a buy/sell order
    
        order_type is either sell or buy
    """
    stm = shared_steem_instance()
    if stm.rpc is not None:
        stm.rpc.rpcconnect()
    if account is None:
        account = stm.config["default_account"]
    market = Market(steem_instance=stm)
    if not unlock_wallet(stm):
        return
    tx = market.cancel(account, order_type, int(order_id))
    tx = json.dumps(tx, indent=4)
    print(tx)


@cli.command()
@click.argument('token', nargs=1)
@click.option('--account', '-a', help='Buy with this account (defaults to "default_account")')
def buybook(token, account):
    """Returns the buy book for the given token

    """
    stm = shared_steem_instance()
    if stm.rpc is not None:
        stm.rpc.rpcconnect()
    market = Market(steem_instance=stm)
    buy_book = market.get_buy_book(token, account)
    sorted_buy_book = sorted(buy_book, key=lambda account: float(account["price"]), reverse=True)
    t = PrettyTable(["order_id", "account", "quantity", "price"])
    t.align = "l"
    for order in sorted_buy_book:
        t.add_row([order["_id"], order["account"], order["quantity"], order["price"]])
    print(t.get_string())    


@cli.command()
@click.argument('token', nargs=1)
@click.option('--account', '-a', help='Buy with this account (defaults to "default_account")')
def sellbook(token, account):
    """Returns the sell book for the given token
    """
    stm = shared_steem_instance()
    if stm.rpc is not None:
        stm.rpc.rpcconnect()
    market = Market(steem_instance=stm)
    sell_book = market.get_sell_book(token, account)
    sorted_sell_book = sorted(sell_book, key=lambda account: float(account["price"]), reverse=False)
    t = PrettyTable(["order_id", "account", "quantity", "price"])
    t.align = "l"
    for order in sorted_sell_book:
        t.add_row([order["_id"], order["account"], order["quantity"], order["price"]])
    print(t.get_string())  


if __name__ == "__main__":
    if getattr(sys, 'frozen', False):
        os.environ['SSL_CERT_FILE'] = os.path.join(sys._MEIPASS, 'lib', 'cert.pem')
        cli(sys.argv[1:])
    else:
        cli()
