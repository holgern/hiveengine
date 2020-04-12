# This Python file uses the following encoding: utf-8
# (c) holger80
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
from beem import Steem
from beem.comment import Comment
from beem.nodelist import NodeList
from hiveengine.wallet import Wallet
import time


if __name__ == "__main__":
    nodelist = NodeList()
    nodelist.update_nodes()
    stm = Steem(node=nodelist.get_hive_nodes())
    
    
    # edit here
    upvote_account = "beembot"
    upvote_token = "DRAGON"
    token_weight_factor = 100 # multiply token amount to get weight
    min_token_amount = 0.01
    max_post_age_days = 3
    whitelist = [] # When empty, the whitelist is disabled
    blacklist_tags = [] # When empty, the tag blacklist is disabled
    reply_comment = "" # When empty, no reply comment is created
    only_main_posts = True
    stm.wallet.unlock("wallet-passwd")
    
    wallet = Wallet(upvote_account, steem_instance=stm)
    
    last_steem_block = 1950 # It is a good idea to store this block, otherwise all transfers will be checked again
    while True:
        history = wallet.get_history(upvote_token)
        for h in history:
            if int(h["block"]) <= last_steem_block:
                continue
            if h["to"] != upvote_account:
                continue
            last_steem_block = int(h["block"])
            if len(whitelist) > 0 and h["from"] not in whitelist:
                print("%s is not in the whitelist, skipping" % h["from"])
                continue
            if float(h["quantity"]) < min_token_amount:
                print("Below min token amount skipping...")
                continue
            try:
                c = Comment(h["memo"], steem_instance=stm)
            except:
                print("%s is not a valid url, skipping" % h["memo"])
                continue
            
            if c.is_comment() and only_main_posts:
                print("%s from %s is a comment, skipping" % (c["permlink"], c["author"]))
                continue
            if (c.time_elapsed().total_seconds() / 60 / 60 / 24) > max_post_age_days:
                print("Post is to old, skipping")
                continue                
            tags_ok = True
            if len(blacklist_tags) > 0 and "tags" in c:
                for t in blacklist_tags:
                    if t in c["tags"]:
                        tags_ok = False
            if not tags_ok:
                print("skipping, as one tag is blacklisted")
                continue
            already_voted = False
            for v in c["active_votes"]:
                if v["voter"] == upvote_account:
                    already_voted = True
            if already_voted:
                print("skipping, as already upvoted")
                continue
            
            upvote_weight = float(h["quantity"]) * token_weight_factor
            if upvote_weight > 100:
                upvote_weight = 100
            print("upvote %s from %s with %.2f %%" % (c["permlink"], c["author"], upvote_weight))
            print(c.upvote(weight=upvote_weight, voter=upvote_account))
            if len(reply_comment) > 0:
                time.sleep(4)
                print(c.reply(reply_comment, author=upvote_account))
            
        time.sleep(60)
