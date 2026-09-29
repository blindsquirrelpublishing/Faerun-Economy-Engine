"""Dedicated product and route detail pages for the market board."""

from typing import Dict, Tuple
from .sourceassets import SOURCING_JS
from .webassets import SEASONAL_JS


DETAIL_CSS = """
body { height: auto; min-height: 100dvh; overflow: auto; background: var(--cp-surface); }
main.detail-shell { display: block; flex: none; min-height: auto; width: 100%; max-width: none; padding: 0 clamp(16px,3%,64px) 48px; margin: 0; background: transparent; box-sizing: border-box; }
.detail-controls { display: flex; flex-wrap: wrap; gap: 10px; align-items: end; padding: 14px 0; border-bottom: 2px solid var(--ink); }
.detail-controls label { display: grid; gap: 4px; color: var(--muted); font-size: 11px; text-transform: uppercase; }
.detail-controls input, .detail-controls select { min-width: 190px; padding: 7px 9px; border: 1px solid var(--line); background: var(--bg); color: var(--ink); font: inherit; }
.detail-title { margin: 22px 0 4px; font-size: 30px; font-weight: 600; }
.detail-subtitle { margin: 0 0 18px; color: var(--muted); }
.detail-grid { display: grid; grid-template-columns: repeat(12, 1fr); gap: 18px; }
.detail-section { grid-column: span 6; border-top: 1px solid var(--line); padding-top: 10px; }
.employees-panel ~ .employees-panel { display: none; }
.detail-section.wide { grid-column: 1 / -1; }
.detail-section h2 { margin: 0 0 8px; font-size: 15px; text-transform: uppercase; }
.facts { display: grid; grid-template-columns: repeat(4, 1fr); border: 1px solid var(--line); }
.fact { min-height: 72px; padding: 10px; border-right: 1px solid var(--line); }
.fact:last-child { border-right: 0; }
.fact b { display: block; font-size: 18px; font-weight: 600; }
.fact span { color: var(--muted); font-size: 11px; text-transform: uppercase; }
.detail-table { width: 100%; border-collapse: collapse; }
.detail-table th, .detail-table td { padding: 7px 8px; border-bottom: 1px solid var(--line-soft); text-align: left; }
.detail-table th { font-size: 11px; text-transform: uppercase; color: var(--muted); }
.detail-table .num { text-align: right; font-variant-numeric: tabular-nums; }
.status { min-height: 22px; padding: 8px 0; color: var(--muted); }
.status.error { color: var(--ink); font-weight: 700; }
.route-leg { display: grid; grid-template-columns: 1fr auto auto auto; gap: 18px; align-items: center; padding: 11px 0; border-bottom: 1px solid var(--line-soft); }
.route-leg b, .route-leg span { display: block; }
.route-leg small { color: var(--muted); }
.empty { color: var(--muted); padding: 16px 0; }
.detail-shell a { color: var(--cp-link); text-underline-offset: 3px; }
.detail-controls { padding: 20px 0; border-bottom: 1px solid var(--cp-border); gap: 16px; }
.detail-controls label { text-transform: none; font-size: 12px; gap: 7px; }
.detail-controls label { flex: 1 1 220px; min-width: 0; }
.detail-controls input, .detail-controls select { font-size: 14px; border-radius: 6px; background: var(--cp-surface-soft); min-width: 0; width: 100%; height: 44px; box-sizing: border-box; }
.detail-controls button { min-height: 44px; padding: 10px 20px; }
.detail-title { font-size: 30px; margin: 28px 0 8px; letter-spacing: 0; font-weight: 600; overflow-wrap: anywhere; }
.detail-subtitle { max-width: 75ch; line-height: 1.7; margin-bottom: 24px; }
.detail-grid { grid-template-columns: repeat(12, minmax(0, 1fr)); gap: 28px; }
.detail-section { min-width: 0; padding-top: 18px; }
.detail-section h2 { font-size: 18px; text-transform: none; margin-bottom: 16px; letter-spacing: 0; }
.facts { border: 0; border-block: 1px solid var(--cp-border); background: linear-gradient(90deg,var(--cp-surface-soft),var(--cp-surface)); }
.fact { padding: 20px 16px; min-width: 0; min-height: 94px; }
.fact b { font-size: 22px; font-variant-numeric: tabular-nums; overflow-wrap: anywhere; line-height: 1.35; margin-bottom: 5px; }
.fact span { text-transform: none; font-size: 12px; }
.detail-section:first-child { border-top: 0; padding-top: 0; }
.table-scroll { overflow: auto; max-height: 65dvh; }
.detail-table th { padding: 12px 10px; background: var(--cp-bg-elevated); letter-spacing: 0; font-size: 10px; }
.detail-table td { padding: 12px 10px; }
.detail-table .num { white-space: nowrap; }
.detail-table td:first-child { font-weight: 600; }
.detail-table tbody tr { cursor: default; }
.detail-table tr.standard-grade { background: var(--cp-accent-soft); box-shadow: inset 3px 0 var(--cp-accent); }
.market-quote { border-left: 3px solid var(--cp-accent); padding-left: 18px; }
.market-quote .fact:first-child b { color: var(--cp-accent); }
.product-specs { display: flex; flex-wrap: wrap; gap: 8px 24px; margin: 0 0 22px; color: var(--cp-text-muted); font-size: 13px; }
.product-specs span { display: inline-flex; gap: 6px; }
.product-specs b { color: var(--cp-text); font-weight: 600; }
.detail-shell .status:empty { display: none; }
.detail-shell .status.error { color: var(--cp-danger); }
.business-detail-shell .detail-controls {
  margin: 18px 0 26px;
  padding: 18px;
  border: 1px solid var(--cp-border);
  border-radius: 18px;
  background: var(--cp-surface-soft);
  box-shadow: 0 8px 24px rgba(25, 35, 45, .10);
}
main.detail-shell.business-detail-shell {
  display: grid;
  grid-template-columns: minmax(250px, 20%) minmax(0, 1fr);
  gap: 24px;
  align-items: start;
}
.business-detail-shell .business-sidebar {
  position: sticky;
  top: 20px;
  min-width: 0;
  padding: 20px 16px;
  background: var(--cp-surface);
  box-sizing: border-box;
}
.business-detail-shell .business-sidebar .detail-controls {
  display: grid;
  margin: 0;
  padding: 0;
  border: 0;
  box-shadow: none;
  background: transparent;
}
.business-detail-shell .business-sidebar input,
.business-detail-shell .business-sidebar select,
.product-detail-shell .product-sidebar input,
.product-detail-shell .product-sidebar select {
  width: calc(100% - 8px);
  margin-inline: 4px;
  border-radius: 12px;
}
.business-detail-shell .business-content { min-width: 0; }
.business-detail-shell .detail-controls input,
.business-detail-shell .detail-controls select {
  border: 1px solid var(--cp-border);
  border-radius: 12px;
  background: var(--cp-surface);
  box-shadow: inset 0 1px 2px rgba(25, 35, 45, .06);
}
.business-detail-shell .detail-controls button {
  border-radius: 12px;
  box-shadow: 0 5px 12px rgba(25, 35, 45, .12);
}
.business-detail-shell .detail-section {
  border: 1px solid var(--cp-border);
  border-radius: 18px;
  padding: 20px;
  background: var(--cp-surface);
  box-shadow: 0 8px 24px rgba(25, 35, 45, .08);
}
.business-detail-shell .detail-section:first-child { padding-top: 20px; }
.business-detail-shell .facts {
  gap: 10px;
  border: 0;
  background: transparent;
}
.business-detail-shell .fact {
  min-height: 82px;
  border: 1px solid var(--cp-border);
  border-radius: 14px;
  background: var(--cp-surface-soft);
  box-shadow: 0 4px 12px rgba(25, 35, 45, .06);
}
.business-detail-shell .detail-table {
  border-collapse: separate;
  border-spacing: 0 8px;
}
.business-detail-shell .detail-table th {
  border: 1px solid var(--cp-border);
  background: var(--cp-surface-soft);
}
.business-detail-shell .detail-table th:first-child { border-radius: 12px 0 0 12px; }
.business-detail-shell .detail-table th:last-child { border-radius: 0 12px 12px 0; }
.business-detail-shell .detail-table td {
  border-top: 1px solid var(--cp-border);
  border-bottom: 1px solid var(--cp-border);
  background: var(--cp-surface);
}
.business-detail-shell .detail-table td:first-child {
  border-left: 1px solid var(--cp-border);
  border-radius: 12px 0 0 12px;
}
.business-detail-shell .detail-table td:last-child {
  border-right: 1px solid var(--cp-border);
  border-radius: 0 12px 12px 0;
}
.route-detail-shell .topbar {
  min-height: 168px;
  background: var(--cp-surface);
  border: 0;
  box-shadow: none;
}
.route-detail-shell .brand h1,
.business-detail-shell .brand h1,
.product-detail-page .brand h1 { font-size: 50px; line-height: 1.05; overflow-wrap: anywhere; }
.route-detail-shell .worldbar {
  display: grid;
  grid-template-columns: 1fr;
  justify-items: end;
  gap: 12px;
}
.route-detail-shell .date-controls,
.route-detail-shell .nav-links {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: flex-end;
  gap: 10px;
}
.route-detail-shell .date-controls,
.route-detail-shell .nav-links { grid-column: 1; }
.route-detail-shell .navlink {
  display: inline-flex;
  align-items: center;
  border: 1px solid var(--cp-border);
  border-radius: 10px;
  background: var(--cp-surface-soft);
  color: var(--cp-text);
  padding: 8px 12px;
  box-shadow: 0 3px 8px rgba(25, 35, 45, .06);
}
.route-detail-shell .navlink:hover {
  border-color: var(--cp-accent);
  background: var(--cp-accent-soft);
  color: var(--cp-accent);
}
main.detail-shell.route-detail-content {
  display: grid;
  grid-template-columns: minmax(250px, 20%) minmax(0, 1fr);
  gap: 24px;
  align-items: start;
}
.route-detail-content .route-sidebar {
  position: sticky;
  top: 20px;
  min-width: 0;
  padding: 20px 16px;
  background: var(--cp-surface);
  box-sizing: border-box;
}
.route-detail-content .route-sidebar .detail-controls {
  display: grid;
  margin: 0;
  padding: 0;
  border: 0;
  box-shadow: none;
  background: transparent;
}
.route-detail-content .route-sidebar input,
.route-detail-content .route-sidebar select { width: calc(100% - 8px); margin-inline: 4px; border-radius: 12px; }
.route-detail-content .route-content { min-width: 0; }
.route-detail-shell [data-world-date],
body > .topbar [data-world-date] { font-size: 20px; padding: 10px 16px; }
.product-detail-page .worldbar {
  display: grid;
  grid-template-columns: 1fr;
  align-items: center;
  justify-items: stretch;
  width: min(100%, 1120px);
  gap: 12px;
}
.product-detail-page .detail-controls {
  display: flex;
  flex-wrap: wrap;
  align-items: end;
  justify-content: flex-end;
  gap: 10px;
  margin: 0;
  padding: 0;
  border: 0;
  box-shadow: none;
  background: transparent;
}
.product-detail-page .detail-controls label {
  flex: 0 1 194px;
  min-width: 150px;
  color: var(--cp-text);
  font-size: 12px;
}
.product-detail-page .detail-controls input {
  height: 44px;
  box-sizing: border-box;
}
.product-detail-page .detail-controls button {
  min-height: 44px;
  padding: 10px 16px;
}
.product-detail-page .date-controls {
  order: 2;
  justify-self: end;
  grid-column: 1;
}
.product-detail-page .detail-controls { order: 1; }
.product-detail-page .nav-links {
  order: 3;
  grid-column: 1 / -1;
  justify-self: end;
}
.product-detail-page .date-controls,
.product-detail-page .nav-links {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: flex-end;
  gap: 10px;
}
.product-detail-page .navlink {
  display: inline-flex;
  align-items: center;
  border: 1px solid var(--cp-border);
  border-radius: 10px;
  background: var(--cp-surface-soft);
  color: var(--cp-text);
  padding: 8px 12px;
  box-shadow: 0 3px 8px rgba(25, 35, 45, .06);
}
.product-detail-page .navlink:hover {
  border-color: var(--cp-accent);
  background: var(--cp-accent-soft);
  color: var(--cp-accent);
}
.product-detail-page .topbar {
  display: grid;
  grid-template-columns: minmax(220px, 1fr) minmax(0, 1120px);
  align-items: start;
}
@media (max-width: 760px) {
  main.detail-shell.route-detail-content { display: block; }
  .route-detail-content .route-sidebar { position: static; margin-bottom: 24px; }
  .business-detail-shell { display: block; }
  .business-detail-shell .business-sidebar { position: static; margin-bottom: 24px; }
  .route-detail-shell .worldbar,
  .route-detail-shell .worldbar,
  .route-detail-shell .date-controls,
  .route-detail-shell .nav-links {
    justify-content: flex-start;
    justify-items: start;
    width: 100%;
  }
  .product-detail-page .topbar { display: flex; }
  .product-detail-page .worldbar { width: 100%; grid-template-columns: 1fr; }
  .product-detail-page .date-controls,
  .product-detail-page .nav-links { justify-self: start; grid-column: auto; }
}
.business-detail-shell .inventory-panel,
.business-detail-shell .employees-panel { background: var(--cp-surface-soft); }
.product-detail-shell .detail-controls {
  margin: 18px 0 26px;
  padding: 18px;
  border: 1px solid var(--cp-border);
  border-radius: 18px;
  background: var(--cp-surface-soft);
  box-shadow: 0 8px 24px rgba(25, 35, 45, .10);
}
.product-detail-shell .detail-controls input,
.product-detail-shell .detail-controls select {
  border: 1px solid var(--cp-border);
  border-radius: 12px;
  background: var(--cp-surface);
  box-shadow: inset 0 1px 2px rgba(25, 35, 45, .06);
}
.product-detail-shell .detail-controls button {
  border-radius: 12px;
  box-shadow: 0 5px 12px rgba(25, 35, 45, .12);
}
.product-detail-shell .detail-title {
  max-width: 38ch;
  margin-top: 30px;
  font-size: clamp(28px, 4vw, 42px);
  line-height: 1.1;
}
.product-detail-shell .detail-subtitle { max-width: 72ch; }
main.detail-shell.product-detail-shell {
  display: grid;
  grid-template-columns: minmax(250px, 20%) minmax(0, 1fr);
  gap: 24px;
  align-items: start;
}
.product-detail-shell .product-sidebar {
  position: sticky;
  top: 20px;
  min-width: 0;
  padding: 20px 16px;
  background: var(--cp-surface);
  box-sizing: border-box;
}
.product-detail-shell .product-sidebar .detail-controls {
  display: grid;
  margin: 0;
  padding: 0;
  border: 0;
  box-shadow: none;
  background: transparent;
}
.product-detail-shell .product-content,
.business-detail-shell .business-content { min-width: 0; }
.product-content .detail-title,
.business-content .detail-title {
  margin: 0 0 12px;
  padding: 18px 20px;
  border: 1px solid var(--cp-border);
  border-radius: 16px;
  background: var(--cp-surface-soft);
  box-shadow: 0 6px 18px rgba(25, 35, 45, .07);
}
.product-detail-shell .detail-section {
  border: 1px solid var(--cp-border);
  border-radius: 18px;
  padding: 20px;
  background: var(--cp-surface);
  box-shadow: 0 8px 24px rgba(25, 35, 45, .08);
}
.product-detail-shell .detail-section:first-child { padding-top: 20px; }
.product-detail-shell .detail-section h2 { font-size: 18px; margin-bottom: 16px; }
.product-detail-shell .product-specs {
  margin-bottom: 18px;
  padding-bottom: 16px;
  border-bottom: 1px solid var(--cp-border);
}
.product-detail-shell .facts {
  gap: 10px;
  border: 0;
  background: transparent;
}
.product-detail-shell .fact {
  min-height: 82px;
  border: 1px solid var(--cp-border);
  border-radius: 14px;
  background: var(--cp-surface-soft);
  box-shadow: 0 4px 12px rgba(25, 35, 45, .06);
}
.product-detail-shell .market-quote {
  border: 1px solid var(--cp-border);
  border-left: 4px solid var(--cp-accent);
  border-radius: 14px;
  padding: 18px;
  background: var(--cp-surface-soft);
}
.product-detail-shell .market-quote .facts { margin-top: 14px; }
.product-detail-shell .detail-table {
  border-collapse: separate;
  border-spacing: 0 8px;
}
.product-detail-shell .detail-table th {
  border: 1px solid var(--cp-border);
  background: var(--cp-surface-soft);
}
.product-detail-shell .detail-table th:first-child { border-radius: 12px 0 0 12px; }
.product-detail-shell .detail-table th:last-child { border-radius: 0 12px 12px 0; }
.product-detail-shell .detail-table td {
  border-top: 1px solid var(--cp-border);
  border-bottom: 1px solid var(--cp-border);
  background: var(--cp-surface);
}
.product-detail-shell .detail-table td:first-child {
  border-left: 1px solid var(--cp-border);
  border-radius: 12px 0 0 12px;
}
.product-detail-shell .detail-table td:last-child {
  border-right: 1px solid var(--cp-border);
  border-radius: 0 12px 12px 0;
}
.product-detail-shell .empty { padding: 24px 8px; }
@media (max-width: 760px) {
  main.detail-shell.product-detail-shell { display: block; }
  .product-detail-shell .product-sidebar { position: static; margin-bottom: 24px; }
  main.detail-shell { width: calc(100% - 32px); }
  .detail-title { font-size: 28px; }
  .detail-controls { align-items: stretch; gap: 12px; }
  .detail-controls label { flex: 1 1 100%; min-width: 0; }
  .detail-controls input, .detail-controls select { min-width: 0; width: 100%; }
  .detail-table { min-width: 460px; }
  .fact { padding: 16px 12px; border-bottom: 1px solid var(--cp-border); }
  .fact b { font-size: 19px; }
  .detail-grid { display: block; }
  .detail-section { margin-top: 20px; }
  .facts { grid-template-columns: repeat(2, 1fr); }
  .fact:nth-child(2) { border-right: 0; }
  .route-leg { grid-template-columns: minmax(0,1fr) minmax(0,1fr); }
}
  .route-leg > div { min-width: 0; overflow-wrap: anywhere; }
  .route-leg > div:first-child { border-left: 3px solid var(--cp-accent); padding-left: 14px; }
  .route-leg { padding: 18px 0; }
  @media (max-width: 760px) {
    main.detail-shell { width: 100%; }
    .detail-controls input, .detail-controls select { font-size: 16px; }
    .detail-controls button { width: 100%; }
    .detail-section:has(> .detail-table) { overflow-x: auto; }
  }
"""


