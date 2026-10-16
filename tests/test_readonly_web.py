"""Read-only enforcement and shared-world behavior over real HTTP listeners."""

from contextlib import ExitStack
from http.client import HTTPConnection
from http.server import ThreadingHTTPServer
import json
import socket
import threading

import pytest

from faerun import cli, web
from faerun.brand import apply_branding
from faerun.calendar import HarptosDate
from faerun.models import C, S
from faerun.orders import TradeStore
from faerun.world import EconomyConfig, World


def request(server, path, method="GET", body=None, headers=None):
    connection = HTTPConnection("127.0.0.1", server.server_port, timeout=10)
    try:
        connection.request(method, path, body=body, headers=headers or {})
        response = connection.getresponse()
        return response.status, response.read()
    finally:
        connection.close()


@pytest.fixture
def world(tmp_path, monkeypatch):
    world = World(
        settlements=[S("Town", "Test", "test", 1000, 0, 0, ind="farm3")],
        commodities=[C("grain", "Grain", "food", 10, produced_by="farm")],
        businesses=[], date=HarptosDate(1492, 1, 1),
        config=EconomyConfig(seasonal_inventory=False, expanded_requirements=False),
        trade_store=TradeStore(tmp_path / "ledger.sqlite3"),
    )
    monkeypatch.setattr(web, "get_world", lambda: world)
    return world


@pytest.fixture
def listeners(world):
    with ExitStack() as stack:
        servers = []
        for handler in (web.Handler, web.ReadOnlyHandler):
            server = stack.enter_context(ThreadingHTTPServer(("127.0.0.1", 0), handler))
            thread = threading.Thread(target=server.serve_forever, daemon=True)
            thread.start()
            stack.callback(thread.join)
            stack.callback(server.shutdown)
            servers.append(server)
        yield servers


def test_all_write_routes_rejected_before_dispatch(listeners, monkeypatch):
    _, reader = listeners
    dispatched = []
    for path in web.POST_ROUTES:
        monkeypatch.setitem(web.POST_ROUTES, path, lambda *_: dispatched.append(True))
        status, raw = request(reader, path, "POST", b'{"anything":true}',
                              {"Content-Type": "application/json"})
        assert status == 403, path
        assert "read-only" in json.loads(raw)["error"]
    assert dispatched == []
    for method in ("PUT", "PATCH", "DELETE", "TRACE", "CUSTOM"):
        status, raw = request(reader, "/api/world", method, b"invalid json")
        assert status == 403
        assert "read-only" in json.loads(raw)["error"]
    assert request(reader, "/api/future-mutation", "POST", b"not json")[0] == 403


def test_same_world_visible_but_not_editable(listeners, world):
    editor, reader = listeners
    before = request(reader, "/api/bootstrap")
    assert before[0] == 200
    assert request(reader, "/api/world", "POST", b'{"year":1500}')[0] == 403
    assert request(reader, "/api/bootstrap") == before
    assert world.date.year == 1492
    status, _ = request(editor, "/api/world", "POST", b'{"year":1493,"month":2}')
    assert status == 200
    assert world.date.year == 1493
    assert request(reader, "/api/bootstrap") == request(editor, "/api/bootstrap")
    assert request(reader, "/api/bootstrap") != before
    assert json.loads(request(reader, "/api/access")[1]) == {"read_only": True}
    assert json.loads(request(editor, "/api/access")[1]) == {"read_only": False}
    for path in ("/api/trade/orders", "/api/board/requests"):
        assert request(reader, path) == request(editor, path)
        assert request(reader, path)[0] == 200


def test_all_pages_get_viewer_presentation_without_changing_editor(listeners):
    editor, reader = listeners
    for name, (body, content_type) in web.STATIC.items():
        if not content_type.startswith("text/html"):
            continue
        assert request(editor, "/" + name) == (200, apply_branding(body).encode("utf-8"))
        status, raw = request(reader, "/" + name)
        if name in web.LORE_ASSETS:
            assert status == 403, name
            continue
        assert status == 200, name
        assert b'id="read-only-notice"' in raw, name
        assert b'id="read-only-style"' in raw, name
    assert request(reader, "/app.css") == request(editor, "/app.css")
    assert request(reader, "/does-not-exist.html")[0] == 404


