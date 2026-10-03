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

MAP_HTML = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Faerun World Map</title>
<link rel="stylesheet" href="app.css">
<link rel="stylesheet" href="map.css">
</head>
<body class="mapbody" data-map-view="planar">

<header class="topbar">
  <div class="brand">
    <span class="mark">&#9906;</span>
    <div>
      <h1>Faer&ucirc;n World Map</h1>
      <p class="tagline">Surveyed settlements and markets aligned over the high-resolution map.</p>
    </div>
  </div>
  <div class="worldbar">
    <span id="world-date" class="pill" data-world-date>&#8230;</span>
    <nav class="nav-links" aria-label="Main navigation">
    <a class="navlink" href="index.html">Markets</a>
    <a class="navlink" href="location.html">Locations</a>
    <a class="navlink" href="business.html">Businesses</a>
    <a class="navlink" href="product.html">Products</a>
    <a class="navlink" href="route.html">Routes</a>
    <span class="navlink navlink-current" aria-current="page">Map</span>
    <a class="navlink" href="planner.html">Route planner</a>
    <a class="navlink" href="mobile.html">Travelling companies</a>
    <a class="navlink" href="trade.html">Merchant guild &amp; POs</a>
    <a class="navlink" href="board.html">Request board</a>
    <a class="navlink" href="lore.html">Lore</a>
    </nav>
  </div>
</header>

<div class="maplayout">
  <div class="stage">
    <canvas id="world-canvas"></canvas>

    <div class="hud">
      <div class="map-controls" aria-label="Map controls">
        <form id="location-search-form" class="locationsearch" role="search">
          <label class="sr-only" for="location-search">Find a location</label>
          <input id="location-search" type="search" list="location-options" placeholder="Find location..." autocomplete="off">
          <datalist id="location-options"></datalist>
          <button type="submit" title="Find a location" aria-label="Find a location">&#128269;</button>
        </form>
        <fieldset class="mapview-switch" aria-label="Base map">
          <legend class="sr-only">Base map</legend>
          <label><input type="radio" name="map-view" value="overlay"><span>Poster map</span></label>
          <label><input type="radio" name="map-view" value="planar" checked><span>2D map</span></label>
          <label><input type="radio" name="map-view" value="terrain"><span>3D terrain</span></label>
        </fieldset>
        <label>Poster backdrop <select id="underlay-source" aria-label="Poster backdrop">
          <option value="default">Original poster</option>
        </select></label>
        <fieldset class="raster-layers" aria-label="Reference overlays">
          <legend>Reference overlays</legend>
          <label><input id="layer-elevation" type="checkbox" disabled> Elevation / sea depth</label>
          <label>Opacity <input id="layer-elevation-alpha" type="range" min="0" max="100" value="35" aria-label="Elevation opacity" disabled></label>
          <label><input id="layer-ground-cover" type="checkbox" disabled> Vegetation</label>
          <label>Opacity <input id="layer-ground-cover-alpha" type="range" min="0" max="100" value="35" aria-label="Vegetation opacity" disabled></label>
        </fieldset>
        <div class="planar-controls">
          <label>Radius <select id="planar-radius" aria-label="2D radius">
            <option value="500">500 miles</option><option value="200" selected>200 miles</option>
            <option value="100">100 miles</option><option value="50">50 miles</option>
          </select></label>
          <label>Grid <select id="planar-grid" aria-label="2D grid">
            <option value="none" selected>None</option><option value="hex">Hex</option>
            <option value="square">Square</option><option value="both">Hex + square</option>
          </select></label>
          <label>Grid size <select id="planar-cell" aria-label="Grid size in miles">
            <option value="1">1 mile</option>
            <option value="5">5 miles</option><option value="10" selected>10 miles</option>
            <option value="25">25 miles</option><option value="50">50 miles</option>
          </select></label>
          <label>Land detail <select id="planar-land-detail" aria-label="Land detail in miles">
            <option value="1" selected>1 mile</option><option value="5">5 miles</option>
          </select></label>
          <label title="Green: forest; magenta: mountains; blue: shorelines; dashed: reviewed regions"><input id="planar-boundaries" type="checkbox"> Terrain boundaries</label>
          <label><input id="planar-poster" type="checkbox" checked> Poster overlay</label>
          <label>Poster opacity <input id="planar-poster-alpha" type="range" min="0" max="100" value="100" aria-label="Poster opacity"></label>
          <label><input id="planar-terrain" type="checkbox"> Inferred land type</label>
          <label>Land opacity <input id="planar-terrain-alpha" type="range" min="0" max="100" value="50" aria-label="Land type opacity" disabled></label>
          <div class="routefilter"><span>Leg types</span><details id="planar-leg-type">
            <summary id="planar-leg-summary">All types</summary>
            <div class="routefiltermenu" id="planar-leg-options"><label><input id="planar-leg-all" type="checkbox" checked> All types</label></div>
          </details></div>
          <button id="planar-center" type="button" title="Center on selected town" aria-label="Center on selected town">&#8982;</button>
        </div>
        <label title="Animate the planned route and its location markers. Your choice is saved in this browser."><input id="animate-routes" type="checkbox"> Animate routes</label>
        <label title="Label every visible location, including small settlements and junctions. Labels may overlap."><input id="show-all-location-labels" type="checkbox"> Show all location labels</label>
        <label>Junction labels <select id="junction-labels">
          <option value="auto" selected>Automatic</option><option value="show">Show all</option><option value="hide">Hide all</option>
        </select></label>
        <label>Travelling company names <select id="company-labels">
          <option value="auto" selected>Automatic</option><option value="show">Show all</option><option value="hide">Hide all</option>
        </select></label>
        <section class="leg-editor" aria-label="Map route leg editor">
          <label><input id="leg-edit-enabled" type="checkbox"> Edit route legs</label>
          <div id="leg-edit-tools" hidden>
            <div class="leg-toolbar" role="group" aria-label="Route tools">
              <button id="leg-new" type="button" title="New leg" aria-label="New leg">+</button>
              <button id="leg-insert" type="button" title="Insert waypoint on a segment" aria-label="Insert waypoint" aria-pressed="false">&#8853;</button>
              <button id="leg-add-point" type="button" title="Add waypoint after selected point (or at end)" aria-label="Add waypoint" aria-pressed="false">&#10133;</button>
              <button id="leg-remove-point" type="button" title="Delete selected waypoint" aria-label="Delete waypoint">&#8854;</button>
              <button id="leg-undo" type="button" title="Undo geometry change" aria-label="Undo geometry change">&#8630;</button>
              <button id="leg-redo" type="button" title="Redo geometry change" aria-label="Redo geometry change">&#8631;</button>
              <button id="leg-smooth" type="button" title="Insert daily travel boundaries along the leg, preserving existing waypoints">Daily travel units</button>
              <button id="leg-curve" type="button" title="Smooth bends through existing waypoints; two-point legs remain straight">Smooth curves</button>
              <button id="leg-coast" type="button" title="Replace sea leg geometry between its endpoints with a route targeting 15 miles offshore">Hug coast (15 mi)</button>
              <button id="leg-straighten" type="button" title="Connect existing waypoints with straight segments">Straighten</button>
              <button id="leg-split" type="button" title="Save as two legs sharing the selected interior waypoint">Split at point</button>
            </div>
            <label>Curvature <input id="leg-curvature" type="range" min="0" max="100" value="75" step="5" aria-label="Route curvature" title="Curve strength applied by Smooth curves or Hug coast"></label>
            <label><input id="leg-snap" type="checkbox" checked> Snap to waypoints and locations</label>
            <label>Name <input id="leg-name" type="text" maxlength="160" autocomplete="off"></label>
            <label>Type <select id="leg-kind">
              <option value="road">Road</option><option value="trail">Foot trail</option>
              <option value="track">Track</option><option value="sea">Sea</option>
              <option value="river">River</option><option value="barge">Barge</option>
              <option value="ferry">Ferry</option><option value="portage">Portage</option>
              <option value="tunnel">Tunnel</option><option value="teleport">Teleportation circle</option>
              <option value="air">Gryphon flight</option><option value="skyship">Skyship</option>
            </select></label>
            <output id="leg-point-count"></output>
            <output id="leg-day-rate"></output>
            <button id="leg-junction" type="button" title="Convert the selected waypoint into an automatically named junction">Convert to junction</button>
            <label>Origin <output id="leg-origin"></output></label>
            <label>Destination <output id="leg-destination"></output></label>
            <div class="leg-toolbar">
              <button id="leg-save" type="button">Save leg</button>
              <button id="leg-cancel" type="button">Cancel</button>
              <button id="leg-delete" type="button">Delete leg</button>
            </div>
          </div>
          <output id="leg-edit-status" role="status" aria-live="polite"></output>
        </section>
        <label class="poster-only-control"><input id="poster-only" type="checkbox" disabled title="Available when the poster image has loaded"> Poster only</label>
        <label><input id="opt-route-icons" type="checkbox" checked> Leg icons</label>
      </div>
      <details class="mapsettings" open ontoggle="this.open=true">
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
              <label><input type="checkbox" name="route-type" value="skyship"> &#128752; Skyship</label>
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
    <section id="route-plan" class="routeplan" aria-live="polite">
      <h2>Plan a route</h2>
      <form id="route-plan-form">
        <label class="sr-only" for="route-plan-origin">Origin</label>
        <input id="route-plan-origin" type="search" list="location-options" placeholder="Origin" autocomplete="off">
        <label class="sr-only" for="route-plan-destination">Destination</label>
        <input id="route-plan-destination" type="search" list="location-options" placeholder="Destination" autocomplete="off">
        <label><input type="checkbox" id="route-plan-cost"> Optimize for cost</label>
        <button type="submit">Show route</button>
      </form>
      <div id="route-plan-result"></div>
    </section>
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

TERRAIN_HTML = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Faerun World Map</title>
<link rel="stylesheet" href="app.css">
<link rel="stylesheet" href="map.css">
</head>
<body class="mapbody" data-map-view="terrain">

<header class="topbar">
  <div class="brand">
    <span class="mark">&#9906;</span>
    <div>
      <h1>Faer&ucirc;n World Map</h1>
      <p class="tagline">Surveyed settlements and markets aligned over the high-resolution map.</p>
    </div>
  </div>
  <div class="worldbar">
    <span id="world-date" class="pill" data-world-date>&#8230;</span>
    <nav class="nav-links" aria-label="Main navigation">
    <a class="navlink" href="index.html">Markets</a>
    <a class="navlink" href="location.html">Locations</a>
    <a class="navlink" href="business.html">Businesses</a>
    <a class="navlink" href="product.html">Products</a>
    <a class="navlink" href="route.html">Routes</a>
    <span class="navlink navlink-current" aria-current="page">Map</span>
    <a class="navlink" href="planner.html">Route planner</a>
    <a class="navlink" href="mobile.html">Travelling companies</a>
    <a class="navlink" href="trade.html">Merchant guild &amp; POs</a>
    <a class="navlink" href="board.html">Request board</a>
    <a class="navlink" href="lore.html">Lore</a>
    </nav>
  </div>
</header>

<div class="maplayout">
  <div class="stage">
    <canvas id="world-canvas"></canvas>

    <div class="hud">
      <div class="map-controls" aria-label="Map controls">
        <form id="location-search-form" class="locationsearch" role="search">
          <label class="sr-only" for="location-search">Find a location</label>
          <input id="location-search" type="search" list="location-options" placeholder="Find location..." autocomplete="off">
          <datalist id="location-options"></datalist>
          <button type="submit" title="Find a location" aria-label="Find a location">&#128269;</button>
        </form>
        <fieldset class="mapview-switch" aria-label="Base map">
          <legend class="sr-only">Base map</legend>
          <label><input type="radio" name="map-view" value="overlay"><span>Poster map</span></label>
          <label><input type="radio" name="map-view" value="planar"><span>2D map</span></label>
          <label><input type="radio" name="map-view" value="terrain" checked><span>3D terrain</span></label>
        </fieldset>
        <label>Poster backdrop <select id="underlay-source" aria-label="Poster backdrop">
          <option value="default">Original poster</option>
        </select></label>
        <fieldset class="raster-layers" aria-label="Reference overlays">
          <legend>Reference overlays</legend>
          <label><input id="layer-elevation" type="checkbox" disabled> Elevation / sea depth</label>
          <label>Opacity <input id="layer-elevation-alpha" type="range" min="0" max="100" value="35" aria-label="Elevation opacity" disabled></label>
          <label><input id="layer-ground-cover" type="checkbox" disabled> Vegetation</label>
          <label>Opacity <input id="layer-ground-cover-alpha" type="range" min="0" max="100" value="35" aria-label="Vegetation opacity" disabled></label>
        </fieldset>
        <div class="planar-controls">
          <label>Radius <select id="planar-radius" aria-label="2D radius">
            <option value="500">500 miles</option><option value="200" selected>200 miles</option>
            <option value="100">100 miles</option><option value="50">50 miles</option>
          </select></label>
          <label>Grid <select id="planar-grid" aria-label="2D grid">
            <option value="none" selected>None</option><option value="hex">Hex</option>
            <option value="square">Square</option><option value="both">Hex + square</option>
          </select></label>
          <label>Grid size <select id="planar-cell" aria-label="Grid size in miles">
            <option value="1">1 mile</option>
            <option value="5">5 miles</option><option value="10" selected>10 miles</option>
            <option value="25">25 miles</option><option value="50">50 miles</option>
          </select></label>
          <label>Land detail <select id="planar-land-detail" aria-label="Land detail in miles">
            <option value="1" selected>1 mile</option><option value="5">5 miles</option>
          </select></label>
          <label title="Green: forest; magenta: mountains; blue: shorelines; dashed: reviewed regions"><input id="planar-boundaries" type="checkbox"> Terrain boundaries</label>
          <label><input id="planar-poster" type="checkbox" checked> Poster overlay</label>
          <label>Poster opacity <input id="planar-poster-alpha" type="range" min="0" max="100" value="100" aria-label="Poster opacity"></label>
          <label><input id="planar-terrain" type="checkbox"> Inferred land type</label>
          <label>Land opacity <input id="planar-terrain-alpha" type="range" min="0" max="100" value="50" aria-label="Land type opacity" disabled></label>
          <div class="routefilter"><span>Leg types</span><details id="planar-leg-type">
            <summary id="planar-leg-summary">All types</summary>
            <div class="routefiltermenu" id="planar-leg-options"><label><input id="planar-leg-all" type="checkbox" checked> All types</label></div>
          </details></div>
          <button id="planar-center" type="button" title="Center on selected town" aria-label="Center on selected town">&#8982;</button>
        </div>
        <label title="Animate the planned route and its location markers. Your choice is saved in this browser."><input id="animate-routes" type="checkbox"> Animate routes</label>
        <label title="Label every visible location, including small settlements and junctions. Labels may overlap."><input id="show-all-location-labels" type="checkbox"> Show all location labels</label>
        <label>Junction labels <select id="junction-labels">
          <option value="auto" selected>Automatic</option><option value="show">Show all</option><option value="hide">Hide all</option>
        </select></label>
        <label>Travelling company names <select id="company-labels">
          <option value="auto" selected>Automatic</option><option value="show">Show all</option><option value="hide">Hide all</option>
        </select></label>
        <section class="leg-editor" aria-label="Map route leg editor">
          <label><input id="leg-edit-enabled" type="checkbox"> Edit route legs</label>
          <div id="leg-edit-tools" hidden>
            <div class="leg-toolbar" role="group" aria-label="Route tools">
              <button id="leg-new" type="button" title="New leg" aria-label="New leg">+</button>
              <button id="leg-insert" type="button" title="Insert waypoint on a segment" aria-label="Insert waypoint" aria-pressed="false">&#8853;</button>
              <button id="leg-add-point" type="button" title="Add waypoint after selected point (or at end)" aria-label="Add waypoint" aria-pressed="false">&#10133;</button>
              <button id="leg-remove-point" type="button" title="Delete selected waypoint" aria-label="Delete waypoint">&#8854;</button>
              <button id="leg-undo" type="button" title="Undo geometry change" aria-label="Undo geometry change">&#8630;</button>
              <button id="leg-redo" type="button" title="Redo geometry change" aria-label="Redo geometry change">&#8631;</button>
              <button id="leg-smooth" type="button" title="Insert daily travel boundaries along the leg, preserving existing waypoints">Daily travel units</button>
              <button id="leg-curve" type="button" title="Smooth bends through existing waypoints; two-point legs remain straight">Smooth curves</button>
              <button id="leg-coast" type="button" title="Replace sea leg geometry between its endpoints with a route targeting 15 miles offshore">Hug coast (15 mi)</button>
              <button id="leg-straighten" type="button" title="Connect existing waypoints with straight segments">Straighten</button>
              <button id="leg-split" type="button" title="Save as two legs sharing the selected interior waypoint">Split at point</button>
            </div>
            <label>Curvature <input id="leg-curvature" type="range" min="0" max="100" value="75" step="5" aria-label="Route curvature" title="Curve strength applied by Smooth curves or Hug coast"></label>
            <label><input id="leg-snap" type="checkbox" checked> Snap to waypoints and locations</label>
            <label>Name <input id="leg-name" type="text" maxlength="160" autocomplete="off"></label>
            <label>Type <select id="leg-kind">
              <option value="road">Road</option><option value="trail">Foot trail</option>
              <option value="track">Track</option><option value="sea">Sea</option>
              <option value="river">River</option><option value="barge">Barge</option>
              <option value="ferry">Ferry</option><option value="portage">Portage</option>
              <option value="tunnel">Tunnel</option><option value="teleport">Teleportation circle</option>
              <option value="air">Gryphon flight</option><option value="skyship">Skyship</option>
            </select></label>
            <output id="leg-point-count"></output>
            <output id="leg-day-rate"></output>
            <button id="leg-junction" type="button" title="Convert the selected waypoint into an automatically named junction">Convert to junction</button>
            <label>Origin <output id="leg-origin"></output></label>
            <label>Destination <output id="leg-destination"></output></label>
            <div class="leg-toolbar">
              <button id="leg-save" type="button">Save leg</button>
              <button id="leg-cancel" type="button">Cancel</button>
              <button id="leg-delete" type="button">Delete leg</button>
            </div>
          </div>
          <output id="leg-edit-status" role="status" aria-live="polite"></output>
        </section>
        <label class="poster-only-control"><input id="poster-only" type="checkbox" disabled title="Available when the poster image has loaded"> Poster only</label>
        <label><input id="opt-route-icons" type="checkbox" checked> Leg icons</label>
      </div>
      <details class="mapsettings" open ontoggle="this.open=true">
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
              <label><input type="checkbox" name="route-type" value="skyship"> &#128752; Skyship</label>
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
    <section id="route-plan" class="routeplan" aria-live="polite">
      <h2>Plan a route</h2>
      <form id="route-plan-form">
        <label class="sr-only" for="route-plan-origin">Origin</label>
        <input id="route-plan-origin" type="search" list="location-options" placeholder="Origin" autocomplete="off">
        <label class="sr-only" for="route-plan-destination">Destination</label>
        <input id="route-plan-destination" type="search" list="location-options" placeholder="Destination" autocomplete="off">
        <label><input type="checkbox" id="route-plan-cost"> Optimize for cost</label>
        <button type="submit">Show route</button>
      </form>
      <div id="route-plan-result"></div>
    </section>
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


