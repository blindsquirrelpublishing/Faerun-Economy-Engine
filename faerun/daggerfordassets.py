"""Daggerford's source-linked town survey, distinct from the Waterdeep atlas."""

DAGGERFORD_HTML = """<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Daggerford town analysis</title>
<script>
document.documentElement.dataset.theme = new URLSearchParams(location.search).get('scoutTheme') ||
  (matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light');
</script>
<link rel="stylesheet" href="daggerford.css"></head><body>
<header><div><span class="eyebrow">Source-linked settlement analysis</span><h1>Daggerford</h1></div>
<nav aria-label="Related pages"><a href="map.html">World map</a>
<a href="location.html?settlement=Daggerford">Daggerford market</a>
<a href="waterdeep.html#city-survey">Waterdeep survey</a></nav></header>
<main>
<div class="actions"><button id="analysis-reload" type="button">Refresh analysis</button>
<button id="analysis-download" type="button" disabled>Download evidence JSON</button></div>
<p id="analysis-status" role="status" aria-live="polite">Loading evidence...</p>
<div id="analysis-results" hidden>
<section class="facts" aria-label="Analysis summary">
<div><b id="active-residents"></b><span>active model residents, unchanged</span></div>
<div><b id="roof-count"></b><span>indexed roof groups, not buildings</span></div>
<div><b id="street-count"></b><span>approximately traced named streets</span></div>
</section>
<div class="analysis-grid">
<section class="map-card" aria-labelledby="map-title">
<h2 id="map-title">Town, castle &amp; riverfront</h2>
<p>North points left on this published map. Outlying farms, the area inset and
the tannery across the river are excluded.</p>
<div class="map-controls">
<label><input id="show-roofs" type="checkbox" checked>Roof groups</label>
<label><input id="show-streets" type="checkbox" checked>Named streets</label>
<label><input id="show-boundaries" type="checkbox" checked>Boundary</label>
<label for="map-zoom">Zoom</label><input id="map-zoom" type="range" min="1" max="3" step=".25" value="1">
</div>
<form id="street-form"><label for="street-select">Find a street</label>
<select id="street-select"></select><button type="submit">Locate</button></form>
<p id="map-status" role="status"></p>
<div id="town-map" class="map-scroll" tabindex="0" aria-label="Zoomable Daggerford source map; scroll to pan">
<div id="map-plane"><img id="source-image" alt="Mike Schley's illustrated map of Daggerford">
<svg id="town-overlay" role="img" aria-label="Reviewed roof-group points and approximate street routes">
<g id="boundary-layer"></g><g id="street-layer"></g><g id="roof-layer"></g></svg></div></div>
<p>Dots identify roof groups, not footprint boundaries. Red dots have explicit
grouping caveats. Select a dot or street to inspect its evidence.</p>
<p id="map-attribution"></p>
<section id="selection" hidden aria-live="polite"><h3 id="selection-title"></h3><pre id="selection-details"></pre></section>
</section>
<aside>
<section class="card"><h2>Population evidence</h2>
<p id="population-note"></p><div class="table-scroll"><table>
<thead><tr><th>Count</th><th>DR year</th><th>Scope &amp; evidence</th></tr></thead>
<tbody id="population-evidence"></tbody></table></div>
<p>No automatic growth or population change is inferred between source dates.</p></section>
<section class="card"><h2>Survey coverage</h2><p id="inventory-summary"></p>
<ul id="analysis-blockers"></ul></section>
<section class="card"><h2>Occupancy sensitivity</h2><p id="sensitivity-note"></p>
<div class="table-scroll"><table><thead><tr><th>Scenario</th><th>Conditional component</th><th>Town total</th></tr></thead>
<tbody id="occupancy-scenarios"></tbody></table></div>
<p>These are assumption-driven components, not a measured population or confidence interval.
Unknown institutional residents are not silently treated as zero.</p></section>
<section class="card"><h2>Map scale</h2><p id="scale-note"></p><pre id="scale-details"></pre></section>
<section class="card"><h2>Sources</h2><ul id="analysis-sources"></ul></section>
<details class="card"><summary>Survey rules &amp; caveats</summary><pre id="survey-caveats"></pre></details>
</aside></div></div></main>
<script src="daggerford.js"></script></body></html>
"""

