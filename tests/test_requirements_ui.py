import json
import subprocess

from faerun.locationassets import LOCATION_CSS, LOCATION_HTML, LOCATION_JS
from faerun.webassets import WORLD_DATE_JS


def test_material_status_ignores_floating_point_residue():
    run_location_script("""
const data = requirements();
data.materials[0] = material({
  unmet_per_day: 1e-12, closing_stock: 6e-16,
  sectors: {}, final_demand_per_day: 0
});
ui.state.settlement = 'Waterdeep';
ui.state.detail = detail('Waterdeep', 17910, data);
ui.renderRequirements(data);
ui.state.materialFilter = 'unmet';
ui.renderRequirementsTable();
assert.equal(ui.el['requirements-count'].textContent, '0 of 2 materials');
const details = ui.materialDetails(data.materials[0]);
assert.ok(details.includes('No final-use demand'));
assert.ok(!details.includes('e-16'));
""")


def test_population_scenario_and_comparison_are_visible_and_escaped():
    run_location_script("""
const data = requirements();
data.profile.population = 200000;
data.profile.population_model = {
  scope: 'City proper <residents>', rationale: 'Scenario <not census>',
  comparison_residents: 130000, household_demand_multiplier: 200000 / 130000,
  assumptions: ['External visitors unknown'],
  evidence: [{title: 'Shared <source>', period: 'Mixed editions',
              description: 'Territory is not additional city consumers',
              url: 'https://example.com/?a=1&b=2'}]
};
ui.renderRequirements(data);
const cards = ui.el['requirements-profile'].innerHTML;
assert.ok(cards.includes('Resident population'));
assert.ok(cards.includes('200,000'));
assert.ok(cards.includes('excludes visitors'));
const notes = ui.el['requirements-assumptions'].innerHTML;
assert.ok(notes.includes('130,000'));
assert.ok(notes.includes('Scenario &lt;not census&gt;'));
assert.ok(notes.includes('Shared &lt;source&gt;'));
assert.ok(notes.includes('External visitors unknown'));
assert.ok(notes.includes('Prices do not scale linearly'));
assert.ok(!notes.includes('City proper <residents>'));
""")


def test_requirements_dashboard_preserves_existing_views_and_accessible_controls():
    for element_id in (
        "requirements-board",
        "requirements-profile",
        "requirements-assumptions",
        "requirements-establishments",
        "requirements-defense",
        "requirements-resources",
        "requirements-output",
        "requirements-services",
        "requirements-summary",
        "requirements-search",
        "requirements-filter",
        "requirements-download",
        "requirements-table",
        "price-table",
        "businesses",
        "timeline-status",
        "load-history",
        "history-chart",
    ):
        assert f'id="{element_id}"' in LOCATION_HTML
    assert 'for="requirements-search"' in LOCATION_HTML
    assert 'for="requirements-filter"' in LOCATION_HTML
    assert 'aria-label="Daily material requirements"' in LOCATION_HTML
    assert 'aria-live="polite"' in LOCATION_HTML
    assert "not canonical census or named businesses" in LOCATION_HTML
    assert "not proven owned inventory" in LOCATION_HTML
    assert "not additive to labor-based establishment counts" in LOCATION_HTML
    assert "Load seven-year price history" in LOCATION_HTML
    assert "84 monthly balances" in LOCATION_HTML
    assert "may take several minutes" in LOCATION_HTML
    assert 'aria-describedby="history-warning"' in LOCATION_HTML
    for panel in ("defense", "resources", "output"):
        assert f'<details id="requirements-{panel}-section"' in LOCATION_HTML
    assert "Import need" in LOCATION_HTML
    assert "Allocated imports" in LOCATION_HTML
    assert "Still unmet" in LOCATION_HTML
    assert "Planned capacity/day" in LOCATION_HTML
    assert "scheduled production plan, not maximum idle factory capacity" in LOCATION_HTML
    assert "conservative local footprint only" in LOCATION_HTML
    assert "Baseline / day" in LOCATION_HTML
    assert "Market demand / day" in LOCATION_HTML
    assert "overflow: auto" in LOCATION_CSS
    assert ".requirements-board [hidden] { display: none; }" in LOCATION_CSS
    assert "\\" not in LOCATION_JS
    assert "\\" not in LOCATION_CSS