MAP_CSS = r"""
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
.routeplan { padding: 10px 14px; border-block: 1px solid var(--line); background: var(--panel); }
.routeplan h2 { margin: 0 0 7px; font-size: 15px; color: var(--ink); }
.routeplan form { display: flex; flex-wrap: wrap; gap: 6px; align-items: center; }
.routeplan input[type="search"] { flex: 1 1 120px; min-width: 0; padding: 4px 6px; border: 1px solid var(--line); border-radius: 3px; background: var(--panel); color: var(--ink); font: inherit; }
.routeplan label { font-size: 11px; color: var(--muted); display: flex; align-items: center; gap: 4px; }
.routeplan button { padding: 4px 10px; border: 1px solid var(--line); border-radius: 3px; background: var(--panel); color: var(--ink); font: inherit; cursor: pointer; }
.routeplan #route-plan-result { margin-top: 8px; font-size: 12px; color: var(--ink); }
.routeplan #route-plan-result .muted { color: var(--muted); }
.planned-route-legs { margin: 12px 0; padding: 0; list-style: none; }
.planned-route-legs li { padding: 9px 10px; border: 1px solid var(--cp-border); border-radius: 10px; background: var(--cp-surface-soft); }
.planned-route-legs li + li { margin-top: 7px; }
.planned-route-legs b, .planned-route-legs small { display: block; }
.planned-route-legs small { margin-top: 3px; color: var(--cp-text-muted); line-height: 1.5; }

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
.raster-layers { display: grid; grid-template-columns: minmax(0, 1fr) minmax(0, 1fr); gap: 8px; min-width: 0; margin: 0; padding: 10px; border: 1px solid var(--cp-border); border-radius: 10px; }
.raster-layers legend { color: var(--cp-text-muted); font-size: 12px; }
.raster-layers label { display: flex; align-items: center; gap: 6px; min-width: 0; }
.raster-layers input[type="range"] { width: 100%; min-width: 0; }
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
.mappanel { flex: 0 0 clamp(320px,27%,520px); max-width: none; min-width: 0; min-height: calc(100% - 32px); align-self: stretch; margin: 16px; padding: 24px 20px; gap: 20px; background: var(--cp-surface); border: 1px solid var(--cp-border); border-radius: 18px; box-shadow: 0 8px 24px rgba(25,35,45,.08); box-sizing: border-box; }
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
.flight-day-list { margin: 8px 0 0 18px; padding: 0; color: var(--cp-text-muted); }
.flight-day-list li { padding: 3px 0; }
.flight-rest { color: var(--cp-accent); font-style: italic; }
.routefacts { grid-template-columns: 1fr auto 1fr; }
.routefacts > * { min-width: 0; overflow-wrap: anywhere; }
.supplychain { padding: 14px 0; background: transparent; }
.supplychain .raw { color: var(--cp-text-muted); }
.supplychain .processed { color: var(--cp-accent); }
.routeplan { padding: 14px 0; background: transparent; border-block: 0; border-bottom: 1px solid var(--cp-border); }
.routeplan input[type="search"], .routeplan button { border-color: var(--cp-border); background: var(--cp-surface); color: var(--cp-text); }
.routeplan label { color: var(--cp-text-muted); }
.routeplan #route-plan-result .muted { color: var(--cp-text-muted); }
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
.mapbody .topbar { min-height: 168px; padding: 20px clamp(16px,3%,64px); background: var(--cp-surface); border: 0; box-shadow: none; }
.mapbody .worldbar { display: grid; grid-template-columns: 1fr; justify-items: end; gap: 12px; flex: 1 1 680px; }
.mapbody .map-controls,
.mapbody .worldbar > [data-world-date],
.mapbody .nav-links { grid-column: 1; }
.map-controls { display: flex; flex-wrap: wrap; align-items: center; justify-content: flex-end; gap: 10px; }
.mapbody .nav-links { display: flex; flex-wrap: wrap; justify-content: flex-end; gap: 10px; }
.mapbody .navlink { display: inline-flex; align-items: center; border: 1px solid var(--cp-border); border-radius: 10px; background: var(--cp-surface-soft); color: var(--cp-text); padding: 8px 12px; box-shadow: 0 3px 8px rgba(25,35,45,.06); }
.mapbody .navlink:hover { border-color: var(--cp-accent); background: var(--cp-accent-soft); color: var(--cp-accent); }
.mapbody .hud {
  position: absolute;
  inset: 0 auto 0 0;
  width: 320px;
  max-width: 320px;
  height: auto;
  overflow-y: auto;
  padding: 20px 16px;
  background: var(--cp-surface);
  border: 0;
  border-right: 1px solid var(--cp-border);
  border-radius: 0;
  box-shadow: none;
  backdrop-filter: none;
  z-index: 4;
}
.mapbody .mapsettings {
  max-height: none;
  overflow: visible;
  padding: 16px;
  border: 1px solid var(--cp-border);
  border-radius: 14px;
  background: var(--cp-surface-soft);
  box-shadow: 0 4px 12px rgba(25,35,45,.06);
}
.mapbody .mapsettings > summary { padding: 0 0 14px; cursor: default; }
.mapbody .hud .map-controls {
  display: grid;
  gap: 12px;
  align-items: stretch;
  justify-content: stretch;
  padding: 0 0 16px;
  margin-bottom: 16px;
  border-bottom: 1px solid var(--cp-border);
}
.mapbody .hud .locationsearch { max-width: none; }
.mapbody .hud .mapview-switch { display: grid; gap: 8px; margin: 0; padding: 0; border: 0; }
.mapbody .hud .mapview-switch label,
.mapbody .hud .map-controls > label { min-height: 32px; }
.mapbody .brand h1 { font-size: 50px; line-height: 1.05; overflow-wrap: anywhere; }
.mapbody [data-world-date] { font-size: 20px; padding: 10px 16px; }
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
.mapbody .navlink {
  border: 1px solid var(--cp-border);
  border-radius: 10px;
  background: var(--cp-surface-soft);
  color: var(--cp-text);
  padding: 8px 12px;
  box-shadow: 0 3px 8px rgba(25,35,45,.06);
}
.mapbody .navlink:hover { background: var(--cp-accent-soft); border-color: var(--cp-accent); color: var(--cp-accent); }
.map-controls .mapview-switch,
.map-controls > label:not(.poster-only-control) { border-radius: 10px; }
@media (max-width: 1000px) {
  body.mapbody { height: auto; min-height: 100dvh; overflow: auto; }
  .maplayout { flex: none; overflow: visible; }
  .stage { flex: none; height: 65dvh; min-height: 420px; }
  .mappanel { max-width: none; flex: none; min-height: 0; margin: 0; overflow: visible; padding: 20px 16px; border-radius: 0; border-inline: 0; border-bottom: 0; box-shadow: none; }
  .mapbody .hud { position: relative; inset: auto; width: 100%; max-width: none; height: auto; border-right: 0; border-bottom: 1px solid var(--cp-border); }
  .mapsettings { max-height: 35dvh; }
  .terrainlegend { bottom: 16px; }
  .mapbody .topbar { padding: 16px; }
  .mapbody .worldbar, .map-controls, .mapbody .nav-links { justify-content: flex-start; justify-items: start; flex-basis: 100%; width: 100%; }
  .mapbody .locationsearch { max-width: none; }
}

.planar-controls { display: none; }
.leg-editor { display: none; }
body[data-map-view="planar"] .leg-editor { display: grid; gap: 8px; border-top: 1px solid var(--cp-border); padding-top: 12px; }
#leg-edit-tools:not([hidden]) { display: grid; gap: 10px; }
#leg-edit-tools label { display: grid; gap: 4px; }
#leg-edit-tools input, #leg-edit-tools select { width: 100%; min-width: 0; box-sizing: border-box; }
#leg-edit-tools input[type="checkbox"] { width: auto; justify-self: start; }
.leg-toolbar { display: flex; flex-wrap: wrap; gap: 6px; }
.leg-toolbar button { min-width: 36px; min-height: 36px; border-radius: 4px; }
.leg-toolbar button[aria-pressed="true"] { background: var(--cp-accent); color: var(--cp-accent-fg); }
#leg-edit-status, #leg-point-count { font-size: 12px; overflow-wrap: anywhere; }
body[data-map-view="planar"] .planar-controls { display: grid; gap: 10px; }
.planar-controls label { display: flex; justify-content: space-between; align-items: center; gap: 8px; }
.planar-controls select { min-width: 0; max-width: 150px; }
#planar-center { width: 36px; height: 36px; font-size: 22px; }
body[data-map-view="planar"] .viewcontrols,
body[data-map-view="planar"] .poster-only-control,
body[data-map-view="planar"] .mapsettings,
body[data-map-view="planar"] .terrainlegend { display: none; }
body[data-map-view="planar"][data-land-overlay="true"] .terrainlegend { display: flex; bottom: 82px; max-height: 25vh; overflow-y: auto; }
body[data-map-view="planar"] .stage { display: flex; padding-left: 320px; }
body[data-map-view="planar"] #world-canvas { min-width: 0; flex: 1; width: 100%; touch-action: none; }
@media (max-width: 1000px) {
  body[data-map-view="planar"] .stage { display: flex; flex-direction: column; height: auto; padding-left: 0; }
  body[data-map-view="planar"] .hud { order: -1; }
  body[data-map-view="planar"] #world-canvas { flex: none; height: 65dvh; min-height: 360px; }
  body[data-map-view="planar"] .mapview-switch { grid-template-columns: repeat(3, minmax(0, 1fr)); }
  body[data-map-view="planar"] .mapview-switch span { padding: 8px 4px; text-align: center; }
  body[data-map-view="planar"] .planar-controls { grid-template-columns: repeat(2, minmax(0, 1fr)); }
  body[data-map-view="planar"] .planar-controls label { flex-wrap: wrap; }
}
"""


