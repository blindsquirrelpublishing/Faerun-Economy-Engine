from copy import deepcopy
from dataclasses import replace
import json
import subprocess

import pytest

from faerun import settlement_analysis, web
from faerun.daggerfordassets import DAGGERFORD_HTML, DAGGERFORD_JS
from faerun.data.settlements import SETTLEMENTS
from faerun.population import population_report
from faerun.world import World


def daggerford():
    return deepcopy(next(s for s in SETTLEMENTS if s.id == "daggerford"))


def test_analysis_api_mcp_and_population_discovery_are_consistent(monkeypatch):
    settlement = replace(daggerford(), population=1717)
    world = World(settlements=[settlement])
    before = world.revision
    report = web.GET_ROUTES["/api/settlement-analysis"](world, {"settlement": ["Daggerford"]})
    assert report["active_baseline"]["resident_population"] == 1717
    assert report["active_population_unchanged"] is True
    assert report["population"]["recommended_resident_population"] is None
    assert report["inventory_summary"]["reviewed_roof_groups"] == 140
    assert len(report["streets"]) == 11
    assert population_report(settlement)["settlement_analysis_page"] == "daggerford.html"
    assert population_report(settlement)["settlement_analysis_endpoint"] == "/api/settlement-analysis?settlement=Daggerford"
    assert world.revision == before
    pytest.importorskip("mcp")
    from faerun import mcp_server

    monkeypatch.setattr(mcp_server, "world", lambda: world)
    assert mcp_server.get_settlement_analysis() == report
    assert "error" in mcp_server.get_settlement_analysis("Unknown")
    assert world.revision == before


def test_optional_preview_is_explicit_and_never_silently_substituted(monkeypatch, tmp_path):
    monkeypatch.setattr(settlement_analysis, "DAGGERFORD_PREVIEW", tmp_path / "absent.jpg")
    report = settlement_analysis.settlement_analysis_report(daggerford())
    assert report["map"]["local_image_available"] is False
    assert report["map"]["local_image_url"] is None
    assert report["map"]["source_hash_verification"]["status"] == "not_checked"
    bad = tmp_path / "wrong.jpg"
    bad.write_bytes(b"not the audited source map")
    monkeypatch.setattr(settlement_analysis, "DAGGERFORD_PREVIEW", bad)
    with pytest.raises(ValueError, match="SHA-256"):
        settlement_analysis.settlement_analysis_report(daggerford())
    with pytest.raises(KeyError):
        settlement_analysis.settlement_analysis_report(replace(daggerford(), id="waterdeep"))


def test_daggerford_page_and_optional_local_image_are_registered():
    assert {"daggerford.html", "daggerford.css", "daggerford.js"} <= web.STATIC.keys()
    assert web.BINARY_STATIC["daggerford-map.jpg"][0] == settlement_analysis.DAGGERFORD_PREVIEW
    assert "North points left" in DAGGERFORD_HTML
    assert "footprint boundaries" in DAGGERFORD_HTML
    for identifier in ("active-residents", "roof-count", "street-count", "town-overlay",
                       "population-evidence", "analysis-download", "occupancy-scenarios"):
        assert f'id="{identifier}"' in DAGGERFORD_HTML


def run_page_script(checks):
    data = settlement_analysis.settlement_analysis_report(daggerford())
    body = DAGGERFORD_JS.split("(function () {", 1)[1].rsplit("}());", 1)[0].rsplit("  load();", 1)[0]
    setup = r"""
const assert = require('node:assert/strict');
class Element {
  constructor() {
    this.children=[]; this.listeners={}; this.style={}; this.attributes=new Map();
    this.value='1'; this.textContent=''; this.hidden=false; this.disabled=false; this.checked=true;
    this.clientWidth=800; this.clientHeight=700; this.offsetLeft=0;
    const classes=new Set();
    this.classList={add:n=>classes.add(n),remove:n=>classes.delete(n),contains:n=>classes.has(n)};
  }
  addEventListener(name, callback) { this.listeners[name]=callback; }
  appendChild(child) { this.children.push(child); return child; }
  replaceChildren(...children) { this.children=children; }
  setAttribute(key,value) {
    this.attributes.set(key,String(value));
    if(key==='class') String(value).split(' ').forEach(n=>this.classList.add(n));
  }
  getBBox() { return {x:100,y:200,width:80,height:200}; }
  get textContent() { return this._text || ''; }
  set textContent(value) { this._text=String(value); }
  click() {}
}
const elements=new Map();
globalThis.document={
  getElementById(id) {
    if(!elements.has(id)) elements.set(id,new Element());
    return elements.get(id);
  },
  createElement:()=>new Element(), createElementNS:()=>new Element()
};
globalThis.window={addEventListener(){}};
"""
    script = setup + "\nconst fixture = " + json.dumps(data) + ";\n" + body + """
(async () => {
""" + checks + """
})().catch(error => { console.error(error); process.exitCode=1; });
"""
    result = subprocess.run(["node", "-"], input=script, capture_output=True, text=True)
    assert result.returncode == 0, result.stdout + result.stderr


def test_page_renders_actual_counts_streets_and_unknown_population():
    run_page_script("""
globalThis.fetch=async url=>{
  assert.equal(url,'/api/settlement-analysis?settlement=Daggerford');
  return {ok:true,json:async()=>fixture};
};
await load();
assert.equal(el('roof-count').textContent,'140');
assert.equal(el('street-count').textContent,'11');
assert.equal(el('active-residents').textContent,'900');
assert.equal(el('roof-layer').children.length,140);
assert.equal(el('street-layer').children.length,11);
assert.equal(el('analysis-download').disabled,false);
assert.ok(el('occupancy-scenarios').children.every(row=>row.children[2].textContent==='Unknown'));
assert.ok(el('scale-note').textContent.includes('conflicting'));
assert.ok(el('analysis-blockers').children.every(node => !node.textContent.includes('[object Object]')));
assert.ok(el('analysis-blockers').children.some(node => node.textContent.includes('Buildings and occupancy:')));
assert.equal(el('town-overlay').attributes.get('viewBox'),'0 0 864 1210');
el('street-select').value=fixture.streets[0].id;
el('street-form').listeners.submit({preventDefault(){}});
assert.equal(el('selection-title').textContent,fixture.streets[0].name);
assert.ok(streetNodes.get(fixture.streets[0].id).classList.contains('selected'));
el('show-roofs').checked=false;
el('show-roofs').listeners.change.call(el('show-roofs'));
assert.equal(el('roof-layer').style.display,'none');
""")


def test_missing_map_and_network_failures_do_not_become_empty_censuses():
    run_page_script("""
fixture.map.local_image_available=false; fixture.map.local_image_url=null;
globalThis.fetch=async()=>({ok:true,json:async()=>fixture});
await load();
assert.equal(el('town-map').hidden,true);
assert.ok(el('map-status').textContent.includes('unavailable'));
assert.equal(el('roof-count').textContent,'140');
globalThis.fetch=async()=>({ok:false,status:503});
await load();
assert.equal(report,null);
assert.equal(el('analysis-results').hidden,true);
assert.equal(el('analysis-download').disabled,true);
assert.equal(el('analysis-reload').disabled,false);
assert.ok(el('analysis-status').textContent.includes('503'));
globalThis.fetch=async()=>({ok:true,json:async()=>({})});
await load();
assert.ok(el('analysis-status').textContent.includes('Invalid Daggerford'));
""")
