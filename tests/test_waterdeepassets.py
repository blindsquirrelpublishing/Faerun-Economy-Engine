from pathlib import Path
import subprocess

from faerun import web
from faerun.waterdeepassets import (
    WATERDEEP_ASSETS,
    WATERDEEP_CSS,
    WATERDEEP_HTML,
    WATERDEEP_JS,
)


def test_waterdeep_atlas_assets_are_served():
    assert {"waterdeep.html", "waterdeep.css", "waterdeep.js"} <= web.STATIC.keys()
    assert "waterdeep-map.jpg" in web.BINARY_STATIC
    image_path, content_type = web.BINARY_STATIC["waterdeep-map.jpg"]
    assert content_type == "image/jpeg"
    assert Path(image_path).is_file()
    hires_path, hires_type = web.BINARY_STATIC["waterdeep-map-hires.jpg"]
    assert hires_type == "image/jpeg"
    assert hires_path.name == "waterdeep-map-hires.jpg"
    assert hires_path.is_file()
    assert 'id="map-image" src="waterdeep-map-hires.jpg"' in WATERDEEP_HTML


def test_waterdeep_atlas_has_search_filters_and_map_controls():
    assert 'id="search-form"' in WATERDEEP_HTML
    assert 'data-filter="ward"' in WATERDEEP_HTML
    assert 'id="measure-toggle"' in WATERDEEP_HTML
    assert 'id="zoom-in"' in WATERDEEP_HTML
    assert 'id="view-3d"' in WATERDEEP_HTML
    assert 'id="orbit-tools"' in WATERDEEP_HTML
    assert "function selectPlace(place, focus, updateHash)" in WATERDEEP_JS
    assert "function addMeasurePoint(point)" in WATERDEEP_JS
    assert "function set3d(enabled)" in WATERDEEP_JS
    assert "state.orbiting = state.is3d" in WATERDEEP_JS
    assert "var MAP_WIDTH = 768;" in WATERDEEP_JS
    assert "var MAP_HEIGHT = 1536;" in WATERDEEP_JS
    assert "width: 768px; height: 1536px" in WATERDEEP_CSS
    assert "viewport.addEventListener('wheel'" in WATERDEEP_JS


def test_waterdeep_atlas_uses_the_shared_artifact_theme():
    assert 'new URLSearchParams(window.location.search).get("scoutTheme")' in WATERDEEP_HTML
    assert "--cp-bg: #f7f4ef;" in WATERDEEP_CSS
    assert 'font: 15px/1.5 "Segoe UI"' in WATERDEEP_CSS


def test_atlas_population_uses_active_api_value_and_surfaces_failures():
    assert 'id="resident-population"' in WATERDEEP_HTML
    assert 'id="population-status"' in WATERDEEP_HTML
    assert "130,000</b>" not in WATERDEEP_HTML
    loader = WATERDEEP_JS.split("  function loadPopulation()", 1)[1].split("  var places =", 1)[0]
    script = """
const assert = require('node:assert/strict');
const elements = new Map();
globalThis.document = {getElementById(id) {
  if (!elements.has(id)) elements.set(id, {textContent: ''});
  return elements.get(id);
}};
""" + "function loadPopulation()" + loader + """
(async () => {
  let report = {
    resident_population: 200000, comparison_residents: 130000, date: '16 Eleint 1492 DR',
    scope: 'City residents', rationale: 'Scenario, not a census'
  };
  let ok = true;
  globalThis.fetch = async url => {
    assert.equal(url, '/api/population?settlement=Waterdeep');
    return {ok, status: 503, json: async () => report};
  };
  await loadPopulation();
  assert.equal(elements.get('resident-population').textContent, (200000).toLocaleString());
  assert.ok(elements.get('population-status').textContent.includes('Scenario, not a census'));
  assert.ok(elements.get('population-status').textContent.includes((130000).toLocaleString()));
  report.resident_population = 175000;
  await loadPopulation();
  assert.equal(elements.get('resident-population').textContent, (175000).toLocaleString());
  report.resident_population = 'invalid';
  await loadPopulation();
  assert.equal(elements.get('resident-population').textContent, 'Unavailable');
  assert.ok(elements.get('population-status').textContent.includes('Invalid resident population'));
  ok = false;
  await loadPopulation();
  assert.equal(elements.get('resident-population').textContent, 'Unavailable');
  assert.ok(elements.get('population-status').textContent.includes('503'));
})().catch(error => { console.error(error); process.exitCode = 1; });
"""
    result = subprocess.run(["node", "-e", script], capture_output=True, text=True)
    assert result.returncode == 0, result.stdout + result.stderr
