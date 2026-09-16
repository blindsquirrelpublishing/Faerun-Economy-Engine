import json
import subprocess
from html.parser import HTMLParser

import pytest

from faerun.locationassets import LOCATION_HTML
from faerun.locationgenassets import (
    LOCATION_GENERATOR_ASSETS,
    LOCATION_GENERATOR_CSS,
    LOCATION_GENERATOR_HTML,
    LOCATION_GENERATOR_JS,
)
from test_city_directory_ui import HARNESS
from test_requirements_ui import run_location_script


PROFILES = {
    "schema_version": 1,
    "basis": "engine_assumptions",
    "profiles": [
        {
            "id": profile_id,
            "name": name,
            "description": description,
            "class_weights": weights,
            "condition_modifier": modifier,
        }
        for profile_id, name, description, weights, modifier in [
            ("village", "Village", "Assumed ordinary village buildings", {"B": 0, "C": 20, "D": 80}, -1),
            ("town", "Town", "Assumed ordinary town buildings", {"B": 10, "C": 50, "D": 40}, 0),
            ("city", "City", "Assumed ordinary city buildings", {"B": 30, "C": 50, "D": 20}, 1),
            ("port", "Port", "Assumed ordinary port buildings", {"B": 15, "C": 55, "D": 30}, 0),
            ("fortress", "Fortress", "Supporting ordinary buildings only", {"B": 20, "C": 60, "D": 20}, 1),
        ]
    ],
}


def generated_payload():
    return {
        "schema_version": 1,
        "generated": True,
        "surveyed": False,
        "live_market_integration": False,
        "can_replace_population": False,
        "location": {"id": "custom_place", "name": "A <custom> & port", "basis": "user_supplied_label"},
        "profile": dict(PROFILES["profiles"][3], basis="engine_assumptions"),
        "parameters": {
            "location": "A <custom> & port", "profile": "port", "count": 2, "seed": 1357,
            "footprint_sqft": 1000, "scenario": "central", "class_b_weight": 15,
            "class_c_weight": 55, "class_d_weight": 30, "condition_modifier": 0,
        },
        "source": {"title": "City System", "publication_year": 1988, "era_note": "Historical rules; not a survey."},
        "occupancy_scenario": {"id": "central", "basis": "Modeled <occupancy>"},
        "assumptions": ["No named occupants.", "Assumed <not surveyed> footprints.", "No live changes."],
        "summary": {
            "buildings": 2, "resolved_buildings": 2, "unresolved_buildings": 0, "classes": {"B": 1, "C": 1},
            "modeled_residents_in_resolved_buildings": 9, "modeled_guests_in_resolved_buildings": 4,
            "modeled_staff_in_resolved_buildings": 2, "city_population": None,
        },
        "buildings": [
            {
                "id": f"generated_{index}", "label": f"Building <{index}>", "building_class": building_class,
                "class_basis": "profile_assumption", "provenance": "generated_scenario", "status": "generated",
                "location_id": "custom_place", "location_name": "A <custom> & port", "ward": None,
                "rolls": {"class_d100": 10, "stories_die": "d4", "stories_roll": 2, "condition_d8": 3,
                          "condition_modifier": 0, "condition_adjusted": 3, "use_d10": 2, "proprietor_d4": 1},
                "assumed_footprint_sqft": 1000, "map_position": None, "historical_business_id": None,
                "structure": {"stories": 2, "basement": True, "tower_or_partial_upper": index == 1},
                "condition": "Good <condition>", "use": {"id": "shop", "label": "Shop <use>", "proprietor_lives_above": True},
                "occupants": {"residents": 4 if index == 1 else 5, "lodging_guests": 2, "staff": 1,
                              "staff_roles": {"keeper": 1}, "occupied_household_sized_units": 1,
                              "household_sized_unit_capacity": 2, "named_people": []},
                "citations": [{"printed_page": 10, "pdf_page": 11, "note": "Source <citation>"}],
                "warnings": ["Assumption <warning>"] if index == 1 else [],
            }
            for index, building_class in [(1, "B"), (2, "C")]
        ],
    }


