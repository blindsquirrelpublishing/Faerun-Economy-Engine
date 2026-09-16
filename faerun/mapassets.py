"""The 3D world map page served by `faerun.web`.

Same trick as `webassets.py`: the page is kept as Python strings so the UI
travels with the package and needs no package-data configuration.

The renderer is deliberately plain Canvas 2D rather than WebGL. It projects the
heightfield from `faerun.mapdata` by hand and paints the cells back to front,
which needs no shaders, no context loss handling and no third-party library -
in keeping with the rest of the project, the whole thing is dependency free.
"""

from __future__ import annotations

from typing import Dict, Tuple

MAP_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Faerun World Map</title>
<link rel="stylesheet" href="app.css">
<link rel="stylesheet" href="map.css">
</head>
<body class="mapbody" data-map-view="overlay">

<header class="topbar">
  <div class="brand">
    <span class="mark">&#9906;</span>
    <div>
      <h1>Faer&ucirc;n World Map</h1>
      <p class="tagline">Surveyed settlements and markets aligned over the high-resolution map.</p>
    </div>
  </div>
  <div class="worldbar">
    <form id="location-search-form" class="locationsearch" role="search">
      <label class="sr-only" for="location-search">Find a location</label>
      <input id="location-search" type="search" list="location-options"
             placeholder="Find location..." autocomplete="off">
      <datalist id="location-options"></datalist>
      <button type="submit" title="Find location" aria-label="Find location">&#128269;</button>
    </form>
    <a class="navlink" href="index.html">&#8592; Commodity board</a>
    <a class="navlink" href="planner.html">Route planner</a>
    <a class="navlink" href="mobile.html">Travelling companies</a>
    <a class="navlink" href="trade.html">Merchant guild &amp; POs</a>
    <a class="navlink" href="waterdeep.html">Waterdeep atlas</a>
    <fieldset class="mapview-switch" aria-label="Base map">
      <legend class="sr-only">Base map</legend>
      <label><input type="radio" name="map-view" value="overlay" checked><span>Poster map</span></label>
      <label><input type="radio" name="map-view" value="terrain"><span>3D terrain</span></label>
    </fieldset>
    <label class="poster-only-control"><input id="poster-only" type="checkbox" disabled title="Available when the poster image has loaded"> Poster only</label>
    <label><input id="opt-route-icons" type="checkbox" checked> Leg icons</label>
    <a class="navlink" id="history-link" href="location.html">Location history &#8594;</a>
    <span id="world-date" class="pill" data-world-date>&#8230;</span>
  </div>
</header>

<div class="maplayout">
  <div class="stage">
    <canvas id="world-canvas"></canvas>

    <div class="hud">
      <details class="mapsettings">
      <summary>Map layers &amp; alignment</summary>
      <div class="hudrow">
        <label>Colour dots by
          <select id="heat-commodity">
            <option value="">Settlement type</option>
          </select>
        </label>
        <label title="Broken lines are multimodal routes: cargo changes carrier along the way, so they cost more and carry more risk."><input type="checkbox" id="opt-routes" checked> Trade routes</label>
        <div class="routefilter"><span>Leg types</span>
          <details id="opt-route-types">
            <summary id="route-type-summary">All types</summary>
            <div class="routefiltermenu">
              <label><input type="checkbox" id="opt-route-all" checked> All types</label>
              <label><input type="checkbox" name="route-type" value="road"> &#8596; Road</label>
              <label><input type="checkbox" name="route-type" value="trail"> &#8226; Foot trail</label>
              <label><input type="checkbox" name="route-type" value="sea"> &#9973; Sea</label>
              <label><input type="checkbox" name="route-type" value="river"> &#8779; River</label>
              <label><input type="checkbox" name="route-type" value="barge"> &#9645; Barge</label>
              <label><input type="checkbox" name="route-type" value="ferry"> &#8644; Ferry</label>
              <label><input type="checkbox" name="route-type" value="portage"> &#8593; Portage</label>
              <label><input type="checkbox" name="route-type" value="tunnel"> &#9673; Tunnel</label>
              <label><input type="checkbox" name="route-type" value="teleport"> &#10022; Teleportation circle</label>
              <label><input type="checkbox" name="route-type" value="air"> &#129413; Gryphon flight</label>
            </div>
          </details>
        </div>
        <label><input type="checkbox" id="opt-labels" checked> Labels</label>
        <label title="Show model-generated connections and roads without surveyed geometry"><input type="checkbox" id="opt-inferred-roads"> Inferred routes</label>
        <label title="Small markets inferred from towns and sites in the surveyed poster. Each has commodity prices and trades through its nearest established hub."><input type="checkbox" id="opt-places" checked> Surveyed markets</label>
        <label title="Show terrain cells within a circular flat-world boundary."><input type="checkbox" id="opt-round-world"> Round world</label>
        <label title="Wrap the map onto a rotatable globe."><input type="checkbox" id="opt-globe"> Globe</label>
        <label>Tiles
          <select id="opt-tiles">
            <option value="smooth">Smooth relief</option>
            <option value="square">Square grid</option>
            <option value="towers">Towers</option>
            <option value="hex3">Hex grid &#8212; coarse</option>
            <option value="hex2">Hex grid &#8212; medium</option>
            <option value="hex1">Hex grid &#8212; fine</option>
            <option value="hexicon3">Icon hexes &#8212; coarse</option>
            <option value="hexicon2">Icon hexes &#8212; medium</option>
            <option value="hexicon1">Icon hexes &#8212; fine</option>
            <option value="hextower3">Hex towers &#8212; coarse</option>
            <option value="hextower2">Hex towers &#8212; medium</option>
            <option value="hextower1">Hex towers &#8212; fine</option>
          </select>
        </label>
        <label>Relief
          <input id="opt-exag" type="range" min="0" max="260" value="0" title="Vertical exaggeration">
        </label>
      </div>
      <div class="hudrow" id="underlay-row" hidden>
        <label title="Drape your own copy of a Faerun poster map over the terrain."><input type="checkbox" id="opt-underlay"> Poster map</label>
        <label>Fade
          <input id="opt-underlay-alpha" type="range" min="0" max="100" value="55" title="Overlay opacity">
        </label>
        <button type="button" id="underlay-align" class="ghost" title="Nudge the poster until its coastlines line up">Align&#8230;</button>
      </div>
      <div class="hudrow" id="underlay-align-row" hidden>
        <label title="Slide the poster east or west, in miles">East
          <input id="opt-underlay-x" type="range" min="-2500" max="2500" step="10" value="-400">
        </label>
        <label title="Slide the poster north or south, in miles">South
          <input id="opt-underlay-y" type="range" min="-2000" max="2500" step="10" value="150">
        </label>
        <label title="Miles of world per poster pixel, x100">Scale
          <input id="opt-underlay-scale" type="range" min="5" max="1200" step="1" value="286">
        </label>
        <label title="Extra north-south stretch, as a percentage">Stretch
          <input id="opt-underlay-stretch" type="range" min="40" max="220" step="1" value="100">
        </label>
        <label title="Follow the relief instead of lying flat"><input type="checkbox" id="opt-underlay-drape" checked> Drape</label>
        <button type="button" id="underlay-survey" class="ghost" title="Snap the poster back to the place the locations survey computes for it">Survey fit</button>
        <button type="button" id="underlay-reset" class="ghost">Reset</button>
      </div>
      <div class="hudrow" id="underlay-readout-row" hidden>
        <span id="underlay-readout" class="hudnote"></span>
      </div>
      <div class="hudrow" id="underlay-none" hidden>
        <span id="underlay-none-text" class="hudnote"></span>
      </div>
      <div class="hudrow" id="calib-row" hidden>
        <label title="Drag the markets onto their true positions on your poster."><input type="checkbox" id="opt-calib"> Realign markets</label>
        <span id="calib-count" class="hudnote"></span>
      </div>
      <div class="hudrow" id="atlas-row" hidden>
        <button type="button" id="atlas-apply" class="ghost" title="Place every market at its surveyed position on your poster">Align from survey</button>
        <span id="atlas-note" class="hudnote"></span>
      </div>
      <div class="hudrow" id="calib-tools" hidden>
        <button type="button" id="calib-undo" class="ghost" title="Drop the last control point">Undo</button>
        <button type="button" id="calib-clear" class="ghost" title="Forget every control point and restore the shipped coordinates">Clear</button>
        <button type="button" id="calib-save" class="ghost" title="Write the new coordinates into the gazetteer">Save</button>
      </div>
      <div class="hudrow" id="calib-help-row" hidden>
        <span id="calib-help" class="hudnote"></span>
      </div>
      <div class="hudrow" id="terrain-edit-row">
        <label title="Click a world-grid cell to correct its terrain type."><input type="checkbox" id="opt-terrain-edit"> Correct terrain</label>
        <label>Set cell to
          <select id="terrain-edit-type">
            <option value="o">Ocean</option>
            <option value="w">Inland water</option>
            <option value="c">Coast</option>
            <option value="p">Plains</option>
            <option value="g">Steppe</option>
            <option value="f">Forest</option>
            <option value="T">Taiga</option>
            <option value="t">Tundra</option>
            <option value="i">Glacier</option>
            <option value="h">Hills</option>
            <option value="m">Mountains</option>
            <option value="d">Desert</option>
            <option value="j">Jungle</option>
            <option value="s">Marsh</option>
            <option value="">Automatic (remove correction)</option>
          </select>
        </label>
        <span id="terrain-edit-help" class="hudnote"></span>
      </div>
      </details>
      <div id="heat-legend" class="heatlegend" hidden></div>
    </div>

    <div class="viewcontrols" aria-label="3D map controls">
      <strong>3D view</strong>
      <button type="button" id="view-tilt" class="ghost">3D oblique</button>
      <button type="button" id="view-top" class="ghost">Top down</button>
      <button type="button" id="view-reset" class="ghost">Reset</button>
    </div>

    <button type="button" id="view-world" class="ghost worldviewcontrol" hidden
            title="Leave local terrain detail and show the whole world">&larr; World view</button>

    <div id="terrain-legend" class="terrainlegend"></div>
    <div id="map-tip" class="maptip" hidden></div>
    <div id="map-status" class="mapstatus">Surveying the Realms&#8230;</div>
  </div>

  <aside class="mappanel">
    <section id="route-selection" class="routeselection" hidden aria-live="polite"></section>
    <div id="place-head" class="placehead">
      <h2>Choose a settlement</h2>
      <p class="muted">Drag to turn the world. Scroll to zoom. Shift-drag (or right-drag) to pan. Click a dot for its market; double-click to zoom in.</p>
    </div>
    <div id="place-stats" class="statgrid"></div>
    <div id="place-notes" class="placenotes"></div>
    <section id="supply-chain" class="supplychain" hidden aria-live="polite"></section>
    <div class="panelctl">
      <input id="goods-search" type="search" placeholder="Filter goods..." autocomplete="off">
      <select id="goods-category"><option value="">All categories</option></select>
    </div>
    <div id="place-prices" class="pricewrap"></div>
  </aside>
</div>

<script src="date.js"></script>
<script src="map.js"></script>
</body>
</html>
"""

TERRAIN_HTML = (
    MAP_HTML
    .replace('data-map-view="overlay"', 'data-map-view="terrain"')
  .replace('value="overlay" checked', 'value="overlay"')
  .replace('value="terrain"><span>', 'value="terrain" checked><span>')
)


MAP_CSS = """
.mapbody { overflow: hidden; }

.maplayout {
  display: flex;
  align-items: stretch;
  height: calc(100vh - 74px);
  min-height: 420px;
}

.stage {
  position: relative;
  flex: 1 1 auto;
  min-width: 0;
  background: #ffffff;
  overflow: hidden;
}

#world-canvas {
  display: block;
  width: 100%;
  height: 100%;
  cursor: grab;
  touch-action: none;
}
#world-canvas.dragging { cursor: grabbing; }
#world-canvas.calibrating { cursor: crosshair; }
#world-canvas.terrain-editing { cursor: cell; }

.locationsearch {
  display: flex;
  align-items: stretch;
  min-width: 190px;
}
.locationsearch input {
  width: 160px;
  min-width: 0;
  padding: 5px 7px;
  border: 1px solid var(--line);
  border-right: 0;
  border-radius: 3px 0 0 3px;
}
.locationsearch button {
  width: 30px;
  padding: 0;
  border: 1px solid var(--line);
  border-radius: 0 3px 3px 0;
  background: #ffffff;
  cursor: pointer;
}
.locationsearch button:hover { border-color: var(--ink); }
.sr-only {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border: 0;
}

