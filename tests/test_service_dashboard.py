import re

from faerun.locationassets import LOCATION_CSS, LOCATION_HTML, LOCATION_JS
from test_requirements_ui import run_location_script


ECONOMY_FIXTURE = r"""
function economy() {
  return {
    enabled: true,
    industries: [{
      id: 'hospitality', name: 'Hospitality <inns>', examples: ['Inn & tavern', '"Guesthouse"'],
      unit: 'guest <night>', workers: 12.5, establishments: 3,
      resident_demand_per_day: 11, visitor_demand_per_day: 19, demand_per_day: 30,
      capacity_per_day: 27, planned_per_day: 26, delivered_per_day: 23,
      unmet_per_day: 7, service_output_gp_per_day: 46, market_service: true,
      inputs: [{commodity_id: 'firewood & fuel', commodity: 'Firewood <bundled>', unit: 'bundle',
                required_per_day: 2.5, consumed_per_day: 1.75}],
      basis: 'Model <staff> & delivery'
    }, {
      id: 'public-order', name: 'Public order', examples: ['Watch'], unit: 'patrol',
      workers: 4.25, establishments: 1, resident_demand_per_day: 8,
      visitor_demand_per_day: 2, demand_per_day: 10, capacity_per_day: 12,
      planned_per_day: 10, delivered_per_day: 9, unmet_per_day: 1,
      service_output_gp_per_day: 9, market_service: false, inputs: [],
      basis: 'Imputed contribution'
    }],
    visitors: {
      enabled: true, arrivals_per_month: 240, overnight_visitors_per_day: 16,
      day_visitors_per_day: 4, visitors_per_day: 20,
      desired_overnight_visitors_per_day: 21, unaccommodated_visitors_per_day: 5,
      beds: 20, occupancy: 0.8, outbound_visitors_per_day: 6,
      resident_presence: 94, visitor_goods_demand_weight_lb_per_day: 65,
      visitor_goods_supplied_weight_lb_per_day: 59,
      visitor_spending_gp_per_day: 70, visitor_spending_abroad_gp_per_day: 80,
      net_visitor_receipts_gp_per_day: -10,
      segments: [
        {id: 'leisure', name: 'Leisure <holiday>', visitors_per_day: 6,
         arrivals_per_month: 60, average_nights: 3, spending_gp_per_day: 18},
        {id: 'pilgrimage', name: 'Pilgrimage', visitors_per_day: 3,
         arrivals_per_month: 30, average_nights: 3, spending_gp_per_day: 9},
        {id: 'scholarly', name: 'Scholarly', visitors_per_day: 3,
         arrivals_per_month: 30, average_nights: 3, spending_gp_per_day: 9},
        {id: 'festival', name: 'Festival', visitors_per_day: 4,
         arrivals_per_month: 90, average_nights: 0, spending_gp_per_day: 14},
        {id: 'adventure', name: 'Adventure', visitors_per_day: 2,
         arrivals_per_month: 15, average_nights: 4, spending_gp_per_day: 10},
        {id: 'business', name: 'Business', visitors_per_day: 2,
         arrivals_per_month: 15, average_nights: 4, spending_gp_per_day: 10}
      ],
      origins: [{id: 'incoming & town', name: 'Incoming <town>',
                 visitors_per_day: 20, spending_gp_per_day: 70}],
      destinations: [{id: 'outgoing & port', name: 'Outgoing <port>',
                      visitors_per_day: 6, spending_gp_per_day: 80}]
    },
    accounts: {
      currency: 'gp', goods_output_gp_per_day: 90, goods_intermediate_gp_per_day: 15,
      goods_value_added_gp_per_day: 75, service_output_gp_per_day: 55,
      service_intermediate_gp_per_day: 5, service_value_added_gp_per_day: 50,
      gross_local_product_gp_per_day: 125, gross_local_product_gp_per_year: 45625,
      glp_per_resident_gp_per_year: 456.25, goods_exports_gp_per_day: 52,
      goods_imports_gp_per_day: 67, goods_trade_balance_gp_per_day: -15,
      visitor_receipts_gp_per_day: 70, resident_travel_spending_gp_per_day: 80,
      net_visitor_receipts_gp_per_day: -10, external_balance_gp_per_day: -25,
      trade_valuation_basis: 'Matched <invoice> & no freight',
      output_valuation_basis: 'Constant <catalogue> & service baseline'
    },
    assumptions: ['Modeled <not measured>', 'Public service is not cash.',
                  'Additional assumption & provenance']
  };
}
function renderEconomyFixture(model = economy()) {
  const data = requirements();
  data.economy = model;
  ui.state.settlement = 'Home & city';
  ui.state.month = 100;
  ui.state.detail = detail('Home', 100, data);
  ui.renderRequirements(data);
  return data;
}
function card(html, label, value, unit) {
  assert.ok(html.includes('<dt>' + label + '</dt><dd>' + value + '<small>' +
    unit + '</small>'), label + ': expected ' + value + ' ' + unit);
}
function tableRow(html, label, values) {
  assert.ok(html.includes('<tr><td>' + label + '</td>' +
    values.map(value => '<td class="num">' + value + '</td>').join('') +
    '</tr>'), label + ': expected ' + values.join(', '));
}
"""