NODE_HARNESS = r"""
const assert = require('node:assert/strict');
const elements = new Map();
const requests = [];
const timers = new Map();
const history = [];
let timerId = 0;
class Element {
  constructor(id) {
    this.id = id;
    this.innerHTML = '';
    this.textContent = '';
    this.value = '';
    this.hidden = false;
    this.disabled = false;
    this.attributes = {};
    this.listeners = {};
    this.classList = {
      toggle: (name, enabled) => { this.attributes[name] = enabled; }
    };
  }
  querySelector(selector) { return element(this.id + '/' + selector); }
  querySelectorAll() { return []; }
  setAttribute(name, value) { this.attributes[name] = value; }
  getAttribute(name) { return this.attributes[name]; }
  addEventListener(name, callback) { this.listeners[name] = callback; }
  getContext() { return new Proxy({}, { get: () => () => {} }); }
}
function element(id) {
  if (!elements.has(id)) elements.set(id, new Element(id));
  return elements.get(id);
}
globalThis.document = {
  getElementById: element,
  querySelectorAll: () => [],
  documentElement: {},
  createElement: () => ({ click() {}, remove() {} }),
  body: { appendChild() {} }
};
globalThis.window = {
  location: { search: '' },
  devicePixelRatio: 1,
  history: { replaceState: (state, title, url) => history.push(url) },
  addEventListener() {},
  setTimeout: callback => { timers.set(++timerId, callback); return timerId; },
  clearTimeout: id => timers.delete(id)
};
globalThis.getComputedStyle = () => ({ getPropertyValue: () => '#123456' });
globalThis.fetch = (path, options) => new Promise((resolve, reject) => {
  requests.push({
    path, options, reject,
    respond: body => resolve({ ok: true, text: () => Promise.resolve(JSON.stringify(body)) })
  });
});
function pending(prefix) { return requests.filter(request => request.path.startsWith(prefix)); }
function tick() { return new Promise(resolve => setImmediate(resolve)); }
function detail(name, month, requirements) {
  return {
    month, label: name + ' month ' + month, season: 'Summer',
    market: { living_standard: 'comfortable', population: 100, prices: [], daily_requirements: [] },
    events: [], goods_moved: 0, requirements
  };
}
function timeline(name, first, last) {
  return {
    settlement: name, settlement_id: name.toLowerCase(), region: 'Test region', basket: [],
    first_month: first, last_month: last, events: [], analysis: null,
    series: Array.from({length: last - first + 1}, (_, index) => ({
      month: first + index, label: name + ' month ' + (first + index),
      season: 'Summer', year: 1490, index: 1, events: []
    }))
  };
}
function material(overrides = {}) {
  return {
    commodity_id: 'bread', commodity: 'Bread <fine>', category: 'staple foods', unit: 'loaf',
    final_demand_per_day: 17, processing_demand_per_day: 3, demand_per_day: 20,
    capacity_per_day: 14, production_per_day: 10, local_use_per_day: 10,
    hinterland_capacity_multiplier: 2.5,
    import_need_per_day: 10, imports_per_day: 7, unmet_per_day: 3,
    surplus_per_day: 0, exports_per_day: 0, consumption_per_day: 17, closing_stock: 0,
    sectors: { staple_diet: 14, exotic_diet: 1, defense: 2 },
    inputs: [{commodity: 'flour', unit: 'sack', required_per_day: 2,
              reserved_per_day: 1, consumed_per_day: 0.5}],
    sources: [
      {source_id: 'home', source: 'Home', supply_type: 'local', quantity_per_day: 10,
       unit_cost: 0.1, distance: 0, days: 0},
      {source_id: 'farm & mill', source: 'Farm <mill>', supply_type: 'import',
       quantity_per_day: 7, unit_cost: 0.2, distance: 40, days: 2}
    ],
    export_destinations: [],
    ...overrides
  };
}
function requirements() {
  return {
    enabled: true, model: 'estimated <test>', date: '1490-01-01',
    profile: {
      population: 100, wealth: 1.2, mage_population: 2, standing_army: 4, militia: 8,
      annual_growth_rate: 0.025, builders: 3, carpenters: 2, new_homes_per_year: 1.5,
      reference_period: 'Fixed annual-average baseline; independent of selected month.',
      provenance: {basis: 'Population <estimate>'},
      assumptions: ['No canonical census', 'A < B'],
      establishments: [{id: 'bakery', name: 'Bakers <estimated>', count: 2,
                        workers: 8, basis: 'Modeled <output>'}]
    },
    assumptions: ['No canonical census', 'Only modeled demand'],
    summary: {
      goods_with_import_need: 1, goods_with_shortfall: 1, goods_with_surplus: 1,
      import_weight_lb_per_day: 14, export_weight_lb_per_day: 10,
      food_demand_lb_per_day: 40, food_consumption_lb_per_day: 34
    },
    materials: [
      material(),
      material({
        commodity_id: 'flour', commodity: 'Flour', unit: 'sack',
        category: 'ingredients', import_need_per_day: 0, imports_per_day: 0,
        unmet_per_day: 0, surplus_per_day: 5, exports_per_day: 2, closing_stock: 3,
        sectors: { construction: 4 }, inputs: [], sources: [],
        export_destinations: [{destination_id: 'harbor & town',
                               destination: 'Harbor <town>', quantity_per_day: 2}]
      })
    ]
  };
}
"""


