"""The poster-map underlay: discovery, serving, and the map-page controls.

The artwork itself is never part of this project, so every test here works with
a throwaway file it creates. The point of the feature is that the engine can
*find* an image the user already owns without anything being copied.
"""

from __future__ import annotations

import os
from types import SimpleNamespace

import pytest

from faerun import underlay
from faerun.mapassets import MAP_ASSETS
from faerun.underlay import (
    ENV_VAR,
    NAME_HINT,
    set_override,
    underlay_bytes,
    underlay_info,
)
from faerun.web import GET_ROUTES, Handler, api_underlay
from faerun.world import get_world

# A PNG signature followed by filler. Nothing here decodes the image - the
# content type comes from the extension and the browser does the decoding - so
# a stand-in keeps the test suite free of any artwork at all.
TINY_PNG = b"\x89PNG\r\n\x1a\n" + bytes(range(32))

# Captured before the autouse fixture stubs the module attribute out, so the
# discovery-order test can still exercise the real thing.
_REAL_SEARCH_DIRS = underlay._search_dirs


@pytest.fixture(autouse=True)
def _isolated(monkeypatch, tmp_path):
    """Keep the tests away from whatever really sits in the user's Downloads."""
    monkeypatch.delenv(ENV_VAR, raising=False)
    monkeypatch.setattr(underlay, "_search_dirs", lambda: [tmp_path])
    set_override(None)
    yield
    set_override(None)


def test_no_image_anywhere_is_reported_calmly(tmp_path):
    info = underlay_info()
    assert info["available"] is False
    assert info["url"] == ""
    # The page tells the user where to put the file, so the list must not be
    # empty or the instructions read as "put it nowhere".
    assert info["searched"]
    assert info["env_var"] == ENV_VAR
    assert underlay_bytes() is None


def test_the_maps_folder_is_searched_before_anything_else(monkeypatch, tmp_path):
    # Dropping a poster into maps/ is the documented way to install one, so it
    # has to be looked at first - ahead of the project root and of ~/Downloads.
    monkeypatch.setattr(underlay, "project_root", lambda: tmp_path)
    dirs = _REAL_SEARCH_DIRS()
    assert dirs[0] == tmp_path / "maps"
    assert tmp_path in dirs
    # No duplicates, or the loose name scan would read a folder twice.
    assert len(dirs) == len(set(dirs))


def test_an_explicit_override_wins(tmp_path):
    poster = tmp_path / "somewhere-else.png"
    poster.write_bytes(TINY_PNG)
    set_override(str(poster))
    info = underlay_info()
    assert info["available"] is True
    assert info["name"] == "somewhere-else.png"
    assert info["mime"] == "image/png"
    assert info["bytes"] == len(TINY_PNG)
    assert underlay_bytes()["raw"] == TINY_PNG


def test_an_override_pointing_at_nothing_falls_through(tmp_path):
    set_override(str(tmp_path / "not-there.jpg"))
    assert underlay_info()["available"] is False


def test_the_environment_variable_is_honoured(monkeypatch, tmp_path):
    poster = tmp_path / "poster.jpg"
    poster.write_bytes(TINY_PNG)
    monkeypatch.setenv(ENV_VAR, str(poster))
    # Named "poster.jpg", so only the environment variable can find it: the
    # name does not match the loose guess and it is not called underlay.*.
    assert underlay_info()["name"] == "poster.jpg"


def test_a_file_called_underlay_is_found_without_configuration(tmp_path):
    (tmp_path / "underlay.jpg").write_bytes(TINY_PNG)
    info = underlay_info()
    assert info["available"] is True
    assert info["mime"] == "image/jpeg"


def test_a_downloaded_poster_is_found_by_its_name(tmp_path):
    # The file that prompted this feature is spelled "Faeun Map.jpg" - one "r"
    # short. Discovery has to survive that, or the feature silently does
    # nothing for the person who asked for it.
    (tmp_path / "Faeun Map.jpg").write_bytes(TINY_PNG)
    assert underlay_info()["name"] == "Faeun Map.jpg"


@pytest.mark.parametrize("name", [
    "Faerun Map.jpg",
    "faerun-world-map.png",
    "Faeun Map.jpg",
    "Forgotten Realms map.webp",
    "sword coast map.png",
    "Faerun Hires.jpg",
    "Toril Hi-Res.webp",
    "Faerun High Resolution.png",
])
def test_plausible_poster_names_match(name):
    assert NAME_HINT.search(name)