def test_economy_sections_are_collapsed_accessible_and_before_materials():
    ids = re.findall(r'id="([^"]+)"', LOCATION_HTML)
    assert len(ids) == len(set(ids))
    for panel in ("industries", "visitors", "accounts", "economy-assumptions"):
        opening = re.search(
            rf'<details id="requirements-{panel}-section"[^>]*>', LOCATION_HTML
        ).group()
        assert "hidden" in opening
        assert " open" not in opening
        assert LOCATION_HTML.index(opening) > LOCATION_HTML.index(
            'id="requirements-content"'
        )
        assert LOCATION_HTML.index(opening) < LOCATION_HTML.index(
            "<h3>Daily material balance</h3>"
        )
        assert f'id="requirements-{panel}"' in LOCATION_HTML
    assert ".requirements-subscroll:focus-visible" in LOCATION_CSS
    assert "\\" not in LOCATION_JS
    assert "\\" not in LOCATION_CSS
    run_location_script(ECONOMY_FIXTURE + r"""
renderEconomyFixture();
for (const panel of ['industries', 'visitors', 'accounts']) {
  assert.equal(ui.el['requirements-' + panel + '-section'].hidden, false);
  const html = ui.el['requirements-' + panel].innerHTML;
  assert.ok(html.includes('role="region" tabindex="0" aria-label="'));
  assert.ok(html.includes('<th scope="col">'));
}
assert.equal(requests.length, 0, 'rendering economy must not fetch any data');
""")


def test_service_sectors_render_all_rows_staffing_delivery_and_expandable_inputs():
    run_location_script(ECONOMY_FIXTURE + r"""
const model = economy();
for (const name of ['Retail', 'Dining', 'Transport', 'Finance', 'Education', 'Healing',
                    'Religion', 'Entertainment', 'Administration', 'Sanitation',
                    'Personal services', 'Professional services']) {
  model.industries.push({...model.industries[1], id: name, name});
}
const data = renderEconomyFixture(model);
const html = ui.el['requirements-industries'].innerHTML;
assert.ok(html.includes('14 modeled service sectors'));
for (const row of model.industries) {
  assert.ok(html.includes(row.name.replace('<', '&lt;').replace('>', '&gt;')));
}
for (const text of ['Resident demand/day', 'Visitor demand/day', 'Total demand/day',
                    'Capacity/day', 'Planned/day', 'Actually delivered/day', 'Still unmet/day',
                    'Workers (FTE)', 'Establishments', 'Service output (gp/day)',
                    'full-time equivalents', 'existing professions plus residual workers',
                    'not additive to the earlier labor count table', 'Imputed public service',
                    'Paid market service', 'not cash sales', 'baseline service valuations']) {
  assert.ok(html.includes(text), text);
}
assert.ok(html.includes('<td class="num">12.5</td><td class="num">3</td>' +
  '<td class="num">11</td><td class="num">19</td><td class="num">30</td>' +
  '<td class="num">27</td><td class="num">26</td><td class="num">23</td>' +
  '<td class="num material-unmet">7</td><td class="num">46.00</td>'));
assert.ok(html.includes('<details id="service-inputs-0" class="service-inputs"><summary>'));
assert.ok(!html.includes('class="service-inputs" open'));
for (const text of ['Hospitality &lt;inns&gt;', 'guest &lt;night&gt;/day',
                    'Inn &amp; tavern', '&quot;Guesthouse&quot;', 'Model &lt;staff&gt; &amp; delivery',
                    'Firewood &lt;bundled&gt;', 'bundle/day', 'Required/day', 'Consumed/day',
                    '<td class="num">2.5</td><td class="num">1.75</td>',
                    'No intermediate inputs supplied']) assert.ok(html.includes(text), text);
assert.ok(html.includes('product.html?commodity=firewood%20%26%20fuel&settlement=Home%20%26%20city'));
const originalLabor = ui.el['requirements-establishments'].innerHTML;
delete data.economy;
ui.renderRequirements(data);
assert.equal(ui.el['requirements-establishments'].innerHTML, originalLabor,
  'service presentation must not add workers to labor counts');
""")


