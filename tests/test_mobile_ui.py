import json
import subprocess

import pytest

from faerun.calendar import HarptosDate
from faerun.detailassets import DETAIL_CSS
from faerun.mobile_economy import mobile_economic_report
from faerun.mobileassets import MOBILE_CSS, MOBILE_HTML, MOBILE_JS
from faerun.web import STATIC
from faerun.world import World


def test_mobile_page_uses_shared_fluid_detail_layout():
    assert '<main class="detail-shell mobile-shell">' in MOBILE_HTML
    assert '<form id="controls" class="detail-controls">' in MOBILE_HTML
    assert MOBILE_HTML.index('href="app.css"') < MOBILE_HTML.index('href="detail.css"')
    assert MOBILE_HTML.index('href="detail.css"') < MOBILE_HTML.index('href="mobile.css"')
    assert STATIC["detail.css"][0] == DETAIL_CSS
    assert "1180px" not in MOBILE_CSS
    assert ".mobile-shell .mobile-itinerary { min-width: 760px; }" in MOBILE_CSS
    assert "overflow: auto" in DETAIL_CSS


@pytest.mark.parametrize("day", [14, 18])
def test_mobile_renderer_preserves_profile_in_responsive_sections(day):
    world = World(date=HarptosDate(1492, 9, day))
    profile = world.find_mobile_location("silver_wheel").profile(world)
    script = """
const assert = require('node:assert/strict');
const elements = {
  'mobile-location': {value:''},
  hero: {innerHTML:''},
  content: {innerHTML:''}
};
globalThis.document = {getElementById(id) {return elements[id];}};
globalThis.history = {replaceState() {}};
""" + MOBILE_JS.split("async function load(){")[0] + """
const profile = """ + json.dumps(profile) + """;
render(profile);
assert.equal(elements['mobile-location'].value, profile.name);
assert.ok(elements.hero.innerHTML.includes(profile.name));
assert.equal((elements.hero.innerHTML.match(/class="fact"/g) || []).length, 4);
const html = elements.content.innerHTML;
assert.ok(html.startsWith('<div class="detail-grid">'));
assert.equal((html.match(/class="detail-section"/g) || []).length, 6);
assert.ok(html.includes('class="detail-section wide"'));
for (const name of ['Daily requirements', 'People and roles', 'Wagons and animals',
                    'Carried inventory', 'Dated itinerary']) {
  assert.ok(html.includes('tabindex="0" role="region" aria-label="' + name + '"'));
}
assert.equal((html.match(/class="detail-table mobile-table"/g) || []).length, 4);
assert.ok(html.includes('class="detail-table mobile-itinerary"'));
assert.ok(html.includes('<th scope="col">Camp or route</th>'));
assert.equal((html.match(/class="active"/g) || []).length, 1);
assert.ok(html.includes('Services offered'));
assert.ok(html.includes('Specialties'));
if (profile.position.host) {
  assert.ok(html.includes('Open host settlement'));
  assert.ok(html.includes('location.html?settlement=' + profile.position.host.id));
} else {
  assert.ok(html.includes('Travelling from Waterdeep to Amphail'));
  assert.ok(!html.includes('Open host settlement'));
}
assert.ok(table(['A', 'B'], '', 'Quoted "region"').includes('aria-label="Quoted &quot;region&quot;"'));
"""
    result = subprocess.run(
        ["node", "-"], input=script, capture_output=True, text=True,
        encoding="utf-8", timeout=20,
    )
    assert result.returncode == 0, result.stdout + result.stderr


