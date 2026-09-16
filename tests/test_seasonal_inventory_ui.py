import json
import subprocess

from faerun.cli import _seasonal_lines
from faerun.detailassets import PRODUCT_JS
from faerun.webassets import SEASONAL_JS
from test_requirements_ui import run_location_script


def seasonal_payload():
    return {
        "commodity": "grain",
        "commodity_name": "Grain",
        "settlement": "Cold town",
        "category": "food",
        "unit": "bushel",
        "price": 10,
        "buy_price": 8,
        "merchant_markup_pct": 25,
        "availability": "common",
        "stock": 240,
        "uncommitted_stock": 40,
        "uncommitted_supply_per_day": 0,
        "stock_horizon_days": 10,
        "uncommitted_basis": "Local carryover after <protected> reserves; not a booking.",
        "inventory": {
            "enabled": True,
            "opening_stock": 250,
            "closing_stock": 240,
            "uncommitted_stock": 17,
            "storage_capacity": 500,
            "reserve_target": 200,
            "spoilage": 1,
            "overflow": 2,
            "stock_draw_per_day": 7,
            "days_of_cover": None,
            "epoch": "1492-01-01",
            "stock_basis": "Replayed <local> stocks, not a ten-day window.",
        },
        "seasonality": {
            "climate": "cold <local>",
            "months": [
                {
                    "month": month,
                    "name": f"Month {month}",
                    "production_multiplier": 6 if month in (8, 9) else 0,
                    "demand_multiplier": 1,
                }
                for month in range(1, 13)
            ],
            "production_multiplier": 0,
            "demand_multiplier": 1,
            "storage_days": 240,
            "storage_loss": 0.001,
            "reserve_days": 90,
        },
    }


def run_js(script):
    result = subprocess.run(
        ["node", "-"], input=script, capture_output=True, text=True,
        encoding="utf-8", timeout=20,
    )
    assert result.returncode == 0, result.stdout + result.stderr


def test_paired_curves_use_quote_local_profile_and_escape_model_copy():
    run_js(
        "const assert = require('node:assert/strict');\n" + SEASONAL_JS
        + "\nconst row = " + json.dumps(seasonal_payload()) + ";\n" + """
const html = seasonalPanel(row, {...row.seasonality, climate:'wrong global climate'});
assert.ok(html.includes('cold &lt;local&gt;'));
assert.ok(!html.includes('wrong global climate'));
assert.equal((html.match(/<polyline /g) || []).length, 2);
assert.equal((html.match(/<th scope="row">/g) || []).length, 12);
for (const label of ['Current production multiplier', 'Current demand multiplier',
                    'Opening stock', 'Closing stock', 'Storage capacity',
                    'Uncommitted local inventory', 'Protected reserve target', 'Storage spoilage', 'Storage overflow',
                    'Stock draw / day', 'Not applicable (no demand)', '1492-01-01']) {
  assert.ok(html.includes(label), label);
}
assert.ok(html.includes('>0x<'));
assert.ok(html.includes('0.1% / day'));
assert.ok(html.includes('>17 bushel<'), 'use physical inventory free stock, not the quote planning quota');
assert.ok(html.includes('in-memory month checkpoints, not on-disk'));
assert.ok(html.includes('Player purchases are not executed'));
assert.ok(html.includes('prior-harvest assumption'));
assert.ok(html.includes('Replayed &lt;local&gt;'));
assert.ok(html.includes('&lt;protected&gt;'));
assert.ok(!html.includes('Infinity'));
assert.ok(!html.includes('NaN'));
assert.equal(seasonalPanel({seasonality:{}, inventory:{}}), '');
assert.ok(seasonalStockBasis({stock_horizon_days:10}).includes('10-day modeled window'));
assert.ok(seasonalPanel({inventory:{}}, row.seasonality).includes('cold &lt;local&gt;'));
const invalid = {...row.seasonality, months:row.seasonality.months.slice(1)};
assert.equal(seasonalPanel({seasonality:invalid}), '');
""")


def test_material_inspection_shows_carryover_and_free_stock_without_daily_surplus():
    run_location_script(
        "const row = " + json.dumps(seasonal_payload()) + ";\n" + """
const data = requirements();
data.materials = [material({...row, commodity_id:'grain', commodity:'Grain', closing_stock:999})];
ui.state.settlement = 'Cold town';
ui.state.detail = detail('Cold town', 100, data);
ui.state.materialFilter = 'uncommitted';
ui.renderRequirementsTable();
assert.equal(ui.el['requirements-count'].textContent, '1 of 1 materials');
const html = ui.materialDetails(data.materials[0]);
assert.ok(html.includes('12-month production'));
assert.ok(html.includes('Local granary / storage reserves'));
assert.ok(html.includes('>240'));
assert.ok(!html.includes('>999'));
assert.ok(!html.includes(' / 10-day window'));
assert.ok(html.includes('Replayed &lt;local&gt;'));
ui.state.detail.market.prices = [{...row, production_type:'raw', multiplier:1, demand_per_day:10}];
ui.renderTable();
const prices = ui.el['price-table'].querySelector('tbody').innerHTML;
assert.ok(prices.includes('after &lt;protected&gt; reserves'));
assert.ok(!prices.includes('10-day modeled window'));
""")