@pytest.mark.parametrize("name", [
    "roadmap.png",
    "screenshot.png",
    "invoice.pdf",
    "cat.jpg",
    "waterdeep-map.jpg",
    "waterdeep-map-hires.jpg",
    "neverwinter-city-map.png",
])
def test_unrelated_names_do_not_match(name):
    assert not NAME_HINT.search(name)


def test_newer_city_map_does_not_replace_world_background(monkeypatch, tmp_path):
    folder = tmp_path / "maps"
    folder.mkdir()
    world = folder / "Faerun Hires.jpg"
    world.write_bytes(TINY_PNG)
    city = folder / "waterdeep-map-hires.jpg"
    city.write_bytes(TINY_PNG + b"city")
    os.utime(world, (1000, 1000))
    os.utime(city, (2000, 2000))
    monkeypatch.setattr(underlay, "_search_dirs", lambda: [folder])
    assert underlay_info()["name"] == world.name
    assert underlay_bytes()["raw"] == TINY_PNG


@pytest.mark.parametrize("folder_name", ["map", "maps"])
def test_city_images_alone_do_not_supply_a_world_background(monkeypatch, tmp_path, folder_name):
    folder = tmp_path / folder_name
    folder.mkdir()
    (folder / "waterdeep-map-hires.jpg").write_bytes(TINY_PNG)
    (folder / "neverwinter-city-map.png").write_bytes(TINY_PNG)
    (folder / "portrait.png").write_bytes(TINY_PNG)
    monkeypatch.setattr(underlay, "_search_dirs", lambda: [folder])
    assert underlay_info()["available"] is False
    assert underlay_bytes() is None


def test_city_images_do_not_hide_world_maps_in_later_folders(monkeypatch, tmp_path):
    folder = tmp_path / "maps"
    folder.mkdir()
    (folder / "waterdeep-map-hires.jpg").write_bytes(TINY_PNG)
    (tmp_path / "Faerun Map.jpg").write_bytes(TINY_PNG)
    monkeypatch.setattr(underlay, "_search_dirs", lambda: [folder, tmp_path])
    assert underlay_info()["name"] == "Faerun Map.jpg"


def test_newest_matching_world_map_still_wins(monkeypatch, tmp_path):
    folder = tmp_path / "maps"
    folder.mkdir()
    for timestamp, name in enumerate(("Faerun Map.png", "Faerun Hires.jpg", "waterdeep-map-hires.jpg"), 1):
        path = folder / name
        path.write_bytes(TINY_PNG)
        os.utime(path, (timestamp * 1000, timestamp * 1000))
    monkeypatch.setattr(underlay, "_search_dirs", lambda: [folder])
    assert underlay_info()["name"] == "Faerun Hires.jpg"


def test_newer_reference_maps_do_not_replace_original_poster(tmp_path):
    poster = tmp_path / "Faerun Hires.jpg"
    poster.write_bytes(TINY_PNG)
    os.utime(poster, (1000, 1000))
    for _, filename in underlay.BACKDROPS.values():
        reference = tmp_path / filename
        reference.write_bytes(TINY_PNG + b"reference")
        os.utime(reference, (2000, 2000))
    assert underlay_info()["name"] == poster.name
    assert underlay_bytes()["raw"] == TINY_PNG
    assert len(underlay_info()["options"]) == 4


def test_reference_images_alone_are_not_an_original_poster(tmp_path):
    for _, filename in underlay.BACKDROPS.values():
        (tmp_path / filename).write_bytes(TINY_PNG)
    assert underlay_info()["available"] is False
    assert underlay_bytes() is None
    assert len(underlay_info()["options"]) == 3


def test_a_non_image_extension_is_ignored(tmp_path):
    (tmp_path / "Faerun Map.txt").write_text("not an image", encoding="utf-8")
    assert underlay_info()["available"] is False


def test_the_bytes_are_re_read_when_the_file_changes(tmp_path):
    poster = tmp_path / "underlay.png"
    poster.write_bytes(TINY_PNG)
    first = underlay_bytes()["raw"]
    assert first == TINY_PNG
    poster.write_bytes(TINY_PNG + b"\x00" * 64)
    assert len(underlay_bytes()["raw"]) == len(TINY_PNG) + 64


