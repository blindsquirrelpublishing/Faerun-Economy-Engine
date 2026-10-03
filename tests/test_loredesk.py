import pytest

from faerun import loredesk


@pytest.fixture(autouse=True)
def isolated_desk(tmp_path, monkeypatch):
    monkeypatch.setattr(loredesk, "desk_path", lambda: tmp_path / "desk.sqlite3")


def test_conversation_round_trip():
    identifier = loredesk.post_desk(None, {"title": "Northern trade", "body": "Research local exports."})["id"]
    loredesk.publish_reply(identifier, "Evidence and proposals.", [{"title": "Source", "url": "https://example.org"}])
    thread = loredesk.read_desk()["threads"][0]
    assert thread["status"] == "answered"
    assert [message["author"] for message in thread["messages"]] == ["You", "Lore"]
    assert thread["messages"][1]["sources"][0]["title"] == "Source"
    loredesk.post_desk(None, {"action": "reply", "id": identifier, "body": "Check the date.", "author": "Lore"})
    thread = loredesk.read_desk()["threads"][0]
    assert thread["status"] == "queued"
    assert thread["messages"][-1]["author"] == "You"


def test_close_and_reopen():
    identifier = loredesk.post_desk(None, {"title": "Map lead", "body": "Check location", "kind": "map"})["id"]
    loredesk.post_desk(None, {"action": "status", "id": identifier, "status": "closed"})
    with pytest.raises(ValueError, match="closed"):
        loredesk.publish_reply(identifier, "Reply")
    with pytest.raises(ValueError, match="Reopen"):
        loredesk.post_desk(None, {"action": "reply", "id": identifier, "body": "Reply"})
    loredesk.post_desk(None, {"action": "status", "id": identifier, "status": "queued"})
    loredesk.publish_reply(identifier, "Reviewed")
    assert loredesk.read_desk()["threads"][0]["status"] == "answered"


@pytest.mark.parametrize("body", [{"title": "", "body": "Test"}, {"title": "Test", "body": " "}, {"title": "Test", "body": "Test", "kind": "invalid"}, {"action": "reply", "id": "absent", "body": "Test"}])
def test_invalid_requests_do_not_write(body):
    with pytest.raises((ValueError, KeyError)):
        loredesk.post_desk(None, body)
    assert loredesk.read_desk()["threads"] == []


def test_invalid_citation_does_not_publish():
    identifier = loredesk.post_desk(None, {"title": "Test", "body": "Question"})["id"]
    with pytest.raises(ValueError, match="HTTP"):
        loredesk.publish_reply(identifier, "Reply", [{"title": "Unsafe", "url": "javascript:alert(1)"}])
    assert len(loredesk.read_desk()["threads"][0]["messages"]) == 1


def test_web_registration_and_javascript():
    import shutil
    import subprocess
    from faerun import web
    from faerun.loreassets import LORE_JS

    assert web.GET_ROUTES["/api/lore-desk"] is loredesk.read_desk
    assert web.POST_ROUTES["/api/lore-desk"] is loredesk.post_desk
    assert "lore.html" in web.STATIC
    node = shutil.which("node")
    if node:
        result = subprocess.run([node, "--check"], input=LORE_JS, text=True, capture_output=True)
        assert result.returncode == 0, result.stderr


def test_http_conversations_and_origin_guard(monkeypatch):
    from http.client import HTTPConnection
    from http.server import ThreadingHTTPServer
    import json
    from threading import Thread
    from faerun import web

    monkeypatch.setattr(web, "get_world", lambda: None)
    server = ThreadingHTTPServer(("127.0.0.1", 0), web.Handler)
    worker = Thread(target=server.serve_forever, daemon=True)
    worker.start()
    client = HTTPConnection("127.0.0.1", server.server_port, timeout=5)
    try:
        client.request("GET", "/lore.html")
        response = client.getresponse()
        assert response.status == 200
        assert b"Lore Desk" in response.read()
        payload = json.dumps({"title": "HTTP test", "body": "Queued research"})
        client.request("POST", "/api/lore-desk", payload, {"Content-Type": "application/json"})
        response = client.getresponse()
        assert response.status == 200
        identifier = json.loads(response.read())["id"]
        loredesk.publish_reply(identifier, "Verified response")
        client.request("GET", "/api/lore-desk")
        response = client.getresponse()
        assert response.status == 200
        assert json.loads(response.read())["threads"][0]["messages"][-1]["author"] == "Lore"
        client.request("POST", "/api/lore-desk", payload, {"Content-Type": "application/json", "Origin": "https://example.org"})
        response = client.getresponse()
        assert response.status == 403
        response.read()
        assert len(loredesk.read_desk()["threads"]) == 1
    finally:
        client.close()
        server.shutdown()
        server.server_close()
        worker.join(timeout=5)