LOCATION_HARNESS = r"""
Element.prototype.setAttribute = function (key, value) {
  if (!this.attributes) this.attributes = {};
  this.attributes[key] = value;
};
Object.defineProperty(Element.prototype, 'options', {get() { return this.children; }});
globalThis.location = new URL('http://localhost/location-generator.html?scoutTheme=dark#settings');
const controls = ['location', 'profile', 'count', 'seed', 'footprint_sqft', 'scenario',
  'class_b_weight', 'class_c_weight', 'class_d_weight', 'condition_modifier'];
['village', 'town', 'city', 'port', 'fortress'].forEach(value =>
  node('location-profile').add(new Option(value, value)));
['low', 'central', 'high'].forEach(value =>
  node('location-scenario').add(new Option(value, value)));
const defaults = {location: '', profile: 'town', count: '20', seed: '1357',
  footprint_sqft: '1000', scenario: 'central'};
controls.forEach(field => { node('location-' + field).value = defaults[field] || ''; });
['count', 'seed', 'footprint_sqft', 'class_b_weight', 'class_c_weight', 'class_d_weight',
 'condition_modifier'].forEach(field => {
  const control = node('location-' + field);
  let value = control.value;
  Object.defineProperty(control, 'value', {
    get() { return value; },
    set(raw) {
      const text = String(raw);
      value = text === '' || /^-?(?:[0-9]+(?:\.[0-9]*)?|\.[0-9]+)(?:[eE][+-]?[0-9]+)?$/.test(text) ? text : '';
    }
  });
});
node('location-generator-download').disabled = true;
node('location-generator-output').hidden = true;
function edit(field, value, eventName = 'input') {
  const control = node('location-' + field);
  control.value = value;
  if (control.listeners[eventName]) control.listeners[eventName]();
  node('location-generator-form').listeners[eventName]();
}
function customMix(checked) {
  node('location-custom-mix').checked = checked;
  node('location-custom-mix').listeners.change();
  node('location-generator-form').listeners.change();
}
function submit() { node('location-generator-form').listeners.submit({preventDefault() {}}); }
function params(request) { return new URL(request.url, location).searchParams; }
function textTree(root) {
  return [String(root.textContent), ...root.children.map(textTree)].join(' ');
}
"""


def run_location_generator_script(body, setup=""):
    script = HARNESS + LOCATION_HARNESS
    script += "\nconst catalog = " + json.dumps(PROFILES) + ";"
    script += "\nconst generated = " + json.dumps(generated_payload()) + ";"
    script += "\n" + setup + "\n" + LOCATION_GENERATOR_JS
    script += "\n(async () => {\n" + body
    script += "\n})().catch(error => { console.error(error); process.exitCode = 1; });"
    result = subprocess.run(
        ["node", "-"], input=script, text=True, encoding="utf-8",
        capture_output=True, timeout=20,
    )
    assert result.returncode == 0, result.stdout + result.stderr


class ControlsParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.elements = {}
        self.labels = set()

    def handle_starttag(self, tag, attrs):
        values = dict(attrs)
        if "id" in values:
            assert values["id"] not in self.elements, "Control IDs must be unique"
            self.elements[values["id"]] = values
        if tag == "label":
            self.labels.add(values["for"])


def test_page_assets_defaults_bounds_accessibility_and_scope():
    assert set(LOCATION_GENERATOR_ASSETS) == {
        "location-generator.html", "location-generator.css", "location-generator.js",
    }
    assert LOCATION_GENERATOR_ASSETS["location-generator.html"] == (
        LOCATION_GENERATOR_HTML, "text/html; charset=utf-8",
    )
    assert 'src="location-generator.js" defer' in LOCATION_GENERATOR_HTML
    assert 'href="location-generator.css"' in LOCATION_GENERATOR_HTML
    assert 'href="index.html"' in LOCATION_GENERATOR_HTML
    assert 'href="map.html"' in LOCATION_GENERATOR_HTML
    parser = ControlsParser()
    parser.feed(LOCATION_GENERATOR_HTML)
    for field, bounds in {
        "count": ("1", "100", "20"), "seed": ("0", "4294967295", "1357"),
        "footprint_sqft": ("1", "1000000", "1000"), "condition_modifier": ("-1", "1", None),
        "class_b_weight": ("0", "100", None), "class_c_weight": ("0", "100", None),
        "class_d_weight": ("0", "100", None),
    }.items():
        control = parser.elements["location-" + field]
        assert tuple(control.get(key) for key in ("min", "max", "value")) == bounds
        assert control["step"] == "1"
        assert "location-" + field in parser.labels
    for field in ("location", "profile", "scenario", "custom-mix"):
        assert "location-" + field in parser.labels
    assert parser.elements["location-location"]["maxlength"] == "120"
    assert "required" in parser.elements["location-location"]
    assert "novalidate" in parser.elements["location-generator-form"]
    assert '<option value="town" selected>' in LOCATION_GENERATOR_HTML
    assert '<option value="central" selected>' in LOCATION_GENERATOR_HTML
    assert 'aria-live="polite"' in LOCATION_GENERATOR_HTML
    assert 'scope="col"' in LOCATION_GENERATOR_HTML
    for text in (
        "any named location", "No invented names", "engine assumptions, not source facts",
        "automatic population fitting", "live economy, population, census, or lore",
        "fortifications, and the garrison", "sum to 100", "not additive",
    ):
        assert text in LOCATION_GENERATOR_HTML
    assert "innerHTML" not in LOCATION_GENERATOR_JS
    assert "textContent" in LOCATION_GENERATOR_JS
    assert "overflow: auto" in LOCATION_GENERATOR_CSS
    assert "[hidden]" in LOCATION_GENERATOR_CSS
    assert "focus-visible" in LOCATION_GENERATOR_CSS


