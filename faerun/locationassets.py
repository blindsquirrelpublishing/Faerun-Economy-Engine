"""The location detail screen: one settlement, seven years, one price line.

Like `webassets` and `mapassets`, the page is kept as Python strings so the UI
travels with the package.  The same two rules apply to every string in here:
no backslash may appear anywhere (which rules out CSS unicode escapes and JS
regex literals), and the three-quote sequence must never occur.  Non-ASCII is
written as HTML entities.
"""

from __future__ import annotations

from typing import Dict, Tuple
from .webassets import SEASONAL_JS

LOCATION_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Faerun Location Detail</title>
<link rel="stylesheet" href="app.css">
<link rel="stylesheet" href="location.css">
</head>
<body class="location-page">

<header class="topbar">
  <div class="brand">
    <span class="mark">&#9201;&#65038;</span>
    <div>
      <h1 id="place-name">Location Detail</h1>
      <p class="tagline" id="place-blurb">Seven years of history, and what it did to the prices.</p>
    </div>
  </div>

  <div class="worldbar">
    <label>Settlement
      <input id="place-search" list="place-list" placeholder="Waterdeep" autocomplete="off">
      <datalist id="place-list"></datalist>
    </label>
    <button id="go" class="primary" type="button">Open</button>
    <span class="pill" data-world-date>&#8230;</span>
    <a class="navlink" href="index.html">&#8592; Commodity board</a>
    <a class="navlink" href="map.html">World map &#8594;</a>
    <a class="navlink" href="planner.html">Route planner</a>
    <a class="navlink" href="trade.html">Merchant guild &amp; POs</a>
    <a id="location-generator-link" class="navlink" href="location-generator.html" hidden>Generate buildings (separate scenario)</a>
  </div>
</header>

<section class="scrubber">
  <div class="scrub-head">
    <div>
      <span class="scrub-label" id="scrub-date">&#8212;</span>
      <span class="pill" id="scrub-season"></span>
      <span class="pill" id="scrub-index"></span>
    </div>
    <div class="scrub-buttons">
      <button id="step-back" type="button" class="ghost" title="Previous month; loads one monthly market" aria-label="Previous month" disabled>&#8592;</button>
      <button id="step-fwd" type="button" class="ghost" title="Next month; loads one monthly market" aria-label="Next month" disabled>&#8594;</button>
      <button id="jump-today" type="button" class="ghost" disabled>Today</button>
      <button id="jump-worst" type="button" class="ghost" title="Requires seven-year price history" disabled>Dearest month</button>
      <button id="jump-best" type="button" class="ghost" title="Requires seven-year price history" disabled>Cheapest month</button>
    </div>
  </div>
  <button id="load-history" type="button" class="ghost" aria-describedby="history-warning" disabled>Load seven-year price history</button>
  <p id="history-warning" class="history-warning">Optional: computes 84 monthly balances and may take several minutes.
    Other API requests may wait while history is computed. Previous/next and Today load only one selected month.</p>
  <div id="history-chart" hidden>
    <input id="scrub" type="range" min="0" max="1" step="1" value="0" aria-label="History month" disabled>
    <canvas id="chart" height="240" aria-label="Historical basket price index"></canvas>
    <div class="chart-key"><span class="basket-key">Basket price index</span><span class="events-key">Active events</span></div>
  </div>
  <p id="timeline-status" class="status" role="status" aria-live="polite"></p>
</section>

<main class="location-main">
  <aside class="sidebar">
    <h2>Happening now</h2>
    <div id="active-events" class="event-cards"></div>

    <h2>Analysis</h2>
    <div id="analysis" class="analysis"></div>

    <h2>The whole chronicle</h2>
    <div id="all-events" class="chronicle-list"></div>
  </aside>

  <section class="content">
    <section class="requirements-board" id="requirements-board" aria-labelledby="requirements-title" aria-busy="true">
      <div class="requirements-heading">
        <div>
          <h2 id="requirements-title">Settlement requirements</h2>
          <p class="muted">Estimated people, producers and daily material flows &mdash; not canonical census or named businesses.</p>
        </div>
        <button id="requirements-download" type="button" class="ghost" disabled>Download requirements JSON</button>
      </div>
      <p id="requirements-status" class="status" role="status" aria-live="polite">Loading requirements...</p>
      <div id="requirements-content" hidden>
        <p id="requirements-model" class="muted"></p>
        <div id="requirements-profile" class="requirements-cards"></div>
        <details class="requirements-notes">
          <summary>Estimation assumptions and provenance</summary>
          <div id="requirements-assumptions"></div>
        </details>
        <details class="requirements-notes">
          <summary>Labor-based establishments and workers (not named businesses)</summary>
          <div id="requirements-establishments"></div>
        </details>
        <details id="requirements-output-section" class="requirements-notes" hidden>
          <summary>Output-equivalent facilities needed (not additional people)</summary>
          <p>Facilities required at planned output and fractional active equivalents at actual output.
            These are not additive to labor-based establishment counts and do not imply new additional workers.
            Rates follow the selected material balance. Throughput is per facility per day;
            quantities use each row's catalog unit.</p>
          <div id="requirements-output"></div>
        </details>
        <details id="requirements-defense-section" class="requirements-notes" hidden>
          <summary>Theoretical defense equipment requirements</summary>
          <p>Standing-army and militia stocks are theoretical equipment requirements, not proven owned inventory.
            Daily replacement is annual replacement divided by 365; annual growth additions are shown separately.</p>
          <div id="requirements-defense"></div>
        </details>
        <details id="requirements-resources-section" class="requirements-notes" hidden>
          <summary>Inferred hinterland acreage, stocks and fishing labor</summary>
          <p>Local hinterland resources are inferred, not surveyed land or verified livestock inventories.
            Acreage describes a conservative local footprint only; actual output may also include established industries
            and source-district baseline calibration, not census acreage.
            Potential fishing labor is separate from allocated fishers. Missing values mean no estimate was supplied.</p>
          <div id="requirements-resources"></div>
        </details>
        <section id="requirements-water-section" hidden aria-labelledby="requirements-water-title">
          <h3 id="requirements-water-title">Domestic water: sources, access and essential needs</h3>
          <div id="requirements-water"></div>
        </section>
        <section id="requirements-services-section" hidden aria-labelledby="requirements-services-title">
          <h3 id="requirements-services-title">Municipal staffing references</h3>
          <p class="muted">These are staffing reference indicators, not total natural water availability or additional service output.
            Rates use the service unit shown per day; no commodity imports are inferred.</p>
          <div id="requirements-services"></div>
        </section>
        <details id="requirements-industries-section" class="requirements-notes service-economy" hidden>
          <summary>Modeled service sectors: demand, capacity and delivery</summary>
          <div id="requirements-industries"></div>
        </details>
        <details id="requirements-visitors-section" class="requirements-notes service-economy" hidden>
          <summary>Tourism and travel: visitors, accommodation and local demand</summary>
          <div id="requirements-visitors"></div>
        </details>
        <details id="requirements-accounts-section" class="requirements-notes service-economy" hidden>
          <summary>Estimated local accounts: gross local product and external balances</summary>
          <div id="requirements-accounts"></div>
        </details>
        <details id="requirements-economy-assumptions-section" class="requirements-notes" hidden>
          <summary>Service economy, tourism and accounting assumptions</summary>
          <div id="requirements-economy-assumptions"></div>
        </details>
        <h3>Daily material balance</h3>
        <div id="requirements-summary" class="requirements-cards"></div>
        <p id="requirements-units" class="muted">Material rates use each commodity's catalog trade unit per day, not pounds.
          Planned capacity is the scheduled production plan, not maximum idle factory capacity.
          Import need is the pre-trade gap; allocated imports are delivered supply; still unmet is the remaining shortfall.
          Surplus is pre-trade exportable output; closing stock is what remains after trade and consumption.
          With seasonal inventory enabled, stored quantities carry forward with losses and protected reserves;
          inspect a material for its local 12-month curves, opening/closing stocks and storage policy.
          Uncommitted quantities additionally protect all planned final and processing demand and subtract allocated exports.
          Total minus final demand is required processing input, not spare stock. Stock estimates are not bookings.</p>
        <div class="requirements-filters">
          <label for="requirements-search">Find material, diet or sector
            <input id="requirements-search" type="search" placeholder="Grain, exotic, construction..." autocomplete="off">
          </label>
          <label for="requirements-filter">Material status
            <select id="requirements-filter">
              <option value="all">All materials</option>
              <option value="imports">Import needs (before trade)</option>
              <option value="unmet">Still unmet (after trade)</option>
              <option value="surplus">Exportable surplus (before trade)</option>
              <option value="uncommitted">Uncommitted supply (after all reservations)</option>
            </select>
          </label>
          <span id="requirements-count" role="status" aria-live="polite"></span>
        </div>
        <div class="requirements-scroll" role="region" tabindex="0" aria-label="Daily material requirements" aria-describedby="requirements-units">
          <table class="requirements-table" id="requirements-table">
            <caption>Demand, local production and trade allocation &mdash; rates in the unit shown for each material</caption>
            <thead><tr>
              <th scope="col">Material / unit per day</th>
              <th scope="col" class="num">Final demand</th>
              <th scope="col" class="num">Processing demand</th>
              <th scope="col" class="num">Total demand</th>
              <th scope="col" class="num">Planned capacity/day</th>
              <th scope="col" class="num">Actual output</th>
              <th scope="col" class="num">Import need<br>(pre-trade)</th>
              <th scope="col" class="num">Allocated imports</th>
              <th scope="col" class="num">Still unmet</th>
              <th scope="col" class="num">Exportable surplus<br>(pre-trade)</th>
              <th scope="col" class="num">Uncommitted/day</th>
              <th scope="col" class="num">Uncommitted stock<br>(estimate)</th>
            </tr></thead>
            <tbody></tbody>
          </table>
        </div>
      </div>
    </section>
    <div class="toolbar">
      <h2 id="table-title">Prices</h2>
      <label>Category <select id="category-filter"><option value="">All</option></select></label>
      <label class="check"><input id="only-moved" type="checkbox"> Only goods the events moved</label>
      <span class="pill" id="living-standard"></span>
      <span class="pill" id="event-cost"></span>
    </div>
    <div id="status" class="status" role="status" aria-live="polite"></div>
    <section class="business-board">
      <h2>Local traders and businesses</h2>
      <p class="muted">Named businesses and offers from the current world market, not the selected historical month.
        Buy from merchant is what you pay; sell to merchant is what you receive. Markup is the gross quoted resale spread over the merchant's purchase price, not net profit.</p>
      <p id="historical-directory-link" hidden><a href="waterdeep.html#historical-directory">Volo's historical Waterdeep businesses &amp; people</a> &mdash; a separate source-linked directory, not live stock or current residents.</p>
      <div id="businesses" class="businesses"></div>
    </section>
    <p class="muted">Prices below are gp per trade unit. Uncommitted stock is an estimate after all modeled needs and export reservations.</p>
    <div class="price-scroll"><table class="prices" id="price-table">
      <thead>
        <tr>
          <th>Commodity</th>
          <th>Category</th>
          <th>Type</th>
          <th class="num">Baseline / day</th>
          <th class="num">Market demand / day</th>
          <th class="num">Buy from merchant</th>
          <th class="num">Sell to merchant</th>
          <th class="num">Merchant markup</th>
          <th class="num">Uncommitted stock</th>
          <th class="num">x base</th>
          <th class="num">Buy without events</th>
          <th class="num">Event effect</th>
          <th>Availability</th>
          <th>Source</th>
        </tr>
      </thead>
      <tbody></tbody>
    </table></div>
  </section>
</main>

<script src="date.js"></script>
<script src="location.js"></script>
</body>
</html>
"""


LOCATION_CSS = """/* Location detail screen. Inherits the palette from app.css. */

.location-page main.location-main {
  display: grid;
  grid-template-columns: 320px 1fr;
  gap: 24px;
  align-items: start;
  padding: 0 24px 48px;
}

.location-main > .content { min-width: 0; }