def run_location_script(body):
    exports = (
        "globalThis.ui = { state, el, renderRequirements, renderRequirementsTable, "
        "materialDetails, toggleMaterial, downloadRequirements, renderTable, renderBusinesses, loadSettlement, "
        "setMonth, requestHistory, start };"
    )
    instrumented = LOCATION_JS.replace("  start();\n})();", exports + "\n})();")
    assert instrumented != LOCATION_JS
    script = NODE_HARNESS + "\n" + WORLD_DATE_JS + "\n" + instrumented
    script += "\n(async () => {\n" + body
    script += "\n})().catch(error => { console.error(error); process.exitCode = 1; });"
    result = subprocess.run(
        ["node", "-"], input=script, capture_output=True, text=True, encoding="utf-8", timeout=20
    )
    assert result.returncode == 0, result.stdout + result.stderr


def test_requirements_render_profile_units_filters_and_material_cascade():
    run_location_script(r"""
ui.state.settlement = 'Home & city';
ui.state.month = 100;
const data = requirements();
ui.state.detail = detail('Home', 100, data);
ui.renderRequirements(data);
assert.equal(ui.el['requirements-content'].hidden, false);
assert.equal(ui.el['requirements-download'].disabled, false);
const profile = ui.el['requirements-profile'].innerHTML;
for (const label of ['Resident population', 'Mages', 'Standing army', 'Militia', 'Annual growth',
                     'Builders', 'Carpenters', 'New homes']) assert.ok(profile.includes(label));
assert.ok(profile.includes('+2.5%'));
assert.ok(ui.el['requirements-model'].textContent.includes('Material balance: 1490-01-01'));
assert.ok(ui.el['requirements-model'].textContent.includes('independent of selected month'));
const assumptions = ui.el['requirements-assumptions'].innerHTML;
assert.ok(assumptions.includes('Population &lt;estimate&gt;'));
assert.ok(assumptions.includes('A &lt; B'));
assert.equal(assumptions.split('No canonical census').length, 2);
assert.ok(ui.el['requirements-establishments'].innerHTML.includes('Bakers &lt;estimated&gt;'));
assert.ok(ui.el['requirements-establishments'].innerHTML.includes('Estimated workers (total)'));
assert.equal(ui.el['requirements-services-section'].hidden, true);
data.profile.service_requirements = [{
  name: 'Water <supply>', unit: 'gallon', required_per_day: 300,
  local_capacity_per_day: 250, unmet_per_day: 50, basis: 'Estimated <aqueduct>'
}];
ui.renderRequirements(data);
assert.equal(ui.el['requirements-services-section'].hidden, false);
const services = ui.el['requirements-services'].innerHTML;
for (const text of ['Water &lt;supply&gt;', 'gallon/day', 'Required/day', 'Local capacity/day',
                    'Still unmet/day', 'Estimated &lt;aqueduct&gt;', '>300<', '>250<', '>50<']) {
  assert.ok(services.includes(text), text);
}
delete data.profile.service_requirements;
ui.renderRequirements(data);
assert.equal(ui.el['requirements-services-section'].hidden, true);
assert.equal(ui.el['requirements-services'].innerHTML, '');
const summary = ui.el['requirements-summary'].innerHTML;
assert.ok(summary.includes('Allocated import weight'));
assert.ok(summary.includes('14<small>lb / day</small>'));
assert.ok(summary.includes('40<small>lb / day</small>'));
const body = ui.el['requirements-table'].querySelector('tbody');
assert.ok(body.innerHTML.includes('Bread &lt;fine&gt;'));
assert.ok(body.innerHTML.includes('loaf/day'));
assert.ok(body.innerHTML.includes('sack/day'));
assert.ok(body.innerHTML.includes('aria-expanded="false"'));
assert.ok(!body.innerHTML.includes('Allocated supplier split'), 'details should render lazily');
const button = new Element('toggle-bread');
button.setAttribute('data-material', 'bread');
button.setAttribute('aria-controls', 'material-detail-0');
const event = {target: {closest: () => button}};
ui.toggleMaterial(event);
assert.equal(button.getAttribute('aria-expanded'), 'true');
assert.equal(element('material-detail-0').hidden, false);
assert.ok(element('material-detail-0').querySelector('td').innerHTML.includes('Allocated supplier split'));
ui.toggleMaterial(event);
assert.equal(button.getAttribute('aria-expanded'), 'false');
assert.equal(element('material-detail-0').hidden, true);
assert.equal(element('material-detail-0').querySelector('td').innerHTML, '');
ui.state.materialFilter = 'imports';
ui.renderRequirementsTable();
assert.equal(ui.el['requirements-count'].textContent, '1 of 2 materials');
assert.ok(body.innerHTML.includes('Bread &lt;fine&gt;'));
assert.ok(!body.innerHTML.includes('>Flour</a>'));
ui.state.materialFilter = 'surplus';
ui.renderRequirementsTable();
assert.ok(body.innerHTML.includes('>Flour</a>'));
assert.ok(!body.innerHTML.includes('Bread &lt;fine&gt;'));
ui.state.materialFilter = 'unmet';
ui.renderRequirementsTable();
assert.ok(body.innerHTML.includes('material-unmet'));
ui.state.materialFilter = 'all';
ui.state.materialSearch = 'exotic diet';
ui.renderRequirementsTable();
assert.equal(ui.el['requirements-count'].textContent, '1 of 2 materials');
ui.state.materialSearch = 'unavailable material';
ui.renderRequirementsTable();
assert.ok(body.innerHTML.includes('No materials match'));
const bread = ui.materialDetails(data.materials[0]);
assert.ok(bread.includes('Source-district baseline calibration: 2.5&#215;'));
assert.ok(bread.includes('modeling assumption, not census acreage'));
assert.ok(bread.includes('aggregate population and workshop input needs before events'));
assert.ok(bread.includes('Actual output may also include established industries'));
const uncalibrated = ui.materialDetails(material({hinterland_capacity_multiplier: undefined}));
assert.ok(!uncalibrated.includes('Source-district baseline calibration:'), 'missing calibration must not be invented');
for (const label of ['staple diet', 'exotic diet', 'defense', 'Required/day',
                     'Reserved/day', 'Consumed/day', 'Actual consumption']) {
  assert.ok(bread.includes(label), label);
}
assert.ok(bread.includes('product.html?commodity=flour&settlement=Home%20%26%20city'));
assert.ok(bread.includes('location.html?settlement=farm%20%26%20mill&month=100'));
assert.ok(bread.includes('Farm &lt;mill&gt;'));
assert.ok(bread.includes('planner.html?origin=farm%20%26%20mill&destination=Home%20%26%20city'));
assert.ok(bread.includes('0.200 gp/loaf'));
assert.ok(bread.includes('40 mi / 2 days'));
const flour = ui.materialDetails(data.materials[1]);
assert.ok(flour.includes('Harbor &lt;town&gt;'));
assert.ok(flour.includes('planner.html?origin=Home%20%26%20city&destination=harbor%20%26%20town'));
assert.ok(flour.includes('Closing stock</dt><dd>3<small>sack</small>'));
assert.ok(flour.includes('No direct processing inputs'));
const tinyNeed = ui.materialDetails(material({consumption_per_day: 0.00001}));
assert.ok(tinyNeed.includes('0.0000100'), 'small exotic quantities must not round to zero');
ui.renderRequirements({enabled: false});
assert.equal(ui.el['requirements-content'].hidden, true);
assert.equal(ui.el['requirements-download'].disabled, true);
assert.ok(ui.el['requirements-status'].textContent.includes('legacy'));
ui.renderRequirements(undefined);
assert.equal(ui.el['requirements-content'].hidden, true);
""")