DAGGERFORD_CSS = """
:root { color-scheme: light; --bg:#f7f4ef; --surface:#fff; --text:#242424;
  --muted:#5c5c5c; --border:#dedede; --accent:#b11f4b; --link:#005a9e; }
html[data-theme="dark"] { color-scheme:dark; --bg:#292929; --surface:#343231;
  --text:#dedede; --muted:#b0b0b0; --border:#5f5f5f; --accent:#fd8ea1; --link:#72b8eb; }
* { box-sizing:border-box; } [hidden] { display:none !important; }
body { margin:0; background:var(--bg); color:var(--text); font:15px/1.5 "Segoe UI",sans-serif; }
header { padding:18px 24px; display:flex; justify-content:space-between; gap:20px;
  align-items:center; background:var(--surface); border-bottom:1px solid var(--border); }
h1 { margin:0; font-size:28px; } h2 { margin:0 0 10px; font-size:19px; }
h3 { font-size:16px; } .eyebrow { text-transform:uppercase; letter-spacing:.12em; color:var(--accent); font-size:11px; font-weight:700; }
nav { display:flex; flex-wrap:wrap; gap:18px; } a { color:var(--link); }
main { padding:20px 24px; max-width:1800px; margin:auto; }
button,select,input { font:inherit; } button,select { padding:7px 10px; border:1px solid var(--border);
  border-radius:6px; background:var(--surface); color:var(--text); }
button { cursor:pointer; } button:hover { border-color:var(--accent); }
button:disabled { opacity:.5; cursor:default; }
.actions,.map-controls { display:flex; gap:12px; flex-wrap:wrap; align-items:center; }
.facts { display:grid; grid-template-columns:repeat(3,1fr); gap:14px; margin:16px 0; }
.facts div,.card,.map-card { background:var(--surface); border:1px solid var(--border); border-radius:10px; padding:18px; }
.facts b { display:block; color:var(--accent); font-size:28px; }
.facts span { color:var(--muted); font-size:12px; }
.analysis-grid { display:grid; grid-template-columns:minmax(0,1fr) 390px; gap:18px; align-items:start; }
.card { margin-bottom:16px; } .map-card { min-width:0; }
.map-card p { font-size:13px; color:var(--muted); }
#street-form { display:flex; flex-wrap:wrap; gap:8px; align-items:center; margin:15px 0; }
.map-scroll { position:relative; height:calc(100vh - 270px); min-height:420px; overflow:auto;
  border:1px solid var(--border); background:var(--bg); }
#map-plane { position:relative; margin:0 auto; }
#source-image { display:block; width:100%; height:100%; }
#town-overlay { position:absolute; inset:0; width:100%; height:100%; }
.boundary { fill:none; stroke:#6d489d; stroke-width:1.5; stroke-dasharray:6 4; pointer-events:none; vector-effect:non-scaling-stroke; }
.street { fill:none; stroke:#006fa6; stroke-width:2; pointer-events:stroke; cursor:pointer; vector-effect:non-scaling-stroke; }
.roof { fill:#dc921a; stroke:#4a3210; stroke-width:.6; cursor:pointer; vector-effect:non-scaling-stroke; }
.roof.caveated { fill:#e34a4a; } .selected { stroke:#eb1c75; stroke-width:4; }
#selection { border-top:1px solid var(--border); margin-top:12px; }
pre { font-size:12px; white-space:pre-wrap; overflow-wrap:anywhere; max-height:300px; overflow-y:auto; }
.table-scroll { overflow:auto; } table { width:100%; border-collapse:collapse; font-size:12px; }
th,td { text-align:left; vertical-align:top; padding:7px 4px; border-bottom:1px solid var(--border); }
ul { padding-left:20px; } #analysis-sources li { margin-bottom:14px; }
@media(max-width:1000px) { .analysis-grid { grid-template-columns:1fr; } header { align-items:flex-start; flex-direction:column; } }
@media(max-width:550px) { main { padding:12px; } .facts { grid-template-columns:1fr; } }
"""