def test_economic_report_generation_export_and_stale_request_protection():
    world = World(date=HarptosDate(1492, 9, 18))
    report = mobile_economic_report("silver_wheel", world)
    script = """
const assert = require('node:assert/strict');
const elements = {};
for (const id of ['mobile-location', 'hero', 'content', 'status',
                  'economic-report', 'generate-report', 'download-report']) {
  elements[id] = {value:'silver_wheel', innerHTML:'', textContent:'',
    disabled:true, hidden:true, setAttribute(name,value){this[name]=value;}};
}
let clicked = false, removed = false, blob, link, cleanup;
globalThis.document = {
  getElementById(id) {return elements[id];},
  createElement() {
    link = {click(){clicked=true;}, remove(){removed=true;}};
    return link;
  },
  body: {appendChild(){}}
};
globalThis.history = {replaceState(){}};
globalThis.location = {search:''};
globalThis.showWorldDate = function(){};
globalThis.window = {setTimeout(fn){cleanup=fn;}};
globalThis.URL.createObjectURL = function(value){blob=value;return 'blob:report';};
let revoked = false;
globalThis.URL.revokeObjectURL = function(value){assert.equal(value,'blob:report');revoked=true;};
""" + MOBILE_JS.split("\ndocument.getElementById('controls')")[0] + """
const report = """ + json.dumps(report) + """;
async function verify() {
  downloadReport();
  assert.ok(elements.status.textContent.includes('Generate an economic report'));
  assert.equal(clicked,false);
  reportState.profile=report.location;
  globalThis.fetch = async function(path){
    assert.equal(path,'/api/mobile-economy?id=silver_wheel');
    return {ok:true,json:async()=>report};
  };
  const pending=generateReport();
  assert.equal(elements['generate-report'].disabled,true);
  assert.equal(elements['download-report'].disabled,true);
  await pending;
  assert.equal(elements['generate-report'].disabled,false);
  assert.equal(elements['download-report'].disabled,false);
  assert.equal(elements['economic-report'].hidden,false);
  const html=elements['economic-report'].innerHTML;
  for(const text of ['Economic report','Household provisioning benchmark',
                    'Supply cover and tenday resupply','Carried stock valuation',
                    'not modeled','Assumptions and exclusions']) {
    assert.ok(html.includes(text),text);
  }
  assert.ok(html.includes('tabindex="0" role="region" aria-label="Supply cover"'));
  assert.ok(html.includes('no trading access while travelling'));
  downloadReport();
  assert.equal(clicked,true);
  assert.equal(removed,true);
  assert.equal(blob.type,'application/json');
  assert.equal(link.download,'mobile-economy-silver_wheel-1492-09-18.json');
  const exported=JSON.parse(await blob.text());
  assert.deepEqual(exported,report);
  assert.equal(exported.economy.accounts.gross_local_product_gp_per_day,null);
  assert.equal(exported.economy.accounts.gross_local_product_status,'not_calculated');
  cleanup();assert.equal(revoked,true);

  const unsafe=structuredClone(report);
  unsafe.economy.assumptions.push('<img src=x onerror=alert(1)>');
  renderEconomicReport(unsafe);
  assert.ok(elements['economic-report'].innerHTML.includes('&lt;img'));
  assert.ok(!elements['economic-report'].innerHTML.includes('<img'));

  globalThis.fetch=async()=>({ok:false,json:async()=>({error:'Pricing unavailable'})});
  await generateReport();
  assert.equal(elements['economic-report'].hidden,true);
  assert.equal(elements['download-report'].disabled,true);
  assert.equal(elements['generate-report'].disabled,false);
  assert.equal(reportState.report,null);
  assert.equal(elements.status.textContent,'Pricing unavailable');
  assert.equal(elements.status.className,'status error');

  let finish;
  globalThis.fetch=()=>new Promise(resolve=>{finish=resolve;});
  const staleReport=generateReport();
  invalidateSelection();
  finish({ok:true,json:async()=>report});
  await staleReport;
  assert.equal(reportState.report,null);
  assert.equal(elements['economic-report'].hidden,true);
  assert.equal(elements['download-report'].disabled,true);
  assert.equal(elements['generate-report'].disabled,true);

  const staleProfile=load();
  invalidateSelection();
  finish({ok:true,json:async()=>report.location});
  await staleProfile;
  assert.equal(reportState.profile,null);

  globalThis.fetch=async()=>({ok:true,json:async()=>report.location});
  await load();
  assert.equal(reportState.profile.id,'silver_wheel');
  assert.equal(elements['generate-report'].disabled,false);
  assert.equal(elements['download-report'].disabled,true);
  globalThis.fetch=async()=>({ok:true,json:async()=>report});
  await generateReport();
  assert.equal(elements['download-report'].disabled,false);
}
verify().catch(error=>{console.error(error);process.exitCode=1;});
"""
    result = subprocess.run(
        ["node", "-"], input=script, capture_output=True, text=True,
        encoding="utf-8", timeout=20,
    )
    assert result.returncode == 0, result.stdout + result.stderr