def test_location_load_does_not_wait_for_timeline_or_accept_stale_location_responses():
    run_location_script(r"""
ui.state.today = 100;
ui.state.month = 100;
ui.loadSettlement('First');
assert.ok(requests[0].path.startsWith('/api/location?settlement=First&month=100'));
assert.equal(pending('/api/timeline').length, 0, 'heavy timeline requires explicit opt-in');
const firstDetail = pending('/api/location')[0];
const firstBusinesses = pending('/api/businesses')[0];
firstDetail.respond(detail('First', 100, requirements()));
await tick();
assert.equal(pending('/api/timeline').length, 0, 'detail completion must not start history');
ui.requestHistory();
assert.equal(pending('/api/timeline').length, 1);
const firstTimeline = pending('/api/timeline')[0];
assert.equal(ui.state.detail.label, 'First month 100');
assert.equal(ui.el['requirements-content'].hidden, false);
assert.equal(ui.state.timeline, null, 'detail must display while timeline is unresolved');
ui.loadSettlement('Second');
assert.equal(ui.state.detail, null);
assert.equal(ui.el['requirements-content'].hidden, true);
assert.equal(ui.el['requirements-download'].disabled, true);
assert.equal(ui.el['price-table'].querySelector('tbody').innerHTML, '');
assert.ok(ui.el.businesses.innerHTML.includes('Loading'));
const secondDetail = pending('/api/location')[1];
assert.equal(pending('/api/timeline').length, 1, 'new timeline must not queue before new detail');
secondDetail.respond(detail('Second', 100, requirements()));
await tick();
assert.equal(pending('/api/timeline').length, 1, 'history opt-in applies only to its own location');
ui.requestHistory();
const secondTimeline = pending('/api/timeline')[1];
firstTimeline.respond(timeline('First', 1, 3));
firstBusinesses.respond({businesses: [{name: 'Old business', offers: [], specialties: []}]});
await tick();
assert.equal(ui.state.settlement, 'Second');
assert.equal(ui.state.detail.label, 'Second month 100');
assert.equal(ui.state.timeline, null);
assert.equal(ui.el['place-name'].textContent, 'Second');
assert.ok(!ui.el.businesses.innerHTML.includes('Old business'));
secondTimeline.respond(timeline('Second', 90, 110));
await tick();
assert.equal(ui.state.month, 100);
assert.equal(pending('/api/location').length, 2, 'timeline should not reload an unchanged month');
assert.equal(ui.el.scrub.disabled, false);
ui.loadSettlement('Third');
const thirdDetail = pending('/api/location')[2];
ui.loadSettlement('Fourth');
assert.equal(thirdDetail.options.signal.aborted, true);
pending('/api/location')[3].respond(detail('Fourth', 100, requirements()));
await tick();
thirdDetail.respond(detail('Third', 100, requirements()));
await tick();
assert.equal(ui.state.detail.label, 'Fourth month 100', 'late response must not repaint');
assert.equal(pending('/api/timeline').length, 2, 'neither obsolete nor current detail may auto-start history');
assert.ok(history.at(-1).includes('settlement=Fourth'));
""")


