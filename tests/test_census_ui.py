import json
import subprocess

from faerun.census import BuildingFootprint, housing_census, waterdeep_housing_report
from faerun.waterdeepassets import WATERDEEP_HTML, WATERDEEP_JS


def run_census_script(checks):
    source = WATERDEEP_JS.split("  var censusReport = null;", 1)[1].split(
        "  image.addEventListener", 1)[0]
    escape = "function escapeHtml(value)" + WATERDEEP_JS.split(
        "function escapeHtml(value)", 1)[1].split("  function selectPlace", 1)[0]
    script = """
const assert = require('node:assert/strict');
const elements = new Map();
function element(id) {
  if (!elements.has(id)) elements.set(id, {
    textContent:'', innerHTML:'', disabled:false, hidden:false, listeners:{},
    addEventListener(name, callback) { this.listeners[name] = callback; }
  });
  return elements.get(id);
}
globalThis.document = {getElementById: element};
globalThis.location = {hash:''};
var censusReport = null;
""" + escape + source + "\n(async () => {\n" + checks + """
})().catch(error => {console.error(error); process.exitCode = 1;});
"""
    result = subprocess.run(["node", "-"], input=script, capture_output=True, text=True)
    assert result.returncode == 0, result.stdout + result.stderr


def test_census_panel_is_on_demand_and_has_coverage_and_download_controls():
    for element in ("housing-census", "census-load", "census-download", "census-status",
                    "census-wards", "census-blockers", "census-assumptions", "census-survey"):
        assert f'id="{element}"' in WATERDEEP_HTML
    assert 'aria-label="Ward-level housing census"' in WATERDEEP_HTML
    assert "if (location.hash === '#housing-census')" in WATERDEEP_JS
    assert "waterdeep-housing-census.json" in WATERDEEP_JS


def test_partial_census_does_not_display_missing_population_as_zero():
    report = housing_census(
        [BuildingFootprint("candidate", None, None)], coverage_complete=False,
        overlaps_resolved=False, class_a_complete=False)
    report["survey"] = {"note": "Source <not census>"}
    report["blockers"].append("<unverified roofs>")
    run_census_script("const report = " + json.dumps(report) + ";\n" + """
renderHousingCensus(report);
assert.ok(element('census-status').textContent.includes('population withheld'));
assert.ok(element('census-summary').textContent.includes('No resident estimate'));
assert.ok(element('census-summary').textContent.includes('0 visually reviewed roofs'));
assert.ok(element('census-wards').innerHTML.includes('Not surveyed'));
assert.ok(element('census-wards').innerHTML.includes('Unknown'));
assert.ok(element('census-blockers').innerHTML.includes('&lt;unverified roofs&gt;'));
assert.ok(!element('census-blockers').innerHTML.includes('<unverified roofs>'));
assert.ok(element('census-survey').textContent.includes('Source <not census>'));
assert.equal(element('census-results').hidden, false);
""")


def test_complete_census_and_download_remain_separate_from_active_population():
    report = housing_census(
        [BuildingFootprint("roof", "castle", 1000, True, "C")],
        coverage_complete=True, overlaps_resolved=True, class_a_complete=True)
    report["survey"] = {}
    run_census_script("const report = " + json.dumps(report) + ";\n" + """
element('resident-population').textContent = '200,000';
globalThis.fetch = async path => {
  assert.equal(path, '/api/census?settlement=Waterdeep');
  return {ok:true, json:async () => report};
};
await loadHousingCensus();
assert.equal(censusReport, report);
assert.equal(element('census-download').disabled, false);
assert.equal(element('census-load').disabled, false);
assert.ok(element('census-summary').textContent.includes('Modeled city residents'));
assert.ok(element('census-status').textContent.includes('has not changed the active population'));
assert.equal(element('resident-population').textContent, '200,000');
globalThis.fetch = async () => ({ok:false, status:503});
await loadHousingCensus();
assert.equal(censusReport, null);
assert.equal(element('census-download').disabled, true);
assert.equal(element('census-results').hidden, true);
assert.ok(element('census-status').textContent.includes('503'));
globalThis.fetch = async () => ({ok:true, json:async () => ({})});
await loadHousingCensus();
assert.ok(element('census-status').textContent.includes('Invalid housing census response'));
assert.equal(element('census-download').disabled, true);
""")


def test_expanded_survey_exposes_input_readiness_without_inventing_occupancy():
    report = waterdeep_housing_report()
    run_census_script("const report = " + json.dumps(report) + ";\n" + """
renderHousingCensus(report);
assert.ok(element('census-summary').textContent.includes('156 visually reviewed roofs'));
assert.ok(element('census-summary').textContent.includes('0 usable for housing calculations'));
const readiness = element('census-readiness').textContent;
assert.ok(readiness.includes('with a ward: 26'));
assert.ok(readiness.includes('with a physical area: 0'));
assert.ok(readiness.includes('with both: 0'));
assert.ok(readiness.includes('unknown occupancy: 26'));
assert.ok(readiness.includes('counts overlap'));
assert.ok(element('census-wards').innerHTML.includes('City of the Dead'));
assert.ok(element('census-status').textContent.includes('population withheld'));
""")