PRODUCT_HTML = """<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Faerun Product Detail</title><link rel="stylesheet" href="app.css"><link rel="stylesheet" href="detail.css"></head>
<body class="product-detail-page"><header class="topbar"><div class="brand"><span class="mark">&#9670;</span><div><h1>Product Detail</h1><p class="tagline">Composition, quality, production and market access.</p></div></div>
<div class="worldbar"><div class="date-controls"><span class="pill" data-world-date>&#8230;</span></div><nav class="nav-links" aria-label="Main navigation"><a class="navlink" href="index.html">Markets</a><a class="navlink" href="location.html">Locations</a><a class="navlink" href="business.html">Businesses</a><span class="navlink navlink-current" aria-current="page">Products</span><a class="navlink" href="route.html">Routes</a><a class="navlink" href="map.html">Map</a><a class="navlink" href="planner.html">Route planner</a><a class="navlink" href="mobile.html">Travelling companies</a><a class="navlink" href="trade.html">Merchant guild &amp; POs</a><a class="navlink" href="board.html">Request board</a></nav></div></header>
<main class="detail-shell product-detail-shell"><aside class="product-sidebar"><form id="controls" class="detail-controls"><label>Product<input id="product" list="products" autocomplete="off"></label><datalist id="products"></datalist><label>Market<input id="market" list="markets" autocomplete="off"></label><datalist id="markets"></datalist><button class="primary" type="submit">Open</button><button id="rebuild" type="button" title="Reload commodities, settlements and businesses added or edited since this server started">Rebuild catalog</button></form></aside><div class="product-content">
<div id="status" class="status" role="status">Loading product details...</div><h1 id="title" class="detail-title">Product</h1><p id="subtitle" class="detail-subtitle"></p><div id="content" class="detail-grid"></div></div></main><script src="date.js"></script><script src="product.js"></script></body></html>"""


