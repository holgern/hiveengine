# hiveengine
Python tools for obtaining and processing hive engine tokens

[![Build Status](https://travis-ci.org/holgern/hiveengine.svg?branch=master)](https://travis-ci.org/holgern/hiveengine)

## Installation
```
pip install hiveengine
```


## Commands
Get the latest block of the sidechain
```
from hiveengine.api import Api
api = Api()
print(api.get_latest_block_info())
```

Get the block with the specified block number of the sidechain
```
from hiveengine.api import Api
api = Api()
print(api.get_block_info(1910))
```

Retrieve the specified transaction info of the sidechain
```
from hiveengine.api import Api
api = Api()
print(api.get_transaction_info("e6c7f351b3743d1ed3d66eb9c6f2c102020aaa5d"))
```

Get the contract specified from the database
```
from hiveengine.api import Api
api = Api()
print(api.get_contract("tokens"))
```

Get an array of objects that match the query from the table of the specified contract
```
from hiveengine.api import Api
api = Api()
print(api.find("tokens", "tokens"))
```

Get the object that matches the query from the table of the specified contract
```
from hiveengine.api import Api
api = Api()
print(api.find_one("tokens", "tokens"))
```

Get the transaction history for an account and a token
```
from hiveengine.api import Api
api = Api()
print(api.get_history("holger80", "FOODIE"))
```
## Token transfer
```
from beem import Steem
from hiveengine.wallet import Wallet
stm = Steem(keys=["5xx"])
wallet = Wallet("test_user", steem_instance=stm)
wallet.transfer("test1",1,"TST", memo="This is a test")
```
## Buy/Sell
### Create a buy order
```
from beem import Steem
from hiveengine.market import Market
stm = Steem(keys=["5xx"])
m=Market(steem_instance=stm)
m.buy("test_user", 1, "TST", 9.99)
```
### Create a sell order

```
from beem import Steem
from hiveengine.market import Market
stm = Steem(keys=["5xx"])
m=Market(steem_instance=stm)
m.sell("test_user", 1, "TST", 9.99)
```
### Cancel a buy order
```
from beem import Steem
from hiveengine.market import Market
stm = Steem(keys=["5xx"])
m=Market(steem_instance=stm)
open_buy_orders = m.get_buy_book("TST", "test_user")
m.cancel("test_user", "buy", open_buy_orders[0]["_id"])
```
### Cancel a sell order
```
from beem import Steem
from hiveengine.market import Market
stm = Steem(keys=["5xx"])
m=Market(steem_instance=stm)
open_sell_orders = m.get_sell_book("TST", "test_user")
m.cancel("test_user", "sell", open_sell_orders[0]["_id"])
```
### Deposit Steem
```
from beem import Steem
from hiveengine.market import Market
stm = Steem(keys=["5xx"])
m=Market(steem_instance=stm)
m.deposit("test_user", 10)
```
### Withdrawal
```
from beem import Steem
from hiveengine.market import Market
stm = Steem(keys=["5xx"])
m=Market(steem_instance=stm)
m.withdraw("test_user", 10)
```