DAGGERFORD_JS = r"""
(function () {
  'use strict';
  var report = null;
  var selected = null;
  var streetNodes = new Map();
  var ns = 'http://www.w3.org/2000/svg';
  function el(id) { return document.getElementById(id); }
  function text(id, value) { el(id).textContent = value; }
  function number(value) { return Number(value).toLocaleString(undefined, {maximumFractionDigits:1}); }
  function svg(tag, attrs) {
    var node = document.createElementNS(ns, tag);
    Object.keys(attrs).forEach(function (key) { node.setAttribute(key, attrs[key]); });
    return node;
  }
  function path(points, closed) {
    return points.map(function (point, i) { return (i ? 'L' : 'M') + point[0] + ',' + point[1]; }).join(' ') +
      (closed ? ' Z' : '');
  }
  function row(target, values) {
    var tr = document.createElement('tr');
    values.forEach(function (value) {
      var td = document.createElement('td'); td.textContent = value; tr.appendChild(td);
    });
    el(target).appendChild(tr);
  }
  function showSelection(node, title, details) {
    if (selected) { selected.classList.remove('selected'); }
    selected = node; node.classList.add('selected');
    text('selection-title', title);
    text('selection-details', JSON.stringify(details, null, 2));
    el('selection').hidden = false;
  }
  function fitMap() {
    if (!report || !report.map.local_image_available) { return; }
    var host = el('town-map');
    var width = Math.min(host.clientWidth, host.clientHeight * report.map.width_px / report.map.height_px);
    el('map-plane').style.width = width * Number(el('map-zoom').value) + 'px';
  }
  function renderMap(data) {
    ['boundary-layer','street-layer','roof-layer'].forEach(function (id) { el(id).replaceChildren(); });
    el('selection').hidden = true;
    streetNodes.clear(); selected = null;
    el('street-select').replaceChildren();
    var imageAvailable = data.map.local_image_available;
    el('town-map').hidden = !imageAvailable;
    text('map-status', imageAvailable
      ? 'Source image checksum verified. Zoom and scroll to inspect the drawing.'
      : 'Local source preview is unavailable. The evidence report is still available; open the cartographer source below.');
    el('town-overlay').setAttribute('viewBox', '0 0 ' + data.map.width_px + ' ' + data.map.height_px);
    el('map-plane').style.aspectRatio = data.map.width_px + ' / ' + data.map.height_px;
    if (imageAvailable) { el('source-image').src = data.map.local_image_url; }
    Object.keys(data.scope.polygons_px).forEach(function (key) {
      el('boundary-layer').appendChild(svg('path', {d:path(data.scope.polygons_px[key], true), class:'boundary'}));
    });
    data.streets.forEach(function (street) {
      var node = svg('path', {d:path(street.points, false), class:'street'});
      var title = svg('title', {}); title.textContent = street.name; node.appendChild(title);
      node.addEventListener('click', function () { showSelection(node, street.name, street); });
      el('street-layer').appendChild(node); streetNodes.set(street.id, node);
      var option = document.createElement('option');
      option.value = street.id; option.textContent = street.name; el('street-select').appendChild(option);
    });
    Object.keys(data.roof_groups).forEach(function (sector) {
      data.roof_groups[sector].forEach(function (group) {
        var caveats = data.roof_group_caveats.filter(function (item) { return item.ids.includes(group[0]); });
        var node = svg('circle', {cx:group[1],cy:group[2],r:3.5,class:'roof' + (caveats.length ? ' caveated' : '')});
        var title = svg('title', {}); title.textContent = 'Roof group ' + group[0]; node.appendChild(title);
        node.addEventListener('click', function () {
          showSelection(node, 'Roof group ' + group[0], {
            id:group[0], sector:sector, landmark:group[3] === null ? null : data.landmarks[String(group[3])],
            unit:'Source roof group, not verified building identity or households', caveats:caveats
          });
        });
        el('roof-layer').appendChild(node);
      });
    });
    text('map-attribution', 'Map: Mike Schley for Scourge of the Sword Coast; copyright Wizards of the Coast. Local analysis of the author-linked public preview; no redistribution license inferred.');
  }
  function render(data) {
    if (!data || data.settlement_id !== 'daggerford' || !data.inventory_summary ||
        !Array.isArray(data.streets) || !Array.isArray(data.population.historical_evidence) ||
        !Number.isInteger(data.active_baseline.resident_population)) {
      throw new Error('Invalid Daggerford analysis response');
    }
    text('active-residents', number(data.active_baseline.resident_population));
    text('roof-count', number(data.inventory_summary.reviewed_roof_groups));
    text('street-count', number(data.streets.length));
    text('population-note', data.population.revision_status);
    el('population-evidence').replaceChildren();
    data.population.historical_evidence.forEach(function (item) {
      row('population-evidence', [number(item.value), item.year_dr == null ? 'Undated' : item.year_dr,
        item.scope + '. ' + item.status]);
    });
    text('inventory-summary', data.inventory_summary.groups_with_explicit_caveats + ' groups have explicit caveats; ' +
      data.inventory_summary.additional_unresolved_symbols + ' further symbols remain unresolved. ' +
      data.inventory_summary.landmark_keys + ' landmark keys are not a building count. Full building and unnamed-street inventories are not established.');
    el('analysis-blockers').replaceChildren();
    data.blockers.forEach(function (blocker) {
      if (typeof blocker.area !== 'string' || typeof blocker.detail !== 'string') {
        throw new Error('Invalid analysis blocker');
      }
      var li = document.createElement('li');
      li.textContent = blocker.area + ': ' + blocker.detail;
      el('analysis-blockers').appendChild(li);
    });
    text('sensitivity-note', data.sensitivity.status + '. ' + data.sensitivity.eligible_roof_groups +
      ' roof groups are eligible for this illustration; this is not residential classification.');
    el('occupancy-scenarios').replaceChildren();
    data.sensitivity.scenarios.forEach(function (scenario) {
      row('occupancy-scenarios', [scenario.name, number(scenario.conditional_noninstitutional_component), 'Unknown']);
    });
    text('scale-note', 'The printed scale has conflicting tick/terminal-label interpretations. No physical scale or town area has been adopted.');
    text('scale-details', JSON.stringify(data.map.scale, null, 2));
    el('analysis-sources').replaceChildren();
    data.sources.forEach(function (source) {
      var li = document.createElement('li');
      var link = document.createElement('a'); link.textContent = source.title;
      var url = new URL(source.url);
      if (!['https:', 'http:'].includes(url.protocol)) { throw new Error('Invalid source URL'); }
      link.href = url.href; link.target = '_blank'; link.rel = 'noopener noreferrer';
      li.appendChild(link);
      var p = document.createElement('p'); p.textContent = source.summary; li.appendChild(p);
      el('analysis-sources').appendChild(li);
    });
    text('survey-caveats', JSON.stringify({
      scope:data.scope, roof_group_caveats:data.roof_group_caveats,
      unresolved_symbols:data.unresolved_symbols, street_notes:data.street_notes,
      sensitivity_assumptions:data.sensitivity, map:data.map
    }, null, 2));
    renderMap(data);
    el('analysis-results').hidden = false;
  }
  function load() {
    el('analysis-reload').disabled = true; el('analysis-download').disabled = true;
    el('analysis-results').hidden = true; report = null;
    text('analysis-status', 'Loading source evidence...');
    return fetch('/api/settlement-analysis?settlement=Daggerford').then(function (response) {
      if (!response.ok) { throw new Error('Request failed (' + response.status + ')'); }
      return response.json();
    }).then(function (data) {
      render(data); report = data; fitMap();
      text('analysis-status', 'Source-linked analysis loaded. Population unchanged; unresolved evidence is shown explicitly.');
      el('analysis-download').disabled = false;
    }).catch(function (error) {
      el('analysis-results').hidden = true; report = null;
      text('analysis-status', 'Could not load Daggerford analysis: ' + error.message);
    }).finally(function () { el('analysis-reload').disabled = false; });
  }
  el('analysis-reload').addEventListener('click', load);
  el('analysis-download').addEventListener('click', function () {
    var url = URL.createObjectURL(new Blob([JSON.stringify(report, null, 2)], {type:'application/json'}));
    var link = document.createElement('a'); link.href = url; link.download = 'daggerford-analysis.json'; link.click();
    setTimeout(function () { URL.revokeObjectURL(url); }, 1000);
  });
  [['show-roofs','roof-layer'],['show-streets','street-layer'],['show-boundaries','boundary-layer']].forEach(function (pair) {
    el(pair[0]).addEventListener('change', function () {
      el(pair[1]).style.display = this.checked ? '' : 'none';
    });
  });
  el('street-form').addEventListener('submit', function (event) {
    event.preventDefault();
    if (!report) { text('analysis-status', 'Load the analysis before locating a street.'); return; }
    var street = report.streets.find(function (item) { return item.id === el('street-select').value; });
    if (!street) { text('map-status', 'No matching street in the current survey.'); return; }
    var node = streetNodes.get(street.id);
    el('show-streets').checked = true; el('street-layer').style.display = '';
    showSelection(node, street.name, street);
    if (!report.map.local_image_available) { return; }
    el('map-zoom').value = Math.max(2, Number(el('map-zoom').value)); fitMap();
    var box = node.getBBox(), host = el('town-map'), plane = el('map-plane');
    var scale = plane.clientWidth / report.map.width_px;
    host.scrollLeft = plane.offsetLeft + (box.x + box.width / 2) * scale - host.clientWidth / 2;
    host.scrollTop = (box.y + box.height / 2) * scale - host.clientHeight / 2;
  });
  el('map-zoom').addEventListener('input', fitMap);
  el('source-image').addEventListener('error', function () {
    el('town-map').hidden = true;
    text('map-status', 'Source preview could not be displayed; consult the linked cartographer source.');
  });
  window.addEventListener('resize', fitMap);
  load();
}());
"""

DAGGERFORD_ASSETS = {
    "daggerford.html": (DAGGERFORD_HTML, "text/html; charset=utf-8"),
    "daggerford.css": (DAGGERFORD_CSS, "text/css; charset=utf-8"),
    "daggerford.js": (DAGGERFORD_JS, "application/javascript; charset=utf-8"),
}