.hud {
  position: absolute;
  top: 10px;
  left: 10px;
  display: flex;
  flex-direction: column;
  gap: 6px;
  padding: 8px 10px;
  background: rgba(255, 255, 255, .92);
  border: 1px solid var(--line);
  border-radius: 4px;
  backdrop-filter: blur(3px);
  max-width: 460px;
}
.hudrow { display: flex; flex-wrap: wrap; gap: 10px; align-items: center; }
.hudrow select { max-width: 210px; }
.hudrow input[type=range] { width: 96px; accent-color: var(--ink); }
.routefilter { display: flex; align-items: center; gap: 5px; }
.routefilter details { position: relative; }
.routefilter summary {
  min-width: 92px;
  padding: 4px 24px 4px 7px;
  border: 1px solid #aaa;
  background: #fff;
  cursor: pointer;
  list-style: none;
}
.routefilter summary::-webkit-details-marker { display: none; }
.routefilter summary::after {
  content: '';
  position: absolute;
  top: 50%;
  right: 8px;
  width: 0;
  height: 0;
  border-left: 4px solid transparent;
  border-right: 4px solid transparent;
  border-top: 5px solid #555;
  transform: translateY(-25%);
}
.routefiltermenu {
  position: absolute;
  z-index: 30;
  top: calc(100% + 3px);
  left: 0;
  display: grid;
  min-width: 175px;
  padding: 6px;
  border: 1px solid var(--line);
  background: rgba(255, 255, 255, .98);
  box-shadow: 0 3px 10px rgba(0, 0, 0, .16);
}
.routefiltermenu label { display: flex; gap: 6px; padding: 4px; white-space: nowrap; }
.hudnote { font-size: 11px; color: #666; line-height: 1.5; max-width: 440px; }
.hudnote code { font-size: 11px; background: #f2f2f2; padding: 1px 3px; }

.viewcontrols {
  position: fixed;
  top: 84px;
  right: 410px;
  z-index: 2147483647;
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  align-items: center;
  padding: 8px 10px;
  background: rgba(255, 255, 255, .96);
  border: 2px solid var(--ink);
  border-radius: 4px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, .14);
}
.viewcontrols strong { font-size: 12px; text-transform: uppercase; letter-spacing: .06em; }
.viewcontrols label { display: inline-flex; align-items: center; gap: 5px; }
.viewcontrols input[type=range] { width: 110px; accent-color: var(--ink); }
body[data-map-view="overlay"] .viewcontrols { display: none; }
.worldviewcontrol {
  position: absolute;
  left: 50%;
  bottom: 18px;
  z-index: 20;
  transform: translateX(-50%);
  padding: 9px 14px;
  background: rgba(255, 255, 255, .96);
  border: 2px solid var(--ink);
  box-shadow: 0 2px 10px rgba(0, 0, 0, .16);
}
body[data-map-view="terrain"] #underlay-row,
body[data-map-view="terrain"] #underlay-align-row,
body[data-map-view="terrain"] #underlay-readout-row,
body[data-map-view="terrain"] #underlay-none,
body[data-map-view="terrain"] #calib-row,
body[data-map-view="terrain"] #atlas-row,
body[data-map-view="terrain"] #calib-tools,
body[data-map-view="terrain"] #calib-help-row { display: none !important; }

.navlink {
  color: var(--ink);
  text-decoration: none;
  border: 1px solid var(--line);
  border-radius: 3px;
  padding: 5px 9px;
  font-size: 13px;
}
.navlink:hover { border-color: var(--ink); }

.heatlegend {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 11px;
  color: var(--muted);
}
.heatbar {
  flex: 1 1 auto;
  height: 9px;
  min-width: 120px;
  border-radius: 5px;
  border: 1px solid var(--line);
  background: linear-gradient(to right, #2a9d4b, #e0a51b, #d52323);
}
.heatnone { color: #777777; }

.terrainlegend {
  position: absolute;
  left: 10px;
  bottom: 10px;
  display: flex;
  flex-wrap: wrap;
  gap: 4px 10px;
  max-width: 420px;
  padding: 7px 9px;
  font-size: 11px;
  color: var(--muted);
  background: rgba(255, 255, 255, .9);
  border: 1px solid var(--line);
  border-radius: 4px;
}
.terrainlegend span { display: inline-flex; align-items: center; gap: 5px; }
.terrainlegend i {
  width: 11px; height: 11px; border-radius: 2px;
  border: 1px solid rgba(0, 0, 0, .45);
}

.maptip {
  position: absolute;
  pointer-events: none;
  padding: 5px 8px;
  font-size: 12px;
  color: var(--ink);
  background: rgba(255, 255, 255, .96);
  border: 1px solid var(--ink);
  border-radius: 3px;
  white-space: nowrap;
  transform: translate(-50%, -140%);
  z-index: 4;
}
.maptip b { color: var(--ink); font-weight: 700; }

.mapstatus {
  position: absolute;
  top: 50%; left: 50%;
  transform: translate(-50%, -50%);
  padding: 10px 16px;
  background: rgba(255, 255, 255, .94);
  border: 1px solid var(--line);
  border-radius: 4px;
  color: var(--muted);
}
.mapstatus.error { color: var(--ink); border-color: var(--ink); font-weight: 700; }

.mappanel {
  flex: 0 0 400px;
  max-width: 400px;
  display: flex;
  flex-direction: column;
  gap: 10px;
  padding: 12px;
  overflow-y: auto;
  background: var(--panel);
  border-left: 1px solid var(--line);
}
.placehead h2 { margin: 0; font-size: 19px; color: var(--ink); font-weight: 600; }
.placehead p { margin: 4px 0 0; font-size: 12px; }
.placehead .sub { color: var(--muted); font-size: 12px; }

.routeselection {
  padding: 9px 10px;
  border: 2px solid var(--ink);
  border-radius: 4px;
  background: var(--panel-2);
}
.routeselection h2 { margin: 0 0 7px; font-size: 15px; font-weight: 600; color: var(--ink); }
.routefacts { display: grid; grid-template-columns: 1fr auto auto auto 1fr; gap: 8px; align-items: center; }
.routefacts div:last-child { text-align: right; }
.routefacts b { display: block; font-size: 13px; color: var(--ink); }
.routefacts span { font-size: 10px; text-transform: uppercase; letter-spacing: .06em; color: var(--muted); }
.routedistance, .routetime { min-width: 64px; text-align: center; font-variant-numeric: tabular-nums; }
.routeicon { font-family: "Segoe UI Symbol", sans-serif; font-size: 16px; margin-right: 4px; }
.routelegs { margin: 8px 0 0; padding: 7px 0 0 24px; border-top: 1px solid var(--line); }
.routelegs li { padding: 3px 0 3px 3px; font-size: 12px; color: var(--ink); }
.routelegs small { color: var(--muted); font-variant-numeric: tabular-nums; }
.routecarriers { margin-top: 4px; }
.routecarriers summary { cursor: pointer; color: var(--muted); font-size: 11px; }
.carriertable { width: 100%; margin-top: 5px; border-collapse: collapse; font-variant-numeric: tabular-nums; }
.carriertable th { color: var(--muted); font-size: 9px; font-weight: 600; text-align: right; text-transform: uppercase; }
.carriertable th:first-child, .carriertable td:first-child { text-align: left; }
.carriertable td { padding: 4px 3px; border-top: 1px solid var(--line); font-size: 10px; text-align: right; vertical-align: top; }
.carriertable td b { display: block; font-size: 11px; }
.carriertable td span { color: var(--muted); }
.carrierselect { margin-top: 3px; padding: 2px 5px; border: 1px solid var(--line); border-radius: 3px; background: var(--panel); color: var(--ink); font: inherit; cursor: pointer; }
.carrierselect[aria-pressed="true"] { border-color: var(--accent); background: var(--accent); color: #fff; }
.supplychain { padding: 10px 14px; border-block: 1px solid var(--line); background: var(--panel); }
.supplychain h2 { margin: 0 0 7px; font-size: 15px; color: var(--ink); }
.supplychain ol { margin: 0; padding-left: 20px; }
.supplychain li { padding: 3px 0; font-size: 12px; color: var(--ink); }
.supplychain small { display: block; color: var(--muted); }
.supplychain .raw { color: #39724c; }
.supplychain .processed { color: #9a4d26; }

.statgrid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 6px;
}
.statgrid div {
  background: var(--panel-2);
  border: 1px solid var(--line);
  border-radius: 4px;
  padding: 5px 7px;
}
.statgrid b { display: block; font-size: 13px; color: var(--ink); font-weight: 600; }
.statgrid span { font-size: 10px; text-transform: uppercase; letter-spacing: .06em; color: var(--muted); }

.placenotes { font-size: 12px; color: var(--muted); }
.placenotes .chips { display: flex; flex-wrap: wrap; gap: 4px; margin-top: 6px; }
.chip {
  padding: 2px 7px;
  border-radius: 10px;
  border: 1px solid var(--line);
  background: var(--panel-2);
  font-size: 11px;
}
/* Same weight ramp as the commodity board: grey, black, bold black. */
.chip.cheap { color: var(--muted); border-color: var(--line); }
.chip.dear { color: var(--ink); border-color: var(--ink); font-weight: 700; }
.chip.event { background: var(--ink); border-color: var(--ink); color: #ffffff; }

.panelctl { display: flex; gap: 6px; }
.panelctl input { flex: 1 1 auto; min-width: 0; }

.pricewrap { flex: 1 1 auto; }
.pricewrap table { width: 100%; border-collapse: collapse; font-size: 12px; }
.pricewrap th {
  position: sticky; top: 0;
  text-align: left;
  padding: 5px 6px;
  color: var(--muted);
  font-weight: 500;
  background: var(--panel);
  border-bottom: 2px solid var(--ink);
}
.pricewrap td { padding: 4px 6px; border-bottom: 1px solid var(--line-soft); }
.pricewrap tbody tr { cursor: pointer; }
.pricewrap tbody tr:hover { background: var(--panel-2); }
.pricewrap tbody tr.active { background: var(--panel-2); box-shadow: inset 3px 0 0 var(--ink); }
.pricewrap .num { text-align: right; font-variant-numeric: tabular-nums; }
.pricewrap .up { color: var(--ink); font-weight: 700; }
.pricewrap .down { color: var(--muted); }
.pricewrap .cat { color: var(--muted); font-size: 11px; }
.pricewrap .none { color: var(--muted); font-style: italic; }

@media (max-width: 1000px) {
  .locationsearch { flex: 1 1 190px; }
  .locationsearch input { width: 100%; }
  .maplayout { flex-direction: column; height: auto; }
  .stage { height: 62vh; }
  .mappanel { flex: 1 1 auto; max-width: none; border-left: 0; border-top: 1px solid var(--line); }
  .viewcontrols { right: 10px; }
  .terrainlegend { bottom: 74px; }
}

.maplayout { flex: 1 1 auto; height: auto; min-height: 0; }
body[data-map-view="terrain"] .poster-only-control { display: none; }
body[data-poster-only="true"] .mappanel,
body[data-poster-only="true"] .hud,
body[data-poster-only="true"] .terrainlegend,
body[data-poster-only="true"] .viewcontrols,
body[data-poster-only="true"] .worldviewcontrol { display: none; }
.mapview-switch { display: flex; min-width: 0; margin: 0; padding: 3px; border: 1px solid var(--cp-border); border-radius: 6px; background: var(--cp-surface-soft); }
.mapview-switch label { position: relative; cursor: pointer; }
.mapview-switch input { position: absolute; opacity: 0; width: 1px; height: 1px; }
.mapview-switch span { display: block; padding: 6px 10px; border-radius: 4px; color: var(--cp-text-muted); white-space: nowrap; }
.mapview-switch input:checked + span { background: var(--cp-accent); color: var(--cp-accent-fg); }
.mapview-switch input:focus-visible + span { outline: 2px solid var(--cp-accent); outline-offset: 3px; }
.mapbody .navlink { border-color: transparent; color: var(--cp-text-muted); }
.mapbody .navlink:hover { background: var(--cp-accent-soft); color: var(--cp-accent); }
.hud {
  top: 16px; left: 16px; max-width: min(390px, calc(100% - 32px));
  padding: 0; background: var(--cp-panel-strong); border-color: var(--cp-border);
  border-radius: 8px; box-shadow: var(--cp-shadow); backdrop-filter: none;
}
.mapsettings { padding: 0 14px; max-height: 48dvh; overflow: auto; }
.mapsettings > summary { padding: 12px 0; font-weight: 600; cursor: pointer; color: var(--cp-text); }
.mapsettings[open] > summary { border-bottom: 1px solid var(--cp-border); margin-bottom: 12px; }
.mapsettings .hudrow { margin-bottom: 12px; gap: 10px 12px; }
.hudnote { color: var(--cp-text-muted); overflow-wrap: anywhere; }
.hudnote code { background: var(--cp-surface-soft); }
.heatlegend:not([hidden]) { padding: 10px 14px; border-top: 1px solid var(--cp-border); }
.routefilter summary { border-color: var(--cp-border); background: var(--cp-surface); border-radius: 4px; }
.routefiltermenu { position: relative; top: 4px; background: var(--cp-surface); box-shadow: none; }
.locationsearch button { background: var(--cp-surface); }
.mappanel { flex: 0 0 clamp(320px,27%,520px); max-width: none; min-width: 0; padding: 24px 20px; gap: 20px; background: var(--cp-surface); box-sizing: border-box; }
.placehead h2 { font-size: 25px; font-weight: 650; }
.placehead p { line-height: 1.65; }
.placehead a, .placenotes a { color: var(--cp-link); }
.statgrid { gap: 0; border-block: 1px solid var(--cp-border); padding: 8px 0; }
.statgrid div { padding: 8px; background: transparent; border: 0; border-radius: 0; min-width: 0; overflow-wrap: anywhere; }
.statgrid b { font-size: 15px; font-variant-numeric: tabular-nums; }
.statgrid span, .routefacts span { letter-spacing: 0; }
.placenotes { line-height: 1.7; }
.chip { background: var(--cp-surface); border-radius: 4px; }
.chip.dear { color: var(--cp-accent); border-color: var(--cp-highlight); background: var(--cp-accent-soft); }
.chip.event { color: var(--cp-accent-fg); background: var(--cp-accent); border-color: var(--cp-accent); }
.panelctl { flex-wrap: wrap; }
.panelctl input { width: 150px; }
.panelctl select { max-width: 100%; }
.routeselection { border: 0; border-top: 3px solid var(--cp-accent); border-radius: 0; background: transparent; padding: 18px 0; }
.routeheading { display: flex; align-items: start; justify-content: space-between; gap: 12px; }
.routeheading h2 { font-size: 18px; line-height: 1.35; margin: 0; }
.routeclose { flex: 0 0 32px; width: 32px; height: 32px; min-height: 32px; padding: 0; font-size: 22px; line-height: 1; background: transparent; border-color: transparent; }
.routeendpoints { display: grid; grid-template-columns: minmax(0, 1fr) auto minmax(0, 1fr); gap: 10px; align-items: center; padding: 18px 0; }
.routeendpoints b { display: block; font-size: 16px; overflow-wrap: anywhere; }
.routeendpoints span { color: var(--cp-text-muted); font-size: 11px; }
.routeendpoints > div:last-child { text-align: right; }
.routesummary { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); border-block: 1px solid var(--cp-border); padding: 12px 0; gap: 8px; }
.routesummary span { display: block; font-size: 11px; color: var(--cp-text-muted); }
.routesummary b { font-size: 16px; font-variant-numeric: tabular-nums; }
.routemodes { margin: 10px 0; color: var(--cp-text-muted); font-size: 12px; line-height: 1.6; }
.routelegs { list-style: none; counter-reset: itinerary; padding: 4px 0 0; border-top: 0; }
.routelegs > li { position: relative; counter-increment: itinerary; margin-left: 11px; padding: 0 0 20px 22px; border-left: 1px solid var(--cp-border-strong); }
.routelegs > li:last-child { border-left-color: transparent; padding-bottom: 4px; }
.routelegs > li::before { content: counter(itinerary); position: absolute; left: -11px; top: 0; width: 22px; height: 22px; display: grid; place-items: center; border-radius: 50%; background: var(--cp-accent); color: var(--cp-accent-fg); font-size: 11px; font-weight: 600; }
.routelegs > li > b { display: block; line-height: 1.6; }
.routelegs > li > small { display: block; margin: 3px 0 8px; }
.routecarriers { overflow-x: auto; }
.routecarriers summary { padding: 6px 0; color: var(--cp-link); }
.carriertable { min-width: 275px; }
.carriertable th { white-space: normal; letter-spacing: 0; padding: 8px 3px; }
.carriertable td { padding: 8px 3px; }
.route-detail-link { display: block; padding-top: 12px; border-top: 1px solid var(--cp-border); color: var(--cp-link); font-weight: 600; text-decoration: none; }
.route-detail-link:hover { text-decoration: underline; }
.routefacts { grid-template-columns: 1fr auto 1fr; }
.routefacts > * { min-width: 0; overflow-wrap: anywhere; }
.supplychain { padding: 14px 0; background: transparent; }
.supplychain .raw { color: var(--cp-text-muted); }
.supplychain .processed { color: var(--cp-accent); }
.pricewrap { overflow-x: auto; flex-shrink: 0; }
.pricewrap th { padding: 10px 6px; border-bottom: 1px solid var(--cp-border-strong); background: var(--cp-bg-elevated); }
.pricewrap td { padding: 9px 6px; }
.pricewrap .num { white-space: nowrap; }
.pricewrap tbody tr.active { background: var(--cp-highlight); box-shadow: inset 3px 0 var(--cp-accent); }
.pricewrap .up { color: var(--cp-accent); }
.viewcontrols { position: absolute; top: auto; bottom: 16px; right: 16px; z-index: 5; border: 1px solid var(--cp-border); background: var(--cp-panel-strong); box-shadow: var(--cp-shadow); }
.viewcontrols strong { letter-spacing: 0; }
.terrainlegend { max-width: min(300px, calc(100% - 32px)); left: 16px; bottom: 16px; background: var(--cp-panel-strong); border-radius: 6px; }
body[data-map-view="terrain"] .terrainlegend { bottom: 78px; }
.maptip, .mapstatus { background: var(--cp-panel-strong); border-color: var(--cp-border); border-radius: 6px; }
.mapbody .topbar { padding: 16px 24px; }
.mapbody .worldbar { flex: 1 1 680px; justify-content: flex-end; gap: 12px 16px; }
.mapbody .locationsearch { flex: 1 1 190px; max-width: 320px; }
.locationsearch input { flex: 1; width: 100%; min-width: 0; border-radius: 6px 0 0 6px; }
.locationsearch button { width: 40px; flex: 0 0 40px; border-radius: 0 6px 6px 0; }
.hud { border-radius: 6px; box-shadow: none; }
.mapsettings > summary { font-size: 13px; }
.mapsettings .hudrow > label { min-height: 32px; }
.panelctl { display: grid; grid-template-columns: repeat(auto-fit,minmax(130px,1fr)); gap: 10px; }
.panelctl input, .panelctl select { width: 100%; min-width: 0; }
.placehead h2 { font-size: 24px; overflow-wrap: anywhere; }
.statgrid { background: linear-gradient(90deg,var(--cp-surface-soft),var(--cp-surface)); }
.viewcontrols { border-radius: 6px; box-shadow: none; max-width: calc(100% - 32px); flex-wrap: wrap; }
.mapbody .navlink:hover { background: transparent; border-color: var(--cp-accent); }
@media (max-width: 1000px) {
  body.mapbody { height: auto; min-height: 100dvh; overflow: auto; }
  .maplayout { flex: none; overflow: visible; }
  .stage { flex: none; height: 65dvh; min-height: 420px; }
  .mappanel { max-width: none; flex: none; overflow: visible; padding: 20px 16px; }
  .mapsettings { max-height: 35dvh; }
  .terrainlegend { bottom: 16px; }
  .mapbody .topbar { padding: 16px; }
  .mapbody .worldbar { justify-content: flex-start; flex-basis: 100%; }
  .mapbody .locationsearch { max-width: none; }
}
"""


MAP_JS = """
// ---------------------------------------------------------------------------
// A hand-rolled 3D renderer on a 2D canvas.
//
// The server hands us a heightfield of Faerun plus the settlement pins and the
// trade graph. We project the mesh vertices ourselves and paint the cells back
// to front (painter's algorithm), which for an axis-aligned grid just means
// walking the rows and columns in the direction that points away from the eye.
// No WebGL, no shaders, no libraries.
// ---------------------------------------------------------------------------

var SCALE = 1000.0;   // miles per scene unit
// The poster-sized frame is almost twice as wide as the shipped terrain. Keep
// peaks large enough to read after fitView scales that full frame on screen.
var BASE_EXAG = 0.34; // scene units at full relief for a peak of height 1.0

// Faerun is about 9.5 million square miles and roughly 15% of Toril's total
// landmass. Its globe footprint is comparable to North America, while every
// part of Toril outside this surveyed map remains ocean.
var FAERUN_AREA_SQ_MI = 9500000;
var FAERUN_TORIL_LAND_SHARE = 0.15;
var GLOBE_FAERUN_WEST = -55 * Math.PI / 180;
var GLOBE_FAERUN_EAST = 55 * Math.PI / 180;
var GLOBE_FAERUN_NORTH = 80 * Math.PI / 180;
var GLOBE_FAERUN_SOUTH = -5 * Math.PI / 180;
var GLOBE_HOME_TILT = (GLOBE_FAERUN_NORTH + GLOBE_FAERUN_SOUTH) / 2;

var canvas = document.getElementById('world-canvas');
var ctx = canvas.getContext('2d');
var tipEl = document.getElementById('map-tip');
var statusEl = document.getElementById('map-status');
var MAP_VIEW = document.body.getAttribute('data-map-view') || 'overlay';
var requestedView = new URLSearchParams(window.location.search).get('view');
if (requestedView === 'overlay' || requestedView === 'terrain') { MAP_VIEW = requestedView; }
document.body.setAttribute('data-map-view', MAP_VIEW);
var mapViewChanged = false;

var state = {
  map: null,
  boot: null,
  nameToId: {},
  yaw: 0.0,
  pitch: MAP_VIEW === 'overlay' ? 1.45 : 0.50,
  dist: 3.4,
  tx: 0.0,
  tz: 0.0,
  exag: 0,
  routes: true,
  routeIcons: true,
  routeTypes: [],
  inferredRoads: false,
  labels: true,
  roundWorld: false,
  selected: null,
  selectedRoute: -1,
  selectedCarrierService: '',
  detailId: '',
  detailRequest: 0,
  hover: -1,
  heat: '',
  heatById: null,
  heatLo: 0,
  heatHi: 0,
  market: null,
  supplyChain: null,
  supplyRouteKeys: {},
  goodsFilter: '',
  goodsCategory: '',
  step: 1,
  tiles: 'smooth',
  hexStep: 2,
  globe: false,
  globeTilt: GLOBE_HOME_TILT,
  globeZoom: 1,
  // Poster-map underlay. The geometry is described in world miles, not in
  // screen pixels, so the alignment survives panning, zooming and tilting:
  // underX/underY are the world coordinates of the poster's top-left corner
  // and underMpp is how many miles one poster pixel covers.
  underInfo: null,
  under: null,
  underOn: false,
  posterOnly: false,
  underAlpha: 0.55,
  underX: -400,
  underY: 150,
  underMpp: 2.86,
  underStretch: 1.0,
  underDrape: true,
  // Where the current poster placement came from: 'survey' if the locations
  // file put it there, 'manual' once the user has nudged it, 'guess' if there
  // was no survey to work from.
  underFrom: 'guess',
  // Surveyed market visibility, plus fallback labels in unenriched worlds.
  places: true,
  // Realignment. calibPoints holds {id, x, y, baseX, baseY} - where a market
  // shipped and where the user says it really belongs. calibArmed is the id
  // waiting for its second click.
  calibOn: false,
  calibPoints: [],
  calibArmed: '',
  calibDirty: false,
  terrainEditOn: false,
  terrainEditSaving: false,
  // The surveyed poster index, when the maps folder ships one.
  atlas: null,
  dirty: true
};

var cam = {
  ex: 0, ey: 0, ez: 0,
  fx: 0, fy: 0, fz: 1,
  rx: 1, ry: 0, rz: 0,
  ux: 0, uy: 1, uz: 0,
  cx: 0, cy: 0, focal: 800, dpr: 1
};

// The poster is drawn cell by cell into this scratch canvas at full opacity and
// then composited once. Blending each cell straight onto the map instead would
// darken every seam, because neighbouring cells deliberately overlap slightly
// to hide the cracks and a semi-transparent overlap blends twice.
var underCanvas = document.createElement('canvas');
var underCtx = underCanvas.getContext('2d');

var mesh = null;
var pins = null;
var routeLines = null;

// Terrain palette: code -> [r, g, b]. The flat poster uses these as categorical
// colors; the 3D page applies hillshade to the same base colors.
var PALETTE = {
  o: [70, 132, 180],
  w: [103, 174, 205],
  i: [225, 242, 245],
  d: [226, 192, 112],
  c: [210, 197, 137],
  t: [180, 190, 177],
  p: [174, 205, 112],
  g: [198, 188, 99],
  m: [128, 118, 108],
  h: [154, 132, 91],
  s: [82, 148, 121],
  T: [83, 128, 103],
  f: [62, 132, 73],
  j: [35, 111, 66]
};
var DEEP_OCEAN = [
  Math.round(PALETTE.o[0] * 0.68),
  Math.round(PALETTE.o[1] * 0.68),
  Math.round(PALETTE.o[2] * 0.68)
];

var LEGEND_ORDER = [
  ['o', 'Ocean'], ['c', 'Coast'], ['p', 'Plains'], ['g', 'Steppe'],
  ['f', 'Forest'], ['T', 'Taiga'], ['t', 'Tundra'], ['i', 'Glacier'],
  ['h', 'Hills'], ['m', 'Mountains'], ['d', 'Desert'], ['j', 'Jungle'],
  ['s', 'Marsh']
];

function terrainCodeAt(index) {
  var code = mesh.codes.charAt(index);
  return PALETTE[code] ? code : 'o';
}

function drawTerrainIcon(code, x, y, size) {
  if (size < 5) { return; }
  var scale = Math.min(1.35, size / 13);
  ctx.save();
  ctx.translate(x, y);
  ctx.scale(scale, scale);
  ctx.strokeStyle = 'rgba(22, 35, 31, .86)';
  ctx.fillStyle = 'rgba(255, 255, 255, .30)';
  ctx.lineWidth = 1.45 / scale;
  ctx.lineCap = 'round';
  ctx.lineJoin = 'round';
  ctx.beginPath();
  if (code === 'm') {
    ctx.moveTo(-7, 5); ctx.lineTo(-1, -7); ctx.lineTo(7, 5);
    ctx.moveTo(-4, 0); ctx.lineTo(-1, -3); ctx.lineTo(1, 0);
  } else if (code === 'h') {
    ctx.moveTo(-8, 5); ctx.quadraticCurveTo(-4, -4, 0, 4);
    ctx.quadraticCurveTo(4, -5, 8, 5);
  } else if (code === 'f' || code === 'T' || code === 'j') {
    ctx.moveTo(-5, 5); ctx.lineTo(-5, 1); ctx.lineTo(-8, 1);
    ctx.lineTo(-5, -6); ctx.lineTo(-2, 1); ctx.lineTo(-5, 1);
    ctx.moveTo(4, 5); ctx.lineTo(4, 2); ctx.lineTo(1, 2);
    ctx.lineTo(4, -5); ctx.lineTo(7, 2); ctx.lineTo(4, 2);
    if (code === 'j') { ctx.moveTo(-8, 5); ctx.quadraticCurveTo(0, 1, 8, 5); }
  } else if (code === 'd') {
    ctx.moveTo(-8, 3); ctx.quadraticCurveTo(-3, -3, 2, 3);
    ctx.quadraticCurveTo(5, 6, 8, 2);
    ctx.moveTo(3, -5); ctx.lineTo(3, -1); ctx.moveTo(1, -3); ctx.lineTo(5, -3);
  } else if (code === 's') {
    ctx.moveTo(-7, 5); ctx.quadraticCurveTo(-3, 2, 1, 5);
    ctx.quadraticCurveTo(5, 2, 8, 5);
    ctx.moveTo(-4, 3); ctx.lineTo(-4, -5); ctx.moveTo(-4, -2); ctx.lineTo(-7, -4);
    ctx.moveTo(4, 3); ctx.lineTo(4, -3); ctx.moveTo(4, -1); ctx.lineTo(7, -3);
  } else if (code === 'o' || code === 'w' || code === 'c') {
    ctx.moveTo(-8, -2); ctx.quadraticCurveTo(-4, -5, 0, -2);
    ctx.quadraticCurveTo(4, 1, 8, -2);
    ctx.moveTo(-8, 3); ctx.quadraticCurveTo(-4, 0, 0, 3);
    ctx.quadraticCurveTo(4, 6, 8, 3);
  } else if (code === 'i' || code === 't') {
    ctx.moveTo(-7, 4); ctx.lineTo(-3, -4); ctx.lineTo(0, 1);
    ctx.lineTo(3, -6); ctx.lineTo(7, 4);
    ctx.moveTo(-6, 5); ctx.lineTo(6, 5);
  } else if (code === 'g') {
    ctx.moveTo(-8, 4); ctx.quadraticCurveTo(-2, -1, 3, 3);
    ctx.quadraticCurveTo(6, 5, 8, 2);
    ctx.moveTo(-5, 1); ctx.lineTo(-2, -4); ctx.moveTo(1, 1); ctx.lineTo(4, -3);
  } else {
    ctx.moveTo(-8, 4); ctx.quadraticCurveTo(-4, 1, 0, 4);
    ctx.quadraticCurveTo(4, 1, 8, 4);
    ctx.moveTo(-5, 2); ctx.lineTo(-3, -3); ctx.moveTo(1, 2); ctx.lineTo(3, -4);
    ctx.moveTo(5, 2); ctx.lineTo(7, -2);
  }
  ctx.stroke();
  ctx.restore();
}

var LABEL_FONT = '12px "Segoe UI", Arial, Helvetica, sans-serif';
var LABEL_FONT_BOLD = 'bold 12px "Segoe UI", Arial, Helvetica, sans-serif';

// Route colors follow map conventions and use a pale casing so they remain
// legible over both the colored terrain and the poster.
var ROUTE_STYLE = {
  road: 'rgba(190, 72, 28, .98)',
  trail: 'rgba(218, 145, 30, .96)',
  sea: 'rgba(0, 110, 196, .96)',
  river: 'rgba(0, 133, 117, .96)',
  barge: 'rgba(0, 133, 117, .94)',
  ferry: 'rgba(0, 133, 117, .92)',
  portage: 'rgba(133, 76, 37, .88)',
  tunnel: 'rgba(112, 73, 138, .88)',
  teleport: 'rgba(0, 151, 167, .96)',
  air: 'rgba(189, 36, 123, .92)'
};
var ROUTE_WIDTH = {
  road: 3.4, trail: 2.8, track: 2.4, sea: 3.4, river: 3.1,
  barge: 2.8, ferry: 2.7, portage: 2.2, tunnel: 2.2,
  teleport: 3.2, air: 3.0
};
var COMPLEX_ROUTE_STYLE = 'rgba(211, 67, 43, .98)';
var GROUND_MULTILEG_ROUTE_STYLE = 'rgba(46, 125, 74, .98)';

// ---------------------------------------------------------------------------
// small helpers
// ---------------------------------------------------------------------------

function esc(value) {
  if (value === null || value === undefined) { return ''; }
  return String(value)
    .split('&').join('&amp;')
    .split('<').join('&lt;')
    .split('>').join('&gt;')
    .split('"').join('&quot;');
}

function gp(value) {
  if (value === null || value === undefined) { return '-'; }
  if (value >= 100) { return value.toFixed(0); }
  if (value >= 10) { return value.toFixed(1); }
  if (value < 1) { return value.toFixed(3); }
  return value.toFixed(2);
}

function quoteMarkup(value) {
  return Number.isFinite(value) ? value.toFixed(1) + '%' : '-';
}

function quotePrice(value) {
  return Number.isFinite(value)
    ? value.toLocaleString(undefined, { minimumFractionDigits: value < 1 ? 3 : 2, maximumFractionDigits: 3 })
    : '-';
}

function clamp(v, lo, hi) { return v < lo ? lo : (v > hi ? hi : v); }

function showStatus(text, isError) {
  if (!text) { statusEl.hidden = true; return; }
  statusEl.hidden = false;
  statusEl.textContent = text;
  statusEl.className = isError ? 'mapstatus error' : 'mapstatus';
}

async function getJson(url) {
  var res = await fetch(url);
  // Read as text first: a 404 from the static handler and a crashed handler
  // both return something that is not JSON, and res.json() would then throw a
  // parse error that hides the real status.
  var body = await res.text();
  var data = null;
  try { data = JSON.parse(body); } catch (err) { data = null; }
  if (!res.ok) {
    var why = data && data.error ? data.error : (body || 'request failed');
    throw new Error(url + ' -> ' + res.status + ': ' + String(why).slice(0, 300));
  }
  if (data === null) {
    throw new Error(url + ' returned a non-JSON body: ' + body.slice(0, 200));
  }
  return data;
}

async function postJson(url, body) {
  var res = await fetch(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body)
  });
  var text = await res.text();
  var data = null;
  try { data = JSON.parse(text); } catch (err) { data = null; }
  if (!res.ok) {
    var why = data && data.error ? data.error : (text || 'request failed');
    throw new Error(url + ' -> ' + res.status + ': ' + String(why).slice(0, 300));
  }
  return data;
}

function invalidate() { state.dirty = true; }

// ---------------------------------------------------------------------------
// mesh construction
// ---------------------------------------------------------------------------

function buildMesh(payload) {
  var W = payload.grid[0];
  var H = payload.grid[1];
  var b = payload.bounds;
  var cellW = (b[2] - b[0]) / W;
  var cellH = (b[3] - b[1]) / H;
  var cx = (b[0] + b[2]) / 2;
  var cy = (b[1] + b[3]) / 2;

  var cells = payload.height;
  var codes = payload.terrain;

  var vx = new Float32Array(W + 1);
  var vz = new Float32Array(H + 1);
  for (var i = 0; i <= W; i++) { vx[i] = (b[0] + i * cellW - cx) / SCALE; }
  for (var j = 0; j <= H; j++) { vz[j] = (b[1] + j * cellH - cy) / SCALE; }

  // Vertex heights: the mean of the touching cells, with water clamped to sea
  // level so the ocean reads as a flat sheet and the shore ramps up out of it.
  var vh = new Float32Array((W + 1) * (H + 1));
  for (var vj = 0; vj <= H; vj++) {
    for (var vi = 0; vi <= W; vi++) {
      var total = 0.0;
      var n = 0;
      for (var dj = -1; dj <= 0; dj++) {
        var cj = vj + dj;
        if (cj < 0 || cj >= H) { continue; }
        for (var di = -1; di <= 0; di++) {
          var ci = vi + di;
          if (ci < 0 || ci >= W) { continue; }
          var raw = cells[cj * W + ci] / 1000.0;
          total += raw > 0 ? raw : 0.0;
          n++;
        }
      }
      vh[vj * (W + 1) + vi] = n > 0 ? total / n : 0.0;
    }
  }

  mesh = {
    W: W, H: H, cx: cx, cy: cy, cellW: cellW, cellH: cellH,
    detail: !!payload.detail,
    bounds: b, vx: vx, vz: vz, vh: vh, cells: cells, codes: codes,
    px: new Float32Array((W + 1) * (H + 1)),
    py: new Float32Array((W + 1) * (H + 1)),
    pd: new Float32Array((W + 1) * (H + 1)),
    ok: new Uint8Array((W + 1) * (H + 1)),
    colors: new Array(W * H)
  };
  shadeMesh();
}

// Fixed light from the north-west and above. Because the light never moves,
// the shaded colour of every cell can be computed once and cached as a string.
function shadeMesh() {
  var W = mesh.W, H = mesh.H;
  var vh = mesh.vh, cells = mesh.cells, codes = mesh.codes;
  var exag = state.exag;
  var sx = (mesh.cellW / SCALE);
  var sz = (mesh.cellH / SCALE);
  var lx = -0.42, ly = 0.80, lz = -0.43;
  var llen = Math.sqrt(lx * lx + ly * ly + lz * lz);
  lx /= llen; ly /= llen; lz /= llen;

  for (var j = 0; j < H; j++) {
    for (var i = 0; i < W; i++) {
      var idx = j * W + i;
      var a = vh[j * (W + 1) + i] * exag;
      var bb = vh[j * (W + 1) + i + 1] * exag;
      var c = vh[(j + 1) * (W + 1) + i] * exag;
      var d = vh[(j + 1) * (W + 1) + i + 1] * exag;

      var dhx = ((bb + d) - (a + c)) / (2 * sx);
      var dhz = ((c + d) - (a + bb)) / (2 * sz);
      var nx = -dhx, ny = 1.0, nz = -dhz;
      var nlen = Math.sqrt(nx * nx + ny * ny + nz * nz) || 1;
      var lambert = (nx * lx + ny * ly + nz * lz) / nlen;
      if (lambert < 0) { lambert = 0; }

      var code = codes.charAt(idx);
      var base = PALETTE[code];
      if (!base) {
        mesh.colors[idx] = 'rgb(' + DEEP_OCEAN[0] + ',' + DEEP_OCEAN[1]
          + ',' + DEEP_OCEAN[2] + ')';
        continue;
      }
      var r = base[0], g = base[1], bl = base[2];
      var raw = cells[idx] / 1000.0;

      if (raw < 0) {
        // Deeper water darkens without discarding the blue category color.
        var depth = clamp(-raw / 0.09, 0, 1);
        var waterShade = 1 - depth * 0.32;
        r = Math.round(r * waterShade);
        g = Math.round(g * waterShade);
        bl = Math.round(bl * waterShade);
        mesh.colors[idx] = 'rgb(' + r + ',' + g + ',' + bl + ')';
        continue;
      }

      // Snowcaps lighten the highest ground, but stop short of paper white so
      // a summit never matches the sea it is nowhere near.
      if (raw > 0.70) {
        var snow = clamp((raw - 0.70) / 0.30, 0, 1) * 0.85;
        r = r + (232 - r) * snow;
        g = g + (232 - g) * snow;
        bl = bl + (232 - bl) * snow;
      }

      var shade = 0.44 + 0.78 * lambert;
      r = Math.round(clamp(r * shade, 0, 255));
      g = Math.round(clamp(g * shade, 0, 255));
      bl = Math.round(clamp(bl * shade, 0, 255));
      mesh.colors[idx] = 'rgb(' + r + ',' + g + ',' + bl + ')';
    }
  }
}

// Bilinear sample of the vertex heightfield at a world position, in raw units.
function sampleHeight(wx, wy) {
  var b = mesh.bounds, W = mesh.W, H = mesh.H;
  var gx = clamp((wx - b[0]) / (b[2] - b[0]) * W, 0, W - 0.001);
  var gy = clamp((wy - b[1]) / (b[3] - b[1]) * H, 0, H - 0.001);
  var i = Math.floor(gx), j = Math.floor(gy);
  var fx = gx - i, fy = gy - j;
  var vh = mesh.vh, row = W + 1;
  var a = vh[j * row + i], bb = vh[j * row + i + 1];
  var c = vh[(j + 1) * row + i], d = vh[(j + 1) * row + i + 1];
  var top = a + (bb - a) * fx;
  var bot = c + (d - c) * fx;
  return top + (bot - top) * fy;
}

function toScene(wx, wy) {
  return [(wx - mesh.cx) / SCALE, (wy - mesh.cy) / SCALE];
}

function buildPins(list) {
  pins = list.map(function (s) {
    var w = calibratedXY(s);
    var p = toScene(w[0], w[1]);
    var h = sampleHeight(w[0], w[1]);
    var pop = Math.max(1, s.population || 1);
    return {
      data: s,
      // Where this market is drawn, which is its shipped position put through
      // the realignment fit. Kept separate from data.x/data.y so a preview can
      // be recomputed without ever mutating the payload.
      wx: w[0],
      wy: w[1],
      sx: p[0],
      sz: p[1],
      h: h,
      // Flat dots sit directly on the terrain, so they read a touch heavier
      // than the old raised pins did at the same size - hence the tighter
      // range here.
      radius: clamp(2.5 + Math.log10(pop / 100) * 1.45, 2.5, 10),
      px: 0, py: 0, depth: 0, vis: false
    };
  });
}

// Non-market survey labels retained for worlds that opt out of enrichment.
var placeDots = [];

function buildPlaces(list) {
  placeDots = (list || []).map(function (p) {
    var s = toScene(p.x, p.y);
    return {
      name: p.name,
      h: sampleHeight(p.x, p.y),
      sx: s[0],
      sz: s[1],
      px: 0, py: 0, depth: 0, vis: false
    };
  });
}

function drawPlaces() {
  if (!state.places || !placeDots.length) { return; }
  // The market labels drawn later assume a left-anchored context, and the
  // names below centre themselves over their dot, so the whole thing is
  // bracketed rather than left to leak.
  ctx.save();
  try {
    paintPlaces();
  } finally {
    ctx.restore();
  }
}

function paintPlaces() {
  var exag = state.exag;
  var i, d, p;
  var vis = [];
  for (i = 0; i < placeDots.length; i++) {
    d = placeDots[i];
    d.vis = false;
    p = project(d.sx, d.h * exag + 0.003, d.sz);
    if (!p) { continue; }
    d.px = p[0]; d.py = p[1]; d.depth = p[2];
    d.vis = true;
    vis.push(d);
  }

  // Hollow, small and grey: present enough to read as a settlement, quiet
  // enough that it never competes with a market that actually has prices.
  ctx.lineWidth = 1;
  ctx.strokeStyle = 'rgba(0, 0, 0, .55)';
  ctx.fillStyle = '#ffffff';
  for (i = 0; i < vis.length; i++) {
    ctx.beginPath();
    ctx.arc(vis[i].px, vis[i].py, 1.7, 0, Math.PI * 2);
    ctx.fill();
    ctx.stroke();
  }

  // Labelling several hundred of these at once would be a grey fog. There is
  // no zoom level to test against here, so the spacing rule below does the
  // work instead: zoomed out almost nothing fits and only a scattering gets
  // named, zoomed in they separate and more of them earn a label. Market
  // labels are drawn after this and so always win the same space.
  if (!state.labels) { return; }
  var budget = 80;
  ctx.font = '9px ui-sans-serif, system-ui, sans-serif';
  ctx.textAlign = 'center';
  ctx.textBaseline = 'bottom';
  ctx.fillStyle = 'rgba(0, 0, 0, .7)';
  ctx.strokeStyle = 'rgba(255, 255, 255, .9)';
  ctx.lineWidth = 2.5;
  var taken = [];
  // Nearest first, so the labels that survive are the ones closest to the eye.
  vis.sort(function (a, b) { return a.depth - b.depth; });
  for (i = 0; i < vis.length && taken.length < budget; i++) {
    d = vis[i];
    var clash = false;
    for (var k = 0; k < taken.length; k++) {
      if (Math.abs(taken[k][0] - d.px) < 58
          && Math.abs(taken[k][1] - d.py) < 13) { clash = true; break; }
    }
    if (clash) { continue; }
    taken.push([d.px, d.py]);
    ctx.strokeText(d.name, d.px, d.py - 3);
    ctx.fillText(d.name, d.px, d.py - 3);
  }
}

var routeSpec = [];
var roadGeometrySpec = [];
var seaAirGeometrySpec = [];

function isWaterCell(column, row) {
  if (column < 0 || column >= mesh.W || row < 0 || row >= mesh.H) { return false; }
  var code = mesh.codes.charAt(row * mesh.W + column);
  return code === 'o' || code === 'w';
}

function isLandCell(column, row) {
  return column >= 0 && column < mesh.W && row >= 0 && row < mesh.H
    && !isWaterCell(column, row);
}

function nearestLandCell(wx, wy, radius) {
  var b = mesh.bounds;
  var column = Math.floor((wx - b[0]) / (b[2] - b[0]) * mesh.W);
  var row = Math.floor((wy - b[1]) / (b[3] - b[1]) * mesh.H);
  var best = null, bestDistance = Infinity;
  for (var dy = -radius; dy <= radius; dy++) {
    for (var dx = -radius; dx <= radius; dx++) {
      if (!isLandCell(column + dx, row + dy)) { continue; }
      var distance = dx * dx + dy * dy;
      if (distance < bestDistance) {
        bestDistance = distance;
        best = [column + dx, row + dy];
      }
    }
  }
  return best;
}

function fractionalLandSegmentIsClear(start, end) {
  var dx = end[0] - start[0], dy = end[1] - start[1];
  var steps = Math.max(1, Math.ceil(Math.max(Math.abs(dx), Math.abs(dy)) * 3));
  for (var step = 0; step <= steps; step++) {
    var progress = step / steps;
    if (!isLandCell(Math.floor(start[0] + dx * progress + 0.5),
      Math.floor(start[1] + dy * progress + 0.5))) { return false; }
  }
  return true;
}

function landRoute(startX, startY, endX, endY) {
  var bounds = mesh.bounds;
  var startColumn = Math.floor((startX - bounds[0]) / (bounds[2] - bounds[0]) * mesh.W);
  var startRow = Math.floor((startY - bounds[1]) / (bounds[3] - bounds[1]) * mesh.H);
  var endColumn = Math.floor((endX - bounds[0]) / (bounds[2] - bounds[0]) * mesh.W);
  var endRow = Math.floor((endY - bounds[1]) / (bounds[3] - bounds[1]) * mesh.H);
  var start = nearestLandCell(startX, startY, 12);
  var end = nearestLandCell(endX, endY, 12);
  if (!start || !end) { return null; }
  var size = mesh.W * mesh.H;
  var parents = new Int32Array(size);
  parents.fill(-1);
  var queue = new Int32Array(size);
  var first = start[1] * mesh.W + start[0];
  var last = end[1] * mesh.W + end[0];
  var head = 0, tail = 0;
  queue[tail++] = first;
  parents[first] = first;
  while (head < tail && parents[last] < 0) {
    var current = queue[head++];
    var column = current % mesh.W;
    var row = Math.floor(current / mesh.W);
    var neighbours = [[column + 1, row], [column - 1, row],
      [column, row + 1], [column, row - 1]];
    for (var n = 0; n < neighbours.length; n++) {
      var next = neighbours[n];
      if (!isLandCell(next[0], next[1])) { continue; }
      var index = next[1] * mesh.W + next[0];
      if (parents[index] >= 0) { continue; }
      parents[index] = current;
      queue[tail++] = index;
    }
  }
  if (parents[last] < 0) { return null; }
  var cells = [];
  for (var at = last; ; at = parents[at]) {
    cells.push([at % mesh.W, Math.floor(at / mesh.W)]);
    if (at === first) { break; }
  }
  cells.reverse();
  var simple = [cells[0]];
  for (var from = 0; from < cells.length - 1;) {
    var to = cells.length - 1;
    while (to > from + 1 && !fractionalLandSegmentIsClear(cells[from], cells[to])) { to--; }
    simple.push(cells[to]);
    from = to;
  }
  var cellW = (bounds[2] - bounds[0]) / mesh.W;
  var cellH = (bounds[3] - bounds[1]) / mesh.H;
  var points = simple.map(function (cell) {
    return [bounds[0] + (cell[0] + 0.5) * cellW,
      bounds[1] + (cell[1] + 0.5) * cellH];
  });
  if (isLandCell(startColumn, startRow)) { points[0] = [startX, startY]; }
  if (isLandCell(endColumn, endRow)) { points[points.length - 1] = [endX, endY]; }
  return points;
}

function waterCellsNear(wx, wy, radius) {
  var b = mesh.bounds;
  var column = Math.floor((wx - b[0]) / (b[2] - b[0]) * mesh.W);
  var row = Math.floor((wy - b[1]) / (b[3] - b[1]) * mesh.H);
  var cells = [];
  for (var dy = -radius; dy <= radius; dy++) {
    for (var dx = -radius; dx <= radius; dx++) {
      if (!isWaterCell(column + dx, row + dy)) { continue; }
      cells.push({ cell: [column + dx, row + dy], distance: dx * dx + dy * dy });
    }
  }
  cells.sort(function (a, b) { return a.distance - b.distance; });
  if (!cells.length) { return []; }
  var shorelineDistance = cells[0].distance + 2;
  return cells.filter(function (candidate) {
    return candidate.distance <= shorelineDistance;
  }).map(function (candidate) { return candidate.cell; });
}

function nearestWaterCell(wx, wy, radius) {
  return waterCellsNear(wx, wy, radius)[0] || null;
}

function localWaterCells(wx, wy, cells) {
  if (!cells.length) { return cells; }
  var b = mesh.bounds;
  var column = Math.floor((wx - b[0]) / (b[2] - b[0]) * mesh.W);
  var row = Math.floor((wy - b[1]) / (b[3] - b[1]) * mesh.H);
  var distance = function (cell) {
    var dx = cell[0] - column, dy = cell[1] - row;
    return dx * dx + dy * dy;
  };
  var nearest = distance(cells[0]);
  return cells.filter(function (cell) { return distance(cell) <= nearest + 2; });
}

function waterSegmentIsClear(start, end) {
  var x = start[0], y = start[1];
  var dx = Math.abs(end[0] - x), sx = x < end[0] ? 1 : -1;
  var dy = -Math.abs(end[1] - y), sy = y < end[1] ? 1 : -1;
  var error = dx + dy;
  while (true) {
    if (!isWaterCell(x, y)) { return false; }
    if (x === end[0] && y === end[1]) { return true; }
    var twice = 2 * error;
    if (twice >= dy) { error += dy; x += sx; }
    if (twice <= dx) { error += dx; y += sy; }
  }
}

function fractionalWaterSegmentIsClear(start, end) {
  var startX = Math.abs(start[0] - Math.round(start[0])) < 1e-5 ? Math.round(start[0]) : start[0];
  var startY = Math.abs(start[1] - Math.round(start[1])) < 1e-5 ? Math.round(start[1]) : start[1];
  var endX = Math.abs(end[0] - Math.round(end[0])) < 1e-5 ? Math.round(end[0]) : end[0];
  var endY = Math.abs(end[1] - Math.round(end[1])) < 1e-5 ? Math.round(end[1]) : end[1];
  var dx = endX - startX, dy = endY - startY;
  var steps = Math.max(1, Math.ceil(Math.max(Math.abs(dx), Math.abs(dy)) * 3));
  for (var step = 0; step <= steps; step++) {
    var progress = step / steps;
    if (!isWaterCell(Math.floor(startX + dx * progress + 0.5),
      Math.floor(startY + dy * progress + 0.5))) { return false; }
  }
  return true;
}

function smoothWaterCells(cells) {
  if (cells.length < 3) { return cells; }
  var smooth = [cells[0]];
  for (var i = 1; i < cells.length - 1; i++) {
    var previous = cells[i - 1], current = cells[i], next = cells[i + 1];
    var before = [previous[0] * 0.25 + current[0] * 0.75,
      previous[1] * 0.25 + current[1] * 0.75];
    var after = [current[0] * 0.75 + next[0] * 0.25,
      current[1] * 0.75 + next[1] * 0.25];
    if (fractionalWaterSegmentIsClear(before, after)) {
      smooth.push(before, after);
    } else {
      smooth.push(current);
    }
  }
  smooth.push(cells[cells.length - 1]);
  for (var segment = 1; segment < smooth.length; segment++) {
    if (!fractionalWaterSegmentIsClear(smooth[segment - 1], smooth[segment])) { return cells; }
  }
  return smooth;
}

function waterCoastDistance(column, row, radius) {
  for (var distance = 1; distance <= radius; distance++) {
    for (var dy = -distance; dy <= distance; dy++) {
      for (var dx = -distance; dx <= distance; dx++) {
        if (Math.abs(dx) !== distance && Math.abs(dy) !== distance) { continue; }
        if (!isWaterCell(column + dx, row + dy)) { return distance - 1; }
      }
    }
  }
  return radius;
}

function waterRoute(startX, startY, endX, endY) {
  var starts = waterCellsNear(startX, startY, 12);
  var ends = waterCellsNear(endX, endY, 12);
  starts = localWaterCells(startX, startY, starts);
  ends = localWaterCells(endX, endY, ends);
  if (!starts.length || !ends.length) { return null; }
  var size = mesh.W * mesh.H;
  var parents = new Int32Array(size);
  parents.fill(-1);
  var costs = new Int32Array(size);
  costs.fill(-1);
  var buckets = [];
  var targets = new Uint8Array(size);
  ends.forEach(function (cell) { targets[cell[1] * mesh.W + cell[0]] = 1; });
  buckets[0] = [];
  starts.forEach(function (cell) {
    var index = cell[1] * mesh.W + cell[0];
    if (costs[index] >= 0) { return; }
    parents[index] = index;
    costs[index] = 0;
    buckets[0].push(index);
  });
  var queued = buckets[0].length, currentCost = 0;
  var last = -1;
  while (queued > 0 && last < 0) {
    while (!buckets[currentCost] || !buckets[currentCost].length) { currentCost++; }
    var current = buckets[currentCost].pop();
    queued--;
    if (costs[current] !== currentCost) { continue; }
    if (targets[current]) { last = current; break; }
    var column = current % mesh.W;
    var row = Math.floor(current / mesh.W);
    var neighbours = [[column + 1, row], [column - 1, row],
      [column, row + 1], [column, row - 1], [column + 1, row + 1],
      [column + 1, row - 1], [column - 1, row + 1], [column - 1, row - 1]];
    for (var n = 0; n < neighbours.length; n++) {
      var next = neighbours[n];
      if (!isWaterCell(next[0], next[1])) { continue; }
      var index = next[1] * mesh.W + next[0];
      var diagonal = next[0] !== column && next[1] !== row;
      var stepCost = (diagonal ? 3 : 2) + waterCoastDistance(next[0], next[1], 4) * 3;
      var candidateCost = currentCost + stepCost;
      if (costs[index] >= 0 && costs[index] <= candidateCost) { continue; }
      costs[index] = candidateCost;
      parents[index] = current;
      if (!buckets[candidateCost]) { buckets[candidateCost] = []; }
      buckets[candidateCost].push(index);
      queued++;
    }
  }
  if (last < 0) { return null; }
  var cells = [];
  for (var at = last; ; at = parents[at]) {
    cells.push([at % mesh.W, Math.floor(at / mesh.W)]);
    if (parents[at] === at) { break; }
  }
  cells.reverse();
  var simple = [cells[0]];
  for (var from = 0; from < cells.length - 1;) {
    var to = Math.min(cells.length - 1, from + 8);
    while (to > from + 1 && !fractionalWaterSegmentIsClear(cells[from], cells[to])) { to--; }
    simple.push(cells[to]);
    from = to;
  }
  return simple.map(function (cell) {
    return [mesh.bounds[0] + (cell[0] + 0.5) * mesh.cellW,
      mesh.bounds[1] + (cell[1] + 0.5) * mesh.cellH];
  });
}

function polylineMiles(points) {
  var distance = 0;
  for (var i = 1; i < points.length; i++) {
    distance += Math.hypot(points[i][0] - points[i - 1][0], points[i][1] - points[i - 1][1]);
  }
  return distance;
}

function plausibleCoastingRoute(spec, points) {
  if (!spec || !/ coasting run$/.test(spec.name || '')) { return true; }
  return polylineMiles(points) <= Number(spec.distance) * 2;
}

function nearestRouteEndpoint(point, byId) {
  var best = null, bestDistance = Infinity;
  Object.keys(byId).forEach(function (id) {
    var pin = byId[id];
    var distance = Math.hypot(pin.wx - point[0], pin.wy - point[1]);
    if (distance < bestDistance) { bestDistance = distance; best = pin; }
  });
  return best;
}

function routeDetails(spec, points, byId, fallbackName, fallbackKind) {
  var start = spec && byId[spec.a] ? byId[spec.a] : nearestRouteEndpoint(points[0], byId);
  var end = spec && byId[spec.b] ? byId[spec.b] : nearestRouteEndpoint(points[points.length - 1], byId);
  var suppliedDistance = spec ? Number(spec.distance) : NaN;
  var kind = (spec && spec.kind) || fallbackKind || 'road';
  return {
    name: (spec && spec.name) || fallbackName || 'Trade route',
    a: spec ? spec.a : (start ? start.data.id : ''),
    b: spec ? spec.b : (end ? end.data.id : ''),
    start: start ? start.data.name : 'Unknown',
    end: end ? end.data.name : 'Unknown',
    kind: kind,
    modes: spec && spec.modes && spec.modes.length ? spec.modes : [kind],
    distance: Number.isFinite(suppliedDistance) ? suppliedDistance : polylineMiles(points),
    days: spec ? Number(spec.days) : NaN,
    carriers: spec && spec.carriers ? spec.carriers : []
  };
}

function routeTypeLabel(kind) {
  var labels = {
    road: 'Road', trail: 'Foot trail', sea: 'Sea',
    river: 'River', barge: 'Barge', ferry: 'Ferry', portage: 'Portage',
    tunnel: 'Tunnel', teleport: 'Teleportation circle', air: 'Gryphon flight'
  };
  return labels[kind] || String(kind || 'Route');
}

function routeTypeIcon(kind) {
  var icons = {
    road: '\u2194', trail: '\u2022', sea: '\u26f5',
    river: '\u224b', barge: '\u25ad', ferry: '\u21c4', portage: '\u2191',
    tunnel: '\u25c9', air: '\\ud83e\\udd85'
  };
  return icons[kind] || '\u25c6';
}

function routeTime(days) {
  if (!Number.isFinite(days)) { return '-'; }
  if (days < 1) { return Math.max(1, Math.round(days * 24)) + ' hr'; }
  return days.toFixed(days < 10 ? 1 : 0) + ' days';
}

function routeLoad(pounds) {
  if (pounds >= 2000) { return (pounds / 2000).toLocaleString(undefined, { maximumFractionDigits: 1 }) + ' tons'; }
  return Math.round(pounds).toLocaleString() + ' lb';
}

function routeCarrierTable(details, routeIndex) {
  var carriers = details.carriers || [];
  if (!carriers.length) { return '<p class="muted">No scheduled carriers.</p>'; }
  var showModes = details.modes && details.modes.length > 1;
  return '<table class="carriertable"><thead><tr><th>Carrier</th><th>Full load</th>' +
    '<th>Efficiency</th><th>Max load</th><th>Time</th></tr></thead><tbody>' +
    carriers.map(function (carrier) {
      var serviceControl = carrier.multileg ? '<button class="carrierselect" type="button" aria-pressed="' +
        (state.selectedCarrierService === carrier.service_id ? 'true' : 'false') +
        '" onclick="selectRouteCarrier(' + routeIndex + ', \\'' + esc(carrier.service_id) + '\\')">' +
        (state.selectedCarrierService === carrier.service_id ? 'All legs selected' : 'Select all legs') + '</button>' : '';
      return '<tr><td><b>' + esc(carrier.name) + '</b>' +
        (showModes ? '<span>' + esc(routeTypeLabel(carrier.mode)) + '</span>' : '') + serviceControl + '</td>' +
        '<td>' + Number(carrier.cost_gp).toLocaleString(undefined, { maximumFractionDigits: 2 }) + ' gp</td>' +
        '<td>' + Number(carrier.cost_gp_per_ton_mile).toFixed(3) + ' gp/ton-mi<br><span>' +
        Number(carrier.speed_miles_per_day).toLocaleString() + ' mi/day</span></td>' +
        '<td>' + routeLoad(Number(carrier.max_load_lb)) + '</td>' +
        '<td>' + routeTime(Number(carrier.days)) + '</td></tr>';
    }).join('') + '</tbody></table>';
}

function routeMatchesFilter(line) {
  if (line.inferredRoad && !state.inferredRoads) { return false; }
  if (!state.routeTypes.length) { return true; }
  var modes = line.details && line.details.modes ? line.details.modes : [line.kind];
  return modes.some(function (mode) { return state.routeTypes.indexOf(mode) >= 0; });
}

function routeConnectedLocationIds() {
  var connected = new Set();
  if (!state.routeTypes.length || !routeLines) { return connected; }
  routeLines.forEach(function (line) {
    if (!routeMatchesFilter(line) || !line.details) { return; }
    if (line.details.a) { connected.add(line.details.a); }
    if (line.details.b) { connected.add(line.details.b); }
  });
  return connected;
}

function multilegService(line) {
  if (!line || !line.details) { return null; }
  return (line.details.carriers || []).find(function (carrier) {
    return carrier.multileg && carrier.service_id;
  }) || null;
}

function routeDisplayColor(line) {
  var service = multilegService(line);
  if (service && service.service_class === 'ground') {
    return GROUND_MULTILEG_ROUTE_STYLE;
  }
  return service ? COMPLEX_ROUTE_STYLE
    : (ROUTE_STYLE[line.kind] || 'rgba(70, 55, 40, .9)');
}

function routeLineDash(line) {
  if (line.multi) { return [8, 5]; }
  if (line.kind === 'trail') { return [7, 5]; }
  if (line.kind === 'portage' || line.kind === 'teleport') { return [2, 5]; }
  return [];
}

function routeSpecByName(name, points, byId, fromName, toName) {
  if (!name) { return null; }
  var namedEndpoints = fromName && toName
    ? [fromName.toLowerCase(), toName.toLowerCase()].sort().join('|')
    : '';
  var best = null, bestDistance = Infinity;
  for (var i = 0; i < routeSpec.length; i++) {
    var spec = routeSpec[i];
    if (spec.name !== name || !byId[spec.a] || !byId[spec.b]) { continue; }
    var a = byId[spec.a], b = byId[spec.b];
    if (namedEndpoints) {
      var specEndpoints = [a.data.name.toLowerCase(), b.data.name.toLowerCase()].sort().join('|');
      if (specEndpoints === namedEndpoints) { return spec; }
      continue;
    }
    var first = points[0], last = points[points.length - 1];
    var forward = Math.hypot(a.wx - first[0], a.wy - first[1])
      + Math.hypot(b.wx - last[0], b.wy - last[1]);
    var reverse = Math.hypot(b.wx - first[0], b.wy - first[1])
      + Math.hypot(a.wx - last[0], a.wy - last[1]);
    var distance = Math.min(forward, reverse);
    if (distance < bestDistance) { bestDistance = distance; best = spec; }
  }
  return best;
}

function routeLegKey(spec) {
  var ends = [spec.a, spec.b].sort();
  return spec.name + '|' + ends[0] + '|' + ends[1];
}

function anchorRoutePoints(points, spec, byId) {
  if (!spec || !byId[spec.a] || !byId[spec.b]) { return points; }
  var a = byId[spec.a], b = byId[spec.b];
  var first = points[0], last = points[points.length - 1];
  var reverse = Math.hypot(b.wx - first[0], b.wy - first[1])
    + Math.hypot(a.wx - last[0], a.wy - last[1])
    < Math.hypot(a.wx - first[0], a.wy - first[1])
    + Math.hypot(b.wx - last[0], b.wy - last[1]);
  var start = reverse ? b : a, end = reverse ? a : b;
  return [[start.wx, start.wy]].concat(points, [[end.wx, end.wy]]);
}

function tracedRoadNetwork(roads) {
  var segments = [], neighbours = {}, seen = {};
  roads.forEach(function (road) {
    var anchors = road.anchors || [], locations = road.locations || [];
    if (anchors.length < 2 || anchors.length !== locations.length) {
      segments.push(road);
      return;
    }
    for (var index = 1; index < anchors.length; index++) {
      var start = locations[index - 1], end = locations[index];
      var points = road.points.slice(anchors[index - 1], anchors[index] + 1);
      if (points.length < 2 || start === end) { continue; }
      var forward = JSON.stringify(points), reverse = JSON.stringify(points.slice().reverse());
      var key = (road.surface || 'road') + '|' + [start, end].sort().join('|') + '|' +
        (forward < reverse ? forward : reverse);
      if (seen[key]) { continue; }
      seen[key] = true;
      segments.push(Object.assign({}, road, {points: points, a: start, b: end}));
      if (road.surface === 'road' || !road.surface) {
        (neighbours[start] || (neighbours[start] = [])).push(end);
        (neighbours[end] || (neighbours[end] = [])).push(start);
      }
    }
  });
  var components = {}, component = 0;
  Object.keys(neighbours).forEach(function (start) {
    if (components[start]) { return; }
    component++;
    var pending = [start];
    components[start] = component;
    while (pending.length) {
      var current = pending.pop();
      neighbours[current].forEach(function (next) {
        if (!components[next]) { components[next] = component; pending.push(next); }
      });
    }
  });
  return {segments: segments, connects: function (start, end) {
    return !!components[start] && components[start] === components[end];
  }};
}

function buildRoutes(list, roadGeometries, seaAirGeometries) {
  routeSpec = list || [];
  roadGeometrySpec = roadGeometries || [];
  seaAirGeometrySpec = seaAirGeometries || [];
  rebuildRouteGeometry();
}

function rebuildRouteGeometry() {
  var byId = {};
  pins.forEach(function (p) { byId[p.data.id] = p; });
  var steps = 6;
  routeLines = [];
  state.selectedRoute = -1;
  updateRouteSelection();
  var tracedRoadLegs = {};
  var tracedSeaAirLegs = {};

  var roadNetwork = tracedRoadNetwork(roadGeometrySpec);
  roadNetwork.segments.forEach(function (road) {
    var rawPoints = road.points || [];
    var roadSpec = road.a && road.b ? routeSpec.find(function (spec) {
      return (spec.kind === 'road' || spec.kind === 'trail' || spec.kind === 'track' || spec.kind === 'portage') &&
        ((spec.a === road.a && spec.b === road.b) || (spec.a === road.b && spec.b === road.a));
    }) : null;
    var roadKind = road.surface || 'road';
    var isFootRoute = roadKind === 'trail' || roadKind === 'track' || roadKind === 'portage';
    var points = road.a || isFootRoute ? rawPoints : anchorRoutePoints(rawPoints, roadSpec, byId);
    if (!points || points.length < 2) { return; }
    if (roadSpec) { tracedRoadLegs[routeLegKey(roadSpec)] = true; }
    var xs = new Float32Array(points.length);
    var zs = new Float32Array(points.length);
    var hs = new Float32Array(points.length);
    for (var i = 0; i < points.length; i++) {
      var wx = Number(points[i][0]);
      var wy = Number(points[i][1]);
      var sc = toScene(wx, wy);
      xs[i] = sc[0];
      zs[i] = sc[1];
      hs[i] = Math.max(0, sampleHeight(wx, wy));
    }
    routeLines.push({
      xs: xs, zs: zs, hs: hs, kind: roadKind,
      multi: false, traced: true,
      details: routeDetails(roadSpec, points, byId, road.name, roadKind)
    });
  });

  seaAirGeometrySpec.forEach(function (route) {
    var rawPoints = route.points || [];
    var tracedSpec = rawPoints.length > 1
      ? routeSpecByName(route.name, rawPoints, byId, route.from, route.to)
      : null;
    var points = anchorRoutePoints(rawPoints, tracedSpec, byId);
    if (points.length < 2) { return; }
    var routeKind = route.surface || 'sea';
    var elevated = routeKind === 'air' || routeKind === 'teleport';
    if (tracedSpec) { tracedSeaAirLegs[routeLegKey(tracedSpec)] = true; }
    var pointCount = elevated ? Math.max(17, (points.length - 1) * 8 + 1) : points.length;
    var xs = new Float32Array(pointCount);
    var zs = new Float32Array(pointCount);
    var hs = new Float32Array(pointCount);
    var lifts = elevated ? new Float32Array(pointCount) : null;
    var firstScene = toScene(Number(points[0][0]), Number(points[0][1]));
    var lastScene = toScene(
      Number(points[points.length - 1][0]), Number(points[points.length - 1][1])
    );
    var span = Math.hypot(lastScene[0] - firstScene[0], lastScene[1] - firstScene[1]);
    var crest = clamp(span * 0.12, 0.035, 0.18);
    var bow = elevated ? clamp(span * 0.055, 0.025, 0.11) : 0;
    var normalX = span ? -(lastScene[1] - firstScene[1]) / span : 0;
    var normalZ = span ? (lastScene[0] - firstScene[0]) / span : 0;
    for (var i = 0; i < pointCount; i++) {
      var progress = pointCount === 1 ? 0 : i / (pointCount - 1);
      var sourcePosition = progress * (points.length - 1);
      var sourceIndex = Math.min(Math.floor(sourcePosition), points.length - 2);
      var sourceProgress = sourcePosition - sourceIndex;
      var wx = Number(points[sourceIndex][0])
        + (Number(points[sourceIndex + 1][0]) - Number(points[sourceIndex][0])) * sourceProgress;
      var wy = Number(points[sourceIndex][1])
        + (Number(points[sourceIndex + 1][1]) - Number(points[sourceIndex][1])) * sourceProgress;
      var sc = toScene(wx, wy);
      var arc = Math.sin(Math.PI * progress);
      xs[i] = sc[0] + normalX * bow * arc;
      zs[i] = sc[1] + normalZ * bow * arc;
      hs[i] = Math.max(0, sampleHeight(wx, wy));
      if (lifts) { lifts[i] = arc * crest; }
    }
    routeLines.push({
      xs: xs, zs: zs, hs: hs, kind: routeKind,
      lifts: lifts, multi: !!route.multimodal, traced: true,
      details: routeDetails(tracedSpec, points, byId, route.name, routeKind)
    });
  });

  routeSpec.forEach(function (r) {
    if (r.kind === 'road' && roadNetwork.connects(r.a, r.b)) { return; }
    if (tracedRoadLegs[routeLegKey(r)] && (r.kind === 'road' || r.kind === 'trail'
      || r.kind === 'track')) { return; }
    if (tracedSeaAirLegs[routeLegKey(r)] && (r.modes || [r.kind]).some(function (mode) {
      return mode === 'sea' || mode === 'air';
    })) { return; }
    var a = byId[r.a];
    var b = byId[r.b];
    if (!a || !b) { return; }
    var overland = r.kind === 'road' || r.kind === 'trail'
      || r.kind === 'track' || r.kind === 'portage';
    var landPoints = overland ? landRoute(a.wx, a.wy, b.wx, b.wy) : null;
    if (overland && !landPoints) { return; }
    var waterGoing = r.kind === 'sea' || r.kind === 'ferry';
    var waterPoints = waterGoing ? waterRoute(a.wx, a.wy, b.wx, b.wy) : null;
    if (waterGoing && !waterPoints) { return; }
    if (waterPoints) {
      waterPoints = anchorRoutePoints(waterPoints, r, byId);
      if (!plausibleCoastingRoute(r, waterPoints)) { return; }
      var waterXs = new Array(waterPoints.length);
      var waterZs = new Array(waterPoints.length);
      var waterHs = new Float32Array(waterPoints.length);
      for (var p = 0; p < waterPoints.length; p++) {
        var waterScene = toScene(waterPoints[p][0], waterPoints[p][1]);
        waterXs[p] = waterScene[0];
        waterZs[p] = waterScene[1];
        waterHs[p] = Math.max(0, sampleHeight(waterPoints[p][0], waterPoints[p][1]));
      }
      routeLines.push({
        xs: waterXs, zs: waterZs, hs: waterHs, kind: r.kind,
        multi: !!r.multimodal, waterRouted: true, inferredRoad: !!r.inferred,
        details: routeDetails(r, waterPoints, byId, r.name, r.kind)
      });
      return;
    }
    if (landPoints) {
      var landXs = new Array(landPoints.length);
      var landZs = new Array(landPoints.length);
      var landHs = new Float32Array(landPoints.length);
      for (var lp = 0; lp < landPoints.length; lp++) {
        var landScene = toScene(landPoints[lp][0], landPoints[lp][1]);
        landXs[lp] = landScene[0];
        landZs[lp] = landScene[1];
        landHs[lp] = Math.max(0, sampleHeight(landPoints[lp][0], landPoints[lp][1]));
      }
      routeLines.push({
        xs: landXs, zs: landZs, hs: landHs, kind: r.kind,
        multi: !!r.multimodal, landRouted: true,
        inferredRoad: !!r.inferred || (r.kind === 'road' && roadGeometrySpec.length > 0),
        details: routeDetails(r, landPoints, byId, r.name, r.kind)
      });
      return;
    }
    var elevated = r.kind === 'air' || r.kind === 'teleport';
    var routeSteps = elevated ? 16 : steps;
    var xs = new Float32Array(routeSteps + 1);
    var zs = new Float32Array(routeSteps + 1);
    var hs = new Float32Array(routeSteps + 1);
    var lifts = elevated ? new Float32Array(routeSteps + 1) : null;
    var span = Math.hypot(b.sx - a.sx, b.sz - a.sz);
    var crest = clamp(span * 0.12, 0.035, 0.18);
    var bow = elevated ? clamp(span * 0.055, 0.025, 0.11) : 0;
    var normalX = span ? -(b.sz - a.sz) / span : 0;
    var normalZ = span ? (b.sx - a.sx) / span : 0;
    for (var k = 0; k <= routeSteps; k++) {
      var t = k / routeSteps;
      var wx = a.wx + (b.wx - a.wx) * t;
      var wy = a.wy + (b.wy - a.wy) * t;
      var sc = toScene(wx, wy);
      var arc = Math.sin(Math.PI * t);
      xs[k] = sc[0] + normalX * bow * arc;
      zs[k] = sc[1] + normalZ * bow * arc;
      hs[k] = Math.max(sampleHeight(wx, wy), a.h * (1 - t) + b.h * t);
      if (lifts) { lifts[k] = arc * crest; }
    }
    routeLines.push({
      xs: xs, zs: zs, hs: hs, kind: r.kind, lifts: lifts,
      multi: !!r.multimodal, inferredRoad: !!r.inferred,
      details: routeDetails(r, [[a.wx, a.wy], [b.wx, b.wy]], byId, r.name, r.kind)
    });
  });
}

// ---------------------------------------------------------------------------
// realignment
//
// The shipped coordinates were tuned for plausible travel times, and their
// error is not uniform - the Sword Coast is close to canon while the Western
// Heartlands are squashed and the Backlands stretched. No pan/scale nudge of
// the poster can reconcile that, because one rigid transform cannot undo a
// distortion that changes sign across the map. So instead the user pins a few
// markets to their true positions and everything else is carried along by a
// smooth fit. This mirrors faerun/calibration.py so the preview matches what
// the server will save.
// ---------------------------------------------------------------------------

var CALIB_EPSILON = 1.0;   // miles; keeps the weights finite at a control point
var CALIB_FALLOFF = 900.0; // miles; beyond this a control point stops pulling
var calibWarp = null;

function solve3(m, rhs) {
  var a = [];
  var i, j, c, r;
  for (i = 0; i < 3; i++) { a.push([m[i][0], m[i][1], m[i][2], rhs[i]]); }
  for (c = 0; c < 3; c++) {
    var pivot = c;
    for (r = c + 1; r < 3; r++) {
      if (Math.abs(a[r][c]) > Math.abs(a[pivot][c])) { pivot = r; }
    }
    if (Math.abs(a[pivot][c]) < 1e-9) { return null; }
    var tmp = a[c]; a[c] = a[pivot]; a[pivot] = tmp;
    var pv = a[c][c];
    for (r = 0; r < 3; r++) {
      if (r === c) { continue; }
      var f = a[r][c] / pv;
      if (!f) { continue; }
      for (j = c; j < 4; j++) { a[r][j] -= f * a[c][j]; }
    }
  }
  return [a[0][3] / a[0][0], a[1][3] / a[1][1], a[2][3] / a[2][2]];
}

function fitAffine(pts) {
  if (pts.length < 3) { return null; }
  var n = [[0, 0, 0], [0, 0, 0], [0, 0, 0]];
  var bx = [0, 0, 0];
  var by = [0, 0, 0];
  pts.forEach(function (p) {
    var basis = [p.baseX, p.baseY, 1];
    for (var i = 0; i < 3; i++) {
      for (var j = 0; j < 3; j++) { n[i][j] += basis[i] * basis[j]; }
      bx[i] += basis[i] * p.x;
      by[i] += basis[i] * p.y;
    }
  });
  var sx = solve3(n, bx);
  var sy = solve3(n, by);
  if (!sx || !sy) { return null; }
  return [sx[0], sx[1], sx[2], sy[0], sy[1], sy[2]];
}

function fitSimilarity(pts) {
  // Rotation, uniform scale and translation. Needs only two points and never
  // goes singular on collinear input, which is where the affine fit gives up.
  var n = pts.length;
  if (n < 2) { return null; }
  var sx0 = 0, sy0 = 0, tx0 = 0, ty0 = 0;
  pts.forEach(function (p) { sx0 += p.baseX; sy0 += p.baseY; tx0 += p.x; ty0 += p.y; });
  sx0 /= n; sy0 /= n; tx0 /= n; ty0 /= n;
  var numRe = 0, numIm = 0, den = 0;
  pts.forEach(function (p) {
    var ax = p.baseX - sx0, ay = p.baseY - sy0;
    var bx = p.x - tx0, by = p.y - ty0;
    numRe += bx * ax + by * ay;
    numIm += by * ax - bx * ay;
    den += ax * ax + ay * ay;
  });
  if (den < 1e-9) { return null; }
  var a = numRe / den, b = numIm / den;
  return [a, -b, tx0 - (a * sx0 - b * sy0), b, a, ty0 - (b * sx0 + a * sy0)];
}

function buildCalibWarp(pts) {
  if (!pts || !pts.length) { return null; }
  if (pts.length === 1) {
    var dx = pts[0].x - pts[0].baseX;
    var dy = pts[0].y - pts[0].baseY;
    return function (x, y) { return [x + dx, y + dy]; };
  }
  var k = fitAffine(pts) || fitSimilarity(pts);
  if (!k) {
    var mx = 0, my = 0;
    pts.forEach(function (p) { mx += p.x - p.baseX; my += p.y - p.baseY; });
    mx /= pts.length; my /= pts.length;
    k = [1, 0, mx, 0, 1, my];
  }
  function affine(x, y) {
    return [k[0] * x + k[1] * y + k[2], k[3] * x + k[4] * y + k[5]];
  }
  // Whatever the affine part could not explain, fed back in by inverse-distance
  // weighting. That is what makes the fit land exactly on every control point
  // rather than merely near it.
  var anchors = pts.map(function (p) {
    var a = affine(p.baseX, p.baseY);
    return { x: p.baseX, y: p.baseY, rx: p.x - a[0], ry: p.y - a[1] };
  });
  return function (x, y) {
    var b = affine(x, y);
    var total = 0, sx = 0, sy = 0;
    for (var i = 0; i < anchors.length; i++) {
      var an = anchors[i];
      var dx = x - an.x, dy = y - an.y;
      var d2 = dx * dx + dy * dy;
      if (d2 < 1e-12) { return [b[0] + an.rx, b[1] + an.ry]; }
      var taper = 1 - Math.sqrt(d2) / CALIB_FALLOFF;
      if (taper <= 0) { continue; }
      var w = taper * taper / (d2 + CALIB_EPSILON);
      total += w; sx += w * an.rx; sy += w * an.ry;
    }
    if (total <= 0) { return b; }
    return [b[0] + sx / total, b[1] + sy / total];
  };
}

function refreshCalibWarp() {
  calibWarp = buildCalibWarp(state.calibPoints);
}

// Where a market should be drawn right now. With no control points loaded we
// trust whatever the server sent, so a saved calibration never flickers back to
// the shipped position while /api/calibration is still in flight.
function calibratedXY(s) {
  if (s.mobile) { return [s.x, s.y]; }
  if (!calibWarp) { return [s.x, s.y]; }
  var bx = (s.bx === undefined || s.bx === null) ? s.x : s.bx;
  var by = (s.by === undefined || s.by === null) ? s.y : s.by;
  return calibWarp(bx, by);
}

// Screen point -> world miles, by casting a ray onto the terrain. Two passes:
// hit sea level, sample the relief there, then re-hit at that height. That is
// enough to kill the parallax that would otherwise put a click on a mountain
// tens of miles from where it looks like it landed.
function groundPoint(px, py) {
  if (!mesh || state.globe) { return null; }
  var a = (px - cam.cx) / cam.focal;
  var b = (cam.cy - py) / cam.focal;
  var dx = cam.fx + a * cam.rx + b * cam.ux;
  var dy = cam.fy + a * cam.ry + b * cam.uy;
  var dz = cam.fz + a * cam.rz + b * cam.uz;
  if (Math.abs(dy) < 1e-6) { return null; }
  var height = 0;
  var world = null;
  for (var pass = 0; pass < 3; pass++) {
    var t = (height - cam.ey) / dy;
    if (t <= 0) { return null; }
    world = [
      (cam.ex + t * dx) * SCALE + mesh.cx,
      (cam.ez + t * dz) * SCALE + mesh.cy
    ];
    height = sampleHeight(world[0], world[1]) * state.exag;
  }
  return world;
}

// Two clicks make a control point: first the market, then where it truly sits.
// Picking a market takes priority over dropping a target, so a mis-click on a
// neighbouring dot re-arms rather than pinning the wrong city on top of it.
function handleCalibClick(hit, px, py) {
  if (!state.calibArmed) {
    if (hit >= 0 && !pins[hit].data.mobile) {
      state.calibArmed = pins[hit].data.id;
      updateCalibHud();
      invalidate();
    }
    return;
  }
  if (hit >= 0 && pins[hit].data.id === state.calibArmed) {
    state.calibArmed = '';
    updateCalibHud();
    invalidate();
    return;
  }
  var world = groundPoint(px, py);
  if (!world) { return; }
  var id = state.calibArmed;
  state.calibArmed = '';
  setCalibPoint(id, world[0], world[1]);
}

function updateTerrainEditHud() {
  var help = document.getElementById('terrain-edit-help');
  if (!help) { return; }
  help.textContent = state.terrainEditOn
    ? 'Click a cell to save the correction. Choose Automatic to remove it.'
    : '';
}

function setTerrainEditMode(on) {
  state.terrainEditOn = !!on;
  document.getElementById('opt-terrain-edit').checked = state.terrainEditOn;
  canvas.classList.toggle('terrain-editing', state.terrainEditOn);
  if (state.terrainEditOn) {
    setCalibMode(false);
    state.globe = false;
    document.getElementById('opt-globe').checked = false;
    state.yaw = 0;
    state.pitch = 1.45;
    state.tiles = 'square';
    document.getElementById('opt-tiles').value = 'square';
    if (mesh) { fitView(); }
  }
  updateTerrainEditHud();
  invalidate();
}

async function saveTerrainCell(px, py) {
  if (!mesh || mesh.detail || state.terrainEditSaving) {
    showStatus(mesh && mesh.detail
      ? 'Return to the world view before correcting world-grid cells.'
      : 'Terrain correction is unavailable here.', true);
    return;
  }
  var world = groundPoint(px, py);
  if (!world) { return; }
  var column = Math.floor((world[0] - mesh.bounds[0]) / mesh.cellW);
  var row = Math.floor((world[1] - mesh.bounds[1]) / mesh.cellH);
  if (column < 0 || column >= mesh.W || row < 0 || row >= mesh.H) { return; }
  var select = document.getElementById('terrain-edit-type');
  var terrain = select.value;
  var label = select.options[select.selectedIndex].text;
  state.terrainEditSaving = true;
  showStatus('Saving terrain correction...');
  try {
    var data = await postJson('/api/terrain-cell', {
      column: column, row: row, terrain: terrain
    });
    state.map = data;
    buildMesh(data);
    buildPins(data.settlements);
    buildPlaces(data.places || []);
    buildRoutes(data.routes || [], data.roadGeometries || [], data.seaAirGeometries || []);
    showStatus('Cell ' + column + ', ' + row + ' set to ' + label + '.');
  } catch (err) {
    showStatus(String(err.message || err), true);
  } finally {
    state.terrainEditSaving = false;
    invalidate();
  }
}

function calibIndexOf(id) {
  for (var i = 0; i < state.calibPoints.length; i++) {
    if (state.calibPoints[i].id === id) { return i; }
  }
  return -1;
}

function setCalibPoint(id, wx, wy) {
  var pin = null;
  for (var i = 0; i < pins.length; i++) {
    if (pins[i].data.id === id) { pin = pins[i]; break; }
  }
  if (!pin) { return; }
  var s = pin.data;
  var entry = {
    id: id,
    name: s.name,
    x: Math.round(wx * 10) / 10,
    y: Math.round(wy * 10) / 10,
    baseX: (s.bx === undefined || s.bx === null) ? s.x : s.bx,
    baseY: (s.by === undefined || s.by === null) ? s.y : s.by
  };
  var at = calibIndexOf(id);
  if (at >= 0) { state.calibPoints[at] = entry; } else { state.calibPoints.push(entry); }
  state.calibDirty = true;
  applyCalibration();
}

// Re-place every marker (and the roads between them) through the current fit.
// The relief is deliberately left alone: it is our invention, the poster is the
// real map, and the server restamps the land under the new positions on the
// next full load anyway.
function applyCalibration() {
  refreshCalibWarp();
  if (pins) {
    pins.forEach(function (p) {
      var w = calibratedXY(p.data);
      p.wx = w[0];
      p.wy = w[1];
      var sc = toScene(w[0], w[1]);
      p.sx = sc[0];
      p.sz = sc[1];
      p.h = sampleHeight(w[0], w[1]);
    });
    rebuildRouteGeometry();
  }
  updateCalibHud();
  invalidate();
}

// ---------------------------------------------------------------------------
// camera
// ---------------------------------------------------------------------------

function updateCamera() {
  var cp = Math.cos(state.pitch), sp = Math.sin(state.pitch);
  var cyw = Math.cos(state.yaw), syw = Math.sin(state.yaw);
  cam.ex = state.tx + state.dist * cp * syw;
  cam.ey = state.dist * sp;
  cam.ez = state.tz + state.dist * cp * cyw;

  var fx = state.tx - cam.ex, fy = -cam.ey, fz = state.tz - cam.ez;
  var flen = Math.sqrt(fx * fx + fy * fy + fz * fz) || 1;
  cam.fx = fx / flen; cam.fy = fy / flen; cam.fz = fz / flen;

  // right = normalise(forward x up), with up = (0, 1, 0)
  var rx = -cam.fz, ry = 0, rz = cam.fx;
  var rlen = Math.sqrt(rx * rx + rz * rz) || 1;
  cam.rx = rx / rlen; cam.ry = ry; cam.rz = rz / rlen;

  // up = right x forward
  cam.ux = cam.ry * cam.fz - cam.rz * cam.fy;
  cam.uy = cam.rz * cam.fx - cam.rx * cam.fz;
  cam.uz = cam.rx * cam.fy - cam.ry * cam.fx;
}

var _pt = [0, 0, 0];

function globeRadius() {
  return Math.min(cam.cx, cam.cy) * 0.88 * state.globeZoom;
}

function globeAngles(x, z) {
  var minX = mesh.vx[0], maxX = mesh.vx[mesh.W];
  var minZ = mesh.vz[0], maxZ = mesh.vz[mesh.H];
  var across = (x - minX) / (maxX - minX);
  var down = (z - minZ) / (maxZ - minZ);
  return [
    GLOBE_FAERUN_WEST + across * (GLOBE_FAERUN_EAST - GLOBE_FAERUN_WEST),
    GLOBE_FAERUN_NORTH + down * (GLOBE_FAERUN_SOUTH - GLOBE_FAERUN_NORTH)
  ];
}

function projectGlobe(x, y, z) {
  var angles = globeAngles(x, z);
  var longitude = angles[0] + state.yaw;
  var latitude = angles[1];
  var cosLatitude = Math.cos(latitude);
  var sphereX = cosLatitude * Math.sin(longitude);
  var sphereY = Math.sin(latitude);
  var sphereZ = cosLatitude * Math.cos(longitude);
  var cosTilt = Math.cos(state.globeTilt), sinTilt = Math.sin(state.globeTilt);
  var rotatedY = sphereY * cosTilt - sphereZ * sinTilt;
  var rotatedZ = sphereY * sinTilt + sphereZ * cosTilt;
  if (rotatedZ < -0.015) { return null; }
  var radius = globeRadius() * (1 + Math.max(0, y) * 0.025);
  _pt[0] = cam.cx + sphereX * radius;
  _pt[1] = cam.cy - rotatedY * radius;
  _pt[2] = 2 - rotatedZ;
  return _pt;
}

function project(x, y, z) {
  if (state.globe) { return projectGlobe(x, y, z); }
  var dx = x - cam.ex, dy = y - cam.ey, dz = z - cam.ez;
  var vz = dx * cam.fx + dy * cam.fy + dz * cam.fz;
  if (vz < 0.06) { return null; }
  var s = cam.focal / vz;
  _pt[0] = cam.cx + (dx * cam.rx + dy * cam.ry + dz * cam.rz) * s;
  _pt[1] = cam.cy - (dx * cam.ux + dy * cam.uy + dz * cam.uz) * s;
  _pt[2] = vz;
  return _pt;
}

function posterBounds() {
  var img = state.under;
  if (MAP_VIEW !== 'overlay' || !img || !img.width || !img.height) { return null; }
  var width = img.width * state.underMpp;
  var height = img.height * state.underMpp * state.underStretch;
  if (!(width > 0) || !(height > 0)) { return null; }
  return [
    state.underX,
    state.underY,
    state.underX + width,
    state.underY + height
  ];
}

function roundWorldBounds() {
  var b = mesh.detail ? mesh.bounds : (posterBounds() || mesh.bounds);
  var width = b[2] - b[0];
  var height = b[3] - b[1];
  // A diagonal-sized disk contains every map corner; the ocean base fills the
  // crescents outside the rectangular source artwork. A local detail patch
  // instead owns an inscribed disk, so surveyed terrain reaches its full rim.
  var diameter = mesh.detail
    ? Math.min(width, height)
    : Math.sqrt(width * width + height * height);
  var cx = (b[0] + b[2]) / 2;
  var cy = (b[1] + b[3]) / 2;
  return [cx - diameter / 2, cy - diameter / 2,
          cx + diameter / 2, cy + diameter / 2];
}

function traceRoundWorld() {
  var b = roundWorldBounds();
  var cx = (b[0] + b[2]) / 2;
  var cy = (b[1] + b[3]) / 2;
  var radius = (b[2] - b[0]) / 2;
  ctx.beginPath();
  for (var i = 0; i <= 96; i++) {
    var angle = Math.PI * 2 * i / 96;
    var sc = toScene(cx + Math.cos(angle) * radius,
                     cy + Math.sin(angle) * radius);
    var p = project(sc[0], 0, sc[1]);
    if (!p) { return false; }
    if (i === 0) { ctx.moveTo(p[0], p[1]); }
    else { ctx.lineTo(p[0], p[1]); }
  }
  ctx.closePath();
  return true;
}

function clipRoundWorld() {
  if (!traceRoundWorld()) { return false; }
  ctx.clip();
  return true;
}

function scenePointInRoundWorld(x, z) {
  if (!state.roundWorld) { return true; }
  var b = roundWorldBounds();
  var centre = toScene((b[0] + b[2]) / 2, (b[1] + b[3]) / 2);
  var radius = (b[2] - b[0]) / (2 * SCALE);
  var dx = x - centre[0];
  var dz = z - centre[1];
  return dx * dx + dz * dz <= radius * radius;
}

function drawRoundWorldBase() {
  if (!state.roundWorld || !traceRoundWorld()) { return; }
  var ocean = DEEP_OCEAN;
  ctx.fillStyle = 'rgb(' + ocean[0] + ',' + ocean[1] + ',' + ocean[2] + ')';
  ctx.fill();
}

function drawRoundWorldEdge() {
  if (!state.roundWorld || !traceRoundWorld()) { return; }
  ctx.strokeStyle = 'rgba(28, 35, 38, .82)';
  ctx.lineWidth = 2;
  ctx.stroke();
}

function fitView() {
  // The poster page is its image, not the larger terrain union behind it.
  // Fitting that exact calibrated footprint preserves the artwork's aspect.
  var b = state.roundWorld ? roundWorldBounds() : (posterBounds() || mesh.bounds);
  if (state.roundWorld) {
    var centre = toScene((b[0] + b[2]) / 2, (b[1] + b[3]) / 2);
    state.tx = centre[0];
    state.tz = centre[1];
  }
  var corners = [
    [b[0], b[1]], [b[2], b[1]], [b[0], b[3]], [b[2], b[3]],
    [(b[0] + b[2]) / 2, b[1]], [(b[0] + b[2]) / 2, b[3]]
  ];
  for (var pass = 0; pass < 6; pass++) {
    updateCamera();
    var minX = 1e9, maxX = -1e9, minY = 1e9, maxY = -1e9, seen = 0;
    for (var i = 0; i < corners.length; i++) {
      var sc = toScene(corners[i][0], corners[i][1]);
      var p = project(sc[0], 0, sc[1]);
      if (!p) { continue; }
      seen++;
      if (p[0] < minX) { minX = p[0]; }
      if (p[0] > maxX) { maxX = p[0]; }
      if (p[1] < minY) { minY = p[1]; }
      if (p[1] > maxY) { maxY = p[1]; }
    }
    if (seen < 3) { state.dist *= 1.35; continue; }
    var needW = (maxX - minX) / (cam.cx * 2 * 0.92);
    var needH = (maxY - minY) / (cam.cy * 2 * 0.92);
    var need = Math.max(needW, needH);
    if (need > 0.001) { state.dist *= need; }
    if (Math.abs(need - 1) < 0.02) { break; }
  }
  if (state.roundWorld) { state.dist *= 1.06; }
  state.dist = clamp(state.dist, 0.35, 12);
}

function clipGroundToPoster() {
  var b = posterBounds();
  if (!b) { return false; }
  var world = [
    [b[0], b[1]], [b[2], b[1]], [b[2], b[3]], [b[0], b[3]]
  ];
  ctx.beginPath();
  for (var i = 0; i < world.length; i++) {
    var sc = toScene(world[i][0], world[i][1]);
    var p = project(sc[0], 0, sc[1]);
    if (!p) { return false; }
    if (i === 0) { ctx.moveTo(p[0], p[1]); }
    else { ctx.lineTo(p[0], p[1]); }
  }
  ctx.closePath();
  ctx.clip();
  return true;
}

function resize() {
  var dpr = window.devicePixelRatio || 1;
  var w = canvas.clientWidth || 800;
  var h = canvas.clientHeight || 600;
  canvas.width = Math.round(w * dpr);
  canvas.height = Math.round(h * dpr);
  underCanvas.width = canvas.width;
  underCanvas.height = canvas.height;
  ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
  cam.dpr = dpr;
  cam.cx = w / 2;
  cam.cy = h / 2;
  cam.focal = Math.min(w, h) * 0.95;
  invalidate();
}

// ---------------------------------------------------------------------------
// drawing
// ---------------------------------------------------------------------------

function drawSky() {
  // Flat white, deliberately not a gradient: the backdrop should read as empty
  // paper so the only tonal variation on screen belongs to the terrain itself.
  var w = cam.cx * 2, h = cam.cy * 2;
  ctx.fillStyle = '#ffffff';
  ctx.fillRect(0, 0, w, h);
}

function projectVertices() {
  var W = mesh.W, H = mesh.H;
  var vx = mesh.vx, vz = mesh.vz, vh = mesh.vh;
  var px = mesh.px, py = mesh.py, pd = mesh.pd, ok = mesh.ok;
  var exag = state.exag;
  if (state.globe) {
    var globeIndex = 0;
    for (var globeRow = 0; globeRow <= H; globeRow++) {
      for (var globeColumn = 0; globeColumn <= W; globeColumn++, globeIndex++) {
        var globePoint = project(vx[globeColumn], vh[globeIndex] * exag, vz[globeRow]);
        if (!globePoint) { ok[globeIndex] = 0; continue; }
        px[globeIndex] = globePoint[0];
        py[globeIndex] = globePoint[1];
        pd[globeIndex] = globePoint[2];
        ok[globeIndex] = 1;
      }
    }
    return;
  }
  var k = 0;
  for (var j = 0; j <= H; j++) {
    var z = vz[j];
    var dz = z - cam.ez;
    for (var i = 0; i <= W; i++, k++) {
      var dx = vx[i] - cam.ex;
      var dy = vh[k] * exag - cam.ey;
      var d = dx * cam.fx + dy * cam.fy + dz * cam.fz;
      if (d < 0.06) { ok[k] = 0; continue; }
      var s = cam.focal / d;
      px[k] = cam.cx + (dx * cam.rx + dy * cam.ry + dz * cam.rz) * s;
      py[k] = cam.cy - (dx * cam.ux + dy * cam.uy + dz * cam.uz) * s;
      ok[k] = 1;
    }
  }
}

function drawGlobeTerrain() {
  var W = mesh.W, H = mesh.H, step = state.step;
  var px = mesh.px, py = mesh.py, pd = mesh.pd, ok = mesh.ok;
  var row = W + 1, cells = [];
  for (var j = 0; j < H; j += step) {
    var j2 = Math.min(j + step, H);
    for (var i = 0; i < W; i += step) {
      var i2 = Math.min(i + step, W);
      var v0 = j * row + i, v1 = j * row + i2;
      var v2 = j2 * row + i2, v3 = j2 * row + i;
      if (!ok[v0] || !ok[v1] || !ok[v2] || !ok[v3]) { continue; }
      cells.push({
        depth: (pd[v0] + pd[v1] + pd[v2] + pd[v3]) / 4,
        points: [v0, v1, v2, v3],
        color: mesh.colors[j * W + i]
      });
    }
  }
  cells.sort(function (a, b) { return b.depth - a.depth; });
  for (var cellIndex = 0; cellIndex < cells.length; cellIndex++) {
    var cell = cells[cellIndex], points = cell.points;
    ctx.beginPath();
    ctx.moveTo(px[points[0]], py[points[0]]);
    for (var pointIndex = 1; pointIndex < points.length; pointIndex++) {
      ctx.lineTo(px[points[pointIndex]], py[points[pointIndex]]);
    }
    ctx.closePath();
    ctx.fillStyle = cell.color;
    ctx.fill();
  }
}

function drawGlobeBase() {
  ctx.beginPath();
  ctx.arc(cam.cx, cam.cy, globeRadius(), 0, Math.PI * 2);
  ctx.fillStyle = 'rgb(' + DEEP_OCEAN[0] + ',' + DEEP_OCEAN[1] + ',' + DEEP_OCEAN[2] + ')';
  ctx.fill();
  ctx.lineWidth = 2;
  ctx.strokeStyle = 'rgba(22, 35, 38, .78)';
  ctx.stroke();
  ctx.clip();
}

function drawTerrain() {
  var W = mesh.W, H = mesh.H, step = state.step;
  var px = mesh.px, py = mesh.py, ok = mesh.ok, colors = mesh.colors;
  var row = W + 1;

  // Painter's algorithm on an axis-aligned grid: walk each axis away from the
  // eye, so nearer cells are painted over farther ones.
  var cols = [];
  var rows = [];
  var i, j;
  for (i = 0; i < W; i += step) { cols.push(i); }
  for (j = 0; j < H; j += step) { rows.push(j); }
  if (Math.sin(state.yaw) <= 0) { cols.reverse(); }
  if (Math.cos(state.yaw) <= 0) { rows.reverse(); }

  for (var rj = 0; rj < rows.length; rj++) {
    j = rows[rj];
    var j2 = Math.min(j + step, H);
    var a0 = j * row;
    var a1 = j2 * row;
    for (var ri = 0; ri < cols.length; ri++) {
      i = cols[ri];
      var i2 = Math.min(i + step, W);
      if (!scenePointInRoundWorld((mesh.vx[i] + mesh.vx[i2]) / 2,
                                  (mesh.vz[j] + mesh.vz[j2]) / 2)) { continue; }
      var v0 = a0 + i, v1 = a0 + i2, v2 = a1 + i2, v3 = a1 + i;
      if (!ok[v0] || !ok[v1] || !ok[v2] || !ok[v3]) { continue; }
      ctx.fillStyle = colors[j * W + i];
      ctx.beginPath();
      ctx.moveTo(px[v0], py[v0]);
      ctx.lineTo(px[v1], py[v1]);
      ctx.lineTo(px[v2], py[v2]);
      ctx.lineTo(px[v3], py[v3]);
      ctx.closePath();
      ctx.fill();
    }
  }
}

function traceTowerFace(points) {
  ctx.beginPath();
  ctx.moveTo(points[0][0], points[0][1]);
  for (var i = 1; i < points.length; i++) {
    ctx.lineTo(points[i][0], points[i][1]);
  }
  ctx.closePath();
}

function drawTowerFace(points, color, shadow) {
  traceTowerFace(points);
  ctx.fillStyle = color;
  ctx.fill();
  if (shadow > 0) {
    traceTowerFace(points);
    ctx.fillStyle = 'rgba(0, 0, 0, ' + shadow + ')';
    ctx.fill();
  }
}

function drawTowers() {
  var W = mesh.W, H = mesh.H, step = state.step;
  var vx = mesh.vx, vz = mesh.vz, cells = mesh.cells, colors = mesh.colors;
  var cols = [], rows = [];
  var i, j;
  for (i = 0; i < W; i += step) { cols.push(i); }
  for (j = 0; j < H; j += step) { rows.push(j); }
  if (Math.sin(state.yaw) <= 0) { cols.reverse(); }
  if (Math.cos(state.yaw) <= 0) { rows.reverse(); }

  var xNearRight = Math.sin(state.yaw) > 0;
  var zNearBottom = Math.cos(state.yaw) > 0;
  for (var rj = 0; rj < rows.length; rj++) {
    j = rows[rj];
    var j2 = Math.min(j + step, H);
    for (var ri = 0; ri < cols.length; ri++) {
      i = cols[ri];
      var i2 = Math.min(i + step, W);
      var raw = Math.max(0, cells[j * W + i] / 1000.0);
      var top = raw * state.exag;
      var x0 = vx[i], x1 = vx[i2], z0 = vz[j], z1 = vz[j2];
      if (!scenePointInRoundWorld((x0 + x1) / 2, (z0 + z1) / 2)) { continue; }
      var topPoints = [];
      var corners = [[x0, z0], [x1, z0], [x1, z1], [x0, z1]];
      var visible = true;
      for (var c = 0; c < 4; c++) {
        var projected = project(corners[c][0], top, corners[c][1]);
        if (!projected) { visible = false; break; }
        topPoints.push([projected[0], projected[1]]);
      }
      if (!visible) { continue; }

      if (top > 0.00001) {
        var xa = xNearRight ? 1 : 0;
        var xb = xNearRight ? 2 : 3;
        var xBaseA = project(corners[xa][0], 0, corners[xa][1]);
        if (xBaseA) { xBaseA = [xBaseA[0], xBaseA[1]]; }
        var xBaseB = project(corners[xb][0], 0, corners[xb][1]);
        if (xBaseB && xBaseA) {
          drawTowerFace([topPoints[xa], topPoints[xb],
            [xBaseB[0], xBaseB[1]], xBaseA], colors[j * W + i], 0.30);
        }

        var za = zNearBottom ? 2 : 0;
        var zb = zNearBottom ? 3 : 1;
        var zBaseA = project(corners[za][0], 0, corners[za][1]);
        if (zBaseA) { zBaseA = [zBaseA[0], zBaseA[1]]; }
        var zBaseB = project(corners[zb][0], 0, corners[zb][1]);
        if (zBaseB && zBaseA) {
          drawTowerFace([topPoints[za], topPoints[zb],
            [zBaseB[0], zBaseB[1]], zBaseA], colors[j * W + i], 0.18);
        }
      }
      drawTowerFace(topPoints, colors[j * W + i], 0);
      ctx.strokeStyle = 'rgba(0, 0, 0, .28)';
      ctx.lineWidth = 0.55;
      traceTowerFace(topPoints);
      ctx.stroke();
    }
  }
}

// Unit offsets for a pointy-top hexagon, clockwise from the top point. X is
// scaled by the half-width and Z by the corner radius, so the tile stays keyed
// to the cell block underneath it even though the cells are square.
var HEX_DX = [0, 1, 1, 0, -1, -1];
var HEX_DZ = [-1, -0.5, 0.5, 1, 0.5, -0.5];

function roundGridSceneBounds() {
  var b = roundWorldBounds();
  var a = toScene(b[0], b[1]);
  var z = toScene(b[2], b[3]);
  return [a[0], a[1], z[0], z[1]];
}

function drawRoundHexGrid() {
  if (!state.roundWorld) { return; }
  var s = state.hexStep;
  var cellW = mesh.vx[1] - mesh.vx[0];
  var cellH = mesh.vz[1] - mesh.vz[0];
  var colSpan = cellW * s;
  var rowSpan = cellH * s;
  var hx = colSpan * 0.51;
  var radius = (rowSpan / 1.5) * 1.02;
  var b = roundGridSceneBounds();
  var rowStart = Math.floor((b[1] - mesh.vz[0]) / rowSpan) - 1;
  var rowEnd = Math.ceil((b[3] - mesh.vz[0]) / rowSpan) + 1;

  ctx.lineJoin = 'round';
  ctx.lineWidth = 0.75;
  ctx.strokeStyle = 'rgba(0, 0, 0, .42)';
  for (var row = rowStart; row <= rowEnd; row++) {
    var shift = (Math.abs(row) % 2) ? colSpan * 0.5 : 0;
    var cz = mesh.vz[0] + row * rowSpan + rowSpan * 0.5;
    var colStart = Math.floor((b[0] - mesh.vx[0] - shift) / colSpan) - 1;
    var colEnd = Math.ceil((b[2] - mesh.vx[0] - shift) / colSpan) + 1;
    for (var col = colStart; col <= colEnd; col++) {
      var cx = mesh.vx[0] + col * colSpan + colSpan * 0.5 + shift;
      ctx.beginPath();
      for (var v = 0; v < 6; v++) {
        var p = project(cx + HEX_DX[v] * hx, 0, cz + HEX_DZ[v] * radius);
        if (!p) { break; }
        if (v === 0) { ctx.moveTo(p[0], p[1]); }
        else { ctx.lineTo(p[0], p[1]); }
      }
      if (v === 6) { ctx.closePath(); ctx.stroke(); }
    }
  }
}

// Hex tiling, offered as an alternative to the smooth relief above.
//
// The height field is sampled on a square grid, so the hexes are laid out
// "odd-r": each tile covers an s x s block of cells and every other band is
// pushed half a column across so the tiles interlock. A tile is flat at the
// mean height of its block, which is what gives the boardgame look. Because
// row spacing is s cells but the corner radius is s/1.5 cells, neighbouring
// bands overlap by design and no wall geometry is needed to close the seams.
function drawHexTerrain(gridOnly, towers, icons) {
  var W = mesh.W, H = mesh.H, s = state.hexStep;
  var vx = mesh.vx, vz = mesh.vz, cells = mesh.cells, colors = mesh.colors;
  var exag = state.exag;

  var colSpan = (vx[1] - vx[0]) * s;
  var rowSpan = (vz[1] - vz[0]) * s;
  var hx = colSpan * 0.51;
  var R = (rowSpan / 1.5) * 1.02;

  // Same painter's ordering as the square pass: walk both axes away from the
  // eye so nearer tiles are laid over farther ones.
  var cols = [];
  var rows = [];
  var i, j, v;
  for (i = 0; i < W; i += s) { cols.push(i); }
  for (j = 0; j < H; j += s) { rows.push(j); }
  if (Math.sin(state.yaw) <= 0) { cols.reverse(); }
  if (Math.cos(state.yaw) <= 0) { rows.reverse(); }

  if (gridOnly) {
    drawRoundHexGrid();
    ctx.lineJoin = 'round';
    ctx.lineWidth = 0.75;
    ctx.strokeStyle = 'rgba(0, 0, 0, .42)';
  }

  var xs = [0, 0, 0, 0, 0, 0];
  var ys = [0, 0, 0, 0, 0, 0];
  var baseXs = [0, 0, 0, 0, 0, 0];
  var baseYs = [0, 0, 0, 0, 0, 0];

  for (var rj = 0; rj < rows.length; rj++) {
    j = rows[rj];
    var shift = (((j / s) | 0) % 2) ? colSpan * 0.5 : 0;
    var cz = vz[j] + rowSpan * 0.5;
    var mj = Math.min(H - 1, j + (s >> 1));

    for (var ri = 0; ri < cols.length; ri++) {
      i = cols[ri];

      // Mean height of the block, with water clamped to sea level so the
      // ocean stays a flat sheet exactly as it does in smooth mode.
      var total = 0.0;
      var n = 0;
      for (var dj = 0; dj < s && j + dj < H; dj++) {
        var base = (j + dj) * W;
        for (var di = 0; di < s && i + di < W; di++) {
          var raw = cells[base + i + di] / 1000.0;
          total += raw > 0 ? raw : 0.0;
          n++;
        }
      }
      var hy = (n > 0 ? total / n : 0.0) * exag;
      var cxw = vx[i] + colSpan * 0.5 + shift;
      if (!scenePointInRoundWorld(cxw, cz)) { continue; }

      var vis = true;
      for (v = 0; v < 6; v++) {
        var p = project(cxw + HEX_DX[v] * hx, hy, cz + HEX_DZ[v] * R);
        if (!p) { vis = false; break; }
        xs[v] = p[0];
        ys[v] = p[1];
      }
      if (!vis) { continue; }

      var color = colors[mj * W + Math.min(W - 1, i + (s >> 1))];
      if (towers && hy > 0.00001) {
        for (v = 0; v < 6; v++) {
          var bp = project(cxw + HEX_DX[v] * hx, 0, cz + HEX_DZ[v] * R);
          if (!bp) { vis = false; break; }
          baseXs[v] = bp[0];
          baseYs[v] = bp[1];
        }
        if (!vis) { continue; }
        for (v = 0; v < 6; v++) {
          var next = (v + 1) % 6;
          var edgeX = (HEX_DX[next] - HEX_DX[v]) * hx;
          var edgeZ = (HEX_DZ[next] - HEX_DZ[v]) * R;
          var normalX = edgeZ;
          var normalZ = -edgeX;
          var eyeX = cam.ex - cxw;
          var eyeZ = cam.ez - cz;
          if (normalX * eyeX + normalZ * eyeZ <= 0) { continue; }
          drawTowerFace([[xs[v], ys[v]], [xs[next], ys[next]],
            [baseXs[next], baseYs[next]], [baseXs[v], baseYs[v]]],
            color, v % 2 ? 0.20 : 0.30);
        }
      }

      ctx.beginPath();
      ctx.moveTo(xs[0], ys[0]);
      for (v = 1; v < 6; v++) { ctx.lineTo(xs[v], ys[v]); }
      ctx.closePath();
      if (gridOnly) {
        ctx.stroke();
      } else {
        ctx.fillStyle = color;
        ctx.fill();
        if (towers) {
          ctx.strokeStyle = 'rgba(0, 0, 0, .32)';
          ctx.lineWidth = 0.65;
          ctx.stroke();
        }
      }
      if (icons) {
        var center = project(cxw, hy + 0.0005, cz);
        var iconSize = Math.min(
          Math.hypot(xs[1] - xs[0], ys[1] - ys[0]),
          Math.hypot(xs[2] - xs[1], ys[2] - ys[1])
        );
        if (center) { drawTerrainIcon(terrainCodeAt(mj * W + Math.min(W - 1, i + (s >> 1))), center[0], center[1], iconSize); }
      }
    }
  }
}

function drawSquareGrid() {
  var W = mesh.W, H = mesh.H, step = state.step;
  var px = mesh.px, py = mesh.py, ok = mesh.ok;
  var row = W + 1;
  ctx.beginPath();
  for (var j = 0; j <= H; j += step) {
    var base = j * row;
    for (var i = 0; i < W; i += step) {
      var i2 = Math.min(i + step, W);
      if (!ok[base + i] || !ok[base + i2]) { continue; }
      ctx.moveTo(px[base + i], py[base + i]);
      ctx.lineTo(px[base + i2], py[base + i2]);
    }
  }
  for (var x = 0; x <= W; x += step) {
    for (var z = 0; z < H; z += step) {
      var z2 = Math.min(z + step, H);
      var a = z * row + x, b = z2 * row + x;
      if (!ok[a] || !ok[b]) { continue; }
      ctx.moveTo(px[a], py[a]);
      ctx.lineTo(px[b], py[b]);
    }
  }
  ctx.lineWidth = 0.55;
  ctx.strokeStyle = 'rgba(0, 0, 0, .30)';
  ctx.stroke();
}

function drawRoundSquareGrid() {
  if (!state.roundWorld) { return; }
  var b = roundGridSceneBounds();
  var stepX = (mesh.vx[1] - mesh.vx[0]) * state.step;
  var stepZ = (mesh.vz[1] - mesh.vz[0]) * state.step;
  var x0 = mesh.vx[0] + Math.floor((b[0] - mesh.vx[0]) / stepX) * stepX;
  var z0 = mesh.vz[0] + Math.floor((b[1] - mesh.vz[0]) / stepZ) * stepZ;
  ctx.beginPath();
  for (var x = x0; x <= b[2] + stepX; x += stepX) {
    var top = project(x, 0, b[1]);
    if (!top) { continue; }
    var topX = top[0], topY = top[1];
    var bottom = project(x, 0, b[3]);
    if (!bottom) { continue; }
    ctx.moveTo(topX, topY);
    ctx.lineTo(bottom[0], bottom[1]);
  }
  for (var z = z0; z <= b[3] + stepZ; z += stepZ) {
    var left = project(b[0], 0, z);
    if (!left) { continue; }
    var leftX = left[0], leftY = left[1];
    var right = project(b[2], 0, z);
    if (!right) { continue; }
    ctx.moveTo(leftX, leftY);
    ctx.lineTo(right[0], right[1]);
  }
  ctx.lineWidth = 0.55;
  ctx.strokeStyle = 'rgba(0, 0, 0, .30)';
  ctx.stroke();
}

// Scratch buffers for the poster mesh, grown on demand rather than reallocated
// every frame.
var underPx = null, underPy = null, underOk = null, underCap = 0;

function underlayGrid(n) {
  var need = (n + 1) * (n + 1);
  if (need > underCap) {
    underPx = new Float64Array(need);
    underPy = new Float64Array(need);
    underOk = new Uint8Array(need);
    underCap = need;
  }
}

function posterOnlyActive() { return MAP_VIEW === 'overlay' && state.posterOnly; }

function drawUnderlay() {
  var img = state.under;
  var posterOnly = posterOnlyActive();
  if ((!state.underOn && !posterOnly) || !img || !img.width || !img.height) { return; }
  if (!posterOnly && state.underAlpha <= 0.001) { return; }
  if (!underCanvas.width || !underCanvas.height) { return; }

  var iw = img.width, ih = img.height;
  var mppX = state.underMpp;
  var mppY = state.underMpp * state.underStretch;
  if (!(mppX > 0) || !(mppY > 0)) { return; }

  // Canvas 2D can only do affine transforms, but the poster lies on a plane
  // seen in perspective, which is a homography. Chopping it into a grid and
  // giving each cell its own affine transform converges on the right answer;
  // the grid just has to be fine enough that the error inside one cell falls
  // below a pixel. It coarsens while the pointer is down, like the terrain.
  var cols = state.step === 2 ? 20 : 44;
  var span = (ih * mppY) / (iw * mppX);
  var rows = Math.round(cols * span);
  if (rows < 3) { rows = 3; }
  if (rows > 120) { rows = 120; }
  var n = Math.max(cols, rows);
  underlayGrid(n);

  var stride = cols + 1;
  var exag = state.underDrape && !posterOnly ? state.exag : 0;
  var k, i, j;

  for (j = 0; j <= rows; j++) {
    var v = ih * j / rows;
    var wy = state.underY + v * mppY;
    for (i = 0; i <= cols; i++) {
      k = j * stride + i;
      var u = iw * i / cols;
      var wx = state.underX + u * mppX;
      var sc = toScene(wx, wy);
      var h = exag ? sampleHeight(wx, wy) * exag : 0;
      var p = project(sc[0], h, sc[1]);
      if (!p) { underOk[k] = 0; continue; }
      // project() hands back a shared array, so copy before the next call.
      underPx[k] = p[0];
      underPy[k] = p[1];
      underOk[k] = 1;
    }
  }

  var dpr = cam.dpr || 1;
  var cw = iw / cols, chh = ih / rows;
  // A sliver of overlap on the far edges hides the hairline cracks that appear
  // between neighbouring affine cells.
  var bleedU = cw * 0.05 + 1, bleedV = chh * 0.05 + 1;

  underCtx.setTransform(1, 0, 0, 1, 0, 0);
  underCtx.clearRect(0, 0, underCanvas.width, underCanvas.height);

  // A deliberately loose cull. One cell can be far larger than the viewport
  // when the camera is right down on the ground, so a tight bound would blank
  // the poster exactly when it is most zoomed in.
  var maxX = underCanvas.width * 12 + 4096;
  var maxY = underCanvas.height * 12 + 4096;

  for (j = 0; j < rows; j++) {
    for (i = 0; i < cols; i++) {
      var a = j * stride + i;
      var b = a + 1;
      var c = a + stride;
      if (!underOk[a] || !underOk[b] || !underOk[c]) { continue; }
      var x0 = underPx[a], y0 = underPy[a];
      var ax = (underPx[b] - x0) / cw, ay = (underPy[b] - y0) / cw;
      var bx = (underPx[c] - x0) / chh, by = (underPy[c] - y0) / chh;
      if (!isFinite(ax) || !isFinite(ay) || !isFinite(bx) || !isFinite(by)) { continue; }
      if (ax * by - ay * bx === 0) { continue; }

      var su = i * cw, sv = j * chh;
      var sw = Math.min(cw + bleedU, iw - su);
      var sh = Math.min(chh + bleedV, ih - sv);
      if (sw <= 0 || sh <= 0) { continue; }

      var dx = x0 * dpr, dy = y0 * dpr;
      if (dx < -maxX || dx > maxX || dy < -maxY || dy > maxY) { continue; }

      underCtx.setTransform(ax * dpr, ay * dpr, bx * dpr, by * dpr, dx, dy);
      try {
        underCtx.drawImage(img, su, sv, sw, sh, 0, 0, sw, sh);
      } catch (err) {
        // A degenerate transform on one cell must not kill the whole frame.
      }
    }
  }
  underCtx.setTransform(1, 0, 0, 1, 0, 0);

  var prev = ctx.globalAlpha;
  var prevComposite = ctx.globalCompositeOperation;
  ctx.globalAlpha = posterOnly ? 1 : state.underAlpha;
  // Multiply retains the terrain's fixed-light shading instead of replacing it
  // with a visually flat poster at higher fade values.
  ctx.globalCompositeOperation = 'multiply';
  ctx.drawImage(underCanvas, 0, 0, cam.cx * 2, cam.cy * 2);
  ctx.globalAlpha = prev;
  ctx.globalCompositeOperation = prevComposite;
}

function routeBezierSegments(points) {
  var segments = [];
  for (var index = 1; index < points.length; index++) {
    var start = points[index - 1], end = points[index];
    var previous = points[Math.max(0, index - 2)];
    var next = points[Math.min(points.length - 1, index + 1)];
    var limit = Math.min(12, Math.hypot(end[0] - start[0], end[1] - start[1]) / 6);
    function control(anchor, before, after, direction) {
      var dx = after[0] - before[0], dy = after[1] - before[1];
      var length = Math.hypot(dx, dy);
      var scale = length ? Math.min(length / 6, limit) / length * direction : 0;
      return [anchor[0] + dx * scale, anchor[1] + dy * scale];
    }
    segments.push([start, control(start, previous, end, 1), control(end, start, next, -1), end]);
  }
  return segments;
}

function projectedRouteCurves(line) {
  var runs = [], points = [];
  for (var index = 0; index < line.xs.length; index++) {
    var lift = line.lifts ? line.lifts[index] : 0;
    var point = project(line.xs[index], line.hs[index] * state.exag + lift + 0.004, line.zs[index]);
    if (!point) {
      if (!state.globe) { return []; }
      if (points.length > 1) { runs.push(routeBezierSegments(points)); }
      points = [];
    } else { points.push([point[0], point[1]]); }
  }
  if (points.length > 1) { runs.push(routeBezierSegments(points)); }
  return runs;
}

function routeBezierPoint(segment, progress) {
  var remaining = 1 - progress;
  return [0, 1].map(function (axis) {
    return remaining * remaining * remaining * segment[0][axis]
      + 3 * remaining * remaining * progress * segment[1][axis]
      + 3 * remaining * progress * progress * segment[2][axis]
      + progress * progress * progress * segment[3][axis];
  });
}

function drawRoutes() {
  if (!routeLines) { return; }
  var exag = state.exag;
  ctx.lineCap = 'round';
  ctx.lineJoin = 'round';
  var selected = state.selectedRoute;
  var selectedGroup = selectedRouteGroup();
  var supplyFocus = selected < 0 && Object.keys(state.supplyRouteKeys).length > 0;
  var selectedLocation = selected < 0 && !supplyFocus ? state.selected : null;
  var locationHasRoutes = selectedLocation && routeLines.some(function (line) {
    return routeMatchesFilter(line) && line.details
      && (line.details.a === selectedLocation || line.details.b === selectedLocation);
  });
  var focusOn = selected >= 0 || supplyFocus || locationHasRoutes;
  for (var pass = 0; pass < (focusOn ? 2 : 1); pass++) {
    for (var r = 0; r < routeLines.length; r++) {
      var line = routeLines[r];
      if (!routeMatchesFilter(line)) { continue; }
      var active = selected >= 0 ? selectedGroup.indexOf(line) >= 0
        : (supplyFocus ? supplyRouteMatches(line) : !!(locationHasRoutes && line.details
          && (line.details.a === selectedLocation || line.details.b === selectedLocation)));
      if (focusOn && ((pass === 0 && active) || (pass === 1 && !active))) { continue; }
      var width = ROUTE_WIDTH[line.kind] || 2.1;
      ctx.setLineDash(routeLineDash(line));
      var curves = projectedRouteCurves(line);
      ctx.beginPath();
      curves.forEach(function (segments) {
        ctx.moveTo(segments[0][0][0], segments[0][0][1]);
        segments.forEach(function (segment) {
          ctx.bezierCurveTo(segment[1][0], segment[1][1], segment[2][0], segment[2][1], segment[3][0], segment[3][1]);
        });
      });
      if (curves.length) {
        var dimmed = focusOn && !active;
        ctx.strokeStyle = dimmed ? 'rgba(238, 238, 238, .72)' : 'rgba(255, 248, 224, .90)';
        ctx.lineWidth = width + 2.4;
        ctx.stroke();
        ctx.strokeStyle = dimmed ? 'rgba(116, 116, 116, .52)' : routeDisplayColor(line);
        ctx.lineWidth = dimmed ? Math.max(1.4, width - 0.5) : width;
        ctx.stroke();
      }
    }
  }
  // Icons need their own final pass or later crossing routes paint over them.
  if (state.routeIcons) {
    for (var iconPass = 0; iconPass < (focusOn ? 2 : 1); iconPass++) {
      for (var iconIndex = 0; iconIndex < routeLines.length; iconIndex++) {
        var iconLine = routeLines[iconIndex];
        if (!routeMatchesFilter(iconLine)) { continue; }
        var iconActive = selected >= 0 ? selectedGroup.indexOf(iconLine) >= 0
          : (supplyFocus ? supplyRouteMatches(iconLine) : !!(locationHasRoutes && iconLine.details
            && (iconLine.details.a === selectedLocation || iconLine.details.b === selectedLocation)));
        if (focusOn && ((iconPass === 0 && iconActive) || (iconPass === 1 && !iconActive))) { continue; }
        var iconPoint = routeIconPoint(iconLine, exag);
        if (iconPoint) { drawRouteIcon(iconPoint[0], iconPoint[1], iconLine, focusOn && !iconActive); }
      }
    }
  }
  // Everything drawn after this -- dots, labels, selection rings -- must be solid.
  ctx.setLineDash([]);
}

function routeIconPoint(line, exag) {
  var index = Math.floor(line.xs.length / 2);
  var lift = line.lifts ? line.lifts[index] : 0;
  var point = project(line.xs[index], line.hs[index] * exag + lift + 0.006, line.zs[index]);
  return point ? [point[0], point[1]] : null;
}

function drawRouteIcon(x, y, line, dimmed) {
  var complex = !!multilegService(line);
  var glyph = complex ? '\u21dd' : routeTypeIcon(line.kind);
  var color = dimmed ? 'rgba(100, 100, 100, .82)' : routeDisplayColor(line);
  ctx.save();
  ctx.setLineDash([]);
  ctx.beginPath();
  ctx.arc(x, y, 8, 0, Math.PI * 2);
  ctx.fillStyle = 'rgba(255, 255, 255, .96)';
  ctx.fill();
  ctx.lineWidth = 2;
  ctx.strokeStyle = color;
  ctx.stroke();
  ctx.font = 'bold 14px "Segoe UI Symbol", sans-serif';
  ctx.textAlign = 'center';
  ctx.textBaseline = 'middle';
  ctx.fillStyle = color;
  if (!complex && line.kind === 'air') { drawGryphonIcon(x, y, color); }
  else { ctx.fillText(glyph, x, y + 0.5); }
  ctx.restore();
}

function drawGryphonIcon(x, y, color) {
  ctx.save();
  ctx.strokeStyle = color;
  ctx.fillStyle = color;
  ctx.lineWidth = 1.4;
  ctx.beginPath();
  ctx.moveTo(x, y + 1);
  ctx.bezierCurveTo(x - 2, y - 4, x - 6, y - 5, x - 6, y - 1);
  ctx.bezierCurveTo(x - 4, y - 2, x - 3, y, x - 2, y + 2);
  ctx.bezierCurveTo(x - 5, y + 1, x - 6, y + 3, x - 7, y + 4);
  ctx.moveTo(x, y + 1);
  ctx.bezierCurveTo(x + 1, y - 4, x + 4, y - 5, x + 5, y - 2);
  ctx.bezierCurveTo(x + 3, y - 2, x + 2, y, x + 2, y + 2);
  ctx.stroke();
  ctx.beginPath();
  ctx.ellipse(x, y + 2, 2.6, 3.2, -0.35, 0, Math.PI * 2);
  ctx.fill();
  ctx.beginPath();
  ctx.arc(x + 2.2, y - 1.3, 1.8, 0, Math.PI * 2);
  ctx.fill();
  ctx.beginPath();
  ctx.moveTo(x + 3.7, y - 1.8);
  ctx.lineTo(x + 6, y - 1.1);
  ctx.lineTo(x + 3.7, y - 0.5);
  ctx.closePath();
  ctx.fill();
  ctx.beginPath();
  ctx.moveTo(x - 1, y + 4);
  ctx.lineTo(x - 2, y + 6);
  ctx.moveTo(x + 1, y + 4);
  ctx.lineTo(x + 2, y + 6);
  ctx.stroke();
  ctx.restore();
}

function drawPortIcon(x, y, radius) {
  var size = Math.max(7, Math.min(11, radius * 1.35));
  var top = y - radius - size - 2;
  ctx.save();
  ctx.lineCap = 'round';
  ctx.lineJoin = 'round';
  ctx.strokeStyle = '#111111';
  ctx.fillStyle = '#ffffff';
  ctx.lineWidth = 1.4;
  ctx.beginPath();
  ctx.moveTo(x, top);
  ctx.lineTo(x, top + size * 0.65);
  ctx.moveTo(x, top + 1);
  ctx.lineTo(x + size * 0.55, top + size * 0.48);
  ctx.lineTo(x, top + size * 0.48);
  ctx.stroke();
  ctx.beginPath();
  ctx.moveTo(x - size * 0.65, top + size * 0.62);
  ctx.lineTo(x + size * 0.65, top + size * 0.62);
  ctx.lineTo(x + size * 0.38, top + size);
  ctx.lineTo(x - size * 0.38, top + size);
  ctx.closePath();
  ctx.fill();
  ctx.stroke();
  ctx.restore();
}

function drawPins() {
  var exag = state.exag;
  var order = [];
  var routeConnected = routeConnectedLocationIds();
  for (var i = 0; i < pins.length; i++) {
    var pin = pins[i];
    pin.vis = false;
    if (pin.data.surveyed && !state.places) { continue; }
    // Seated on the ground itself. Nudged up by a hair only so the dot is not
    // z-fought by the terrain quad it stands on.
    var p = project(pin.sx, pin.h * exag + 0.004, pin.sz);
    if (!p) { continue; }
    pin.px = p[0]; pin.py = p[1]; pin.depth = p[2];
    pin.vis = true;
    order.push(i);
  }
  order.sort(function (a, b) { return pins[b].depth - pins[a].depth; });

  for (var k = 0; k < order.length; k++) {
    var s = pins[order[k]];
    var selected = state.selected === s.data.id;
    var hovered = state.hover === order[k];

    var r = s.radius * (selected ? 1.5 : (hovered ? 1.25 : 1));
    if (state.heatById) {
      drawPriceTower(s, r, selected);
      continue;
    }
    ctx.beginPath();
    if (s.data.mobile) {
      ctx.moveTo(s.px, s.py - r * 1.4);
      ctx.lineTo(s.px + r * 1.4, s.py);
      ctx.lineTo(s.px, s.py + r * 1.4);
      ctx.lineTo(s.px - r * 1.4, s.py);
      ctx.closePath();
    } else {
      ctx.arc(s.px, s.py, r, 0, Math.PI * 2);
    }
    ctx.fillStyle = pinFill(s, state.routeTypes.length > 0 && !routeConnected.has(s.data.id));
    ctx.fill();
    ctx.lineWidth = selected ? 3 : 2;
    ctx.strokeStyle = '#ffffff';
    ctx.stroke();
    if (selected) {
      // A white ring alone would vanish against snow or glacier, so the
      // selected dot gets a second black ring just outside it.
      ctx.lineWidth = 1;
      ctx.strokeStyle = '#000000';
      ctx.beginPath();
      ctx.arc(s.px, s.py, r + 1.8, 0, Math.PI * 2);
      ctx.stroke();
    }

    if (s.data.port) { drawPortIcon(s.px, s.py, r); }

    if (state.calibOn) {
      if (state.calibArmed === s.data.id) {
        // The armed market waits for its second click, so it has to be obvious
        // which one is listening.
        ctx.lineWidth = 2;
        ctx.strokeStyle = '#000000';
        ctx.setLineDash([3, 3]);
        ctx.beginPath();
        ctx.arc(s.px, s.py, r + 6, 0, Math.PI * 2);
        ctx.stroke();
        ctx.setLineDash([]);
      } else if (calibIndexOf(s.data.id) >= 0) {
        // Already pinned by hand: this one is ground truth, not a guess.
        ctx.lineWidth = 1.5;
        ctx.strokeStyle = 'rgba(0, 0, 0, .55)';
        ctx.beginPath();
        ctx.arc(s.px, s.py, r + 4, 0, Math.PI * 2);
        ctx.stroke();
      }
    }
  }
  if (state.labels) { drawLabels(order); }
}

function priceTowerStyle(pin) {
  var value = state.heatById && state.heatById[pin.data.id];
  if (value === undefined || value === null) {
    return {color: '#858585', height: 10};
  }
  var span = state.heatHi - state.heatLo;
  var t = span > 0 ? clamp((value - state.heatLo) / span, 0, 1) : 0.5;
  var low = [42, 157, 75], middle = [224, 165, 27], high = [213, 35, 35];
  var a = t < 0.5 ? low : middle;
  var b = t < 0.5 ? middle : high;
  var mix = t < 0.5 ? t * 2 : (t - 0.5) * 2;
  var rgb = a.map(function (channel, index) {
    return Math.round(channel + (b[index] - channel) * mix);
  });
  return {color: 'rgb(' + rgb.join(',') + ')', height: 14 + 56 * t};
}

function drawPriceTower(pin, radius, selected) {
  var style = priceTowerStyle(pin);
  var width = clamp(radius * 1.35, 5, 13);
  if (state.globe) {
    drawGlobePriceTower(pin, width, style, selected);
    return;
  }
  var left = pin.px - width * 0.5;
  var top = pin.py - style.height;
  pin.towerTipX = pin.px;
  pin.towerTipY = top;
  pin.towerTop = top;

  ctx.fillStyle = style.color;
  ctx.fillRect(left, top, width, style.height);
  ctx.lineWidth = selected ? 3 : 1.5;
  ctx.strokeStyle = '#ffffff';
  ctx.strokeRect(left, top, width, style.height);
  ctx.beginPath();
  ctx.ellipse(pin.px, top, width * 0.5, Math.max(2, width * 0.22), 0, 0, Math.PI * 2);
  ctx.fill();
  ctx.stroke();
  if (selected) {
    ctx.lineWidth = 1;
    ctx.strokeStyle = '#000000';
    ctx.strokeRect(left - 2, top - 2, width + 4, style.height + 4);
  }
}

function drawGlobePriceTower(pin, width, style, selected) {
  // This is the projection of the local sphere normal. It foreshortens toward
  // the centre of the visible hemisphere and leans outward toward the limb.
  var normalX = pin.px - cam.cx;
  var normalY = pin.py - cam.cy;
  var radialDistance = Math.hypot(normalX, normalY);
  var radialScale = radialDistance / Math.max(1, globeRadius());
  var normalLength = radialDistance || 1;
  normalX /= normalLength;
  normalY /= normalLength;
  var projectedHeight = Math.max(2, style.height * radialScale);
  var tipX = pin.px + normalX * projectedHeight;
  var tipY = pin.py + normalY * projectedHeight;
  var sideX = -normalY * width * 0.5;
  var sideY = normalX * width * 0.5;

  pin.towerTipX = tipX;
  pin.towerTipY = tipY;
  pin.towerTop = Math.min(pin.py, tipY);

  ctx.beginPath();
  ctx.moveTo(pin.px - sideX, pin.py - sideY);
  ctx.lineTo(pin.px + sideX, pin.py + sideY);
  ctx.lineTo(tipX + sideX, tipY + sideY);
  ctx.lineTo(tipX - sideX, tipY - sideY);
  ctx.closePath();
  ctx.fillStyle = style.color;
  ctx.fill();
  ctx.lineWidth = selected ? 3 : 1.5;
  ctx.strokeStyle = '#ffffff';
  ctx.stroke();

  ctx.beginPath();
  ctx.ellipse(tipX, tipY, width * 0.5, Math.max(2, width * 0.22),
    Math.atan2(normalY, normalX) + Math.PI * 0.5, 0, Math.PI * 2);
  ctx.fill();
  ctx.stroke();
  if (selected) {
    ctx.lineWidth = 1;
    ctx.strokeStyle = '#000000';
    ctx.beginPath();
    ctx.moveTo(pin.px - sideX * 1.35, pin.py - sideY * 1.35);
    ctx.lineTo(pin.px + sideX * 1.35, pin.py + sideY * 1.35);
    ctx.lineTo(tipX + sideX * 1.35, tipY + sideY * 1.35);
    ctx.lineTo(tipX - sideX * 1.35, tipY - sideY * 1.35);
    ctx.closePath();
    ctx.stroke();
  }
}

function pinFill(pin, disconnected) {
  if (disconnected) { return '#969696'; }
  if (state.heatById) {
    var v = state.heatById[pin.data.id];
    // Pure white means "no reading". The ramp below deliberately stops short
    // of white at both ends so an unpriced pin cannot be mistaken for a cheap
    // one - in greyscale that is the only spare value left to spend.
    if (v === undefined || v === null) { return '#ffffff'; }
    var span = state.heatHi - state.heatLo;
    var t = span > 0 ? clamp((v - state.heatLo) / span, 0, 1) : 0.5;
    // Cheap (light) to dear (near black) - a single monotonic ramp, which
    // survives the loss of hue far better than the old green-amber-red scale.
    var s = Math.round(215 - 185 * t);
    return 'rgb(' + s + ',' + s + ',' + s + ')';
  }
  return '#d52323';
}

function drawLabels(order) {
  ctx.font = LABEL_FONT;
  ctx.textBaseline = 'middle';
  var taken = [];
  // Draw the nearest labels first so they win the space.
  for (var k = order.length - 1; k >= 0; k--) {
    var s = pins[order[k]];
    var d = s.data;
    var important = state.selected === d.id || state.hover === order[k];
    if (!important && d.population < 12000) { continue; }
    var text = d.name;
    // Set the font before measuring, so the collision box matches the weight
    // the label is actually drawn at.
    ctx.font = important ? LABEL_FONT_BOLD : LABEL_FONT;
    var w = ctx.measureText(text).width;
    var lx = (state.heatById ? s.towerTipX : s.px) + s.radius + 5;
    var ly = (state.heatById ? s.towerTipY : s.py) - 4;
    var box = [lx - 2, ly - 8, lx + w + 2, ly + 8];
    var clash = false;
    for (var t = 0; t < taken.length; t++) {
      var o = taken[t];
      if (box[0] < o[2] && box[2] > o[0] && box[1] < o[3] && box[3] > o[1]) {
        clash = true;
        break;
      }
    }
    if (clash && !important) { continue; }
    taken.push(box);
    // Halo then text, inverted from the old dark theme: a white outline keeps
    // black labels legible over dark forest and pale sea alike. The font has
    // to be set before the halo is stroked so the outline matches the glyphs
    // it is meant to be backing.
    ctx.lineWidth = 3;
    ctx.strokeStyle = 'rgba(255, 255, 255, .92)';
    ctx.strokeText(text, lx, ly);
    ctx.fillStyle = '#000000';
    ctx.fillText(text, lx, ly);
  }
}

function draw() {
  if (!mesh) { return; }
  updateCamera();
  drawSky();
  ctx.save();
  if (posterOnlyActive()) {
    drawUnderlay();
    drawPlaces();
    if (state.routes) { drawRoutes(); }
    drawPins();
    ctx.restore();
    return;
  }
  if (state.globe) {
    drawGlobeBase();
    projectVertices();
    drawGlobeTerrain();
    drawUnderlay();
    drawPlaces();
    if (state.routes) { drawRoutes(); }
    drawPins();
    ctx.restore();
    return;
  }
  if (!state.roundWorld) { clipGroundToPoster(); }
  drawRoundWorldBase();
  if (state.tiles === 'hex' || state.tiles === 'hex-towers' || state.tiles === 'hex-icons') {
    // Hex tiles are projected corner by corner, so the shared vertex grid that
    // projectVertices fills is not consulted at all in this mode.
    drawHexTerrain(false, state.tiles === 'hex-towers', false);
  } else if (state.tiles === 'towers') {
    drawTowers();
  } else {
    projectVertices();
    drawTerrain();
  }
  // Over the terrain but under the routes and dots: the poster is reference
  // artwork, and the engine's own data has to stay readable on top of it.
  drawUnderlay();
  // Grid strokes belong above the poster. Drawing them with the terrain fill
  // made an enabled poster hide the selected grid completely.
  if (state.roundWorld) {
    ctx.save();
    clipRoundWorld();
  }
  if (state.tiles === 'hex') {
    drawHexTerrain(true, false, false);
  } else if (state.tiles === 'hex-icons') {
    drawHexTerrain(true, false, true);
  } else if (state.tiles === 'square') {
    drawRoundSquareGrid();
    drawSquareGrid();
  }
  if (state.roundWorld) { ctx.restore(); }
  if (state.roundWorld) {
    drawPlaces();
    if (state.routes) { drawRoutes(); }
    drawPins();
    ctx.restore();
    drawRoundWorldEdge();
  } else {
    ctx.restore();
    drawPlaces();
    if (state.routes) { drawRoutes(); }
    drawPins();
  }
}

var renderBroken = false;

function frame() {
  if (state.dirty && !renderBroken) {
    state.dirty = false;
    // A throw inside draw() would otherwise be swallowed by the animation
    // callback and leave a blank canvas with no explanation. Report it once
    // and stop the loop instead.
    try {
      draw();
    } catch (err) {
      renderBroken = true;
      showStatus('Renderer error: ' + (err && err.message ? err.message : err), true);
      throw err;
    }
  }
  window.requestAnimationFrame(frame);
}

// ---------------------------------------------------------------------------
// interaction
// ---------------------------------------------------------------------------

var drag = null;
var recentMarketClick = null;
var idleTimer = null;

function beginInteract() {
  if (state.step !== 2) { state.step = 2; }
  if (idleTimer) { window.clearTimeout(idleTimer); }
}

function endInteract() {
  if (idleTimer) { window.clearTimeout(idleTimer); }
  idleTimer = window.setTimeout(function () {
    state.step = 1;
    invalidate();
  }, 140);
}

canvas.addEventListener('pointerdown', function (ev) {
  canvas.setPointerCapture(ev.pointerId);
  drag = {
    x: ev.clientX,
    y: ev.clientY,
    pan: ev.shiftKey || ev.button === 2 || ev.button === 1,
    moved: 0
  };
  canvas.classList.add('dragging');
});

canvas.addEventListener('pointermove', function (ev) {
  var rect = canvas.getBoundingClientRect();
  if (!drag) {
    var hit = pick(ev.clientX - rect.left, ev.clientY - rect.top);
    if (hit !== state.hover) {
      state.hover = hit;
      updateTip(hit, ev.clientX - rect.left, ev.clientY - rect.top);
      invalidate();
    } else if (hit >= 0) {
      updateTip(hit, ev.clientX - rect.left, ev.clientY - rect.top);
    }
    return;
  }
  var dx = ev.clientX - drag.x;
  var dy = ev.clientY - drag.y;
  drag.x = ev.clientX;
  drag.y = ev.clientY;
  drag.moved += Math.abs(dx) + Math.abs(dy);
  beginInteract();
  if (state.globe) {
    state.yaw -= dx * 0.006;
    state.globeTilt = clamp(state.globeTilt + dy * 0.005, -1.25, 1.25);
  } else if (drag.pan) {
    // Pan along the camera basis flattened onto the ground plane, so the
    // world tracks the pointer no matter where the orbit currently sits.
    var k = state.dist * 0.0016;
    var rl = Math.sqrt(cam.rx * cam.rx + cam.rz * cam.rz) || 1;
    var grx = cam.rx / rl, grz = cam.rz / rl;
    var fl = Math.sqrt(cam.fx * cam.fx + cam.fz * cam.fz) || 1;
    var gfx = cam.fx / fl, gfz = cam.fz / fl;
    state.tx -= (dx * grx + dy * gfx) * k;
    state.tz -= (dx * grz + dy * gfz) * k;
    state.tx = clamp(state.tx, -3, 3);
    state.tz = clamp(state.tz, -4, 4);
  } else {
    state.yaw -= dx * 0.006;
    state.pitch = clamp(state.pitch + dy * 0.005, 0.12, 1.5);
  }
  invalidate();
});

function endDrag(ev) {
  if (!drag) { return; }
  canvas.classList.remove('dragging');
  var rect = canvas.getBoundingClientRect();
  if (drag.moved < 5 && !drag.pan) {
    var mx = ev.clientX - rect.left;
    var my = ev.clientY - rect.top;
    var hit = pick(mx, my);
    if (state.terrainEditOn) {
      saveTerrainCell(mx, my);
    } else if (state.calibOn) {
      handleCalibClick(hit, mx, my);
    } else {
      if (hit < 0) {
        var routeHit = pickRoute(mx, my);
        if (routeHit < 0) { state.selected = null; }
        selectRoute(routeHit);
        recentMarketClick = null;
        drag = null;
        endInteract();
        return;
      }
      selectRoute(-1);
      var now = performance.now();
      var prior = recentMarketClick;
      var dx = prior ? mx - prior.x : 0;
      var dy = prior ? my - prior.y : 0;
      var nearbyRepeat = prior && now - prior.at < 500 && dx * dx + dy * dy < 144;
      var id = pins[hit].data.id;
      var doubleClick = nearbyRepeat && prior.id === id;
      recentMarketClick = { id: id, x: mx, y: my, at: performance.now() };
      selectSettlement(id);
      if (!pins[hit].data.mobile) {
        if (doubleClick) { loadTerrainDetail(id); }
      }
    }
  }
  drag = null;
  endInteract();
}

canvas.addEventListener('pointerup', endDrag);
canvas.addEventListener('pointercancel', function () {
  drag = null;
  canvas.classList.remove('dragging');
  endInteract();
});
canvas.addEventListener('contextmenu', function (ev) { ev.preventDefault(); });

canvas.addEventListener('wheel', function (ev) {
  ev.preventDefault();
  beginInteract();
  var factor = Math.exp(ev.deltaY * 0.0012);
  if (state.globe) {
    state.globeZoom = clamp(state.globeZoom / factor, 0.55, 2.5);
  } else {
    state.dist = clamp(state.dist * factor, 0.35, 12);
  }
  invalidate();
  endInteract();
}, { passive: false });

canvas.addEventListener('pointerleave', function () {
  state.hover = -1;
  tipEl.hidden = true;
  invalidate();
});

window.addEventListener('keydown', function (ev) {
  var tag = (ev.target && ev.target.tagName) || '';
  if (tag === 'INPUT' || tag === 'SELECT' || tag === 'TEXTAREA') { return; }
  var handled = true;
  if (ev.key === 'ArrowLeft') { state.yaw -= 0.08; }
  else if (ev.key === 'ArrowRight') { state.yaw += 0.08; }
  else if (ev.key === 'ArrowUp') {
    if (state.globe) { state.globeTilt = clamp(state.globeTilt + 0.05, -1.25, 1.25); }
    else { state.pitch = clamp(state.pitch + 0.05, 0.12, 1.5); }
  }
  else if (ev.key === 'ArrowDown') {
    if (state.globe) { state.globeTilt = clamp(state.globeTilt - 0.05, -1.25, 1.25); }
    else { state.pitch = clamp(state.pitch - 0.05, 0.12, 1.5); }
  }
  else if (ev.key === '+' || ev.key === '=') {
    if (state.globe) { state.globeZoom = clamp(state.globeZoom * 1.1, 0.55, 2.5); }
    else { state.dist = clamp(state.dist * 0.9, 0.35, 12); }
  }
  else if (ev.key === '-' || ev.key === '_') {
    if (state.globe) { state.globeZoom = clamp(state.globeZoom / 1.1, 0.55, 2.5); }
    else { state.dist = clamp(state.dist * 1.1, 0.35, 12); }
  }
  else if (ev.key === 'Escape' && state.calibOn) {
    // Cancel the half-finished control point first; a second Esc leaves the
    // mode. Otherwise arming the wrong city would be a trap.
    if (state.calibArmed) { state.calibArmed = ''; updateCalibHud(); } else { setCalibMode(false); }
  }
  else { handled = false; }
  if (handled) { ev.preventDefault(); invalidate(); }
});

function pick(mx, my) {
  if (posterOnlyActive()) { return -1; }
  if (!pins) { return -1; }
  var best = -1;
  var bestDist = 18 * 18;
  for (var i = 0; i < pins.length; i++) {
    var p = pins[i];
    if (!p.vis) { continue; }
    var dx = p.px - mx;
    var dy = p.py - my;
    var d = dx * dx + dy * dy;
    if (state.heatById && p.towerTop !== undefined) {
      var towerReach = p.radius + 7;
      if (state.globe && p.towerTipX !== undefined) {
        var axisDistance = pointSegmentDistanceSquared(mx, my,
          p.px, p.py, p.towerTipX, p.towerTipY);
        if (axisDistance <= towerReach * towerReach && axisDistance < bestDist) {
          bestDist = axisDistance;
          best = i;
        }
        continue;
      }
      if (Math.abs(dx) <= towerReach && my >= p.towerTop - 5 && my <= p.py + 5) {
        var towerDistance = dx * dx;
        if (towerDistance < bestDist) { bestDist = towerDistance; best = i; }
        continue;
      }
    }
    // Slop is a little wider than it was, because the dots are smaller than
    // the old pin heads and there is no stem left to aim at.
    var reach = (p.radius + 9) * (p.radius + 9);
    if (d < reach && d < bestDist) { bestDist = d; best = i; }
  }
  return best;
}

function pointSegmentDistanceSquared(px, py, ax, ay, bx, by) {
  var dx = bx - ax, dy = by - ay;
  var lengthSquared = dx * dx + dy * dy;
  var t = lengthSquared ? ((px - ax) * dx + (py - ay) * dy) / lengthSquared : 0;
  t = clamp(t, 0, 1);
  var x = ax + t * dx, y = ay + t * dy;
  return (px - x) * (px - x) + (py - y) * (py - y);
}

function pickRoute(mx, my) {
  if (!state.routes || !routeLines) { return -1; }
  var best = -1, bestDistance = 10 * 10;
  for (var r = 0; r < routeLines.length; r++) {
    var line = routeLines[r];
    if (!routeMatchesFilter(line)) { continue; }
    projectedRouteCurves(line).forEach(function (segments) {
      segments.forEach(function (segment) {
        var prior = segment[0];
        for (var step = 1; step <= 8; step++) {
          var current = routeBezierPoint(segment, step / 8);
          var distance = pointSegmentDistanceSquared(mx, my, prior[0], prior[1], current[0], current[1]);
          if (distance < bestDistance) { bestDistance = distance; best = r; }
          prior = current;
        }
      });
    });
  }
  return best;
}

function selectedRouteGroup() {
  var selected = routeLines && state.selectedRoute >= 0 ? routeLines[state.selectedRoute] : null;
  if (!selected || !selected.details) { return []; }
  if (!state.selectedCarrierService) { return [selected]; }
  var group = [selected];
  var stops = {};
  stops[selected.details.a] = true;
  stops[selected.details.b] = true;
  var changed = true;
  while (changed) {
    changed = false;
    routeLines.forEach(function (line) {
      if (group.indexOf(line) >= 0 || !line.details || line.details.name !== selected.details.name) { return; }
      var carriesService = (line.details.carriers || []).some(function (carrier) {
        return carrier.service_id === state.selectedCarrierService;
      });
      if (!carriesService) { return; }
      if (stops[line.details.a] || stops[line.details.b]) {
        group.push(line);
        stops[line.details.a] = true;
        stops[line.details.b] = true;
        changed = true;
      }
    });
  }
  return group;
}

function orderedRouteLegs(group) {
  if (!group.length) { return []; }
  var degree = {};
  group.forEach(function (line) {
    degree[line.details.a] = (degree[line.details.a] || 0) + 1;
    degree[line.details.b] = (degree[line.details.b] || 0) + 1;
  });
  var selected = routeLines[state.selectedRoute];
  var current = degree[selected.details.a] === 1 ? selected.details.a
    : (degree[selected.details.b] === 1 ? selected.details.b
      : Object.keys(degree).filter(function (id) { return degree[id] === 1; }).sort()[0]);
  if (!current) { return group.map(function (line) { return { line: line, reverse: false }; }); }
  var remaining = group.slice();
  var ordered = [];
  while (remaining.length) {
    var next = remaining.findIndex(function (line) {
      return line.details.a === current || line.details.b === current;
    });
    if (next < 0) { break; }
    var line = remaining.splice(next, 1)[0];
    var reverse = line.details.b === current;
    ordered.push({ line: line, reverse: reverse });
    current = reverse ? line.details.a : line.details.b;
  }
  return ordered;
}

function updateRouteSelection() {
  var panel = document.getElementById('route-selection');
  var line = routeLines && state.selectedRoute >= 0 ? routeLines[state.selectedRoute] : null;
  if (!line || !line.details) { panel.hidden = true; panel.innerHTML = ''; return; }
  var group = selectedRouteGroup();
  var legs = orderedRouteLegs(group);
  var details = line.details;
  var first = legs[0];
  var last = legs[legs.length - 1];
  var start = first ? (first.reverse ? first.line.details.end : first.line.details.start) : details.start;
  var end = last ? (last.reverse ? last.line.details.start : last.line.details.end) : details.end;
  var distance = group.reduce(function (total, routeLine) { return total + routeLine.details.distance; }, 0);
  var days = group.reduce(function (total, routeLine) { return total + routeLine.details.days; }, 0);
  var service = multilegService(line);
  var modes = Array.from(new Set(group.reduce(function (all, routeLine) {
    return all.concat(routeLine.details.modes || []);
  }, [])));
  var type = (service ? 'Multileg service &middot; ' : '') + modes.map(function (mode) {
    return '<span class="routeicon">' + esc(routeTypeIcon(mode)) + '</span>' + esc(routeTypeLabel(mode));
  }).join(' + ');
  var itinerary = legs.length ? '<ol class="routelegs">' + legs.map(function (leg) {
    var legStart = leg.reverse ? leg.line.details.end : leg.line.details.start;
    var legEnd = leg.reverse ? leg.line.details.start : leg.line.details.end;
    return '<li><b>' + esc(legStart) + ' &rarr; ' + esc(legEnd) + '</b> <small>' +
      Math.round(leg.line.details.distance).toLocaleString() + ' mi &middot; ' +
      routeTime(leg.line.details.days) + '</small><details class="routecarriers"' +
      (leg.line === line ? ' open' : '') + '><summary>' +
      (leg.line.details.carriers || []).length + ' available carriers</summary>' +
      routeCarrierTable(leg.line.details, routeLines.indexOf(leg.line)) + '</details></li>';
  }).join('') + '</ol>' : '';
  panel.hidden = false;
  panel.innerHTML = '<div class="routeheading"><h2>' + esc(details.name) + '</h2>' +
    '<button type="button" class="routeclose" aria-label="Clear route selection" title="Clear route selection" onclick="selectRoute(-1)">&times;</button></div>' +
    '<div class="routeendpoints"><div><span>From</span><b>' + esc(start) + '</b></div>' +
    '<span aria-hidden="true">&rarr;</span><div><span>To</span><b>' + esc(end) + '</b></div></div>' +
    '<div class="routesummary"><div><span>Distance</span><b>' + Math.round(distance).toLocaleString() + ' mi</b></div>' +
    '<div><span>Travel time</span><b>' + routeTime(days) + '</b></div>' +
    '<div><span>Legs</span><b>' + legs.length + '</b></div></div>' +
    '<p class="routemodes"><span>Type</span> &middot; ' + type +
    (line.inferredRoad ? ' &middot; Model-generated connection (not a mapped road or trail)' : '') + '</p>' + itinerary +
    '<a class="route-detail-link" href="route.html?origin=' + encodeURIComponent(start) +
    '&destination=' + encodeURIComponent(end) + '">Compare endpoint routes &rarr;</a>' +
    '<a class="route-detail-link" href="planner.html?origin=' + encodeURIComponent(start) +
    '&destination=' + encodeURIComponent(end) + '">Plan shipment cost &rarr;</a>';
}

function selectRoute(index) {
  state.selectedRoute = index;
  var service = routeLines && index >= 0 ? multilegService(routeLines[index]) : null;
  state.selectedCarrierService = service ? service.service_id : '';
  updateRouteSelection();
  invalidate();
}

function selectRouteCarrier(index, serviceId) {
  state.selectedRoute = index;
  state.selectedCarrierService = state.selectedCarrierService === serviceId ? '' : serviceId;
  updateRouteSelection();
  invalidate();
}

function supplyRouteKey(from, to) {
  return [String(from || '').toLowerCase(), String(to || '').toLowerCase()].sort().join('|');
}

function supplyRouteMatches(line) {
  return !!(line.details && state.supplyRouteKeys[
    supplyRouteKey(line.details.start, line.details.end)
  ]);
}

function supplyChainRows(node, depth) {
  var route = node.route && node.route.reachable ? node.route : null;
  var movement = route
    ? route.path.map(esc).join(' &rarr; ') + ' &middot; ' + Math.round(route.distance).toLocaleString() + ' mi'
    : 'Produced locally in ' + esc(node.market);
  var typeClass = node.production_type === 'raw' ? 'raw' : 'processed';
  var row = '<li style="margin-left:' + (depth * 12) + 'px"><b>' + esc(node.name) + '</b> ' +
    '<span class="' + typeClass + '">' + esc(node.production_type) + '</span>' +
    '<small>' + Number(node.quantity).toLocaleString(undefined, { maximumFractionDigits: 6 }) + ' ' +
    esc(node.unit) + ' &middot; ' + movement + '</small></li>';
  return row + (node.inputs || []).map(function (input) {
    return supplyChainRows(input, depth + 1);
  }).join('');
}

function collectSupplyRoutes(node) {
  if (node.route && node.route.reachable) {
    (node.route.legs || []).forEach(function (leg) {
      state.supplyRouteKeys[supplyRouteKey(leg.from, leg.to)] = true;
    });
  }
  (node.inputs || []).forEach(collectSupplyRoutes);
}

async function showSupplyChain(commodityId) {
  var panel = document.getElementById('supply-chain');
  if (!state.selected || !commodityId) {
    state.supplyChain = null;
    state.supplyRouteKeys = {};
    panel.hidden = true;
    invalidate();
    return;
  }
  panel.hidden = false;
  panel.innerHTML = '<h2>Loading supply chain&#8230;</h2>';
  try {
    var data = await getJson('/api/supply-chain?settlement=' + encodeURIComponent(state.selected) +
      '&commodity=' + encodeURIComponent(commodityId));
    state.supplyChain = data;
    state.supplyRouteKeys = {};
    collectSupplyRoutes(data.chain);
    panel.innerHTML = '<h2>' + esc(data.commodity_name) + ' sourcing into ' + esc(data.settlement) + '</h2>' +
      '<ol>' + supplyChainRows(data.chain, 0) + '</ol>';
    invalidate();
  } catch (err) {
    panel.innerHTML = '<h2>Supply chain unavailable</h2><p class="muted">' + esc(err.message) + '</p>';
  }
}

function updateTip(hit, mx, my) {
  if (hit < 0) { tipEl.hidden = true; return; }
  var d = pins[hit].data;
  var extra = '';
  if (state.heatById) {
    var v = state.heatById[d.id];
    extra = v === undefined || v === null
      ? ' &middot; not traded'
      : ' &middot; ' + gp(v) + ' gp';
  }
  tipEl.hidden = false;
  tipEl.innerHTML = '<b>' + esc(d.name) + '</b> &middot; ' + esc(d.region) + extra;
  tipEl.style.left = mx + 'px';
  tipEl.style.top = my + 'px';
}

// ---------------------------------------------------------------------------
// panel
// ---------------------------------------------------------------------------

function loadTerrainDetail(id) {
  var request = ++state.detailRequest;
  getJson('/api/terrain-detail?settlement=' + encodeURIComponent(id))
    .then(function (detail) {
      if (request !== state.detailRequest || state.selected !== id) { return; }
      buildMesh(detail);
      buildPins(state.map.settlements);
      buildPlaces(state.map.places || []);
      rebuildRouteGeometry();
      state.detailId = id;
      document.getElementById('view-world').hidden = false;
      state.yaw = 0;
      state.pitch = 1.35;
      fitView();
      showStatus('5-mile terrain detail');
      invalidate();
    })
    .catch(function (err) {
      if (request === state.detailRequest) {
        showStatus('Local terrain unavailable: ' + err.message, true);
      }
    });
}

async function selectSettlement(id) {
  state.selected = id;
  state.selectedRoute = -1;
  state.selectedCarrierService = '';
  state.supplyChain = null;
  state.supplyRouteKeys = {};
  document.getElementById('supply-chain').hidden = true;
  updateRouteSelection();
  invalidate();
  var link = document.getElementById('history-link');
  if (link) {
    link.href = 'location.html?settlement=' + encodeURIComponent(id);
  }
  var head = document.getElementById('place-head');
  head.innerHTML = '<h2>Loading&#8230;</h2>';
  var selectedPin = pins.find(function (item) { return item.data.id === id; });
  if (selectedPin && selectedPin.data.mobile) {
    try {
      var mobile = await getJson('/api/mobile-location?id=' + encodeURIComponent(id));
      var position = mobile.position;
      var positionText = position.status === 'encamped'
        ? 'Encamped at ' + position.host.name
        : 'Travelling from ' + position.origin.name + ' to ' + position.destination.name;
      head.innerHTML = '<h2>' + esc(mobile.name) + '</h2><p class="sub">Travelling company &middot; ' +
        Number(mobile.population).toLocaleString() + ' people</p><p class="muted">' +
        esc(positionText) + '</p><p class="muted">' + esc(mobile.description) + '</p>' +
        '<p><a href="mobile.html?id=' + encodeURIComponent(id) + '">Open travelling-company profile</a></p>';
      if (link) { link.href = 'mobile.html?id=' + encodeURIComponent(id); }
    } catch (err) {
      head.innerHTML = '<h2>Mobile profile unavailable</h2><p class="muted">' + esc(err.message) + '</p>';
    }
    return;
  }
  try {
    state.market = await getJson('/api/market?settlement=' + encodeURIComponent(id));
    renderPanel();
  } catch (err) {
    head.innerHTML = '<h2>Market unavailable</h2><p class="muted">' + esc(err.message) + '</p>';
  }
}

function focusSettlement(id) {
  if (state.detailId && state.map) {
    state.detailRequest++;
    buildMesh(state.map);
    buildPins(state.map.settlements);
    buildPlaces(state.map.places || []);
    rebuildRouteGeometry();
    state.detailId = '';
    document.getElementById('view-world').hidden = true;
  }
  var pin = pins && pins.find(function (item) { return item.data.id === id; });
  if (!pin) { return false; }
  if (state.globe) {
    var angles = globeAngles(pin.sx, pin.sz);
    state.yaw = -angles[0];
    state.globeTilt = angles[1];
    state.globeZoom = Math.max(state.globeZoom, 1.15);
  } else {
    state.tx = pin.sx;
    state.tz = pin.sz;
    state.dist = clamp(state.dist, 0.55, 1.15);
  }
  selectSettlement(id);
  invalidate();
  return true;
}

function findLocation(query) {
  var needle = String(query || '').trim().toLowerCase();
  if (!needle || !state.map) { return null; }
  var settlements = state.map.settlements || [];
  return settlements.find(function (item) {
    return item.name.toLowerCase() === needle;
  }) || settlements.find(function (item) {
    return item.name.toLowerCase().indexOf(needle) === 0;
  }) || settlements.find(function (item) {
    return item.name.toLowerCase().indexOf(needle) >= 0;
  }) || null;
}

function renderPanel() {
  var m = state.market;
  if (!m) { return; }
  var head = document.getElementById('place-head');
  head.innerHTML =
    '<h2>' + esc(m.settlement) + '</h2>' +
    '<p class="sub">' + esc(m.region) + ' &middot; ' + esc(m.size) +
    ' &middot; ' + Number(m.population).toLocaleString() + ' souls</p>' +
    '<p class="muted">' + esc(m.description || '') + '</p>';

  var stats = document.getElementById('place-stats');
  stats.innerHTML =
    stat('Ruler', m.ruler || 'None') +
    stat('Wealth', Number(m.wealth).toFixed(2)) +
    stat('Tariff', (Number(m.tariff) * 100).toFixed(0) + '%') +
    stat('Season', m.season) +
    stat('Date', m.date) +
    stat('Goods', String((m.prices || []).length));

  var notes = document.getElementById('place-notes');
  var html = '';
  var traitChips = '';
  (m.traits || []).forEach(function (t) {
    traitChips += '<span class="chip">' + esc(t) + '</span>';
  });
  if (traitChips) { html += '<div class="chips">' + traitChips + '</div>'; }

  var chips = '';
  (m.events || []).forEach(function (e) {
    chips += '<span class="chip event">' + esc(e) + '</span>';
  });
  // cheap_here / dear_here are objects: {commodity, price, unit, x_base}
  (m.cheap_here || []).forEach(function (c) {
    chips += '<span class="chip cheap">' + esc(c.commodity) +
      ' ' + gp(c.price) + ' gp</span>';
  });
  (m.dear_here || []).forEach(function (c) {
    chips += '<span class="chip dear">' + esc(c.commodity) +
      ' ' + gp(c.price) + ' gp</span>';
  });
  if (chips) { html += '<div class="chips">' + chips + '</div>'; }
  notes.innerHTML = html;

  renderPrices();
}

function stat(label, value) {
  return '<div><b>' + esc(value) + '</b><span>' + esc(label) + '</span></div>';
}

function renderPrices() {
  var wrap = document.getElementById('place-prices');
  var m = state.market;
  if (!m) { wrap.innerHTML = ''; return; }
  var needle = state.goodsFilter.toLowerCase();
  var rows = (m.prices || []).filter(function (q) {
    if (state.goodsCategory && q.category !== state.goodsCategory) { return false; }
    if (!needle) { return true; }
    return q.commodity_name.toLowerCase().indexOf(needle) >= 0 ||
      q.category.toLowerCase().indexOf(needle) >= 0;
  });

  var body = '';
  rows.forEach(function (q) {
    var mult = Number(q.multiplier || 1);
    var cls = mult > 1.08 ? 'up' : (mult < 0.94 ? 'down' : '');
    var active = state.heat === q.commodity ? ' class="active"' : '';
    var avail = q.availability === 'none'
      ? '<span class="none">none</span>'
      : esc(q.availability);
    var qualities = (q.quality_offers || []).filter(function (offer) {
      return offer.stock > 0;
    }).map(function (offer) {
      return offer.quality;
    }).join(' &middot; ');
    body +=
      '<tr' + active + ' data-commodity="' + esc(q.commodity) + '">' +
      '<td>' + esc(q.commodity_name) +
      '<div class="cat">' + esc(q.category) + ' &middot; ' + esc(q.production_type) + ' &middot; ' + esc(q.unit) + '</div>' +
      (qualities ? '<div class="cat">' + qualities + '</div>' : '') + '</td>' +
      '<td class="num">' + quotePrice(q.price) + '</td>' +
      '<td class="num">' + quotePrice(q.buy_price) + '</td>' +
      '<td class="num">' + quoteMarkup(q.merchant_markup_pct) + '</td>' +
      '<td class="num">' + (q.uncommitted_stock == null ? '-' : q.uncommitted_stock.toLocaleString()) + '</td>' +
      '<td class="num ' + cls + '">' + mult.toFixed(2) + 'x</td>' +
      '<td>' + avail + '</td>' +
      '</tr>';
  });

  wrap.innerHTML =
    '<table><thead><tr><th>Commodity</th><th class="num">Buy from merchant</th>' +
    '<th class="num">Sell to merchant</th><th class="num">Markup</th><th class="num">Uncommitted stock</th>' +
    '<th class="num">vs base</th><th>Supply</th></tr></thead><tbody>' +
    (body || '<tr><td colspan="7" class="muted">No goods match.</td></tr>') +
    '</tbody></table><p class="muted">Prices are gp per trade unit. With seasonal inventories, uncommitted stock is closing inventory above protected reserves and ingredient commitments. Historical and legacy views use a stock-window estimate. Neither is a booking.</p>';

  Array.prototype.forEach.call(wrap.querySelectorAll('tr[data-commodity]'), function (tr) {
    tr.addEventListener('click', function () {
      var id = tr.getAttribute('data-commodity');
      document.getElementById('heat-commodity').value = id;
      applyHeat(id);
      showSupplyChain(id);
    });
  });
}

// ---------------------------------------------------------------------------
// price heat map
// ---------------------------------------------------------------------------

async function applyHeat(commodityId) {
  state.heat = commodityId || '';
  var legend = document.getElementById('heat-legend');
  if (!state.heat) {
    state.heatById = null;
    legend.hidden = true;
    renderPrices();
    invalidate();
    return;
  }
  legend.hidden = false;
  legend.innerHTML = '<span>Loading prices&#8230;</span>';
  try {
    var data = await getJson('/api/compare?commodity=' +
      encodeURIComponent(state.heat) + '&limit=400');
    var byId = {};
    var lo = Infinity;
    var hi = -Infinity;
    (data.markets || []).forEach(function (q) {
      var id = state.nameToId[q.settlement];
      if (!id || q.price === null || q.price === undefined) { return; }
      byId[id] = q.price;
      if (q.price < lo) { lo = q.price; }
      if (q.price > hi) { hi = q.price; }
    });
    if (!isFinite(lo)) { lo = 0; hi = 0; }
    state.heatById = byId;
    state.heatLo = lo;
    state.heatHi = hi;
    legend.innerHTML =
      '<span>' + gp(lo) + ' gp</span>' +
      '<span class="heatbar"></span>' +
      '<span>' + gp(hi) + ' gp</span>' +
      '<span>&middot; ' + esc(data.commodity) + ' per ' + esc(data.unit) + '</span>' +
      '<span class="heatnone">&middot; gray = no price</span>';
    renderPrices();
    invalidate();
  } catch (err) {
    legend.innerHTML = '<span>' + esc(err.message) + '</span>';
  }
}

// ---------------------------------------------------------------------------
// wiring
// ---------------------------------------------------------------------------

function buildTerrainLegend() {
  var el = document.getElementById('terrain-legend');
  var html = '';
  LEGEND_ORDER.forEach(function (pair) {
    var c = PALETTE[pair[0]];
    html += '<span><i style="background: rgb(' + c[0] + ',' + c[1] + ',' + c[2] +
      ')"></i>' + esc(pair[1]) + '</span>';
  });
  var survey = state.map ? state.map.terrainSurvey : null;
  if (survey && survey.available) {
    if (survey.mode === 'full-grid') {
      html += '<span><b>Terrain grid:</b> ' + Number(survey.sourceCells || 0) +
        ' source cells; ' + Number(survey.appliedSamples || 0) +
        ' rendered samples; classifications, not measured elevations</span>';
    } else {
      html += '<span><b>Survey:</b> ' + Number(survey.appliedSamples || survey.matched || 0) +
        ' of ' + Number(survey.locations || 0) +
        ' usable location cells; relief classes, not measured elevations</span>';
    }
  }
  el.innerHTML = html;
}

// ---------------------------------------------------------------------------
// poster underlay
// ---------------------------------------------------------------------------

// Bumped from v1 when the survey started placing the poster for us. A saved v1
// alignment is always a hand-nudged guess made before that existed, and letting
// it win would hide the real placement behind the very error it was fighting.
var UNDERLAY_KEY = 'faerun.underlay.v2';

function underlayEl(id) { return document.getElementById(id); }

function saveUnderlay() {
  try {
    window.localStorage.setItem(UNDERLAY_KEY, JSON.stringify({
      on: state.underOn,
      alpha: state.underAlpha,
      x: state.underX,
      y: state.underY,
      mpp: state.underMpp,
      stretch: state.underStretch,
      drape: state.underDrape,
      from: state.underFrom
    }));
  } catch (err) {
    // Private-browsing mode and full quotas both throw here. Losing the
    // alignment between sessions is a nuisance, not a failure.
  }
}

function loadSavedUnderlay() {
  try {
    var raw = window.localStorage.getItem(UNDERLAY_KEY);
    if (!raw) { return null; }
    var v = JSON.parse(raw);
    return v && typeof v === 'object' ? v : null;
  } catch (err) {
    return null;
  }
}

// Best first guess at where the poster sits in world miles. The engine's window
// is 3040 miles from the Sea of Moving Ice down to the Shining Sea, and every
// published Faerun poster is cropped to very nearly that same north-south span,
// so fitting the poster's height to it lands within a nudge or two. The east
// offset is measured from Waterdeep, which is the easiest landmark to find on
// both maps.
function defaultUnderlayFit() {
  var img = state.under;
  var ih = (img && img.height) ? img.height : 1064;
  state.underMpp = 3040 / ih;
  state.underStretch = 1.0;
  state.underX = -400;
  state.underY = 150;
  state.underFrom = 'guess';
}

// The real thing: the survey knows which pixel of the poster is Waterdeep and
// how many miles a poster pixel covers, and Waterdeep has a world coordinate,
// so the poster's own corners can be worked out in miles. Everything is derived
// from the *loaded* image's pixel size rather than the width the survey records,
// so a resized copy of the same artwork still lands in the right place.
function surveyUnderlayFit() {
  var img = state.under;
  var s = state.underInfo ? state.underInfo.survey : null;
  if (!img || !img.width || !img.height) { return false; }
  if (!s || !s.available) { return false; }
  if (!(s.widthMiles > 0) || !(s.heightMiles > 0)) { return false; }
  var mppX = s.widthMiles / img.width;
  var mppY = s.heightMiles / img.height;
  if (!(mppX > 0) || !(mppY > 0)) { return false; }
  state.underMpp = mppX;
  state.underStretch = mppY / mppX;
  state.underX = s.x;
  state.underY = s.y;
  state.underFrom = 'survey';
  return true;
}

// Survey first, hand-fit only as a fallback.
function autoUnderlayFit() {
  if (!surveyUnderlayFit()) { defaultUnderlayFit(); }
}

function syncUnderlayControls() {
  var row = underlayEl('underlay-row');
  if (row) { row.hidden = !(state.underInfo && state.underInfo.available); }
  underlayEl('opt-underlay').checked = state.underOn;
  underlayEl('opt-underlay-alpha').value = String(Math.round(state.underAlpha * 100));
  underlayEl('opt-underlay-x').value = String(Math.round(state.underX));
  underlayEl('opt-underlay-y').value = String(Math.round(state.underY));
  underlayEl('opt-underlay-scale').value = String(Math.round(state.underMpp * 100));
  underlayEl('opt-underlay-stretch').value = String(Math.round(state.underStretch * 100));
  underlayEl('opt-underlay-drape').checked = state.underDrape;

  updateUnderlayReadout();
}

// Kept apart from syncUnderlayControls because writing a value back onto a
// range input while it is being dragged can interrupt the drag. Sliding an
// alignment control updates only the readout.
function updateUnderlayReadout() {
  var img = state.under;
  var readout = underlayEl('underlay-readout');
  var readoutRow = underlayEl('underlay-readout-row');
  var showAlign = !underlayEl('underlay-align-row').hidden;
  if (readoutRow) { readoutRow.hidden = !showAlign; }
  if (readout && img) {
    var w = Math.round(img.width * state.underMpp);
    var h = Math.round(img.height * state.underMpp * state.underStretch);
    var s = state.underInfo ? state.underInfo.survey : null;
    var how;
    if (state.underFrom === 'survey') {
      // Worth spelling out: before the survey is applied to the markets the
      // poster is right and the towns are wrong, which looks like a bug in the
      // alignment when it is in fact the thing the overlay is there to show.
      how = ' Placed from the locations survey, anchored on ' +
        ((s && s.anchor) ? s.anchor : 'Waterdeep') +
        '. If the towns do not sit on their poster labels, the markets have not ' +
        'been realigned yet - run: faerun atlas --apply, then reload.';
    } else if (state.underFrom === 'manual') {
      how = ' Nudged by hand. Survey fit puts it back.';
    } else {
      how = ' Rough fit - no locations survey was found to place it properly.';
    }
    readout.textContent =
      (state.underInfo ? state.underInfo.name + ' - ' : '') +
      img.width + ' x ' + img.height + 'px covering ' + w + ' x ' + h +
      ' miles, top-left at (' + Math.round(state.underX) + ', ' +
      Math.round(state.underY) + '). Waterdeep is at (600, 1200), ' +
      'Baldurs Gate (560, 1800), Calimport (660, 2600).' + how;
  }
}

function setMapView(view) {
  if (view !== 'overlay' && view !== 'terrain') { return; }
  MAP_VIEW = view;
  mapViewChanged = true;
  document.body.setAttribute('data-map-view', view);
  document.body.setAttribute('data-poster-only', String(posterOnlyActive()));
  state.underOn = view === 'overlay' && !!state.under;
  if (view === 'terrain') {
    state.calibOn = false;
    state.calibArmed = '';
    document.getElementById('opt-calib').checked = false;
    canvas.classList.remove('calibrating');
  }
  document.querySelectorAll('input[name="map-view"]').forEach(function (input) {
    input.checked = input.value === view;
  });
  var url = new URL(window.location.href);
  url.pathname = url.pathname.replace(/terrain[.]html$/, 'map.html');
  url.searchParams.set('view', view);
  window.history.replaceState(null, '', url);
  syncUnderlayControls();
  resize();
  invalidate();
}

function applyUnderlayImage(img) {
  state.under = img;
  document.getElementById('poster-only').disabled = false;
  var saved = loadSavedUnderlay();
  if (saved && typeof saved.mpp === 'number' && saved.mpp > 0) {
    state.underOn = !!saved.on;
    state.underAlpha = typeof saved.alpha === 'number' ? saved.alpha : 0.55;
    state.underX = Number(saved.x) || 0;
    state.underY = Number(saved.y) || 0;
    state.underMpp = saved.mpp;
    state.underStretch = Number(saved.stretch) || 1;
    state.underDrape = saved.drape !== false;
    state.underFrom = saved.from === 'survey' ? 'survey' : 'manual';
  } else {
    autoUnderlayFit();
  }
  if (MAP_VIEW === 'overlay') {
    state.underOn = true;
    state.underDrape = false;
  } else if (MAP_VIEW === 'terrain') {
    state.underOn = false;
  }
  syncUnderlayControls();
  if (MAP_VIEW === 'overlay' && mesh && !mapViewChanged) { fitView(); }
  invalidate();
}

async function loadUnderlay() {
  var info;
  try {
    info = await getJson('/api/underlay');
  } catch (err) {
    // An older server started before this feature existed has no such route.
    return;
  }
  state.underInfo = info;
  if (!info.available) {
    var none = underlayEl('underlay-none');
    var text = underlayEl('underlay-none-text');
    if (none && text) {
      none.hidden = false;
      text.innerHTML =
        'No poster map found. Drop your own copy into <code>' +
        esc(info.searched[0]) + '</code> - any poster-shaped filename works, ' +
        'or name it <code>underlay.jpg</code> - then reload. You can also set ' +
        '<code>' + esc(info.env_var) + '</code> or pass <code>-Underlay</code> ' +
        'to run.ps1. The artwork is never copied into this project.';
    }
    return;
  }
  var img = new Image();
  img.onload = function () { applyUnderlayImage(img); };
  img.onerror = function () {
    showStatus('The poster map at ' + info.path + ' could not be decoded.', true);
  };
  img.src = info.url;
}

function wireUnderlay() {
  underlayEl('opt-underlay').addEventListener('change', function (ev) {
    state.underOn = ev.target.checked;
    saveUnderlay();
    invalidate();
  });
  underlayEl('opt-underlay-alpha').addEventListener('input', function (ev) {
    state.underAlpha = Number(ev.target.value) / 100;
    saveUnderlay();
    invalidate();
  });
  underlayEl('underlay-align').addEventListener('click', function () {
    var row = underlayEl('underlay-align-row');
    row.hidden = !row.hidden;
    syncUnderlayControls();
    if (!row.hidden && !state.underOn) {
      // Opening the aligner with the poster switched off shows nothing to
      // align against, which reads as a broken control.
      state.underOn = true;
      underlayEl('opt-underlay').checked = true;
      saveUnderlay();
      invalidate();
    }
  });
  underlayEl('underlay-reset').addEventListener('click', function () {
    autoUnderlayFit();
    saveUnderlay();
    syncUnderlayControls();
    invalidate();
  });
  var surveyBtn = underlayEl('underlay-survey');
  if (surveyBtn) {
    surveyBtn.addEventListener('click', function () {
      if (!surveyUnderlayFit()) {
        showStatus('No locations survey to place the poster with.');
        return;
      }
      saveUnderlay();
      syncUnderlayControls();
      invalidate();
    });
  }
  underlayEl('opt-underlay-drape').addEventListener('change', function (ev) {
    state.underDrape = ev.target.checked;
    saveUnderlay();
    invalidate();
  });

  var nudge = [
    ['opt-underlay-x', function (v) { state.underX = v; }],
    ['opt-underlay-y', function (v) { state.underY = v; }],
    ['opt-underlay-scale', function (v) { state.underMpp = v / 100; }],
    ['opt-underlay-stretch', function (v) { state.underStretch = v / 100; }]
  ];
  nudge.forEach(function (pair) {
    underlayEl(pair[0]).addEventListener('input', function (ev) {
      pair[1](Number(ev.target.value));
      state.underFrom = 'manual';
      // Dragging an alignment slider is an interaction like any other, so the
      // poster coarsens while it moves and sharpens when it stops.
      beginInteract();
      endInteract();
      saveUnderlay();
      updateUnderlayReadout();
      invalidate();
    });
  });
}

// ---------------------------------------------------------------------------
// realignment HUD
// ---------------------------------------------------------------------------

function calibEl(id) { return document.getElementById(id); }

function updateCalibHud() {
  var n = state.calibPoints.length;
  var count = calibEl('calib-count');
  if (count) {
    count.textContent = n
      ? (n + (n === 1 ? ' market pinned' : ' markets pinned'))
      : 'No markets pinned yet';
  }
  var tools = calibEl('calib-tools');
  if (tools) { tools.hidden = !state.calibOn; }
  var helpRow = calibEl('calib-help-row');
  var help = calibEl('calib-help');
  if (helpRow) { helpRow.hidden = !state.calibOn; }
  if (help && state.calibOn) {
    if (state.calibArmed) {
      var name = state.calibArmed;
      var at = calibIndexOf(state.calibArmed);
      if (at >= 0) { name = state.calibPoints[at].name; }
      for (var i = 0; pins && i < pins.length; i++) {
        if (pins[i].data.id === state.calibArmed) { name = pins[i].data.name; break; }
      }
      help.textContent = 'Now click where ' + name + ' really belongs on the poster. Esc to cancel.';
    } else if (n < 3) {
      help.textContent = 'Click a market, then click its true spot. Three or more spread-out pins give the best fit.';
    } else {
      help.textContent = 'Click a market, then click its true spot. Save writes the new coordinates into the gazetteer.';
    }
  }
  var save = calibEl('calib-save');
  if (save) { save.disabled = !state.calibDirty; }
  var undo = calibEl('calib-undo');
  if (undo) { undo.disabled = !n; }
}

function setCalibMode(on) {
  var wasOn = state.calibOn;
  state.calibOn = !!on;
  state.calibArmed = '';
  var box = calibEl('opt-calib');
  if (box) { box.checked = state.calibOn; }
  canvas.classList.toggle('calibrating', state.calibOn);
  if (state.calibOn) {
    // Flat-on is the only view where a click lands where it looks like it
    // lands, so realigning drops the tilt rather than fighting the parallax.
    state.yaw = 0;
    state.pitch = 1.45;
    if (state.underInfo && state.underInfo.available && !state.underOn) {
      state.underOn = true;
      var poster = calibEl('opt-underlay');
      if (poster) { poster.checked = true; }
      saveUnderlay();
    }
  } else if (wasOn && state.pitch > 1.30) {
    // Calibration needs a flat view, but leaving it should return to an actual
    // relief view rather than making the whole map appear permanently 2D.
    state.yaw = -0.35;
    state.pitch = 0.50;
    if (mesh) { fitView(); }
  }
  updateCalibHud();
  invalidate();
}

async function saveCalibration(points) {
  showStatus('Re-surveying the Realms...');
  try {
    var payload = points.map(function (p) { return { id: p.id, x: p.x, y: p.y }; });
    await postJson('/api/calibrate', { points: payload });
    // Coordinates drive freight distances, so prices have moved too. Reload the
    // map rather than patching it, so the relief is restamped under the new
    // positions and roads, dots and terrain agree again.
    var data = await getJson('/api/map');
    state.map = data;
    buildMesh(data);
    buildPins(data.settlements);
    buildPlaces(data.places || []);
    buildRoutes(data.routes || [], data.roadGeometries || [], data.seaAirGeometries || []);
    state.calibDirty = false;
    applyCalibration();
    showStatus('');
  } catch (err) {
    showStatus(String(err.message || err), true);
  }
}

function wireCalibration() {
  var box = calibEl('opt-calib');
  if (!box) { return; }
  box.addEventListener('change', function (ev) { setCalibMode(ev.target.checked); });
  calibEl('calib-undo').addEventListener('click', function () {
    if (!state.calibPoints.length) { return; }
    state.calibPoints.pop();
    state.calibDirty = true;
    state.calibArmed = '';
    applyCalibration();
  });
  calibEl('calib-clear').addEventListener('click', function () {
    state.calibPoints = [];
    state.calibArmed = '';
    refreshCalibWarp();
    // Straight to the server: with no control points left there is nothing to
    // preview, and only a reload can put the markets back where they shipped.
    saveCalibration([]);
  });
  calibEl('calib-save').addEventListener('click', function () {
    saveCalibration(state.calibPoints);
  });
  var atlasBtn = calibEl('atlas-apply');
  if (atlasBtn) {
    atlasBtn.addEventListener('click', function () { applyAtlas(); });
  }
}

// A surveyed index of the poster beats dragging dots by hand, so when one is
// present it is offered as a single button and the manual tools stay as the
// way to touch up whatever the survey did not name.
async function loadAtlas() {
  var row = calibEl('atlas-row');
  var note = calibEl('atlas-note');
  if (!row) { return; }
  var info = null;
  try {
    info = await getJson('/api/atlas');
  } catch (err) {
    return;
  }
  if (!info || !info.available) { return; }
  state.atlas = info;
  row.hidden = false;
  if (note) {
    var missed = (info.missing || []).length;
    var inferred = (info.inferred || []).length;
    var surveyed = Number(info.surveyed || (info.count - inferred));
    var text = surveyed + ' surveyed';
    if (inferred) { text += '; ' + inferred + ' placed from engine coordinates'; }
    text += '; ' + info.count + ' of ' + (info.count + missed)
      + ' markets indexed in ' + (info.path || 'the survey');
    if (missed) { text += '; ' + missed + ' not surveyed, left as they are'; }
    var ter = info.terrain;
    if (ter && ter.anchored) {
      text += '. Scenery: ' + ter.anchored + ' of ' + ter.landmarks
        + ' seas, forests and ranges pinned too';
    }
    note.textContent = text;
  }
}

async function applyAtlas() {
  showStatus('Placing the markets from the survey...');
  try {
    await postJson('/api/atlas/apply', {});
    var data = await getJson('/api/map');
    state.map = data;
    buildMesh(data);
    buildPins(data.settlements);
    buildPlaces(data.places || []);
    buildRoutes(data.routes || [], data.roadGeometries || [], data.seaAirGeometries || []);
    state.calibDirty = false;
    await loadCalibration();
    showStatus('');
  } catch (err) {
    showStatus(String(err.message || err), true);
  }
}

async function loadCalibration() {
  var row = calibEl('calib-row');
  try {
    var info = await getJson('/api/calibration');
    state.calibPoints = (info && info.points) || [];
  } catch (err) {
    state.calibPoints = [];
  }
  if (row) { row.hidden = false; }
  state.calibDirty = false;
  applyCalibration();
}

function wireControls() {
  document.getElementById('opt-round-world').checked = state.roundWorld;
  document.getElementById('opt-globe').checked = state.globe;
  wireUnderlay();
  wireCalibration();
  document.getElementById('opt-terrain-edit').addEventListener('change', function (ev) {
    setTerrainEditMode(ev.target.checked);
  });
  document.getElementById('opt-routes').addEventListener('change', function (ev) {
    state.routes = ev.target.checked;
    invalidate();
  });
  document.getElementById('opt-route-icons').addEventListener('change', function (ev) {
    state.routeIcons = ev.target.checked;
    invalidate();
  });
  var routeTypeInputs = Array.from(document.querySelectorAll('input[name="route-type"]'));
  var routeAll = document.getElementById('opt-route-all');
  function updateRouteTypes(ev) {
    if (ev.target === routeAll && routeAll.checked) {
      routeTypeInputs.forEach(function (input) { input.checked = false; });
    } else if (ev.target !== routeAll) {
      routeAll.checked = false;
    }
    state.routeTypes = routeTypeInputs.filter(function (input) { return input.checked; })
      .map(function (input) { return input.value; });
    if (!state.routeTypes.length) { routeAll.checked = true; }
    var summary = document.getElementById('route-type-summary');
    summary.textContent = state.routeTypes.length === 0 ? 'All types'
      : (state.routeTypes.length <= 2
        ? state.routeTypes.map(routeTypeLabel).join(', ')
        : state.routeTypes.length + ' types');
    if (state.selectedRoute >= 0 && !routeMatchesFilter(routeLines[state.selectedRoute])) {
      selectRoute(-1);
    }
    invalidate();
  }
  routeAll.addEventListener('change', updateRouteTypes);
  routeTypeInputs.forEach(function (input) { input.addEventListener('change', updateRouteTypes); });
  document.getElementById('opt-labels').addEventListener('change', function (ev) {
    state.labels = ev.target.checked;
    invalidate();
  });
  document.getElementById('opt-round-world').addEventListener('change', function (ev) {
    state.roundWorld = ev.target.checked;
    if (state.roundWorld) {
      state.globe = false;
      document.getElementById('opt-globe').checked = false;
    }
    fitView();
    invalidate();
  });
  document.getElementById('opt-globe').addEventListener('change', function (ev) {
    state.globe = ev.target.checked;
    if (state.globe) {
      state.roundWorld = false;
      document.getElementById('opt-round-world').checked = false;
      state.yaw = 0;
      state.globeTilt = GLOBE_HOME_TILT;
      state.globeZoom = 1;
    } else {
      state.yaw = 0;
      state.pitch = 0.50;
      fitView();
    }
    invalidate();
  });
  var placesOpt = document.getElementById('opt-places');
  if (placesOpt) {
    placesOpt.addEventListener('change', function (ev) {
      state.places = ev.target.checked;
      invalidate();
    });
  }
  document.getElementById('opt-tiles').addEventListener('change', function (ev) {
    var v = ev.target.value;
    if (v === 'smooth') {
      state.tiles = 'smooth';
    } else if (v === 'square') {
      state.tiles = 'square';
    } else if (v === 'towers') {
      state.tiles = 'towers';
    } else if (v.indexOf('hextower') === 0) {
      state.tiles = 'hex-towers';
      state.hexStep = Number(v.slice(8)) || 2;
    } else if (v.indexOf('hexicon') === 0) {
      state.tiles = 'hex-icons';
      state.hexStep = Number(v.slice(7)) || 2;
    } else {
      state.tiles = 'hex';
      state.hexStep = Number(v.slice(3)) || 2;
    }
    invalidate();
  });
  document.getElementById('opt-exag').addEventListener('input', function (ev) {
    state.exag = BASE_EXAG * (Number(ev.target.value) / 100);
    if (!mesh) { return; }
    shadeMesh();
    invalidate();
  });
  function showWorldView() {
    state.detailRequest++;
    if (state.detailId && state.map) {
      buildMesh(state.map);
      buildPins(state.map.settlements);
      buildPlaces(state.map.places || []);
      rebuildRouteGeometry();
      state.detailId = '';
      document.getElementById('view-world').hidden = true;
      showStatus('');
    }
    state.yaw = 0;
    if (state.globe) {
      state.globeTilt = GLOBE_HOME_TILT;
      state.globeZoom = 1;
      invalidate();
      return;
    }
    state.pitch = 0.50;
    state.tx = 0;
    state.tz = 0;
    if (!mesh) { return; }
    fitView();
    invalidate();
  }
  document.getElementById('view-world').addEventListener('click', showWorldView);
  document.getElementById('view-reset').addEventListener('click', function () {
    showWorldView();
  });
  document.getElementById('view-top').addEventListener('click', function () {
    state.globe = false;
    document.getElementById('opt-globe').checked = false;
    state.yaw = 0;
    state.pitch = 1.45;
    if (!mesh) { return; }
    fitView();
    invalidate();
  });
  document.getElementById('view-tilt').addEventListener('click', function () {
    state.globe = false;
    document.getElementById('opt-globe').checked = false;
    state.yaw = -0.45;
    state.pitch = 0.34;
    if (state.underOn && !state.underDrape) {
      state.underDrape = true;
      var drape = document.getElementById('opt-underlay-drape');
      if (drape) { drape.checked = true; }
      saveUnderlay();
    }
    if (!mesh) { return; }
    fitView();
    invalidate();
  });
  document.getElementById('heat-commodity').addEventListener('change', function (ev) {
    applyHeat(ev.target.value);
  });
  document.getElementById('goods-search').addEventListener('input', function (ev) {
    state.goodsFilter = ev.target.value;
    renderPrices();
  });
  document.getElementById('goods-category').addEventListener('change', function (ev) {
    state.goodsCategory = ev.target.value;
    renderPrices();
  });
  document.getElementById('location-search-form').addEventListener('submit', function (ev) {
    ev.preventDefault();
    var input = document.getElementById('location-search');
    var location = findLocation(input.value);
    if (!location) {
      input.setCustomValidity('Location not found');
      input.reportValidity();
      return;
    }
    input.setCustomValidity('');
    input.value = location.name;
    focusSettlement(location.id);
  });
  document.getElementById('location-search').addEventListener('input', function (ev) {
    ev.target.setCustomValidity('');
  });
  window.addEventListener('resize', function () {
    resize();
  });
}

async function start() {
  buildTerrainLegend();
  wireControls();
  document.getElementById('poster-only').addEventListener('change', function (event) {
    state.posterOnly = event.target.checked;
    document.body.setAttribute('data-poster-only', String(posterOnlyActive()));
    tipEl.hidden = true;
    state.hover = -1;
    resize();
    invalidate();
  });
  document.getElementById('opt-inferred-roads').addEventListener('change', function (event) {
    state.inferredRoads = event.target.checked;
    if (state.selectedRoute >= 0 && !routeMatchesFilter(routeLines[state.selectedRoute])) { selectRoute(-1); }
    invalidate();
  });
  document.querySelectorAll('input[name="map-view"]').forEach(function (input) {
    input.checked = input.value === MAP_VIEW;
    input.addEventListener('change', function () { setMapView(input.value); });
  });
  try {
    showStatus('Surveying the Realms...');
    var results = await Promise.all([getJson('/api/map'), getJson('/api/bootstrap')]);
    state.map = results[0];
    state.boot = results[1];
    buildTerrainLegend();

    showWorldDate(state.boot);

    var commoditySelect = document.getElementById('heat-commodity');
    var categorySelect = document.getElementById('goods-category');
    state.boot.commodities.forEach(function (c) {
      var opt = document.createElement('option');
      opt.value = c.id;
      opt.textContent = c.name + ' (' + c.category + ')';
      commoditySelect.appendChild(opt);
    });
    state.boot.categories.forEach(function (cat) {
      var opt = document.createElement('option');
      opt.value = cat;
      opt.textContent = cat;
      categorySelect.appendChild(opt);
    });

    state.map.settlements.forEach(function (s) { state.nameToId[s.name] = s.id; });
    var locationOptions = document.getElementById('location-options');
    state.map.settlements
      .slice()
      .sort(function (a, b) { return a.name.localeCompare(b.name); })
      .forEach(function (settlement) {
        var option = document.createElement('option');
        option.value = settlement.name;
        locationOptions.appendChild(option);
      });

    buildMesh(state.map);
    buildPins(state.map.settlements);
    buildPlaces(state.map.places || []);
    buildRoutes(
      state.map.routes || [],
      state.map.roadGeometries || [],
      state.map.seaAirGeometries || []
    );

    resize();
    fitView();
    showStatus('');
    invalidate();
    window.requestAnimationFrame(frame);
    // Deliberately not awaited: the poster can be tens of megabytes and the
    // map must not sit blank waiting for it.
    loadUnderlay();
    loadCalibration();
    loadAtlas();
  } catch (err) {
    showStatus('Could not load the map: ' + err.message, true);
  }
}

// Anything that escapes entirely still has to be visible on the page, since the
// canvas would otherwise just sit there black with no clue as to why.
window.addEventListener('error', function (ev) {
  var msg = ev && ev.message ? ev.message : 'unknown error';
  var where = ev && ev.lineno ? ' (line ' + ev.lineno + ')' : '';
  showStatus('Map script error: ' + msg + where, true);
});
window.addEventListener('unhandledrejection', function (ev) {
  var why = ev && ev.reason ? (ev.reason.message || ev.reason) : 'unknown error';
  showStatus('Map request failed: ' + why, true);
});

start();
"""


MAP_ASSETS: Dict[str, Tuple[str, str]] = {
    "map.html": (MAP_HTML, "text/html; charset=utf-8"),
    "terrain.html": (TERRAIN_HTML, "text/html; charset=utf-8"),
    "map.css": (MAP_CSS, "text/css; charset=utf-8"),
    "map.js": (MAP_JS, "application/javascript; charset=utf-8"),
}
