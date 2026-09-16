import json
import subprocess

from faerun.detailassets import COMMON_JS, PRODUCT_JS
from faerun.sourceassets import SOURCING_JS
from faerun.webassets import APP_JS


def test_supplier_renderer_and_page_scripts():
    script = COMMON_JS + SOURCING_JS + r"""
const assert = require('node:assert/strict');
const quote = {unit: 'bushel', sources: [
  {source_id:'town', source:'Local <mill>', supply_type:'local', quantity_per_day:20, share:0.2, unit_cost:1, days:0, distance:0},
  {source_id:'farm', source:'Farm', supply_type:'import', quantity_per_day:60, share:0.6, unit_cost:2, days:2, distance:40}
], unmet_demand_per_day:20, exports_per_day:0,
backup_sources:[{source:'Reserve', available_per_day:30, days:3, unit_cost:4}]};
assert.match(sourceSummary(quote), /Local 20%.*1 supplier.*Shortfall 20/);
const html = sourceBreakdown(quote);
assert.match(html, /Local &lt;mill&gt;/);
assert.match(html, /Backup suppliers \(unreserved\): 1/);
assert.match(html, /Unmet demand: 20 bushel\/day/);
assert.equal(sourceSummary({sources:[]}), 'No allocated supply');
assert.match(sourceSummary({...quote, sources:[...quote.sources, quote.sources[1]]}), /2 suppliers/);
const material = sourceBreakdown({...quote, production_capacity_per_day:100, production_per_day:20,
  production_inputs:[{commodity:'flour',unit:'sack',required_per_day:2,reserved_per_day:1,consumed_per_day:0.4}],
  household_demand_per_day:100,household_consumption_per_day:20,
  processing_demand_per_day:0,processing_consumption_per_day:0,material_closing_stock:0});
assert.match(material, /Daily material balance/);
assert.match(material, /Output: 20 \/ Capacity: 100/);
assert.match(material, /flour<\/a> \(sack\)/);
assert.match(material, /Consumed\/day/);
assert.equal(materialBreakdown(quote), '');
"""
    script += "\nnew Function(" + json.dumps(APP_JS) + ");"
    script += "\nnew Function(" + json.dumps(PRODUCT_JS) + ");"
    subprocess.run(["node", "-"], input=script, check=True, capture_output=True, text=True)