def test_catalog_defaults_are_fetched_and_generation_is_explicit():
    run_location_generator_script(r"""
assert.equal(requests.length, 1);
assert.equal(requests[0].url, '/api/location-profiles');
assert.ok(node('location-profile-defaults').textContent.includes('Loading profile'));
assert.equal(node('location-generator-download').disabled, true);
assert.equal(node('location-mix-fields').disabled, true);
await respond(requests[0], catalog);
assert.ok(node('location-profile-defaults').textContent.includes('Class B: 10%, C: 50%, D: 40%'));
assert.ok(node('location-profile-defaults').textContent.includes('condition modifier: 0'));
assert.equal(node('location-class_b_weight').value, '10');
assert.equal(requests.length, 1, 'loading defaults must not generate a scenario');
assert.equal(node('location-condition_modifier').value, '');
edit('profile', 'fortress', 'change');
assert.ok(node('location-profile-defaults').textContent.includes('Supporting ordinary buildings only'));
assert.ok(node('location-profile-defaults').textContent.includes('Class B: 20%, C: 60%, D: 20%'));
assert.ok(node('location-profile-defaults').textContent.includes('condition modifier: 1'));
edit('location', 'A custom place');
submit();
assert.deepEqual(Object.fromEntries(params(requests[1])), {
  location: 'A custom place', profile: 'fortress', count: '20', seed: '1357',
  footprint_sqft: '1000', scenario: 'central'
});
""")


def test_loading_render_safe_text_effective_url_and_json_export():
    run_location_generator_script(r"""
await respond(requests[0], catalog);
edit('location', 'A <custom> & port');
edit('profile', 'port', 'change');
edit('count', '2');
submit();
assert.equal(node('location-generator-download').disabled, true);
assert.equal(node('location-generator-output').attributes['aria-busy'], 'true');
assert.ok(node('location-generator-status').textContent.includes('Generating'));
assert.equal(params(requests[1]).get('location'), 'A <custom> & port');
await respond(requests[1], generated);
assert.equal(node('location-generator-output').hidden, false);
assert.equal(node('location-generator-output').attributes['aria-busy'], 'false');
assert.equal(node('location-generator-results').children.length, 2);
assert.equal(node('result-title').textContent, 'A <custom> & port — generated scenario');
const row = node('location-generator-results').children[0];
assert.equal(row.children[0].children[0].textContent, 'Building <1>');
assert.equal(row.children[1].textContent, 'Class B / Shop <use>');
assert.ok(row.children[2].textContent.includes('tower or partial upper floor'));
assert.equal(row.children[3].textContent, '4');
assert.ok(textTree(row).includes('Source <citation>'));
assert.ok(textTree(row).includes('Assumption <warning>'));
assert.ok(textTree(row).includes('"named_people": []'));
assert.ok(node('location-generator-summary').textContent.includes('B: 1, C: 1'));
assert.ok(node('location-generator-summary').textContent.includes('City population: not estimated'));
assert.ok(node('location-generator-summary').textContent.includes('not additive'));
assert.ok(node('location-generator-summary').textContent.includes('No live economy'));
assert.ok(node('location-generator-effective').textContent.includes('Class B: 15%, C: 55%, D: 30%'));
assert.ok(node('location-generator-source').textContent.includes('printed pp. 10'));
assert.ok(node('location-generator-provenance').textContent.includes('Modeled <occupancy>'));
assert.equal(node('location-generator-assumptions').children[1].textContent, 'Assumed <not surveyed> footprints.');
assert.equal(node('location-generator-download').disabled, false);
Object.entries(generated.parameters).forEach(([key, value]) =>
  assert.equal(location.searchParams.get(key), String(value), key));
assert.equal(location.searchParams.get('scoutTheme'), 'dark');
assert.equal(location.hash, '#settings');
node('location-generator-download').click();
assert.deepEqual(JSON.parse(await downloads[0].text()), generated);
submit();
assert.equal(node('location-generator-download').disabled, true, 'reloading disables the previous download');
assert.equal(node('location-generator-output').hidden, true);
assert.equal(node('location-generator-source').textContent, '');
assert.equal(node('location-generator-assumptions').children.length, 0);
await respond(requests[2], {error: 'Count must be an integer'}, false);
assert.ok(node('location-generator-status').textContent.includes('Count must be an integer'));
assert.equal(node('location-generator-download').disabled, true);
assert.equal(node('location-generator-output').attributes['aria-busy'], 'false');
node('location-generator-download').click();
assert.equal(downloads.length, 1, 'failed requests cannot export the previous snapshot');
""")