def test_inferred_defense_resources_and_output_facilities_remain_separate():
    run_location_script(r"""
ui.state.settlement = 'Home & city';
ui.state.month = 100;
const data = requirements();
ui.state.detail = detail('Home', 100, data);
ui.renderRequirements(data);
for (const panel of ['defense', 'resources', 'output']) {
  assert.equal(ui.el['requirements-' + panel + '-section'].hidden, true);
}
const laborTable = ui.el['requirements-establishments'].innerHTML;
data.profile.defense_equipment = {
  sword_longsword: {
    standing_stock: 120, militia_stock: 50, annual_replacement: 365, annual_growth_additions: 73
  },
  shield: {standing_stock: 0, militia_stock: 0}
};
data.materials.push(material({
  commodity_id: 'sword_longsword', commodity: 'Longsword <theoretical>', unit: 'sword'
}));
data.profile.resource_assumptions = {
  farm_acres: 450, woodland_acres: 120, dairy_stock: 35, poultry_stock: 90,
  hives: 0, draft_oxen: 5, fishers: 30, assumptions: ['Not a <survey>']
};
data.profile.fishers = 18;
data.profile.output_establishments = [{
  name: 'Bakers <output equivalent>', count: 5, active_equivalents: 0.125,
  planned_per_day: 2000, actual_per_day: 50, unit: 'loaf', throughput_per_day: 400,
  basis: 'Inferred <throughput>; not additional workers'
}];
ui.renderRequirements(data);
for (const panel of ['defense', 'resources', 'output']) {
  assert.equal(ui.el['requirements-' + panel + '-section'].hidden, false);
}
assert.equal(ui.el['requirements-establishments'].innerHTML, laborTable,
             'output-equivalent facilities must not change labor establishment counts');
const defense = ui.el['requirements-defense'].innerHTML;
assert.ok(defense.includes('product.html?commodity=sword_longsword&settlement=Home%20%26%20city'));
assert.ok(defense.includes('Longsword &lt;theoretical&gt;'));
assert.ok(defense.includes('Replacement/year'));
assert.ok(defense.includes('Replacement/day'));
assert.ok(defense.includes('>365</td><td class="num">1</td><td class="num">73</td>'),
          'replacement/day must be annual replacement /365, excluding growth additions');
assert.ok(defense.includes('<small>sword</small>'));
assert.ok(defense.includes('&#8212;'), 'missing equipment estimates must not become zero');
const resources = ui.el['requirements-resources'].innerHTML;
for (const label of ['Farm hinterland', 'Managed woodland', 'Dairy stock', 'Poultry stock',
                     'Beehives', 'Draft oxen', 'Potential fishers', 'Allocated fishers']) {
  assert.ok(resources.includes(label), label);
}
assert.ok(resources.includes('>450</td><td>acres'));
assert.ok(resources.includes('Beehives</td><td class="num">0</td>'), 'zero is a real estimate');
assert.ok(resources.includes('Potential fishers</td><td class="num">30</td>'));
assert.ok(resources.includes('Allocated fishers</td><td class="num">18</td>'));
assert.ok(resources.includes('Not a &lt;survey&gt;'));
const output = ui.el['requirements-output'].innerHTML;
for (const label of ['Required facilities (planned)', 'Active equivalents (actual)',
                     'Planned output/day', 'Actual output/day', 'Throughput/facility/day']) {
  assert.ok(output.includes(label), label);
}
assert.ok(output.includes('Bakers &lt;output equivalent&gt;'));
assert.ok(output.includes('loaf/day'));
assert.ok(output.includes('>5</td><td class="num">0.125</td>'));
assert.ok(output.includes('Inferred &lt;throughput&gt;; not additional workers'));
assert.equal(requests.length, 0, 'profile panels must not fetch supply chains');
data.profile.resource_assumptions = {farm_acres: 0};
delete data.profile.fishers;
delete data.profile.defense_equipment;
delete data.profile.output_establishments;
ui.renderRequirements(data);
assert.equal(ui.el['requirements-defense-section'].hidden, true);
assert.equal(ui.el['requirements-defense'].innerHTML, '');
assert.equal(ui.el['requirements-output-section'].hidden, true);
assert.equal(ui.el['requirements-output'].innerHTML, '');
assert.equal(ui.el['requirements-resources-section'].hidden, false);
assert.ok(ui.el['requirements-resources'].innerHTML.includes('Farm hinterland</td><td class="num">0</td>'));
assert.ok(ui.el['requirements-resources'].innerHTML.includes('Allocated fishers</td><td class="num">&#8212;</td>'));
delete data.profile.resource_assumptions;
ui.renderRequirements(data);
assert.equal(ui.el['requirements-resources-section'].hidden, true);
assert.equal(ui.el['requirements-resources'].innerHTML, '');
""")


