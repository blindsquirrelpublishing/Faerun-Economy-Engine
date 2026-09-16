import json
import subprocess

from faerun.surveyassets import SURVEY_JS
from faerun.waterdeepassets import WATERDEEP_ASSETS, WATERDEEP_HTML, WATERDEEP_JS


def report(kind="streets"):
    return {
        "coordinate_space": {
            "width": 3560, "height": 7256, "units": "image_pixels", "origin": "top_left",
        },
        "coverage": {"complete": False},
        "limitations": ["Not a population census"],
        "features": [{
            "id": "street-1" if kind == "streets" else "roof-1",
            "properties": {"name": "High Road" if kind == "streets" else None, "status": "candidate"},
            "geometry": (
                {"type": "LineString", "coordinates": [[100, 200], [300, 600]]}
                if kind == "streets" else
                {"type": "Polygon", "coordinates": [[[100, 200], [140, 200], [140, 240], [100, 200]]]}
            ),
        }],
    }


def run_script(checks):
    source = SURVEY_JS.split("(function () {", 1)[1].rsplit("}());", 1)[0]
    setup = r"""
const assert = require('node:assert/strict');
class FakeElement {
  constructor() {
    this.children = []; this.dataset = {}; this.listeners = {};
    this.attributes = new Map(); this.value = ''; this.textContent = '';
    this.disabled = false; this.hidden = false; this.checked = false;
    const classes = new Set();
    this.classList = {
      add: name => classes.add(name), remove: name => classes.delete(name),
      contains: name => classes.has(name)
    };
  }
  addEventListener(name, callback) { this.listeners[name] = callback; }
  appendChild(child) { this.children.push(child); return child; }
  replaceChildren(...children) { this.children = children; }
  setAttribute(key, value) {
    this.attributes.set(key, String(value));
    if (key === 'class') String(value).split(' ').forEach(name => this.classList.add(name));
  }
  removeAttribute(key) { this.attributes.delete(key); }
  toggleAttribute(key, force) {
    if (force) this.setAttribute(key, ''); else this.removeAttribute(key);
  }
  closest(selector) { return this.classList.contains(selector.slice(1)) ? this : null; }
  scrollIntoView() {}
  click() {}
}
const elements = new Map();
globalThis.document = {
  getElementById(id) {
    if (!elements.has(id)) elements.set(id, new FakeElement());
    return elements.get(id);
  },
  createElement: () => new FakeElement(),
  createElementNS: () => new FakeElement(),
  createDocumentFragment: () => new FakeElement()
};
document.getElementById('survey-show-streets').checked = true;
globalThis.location = {href:'http://localhost/waterdeep.html?keep=yes', hash:'', search:''};
globalThis.history = {replaceState(a, b, url) { this.url = url; }};
globalThis.CustomEvent = class { constructor(type, options) { this.type = type; this.detail = options.detail; } };
globalThis.window = {events:[], dispatchEvent(event) { this.events.push(event); }};
"""
    data = "\nconst streetsFixture = " + json.dumps(report()) + ";\n"
    data += "const roofsFixture = " + json.dumps(report("roofs")) + ";\n"
    script = setup + data + source + "\n(async () => {\n" + checks + """
})().catch(error => { console.error(error); process.exitCode = 1; });
"""
    result = subprocess.run(["node", "-"], input=script, capture_output=True, text=True)
    assert result.returncode == 0, result.stdout + result.stderr


def test_survey_assets_use_native_coordinates_without_moving_existing_markers():
    assert "waterdeep-survey.js" in WATERDEEP_ASSETS
    assert 'src="waterdeep-map-hires.jpg"' in WATERDEEP_HTML
    assert WATERDEEP_HTML.count('preserveAspectRatio="none"') == 3
    for identifier in ("city-survey", "street-query", "survey-roofs-layer", "survey-streets-layer",
                       "survey-boundary-layer", "survey-roofs-download", "survey-streets-download"):
        assert f'id="{identifier}"' in WATERDEEP_HTML
    assert "var MAP_WIDTH = 768;" in WATERDEEP_JS
    assert "var MAP_HEIGHT = 1536;" in WATERDEEP_JS
    assert "waterdeep-focus-point" in WATERDEEP_JS
    assert "window.WaterdeepSurvey.searchStreet" in WATERDEEP_JS


def test_survey_rejects_invalid_coordinates_and_duplicate_features():
    run_script("""
assert.equal(validateReport(streetsFixture), streetsFixture);
const duplicate = structuredClone(streetsFixture);
duplicate.features.push(duplicate.features[0]);
assert.throws(() => validateReport(duplicate), /duplicate/);
const outside = structuredClone(streetsFixture);
outside.features[0].geometry.coordinates[0][0] = 3561;
assert.throws(() => validateReport(outside), /outside/);
const wrongProjection = structuredClone(streetsFixture);
wrongProjection.coordinate_space.units = 'longitude_latitude';
assert.throws(() => validateReport(wrongProjection), /coordinates/);
assert.throws(() => validateReport({}), /Invalid map survey/);
assert.equal(geometryPath(roofsFixture.features[0].geometry), 'M100,200 L140,200 L140,240 L100,200 Z');
""")