def test_custom_mix_uses_catalog_values_and_sends_all_three_overrides():
    run_location_generator_script(r"""
await respond(requests[0], catalog);
customMix(true);
assert.equal(node('location-mix-fields').disabled, false);
assert.equal(node('location-mix-fields').hidden, false);
edit('location', 'Home');
edit('class_b_weight', '0');
edit('class_c_weight', '60');
edit('class_d_weight', '40');
edit('condition_modifier', '-1');
submit();
assert.equal(params(requests[1]).get('class_b_weight'), '0');
assert.equal(params(requests[1]).get('class_c_weight'), '60');
assert.equal(params(requests[1]).get('class_d_weight'), '40');
assert.equal(params(requests[1]).get('condition_modifier'), '-1');
edit('profile', 'village', 'change');
assert.equal(node('location-class_c_weight').value, '60', 'profile changes preserve explicit custom overrides');
customMix(false);
edit('condition_modifier', '');
submit();
assert.equal(params(requests[2]).has('class_b_weight'), false);
assert.equal(params(requests[2]).has('condition_modifier'), false);
customMix(true);
assert.equal(node('location-class_c_weight').value, '20', 'turning custom mix off restores catalog values');
edit('class_d_weight', '');
submit();
assert.equal(params(requests[3]).get('class_d_weight'), '', 'incomplete custom mix must reach validation');
await respond(requests[3], {error: 'Supply all three integer percentages summing to 100'}, false);
assert.ok(node('location-generator-status').textContent.includes('all three integer percentages'));
""")


@pytest.mark.parametrize("event_name", ["input", "change"])
def test_editing_invalidates_export_and_aborts_pending_results(event_name):
    run_location_generator_script(r"""
await respond(requests[0], catalog);
edit('location', 'First');
submit();
await respond(requests[1], generated);
assert.equal(node('location-generator-download').disabled, false);
edit('count', '5', EVENT_NAME);
assert.equal(node('location-generator-download').disabled, true);
assert.equal(node('location-generator-results').children.length, 0);
assert.ok(node('location-generator-status').textContent.includes('Settings changed'));
submit();
edit('count', '6', EVENT_NAME);
assert.equal(requests[2].options.signal.aborted, true);
await respond(requests[2], generated);
assert.equal(node('location-generator-download').disabled, true);
assert.equal(node('location-generator-results').children.length, 0);
assert.ok(node('location-generator-status').textContent.includes('Settings changed'));
""", setup="const EVENT_NAME = " + json.dumps(event_name) + ";")


@pytest.mark.parametrize("stale_failure", [False, True])
def test_latest_request_wins_over_stale_success_or_error(stale_failure):
    run_location_generator_script(r"""
await respond(requests[0], catalog);
submit();
submit();
assert.equal(requests[1].options.signal.aborted, true);
const latest = structuredClone(generated); latest.location.name = 'Latest location';
await respond(requests[2], latest);
await respond(requests[1], STALE_FAILURE ? {error: 'Stale failure'} : generated, !STALE_FAILURE);
assert.ok(node('location-generator-status').textContent.includes('Latest location'));
assert.equal(node('result-title').textContent, 'Latest location — generated scenario');
assert.equal(node('location-generator-download').disabled, false);
node('location-generator-download').click();
assert.deepEqual(JSON.parse(await downloads[0].text()), latest);
""", setup="const STALE_FAILURE = " + json.dumps(stale_failure) + ";")