def test_product_load_requests_local_profile_and_keeps_buy_sell_semantics():
    script = PRODUCT_JS.replace(
        "start().catch(function(e){setStatus(e.message,true);});", ""
    )
    run_js(
        """
const assert = require('node:assert/strict');
const elements = new Map();
globalThis.document = {getElementById(id) {
  if (!elements.has(id)) elements.set(id, {value:'', innerHTML:'', textContent:'', addEventListener(){}});
  return elements.get(id);
}};
globalThis.history = {replaceState(){}};
""" + script + "\nconst row = " + json.dumps(seasonal_payload()) + ";\n" + """
document.getElementById('product').value = 'grain';
document.getElementById('market').value = 'Cold town';
get = async function(path, params) {
  if (path === '/api/market') return {prices:[row]};
  assert.equal(params.settlement, 'Cold town');
  return {commodity:{id:'grain', name:'Grain', category:'food', production_type:'raw',
    unit:'bushel', weight:60, base_price:6, bom:{}}, components:{}, sourcing:{sources:[]},
    seasonal_inventory:true, seasonality:{...row.seasonality, climate:'wrong global climate'}};
};
(async function() {
  await load();
  assert.equal(document.getElementById('status').textContent, '');
  const html = document.getElementById('content').innerHTML;
  assert.ok(html.includes('Buy from merchant / bushel'));
  assert.ok(html.includes('Sell to merchant / bushel'));
  assert.ok(html.includes('10.00 gp'));
  assert.ok(html.includes('8.00 gp'));
  assert.ok(html.includes('cold &lt;local&gt;'));
  assert.ok(!html.includes('wrong global climate'));
  assert.ok(html.includes('Protected reserve target'));
})().catch(error => {console.error(error); process.exitCode = 1;});
""")


def test_cli_seasonal_storage_summary_handles_no_demand_and_legacy_payload():
    assert _seasonal_lines({}) == []
    lines = _seasonal_lines(seasonal_payload())
    text = "\n".join(lines)
    for label in ("local climate cold <local>", "seasonal production x0 | demand x1",
                  "Production potential", "Month 12", "protected reserve 200.000",
                  "not applicable (no demand)", "1492-01-01", "0.1% storage loss/day",
                  "free local stock  17.000", "in-memory month checkpoints",
                  "player purchases do not execute", "same-day steady-state deliveries"):
        assert label in text


def test_pre_epoch_fallback_is_explicit_without_fabricating_inventory():
    payload = seasonal_payload()
    payload["inventory"] = {
        "enabled": False,
        "reason": "Requested date precedes <inventory epoch>",
        "epoch": "1492-01-01",
    }
    text = "\n".join(_seasonal_lines(payload))
    assert "inventory disabled: Requested date precedes <inventory epoch>" in text
    assert "earlier dates use steady-state quotes" in text
    assert "free local stock" not in text
    run_js(
        "const assert = require('node:assert/strict');\n" + SEASONAL_JS
        + "\nconst row = " + json.dumps(payload) + ";\n" + """
const html = seasonalPanel(row);
assert.ok(html.includes('Inventory disabled for this quote'));
assert.ok(html.includes('Requested date precedes &lt;inventory epoch&gt;'));
assert.ok(html.includes('Configured epoch: 1492-01-01'));
assert.ok(html.includes('not an applied inventory simulation'));
assert.ok(!html.includes('Opening stock'));
assert.ok(!html.includes('Local granary'));
assert.ok(seasonalStockBasis(row).includes('Requested date precedes'));
assert.ok(seasonalStockBasis(row).includes('10-day modeled window'));
row.seasonality = {};
assert.ok(seasonalPanel(row).includes('Inventory disabled for this quote'));
""")


def test_cli_price_uses_inventory_basis_without_changing_bulk_prices(monkeypatch, capsys):
    from argparse import Namespace
    from types import SimpleNamespace
    from faerun import cli
    from faerun.world import World

    payload = seasonal_payload()
    quote = SimpleNamespace(
        **payload, to_dict=lambda: payload, base_price=6, multiplier=1,
        demand_per_day=10, production_per_day=0, supply_index=1, demand_index=1,
        scarcity=1, source=None, factors={}, notes=[],
    )
    monkeypatch.setattr(cli, "price_for", lambda *args, **kwargs: quote)
    cli.cmd_price(Namespace(
        settlement="Cold town", commodity="grain", quantity=3, json=False,
    ), World())
    text = capsys.readouterr().out
    assert "buy from merchant 10.00 gp per bushel  (x3 = 30.00 gp)" in text
    assert "sell to merchant  8.00 gp per bushel  (x3 = 24.00 gp)" in text
    assert "after protected reserves" in text
    assert "over 10 modeled days" not in text
    assert "storage capacity" in text


def test_product_api_resolves_local_curve_and_retains_no_market_path(monkeypatch):
    from faerun import web
    from faerun.seasonality import seasonal_profile
    from faerun.world import World

    world = World()
    monkeypatch.setattr(web, "commodity_sources", lambda *args, **kwargs: {"sources": []})
    legacy = web.api_product(world, {"commodity": ["grain"]})
    assert legacy["seasonality"] == {}
    assert legacy["seasonal_inventory"] is False
    for key in ("production_profile", "demand_profile", "regional_production_profiles",
                "storage_days", "storage_loss", "reserve_days"):
        assert key in legacy["commodity"]
    result = web.api_product(world, {"commodity": ["grain"], "settlement": ["Bryn Shander"]})
    expected = seasonal_profile(
        world.find_commodity("grain"), world.find_settlement("Bryn Shander"), world.date
    )
    assert result["seasonality"] == expected
    assert result["settlement"] == "Bryn Shander"
    assert len(result["seasonality"]["months"]) == 12
    bootstrap = web.api_bootstrap(world, {})
    assert bootstrap["seasonal_inventory"] is False
    assert bootstrap["inventory_epoch"] == world.config.inventory_epoch
    grain = next(row for row in bootstrap["commodities"] if row["id"] == "grain")
    assert grain["storage_days"] == legacy["commodity"]["storage_days"]
    assert grain["regional_production_profiles"] == legacy["commodity"]["regional_production_profiles"]