ROUTE_HTML = """<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Faerun Route Detail</title><link rel="stylesheet" href="app.css"><link rel="stylesheet" href="detail.css"></head>
<body class="route-detail-shell"><header class="topbar"><div class="brand"><span class="mark">&#8644;</span><div><h1>Route Detail</h1><p class="tagline">Carriage time, freight, hazards and every transfer.</p></div></div>
<div class="worldbar"><div class="date-controls"><span class="pill" data-world-date>&#8230;</span></div><nav class="nav-links" aria-label="Main navigation"><a class="navlink" href="index.html">Markets</a><a class="navlink" href="location.html">Locations</a><a class="navlink" href="business.html">Businesses</a><a class="navlink" href="product.html">Products</a><span class="navlink navlink-current" aria-current="page">Routes</span><a class="navlink" href="map.html">Map</a><a class="navlink" href="planner.html">Route planner</a><a class="navlink" href="mobile.html">Travelling companies</a><a class="navlink" href="trade.html">Merchant guild &amp; POs</a><a class="navlink" href="board.html">Request board</a></nav></div></header>
<main class="detail-shell route-detail-content"><aside class="route-sidebar"><form id="controls" class="detail-controls"><label>Origin<input id="origin" list="places" autocomplete="off"></label><label>Destination<input id="destination" list="places" autocomplete="off"></label><datalist id="places"></datalist><label>Optimize<select id="optimise"><option value="days">Travel time</option><option value="cost">Freight cost</option></select></label><button class="primary" type="submit">Plan route</button></form></aside><div class="route-content">
<div id="status" class="status"></div><h1 id="title" class="detail-title">Route</h1><p id="subtitle" class="detail-subtitle"></p><div id="content" class="detail-grid"></div></div></main><script src="date.js"></script><script src="route.js"></script></body></html>"""


