"""The single-page commodity board served by `faerun.web`.

Kept as Python strings rather than a static/ directory so the UI travels with
the package and needs no package-data configuration to install.
"""

from __future__ import annotations

from typing import Dict, Tuple

INDEX_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Faerun Market Board</title>
<link rel="stylesheet" href="app.css">
</head>
<body>

<header class="topbar">
  <div class="brand">
    <span class="mark">&#9878;&#65038;</span>
    <div>
      <h1>Faer&ucirc;n Market Board</h1>
      <span id="mode-badge" class="mode-badge">Standard mode</span>
      <p class="tagline">Commodity prices by settlement, adjusted for supply, demand, distance, tariffs and season.</p>
    </div>
  </div>

  <div class="worldbar">
    <div class="date-controls">
    <label>Month <select id="month-select"></select></label>
    <label>Year <input id="year-input" type="number" step="1"></label>
    <label>Seed <input id="seed-input" type="number" step="1" title="Rerolls the random market wobble"></label>
    <label class="check"><input id="seasonal-toggle" type="checkbox"> Seasonal inventory</label>
    <button id="apply-world" class="primary" type="button">Apply</button>
    <span id="world-date" class="pill" data-world-date></span>
    </div>
    <nav class="nav-links" aria-label="Main navigation">
    <span class="navlink navlink-current" aria-current="page">Markets</span>
    <a class="navlink" href="location.html">Locations</a>
    <a class="navlink" href="business.html">Businesses</a>
    <a class="navlink" href="product.html">Products</a>
    <a class="navlink" href="route.html">Routes</a>
    <a class="navlink" href="map.html">Map</a>
    <a class="navlink" href="planner.html">Route planner</a>
    <a class="navlink" href="mobile.html">Travelling companies</a>
    <a class="navlink" href="trade.html">Merchant guild &amp; POs</a>
    <a class="navlink" href="events.html">Events</a>
    <a class="navlink" href="board.html">Request board</a>
    <a class="navlink" href="lore.html">Lore</a>
    </nav>
  </div>
</header>

<main>
  <aside class="sidebar">
    <input id="settlement-search" type="search" placeholder="Search settlements..." autocomplete="off">
    <select id="region-filter"><option value="">All regions</option></select>
    <div id="settlement-list" class="settlement-list"></div>
  </aside>

  <section class="board">
    <div id="market-header" class="market-header"></div>

    <div class="controls">
      <input id="commodity-search" type="search" placeholder="Filter goods..." autocomplete="off">
      <select id="category-filter"><option value="">All categories</option></select>
      <label class="check"><input id="available-only" type="checkbox" checked> Available products only</label>
      <label class="check"><input id="only-local" type="checkbox"> Local produce only</label>
      <label class="check" title="Skip expanded requirements and seasonal inventory replay for faster reference prices"><input id="simple-price-mode" type="checkbox"> Simple prices</label>
      <span id="row-count" class="muted"></span>
    </div>

    <div id="board-status" class="status"></div>

    <div class="table-wrap">
      <table id="price-table">
        <thead>
          <tr>
            <th data-sort="commodity_name">Commodity</th>
            <th data-sort="category">Category</th>
            <th data-sort="production_type">Type</th>
            <th data-sort="unit">Unit</th>
            <th data-sort="base_price" class="num">Base</th>
            <th data-sort="price" class="num">Buy from merchant</th>
            <th data-sort="buy_price" class="num">Sell to merchant</th>
            <th data-sort="merchant_markup_pct" class="num" title="Quoted resale markup over the merchant's purchase offer, before costs and losses">Merchant markup</th>
            <th data-sort="multiplier" class="num">vs base</th>
            <th data-sort="availability">Availability</th>
            <th data-sort="stock" class="num">Stock estimate</th>
            <th data-sort="uncommitted_stock" class="num" title="Whole trade units beyond planned demand, exports and dated PO claims. Open the Merchant guild desk for the exact supply window and reservation.">Uncommitted stock</th>
            <th data-sort="demand_per_day" class="num">Demand/day</th>
            <th data-sort="source">Sourced from</th>
          </tr>
        </thead>
        <tbody id="price-body"></tbody>
      </table>
    </div>
    <p class="muted">Buy from merchant is what you pay; sell to merchant is what you receive.
      Uncommitted stock protects final demand, workshop inputs, and allocated exports.
      With seasonal inventory enabled, local stocks carry forward with storage losses and protected reserves;
      otherwise stock uses a steady-state window estimate. Neither is a booking; prices can still move with quantity.</p>
  </section>

  <aside id="detail" class="detail">
    <div class="detail-empty">Select a commodity to see its price history and how other markets compare.</div>
  </aside>
</main>

<script src="date.js"></script>
<script src="app.js" defer></script>
</body>
</html>
"""

APP_CSS = """
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
  --bg: var(--cp-surface);
  --panel: var(--cp-bg-elevated);
  --panel-2: var(--cp-surface-soft);
  --line: var(--cp-border);
  --line-soft: var(--cp-border);
  --ink: var(--cp-text);
  --muted: var(--cp-text-muted);
  --accent: var(--cp-accent);
}

* { box-sizing: border-box; }

body {
  margin: 0;
  height: 100vh;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  background: var(--bg);
  color: var(--ink);
  font: 14px/1.45 -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
}

h1 { font-size: 20px; margin: 0; letter-spacing: .01em; font-weight: 600; }
.tagline { margin: 2px 0 0; color: var(--muted); font-size: 12px; }
.mode-badge {
  display: inline-block;
  margin-top: 4px;
  padding: 3px 8px;
  border-radius: 999px;
  border: 1px solid var(--line);
  background: rgba(17, 24, 39, 0.06);
  color: var(--cp-text-muted);
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.04em;
  text-transform: uppercase;
}
.mode-badge.seasonal {
  background: linear-gradient(135deg, rgba(177, 31, 75, 0.15), rgba(245, 158, 11, 0.18));
  border-color: rgba(177, 31, 75, 0.35);
  color: var(--cp-accent);
  box-shadow: inset 0 0 0 1px rgba(177, 31, 75, 0.12);
}
.muted { color: var(--muted); }

