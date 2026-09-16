import json
import subprocess

import pytest

from faerun.detailassets import COMMON_JS, PRODUCT_JS
from faerun.locationassets import LOCATION_HTML, LOCATION_JS
from faerun.mapassets import MAP_JS
from faerun.webassets import APP_JS, INDEX_HTML
from test_requirements_ui import run_location_script


@pytest.mark.parametrize("script", [APP_JS, LOCATION_JS, PRODUCT_JS, MAP_JS],
                         ids=["board", "location", "product", "map"])
def test_price_scripts_compile(script):
    result = subprocess.run(["node", "--check"], input=script, capture_output=True,
                            text=True, encoding="utf-8", timeout=20)
    assert result.returncode == 0, result.stderr


def test_all_price_views_name_both_directions_and_free_stock():
    for text in (INDEX_HTML, APP_JS, LOCATION_HTML, LOCATION_JS, PRODUCT_JS, MAP_JS):
        assert "Buy from merchant" in text
        assert "Sell to merchant" in text
        assert "Uncommitted" in text
    assert 'data-sort="merchant_markup_pct"' in INDEX_HTML
    assert 'data-sort="uncommitted_stock"' in INDEX_HTML
    assert "Total minus final demand is required processing input" in LOCATION_HTML


def test_low_value_buy_and_sell_prices_do_not_round_to_the_same_display():
    start = MAP_JS.index("function gp(value)")
    end = MAP_JS.index("function clamp", start)
    script = COMMON_JS + MAP_JS[start:end] + """
console.log(JSON.stringify({
  productBuy:coin(.022),productSell:coin(.016),mapBuy:quotePrice(.022),mapSell:quotePrice(.016),
  mapFull:quotePrice(1.138),productFull:coin(1.138),
  expectedFull:(1.138).toLocaleString(undefined,{minimumFractionDigits:2,maximumFractionDigits:3})
}));
"""
    result = subprocess.run(["node", "-"], input=script, capture_output=True,
                            text=True, encoding="utf-8", timeout=20)
    assert result.returncode == 0, result.stderr
    prices = json.loads(result.stdout)
    assert prices["productBuy"] != prices["productSell"]
    assert prices["mapBuy"] != prices["mapSell"]
    assert prices["mapFull"] == prices["expectedFull"]
    assert prices["productFull"] == prices["expectedFull"] + " gp"


def test_location_renders_two_prices_markup_and_uncommitted_quantity():
    run_location_script("""
ui.state.settlement = 'Town';
ui.state.detail = detail('Town', 100, requirements());
ui.state.detail.market.prices = [{
  commodity:'grain', commodity_name:'Grain', category:'food', production_type:'raw',
  unit:'bushel', price:10, buy_price:8, merchant_markup_pct:25,
  multiplier:1.1, stock:100, uncommitted_stock:20, stock_horizon_days:10,
  demand_per_day:8, availability:'common', source:null
}];
ui.renderTable();
const html = ui.el['price-table'].querySelector('tbody').innerHTML;
assert.ok(html.includes('>10.00</td>'));
assert.ok(html.includes('>8.00</td>'));
assert.ok(html.includes('>25.0%</td>'));
assert.ok(html.includes('10-day modeled window'));
assert.ok(html.includes('>20</td>'));
assert.equal((html.match(/<td/g)||[]).length, 14);
const data = requirements();
data.materials[0].uncommitted_supply_per_day = 0;
data.materials[1].uncommitted_supply_per_day = 3;
data.materials[1].uncommitted_stock = 30;
data.materials[1].stock_horizon_days = 10;
ui.state.detail.requirements = data;
ui.state.materialFilter = 'uncommitted';
ui.renderRequirementsTable();
assert.equal(ui.el['requirements-count'].textContent, '1 of 2 materials');
assert.ok(ui.el['requirements-table'].querySelector('tbody').innerHTML.includes('>30</td>'));
""")