BUSINESS_HTML = """<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Faerun Business Detail</title><link rel="stylesheet" href="app.css"><link rel="stylesheet" href="detail.css"></head>
<body><header class="topbar"><div class="brand"><span class="mark">&#9670;</span><div><h1>Business Detail</h1><p class="tagline">Ability scores, skills, branches and market offers.</p></div></div>
<div class="worldbar"><div class="date-controls"><span class="pill" data-world-date>&#8230;</span></div><nav class="nav-links" aria-label="Main navigation"><a class="navlink" href="index.html">Markets</a><a class="navlink" href="location.html">Locations</a><span class="navlink navlink-current" aria-current="page">Businesses</span><a class="navlink" href="product.html">Products</a><a class="navlink" href="route.html">Routes</a><a class="navlink" href="map.html">Map</a><a class="navlink" href="planner.html">Route planner</a><a class="navlink" href="mobile.html">Travelling companies</a><a class="navlink" href="trade.html">Merchant guild &amp; POs</a><a class="navlink" href="board.html">Request board</a></nav></div></header>
<main class="detail-shell business-detail-shell"><aside class="business-sidebar"><form id="controls" class="detail-controls"><label>Business type<select id="business-type"><option value="">All types</option></select></label><label>Business<select id="business"></select></label><label>Market for offers<input id="market" list="markets" autocomplete="off"></label><datalist id="markets"></datalist><button class="primary" type="submit">Open</button></form></aside><div class="business-content">
<div id="status" class="status">Loading business details...</div><h1 id="title" class="detail-title">Business</h1><p id="subtitle" class="detail-subtitle"></p><div id="content" class="detail-grid"></div></div></main><script src="date.js"></script><script src="business.js"></script></body></html>"""


