"""Loopback/private-network access control for trade and board API routes."""

from email.message import Message
from types import SimpleNamespace

import pytest

from faerun.web import ApiError, Handler


def make_handler(client_ip, host_header, origin=None, port=8883):
    handler = object.__new__(Handler)
    handler.client_address = (client_ip, 5555)
    headers = Message()
    headers["Host"] = host_header
    if origin is not None:
        headers["Origin"] = origin
    handler.headers = headers
    handler.server = SimpleNamespace(server_address=("0.0.0.0", port))
    return handler


def test_guard_allows_loopback_clients():
    make_handler("127.0.0.1", "127.0.0.1:8883")._guard_trade_request()


def test_guard_allows_private_lan_clients_addressed_to_their_own_lan_ip():
    make_handler("192.168.1.50", "192.168.1.32:8883",
                 origin="http://192.168.1.32:8883")._guard_trade_request()


def test_guard_rejects_public_internet_clients():
    with pytest.raises(ApiError, match="local network"):
        make_handler("8.8.8.8", "192.168.1.32:8883")._guard_trade_request()


def test_guard_rejects_a_host_header_that_is_not_a_local_ip():
    with pytest.raises(ApiError, match="local server address"):
        make_handler("192.168.1.50", "evil.example.com:8883")._guard_trade_request()


def test_guard_rejects_mismatched_origin():
    with pytest.raises(ApiError, match="Cross-origin"):
        make_handler("192.168.1.50", "192.168.1.32:8883",
                     origin="http://attacker.example.com")._guard_trade_request()


def test_guard_rejects_wrong_port():
    with pytest.raises(ApiError, match="local server address"):
        make_handler("192.168.1.50", "192.168.1.32:9999")._guard_trade_request()
