# This Python file uses the following encoding: utf-8
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals


class TokenDoesNotExists(Exception):
    """ Token does not (yet) exists
    """
    pass


class TokenNotInWallet(Exception):
    """ The token is not in the account wallet
    """
    pass


class InsufficientTokenAmount(Exception):
    """ Not suffienct amount for transfer in the wallet
    """
    pass


class InvalidTokenAmount(Exception):
    """ Invalid token amount (not fitting precision or max supply)
    """
    pass


class TokenIssueNotPermitted(Exception):
    """ Only the token issuer is allowed to permit new tokens
    """
    pass


class MaxSupplyReached(Exception):
    """ Only the token issuer is allowed to permit new tokens
    """
    pass