def test_topographical_is_an_optional_backdrop(tmp_path):
    (tmp_path / "underlay.jpg").write_bytes(TINY_PNG)
    (tmp_path / "Fareun Topographical.png").write_bytes(TINY_PNG + b"topographical")
    assert underlay_info()["name"] == "underlay.jpg"
    info = underlay_info("topographical")
    assert info["available"] is True
    assert info["mime"] == "image/png"
    assert info["url"] == "/underlay.img?source=topographical"
    assert [option["id"] for option in info["options"]] == ["default", "topographical"]
    assert underlay_bytes("topographical")["raw"] == TINY_PNG + b"topographical"
    assert underlay_bytes()["raw"] == TINY_PNG


def test_backdrop_selection_does_not_accept_paths(tmp_path):
    poster = tmp_path / "private.png"
    poster.write_bytes(TINY_PNG)
    assert underlay_bytes(str(poster)) is None
    assert underlay_info("../private.png")["available"] is False


@pytest.mark.parametrize("source,filename", [
    ("elevation", "Faerun elevation and sea-depth map.png"),
    ("ground-cover", "Flat-color Faerun ground cover map.png"),
])
def test_additional_backdrops_are_selectable(tmp_path, source, filename):
    (tmp_path / filename).write_bytes(TINY_PNG)
    info = underlay_info(source)
    assert info["available"] is True
    assert info["name"] == filename
    assert info["url"] == "/underlay.img?source=" + source
    assert info["mime"] == "image/png"
    assert source in [option["id"] for option in info["options"]]
    assert underlay_bytes(source)["raw"] == TINY_PNG
    assert "'" + source + "'" in MAP_ASSETS["map.js"][0]
    (tmp_path / filename).unlink()
    assert underlay_info(source)["available"] is False
    assert underlay_bytes(source) is None


def test_missing_topographical_backdrop_is_unavailable(tmp_path):
    (tmp_path / "underlay.jpg").write_bytes(TINY_PNG)
    assert underlay_info("topographical")["available"] is False
    assert underlay_info()["options"] == [{"id": "default", "label": "Original poster"}]


def test_topographical_api_and_image_handler(tmp_path, monkeypatch):
    from faerun import atlas

    (tmp_path / "Fareun Topographical.png").write_bytes(TINY_PNG)
    placement = {"available": True, "widthMiles": 3800, "heightMiles": 2540}
    monkeypatch.setattr(atlas, "underlay_placement", lambda settlements: placement)
    info = api_underlay(SimpleNamespace(settlements={}), {"source": ["topographical"]})
    assert info["source"] == "topographical"
    assert info["survey"] == placement
    responses = []
    handler = SimpleNamespace(
        _send_bytes=lambda raw, mime: responses.append((raw, mime)),
        _send_json=lambda body, status: responses.append((body, status)),
    )
    Handler._send_underlay(handler, "topographical")
    assert responses.pop() == (TINY_PNG, "image/png")
    Handler._send_underlay(handler, "../private.png")
    assert responses.pop()[1] == 404


def test_backdrop_selector_is_present_in_both_map_views():
    for name in ("map.html", "terrain.html"):
        assert MAP_ASSETS[name][0].count('id="underlay-source"') == 1
    javascript = MAP_ASSETS["map.js"][0]
    assert "faerun.underlay.source" in javascript
    assert "UNDERLAY_KEY + '.' + source" in javascript
    assert "request !== underlayRequest" in javascript


def test_the_api_route_is_registered_and_answers(tmp_path):
    assert GET_ROUTES["/api/underlay"] is api_underlay
    payload = api_underlay(get_world(), {})
    assert set(payload) >= {"available", "url", "name", "searched", "env_var"}


def test_the_map_page_carries_the_overlay_controls():
    html = MAP_ASSETS["map.html"][0]
    for marker in ("opt-underlay", "opt-underlay-alpha", "opt-underlay-x",
                   "opt-underlay-scale", "underlay-align", "underlay-reset"):
        assert marker in html, marker

    js = MAP_ASSETS["map.js"][0]
    for marker in ("drawUnderlay", "loadUnderlay", "/api/underlay",
                   "faerun.underlay.v1"):
        assert marker in js, marker
    # The poster must be painted after the terrain and before the dots, or the
    # settlement markers vanish underneath the artwork.
    assert js.index("drawUnderlay();") < js.index("drawPins();")


def test_the_map_assets_stay_plain_ascii_with_no_escapes():
    # The asset strings are triple-quoted Python. A stray backslash or quote
    # sequence in them is a syntax error at import, which is why every non-ASCII
    # character in the page is written as an HTML entity.
    for name in ("map.html", "map.css", "map.js"):
        body = MAP_ASSETS[name][0]
        assert body.isascii(), name
        assert "\\" not in body, name
        assert '"""' not in body, name