def test_tourism_separates_arrivals_presence_beds_goods_pressure_and_current_month_links():
    run_location_script(ECONOMY_FIXTURE + r"""
const data = renderEconomyFixture();
const html = ui.el['requirements-visitors'].innerHTML;
card(html, 'Monthly arrivals', '240', 'trips / 30-day Harptos month');
card(html, 'All visitors present', '20', 'average people / day');
card(html, 'Overnight visitors present', '16', 'average people / day');
card(html, 'Day visitors present', '4', 'average people / day');
card(html, 'Residents traveling away', '6', 'average people / day');
card(html, 'Desired overnight visitors', '21', 'average people / day');
card(html, 'Unaccommodated overnight demand', '5', 'average people / day; not arrivals');
card(html, 'Available beds', '20', 'modeled beds');
card(html, 'Bed occupancy', '80.0%', 'share of beds occupied; unavailable if no beds');
card(html, 'Resident presence', '94', 'resident food-demand equivalents at home');
card(html, 'Visitor goods demand', '65', 'lb / day');
card(html, 'Visitor goods supplied', '59', 'lb / day');
card(html, 'Visitor spending here', '70.00', 'gp / day');
card(html, 'Resident travel spending away', '80.00', 'gp / day');
card(html, 'Net visitor receipts', '-10.00', 'gp / day; receipts minus outlays');
tableRow(html, 'Leisure &lt;holiday&gt;', ['6', '60', '3', '18.00']);
tableRow(html, 'Festival', ['4', '90', '0', '14.00']);
for (const segment of ['Pilgrimage', 'Scholarly', 'Adventure', 'Business']) {
  assert.ok(html.includes('<td>' + segment + '</td>'), segment);
}
for (const text of ['zero average nights', 'Refused overnight demand is not counted as arrivals',
                    'Resident home food demand is reduced', 'food and service-material pressure',
                    'transfers between modeled cities', 'not new global gold',
                    'Incoming &lt;town&gt;', 'Outgoing &lt;port&gt;']) assert.ok(html.includes(text), text);
tableRow(html, '<a href="location.html?settlement=incoming%20%26%20town&month=100">Incoming &lt;town&gt;</a>',
  ['20', '70.00']);
tableRow(html, '<a href="location.html?settlement=outgoing%20%26%20port&month=100">Outgoing &lt;port&gt;</a>',
  ['6', '80.00']);
ui.state.month = 101;
ui.renderRequirements(data);
assert.ok(ui.el['requirements-visitors'].innerHTML.includes('outgoing%20%26%20port&month=101'));
ui.state.month = null;
ui.renderRequirements(data);
assert.ok(!ui.el['requirements-visitors'].innerHTML.includes('&month='));
""")


