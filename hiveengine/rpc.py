"""graphennewsrpc."""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
from builtins import next
from builtins import str
from builtins import object
import sys
import json
import logging
import re

from .version import version as hiveengine_version
if sys.version_info[0] < 3:
    from thread import interrupt_main
else:
    from _thread import interrupt_main

REQUEST_MODULE = None
if not REQUEST_MODULE:
    try:
        import requests
        from requests.adapters import HTTPAdapter
        from requests.packages.urllib3.util.retry import Retry
        from requests.exceptions import ConnectionError
        REQUEST_MODULE = "requests"
    except ImportError:
        REQUEST_MODULE = None

log = logging.getLogger(__name__)



class RPCError(Exception):
    """RPCError Exception."""

    pass


class RPCErrorDoRetry(Exception):
    """RPCErrorDoRetry Exception."""

    pass


class UnauthorizedError(Exception):
    """UnauthorizedError Exception."""

    pass


class SessionInstance(object):
    """Singelton for the Session Instance"""
    instance = None


def set_session_instance(instance):
    """Set session instance"""
    SessionInstance.instance = instance


def shared_session_instance():
    """Get session instance"""
    if REQUEST_MODULE is None:
        raise Exception()
    if not SessionInstance.instance:
        SessionInstance.instance = requests.Session()
    return SessionInstance.instance


def get_endpoint_name(*args, **kwargs):
        # Sepcify the endpoint to talk to
    endpoint = "contracts"
    if ("endpoint" in kwargs) and len(kwargs["endpoint"]) > 0:
        endpoint = kwargs["endpoint"]
    return endpoint


class RPC(object):
    """
    This class allows to call API methods synchronously, without callbacks.

    It logs warnings and errors.

    Usage:

        .. code-block:: python

            from hiveengine.rpc import RPC
            rpc = RPC()
            print(rpc.getLatestBlockInfo(endpoint="blockchain"))

    """

    def __init__(self, url=None, user=None, password=None, **kwargs):
        """Init."""
        self._request_id = 0
        self.timeout = kwargs.get('timeout', 60)
        num_retries = kwargs.get("num_retries", -1)
        num_retries_call = kwargs.get("num_retries_call", 5)

        self.user = user
        self.password = password
        if url is None:
            self.url = 'https://api.hive-engine.com/rpc/'
        else:
            self.url = url
        self.session = shared_session_instance()
        self.headers = {'User-Agent': 'hiveengine v%s' % (hiveengine_version),
                        'content-type': 'application/json'}        
        self.rpc_queue = []

    def get_request_id(self):
        """Get request id."""
        self._request_id += 1
        return self._request_id

    def request_send(self, endpoint, payload):
        if self.user is not None and self.password is not None:
            response = self.session.post(self.url + endpoint,
                                         data=payload,
                                         headers=self.headers,
                                         timeout=self.timeout,
                                         auth=(self.user, self.password))
        else:
            response = self.session.post(self.url + endpoint,
                                         data=payload,
                                         headers=self.headers,
                                         timeout=self.timeout)
        if response.status_code == 401:
            raise UnauthorizedError
        return response.text

    def version_string_to_int(self, network_version):
        version_list = network_version.split('.')
        return int(int(version_list[0]) * 1e8 + int(version_list[1]) * 1e4 + int(version_list[2]))

    def _check_for_server_error(self, reply):
        """Checks for server error message in reply"""
        if re.search("Internal Server Error", reply) or re.search("500", reply):
            raise RPCErrorDoRetry("Internal Server Error")
        elif re.search("Not Implemented", reply) or re.search("501", reply):
            raise RPCError("Not Implemented")
        elif re.search("Bad Gateway", reply) or re.search("502", reply):
            raise RPCErrorDoRetry("Bad Gateway")
        elif re.search("Too Many Requests", reply) or re.search("429", reply):
            raise RPCErrorDoRetry("Too Many Requests")
        elif re.search("Service Temporarily Unavailable", reply) or re.search("Service Unavailable", reply) or re.search("503", reply):
            raise RPCErrorDoRetry("Service Temporarily Unavailable")
        elif re.search("Gateway Time-out", reply) or re.search("Gateway Timeout", reply) or re.search("504", reply):
            raise RPCErrorDoRetry("Gateway Time-out")
        elif re.search("HTTP Version not supported", reply) or re.search("505", reply):
            raise RPCError("HTTP Version not supported")
        elif re.search("Variant Also Negotiates", reply) or re.search("506", reply):
            raise RPCError("Variant Also Negotiates")
        elif re.search("Insufficient Storage", reply) or re.search("507", reply):
            raise RPCError("Insufficient Storage")
        elif re.search("Loop Detected", reply) or re.search("508", reply):
            raise RPCError("Loop Detected")
        elif re.search("Bandwidth Limit Exceeded", reply) or re.search("509", reply):
            raise RPCError("Bandwidth Limit Exceeded")
        elif re.search("Not Extended", reply) or re.search("510", reply):
            raise RPCError("Not Extended")
        elif re.search("Network Authentication Required", reply) or re.search("511", reply):
            raise RPCError("Network Authentication Required")
        else:
            raise RPCError("Client returned invalid format. Expected JSON!")

    def rpcexec(self, endpoint, payload):
        """
        Execute a call by sending the payload.

        :param json payload: Payload data
        :raises ValueError: if the server does not respond in proper JSON format
        :raises RPCError: if the server returns an error
        """
        log.debug(json.dumps(payload))

        reply = self.request_send(endpoint, json.dumps(payload, ensure_ascii=False).encode('utf8'))

        ret = {}
        try:
            ret = json.loads(reply, strict=False)
        except ValueError:
            self._check_for_server_error(reply)

        log.debug(json.dumps(reply))

        if isinstance(ret, dict) and 'error' in ret:
            if 'detail' in ret['error']:
                raise RPCError(ret['error']['detail'])
            else:
                raise RPCError(ret['error']['message'])
        else:
            if isinstance(ret, list):
                ret_list = []
                for r in ret:
                    if isinstance(r, dict) and 'error' in r:
                        if 'detail' in r['error']:
                            raise RPCError(r['error']['detail'])
                        else:
                            raise RPCError(r['error']['message'])
                    elif isinstance(r, dict) and "result" in r:
                        ret_list.append(r["result"])
                    else:
                        ret_list.append(r)
                return ret_list
            elif isinstance(ret, dict) and "result" in ret:
                self.nodes.reset_error_cnt_call()
                return ret["result"]
            elif isinstance(ret, int):
                raise RPCError("Client returned invalid format. Expected JSON! Output: %s" % (str(ret)))
            else:
                return ret
        return ret

    # End of Deprecated methods
    ####################################################################
    def __getattr__(self, name):
        """Map all methods to RPC calls and pass through the arguments."""
        def method(*args, **kwargs):
            endpoint = get_endpoint_name(*args, **kwargs)
            args = json.loads(json.dumps(args))
            # let's be able to define the num_retries per query
            if len(args) > 0:
                args = args[0]
            query = {"method": name,
                     "jsonrpc": "2.0",
                     "params": args,
                     "id": self.get_request_id()}
            self.rpc_queue.append(query)
            query = self.rpc_queue
            self.rpc_queue = []
            r = self.rpcexec(endpoint, query)
            return r
        return method
