0.2.2
-----
* fix hiveengine info for NFT symbols
* add min-hive parameter to nftsellbook
* add cheapest-only parameter to nftsellbook
* Read groupBy when grouping is empty in nftsellbook
* update_url, update_metadata, update_name, update_org_name, update_product_name, add_authorized_issuing_accounts,
  add_authorized_issuing_contracts, remove_authorized_issuing_accounts, remove_authorized_issuing_contracts,
  transfer_ownership, add_property, set_property_permissions, set_properties, set_group_by,
  update_property_definition, issue, issue_multiple, enable_delegation added to Nft
* New nft command to view properties of an NFT object
* Fix nfttrades command and lists a trades summary when now symbol was given
* Add interactive mode to nftsellbook for buy, cancel or change price

0.2.1
-----
* Fix nft_id list in nftbuy, nftcancel, nftchangeprice and nftsell

0.2.0
-----
* add NFT support (collection, nft, nftmarket, nfts)
* add NFT related commands to cli (collection, nftbuy, nftcancel, nftchangeprice, nftlist, nftopen, nftparams, nftsell, nftsellbook, nfttrades)

0.1.5
-----
* allow to cancel all buy / sell orders at once
* show all buy/sell order for an account

0.1.4
-----
* allow so transfer / stake / unstake / sell all tokens at once
* When no amount is given by transfer / stake / unstake the token balance is used
* new balance command

0.1.3
-----
* some bug-fixes

0.1.2
-----
* Fix stake and cancel unstake operation

0.1.1
-----
* Allow to add key directly without wallet in cli

0.1.0
-----
* Inital version