def test_accounts_display_exact_value_added_signed_balances_and_valuation_cautions():
    run_location_script(ECONOMY_FIXTURE + r"""
const data = renderEconomyFixture();
let html = ui.el['requirements-accounts'].innerHTML;
card(html, 'Gross local product (GLP)', '125', 'gp / day; estimated');
card(html, 'Annualized GLP', '45625', 'gp / year; current-day run rate');
card(html, 'Annualized GLP per resident', '456', 'gp / resident / year; current-day run rate');
tableRow(html, 'Goods', ['90.00', '15.00', '75.00']);
tableRow(html, 'Services', ['55.00', '5.00', '50.00']);
tableRow(html, 'Goods exports', ['52.00']);
tableRow(html, 'Goods imports', ['67.00']);
tableRow(html, 'Merchandise balance (exports minus imports)', ['-15.00']);
tableRow(html, 'Visitor receipts', ['70.00']);
tableRow(html, 'Resident travel outlays', ['80.00']);
tableRow(html, 'Net travel receipts (receipts minus outlays)', ['-10.00']);
tableRow(html, 'Combined external balance (merchandise plus net travel)', ['-25.00']);
for (const text of ['value added = output minus intermediates', 'annualized current-day run rates (365 days)',
                    'not a measured year total', 'constant catalogue commodity prices and baseline service',
                    'not the current nominal market-price series', 'identical producer-gate invoice',
                    'excluding freight and tariffs', 'different valuation basis', 'one nominal price series',
                    'Tourist retail goods already enter', 'Do not add visitor receipts or exports again to GLP',
                    'not profits, treasury balances, or immediate automatic wealth gains',
                    'Matched &lt;invoice&gt; &amp; no freight', 'Constant &lt;catalogue&gt; &amp; service baseline']) {
  assert.ok(html.includes(text), text);
}
Object.assign(data.economy.accounts, {
  goods_trade_balance_gp_per_day: 1.25, net_visitor_receipts_gp_per_day: 0,
  external_balance_gp_per_day: 1.25, glp_per_resident_gp_per_year: null,
  service_value_added_gp_per_day: -0.125
});
ui.renderRequirements(data);
html = ui.el['requirements-accounts'].innerHTML;
tableRow(html, 'Merchandise balance (exports minus imports)', ['+1.25']);
tableRow(html, 'Net travel receipts (receipts minus outlays)', ['0.000']);
tableRow(html, 'Combined external balance (merchandise plus net travel)', ['+1.25']);
tableRow(html, 'Services', ['55.00', '5.00', '-0.125']);
card(html, 'Annualized GLP per resident', '&#8212;', 'gp / resident / year; current-day run rate');
""")


def test_optional_economy_sections_clear_legacy_disabled_empty_and_nullable_data():
    run_location_script(ECONOMY_FIXTURE + r"""
const panels = ['industries', 'visitors', 'accounts', 'economy-assumptions'];
const data = renderEconomyFixture();
for (const legacy of [undefined, {enabled: false}, requirements()]) {
  renderEconomyFixture();
  ui.renderRequirements(legacy);
  for (const panel of panels) {
    assert.equal(ui.el['requirements-' + panel + '-section'].hidden, true, panel);
    assert.equal(ui.el['requirements-' + panel].innerHTML, '', panel);
  }
}
renderEconomyFixture({...economy(), enabled: false});
for (const panel of panels) assert.equal(ui.el['requirements-' + panel + '-section'].hidden, true);
renderEconomyFixture({enabled: true});
for (const panel of panels) assert.equal(ui.el['requirements-' + panel + '-section'].hidden, true);
const disabledVisitors = economy();
disabledVisitors.visitors.enabled = false;
renderEconomyFixture(disabledVisitors);
assert.equal(ui.el['requirements-visitors-section'].hidden, true);
assert.equal(ui.el['requirements-visitors'].innerHTML, '');
assert.equal(ui.el['requirements-industries-section'].hidden, false);
assert.equal(ui.el['requirements-accounts-section'].hidden, false);
renderEconomyFixture({enabled: true, industries: [], assumptions: [],
  visitors: {enabled: true, beds: 0, occupancy: null, origins: [], destinations: [], segments: []},
  accounts: {}});
const visitors = ui.el['requirements-visitors'].innerHTML;
card(visitors, 'Available beds', '0', 'modeled beds');
card(visitors, 'Bed occupancy', '&#8212;', 'share of beds occupied; unavailable if no beds');
assert.ok(visitors.includes('No incoming visitor origins supplied'));
assert.ok(visitors.includes('No outgoing resident destinations supplied'));
assert.ok(visitors.includes('No visitor segment estimates supplied'));
const accounts = ui.el['requirements-accounts'].innerHTML;
card(accounts, 'Gross local product (GLP)', '&#8212;', 'gp / day; estimated');
assert.ok(accounts.includes('Supplied trade valuation basis: Not supplied.'));
assert.ok(accounts.includes('Supplied output valuation basis: Not supplied.'));
assert.ok(!visitors.includes('NaN') && !accounts.includes('NaN'));
assert.ok(!visitors.includes('undefined') && !accounts.includes('undefined'));
assert.equal(requests.length, 0);
""")