COMMON_JS = """
function esc(v){return String(v==null?'':v).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/\"/g,'&quot;');}
function coin(v){if(v==null)return '-';var digits=Math.abs(v)<1?3:2;return Number(v).toLocaleString(undefined,{minimumFractionDigits:digits,maximumFractionDigits:3})+' gp';}
function markup(v){return Number.isFinite(v)?v.toFixed(1)+'%':'-';}
function stockUnits(v){return Number.isFinite(v)?v.toLocaleString():'-';}
function query(k){return new URLSearchParams(location.search).get(k)||'';}
async function get(path,params){var u=new URL(path,location.origin);Object.keys(params||{}).forEach(function(k){if(params[k])u.searchParams.set(k,params[k]);});var r=await fetch(u);var d=await r.json();if(!r.ok)throw new Error(d.error||r.statusText);return d;}
async function post(path,body){var r=await fetch(path,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body||{})});var d=await r.json();if(!r.ok)throw new Error(d.error||r.statusText);return d;}
function fact(label,value){return '<div class="fact"><b>'+esc(value)+'</b><span>'+esc(label)+'</span></div>';}
function setStatus(text,error){var e=document.getElementById('status');e.textContent=text||'';e.className='status'+(error?' error':'');}
"""


PRODUCT_JS = COMMON_JS + SOURCING_JS + SEASONAL_JS + """
var boot=null;
function table(headers,rows){return '<div class="table-scroll" tabindex="0" role="region" aria-label="Scrollable product table"><table class="detail-table"><thead><tr>'+headers.map(function(h){return '<th>'+esc(h)+'</th>';}).join('')+'</tr></thead><tbody>'+rows.join('')+'</tbody></table></div>';}
async function load(){var product=document.getElementById('product').value||'spellbook_blank';var market=document.getElementById('market').value||'Waterdeep';setStatus('Loading product and market...');try{var both=await Promise.all([get('/api/product',{commodity:product,settlement:market}),get('/api/market',{settlement:market})]);var data=both[0],quote=both[1].prices.find(function(q){return q.commodity===data.commodity.id;});if(!quote)throw new Error('Product is not quoted in this market.');history.replaceState(null,'','product.html?commodity='+encodeURIComponent(data.commodity.id)+'&settlement='+encodeURIComponent(quote.settlement));document.getElementById('product').value=data.commodity.name;document.getElementById('market').value=quote.settlement;document.getElementById('title').textContent=data.commodity.name;document.getElementById('subtitle').textContent=data.commodity.description||data.commodity.category+' traded by the '+data.commodity.unit+'.';
var bom=Object.entries(data.commodity.bom||{}).map(function(entry){var c=data.components[entry[0]];return '<tr><td><a href="product.html?commodity='+encodeURIComponent(entry[0])+'&settlement='+encodeURIComponent(quote.settlement)+'">'+esc(c.name)+'</a></td><td class="num">'+entry[1].toLocaleString()+'</td><td>'+esc(c.unit)+'</td></tr>';});
var qualities=(quote.quality_offers||[]).map(function(o){return '<tr'+(o.quality==='standard'?' class="standard-grade"':'')+'><td>'+esc(o.quality)+'</td><td class="num">'+coin(o.price)+'</td><td class="num">'+coin(o.buy_price)+'</td><td class="num">'+markup(o.merchant_markup_pct)+'</td><td>'+esc(o.availability)+'</td><td class="num">'+o.stock.toLocaleString()+'</td><td class="num">'+stockUnits(o.uncommitted_stock)+'</td></tr>';});
var sources=data.sourcing.sources.map(function(s){return '<tr><td><a href="location.html?settlement='+encodeURIComponent(s.id)+'">'+esc(s.name)+'</a></td><td>'+esc(s.region)+'</td><td>'+esc(s.quality)+'</td><td class="num">'+s.production_per_day.toLocaleString()+'</td></tr>';});
var standard=(quote.quality_offers||[]).find(function(offer){return offer.quality==='standard';})||quote;
var seasonal=seasonalPanel(quote,data.seasonal_inventory?data.seasonality:null);
var special=data.special_order;
var specialOrderHtml='';
if (special && special.needed) {
  specialOrderHtml = special.available
    ? '<div class="market-quote"><h2>Special order</h2><p>Not carried in stock here. The merchant can special-order it from <b>'+esc(special.source)+'</b> ('+esc(special.source_days)+' days away).</p><div class="facts">'+fact('Special order price / '+esc(special.unit),coin(special.special_order_price))+fact('Lead time',special.lead_time_days+' days')+fact('Rush surcharge',markup(special.rush_premium_pct))+'</div></div>'
    : '<div class="market-quote"><h2>Special order</h2><p>Not carried in stock here, and no reachable supplier currently has uncommitted stock to special-order.</p></div>';
}
document.getElementById('content').innerHTML='<section class="detail-section wide"><div class="product-specs"><span>Category <b>'+esc(data.commodity.category)+'</b></span><span>Trade unit <b>'+esc(data.commodity.unit)+'</b></span><span>Weight <b>'+esc(data.commodity.weight)+' lb</b></span><span>Type <b>'+esc(data.commodity.production_type)+'</b></span><span>Base price <b>'+esc(coin(data.commodity.base_price))+'</b></span></div><div class="market-quote"><h2>Standard grade in '+esc(quote.settlement)+'</h2><div class="facts">'+fact('Buy from merchant / '+data.commodity.unit,coin(standard.price))+fact('Sell to merchant / '+data.commodity.unit,coin(standard.buy_price==null?quote.buy_price:standard.buy_price))+fact('Merchant markup',markup(standard.merchant_markup_pct))+fact('Availability',standard.availability)+fact('Modeled grade stock',Number(standard.stock).toLocaleString())+fact('Uncommitted grade stock',stockUnits(standard.uncommitted_stock))+'</div><p>Markup is quoted resale price divided by the merchant purchase offer, minus one; it is before costs and losses. '+esc(seasonalFreeBasis(quote))+'</p><p>'+esc(seasonalStockBasis(quote))+'</p></div>'+specialOrderHtml+'</section>'+
(seasonal?'<section class="detail-section wide">'+seasonal+'</section>':'')+
'<section class="detail-section"><h2>Crafting inputs per '+esc(data.commodity.unit)+'</h2>'+(bom.length?table(['Component','Quantity','Unit'],bom):'<p class="empty">No component BOM: this good is directly gathered, raised or extracted.</p>')+'</section>'+
'<section class="detail-section"><h2>Quality in '+esc(quote.settlement)+'</h2>'+table(['Grade','Buy from merchant','Sell to merchant','Markup','Availability','Stock estimate','Uncommitted'],qualities)+'<p>Grade quantities partition one shared market pool; do not add alternatives or treat them as reserved orders.</p><p><a href="location.html?settlement='+encodeURIComponent(quote.settlement)+'">Open location detail</a></p></section>'+
'<section class="detail-section wide"><h2>Supply in '+esc(quote.settlement)+'</h2>'+sourceBreakdown(quote)+'</section>'+
'<section class="detail-section wide"><h2>Production centers</h2>'+table(['Location','Region','Reputation','Output / day'],sources)+'</section>';setStatus('');}catch(e){setStatus(e.message,true);}}
async function start(){
  document.getElementById('product').value=query('commodity')||'Blank spellbook';
  document.getElementById('market').value=query('settlement')||'Waterdeep';
  setStatus('Loading product details. First-time market calculations can take a while.');
  boot=await get('/api/bootstrap');
  showWorldDate(boot);
  document.getElementById('products').innerHTML=boot.commodities.map(function(c){return '<option value="'+esc(c.name)+'">'+esc(c.category)+'</option>';}).join('');
  document.getElementById('markets').innerHTML=boot.settlements.map(function(s){return '<option value="'+esc(s.name)+'">'+esc(s.region)+'</option>';}).join('');
  await load();
}
document.getElementById('controls').addEventListener('submit',function(e){e.preventDefault();load();});
document.getElementById('rebuild').addEventListener('click',async function(){setStatus('Reloading catalog from disk...');try{var r=await post('/api/rebuild',{});boot=r;var counts=r.reloaded;document.getElementById('products').innerHTML=boot.commodities.map(function(c){return '<option value="'+esc(c.name)+'">'+esc(c.category)+'</option>';}).join('');document.getElementById('markets').innerHTML=boot.settlements.map(function(s){return '<option value="'+esc(s.name)+'">'+esc(s.region)+'</option>';}).join('');await load();setStatus('Reloaded '+counts.commodities+' commodities, '+counts.settlements+' settlements, '+counts.businesses+' businesses.');}catch(e){setStatus(e.message,true);}});
start().catch(function(e){setStatus(e.message,true);});
"""


