"""Interactive Waterdeep city atlas served by :mod:`faerun.web`."""

from __future__ import annotations

from typing import Dict, Tuple

from .cityassets import WATERDEEP_DIRECTORY_JS
from .buildingassets import BUILDING_GENERATOR_JS
from .surveyassets import SURVEY_CSS, SURVEY_JS

WATERDEEP_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<script>
  (() => {
    const param = new URLSearchParams(window.location.search).get("scoutTheme");
    const theme =
      param || (window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light");
    document.documentElement.setAttribute("data-theme", theme);
  })();
</script>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Waterdeep Interactive Map</title>
<link rel="stylesheet" href="waterdeep.css">
</head>
<body>
<header class="atlasbar">
  <a class="backlink" href="map.html" aria-label="Back to Faerun world map">&#8592;</a>
  <div class="titleblock">
    <span class="eyebrow">Sword Coast atlas</span>
    <h1>Waterdeep</h1>
  </div>
  <form id="search-form" class="search" role="search">
    <label class="sr-only" for="search">Find a ward, landmark, or street</label>
    <input id="search" type="search" list="place-options" placeholder="Find a ward, landmark, or street..." autocomplete="off">
    <datalist id="place-options"></datalist>
    <button type="submit">Find</button>
  </form>
  <nav aria-label="Atlas pages">
    <a href="map.html">World map</a>
    <a href="location.html?settlement=Waterdeep">Market</a>
  </nav>
</header>

<main class="atlas">
  <section class="mapcolumn" aria-label="Interactive city map">
    <div class="filterbar" id="filters" aria-label="Marker filters">
      <button class="filter active" type="button" data-filter="all">All places</button>
      <button class="filter" type="button" data-filter="ward">Wards</button>
      <button class="filter" type="button" data-filter="landmark">Landmarks</button>
      <button class="filter" type="button" data-filter="gate">Gates</button>
      <button class="filter" type="button" data-filter="harbor">Harbor</button>
    </div>

    <div id="viewport" class="viewport" tabindex="0"
         aria-label="3D map of Waterdeep. Drag to pan; shift-drag to orbit; use the mouse wheel or plus and minus keys to zoom.">
      <div id="scene" class="scene">
        <div id="map-plane" class="mapplane">
          <img id="map-image" src="waterdeep-map-hires.jpg" width="768" height="1536"
               alt="Detailed illustrated street map of Waterdeep">
          <svg id="survey-roofs-layer" class="survey-layer" viewBox="0 0 3560 7256"
               preserveAspectRatio="none" aria-label="Roof survey evidence" hidden></svg>
          <svg id="survey-streets-layer" class="survey-layer" viewBox="0 0 3560 7256"
               preserveAspectRatio="none" aria-label="Street survey evidence" hidden></svg>
          <svg id="survey-boundary-layer" class="survey-layer" viewBox="0 0 3560 7256"
               preserveAspectRatio="none" aria-label="City survey boundary"></svg>
          <svg id="measure-layer" viewBox="0 0 768 1536" aria-hidden="true">
            <line id="measure-line" x1="0" y1="0" x2="0" y2="0"></line>
            <circle id="measure-a" cx="0" cy="0" r="7"></circle>
            <circle id="measure-b" cx="0" cy="0" r="7"></circle>
          </svg>
          <div id="markers" aria-label="Map markers"></div>
        </div>
      </div>
      <div class="maptools" aria-label="Map controls">
        <button id="view-3d" class="active" type="button" title="Toggle 3D view" aria-pressed="true">3D</button>
        <button id="zoom-in" type="button" title="Zoom in (+)">+</button>
        <button id="zoom-out" type="button" title="Zoom out (-)">&#8722;</button>
        <button id="fit-map" type="button" title="Fit the whole map (0)">&#9635;</button>
      </div>
      <div id="orbit-tools" class="orbittools" aria-label="3D view controls">
        <button id="rotate-left" type="button" title="Rotate counterclockwise">&#8634;</button>
        <button id="tilt-down" type="button" title="Lower viewing angle">&#8595;</button>
        <button id="tilt-up" type="button" title="Raise viewing angle">&#8593;</button>
        <button id="rotate-right" type="button" title="Rotate clockwise">&#8635;</button>
        <button id="reset-view" type="button" title="Reset 3D view">N</button>
      </div>
      <div class="scalebar" aria-hidden="true"><span></span><b>1 mile</b></div>
      <div id="map-hint" class="hint">Drag to pan &middot; Shift-drag to orbit &middot; Scroll to zoom</div>
    </div>
  </section>

  <aside class="sidebar">
    <section id="welcome" class="welcome">
      <span class="sectionlabel">The City of Splendors</span>
      <h2>Explore Waterdeep</h2>
      <p>Select a marker to discover the wards, gates, streets, and storied places of the greatest city on the Sword Coast.</p>
      <p><a href="#historical-directory">Browse historical businesses &amp; people</a></p>
      <p><a href="#city-survey">Explore mapped streets &amp; roof evidence</a></p>
      <p><a href="#housing-census">Inspect the building-based housing census</a></p>
      <p><a href="#building-generator">Generate noncanonical buildings &amp; occupant counts</a></p>
      <div class="quickfacts">
        <div><b id="resident-population">Loading...</b><span>modeled residents</span></div>
        <div><b>8</b><span>wards &amp; environs</span></div>
        <div><b>Deepwater</b><span>natural harbor</span></div>
      </div>
      <p id="population-status" role="status" aria-live="polite">Loading population basis...</p>
      <div class="guide">
        <h3>Map guide</h3>
        <p><kbd>+</kbd> <kbd>&minus;</kbd> zoom &nbsp; <kbd>Shift</kbd> + drag orbit &nbsp; <kbd>0</kbd> reset</p>
      </div>
    </section>

    <section id="details" class="details" hidden aria-live="polite">
      <button id="close-details" class="close" type="button" aria-label="Close place details">&times;</button>
      <span id="detail-type" class="sectionlabel"></span>
      <h2 id="detail-name"></h2>
      <p id="detail-description"></p>
      <dl id="detail-facts"></dl>
      <div class="detailactions">
        <button id="share-place" type="button">Copy direct link</button>
        <a href="location.html?settlement=Waterdeep">Open Waterdeep market</a>
      </div>
    </section>

    <section id="city-survey" class="directory" aria-labelledby="city-survey-title">
      <span class="sectionlabel">High-resolution map evidence</span>
      <h2 id="city-survey-title">Streets &amp; building survey</h2>
      <p>Whole mapped city, including Field Ward, the cemetery and harbor islands;
        outlying farms excluded. Map candidates, reviewed structures and residents
        are different quantities.</p>
      <div class="directory-actions">
        <button id="survey-load" type="button">Load streets &amp; roofs</button>
      </div>
      <div class="survey-switches">
        <label><input id="survey-show-streets" type="checkbox" checked>Streets</label>
        <label><input id="survey-show-roofs" type="checkbox">Roof records</label>
        <label><input id="survey-show-boundary" type="checkbox" checked>Boundary</label>
      </div>
      <p class="survey-status" id="survey-streets-status" role="status">Street evidence not loaded.</p>
      <p class="survey-status" id="survey-roofs-status" role="status">Roof evidence not loaded.</p>
      <h3 id="survey-estimate">Citywide structure estimate not loaded</h3>
      <p id="survey-estimate-uncertainty" class="survey-status"></p>
      <p id="survey-scale-status" class="survey-status"></p>
      <form id="street-search" role="search">
        <label class="sr-only" for="street-query">Find a mapped street name or segment ID</label>
        <input id="street-query" type="search" placeholder="Street name or segment ID">
        <button type="submit">Find</button>
      </form>
      <p id="street-result-count" class="survey-status" role="status"></p>
      <ul id="street-results" aria-label="Matching mapped streets"></ul>
      <div id="survey-selection" hidden>
        <h3 id="survey-feature-name"></h3>
        <pre id="survey-feature-details"></pre>
      </div>
      <details><summary>Street coverage, sources &amp; limitations</summary>
        <pre id="survey-streets-metadata"></pre>
      </details>
      <details><summary>Building counts, estimates &amp; validation</summary>
        <pre id="survey-roofs-metadata"></pre>
      </details>
      <div class="directory-actions">
        <button id="survey-streets-download" type="button" disabled>Download streets</button>
        <button id="survey-roofs-download" type="button" disabled>Download roof survey</button>
      </div>
      <p>Amber outlines are roof evidence, not household boundaries. Blue lines are
        street records; blue dots locate labels without asserting a traced route.
        Select a record to inspect its review status. Active population is unchanged.</p>
    </section>

    <section id="housing-census" class="directory" aria-labelledby="census-title">
      <span class="sectionlabel">City System housing model</span>
      <h2 id="census-title">Building-based census</h2>
      <p>Measured roofs and assumed occupancy are separate inputs. Unresolved maps,
        scale, or institutions prevent a citywide population claim.</p>
      <p>This section retains the separate historical City System survey.
        <a href="#city-survey">View the high-resolution city map evidence above.</a></p>
      <div class="directory-actions">
        <button id="census-load" type="button">Inspect survey &amp; estimate</button>
        <button id="census-download" type="button" disabled>Download census JSON</button>
      </div>
      <p id="census-status" role="status" aria-live="polite">Not loaded. The active population is unchanged.</p>
      <div id="census-results" hidden>
        <p id="census-summary"></p>
        <p id="census-readiness"></p>
        <ul id="census-blockers"></ul>
        <div class="census-table">
          <table aria-label="Ward-level housing census">
            <thead><tr><th>Ward</th><th>Records</th><th>Estimable</th><th>Covered residents<br>(central)</th></tr></thead>
            <tbody id="census-wards"></tbody>
          </table>
        </div>
        <details><summary>Source rules &amp; occupancy assumptions</summary>
          <p id="census-formula"></p>
          <ul id="census-assumptions"></ul>
          <pre id="census-scenarios"></pre>
        </details>
        <details><summary>Survey coverage &amp; validation</summary><pre id="census-survey"></pre></details>
      </div>
    </section>

    <section id="building-generator" class="directory" aria-labelledby="building-generator-title">
      <span class="sectionlabel">Generated, not surveyed</span>
      <h2 id="building-generator-title">Building scenarios</h2>
      <p id="building-generator-source">City System rules with explicit occupancy assumptions. Not a census or a claim about existing buildings.</p>
      <p>No invented names. Named people remain in the <a href="#historical-directory">source-linked historical directory</a>, attached only to their documented establishments.</p>
      <form id="building-generator-form">
        <label for="building-ward">Ward</label>
        <select id="building-ward">
          <option>Castle Ward</option><option>Sea Ward</option><option>North Ward</option>
          <option selected>Trades Ward</option><option>Southern Ward</option><option>Dock Ward</option>
        </select>
        <label for="building-building_class">Class</label>
        <select id="building-building_class"><option value="">Source dice table</option><option value="B">B - Grand buildings</option><option value="C">C - Row buildings</option><option value="D">D - Lesser buildings</option></select>
        <label for="building-count">Buildings (1-100)</label>
        <input id="building-count" type="number" min="1" max="100" step="1" value="20" required>
        <label for="building-seed">Repeatable seed</label>
        <input id="building-seed" type="number" min="0" max="4294967295" step="1" value="1357" required>
        <label for="building-footprint_sqft">Assumed footprint per building (sq ft)</label>
        <input id="building-footprint_sqft" type="number" min="1" max="1000000" step="any" value="1000" required>
        <label for="building-scenario">Occupancy assumptions</label>
        <select id="building-scenario"><option value="low">Low</option><option value="central" selected>Central</option><option value="high">High</option></select>
        <div class="directory-actions">
          <button type="submit">Generate buildings</button>
          <button id="building-generator-download" type="button" disabled>Download scenario JSON</button>
        </div>
      </form>
      <p>Class A landmarks need individual authoring. Southern Ward rolls 3-4 remain unresolved unless you choose a class.</p>
      <p id="building-generator-status" role="status" aria-live="polite">Not generated. Active population and surveyed roofs are unchanged.</p>
      <details><summary>Generation &amp; occupancy assumptions</summary><ul id="building-generator-assumptions"></ul></details>
      <div id="building-generator-results"></div>
    </section>

    <section id="historical-directory" class="directory" aria-labelledby="directory-title">
      <span class="sectionlabel">Source-linked historical model</span>
      <h2 id="directory-title">Businesses &amp; people</h2>
      <p id="directory-source">Volo's historical account, separate from the live 1492 DR economy.</p>
      <details class="directory-scope"><summary>Coverage &amp; modeling limits</summary><p id="directory-scope"></p></details>
      <form id="directory-form" role="search" aria-label="Historical city directory">
        <label for="directory-search">Name, trade, or associated person</label>
        <input id="directory-search" type="search" placeholder="Inn, books, proprietor..." autocomplete="off">
        <label for="directory-ward">Ward (affiliation for people)</label>
        <select id="directory-ward"><option value="">All wards</option></select>
        <label for="directory-kind">Record type</label>
        <select id="directory-kind"><option value="all">Businesses and people</option><option value="business">Businesses</option><option value="person">People</option></select>
        <label for="directory-category">Business category</label>
        <select id="directory-category"><option value="">All categories</option></select>
        <div class="directory-actions">
          <button type="submit">Find</button>
          <button id="directory-clear" type="button">Clear filters</button>
          <button id="directory-download" type="button" disabled>Download results JSON</button>
        </div>
      </form>
      <p id="directory-status" role="status" aria-live="polite"></p>
      <div id="directory-results"></div>
    </section>

    <section class="measurecard">
      <div>
        <span class="sectionlabel">Cartographer's tools</span>
        <h2>Measure distance</h2>
      </div>
      <button id="measure-toggle" type="button" aria-pressed="false">Start</button>
      <p id="measure-help">Choose two points to estimate distance and walking time.</p>
      <p>Distances use the atlas's assumed display scale, not a verified physical survey calibration.</p>
      <output id="measure-result"></output>
    </section>
  </aside>
</main>

<div id="toast" class="toast" role="status" aria-live="polite"></div>
<script src="waterdeep.js"></script>
<script src="waterdeep-directory.js"></script>
<script src="building-generator.js"></script>
<script src="waterdeep-survey.js"></script>
</body>
</html>
"""


WATERDEEP_CSS = """
:root {
  color-scheme: light;
  --cp-bg: #f7f4ef;
  --cp-bg-elevated: #fcfbf8;
  --cp-surface: #ffffff;
  --cp-surface-soft: #f5f5f5;
  --cp-border: #dedede;
  --cp-border-strong: #919191;
  --cp-text: #242424;
  --cp-text-muted: #5c5c5c;
  --cp-text-soft: #6f6f6f;
  --cp-accent: #b11f4b;
  --cp-accent-hover: #9a1a41;
  --cp-accent-soft: rgba(177, 31, 75, 0.08);
  --cp-accent-fg: #ffffff;
  --cp-success: #16a34a;
  --cp-danger: #dc2626;
  --cp-warning: #f59e0b;
  --cp-link: #0078d4;
  --cp-shadow: 0 18px 48px rgba(0, 0, 0, 0.12);
  --cp-overlay: rgba(255, 255, 255, 0.8);
  --cp-panel: rgba(255, 255, 255, 0.86);
  --cp-panel-strong: rgba(255, 255, 255, 0.96);
  --cp-sheen: rgba(255, 255, 255, 0.55);
  --cp-highlight: rgba(177, 31, 75, 0.12);
}
html[data-theme="dark"] {
  color-scheme: dark;
  --cp-bg: #3d3b3a;
  --cp-bg-elevated: #343231;
  --cp-surface: #292929;
  --cp-surface-soft: #2e2e2e;
  --cp-border: #474747;
  --cp-border-strong: #5f5f5f;
  --cp-text: #dedede;
  --cp-text-muted: #919191;
  --cp-text-soft: #b0b0b0;
  --cp-accent: #fd8ea1;
  --cp-accent-hover: #fb7b91;
  --cp-accent-soft: rgba(253, 142, 161, 0.14);
  --cp-accent-fg: #1a1a1a;
  --cp-success: #4ade80;
  --cp-danger: #f87171;
  --cp-warning: #fbbf24;
  --cp-link: #4da6ff;
  --cp-shadow: 0 18px 48px rgba(0, 0, 0, 0.32);
  --cp-overlay: rgba(41, 41, 41, 0.88);
  --cp-panel: rgba(41, 41, 41, 0.72);
  --cp-panel-strong: rgba(41, 41, 41, 0.96);
  --cp-sheen: rgba(255, 255, 255, 0.04);
  --cp-highlight: rgba(253, 142, 161, 0.12);
}

* { box-sizing: border-box; }
html, body { width: 100%; height: 100%; margin: 0; overflow: hidden; }
body {
  background: var(--cp-bg);
  color: var(--cp-text);
  font: 15px/1.5 "Segoe UI", Aptos, Calibri, -apple-system, BlinkMacSystemFont, sans-serif;
}
button, input { font: inherit; }
button, a { -webkit-tap-highlight-color: transparent; }
a { color: var(--cp-link); text-decoration: none; }
a:hover { text-decoration: underline; }
.sr-only {
  position: absolute; width: 1px; height: 1px; padding: 0; margin: -1px;
  overflow: hidden; clip: rect(0, 0, 0, 0); white-space: nowrap; border: 0;
}
.atlasbar {
  height: 72px; display: flex; align-items: center; gap: 20px; padding: 8px 20px;
  background: var(--cp-bg-elevated); border-bottom: 1px solid var(--cp-border);
  position: relative; z-index: 20;
}
.backlink {
  width: 40px; height: 40px; display: grid; place-items: center; border: 1px solid var(--cp-border);
  border-radius: 0.625rem; color: var(--cp-text); font-size: 22px; background: var(--cp-surface);
}
.titleblock { min-width: 200px; }
.titleblock h1 { margin: -3px 0 0; font-size: 27px; line-height: 1.1; letter-spacing: .03em; }
.eyebrow, .sectionlabel {
  color: var(--cp-accent); font-size: 11px; font-weight: 700; letter-spacing: .14em; text-transform: uppercase;
}
.search { flex: 1; display: flex; max-width: 620px; }
.search input {
  width: 100%; height: 40px; border: 1px solid var(--cp-border); border-right: 0;
  border-radius: 0.625rem 0 0 0.625rem; padding: 0 14px;
  background: var(--cp-surface); color: var(--cp-text); outline: none;
}
.search input:focus { border-color: var(--cp-accent); box-shadow: inset 0 0 0 1px var(--cp-accent); }
.search button, .filter, .detailactions button, .measurecard button {
  border: 1px solid var(--cp-accent); background: var(--cp-accent); color: var(--cp-accent-fg);
  font-weight: 600; cursor: pointer;
}
.search button { border-radius: 0 0.625rem 0.625rem 0; padding: 0 18px; }
.search button:hover, .detailactions button:hover, .measurecard button:hover { background: var(--cp-accent-hover); }
.atlasbar nav { margin-left: auto; display: flex; gap: 16px; white-space: nowrap; }
.atlas { height: calc(100% - 72px); display: grid; grid-template-columns: minmax(0, 1fr) 360px; }
.mapcolumn { min-width: 0; display: flex; flex-direction: column; }
.filterbar {
  min-height: 52px; display: flex; gap: 8px; align-items: center; padding: 8px 16px;
  background: var(--cp-bg-elevated); border-bottom: 1px solid var(--cp-border); overflow-x: auto;
}
.filter {
  padding: 7px 12px; border-radius: 999px; color: var(--cp-text); background: var(--cp-surface);
  border-color: var(--cp-border); white-space: nowrap;
}
.filter:hover { border-color: var(--cp-border-strong); }
.filter.active { background: var(--cp-accent); border-color: var(--cp-accent); color: var(--cp-accent-fg); }
.viewport {
  position: relative; flex: 1; min-height: 0; overflow: hidden; cursor: grab;
  background: var(--cp-surface-soft); touch-action: none; outline: none; perspective: 1500px;
  perspective-origin: 50% 42%;
}
.viewport:focus-visible { box-shadow: inset 0 0 0 2px var(--cp-accent); }
.viewport.dragging { cursor: grabbing; }
.viewport.measuring { cursor: crosshair; }
.scene {
  position: absolute; width: 768px; height: 1536px; transform-origin: 0 0;
  transform-style: preserve-3d; will-change: transform;
}
.mapplane {
  position: absolute; inset: 0; width: 768px; height: 1536px; overflow: hidden;
  transform-origin: 50% 50%; transform-style: preserve-3d; will-change: transform;
  transition: transform .35s ease;
}
.mapplane::after {
  content: ""; position: absolute; inset: 0; z-index: -1; transform: translateZ(-18px);
  background: var(--cp-border-strong); border: 2px solid var(--cp-border-strong);
  box-shadow: var(--cp-shadow);
}
.mapplane > img {
  position: absolute; inset: 0; width: 768px; height: 1536px; display: block;
  user-select: none; pointer-events: none; box-shadow: var(--cp-shadow); transform: translateZ(0);
}
#measure-layer { position: absolute; inset: 0; width: 768px; height: 1536px; pointer-events: none; overflow: visible; }
#measure-layer line { stroke: var(--cp-accent); stroke-width: 4; stroke-dasharray: 12 8; }
#measure-layer circle { fill: var(--cp-surface); stroke: var(--cp-accent); stroke-width: 4; }
#measure-layer:not(.visible) { display: none; }
.marker {
  position: absolute; width: 28px; height: 28px; margin: -14px 0 0 -14px;
  border: 3px solid var(--cp-surface); border-radius: 50%; background: var(--cp-accent);
  color: var(--cp-accent-fg); box-shadow: 0 0 0 2px var(--cp-accent);
  cursor: pointer; display: grid; place-items: center; font-size: 13px; font-weight: 800;
  transform: translateZ(22px); transform-style: preserve-3d;
}
.marker[data-kind="ward"] { background: var(--cp-accent); box-shadow: 0 0 0 2px var(--cp-accent); }
.marker[data-kind="landmark"] { background: var(--cp-link); box-shadow: 0 0 0 2px var(--cp-link); }
.marker[data-kind="gate"] { background: var(--cp-warning); box-shadow: 0 0 0 2px var(--cp-warning); }
.marker[data-kind="harbor"] { background: var(--cp-success); box-shadow: 0 0 0 2px var(--cp-success); }
.marker.selected { width: 34px; height: 34px; margin: -17px 0 0 -17px; z-index: 5; }
.marker.hidden { display: none; }
.marker-label {
  position: absolute; left: 50%; bottom: calc(100% + 10px); transform: translateX(-50%);
  padding: 4px 8px; border-radius: 0.625rem; white-space: nowrap; pointer-events: none;
  background: var(--cp-panel-strong); color: var(--cp-text); border: 1px solid var(--cp-border);
  font-size: 12px; font-weight: 700; opacity: 0;
}
.marker:hover .marker-label, .marker:focus-visible .marker-label, .marker.selected .marker-label { opacity: 1; }
.maptools {
  position: absolute; top: 16px; right: 16px; display: grid; overflow: hidden;
  border: 1px solid var(--cp-border); border-radius: 0.625rem; background: var(--cp-panel-strong);
  box-shadow: var(--cp-shadow);
}
.maptools button {
  width: 40px; height: 40px; border: 0; border-bottom: 1px solid var(--cp-border);
  background: var(--cp-surface); color: var(--cp-text); font-size: 22px; font-weight: 500; cursor: pointer;
}
.maptools button:last-child { border-bottom: 0; font-size: 17px; }
.maptools button:hover { background: var(--cp-accent-soft); color: var(--cp-accent); }
.maptools button.active { background: var(--cp-accent); color: var(--cp-accent-fg); }
.orbittools {
  position: absolute; top: 16px; left: 50%; transform: translateX(-50%); display: flex;
  border: 1px solid var(--cp-border); border-radius: 0.625rem; overflow: hidden;
  background: var(--cp-panel-strong); box-shadow: var(--cp-shadow);
}
.orbittools button {
  width: 40px; height: 36px; border: 0; border-right: 1px solid var(--cp-border);
  background: var(--cp-surface); color: var(--cp-text); cursor: pointer; font-size: 17px;
}
.orbittools button:last-child { border-right: 0; font-size: 12px; font-weight: 800; }
.orbittools button:hover { background: var(--cp-accent-soft); color: var(--cp-accent); }
.viewport:not(.is-3d) .orbittools { display: none; }
.viewport.is-3d.orbiting { cursor: move; }
.hint, .scalebar {
  position: absolute; bottom: 16px; background: var(--cp-panel-strong); border: 1px solid var(--cp-border);
  border-radius: 0.625rem; color: var(--cp-text-muted); font-size: 12px; box-shadow: var(--cp-shadow);
}
.hint { left: 16px; padding: 7px 10px; }
.scalebar { right: 16px; padding: 7px 10px; min-width: 100px; }
.scalebar span { display: block; height: 4px; border: solid var(--cp-text); border-width: 0 2px 2px; }
.scalebar b { display: block; margin-top: 2px; text-align: center; font-size: 11px; }
.sidebar {
  overflow-y: auto; background: var(--cp-bg-elevated); border-left: 1px solid var(--cp-border);
  padding: 28px 24px;
}
.sidebar h2 { margin: 4px 0 12px; font-size: 24px; line-height: 1.2; }
.sidebar h3 { margin: 0 0 6px; font-size: 14px; }
.sidebar p { color: var(--cp-text-muted); }
.census-table { overflow-x: auto; }
.census-table table { width: 100%; border-collapse: collapse; font-size: 12px; }
.census-table th, .census-table td { padding: 8px 4px; text-align: left; border-bottom: 1px solid var(--cp-border); }
#housing-census pre { white-space: pre-wrap; overflow-wrap: anywhere; font-size: 12px; }
.quickfacts { display: grid; grid-template-columns: repeat(3, 1fr); margin: 24px 0; border-block: 1px solid var(--cp-border); }
.quickfacts div { padding: 14px 4px; text-align: center; border-right: 1px solid var(--cp-border); }
.quickfacts div:last-child { border-right: 0; }
.quickfacts b, .quickfacts span { display: block; }
.quickfacts b { font-size: 14px; color: var(--cp-text); }
.quickfacts span { font-size: 10px; color: var(--cp-text-muted); }
.guide, .measurecard {
  padding: 16px; border: 1px solid var(--cp-border); border-radius: 16px; background: var(--cp-surface);
  box-shadow: 0 0 2px var(--cp-border), 0 1px 2px var(--cp-border);
}
kbd {
  padding: 2px 5px; border: 1px solid var(--cp-border-strong); border-radius: 4px;
  background: var(--cp-surface-soft); font: 11px Consolas, "Courier New", Courier, monospace;
}
.details { position: relative; }
.close {
  position: absolute; right: 0; top: -6px; width: 36px; height: 36px; border: 0;
  background: transparent; color: var(--cp-text-muted); font-size: 26px; cursor: pointer;
}
.details dl { display: grid; grid-template-columns: 90px 1fr; gap: 10px 12px; padding: 16px 0; border-block: 1px solid var(--cp-border); }
.details dt { color: var(--cp-text-muted); }
.details dd { margin: 0; font-weight: 600; }
.detailactions { display: flex; flex-direction: column; gap: 10px; margin-top: 18px; }
.detailactions button, .detailactions a { min-height: 40px; border-radius: 0.625rem; display: grid; place-items: center; }
.detailactions a { border: 1px solid var(--cp-border); background: var(--cp-surface); }
.measurecard { margin-top: 24px; }
.measurecard > div { display: inline-block; }
.measurecard h2 { font-size: 18px; margin-bottom: 4px; }
.measurecard button { float: right; border-radius: 0.625rem; padding: 7px 14px; }
.measurecard button[aria-pressed="true"] { background: var(--cp-danger); border-color: var(--cp-danger); }
.measurecard p { clear: both; margin-bottom: 4px; font-size: 13px; }
#measure-result { display: block; color: var(--cp-accent); font-weight: 700; min-height: 24px; }
.toast {
  position: fixed; left: 50%; bottom: 24px; z-index: 30; transform: translate(-50%, 20px);
  padding: 10px 16px; border-radius: 0.625rem; background: var(--cp-text); color: var(--cp-bg);
  opacity: 0; pointer-events: none; transition: opacity .2s, transform .2s;
}
.toast.visible { opacity: 1; transform: translate(-50%, 0); }
.directory { margin-top: 28px; padding-top: 24px; border-top: 1px solid var(--cp-border); }
.directory form { display: grid; gap: 6px; margin-top: 16px; }
.directory label { font-size: 12px; font-weight: 600; margin-top: 6px; }
.directory input, .directory select {
  width: 100%; min-width: 0; padding: 8px; border: 1px solid var(--cp-border);
  border-radius: 6px; background: var(--cp-surface); color: var(--cp-text); font: inherit;
}
.directory-actions { display: flex; gap: 8px; flex-wrap: wrap; margin-top: 10px; }
.directory-actions button { padding: 7px 10px; border-radius: 6px; }
.directory button:disabled { opacity: .5; cursor: not-allowed; }
.directory-entry { border-top: 1px solid var(--cp-border); padding: 12px 0; overflow-wrap: anywhere; }
.directory-entry summary { cursor: pointer; font-weight: 700; }
.directory-entry h4 { margin: 14px 0 4px; }
.directory .directory-meta, .directory .directory-citation { font-size: 12px; color: var(--cp-text-muted); }
.directory-citation { display: block; margin-top: 4px; }
.directory .directory-link { background: none; border: 0; color: var(--cp-link); padding: 0; text-align: left; text-decoration: underline; font: inherit; cursor: pointer; }
.directory .directory-error { color: var(--cp-danger); }
.directory-scope { font-size: 12px; }
.directory-scope summary { cursor: pointer; }
.directory pre { white-space: pre-wrap; overflow-wrap: anywhere; font-size: 12px; }

@media (max-width: 900px) {
  .atlasbar nav { display: none; }
  .titleblock { min-width: 150px; }
  .atlas { grid-template-columns: minmax(0, 1fr) 300px; }
}
@media (max-width: 700px) {
  html, body { overflow: auto; }
  .atlasbar { height: auto; min-height: 68px; flex-wrap: wrap; gap: 10px; padding: 8px 12px; }
  .titleblock { min-width: 0; }
  .titleblock .eyebrow { display: none; }
  .titleblock h1 { font-size: 22px; }
  .search { order: 3; max-width: none; flex-basis: 100%; }
  .atlas { height: auto; min-height: calc(100vh - 116px); display: flex; flex-direction: column; }
  .mapcolumn { height: 68vh; min-height: 430px; }
  .sidebar { border-left: 0; border-top: 1px solid var(--cp-border); overflow: visible; padding: 22px 18px; }
  .hint { display: none; }
}
"""


WATERDEEP_JS = r"""
(function () {
  'use strict';

  var MAP_WIDTH = 768;
  var MAP_HEIGHT = 1536;
  var MILES_PER_PIXEL = 0.007;
  function loadPopulation() {
    var count = document.getElementById('resident-population');
    var status = document.getElementById('population-status');
    return fetch('/api/population?settlement=Waterdeep').then(function (response) {
      if (!response.ok) { throw new Error('Population request failed (' + response.status + ')'); }
      return response.json();
    }).then(function (report) {
      if (!Number.isInteger(report.resident_population) || report.resident_population < 0) {
        throw new Error('Invalid resident population in response');
      }
      count.textContent = report.resident_population.toLocaleString();
      status.textContent = report.date + ': ' + report.scope + '. ' +
        (report.rationale || 'Gazetteer estimate; not a census.') +
        (report.comparison_residents !== undefined
          ? ' Comparison baseline: ' + report.comparison_residents.toLocaleString() + ' residents.'
          : '');
    }).catch(function (error) {
      count.textContent = 'Unavailable';
      status.textContent = error.message;
    });
  }
  var places = [
    {id:'sea-ward', name:'Sea Ward', kind:'ward', x:225, y:430, icon:'S', subtitle:'Ward of villas and temples',
      description:'Waterdeep\'s most affluent ward rises above the western cliffs. Noble villas, fashionable temples, and the Field of Triumph line its broad streets.',
      facts:{Character:'Noble and ceremonial', Notable:'Field of Triumph', Access:'North of Castle Ward'}},
    {id:'north-ward', name:'North Ward', kind:'ward', x:475, y:450, icon:'N', subtitle:'Quiet streets and noble estates',
      description:'A prosperous residential ward of townhouses, walled gardens, and old families, stretching toward the city\'s northern gates.',
      facts:{Character:'Residential', Notable:'Cliffwatch', Access:'North Gate and Troll Gate'}},
    {id:'castle-ward', name:'Castle Ward', kind:'ward', x:390, y:730, icon:'C', subtitle:'Civic heart of Waterdeep',
      description:'The city\'s administrative and ceremonial center, dominated by Castle Waterdeep, Piergeiron\'s Palace, and the great open market.',
      facts:{Character:'Civic and mercantile', Notable:'Castle Waterdeep', Access:'Central avenues'}},
    {id:'trades-ward', name:'Trades Ward', kind:'ward', x:545, y:930, icon:'T', subtitle:'Guildhalls, shops, and workshops',
      description:'The busiest commercial streets in Waterdeep are packed with guildhalls, workshops, inns, and merchants from across Faerun.',
      facts:{Character:'Commercial', Notable:'The High Road', Access:'Between Castle and North Wards'}},
    {id:'city-of-the-dead', name:'City of the Dead', kind:'ward', x:570, y:745, icon:'D', subtitle:'Garden cemetery and sacred ward',
      description:'By day this walled cemetery is a quiet public garden. Its tombs and mausoleums are guarded after dusk, when the gates are closed.',
      facts:{Character:'Sacred garden', Notable:'Warrior\'s Monument', Access:'East of Trades Ward'}},
    {id:'dock-ward', name:'Dock Ward', kind:'ward', x:455, y:1110, icon:'K', subtitle:'Wharves, taverns, and hard bargains',
      description:'A dense waterfront maze where sailors, caravan factors, laborers, and adventurers mingle beneath the cranes of the harbor.',
      facts:{Character:'Maritime and rough', Notable:'The Old Xoblob Shop', Access:'Great Harbor waterfront'}},
    {id:'south-ward', name:'South Ward', kind:'ward', x:600, y:1200, icon:'O', subtitle:'Caravans and working neighborhoods',
      description:'Caravan yards, stables, warehouses, and crowded homes fill the southern ward around the Trade Way approaches.',
      facts:{Character:'Working and caravan', Notable:'Caravan Court', Access:'South Gate'}},
    {id:'deepwater-harbor', name:'Deepwater Harbor', kind:'harbor', x:375, y:1320, icon:'H', subtitle:'The harbor that made the city',
      description:'The sheltered deep-water anchorage welcomes vessels from the Sword Coast and far beyond, protected by the harbor islands and city defenses.',
      facts:{Character:'Major seaport', Notable:'Deepwater Isle', Access:'Great Harbor'}},
    {id:'mount-waterdeep', name:'Mount Waterdeep', kind:'landmark', x:205, y:835, icon:'M', subtitle:'The city\'s western sentinel',
      description:'The mountain shoulders the city against the sea, crowned by the fortress of the Griffon Cavalry and threaded with old paths and hidden chambers.',
      facts:{Type:'Natural landmark', Notable:'Griffon Cavalry', Ward:'Sea and Castle Wards'}},
    {id:'castle-waterdeep', name:'Castle Waterdeep', kind:'landmark', x:350, y:755, icon:'1', subtitle:'Fortress above the harbor',
      description:'Waterdeep\'s ancient fortress watches the harbor and houses barracks, armories, courts, and defenses for the City Guard.',
      facts:{Type:'Fortress', Ward:'Castle Ward', Access:'Castle Ward heights'}},
    {id:'palace', name:'Piergeiron\'s Palace', kind:'landmark', x:320, y:780, icon:'2', subtitle:'Seat of the Open Lord',
      description:'The grand palace is the public center of Waterdeep\'s government and the traditional seat of the Open Lord.',
      facts:{Type:'Civic palace', Ward:'Castle Ward', Access:'Palace square'}},
    {id:'market', name:'The Market', kind:'landmark', x:365, y:585, icon:'3', subtitle:'Waterdeep\'s great open market',
      description:'A sprawling open marketplace where stalls offer food, craftwork, curiosities, and imports from every road and sea lane.',
      facts:{Type:'Marketplace', Ward:'Castle Ward', Hours:'Dawn to dusk'}},
    {id:'yawning-portal', name:'The Yawning Portal', kind:'landmark', x:395, y:650, icon:'4', subtitle:'Inn above the entrance to Undermountain',
      description:'This famous inn surrounds a deep well descending into Undermountain. Adventurers gather here to trade stories and risk the descent.',
      facts:{Type:'Inn and dungeon access', Ward:'Castle Ward', Proprietor:'Durnan'}},
    {id:'field-of-triumph', name:'Field of Triumph', kind:'landmark', x:370, y:160, icon:'5', subtitle:'Arena of games and spectacle',
      description:'Waterdeep\'s great arena hosts tournaments, races, public games, and civic celebrations before enormous crowds.',
      facts:{Type:'Arena', Ward:'Sea Ward', Access:'Northwest avenues'}},
    {id:'north-gate', name:'North Gate', kind:'gate', x:490, y:120, icon:'G', subtitle:'Northern road to the Sword Coast',
      description:'One of the principal northern entrances, carrying travelers and traffic toward Amphail and the Long Road.',
      facts:{Type:'City gate', Ward:'North Ward', Road:'Long Road'}},
    {id:'troll-gate', name:'Troll Gate', kind:'gate', x:185, y:48, icon:'G', subtitle:'Northeastern gate',
      description:'A guarded northeastern entrance named for the foes once driven from the city, opening toward the farms beyond the walls.',
      facts:{Type:'City gate', Ward:'North Ward', Road:'High Road approaches'}},
    {id:'south-gate', name:'South Gate', kind:'gate', x:660, y:1330, icon:'G', subtitle:'Caravan entrance from the Trade Way',
      description:'The great southern gate admits caravans from Daggerford and the Trade Way into the yards and warehouses of South Ward.',
      facts:{Type:'City gate', Ward:'South Ward', Road:'Trade Way'}},
    {id:'mistshore', name:'Mistshore', kind:'harbor', x:350, y:1135, icon:'A', subtitle:'Rafts and wrecks along the waterfront',
      description:'A ramshackle floating neighborhood of lashed-together vessels, pontoons, and salvage on the edge of Dock Ward.',
      facts:{Type:'Waterfront quarter', Ward:'Dock Ward', Access:'Great Harbor'}},
    {id:'deepwater-isle', name:'Deepwater Isle', kind:'harbor', x:330, y:1460, icon:'I', subtitle:'Harbor island and naval defense',
      description:'The largest island sheltering the harbor supports naval facilities and helps guard the approaches to the City of Splendors.',
      facts:{Type:'Harbor island', Notable:'Naval harbor', Access:'By boat'}},
    {id:'sea-maidens-faire', name:'Sea Maidens Faire', kind:'harbor', x:275, y:1190, icon:'F', subtitle:'Ships, spectacle, and seasonal revels',
      description:'The colorful fleet and traveling faire brings exotic ships, performers, and crowds to Waterdeep\'s harbor.',
      facts:{Type:'Fleet and festival', Ward:'Harbor', Access:'By quay or boat'}}
  ];

  var viewport = document.getElementById('viewport');
  var scene = document.getElementById('scene');
  var mapPlane = document.getElementById('map-plane');
  var markerHost = document.getElementById('markers');
  var image = document.getElementById('map-image');
  var state = {scale:1, x:0, y:0, minScale:.15, maxScale:4, dragging:false, pointer:null,
               startX:0, startY:0, originX:0, originY:0, filter:'all', selected:null,
               measuring:false, measurePoints:[], is3d:true, tilt:42, rotation:-5,
               orbiting:false, originTilt:42, originRotation:-5};

  function clamp(value, low, high) { return Math.max(low, Math.min(high, value)); }

  function applyTransform() {
    scene.style.transform = 'translate(' + state.x + 'px,' + state.y + 'px) scale(' + state.scale + ')';
    mapPlane.style.transform = state.is3d
      ? 'rotateX(' + state.tilt + 'deg) rotateZ(' + state.rotation + 'deg)'
      : 'rotateX(0deg) rotateZ(0deg)';
    document.querySelector('.scalebar span').style.width = Math.round(1 / MILES_PER_PIXEL * state.scale) + 'px';
  }

  function set3d(enabled) {
    state.is3d = enabled;
    viewport.classList.toggle('is-3d', enabled);
    var button = document.getElementById('view-3d');
    button.classList.toggle('active', enabled);
    button.setAttribute('aria-pressed', String(enabled));
    document.getElementById('map-hint').textContent = enabled
      ? 'Drag to pan · Shift-drag to orbit · Scroll to zoom'
      : 'Drag to pan · Scroll to zoom · Click a marker';
    applyTransform();
  }

  function orbit(rotationDelta, tiltDelta) {
    state.rotation = (state.rotation + rotationDelta) % 360;
    state.tilt = clamp(state.tilt + tiltDelta, 18, 68);
    applyTransform();
  }

  function resetView() {
    state.rotation = -5;
    state.tilt = 42;
    fitMap();
  }

  function fitMap() {
    var rect = viewport.getBoundingClientRect();
    var scale = Math.min((rect.width - 40) / MAP_WIDTH, (rect.height - 40) / MAP_HEIGHT);
    if (state.is3d) { scale *= .58; }
    state.scale = clamp(scale, state.minScale, 1.2);
    state.x = (rect.width - MAP_WIDTH * state.scale) / 2;
    state.y = (rect.height - MAP_HEIGHT * state.scale) / 2;
    applyTransform();
  }

  function zoomAt(factor, clientX, clientY) {
    var rect = viewport.getBoundingClientRect();
    var px = clientX == null ? rect.width / 2 : clientX - rect.left;
    var py = clientY == null ? rect.height / 2 : clientY - rect.top;
    var oldScale = state.scale;
    state.scale = clamp(oldScale * factor, state.minScale, state.maxScale);
    var ratio = state.scale / oldScale;
    state.x = px - (px - state.x) * ratio;
    state.y = py - (py - state.y) * ratio;
    applyTransform();
  }

  function focusPlace(place) {
    var rect = viewport.getBoundingClientRect();
    state.scale = Math.max(state.scale, Math.min(2.15, rect.width < 700 ? 1.45 : 1.8));
    var dx = place.x - MAP_WIDTH / 2;
    var dy = place.y - MAP_HEIGHT / 2;
    var radians = state.is3d ? state.rotation * Math.PI / 180 : 0;
    var projectedX = dx * Math.cos(radians) - dy * Math.sin(radians);
    var projectedY = dx * Math.sin(radians) + dy * Math.cos(radians);
    if (state.is3d) { projectedY *= Math.cos(state.tilt * Math.PI / 180); }
    state.x = rect.width / 2 - (MAP_WIDTH / 2 + projectedX) * state.scale;
    state.y = rect.height / 2 - (MAP_HEIGHT / 2 + projectedY) * state.scale;
    applyTransform();
  }

  window.addEventListener('waterdeep-focus-point', function (event) {
    var point = event.detail;
    if (!point || !Number.isFinite(point.x) || !Number.isFinite(point.y) ||
        point.x < 0 || point.x > MAP_WIDTH || point.y < 0 || point.y > MAP_HEIGHT) {
      showToast('Cannot focus invalid survey coordinates');
      return;
    }
    focusPlace(point);
  });

  function titleKind(kind) {
    return {ward:'City ward', landmark:'Landmark', gate:'City gate', harbor:'Harbor & island'}[kind] || kind;
  }

  function escapeHtml(value) {
    return String(value).replace(/[&<>"']/g, function (c) {
      return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c];
    });
  }

  function selectPlace(place, focus, updateHash) {
    state.selected = place;
    document.querySelectorAll('.marker').forEach(function (el) {
      el.classList.toggle('selected', el.dataset.id === place.id);
    });
    document.getElementById('welcome').hidden = true;
    document.getElementById('details').hidden = false;
    document.getElementById('detail-type').textContent = titleKind(place.kind) + ' · ' + place.subtitle;
    document.getElementById('detail-name').textContent = place.name;
    document.getElementById('detail-description').textContent = place.description;
    document.getElementById('detail-facts').innerHTML = Object.keys(place.facts).map(function (key) {
      return '<dt>' + escapeHtml(key) + '</dt><dd>' + escapeHtml(place.facts[key]) + '</dd>';
    }).join('');
    if (updateHash !== false) { history.replaceState(null, '', '#' + place.id); }
    if (focus !== false) { focusPlace(place); }
  }

  function closeDetails() {
    state.selected = null;
    document.querySelectorAll('.marker').forEach(function (el) { el.classList.remove('selected'); });
    document.getElementById('details').hidden = true;
    document.getElementById('welcome').hidden = false;
    history.replaceState(null, '', location.pathname + location.search);
  }

  function pointFromEvent(ev) {
    var rect = viewport.getBoundingClientRect();
    var localX = (ev.clientX - rect.left - state.x) / state.scale;
    var localY = (ev.clientY - rect.top - state.y) / state.scale;
    if (!state.is3d) {
      return {x:clamp(localX, 0, MAP_WIDTH), y:clamp(localY, 0, MAP_HEIGHT)};
    }
    var dx = localX - MAP_WIDTH / 2;
    var dy = (localY - MAP_HEIGHT / 2) / Math.cos(state.tilt * Math.PI / 180);
    var radians = -state.rotation * Math.PI / 180;
    return {
      x: clamp(MAP_WIDTH / 2 + dx * Math.cos(radians) - dy * Math.sin(radians), 0, MAP_WIDTH),
      y: clamp(MAP_HEIGHT / 2 + dx * Math.sin(radians) + dy * Math.cos(radians), 0, MAP_HEIGHT)
    };
  }

  function addMeasurePoint(point) {
    if (state.measurePoints.length >= 2) { state.measurePoints = []; }
    state.measurePoints.push(point);
    renderMeasure();
  }

  function renderMeasure() {
    var layer = document.getElementById('measure-layer');
    var a = state.measurePoints[0];
    var b = state.measurePoints[1];
    layer.classList.toggle('visible', Boolean(a));
    if (!a) {
      document.getElementById('measure-result').textContent = '';
      return;
    }
    ['measure-a', 'measure-b'].forEach(function (id, index) {
      var point = state.measurePoints[index] || a;
      var circle = document.getElementById(id);
      circle.setAttribute('cx', point.x);
      circle.setAttribute('cy', point.y);
    });
    var line = document.getElementById('measure-line');
    line.setAttribute('x1', a.x); line.setAttribute('y1', a.y);
    line.setAttribute('x2', (b || a).x); line.setAttribute('y2', (b || a).y);
    if (b) {
      var miles = Math.hypot(b.x - a.x, b.y - a.y) * MILES_PER_PIXEL;
      var distance = miles < .1 ? Math.round(miles * 5280) + ' ft' : miles.toFixed(2) + ' mi';
      var minutes = Math.max(1, Math.round(miles / 3 * 60));
      document.getElementById('measure-result').textContent = distance + ' · about ' + minutes + ' min on foot';
      document.getElementById('measure-help').textContent = 'Click another point to begin a new measurement.';
    } else {
      document.getElementById('measure-help').textContent = 'Now choose the second point.';
    }
  }

  function renderMarkers() {
    markerHost.innerHTML = '';
    places.forEach(function (place) {
      var button = document.createElement('button');
      button.type = 'button';
      button.className = 'marker';
      button.dataset.id = place.id;
      button.dataset.kind = place.kind;
      button.style.left = place.x + 'px';
      button.style.top = place.y + 'px';
      button.setAttribute('aria-label', place.name + ', ' + titleKind(place.kind));
      button.innerHTML = '<span aria-hidden="true">' + escapeHtml(place.icon) + '</span><span class="marker-label">' + escapeHtml(place.name) + '</span>';
      button.addEventListener('pointerdown', function (ev) { ev.stopPropagation(); });
      button.addEventListener('click', function (ev) {
        ev.stopPropagation();
        if (state.measuring) { addMeasurePoint({x:place.x, y:place.y}); return; }
        selectPlace(place, true, true);
      });
      markerHost.appendChild(button);
    });
    document.getElementById('place-options').innerHTML = places.map(function (place) {
      return '<option value="' + escapeHtml(place.name) + '">' + escapeHtml(titleKind(place.kind)) + '</option>';
    }).join('');
  }

  function setFilter(kind) {
    state.filter = kind;
    document.querySelectorAll('.filter').forEach(function (button) {
      button.classList.toggle('active', button.dataset.filter === kind);
    });
    document.querySelectorAll('.marker').forEach(function (marker) {
      marker.classList.toggle('hidden', kind !== 'all' && marker.dataset.kind !== kind);
    });
  }

  function findPlace(query) {
    var wanted = query.trim().toLowerCase();
    if (!wanted) { return null; }
    return places.find(function (place) { return place.name.toLowerCase() === wanted; }) ||
      places.find(function (place) { return place.name.toLowerCase().indexOf(wanted) >= 0; });
  }

  function showToast(message) {
    var toast = document.getElementById('toast');
    toast.textContent = message;
    toast.classList.add('visible');
    clearTimeout(showToast.timer);
    showToast.timer = setTimeout(function () { toast.classList.remove('visible'); }, 1800);
  }

  document.getElementById('search-form').addEventListener('submit', function (ev) {
    ev.preventDefault();
    var place = findPlace(document.getElementById('search').value);
    if (!place) {
      if (window.WaterdeepSurvey) { window.WaterdeepSurvey.searchStreet(document.getElementById('search').value); }
      else { showToast('No matching place found'); }
      return;
    }
    setFilter('all');
    selectPlace(place, true, true);
  });
  document.getElementById('filters').addEventListener('click', function (ev) {
    var button = ev.target.closest('[data-filter]');
    if (button) { setFilter(button.dataset.filter); }
  });
  document.getElementById('zoom-in').addEventListener('click', function () { zoomAt(1.25); });
  document.getElementById('zoom-out').addEventListener('click', function () { zoomAt(.8); });
  document.getElementById('fit-map').addEventListener('click', fitMap);
  document.getElementById('view-3d').addEventListener('click', function () { set3d(!state.is3d); });
  document.getElementById('rotate-left').addEventListener('click', function () { orbit(-15, 0); });
  document.getElementById('rotate-right').addEventListener('click', function () { orbit(15, 0); });
  document.getElementById('tilt-down').addEventListener('click', function () { orbit(0, 7); });
  document.getElementById('tilt-up').addEventListener('click', function () { orbit(0, -7); });
  document.getElementById('reset-view').addEventListener('click', resetView);
  document.getElementById('close-details').addEventListener('click', closeDetails);
  document.getElementById('share-place').addEventListener('click', function () {
    var url = location.href;
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(url).then(function () { showToast('Direct link copied'); });
    } else {
      showToast(url);
    }
  });
  document.getElementById('measure-toggle').addEventListener('click', function () {
    state.measuring = !state.measuring;
    state.measurePoints = [];
    viewport.classList.toggle('measuring', state.measuring);
    this.setAttribute('aria-pressed', String(state.measuring));
    this.textContent = state.measuring ? 'Stop' : 'Start';
    document.getElementById('measure-help').textContent = state.measuring
      ? 'Choose the first point on the map.' : 'Choose two points to estimate distance and walking time.';
    renderMeasure();
  });

  viewport.addEventListener('wheel', function (ev) {
    ev.preventDefault();
    zoomAt(ev.deltaY < 0 ? 1.12 : .89, ev.clientX, ev.clientY);
  }, {passive:false});
  viewport.addEventListener('pointerdown', function (ev) {
    if (state.measuring) {
      if (!ev.target.closest('.marker')) { addMeasurePoint(pointFromEvent(ev)); }
      return;
    }
    state.dragging = true; state.pointer = ev.pointerId;
    state.startX = ev.clientX; state.startY = ev.clientY;
    state.originX = state.x; state.originY = state.y;
    state.orbiting = state.is3d && (ev.shiftKey || ev.button === 2);
    state.originTilt = state.tilt; state.originRotation = state.rotation;
    viewport.setPointerCapture(ev.pointerId);
    viewport.classList.add('dragging');
    viewport.classList.toggle('orbiting', state.orbiting);
  });
  viewport.addEventListener('pointermove', function (ev) {
    if (!state.dragging || ev.pointerId !== state.pointer) { return; }
    if (state.orbiting) {
      state.rotation = state.originRotation + (ev.clientX - state.startX) * .18;
      state.tilt = clamp(state.originTilt - (ev.clientY - state.startY) * .14, 18, 68);
    } else {
      state.x = state.originX + ev.clientX - state.startX;
      state.y = state.originY + ev.clientY - state.startY;
    }
    applyTransform();
  });
  function endDrag(ev) {
    if (ev.pointerId !== state.pointer) { return; }
    state.dragging = false; state.orbiting = false; state.pointer = null;
    viewport.classList.remove('dragging', 'orbiting');
  }
  viewport.addEventListener('pointerup', endDrag);
  viewport.addEventListener('pointercancel', endDrag);
  viewport.addEventListener('contextmenu', function (ev) { ev.preventDefault(); });
  viewport.addEventListener('keydown', function (ev) {
    var handled = true;
    if (ev.key === '+' || ev.key === '=') { zoomAt(1.2); }
    else if (ev.key === '-') { zoomAt(.82); }
    else if (ev.key === '0') { fitMap(); }
    else if (ev.key === 'ArrowLeft') { state.x += 40; applyTransform(); }
    else if (ev.key === 'ArrowRight') { state.x -= 40; applyTransform(); }
    else if (ev.key === 'ArrowUp') { state.y += 40; applyTransform(); }
    else if (ev.key === 'ArrowDown') { state.y -= 40; applyTransform(); }
    else if (ev.key === 'Escape') { closeDetails(); }
    else { handled = false; }
    if (handled) { ev.preventDefault(); }
  });

  var censusReport = null;

  function renderHousingCensus(report) {
    if (!Array.isArray(report.wards) || !Array.isArray(report.blockers) ||
        !Number.isInteger(report.inventory_records)) {
      throw new Error('Invalid housing census response');
    }
    var values = report.city_residents || report.covered_residents;
    var label = report.city_residents ? 'Modeled city residents' : 'Covered subtotal only, not city population';
    var scenarios = values ? ['low', 'central', 'high'].map(function (name) {
      return name + ': ' + Number(values[name]).toLocaleString(undefined, {maximumFractionDigits: 1});
    }).join(' / ') : 'No resident estimate: required physical evidence is missing.';
    document.getElementById('census-status').textContent = report.can_replace_population
      ? 'Housing scenario calculated. This is not a verified census and has not changed the active population.'
      : 'Citywide population withheld: survey evidence is incomplete. Active population unchanged.';
    document.getElementById('census-summary').textContent = report.inventory_records.toLocaleString() +
      ' inventory records; ' + report.verified_buildings.toLocaleString() + ' visually reviewed roofs; ' +
      report.estimable_buildings.toLocaleString() + ' usable for housing calculations. ' + label + '. ' + scenarios;
    var readiness = report.input_readiness;
    document.getElementById('census-readiness').textContent = readiness
      ? 'Verified roofs with a ward: ' + readiness.verified_with_ward +
        '; with a physical area: ' + readiness.verified_with_physical_area +
        '; with both: ' + readiness.verified_with_ward_and_physical_area +
        '. Class A roofs with unknown occupancy: ' + readiness.verified_class_a_occupancy_unknown +
        '. These readiness counts overlap; they are not additional buildings or residents.'
      : 'Detailed input readiness was not supplied.';
    document.getElementById('census-blockers').innerHTML = report.blockers.map(function (reason) {
      return '<li>' + escapeHtml(reason) + '</li>';
    }).join('');
    document.getElementById('census-wards').innerHTML = report.wards.map(function (ward) {
      return '<tr><td>' + escapeHtml(ward.name) + '</td><td>' +
        (ward.inventory_records ? ward.inventory_records.toLocaleString() : 'Not surveyed') +
        '</td><td>' + ward.estimable_buildings.toLocaleString() + '</td><td>' +
        (ward.covered_residents ? Number(ward.covered_residents.central).toLocaleString(
          undefined, {maximumFractionDigits: 1}) : 'Unknown') + '</td></tr>';
    }).join('');
    document.getElementById('census-formula').textContent = report.formula;
    document.getElementById('census-assumptions').innerHTML = report.assumptions.map(function (text) {
      return '<li>' + escapeHtml(text) + '</li>';
    }).join('');
    document.getElementById('census-scenarios').textContent = JSON.stringify(report.scenarios, null, 2);
    document.getElementById('census-survey').textContent = JSON.stringify(report.survey, null, 2);
    document.getElementById('census-results').hidden = false;
  }

  function loadHousingCensus() {
    var load = document.getElementById('census-load');
    var download = document.getElementById('census-download');
    load.disabled = true;
    download.disabled = true;
    censusReport = null;
    document.getElementById('census-results').hidden = true;
    document.getElementById('census-status').textContent = 'Reading the building inventory...';
    return fetch('/api/census?settlement=Waterdeep').then(function (response) {
      if (!response.ok) { throw new Error('Housing census request failed (' + response.status + ')'); }
      return response.json();
    }).then(function (report) {
      renderHousingCensus(report);
      censusReport = report;
      download.disabled = false;
    }).catch(function (error) {
      document.getElementById('census-status').textContent = 'Could not load the housing census: ' + error.message;
    }).finally(function () { load.disabled = false; });
  }

  document.getElementById('census-load').addEventListener('click', loadHousingCensus);
  document.getElementById('census-download').addEventListener('click', function () {
    if (!censusReport) { return; }
    var url = URL.createObjectURL(new Blob([JSON.stringify(censusReport, null, 2)], {type:'application/json'}));
    var link = document.createElement('a');
    link.href = url;
    link.download = 'waterdeep-housing-census.json';
    link.click();
    setTimeout(function () { URL.revokeObjectURL(url); }, 1000);
  });
  if (location.hash === '#housing-census') { loadHousingCensus(); }

  image.addEventListener('load', fitMap);
  window.addEventListener('resize', fitMap);
  renderMarkers();
  loadPopulation();
  set3d(true);
  if (image.complete) { fitMap(); }
  var direct = places.find(function (place) { return '#' + place.id === location.hash; });
  if (direct) { setTimeout(function () { selectPlace(direct, true, false); }, 0); }
}());
"""


WATERDEEP_CSS += SURVEY_CSS

WATERDEEP_ASSETS: Dict[str, Tuple[str, str]] = {
    "waterdeep.html": (WATERDEEP_HTML, "text/html; charset=utf-8"),
    "waterdeep.css": (WATERDEEP_CSS, "text/css; charset=utf-8"),
    "waterdeep.js": (WATERDEEP_JS, "application/javascript; charset=utf-8"),
    "waterdeep-directory.js": (WATERDEEP_DIRECTORY_JS, "application/javascript; charset=utf-8"),
    "building-generator.js": (BUILDING_GENERATOR_JS, "application/javascript; charset=utf-8"),
    "waterdeep-survey.js": (SURVEY_JS, "application/javascript; charset=utf-8"),
}