def test_economy_escapes_text_exposes_all_assumptions_and_preserves_json_export():
    run_location_script(ECONOMY_FIXTURE + r"""
const model = economy();
const attack = '<img src=x onerror="bad()">';
model.industries[0].name = attack;
model.industries[0].unit = attack;
model.industries[0].basis = attack;
model.industries[0].examples.push(attack);
model.industries[0].inputs[0].commodity = attack;
model.industries[0].inputs[0].commodity_id = attack;
model.visitors.origins[0].name = attack;
model.visitors.origins[0].id = attack;
model.visitors.segments[0].name = attack;
model.accounts.trade_valuation_basis = attack;
model.accounts.output_valuation_basis = attack;
model.assumptions.push(attack);
const data = renderEconomyFixture(model);
for (const panel of ['industries', 'visitors', 'accounts', 'economy-assumptions']) {
  const html = ui.el['requirements-' + panel].innerHTML;
  assert.ok(!html.includes('<img'), panel);
  assert.ok(html.includes('&lt;img src=x onerror=&quot;bad()&quot;&gt;'), panel);
}
const assumptions = ui.el['requirements-economy-assumptions'].innerHTML;
assert.equal(assumptions.split('<li>').length - 1, model.assumptions.length);
for (const text of ['Modeled &lt;not measured&gt;', 'Public service is not cash.',
                    'Additional assumption &amp; provenance']) assert.ok(assumptions.includes(text), text);
assert.ok(ui.el['requirements-visitors'].innerHTML.includes('settlement=' + encodeURIComponent(attack) + '&month=100'));
let downloaded;
URL.createObjectURL = blob => { downloaded = blob; return 'blob:economy'; };
ui.downloadRequirements();
assert.equal(downloaded.type, 'application/json');
assert.deepEqual(JSON.parse(await downloaded.text()), {
  settlement: 'Home & city', month: 100, requirements: data
});
""")


def test_location_responses_render_economy_without_history_and_ignore_stale_data():
    run_location_script(ECONOMY_FIXTURE + r"""
ui.state.today = 100;
ui.state.month = 100;
ui.loadSettlement('First');
const first = pending('/api/location')[0];
ui.loadSettlement('Second');
const second = pending('/api/location')[1];
const latest = requirements();
latest.economy = economy();
latest.economy.industries[0].name = 'Latest hospitality';
second.respond(detail('Second', 100, latest));
await tick();
assert.ok(ui.el['requirements-industries'].innerHTML.includes('Latest hospitality'));
assert.equal(ui.el['requirements-visitors-section'].hidden, false);
const stale = requirements();
stale.economy = economy();
stale.economy.industries[0].name = 'Stale hospitality';
first.respond(detail('First', 100, stale));
await tick();
assert.ok(ui.el['requirements-industries'].innerHTML.includes('Latest hospitality'));
assert.ok(!ui.el['requirements-industries'].innerHTML.includes('Stale hospitality'));
assert.equal(pending('/api/timeline').length, 0);
assert.ok(requests.every(request => request.path.startsWith('/api/location?') ||
  request.path.startsWith('/api/businesses?')), 'no new economy or dynamics API requests');
const economyHTML = ui.el['requirements-industries'].innerHTML;
ui.state.materialFilter = 'unmet';
ui.renderRequirementsTable();
assert.equal(ui.el['requirements-count'].textContent, '1 of 2 materials');
assert.equal(ui.el['requirements-industries'].innerHTML, economyHTML);
ui.loadSettlement('Legacy');
assert.equal(ui.el['requirements-content'].hidden, true, 'old economy hidden while loading');
pending('/api/location')[2].respond(detail('Legacy', 100, requirements()));
await tick();
for (const panel of ['industries', 'visitors', 'accounts', 'economy-assumptions']) {
  assert.equal(ui.el['requirements-' + panel + '-section'].hidden, true, panel);
  assert.equal(ui.el['requirements-' + panel].innerHTML, '', panel);
}
""")