def test_raw_invalid_deep_links_are_retained_until_the_specific_control_is_edited():
    run_location_generator_script(r"""
assert.equal(requests.length, 1, 'even invalid deep links prefill only');
assert.equal(node('location-count').value, '', 'number input sanitization is modeled by the harness');
assert.equal(node('location-profile').value, '<unsupported>');
assert.ok(node('location-profile').options.some(option => option.textContent === 'Unsupported value: <unsupported>'));
assert.equal(node('location-advanced').open, true);
await respond(requests[0], catalog);
assert.ok(node('location-profile-defaults').textContent.includes('Unsupported profile: <unsupported>'));
edit('location', 'Edited label');
submit();
assert.equal(params(requests[1]).get('profile'), '<unsupported>');
assert.equal(params(requests[1]).get('scenario'), 'impossible');
assert.equal(params(requests[1]).get('count'), 'bad-number');
assert.equal(params(requests[1]).get('class_b_weight'), 'bad-weight');
assert.equal(params(requests[1]).get('class_c_weight'), '');
assert.equal(params(requests[1]).get('class_d_weight'), '');
assert.equal(params(requests[1]).get('condition_modifier'), '');
await respond(requests[1], {error: 'Unsupported profile <unsupported>'}, false);
assert.ok(node('location-generator-status').textContent.includes('Unsupported profile <unsupported>'));
assert.equal(location.searchParams.get('count'), 'bad-number', 'failed generation must not rewrite URL state');
submit();
assert.equal(params(requests[2]).get('count'), 'bad-number', 'invalid raw state survives retries');
edit('profile', 'port', 'change');
edit('scenario', 'central', 'change');
edit('count', '2');
customMix(false);
edit('condition_modifier', '');
submit();
assert.equal(params(requests[3]).get('profile'), 'port');
assert.equal(params(requests[3]).get('count'), '2');
assert.equal(params(requests[3]).has('class_b_weight'), false);
assert.equal(params(requests[3]).has('condition_modifier'), false);
await respond(requests[3], generated);
assert.equal(node('location-generator-download').disabled, false);
""", setup="globalThis.location = new URL(" + json.dumps(
        "http://localhost/location-generator.html?location=Old&profile=%3Cunsupported%3E"
        "&scenario=impossible&count=bad-number&class_b_weight=bad-weight&condition_modifier="
    ) + ");")


def test_valid_deep_link_prefills_and_preserves_effective_values_before_catalog_load():
    query = "&".join(
        f"{key}={value}" for key, value in {
            "location": "Neverwinter", "profile": "port", "count": "20", "seed": "0",
            "footprint_sqft": "1000000", "scenario": "high",
            "class_b_weight": "0", "class_c_weight": "100", "class_d_weight": "0",
            "condition_modifier": "-1",
        }.items()
    )
    run_location_generator_script(r"""
assert.equal(requests.length, 1);
assert.equal(node('location-location').value, 'Neverwinter');
assert.equal(node('location-profile').value, 'port');
assert.equal(node('location-custom-mix').checked, true);
assert.equal(node('location-class_b_weight').value, '0');
submit();
assert.equal(params(requests[1]).get('seed'), '0');
assert.equal(params(requests[1]).get('footprint_sqft'), '1000000');
assert.equal(params(requests[1]).get('class_b_weight'), '0');
assert.equal(params(requests[1]).get('class_c_weight'), '100');
assert.equal(params(requests[1]).get('condition_modifier'), '-1');
await respond(requests[0], catalog);
assert.equal(node('location-class_c_weight').value, '100', 'late catalog must not replace URL overrides');
assert.equal(node('location-generator-output').attributes['aria-busy'], 'true', 'catalog is independent of generation');
""", setup="globalThis.location = new URL(" + json.dumps(
        "http://localhost/location-generator.html?" + query
    ) + ");")


def test_catalog_failure_can_retry_and_does_not_prevent_server_generation():
    run_location_generator_script(r"""
await respond(requests[0], {error: 'Catalog <unavailable>'}, false);
assert.ok(node('location-profile-defaults').textContent.includes('Catalog <unavailable>'));
assert.equal(node('location-profiles-retry').hidden, false);
edit('location', 'Anywhere');
submit();
await respond(requests[1], generated);
assert.equal(node('location-generator-download').disabled, false);
node('location-profiles-retry').click();
assert.equal(requests[2].url, '/api/location-profiles');
await respond(requests[2], catalog);
assert.equal(node('location-profiles-retry').hidden, true);
assert.ok(node('location-profile-defaults').textContent.includes('Class B: 15%'));
assert.equal(node('location-generator-download').disabled, false);
""")