MAP_JS = r"""
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
var MAP_VIEW = document.body.getAttribute('data-map-view') || 'planar';
var requestedView = new URLSearchParams(window.location.search).get('view');
if (requestedView === 'overlay' || requestedView === 'terrain' || requestedView === 'planar') { MAP_VIEW = requestedView; }
document.body.setAttribute('data-map-view', MAP_VIEW);
var mapViewChanged = false;
var initialRouteTypes = new URLSearchParams(window.location.search).get('routeTypes');
initialRouteTypes = initialRouteTypes === null
  ? ['road', 'trail', 'sea', 'river', 'barge', 'ferry', 'portage', 'tunnel']
  : initialRouteTypes.split(',').filter(Boolean);

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
  verifiedOnly: true,
  routeIcons: true,
  animateRoutes: null,
  routeTypes: initialRouteTypes.slice(),
  inferredRoads: false,
  labels: true,
  showAllLocationLabels: false,
  junctionLabels: 'auto',
  companyLabels: 'auto',
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
  planRoute: null,
  planRouteKeys: {},
  planRequest: 0,
  goodsFilter: '',
  goodsCategory: '',
  step: 1,
  tiles: 'smooth',
  planarRadius: 200,
  planarLegTypes: initialRouteTypes.includes('trail') ? initialRouteTypes.concat('track') : initialRouteTypes.slice(),
  planarGrid: 'none',
  planarCell: 10,
  planarLandDetail: 1,
  planarBoundaries: false,
  planarPoster: true,
  planarPosterAlpha: 1,
  planarTerrain: false,
  planarTerrainAlpha: 0.5,
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
  rasterLayers: {
    elevation: {on: false, alpha: 0.35, image: null, loading: false},
    'ground-cover': {on: false, alpha: 0.35, image: null, loading: false}
  },
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
var baseRouteLines = [];
var mapLegEdits = {revision: 0, legs: {}};
var legEditor = {enabled: false, ready: false, draft: null, point: -1, insert: false,
  creating: false, dirty: false, saving: false, undo: [], redo: [], drag: null};

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

function mapLabelScale() {
  return MAP_VIEW === 'planar' ? 400 / state.planarRadius : 1;
}

function mapLabelFont(size, bold) {
  return (bold ? 'bold ' : '') + (size * mapLabelScale()) + 'px "Segoe UI", Arial, Helvetica, sans-serif';
}

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

var planarTiles = new Map();
var planarTilesLoading = 0;
var planarTileEpoch = 0;

function buildMesh(payload) {
  planarTiles.clear();
  planarTileEpoch++;
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
      data: p,
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
    if (!locationVisible(d.data)) { continue; }
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
    ctx.arc(vis[i].px, vis[i].py, MAP_VIEW === 'planar' ? 5 * planarScale() : 1.7, 0, Math.PI * 2);
    ctx.fill();
    ctx.stroke();
  }

  // Labelling several hundred of these at once would be a grey fog. There is
  // no zoom level to test against here, so the spacing rule below does the
  // work instead: zoomed out almost nothing fits and only a scattering gets
  // named, zoomed in they separate and more of them earn a label. Market
  // labels are drawn after this and so always win the same space.
  if (!state.labels) { return; }
  var budget = state.showAllLocationLabels ? Infinity : 80;
  var labelScale = mapLabelScale();
  ctx.font = mapLabelFont(9, false);
  ctx.textAlign = 'center';
  ctx.textBaseline = 'bottom';
  ctx.fillStyle = 'rgba(0, 0, 0, .7)';
  ctx.strokeStyle = 'rgba(255, 255, 255, .9)';
  ctx.lineWidth = 2.5 * labelScale;
  var taken = [];
  // Nearest first, so the labels that survive are the ones closest to the eye.
  vis.sort(function (a, b) { return a.depth - b.depth; });
  for (i = 0; i < vis.length && taken.length < budget; i++) {
    d = vis[i];
    var clash = false;
    for (var k = 0; !state.showAllLocationLabels && k < taken.length; k++) {
        if (Math.abs(taken[k][0] - d.px) < 58 * labelScale
          && Math.abs(taken[k][1] - d.py) < 13 * labelScale) { clash = true; break; }
    }
    if (clash) { continue; }
    taken.push([d.px, d.py]);
    ctx.strokeText(d.name, d.px, d.py - 3 * labelScale);
    ctx.fillText(d.name, d.px, d.py - 3 * labelScale);
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
  return routedWaterPath(startX, startY, endX, endY, 0);
}

function coastDistanceField() {
  if (mesh.coastDistances) { return mesh.coastDistances; }
  var distances = new Float64Array(mesh.W * mesh.H);
  var diagonal = Math.hypot(mesh.cellW, mesh.cellH);
  for (var index = 0; index < distances.length; index++) {
    distances[index] = isWaterCell(index % mesh.W, Math.floor(index / mesh.W)) ? Infinity : 0;
  }
  function relax(column, row, direction) {
    var index = row * mesh.W + column;
    var neighbours = [[column - direction, row, mesh.cellW],
      [column, row - direction, mesh.cellH],
      [column - direction, row - direction, diagonal],
      [column + direction, row - direction, diagonal]];
    neighbours.forEach(function (next) {
      if (next[0] >= 0 && next[0] < mesh.W && next[1] >= 0 && next[1] < mesh.H) {
        distances[index] = Math.min(distances[index], distances[next[1] * mesh.W + next[0]] + next[2]);
      }
    });
  }
  for (var row = 0; row < mesh.H; row++) {
    for (var column = 0; column < mesh.W; column++) { relax(column, row, 1); }
  }
  for (var row = mesh.H - 1; row >= 0; row--) {
    for (var column = mesh.W - 1; column >= 0; column--) { relax(column, row, -1); }
  }
  var shoreline = Math.min(mesh.cellW, mesh.cellH) / 2;
  mesh.coastDistances = distances.map(function (distance) { return Math.max(0, distance - shoreline); });
  return mesh.coastDistances;
}

function routedWaterPath(startX, startY, endX, endY, coastMiles) {
  var starts = waterCellsNear(startX, startY, 12);
  var ends = waterCellsNear(endX, endY, 12);
  starts = localWaterCells(startX, startY, starts);
  ends = localWaterCells(endX, endY, ends);
  if (!starts.length || !ends.length) { return null; }
  var coast = coastMiles ? coastDistanceField() : null;
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
      if (coastMiles && diagonal && !fractionalWaterSegmentIsClear([column, row], next)) { continue; }
      var penalty = coast ? Math.min(100, Math.round(Math.abs(coast[index] - coastMiles) * 4))
        : waterCoastDistance(next[0], next[1], 4) * 3;
      var stepCost = (diagonal ? 3 : 2) + penalty;
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
    var to = coastMiles ? from + 1 : Math.min(cells.length - 1, from + 8);
    if (coastMiles) {
      var deltaColumn = cells[to][0] - cells[from][0], deltaRow = cells[to][1] - cells[from][1];
      while (to + 1 < cells.length && cells[to + 1][0] - cells[to][0] === deltaColumn &&
          cells[to + 1][1] - cells[to][1] === deltaRow) { to++; }
    }
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
    ,unavailable: !!(spec && spec.unavailable)
  };
}

function routeTypeLabel(kind) {
  var labels = {
    road: 'Road', trail: 'Foot trail', sea: 'Sea',
    river: 'River', barge: 'Barge', ferry: 'Ferry', portage: 'Portage',
    tunnel: 'Tunnel', teleport: 'Teleportation circle', air: 'Gryphon flight', skyship: 'Skyship'
  };
  return labels[kind] || String(kind || 'Route');
}

function routeTypeIcon(kind) {
  var icons = {
    road: '↔', trail: '•', sea: '⛵',
    river: '≋', barge: '▭', ferry: '⇄', portage: '↑',
    tunnel: '◉', air: '\ud83e\udd85', skyship: '✈'
  };
  return icons[kind] || '◆';
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
        '" onclick="selectRouteCarrier(' + routeIndex + ', \'' + esc(carrier.service_id) + '\')">' +
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

function routeMatchesFilter(line, allowPlannedInferred) {
  if (MAP_VIEW === 'planar') { return planarLegVisible(line); }
  if (line.inferredRoad && !state.inferredRoads && !allowPlannedInferred) { return false; }
  if (!state.routeTypes.length) { return true; }
  var modes = line.details && line.details.modes ? line.details.modes : [line.kind];
  return modes.some(function (mode) {
    return state.routeTypes.indexOf(mode === 'track' ? 'trail' : mode) >= 0;
  });
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
  if (line.details && line.details.unavailable) { return 'rgba(130, 130, 130, .48)'; }
  if (line.kind === 'track') { return '#d52323'; }
  if (line.kind === 'trail') { return '#ffcd44'; }
  var service = multilegService(line);
  if (service && service.service_class === 'ground') {
    return GROUND_MULTILEG_ROUTE_STYLE;
  }
  return service ? COMPLEX_ROUTE_STYLE
    : (ROUTE_STYLE[line.kind] || 'rgba(70, 55, 40, .9)');
}

function routeLineDash(line) {
  if (line.details && line.details.unavailable) { return [5, 7]; }
  if (line.kind === 'track') { return [7, 14]; }
  if (line.kind === 'trail') { return [0, 8]; }
  if (line.multi) { return [8, 5]; }
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
      editId: 'road:' + JSON.stringify([road.id || road.name, road.a || '', road.b || '']),
      sourcePoints: points,
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
    var elevated = routeKind === 'air' || routeKind === 'skyship' || routeKind === 'teleport';
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
      editId: 'survey:' + JSON.stringify([route.id || route.name, route.from || '', route.to || '']),
      sourcePoints: points,
      lifts: lifts, multi: !!route.multimodal, traced: true,
      details: routeDetails(tracedSpec, points, byId, route.name, routeKind)
    });
  });

  routeSpec.forEach(function (r) {
    if (r.kind === 'road' && roadNetwork.connects(r.a, r.b)
      && tracedRoadLegs[routeLegKey(r)]) { return; }
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
    var airGoing = r.kind === 'air';
    var landPoints = (overland || airGoing) ? landRoute(a.wx, a.wy, b.wx, b.wy) : null;
    if (airGoing && !landPoints) { landPoints = [[a.wx, a.wy], [b.wx, b.wy]]; }
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
        editId: 'route:' + routeLegKey(r), sourcePoints: waterPoints,
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
        editId: 'route:' + routeLegKey(r), sourcePoints: landPoints,
        multi: !!r.multimodal, landRouted: !airGoing, airRouted: airGoing,
        inferredRoad: !!r.inferred || (r.kind === 'road' && roadGeometrySpec.length > 0),
        details: routeDetails(r, landPoints, byId, r.name, r.kind)
      });
      return;
    }
    var elevated = r.kind === 'air' || r.kind === 'skyship' || r.kind === 'teleport';
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
      editId: 'route:' + routeLegKey(r), sourcePoints: [[a.wx, a.wy], [b.wx, b.wy]],
      multi: !!r.multimodal, inferredRoad: !!r.inferred,
      details: routeDetails(r, [[a.wx, a.wy], [b.wx, b.wy]], byId, r.name, r.kind)
    });
  });
  baseRouteLines = routeLines.slice();
  applyMapLegEdits();
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
  if (s.mobile || s.mapPositionEdited) { return [s.x, s.y]; }
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
  // The near plane has to follow the camera in. A fixed 60 miles is harmless
  // at world scale and clips away the entire scene once you are close enough
  // to read one-mile cells. Never further out than it used to be.
  cam.near = Math.min(0.06, state.dist * 0.02);

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
  if (MAP_VIEW === 'planar') {
    var scale = planarScale() * SCALE;
    _pt[0] = cam.cx + (x - state.tx) * scale;
    _pt[1] = cam.cy + (z - state.tz) * scale;
    _pt[2] = 1;
    return _pt;
  }
  if (state.globe) { return projectGlobe(x, y, z); }
  var dx = x - cam.ex, dy = y - cam.ey, dz = z - cam.ez;
  var vz = dx * cam.fx + dy * cam.fy + dz * cam.fz;
  if (vz < cam.near) { return null; }
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

function minDistance() {
  // How close the camera may get, in scene units of SCALE miles. Only a local
  // detail patch earns the deep floor: the world heightfield has nothing finer
  // than twenty-mile cells to show, so there is no point walking up to it.
  if (!mesh || !mesh.detail || !mesh.cellW) { return 0.35; }
  return Math.max(0.0015, mesh.cellW * 4 / SCALE);
}

function fitView() {
  if (MAP_VIEW === 'planar') { return; }
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
  state.dist = clamp(state.dist, minDistance(), 12);
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

// ---------------------------------------------------------------------------
// level of detail
// ---------------------------------------------------------------------------

// Cells the canvas can fill in one frame. Cost is not quite linear in the
// count - a coarse step draws fewer, larger quads - so this is set from the
// worst case, a shallow oblique view where the ground runs to the horizon.
// Without it the five-mile field would ask for half a million quads a frame.
var TERRAIN_BUDGET = 16000;

// Cell index window that can reach the canvas, and the lattice spacing drawn
// within it. Zoomed out the window is the whole field and the spacing is
// coarse; zoomed in the window is small and every cell is drawn.
var view = { i0: 0, i1: 0, j0: 0, j1: 0, step: 1 };

function updateViewWindow() {
  var W = mesh.W, H = mesh.H;
  if (state.globe || state.roundWorld) {
    // Both of these draw the whole field however far away it is, so there is
    // no window to take.
    view.i0 = 0; view.i1 = W; view.j0 = 0; view.j1 = H;
  } else {
    // Ground the camera can see, as a square around the target. At a shallow
    // pitch the ground runs away to the horizon, so the box grows as the
    // camera lies down.
    var halfMiles = state.dist * SCALE * (cam.cx / cam.focal) * 1.6;
    halfMiles /= Math.max(0.22, Math.sin(state.pitch));
    var b = mesh.bounds;
    var cxMiles = state.tx * SCALE + mesh.cx;
    var cyMiles = state.tz * SCALE + mesh.cy;
    view.i0 = Math.max(0, Math.floor((cxMiles - halfMiles - b[0]) / mesh.cellW));
    view.i1 = Math.min(W, Math.ceil((cxMiles + halfMiles - b[0]) / mesh.cellW));
    view.j0 = Math.max(0, Math.floor((cyMiles - halfMiles - b[1]) / mesh.cellH));
    view.j1 = Math.min(H, Math.ceil((cyMiles + halfMiles - b[1]) / mesh.cellH));
  }
  var visible = Math.max(1, (view.i1 - view.i0) * (view.j1 - view.j0));
  var budget = TERRAIN_BUDGET / state.step;
  var step = 1;
  while (step < 64 && visible / (step * step) > budget) { step++; }
  view.step = step;
  // Align to the lattice so cells do not shimmer as the view is panned.
  view.i0 -= view.i0 % step;
  view.j0 -= view.j0 % step;
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
  var row = W + 1;
  var step = view.step;
  // Anything left outside the window keeps ok = 0, so every consumer of the
  // shared vertex arrays skips it rather than reading a stale projection.
  ok.fill(0);
  var near = cam.near;
  // One lattice point past the window, clamped, so the far edge of the last
  // drawn cell has a projected corner to use.
  for (var j = view.j0; j <= view.j1 + step; j += step) {
    var jj = Math.min(j, H);
    var z = vz[jj];
    var dz = z - cam.ez;
    var base = jj * row;
    for (var i = view.i0; i <= view.i1 + step; i += step) {
      var ii = Math.min(i, W);
      var k = base + ii;
      var dx = vx[ii] - cam.ex;
      var dy = vh[k] * exag - cam.ey;
      var d = dx * cam.fx + dy * cam.fy + dz * cam.fz;
      if (d < near) { ok[k] = 0; continue; }
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
  var W = mesh.W, H = mesh.H, step = view.step;
  var px = mesh.px, py = mesh.py, ok = mesh.ok, colors = mesh.colors;
  var row = W + 1;

  // Painter's algorithm on an axis-aligned grid: walk each axis away from the
  // eye, so nearer cells are painted over farther ones.
  var cols = [];
  var rows = [];
  var i, j;
  for (i = view.i0; i < view.i1; i += step) { cols.push(i); }
  for (j = view.j0; j < view.j1; j += step) { rows.push(j); }
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
  var W = mesh.W, H = mesh.H, step = view.step;
  var vx = mesh.vx, vz = mesh.vz, cells = mesh.cells, colors = mesh.colors;
  var cols = [], rows = [];
  var i, j;
  for (i = view.i0; i < view.i1; i += step) { cols.push(i); }
  for (j = view.j0; j < view.j1; j += step) { rows.push(j); }
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
  var W = mesh.W, H = mesh.H, step = view.step;
  var px = mesh.px, py = mesh.py, ok = mesh.ok;
  var row = W + 1;
  ctx.beginPath();
  for (var j = view.j0; j <= view.j1; j += step) {
    var base = j * row;
    for (var i = view.i0; i < view.i1; i += step) {
      var i2 = Math.min(i + step, W);
      if (!ok[base + i] || !ok[base + i2]) { continue; }
      ctx.moveTo(px[base + i], py[base + i]);
      ctx.lineTo(px[base + i2], py[base + i2]);
    }
  }
  for (var x = view.i0; x <= view.i1; x += step) {
    for (var z = view.j0; z < view.j1; z += step) {
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
  if (!img || !img.width || !img.height) { return; }
  if ((state.underOn || posterOnly) && (posterOnly || state.underAlpha > 0.001)) {
    drawUnderlayLayer(img, posterOnly ? 1 : state.underAlpha, posterOnly);
  }
  if (!posterOnly && state.rasterLayers) {
    Object.values(state.rasterLayers).forEach(function (layer) {
      if (layer.on && layer.image && layer.alpha > 0) {
        drawUnderlayLayer(layer.image, layer.alpha, false);
      }
    });
  }
}

function drawUnderlayLayer(img, alpha, posterOnly) {
  if (!underCanvas.width || !underCanvas.height) { return; }

  var iw = img.width, ih = img.height;
  var mppX = state.underMpp * state.under.width / iw;
  var mppY = state.underMpp * state.underStretch * state.under.height / ih;
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
  ctx.globalAlpha = alpha;
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
    var lift = (line.lifts ? line.lifts[index] : 0) + flightDayLift(line);
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

function projectedFlightHops(line) {
  var hops = Math.max(1, Math.ceil(Number(line.details && line.details.distance || 0) / 80));
  var gap = 0;
  var points = [];
  function pointAt(progress) {
    var position = progress * (line.xs.length - 1);
    var index = Math.min(line.xs.length - 2, Math.floor(position));
    var fraction = position - index;
    var x = line.xs[index] + (line.xs[index + 1] - line.xs[index]) * fraction;
    var z = line.zs[index] + (line.zs[index + 1] - line.zs[index]) * fraction;
    var h = line.hs[index] + (line.hs[index + 1] - line.hs[index]) * fraction;
    var projected = project(x, h * state.exag + flightDayLift(line) + 0.004, z);
    return projected ? [projected[0], projected[1]] : null;
  }
  for (var hop = 0; hop < hops; hop++) {
    var start = pointAt(hop / hops + gap);
    var end = pointAt((hop + 1) / hops - gap);
    if (start && end) { points.push([start, end]); }
  }
  return points;
}

function flightDayLift(line) {
  return 0;
}

function flightDayProgress(line) {
  return 0.5;
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
  var planFocus = selected < 0 && Object.keys(state.planRouteKeys).length > 0;
  var supplyFocus = selected < 0 && !planFocus && Object.keys(state.supplyRouteKeys).length > 0;
  var selectedLocation = selected < 0 && !planFocus && !supplyFocus ? state.selected : null;
  var locationHasRoutes = selectedLocation && routeLines.some(function (line) {
    return routeMatchesFilter(line) && line.details
      && (line.details.a === selectedLocation || line.details.b === selectedLocation);
  });
  var focusOn = selected >= 0 || planFocus || supplyFocus || locationHasRoutes;
  for (var pass = 0; pass < 1; pass++) {
    for (var r = 0; r < routeLines.length; r++) {
      var line = routeLines[r];
      if (!routeMatchesFilter(line, planFocus && planRouteMatches(line))) { continue; }
      var active = selected >= 0 ? selectedGroup.indexOf(line) >= 0
        : (planFocus ? planRouteMatches(line) : (supplyFocus ? supplyRouteMatches(line) : !!(locationHasRoutes && line.details
          && (line.details.a === selectedLocation || line.details.b === selectedLocation))));
      if (focusOn && !active) { continue; }
      var width = ROUTE_WIDTH[line.kind] || 2.1;
      if (planFocus && active) { width *= 2; }
      ctx.setLineDash(routeLineDash(line));
      var curves = projectedRouteCurves(line);
      ctx.beginPath();
      if (line.kind === 'air') {
        projectedFlightHops(line).forEach(function (hop) {
          var midX = (hop[0][0] + hop[1][0]) / 2;
          var midY = (hop[0][1] + hop[1][1]) / 2 - 18;
          ctx.moveTo(hop[0][0], hop[0][1]);
          ctx.quadraticCurveTo(midX, midY, hop[1][0], hop[1][1]);
        });
      } else {
        curves.forEach(function (segments) {
          ctx.moveTo(segments[0][0][0], segments[0][0][1]);
          segments.forEach(function (segment) {
            ctx.bezierCurveTo(segment[1][0], segment[1][1], segment[2][0], segment[2][1], segment[3][0], segment[3][1]);
          });
        });
      }
      if (curves.length) {
        var dimmed = false;
        ctx.strokeStyle = dimmed ? 'rgba(238, 238, 238, .72)' : 'rgba(255, 248, 224, .90)';
        ctx.lineWidth = width + 2.4;
        ctx.stroke();
        ctx.strokeStyle = dimmed ? 'rgba(116, 116, 116, .52)' : routeDisplayColor(line);
        ctx.lineWidth = dimmed ? Math.max(1.4, width - 0.5) : width;
        ctx.stroke();
        if (planFocus && active && routeAnimationActive()) {
          ctx.save(); ctx.setLineDash([10, 18]); ctx.lineDashOffset = -performance.now() / 45;
          ctx.lineWidth = width / 2; ctx.strokeStyle = '#ffffff'; ctx.stroke(); ctx.restore();
        }
      }
    }
  }
  // Icons need their own final pass or later crossing routes paint over them.
  if (state.routeIcons) {
    for (var iconPass = 0; iconPass < 1; iconPass++) {
      for (var iconIndex = 0; iconIndex < routeLines.length; iconIndex++) {
        var iconLine = routeLines[iconIndex];
        if (!routeMatchesFilter(iconLine, planFocus && planRouteMatches(iconLine))) { continue; }
        var iconActive = selected >= 0 ? selectedGroup.indexOf(iconLine) >= 0
          : (planFocus ? planRouteMatches(iconLine) : (supplyFocus ? supplyRouteMatches(iconLine) : !!(locationHasRoutes && iconLine.details
            && (iconLine.details.a === selectedLocation || iconLine.details.b === selectedLocation))));
        if (focusOn && !iconActive) { continue; }
        var iconPoint = routeIconPoint(iconLine, exag);
        if (iconPoint) { drawRouteIcon(iconPoint[0], iconPoint[1], iconLine, focusOn && !iconActive); }
      }
    }
  }
  // Everything drawn after this -- dots, labels, selection rings -- must be solid.
  ctx.setLineDash([]);
}

function routeIconPoint(line, exag) {
  var index = line.kind === 'air'
    ? Math.min(line.xs.length - 1, Math.floor(flightDayProgress(line) * line.xs.length))
    : Math.floor(line.xs.length / 2);
  var lift = (line.lifts ? line.lifts[index] : 0) + flightDayLift(line);
  var point = project(line.xs[index], line.hs[index] * exag + lift + 0.006, line.zs[index]);
  if (point && line.kind === 'air') { point = [point[0], point[1] - 18, point[2]]; }
  return point ? [point[0], point[1]] : null;
}

function drawRouteIcon(x, y, line, dimmed) {
  var complex = !!multilegService(line);
  var glyph = complex ? '⇝' : routeTypeIcon(line.kind);
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

function plannedLocation(name) {
  return !!(state.planRoute && !legEditor.enabled && (state.planRoute.legs || []).some(function (leg) {
    return leg.from === name || leg.to === name;
  }));
}

function routeAnimationsEnabled() {
  return state.animateRoutes === null
    ? !window.matchMedia('(prefers-reduced-motion: reduce)').matches
    : state.animateRoutes;
}

function routeAnimationActive() {
  return !!(state.planRoute && !legEditor.enabled && routeAnimationsEnabled());
}

function wireRouteAnimation() {
  var input = document.getElementById('animate-routes');
  var key = 'faerun-map-animate-routes';
  try {
    var saved = window.localStorage.getItem(key);
    if (saved !== null && saved !== 'true' && saved !== 'false') {
      throw new Error('Invalid saved route animation preference');
    }
    state.animateRoutes = saved === null ? null : saved === 'true';
  } catch (err) {
    console.error('Route animation preference could not be restored.', err);
    showStatus('Route animation preference could not be restored.', true);
  }
  input.checked = routeAnimationsEnabled();
  input.addEventListener('change', function () {
    state.animateRoutes = input.checked;
    invalidate();
    try {
      window.localStorage.setItem(key, String(state.animateRoutes));
    } catch (err) {
      console.error('Route animation preference could not be saved.', err);
      showStatus('Route animation preference could not be saved; this choice applies only to this page.', true);
    }
  });
  window.matchMedia('(prefers-reduced-motion: reduce)').addEventListener('change', function () {
    if (state.animateRoutes === null) {
      input.checked = routeAnimationsEnabled();
      invalidate();
    }
  });
}

function drawRoutePulse(x, y, radius) {
  if (!routeAnimationActive()) { return; }
  var phase = (performance.now() % 1600) / 1600;
  ctx.save(); ctx.setLineDash([]);
  ctx.globalAlpha *= 1 - phase;
  ctx.strokeStyle = '#d62f39'; ctx.lineWidth = 2;
  ctx.beginPath(); ctx.arc(x, y, radius + 3 + phase * 10, 0, Math.PI * 2); ctx.stroke();
  ctx.restore();
}

function mapPinRadius(pin, selected, hovered) {
  var emphasis = plannedLocation(pin.data.name) ? 2 : 1;
  if (MAP_VIEW === 'planar') {
    return (pin.data.mobile ? 2.5 : 3.75) * planarScale() * emphasis;
  }
  return pin.radius * (pin.data.mobile ? 1 : 0.75) * (selected ? 1.5 : (hovered ? 1.25 : 1)) * emphasis;
}

function caravanIconPosition(pin) {
  var hostId = pin.data.status === 'encamped' && pin.data.host && pin.data.host.id;
  var host = hostId && pins.find(function (candidate) { return candidate.data.id === hostId; });
  var anchor = host && host.vis ? host : pin;
  if (MAP_VIEW === 'planar' && !host) { return {x: pin.px, y: pin.py}; }
  var radius = mapPinRadius(anchor, state.selected === anchor.data.id, state.hover === pins.indexOf(anchor));
  var companions = host ? pins.filter(function (candidate) {
    return candidate.vis && candidate.data.mobile && candidate.data.status === 'encamped' &&
      candidate.data.host && candidate.data.host.id === hostId;
  }).sort(function (left, right) { return left.data.id.localeCompare(right.data.id); }) : [pin];
  var markerRadius = MAP_VIEW === 'planar' ? companions.reduce(function (largest, candidate) {
    return Math.max(largest, mapPinRadius(candidate, false, false));
  }, mapPinRadius(pin, false, false)) : 18;
  var gap = MAP_VIEW === 'planar' ? 1.25 * planarScale() : 6;
  var spacing = markerRadius * 2 + gap;
  var distance = radius + markerRadius + gap;
  var index = Math.max(0, companions.indexOf(pin));
  // Use chord spacing to fit a chain around each ring without overlapping icons.
  var capacity = Math.max(1, Math.floor(Math.PI / Math.asin(Math.min(1, spacing / (2 * distance)))));
  while (index >= capacity) {
    index -= capacity;
    distance += spacing;
    capacity = Math.max(1, Math.floor(Math.PI / Math.asin(spacing / (2 * distance))));
  }
  var angle = -Math.PI / 2 + index * 2 * Math.PI / capacity;
  return {x: anchor.px + Math.cos(angle) * distance, y: anchor.py + Math.sin(angle) * distance};
}

function drawCaravanMarker(pin) {
  var center = caravanIconPosition(pin);
  var radius = mapPinRadius(pin, false, false);
  ctx.save(); ctx.setLineDash([]);
  ctx.beginPath(); ctx.arc(center.x, center.y, radius, 0, Math.PI * 2);
  ctx.fillStyle = '#ffffff'; ctx.fill();
  ctx.strokeStyle = '#000000'; ctx.lineWidth = 0.2 * planarScale(); ctx.stroke();
  // The covered wagon's full bounds fit inside the circle at every zoom.
  ctx.translate(center.x, center.y);
  ctx.scale(radius / 18, radius / 18);
  drawCaravanIcon(0, 0, '#8a4d23');
  ctx.restore();
}

function drawCaravanIcon(x, y, color) {
  ctx.save(); ctx.setLineDash([]); ctx.lineWidth = 2;
  ctx.strokeStyle = '#ffffff'; ctx.fillStyle = color;
  ctx.beginPath(); ctx.rect(x - 9, y - 6, 18, 10); ctx.fill(); ctx.stroke();
  ctx.beginPath(); ctx.moveTo(x - 9, y - 6);
  ctx.quadraticCurveTo(x, y - 15, x + 9, y - 6); ctx.stroke();
  [-5, 5].forEach(function (offset) {
    ctx.beginPath(); ctx.arc(x + offset, y + 6, 3, 0, Math.PI * 2); ctx.fill(); ctx.stroke();
  });
  ctx.restore();
}

function drawPins() {
  var exag = state.exag;
  var order = [];
  var routeConnected = routeConnectedLocationIds();
  for (var i = 0; i < pins.length; i++) {
    var pin = pins[i];
    pin.vis = false;
    if (!locationVisible(pin.data)) { continue; }
    if (pin.data.surveyed && !state.places) { continue; }
    // Seated on the ground itself. Nudged up by a hair only so the dot is not
    // z-fought by the terrain quad it stands on.
    var p = project(pin.sx, pin.h * exag + 0.004, pin.sz);
    if (!p) { continue; }
    pin.px = p[0]; pin.py = p[1]; pin.depth = p[2];
    pin.vis = true;
    order.push(i);
  }
  order.sort(function (a, b) {
    return Number(!!pins[a].data.mobile) - Number(!!pins[b].data.mobile) || pins[b].depth - pins[a].depth;
  });

  for (var k = 0; k < order.length; k++) {
    var s = pins[order[k]];
    var selected = state.selected === s.data.id;
    var hovered = state.hover === order[k];

    var r = mapPinRadius(s, selected, hovered);
    if (plannedLocation(s.data.name)) { drawRoutePulse(s.px, s.py, r); }
    if (MAP_VIEW === 'planar' && s.data.mobile) {
      drawCaravanMarker(s);
      continue;
    }
    if (state.heatById && !(MAP_VIEW === 'planar' && s.data.mobile)) {
      drawPriceTower(s, r, selected);
      continue;
    }
    ctx.beginPath();
    if (s.data.mapOnly && MAP_VIEW !== 'planar') {
      ctx.rect(s.px - r, s.py - r, r * 2, r * 2);
    } else {
      ctx.arc(s.px, s.py, r, 0, Math.PI * 2);
    }
    ctx.fillStyle = MAP_VIEW === 'planar' && s.data.mobile ? '#ffffff' :
      pinFill(s, state.routeTypes.length > 0 && !routeConnected.has(s.data.id));
    ctx.fill();
    var scaledBorder = MAP_VIEW === 'planar';
    ctx.lineWidth = scaledBorder ? 0.6 * planarScale() : (selected ? 4 : 3);
    ctx.strokeStyle = scaledBorder ? '#000000' : '#ffffff';
    ctx.stroke();
    if (selected && !scaledBorder) {
      // A white ring alone would vanish against snow or glacier, so the
      // selected dot gets a second black ring just outside it.
      ctx.lineWidth = 1;
      ctx.strokeStyle = '#000000';
      ctx.beginPath();
      ctx.arc(s.px, s.py, r + 1.8, 0, Math.PI * 2);
      ctx.stroke();
    }

    if (MAP_VIEW === 'planar') { drawLocationTypeIcon(s.data, s.px, s.py, r); }
    if (locationIsPort(s.data) && (MAP_VIEW !== 'planar' || !['city', 'capital'].includes(locationType(s.data)))) {
      drawPortIcon(s.px, s.py, r);
    }
    if (s.data.mobile) {
      var caravan = caravanIconPosition(s);
      drawCaravanIcon(caravan.x, caravan.y, '#8a4d23');
    }
    if (s.data.gryphonPort) { drawGryphonIcon(s.px, s.py - r - 6, '#7a3b12'); }

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
  if (state.labels || state.companyLabels === 'show') { drawLabels(order); }
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
  var labelScale = mapLabelScale();
  ctx.font = mapLabelFont(12, false);
  ctx.textAlign = 'left';
  ctx.textBaseline = 'middle';
  var taken = [];
  // Draw the nearest labels first so they win the space.
  for (var k = order.length - 1; k >= 0; k--) {
    var s = pins[order[k]];
    var d = s.data;
    if (d.mobile && state.companyLabels === 'hide') { continue; }
    var showCompany = d.mobile && state.companyLabels === 'show';
    if (!state.labels && !showCompany) { continue; }
    var showAll = state.showAllLocationLabels || showCompany;
    var important = state.selected === d.id || state.hover === order[k];
    if (!showAll && !important && d.population < 12000) { continue; }
    var text = d.name;
    // Set the font before measuring, so the collision box matches the weight
    // the label is actually drawn at.
    ctx.font = mapLabelFont(12, important);
    var w = ctx.measureText(text).width;
    var marker = d.mobile ? caravanIconPosition(s) :
      {x: state.heatById ? s.towerTipX : s.px, y: state.heatById ? s.towerTipY : s.py};
    var lx = marker.x + mapPinRadius(s, state.selected === d.id, state.hover === order[k]) + 5 * labelScale;
    var ly = marker.y - 4 * labelScale;
    if (MAP_VIEW === 'planar' && d.mobile && d.status === 'encamped') {
      ly = marker.y + mapPinRadius(s, false, false) + 10 * labelScale;
    }
    var box = [lx - 2 * labelScale, ly - 8 * labelScale, lx + w + 2 * labelScale, ly + 8 * labelScale];
    var clash = false;
    for (var t = 0; !showAll && t < taken.length; t++) {
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
    ctx.lineWidth = 3 * labelScale;
    ctx.strokeStyle = 'rgba(255, 255, 255, .92)';
    ctx.strokeText(text, lx, ly);
    ctx.fillStyle = '#000000';
    ctx.fillText(text, lx, ly);
  }
}

function planarScale() {
  return Math.max(1, Math.min(cam.cx, cam.cy) - 24) / state.planarRadius;
}

function planarPoint(worldX, worldY) {
  var scale = planarScale();
  return [cam.cx + (worldX - mesh.cx - state.tx * SCALE) * scale,
          cam.cy + (worldY - mesh.cy - state.tz * SCALE) * scale];
}

function setPlanarRadius(radius) {
  state.planarRadius = Number(radius);
  document.getElementById('planar-radius').value = String(radius);
  if (state.selected) { focusSettlement(state.selected); }
  invalidate();
}

function stepPlanarRadius(direction) {
  var radii = [50, 100, 200, 500];
  var index = radii.indexOf(state.planarRadius);
  setPlanarRadius(radii[clamp(index + direction, 0, radii.length - 1)]);
}

function drawPlanarGrid(left, top, right, bottom) {
  var cell = state.planarCell;
  var scale = planarScale();
  if (cell * scale < 3) { return; }
  ctx.lineWidth = 1;
  if (state.planarGrid === 'square' || state.planarGrid === 'both') {
    ctx.beginPath();
    ctx.strokeStyle = 'rgba(20, 55, 85, .48)';
    for (var column = Math.floor(left / cell); column <= Math.ceil(right / cell); column++) {
      var squareTop = planarPoint(column * cell, top);
      var squareBottom = planarPoint(column * cell, bottom);
      ctx.moveTo(squareTop[0], squareTop[1]); ctx.lineTo(squareBottom[0], squareBottom[1]);
    }
    for (var row = Math.floor(top / cell); row <= Math.ceil(bottom / cell); row++) {
      var squareLeft = planarPoint(left, row * cell);
      var squareRight = planarPoint(right, row * cell);
      ctx.moveTo(squareLeft[0], squareLeft[1]); ctx.lineTo(squareRight[0], squareRight[1]);
    }
    ctx.stroke();
  }
  if (state.planarGrid === 'hex' || state.planarGrid === 'both') {
    var side = cell / Math.sqrt(3);
    var rowHeight = side * 1.5;
    ctx.beginPath();
    ctx.strokeStyle = 'rgba(65, 30, 45, .55)';
    for (var hexRow = Math.floor(top / rowHeight) - 1; hexRow <= Math.ceil(bottom / rowHeight) + 1; hexRow++) {
      var offset = ((hexRow % 2) + 2) % 2 * cell / 2;
      for (var hexColumn = Math.floor(left / cell) - 1; hexColumn <= Math.ceil(right / cell) + 1; hexColumn++) {
        var center = planarPoint(hexColumn * cell + offset, hexRow * rowHeight);
        for (var corner = 0; corner < 6; corner++) {
          var angle = Math.PI / 3 * corner - Math.PI / 2;
          var cornerX = center[0] + Math.cos(angle) * side * scale;
          var cornerY = center[1] + Math.sin(angle) * side * scale;
          if (!corner) { ctx.moveTo(cornerX, cornerY); } else { ctx.lineTo(cornerX, cornerY); }
        }
        ctx.closePath();
      }
    }
    ctx.stroke();
  }
}

function applyMapLegEdits() {
  var originals = {};
  baseRouteLines.forEach(function (line) { originals[line.editId] = line; });
  routeLines = baseRouteLines.filter(function (line) { return !mapLegEdits.legs[line.editId]; });
  routeLines = routeLines.map(function (line) {
    var name = (mapLegEdits.names || {})[line.editId];
    return name ? Object.assign({}, line, {details: Object.assign({}, line.details, {name: name})}) : line;
  });
  Object.keys(mapLegEdits.legs).forEach(function (identifier) {
    var saved = mapLegEdits.legs[identifier];
    if (saved.deleted) { return; }
    var original = originals[identifier];
    var geometry = saved.path || saved.points;
    var distance = 0;
    geometry.forEach(function (point, index) {
      if (index) { distance += Math.hypot(point[0] - geometry[index - 1][0], point[1] - geometry[index - 1][1]); }
    });
    var line = Object.assign({}, original || {}, {editId: identifier, sourcePoints: geometry,
      waypoints: saved.points, pointIndices: saved.pointIndices,
      kind: saved.kind, traced: true, inferredRoad: false, lifts: null, multi: false,
      xs: [], zs: [], hs: [], details: Object.assign({}, original ? original.details : {},
        {name: saved.name, kind: saved.kind, modes: [saved.kind], distance: distance, carriers: []})});
    geometry.forEach(function (point) {
      var scene = toScene(point[0], point[1]);
      line.xs.push(scene[0]); line.zs.push(scene[1]); line.hs.push(Math.max(0, sampleHeight(point[0], point[1])));
    });
    routeLines.push(line);
  });
  state.selectedRoute = -1;
  invalidate();
}

function legMessage(message) { document.getElementById('leg-edit-status').textContent = message; }

function planarLegEndpoints(points) {
  function endpoint(point) {
    var junction = Object.values(mapLegEdits.junctions || {}).find(function (item) {
      return Math.hypot(item.point[0] - point[0], item.point[1] - point[1]) < 0.001;
    });
    if (junction) { return {point: junction.point, name: junction.name, distance: 0}; }
    var closest = null, distance = Infinity;
    (pins || []).forEach(function (pin) {
      if (pin.data.mobile) { return; }
      var miles = Math.hypot(pin.wx - point[0], pin.wy - point[1]);
      if (miles < distance) { closest = pin; distance = miles; }
    });
    return {point: closest ? [closest.wx, closest.wy] : point,
      name: closest ? closest.data.name : 'Unknown', distance: distance};
  }
  if (!points || points.length < 2) { return null; }
  var ends = [endpoint(points[0]), endpoint(points[points.length - 1])];
  ends.sort(function (left, right) {
    return left.point[1] - right.point[1] || left.point[0] - right.point[0];
  });
  return {origin: ends[0], destination: ends[1]};
}

function legEndpointLabel(endpoint) {
  return endpoint.name + (Number.isFinite(endpoint.distance) && endpoint.distance > 2.5
    ? ' (nearest, ' + endpoint.distance.toFixed(1) + ' mi)' : '');
}

function namedRoadLeg(draft) {
  if (draft.kind !== 'road') { return draft.name; }
  var endpoints = planarLegEndpoints(draft.points);
  if (!endpoints || endpoints.origin.name === 'Unknown' || endpoints.destination.name === 'Unknown') { return draft.name; }
  var base = String(draft.name).replace(/: .* to .*$/, '').replace(/ [(]part [12][)]$/, '').trim();
  return base + ': ' + endpoints.origin.name + ' to ' + endpoints.destination.name;
}

function syncLegEditor() {
  var draft = legEditor.draft, busy = legEditor.saving;
  var endpoints = draft && planarLegEndpoints(draft.points);
  document.getElementById('leg-origin').textContent = endpoints ? legEndpointLabel(endpoints.origin) : '-';
  document.getElementById('leg-destination').textContent = endpoints ? legEndpointLabel(endpoints.destination) : '-';
  document.getElementById('leg-edit-tools').hidden = !legEditor.enabled;
  document.getElementById('leg-edit-enabled').checked = legEditor.enabled;
  document.getElementById('leg-edit-enabled').disabled = !legEditor.ready || busy || !!(locationEditor && locationEditor.enabled);
  ['name', 'kind'].forEach(function (field) {
    var control = document.getElementById('leg-' + field);
    control.disabled = !draft || busy;
    control.value = draft ? draft[field] : (field === 'kind' ? 'road' : '');
  });
  document.getElementById('leg-new').disabled = busy || !legEditor.ready;
  document.getElementById('leg-save').disabled = busy || !draft || draft.points.length < 2 || !legEditor.dirty;
  document.getElementById('leg-delete').disabled = busy || !draft || legEditor.creating;
  document.getElementById('leg-cancel').disabled = busy || !draft;
  document.getElementById('leg-insert').disabled = busy || !draft || legEditor.creating;
  document.getElementById('leg-insert').setAttribute('aria-pressed', String(legEditor.insert));
  document.getElementById('leg-add-point').disabled = busy || !draft;
  document.getElementById('leg-add-point').setAttribute('aria-pressed', String(!!legEditor.add));
  document.getElementById('leg-remove-point').disabled = busy || !draft || legEditor.point < 0 || draft.points.length <= 2;
  document.getElementById('leg-undo').disabled = busy || !legEditor.undo.length;
  document.getElementById('leg-redo').disabled = busy || !legEditor.redo.length;
  var dailyMiles = draft ? legDailyMiles(draft.kind) : 0;
  document.getElementById('leg-smooth').disabled = busy || !draft || draft.points.length < 2 || !dailyMiles;
  document.getElementById('leg-curve').disabled = busy || !draft || draft.points.length < 2;
  document.getElementById('leg-coast').disabled = busy || !draft || draft.points.length < 2 || draft.kind !== 'sea';
  document.getElementById('leg-curvature').disabled = busy || !draft || draft.points.length < 2;
  document.getElementById('leg-straighten').disabled = busy || !draft || !draft.path;
  document.getElementById('leg-day-rate').textContent = draft
    ? (dailyMiles ? dailyMiles + ' mi/day (' + (dailyMiles / 3).toFixed(1) + ' leagues)' : 'No daily travel rate') : '';
  document.getElementById('leg-split').disabled = busy || !draft || legEditor.point <= 0 || legEditor.point >= draft.points.length - 1;
  document.getElementById('leg-junction').disabled = busy || !draft || draft.points.length < 2 ||
    !['road', 'trail', 'track'].includes(draft.kind) || legEditor.point < 0;
  document.getElementById('leg-point-count').textContent = draft
    ? draft.points.length + ' waypoints / ' + Math.max(0, draft.points.length - 1) + ' segments' +
      (legEditor.point >= 0 ? ' / Point ' + (legEditor.point + 1) : '') + (legEditor.dirty ? ' / Unsaved' : '') : '';
}

async function discardLegDraft() {
  if (legEditor.saving) { return false; }
  if (legEditor.dirty) {
    if (!window.confirm('Save route leg changes before continuing?')) { return false; }
    await saveLegDraft(false);
    if (legEditor.dirty) { return false; }
  }
  legEditor.draft = null; legEditor.point = -1; legEditor.insert = false;
  legEditor.add = false; legEditor.snapTarget = null;
  legEditor.creating = false; legEditor.dirty = false; legEditor.undo = []; legEditor.redo = [];
  legEditor.drag = null;
  syncLegEditor(); invalidate(); return true;
}

function rememberLeg() {
  legEditor.undo.push(JSON.stringify(legEditor.draft));
  if (legEditor.undo.length > 100) { legEditor.undo.shift(); }
  legEditor.redo = []; legEditor.dirty = true;
}

function legHistory(undo) {
  var source = undo ? legEditor.undo : legEditor.redo;
  var target = undo ? legEditor.redo : legEditor.undo;
  if (!source.length || legEditor.saving) { return; }
  target.push(JSON.stringify(legEditor.draft));
  legEditor.draft = JSON.parse(source.pop()); legEditor.point = -1; legEditor.dirty = true;
  syncLegEditor(); invalidate();
}

function legWorldPoint(screenX, screenY) {
  return [mesh.cx + state.tx * SCALE + (screenX - cam.cx) / planarScale(),
          mesh.cy + state.tz * SCALE + (screenY - cam.cy) / planarScale()];
}

function nearestLegSegment(points, screenX, screenY) {
  var best = {index: -1, distance: 12 * 12, point: null};
  for (var index = 1; index < points.length; index++) {
    var start = planarPoint(points[index - 1][0], points[index - 1][1]);
    var end = planarPoint(points[index][0], points[index][1]);
    var deltaX = end[0] - start[0], deltaY = end[1] - start[1];
    var length = deltaX * deltaX + deltaY * deltaY;
    var fraction = length ? clamp(((screenX - start[0]) * deltaX + (screenY - start[1]) * deltaY) / length, 0, 1) : 0;
    var nearestX = start[0] + deltaX * fraction, nearestY = start[1] + deltaY * fraction;
    var distance = Math.pow(nearestX - screenX, 2) + Math.pow(nearestY - screenY, 2);
    if (distance < best.distance) { best = {index: index, distance: distance, point: legWorldPoint(nearestX, nearestY)}; }
  }
  return best;
}

function snappedLegPoint(screenX, screenY, bypass) {
  var result = {point: legWorldPoint(screenX, screenY), label: ''};
  var bestDistance = 14 * 14;
  if (!bypass && document.getElementById('leg-snap').checked) {
    function consider(point, label) {
      var screen = planarPoint(point[0], point[1]);
      var distance = Math.pow(screen[0] - screenX, 2) + Math.pow(screen[1] - screenY, 2);
      if (distance <= bestDistance) {
        bestDistance = distance; result = {point: point.slice(), label: label};
      }
    }
    (routeLines || []).forEach(function (line) {
      if (!planarLegVisible(line)) { return; }
      if (legEditor.draft && line.editId === legEditor.draft.id) { return; }
      (line.waypoints || line.sourcePoints || []).forEach(function (point, index) {
        consider(point, (line.details.name || 'Leg') + ' / Point ' + (index + 1));
      });
    });
    (pins || []).forEach(function (pin) {
      if (!pin.data.mobile) { consider([pin.wx, pin.wy], pin.data.name); }
    });
    Object.values(mapLegEdits.junctions || {}).forEach(function (junction) {
      consider(junction.point, junction.name);
    });
  }
  legEditor.snapTarget = result.label ? result : null;
  return result;
}

function addLegWaypoint(screenX, screenY, bypass) {
  var target = snappedLegPoint(screenX, screenY, bypass);
  var position = legEditor.point >= 0 ? legEditor.point + 1 : legEditor.draft.points.length;
  rememberLeg();
  insertLegWaypoint(legEditor.draft, position, target.point);
  legEditor.point = position;
  legMessage(target.label ? 'Snapped to ' + target.label : '');
  syncLegEditor(); invalidate();
}

async function editLegAt(screenX, screenY) {
  var nearest = null, distance = 144;
  routeLines.forEach(function (line) {
    if (!line.sourcePoints || !planarLegVisible(line)) { return; }
    var hit = nearestLegSegment(line.sourcePoints, screenX, screenY);
    if (hit.index >= 0 && hit.distance < distance) { nearest = line; distance = hit.distance; }
  });
  if (!nearest || !await discardLegDraft()) { return; }
  legEditor.draft = {id: nearest.editId, name: nearest.details.name || 'Map leg', kind: nearest.kind,
    points: (nearest.waypoints || nearest.sourcePoints).map(function (point) { return point.slice(); })};
  if (nearest.pointIndices) {
    legEditor.draft.path = nearest.sourcePoints.map(function (point) { return point.slice(); });
    legEditor.draft.pointIndices = nearest.pointIndices.slice();
  }
  legMessage(''); syncLegEditor(); invalidate();
}

function junctionAt(screenX, screenY) {
  return junctionLocations().find(function (location) {
    var screen = planarPoint(location.x, location.y);
    return Math.hypot(screenX - screen[0], screenY - screen[1]) <= 2.5 * planarScale() + 7;
  });
}

function legPointerDown(event) {
  if (MAP_VIEW !== 'planar' || !legEditor.enabled || event.shiftKey || event.button !== 0) { return false; }
  if (legEditor.saving) { return true; }
  var rect = canvas.getBoundingClientRect();
  var screenX = event.clientX - rect.left, screenY = event.clientY - rect.top;
  var draft = legEditor.draft;
  if (!draft) {
    var junction = junctionAt(screenX, screenY);
    if (junction) { focusJunction(junction); return true; }
  }
  if (draft) {
    var nearestPoint = -1, distance = 100;
    draft.points.forEach(function (point, index) {
      var screen = planarPoint(point[0], point[1]);
      var delta = Math.pow(screen[0] - screenX, 2) + Math.pow(screen[1] - screenY, 2);
      if (delta < distance) { nearestPoint = index; distance = delta; }
    });
    if (nearestPoint >= 0 && !legEditor.insert && !legEditor.add) {
      legEditor.point = nearestPoint;
      legEditor.drag = {pointer: event.pointerId, remembered: false};
      canvas.setPointerCapture(event.pointerId); syncLegEditor(); invalidate(); return true;
    }
    if (legEditor.add || (legEditor.creating && !legEditor.insert)) {
      addLegWaypoint(screenX, screenY, event.altKey); return true;
    }
    if (legEditor.insert) {
      var segment = nearestLegSegment(draft.path || draft.points, screenX, screenY);
      if (segment.index >= 0) {
        var target = snappedLegPoint(screenX, screenY, event.altKey);
        var position = draft.path ? draft.pointIndices.findIndex(function (index) { return index >= segment.index; }) : segment.index;
        rememberLeg(); insertLegWaypoint(draft, position, target.label ? target.point : segment.point, segment.index);
        legEditor.point = position; legEditor.insert = false;
        legMessage(target.label ? 'Snapped to ' + target.label : '');
        syncLegEditor(); invalidate();
      }
      return true;
    }
  }
  editLegAt(screenX, screenY);
  return true;
}

async function saveLegDraft(deleted) {
  if (!legEditor.draft || legEditor.saving) { return; }
  if (deleted && !window.confirm('Delete this map leg?')) { return; }
  var body = Object.assign({}, legEditor.draft, {revision: mapLegEdits.revision, deleted: !!deleted});
  if (!deleted) { body.name = namedRoadLeg(body); }
  legEditor.saving = true; syncLegEditor(); legMessage('Saving...');
  try {
    mapLegEdits = await postJson('/api/map-route-leg', body);
    applyMapLegEdits(); updateRouteSelection();
    clearPlannedRoute();
    legEditor.saving = false; legEditor.dirty = false;
    if (deleted) { discardLegDraft(); }
    else { legEditor.draft.name = body.name; legEditor.creating = false; legEditor.undo = []; legEditor.redo = []; }
    legMessage(deleted ? 'Leg deleted' : 'Leg saved');
  } catch (error) { legMessage(error.message); }
  finally { legEditor.saving = false; syncLegEditor(); invalidate(); }
}

async function setLegEditing(enabled) {
  if (!enabled && !await discardLegDraft()) { syncLegEditor(); return; }
  legEditor.enabled = enabled; syncLegEditor(); invalidate();
}

function legDailyMiles(kind) {
  var rates = state.map && state.map.travelMilesPerDay;
  var rate = Number(rates && rates[kind]);
  return Number.isFinite(rate) && rate > 0 ? rate : 0;
}

function dailyTravelPath(points, segmentMiles) {
  if (!Number.isFinite(segmentMiles) || segmentMiles <= 0) { throw new Error('No daily travel rate for this leg type.'); }
  if (!points.length) { return []; }
  var travelled = 0, nextStop = segmentMiles;
  var result = [points[0].slice()];
  for (var index = 1; index < points.length; index++) {
    var start = points[index - 1], end = points[index];
    var distance = Math.hypot(end[0] - start[0], end[1] - start[1]);
    var endDistance = travelled + distance;
    for (; nextStop < endDistance - 1e-8; nextStop += segmentMiles) {
      if (result.length >= 9999) { throw new Error('Subdivision exceeds the 10000-waypoint limit.'); }
      var miles = nextStop - travelled;
      result.push([start[0] + (end[0] - start[0]) * miles / distance,
                   start[1] + (end[1] - start[1]) * miles / distance]);
    }
    if (distance > 0) {
      if (result.length >= 10000) { throw new Error('Subdivision exceeds the 10000-waypoint limit.'); }
      result.push(end.slice());
    }
    if (Math.abs(nextStop - endDistance) < 1e-8) { nextStop += segmentMiles; }
    travelled = endDistance;
  }
  return result;
}

function dailyTravelGeometry(points, segmentMiles, junctions) {
  var path = dailyTravelPath(points, segmentMiles), handles = [], indices = [], distance = 0;
  path.forEach(function (point, index) {
    if (index) { distance += Math.hypot(point[0] - path[index - 1][0], point[1] - path[index - 1][1]); }
    var daily = Math.abs(distance - Math.round(distance / segmentMiles) * segmentMiles) < 1e-7;
    var junction = (junctions || []).some(function (anchor) { return Math.hypot(point[0] - anchor[0], point[1] - anchor[1]) < 0.001; });
    if (!index || index === path.length - 1 || daily || junction) { handles.push(point.slice()); indices.push(index); }
  });
  return {points: handles, path: path, pointIndices: indices};
}

function curvedLegGeometry(points, amount, waterOnly) {
  if (points.length < 2) { throw new Error('Select a leg with at least two waypoints.'); }
  var path = [points[0].slice()], indices = [0];
  amount = Math.max(0, Math.min(1, Number(amount) || 0));
  function waterCell(point) {
    return [(point[0] - mesh.bounds[0]) / mesh.cellW - 0.5,
      (point[1] - mesh.bounds[1]) / mesh.cellH - 0.5];
  }
  for (var index = 1; index < points.length; index++) {
    var start = points[index - 1], end = points[index];
    var previous = points[Math.max(0, index - 2)], next = points[Math.min(points.length - 1, index + 1)];
    var length = Math.hypot(end[0] - start[0], end[1] - start[1]);
    var beforeLength = Math.hypot(end[0] - previous[0], end[1] - previous[1]) || 1;
    var afterLength = Math.hypot(next[0] - start[0], next[1] - start[1]) || 1;
    var steps = Math.max(8, Math.ceil(length / 2));
    if (path.length + steps > 10000) { throw new Error('Curve exceeds the 10000-vertex limit.'); }
    var segment = [start.slice()];
    for (var sample = 1; sample < steps; sample++) {
      var progress = sample / steps, inverse = 1 - progress;
      var firstWeight = 3 * inverse * inverse * progress;
      var secondWeight = 3 * inverse * progress * progress;
      segment.push([0, 1].map(function (axis) {
        var first = start[axis] + (end[axis] - previous[axis]) / beforeLength * length * amount / 3;
        var second = end[axis] - (next[axis] - start[axis]) / afterLength * length * amount / 3;
        return inverse * inverse * inverse * start[axis] + firstWeight * first +
          secondWeight * second + progress * progress * progress * end[axis];
      }));
    }
    segment.push(end.slice());
    var clear = !waterOnly || segment.slice(1).every(function (point, offset) {
      return fractionalWaterSegmentIsClear(waterCell(segment[offset]), waterCell(point));
    });
    if (clear) { path.push.apply(path, segment.slice(1)); }
    else { path.push(end.slice()); }
    indices.push(path.length - 1);
  }
  return {points: points.map(function (point) { return point.slice(); }), path: path, pointIndices: indices};
}

function coastalLegGeometry(points, amount) {
  var first = points[0], last = points[points.length - 1];
  var route = routedWaterPath(first[0], first[1], last[0], last[1], 15);
  if (!route || !route.length) { throw new Error('No connected water route found. Draft unchanged.'); }
  if (Math.hypot(route[0][0] - first[0], route[0][1] - first[1]) > 15 ||
      Math.hypot(route[route.length - 1][0] - last[0], route[route.length - 1][1] - last[1]) > 15) {
    throw new Error('Sea leg endpoints must be within 15 miles of mapped water. Draft unchanged.');
  }
  if (Math.hypot(route[0][0] - first[0], route[0][1] - first[1]) > 1e-8) { route.unshift(first.slice()); }
  else { route[0] = first.slice(); }
  if (Math.hypot(route[route.length - 1][0] - last[0], route[route.length - 1][1] - last[1]) > 1e-8) { route.push(last.slice()); }
  else { route[route.length - 1] = last.slice(); }
  return curvedLegGeometry(route, amount, true);
}

function reshapeLeg(coastal) {
  var draft = legEditor.draft;
  if (!draft || draft.points.length < 2 || legEditor.saving || (coastal && draft.kind !== 'sea')) { return; }
  try {
    var amount = Number(document.getElementById('leg-curvature').value) / 100;
    var geometry = coastal ? coastalLegGeometry(draft.points, amount)
      : curvedLegGeometry(draft.points, amount, draft.kind === 'sea');
    rememberLeg(); Object.assign(draft, geometry); legEditor.point = -1;
    legEditor.snapTarget = null; syncLegEditor(); invalidate();
    legMessage(coastal ? 'Coastal draft targets approximately 15 miles offshore; ports and narrow channels may be closer. Save leg to keep changes.'
      : 'Curved draft ready. Waypoints preserved. Save leg to keep changes.');
  } catch (error) { legMessage(error.message); }
}

function insertLegWaypoint(draft, position, point, pathIndex) {
  if (draft.path) {
    if (pathIndex === undefined) { pathIndex = position >= draft.points.length ? draft.path.length : draft.pointIndices[position - 1] + 1; }
    draft.path.splice(pathIndex, 0, point.slice());
    draft.pointIndices = draft.pointIndices.map(function (index) { return index >= pathIndex ? index + 1 : index; });
    draft.pointIndices.splice(position, 0, pathIndex);
  }
  draft.points.splice(position, 0, point);
}

function moveLegWaypoint(draft, index, point) {
  draft.points[index] = point;
  if (draft.path) { draft.path[draft.pointIndices[index]] = point.slice(); }
}

function removeLegWaypoint(draft, index) {
  if (draft.path) {
    if (index === 0) {
      var cut = draft.pointIndices[1]; draft.path = draft.path.slice(cut);
      draft.pointIndices = draft.pointIndices.map(function (value) { return value - cut; });
    } else if (index === draft.points.length - 1) { draft.path = draft.path.slice(0, draft.pointIndices[index - 1] + 1); }
    draft.pointIndices.splice(index, 1);
  }
  draft.points.splice(index, 1);
}

function suggestedJunctionName(identifiers, point) {
  var roads = identifiers.map(function (identifier) { return mapLegEdits.legs[identifier]; })
    .filter(function (leg) { return leg && !leg.deleted; });
  function throughRoad(leg) {
    return leg.points.slice(1, -1).some(function (waypoint) {
      return Math.hypot(point[0] - waypoint[0], point[1] - waypoint[1]) < 0.001;
    }) ? 1 : 0;
  }
  roads.sort(function (left, right) { return throughRoad(right) - throughRoad(left); });
  var names = [];
  roads.forEach(function (leg) {
    var name = leg.name.replace(/ [(]part [12][)]$/, '').replace(/: .* to .*$/, '').trim();
    if (name && !names.some(function (existing) { return existing.toLowerCase() === name.toLowerCase(); })) { names.push(name); }
  });
  return names.join('/') + ' Junction';
}

function straightenLeg() {
  var draft = legEditor.draft;
  if (!draft || !draft.path || legEditor.saving) { return; }
  rememberLeg();
  delete draft.path;
  delete draft.pointIndices;
  legEditor.snapTarget = null;
  syncLegEditor(); invalidate();
}

function syncPlanarLegFilter() {
  var selected = state.planarLegTypes;
  document.getElementById('planar-leg-all').checked = !selected.length;
  var labels = [];
  document.querySelectorAll('input[name="planar-leg-type"]').forEach(function (input) {
    input.checked = selected.includes(input.value);
    if (input.checked) { labels.push(input.parentElement.textContent.trim()); }
  });
  document.getElementById('planar-leg-summary').textContent = labels.join(', ') || 'All types';
}

function wireLegEditor() {
  syncLegEditor();
  document.getElementById('leg-split').addEventListener('click', async function () {
    var draft = legEditor.draft;
    if (!draft || legEditor.saving || legEditor.point <= 0 || legEditor.point >= draft.points.length - 1) { return; }
    if (!window.confirm('Save this draft as two separate legs at the selected waypoint? This replaces the original leg.')) { return; }
    legEditor.saving = true; syncLegEditor();
    try {
      mapLegEdits = await postJson('/api/map-route-leg', Object.assign({}, draft, {
        revision: mapLegEdits.revision, split_index: legEditor.point
      }));
      applyMapLegEdits(); updateRouteSelection(); clearPlannedRoute();
      legEditor.saving = false; legEditor.dirty = false; discardLegDraft();
      legMessage('Saved two legs. Select either leg to edit or rename it.');
    } catch (error) { legMessage(error.message); }
    finally { legEditor.saving = false; syncLegEditor(); invalidate(); }
  });
  document.getElementById('leg-junction').addEventListener('click', async function () {
    if (!legEditor.draft || legEditor.point < 0 || legEditor.saving ||
        !['road', 'trail', 'track'].includes(legEditor.draft.kind)) { return; }
    if (legEditor.dirty || !mapLegEdits.legs[legEditor.draft.id]) {
      await saveLegDraft(false);
      if (legEditor.dirty || !mapLegEdits.legs[legEditor.draft.id]) { return; }
    }
    var point = legEditor.draft.points[legEditor.point];
    var shared = Object.keys(mapLegEdits.legs).filter(function (identifier) {
      var leg = mapLegEdits.legs[identifier];
      return !leg.deleted && ['road', 'trail', 'track'].includes(leg.kind) && leg.points.some(function (waypoint) {
        return Math.hypot(point[0] - waypoint[0], point[1] - waypoint[1]) < 0.001;
      });
    });
    if (!shared.length) { legMessage('Save a road or trail waypoint before converting it.'); return; }
    legEditor.saving = true; syncLegEditor();
    try {
      var existingId = Object.keys(mapLegEdits.junctions || {}).find(function (identifier) {
        var junction = mapLegEdits.junctions[identifier];
        return Math.hypot(point[0] - junction.point[0], point[1] - junction.point[1]) < 0.001;
      });
      mapLegEdits = await postJson('/api/map-junction', {id: existingId, point: point, legs: shared, revision: mapLegEdits.revision});
      applyMapLegEdits();
      if (mapLegEdits.legs[legEditor.draft.id]) { legEditor.draft.name = mapLegEdits.legs[legEditor.draft.id].name; }
      syncJunctionLocations();
      clearPlannedRoute(); legMessage('Junction saved');
    } catch (error) { legMessage(error.message); }
    finally { legEditor.saving = false; syncLegEditor(); invalidate(); }
  });
  var legFilter = document.getElementById('planar-leg-type');
  Array.from(document.getElementById('leg-kind').options).forEach(function (option) {
    var label = document.createElement('label');
    var input = document.createElement('input');
    input.type = 'checkbox'; input.name = 'planar-leg-type'; input.value = option.value;
    label.appendChild(input); label.appendChild(document.createTextNode(' ' + option.textContent));
    document.getElementById('planar-leg-options').appendChild(label);
  });
  syncPlanarLegFilter();
  legFilter.addEventListener('change', async function (event) {
    if (legEditor.draft && !await discardLegDraft()) { syncPlanarLegFilter(); return; }
    state.planarLegTypes = event.target.id === 'planar-leg-all' ? [] :
      Array.from(document.querySelectorAll('input[name="planar-leg-type"]:checked')).map(function (input) { return input.value; });
    syncPlanarLegFilter();
    state.selectedRoute = -1; legEditor.snapTarget = null;
    clearPlannedRoute(); updateRouteSelection(); invalidate();
  });
  getJson('/api/map-route-legs').then(function (payload) {
    mapLegEdits = payload; legEditor.ready = true;
    syncJunctionLocations();
    if (baseRouteLines.length) { applyMapLegEdits(); }
    syncLegEditor(); invalidate();
  }).catch(function (error) { legMessage('Route edits unavailable: ' + error.message); });
  document.getElementById('leg-edit-enabled').addEventListener('change', function (event) {
    setLegEditing(event.target.checked);
  });
  document.getElementById('leg-straighten').addEventListener('click', straightenLeg);
  document.getElementById('leg-curve').addEventListener('click', function () { reshapeLeg(false); });
  document.getElementById('leg-coast').addEventListener('click', function () { reshapeLeg(true); });
  document.getElementById('leg-smooth').addEventListener('click', function () {
    if (!legEditor.draft || legEditor.saving) { return; }
    try {
      var dailyMiles = legDailyMiles(legEditor.draft.kind);
      var junctions = Object.values(mapLegEdits.junctions || {}).map(function (junction) { return junction.point; });
      var geometry = dailyTravelGeometry(legEditor.draft.path || legEditor.draft.points, dailyMiles, junctions);
      rememberLeg(); Object.assign(legEditor.draft, geometry); legEditor.point = -1;
      legEditor.snapTarget = null; syncLegEditor(); invalidate();
      legMessage('Replaced old points with daily stops every ' + dailyMiles + ' miles. Original path, endpoints and junctions preserved. Save leg to keep changes.');
    } catch (error) { legMessage(error.message); }
  });
  document.getElementById('leg-new').addEventListener('click', async function () {
    if (!await discardLegDraft()) { return; }
    legEditor.draft = {id: 'custom:' + crypto.randomUUID(), name: 'New leg', kind: 'road', points: []};
    legEditor.creating = true; legEditor.dirty = true;
    legMessage(''); syncLegEditor(); invalidate(); document.getElementById('leg-name').focus();
  });
  ['name', 'kind'].forEach(function (field) {
    document.getElementById('leg-' + field).addEventListener(field === 'name' ? 'input' : 'change', function (event) {
      if (!legEditor.draft || legEditor.saving) { return; }
      rememberLeg(); legEditor.draft[field] = event.target.value; syncLegEditor(); invalidate();
    });
  });
  document.getElementById('leg-insert').addEventListener('click', function () {
    legEditor.insert = !legEditor.insert; legEditor.add = false; syncLegEditor();
  });
  document.getElementById('leg-add-point').addEventListener('click', function () {
    legEditor.add = !legEditor.add; legEditor.insert = false; syncLegEditor();
  });
  document.getElementById('leg-snap').addEventListener('change', function () {
    legEditor.snapTarget = null; legMessage(''); invalidate();
  });
  document.getElementById('leg-remove-point').addEventListener('click', function () {
    if (!legEditor.draft || legEditor.point < 0 || legEditor.draft.points.length <= 2) { return; }
    rememberLeg(); removeLegWaypoint(legEditor.draft, legEditor.point); legEditor.point = -1;
    syncLegEditor(); invalidate();
  });
  document.getElementById('leg-undo').addEventListener('click', function () { legHistory(true); });
  document.getElementById('leg-redo').addEventListener('click', function () { legHistory(false); });
  document.getElementById('leg-save').addEventListener('click', function () { saveLegDraft(false); });
  document.getElementById('leg-delete').addEventListener('click', function () { saveLegDraft(true); });
  document.getElementById('leg-cancel').addEventListener('click', async function () { if (await discardLegDraft()) { legMessage(''); } });
  window.addEventListener('beforeunload', function (event) {
    if (legEditor.dirty || legEditor.saving) { event.preventDefault(); event.returnValue = ''; }
  });
}

function planarLegVisible(line) {
  return !state.planarLegTypes.length || state.planarLegTypes.includes(line.kind);
}

function strokePlanarLeg(color, width, dash, widthScale) {
  var zoom = 200 / state.planarRadius;
  var strokeScale = zoom * (widthScale == null ? 1 : widthScale);
  ctx.lineCap = 'round'; ctx.lineJoin = 'round';
  ctx.setLineDash(dash.map(function (length) { return length * zoom; }));
  ctx.lineWidth = (width + 4) * strokeScale; ctx.strokeStyle = '#202b30'; ctx.stroke();
  ctx.lineWidth = (width + 2) * strokeScale; ctx.strokeStyle = '#ffffff'; ctx.stroke();
  ctx.lineWidth = width * strokeScale; ctx.strokeStyle = color; ctx.stroke();
}

function drawPlanarLegs() {
  ctx.save();
  var draft = legEditor.enabled && legEditor.draft;
  ctx.save();
  if (draft || (!legEditor.enabled && state.planRoute && state.planRoute.mapRoads)) { ctx.globalAlpha *= 0.2; }
  routeLines.forEach(function (line) {
    if (!line.sourcePoints || !planarLegVisible(line)) { return; }
    if (legEditor.enabled && legEditor.draft && line.editId === legEditor.draft.id) { return; }
    ctx.beginPath();
    line.sourcePoints.forEach(function (point, index) {
      var screen = planarPoint(point[0], point[1]);
      if (!index) { ctx.moveTo(screen[0], screen[1]); } else { ctx.lineTo(screen[0], screen[1]); }
    });
    strokePlanarLeg(routeDisplayColor(line), state.selectedRoute >= 0 && routeLines[state.selectedRoute] === line ? 6 : 4, routeLineDash(line), line.kind === 'trail' ? 0.5 : 1);
    if (legEditor.enabled) {
      ctx.setLineDash([]); ctx.lineWidth = 1; ctx.fillStyle = '#ffffff';
      (line.waypoints || line.sourcePoints).forEach(function (point) {
        var screen = planarPoint(point[0], point[1]);
        if (screen[0] < 0 || screen[1] < 0 || screen[0] > cam.cx * 2 || screen[1] > cam.cy * 2) { return; }
        ctx.beginPath(); ctx.arc(screen[0], screen[1], 3, 0, Math.PI * 2); ctx.fill(); ctx.stroke();
      });
    }
    if (state.routeIcons && !legEditor.enabled) {
      var middle = line.sourcePoints[Math.floor(line.sourcePoints.length / 2)];
      var icon = planarPoint(middle[0], middle[1]);
      if (icon[0] >= 0 && icon[0] <= cam.cx * 2 && icon[1] >= 0 && icon[1] <= cam.cy * 2) {
        drawRouteIcon(icon[0], icon[1], line, false);
      }
    }
  });
  ctx.restore();
  if (draft) {
    ctx.setLineDash([]); ctx.strokeStyle = '#007c91'; ctx.lineWidth = 3;
    ctx.beginPath();
    (draft.path || draft.points).forEach(function (point, index) {
      var screen = planarPoint(point[0], point[1]);
      if (!index) { ctx.moveTo(screen[0], screen[1]); } else { ctx.lineTo(screen[0], screen[1]); }
    });
    strokePlanarLeg('#007c91', 5, []);
    ctx.strokeStyle = '#007c91'; ctx.lineWidth = 3;
    ctx.font = '12px sans-serif'; ctx.textBaseline = 'bottom'; ctx.textAlign = 'left';
    draft.points.forEach(function (point, index) {
      var screen = planarPoint(point[0], point[1]);
      if (screen[0] < -10 || screen[1] < -10 || screen[0] > cam.cx * 2 + 10 || screen[1] > cam.cy * 2 + 10) { return; }
      ctx.beginPath(); ctx.arc(screen[0], screen[1], 6, 0, Math.PI * 2);
      ctx.fillStyle = index === legEditor.point ? '#ffcd44' : '#ffffff'; ctx.fill(); ctx.stroke();
      ctx.strokeStyle = '#ffffff'; ctx.lineWidth = 3; ctx.strokeText(String(index + 1), screen[0] + 9, screen[1] - 6);
      ctx.fillStyle = '#12343c'; ctx.fillText(String(index + 1), screen[0] + 9, screen[1] - 6);
      ctx.strokeStyle = '#007c91'; ctx.lineWidth = 3;
    });
  }
  if (legEditor.enabled && legEditor.snapTarget) {
    var snap = planarPoint(legEditor.snapTarget.point[0], legEditor.snapTarget.point[1]);
    ctx.beginPath(); ctx.arc(snap[0], snap[1], 11, 0, Math.PI * 2);
    ctx.setLineDash([]); ctx.strokeStyle = '#00834d'; ctx.lineWidth = 3; ctx.stroke();
  }
  ctx.restore();
}

function drawMapJunctions() {
  var labelScale = mapLabelScale();
  ctx.save(); ctx.setLineDash([]); ctx.font = mapLabelFont(12, true); ctx.textAlign = 'left'; ctx.textBaseline = 'middle';
  Object.entries(mapLegEdits.junctions || {}).forEach(function (entry) {
    var identifier = entry[0], junction = entry[1];
    var point = planarPoint(junction.point[0], junction.point[1]);
    if (point[0] < -100 || point[0] > cam.cx * 2 + 100 || point[1] < -20 || point[1] > cam.cy * 2 + 20) { return; }
    ctx.fillStyle = '#ffcd44'; ctx.strokeStyle = '#163a45'; ctx.lineWidth = 3;
    var radius = 2.5 * planarScale() * (plannedLocation(junction.name) ? 2 : 1);
    if (plannedLocation(junction.name)) { drawRoutePulse(point[0], point[1], radius); }
    ctx.beginPath(); ctx.arc(point[0], point[1], radius, 0, Math.PI * 2);
    ctx.fill(); ctx.stroke();
    if (state.junctionLabels === 'hide') { return; }
    if (state.junctionLabels !== 'show' && !state.showAllLocationLabels &&
        state.selected !== 'junction:' + identifier) { return; }
    ctx.strokeStyle = '#ffffff'; ctx.lineWidth = 4 * labelScale;
    ctx.strokeText(junction.name, point[0] + 10 * labelScale, point[1] - 10 * labelScale);
    ctx.fillStyle = '#163a45'; ctx.fillText(junction.name, point[0] + 10 * labelScale, point[1] - 10 * labelScale);
  });
  ctx.restore();
}

function planarDistanceRuler(scale, availableWidth) {
  var target = Math.min(160, Math.max(1, availableWidth - 48));
  var maximum = target / scale;
  var magnitude = Math.pow(10, Math.floor(Math.log10(maximum)));
  var units = maximum / magnitude;
  var miles = (units >= 5 ? 5 : units >= 2 ? 2 : 1) * magnitude;
  return {pixels: miles * scale, miles: miles};
}

function drawPlanarRuler() {
  var ruler = planarDistanceRuler(planarScale(), cam.cx * 2);
  var left = 24, bottom = cam.cy * 2 - 24;
  ctx.save(); ctx.setLineDash([]);
  ctx.fillStyle = 'rgba(255,255,255,0.94)';
  ctx.fillRect(left - 10, bottom - 34, ruler.pixels + 20, 46);
  ctx.strokeStyle = '#163a45'; ctx.lineWidth = 2;
  var segmentWidth = ruler.pixels / 4;
  for (var segment = 0; segment < 4; segment++) {
    ctx.fillStyle = segment % 2 === 0 ? '#163a45' : '#ffffff';
    ctx.fillRect(left + segment * segmentWidth, bottom - 6, segmentWidth, 6);
  }
  ctx.strokeRect(left, bottom - 6, ruler.pixels, 6);
  ctx.beginPath();
  for (var tick = 0; tick <= 4; tick++) {
    var tickX = left + tick * segmentWidth;
    ctx.moveTo(tickX, bottom); ctx.lineTo(tickX, bottom - 9);
  }
  ctx.stroke();
  ctx.font = '12px sans-serif'; ctx.textBaseline = 'bottom'; ctx.fillStyle = '#163a45';
  ctx.textAlign = 'left'; ctx.fillText('0', left, bottom - 10);
  ctx.textAlign = 'center'; ctx.fillText(Number((ruler.miles / 2).toPrecision(6)), left + ruler.pixels / 2, bottom - 10);
  ctx.textAlign = 'right'; ctx.fillText(Number(ruler.miles.toPrecision(6)) + ' mi', left + ruler.pixels, bottom - 10);
  ctx.restore();
}

function drawPlanarItinerary() {
  if (!state.planRoute || !state.planRoute.mapRoads || legEditor.enabled) { return; }
  ctx.save(); ctx.setLineDash([]); ctx.lineCap = 'round'; ctx.lineJoin = 'round';
  var width = Math.max(4, 8 * 200 / state.planarRadius);
  state.planRoute.legs.forEach(function (leg) {
    if (!leg.points || leg.points.length < 2) { return; }
    ctx.beginPath();
    leg.points.forEach(function (point, index) {
      var screen = planarPoint(point[0], point[1]);
      if (!index) { ctx.moveTo(screen[0], screen[1]); } else { ctx.lineTo(screen[0], screen[1]); }
    });
    ctx.setLineDash([]);
    ctx.lineWidth = width + 5; ctx.strokeStyle = '#202b30'; ctx.stroke();
    ctx.lineWidth = width + 3; ctx.strokeStyle = '#ffffff'; ctx.stroke();
    ctx.lineWidth = width; ctx.strokeStyle = '#d62f39'; ctx.stroke();
    if (routeAnimationActive()) {
      ctx.setLineDash([10, 18]); ctx.lineDashOffset = -performance.now() / 45;
      ctx.lineWidth = width / 2; ctx.strokeStyle = '#ffffff'; ctx.stroke();
    }
  });
  ctx.restore();
}

function drawPlanarFineTerrain(left, top, right, bottom) {
  var origin = state.map.settlements.find(function (place) { return place.id === 'waterdeep'; });
  if (!origin) { return; }
  var scale = planarScale();
  var epoch = planarTileEpoch;
  var firstColumn = Math.floor((left - origin.x) / 200);
  var lastColumn = Math.floor((right - origin.x) / 200);
  var firstRow = Math.floor((origin.y - bottom) / 200);
  var lastRow = Math.floor((origin.y - top) / 200);
  function requestTile(column, row, key) {
    planarTilesLoading++;
    planarTiles.set(key, {loading: true});
    getJson('/api/planar-terrain?column=' + column + '&row=' + row).then(function (tile) {
      if (epoch !== planarTileEpoch) { return; }
      if (tile.grid[0] && tile.grid[1]) {
        var surface = document.createElement('canvas');
        surface.width = tile.grid[0]; surface.height = tile.grid[1];
        var context = surface.getContext('2d');
        var pixels = context.createImageData(surface.width, surface.height);
        for (var index = 0; index < tile.terrain.length; index++) {
          var color = PALETTE[tile.terrain[index]];
          if (!color) { continue; }
          pixels.data[index * 4] = color[0];
          pixels.data[index * 4 + 1] = color[1];
          pixels.data[index * 4 + 2] = color[2];
          pixels.data[index * 4 + 3] = 255;
        }
        context.putImageData(pixels, 0, 0);
        tile.surface = surface;
      }
      planarTiles.set(key, tile);
      if (planarTiles.size > 96) { planarTiles.delete(planarTiles.keys().next().value); }
    }).catch(function (err) {
      if (epoch !== planarTileEpoch) { return; }
      planarTiles.set(key, {failed: true});
      showStatus('One-mile terrain unavailable: ' + err.message, true);
    }).finally(function () { planarTilesLoading--; invalidate(); });
  }
  ctx.save();
  ctx.imageSmoothingEnabled = false;
  for (var row = firstRow; row <= lastRow; row++) {
    for (var column = firstColumn; column <= lastColumn; column++) {
      var key = column + ',' + row;
      var tile = planarTiles.get(key);
      if (!tile && planarTilesLoading < 4) { requestTile(column, row, key); }
      if (!tile || !tile.surface) { continue; }
      var point = planarPoint(origin.x + tile.column, origin.y - tile.row - 1);
      ctx.drawImage(tile.surface, point[0], point[1], tile.grid[0] * scale, tile.grid[1] * scale);
    }
  }
  ctx.restore();
}

function drawPlanarBoundaries(firstColumn, lastColumn, firstRow, lastRow) {
  if (!state.planarBoundaries) { return; }
  var origin = state.map.settlements.find(function (place) { return place.id === 'waterdeep'; });
  var source = origin && state.map.sourceBoundaries;
  var sourceBounds = source ? [origin.x + source.bounds[0], origin.y - source.bounds[3],
    origin.x + source.bounds[1], origin.y - source.bounds[2]] : null;
  function group(code) {
    if (code === 'o' || code === 'w') { return 'water'; }
    if (code === 'f' || code === 'j' || code === 'T') { return 'forest'; }
    return code === 'm' ? 'mountain' : '';
  }
  var paths = {water: [], forest: [], mountain: []};
  function edge(first, second, startX, startY, endX, endY) {
    if (first === second) { return; }
    var kind = first === 'water' || second === 'water' ? 'water' :
      first === 'mountain' || second === 'mountain' ? 'mountain' : 'forest';
    if (!first && !second) { return; }
    if (sourceBounds) {
      var middleX = (startX + endX) / 2, middleY = (startY + endY) / 2;
      if (middleX >= sourceBounds[0] && middleX <= sourceBounds[2] &&
          middleY >= sourceBounds[1] && middleY <= sourceBounds[3]) { return; }
    }
    paths[kind].push([startX, startY, endX, endY]);
  }
  var bounds = mesh.bounds;
  for (var row = firstRow; row < lastRow; row++) {
    for (var column = firstColumn; column < lastColumn; column++) {
      var index = row * mesh.W + column;
      var current = group(terrainCodeAt(index));
      var west = bounds[0] + column * mesh.cellW;
      var north = bounds[1] + row * mesh.cellH;
      if (column + 1 < mesh.W) {
        edge(current, group(terrainCodeAt(index + 1)), west + mesh.cellW, north, west + mesh.cellW, north + mesh.cellH);
      }
      if (row + 1 < mesh.H) {
        edge(current, group(terrainCodeAt(index + mesh.W)), west, north + mesh.cellH, west + mesh.cellW, north + mesh.cellH);
      }
    }
  }
  if (source) {
    Object.keys(paths).forEach(function (kind) {
      (source.segments[kind] || []).forEach(function (line) {
        paths[kind].push([origin.x + line[0], origin.y - line[1], origin.x + line[2], origin.y - line[3]]);
      });
    });
  }
  ctx.save();
  ctx.globalAlpha = 1;
  var colors = {water: '#007bbd', forest: '#146d32', mountain: '#a31879'};
  Object.keys(paths).forEach(function (kind) {
    ctx.beginPath();
    paths[kind].forEach(function (line) {
      var start = planarPoint(line[0], line[1]), end = planarPoint(line[2], line[3]);
      ctx.moveTo(start[0], start[1]); ctx.lineTo(end[0], end[1]);
    });
    ctx.strokeStyle = '#ffffff'; ctx.lineWidth = 3.5; ctx.stroke();
    ctx.strokeStyle = colors[kind]; ctx.lineWidth = 1.7; ctx.stroke();
  });
  if (origin) {
    (state.map.boundaryRegions || []).forEach(function (region) {
      if (source && (source.supersedes || []).indexOf(region.id) >= 0) { return; }
      ctx.beginPath();
      region.polygon.forEach(function (point, index) {
        var screen = planarPoint(origin.x + point[0], origin.y - point[1]);
        if (!index) { ctx.moveTo(screen[0], screen[1]); } else { ctx.lineTo(screen[0], screen[1]); }
      });
      ctx.closePath();
      ctx.setLineDash([7, 4]);
      ctx.strokeStyle = '#ffffff'; ctx.lineWidth = 5; ctx.stroke();
      ctx.strokeStyle = region.terrain === 'M' ? colors.mountain : region.terrain === 'H' ? '#995015' : colors.forest;
      ctx.lineWidth = 2.5; ctx.stroke();
      ctx.setLineDash([]);
      var label = planarPoint(origin.x + region.bounds[0], origin.y - region.bounds[3]);
      ctx.font = '12px sans-serif'; ctx.lineWidth = 3; ctx.strokeStyle = '#ffffff';
      ctx.strokeText(region.name, label[0], label[1] - 5);
      ctx.fillStyle = '#162a20'; ctx.fillText(region.name, label[0], label[1] - 5);
    });
  }
  ctx.restore();
}

function drawPlanar() {
  drawSky();
  var scale = planarScale();
  ctx.save();
  if (state.under && state.under.width && state.under.height) {
    var posterCorner = planarPoint(state.underX, state.underY);
    ctx.beginPath();
    ctx.rect(posterCorner[0], posterCorner[1],
      state.under.width * state.underMpp * scale,
      state.under.height * state.underMpp * state.underStretch * scale);
    ctx.clip();
  }
  var centerX = mesh.cx + state.tx * SCALE;
  var centerY = mesh.cy + state.tz * SCALE;
  var left = centerX - cam.cx / scale, right = centerX + cam.cx / scale;
  var top = centerY - cam.cy / scale, bottom = centerY + cam.cy / scale;
  var bounds = mesh.bounds;
  var firstColumn = Math.max(0, Math.floor((left - bounds[0]) / mesh.cellW));
  var lastColumn = Math.min(mesh.W, Math.ceil((right - bounds[0]) / mesh.cellW));
  var firstRow = Math.max(0, Math.floor((top - bounds[1]) / mesh.cellH));
  var lastRow = Math.min(mesh.H, Math.ceil((bottom - bounds[1]) / mesh.cellH));
  function paintLandTypes() {
    for (var row = firstRow; row < lastRow; row++) {
      for (var column = firstColumn; column < lastColumn; column++) {
        var point = planarPoint(bounds[0] + column * mesh.cellW, bounds[1] + row * mesh.cellH);
        var color = PALETTE[terrainCodeAt(row * mesh.W + column)];
        ctx.fillStyle = 'rgb(' + color.join(',') + ')';
        ctx.fillRect(point[0], point[1], mesh.cellW * scale, mesh.cellH * scale);
      }
    }
    if (state.planarLandDetail === 1) { drawPlanarFineTerrain(left, top, right, bottom); }
  }
  paintLandTypes();
  if (state.planarPoster && state.under) {
    var poster = planarPoint(state.underX, state.underY);
    ctx.save();
    ctx.globalAlpha = state.planarPosterAlpha;
    ctx.drawImage(state.under, poster[0], poster[1],
      state.under.width * state.underMpp * scale,
      state.under.height * state.underMpp * state.underStretch * scale);
    ctx.restore();
  }
  if (state.under && state.rasterLayers) {
    Object.values(state.rasterLayers).forEach(function (layer) {
      if (!layer.on || !layer.image || layer.alpha <= 0) { return; }
      var corner = planarPoint(state.underX, state.underY);
      ctx.save();
      ctx.globalAlpha = layer.alpha;
      ctx.drawImage(layer.image, corner[0], corner[1],
        state.under.width * state.underMpp * scale,
        state.under.height * state.underMpp * state.underStretch * scale);
      ctx.restore();
    });
  }
  if (state.planarTerrain && state.planarTerrainAlpha > 0) {
    ctx.save();
    ctx.globalAlpha = state.planarTerrainAlpha;
    paintLandTypes();
    ctx.restore();
  }
  drawPlanarGrid(left, top, right, bottom);
  drawPlanarBoundaries(firstColumn, lastColumn, firstRow, lastRow);
  if (legEditor.enabled) {
    drawPlaces(); drawPins(); drawMapJunctions();
  }
  if (state.routes || legEditor.enabled) { drawPlanarLegs(); }
  drawPlanarItinerary();
  if (!legEditor.enabled) {
    drawPlaces(); drawPins(); drawMapJunctions();
  }
  drawLocationDraft();
  ctx.restore();
  drawPlanarRuler();
}

function draw() {
  if (!mesh) { return; }
  if (MAP_VIEW === 'planar') { drawPlanar(); return; }
  updateCamera();
  updateViewWindow();
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
  if ((state.dirty || routeAnimationActive()) && !renderBroken) {
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

var locationEditor = {enabled: false, draft: null, placing: false, busy: false};
var PLACE_TYPES = {location: 'Location', city: 'City', village: 'Village', vale: 'Vale',
  town: 'Town', hamlet: 'Hamlet', fortress: 'Fortress',
  ruin: 'Ruins', site: 'Site', capital: 'Capital',
  temple: 'Temple', bridge: 'Bridge', crypt: 'Crypt', cave: 'Cave', mine: 'Mine',
  shrine: 'Shrine', landmark: 'Landmark', inn: 'Inn', campsite: 'Campsite',
  caravan_stop: 'Caravan Stop', trading_post: 'Trading Post'};
var LOCATION_LEGEND_ROWS = {city: 2493, port: 2536, fortress: 2580, ruin: 2623,
  site: 2667, capital: 2710, port_capital: 2754, temple: 2798, bridge: 2842};
var locationLegendIcons = {};
var locationLegendImage = null;

function locationType(item) {
  if (item.placeType === 'port') { return 'city'; }
  if (item.placeType === 'port_capital') { return 'capital'; }
  return item.placeType || (item.mapOnly ? 'location' : 'city');
}

function locationIsPort(item) {
  return typeof item.isPort === 'boolean' ? item.isPort :
    !!item.port || item.placeType === 'port' || item.placeType === 'port_capital';
}

function locationIconType(item) {
  var kind = locationType(item);
  return locationIsPort(item) && kind === 'city' ? 'port' :
    locationIsPort(item) && kind === 'capital' ? 'port_capital' : kind;
}

function drawLocationTypeIcon(item, x, y, radius) {
  var kind = locationIconType(item), row = LOCATION_LEGEND_ROWS[kind];
  var image = state.under;
  if (row == null || !image || !image.width || !image.height) { return; }
  if (locationLegendImage !== image) { locationLegendIcons = {}; locationLegendImage = image; }
  var icon = locationLegendIcons[kind];
  if (!icon) {
    icon = document.createElement('canvas'); icon.width = 60; icon.height = 32;
    var context = icon.getContext('2d', {willReadFrequently: true});
    context.drawImage(image, 4265 * image.width / 4763, row * image.height / 3185,
      60 * image.width / 4763, 32 * image.height / 3185, 0, 0, 60, 32);
    var pixels = context.getImageData(0, 0, 60, 32);
    var minX = 60, minY = 32, maxX = -1, maxY = -1;
    for (var index = 0; index < pixels.data.length; index += 4) {
      var darkness = Math.max(pixels.data[index], pixels.data[index + 1], pixels.data[index + 2]);
      pixels.data[index + 3] = Math.max(0, Math.min(255, (190 - darkness) * 3));
      pixels.data[index] = pixels.data[index + 1] = pixels.data[index + 2] = 0;
      if (pixels.data[index + 3] > 100) {
        var pixelX = (index / 4) % 60, pixelY = Math.floor(index / 240);
        minX = Math.min(minX, pixelX); maxX = Math.max(maxX, pixelX);
        minY = Math.min(minY, pixelY); maxY = Math.max(maxY, pixelY);
      }
    }
    context.putImageData(pixels, 0, 0);
    icon.inkBounds = maxX >= minX ? [minX, minY, maxX - minX + 1, maxY - minY + 1] : null;
    locationLegendIcons[kind] = icon;
  }
  var bounds = icon.inkBounds;
  if (!bounds) { return; }
  var size = radius * 1.4 / Math.max(bounds[2], bounds[3]);
  var width = bounds[2] * size, height = bounds[3] * size;
  ctx.save(); ctx.beginPath(); ctx.arc(x, y, radius * 0.82, 0, Math.PI * 2); ctx.clip();
  ctx.drawImage(icon, bounds[0], bounds[1], bounds[2], bounds[3], x - width / 2, y - height / 2, width, height);
  ctx.restore();
}

function nearestRoadsidePoint(screenX, screenY) {
  var best = null, distance = 18;
  routeLines.forEach(function (line) {
    if (!['road', 'track', 'trail'].includes(line.kind) || !planarLegVisible(line)) { return; }
    var saved = mapLegEdits.legs[line.editId];
    if (!saved || saved.deleted) { return; }
    var points = saved.path || saved.points;
    for (var index = 1; index < points.length; index++) {
      var start = planarPoint(points[index - 1][0], points[index - 1][1]);
      var end = planarPoint(points[index][0], points[index][1]);
      var deltaX = end[0] - start[0], deltaY = end[1] - start[1];
      var length = deltaX * deltaX + deltaY * deltaY;
      var fraction = length ? Math.max(0, Math.min(1,
        ((screenX - start[0]) * deltaX + (screenY - start[1]) * deltaY) / length)) : 0;
      var candidate = Math.hypot(screenX - start[0] - fraction * deltaX, screenY - start[1] - fraction * deltaY);
      if (candidate < distance) {
        distance = candidate;
        best = {roadLegId: line.editId, roadName: saved.name,
          x: points[index - 1][0] + fraction * (points[index][0] - points[index - 1][0]),
          y: points[index - 1][1] + fraction * (points[index][1] - points[index - 1][1])};
      }
    }
  });
  return best;
}

function drawLocationDraft() {
  var draft = locationEditor.draft;
  if (!locationEditor.enabled || !draft || !Number.isFinite(draft.x) || !Number.isFinite(draft.y)) { return; }
  var point = planarPoint(draft.x, draft.y);
  ctx.save(); ctx.setLineDash([4, 3]); ctx.strokeStyle = '#007c91'; ctx.lineWidth = 3;
  ctx.beginPath(); ctx.arc(point[0], point[1], 12, 0, Math.PI * 2); ctx.stroke(); ctx.restore();
}

function editableLocations() {
  if (!state.map) { return []; }
  return (state.map.settlements || []).concat(state.map.places || []).filter(function (item) { return !item.mobile; });
}

function locationVisible(item) {
  return !state.verifiedOnly || !!item.mobile || item.verified === true;
}

function syncLocationEditor() {
  var draft = locationEditor.draft;
  document.getElementById('location-edit-tools').hidden = !locationEditor.enabled;
  document.getElementById('location-edit-enabled').checked = locationEditor.enabled;
  ['new', 'waypoint', 'pick', 'name', 'x', 'y', 'acres', 'move', 'save', 'delete', 'cancel', 'type', 'port', 'portal', 'gryphon', 'verified', 'inhabited', 'notes', 'road'].forEach(function (name) {
    document.getElementById('location-edit-' + name).disabled = locationEditor.busy ||
      (!draft && !['new', 'waypoint', 'pick'].includes(name));
  });
  var custom = draft && (!draft.id || draft.mapOnly);
  ['inhabited', 'notes', 'road'].forEach(function (name) {
    document.getElementById('location-edit-' + name).disabled = locationEditor.busy || !custom;
  });
  document.getElementById('location-edit-type').value = draft ? locationType(draft) : 'location';
  document.getElementById('location-edit-verified').checked = !!(draft && draft.verified);
  document.getElementById('location-edit-port').checked = !!draft && locationIsPort(draft);
  document.getElementById('location-edit-portal').checked = !!(draft && draft.portalGate);
  document.getElementById('location-edit-gryphon').checked = !!(draft && draft.gryphonPort);
  document.getElementById('location-edit-inhabited').checked = !!(draft && draft.inhabited);
  document.getElementById('location-edit-notes').value = draft && draft.notes || '';
  document.getElementById('location-edit-acres').value = draft && draft.landAcres != null ? draft.landAcres : '';
  document.getElementById('location-edit-road').checked = !!(draft && (draft.attachRoad || draft.roadLegId));
  if (draft && (draft.attachRoad || draft.roadLegId)) {
    document.getElementById('location-edit-x').disabled = true;
    document.getElementById('location-edit-y').disabled = true;
    document.getElementById('location-edit-save').disabled = locationEditor.busy || !draft.roadLegId;
  }
  document.getElementById('location-edit-road-name').textContent = draft && draft.roadName || '';
  document.getElementById('location-edit-name').readOnly = !!(draft && draft.id && !draft.mapOnly);
  document.getElementById('location-edit-delete').disabled = locationEditor.busy || !draft || !draft.id;
  ['name', 'x', 'y'].forEach(function (name) {
    document.getElementById('location-edit-' + name).value = draft ? draft[name] : '';
  });
  document.getElementById('location-edit-move').setAttribute('aria-pressed', String(locationEditor.placing));
  document.getElementById('leg-edit-enabled').disabled = locationEditor.enabled || !legEditor.ready || legEditor.saving;
  document.getElementById('location-edit-enabled').disabled = locationEditor.busy;
}

function refreshLocationOptions() {
  var select = document.getElementById('location-edit-pick');
  select.replaceChildren(new Option('Choose location', ''));
  editableLocations().sort(function (left, right) { return left.name.localeCompare(right.name); }).forEach(function (item) {
    select.add(new Option(item.name, item.id));
  });
  var options = document.getElementById('location-options');
  options.replaceChildren();
  (state.map.settlements || []).forEach(function (item) { options.appendChild(new Option(item.name, item.name)); });
  syncJunctionLocations();
}

function locationEditorClick(screenX, screenY) {
  if (!locationEditor.enabled || locationEditor.busy) { return; }
  if (locationEditor.placing && locationEditor.draft) {
    if (locationEditor.draft.attachRoad || locationEditor.draft.roadLegId) {
      var roadside = nearestRoadsidePoint(screenX, screenY);
      if (!roadside) {
        document.getElementById('location-edit-status').textContent = 'Choose a point on a visible saved road, track or trail.';
        return;
      }
      Object.assign(locationEditor.draft, roadside);
      document.getElementById('location-edit-status').textContent = '';
    } else {
      var point = legWorldPoint(screenX, screenY);
      locationEditor.draft.x = Number(point[0].toFixed(4));
      locationEditor.draft.y = Number(point[1].toFixed(4));
    }
    locationEditor.placing = false;
  } else {
    var nearest = null, distance = 16;
    editableLocations().forEach(function (item) {
      if (!locationVisible(item)) { return; }
      var world = calibratedXY(item), screen = planarPoint(world[0], world[1]);
      var candidate = Math.hypot(screenX - screen[0], screenY - screen[1]);
      if (candidate < distance) { nearest = item; distance = candidate; }
    });
    if (nearest) {
      var position = calibratedXY(nearest);
      locationEditor.draft = Object.assign({}, nearest, {x: position[0], y: position[1]});
      document.getElementById('location-edit-pick').value = nearest.id;
    }
  }
  syncLocationEditor(); invalidate();
}

async function saveLocationDraft(deleted) {
  var draft = locationEditor.draft;
  if (!draft || locationEditor.busy) { return; }
  if (deleted && !window.confirm('Delete ' + draft.name + ' from the map? Catalog records and route legs are retained.')) { return; }
  var status = document.getElementById('location-edit-status');
  locationEditor.busy = true; syncLocationEditor(); status.textContent = 'Saving...';
  try {
    var result = await postJson('/api/map-location', {id: draft.id, name: draft.name,
      placeType: locationType(draft), isPort: locationIsPort(draft), verified: !!draft.verified, inhabited: draft.inhabited, notes: draft.notes, roadLegId: draft.roadLegId || null,
      portalGate: !!draft.portalGate, gryphonPort: !!draft.gryphonPort,
      landAcres: draft.landAcres,
      x: draft.x, y: draft.y, deleted: deleted, revision: state.map.locationRevision});
    Object.assign(state.map, {settlements: result.settlements, places: result.places, locationRevision: result.locationRevision});
    buildPins(result.settlements); buildPlaces(result.places); refreshLocationOptions();
    clearPlannedRoute();
    state.selected = null; state.market = null; state.hover = -1;
    document.getElementById('place-head').textContent = '';
    ['place-stats', 'place-notes', 'place-prices'].forEach(function (id) { document.getElementById(id).textContent = ''; });
    locationEditor.draft = null; locationEditor.placing = false;
    status.textContent = deleted ? 'Location deleted from map.' : 'Location saved.';
  } catch (error) { status.textContent = error.message; }
  finally { locationEditor.busy = false; syncLocationEditor(); invalidate(); }
}

function wireLocationEditor() {
  var filterLabel = document.createElement('label');
  filterLabel.innerHTML = '<input type="checkbox" id="locations-verified-only" checked> Verified locations only';
  document.querySelector('.map-controls').appendChild(filterLabel);
  document.getElementById('locations-verified-only').addEventListener('change', function (event) {
    state.verifiedOnly = event.target.checked;
    state.hover = -1; invalidate();
  });
  if (MAP_VIEW !== 'planar') { return; }
  var panel = document.createElement('section');
  panel.setAttribute('aria-label', 'Map location editor');
  panel.innerHTML = '<label><input type="checkbox" id="location-edit-enabled"> Edit locations</label>' +
    '<div id="location-edit-tools" hidden><label>Location <select id="location-edit-pick"></select></label>' +
    '<button type="button" id="location-edit-new" title="Add location" aria-label="Add location">+</button>' +
    '<button type="button" id="location-edit-waypoint" title="Add roadside waypoint" aria-label="Add roadside waypoint">&#8853;</button>' +
    '<label>Name <input id="location-edit-name" maxlength="160"></label>' +
    '<label>Place type <select id="location-edit-type">' + Object.keys(PLACE_TYPES).map(function (kind) {
      return '<option value="' + kind + '">' + PLACE_TYPES[kind] + '</option>';
    }).join('') + '</select></label>' +
    '<label><input type="checkbox" id="location-edit-verified"> Verified</label>' +
    '<label><input type="checkbox" id="location-edit-port"> Port</label>' +
    '<label><input type="checkbox" id="location-edit-portal"> Portal gate</label>' +
    '<label><input type="checkbox" id="location-edit-gryphon"> Gryphon port</label>' +
    '<label><input type="checkbox" id="location-edit-inhabited"> Inhabited</label>' +
    '<label>Notes <textarea id="location-edit-notes" maxlength="2000" rows="2"></textarea></label>' +
    '<label><input type="checkbox" id="location-edit-road"> On road</label><span id="location-edit-road-name"></span>' +
    '<label>East (mi) <input id="location-edit-x" type="number" step="any"></label>' +
    '<label>South (mi) <input id="location-edit-y" type="number" step="any"></label>' +
    '<label>Land area (acres) <input id="location-edit-acres" type="number" min="0.000001" step="any" placeholder="Unknown"></label>' +
    '<button type="button" id="location-edit-move" title="Place location at next map click" aria-label="Move location" aria-pressed="false">&#10021;</button>' +
    '<button type="button" id="location-edit-save">Save location</button>' +
    '<button type="button" id="location-edit-delete">Delete location</button>' +
    '<button type="button" id="location-edit-cancel">Cancel</button></div>' +
    '<p id="location-edit-status" role="status"></p>';
  document.querySelector('.map-controls').appendChild(panel);
  panel.style.maxWidth = '100%';
  panel.querySelectorAll('input:not([type="checkbox"]), select, textarea').forEach(function (input) {
    input.style.maxWidth = '100%'; input.style.boxSizing = 'border-box';
  });
  document.getElementById('location-edit-enabled').addEventListener('change', async function (event) {
    if (!state.map || !mesh) { event.target.checked = false; return; }
    if (event.target.checked) {
      await setLegEditing(false);
      if (legEditor.enabled) { event.target.checked = false; return; }
      setCalibMode(false);
    }
    locationEditor.enabled = event.target.checked;
    locationEditor.draft = null; locationEditor.placing = false;
    refreshLocationOptions(); syncLocationEditor(); invalidate();
  });
  document.getElementById('location-edit-pick').addEventListener('change', function (event) {
    var item = editableLocations().find(function (item) { return item.id === event.target.value; });
    var position = item && calibratedXY(item);
    locationEditor.draft = item ? Object.assign({}, item, {x: position[0], y: position[1]}) : null;
    locationEditor.placing = false; syncLocationEditor(); invalidate();
  });
  document.getElementById('location-edit-new').addEventListener('click', function () {
    locationEditor.draft = {name: '', x: mesh.cx + state.tx * SCALE, y: mesh.cy + state.tz * SCALE,
      mapOnly: true, placeType: 'location', isPort: false, verified: true, inhabited: false, notes: ''};
    locationEditor.placing = true; syncLocationEditor(); invalidate(); document.getElementById('location-edit-name').focus();
  });
  document.getElementById('location-edit-waypoint').addEventListener('click', function () {
    document.getElementById('location-edit-new').click();
    Object.assign(locationEditor.draft, {placeType: 'inn', inhabited: true, attachRoad: true});
    syncLocationEditor();
  });
  document.getElementById('location-edit-type').addEventListener('change', function (event) {
    if (locationEditor.draft) { locationEditor.draft.placeType = event.target.value; }
  });
  document.getElementById('location-edit-inhabited').addEventListener('change', function (event) {
    if (locationEditor.draft) { locationEditor.draft.inhabited = event.target.checked; }
  });
  document.getElementById('location-edit-verified').addEventListener('change', function (event) {
    if (locationEditor.draft) { locationEditor.draft.verified = event.target.checked; }
  });
  document.getElementById('location-edit-port').addEventListener('change', function (event) {
    if (locationEditor.draft) { locationEditor.draft.isPort = event.target.checked; }
  });
  document.getElementById('location-edit-portal').addEventListener('change', function (event) {
    if (locationEditor.draft) { locationEditor.draft.portalGate = event.target.checked; }
  });
  document.getElementById('location-edit-gryphon').addEventListener('change', function (event) {
    if (locationEditor.draft) { locationEditor.draft.gryphonPort = event.target.checked; }
  });
  document.getElementById('location-edit-notes').addEventListener('input', function (event) {
    if (locationEditor.draft) { locationEditor.draft.notes = event.target.value; }
  });
  document.getElementById('location-edit-acres').addEventListener('input', function (event) {
    if (locationEditor.draft) {
      locationEditor.draft.landAcres = event.target.value === '' ? null : event.target.valueAsNumber;
      invalidate();
    }
  });
  document.getElementById('location-edit-road').addEventListener('change', function (event) {
    if (!locationEditor.draft) { return; }
    locationEditor.draft.attachRoad = event.target.checked;
    locationEditor.draft.roadLegId = null; locationEditor.draft.roadName = '';
    locationEditor.placing = event.target.checked; syncLocationEditor(); invalidate();
  });
  ['name', 'x', 'y'].forEach(function (field) {
    document.getElementById('location-edit-' + field).addEventListener('input', function (event) {
      if (locationEditor.draft) { locationEditor.draft[field] = field === 'name' ? event.target.value : event.target.valueAsNumber; }
      invalidate();
    });
  });
  document.getElementById('location-edit-move').addEventListener('click', function () {
    locationEditor.placing = !locationEditor.placing; syncLocationEditor();
  });
  document.getElementById('location-edit-save').addEventListener('click', function () { saveLocationDraft(false); });
  document.getElementById('location-edit-delete').addEventListener('click', function () { saveLocationDraft(true); });
  document.getElementById('location-edit-cancel').addEventListener('click', function () {
    locationEditor.draft = null; locationEditor.placing = false; syncLocationEditor(); invalidate();
  });
  syncLocationEditor();
}

canvas.addEventListener('pointerdown', function (ev) {
  if (legPointerDown(ev)) { return; }
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
  if (legEditor.drag && legEditor.drag.pointer === ev.pointerId) {
    if (!legEditor.drag.remembered) { rememberLeg(); legEditor.drag.remembered = true; }
    var target = snappedLegPoint(ev.clientX - rect.left, ev.clientY - rect.top, ev.altKey);
    moveLegWaypoint(legEditor.draft, legEditor.point, target.point);
    legMessage(target.label ? 'Snapped to ' + target.label : '');
    syncLegEditor(); invalidate(); return;
  }
  if (MAP_VIEW === 'planar' && legEditor.enabled && legEditor.draft && !drag) {
    snappedLegPoint(ev.clientX - rect.left, ev.clientY - rect.top, ev.altKey);
    invalidate();
  }
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
  var dy = drag.y - ev.clientY;
  drag.x = ev.clientX;
  drag.y = ev.clientY;
  drag.moved += Math.abs(dx) + Math.abs(dy);
  beginInteract();
  if (MAP_VIEW === 'planar') {
    state.tx -= dx / (planarScale() * SCALE);
    state.tz += dy / (planarScale() * SCALE);
  } else if (state.globe) {
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
  if (legEditor.drag) { legEditor.drag = null; syncLegEditor(); return; }
  if (!drag) { return; }
  canvas.classList.remove('dragging');
  var rect = canvas.getBoundingClientRect();
  if (drag.moved < 5 && !drag.pan) {
    var mx = ev.clientX - rect.left;
    var my = ev.clientY - rect.top;
    if (MAP_VIEW === 'planar' && locationEditor.enabled) {
      locationEditorClick(mx, my); drag = null; endInteract(); return;
    }
    if (MAP_VIEW === 'planar' && !legEditor.enabled && !state.calibOn && !state.terrainEditOn) {
      var junction = junctionAt(mx, my);
      if (junction) { focusJunction(junction); drag = null; endInteract(); return; }
    }
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
      if (!pins[hit].data.mobile && !pins[hit].data.mapOnly) {
        if (doubleClick) { loadTerrainDetail(id); }
      }
    }
  }
  drag = null;
  endInteract();
}

canvas.addEventListener('pointerup', endDrag);
canvas.addEventListener('pointercancel', function () {
  legEditor.drag = null;
  drag = null;
  canvas.classList.remove('dragging');
  endInteract();
});
canvas.addEventListener('contextmenu', function (ev) { ev.preventDefault(); });

canvas.addEventListener('wheel', function (ev) {
  ev.preventDefault();
  if (MAP_VIEW === 'planar') {
    if (ev.deltaY) { stepPlanarRadius(ev.deltaY > 0 ? 1 : -1); }
    return;
  }
  beginInteract();
  var factor = Math.exp(ev.deltaY * 0.0012);
  if (state.globe) {
    state.globeZoom = clamp(state.globeZoom / factor, 0.55, 2.5);
  } else {
    state.dist = clamp(state.dist * factor, minDistance(), 12);
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
  if (MAP_VIEW === 'planar') {
    var pan = state.planarRadius / (5 * SCALE);
    if (ev.key === 'ArrowLeft') { state.tx -= pan; }
    else if (ev.key === 'ArrowRight') { state.tx += pan; }
    else if (ev.key === 'ArrowUp') { state.tz -= pan; }
    else if (ev.key === 'ArrowDown') { state.tz += pan; }
    else if (ev.key === '+' || ev.key === '=') { stepPlanarRadius(-1); }
    else if (ev.key === '-' || ev.key === '_') { stepPlanarRadius(1); }
    else { return; }
    ev.preventDefault(); invalidate(); return;
  }
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
    else { state.dist = clamp(state.dist * 0.9, minDistance(), 12); }
  }
  else if (ev.key === '-' || ev.key === '_') {
    if (state.globe) { state.globeZoom = clamp(state.globeZoom / 1.1, 0.55, 2.5); }
    else { state.dist = clamp(state.dist * 1.1, minDistance(), 12); }
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
  var bestDist = MAP_VIEW === 'planar' ? Infinity : 18 * 18;
  for (var i = 0; i < pins.length; i++) {
    var p = pins[i];
    if (!p.vis) { continue; }
    if (p.data.mobile) {
      var caravan = caravanIconPosition(p);
      if (MAP_VIEW === 'planar') {
        var markerDistance = (mx - caravan.x) ** 2 + (my - caravan.y) ** 2;
        var markerReach = mapPinRadius(p, false, false) + 7;
        if (markerDistance < markerReach * markerReach && markerDistance < bestDist) {
          bestDist = markerDistance; best = i;
        }
        continue;
      }
      if (Math.abs(mx - caravan.x) <= 13 && Math.abs(my - caravan.y) <= 15) { return i; }
    }
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
    var radius = mapPinRadius(p, state.selected === p.data.id, state.hover === i);
    var reach = (radius + 9) * (radius + 9);
    if (d < reach && (d < bestDist || (d === bestDist && p.data.mobile))) { bestDist = d; best = i; }
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
    if (MAP_VIEW === 'planar' && line.sourcePoints) {
      var hit = nearestLegSegment(line.sourcePoints, mx, my);
      if (hit.index >= 0 && hit.distance < bestDistance) { bestDistance = hit.distance; best = r; }
      continue;
    }
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
  var mapEndpoints = MAP_VIEW === 'planar' && group.length === 1 ? planarLegEndpoints(line.sourcePoints) : null;
  if (mapEndpoints) { start = mapEndpoints.origin.name; end = mapEndpoints.destination.name; }
  var distance = group.reduce(function (total, routeLine) { return total + routeLine.details.distance; }, 0);
  var days = group.reduce(function (total, routeLine) { return total + routeLine.details.days; }, 0);
  var dailyHops = group.reduce(function (total, routeLine) {
    return total + (routeLine.kind === 'air' ? Math.max(1, Math.ceil(routeLine.details.distance / 80)) : 1);
  }, 0);
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
    if (mapEndpoints) { legStart = start; legEnd = end; }
    return '<li><b>' + esc(legStart) + ' &rarr; ' + esc(legEnd) + '</b> <small>' +
      Math.round(leg.line.details.distance).toLocaleString() + ' mi &middot; ' +
      (leg.line.kind === 'air' ? Number(leg.line.details.days).toFixed(1) + ' days' : routeTime(leg.line.details.days)) + '</small><details class="routecarriers"' +
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
    '<div><span>Travel time</span><b>' + (modes.indexOf('air') >= 0 ? Number(days).toFixed(1) + ' days' : routeTime(days)) + '</b></div>' +
    '<div><span>Daily hops</span><b>' + dailyHops + '</b></div></div>' +
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

function planRouteMatches(line) {
  return !!(state.planRouteKeys[line.editId] || (line.details && state.planRouteKeys[
    supplyRouteKey(line.details.start, line.details.end)
  ]));
}

function collectPlanRoute(data) {
  (data.legs || []).forEach(function (leg) {
    state.planRouteKeys[supplyRouteKey(leg.from, leg.to)] = true;
    if (leg.id) { state.planRouteKeys[leg.id] = true; }
  });
}

function collectPlanPath(names) {
  for (var i = 0; i < names.length - 1; i++) {
    state.planRouteKeys[supplyRouteKey(names[i], names[i + 1])] = true;
  }
}

function fitPlanRoute(originName, destinationName) {
  if (MAP_VIEW === 'planar' && state.planRoute && state.planRoute.mapRoads) {
    var points = state.planRoute.legs.reduce(function (all, leg) { return all.concat(leg.points); }, []);
    if (!points.length) { return; }
    var west = Infinity, east = -Infinity, north = Infinity, south = -Infinity;
    points.forEach(function (point) {
      west = Math.min(west, point[0]); east = Math.max(east, point[0]);
      north = Math.min(north, point[1]); south = Math.max(south, point[1]);
    });
    var center = toScene((west + east) / 2, (north + south) / 2);
    state.tx = center[0]; state.tz = center[1];
    var radius = Math.hypot(east - west, south - north) / 2;
    state.planarRadius = [50, 100, 200, 500].find(function (value) { return value >= radius; }) || 500;
    document.getElementById('planar-radius').value = String(state.planarRadius);
    return;
  }
  var originId = state.nameToId[originName];
  var destId = state.nameToId[destinationName];
  var originPin = pins.find(function (item) { return item.data.id === originId; });
  var destPin = pins.find(function (item) { return item.data.id === destId; });
  if (!originPin || !destPin) { return; }
  state.tx = (originPin.sx + destPin.sx) / 2;
  state.tz = (originPin.sz + destPin.sz) / 2;
  var span = Math.hypot(destPin.sx - originPin.sx, destPin.sz - originPin.sz);
  state.dist = clamp(span * 0.9 + 0.4, 0.55, 12);
}

function renderPlannedRoute(data) {
  var panel = document.getElementById('route-plan-result');
  function dailyFlightSchedule(leg) {
    if (leg.mode !== 'air' && !(leg.modes || []).includes('air')) { return ''; }
    var flightDays = Math.max(1, Math.ceil(Number(leg.miles || 0) / 80));
    var rows = [];
    for (var day = 1; day <= flightDays; day++) {
      var miles = day === flightDays ? Number(leg.miles || 0) - (flightDays - 1) * 80 : 80;
      rows.push('<li>Day ' + day + ': fly ' + Math.max(0, Math.round(miles)) + ' mi</li>');
      if (day < flightDays) { rows.push('<li class="flight-rest">Land and rest before Day ' + (day + 1) + '</li>'); }
    }
    return '<ol class="flight-day-list"><li><b>Gryphon daily schedule</b> &middot; max 80 mi before landing</li>' + rows.join('') + '</ol>';
  }
  var legs = (data.legs || []).map(function (leg, index) {
    return '<li><b>' + (index + 1) + '. ' + esc(leg.from) + ' → ' + esc(leg.to) +
      '</b><small>' + esc(leg.via || 'local track') + ' &middot; ' + esc(leg.mode_label || leg.mode || '') +
      ' &middot; ' + Math.round(leg.miles).toLocaleString() + ' mi &middot; ' + routeTime(leg.days) +
      ' &middot; hazard ' + Number(leg.hazard || 0).toFixed(2) + 'x</small>' + dailyFlightSchedule(leg) + '</li>';
  }).join('');
  var plannerUrl = 'planner.html?origin=' + encodeURIComponent(data.origin) +
    '&destination=' + encodeURIComponent(data.destination) +
    '&include_inferred=' + (state.inferredRoads ? '1' : '0');
  panel.innerHTML = '<p>' + esc(data.path.join(' → ')) + '</p>' +
    (legs ? '<ol class="planned-route-legs">' + legs + '</ol>' : '') +
    '<p class="muted">' + Math.round(data.distance).toLocaleString() + ' mi &middot; ' +
    routeTime(data.days) + ' &middot; ' + esc(data.modes.map(routeTypeLabel).join(', ')) + '</p>' +
    '<p><a class="route-detail-link" href="' + plannerUrl + '">Open detailed legs, prices &amp; carrier choices &rarr;</a></p>' +
    '<button type="button" id="route-plan-clear" class="ghost">Clear</button>';
}

function clearPlannedRoute() {
  state.planRoute = null;
  state.planRouteKeys = {};
  document.getElementById('route-plan-result').innerHTML = '';
  invalidate();
}

async function showPlanPath(names) {
  var panel = document.getElementById('route-plan-result');
  if (!names || names.length < 2) { return; }
  var requestToken = ++state.planRequest;
  state.planRoute = null;
  state.planRouteKeys = {};
  panel.textContent = 'Loading mapped itinerary...';
  try {
    var legs = [], distance = 0, days = 0;
    for (var index = 1; index < names.length; index++) {
      var segment = await getJson('/api/route?origin=' + encodeURIComponent(names[index - 1]) +
        '&destination=' + encodeURIComponent(names[index]) + '&optimise=days');
      if (requestToken !== state.planRequest) { return; }
      if (!segment.reachable) { throw new Error('This itinerary no longer connects on the saved map.'); }
      legs = legs.concat(segment.legs); distance += segment.distance; days += segment.days;
    }
    var data = {origin: names[0], destination: names[names.length - 1], reachable: true,
      mapRoads: legs.every(function (leg) { return leg.points && leg.points.length; }),
      legs: legs, distance: distance, days: days,
      modes: Array.from(new Set(legs.flatMap(function (leg) { return leg.modes || [leg.mode]; }))),
      path: [names[0]].concat(legs.map(function (leg) { return leg.to; }))};
    state.planRoute = data;
    collectPlanRoute(data); renderPlannedRoute(data); fitPlanRoute(data.origin, data.destination);
  } catch (error) {
    if (requestToken !== state.planRequest) { return; }
    panel.textContent = error.message;
  }
  invalidate();
}

function publishedMapPath(origin, destination) {
  if (!routeLines || !routeLines.length) { return null; }
  var edges = {};
  routeLines.forEach(function (line) {
    if (line.inferredRoad || !line.details || !routeMatchesFilter(line)) { return; }
    var start = line.details.start, end = line.details.end;
    if (!start || !end) { return; }
    (edges[start] || (edges[start] = [])).push({to: end, cost: Number(line.details.distance) || 1});
    (edges[end] || (edges[end] = [])).push({to: start, cost: Number(line.details.distance) || 1});
  });
  if (!edges[origin] || !edges[destination]) { return null; }
  var distance = {}, previous = {}, open = [origin];
  distance[origin] = 0;
  while (open.length) {
    open.sort(function (a, b) { return distance[a] - distance[b]; });
    var current = open.shift();
    if (current === destination) { break; }
    (edges[current] || []).forEach(function (edge) {
      var next = distance[current] + edge.cost;
      if (distance[edge.to] === undefined || next < distance[edge.to]) {
        distance[edge.to] = next;
        previous[edge.to] = current;
        if (open.indexOf(edge.to) < 0) { open.push(edge.to); }
      }
    });
  }
  if (distance[destination] === undefined) { return null; }
  var path = [], cursor = destination;
  while (cursor) { path.unshift(cursor); cursor = previous[cursor]; }
  return path.length > 1 ? path : null;
}

function junctionRoadPlan(origin, destination) {
  var graph = {}, junctions = Object.values(mapLegEdits.junctions || {});
  function endpoint(point) {
    var best = null, distance = 2.5;
    (pins || []).forEach(function (pin) {
      if (pin.data.mobile) { return; }
      var candidate = Math.hypot(point[0] - pin.wx, point[1] - pin.wy);
      if (candidate <= distance) { distance = candidate; best = pin.data.name; }
    });
    return best;
  }
  routeLines.forEach(function (line) {
    if (!['road', 'trail', 'track', 'ferry'].includes(line.kind) || !planarLegVisible(line)) { return; }
    var points = line.sourcePoints || [], anchors = [], distance = 0;
    points.forEach(function (point, index) {
      if (index) { distance += Math.hypot(point[0] - points[index - 1][0], point[1] - points[index - 1][1]); }
      var junction = junctions.find(function (item) {
        return item.legs.includes(line.editId) && Math.hypot(point[0] - item.point[0], point[1] - item.point[1]) < 0.001;
      });
      var name = junction ? junction.name : ((index === 0 || index === points.length - 1)
        ? (endpoint(point) || 'Road waypoint (' + point[0].toFixed(6) + ', ' + point[1].toFixed(6) + ')') : null);
      if (name) { anchors.push({name: name, distance: distance, index: index}); }
    });
    for (var index = 1; index < anchors.length; index++) {
      var start = anchors[index - 1], end = anchors[index];
      if (start.name === end.name) { continue; }
      var miles = end.distance - start.distance;
      var pointsSlice = points.slice(start.index, end.index + 1);
      (graph[start.name] || (graph[start.name] = [])).push({from: start.name, to: end.name, miles: miles,
        via: line.details.name, mode: line.kind, points: pointsSlice, id: line.editId});
      (graph[end.name] || (graph[end.name] = [])).push({from: end.name, to: start.name, miles: miles,
        via: line.details.name, mode: line.kind, points: pointsSlice.slice().reverse(), id: line.editId});
    }
  });
  var distance = {}, previous = {}, open = [origin]; distance[origin] = 0;
  while (open.length) {
    open.sort(function (left, right) { return distance[left] - distance[right]; });
    var current = open.shift();
    if (current === destination) { break; }
    (graph[current] || []).forEach(function (edge) {
      var next = distance[current] + edge.miles;
      if (distance[edge.to] === undefined || next < distance[edge.to]) {
        distance[edge.to] = next; previous[edge.to] = edge;
        if (!open.includes(edge.to)) { open.push(edge.to); }
      }
    });
  }
  if (distance[destination] === undefined) { return null; }
  var legs = [], cursor = destination;
  while (cursor !== origin) { var edge = previous[cursor]; legs.unshift(edge); cursor = edge.from; }
  var itinerary = [];
  legs.forEach(function (leg) {
    var last = itinerary[itinerary.length - 1];
    if (last && last.to === leg.from && last.id === leg.id && last.via === leg.via && last.mode === leg.mode &&
        junctions.some(function (junction) { return junction.name === leg.from; })) {
      last.to = leg.to;
      last.miles += leg.miles;
      last.points = last.points.concat(leg.points.slice(1));
    } else { itinerary.push(Object.assign({}, leg, {points: leg.points.slice()})); }
  });
  return {origin: origin, destination: destination, reachable: true, mapRoads: true,
    distance: distance[destination], legs: itinerary, path: [origin].concat(itinerary.map(function (leg) { return leg.to; }))};
}

async function showPlannedRoute(origin, destination, optimise) {
  var panel = document.getElementById('route-plan-result');
  if (!origin || !destination) { return; }
  var requestToken = ++state.planRequest;
  state.planRoute = null;
  state.planRouteKeys = {};
  var pendingUrl = new URL(window.location.href);
  pendingUrl.searchParams.delete('planPath');
  history.replaceState(null, '', pendingUrl.pathname + '?' + pendingUrl.searchParams.toString());
  invalidate();
  panel.innerHTML = '<p class="muted">Planning route&#8230;</p>';
  try {
    var selectedTypes = (MAP_VIEW === 'planar' ? state.planarLegTypes : state.routeTypes).join(',');
    var data = await getJson('/api/route?origin=' + encodeURIComponent(origin) +
      '&destination=' + encodeURIComponent(destination) +
      '&optimise=' + encodeURIComponent(optimise || 'days') +
      '&include_inferred=' + (state.inferredRoads ? '1' : '0') +
      (selectedTypes ? '&route_type=' + encodeURIComponent(selectedTypes) : ''));
    if (requestToken !== state.planRequest) { return; }
    if (!data.reachable) {
      state.planRoute = null;
      state.planRouteKeys = {};
      panel.innerHTML = '<p class="muted">No route connects these settlements.</p>';
      invalidate();
      return;
    }
    state.planRoute = data;
    state.planOptimise = optimise || 'days';
    state.planRouteKeys = {};
    collectPlanRoute(data);
    renderPlannedRoute(data);
    fitPlanRoute(data.origin, data.destination);
    var planUrl = new URL(window.location.href);
    planUrl.searchParams.set('planOrigin', data.origin);
    planUrl.searchParams.set('planDestination', data.destination);
    planUrl.searchParams.set('planOptimise', optimise || 'days');
    planUrl.searchParams.delete('planPath');
    if (state.routeTypes.length) { planUrl.searchParams.set('routeTypes', state.routeTypes.join(',')); }
    history.replaceState(null, '', planUrl.pathname + '?' + planUrl.searchParams.toString());
    invalidate();
  } catch (err) {
    if (requestToken !== state.planRequest) { return; }
    panel.innerHTML = '<p class="muted">' + esc(err.message) + '</p>';
  }
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
  if (MAP_VIEW === 'planar') { focusSettlement(id); return; }
  var request = ++state.detailRequest;
  getJson('/api/terrain-detail?settlement=' + encodeURIComponent(id))
    .then(function (detail) {
      if (request !== state.detailRequest || state.selected !== id) { return; }
      buildMesh(detail);
      // Scene coordinates are relative to the mesh centre, so the old target
      // now points hundreds of miles off the new patch. Harmless while the
      // camera could not get closer than 350 miles; fatal once it can.
      var middle = toScene((detail.bounds[0] + detail.bounds[2]) / 2,
                           (detail.bounds[1] + detail.bounds[3]) / 2);
      state.tx = middle[0];
      state.tz = middle[1];
      buildPins(state.map.settlements);
      buildPlaces(state.map.places || []);
      rebuildRouteGeometry();
      state.detailId = id;
      document.getElementById('view-world').hidden = false;
      state.yaw = 0;
      state.pitch = 1.35;
      fitView();
      showStatus(detail.cellMiles + '-mile terrain detail');
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
  if (MAP_VIEW === 'planar') {
    var focusPin = pins && pins.find(function (item) { return item.data.id === id; });
    if (focusPin) { state.tx = focusPin.sx; state.tz = focusPin.sz; }
  }
  state.selectedRoute = -1;
  state.selectedCarrierService = '';
  state.supplyChain = null;
  state.supplyRouteKeys = {};
  document.getElementById('supply-chain').hidden = true;
  updateRouteSelection();
  invalidate();
  var link = document.getElementById('history-link');
  if (link) {
    link.hidden = false;
    link.href = 'location.html?settlement=' + encodeURIComponent(id);
  }
  var head = document.getElementById('place-head');
  head.innerHTML = '<h2>Loading&#8230;</h2>';
  var selectedPin = pins.find(function (item) { return item.data.id === id; });
  if (selectedPin && selectedPin.data.mapOnly) {
    state.market = null;
    var site = selectedPin.data;
    head.innerHTML = '<h2>' + esc(site.name) + '</h2><p class="sub">' +
      esc(PLACE_TYPES[site.placeType] || 'Location') + ' &middot; ' + (site.inhabited ? 'Inhabited' : 'Uninhabited') + '</p>' +
      (site.roadName ? '<p>' + esc(site.roadName) + '</p>' : '') +
      (site.notes ? '<p style="white-space:pre-wrap">' + esc(site.notes) + '</p>' : '');
    if (link) { link.hidden = true; }
    ['place-stats', 'place-notes', 'place-prices'].forEach(function (id) { document.getElementById(id).textContent = ''; });
    return;
  }
  if (selectedPin && selectedPin.data.mobile) {
    if (selectedPin.data.carrier) {
      var carrier = selectedPin.data;
      head.innerHTML = '<h2>' + esc(carrier.name) + '</h2><p class="sub">Carrier service &middot; ' +
        esc(carrier.status || 'rolling') + '</p><p class="muted">' +
        esc('On ' + (carrier.route || 'active route') + ': ' + carrier.origin + ' to ' + carrier.destination) +
        ' &middot; ' + Math.round(carrier.progress * 100) + '% complete</p><p class="muted">Capacity: ' +
        Number(carrier.capacity_lb || 0).toLocaleString() + ' lb</p><p><a href="business.html?business=' +
        encodeURIComponent(carrier.id) + '">Open carrier business profile</a></p>';
      if (link) { link.href = 'business.html?business=' + encodeURIComponent(carrier.id); }
      return;
    }
    try {
      var mobile = await getJson('/api/mobile-location?id=' + encodeURIComponent(id));
      var position = mobile.position;
      var positionText = position.status === 'encamped'
        ? 'Encamped at ' + position.host.name
        : 'Travelling from ' + position.origin.name + ' to ' + position.destination.name;
      if (position.position_source === 'route_unavailable') {
        positionText += ' (mapped route unavailable; marker remains at last known origin)';
      }
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
    var market = await getJson('/api/market?settlement=' + encodeURIComponent(id));
    if (state.selected !== id) { return; }
    state.market = market;
    renderPanel();
  } catch (err) {
    head.innerHTML = '<h2>Market unavailable</h2><p class="muted">' + esc(err.message) + '</p>';
  }
}

function focusSettlement(id) {
  var junction = junctionLocations().find(function (location) { return location.id === id; });
  if (junction) { return focusJunction(junction); }
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

function junctionLocations() {
  return Object.keys(mapLegEdits.junctions || {}).map(function (identifier) {
    var junction = mapLegEdits.junctions[identifier];
    return {id: 'junction:' + identifier, name: junction.name, x: junction.point[0], y: junction.point[1], junction: true};
  });
}

function syncJunctionLocations() {
  var options = document.getElementById('location-options');
  options.querySelectorAll('[data-junction]').forEach(function (option) { option.remove(); });
  junctionLocations().forEach(function (location) {
    var option = document.createElement('option'); option.value = location.name;
    option.setAttribute('data-junction', location.id); options.appendChild(option);
  });
}

async function renameJunction(identifier, name) {
  var junction = mapLegEdits.junctions[identifier];
  if (!junction || legEditor.saving) { throw new Error('Junction is unavailable or another save is in progress.'); }
  if (legEditor.dirty) { throw new Error('Save or cancel your route leg changes before renaming a junction.'); }
  var oldName = junction.name;
  legEditor.saving = true; syncLegEditor();
  try {
    mapLegEdits = await postJson('/api/map-junction', {
      id: identifier, name: name.trim(), point: junction.point, legs: junction.legs, revision: mapLegEdits.revision
    });
    var newName = mapLegEdits.junctions[identifier].name;
    applyMapLegEdits(); syncJunctionLocations(); clearPlannedRoute();
    ['route-plan-origin', 'route-plan-destination'].forEach(function (id) {
      var input = document.getElementById(id);
      if (input.value === oldName) { input.value = newName; }
    });
    if (legEditor.draft && mapLegEdits.legs[legEditor.draft.id]) {
      legEditor.draft.name = mapLegEdits.legs[legEditor.draft.id].name;
    }
    if (state.selected === 'junction:' + identifier) {
      focusJunction(junctionLocations().find(function (location) { return location.id === state.selected; }));
    }
  } finally { legEditor.saving = false; syncLegEditor(); invalidate(); }
}

async function deleteJunction(identifier) {
  var junction = (mapLegEdits.junctions || {})[identifier];
  if (!junction || legEditor.saving) { throw new Error('Junction is unavailable or another save is in progress.'); }
  if (legEditor.dirty || locationEditor.draft || locationEditor.busy) {
    throw new Error('Save or cancel your map edits before deleting a junction.');
  }
  if (!window.confirm('Delete junction "' + junction.name + '"? Connected roads and waypoints will be kept.')) { return; }
  legEditor.saving = true; syncLegEditor();
  try {
    mapLegEdits = await postJson('/api/map-junction', {
      id: identifier, deleted: true, revision: mapLegEdits.revision
    });
    applyMapLegEdits(); syncJunctionLocations(); clearPlannedRoute();
    ['route-plan-origin', 'route-plan-destination'].forEach(function (id) {
      var input = document.getElementById(id);
      if (input.value === junction.name) { input.value = ''; }
    });
    if (state.selected === 'junction:' + identifier) {
      state.selected = null;
      document.getElementById('place-head').textContent = 'Junction deleted. Roads and waypoints were kept.';
      ['place-stats', 'place-notes', 'place-prices'].forEach(function (id) {
        document.getElementById(id).textContent = '';
      });
    }
    updateRouteSelection();
  } finally { legEditor.saving = false; syncLegEditor(); invalidate(); }
}

function focusJunction(location) {
  if (!mesh) { return false; }
  var scene = toScene(location.x, location.y);
  state.tx = scene[0]; state.tz = scene[1]; state.selected = location.id;
  state.market = null; state.selectedRoute = -1; state.selectedCarrierService = '';
  state.supplyChain = null; state.supplyRouteKeys = {};
  document.getElementById('supply-chain').hidden = true;
  document.getElementById('place-head').innerHTML = '<h2>' + esc(location.name) + '</h2><p class="sub">Road junction</p>';
  var renameForm = document.createElement('form');
  var renameLabel = document.createElement('label');
  renameLabel.textContent = 'Junction name';
  var renameInput = document.createElement('input');
  renameInput.type = 'text'; renameInput.value = location.name; renameInput.required = true;
  renameInput.maxLength = 160; renameInput.style.width = '100%'; renameInput.style.boxSizing = 'border-box';
  renameLabel.appendChild(renameInput); renameForm.appendChild(renameLabel);
  var renameButton = document.createElement('button');
  renameButton.type = 'submit'; renameButton.textContent = 'Rename junction'; renameForm.appendChild(renameButton);
  var deleteButton = document.createElement('button');
  deleteButton.type = 'button'; deleteButton.textContent = 'Delete junction'; renameForm.appendChild(deleteButton);
  var renameStatus = document.createElement('p'); renameStatus.setAttribute('role', 'status');
  renameForm.appendChild(renameStatus);
  deleteButton.addEventListener('click', async function () {
    deleteButton.disabled = true; renameButton.disabled = true; renameStatus.textContent = '';
    try { await deleteJunction(location.id.slice(9)); }
    catch (error) { renameStatus.textContent = error.message; }
    finally { deleteButton.disabled = false; renameButton.disabled = false; }
  });
  renameForm.addEventListener('submit', async function (event) {
    event.preventDefault();
    if (!renameInput.value.trim()) { renameStatus.textContent = 'Enter a junction name.'; return; }
    renameButton.disabled = true; renameStatus.textContent = 'Saving...';
    try {
      await renameJunction(location.id.slice(9), renameInput.value);
    } catch (error) { renameStatus.textContent = error.message; }
    finally { renameButton.disabled = false; }
  });
  document.getElementById('place-head').appendChild(renameForm);
  ['place-stats', 'place-notes', 'place-prices'].forEach(function (id) { document.getElementById(id).innerHTML = ''; });
  var junction = mapLegEdits.junctions[location.id.slice(9)];
  document.getElementById('place-notes').innerHTML = '<ul>' + junction.legs.map(function (identifier) {
    var leg = mapLegEdits.legs[identifier];
    return leg && !leg.deleted ? '<li>' + esc(leg.name) + '</li>' : '';
  }).join('') + '</ul>';
  var historyLink = document.getElementById('history-link');
  if (historyLink) { historyLink.hidden = true; }
  updateRouteSelection(); invalidate(); return true;
}

function findLocation(query) {
  var needle = String(query || '').trim().toLowerCase();
  if (!needle || !state.map) { return null; }
  var settlements = (state.map.settlements || []).concat(junctionLocations());
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
var UNDERLAY_SOURCE_KEY = 'faerun.underlay.source';
var underlayRequest = 0;
var RASTER_LAYERS_KEY = 'faerun.reference-layers.v1';
var rasterLayersRestored = false;

function saveRasterLayers() {
  var preferences = {};
  Object.keys(state.rasterLayers).forEach(function (source) {
    var layer = state.rasterLayers[source];
    preferences[source] = {on: layer.on, alpha: layer.alpha};
  });
  try { window.localStorage.setItem(RASTER_LAYERS_KEY, JSON.stringify(preferences)); }
  catch (err) { showStatus('Reference overlay preferences could not be saved.', true); }
}

function syncRasterLayerControls() {
  var options = state.underInfo ? state.underInfo.options || [] : [];
  Object.keys(state.rasterLayers).forEach(function (source) {
    var layer = state.rasterLayers[source];
    var toggle = underlayEl('layer-' + source);
    toggle.disabled = !state.under || !options.some(function (option) { return option.id === source; });
    toggle.checked = layer.on;
    toggle.title = toggle.disabled ? 'This local reference image is unavailable.' : '';
    var opacity = underlayEl('layer-' + source + '-alpha');
    opacity.disabled = toggle.disabled || !layer.on;
    opacity.value = String(Math.round(layer.alpha * 100));
  });
}

async function loadRasterLayer(source) {
  var layer = state.rasterLayers[source];
  if (layer.image || layer.loading) { return; }
  layer.loading = true;
  try {
    var info = await getJson('/api/underlay?source=' + encodeURIComponent(source));
    if (!info.available) { throw new Error('The local reference image is unavailable.'); }
    layer.image = await new Promise(function (resolve, reject) {
      var image = new Image();
      image.onload = function () { resolve(image); };
      image.onerror = function () { reject(new Error('The reference image could not be decoded: ' + info.name)); };
      image.src = info.url;
    });
  } catch (err) {
    layer.on = false;
    saveRasterLayers();
    showStatus('Could not load ' + source + ': ' + err.message, true);
  } finally {
    layer.loading = false;
    syncRasterLayerControls();
    invalidate();
  }
}

function restoreRasterLayers() {
  if (!rasterLayersRestored) {
    rasterLayersRestored = true;
    try {
      var saved = JSON.parse(window.localStorage.getItem(RASTER_LAYERS_KEY) || '{}');
      Object.keys(state.rasterLayers).forEach(function (source) {
        var value = saved && saved[source];
        if (!value) { return; }
        var layer = state.rasterLayers[source];
        layer.on = value.on === true;
        if (typeof value.alpha === 'number' && isFinite(value.alpha)) {
          layer.alpha = Math.max(0, Math.min(1, value.alpha));
        }
      });
    } catch (err) { showStatus('Reference overlay preferences could not be restored.', true); }
  }
  syncRasterLayerControls();
  Object.keys(state.rasterLayers).forEach(function (source) {
    if (state.rasterLayers[source].on) { loadRasterLayer(source); }
  });
}

function underlayStorageKey() {
  var source = state.underInfo && state.underInfo.source;
  return source && source !== 'default' ? UNDERLAY_KEY + '.' + source : UNDERLAY_KEY;
}

function underlayEl(id) { return document.getElementById(id); }

function saveUnderlay() {
  try {
    window.localStorage.setItem(underlayStorageKey(), JSON.stringify({
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
    var raw = window.localStorage.getItem(underlayStorageKey());
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

async function setMapView(view) {
  if (view !== 'overlay' && view !== 'terrain' && view !== 'planar') { return; }
  if (MAP_VIEW === 'planar' && view !== 'planar' && !await discardLegDraft()) {
    document.querySelectorAll('input[name="map-view"]').forEach(function (input) { input.checked = input.value === MAP_VIEW; });
    return;
  }
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
  if (view === 'planar') {
    state.globe = false;
    state.roundWorld = false;
    state.terrainEditOn = false;
    state.calibOn = false;
    ['opt-globe', 'opt-round-world', 'opt-terrain-edit', 'opt-calib'].forEach(function (id) {
      document.getElementById(id).checked = false;
    });
    canvas.classList.remove('calibrating', 'terrain-editing');
    var target = state.selected || (findLocation('Waterdeep') || {}).id;
    if (target) { focusSettlement(target); }
  }
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

async function loadUnderlay(source) {
  var request = ++underlayRequest;
  if (!source) {
    try { source = window.localStorage.getItem(UNDERLAY_SOURCE_KEY); } catch (err) {}
  }
  source = ['topographical', 'elevation', 'ground-cover'].indexOf(source) >= 0 ? source : 'default';
  var info;
  try {
    info = await getJson('/api/underlay?source=' + encodeURIComponent(source));
  } catch (err) {
    if (request === underlayRequest) {
      underlayEl('underlay-source').value = (state.underInfo && state.underInfo.source) || 'default';
      showStatus('The poster backdrop could not be loaded.', true);
    }
    return;
  }
  if (request !== underlayRequest) { return; }
  var options = info.options || [{id: 'default', label: 'Original poster'}];
  var select = underlayEl('underlay-source');
  select.innerHTML = options.map(function (option) {
    return '<option value="' + esc(option.id) + '">' + esc(option.label) + '</option>';
  }).join('');
  select.value = source;
  if (!info.available) {
    if (options.length && options[0].id !== source) {
      return loadUnderlay(options[0].id);
    }
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
  img.onload = function () {
    if (request !== underlayRequest) { return; }
    state.underInfo = info;
    underlayEl('underlay-none').hidden = true;
    try { window.localStorage.setItem(UNDERLAY_SOURCE_KEY, source); } catch (err) {}
    applyUnderlayImage(img);
    restoreRasterLayers();
  };
  img.onerror = function () {
    if (request !== underlayRequest) { return; }
    select.value = (state.underInfo && state.underInfo.source) || 'default';
    showStatus('The poster map at ' + info.path + ' could not be decoded.', true);
  };
  img.src = info.url;
}

function wireUnderlay() {
  Object.keys(state.rasterLayers).forEach(function (source) {
    underlayEl('layer-' + source).addEventListener('change', function (ev) {
      state.rasterLayers[source].on = ev.target.checked;
      saveRasterLayers();
      syncRasterLayerControls();
      if (ev.target.checked) { loadRasterLayer(source); }
      invalidate();
    });
    underlayEl('layer-' + source + '-alpha').addEventListener('input', function (ev) {
      state.rasterLayers[source].alpha = Number(ev.target.value) / 100;
      saveRasterLayers();
      invalidate();
    });
  });
  underlayEl('underlay-source').addEventListener('change', function (ev) {
    if (state.under) { saveUnderlay(); }
    loadUnderlay(ev.target.value);
  });
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

function wireLocationLabels() {
  var all = document.getElementById('show-all-location-labels');
  var labels = document.getElementById('opt-labels');
  var key = 'faerun-map-show-all-location-labels';
  try {
    var saved = window.localStorage.getItem(key);
    if (saved !== null && saved !== 'true' && saved !== 'false') {
      throw new Error('Invalid saved location label preference');
    }
    state.showAllLocationLabels = saved === 'true';
  } catch (err) {
    console.error('Location label preference could not be restored.', err);
    showStatus('Location label preference could not be restored.', true);
  }
  if (state.showAllLocationLabels) { state.labels = true; }
  all.checked = state.showAllLocationLabels;
  labels.checked = state.labels;
  function save() {
    invalidate();
    try {
      window.localStorage.setItem(key, String(state.showAllLocationLabels));
    } catch (err) {
      console.error('Location label preference could not be saved.', err);
      showStatus('Location label preference could not be saved; this choice applies only to this page.', true);
    }
  }
  all.addEventListener('change', function () {
    state.showAllLocationLabels = all.checked;
    if (all.checked) { state.labels = true; labels.checked = true; }
    save();
  });
  labels.addEventListener('change', function () {
    state.labels = labels.checked;
    if (!labels.checked) { state.showAllLocationLabels = false; all.checked = false; }
    save();
  });
}

function wireMarkerLabels(id, property, label) {
  var input = document.getElementById(id);
  var key = 'faerun-map-' + id;
  try {
    var saved = window.localStorage.getItem(key);
    if (saved !== null && !['auto', 'show', 'hide'].includes(saved)) {
      throw new Error('Invalid saved ' + label.toLowerCase() + ' label preference');
    }
    state[property] = saved === null ? 'auto' : saved;
  } catch (err) {
    console.error(label + ' label preference could not be restored.', err);
    showStatus(label + ' label preference could not be restored.', true);
  }
  input.value = state[property];
  input.addEventListener('change', function () {
    state[property] = input.value;
    invalidate();
    try {
      window.localStorage.setItem(key, state[property]);
    } catch (err) {
      console.error(label + ' label preference could not be saved.', err);
      showStatus(label + ' label preference could not be saved; this choice applies only to this page.', true);
    }
  });
}

function wireControls() {
  wireLocationLabels();
  wireMarkerLabels('junction-labels', 'junctionLabels', 'Junction');
  wireMarkerLabels('company-labels', 'companyLabels', 'Travelling company');
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
    var routeUrl = new URL(window.location.href);
    if (state.routeTypes.length) { routeUrl.searchParams.set('routeTypes', state.routeTypes.join(',')); }
    else { routeUrl.searchParams.delete('routeTypes'); }
    history.replaceState(null, '', routeUrl.pathname + '?' + routeUrl.searchParams.toString());
    var summary = document.getElementById('route-type-summary');
    summary.textContent = state.routeTypes.length === 0 ? 'All types'
      : (state.routeTypes.length <= 2
        ? state.routeTypes.map(routeTypeLabel).join(', ')
        : state.routeTypes.length + ' types');
    if (state.selectedRoute >= 0 && !routeMatchesFilter(routeLines[state.selectedRoute])) {
      selectRoute(-1);
    }
    if (state.planRoute) {
      showPlannedRoute(state.planRoute.origin, state.planRoute.destination,
        state.planOptimise || 'days');
    }
    invalidate();
  }
  routeAll.addEventListener('change', updateRouteTypes);
  routeTypeInputs.forEach(function (input) { input.addEventListener('change', updateRouteTypes); });
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
  document.getElementById('route-plan-form').addEventListener('submit', function (ev) {
    ev.preventDefault();
    var originInput = document.getElementById('route-plan-origin');
    var destinationInput = document.getElementById('route-plan-destination');
    var origin = findLocation(originInput.value);
    var destination = findLocation(destinationInput.value);
    var panel = document.getElementById('route-plan-result');
    if (!origin || !destination) {
      panel.innerHTML = '<p class="muted">Enter an origin and destination that both match a settlement.</p>';
      return;
    }
    originInput.value = origin.name;
    destinationInput.value = destination.name;
    showPlannedRoute(origin.name, destination.name,
      document.getElementById('route-plan-cost').checked ? 'cost' : 'days');
  });
  document.getElementById('route-plan-result').addEventListener('click', function (ev) {
    if (ev.target.id === 'route-plan-clear') { clearPlannedRoute(); }
  });
  window.addEventListener('resize', function () {
    resize();
  });
}

var mapRefreshBusy = false;
function mapHasDraft() {
  return legEditor.dirty || legEditor.saving || !!locationEditor.draft || locationEditor.busy || state.calibDirty;
}

async function refreshSharedMap() {
  if (!state.map || mapRefreshBusy || mapHasDraft()) { return; }
  mapRefreshBusy = true;
  try {
    var stamp = await getJson('/api/map-revision');
    if (stamp.version === state.map.mapVersion || mapHasDraft()) { return; }
    var data = await getJson('/api/map');
    var edits = await getJson('/api/map-route-legs');
    var after = await getJson('/api/map-revision');
    if (mapHasDraft() || after.version !== data.mapVersion || after.version !== stamp.version) { return; }
    state.map = data; mapLegEdits = edits;
    buildMesh(data); buildPins(data.settlements); buildPlaces(data.places || []);
    buildRoutes(data.routes || [], data.roadGeometries || [], data.seaAirGeometries || []);
    if (MAP_VIEW === 'planar') { refreshLocationOptions(); }
    clearPlannedRoute();
    if (legEditor.draft) { await discardLegDraft(); }
    if (state.selected && pins.some(function (pin) { return pin.data.id === state.selected; })) {
      selectSettlement(state.selected);
    } else {
      state.selected = null; state.market = null;
      ['place-head', 'place-stats', 'place-notes', 'place-prices'].forEach(function (id) {
        document.getElementById(id).textContent = '';
      });
    }
    invalidate();
  } catch (error) { showStatus('Map refresh unavailable: ' + error.message, true); }
  finally { mapRefreshBusy = false; }
}

async function start() {
  buildTerrainLegend();
  wireControls();
  wireRouteAnimation();
  wireLegEditor();
  wireLocationEditor();
  window.setInterval(function () { if (!document.hidden) { refreshSharedMap(); } }, 5000);
  window.addEventListener('focus', refreshSharedMap);
  document.getElementById('planar-radius').addEventListener('change', function (event) {
    setPlanarRadius(event.target.value);
  });
  document.getElementById('planar-grid').addEventListener('change', function (event) {
    state.planarGrid = event.target.value; invalidate();
  });
  document.getElementById('planar-cell').addEventListener('change', function (event) {
    state.planarCell = Number(event.target.value); invalidate();
  });
  document.getElementById('planar-land-detail').addEventListener('change', function (event) {
    state.planarLandDetail = Number(event.target.value); invalidate();
  });
  document.getElementById('planar-boundaries').addEventListener('change', function (event) {
    state.planarBoundaries = event.target.checked; invalidate();
  });
  document.getElementById('planar-poster').addEventListener('change', function (event) {
    state.planarPoster = event.target.checked;
    document.getElementById('planar-poster-alpha').disabled = !state.planarPoster;
    invalidate();
  });
  document.getElementById('planar-poster-alpha').addEventListener('input', function (event) {
    state.planarPosterAlpha = Number(event.target.value) / 100; invalidate();
  });
  document.getElementById('planar-terrain').addEventListener('change', function (event) {
    state.planarTerrain = event.target.checked;
    document.body.setAttribute('data-land-overlay', String(state.planarTerrain));
    document.getElementById('planar-terrain-alpha').disabled = !state.planarTerrain;
    invalidate();
  });
  document.getElementById('planar-terrain-alpha').addEventListener('input', function (event) {
    state.planarTerrainAlpha = Number(event.target.value) / 100; invalidate();
  });
  document.getElementById('planar-center').addEventListener('click', function () {
    var target = state.selected || (findLocation('Waterdeep') || {}).id;
    if (target) { focusSettlement(target); }
  });
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
    if (MAP_VIEW === 'planar') { setMapView('planar'); }
    showStatus('');
    invalidate();
    window.requestAnimationFrame(frame);
    var planParams = new URLSearchParams(window.location.search);
    var savedRouteTypes = state.routeTypes;
    if (savedRouteTypes.length) {
      document.querySelectorAll('input[name="route-type"]').forEach(function (input) {
        input.checked = savedRouteTypes.indexOf(input.value) >= 0;
      });
      document.getElementById('opt-route-all').checked = false;
      state.routeTypes = savedRouteTypes;
      document.getElementById('route-type-summary').textContent = savedRouteTypes.length <= 2
        ? savedRouteTypes.map(routeTypeLabel).join(', ')
        : savedRouteTypes.length + ' types';
    }
    var planPath = planParams.get('planPath');
    var planOrigin = planParams.get('planOrigin');
    var planDestination = planParams.get('planDestination');
    if (planPath) {
      try {
        var names = JSON.parse(planPath);
        if (Array.isArray(names) && names.length > 1) {
          document.getElementById('route-plan-origin').value = names[0];
          document.getElementById('route-plan-destination').value = names[names.length - 1];
          showPlanPath(names);
        }
      } catch (err) { /* malformed deep link: ignore and show the plain map */ }
    } else if (planOrigin && planDestination) {
      document.getElementById('route-plan-origin').value = planOrigin;
      document.getElementById('route-plan-destination').value = planDestination;
      var planOptimise = planParams.get('planOptimise') || 'days';
      document.getElementById('route-plan-cost').checked = planOptimise === 'cost';
      showPlannedRoute(planOrigin, planDestination, planOptimise);
    }
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