def test_month_changes_clear_stale_values_and_ignore_old_success_and_errors():
    run_location_script(r"""
ui.state.today = 100;
ui.state.month = 100;
ui.loadSettlement('Home');
const oldest = pending('/api/location')[0];
assert.equal(pending('/api/timeline').length, 0);
ui.setMonth(101, false);
assert.equal(oldest.options.signal.aborted, true);
assert.equal(ui.el['requirements-content'].hidden, true);
oldest.respond(detail('Home', 100, requirements()));
await tick();
assert.equal(ui.state.detail, null, 'debounce window must also reject stale data');
assert.equal(pending('/api/timeline').length, 0, 'stale completion must not launch history');
for (const callback of timers.values()) callback();
timers.clear();
const previous = pending('/api/location')[1];
ui.setMonth(102, true);
const latest = pending('/api/location')[2];
latest.respond(detail('Home', 102, requirements()));
await tick();
assert.equal(pending('/api/timeline').length, 0);
ui.requestHistory();
assert.equal(pending('/api/timeline').length, 1);
pending('/api/timeline')[0].respond(timeline('Home', 90, 110));
await tick();
assert.equal(ui.state.month, 102, 'late timeline must retain the latest month');
previous.reject(new Error('Old request failed'));
await tick();
assert.equal(ui.state.detail.label, 'Home month 102');
assert.equal(ui.el.status.innerHTML, '');
assert.equal(ui.el['requirements-board'].getAttribute('aria-busy'), 'false');
ui.setMonth(103, true);
pending('/api/location')[3].reject(new Error('Selected month failed'));
await tick();
assert.equal(ui.state.detail, null);
assert.equal(ui.el['requirements-content'].hidden, true);
assert.equal(ui.el['requirements-download'].disabled, true);
assert.ok(ui.el['requirements-status'].textContent.includes('Selected month failed'));
assert.equal(ui.el['requirements-board'].getAttribute('aria-busy'), 'false');
assert.equal(ui.el['price-table'].querySelector('tbody').innerHTML, '');
assert.equal(pending('/api/timeline').length, 1, 'history should load only once per location');
""")