ROUTE_JS = COMMON_JS + """
var carrierPlanner=document.getElementById('carrier-planner');if(carrierPlanner)carrierPlanner.addEventListener('click',function(){this.href='planner.html?'+new URLSearchParams({origin:document.getElementById('origin').value||'Waterdeep',destination:document.getElementById('destination').value||'Daggerford'});});
async function load(){var origin=document.getElementById('origin').value||'Waterdeep';var destination=document.getElementById('destination').value||'Daggerford';var optimise=document.getElementById('optimise').value;setStatus('Planning route...');try{var d=await get('/api/route',{origin:origin,destination:destination,optimise:optimise});if(!d.reachable)throw new Error('No route connects these settlements.');history.replaceState(null,'','route.html?origin='+encodeURIComponent(d.origin)+'&destination='+encodeURIComponent(d.destination)+'&optimise='+optimise);document.getElementById('origin').value=d.origin;document.getElementById('destination').value=d.destination;document.getElementById('title').textContent=d.origin+' to '+d.destination;document.getElementById('subtitle').textContent='Optimized for '+(optimise==='cost'?'freight cost':'travel time')+'.';var legs=d.legs.map(function(l,i){return '<div class="route-leg"><div><b>'+(i+1)+'. '+esc(l.from)+' to '+esc(l.to)+'</b><small>'+esc(l.via||'local track')+' · '+esc(l.mode_label)+'</small></div><div><b>'+Math.round(l.miles).toLocaleString()+' mi</b><small>distance</small></div><div><b>'+Number(l.days).toFixed(1)+' days</b><small>travel</small></div><div><b>'+Number(l.hazard).toFixed(2)+'x</b><small>hazard</small></div></div>';}).join('');document.getElementById('content').innerHTML='<section class="detail-section wide"><div class="facts">'+fact('Distance',Math.round(d.distance).toLocaleString()+' mi')+fact('Travel time',Number(d.days).toFixed(1)+' days')+fact('Freight / 100 lb',coin(d.freight_gp_per_100lb))+fact('Hazard',Number(d.hazard).toFixed(2)+'x')+'</div></section><section class="detail-section wide"><h2>Itinerary</h2>'+legs+'</section><section class="detail-section"><h2>Route profile</h2><div class="facts">'+fact('Modes',d.modes.join(' + '))+fact('Transfers',d.transfers)+fact('Caravan time',Number(d.caravan_days).toFixed(1)+' days')+fact('Stops',d.path.length)+'</div></section><section class="detail-section"><h2>Endpoints</h2><p><a href="location.html?settlement='+encodeURIComponent(d.origin)+'">'+esc(d.origin)+'</a> to <a href="location.html?settlement='+encodeURIComponent(d.destination)+'">'+esc(d.destination)+'</a></p><p><a href="map.html?'+new URLSearchParams({planOrigin:d.origin,planDestination:d.destination,planOptimise:optimise})+'">View this route on the map &rarr;</a></p></section>';setStatus('');}catch(e){setStatus(e.message,true);}}
async function start(){var boot=await get('/api/bootstrap');showWorldDate(boot);document.getElementById('places').innerHTML=boot.settlements.map(function(s){return '<option value="'+esc(s.name)+'">'+esc(s.region)+'</option>';}).join('');document.getElementById('origin').value=query('origin')||'Waterdeep';document.getElementById('destination').value=query('destination')||'Daggerford';document.getElementById('optimise').value=query('optimise')||'days';load();}
document.getElementById('controls').addEventListener('submit',function(e){e.preventDefault();load();});start().catch(function(e){setStatus(e.message,true);});
"""


