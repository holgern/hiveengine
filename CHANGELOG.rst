## 0.5.0
* Add stake, unstake, cancel_unstake to Wallet class
* Add stake, unstake, cancel_unstake to the command line tool
* Add stake and pendingUnstake to info from the commandline tool

## 0.4.6
* Allow to change the ssc id

## 0.4.5
* Propagate Api to all steemengine objects
* tsetnet can be used https://testapi.steem-engine.com/

## 0.4.4
* Fix URL for RPC object

## 0.4.3
* Change URL also in RPC object

## 0.4.2
* URL for steemengine API can be set
* Fix cancel for handling new buy/sell id

## 0.4.1
* Fix cancel order id (int)

## 0.4.0
* quantize added to Token class
* TokenDoesNotExists is raised in the Token class when token does not exists
* Exception InvalidTokenAmount is raised when amount to transfer or to issue is below precision
* new issue function added to wallet
* token precision is taken into account for transfer and issue
* TokenIssueNotPermitted is raised when an account which is not the token issuer tries to issue
* Add amount quantization to deposit, withdraw, buy and sell
* Add transfer, issue, withdraw, deposit, buy, sell, cancel, buybook, sellbook to CLI

## 0.3.1
* Fix circular dependency

## 0.3.0
* Token class added, allows to get information about markets, holder and the token itself
* CLI added for showing information about blocks, transaction, token and accounts
* more unit tests
* buy/sell book for account added

## 0.2.0
* Market, Tokens and Wallet class added
* Token transfer are possible
* Market buy/sell/cancel of token is possible
* deposit/withdrawel added

## 0.1.0
* Inital version
* Api class added