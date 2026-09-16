import json

import pytest

from faerun.detailassets import PRODUCT_HTML, PRODUCT_JS
from faerun.webassets import APP_JS
from test_seasonal_inventory_ui import run_js, seasonal_payload


def run_board_detail_script(test):
    row = {
        **seasonal_payload(),
        "base_price": 6,
        "multiplier": 1,
        "supply_index": 1,
        "demand_index": 1,
        "demand_per_day": 10,
        "production_type": "raw",
    }
    run_js(
        """
const assert = require('node:assert/strict');
const elements = new Map();
function element() {
  return {innerHTML:'', textContent:'', disabled:false, listeners:{},
    addEventListener(type, callback) {this.listeners[type] = callback;}};
}
const panel = element();
Object.defineProperty(panel, 'innerHTML', {
  get() {return this.markup || '';},
  set(value) {
    this.markup = value;
    for (const id of ['detail-history', 'load-detail-history', 'detail-compare']) {
      elements.set(id, element());
    }
  }
});
elements.set('detail', panel);
globalThis.document = {getElementById(id) {return elements.get(id) || null;}};
""" + APP_JS.replace("\nstart();\n", "\n")
        + "\nconst row = " + json.dumps(row) + ";\n" + """
state.boot = {commodities:[{id:'grain', name:'Grain', unit:'bushel'}]};
state.rows = [row];
state.selected = 'grain';
state.settlementId = 'cold_town';
state.report = {settlement:'Cold town'};
const requests = [];
getJSON = async function(path, params) {
  requests.push({path, params});
  return {markets:[], series:[], low:1, average:1, high:1};
};
(async function() {
""" + test + """
})().catch(error => {console.error(error); process.exitCode = 1;});
""")


def test_board_drill_through_does_not_request_price_history_automatically():
    run_board_detail_script("""
await renderDetail('grain');
assert.deepEqual(requests.map(r => r.path), ['/api/compare']);
assert.ok(panel.innerHTML.includes('product.html?commodity=grain&settlement=Cold%20town'));
assert.ok(panel.innerHTML.includes('id="load-detail-history"'));
assert.ok(panel.innerHTML.includes('Other API requests may wait'));
assert.ok(panel.innerHTML.includes('12-month production'));
""")


def test_board_history_is_explicit_retryable_and_ignores_duplicate_clicks():
    run_board_detail_script("""
await renderDetail('grain');
const button = elements.get('load-detail-history');
const box = elements.get('detail-history');
let calls = 0, complete;
getJSON = function(path, params) {
  assert.equal(path, '/api/history');
  assert.deepEqual(params, {settlement:'cold_town', commodity:'grain', months:12});
  calls++;
  if (calls === 1) return Promise.reject(new Error('History unavailable'));
  return new Promise(resolve => {complete = resolve;});
};
await button.listeners.click();
assert.equal(button.disabled, false);
assert.equal(box.textContent, 'History unavailable');
assert.ok(button.textContent.includes('Retry'));
const pending = button.listeners.click();
assert.equal(button.disabled, true);
await button.listeners.click();
assert.equal(calls, 2);
complete({series:[{month:'Hammer', price:1}, {month:'Alturiak', price:2}],
  low:1, average:1.5, high:2});
await pending;
assert.ok(box.innerHTML.includes('<svg'));
assert.ok(button.textContent.includes('loaded'));
assert.equal(button.disabled, true);
""")


@pytest.mark.parametrize("fails", [False, True], ids=["success", "failure"])
def test_old_history_result_does_not_replace_reopened_commodity(fails):
    run_board_detail_script("""
await renderDetail('grain');
let complete, fail;
getJSON = function(path) {
  if (path === '/api/compare') return Promise.resolve({markets:[]});
  return new Promise((resolve, reject) => {complete = resolve; fail = reject;});
};
const pending = elements.get('load-detail-history').listeners.click();
await renderDetail('grain');
const currentBox = elements.get('detail-history');
const currentButton = elements.get('load-detail-history');
""" + (
        "fail(new Error('Old request failed'));"
        if fails else "complete({series:[], low:1, average:1, high:1});"
    ) + """
await pending;
assert.equal(currentBox.innerHTML, '');
assert.equal(currentBox.textContent, '');
assert.equal(currentButton.disabled, false);
""")


@pytest.mark.parametrize("fails", [False, True], ids=["success", "failure"])
def test_old_market_comparison_does_not_replace_reopened_commodity(fails):
    run_board_detail_script("""
let complete, fail, calls = 0;
getJSON = function(path) {
  assert.equal(path, '/api/compare');
  if (++calls > 1) return Promise.resolve({markets:[]});
  return new Promise((resolve, reject) => {complete = resolve; fail = reject;});
};
const pending = renderDetail('grain');
await renderDetail('grain');
const currentBox = elements.get('detail-compare');
const currentMarkup = currentBox.innerHTML;
""" + (
        "fail(new Error('Old comparison failed'));"
        if fails else "complete({markets:[{settlement:'Old town', price:1, buy_price:1}]});"
    ) + """
await pending;
assert.equal(currentBox.innerHTML, currentMarkup);
assert.equal(currentBox.textContent, '');
""")


def test_product_start_shows_drill_through_target_while_bootstrap_is_pending():
    script = PRODUCT_JS.replace(
        "start().catch(function(e){setStatus(e.message,true);});", ""
    )
    run_js("""
const assert = require('node:assert/strict');
const elements = new Map();
globalThis.document = {getElementById(id) {
  if (!elements.has(id)) elements.set(id,
    {value:'', innerHTML:'', textContent:'', addEventListener(){}});
  return elements.get(id);
}};
globalThis.location = {search:'?commodity=grain&settlement=Cold%20town'};
globalThis.showWorldDate = function() {};
""" + script + """
let complete, loaded = false;
get = function(path) {
  assert.equal(path, '/api/bootstrap');
  return new Promise(resolve => {complete = resolve;});
};
load = async function() {loaded = true;};
(async function() {
  const pending = start();
  assert.equal(document.getElementById('product').value, 'grain');
  assert.equal(document.getElementById('market').value, 'Cold town');
  assert.match(document.getElementById('status').textContent, /Loading/);
  assert.equal(loaded, false);
  complete({commodities:[{name:'Grain', category:'food'}],
    settlements:[{name:'Cold town', region:'North'}]});
  await pending;
  assert.equal(loaded, true);
})().catch(error => {console.error(error); process.exitCode = 1;});
""")
    assert 'id="status" class="status" role="status"' in PRODUCT_HTML