BUSINESS_JS = COMMON_JS + """
var boot=null, businessCatalog=[];
function businessType(b){if(b.carrier_service_id)return 'Carrier';var text=(b.name+' '+(b.specialties||[]).join(' ')+' '+(b.services||[]).join(' ')).toLowerCase();if(text.indexOf('warehouse')>=0)return 'Warehouse';if(text.indexOf('brew')>=0||text.indexOf('bak')>=0||text.indexOf('inn')>=0||text.indexOf('lodg')>=0||text.indexOf('spirits')>=0)return 'Hospitality';if(Object.keys(b.offers||{}).length)return 'Trader';if(text.indexOf('forge')>=0||text.indexOf('arm')>=0||text.indexOf('smith')>=0||text.indexOf('workshop')>=0||text.indexOf('manufact')>=0)return 'Workshop';return 'Service';}
function renderBusinessOptions(){var type=document.getElementById('business-type').value;var current=document.getElementById('business').value;var rows=businessCatalog.filter(function(b){return !type||businessType(b)===type;}).sort(function(a,b){return a.name.localeCompare(b.name);});document.getElementById('business').innerHTML=rows.map(function(b){return '<option value="'+esc(b.id)+'">'+esc(b.name)+'</option>';}).join('');if(rows.some(function(b){return b.id===current;}))document.getElementById('business').value=current;else if(rows.length)document.getElementById('business').value=rows[0].id;}
async function renderBusinessInventory(){var content=document.getElementById('content');if(!content||content.querySelector('.inventory-panel'))return;var raw=document.getElementById('business').value||query('business');if(!raw)return;try{var d=(await get('/api/business',{business:raw,settlement:document.getElementById('market').value||'Waterdeep'})).business;var sections=(d.locations_detail||[]).map(function(location){var rows=Object.entries(location.inventory||{}).map(function(entry){return '<tr><td>'+esc(titleCase(entry[0]))+'</td><td class="num">'+stockUnits(entry[1])+'</td></tr>';});return '<section class="detail-section inventory-panel"><h2>'+esc(location.name)+' inventory</h2><p class="product-specs"><span>Role <b>'+esc(location.id===d.headquarters?'Headquarters':'Branch')+'</b></span><span>Mode <b>'+esc(d.location_mode||'fixed')+'</b></span></p>'+table(['Commodity','Units'],rows)+'</section>';}).join('');if(sections)content.insertAdjacentHTML('beforeend',sections);}catch(e){}}
async function renderBusinessEmployees(){var content=document.getElementById('content');if(!content||content.querySelector('.employees-panel')||content.dataset.employeesRendered)return;content.dataset.employeesRendered='pending';var raw=document.getElementById('business').value||query('business');if(!raw)return;try{var d=(await get('/api/business',{business:raw,settlement:document.getElementById('market').value||'Waterdeep'})).business;var rows=(d.employee_roster||[]).map(function(worker){return '<tr><td>'+esc(worker.class)+'</td><td class="num">'+worker.level+'</td><td class="num">'+worker.count+'</td></tr>';});if(rows.length)content.insertAdjacentHTML('beforeend','<section class="detail-section employees-panel"><h2>Employees</h2><p class="product-specs"><span>Total staff <b>'+stockUnits(d.employee_total)+'</b></span></p>'+table(['Class','Level','Count'],rows)+'</section>');}catch(e){}}
async function renderBusinessAddresses(){var content=document.getElementById('content');var section=Array.from(content.querySelectorAll('.detail-section')).find(function(item){var heading=item.querySelector('h2');return heading&&heading.textContent==='Locations';});if(!section||section.dataset.addressesRendered)return;section.dataset.addressesRendered='pending';var raw=document.getElementById('business').value||query('business');try{var d=(await get('/api/business',{business:raw,settlement:document.getElementById('market').value||'Waterdeep'})).business;var tableNode=section.querySelector('table');if(!tableNode)return;section.dataset.addressesRendered='1';tableNode.tHead.rows[0].insertAdjacentHTML('beforeend','<th>Address</th>');Array.from(tableNode.tBodies[0].rows).forEach(function(row,index){var location=d.locations_detail[index];var address=location&&location.address||{};row.insertAdjacentHTML('beforeend','<td>'+esc([address.street,address.district,address.city,address.zip].filter(Boolean).join(', '))+'</td>');});}catch(e){}}
new MutationObserver(function(){renderBusinessInventory();renderBusinessEmployees();renderBusinessAddresses();}).observe(document.getElementById('content'),{childList:true});
function table(headers,rows){return '<div class="table-scroll" tabindex="0"><table class="detail-table"><thead><tr>'+headers.map(function(h){return '<th>'+esc(h)+'</th>';}).join('')+'</tr></thead><tbody>'+rows.join('')+'</tbody></table></div>';}
function titleCase(value){return String(value).replace(/_/g,' ').replace(/\\b\\w/g,function(c){return c.toUpperCase();});}
async function load(){var raw=document.getElementById('business').value||'ironstar_forge_company';var market=document.getElementById('market').value||'Waterdeep';setStatus('Loading business details...');try{var d=(await get('/api/business',{business:raw,settlement:market})).business;history.replaceState(null,'','business.html?business='+encodeURIComponent(d.id)+'&settlement='+encodeURIComponent(d.market_settlement_id));document.getElementById('business').value=d.name;document.getElementById('market').value=d.market_settlement;document.getElementById('title').textContent=d.name;document.getElementById('subtitle').textContent=d.description||'Merchant house or workshop';var scores=Object.entries(d.ability_scores||{}).map(function(e){return fact(e[0],e[1]);}).join('');var skills=Object.entries(d.skills||{}).map(function(e){return '<tr><td>'+esc(titleCase(e[0]))+'</td><td class="num">'+e[1]+'</td></tr>';});var locations=(d.locations_detail||[]).map(function(l){return '<tr><td><a href="location.html?settlement='+encodeURIComponent(l.id)+'">'+esc(l.name)+'</a></td><td>'+ (l.id===d.headquarters?'Headquarters':'Branch') +'</td></tr>';});var offers=(d.offers||[]).map(function(o){return '<tr><td><a href="product.html?commodity='+encodeURIComponent(o.commodity)+'&settlement='+encodeURIComponent(d.market_settlement_id)+'">'+esc(o.commodity_name)+'</a></td><td>'+esc(o.quality)+'</td><td class="num">'+coin(o.price)+'</td><td class="num">'+coin(o.buy_price)+'</td><td class="num">'+stockUnits(o.stock)+'</td></tr>';});document.getElementById('content').innerHTML='<section class="detail-section wide"><div class="facts">'+scores+'</div><p class="product-specs"><span>Headquarters <b>'+esc(d.headquarters_name)+'</b></span><span>Price position <b>'+Number(d.price_modifier).toFixed(2)+'x</b></span><span>Specialties <b>'+esc((d.specialties||[]).join(' / '))+'</b></span></p></section><section class="detail-section"><h2>Business skills</h2>'+table(['Skill','Rating'],skills)+'</section><section class="detail-section"><h2>Locations</h2>'+table(['Settlement','Role'],locations)+'</section><section class="detail-section wide"><h2>Offers in '+esc(d.market_settlement)+'</h2>'+ (offers.length?table(['Commodity','Grade','Sell price','Buy price','Stock'],offers):'<p class="empty">No current offers are available in this market.</p>')+'</section>';setStatus('');}catch(e){setStatus(e.message,true);}}
async function start(){boot=await get('/api/bootstrap');showWorldDate(boot);businessCatalog=boot.businesses||[];var types=[...new Set(businessCatalog.map(businessType))].sort();document.getElementById('business-type').insertAdjacentHTML('beforeend',types.map(function(type){return '<option value="'+esc(type)+'">'+esc(type)+'</option>';}).join(''));document.getElementById('markets').innerHTML=boot.settlements.map(function(s){return '<option value="'+esc(s.name)+'">'+esc(s.region)+'</option>';}).join('');document.getElementById('business').value=query('business')||'ironstar_forge_company';renderBusinessOptions();document.getElementById('market').value=query('settlement')||'Waterdeep';await load();}
document.getElementById('business-type').addEventListener('change',function(){renderBusinessOptions();load();});
document.getElementById('controls').addEventListener('submit',function(e){e.preventDefault();load();});start().catch(function(e){setStatus(e.message,true);});
"""


DETAIL_ASSETS: Dict[str, Tuple[str, str]] = {
    "product.html": (PRODUCT_HTML, "text/html; charset=utf-8"),
    "product.js": (PRODUCT_JS, "application/javascript; charset=utf-8"),
    "route.html": (ROUTE_HTML, "text/html; charset=utf-8"),
    "route.js": (ROUTE_JS, "application/javascript; charset=utf-8"),
    "business.html": (BUSINESS_HTML, "text/html; charset=utf-8"),
    "business.js": (BUSINESS_JS, "application/javascript; charset=utf-8"),
    "detail.css": (DETAIL_CSS, "text/css; charset=utf-8"),
}