def test_lore_is_disabled_only_on_read_only_listener(listeners, monkeypatch):
    editor, reader = listeners
    calls = []

    def lore(world, params):
        calls.append(params)
        return {"threads": [], "research": []}

    monkeypatch.setitem(web.GET_ROUTES, "/api/lore-desk", lore)
    for path in ("/api/lore-desk", "/api/lore-desk?status=queued",
                 *("/" + name for name in web.LORE_ASSETS)):
        status, raw = request(reader, path)
        assert status == 403, path
        assert "Lore is unavailable" in json.loads(raw)["error"]
    assert calls == []
    assert request(editor, "/api/lore-desk")[0] == 200
    assert len(calls) == 1
    for name, (body, content_type) in web.LORE_ASSETS.items():
        expected = apply_branding(body) if content_type.startswith("text/html") else body
        assert request(editor, "/" + name) == (200, expected.encode("utf-8"))
    html = request(reader, "/map.html")[1].decode("utf-8")
    assert 'a[href="lore.html"]' in html


@pytest.mark.parametrize("command", ["serve", "map", "location"])
@pytest.mark.parametrize("option,expected", [([], None), (["--read-only-port"], 8884),
                                          (["--read-only-port", "9000"], 9000)])
def test_cli_passes_read_only_port(command, option, expected, world, monkeypatch):
    seen = {}
    monkeypatch.setattr(web, "serve", lambda **kwargs: seen.update(kwargs))
    host_option = ["--read-only-host", "0.0.0.0"] if expected is not None else []
    args = cli.build_parser().parse_args([command, "--no-browser", *option, *host_option])
    args.func(args, world)
    assert seen["read_only_port"] == expected
    assert seen["read_only_host"] == ("0.0.0.0" if expected is not None else None)


def test_web_entrypoint_passes_read_only_port(monkeypatch):
    seen = {}
    monkeypatch.setattr(web, "serve", lambda *args, **kwargs: seen.update(kwargs))
    assert web.main(["--no-browser", "--read-only-port", "8884",
                     "--read-only-host", "0.0.0.0"]) == 0
    assert seen["read_only_port"] == 8884
    assert seen["read_only_host"] == "0.0.0.0"


@pytest.mark.parametrize("reader_host", [None, "0.0.0.0"])
def test_serve_starts_and_closes_both_listeners(world, monkeypatch, reader_host):
    real_serve = ThreadingHTTPServer.serve_forever
    servers = []
    reader_started = threading.Event()

    def serve_forever(server):
        servers.append(server)
        if server.RequestHandlerClass is web.ReadOnlyHandler:
            reader_started.set()
            return real_serve(server)
        assert reader_started.wait(5)
        reader = next(item for item in servers if item.RequestHandlerClass is web.ReadOnlyHandler)
        assert server.server_address[0] == "127.0.0.1"
        assert reader.server_address[0] == (reader_host or "127.0.0.1")
        assert json.loads(request(reader, "/api/access")[1])["read_only"] is True
        raise KeyboardInterrupt

    monkeypatch.setattr(ThreadingHTTPServer, "serve_forever", serve_forever)
    monkeypatch.setattr(web, "underlay_info", lambda: {"available": False, "searched": ["test"]})
    web.serve(port=0, read_only_port=0, open_browser=False, read_only_host=reader_host)
    assert len(servers) == 2
    assert all(server.socket.fileno() == -1 for server in servers)


def test_occupied_read_only_port_closes_primary(world, monkeypatch):
    created = []
    real_server = web.ThreadingHTTPServer

    def make_server(*args):
        server = real_server(*args)
        created.append(server)
        return server

    monkeypatch.setattr(web, "ThreadingHTTPServer", make_server)
    with socket.socket() as occupied:
        occupied.bind(("127.0.0.1", 0))
        occupied.listen()
        with pytest.raises(SystemExit, match="1"):
            web.serve(port=0, read_only_port=occupied.getsockname()[1], open_browser=False)
    assert len(created) == 1
    assert created[0].socket.fileno() == -1


def test_same_port_is_rejected_before_startup():
    with pytest.raises(ValueError, match="must be different"):
        web.serve(port=8883, read_only_port=8883, open_browser=False)


def test_read_only_host_requires_port():
    with pytest.raises(ValueError, match="requires --read-only-port"):
        web.serve(read_only_host="0.0.0.0", open_browser=False)