def test_timeline_retains_selected_month_or_explicitly_clamps_outside_history():
    run_location_script(r"""
ui.state.today = 100;
ui.state.month = 75;
ui.loadSettlement('Home');
pending('/api/location')[0].respond(detail('Home', 75, requirements()));
await tick();
ui.requestHistory();
pending('/api/timeline')[0].respond(timeline('Home', 70, 110));
await tick();
assert.equal(ui.state.month, 75, 'timeline must not jump back to today');
assert.equal(pending('/api/location').length, 1);
ui.loadSettlement('Other');
pending('/api/location')[1].respond(detail('Other', 75, requirements()));
await tick();
ui.requestHistory();
ui.setMonth(76, true);
pending('/api/timeline')[1].respond(timeline('Other', 90, 110));
await tick();
assert.equal(ui.state.month, 90);
assert.ok(ui.el['timeline-status'].textContent.includes('nearest available month'));
assert.ok(pending('/api/location').at(-1).path.endsWith('&month=90'));
assert.equal(pending('/api/location')[2].options.signal.aborted, true);
pending('/api/location')[2].respond(detail('Other', 76, requirements()));
await tick();
assert.equal(ui.state.detail, null);
pending('/api/location')[3].respond(detail('Other', 90, requirements()));
await tick();
assert.equal(ui.state.detail.label, 'Other month 90');
ui.loadSettlement('NoHistory');
pending('/api/location')[4].respond(detail('NoHistory', 90, requirements()));
await tick();
ui.requestHistory();
pending('/api/timeline')[2].reject(new Error('History failed'));
await tick();
assert.equal(ui.state.detail.label, 'NoHistory month 90');
assert.equal(ui.el['requirements-content'].hidden, false);
assert.ok(ui.el['timeline-status'].textContent.includes('History failed'));
assert.equal(ui.el.status.innerHTML, '');
""")


def test_start_honors_month_links_without_overriding_a_new_manual_selection():
    run_location_script(r"""
window.location.search = '?settlement=Home&month=95';
ui.start();
pending('/api/bootstrap')[0].respond({settlements: [], categories: []});
pending('/api/chronicle')[0].respond({today: 100});
await tick();
assert.equal(ui.state.month, 95);
assert.equal(ui.state.settlement, 'Home');
assert.ok(pending('/api/location')[0].path.endsWith('&month=95'));
assert.equal(pending('/api/timeline').length, 0);
pending('/api/location')[0].respond(detail('Home', 95, requirements()));
await tick();
assert.equal(pending('/api/timeline').length, 0);
""")
    run_location_script(r"""
window.location.search = '?settlement=Initial&month=95';
ui.start();
ui.loadSettlement('Manually selected');
pending('/api/location')[0].respond(detail('Manually selected', 100, requirements()));
await tick();
pending('/api/bootstrap')[0].respond({settlements: [], categories: []});
pending('/api/chronicle')[0].respond({today: 100});
await tick();
assert.equal(ui.state.settlement, 'Manually selected');
assert.equal(ui.state.month, 100);
assert.equal(pending('/api/location').length, 1);
assert.equal(ui.state.detail.label, 'Manually selected month 100');
""")


