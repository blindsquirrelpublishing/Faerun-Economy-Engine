import struct
from http.client import HTTPConnection
from http.server import ThreadingHTTPServer
from threading import Thread

from faerun import web
from faerun.brand import BRAND_BINARY_ASSETS, BRAND_NAME, COPYRIGHT_YEAR, apply_branding

PAGE = (
    "<!DOCTYPE html><html><head><title>Faerun Test</title></head>"
    '<body><header><div class="brand"><h1>Test</h1></div></header><main></main></body></html>'
)


def test_branding_adds_logo_favicon_title_and_footer():
    page = apply_branding(PAGE)
    assert f"Faerun Test | {BRAND_NAME}</title>" in page
    assert 'rel="icon"' in page and 'href="brand.css"' in page
    brand_div = page.index('<div class="brand">')
    assert page[brand_div + len('<div class="brand">'):].startswith('<a class="fc-mark"')
    assert f"&copy; {COPYRIGHT_YEAR} {BRAND_NAME}" in page
    assert "Wizards of the Coast" in page
    assert page.index("<footer") > page.index("</main>")
    assert page.rstrip().endswith("</body></html>")
    assert "fc-footer-compact" not in page


def test_branding_is_idempotent_and_uses_compact_footer_on_fixed_layouts():
    assert apply_branding(apply_branding(PAGE)).count("<footer") == 1
    fixed = PAGE.replace("<body>", '<body class="mapbody">')
    assert "fc-footer-compact" in apply_branding(fixed)


def test_branding_falls_back_to_the_header_without_a_brand_block():
    page = apply_branding("<html><head></head><body><header><h1>x</h1></header></body></html>")
    assert page.index("fc-mark") < page.index("<h1>")


def test_every_html_page_is_branded_when_served():
    for name, (body, content_type) in web.STATIC.items():
        if content_type.startswith("text/html"):
            branded = apply_branding(body)
            assert branded.count("<footer") == 1, name
            assert "faerun-cartographers-192.png" in branded, name


def test_logo_assets_are_real_pngs_with_transparency():
    for name, (path, content_type) in BRAND_BINARY_ASSETS.items():
        assert path.is_file(), name
        if content_type == "image/png":
            data = path.read_bytes()
            assert data[:8] == b"\x89PNG\r\n\x1a\n"
            width, height, _, color_type = struct.unpack(">IIBB", data[16:26])
            assert width == height and color_type == 6, name


def test_brand_assets_and_branded_pages_are_served(monkeypatch):
    monkeypatch.setattr(web, "get_world", lambda: None)
    server = ThreadingHTTPServer(("127.0.0.1", 0), web.Handler)
    Thread(target=server.serve_forever, daemon=True).start()
    client = HTTPConnection("127.0.0.1", server.server_port, timeout=5)
    try:
        for path, expected in (
            ("/faerun-cartographers-192.png", "image/png"),
            ("/favicon.ico", "image/x-icon"),
            ("/brand.css", "text/css; charset=utf-8"),
        ):
            client.request("GET", path)
            response = client.getresponse()
            assert response.status == 200, path
            assert response.getheader("Content-Type") == expected
            assert response.read()
        client.request("GET", "/location.html")
        response = client.getresponse()
        body = response.read().decode("utf-8")
        assert response.status == 200
        assert "<footer" in body and BRAND_NAME in body
    finally:
        client.close()
        server.shutdown()
        server.server_close()