.scrubber {
  padding: 16px 24px 8px;
  border-bottom: 1px solid var(--line);
}

.scrub-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 16px;
  flex-wrap: wrap;
  margin-bottom: 8px;
}

.scrub-label {
  font-size: 20px;
  font-weight: 600;
  letter-spacing: 0.01em;
}

.scrub-buttons { display: flex; gap: 6px; flex-wrap: wrap; }
.scrubber [hidden] { display: none; }
.history-warning { margin: 8px 0 0; font-size: 12px; line-height: 1.6; color: var(--muted); }

#scrub {
  width: 100%;
  margin: 4px 0 12px;
  accent-color: var(--ink);
}

#chart {
  width: 100%;
  display: block;
  border: 1px solid var(--line);
  background: var(--panel);
}

.chart-key { margin: 8px 0 4px; font-size: 12px; }

.event-cards { display: flex; flex-direction: column; gap: 10px; }

.event-card {
  border: 1px solid var(--line);
  padding: 10px 12px;
  background: var(--panel-2);
}

.event-card h3 {
  margin: 0 0 4px;
  font-size: 14px;
  letter-spacing: 0.01em;
}

.event-card p { margin: 0 0 6px; font-size: 12px; color: var(--muted); }

.event-mods {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  font-size: 11px;
  text-transform: uppercase;
  letter-spacing: 0.06em;
}

.event-mods span {
  border: 1px solid var(--line);
  padding: 1px 6px;
}

.analysis { font-size: 13px; }

.analysis dl {
  display: grid;
  grid-template-columns: 1fr auto;
  gap: 4px 12px;
  margin: 0 0 12px;
}

.analysis dt { color: var(--muted); }
.analysis dd { margin: 0; text-align: right; font-variant-numeric: tabular-nums; }

.impact { list-style: none; margin: 0; padding: 0; }

.impact li {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  padding: 4px 0;
  border-bottom: 1px solid var(--line-soft);
  font-size: 12px;
}

.impact .amount { font-variant-numeric: tabular-nums; white-space: nowrap; }

.chronicle-list { font-size: 12px; max-height: 340px; overflow-y: auto; }

.chronicle-list button {
  display: block;
  width: 100%;
  text-align: left;
  background: none;
  border: 0;
  border-bottom: 1px solid var(--line-soft);
  padding: 6px 2px;
  cursor: pointer;
  color: inherit;
  font: inherit;
}

.chronicle-list button:hover { background: var(--panel-2); }
.chronicle-list button.live { border-left: 3px solid var(--ink); padding-left: 8px; }
.chronicle-list .when { display: block; color: var(--muted); font-size: 11px; }

.toolbar {
  display: flex;
  align-items: center;
  gap: 16px;
  flex-wrap: wrap;
  margin-bottom: 8px;
}

.toolbar h2 { margin: 0; }
.toolbar .check { display: flex; align-items: center; gap: 6px; }

table.prices { width: 100%; border-collapse: collapse; font-size: 13px; }
.price-scroll { width: 100%; overflow-x: auto; }
.price-scroll table.prices { min-width: 980px; }
.need-detail { display: block; color: var(--muted); font-size: 10px; white-space: nowrap; }

/* Pending selections clear their old values rather than presenting stale data. */
table.prices.loading tbody { opacity: 0.3; }
table.prices tbody { transition: opacity 120ms linear; }

table.prices th, table.prices td {
  padding: 5px 8px;
  border-bottom: 1px solid var(--line-soft);
  text-align: left;
}

table.prices th {
  border-bottom: 1px solid var(--line);
  font-size: 11px;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: var(--muted);
}

table.prices td.num, table.prices th.num {
  text-align: right;
  font-variant-numeric: tabular-nums;
}

tr.moved td { background: var(--panel-2); }
td.up { font-weight: 600; }
td.down { font-weight: 600; }
td.flat { color: var(--muted); }

.status { margin: 8px 0; color: var(--muted); font-size: 13px; min-height: 18px; }

.business-board { margin: 8px 0 22px; border-top: 2px solid var(--ink); padding-top: 10px; }
.businesses { display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 12px; }
.business { border: 1px solid var(--line); padding: 10px; }
.business h3 { margin: 0 0 3px; font-size: 15px; }
.business p { margin: 4px 0; color: var(--muted); font-size: 12px; }
.business table { width: 100%; border-collapse: collapse; margin-top: 8px; }
.business th, .business td {
  padding: 4px;
  border-top: 1px solid var(--line-soft);
  font-size: 11px;
  text-align: left;
}
.business .num { text-align: right; font-variant-numeric: tabular-nums; }

@media (max-width: 900px) {
  .location-page main.location-main {
    display: block;
    min-height: auto;
    flex: 0 0 auto;
  }
  .location-main > .content { margin-top: 24px; }
}