def test_network_and_invalid_json_errors_clear_stale_downloads_and_allow_retry():
    run_location_generator_script(r"""
await respond(requests[0], catalog);
submit();
requests[1].resolve({ok: true, json: async () => { throw new Error('Invalid JSON'); }});
await tick();
assert.ok(node('location-generator-status').textContent.includes('Invalid JSON'));
assert.equal(node('location-generator-download').disabled, true);
submit();
await respond(requests[2], generated);
assert.equal(node('location-generator-download').disabled, false);
globalThis.fetch = async () => { throw new Error('Network unavailable'); };
submit();
await tick();
assert.ok(node('location-generator-status').textContent.includes('Network unavailable'));
assert.equal(node('location-generator-download').disabled, true);
assert.equal(node('location-generator-results').children.length, 0);
""")


def test_unresolved_occupants_render_unknown_not_zero():
    run_location_generator_script(r"""
await respond(requests[0], catalog);
submit();
generated.buildings[0].structure = null;
generated.buildings[0].use = null;
generated.buildings[0].occupants = null;
generated.buildings[0].warnings = ['Unresolved source roll; no reroll.'];
generated.summary.resolved_buildings = 1; generated.summary.unresolved_buildings = 1;
await respond(requests[1], generated);
const row = node('location-generator-results').children[0];
assert.equal(row.children[1].textContent, 'Unresolved source roll');
assert.deepEqual(row.children.slice(3).map(cell => cell.textContent), ['Unknown', 'Unknown', 'Unknown']);
assert.ok(textTree(row).includes('Unresolved source roll; no reroll.'));
assert.ok(node('location-generator-summary').textContent.includes('1 unresolved'));
""")


def test_every_location_links_to_generator_with_actual_name_and_safe_encoding():
    assert 'id="location-generator-link"' in LOCATION_HTML
    assert "Generate buildings (separate scenario)" in LOCATION_HTML
    run_location_script(r"""
ui.loadSettlement('baldur_s_gate');
assert.equal(element('location-generator-link').hidden, false);
assert.equal(element('location-generator-link').href, 'location-generator.html?location=baldur_s_gate');
const canonical = detail("Baldur's Gate & <harbor>", 17910, requirements());
canonical.market.settlement = "Baldur's Gate & <harbor>";
pending('/api/location?')[0].respond(canonical);
await tick();
assert.equal(new URL(element('location-generator-link').href, 'http://localhost/').searchParams.get('location'),
  "Baldur's Gate & <harbor>", 'resolved display name must replace the internal ID');
ui.loadSettlement('Neverwinter');
assert.equal(new URL(element('location-generator-link').href, 'http://localhost/').searchParams.get('location'),
  'Neverwinter', 'navigating must not retain the previous location');
ui.loadSettlement('Custom & <location>');
assert.equal(element('location-generator-link').href,
  'location-generator.html?location=Custom%20%26%20%3Clocation%3E');
""")


def test_generator_link_resolves_bootstrap_ids_before_market_data_and_ignores_stale_details():
    run_location_script(r"""
window.location.search = '?settlement=baldur_s_gate';
ui.start();
pending('/api/bootstrap')[0].respond({settlements: [
  {id: 'baldur_s_gate', name: "Baldur's Gate", region: 'Sword Coast'},
  {id: 'neverwinter', name: 'Neverwinter', region: 'Sword Coast'}
], categories: []});
pending('/api/chronicle')[0].respond({today: 100});
await tick();
assert.equal(new URL(element('location-generator-link').href, 'http://localhost/').searchParams.get('location'),
  "Baldur's Gate", 'initial link must use a name, not the internal settlement ID');
ui.loadSettlement('neverwinter');
assert.equal(new URL(element('location-generator-link').href, 'http://localhost/').searchParams.get('location'),
  'Neverwinter');
const stale = detail("Baldur's Gate", 100, requirements());
stale.market.settlement = "Baldur's Gate";
pending('/api/location?')[0].respond(stale);
await tick();
assert.equal(new URL(element('location-generator-link').href, 'http://localhost/').searchParams.get('location'),
  'Neverwinter', 'late responses must not retarget the generator link');
""")
