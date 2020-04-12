import time
import logging
import json
from hiveengine.api import Api
from beem.block import Block
log = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


if __name__ == "__main__":
    api = Api()
    latest_block = api.get_latest_block_info()

    scan_token = ['BTC']
    print("Scanning all blocks from 0 to %d..." % latest_block['blockNumber'])
    steemp_payments = []
    
    for block_num in range(14500, latest_block['blockNumber']):
        block = api.get_block_info(block_num)
        if block_num % 1000 == 0:
            print("%.2f %%" % (block["blockNumber"]/latest_block['blockNumber'] * 100))
        for trx in block["transactions"]:
            
            if trx["contract"] not in ['market']:
                continue
            if trx["action"] not in ['buy', 'sell']:
                continue

            
            logs = json.loads(trx["logs"])
            sender = trx["sender"]
            payload = json.loads(trx["payload"])
            contract = trx["contract"]
            action = trx["action"]            
            
            if action == "sell":
                if "events" not in logs:
                    continue
                elif len(logs["events"]) == 1:
                    continue
                else:
                    token_found = False
                    for transfer in logs["events"]:
                        if transfer["data"]["symbol"] in scan_token:
                            token_found = True
                    if token_found:
                        steem_block = Block(block["refSteemBlockNumber"])
                        print("%d (%s) - %s:" % (block["blockNumber"], steem_block.json()["timestamp"], trx['transactionId']))
                        print("%s sold %s %s for %s" % (trx["sender"], payload["quantity"], payload["symbol"], payload["price"]))
                        for transfer in logs["events"]:
                            print("    - %s transfers %s %s to %s" % (transfer["data"]["from"], transfer["data"]["quantity"], transfer["data"]["symbol"], transfer["data"]["to"]))                    
                                
            elif action == "buy":
                if "events" not in logs:
                    continue
                elif len(logs["events"]) == 1:
                    continue
                else:
                    token_found = False
                    for transfer in logs["events"]:
                        if transfer["data"]["symbol"] in scan_token:
                            token_found = True
                    if token_found:
                        steem_block = Block(block["refSteemBlockNumber"])
                        print("%d (%s) - %s" % (block["blockNumber"], steem_block.json()["timestamp"], trx['transactionId']))
                        print("%s bought %s %s for %s" % (trx["sender"], payload["quantity"], payload["symbol"], payload["price"]))
                        for transfer in logs["events"]:
                            print("    - %s transfers %s %s to %s" % (transfer["data"]["from"], transfer["data"]["quantity"], transfer["data"]["symbol"], transfer["data"]["to"]))
                
        