def test_history_is_opt_in_and_single_month_navigation_remains_available():
    run_location_script(r"""
window.location.search = '?settlement=Home&month=95';
ui.start();
assert.equal(ui.el['step-fwd'].disabled, true);
assert.equal(ui.el['history-chart'].hidden, true);
pending('/api/bootstrap')[0].respond({settlements: [], categories: []});
pending('/api/chronicle')[0].respond({today: 100});
await tick();
ui.requestHistory();
assert.equal(pending('/api/timeline').length, 0, 'cannot queue history ahead of first detail');
pending('/api/location')[0].respond(detail('Home', 95, requirements()));
pending('/api/businesses')[0].respond({businesses: [
  {name: 'Local baker', is_headquarters: true, offers: [], specialties: []}
]});
await tick();
assert.equal(pending('/api/timeline').length, 0);
assert.ok(ui.el.businesses.innerHTML.includes('Local baker'));
assert.equal(ui.el['load-history'].disabled, false);
assert.equal(ui.el['step-back'].disabled, false);
assert.equal(ui.el['step-fwd'].disabled, false);
assert.equal(ui.el['jump-today'].disabled, false);
assert.equal(ui.el['jump-worst'].disabled, true);
assert.equal(ui.el['jump-best'].disabled, true);
assert.equal(ui.el.scrub.disabled, true);
ui.el['step-fwd'].listeners.click();
assert.equal(ui.state.month, 96);
assert.ok(pending('/api/location').at(-1).path.endsWith('&month=96'));
assert.equal(ui.el['load-history'].disabled, true);
pending('/api/location')[1].respond(detail('Home', 96, requirements()));
await tick();
ui.el['jump-today'].listeners.click();
assert.equal(ui.state.month, 100);
pending('/api/location')[2].respond(detail('Home', 100, requirements()));
await tick();
assert.equal(pending('/api/timeline').length, 0, 'month navigation must not compute seven-year history');
assert.equal(ui.el['requirements-content'].hidden, false);
ui.el['load-history'].listeners.click();
ui.el['load-history'].listeners.click();
assert.equal(pending('/api/timeline').length, 1, 'repeated clicks must not duplicate heavy work');
assert.equal(ui.el['load-history'].disabled, true);
assert.equal(ui.el['requirements-content'].hidden, false);
assert.ok(ui.el['timeline-status'].textContent.includes('84 monthly balances'));
assert.ok(ui.el['timeline-status'].textContent.includes('delay other API requests'));
pending('/api/timeline')[0].reject(new Error('History unavailable'));
await tick();
assert.equal(ui.el['load-history'].disabled, false);
assert.equal(ui.el['requirements-content'].hidden, false);
assert.ok(ui.el['load-history'].textContent.includes('Retry'));
ui.el['load-history'].listeners.click();
assert.equal(pending('/api/timeline').length, 2);
pending('/api/timeline')[1].respond(timeline('Home', 90, 110));
await tick();
assert.equal(ui.state.month, 100);
assert.equal(ui.el['history-chart'].hidden, false);
assert.equal(ui.el['jump-worst'].disabled, false);
assert.equal(ui.el.scrub.disabled, false);
assert.equal(ui.el['load-history'].disabled, true);
assert.equal(pending('/api/location').length, 3, 'loading history must not reload selected month');
""")


def test_requirements_javascript_is_valid_and_downloads_complete_payload():
    run_location_script(r"""
const data = requirements();
ui.state.settlement = 'Home';
ui.state.month = 100;
ui.state.detail = detail('Home', 100, data);
let downloaded;
let link;
let revoked;
URL.createObjectURL = blob => { downloaded = blob; return 'blob:requirements'; };
URL.revokeObjectURL = url => { revoked = url; };
document.createElement = () => (link = {click() { this.clicked = true; }, remove() {}});
ui.downloadRequirements();
assert.equal(link.download, 'location-requirements-100.json');
assert.equal(link.clicked, true);
assert.equal(downloaded.type, 'application/json');
assert.deepEqual(JSON.parse(await downloaded.text()), {
  settlement: 'Home', month: 100, requirements: data
});
for (const callback of timers.values()) callback();
assert.equal(revoked, 'blob:requirements');
""")
    subprocess.run(
        ["node", "-"],
        input="new Function(" + json.dumps(LOCATION_JS) + ");",
        capture_output=True,
        text=True,
        check=True,
        timeout=20,
    )