button, input, select {
  font: inherit;
  color: var(--ink);
  background: #ffffff;
  border: 1px solid var(--line);
  border-radius: 3px;
  padding: 5px 8px;
}
button { cursor: pointer; }
button:hover { border-color: var(--ink); }
button.primary { background: var(--ink); color: #ffffff; border-color: var(--ink); font-weight: 600; }
button.primary:hover { background: #333333; }
button.ghost { background: transparent; }
label { display: inline-flex; align-items: center; gap: 6px; color: var(--muted); font-size: 12px; }
input[type=number] { width: 76px; }
:focus-visible { outline: 2px solid var(--ink); outline-offset: 1px; }

.topbar {
  display: flex; flex-wrap: wrap; gap: 16px;
  align-items: center; justify-content: space-between;
  padding: 12px 18px;
  background: var(--bg);
  border-bottom: 2px solid var(--ink);
}
.brand { display: flex; align-items: center; gap: 12px; }
.mark { font-size: 28px; color: var(--ink); }
.worldbar { display: flex; flex-wrap: wrap; align-items: center; gap: 10px; }
.date-controls { display: flex; flex-wrap: wrap; align-items: center; justify-content: flex-end; gap: 10px; }
.nav-links { display: flex; flex-wrap: wrap; align-items: center; justify-content: flex-end; gap: 10px; }
.pill {
  background: var(--panel); border: 1px solid var(--line);
  border-radius: 999px; padding: 4px 12px; color: var(--ink); font-size: 12px;
}

.navlink {
  color: var(--ink); text-decoration: none; font-size: 13px;
  border: 1px solid var(--line); border-radius: 3px; padding: 5px 9px;
}
.navlink-current,
.topbar .navlink-current {
  color: var(--cp-text-soft) !important;
  background: var(--cp-surface-soft) !important;
  border-color: var(--cp-border) !important;
  opacity: .62;
  cursor: default;
  pointer-events: none;
}
.navlink:hover { border-color: var(--ink); }

.eventdrawer {
  flex: 0 0 auto;
  background: var(--panel);
  border-bottom: 1px solid var(--line);
}
.eventdrawer summary {
  padding: 7px 18px;
  color: var(--ink);
  font-size: 12px;
  font-weight: 600;
  cursor: pointer;
  user-select: none;
}
.eventdrawer[open] summary { border-bottom: 1px solid var(--line); }
.eventbar {
  display: flex; flex-wrap: wrap; align-items: center; gap: 10px;
  padding: 8px 18px; background: var(--panel);
  max-height: min(36vh, 300px);
  overflow: auto;
}
.event-list { display: flex; flex-wrap: wrap; gap: 6px; margin-left: auto; }
.event-chip {
  display: inline-flex; align-items: center; gap: 6px;
  background: #ffffff; border: 1px solid var(--ink); color: var(--ink);
  border-radius: 999px; padding: 2px 6px 2px 10px; font-size: 12px;
}
.event-chip button {
  border: none; background: transparent; color: var(--ink);
  padding: 0 4px; line-height: 1; font-size: 14px;
}
.event-chip button:hover { color: var(--muted); }

main {
  display: grid;
  grid-template-columns: 260px minmax(0, 1fr) 330px;
  gap: 1px;
  background: var(--line);
  flex: 1 1 auto;
  min-height: 0;
}
@media (max-width: 1200px) {
  main { grid-template-columns: 220px minmax(0, 1fr); }
  .detail { display: none; }
}

.sidebar, .board, .detail { background: var(--bg); overflow: auto; }
.sidebar { padding: 10px; display: flex; flex-direction: column; gap: 8px; }
.sidebar input, .sidebar select { width: 100%; }
.settlement-list { overflow: auto; }

.region-head {
  color: var(--ink); font-size: 11px; text-transform: uppercase;
  letter-spacing: .08em; margin: 12px 0 4px; padding-left: 4px;
  font-weight: 700; padding-bottom: 2px; border-bottom: 1px solid var(--line-soft);
}
.settlement {
  padding: 5px 8px; border-radius: 3px; cursor: pointer;
  display: flex; justify-content: space-between; gap: 8px; align-items: baseline;
}
.settlement:hover { background: var(--panel-2); }
.settlement.active { background: var(--ink); color: #ffffff; }
.settlement.active .settlement-meta { color: #cccccc; }
.settlement-meta { color: var(--muted); font-size: 11px; white-space: nowrap; }
.settlement-events { display: flex; flex-wrap: wrap; gap: 4px; grid-column: 1 / -1; margin-top: 4px; }
.settlement-event { color: var(--cp-accent); font-size: 11px; line-height: 1.25; }
.settlement-event::before { content: '• '; }
.location-events-panel { margin-top: 14px; padding: 14px 16px; border: 1px solid var(--cp-border); border-left: 4px solid var(--cp-accent); border-radius: 12px; background: var(--cp-surface-soft); }
.location-events-panel h3 { margin: 0 0 8px; font-size: 14px; }
.location-event-narrative { margin: 8px 0 0; color: var(--cp-text-muted); line-height: 1.55; }

.board { display: flex; flex-direction: column; }
.market-header { padding: 14px 18px 6px; }
.market-header h2 { margin: 0 0 2px; font-size: 22px; color: var(--ink); font-weight: 600; }
.market-header .facts { color: var(--muted); font-size: 12px; }
.market-header .desc { margin: 6px 0 0; font-size: 13px; max-width: 70ch; }
.tags { margin-top: 6px; display: flex; flex-wrap: wrap; gap: 4px; }
.tag {
  font-size: 11px; background: var(--panel); border: 1px solid var(--line);
  border-radius: 3px; padding: 1px 6px; color: var(--muted);
}
.tag.warn { background: var(--ink); border-color: var(--ink); color: #ffffff; }

.controls {
  display: flex; flex-wrap: wrap; align-items: center; gap: 10px;
  padding: 8px 18px; border-bottom: 1px solid var(--line);
}
.controls input[type=search] { min-width: 180px; }
.check { gap: 4px; }
.status { padding: 10px 18px; color: var(--muted); }
.status.error { color: var(--ink); font-weight: 700; }
.market-progress {
  display: grid;
  gap: 6px;
  max-width: 420px;
}
.market-progress span { font-size: 12px; }
.market-progress .bar {
  position: relative;
  height: 8px;
  overflow: hidden;
  border: 1px solid var(--line);
  border-radius: 999px;
  background: var(--panel-2);
}
.market-progress .fill {
  display: block;
  height: 100%;
  border-radius: inherit;
  background: linear-gradient(90deg, var(--accent), var(--cp-warning));
  transition: width 180ms ease;
}
.market-progress .bar.indeterminate::before {
  content: "";
  position: absolute;
  inset-block: 0;
  width: 42%;
  border-radius: inherit;
  background: linear-gradient(90deg, var(--accent), var(--cp-warning));
  animation: market-progress 1.1s ease-in-out infinite;
}
@keyframes market-progress {
  0% { transform: translateX(-115%); }
  100% { transform: translateX(250%); }
}

.table-wrap { overflow: auto; flex: 1; }
table { border-collapse: collapse; width: 100%; font-size: 13px; }
thead th {
  position: sticky; top: 0; z-index: 1;
  background: var(--bg); border-bottom: 2px solid var(--ink);
  text-align: left; padding: 7px 10px; cursor: pointer;
  font-size: 11px; text-transform: uppercase; letter-spacing: .06em; color: var(--muted);
  white-space: nowrap;
}
thead th:hover { color: var(--ink); }
thead th.sorted { color: var(--ink); font-weight: 700; }
tbody td { padding: 5px 10px; border-bottom: 1px solid var(--line-soft); }
tbody tr { cursor: pointer; }
tbody tr:hover { background: var(--panel); }
tbody tr.active { background: var(--panel-2); box-shadow: inset 3px 0 0 var(--ink); }
.num { text-align: right; font-variant-numeric: tabular-nums; }

/* Without colour, price pressure reads as a weight ramp: grey, black, bold. */
.cheap { color: var(--muted); }
.dear { color: var(--ink); font-weight: 700; }
.imported { color: var(--ink); }

.detail { padding: 14px; }
.detail-empty { color: var(--muted); font-size: 13px; }
.detail h3 { margin: 0 0 2px; color: var(--ink); font-size: 17px; font-weight: 600; }
.detail h4 {
  margin: 18px 0 6px; font-size: 11px; text-transform: uppercase;
  letter-spacing: .08em; color: var(--muted); font-weight: 700;
}
.detail .desc { font-size: 12px; color: var(--muted); margin: 4px 0 0; }
.kv { display: grid; grid-template-columns: auto 1fr; gap: 2px 10px; font-size: 12px; margin-top: 8px; }
.kv div:nth-child(odd) { color: var(--muted); }
.kv div:nth-child(even) { text-align: right; font-variant-numeric: tabular-nums; }
.spark { width: 100%; height: 90px; background: var(--bg); border: 1px solid var(--line); border-radius: 3px; }
.mini { width: 100%; font-size: 12px; border-collapse: collapse; }
.mini td { padding: 3px 4px; border-bottom: 1px solid var(--line-soft); }
.mini td:last-child { text-align: right; font-variant-numeric: tabular-nums; }
.here { color: var(--ink); font-weight: 700; }

body {
  height: 100dvh;
  font-family: "Segoe UI", Aptos, Calibri, sans-serif;
  background: var(--cp-bg);
}
h1, h2, h3, h4, th, .region-head { letter-spacing: 0; }
button, input, select { border-radius: 6px; min-height: 34px; background: var(--cp-surface); }
input[type=checkbox], input[type=range] { min-height: 0; accent-color: var(--cp-accent); }
button:hover, select:hover { border-color: var(--cp-accent); }
button.primary { background: var(--cp-accent); border-color: var(--cp-accent); color: var(--cp-accent-fg); }
button.primary:hover { background: var(--cp-accent-hover); }
:focus-visible { outline: 2px solid var(--cp-accent); outline-offset: 3px; }
.topbar {
  flex: 0 0 auto;
  min-height: 168px;
  gap: 16px 24px;
  padding: 20px clamp(16px,3%,64px);
  background: var(--cp-surface-soft);
  border-bottom: 1px solid var(--cp-border);
  border-top: 3px solid var(--cp-accent);
}
.brand { min-width: 0; }
.brand h1 { font-size: 50px; font-weight: 600; line-height: 1.05; overflow-wrap: anywhere; }
.brand .mark { color: var(--cp-accent); font-size: 32px; flex-shrink: 0; }
.tagline { display: none; }
.worldbar { gap: 12px; min-width: 0; }
.navlink { border: 0; border-bottom: 2px solid transparent; border-radius: 0; color: var(--cp-text-muted); padding: 8px 0; }
.navlink:hover { color: var(--cp-accent); background: transparent; border-color: var(--cp-accent); }
.pill { border: 0; background: var(--cp-accent-soft); color: var(--cp-accent); font-weight: 600; border-radius: 6px; }
#world-date { font-size: 20px; padding: 10px 16px; }
.date-tile,
[data-world-date] {
  display: grid;
  gap: 2px;
  min-width: 210px;
  min-height: 72px;
  padding: 9px 16px !important;
  text-align: center;
  line-height: 1.15;
  white-space: nowrap;
}
.date-line { display: block; }
.date-line-day { font-size: 16px; font-weight: 700; }
.date-line-season { font-size: 13px; text-transform: capitalize; }
.date-line-moon { font-size: 12px; opacity: .78; }
.eventdrawer { background: var(--cp-surface); }
.eventdrawer summary { padding: 12px clamp(16px,3%,64px); color: var(--cp-text-muted); }
main { grid-template-columns: minmax(210px,16%) minmax(0, 1fr) minmax(290px,23%); }
main:has(.detail-empty) { grid-template-columns: minmax(210px,16%) minmax(0, 1fr); }
.detail:has(.detail-empty) { display: none; }
.sidebar { padding: 20px 16px; background: var(--cp-surface-soft); gap: 12px; min-width: 0; }
.region-head { margin-top: 20px; padding: 0 10px 7px; font-size: 10px; color: var(--cp-text-soft); }
.settlement { padding: 8px 10px; min-height: 36px; border-radius: 6px; }
.settlement.active { background: var(--cp-accent-soft); color: var(--cp-accent); box-shadow: inset 3px 0 var(--cp-accent); font-weight: 600; }
.settlement.active .settlement-meta { color: var(--cp-text-muted); }
.market-header { padding: 26px 24px 20px; background: linear-gradient(90deg,var(--cp-surface-soft),var(--cp-surface)); border-bottom: 1px solid var(--cp-border); }
.market-header h2 { font-size: 28px; font-weight: 650; margin-bottom: 6px; }
.market-header .desc { line-height: 1.65; }
.tags { gap: 6px; margin-top: 12px; }
.tag { background: var(--cp-surface); padding: 3px 7px; border-radius: 4px; }
.tag.warn { background: var(--cp-accent-soft); color: var(--cp-accent); border-color: var(--cp-highlight); }
.controls { padding: 12px 24px; }
.status:empty { display: none; }
.status.error { color: var(--cp-danger); }
#price-table { min-width: 1080px; }
thead th { padding: 12px 10px; background: var(--cp-bg-elevated); border-bottom: 1px solid var(--cp-border-strong); font-size: 10px; }
thead th.sorted { color: var(--cp-accent); }
tbody td { padding: 10px; }
tbody tr:nth-child(even) { background: var(--cp-bg-elevated); }
tbody tr:hover { background: var(--cp-accent-soft); }
tbody tr.active { background: var(--cp-highlight); box-shadow: inset 3px 0 var(--cp-accent); }
#price-table td:first-child { font-weight: 600; min-width: 155px; }
#price-table td.num { white-space: nowrap; }
#price-table td:nth-child(6) { font-weight: 700; }
.dear { color: var(--cp-accent); }
.imported { color: var(--cp-link); }
.detail { padding: 24px 20px; background: var(--cp-surface); min-width: 0; border-top: 3px solid var(--cp-accent); }
.detail h3 { font-size: 21px; }
.detail h4 { padding-bottom: 8px; border-bottom: 1px solid var(--cp-border); }
.kv { gap: 9px 12px; grid-template-columns: minmax(0,1fr) minmax(0,1fr); }
.kv div { overflow-wrap: anywhere; }
.spark { border-radius: 6px; margin-top: 8px; }
.mini td { padding: 7px 4px; }
.detail .mini { table-layout: fixed; }
.detail .mini th { padding: 8px 3px; white-space: normal; overflow-wrap: anywhere; font-size: 9px; }
.detail .mini td { padding: 7px 3px; overflow-wrap: anywhere; font-size: 11px; }
.detail .mini .num { white-space: nowrap; }
.detail a { color: var(--cp-link); }
.supply-breakdown { margin: 14px 0; min-width: 0; }
.supply-breakdown summary { cursor: pointer; padding: 9px 0; overflow-wrap: anywhere; }
.supply-breakdown table { width: 100%; border-collapse: collapse; font-size: 12px; }
.supply-breakdown th, .supply-breakdown td { padding: 8px; text-align: left; border-bottom: 1px solid var(--cp-border); }
.supply-breakdown th { color: var(--cp-text-muted); }
.supply-breakdown p { overflow-wrap: anywhere; }
button, input:not([type=checkbox]):not([type=range]):not([type=radio]), select { min-height: 40px; }
input:not([type=checkbox]):not([type=range]):not([type=radio]), select { background: var(--cp-surface-soft); border-color: var(--cp-border); }
input:focus, select:focus { background: var(--cp-surface); }
button:disabled { opacity: .55; cursor: default; }
summary::marker { color: var(--cp-accent); }
.board { min-width: 0; }
tbody tr:nth-child(even) { background: var(--cp-surface-soft); }
tbody tr:hover { background: var(--cp-accent-soft); }
thead th { background: var(--cp-surface-soft); }
.eventbar { padding: 12px clamp(16px,3%,64px); }
.event-chip { background: var(--cp-surface-soft); border-color: var(--cp-border); color: var(--cp-text); border-radius: 6px; }
.topbar, .sidebar, .market-header, .controls, .detail {
  box-shadow: 0 8px 24px rgba(25, 35, 45, .06);
}
.board > .table-wrap {
  margin: 0 18px 18px;
  padding: 14px;
  border: 1px solid var(--cp-border);
  border-radius: 18px;
  background: var(--cp-surface);
  box-shadow: 0 8px 24px rgba(25, 35, 45, .07);
}
.board > .controls {
  margin: 0 18px 14px;
  padding: 14px 16px;
  border: 1px solid var(--cp-border);
  border-radius: 16px;
  background: var(--cp-surface);
  box-shadow: 0 7px 20px rgba(25, 35, 45, .07);
}
.board > .market-header {
  margin: 18px 18px 14px;
  padding: 20px 22px;
  border: 1px solid var(--cp-border);
  border-radius: 18px;
  background: var(--cp-surface);
  box-shadow: 0 8px 24px rgba(25, 35, 45, .07);
}
.eventdrawer {
  margin: 12px 18px 18px;
  border: 1px solid var(--cp-border);
  border-radius: 16px;
  background: var(--cp-surface);
  box-shadow: 0 7px 20px rgba(25, 35, 45, .07);
  overflow: hidden;
}
.eventdrawer + main {
  margin-top: 0;
  padding-top: 0;
}
.board-shell > .sidebar,
main > .sidebar {
  margin: 18px 0 18px 18px;
  border: 1px solid var(--cp-border);
  border-radius: 18px;
  background: var(--cp-surface);
  box-shadow: 0 8px 24px rgba(25, 35, 45, .07);
}
main > .detail {
  margin: 18px 18px 18px 0;
  border: 1px solid var(--cp-border);
  border-radius: 18px;
  background: var(--cp-surface);
  box-shadow: 0 8px 24px rgba(25, 35, 45, .07);
}
.board,
main > .sidebar,
main > .detail {
  background: var(--cp-surface);
}
.board {
  min-height: 0;
  overflow: hidden;
}
.board > .table-wrap {
  min-height: 0;
}
main > .detail {
  min-height: 0;
  overflow: hidden;
}
main {
  gap: 24px;
  background: var(--cp-surface);
}
main > .sidebar,
main > .detail {
  margin: 0;
  border: 0;
  border-radius: 0;
  box-shadow: none;
}
main {
  grid-template-columns: minmax(250px, 20%) minmax(0, 1fr) minmax(290px, 23%);
}
.sidebar {
  padding-right: 24px;
}
.settlement-list {
  padding-right: 8px;
  scrollbar-gutter: stable;
}
.sidebar > input,
.sidebar > select {
  width: calc(100% - 8px);
  margin-inline: 4px;
  border-radius: 12px;
}
.topbar {
  background: var(--cp-surface);
  border-top: 0;
  border-bottom: 0;
  box-shadow: none;
}
body {
  background: var(--cp-surface);
}
.worldbar { display: grid; justify-items: end; gap: 12px; }
.navlink {
  display: inline-flex;
  align-items: center;
  border: 1px solid var(--cp-border);
  border-radius: 10px;
  background: var(--cp-surface-soft);
  color: var(--cp-text);
  padding: 8px 12px;
  box-shadow: 0 3px 8px rgba(25, 35, 45, .06);
}
.navlink:hover {
  border-color: var(--cp-accent);
  background: var(--cp-accent-soft);
  color: var(--cp-accent);
}
.eventdrawer {
  margin: 12px 18px 18px;
  border: 1px solid var(--cp-border);
  border-radius: 16px;
  background: var(--cp-surface);
  box-shadow: 0 7px 20px rgba(25, 35, 45, .07);
}
.eventdrawer,
.eventdrawer summary,
.eventdrawer .eventbar {
  background: var(--cp-surface);
}
@media (max-width: 1200px) {
  main { grid-template-columns: 240px minmax(0, 1fr); }
}
@media (max-width: 700px) {
  main { grid-template-columns: 1fr; }
  .sidebar { padding-right: 16px; }
  .worldbar, .date-controls, .nav-links { justify-content: flex-start; justify-items: start; width: 100%; }
}
.sidebar .settlement {
  margin: 4px 0;
  padding: 10px 12px;
  border: 1px solid var(--cp-border);
  border-radius: 12px;
  background: var(--cp-surface-soft);
}
.sidebar .settlement:hover { background: var(--cp-accent-soft); }
.sidebar .settlement.active {
  border-color: var(--cp-accent);
  background: var(--cp-accent-soft);
  box-shadow: inset 3px 0 var(--cp-accent), 0 4px 12px rgba(25, 35, 45, .06);
}
.detail > .detail-empty,
.detail > h3,
.detail > .desc,
.detail > .kv,
.detail > .spark,
.detail > .mini,
.detail > .supply-breakdown {
  padding: 16px;
  border: 1px solid var(--cp-border);
  border-radius: 14px;
  background: var(--cp-surface-soft);
}
.detail > h3 { margin-top: 0; }
.detail > .desc { margin-top: 10px; }
.detail > .kv { margin-top: 10px; }
.board > p.muted {
  margin: 0 24px 24px;
  padding: 14px 16px;
  border: 1px solid var(--cp-border);
  border-radius: 14px;
  background: var(--cp-surface-soft);
  color: var(--cp-text-muted);
  line-height: 1.65;
  text-align: left;
}
button, input, select, textarea { border-radius: 10px; }
button { box-shadow: 0 4px 10px rgba(25, 35, 45, .08); }
.navlink { box-shadow: none; }
#price-table { border-collapse: separate; border-spacing: 0 7px; }
#price-table thead th { border-bottom: 0; background: var(--cp-surface-soft); }
#price-table thead th:first-child { border-radius: 12px 0 0 12px; }
#price-table thead th:last-child { border-radius: 0 12px 12px 0; }
#price-table tbody td { border-top: 1px solid var(--cp-border); border-bottom: 1px solid var(--cp-border); background: var(--cp-surface); }
#price-table tbody td:first-child { border-left: 1px solid var(--cp-border); border-radius: 12px 0 0 12px; }
#price-table tbody td:last-child { border-right: 1px solid var(--cp-border); border-radius: 0 12px 12px 0; }
.detail { border-left: 1px solid var(--cp-border); }
@media (max-width: 1200px) {
  main, main:has(.detail-empty) { grid-template-columns: 210px minmax(0, 1fr); }
  .detail:not(:has(.detail-empty)) { display: block; grid-column: 2; max-height: 45dvh; border-top: 1px solid var(--cp-border); }
  .sidebar { grid-row: 1 / span 2; }
  .board { min-height: 320px; }
}
@media (max-width: 700px) {
  body { height: auto; min-height: 100dvh; overflow: auto; }
  .topbar { padding: 12px 16px; }
  .brand h1 { font-size: 32px; }
  .worldbar { width: 100%; }
  main, main:has(.detail-empty) { display: flex; flex-direction: column; }
  .sidebar { padding: 12px 16px; display: grid; grid-template-columns: 1fr 1fr; overflow: visible; }
  .settlement-list { grid-column: 1 / -1; max-height: 170px; }
  .board { min-height: 500px; overflow: visible; }
  .market-header { padding: 20px 16px; }
  .controls { padding: 12px 16px; }
  .controls input[type=search] { min-width: 0; width: 100%; }
  .table-wrap { max-height: 65dvh; flex: auto; }
  .detail:not(:has(.detail-empty)) { max-height: none; overflow: visible; }
}
"""

APP_CSS += """
.seasonal-panel { margin-block: 20px; min-width: 0; }
.seasonal-panel h3, .seasonal-panel h4 { margin-block: 16px 8px; }
.seasonal-panel p { line-height: 1.65; }
.seasonal-chart { overflow-x: auto; }
.seasonal-chart svg { display: block; width: 100%; min-width: 560px; height: auto; color: var(--cp-text, #26333d); }
.seasonal-production { stroke: var(--cp-accent, #9b462d); }
.seasonal-demand { stroke: var(--cp-text, #26333d); stroke-dasharray: 7 4; }
.seasonal-legend { display: flex; flex-wrap: wrap; gap: 8px 24px; font-size: 12px; }
.seasonal-legend span::before { content: ''; display: inline-block; width: 24px; margin-right: 6px; vertical-align: middle; border-top: 3px solid var(--cp-accent, #9b462d); }
.seasonal-legend .demand-key::before { border-top: 3px dashed var(--cp-text, #26333d); }
.seasonal-facts { display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 12px; margin-block: 16px; }
.seasonal-facts div { border: 1px solid var(--cp-border, #ddd); padding: 10px 12px; }
.seasonal-facts dt { font-size: 12px; color: var(--cp-text-muted, #596571); }
.seasonal-facts dd { margin: 5px 0 0; font-size: 16px; font-variant-numeric: tabular-nums; overflow-wrap: anywhere; }
.seasonal-panel table { width: 100%; border-collapse: collapse; }
.seasonal-panel th, .seasonal-panel td { padding: 8px; border-bottom: 1px solid var(--cp-border, #ddd); text-align: left; }
.seasonal-panel summary { cursor: pointer; }
"""

SEASONAL_JS = """
function seasonalEscape(value) {
  return String(value == null ? '' : value).replace(/&/g, '&amp;')
    .replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
}
function seasonalNumber(value) {
  return Number.isFinite(value) ? value.toLocaleString(undefined, {maximumFractionDigits: 3}) : '-';
}
function seasonalEnabled(row) { return !!(row.inventory && row.inventory.enabled); }
function seasonalStockBasis(row) {
  if (seasonalEnabled(row)) {
    return row.inventory.stock_basis || 'Modeled local stock carried forward between dates, after consumption, trade and storage losses.';
  }
  var reason = row.inventory && row.inventory.enabled === false ? row.inventory.reason : '';
  return (reason ? reason + ' ' : '') + seasonalNumber(row.stock_horizon_days) +
    '-day modeled window; a steady-state stock estimate, not a booking.';
}
function seasonalFreeBasis(row) {
  return row.uncommitted_basis || (seasonalEnabled(row)
    ? 'Uncommitted stock excludes protected reserves, local requirements and export commitments; it is not a booking.'
    : seasonalStockBasis(row));
}
function seasonalPanel(row, fallbackProfile) {
  var profile = row.seasonality && Array.isArray(row.seasonality.months) && row.seasonality.months.length
    ? row.seasonality : (fallbackProfile || {});
  var months = Array.isArray(profile.months) ? profile.months : [];
  var enabled = seasonalEnabled(row), inventory = row.inventory || {};
  var disabledReason = inventory.enabled === false ? inventory.reason : '';
  var valid = months.length === 12 && months.every(function (m) {
    return Number.isFinite(m.production_multiplier) && m.production_multiplier >= 0 &&
      Number.isFinite(m.demand_multiplier) && m.demand_multiplier >= 0;
  });
  if (!valid && !enabled && !disabledReason) return '';
  function metric(label, value) {
    return '<div><dt>' + seasonalEscape(label) + '</dt><dd>' + seasonalEscape(value) + '</dd></div>';
  }
  var html = '<section class="seasonal-panel" aria-label="Regional seasonality and local inventory">';
  if (disabledReason) {
    html += '<p><strong>Inventory disabled for this quote:</strong> ' + seasonalEscape(disabledReason) +
      ' Historical dates before the replay epoch use steady-state quotes, not a backdated physical ledger.' +
      (inventory.epoch ? ' Configured epoch: ' + seasonalEscape(inventory.epoch) + '.' : '') +
      (valid ? ' The curves below describe configured seasonality, not an applied inventory simulation for this date.' : '') + '</p>';
  }
  if (valid) {
    var ceiling = Math.max(1, ...months.map(function (m) { return Math.max(m.production_multiplier, m.demand_multiplier); }));
    var top = Math.ceil(ceiling * 2) / 2;
    function x(i) { return 52 + i * 60; }
    function y(value) { return 200 - value / top * 164; }
    function points(field) {
      return months.map(function (m, i) { return x(i) + ',' + y(m[field]).toFixed(2); }).join(' ');
    }
    html += '<h3>12-month production &amp; demand curves</h3><p>Local climate: <strong>' +
      seasonalEscape(profile.climate || 'unspecified') +
      '</strong>. Multipliers relative to the configured baseline; these are modeling assumptions, not canonical agronomy. ' +
      'Production is seasonal potential, not guaranteed output: recipes still need their inputs.</p>' +
      '<div class="seasonal-legend"><span>Production potential (solid)</span><span class="demand-key">Demand (dashed)</span></div>' +
      '<div class="seasonal-chart" tabindex="0" role="region" aria-label="Scrollable monthly production and demand chart">' +
      '<svg viewBox="0 0 752 244" role="img" aria-label="Twelve monthly production and demand multipliers; exact values in the table below">' +
      '<title>Regional production potential and demand by month</title>' +
      '<path d="M52 30 V200 H712" fill="none" stroke="currentColor" opacity=".4"/>' +
      '<path d="M52 ' + y(1).toFixed(2) + ' H712" fill="none" stroke="currentColor" opacity=".25" stroke-dasharray="3 4"/>' +
      '<text x="4" y="204" fill="currentColor" font-size="11">0x</text>' +
      '<text x="4" y="' + (y(1) + 4).toFixed(2) + '" fill="currentColor" font-size="11">1x</text>' +
      (top > 1 ? '<text x="4" y="36" fill="currentColor" font-size="11">' + top + 'x</text>' : '') +
      '<polyline class="seasonal-production" fill="none" stroke-width="3" points="' + points('production_multiplier') + '"/>' +
      '<polyline class="seasonal-demand" fill="none" stroke-width="3" points="' + points('demand_multiplier') + '"/>' +
      months.map(function (m, i) {
        return '<text x="' + x(i) + '" y="224" fill="currentColor" text-anchor="middle" font-size="10"><title>' +
          seasonalEscape(m.name) + '</title>' + seasonalEscape(String(m.name || m.month).slice(0, 4)) + '</text>';
      }).join('') + '</svg></div><dl class="seasonal-facts">' +
      metric('Current production multiplier', seasonalNumber(profile.production_multiplier) + 'x') +
      metric('Current demand multiplier', seasonalNumber(profile.demand_multiplier) + 'x') + '</dl>' +
      '<details><summary>Inspect all 12 monthly values</summary><table><thead><tr><th scope="col">Month</th>' +
      '<th scope="col">Production potential</th><th scope="col">Demand</th></tr></thead><tbody>' +
      months.map(function (m) {
        return '<tr><th scope="row">' + seasonalEscape(m.name || m.month) + '</th><td>' +
          seasonalNumber(m.production_multiplier) + 'x</td><td>' + seasonalNumber(m.demand_multiplier) + 'x</td></tr>';
      }).join('') + '</tbody></table></details>';
  }
  if (enabled) {
    var unit = row.unit || 'trade units';
    function amount(value) { return seasonalNumber(value) + ' ' + unit; }
    html += '<h3>Local granary / storage reserves</h3><p>Market-wide modeled quantities, not a ten-day stock-window estimate ' +
      'or a survey of individual warehouses. Grade offers share this market pool.</p><dl class="seasonal-facts">' +
      metric('Opening stock', amount(inventory.opening_stock)) +
      metric('Closing stock', amount(inventory.closing_stock)) +
      metric('Uncommitted local inventory', amount(inventory.uncommitted_stock)) +
      metric('Storage capacity', amount(inventory.storage_capacity)) +
      metric('Protected reserve target', amount(inventory.reserve_target)) +
      metric('Storage spoilage', amount(inventory.spoilage)) +
      metric('Storage overflow', amount(inventory.overflow)) +
      metric('Stock draw / day', amount(inventory.stock_draw_per_day) + '/day') +
      metric('Days of cover', inventory.days_of_cover === null ? 'Not applicable (no demand)' : seasonalNumber(inventory.days_of_cover) + ' days') +
      (Number.isFinite(profile.storage_days) ? metric('Storage capacity basis', seasonalNumber(profile.storage_days) + ' baseline days') : '') +
      (Number.isFinite(profile.storage_loss) ? metric('Storage loss rate', seasonalNumber(profile.storage_loss * 100) + '% / day') : '') +
      (Number.isFinite(profile.reserve_days) ? metric('Reserve policy', seasonalNumber(profile.reserve_days) + ' baseline days') : '') +
      metric('Replay epoch', inventory.epoch || 'Not supplied') + '</dl><p><strong>Stock basis:</strong> ' +
      seasonalEscape(seasonalStockBasis(row)) + '</p><p>' + seasonalEscape(seasonalFreeBasis(row)) +
      ' Inventory free stock is the physical-model pool; dated PO planning quotas may differ.</p>' +
      '<p>Stored ingredients can support milling, baking and brewing outside the harvest season. ' +
      'Storage does not guarantee uninterrupted supply.</p>' +
      '<details><summary>Daily replay assumptions and limits</summary>' +
      '<p>The configurable inventory epoch defaults to 1492-01-01. Initial stocks are seeded to reserve targets ' +
      'as a prior-harvest assumption, unless overridden for a location/product; storage capacities can also be overridden. ' +
      'Both ingredients and finished goods are tracked.</p>' +
      '<p>Daily balances replay deterministically using ' +
      (inventory.checkpoint_storage === 'local SQLite cache'
        ? 'versioned local SQLite checkpoints shared across restarts. '
        : 'in-memory month checkpoints, not on-disk inventory persistence. ') +
      'Restarting with the same configuration and events reconstructs identical balances. ' +
      'Player purchases are not executed against this physical inventory.</p>' +
      '<p>Imports are same-day steady-state deliveries, not scheduled shipment arrivals. Manufacturing labor ceilings ' +
      'and physical shipment loss accounting are not modeled.</p></details>';
  }
  return html + '</section>';
}
"""

from .sourceassets import SOURCING_JS

APP_JS = SOURCING_JS + SEASONAL_JS + """
'use strict';

const state = {
  boot: null,
  settlementId: null,
  report: null,
  rows: [],
  selected: null,
  sort: { key: 'category', dir: 1 },
  requestToken: 0,
  progressTimer: null,
};

const $ = (id) => document.getElementById(id);

function esc(value) {
  return String(value === null || value === undefined ? '' : value)
    .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}

function coin(gp) {
  if (gp === null || gp === undefined) return '-';
  if (gp >= 1) return gp.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 3 }) + ' gp';
  if (gp >= 0.1) return (gp * 10).toLocaleString(undefined, { minimumFractionDigits: 1, maximumFractionDigits: 2 }) + ' sp';
  return (gp * 100).toFixed(1) + ' cp';
}

function quoteMarkup(value) {
  return Number.isFinite(value) ? value.toFixed(1) + '%' : '&mdash;';
}

function quoteQuantity(value) {
  return Number.isFinite(value) ? value.toLocaleString(undefined, { maximumFractionDigits: 3 }) : '&mdash;';
}

function progressId() {
  return 'market-' + Date.now().toString(36) + '-' + Math.random().toString(36).slice(2, 8);
}

function marketProgress(progress) {
  const done = Number(progress.done || 0);
  const total = Number(progress.total || 0);
  const percent = total > 0 ? Math.max(0, Math.min(100, Math.round(done / total * 100))) : null;
  const label = progress.label && progress.status !== 'complete' ? ' · ' + progress.label : '';
  const text = percent === null
    ? 'Consulting the market...' + label
    : 'Consulting the market... ' + done.toLocaleString() + ' / ' + total.toLocaleString() +
      ' goods (' + percent + '%)' + label;
  const aria = percent === null ? '' : ' aria-valuemin="0" aria-valuemax="100" aria-valuenow="' + percent + '"';
  const bar = percent === null
    ? '<div class="bar indeterminate"></div>'
    : '<div class="bar"><i class="fill" style="width:' + percent + '%"></i></div>';
  return '<div class="market-progress" role="progressbar" aria-label="Consulting the market" aria-busy="true"' + aria + '>' +
    '<span>' + esc(text) + '</span>' + bar + '</div>';
}

function stopProgress() {
  if (state.progressTimer !== null) {
    window.clearInterval(state.progressTimer);
    state.progressTimer = null;
  }
}

async function getJSON(path, params) {
  const url = new URL(path, window.location.origin);
  Object.entries(params || {}).forEach(([k, v]) => {
    if (v !== null && v !== undefined && v !== '') url.searchParams.set(k, v);
  });
  const res = await fetch(url);
  const data = await res.json().catch(() => ({ error: 'bad JSON from server' }));
  if (!res.ok) throw new Error(data.error || ('HTTP ' + res.status));
  return data;
}

async function postJSON(path, body) {
  const res = await fetch(path, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body || {}),
  });
  const data = await res.json().catch(() => ({ error: 'bad JSON from server' }));
  if (!res.ok) throw new Error(data.error || ('HTTP ' + res.status));
  return data;
}

// ---------------------------------------------------------------------------
// World / bootstrap
// ---------------------------------------------------------------------------

function setModeBadge(boot) {
  const modeLabel = boot.seasonal_inventory ? 'Seasonal inventory' : 'Standard mode';
  const badge = $('mode-badge');
  if (badge) badge.textContent = modeLabel;
  badge && badge.classList.toggle('seasonal', !!boot.seasonal_inventory);
  return modeLabel;
}

function setDocumentTitle(boot) {
  const modeLabel = setModeBadge(boot);
  document.title = 'Faerun Market Board — ' + modeLabel;
}

function applyBoot(boot) {
  state.boot = boot;
  setDocumentTitle(boot);

  const month = $('month-select');
  if (!month.options.length) {
    boot.months.forEach((m) => {
      const opt = document.createElement('option');
      opt.value = m.number;
      opt.textContent = m.name + ' (' + m.season + ')';
      month.appendChild(opt);
    });
  }
  month.value = boot.month;
  $('year-input').value = boot.year;
  $('seed-input').value = boot.seed;
  $('seasonal-toggle').checked = !!boot.seasonal_inventory;
  showWorldDate(boot);

  const region = $('region-filter');
  if (region.options.length <= 1) {
    boot.regions.forEach((r) => {
      const opt = document.createElement('option');
      opt.value = r;
      opt.textContent = r;
      region.appendChild(opt);
    });
  }

  const cat = $('category-filter');
  if (cat.options.length <= 1) {
    boot.categories.forEach((c) => {
      const opt = document.createElement('option');
      opt.value = c;
      opt.textContent = c;
      cat.appendChild(opt);
    });
  }

  renderSidebar();
}

// ---------------------------------------------------------------------------
// Settlement sidebar
// ---------------------------------------------------------------------------

function renderSidebar() {
  const query = $('settlement-search').value.trim().toLowerCase();
  const region = $('region-filter').value;
  const box = $('settlement-list');

  const matches = state.boot.settlements.filter((s) => {
    if (region && s.region !== region) return false;
    if (!query) return true;
    return s.name.toLowerCase().includes(query) || s.region.toLowerCase().includes(query);
  });

  if (!matches.length) {
    box.innerHTML = '<p class="muted">No settlements match.</p>';
    return;
  }

  let html = '';
  let current = null;
  const events = state.boot.events || [];
  function locationEvents(settlement) {
    return events.filter((event) => {
      const settlements = event.settlements || [];
      const zones = event.zones || [];
      const regions = event.regions || [];
      return (!settlements.length && !zones.length && !regions.length)
        || settlements.includes(settlement.id)
        || zones.includes(settlement.zone)
        || regions.includes(settlement.region);
    });
  }
  matches.forEach((s) => {
    if (s.region !== current) {
      current = s.region;
      html += '<div class="region-head">' + esc(current) + '</div>';
    }
    const flags = (s.port ? ' &#9875;&#65038;' : '') + (s.underdark ? ' &#9660;' : '');
    const locationEventsForSettlement = locationEvents(s);
    const eventHtml = locationEventsForSettlement.length
      ? '<div class="settlement-events">' + locationEventsForSettlement.map((event) =>
        '<span class="settlement-event" title="' + esc(event.description || event.name) + '">' + esc(event.name) + '</span>'
      ).join('') + '</div>' : '';
    html += '<div class="settlement' + (s.id === state.settlementId ? ' active' : '') +
      '" data-id="' + esc(s.id) + '" title="' + esc(s.size + ', population ' +
      s.population.toLocaleString()) + '">' +
      '<span>' + esc(s.name) + flags + '</span>' +
      '<span class="settlement-meta">' + esc(s.size) + '</span>' + eventHtml + '</div>';
  });
  box.innerHTML = html;

  box.querySelectorAll('.settlement').forEach((el) => {
    el.addEventListener('click', () => selectSettlement(el.dataset.id));
  });
}

function selectSettlement(id) {
  state.settlementId = id;
  state.selected = null;
  renderSidebar();
  loadMarket();
}

// ---------------------------------------------------------------------------
// The board
// ---------------------------------------------------------------------------

function showError(err) {
  const status = $('board-status');
  status.className = 'status error';
  status.textContent = String(err.message || err);
  $('row-count').textContent = 'Prices unavailable';
}

function setRowCount(text) {
  $('row-count').textContent = text;
}

async function loadMarket() {
  if (!state.settlementId) return;
  const token = ++state.requestToken;
  const status = $('board-status');
  const id = progressId();
  stopProgress();
  status.className = 'status';
  setRowCount('Loading prices...');
  status.innerHTML = marketProgress({ status: 'starting' });
  state.progressTimer = window.setInterval(async () => {
    if (token !== state.requestToken) return;
    try {
      const progress = await getJSON('/api/progress', { id });
      if (token === state.requestToken && progress.status !== 'unknown') {
        status.innerHTML = marketProgress(progress);
      }
    } catch (_ignored) { /* progress is auxiliary; the market request owns errors */ }
  }, 350);
  try {
    const report = await getJSON('/api/market', {
      settlement: state.settlementId,
      progress: id,
      simple: $('simple-price-mode').checked ? '1' : '',
    });
    if (token !== state.requestToken) return;
    stopProgress();
    state.report = report;
    state.rows = report.prices;
    status.textContent = '';
    renderMarketHeader();
    renderTable();
    if (state.selected) renderDetail(state.selected);
  } catch (err) {
    stopProgress();
    if (token === state.requestToken) showError(err);
  }
}

function renderMarketHeader() {
  const r = state.report;
  const link = $('history-link');
  if (link && state.settlementId) {
    link.href = 'location.html?settlement=' + encodeURIComponent(state.settlementId);
  }
  const facts = [
    r.region,
    r.size,
    'population ' + r.population.toLocaleString(),
    'tariff ' + (r.tariff * 100).toFixed(0) + '%',
    'wealth x' + r.wealth.toFixed(2),
  ].join(' &middot; ');

  const tags = (r.traits || []).map((t) => '<span class="tag">' + esc(t) + '</span>').join('') +
    (r.events || []).map((e) => '<span class="tag warn">' + esc(e) + '</span>').join('');
  const settlement = (state.boot.settlements || []).find((item) => item.id === state.settlementId);
  const locationEvents = (state.boot.events || []).filter((event) => {
    if (!settlement) return false;
    const settlements = event.settlements || [];
    const zones = event.zones || [];
    const regions = event.regions || [];
    return (!settlements.length && !zones.length && !regions.length)
      || settlements.includes(settlement.id)
      || zones.includes(settlement.zone)
      || regions.includes(settlement.region);
  });
  const eventPanel = locationEvents.length
    ? '<section class="location-events-panel"><h3>Happening here</h3>' + locationEvents.map((event) =>
      '<article><strong>' + esc(event.name) + '</strong><p class="location-event-narrative">' + esc(event.description || 'No narrative recorded.') + '</p></article>'
    ).join('') + '</section>' : '';

  $('market-header').innerHTML =
    '<h2>' + esc(r.settlement) + '</h2>' +
    '<div class="facts">' + facts + '</div>' +
    (r.ruler ? '<div class="facts">Ruled by ' + esc(r.ruler) + '</div>' : '') +
    (r.description ? '<p class="desc">' + esc(r.description) + '</p>' : '') +
    (tags ? '<div class="tags">' + tags + '</div>' : '') + eventPanel;
}

function visibleRows() {
  const query = $('commodity-search').value.trim().toLowerCase();
  const category = $('category-filter').value;
  const availableOnly = $('available-only').checked;
  const localOnly = $('only-local').checked;

  let rows = state.rows.filter((q) => {
    if (category && q.category !== category) return false;
    if (availableOnly && (!(Number(q.stock) > 0) || q.availability === 'unavailable')) return false;
    if (localOnly && q.source) return false;
    if (!query) return true;
    return q.commodity_name.toLowerCase().includes(query) ||
      q.category.toLowerCase().includes(query);
  });

  const { key, dir } = state.sort;
  rows = rows.slice().sort((a, b) => {
    let x = a[key];
    let y = b[key];
    if (x === null || x === undefined) x = typeof y === 'number' ? -Infinity : '';
    if (y === null || y === undefined) y = typeof x === 'number' ? -Infinity : '';
    if (typeof x === 'number' && typeof y === 'number') return (x - y) * dir;
    return String(x).localeCompare(String(y)) * dir;
  });
  return rows;
}

function renderTable() {
  const rows = visibleRows();
  setRowCount(rows.length + ' of ' + state.rows.length + ' goods');

  document.querySelectorAll('#price-table thead th').forEach((th) => {
    th.classList.toggle('sorted', th.dataset.sort === state.sort.key);
  });

  $('price-body').innerHTML = rows.map((q) => {
    const cls = q.multiplier < 0.95 ? 'cheap' : (q.multiplier > 1.25 ? 'dear' : '');
    return '<tr data-id="' + esc(q.commodity) + '"' +
      (state.selected === q.commodity ? ' class="active"' : '') + '>' +
      '<td>' + esc(q.commodity_name) + '</td>' +
      '<td class="muted">' + esc(q.category) + '</td>' +
      '<td class="muted">' + esc(q.production_type) + '</td>' +
      '<td class="muted">' + esc(q.unit) + '</td>' +
      '<td class="num muted">' + coin(q.base_price) + '</td>' +
      '<td class="num">' + coin(q.price) + '</td>' +
      '<td class="num muted">' + coin(q.buy_price) + '</td>' +
      '<td class="num">' + quoteMarkup(q.merchant_markup_pct) + '</td>' +
      '<td class="num ' + cls + '">x' + q.multiplier.toFixed(2) + '</td>' +
      '<td>' + esc(q.availability) + '</td>' +
      '<td class="num muted">' + q.stock.toLocaleString() + '</td>' +
      '<td class="num" title="' + esc(seasonalFreeBasis(q)) + '">' +
        quoteQuantity(q.uncommitted_stock) + '</td>' +
      '<td class="num muted">' + q.demand_per_day.toLocaleString(undefined, {
        maximumFractionDigits: 2,
      }) + '</td>' +
      '<td class="' + (q.source ? 'imported' : 'muted') + '">' +
      esc(sourceSummary(q)) + '</td></tr>';
  }).join('');

  document.querySelectorAll('#price-body tr').forEach((tr) => {
    tr.addEventListener('click', () => {
      state.selected = tr.dataset.id;
      renderTable();
      renderDetail(state.selected);
    });
  });
}

// ---------------------------------------------------------------------------
// Detail panel
// ---------------------------------------------------------------------------

function sparkline(series) {
  if (!series.length) return '';
  const prices = series.map((p) => p.price);
  const lo = Math.min.apply(null, prices);
  const hi = Math.max.apply(null, prices);
  const span = (hi - lo) || 1;
  const w = 300;
  const h = 90;
  const pad = 8;
  const step = series.length > 1 ? (w - pad * 2) / (series.length - 1) : 0;

  const points = series.map((p, i) => {
    const x = pad + i * step;
    const y = h - pad - ((p.price - lo) / span) * (h - pad * 2);
    return x.toFixed(1) + ',' + y.toFixed(1);
  }).join(' ');

  const dots = series.map((p, i) => {
    const x = pad + i * step;
    const y = h - pad - ((p.price - lo) / span) * (h - pad * 2);
    return '<circle cx="' + x.toFixed(1) + '" cy="' + y.toFixed(1) + '" r="2" fill="#000000">' +
      '<title>' + esc(p.month + ': ' + coin(p.price)) + '</title></circle>';
  }).join('');

  return '<svg class="spark" viewBox="0 0 ' + w + ' ' + h + '" preserveAspectRatio="none">' +
    '<polyline fill="none" stroke="#000000" stroke-width="1.5" points="' + points + '"/>' +
    dots + '</svg>';
}

async function renderDetail(commodityId) {
  const panel = $('detail');
  const quote = state.rows.find((q) => q.commodity === commodityId);
  if (!quote) return;

  const commodity = state.boot.commodities.find((row) => row.id === commodityId) || {};
  const bomRows = Object.entries(commodity.bom || {}).map(([componentId, quantity]) => {
    const component = state.boot.commodities.find((row) => row.id === componentId) || {
      name: componentId,
      unit: 'unit',
    };
    return '<tr><td>' + esc(component.name) + '</td>' +
      '<td class="num">' + quantity.toLocaleString(undefined, { maximumFractionDigits: 4 }) +
      '</td><td class="muted">' + esc(component.unit) + '</td></tr>';
  }).join('');

  const qualityRows = (quote.quality_offers || []).map((offer) =>
    '<tr><td>' + esc(offer.quality) + '</td>' +
    '<td class="num">' + coin(offer.price) + '</td>' +
    '<td class="num">' + coin(offer.buy_price) + '</td>' +
    '<td class="num">' + quoteMarkup(offer.merchant_markup_pct) + '</td>' +
    '<td>' + esc(offer.availability) + '</td>' +
    '<td class="num muted">' + offer.stock.toLocaleString() + '</td>' +
    '<td class="num">' + quoteQuantity(offer.uncommitted_stock) + '</td></tr>'
  ).join('');

  panel.innerHTML = '<h3>' + esc(quote.commodity_name) + '</h3>' +
    '<div class="muted">' + esc(quote.category) + ' &middot; ' + esc(quote.production_type) + ' &middot; per ' + esc(quote.unit) + '</div>' +
    '<div class="kv">' +
    '<div>Buy from merchant</div><div>' + coin(quote.price) + '</div>' +
    '<div>Sell to merchant</div><div>' + coin(quote.buy_price) + '</div>' +
    '<div>Merchant markup</div><div>' + quoteMarkup(quote.merchant_markup_pct) + '</div>' +
    '<div>Uncommitted / day</div><div>' + quoteQuantity(quote.uncommitted_supply_per_day) + '</div>' +
    '<div>Uncommitted stock</div><div>' + quoteQuantity(quote.uncommitted_stock) +
      (seasonalEnabled(quote) ? '' : ' / ' + quoteQuantity(quote.stock_horizon_days) + ' days') + '</div>' +
    '<div>Base price</div><div>' + coin(quote.base_price) + '</div>' +
    '<div>Multiplier</div><div>x' + quote.multiplier.toFixed(2) + '</div>' +
    '<div>Availability</div><div>' + esc(quote.availability) + '</div>' +
    '<div>Modeled stock</div><div>' + quote.stock.toLocaleString() + '</div>' +
    (quote.production_per_day > 0
      ? '<div>Local production / day</div><div>' +
        quote.production_per_day.toLocaleString(undefined, { maximumFractionDigits: 2 }) +
        ' ' + esc(quote.unit) + '</div>'
      : '') +
    '<div>Demand / day</div><div>' +
      quote.demand_per_day.toLocaleString(undefined, { maximumFractionDigits: 2 }) +
      ' ' + esc(quote.unit) + '</div>' +
    '<div>Supply index</div><div>' + quote.supply_index.toFixed(2) + '</div>' +
    '<div>Demand index</div><div>' + quote.demand_index.toFixed(2) + '</div>' +
    '<div>Supply</div><div>' + esc(sourceSummary(quote)) + '</div>' +
    '</div><p class="muted">' + esc(seasonalStockBasis(quote)) + ' ' + esc(seasonalFreeBasis(quote)) +
    '</p>' + seasonalPanel(quote) + sourceBreakdown(quote) +
    ((quote.notes && quote.notes.length)
      ? '<p class="desc">' + esc(quote.notes.join('; ')) + '</p>' : '') +
    '<p><a href="product.html?commodity=' + encodeURIComponent(quote.commodity) +
      '&settlement=' + encodeURIComponent(quote.settlement) + '">Open full product detail</a></p>' +
    (bomRows
      ? '<h4>Crafting inputs per ' + esc(quote.unit) + '</h4>' +
        '<table><thead><tr><th>Component</th><th class="num">Quantity</th>' +
        '<th>Unit</th></tr></thead><tbody>' + bomRows + '</tbody></table>'
      : '') +
    '<h4>Quality on offer</h4>' +
    '<table><thead><tr><th>Grade</th><th class="num">Buy from merchant</th>' +
    '<th class="num">Sell to merchant</th><th class="num">Markup</th>' +
    '<th>Availability</th><th class="num">Stock</th><th class="num">Uncommitted</th></tr></thead>' +
    '<tbody>' + qualityRows + '</tbody></table>' +
    '<p class="muted">Markup is (buy price / sell-to-merchant price - 1). It is not net profit. ' +
      'Grade quantities share one uncommitted market pool and follow its modeled quality mix.</p>' +
    '<h4>Consumer buy price through the year</h4>' +
    '<button id="load-detail-history" type="button" aria-describedby="detail-history-warning">Load twelve-month price forecast</button>' +
    '<p id="detail-history-warning" class="muted">Optional: calculates future monthly prices. ' +
      'Seasonal inventory may need many daily allocations; the forecast runs in the background. ' +
      'The production and demand curves above do not require this forecast.</p>' +
    '<div id="detail-history" class="muted" role="status"></div>' +
    '<h4>Cheapest markets in the Realms</h4><div id="detail-compare" class="muted">loading...</div>';

  const token = state.requestToken;
  const settlementId = state.settlementId;
  const historyBox = $('detail-history');
  const historyButton = $('load-detail-history');
  const historyIsCurrent = () => token === state.requestToken &&
    state.selected === commodityId && $('detail-history') === historyBox;
  historyButton.addEventListener('click', async () => {
    if (historyButton.disabled || !historyIsCurrent()) return;
    historyButton.disabled = true;
    historyButton.textContent = 'Computing twelve-month price forecast...';
    historyBox.textContent = 'Calculating monthly prices; other API requests may wait.';
    try {
      const hist = await getJSON('/api/history', {
        settlement: settlementId, commodity: commodityId, months: 12,
      });
      if (!historyIsCurrent()) return;
      historyBox.innerHTML = sparkline(hist.series) +
        '<div class="muted" style="font-size:11px">low ' + coin(hist.low) +
        ' &middot; avg ' + coin(hist.average) + ' &middot; high ' + coin(hist.high) + '</div>';
      historyButton.textContent = 'Twelve-month price forecast loaded';
    } catch (err) {
      if (!historyIsCurrent()) return;
      historyBox.textContent = String(err.message || err);
      historyButton.disabled = false;
      historyButton.textContent = 'Retry twelve-month price forecast';
    }
  });

  const compareBox = $('detail-compare');
  try {
    const cmp = await getJSON('/api/compare', { commodity: commodityId, limit: 12 });
    if (token !== state.requestToken || state.selected !== commodityId ||
        $('detail-compare') !== compareBox) return;
    compareBox.innerHTML = '<table class="mini"><thead><tr><th>Market</th>' +
      '<th>Buy from merchant</th><th>Sell to merchant</th><th>Uncommitted</th></tr></thead><tbody>' + cmp.markets.map((m) =>
      '<tr class="' + (m.settlement === state.report.settlement ? 'here' : '') + '">' +
      '<td>' + esc(m.settlement) + '</td>' +
      '<td>' + coin(m.price) + '</td><td>' + coin(m.buy_price) + '</td>' +
      '<td>' + quoteQuantity(m.uncommitted_stock) + '</td></tr>').join('') + '</tbody></table>';
  } catch (err) {
    if (token === state.requestToken && state.selected === commodityId &&
        $('detail-compare') === compareBox) compareBox.textContent = String(err.message || err);
  }
}

// ---------------------------------------------------------------------------
// Wiring
// ---------------------------------------------------------------------------

function wire() {
  $('settlement-search').addEventListener('input', renderSidebar);
  $('region-filter').addEventListener('change', renderSidebar);

  ['commodity-search', 'category-filter', 'available-only', 'only-local'].forEach((id) => {
    const el = $(id);
    el.addEventListener(el.tagName === 'INPUT' && el.type !== 'checkbox' ? 'input' : 'change',
      () => { if (state.report) renderTable(); });
  });

  $('simple-price-mode').addEventListener('change', () => {
    if (state.settlementId) loadMarket();
  });

  $('seasonal-toggle').addEventListener('change', async () => {
    try {
      const payload = { seasonal_inventory: $('seasonal-toggle').checked };
      applyBoot(await postJSON('/api/world', payload));
      await loadMarket();
    } catch (err) { showError(err); }
  });

  document.querySelectorAll('#price-table thead th').forEach((th) => {
    th.addEventListener('click', () => {
      const key = th.dataset.sort;
      if (!key) return;
      if (state.sort.key === key) {
        state.sort.dir *= -1;
      } else {
        state.sort.key = key;
        state.sort.dir = (key === 'price' || key === 'multiplier' ||
          key === 'stock' || key === 'demand_per_day' || key === 'base_price' ||
          key === 'buy_price' || key === 'merchant_markup_pct' || key === 'uncommitted_stock') ? -1 : 1;
      }
      if (state.report) renderTable();
    });
  });

  $('apply-world').addEventListener('click', async () => {
    // Only send fields the user actually filled in, so a blank box does not
    // silently reset the year or seed to zero.
    const payload = { month: Number($('month-select').value) };
    const year = $('year-input').value.trim();
    const seed = $('seed-input').value.trim();
    if (year !== '') payload.year = Number(year);
    if (seed !== '') payload.seed = Number(seed);
    try {
      applyBoot(await postJSON('/api/world', payload));
      await loadMarket();
    } catch (err) { showError(err); }
  });

}

async function start() {
  wire();
  try {
    const boot = await getJSON('/api/bootstrap', {});
    applyBoot(boot);
    const first = boot.settlements.find((s) => s.name === 'Waterdeep') || boot.settlements[0];
    if (first) selectSettlement(first.id);
  } catch (err) {
    showError(err);
  }
}

start();
"""

WORLD_DATE_JS = """
function showWorldDate(boot) {
  const label = boot.follows_real_date ? 'Today' : 'Date';
  document.querySelectorAll('[data-world-date]').forEach((element) => {
    element.innerHTML = '<span class="date-line date-line-day">' + label + ': ' + boot.date + '</span>'
      + '<span class="date-line date-line-season">' + boot.season + '</span>'
      + '<span class="date-line date-line-moon">' + (boot.moon_phase ? '☾ ' + boot.moon_phase : 'Moon phase unavailable') + '</span>';
    element.title = boot.follows_real_date
      ? 'Live date anchored at 1 Hammer 1492 DR = 1 January 2026 UTC'
      : 'Manually selected simulation date';
  });
}
"""

ASSETS: Dict[str, Tuple[str, str]] = {
    "index.html": (INDEX_HTML, "text/html; charset=utf-8"),
    "app.css": (APP_CSS, "text/css; charset=utf-8"),
    "app.js": (APP_JS, "application/javascript; charset=utf-8"),
    "date.js": (WORLD_DATE_JS, "application/javascript; charset=utf-8"),
}