body.location-page { height: auto; min-height: 100dvh; overflow: auto; background: var(--cp-bg-elevated); }
.location-page .brand h1 { font-size: 25px; overflow-wrap: anywhere; }
.location-page .tagline { display: none; }
.location-page .topbar { align-items: start; }
.location-page main.location-main { grid-template-columns: minmax(240px,21%) minmax(0, 1fr); gap: 32px; padding: 28px clamp(16px,3%,64px) 48px; background: var(--cp-surface); flex: none; min-height: auto; width: 100%; box-sizing: border-box; }
.location-main > .content { min-width: 0; }
.location-main > .sidebar { padding: 0; overflow: visible; background: transparent; display: block; }
.location-main h2 { font-size: 17px; font-weight: 650; letter-spacing: 0; }
.location-main > .sidebar > h2 { padding-top: 20px; margin: 0 0 12px; border-top: 1px solid var(--cp-border); }
.location-main > .sidebar > h2:first-child { padding-top: 0; border: 0; }
.scrubber { padding: 24px clamp(16px,3%,64px) 20px; background: linear-gradient(90deg,var(--cp-surface-soft),var(--cp-surface)); flex: none; border-bottom: 1px solid var(--cp-border); }
.scrub-label { font-size: 23px; letter-spacing: 0; }
.scrub-head > div:first-child { display: flex; flex-wrap: wrap; align-items: center; gap: 8px; }
#scrub { accent-color: var(--cp-accent); cursor: pointer; }
#chart { height: 240px; border: 0; background: transparent; }
.chart-key { display: flex; gap: 20px; margin: 10px 0 0 48px; color: var(--cp-text-muted); font-size: 11px; }
.chart-key span { display: inline-flex; align-items: center; gap: 7px; }
.chart-key span::before { content: ''; display: inline-block; width: 18px; height: 3px; background: var(--cp-accent); }
.chart-key .events-key::before { height: 10px; background: var(--cp-highlight); border: 1px solid var(--cp-border); }
.event-card { border: 1px solid var(--cp-border); border-left: 3px solid var(--cp-accent); border-radius: 6px; background: var(--cp-bg-elevated); padding: 14px; }
.event-card h3 { letter-spacing: 0; line-height: 1.45; }
.event-card p { line-height: 1.65; }
.event-mods { letter-spacing: 0; }
.event-mods span { background: var(--cp-surface); border-radius: 4px; padding: 3px 6px; }
.analysis dl { padding: 12px 0; gap: 10px; }
.analysis dd { font-weight: 600; }
.impact li { padding: 9px 0; }
.chronicle-list { max-height: 460px; margin-bottom: 20px; }
.chronicle-list button { padding: 12px 10px; border-left: 2px solid var(--cp-border); line-height: 1.6; }
.chronicle-list button.live { border-left-color: var(--cp-accent); background: var(--cp-accent-soft); padding-left: 10px; }
.chronicle-list button:hover { background: var(--cp-accent-soft); }
.toolbar { padding: 0 0 16px; gap: 12px; border-bottom: 1px solid var(--cp-border); }
.toolbar h2 { flex: 1 0 100%; font-size: 22px; }
.business-board { border-top: 0; padding: 0; margin: 20px 0 28px; }
.businesses { grid-template-columns: repeat(auto-fit, minmax(min(100%, 290px), 1fr)); gap: 14px; }
.business { min-width: 0; padding: 20px; border-radius: 6px; background: var(--cp-surface-soft); border: 1px solid var(--cp-border); }
.business h3 { font-size: 17px; line-height: 1.4; }
.business p { line-height: 1.6; }
.business details { margin-top: 12px; border-top: 1px solid var(--cp-border); }
.business summary { padding-top: 10px; cursor: pointer; color: var(--cp-accent); font-size: 12px; font-weight: 600; }
.business a, .location-main a { color: var(--cp-link); }
.business table { table-layout: fixed; }
.business th { white-space: normal; letter-spacing: 0; background: transparent; }
.business td { overflow-wrap: anywhere; }
.business .num { white-space: nowrap; }
.price-scroll { max-height: 72dvh; border-block: 1px solid var(--cp-border); }
table.prices th { padding: 12px 8px; letter-spacing: 0; font-size: 10px; background: var(--cp-bg-elevated); }
table.prices td { padding: 10px 8px; }
table.prices td:first-child { font-weight: 600; }
table.prices td.num { white-space: nowrap; }
tr.moved td { background: var(--cp-accent-soft); }
td.up { color: var(--cp-accent); }
.location-page .status:empty { display: none; }
.location-page .worldbar label { flex-wrap: wrap; min-width: 0; }
.location-page #place-search { min-width: 0; max-width: 100%; }
.scrub-head, .scrub-buttons { flex-wrap: wrap; gap: 12px; }
.analysis dd { min-width: 0; overflow-wrap: anywhere; }
.requirements-board { margin-bottom: 32px; padding-bottom: 28px; border-bottom: 2px solid var(--cp-border); }
.requirements-board [hidden] { display: none; }
.requirements-heading { display: flex; justify-content: space-between; align-items: start; gap: 16px; flex-wrap: wrap; }
.requirements-heading h2 { margin: 0; font-size: 22px; }
.requirements-heading p, .requirements-board .muted { font-size: 12px; line-height: 1.65; }
.requirements-heading > div { flex: 1 1 320px; }
.requirements-heading button { white-space: normal; }
.requirements-cards { display: grid; grid-template-columns: repeat(auto-fit, minmax(135px, 1fr)); gap: 10px; margin: 14px 0; }
.requirements-card { margin: 0; padding: 12px; border: 1px solid var(--cp-border); border-radius: 6px; background: var(--cp-surface-soft); min-width: 0; }
.requirements-card dt { color: var(--cp-text-muted); font-size: 11px; line-height: 1.5; }
.requirements-card dd { margin: 5px 0 0; font-size: 18px; font-weight: 650; overflow-wrap: anywhere; font-variant-numeric: tabular-nums; }
.requirements-card small { display: block; color: var(--cp-text-muted); font-size: 10px; font-weight: 400; }
.requirements-notes { margin: 12px 0; padding: 12px; border: 1px solid var(--cp-border); border-radius: 6px; font-size: 12px; line-height: 1.65; }
.requirements-notes summary { cursor: pointer; color: var(--cp-accent); font-weight: 600; }
.requirements-notes pre { white-space: pre-wrap; overflow-wrap: anywhere; font: inherit; }
.requirements-filters { display: flex; align-items: end; gap: 14px; flex-wrap: wrap; margin: 16px 0 12px; }
.requirements-filters label { display: flex; flex-direction: column; align-items: start; gap: 6px; font-size: 12px; min-width: 0; }
.requirements-filters input, .requirements-filters select { max-width: 100%; box-sizing: border-box; }
#requirements-count { color: var(--cp-text-muted); font-size: 12px; }
.requirements-scroll { overflow: auto; max-height: 65dvh; border: 1px solid var(--cp-border); border-radius: 6px; }
.requirements-table { width: 100%; border-collapse: collapse; font-size: 12px; }
#requirements-table { min-width: 1120px; }
.requirements-table caption { text-align: left; padding: 10px; font-size: 11px; color: var(--cp-text-muted); }
.requirements-table th, .requirements-table td { padding: 10px 8px; border-bottom: 1px solid var(--cp-border); text-align: left; vertical-align: top; }
.requirements-table th { font-size: 10px; font-weight: 650; background: var(--cp-bg-elevated); }
#requirements-table > thead > tr > th { position: sticky; top: 0; z-index: 1; }
.requirements-table .num { text-align: right; white-space: nowrap; font-variant-numeric: tabular-nums; }
.requirements-table td:first-child { min-width: 155px; }
.requirements-table small { display: block; color: var(--cp-text-muted); font-size: 10px; }
.requirements-table button { margin-top: 6px; font-size: 11px; }
.requirements-table .material-unmet { font-weight: 700; color: var(--cp-accent); background: var(--cp-accent-soft); }
.material-detail > td { background: var(--cp-surface-soft); padding: 16px; }
.material-detail h4 { margin: 16px 0 8px; font-size: 13px; }
.material-detail p { font-size: 12px; line-height: 1.65; }
.material-detail .requirements-cards { grid-template-columns: repeat(auto-fit, minmax(130px, 1fr)); }
.material-detail .requirements-card dd { font-size: 14px; }
.material-detail-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(310px, 1fr)); gap: 16px; }
.material-detail-grid > div { min-width: 0; }
.requirements-subscroll { overflow-x: auto; }
.requirements-table .requirements-table td:first-child { min-width: 0; }
.requirements-table a:focus-visible, .requirements-board summary:focus-visible, .requirements-scroll:focus-visible, .requirements-subscroll:focus-visible { outline: 2px solid var(--cp-accent); outline-offset: 3px; }
.service-economy { min-width: 0; }
.service-economy h4 { margin: 18px 0 8px; font-size: 13px; }
.service-economy p, .service-economy .service-inputs { overflow-wrap: anywhere; }
.service-economy .requirements-card dd { font-size: 16px; }
#requirements-industries > .requirements-subscroll > table { min-width: 1250px; }
.service-inputs { padding: 4px; }
.service-inputs .requirements-subscroll { max-width: 800px; }
@media (max-width: 900px) {
  .location-page main.location-main { display: flex; flex-direction: column; padding: 20px 16px 32px; gap: 24px; }
  .location-main > .content { order: -1; margin: 0; width: 100%; }
  .location-main > .sidebar { width: 100%; }
  .scrubber { padding: 20px 16px; }
  .scrub-label { font-size: 20px; }
  .location-page .brand h1 { font-size: 24px; }
  .chart-key { margin-left: 0; flex-wrap: wrap; }
}
"""


LOCATION_JS = SEASONAL_JS + """/* Location detail: a timeline scrubber over the chronicle window. */
(function () {
  'use strict';

  var materialEpsilon = 0.000001;
  var generatorLocations = [];

  var state = {
    settlement: null,
    timeline: null,
    detail: null,
    month: null,
    first: 0,
    last: 0,
    today: null,
    onlyMoved: false,
    category: '',
    materialSearch: '',
    materialFilter: 'all',
    openMaterials: new Set()
  };

  var el = {};
  var ids = ['place-name', 'place-blurb', 'place-search', 'place-list', 'go',
             'scrub', 'scrub-date', 'scrub-season', 'scrub-index', 'chart',
             'active-events', 'analysis', 'all-events', 'category-filter',
             'only-moved', 'status', 'price-table', 'table-title', 'event-cost',
             'living-standard',
             'step-back', 'step-fwd', 'jump-today', 'jump-worst', 'jump-best',
             'businesses', 'timeline-status', 'load-history', 'history-chart', 'requirements-board',
             'requirements-content', 'requirements-status', 'requirements-model',
             'requirements-profile', 'requirements-assumptions',
             'requirements-establishments', 'requirements-summary',
             'requirements-output-section', 'requirements-output',
             'requirements-defense-section', 'requirements-defense',
             'requirements-resources-section', 'requirements-resources',
             'requirements-services-section', 'requirements-services',
             'requirements-water-section', 'requirements-water',
             'requirements-industries-section', 'requirements-industries',
             'requirements-visitors-section', 'requirements-visitors',
             'requirements-accounts-section', 'requirements-accounts',
             'requirements-economy-assumptions-section', 'requirements-economy-assumptions',
             'requirements-search', 'requirements-filter', 'requirements-count',
             'requirements-table', 'requirements-download'];
  ids.forEach(function (id) { el[id] = document.getElementById(id); });

  function esc(text) {
    return String(text === null || text === undefined ? '' : text)
      .split('&').join('&amp;')
      .split('<').join('&lt;')
      .split('>').join('&gt;')
      .split('"').join('&quot;');
  }

  function money(value) {
    if (value === null || value === undefined) { return '&#8212;'; }
    if (value >= 100) { return value.toFixed(0); }
    if (value >= 1) { return value.toFixed(2); }
    return value.toFixed(3);
  }

  function pct(value) {
    if (value === null || value === undefined) { return '&#8212;'; }
    var sign = value > 0 ? '+' : '';
    return sign + (value * 100).toFixed(1) + '%';
  }

  function quantity(value) {
    if (value === null || value === undefined) { return '&#8212;'; }
    if (Math.abs(value) < 1e-9) { return '0'; }
    if (value !== 0 && Math.abs(value) > 0 && Math.abs(value) < 0.001) {
      return Number(value).toPrecision(3);
    }
    return Number(value).toLocaleString(undefined, { maximumFractionDigits: 3 });
  }

  function quoteMarkup(value) {
    return Number.isFinite(value) ? value.toFixed(1) + '%' : '&#8212;';
  }

  function quoteMoney(value) {
    if (!Number.isFinite(value)) { return '&#8212;'; }
    return value.toLocaleString(undefined, { minimumFractionDigits: value < 1 ? 3 : 2, maximumFractionDigits: 3 });
  }

  function say(message) {
    el.status.innerHTML = message ? esc(message) : '';
  }

  /* An endpoint this page needs but the server has never heard of means the
     server is an older build that predates the location screen.  That answer
     is plain text, not JSON, so parsing it blind would raise a syntax error
     and hide the real problem behind nonsense. */
  function get(path, signal) {
    return fetch(path, { headers: { 'Accept': 'application/json' }, signal: signal })
      .then(function (response) {
        return response.text().then(function (text) {
          var body = null;
          try { body = JSON.parse(text); } catch (ignored) { body = null; }
          if (!response.ok) {
            if (body && body.error) { throw new Error(body.error); }
            if (response.status === 404) {
              throw new Error(path + ' is not served by this copy of the ' +
                'engine. Stop the server window and run run.ps1 again - the ' +
                'pages are baked in when the server starts.');
            }
            throw new Error('request failed (HTTP ' + response.status + ')');
          }
          if (body === null) {
            throw new Error(path + ' did not return JSON. Restart the server.');
          }
          return body;
        });
      });
  }

  function query(name) {
    var pairs = window.location.search.replace('?', '').split('&');
    for (var i = 0; i < pairs.length; i += 1) {
      var bits = pairs[i].split('=');
      if (decodeURIComponent(bits[0]) === name) {
        return decodeURIComponent((bits[1] || '').split('+').join(' '));
      }
    }
    return null;
  }

  /* ---------------------------------------------------------------- chart */

  function chartGeometry() {
    var canvas = el.chart;
    var ratio = window.devicePixelRatio || 1;
    var width = canvas.clientWidth || 800;
    var height = 240;
    if (canvas.width !== Math.round(width * ratio)) {
      canvas.width = Math.round(width * ratio);
      canvas.height = Math.round(height * ratio);
    }
    var ctx = canvas.getContext('2d');
    ctx.setTransform(ratio, 0, 0, ratio, 0, 0);
    return { ctx: ctx, w: width, h: height, padL: 48, padR: 12, padT: 14, padB: 26 };
  }

  function drawChart() {
    var g = chartGeometry();
    var ctx = g.ctx;
    var palette = getComputedStyle(document.documentElement);
    var accent = palette.getPropertyValue('--cp-accent').trim();
    var border = palette.getPropertyValue('--cp-border').trim();
    var muted = palette.getPropertyValue('--cp-text-muted').trim();
    ctx.clearRect(0, 0, g.w, g.h);
    var series = state.timeline ? state.timeline.series : null;
    if (!series || !series.length) { return; }

    var plotW = g.w - g.padL - g.padR;
    var plotH = g.h - g.padT - g.padB;
    var lo = Infinity;
    var hi = -Infinity;
    series.forEach(function (row) {
      if (row.index < lo) { lo = row.index; }
      if (row.index > hi) { hi = row.index; }
    });
    if (hi - lo < 0.0001) { hi = lo + 0.1; }
    var pad = (hi - lo) * 0.12;
    lo -= pad;
    hi += pad;

    function xOf(month) {
      var span = state.last - state.first || 1;
      return g.padL + ((month - state.first) / span) * plotW;
    }
    function yOf(value) {
      return g.padT + plotH - ((value - lo) / (hi - lo)) * plotH;
    }

    /* Months in which something was happening, shaded behind everything. */
    ctx.fillStyle = palette.getPropertyValue('--cp-highlight').trim();
    var run = null;
    series.forEach(function (row, i) {
      var busy = row.events && row.events.length;
      if (busy && run === null) { run = row.month; }
      if ((!busy || i === series.length - 1) && run !== null) {
        var endMonth = busy ? row.month : series[i - 1].month;
        var x0 = xOf(run);
        var x1 = xOf(endMonth) + (plotW / Math.max(1, series.length));
        ctx.fillRect(x0, g.padT, Math.max(1.5, x1 - x0), plotH);
        run = null;
      }
    });

    /* Year gridlines and labels. */
    ctx.strokeStyle = border;
    ctx.fillStyle = muted;
    ctx.lineWidth = 1;
    ctx.font = '11px "Segoe UI", sans-serif';
    ctx.textAlign = 'center';
    series.forEach(function (row) {
      if (row.month % 12 !== 1) { return; }
      var x = Math.round(xOf(row.month)) + 0.5;
      ctx.beginPath();
      ctx.moveTo(x, g.padT);
      ctx.lineTo(x, g.padT + plotH);
      ctx.stroke();
      ctx.fillText(String(row.year), x, g.h - 8);
    });

    /* Value axis. */
    ctx.textAlign = 'right';
    for (var step = 0; step <= 3; step += 1) {
      var value = lo + ((hi - lo) * step) / 3;
      var y = Math.round(yOf(value)) + 0.5;
      ctx.strokeStyle = border;
      ctx.beginPath();
      ctx.moveTo(g.padL, y);
      ctx.lineTo(g.padL + plotW, y);
      ctx.stroke();
      ctx.fillStyle = muted;
      ctx.fillText(value.toFixed(2), g.padL - 6, y + 3);
    }

    /* The basket line. */
    ctx.strokeStyle = accent;
    ctx.lineWidth = 2.4;
    ctx.beginPath();
    series.forEach(function (row, i) {
      var x = xOf(row.month);
      var y = yOf(row.index);
      if (i === 0) { ctx.moveTo(x, y); } else { ctx.lineTo(x, y); }
    });
    ctx.stroke();

    /* Today, and the month being examined. */
    if (state.today !== null) {
      ctx.strokeStyle = muted;
      ctx.lineWidth = 1;
      var tx = Math.round(xOf(state.today)) + 0.5;
      ctx.beginPath();
      ctx.moveTo(tx, g.padT);
      ctx.lineTo(tx, g.padT + plotH);
      ctx.stroke();
    }
    if (state.month !== null) {
      var mx = Math.round(xOf(state.month)) + 0.5;
      ctx.strokeStyle = accent;
      ctx.lineWidth = 1.4;
      ctx.beginPath();
      ctx.moveTo(mx, g.padT);
      ctx.lineTo(mx, g.padT + plotH);
      ctx.stroke();
      var row = seriesAt(state.month);
      if (row) {
        ctx.fillStyle = accent;
        ctx.beginPath();
        ctx.arc(xOf(row.month), yOf(row.index), 3.5, 0, Math.PI * 2);
        ctx.fill();
      }
    }
  }

  function seriesAt(month) {
    var series = state.timeline ? state.timeline.series : [];
    for (var i = 0; i < series.length; i += 1) {
      if (series[i].month === month) { return series[i]; }
    }
    return null;
  }

  /* ------------------------------------------------------------- panels */

  function renderActiveEvents(events) {
    if (!events || !events.length) {
      el['active-events'].innerHTML =
        '<p class="muted">Nothing of note. The market is quiet this month.</p>';
      return;
    }
    el['active-events'].innerHTML = events.map(function (e) {
      var mods = [];
      if (e.supply !== 1) { mods.push('supply ' + pct(e.supply - 1)); }
      if (e.demand !== 1) { mods.push('demand ' + pct(e.demand - 1)); }
      if (e.price !== 1) { mods.push('price ' + pct(e.price - 1)); }
      if (e.risk) { mods.push('risk +' + e.risk.toFixed(2)); }
      var when = e.start ? esc(e.start) : 'always';
      if (e.end) { when += ' to ' + esc(e.end); }
      return '<article class="event-card">' +
        '<h3>' + esc(e.name) + '</h3>' +
        '<p>' + esc(e.description) + '</p>' +
        '<p class="muted">' + when + ' &#183; ' + esc(e.scope) + '</p>' +
        '<div class="event-mods">' +
        mods.map(function (m) { return '<span>' + esc(m) + '</span>'; }).join('') +
        '</div></article>';
    }).join('');
  }

  function renderAnalysis(analysis) {
    if (!analysis) { el.analysis.innerHTML = ''; return; }
    var rows = [
      ['Months charted', analysis.months],
      ['Average basket index', analysis.mean_index],
      ['Volatility', analysis.volatility],
      ['High to low spread', analysis.spread],
      ['Months with events', analysis.troubled_months],
      ['Quiet months', analysis.quiet_months]
    ];
    var html = '<dl>' + rows.map(function (pair) {
      return '<dt>' + esc(pair[0]) + '</dt><dd>' + esc(pair[1]) + '</dd>';
    }).join('') + '</dl>';

    if (analysis.dearest) {
      html += '<p class="muted">Dearest: <strong>' + esc(analysis.dearest.label) +
        '</strong> at ' + esc(analysis.dearest.index) + '. Cheapest: <strong>' +
        esc(analysis.cheapest.label) + '</strong> at ' +
        esc(analysis.cheapest.index) + '.</p>';
    }
    if (analysis.sharpest_move) {
      html += '<p class="muted">Sharpest single month move: ' +
        pct(analysis.sharpest_move.change) + ' in ' +
        esc(analysis.sharpest_move.label) + '.</p>';
    }
    if (analysis.event_impact && analysis.event_impact.length) {
      html += '<h3>What each event did to the basket</h3><ul class="impact">' +
        analysis.event_impact.map(function (row) {
          return '<li><span>' + esc(row.name) + '</span>' +
            '<span class="amount">' + pct(row.change) + '</span></li>';
        }).join('') + '</ul>';
    }
    el.analysis.innerHTML = html;
  }

  function renderChronicle(events) {
    if (!events || !events.length) {
      el['all-events'].innerHTML = '<p class="muted">No recorded history.</p>';
      return;
    }
    el['all-events'].innerHTML = events.map(function (e) {
      var live = (e.start_month !== null && state.month !== null &&
                  state.month >= e.start_month &&
                  (e.end_month === null || state.month <= e.end_month));
      var when = e.start ? esc(e.start) : 'always';
      if (e.end) { when += ' to ' + esc(e.end); }
      return '<button type="button" class="' + (live ? 'live' : '') +
        '" data-month="' + (e.start_month === null ? '' : e.start_month) + '">' +
        esc(e.name) + '<span class="when">' + when + '</span></button>';
    }).join('');
    Array.prototype.forEach.call(
      el['all-events'].querySelectorAll('button'),
      function (button) {
        button.addEventListener('click', function () {
          var month = parseInt(button.getAttribute('data-month'), 10);
          if (!isNaN(month)) { setMonth(month, true); }
        });
      }
    );
  }

  function renderTable() {
    var body = el['price-table'].querySelector('tbody');
    if (!state.detail) { body.innerHTML = ''; return; }
    var quiet = state.detail.quiet || {};
    var requirements = {};
    (state.detail.market.daily_requirements || []).forEach(function (row) {
      requirements[row.commodity_id] = row;
    });
    function changeOf(q) {
      var was = quiet[q.commodity];
      if (!was) { return null; }
      var change = q.price / was - 1;
      return Math.abs(change) < 0.005 ? null : change;
    }
    var rows = state.detail.market.prices.filter(function (q) {
      if (state.category && q.category !== state.category) { return false; }
      if (state.onlyMoved && changeOf(q) === null) { return false; }
      return true;
    });
    if (!rows.length) {
      body.innerHTML = '<tr><td colspan="14" class="muted">Nothing matches.</td></tr>';
      return;
    }
    body.innerHTML = rows.map(function (q) {
      var change = changeOf(q);
      var moved = change !== null;
      var klass = !moved ? 'flat' : (change > 0 ? 'up' : 'down');
      var was = quiet[q.commodity];
      var wasText = was === undefined ? '&#8212;' : quoteMoney(was);
      var need = requirements[q.commodity];
      var baseline = need
        ? quantity(need.settlement_per_day) + '<span class="need-detail">' +
          quantity(need.per_person_per_day) + ' per soul</span>'
        : '&#8212;';
      return '<tr class="' + (moved ? 'moved' : '') + '">' +
        '<td><a href="product.html?commodity=' + encodeURIComponent(q.commodity) +
        '&settlement=' + encodeURIComponent(state.settlement) + '">' + esc(q.commodity_name) +
        '</a> <span class="muted">/ ' +
        esc(q.unit) + '</span></td>' +
        '<td>' + esc(q.category) + '</td>' +
        '<td>' + esc(q.production_type) + '</td>' +
        '<td class="num">' + baseline + '</td>' +
        '<td class="num">' + quantity(q.demand_per_day) + '</td>' +
        '<td class="num">' + quoteMoney(q.price) + '</td>' +
        '<td class="num">' + quoteMoney(q.buy_price) + '</td>' +
        '<td class="num">' + quoteMarkup(q.merchant_markup_pct) + '</td>' +
        '<td class="num" title="' + esc(seasonalFreeBasis(q)) + '">' + quantity(q.uncommitted_stock) + '</td>' +
        '<td class="num">' + q.multiplier.toFixed(2) + '</td>' +
        '<td class="num">' + wasText + '</td>' +
        '<td class="num ' + klass + '">' +
        (moved ? pct(change) : '&#8212;') + '</td>' +
        '<td>' + esc(q.availability) + '</td>' +
        '<td>' + esc(q.source || 'local') + '</td>' +
        '</tr>';
    }).join('');
  }

  function renderBusinesses(data) {
    document.getElementById('historical-directory-link').hidden = data.settlement_id !== 'waterdeep';
    var businesses = data.businesses || [];
    if (!businesses.length) {
      el.businesses.innerHTML = '<p class="muted">No named businesses are recorded here yet.</p>';
      return;
    }
    el.businesses.innerHTML = businesses.map(function (business) {
      var offers = business.offers.map(function (offer) {
        return '<tr><td><a href="product.html?commodity=' +
          encodeURIComponent(offer.commodity) + '&settlement=' +
          encodeURIComponent(data.settlement_id) + '">' + esc(offer.commodity_name) +
          '</a></td><td>' + esc(offer.quality) + '</td><td class="num">' +
          quoteMoney(offer.price) + '</td><td class="num">' + quoteMoney(offer.buy_price) +
          '</td><td class="num">' + quoteMarkup(offer.merchant_markup_pct) +
          '</td><td class="num">' + offer.stock +
          '</td><td class="num">' + quantity(offer.uncommitted_stock) + '</td></tr>';
      }).join('');
      var presence = business.is_headquarters
        ? 'Headquarters'
        : 'Satellite branch; headquarters in ' + esc(business.headquarters_name);
      return '<article class="business"><h3>' + esc(business.name) + '</h3><p>' +
        presence + '</p><p>' + esc(business.specialties.join(' / ')) +
        '</p><details><summary>' + business.offers.length + ' offers</summary>' +
        '<table><thead><tr><th>Product</th><th>Grade</th>' +
        '<th class="num">Buy from merchant (gp)</th><th class="num">Sell to merchant (gp)</th>' +
        '<th class="num">Markup</th><th class="num">Stock</th><th class="num">Uncommitted</th></tr></thead><tbody>' +
        offers + '</tbody></table></details></article>';
    }).join('');
  }

  /* ------------------------------------------------------- requirements */

  function productLink(id, name, settlement) {
    return '<a href="product.html?commodity=' + encodeURIComponent(id) +
      '&settlement=' + encodeURIComponent(settlement || state.settlement) +
      '">' + esc(name || id) + '</a>';
  }

  function locationLink(id, name) {
    return '<a href="location.html?settlement=' + encodeURIComponent(id) +
      (state.month === null ? '' : '&month=' + encodeURIComponent(state.month)) +
      '">' + esc(name || id) + '</a>';
  }

  function plannerLink(origin, destination) {
    return '<a href="planner.html?origin=' + encodeURIComponent(origin) +
      '&destination=' + encodeURIComponent(destination) + '">Route planner</a>';
  }

  function requirementCard(label, value, unit) {
    return '<dl class="requirements-card"><dt>' + esc(label) + '</dt><dd>' +
      value + (unit ? '<small>' + esc(unit) + '</small>' : '') + '</dd></dl>';
  }

  function requirementTable(headers, rows, label) {
    return '<div class="requirements-subscroll" role="region" tabindex="0" aria-label="' +
      esc(label) + '"><table class="requirements-table"><thead><tr>' +
      headers.map(function (header) { return '<th scope="col">' + esc(header) + '</th>'; }).join('') +
      '</tr></thead><tbody>' + rows + '</tbody></table></div>';
  }

  function sectorLabel(key) {
    return String(key).split('_').join(' ').split('-').join(' ');
  }

  function renderProfileDetails(profile, materials) {
    var output = profile.output_establishments || [];
    el['requirements-output-section'].hidden = !output.length;
    el['requirements-output'].innerHTML = output.length
      ? requirementTable(['Facility / output unit per day', 'Required facilities (planned)',
        'Active equivalents (actual)', 'Planned output/day', 'Actual output/day',
        'Throughput/facility/day', 'Basis'], output.map(function (row) {
          return '<tr><td>' + esc(row.name) + '<small>' + esc(row.unit) +
            '/day</small></td><td class="num">' + quantity(row.count) +
            '</td><td class="num">' + quantity(row.active_equivalents) +
            '</td><td class="num">' + quantity(row.planned_per_day) +
            '</td><td class="num">' + quantity(row.actual_per_day) +
            '</td><td class="num">' + quantity(row.throughput_per_day) +
            '</td><td>' + esc(row.basis) + '</td></tr>';
        }).join(''), 'Output-equivalent facility requirements')
      : '';
    var equipment = profile.defense_equipment || {};
    var goods = Object.keys(equipment);
    el['requirements-defense-section'].hidden = !goods.length;
    el['requirements-defense'].innerHTML = goods.length
      ? requirementTable(['Equipment / unit', 'Standing stock required', 'Militia stock required',
        'Replacement/year', 'Replacement/day', 'Growth additions/year'], goods.map(function (id) {
          var row = equipment[id];
          var material = materials.find(function (item) { return item.commodity_id === id; });
          var daily = row.annual_replacement === null || row.annual_replacement === undefined
            ? null : row.annual_replacement / 365;
          return '<tr><td>' + productLink(id, material ? material.commodity : id) +
            '<small>' + esc(material ? material.unit : 'catalog units') +
            '</small></td><td class="num">' + quantity(row.standing_stock) +
            '</td><td class="num">' + quantity(row.militia_stock) +
            '</td><td class="num">' + quantity(row.annual_replacement) +
            '</td><td class="num">' + quantity(daily) +
            '</td><td class="num">' + quantity(row.annual_growth_additions) + '</td></tr>';
        }).join(''), 'Theoretical defense equipment requirements')
      : '';
    var resources = profile.resource_assumptions || {};
    var hasResources = Object.keys(resources).length || profile.fishers !== undefined && profile.fishers !== null;
    el['requirements-resources-section'].hidden = !hasResources;
    var resourceRows = [
      ['Farm hinterland', resources.farm_acres, 'acres', 'Inferred farmland'],
      ['Managed woodland', resources.woodland_acres, 'acres', 'Inferred woodland'],
      ['Dairy stock', resources.dairy_stock, 'animals', 'Inferred herd'],
      ['Poultry stock', resources.poultry_stock, 'birds', 'Inferred flock'],
      ['Beehives', resources.hives, 'hives', 'Inferred apiaries'],
      ['Draft oxen', resources.draft_oxen, 'animals', 'Inferred draft stock'],
      ['Potential fishers', resources.fishers, 'workers', 'Resource-based potential, not allocated labor'],
      ['Allocated fishers', profile.fishers, 'workers', 'Actual labor assigned by the model, not surveyed people']
    ];
    el['requirements-resources'].innerHTML = hasResources
      ? requirementTable(['Resource / labor', 'Estimated amount', 'Unit', 'Interpretation'],
        resourceRows.map(function (row) {
          return '<tr><td>' + esc(row[0]) + '</td><td class="num">' + quantity(row[1]) +
            '</td><td>' + esc(row[2]) + '</td><td>' + esc(row[3]) + '</td></tr>';
        }).join(''), 'Inferred hinterland resources and fishing labor') +
        (resources.assumptions && resources.assumptions.length
          ? '<details><summary>Resource-model assumptions</summary><ul>' +
            resources.assumptions.map(function (item) { return '<li>' + esc(item) + '</li>'; }).join('') +
            '</ul></details>' : '')
      : '';
  }

  function economyQuantity(value) {
    return quantity(Number.isFinite(value) ? value : null);
  }

  function economyMoney(value, signed) {
    if (!Number.isFinite(value)) { return money(null); }
    return (value < 0 ? '-' : signed && value > 0 ? '+' : '') + money(Math.abs(value));
  }

  function economyPercent(value) {
    return pct(Number.isFinite(value) ? value : null).replace('+', '');
  }

  function renderIndustries(industries) {
    return '<p>' + quantity(industries.length) + ' modeled service sectors, not named businesses. ' +
      'Workers are full-time equivalents (FTE), reclassifying existing professions plus residual workers: ' +
      '<strong>not additive to the earlier labor count table</strong>. Establishments are modeled estimates.</p>' +
      '<p>Selected-month daily rates use each sector&#39;s own unit, not a shared quantity to sum. ' +
      'Demand includes residents and visitors. Capacity is potential delivery; planned service may be ' +
      'limited by demand; actually delivered service also depends on available intermediate inputs. ' +
      'Paid market services are distinguished from imputed public services: public-service output is ' +
      'an estimated contribution, not cash sales. Output uses baseline service valuations.</p>' +
      requirementTable(['Sector / unit per day', 'Workers (FTE)', 'Establishments',
        'Resident demand/day', 'Visitor demand/day', 'Total demand/day', 'Capacity/day',
        'Planned/day', 'Actually delivered/day', 'Still unmet/day', 'Service output (gp/day)'],
        industries.map(function (row, index) {
          var inputs = row.inputs || [];
          var inputTable = inputs.length
            ? requirementTable(['Intermediate input / unit', 'Required/day', 'Consumed/day'],
              inputs.map(function (input) {
                return '<tr><td>' + productLink(input.commodity_id, input.commodity) +
                  '<small>' + esc(input.unit) + '/day</small></td><td class="num">' +
                  economyQuantity(input.required_per_day) + '</td><td class="num">' +
                  economyQuantity(input.consumed_per_day) + '</td></tr>';
              }).join(''), 'Intermediate inputs for ' + (row.name || row.id))
            : '<p>No intermediate inputs supplied for this sector.</p>';
          return '<tr><td>' + esc(row.name || row.id) + '<small>' + esc(row.unit) +
            '/day</small><small>' + (row.market_service === true ? 'Paid market service' :
              row.market_service === false ? 'Imputed public service' : 'Valuation type not supplied') +
            '</small>' + ((row.examples || []).length ? '<small>Examples: ' +
              row.examples.map(esc).join(', ') + '</small>' : '') + '</td><td class="num">' +
            economyQuantity(row.workers) + '</td><td class="num">' +
            economyQuantity(row.establishments) + '</td>' +
            ['resident_demand_per_day', 'visitor_demand_per_day', 'demand_per_day',
              'capacity_per_day', 'planned_per_day', 'delivered_per_day', 'unmet_per_day']
              .map(function (field) {
                return '<td class="num' +
                  (field === 'unmet_per_day' && row[field] > materialEpsilon ? ' material-unmet' : '') +
                  '">' + economyQuantity(row[field]) + '</td>';
              }).join('') + '<td class="num">' + economyMoney(row.service_output_gp_per_day) +
            '</td></tr><tr><td colspan="11"><details id="service-inputs-' + index +
            '" class="service-inputs"><summary>Inputs and estimation basis: ' + esc(row.name || row.id) +
            '</summary><p>' + esc(row.basis || 'No sector estimation basis supplied.') +
            '</p>' + inputTable + '</details></td></tr>';
        }).join(''), 'Modeled service sector demand, staffing and delivery');
  }

  function visitorLocations(rows, label) {
    if (!rows.length) { return '<p>No ' + esc(label.toLowerCase()) + ' supplied.</p>'; }
    return requirementTable(['Location', 'Average people/day', 'Travel spending (gp/day)'],
      rows.map(function (row) {
        return '<tr><td>' + locationLink(row.id, row.name) + '</td><td class="num">' +
          economyQuantity(row.visitors_per_day) + '</td><td class="num">' +
          economyMoney(row.spending_gp_per_day) + '</td></tr>';
      }).join(''), label);
  }

  function renderVisitors(visitors) {
    var segments = visitors.segments || [];
    return '<p>Arrivals are trips per <strong>30-day Harptos month</strong>; average people present per day ' +
      'are a different measure, not monthly arrivals. Day visitors have zero average nights. ' +
      'Refused overnight demand is not counted as arrivals. These are modeled travel flows, not measured tourism.</p>' +
      '<h4>Travel flows and average people present</h4><div class="requirements-cards">' + [
        requirementCard('Monthly arrivals', economyQuantity(visitors.arrivals_per_month), 'trips / 30-day Harptos month'),
        requirementCard('All visitors present', economyQuantity(visitors.visitors_per_day), 'average people / day'),
        requirementCard('Overnight visitors present', economyQuantity(visitors.overnight_visitors_per_day), 'average people / day'),
        requirementCard('Day visitors present', economyQuantity(visitors.day_visitors_per_day), 'average people / day'),
        requirementCard('Residents traveling away', economyQuantity(visitors.outbound_visitors_per_day), 'average people / day')
      ].join('') + '</div><h4>Accommodation and resident presence</h4><div class="requirements-cards">' + [
        requirementCard('Desired overnight visitors', economyQuantity(visitors.desired_overnight_visitors_per_day), 'average people / day'),
        requirementCard('Unaccommodated overnight demand', economyQuantity(visitors.unaccommodated_visitors_per_day), 'average people / day; not arrivals'),
        requirementCard('Available beds', economyQuantity(visitors.beds), 'modeled beds'),
        requirementCard('Bed occupancy', economyPercent(visitors.occupancy), 'share of beds occupied; unavailable if no beds'),
        requirementCard('Residents at home', economyQuantity(visitors.residents_at_home), 'modeled residents minus outbound visitors'),
        requirementCard('Modeled people present', economyQuantity(visitors.modeled_present_population), 'residents at home plus modeled inbound visitors'),
        requirementCard('Resident presence', economyQuantity(visitors.resident_presence), 'resident food-demand equivalents at home')
      ].join('') + '</div><h4>Visitor demand and spending</h4><div class="requirements-cards">' + [
        requirementCard('Visitor goods demand', economyQuantity(visitors.visitor_goods_demand_weight_lb_per_day), 'lb / day'),
        requirementCard('Visitor goods supplied', economyQuantity(visitors.visitor_goods_supplied_weight_lb_per_day), 'lb / day'),
        requirementCard('Visitor spending here', economyMoney(visitors.visitor_spending_gp_per_day), 'gp / day'),
        requirementCard('Resident travel spending away', economyMoney(visitors.visitor_spending_abroad_gp_per_day), 'gp / day'),
        requirementCard('Net visitor receipts', economyMoney(visitors.net_visitor_receipts_gp_per_day, true), 'gp / day; receipts minus outlays')
      ].join('') + '</div><p>Resident home food demand is reduced while residents are away. ' +
      'More guests add food and service-material pressure, including intermediate inputs. ' +
      'External visitors are unknown and excluded; modeled people present is not a complete city census. ' +
      'Domestic travel spending transfers between modeled cities; it is not new global gold.</p>' +
      '<h4>Visitor segments</h4>' + (segments.length
        ? requirementTable(['Segment', 'Average people present/day', 'Arrivals / 30-day month',
          'Average nights / trip', 'Spending (gp/day)'], segments.map(function (row) {
            return '<tr><td>' + esc(row.name || row.id) + '</td><td class="num">' +
              economyQuantity(row.visitors_per_day) + '</td><td class="num">' +
              economyQuantity(row.arrivals_per_month) + '</td><td class="num">' +
              economyQuantity(row.average_nights) + '</td><td class="num">' +
              economyMoney(row.spending_gp_per_day) + '</td></tr>';
          }).join(''), 'Visitor segments and trip lengths')
        : '<p>No visitor segment estimates supplied.</p>') +
      '<h4>Incoming origins</h4>' + visitorLocations(visitors.origins || [], 'Incoming visitor origins') +
      '<h4>Outgoing destinations</h4>' + visitorLocations(visitors.destinations || [], 'Outgoing resident destinations');
  }

  function renderAccounts(accounts) {
    return '<p><strong>Estimated gross local product (GLP)</strong> is the local GDP-style estimate: ' +
      'goods value added plus service value added, where value added = output minus intermediates. ' +
      'All amounts are in gp. Public services include imputed output, not just paid sales.</p>' +
      '<div class="requirements-cards">' + [
        requirementCard('Gross local product (GLP)', economyMoney(accounts.gross_local_product_gp_per_day), 'gp / day; estimated'),
        requirementCard('Annualized GLP', economyMoney(accounts.gross_local_product_gp_per_year), 'gp / year; current-day run rate'),
        requirementCard('Annualized GLP per resident', economyMoney(accounts.glp_per_resident_gp_per_year), 'gp / resident / year; current-day run rate')
      ].join('') + '</div><p>Annual values are <strong>annualized current-day run rates (365 days)</strong>, ' +
      'not a measured year total. An unavailable per-resident value is not zero.</p>' +
      '<h4>Output and value added</h4>' +
      requirementTable(['Activity', 'Output (gp/day)', 'Intermediates consumed (gp/day)', 'Value added (gp/day)'],
        [['Goods', 'goods'], ['Services', 'service']].map(function (row) {
          return '<tr><td>' + esc(row[0]) + '</td><td class="num">' +
            economyMoney(accounts[row[1] + '_output_gp_per_day']) + '</td><td class="num">' +
            economyMoney(accounts[row[1] + '_intermediate_gp_per_day']) + '</td><td class="num">' +
            economyMoney(accounts[row[1] + '_value_added_gp_per_day']) + '</td></tr>';
        }).join(''), 'Local output, intermediates and value added') +
      '<p><strong>Output and GLP valuation:</strong> constant catalogue commodity prices and baseline service ' +
      'valuations, not the current nominal market-price series.</p><p>Supplied output valuation basis: ' +
      esc(accounts.output_valuation_basis || 'Not supplied.') + '</p>' +
      '<h4>Merchandise trade and travel balances</h4>' +
      requirementTable(['External flow or balance', 'gp / day'],
        [
          ['Goods exports', 'goods_exports_gp_per_day'],
          ['Goods imports', 'goods_imports_gp_per_day'],
          ['Merchandise balance (exports minus imports)', 'goods_trade_balance_gp_per_day', true],
          ['Visitor receipts', 'visitor_receipts_gp_per_day'],
          ['Resident travel outlays', 'resident_travel_spending_gp_per_day'],
          ['Net travel receipts (receipts minus outlays)', 'net_visitor_receipts_gp_per_day', true],
          ['Combined external balance (merchandise plus net travel)', 'external_balance_gp_per_day', true]
        ].map(function (row) {
          return '<tr><td>' + esc(row[0]) + '</td><td class="num">' +
            economyMoney(accounts[row[1]], row[2]) + '</td></tr>';
        }).join(''), 'Merchandise and travel external balances') +
      '<p><strong>Trade valuation:</strong> both counterparties use the identical producer-gate invoice, ' +
      'excluding freight and tariffs. This is a different valuation basis from constant-price output and GLP; ' +
      'do not compare them as one nominal price series.</p><p>Supplied trade valuation basis: ' +
      esc(accounts.trade_valuation_basis || 'Not supplied.') + '</p>' +
      '<p>Tourist retail goods already enter the local goods and value-added model. ' +
      '<strong>Do not add visitor receipts or exports again to GLP.</strong> Domestic travel spending is a ' +
      'transfer, not new global gold. Financial balances are not profits, treasury balances, or immediate ' +
      'automatic wealth gains.</p>';
  }

  function renderEconomy(economy) {
    var enabled = economy && economy.enabled;
    var industries = enabled && economy.industries || [];
    var visitors = enabled && economy.visitors;
    var accounts = enabled && economy.accounts;
    var assumptions = enabled && economy.assumptions || [];
    el['requirements-industries-section'].hidden = !industries.length;
    el['requirements-industries'].innerHTML = industries.length ? renderIndustries(industries) : '';
    el['requirements-visitors-section'].hidden = !(visitors && visitors.enabled);
    el['requirements-visitors'].innerHTML = visitors && visitors.enabled ? renderVisitors(visitors) : '';
    el['requirements-accounts-section'].hidden = !accounts;
    el['requirements-accounts'].innerHTML = accounts ? renderAccounts(accounts) : '';
    el['requirements-economy-assumptions-section'].hidden = !assumptions.length;
    el['requirements-economy-assumptions'].innerHTML = assumptions.length ? '<ul>' +
      assumptions.map(function (item) { return '<li>' + esc(item) + '</li>'; }).join('') + '</ul>' : '';
  }

  function renderWater(water) {
    el['requirements-water-section'].hidden = !water;
    if (!water) { el['requirements-water'].innerHTML = ''; return; }
    var status = water.total_person_days === 0 ? 'No domestic water demand' :
      water.status === 'essential_gap' ? 'Modeled essential-water gap: review source and access assumptions' :
      water.status === 'routine_gap' ? 'Essential needs covered; a routine-use gap remains (estimate)' :
      'Domestic water needs covered (estimate)';
    var cards = [
      ['Usable freshwater', water.usable_gallons_per_day],
      ['Municipal delivery', water.municipal_delivered_gallons_per_day],
      ['Household / private collection', water.household_delivered_gallons_per_day],
      ['Essential drinking and cooking need', water.essential_demand_gallons_per_day],
      ['Essential-water gap', water.essential_gap_gallons_per_day],
      ['Routine-use gap', water.routine_gap_gallons_per_day]
    ];
    var demandRows = [
      ['Drinking', water.drinking_demand_gallons_per_day],
      ['Essential cooking', water.essential_cooking_demand_gallons_per_day],
      ['Other domestic use', water.routine_demand_gallons_per_day],
      ['Total domestic need', water.total_demand_gallons_per_day],
      ['Total delivered', water.total_delivered_gallons_per_day],
      ['Source / usable-yield gap', water.source_gap_gallons_per_day],
      ['Collection / distribution gap', water.access_gap_gallons_per_day],
      ['Operational / input gap', water.operations_gap_gallons_per_day],
      ['Usable water not drawn', water.unused_usable_gallons_per_day]
    ];
    var sourceRows = (water.sources || []).map(function (row) {
      return '<tr><td>' + esc(row.name) + '</td><td class="num">' +
        quantity(row.raw_gallons_per_day) + '</td><td class="num">' +
        quantity(row.usable_gallons_per_day) + '</td><td>' + esc(row.basis) + '</td></tr>';
    }).join('');
    el['requirements-water'].innerHTML = '<p><strong>' + esc(status) +
      '</strong></p><p>Evidence: ' + esc(water.evidence) +
      '. Estimates are not a hydrological survey, a confirmed crisis, or a mortality prediction.</p>' +
      '<div class="requirements-cards">' + cards.map(function (row) {
        return requirementCard(row[0], quantity(row[1]), 'gallons / day');
      }).join('') + '</div><details class="requirements-notes"><summary>Water sources and delivery balance</summary>' +
      '<p>Municipal delivery and household collection share one finite usable-water pool. ' +
      'Essential use is allocated before other domestic use. A lack of municipal workers does not mean a lack of water.</p>' +
      requirementTable(['Water source', 'Raw gallons/day', 'Usable gallons/day', 'Evidence / basis'],
        sourceRows || '<tr><td colspan="4">No source yield supplied for this scenario.</td></tr>', 'Estimated water sources') +
      requirementTable(['Delivery channel', 'Capacity (gallons/day)', 'Delivered (gallons/day)'],
        '<tr><td>Municipal distribution</td><td class="num">' + quantity(water.municipal_capacity_gallons_per_day) +
        '</td><td class="num">' + quantity(water.municipal_delivered_gallons_per_day) +
        '</td></tr><tr><td>Household / private collection</td><td class="num">' +
        quantity(water.household_capacity_gallons_per_day) + '</td><td class="num">' +
        quantity(water.household_delivered_gallons_per_day) + '</td></tr>', 'Water access and delivery') +
      requirementTable(['Water use or limiting factor', 'Gallons/day'], demandRows.map(function (row) {
        return '<tr><td>' + esc(row[0]) + '</td><td class="num">' + quantity(row[1]) + '</td></tr>';
      }).join(''), 'Domestic water balance') +
      '<p>' + esc(water.municipal_delivery_basis || '') + '</p><ul>' +
      (water.assumptions || []).map(function (text) { return '<li>' + esc(text) + '</li>'; }).join('') +
      '</ul><p>No water inventory, shortage duration or population loss is simulated.</p></details>';
  }

  function renderRequirements(requirements) {
    var enabled = requirements && requirements.enabled;
    el['requirements-content'].hidden = !enabled;
    el['requirements-download'].disabled = !enabled;
    el['requirements-status'].textContent = enabled ? '' :
      'Expanded requirements are unavailable in this legacy model. Prices and named businesses remain available below.';
    renderEconomy(enabled ? requirements.economy : null);
    renderWater(enabled ? requirements.water : null);
    if (!enabled) { return; }
    var profile = requirements.profile || {};
    var summary = requirements.summary || {};
    el['requirements-model'].textContent = 'Model: ' + (requirements.model || 'unspecified') +
      ' / Material balance: ' + (requirements.date || state.detail.label || 'selected month') +
      (profile.reference_period ? ' / Demographics and local services: ' + profile.reference_period : '');
    el['requirements-profile'].innerHTML = [
      requirementCard('Resident population', quantity(profile.population), 'modeled people; excludes visitors'),
      requirementCard('Wealth', quantity(profile.wealth), 'model wealth factor'),
      requirementCard('Mages', quantity(profile.mage_population), 'estimated people'),
      requirementCard('Standing army', quantity(profile.standing_army), 'estimated people'),
      requirementCard('Militia', quantity(profile.militia), 'estimated people'),
      requirementCard('Annual growth', pct(profile.annual_growth_rate), 'per year'),
      requirementCard('Builders', quantity(profile.builders), 'estimated workers'),
      requirementCard('Carpenters', quantity(profile.carpenters), 'estimated workers'),
      requirementCard('New homes', quantity(profile.new_homes_per_year), 'estimated homes / year')
    ].join('');
    var assumptions = (profile.assumptions || []).concat(requirements.assumptions || []);
    var populationModel = profile.population_model;
    if (populationModel) {
      assumptions = assumptions.concat(populationModel.assumptions || []);
    }
    assumptions = assumptions.filter(function (item, index) { return assumptions.indexOf(item) === index; });
    var provenance = profile.provenance;
    if (provenance && typeof provenance !== 'string') { provenance = JSON.stringify(provenance, null, 2); }
    var populationNotes = populationModel ? '<h4>Population basis</h4><p>' +
      esc(populationModel.scope) + '</p><p>' +
      esc(populationModel.rationale || 'Gazetteer estimate; no dated census supplied.') + '</p>' +
      (populationModel.comparison_residents !== undefined ? '<p>Comparison baseline: ' +
        quantity(populationModel.comparison_residents) + ' residents; per-person household demand multiplier: ' +
        quantity(populationModel.household_demand_multiplier) + '. Prices do not scale linearly.</p>' : '') +
      '<ul>' + (populationModel.evidence || []).map(function (source) {
        return '<li>' + esc(source.title) + ' (' + esc(source.period) + '): ' +
          esc(source.description) + ' Source: ' + esc(source.url) + '</li>';
      }).join('') + '</ul>' +
      (populationModel.settlement_id === 'daggerford'
        ? '<p><a href="daggerford.html">Inspect Daggerford population, buildings &amp; streets</a></p>' : '') : '';
    el['requirements-assumptions'].innerHTML = '<p>These are simulation estimates, not canonical demographic facts.</p>' +
      populationNotes +
      '<h4>Provenance</h4><pre>' + esc(provenance || 'No provenance supplied.') + '</pre>' +
      '<h4>Assumptions</h4>' + (assumptions.length ? '<ul>' +
        assumptions.map(function (item) { return '<li>' + esc(item) + '</li>'; }).join('') + '</ul>' :
        '<p>No additional assumptions supplied.</p>');
    var establishments = profile.establishments || [];
    el['requirements-establishments'].innerHTML = establishments.length
      ? '<p>Modeled producers and services; counts do not identify named businesses.</p>' +
        requirementTable(['Establishment type', 'Estimated count', 'Estimated workers (total)', 'Basis'],
          establishments.map(function (row) {
            return '<tr><td>' + esc(row.name || row.id) + '</td><td class="num">' +
              quantity(row.count) + '</td><td class="num">' + quantity(row.workers) +
              '</td><td>' + esc(row.basis) + '</td></tr>';
          }).join(''), 'Estimated establishments')
      : '<p>No establishment estimates supplied.</p>';
    renderProfileDetails(profile, requirements.materials || []);
    var services = (profile.service_requirements || []).filter(function (service) {
      return !(requirements.water && service.scope === 'municipal_water_reference');
    });
    el['requirements-services-section'].hidden = !services.length;
    el['requirements-services'].innerHTML = services.length
      ? requirementTable(['Service', 'Unit per day', 'Required/day', 'Local capacity/day', 'Still unmet/day', 'Estimate basis'],
        services.map(function (service) {
          return '<tr><td>' + esc(service.name) + '</td><td>' + esc(service.unit) +
            '/day</td><td class="num">' + quantity(service.required_per_day) +
            '</td><td class="num">' + quantity(service.local_capacity_per_day) +
            '</td><td class="num' + (service.unmet_per_day > 0 ? ' material-unmet' : '') + '">' +
            quantity(service.unmet_per_day) + '</td><td>' + esc(service.basis) + '</td></tr>';
        }).join(''), 'Local service requirements')
      : '';
    el['requirements-summary'].innerHTML = [
      requirementCard('Goods needing imports', quantity(summary.goods_with_import_need), 'pre-trade gap'),
      requirementCard('Goods still unmet', quantity(summary.goods_with_shortfall), 'after trade'),
      requirementCard('Goods with surplus', quantity(summary.goods_with_surplus), 'pre-trade exportable output'),
      requirementCard('Allocated import weight', quantity(summary.import_weight_lb_per_day), 'lb / day'),
      requirementCard('Allocated export weight', quantity(summary.export_weight_lb_per_day), 'lb / day'),
      requirementCard('Food demand', quantity(summary.food_demand_lb_per_day), 'lb / day'),
      requirementCard('Food consumed', quantity(summary.food_consumption_lb_per_day), 'lb / day')
    ].join('');
    renderRequirementsTable();
  }

  function renderRequirementsTable() {
    var requirements = state.detail && state.detail.requirements;
    var body = el['requirements-table'].querySelector('tbody');
    if (!requirements || !requirements.enabled) { body.innerHTML = ''; return; }
    var materials = requirements.materials || [];
    var search = state.materialSearch.trim().toLowerCase();
    var rows = materials.filter(function (row) {
      if (state.materialFilter === 'imports' && !(row.import_need_per_day > materialEpsilon)) { return false; }
      if (state.materialFilter === 'unmet' && !(row.unmet_per_day > materialEpsilon)) { return false; }
      if (state.materialFilter === 'surplus' && !(row.surplus_per_day > materialEpsilon)) { return false; }
      if (state.materialFilter === 'uncommitted' &&
          !(row.uncommitted_supply_per_day > materialEpsilon || row.uncommitted_stock > materialEpsilon)) { return false; }
      var words = [row.commodity, row.commodity_id, row.category, row.unit,
        Object.keys(row.sectors || {}).map(sectorLabel).join(' '),
        (row.inputs || []).map(function (input) { return input.commodity; }).join(' ')].join(' ');
      return !search || words.toLowerCase().indexOf(search) !== -1;
    });
    el['requirements-count'].textContent = rows.length + ' of ' + materials.length + ' materials';
    if (!rows.length) {
      body.innerHTML = '<tr><td colspan="12">No materials match these filters.</td></tr>';
      return;
    }
    body.innerHTML = rows.map(function (row, index) {
      var open = state.openMaterials.has(row.commodity_id);
      var detailId = 'material-detail-' + index;
      var fields = ['final_demand_per_day', 'processing_demand_per_day', 'demand_per_day',
        'capacity_per_day', 'production_per_day', 'import_need_per_day',
        'imports_per_day', 'unmet_per_day', 'surplus_per_day', 'uncommitted_supply_per_day', 'uncommitted_stock'];
      return '<tr><td>' + productLink(row.commodity_id, row.commodity) +
        '<small>' + esc(row.category) + ' / ' + esc(row.unit) + '/day</small>' +
        '<button type="button" class="ghost" data-material="' + esc(row.commodity_id) +
        '" aria-expanded="' + open + '" aria-controls="' + detailId +
        '" aria-label="Details for ' + esc(row.commodity) + '">Requirements, storage &amp; suppliers</button></td>' +
        fields.map(function (field) {
          var shortfall = field === 'unmet_per_day' && row[field] > materialEpsilon;
          return '<td class="num' + (shortfall ? ' material-unmet' : '') + '">' +
            quantity(row[field]) + '</td>';
        }).join('') + '</tr><tr id="' + detailId + '" class="material-detail"' +
        (open ? '' : ' hidden') + '><td colspan="12">' +
        (open ? materialDetails(row) : '') + '</td></tr>';
    }).join('');
  }

  function materialDetails(row) {
    var rateUnit = (row.unit || 'trade units') + '/day';
    var calibration = row.hinterland_capacity_multiplier === null || row.hinterland_capacity_multiplier === undefined
      ? '' : '<p><strong>Source-district baseline calibration: ' +
        quantity(row.hinterland_capacity_multiplier) + '&#215;.</strong> This is a modeling assumption, not census acreage. ' +
        'Factors above 1 expand inferred hinterland to support aggregate population and workshop input needs before events. ' +
        'Actual output may also include established industries.</p>';
    var balance = '<div class="requirements-cards">' + [
      requirementCard('Local use', quantity(row.local_use_per_day), rateUnit),
      requirementCard('Actual consumption', quantity(row.consumption_per_day), rateUnit),
      requirementCard('Allocated exports', quantity(row.exports_per_day), rateUnit),
      requirementCard('Uncommitted flow before dated POs', quantity(row.uncommitted_supply_per_day), rateUnit),
      requirementCard('Uncommitted stock', quantity(row.uncommitted_stock),
        (row.unit || 'trade units') + (row.order_supply_window
          ? ' / ' + row.order_supply_window.start + ' to ' + row.order_supply_window.end
          : (!seasonalEnabled(row) && Number.isFinite(row.stock_horizon_days) ? ' / ' + row.stock_horizon_days + '-day window' : ''))),
      requirementCard('Dated PO claims', quantity(row.order_claimed_stock || 0),
        'All grades and export takeovers; not additional demand'),
      requirementCard('Closing stock', quantity(seasonalEnabled(row) ? row.inventory.closing_stock : row.closing_stock), row.unit || 'trade units')
    ].join('') + '</div>';
    var sectors = Object.keys(row.sectors || {});
    var sectorRows = sectors.map(function (sector) {
      return '<tr><td>' + esc(sectorLabel(sector)) + '</td><td class="num">' +
        quantity(row.sectors[sector]) + '</td></tr>';
    }).join('');
    var inputs = row.inputs || [];
    var allMaterials = state.detail.requirements.materials || [];
    var inputRows = inputs.map(function (input) {
      var material = allMaterials.find(function (item) { return item.commodity_id === input.commodity; });
      return '<tr><td>' + productLink(input.commodity, material ? material.commodity : input.commodity) +
        '<small>' + esc(input.unit) + '/day</small></td><td class="num">' +
        quantity(input.required_per_day) + '</td><td class="num">' +
        quantity(input.reserved_per_day) + '</td><td class="num">' +
        quantity(input.consumed_per_day) + '</td></tr>';
    }).join('');
    var sources = row.sources || [];
    var totalAllocated = sources.reduce(function (total, source) {
      return total + Number(source.quantity_per_day || 0);
    }, 0);
    var sourceRows = sources.map(function (source) {
      var origin = source.source_id || source.source;
      return '<tr><td>' + locationLink(origin, source.source) +
        '<small>' + productLink(row.commodity_id, 'Product at source', origin) +
        '</small></td><td>' + esc(source.supply_type) + '</td><td class="num">' +
        quantity(source.quantity_per_day) + '</td><td class="num">' +
        (totalAllocated ? quantity(source.quantity_per_day / totalAllocated * 100) + '%' : '&#8212;') +
        '</td><td class="num">' + money(source.unit_cost) + ' gp/' + esc(row.unit) +
        '</td><td>' + quantity(source.distance) + ' mi / ' + quantity(source.days) + ' days' +
        (source.supply_type === 'local' ? '' : '<small>' + plannerLink(origin, state.settlement) + '</small>') +
        '</td></tr>';
    }).join('');
    var destinations = row.export_destinations || [];
    var destinationRows = destinations.map(function (destination) {
      var id = destination.destination_id || destination.destination;
      return '<tr><td>' + locationLink(id, destination.destination) + '</td><td class="num">' +
        quantity(destination.quantity_per_day) + '</td><td>' +
        productLink(row.commodity_id, 'Product at destination', id) + ' / ' +
        plannerLink(state.settlement, id) + '</td></tr>';
    }).join('');
    return '<h4>' + esc(row.commodity) + ': consumption and remaining stock</h4>' + calibration + balance +
      '<p><strong>Stock basis:</strong> ' + esc(seasonalStockBasis(row)) + ' ' + esc(seasonalFreeBasis(row)) + '</p>' +
      seasonalPanel(row) +
      '<div class="material-detail-grid"><div><h4>Final demand by sector</h4>' +
      (sectorRows ? requirementTable(['Sector / diet', rateUnit], sectorRows, 'Final demand sectors') :
        (row.final_demand_per_day === 0 ? '<p>No final-use demand; any requirement here is for processing.</p>' :
          '<p>No sector breakdown supplied.</p>')) +
      '</div><div><h4>Direct processing inputs / material cascade</h4>' +
      '<p>Required, reserved and actually consumed inputs are distinct. Follow an ingredient product for its recipe, or a supplier location for its own requirements. These are direct modeled inputs, not a second demand estimate.</p>' +
      (inputRows ? requirementTable(['Input / unit per day', 'Required/day', 'Reserved/day', 'Consumed/day'],
        inputRows, 'Direct processing inputs') : '<p>No direct processing inputs for this material.</p>') +
      '</div></div><h4>Allocated supplier split</h4>' +
      (sourceRows ? requirementTable(['Supplier', 'Type', rateUnit, 'Share of allocated supply', 'Unit cost', 'Delivery / route'],
        sourceRows, 'Allocated suppliers') : '<p>No allocated suppliers. An import need is not a confirmed delivery.</p>') +
      '<h4>Export destinations</h4>' +
      (destinationRows ? requirementTable(['Destination', rateUnit, 'Product / route'],
        destinationRows, 'Allocated export destinations') : '<p>No exports allocated to other locations.</p>');
  }

  function toggleMaterial(event) {
    var button = event.target.closest('button[data-material]');
    if (!button || !state.detail || !state.detail.requirements) { return; }
    var id = button.getAttribute('data-material');
    var row = (state.detail.requirements.materials || []).find(function (item) {
      return item.commodity_id === id;
    });
    if (!row) { return; }
    var detail = document.getElementById(button.getAttribute('aria-controls'));
    var open = !state.openMaterials.has(id);
    if (open) { state.openMaterials.add(id); } else { state.openMaterials.delete(id); }
    button.setAttribute('aria-expanded', String(open));
    detail.hidden = !open;
    detail.querySelector('td').innerHTML = open ? materialDetails(row) : '';
  }

  function downloadRequirements() {
    var requirements = state.detail && state.detail.requirements;
    if (!requirements || !requirements.enabled) { return; }
    var payload = { settlement: state.settlement, month: state.month, requirements: requirements };
    var blob = new Blob([JSON.stringify(payload, null, 2)], { type: 'application/json' });
    var url = URL.createObjectURL(blob);
    var link = document.createElement('a');
    link.href = url;
    link.download = 'location-requirements-' + state.month + '.json';
    document.body.appendChild(link);
    link.click();
    link.remove();
    window.setTimeout(function () { URL.revokeObjectURL(url); }, 1000);
  }

  /* ------------------------------------------------------------ loading */

  var detailTimer = null;
  var detailController = null;
  var detailRequest = 0;
  var settlementRequest = 0;
  var timelineGeneration = 0;

  function setDetailBusy(busy) {
    el['price-table'].classList.toggle('loading', busy);
    el['price-table'].setAttribute('aria-busy', String(busy));
    el['requirements-board'].setAttribute('aria-busy', String(busy));
    el['load-history'].disabled = busy || !state.detail || timelineGeneration === settlementRequest;
  }

  function clearDetail(message) {
    detailRequest += 1;
    if (detailController) { detailController.abort(); detailController = null; }
    if (detailTimer !== null) { window.clearTimeout(detailTimer); detailTimer = null; }
    state.detail = null;
    state.openMaterials.clear();
    el['price-table'].querySelector('tbody').innerHTML = '';
    el['table-title'].textContent = 'Prices';
    el['living-standard'].textContent = '';
    el['event-cost'].textContent = '';
    el['active-events'].innerHTML = '<p class="muted">Loading selected month...</p>';
    el['requirements-content'].hidden = true;
    el['requirements-download'].disabled = true;
    el['requirements-table'].querySelector('tbody').innerHTML = '';
    el['requirements-status'].textContent = message;
    setDetailBusy(true);
    say(message);
  }

  function setTimelineEnabled(enabled) {
    ['scrub', 'jump-worst', 'jump-best'].forEach(function (id) {
      el[id].disabled = !enabled;
    });
    el['history-chart'].hidden = !enabled;
  }

  function setMonthNavigation(enabled) {
    el['step-back'].disabled = !enabled || state.month === null || state.month <= 0;
    el['step-fwd'].disabled = !enabled || state.month === null;
    el['jump-today'].disabled = !enabled || state.today === null;
  }

  function updateHistory() {
    try {
      window.history.replaceState({}, '', '?settlement=' + encodeURIComponent(state.settlement) +
        (state.month === null ? '' : '&month=' + encodeURIComponent(state.month)));
    } catch (ignored) { /* file:// has no history to write */ }
  }

  function showMonth() {
    var row = seriesAt(state.month);
    el.scrub.value = String(state.month - state.first);
    el['scrub-date'].textContent = row ? row.label : state.detail ? state.detail.label :
      state.month === state.today ? 'Current month' : 'Month ' + state.month;
    el['scrub-season'].textContent = row ? row.season : state.detail ? state.detail.season : '';
    el['scrub-index'].textContent = row ? 'basket index ' + row.index.toFixed(3) : '';
    drawChart();
    if (state.timeline) { renderChronicle(state.timeline.events); }
  }

  function setMonth(month, immediate) {
    if (!Number.isInteger(month) || month < 0) { return; }
    if (state.timeline) { month = Math.max(state.first, Math.min(state.last, month)); }
    if (state.month === month && state.detail) { showMonth(); return; }
    state.month = month;
    clearDetail('Loading requirements and prices for the selected month...');
    showMonth();
    updateHistory();
    if (immediate) { loadDetail(); }
    else { detailTimer = window.setTimeout(loadDetail, 220); }
  }

  function loadDetail() {
    if (!state.settlement) { return; }
    detailTimer = null;
    var name = state.settlement;
    var month = state.month;
    var generation = settlementRequest;
    var request = ++detailRequest;
    var controller = new AbortController();
    detailController = controller;
    function isCurrent() {
      return generation === settlementRequest && request === detailRequest && name === state.settlement;
    }
    var row = seriesAt(month);
    var message = 'Loading requirements and prices for ' + name + ' / ' +
      (row ? row.label : month === state.today ? 'the current month' : 'month ' + month) + '...';
    el['requirements-status'].textContent = message;
    say(message);
    setDetailBusy(true);
    /* Aborting a fetch cannot cancel server work, so every completion also
       checks its generation. History is expensive and requires explicit opt-in. */
    get('/api/location?settlement=' + encodeURIComponent(name) +
        (month === null ? '' : '&month=' + month), controller.signal)
      .then(function (data) {
        if (!isCurrent() || state.month !== month) { return; }
        state.detail = data;
        state.month = data.month;
        el['place-name'].textContent = data.market.settlement || name;
        updateGeneratorLink(data.market.settlement || name);
        el['table-title'].textContent = 'Prices in ' + data.label;
        el['living-standard'].textContent = data.market.living_standard +
          ' living standard · ' + data.market.population.toLocaleString() + ' souls';
        el['event-cost'].textContent = data.goods_moved
          ? 'events are moving ' + data.goods_moved + ' goods, basket ' +
            pct(data.event_cost)
          : 'no event pressure';
        renderActiveEvents(data.events);
        renderTable();
        renderRequirements(data.requirements);
        showMonth();
        updateHistory();
        say('');
      })
      .catch(function (err) {
        if (!isCurrent() || err.name === 'AbortError') { return; }
        state.detail = null;
        el['price-table'].querySelector('tbody').innerHTML = '';
        el['table-title'].textContent = 'Prices unavailable';
        el['living-standard'].textContent = '';
        el['event-cost'].textContent = '';
        el['requirements-content'].hidden = true;
        el['requirements-download'].disabled = true;
        el['requirements-status'].textContent = 'Could not load requirements: ' + err.message;
        el['active-events'].innerHTML = '<p class="muted">Selected month could not be loaded.</p>';
        say(err.message);
      })
      .then(function () {
        if (!isCurrent()) { return; }
        detailController = null;
        setDetailBusy(false);
        setMonthNavigation(true);
      });
  }

  function updateGeneratorLink(name) {
    var link = document.getElementById('location-generator-link');
    var known = generatorLocations.find(function (row) {
      return row.id === name || row.name.toLowerCase() === String(name).toLowerCase();
    });
    if (known) { name = known.name; }
    link.href = 'location-generator.html?location=' + encodeURIComponent(name);
    link.hidden = !name;
  }

  function loadSettlement(name) {
    var generation = ++settlementRequest;
    state.settlement = name;
    state.timeline = null;
    if (state.month === null) { state.month = state.today; }
    clearDetail('Loading requirements and prices for ' + name + '...');
    setTimelineEnabled(false);
    setMonthNavigation(false);
    el['load-history'].textContent = 'Load seven-year price history';
    el['history-chart'].setAttribute('aria-busy', 'false');
    el['place-name'].textContent = name;
    updateGeneratorLink(name);
    el['place-blurb'].textContent = '';
    el['analysis'].innerHTML = '<p class="muted">Historical analysis is available after loading seven-year price history.</p>';
    el['all-events'].innerHTML = '<p class="muted">Load seven-year price history to see the full chronicle.</p>';
    el['timeline-status'].textContent = 'Full history is not loaded automatically. You can browse individual months without it.';
    el.businesses.innerHTML = '<p class="muted">Loading named businesses...</p>';
    document.getElementById('historical-directory-link').hidden = true;
    showMonth();
    updateHistory();
    loadDetail();
    get('/api/businesses?settlement=' + encodeURIComponent(name))
      .then(function (data) {
        if (generation === settlementRequest) { renderBusinesses(data); }
      })
      .catch(function (err) {
        if (generation !== settlementRequest) { return; }
        el.businesses.innerHTML = '<p class="muted">' + esc(err.message) + '</p>';
      });
  }

  function requestHistory() {
    if (!state.detail || detailController || timelineGeneration === settlementRequest) { return; }
    loadTimeline(state.settlement, settlementRequest);
  }

  function loadTimeline(name, generation) {
    if (generation !== settlementRequest || timelineGeneration === generation) { return; }
    timelineGeneration = generation;
    el['load-history'].disabled = true;
    el['load-history'].textContent = 'Computing seven-year price history...';
    el['history-chart'].setAttribute('aria-busy', 'true');
    el['timeline-status'].textContent = 'Computing 84 monthly balances; this may take several minutes and delay other API requests. The loaded dashboard remains visible.';
    get('/api/timeline?settlement=' + encodeURIComponent(name))
      .then(function (data) {
        if (generation !== settlementRequest) { return; }
        state.timeline = data;
        state.first = data.first_month;
        state.last = data.last_month;
        el['place-name'].textContent = data.settlement;
        updateGeneratorLink(data.settlement);
        el['place-blurb'].textContent = data.region + ' - a basket of ' +
          data.basket.map(function (c) { return c.name; }).join(', ');
        el.scrub.min = '0';
        el.scrub.max = String(state.last - state.first);
        renderAnalysis(data.analysis);
        setTimelineEnabled(true);
        el['history-chart'].setAttribute('aria-busy', 'false');
        el['load-history'].textContent = 'Seven-year price history loaded';
        var selected = state.month === null ? state.today : state.month;
        if (selected === null) {
          el['timeline-status'].textContent = '';
          showMonth();
          return;
        }
        var start = Math.max(state.first, Math.min(state.last, selected));
        el['timeline-status'].textContent = start !== selected
          ? 'The selected month is outside this history window; showing the nearest available month.' : '';
        if (state.month !== start) { setMonth(start, true); }
        else { showMonth(); }
      })
      .catch(function (err) {
        if (generation !== settlementRequest) { return; }
        timelineGeneration = 0;
        el['history-chart'].setAttribute('aria-busy', 'false');
        el['load-history'].disabled = !!detailController || !state.detail;
        el['load-history'].textContent = 'Retry seven-year price history';
        el['timeline-status'].textContent = 'Price history unavailable: ' + err.message;
      });
  }

  /* ---------------------------------------------------------------- init */

  function wire() {
    el['load-history'].addEventListener('click', requestHistory);
    el.go.addEventListener('click', function () {
      if (el['place-search'].value.trim()) {
        loadSettlement(el['place-search'].value.trim());
      }
    });
    el['place-search'].addEventListener('change', function () {
      if (el['place-search'].value.trim()) {
        loadSettlement(el['place-search'].value.trim());
      }
    });
    el.scrub.addEventListener('input', function () {
      setMonth(state.first + parseInt(el.scrub.value, 10), false);
    });
    el['step-back'].addEventListener('click', function () {
      setMonth(state.month - 1, true);
    });
    el['step-fwd'].addEventListener('click', function () {
      setMonth(state.month + 1, true);
    });
    el['jump-today'].addEventListener('click', function () {
      if (state.today !== null) { setMonth(state.today, true); }
    });
    el['jump-worst'].addEventListener('click', function () {
      var a = state.timeline && state.timeline.analysis;
      if (a && a.dearest) { setMonth(a.dearest.month, true); }
    });
    el['jump-best'].addEventListener('click', function () {
      var a = state.timeline && state.timeline.analysis;
      if (a && a.cheapest) { setMonth(a.cheapest.month, true); }
    });
    el['category-filter'].addEventListener('change', function () {
      state.category = el['category-filter'].value;
      renderTable();
    });
    el['only-moved'].addEventListener('change', function () {
      state.onlyMoved = el['only-moved'].checked;
      renderTable();
    });
    el['requirements-search'].addEventListener('input', function () {
      state.materialSearch = el['requirements-search'].value;
      renderRequirementsTable();
    });
    el['requirements-filter'].addEventListener('change', function () {
      state.materialFilter = el['requirements-filter'].value;
      renderRequirementsTable();
    });
    el['requirements-table'].addEventListener('click', toggleMaterial);
    el['requirements-download'].addEventListener('click', downloadRequirements);
    el.chart.addEventListener('click', function (event) {
      if (!state.timeline) { return; }
      var box = el.chart.getBoundingClientRect();
      var padL = 48;
      var padR = 12;
      var plotW = box.width - padL - padR;
      var ratio = (event.clientX - box.left - padL) / (plotW || 1);
      ratio = Math.max(0, Math.min(1, ratio));
      setMonth(state.first + Math.round(ratio * (state.last - state.first)), true);
    });
    window.addEventListener('resize', drawChart);
  }

  function start() {
    wire();
    setTimelineEnabled(false);
    setMonthNavigation(false);
    Promise.all([get('/api/bootstrap'), get('/api/chronicle')])
      .then(function (both) {
        var boot = both[0];
        var chron = both[1];
        generatorLocations = boot.settlements;
        if (state.settlement) { updateGeneratorLink(state.settlement); }
        showWorldDate(boot);
        state.today = chron.today;
        var requestedMonth = query('month');
        var parsedMonth = Number(requestedMonth);
        if (!state.settlement) {
          state.month = requestedMonth !== null && requestedMonth.trim() !== '' &&
            Number.isInteger(parsedMonth) && parsedMonth >= 0 ? parsedMonth : state.today;
        }
        el['place-list'].innerHTML = boot.settlements.map(function (s) {
          return '<option value="' + esc(s.name) + '">' + esc(s.region) +
            '</option>';
        }).join('');
        el['category-filter'].innerHTML = '<option value="">All</option>' +
          boot.categories.map(function (c) {
            return '<option value="' + esc(c) + '">' + esc(c) + '</option>';
          }).join('');
        var wanted = query('settlement') || 'Waterdeep';
        if (!state.settlement) {
          el['place-search'].value = wanted;
          loadSettlement(wanted);
        }
      })
      .catch(function (err) {
        if (state.settlement) { return; }
        el['requirements-status'].textContent = 'Could not initialize requirements: ' + err.message;
        setDetailBusy(false);
        say(err.message);
      });
  }

  start();
})();
"""


LOCATION_ASSETS: Dict[str, Tuple[str, str]] = {
    "location.html": (LOCATION_HTML, "text/html; charset=utf-8"),
    "location.css": (LOCATION_CSS, "text/css; charset=utf-8"),
    "location.js": (LOCATION_JS, "application/javascript; charset=utf-8"),
}