def test_street_selection_focuses_native_geometry_and_preserves_url_parameters():
    run_script("""
let calls = 0;
globalThis.fetch = async url => {
  calls++;
  assert.equal(url, '/api/streets?settlement=Waterdeep');
  return {ok:true, json:async () => streetsFixture};
};
await searchStreet('High Road');
assert.equal(calls, 1);
assert.ok(nodes.streets.get('street-1').classList.contains('selected'));
assert.equal(element('survey-feature-name').textContent, 'High Road');
assert.ok(element('survey-feature-details').textContent.includes('candidate'));
assert.equal(window.events[0].type, 'waterdeep-focus-point');
assert.equal(window.events[0].detail.x, 200 * 768 / 3560);
assert.equal(window.events[0].detail.y, 400 * 1536 / 7256);
assert.equal(history.url.searchParams.get('keep'), 'yes');
assert.equal(history.url.searchParams.get('street'), 'street-1');
await searchStreet('NOT A ROAD');
assert.equal(calls, 1);
assert.ok(element('street-result-count').textContent.startsWith('0 '));
assert.equal(window.events.length, 1);
""")


def test_partial_network_failure_does_not_hide_working_layer_or_change_population():
    run_script("""
element('resident-population').textContent = '200,000';
globalThis.fetch = async url => url.includes('/streets')
  ? {ok:true, json:async () => streetsFixture}
  : {ok:false, status:503};
await loadAll();
assert.ok(reports.streets);
assert.equal(reports.roofs, null);
assert.ok(element('survey-roofs-status').textContent.includes('503'));
assert.equal(element('survey-roofs-download').disabled, true);
assert.equal(element('survey-streets-download').disabled, false);
assert.equal(element('survey-load').disabled, false);
assert.equal(element('resident-population').textContent, '200,000');
globalThis.fetch = async () => ({ok:true, json:async () => roofsFixture});
await loadAll();
assert.ok(reports.roofs);
assert.equal(element('survey-roofs-download').disabled, false);
assert.ok(element('survey-roofs-layer').attributes.has('hidden'));
assert.equal(element('resident-population').textContent, '200,000');
""")


def test_feature_selection_does_not_intercept_pan_or_measure_gestures():
    run_script("""
globalThis.fetch = async () => ({ok:true, json:async () => streetsFixture});
await loadLayer('streets');
const target = nodes.streets.get('street-1');
const down = {target, button:0, shiftKey:false, pointerId:1, clientX:10, clientY:20};
viewport.listeners.pointerdown(down);
viewport.listeners.pointerup({...down, clientX:40});
assert.equal(selected, null);
viewport.listeners.pointerdown(down);
viewport.listeners.pointermove({...down, clientX:40});
viewport.listeners.pointerup(down);
assert.equal(selected, null);
viewport.classList.add('measuring');
viewport.listeners.pointerdown(down);
viewport.listeners.pointerup(down);
assert.equal(selected, null);
viewport.classList.remove('measuring');
viewport.listeners.pointerdown(down);
viewport.listeners.pointerup(down);
assert.equal(selected, target);
assert.equal(window.events.length, 0);
""")


def test_label_only_streets_remain_points_and_names_are_rendered_as_text():
    run_script("""
const labels = structuredClone(streetsFixture);
labels.features[0].properties.name = '<img src=x onerror=alert(1)>';
labels.features[0].geometry = {type:'Point', coordinates:[200, 300]};
globalThis.fetch = async () => ({ok:true, json:async () => labels});
await loadLayer('streets');
const node = nodes.streets.get('street-1');
assert.ok(node.classList.contains('survey-label-anchor'));
assert.equal(node.attributes.get('cx'), '200');
const button = element('street-results').children[0].children[0];
assert.equal(button.textContent, '<img src=x onerror=alert(1)> (label only)');
assert.ok(element('survey-streets-status').textContent.includes('labels only'));
""")


def test_real_estimate_is_visible_without_becoming_a_population_claim():
    from faerun.hires_survey import waterdeep_hires_report
    from faerun.streets import waterdeep_streets_report

    roofs = waterdeep_hires_report()
    streets = waterdeep_streets_report()
    # Full geometry is validated by its own tests; retain real metadata here.
    roofs["features"] = roofs["features"][:1]
    streets["features"] = streets["features"][:1]
    run_script(
        "const roofReport = " + json.dumps(roofs) + ";\n"
        "const streetReport = " + json.dumps(streets) + ";\n" + """
element('resident-population').textContent = '200,000';
renderMetadata('roofs', roofReport);
renderMetadata('streets', streetReport);
assert.ok(element('survey-estimate').textContent.includes((7567).toLocaleString()));
assert.ok(element('survey-estimate-uncertainty').textContent.includes('sampling-only 95%'));
assert.ok(element('survey-estimate-uncertainty').textContent.includes('not confidence bounds'));
assert.ok(element('survey-streets-status').textContent.includes('NOT fully verified or complete'));
assert.ok(element('survey-scale-status').textContent.includes('310 original image pixels = 1000 feet'));
assert.equal(element('resident-population').textContent, '200,000');
""")
