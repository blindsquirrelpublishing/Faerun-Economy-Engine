from faerun.mapassets import MAP_ASSETS, MAP_CSS, MAP_HTML, MAP_JS, TERRAIN_HTML


def test_grid_modes_are_available():
    assert '<option value="square">Square grid</option>' in MAP_HTML
    assert '<option value="towers">Towers</option>' in MAP_HTML
    assert '<option value="hex3">Hex grid' in MAP_HTML
    assert '<option value="hex2">Hex grid' in MAP_HTML
    assert '<option value="hex1">Hex grid' in MAP_HTML
    assert '<option value="hexicon3">Icon hexes' in MAP_HTML
    assert '<option value="hexicon2">Icon hexes' in MAP_HTML
    assert '<option value="hexicon1">Icon hexes' in MAP_HTML
    assert '<option value="hextower3">Hex towers' in MAP_HTML
    assert '<option value="hextower2">Hex towers' in MAP_HTML
    assert '<option value="hextower1">Hex towers' in MAP_HTML


def test_world_grid_cells_can_be_manually_reclassified():
    assert 'id="opt-terrain-edit"' in MAP_HTML
    assert 'id="terrain-edit-type"' in MAP_HTML
    assert '<option value="o">Ocean</option>' in MAP_HTML
    assert '<option value="">Automatic (remove correction)</option>' in MAP_HTML
    assert "function saveTerrainCell(px, py)" in MAP_JS
    assert "postJson('/api/terrain-cell'" in MAP_JS
    assert "column: column, row: row, terrain: terrain" in MAP_JS
    assert "if (state.terrainEditOn)" in MAP_JS


def test_both_map_views_have_location_search_and_camera_focus():
    assert 'id="location-search-form" class="locationsearch"' in MAP_HTML
    assert 'id="location-search" type="search"' in MAP_HTML
    assert 'id="location-options"' in MAP_HTML
    assert 'id="location-search-form" class="locationsearch"' in TERRAIN_HTML
    assert "function findLocation(query)" in MAP_JS
    assert "function focusSettlement(id)" in MAP_JS
    assert "state.tx = pin.sx" in MAP_JS
    assert "state.tz = pin.sz" in MAP_JS
    assert "focusSettlement(location.id)" in MAP_JS
    assert "locationOptions.appendChild(option)" in MAP_JS


def test_grid_strokes_are_drawn_after_poster():
    draw = MAP_JS[MAP_JS.index("function draw()"):MAP_JS.index(
        "var renderBroken"
    )]
    flat_draw = draw[draw.index("if (!state.roundWorld) { clipGroundToPoster(); }"):]
    assert flat_draw.index("drawUnderlay();") < flat_draw.index("drawHexTerrain(true, false, false);")
    assert flat_draw.index("drawUnderlay();") < flat_draw.index("drawSquareGrid();")
    assert flat_draw.index("clipGroundToPoster();") < flat_draw.index("drawUnderlay();")
    assert flat_draw.index("drawSquareGrid();") < flat_draw.index("ctx.restore();")


def test_tile_control_wires_square_and_hex_modes():
    assert "v === 'square'" in MAP_JS
    assert "state.tiles = 'square'" in MAP_JS
    assert "state.tiles = 'hex'" in MAP_JS


def test_round_world_grids_fill_the_ocean_to_the_disk_edge():
    assert "function roundGridSceneBounds()" in MAP_JS
    assert "function drawRoundSquareGrid()" in MAP_JS
    assert "function drawRoundHexGrid()" in MAP_JS
    assert "drawRoundSquareGrid();" in MAP_JS
    assert "var topX = top[0], topY = top[1]" in MAP_JS
    assert "var leftX = left[0], leftY = left[1]" in MAP_JS
    grid_pass = MAP_JS[MAP_JS.index("function drawHexTerrain(gridOnly, towers, icons)"):
                       MAP_JS.index("function drawSquareGrid()")]
    assert "if (gridOnly)" in grid_pass
    assert "drawRoundHexGrid();" in grid_pass


def test_unknown_and_filler_cells_use_the_ocean_palette():
    assert "var DEEP_OCEAN = [" in MAP_JS
    assert "Math.round(PALETTE.o[0] * 0.68)" in MAP_JS
    assert "if (!base)" in MAP_JS
    assert "mesh.colors[idx] = 'rgb(' + DEEP_OCEAN[0]" in MAP_JS
    assert "var ocean = DEEP_OCEAN;" in MAP_JS
    assert "rgb(54, 112, 158)" not in MAP_JS


def test_double_clicking_a_market_loads_local_five_mile_terrain():
    assert "getJson('/api/terrain-detail?settlement='" in MAP_JS
    pointer_up = MAP_JS[MAP_JS.index("function endDrag(ev)"):
                        MAP_JS.index("canvas.addEventListener('pointerup'")]
    assert "now - prior.at < 500" in pointer_up
    assert "var doubleClick = nearbyRepeat && prior.id === id" in pointer_up
    assert "recentMarketClick = { id: id" in pointer_up
    assert "selectSettlement(id);" in pointer_up
    assert "if (doubleClick) { loadTerrainDetail(id); }" in pointer_up
    assert "showStatus('5-mile terrain detail')" in MAP_JS
    assert "state.pitch = 1.35" in MAP_JS
    assert "if (state.detailId && state.map)" in MAP_JS
    assert "buildMesh(state.map);" in MAP_JS
    assert "var b = mesh.detail ? mesh.bounds" in MAP_JS
    assert "? Math.min(width, height)" in MAP_JS


def test_route_segments_can_be_selected_and_isolated_with_details():
    assert 'id="route-selection" class="routeselection" hidden' in MAP_HTML
    assert ".routefacts {" in MAP_CSS
    assert "function pickRoute(mx, my)" in MAP_JS
    assert "pointSegmentDistanceSquared" in MAP_JS
    assert "var routeHit = pickRoute(mx, my)" in MAP_JS
    assert "selectRoute(routeHit)" in MAP_JS
    assert "state.selectedRoute = index" in MAP_JS
    assert "dimmed ? 'rgba(116, 116, 116, .52)'" in MAP_JS
    assert "details.start" in MAP_JS
    assert "details.end" in MAP_JS
    assert "return all.concat(routeLine.details.modes || []);" in MAP_JS
    assert "modes.map(function (mode)" in MAP_JS
    assert "routeTypeIcon(mode)" in MAP_JS
    assert "<span>Type</span>" in MAP_JS
    assert "Math.round(distance).toLocaleString() + ' mi</b>" in MAP_JS
    assert "<span>Travel time</span>" in MAP_JS
    assert "routeTime(days)" in MAP_JS
    assert "function routeTime(days)" in MAP_JS
    assert "function selectedRouteGroup()" in MAP_JS
    assert "function orderedRouteLegs(group)" in MAP_JS
    assert "selectedGroup.indexOf(line) >= 0" in MAP_JS
    assert "<ol class=\"routelegs\">" in MAP_JS
    assert "routeTime(leg.line.details.days)" in MAP_JS


def test_untraced_local_route_legs_use_terrain_routing():
    assert "var tracedRoadLegs = {};" in MAP_JS
    assert "tracedRoadLegs[routeLegKey(roadSpec)] = true" in MAP_JS
    assert "if (tracedRoadLegs[routeLegKey(r)]" in MAP_JS
    assert "if (roadGeometrySpec.length &&" not in MAP_JS
    assert "var landPoints = overland ? landRoute(" in MAP_JS


def test_selected_route_legs_show_available_carriers_and_operating_metrics():
    assert ".carriertable {" in MAP_CSS
    assert "function routeCarrierTable(details, routeIndex)" in MAP_JS
    assert "function routeLoad(pounds)" in MAP_JS
    assert "carrier.cost_gp" in MAP_JS
    assert "carrier.cost_gp_per_ton_mile" in MAP_JS
    assert "carrier.speed_miles_per_day" in MAP_JS
    assert "carrier.max_load_lb" in MAP_JS
    assert "(leg.line === line ? ' open' : '')" in MAP_JS
    assert "' available carriers</summary>'" in MAP_JS


def test_multileg_carrier_selection_expands_to_connected_service_legs():
    assert "selectedCarrierService: ''" in MAP_JS
    assert "function selectRouteCarrier(index, serviceId)" in MAP_JS
    assert "carrier.service_id === state.selectedCarrierService" in MAP_JS
    assert "if (!state.selectedCarrierService) { return [selected]; }" in MAP_JS
    assert r'''onclick="selectRouteCarrier(' + routeIndex + ', \'''' in MAP_JS
    assert "Select all legs" in MAP_JS
    assert "All legs selected" in MAP_JS
    assert '.carrierselect[aria-pressed="true"]' in MAP_CSS


def test_product_selection_draws_its_recursive_supply_chain_routes():
    assert 'id="supply-chain" class="supplychain" hidden' in MAP_HTML
    assert "getJson('/api/supply-chain?settlement='" in MAP_JS
    assert "function collectSupplyRoutes(node)" in MAP_JS
    assert "function supplyRouteMatches(line)" in MAP_JS
    assert "supplyFocus ? supplyRouteMatches(line)" in MAP_JS
    assert "showSupplyChain(id);" in MAP_JS


def test_complex_routes_have_distinct_styling_icon_and_direct_selection():
    assert "var COMPLEX_ROUTE_STYLE = 'rgba(211, 67, 43, .98)'" in MAP_JS
    assert "var GROUND_MULTILEG_ROUTE_STYLE = 'rgba(46, 125, 74, .98)'" in MAP_JS
    assert "function multilegService(line)" in MAP_JS
    assert "function routeDisplayColor(line)" in MAP_JS
    assert "service.service_class === 'ground'" in MAP_JS
    assert "ctx.strokeStyle = dimmed ? 'rgba(116, 116, 116, .52)' : routeDisplayColor(line)" in MAP_JS
    assert "var glyph = complex ? '\u21dd' : routeTypeIcon(line.kind)" in MAP_JS
    assert "Multileg service &middot;" in MAP_JS
    assert "state.selectedCarrierService = service ? service.service_id : ''" in MAP_JS


def test_route_types_can_be_filtered_and_non_road_overland_legs_are_dashed():
    assert 'id="opt-route-types"' in MAP_HTML
    assert 'name="route-type" value="trail"' in MAP_HTML
    assert 'name="route-type" value="track"' not in MAP_HTML
    assert 'id="opt-route-all" checked' in MAP_HTML
    assert "border-top: 5px solid #555" in MAP_CSS
    assert "trail: 'rgba(218, 145, 30, .96)'" in MAP_JS
    assert "track: 'rgba(143, 91, 45, .94)'" not in MAP_JS
    assert "function routeMatchesFilter(line)" in MAP_JS
    assert "if (!routeMatchesFilter(line)) { continue; }" in MAP_JS
    assert "state.routeTypes = routeTypeInputs.filter" in MAP_JS
    assert "modes.some(function (mode) { return state.routeTypes.indexOf(mode) >= 0; })" in MAP_JS


def test_route_type_filter_greys_locations_without_matching_connections():
    assert "function routeConnectedLocationIds()" in MAP_JS
    assert "if (!routeMatchesFilter(line) || !line.details) { return; }" in MAP_JS
    assert "connected.add(line.details.a)" in MAP_JS
    assert "connected.add(line.details.b)" in MAP_JS
    assert "state.routeTypes.length > 0 && !routeConnected.has(s.data.id)" in MAP_JS
    assert "if (disconnected) { return '#969696'; }" in MAP_JS


def test_sea_routes_choose_connected_coastal_anchors():
    assert "function waterCellsNear(wx, wy, radius)" in MAP_JS
    assert "var shorelineDistance = cells[0].distance + 2" in MAP_JS
    assert "candidate.distance <= shorelineDistance" in MAP_JS
    assert "var starts = waterCellsNear(startX, startY, 12)" in MAP_JS
    assert "var ends = waterCellsNear(endX, endY, 12)" in MAP_JS
    assert "function localWaterCells(wx, wy, cells)" in MAP_JS
    assert "starts = localWaterCells(startX, startY, starts)" in MAP_JS
    assert "ends = localWaterCells(endX, endY, ends)" in MAP_JS
    assert "var targets = new Uint8Array(size)" in MAP_JS
    assert "starts.forEach(function (cell)" in MAP_JS
    assert "if (targets[current]) { last = current; break; }" in MAP_JS
    assert "function waterCoastDistance(column, row, radius)" in MAP_JS
    assert "< 1e-5 ? Math.round" in MAP_JS
    assert "[column + 1, row + 1]" in MAP_JS
    assert "waterCoastDistance(next[0], next[1], 4) * 3" in MAP_JS
    assert "if (line.kind === 'trail') { return [7, 5]; }" in MAP_JS


def test_every_route_leg_has_a_type_icon_on_the_map_and_in_details():
    assert "function routeTypeIcon(kind)" in MAP_JS
    assert "function drawRouteIcon(x, y, line, dimmed)" in MAP_JS
    assert "function routeIconPoint(line, exag)" in MAP_JS
    assert 'id="opt-route-icons" type="checkbox" checked' in MAP_HTML
    assert "Icons need their own final pass" in MAP_JS
    assert "if (state.routeIcons) {" in MAP_JS
    assert "state.routeIcons = ev.target.checked;" in MAP_JS
    assert "drawRouteIcon(iconPoint[0], iconPoint[1], iconLine" in MAP_JS
    assert "ctx.arc(x, y, 8, 0, Math.PI * 2)" in MAP_JS
    assert "routeTypeIcon(mode)" in MAP_JS
    assert 'class="routeicon"' in MAP_JS
    assert ".routeicon {" in MAP_CSS


def test_air_routes_use_a_gryphon_icon():
    assert 'name="route-type" value="air"> &#129413; Gryphon flight' in MAP_HTML
    assert "air: 'Gryphon flight'" in MAP_JS
    assert "function drawGryphonIcon(x, y, color)" in MAP_JS
    assert "if (!complex && line.kind === 'air') { drawGryphonIcon(x, y, color); }" in MAP_JS


def test_teleport_routes_have_a_filter_style_and_label():
    assert 'name="route-type" value="teleport"> &#10022; Teleportation circle' in MAP_HTML
    assert "teleport: 'rgba(0, 151, 167, .96)'" in MAP_JS
    assert "teleport: 'Teleportation circle'" in MAP_JS
    assert "line.kind === 'portage' || line.kind === 'teleport'" in MAP_JS
    assert "routeKind === 'air' || routeKind === 'teleport'" in MAP_JS
    assert "r.kind === 'air' || r.kind === 'teleport'" in MAP_JS
    assert "var lifts = elevated ? new Float32Array(pointCount) : null;" in MAP_JS
    assert "var lifts = elevated ? new Float32Array(routeSteps + 1) : null;" in MAP_JS
    assert MAP_JS.count("var bow = elevated ? clamp(span * 0.055, 0.025, 0.11) : 0;") == 2
    assert MAP_JS.count("normalX * bow * arc") == 2
    assert MAP_JS.count("normalZ * bow * arc") == 2


def test_ports_use_boat_icons_and_marker_size_tracks_population():
    assert "function drawPortIcon(x, y, radius)" in MAP_JS
    assert "if (s.data.port) { drawPortIcon(s.px, s.py, r); }" in MAP_JS
    assert "Math.log10(pop / 100) * 1.45" in MAP_JS
    assert "2.5, 10" in MAP_JS


def test_product_filter_draws_price_towers_with_color_height_and_no_price_state():
    assert "function drawPriceTower(pin, radius, selected)" in MAP_JS
    assert "function priceTowerStyle(pin)" in MAP_JS
    assert "height: 14 + 56 * t" in MAP_JS
    assert "return {color: '#858585', height: 10}" in MAP_JS
    assert "drawPriceTower(s, r, selected)" in MAP_JS
    assert "my >= p.towerTop - 5 && my <= p.py + 5" in MAP_JS
    assert "gray = no price" in MAP_JS
    assert "#2a9d4b, #e0a51b, #d52323" in MAP_CSS


def test_location_selection_highlights_connected_route_legs_and_red_pins():
    assert "line.details.a === selectedLocation" in MAP_JS
    assert "line.details.b === selectedLocation" in MAP_JS
    assert "var dimmed = focusOn && !active" in MAP_JS
    assert "state.selectedRoute = -1" in MAP_JS
    assert "return '#d52323'" in MAP_JS
    assert "ctx.strokeStyle = '#ffffff'" in MAP_JS


def test_sea_route_geometry_is_anchored_to_locations_without_legacy_overlap():
    assert "function anchorRoutePoints(points, spec, byId)" in MAP_JS
    assert "waterPoints = anchorRoutePoints(waterPoints, r, byId)" in MAP_JS
    assert "routeSpecByName(route.name, rawPoints, byId, route.from, route.to)" in MAP_JS
    assert "if (specEndpoints === namedEndpoints) { return spec; }" in MAP_JS
    assert "if (!isAir) { return; }" not in MAP_JS


def test_traced_sea_leg_only_matches_its_declared_endpoints():
    import shutil
    import subprocess

    import pytest

    node = shutil.which("node")
    if not node:
        pytest.skip("Node.js is required for the geometry check")
    helper = MAP_JS[MAP_JS.index("function routeSpecByName("):
                    MAP_JS.index("function routeLegKey(")]
    script = """
const assert = require('node:assert/strict');
""" + helper + """
const teziirMarsember = {name:'The Dragonmere',a:'teziir',b:'marsember'};
var routeSpec = [teziirMarsember];
const byId = {
  teziir:{wx:10,wy:20,data:{name:'Teziir'}},
  marsember:{wx:30,wy:40,data:{name:'Marsember'}}
};
const tracedPoints = [[11,21],[29,39]];
assert.equal(
  routeSpecByName('The Dragonmere', tracedPoints, byId, 'Teziir', 'Suzail'),
  null
);
assert.equal(
  routeSpecByName('The Dragonmere', tracedPoints, byId, 'Marsember', 'Teziir'),
  teziirMarsember
);
"""
    subprocess.run([node, "-e", script], check=True, capture_output=True, text=True)


def test_local_detail_has_a_world_view_control():
    assert 'id="view-world" class="ghost worldviewcontrol" hidden' in MAP_HTML
    assert ".worldviewcontrol {" in MAP_CSS
    assert "document.getElementById('view-world').hidden = false" in MAP_JS
    assert "function showWorldView()" in MAP_JS
    assert "addEventListener('click', showWorldView)" in MAP_JS
    assert "document.getElementById('view-world').hidden = true" in MAP_JS


def test_relief_defaults_to_zero():
    assert 'id="opt-exag" type="range" min="0" max="260" value="0"' in MAP_HTML
    assert "exag: 0" in MAP_JS


def test_relief_control_is_shared_with_the_poster_map():
    shared_hud = MAP_HTML[MAP_HTML.index('<div class="hud">'):
                          MAP_HTML.index('<div class="viewcontrols"')]
    assert 'id="opt-exag"' in shared_hud
    view_controls = MAP_HTML[MAP_HTML.index('<div class="viewcontrols"'):
                             MAP_HTML.index('id="view-world"')]
    assert 'id="opt-exag"' not in view_controls


def test_tower_mode_extrudes_cells_from_the_relief_value():
    assert "function drawTowers()" in MAP_JS
    assert "var top = raw * state.exag" in MAP_JS
    assert "drawTowerFace([topPoints[xa], topPoints[xb]" in MAP_JS
    assert "drawTowerFace([topPoints[za], topPoints[zb]" in MAP_JS
    assert "state.tiles === 'towers'" in MAP_JS


def test_hex_tower_modes_draw_camera_facing_walls():
    assert "function drawHexTerrain(gridOnly, towers, icons)" in MAP_JS
    assert "if (towers && hy > 0.00001)" in MAP_JS
    assert "normalX * eyeX + normalZ * eyeZ <= 0" in MAP_JS
    assert "state.tiles === 'hex-towers'" in MAP_JS
    assert "v.indexOf('hextower') === 0" in MAP_JS


def test_icon_hex_modes_draw_terrain_symbols_at_tile_centres():
    assert "function drawTerrainIcon(code, x, y, size)" in MAP_JS
    assert "state.tiles === 'hex-icons'" in MAP_JS
    assert "v.indexOf('hexicon') === 0" in MAP_JS
    assert "drawTerrainIcon(terrainCodeAt(" in MAP_JS
    assert "if (size < 5)" in MAP_JS


def test_3d_view_restores_visible_draped_relief():
    assert 'class="viewcontrols"' in MAP_HTML
    assert "<strong>3D view</strong>" in MAP_HTML
    assert ".viewcontrols { top: auto" not in MAP_CSS
    assert "position: fixed;" in MAP_CSS
    assert "z-index: 2147483647;" in MAP_CSS
    assert "var BASE_EXAG = 0.34" in MAP_JS
    assert "state.pitch = 0.34" in MAP_JS
    assert "state.underDrape = true" in MAP_JS
    assert "ctx.globalCompositeOperation = 'multiply'" in MAP_JS


def test_unified_map_keeps_legacy_terrain_entry_point():
    assert 'data-map-view="overlay"' in MAP_HTML
    assert 'data-map-view="terrain"' in TERRAIN_HTML
    assert "Poster map" in MAP_HTML
    assert "3D terrain" in MAP_HTML
    assert "terrain.html" in MAP_ASSETS
    assert "MAP_VIEW === 'overlay' ? 1.45 : 0.50" in MAP_JS
    assert "state.underOn = true" in MAP_JS
    assert "state.underOn = false" in MAP_JS
    assert "exag: 0" in MAP_JS


def test_map_view_switch_preserves_exploration_state():
        import shutil
        import subprocess

        import pytest

        node = shutil.which("node")
        if not node:
                pytest.skip("Node.js is required for the map interaction check")
        switch = MAP_JS[MAP_JS.index("function setMapView(view)"):
                                        MAP_JS.index("function applyUnderlayImage(img)")]
        script = """
const assert = require('node:assert/strict');
var MAP_VIEW = 'overlay';
var mapViewChanged = false;
var state = {
    under: {}, underOn: true, calibOn: true, calibArmed: 'waterdeep',
    selected: 'daggerford', selectedRoute: 4, heat: 'bread',
    tx: 300, tz: 500, dist: 2.4, pitch: 1.45, yaw: 0.1,
    selectedCarrierService: 'caravan', detailId: 'daggerford', exag: 0.7
};
const before = {...state};
const radios = [{value: 'overlay'}, {value: 'terrain'}];
var bodyView;
var checkbox = {checked: true};
var document = {
    body: {setAttribute: (name, value) => {if (name === 'data-map-view') bodyView = value;}},
    querySelectorAll: () => radios,
    getElementById: () => checkbox
};
var canvas = {classList: {remove: () => {}}};
var window = {
    location: {href: 'http://localhost/terrain.html?settlement=daggerford'},
    history: {replaceState: (data, title, url) => {window.location.href = String(url);}}
};
var syncUnderlayControls = () => {};
var invalidate = () => {};
var resize = () => {};
var posterOnlyActive = () => MAP_VIEW === 'overlay' && !!state.posterOnly;
""" + switch + """
setMapView('terrain');
assert.equal(state.underOn, false);
assert.equal(state.calibOn, false);
assert.equal(checkbox.checked, false);
assert.equal(bodyView, 'terrain');
assert.equal(radios[1].checked, true);
assert.equal(new URL(window.location.href).pathname, '/map.html');
setMapView('overlay');
assert.equal(state.underOn, true);
assert.equal(bodyView, 'overlay');
assert.equal(radios[0].checked, true);
assert.equal(new URL(window.location.href).searchParams.get('settlement'), 'daggerford');
assert.equal(new URL(window.location.href).searchParams.get('view'), 'overlay');
for (const key of ['selected', 'selectedRoute', 'heat', 'tx', 'tz', 'dist',
                                     'pitch', 'yaw', 'selectedCarrierService', 'detailId', 'exag']) {
    assert.equal(state[key], before[key], key);
}
setMapView('invalid');
assert.equal(MAP_VIEW, 'overlay');
"""
        subprocess.run([node, "-e", script], check=True, capture_output=True, text=True)


def test_route_inspector_summarizes_all_legs_and_can_clear_selection():
        import shutil
        import subprocess

        import pytest

        node = shutil.which("node")
        if not node:
                pytest.skip("Node.js is required for the route interaction check")
        render = MAP_JS[MAP_JS.index("function updateRouteSelection()"):
                                        MAP_JS.index("function selectRoute(index)")]
        script = """
const assert = require('node:assert/strict');
const panel = {hidden: true, innerHTML: ''};
const document = {getElementById: () => panel};
const state = {selectedRoute: 0};
const routeLines = [
    {details: {name: 'Coastal service', start: 'Alpha', end: 'Bravo',
        modes: ['road'], distance: 24, days: 1, carriers: []}},
    {details: {name: 'Coastal service', start: 'Bravo', end: 'Charlie',
        modes: ['sea', 'road'], distance: 72, days: 1, carriers: []}}
];
const selectedRouteGroup = () => routeLines;
const orderedRouteLegs = group => group.map(line => ({line, reverse: false}));
const multilegService = () => ({service_id: 'coastal'});
const esc = value => String(value);
const routeTypeIcon = () => '';
const routeTypeLabel = mode => mode;
const routeTime = days => days + ' days';
const routeCarrierTable = () => '';
""" + render + """
updateRouteSelection();
assert.equal(panel.hidden, false);
assert.ok(panel.innerHTML.includes('96 mi'));
assert.ok(panel.innerHTML.includes('<b>2 days</b>'));
assert.ok(panel.innerHTML.includes('<span>Legs</span><b>2</b>'));
const modes = panel.innerHTML.match(/<p class="routemodes">(.*?)<\\/p>/)[1];
assert.equal((modes.match(/road/g) || []).length, 1);
assert.ok(modes.includes('sea'));
assert.ok(panel.innerHTML.includes('origin=Alpha&destination=Charlie'));
assert.ok(panel.innerHTML.includes('aria-label="Clear route selection"'));
state.selectedRoute = -1;
updateRouteSelection();
assert.equal(panel.hidden, true);
assert.equal(panel.innerHTML, '');
"""
        subprocess.run([node, "-e", script], check=True, capture_output=True, text=True)


def test_poster_only_keeps_locations_and_route_legs():
    import shutil
    import subprocess

    import pytest

    node = shutil.which("node")
    if not node:
        pytest.skip("Node.js is required for the rendering check")
    draw = MAP_JS[MAP_JS.index("function draw()"):
                  MAP_JS.index("var renderBroken")]
    helper = MAP_JS[MAP_JS.index("function posterOnlyActive()"):
                    MAP_JS.index("function drawUnderlay()")]
    script = """
const assert = require('node:assert/strict');
const mesh = {};
const state = {posterOnly: true, routes: true, labels: true, selected: 'daggerford'};
let MAP_VIEW = 'overlay';
const calls = [];
const updateCamera = () => calls.push('camera');
const drawSky = () => calls.push('sky');
const drawUnderlay = () => calls.push('poster');
const drawPlaces = () => calls.push('places');
const drawRoutes = () => calls.push('routes');
const drawPins = () => calls.push('pins');
const ctx = {save: () => calls.push('save'), restore: () => calls.push('restore')};
""" + helper + draw + """
draw();
assert.deepEqual(calls, ['camera', 'sky', 'save', 'poster', 'places', 'routes', 'pins', 'restore']);
assert.equal(state.routes, true);
assert.equal(state.labels, true);
assert.equal(state.selected, 'daggerford');
calls.length = 0;
state.routes = false;
draw();
assert.deepEqual(calls, ['camera', 'sky', 'save', 'poster', 'places', 'pins', 'restore']);
MAP_VIEW = 'terrain';
assert.equal(posterOnlyActive(), false);
"""
    subprocess.run([node, "-e", script], check=True, capture_output=True, text=True)
    assert 'id="poster-only"' in MAP_HTML
    assert "ctx.globalAlpha = posterOnly ? 1 : state.underAlpha" in MAP_JS
    assert MAP_JS.count("if (posterOnlyActive()) { return -1; }") == 1
    assert "if (drag.moved < 5 && !drag.pan)" in MAP_JS


def test_overlay_frame_uses_exact_poster_aspect():
    assert "function posterBounds()" in MAP_JS
    assert "img.width * state.underMpp" in MAP_JS
    assert "img.height * state.underMpp * state.underStretch" in MAP_JS
    assert "var b = mesh.detail ? mesh.bounds : (posterBounds() || mesh.bounds);" in MAP_JS
    assert "function clipGroundToPoster()" in MAP_JS


def test_round_world_frame_filters_ground_without_clipping_towers_or_markers():
    assert 'id="opt-round-world" checked' not in MAP_HTML
    assert 'id="opt-round-world"' in MAP_HTML
    assert "roundWorld: false" in MAP_JS
    assert "function clipRoundWorld()" in MAP_JS
    assert "function drawRoundWorldBase()" in MAP_JS
    assert "function drawRoundWorldEdge()" in MAP_JS
    assert "Math.sqrt(width * width + height * height)" in MAP_JS
    assert "state.roundWorld = ev.target.checked" in MAP_JS
    assert "state.roundWorld ? roundWorldBounds()" in MAP_JS
    assert "state.tx = centre[0]" in MAP_JS
    assert "state.tz = centre[1]" in MAP_JS
    assert "if (state.roundWorld) { state.dist *= 1.06; }" in MAP_JS
    drawing = MAP_JS[MAP_JS.index("function draw()"):MAP_JS.index(
        "var renderBroken"
    )]
    flat_drawing = drawing[drawing.index("if (!state.roundWorld) { clipGroundToPoster(); }"):]
    assert "if (!state.roundWorld) { clipGroundToPoster(); }" in flat_drawing
    assert flat_drawing.index("drawRoundWorldBase();") < flat_drawing.index("drawTerrain();")
    assert flat_drawing.index("clipRoundWorld();") > flat_drawing.index("drawUnderlay();")
    assert flat_drawing.index("ctx.restore();") < flat_drawing.index("drawPlaces();")
    assert "function scenePointInRoundWorld(x, z)" in MAP_JS
    assert "scenePointInRoundWorld((x0 + x1) / 2" in MAP_JS
    assert "scenePointInRoundWorld(cxw, cz)" in MAP_JS


def test_globe_view_wraps_map_layers_onto_a_sphere():
    assert 'id="opt-globe"' in MAP_HTML
    assert 'id="opt-globe"' in TERRAIN_HTML
    assert "globe: false" in MAP_JS
    assert "function projectGlobe(x, y, z)" in MAP_JS
    assert "function drawGlobeTerrain()" in MAP_JS
    assert "cells.sort(function (a, b) { return b.depth - a.depth; })" in MAP_JS
    assert "function drawGlobeBase()" in MAP_JS
    assert "if (state.globe) { return projectGlobe(x, y, z); }" in MAP_JS
    assert "state.globeTilt = clamp" in MAP_JS
    assert "state.globeZoom = clamp" in MAP_JS
    assert "document.getElementById('opt-round-world').checked = false" in MAP_JS
    assert "document.getElementById('opt-globe').checked = state.globe" in MAP_JS
    assert "if (!state.globe) { return []; }" in MAP_JS
    assert "var angles = globeAngles(pin.sx, pin.sz)" in MAP_JS
    assert "var FAERUN_AREA_SQ_MI = 9500000" in MAP_JS
    assert "var FAERUN_TORIL_LAND_SHARE = 0.15" in MAP_JS
    assert "var GLOBE_FAERUN_WEST = -55 * Math.PI / 180" in MAP_JS
    assert "var GLOBE_FAERUN_EAST = 55 * Math.PI / 180" in MAP_JS
    assert "var GLOBE_FAERUN_NORTH = 80 * Math.PI / 180" in MAP_JS
    assert "var GLOBE_FAERUN_SOUTH = -5 * Math.PI / 180" in MAP_JS
    assert "globeTilt: GLOBE_HOME_TILT" in MAP_JS
    globe_base = MAP_JS[MAP_JS.index("function drawGlobeBase()"):
                        MAP_JS.index("function drawTerrain()")]
    assert "DEEP_OCEAN" in globe_base


def test_globe_price_towers_follow_the_local_surface_normal():
    assert "function drawGlobePriceTower(pin, width, style, selected)" in MAP_JS
    assert "var normalX = pin.px - cam.cx" in MAP_JS
    assert "var normalY = pin.py - cam.cy" in MAP_JS
    assert "var radialScale = radialDistance / Math.max(1, globeRadius())" in MAP_JS
    assert "var tipX = pin.px + normalX * projectedHeight" in MAP_JS
    assert "var tipY = pin.py + normalY * projectedHeight" in MAP_JS
    assert "pointSegmentDistanceSquared(mx, my" in MAP_JS
    assert "state.heatById ? s.towerTipX : s.px" in MAP_JS
    assert "state.heatById ? s.towerTipY : s.py" in MAP_JS


def test_terrain_legend_reports_all_applied_survey_cells():
    assert "survey.appliedSamples || survey.matched || 0" in MAP_JS
    assert "survey.locations || 0" in MAP_JS
    assert "survey.mode === 'full-grid'" in MAP_JS
    assert "survey.sourceCells || 0" in MAP_JS


def test_terrain_uses_category_colors_on_both_pages():
    assert "o: [70, 132, 180]" in MAP_JS
    assert "p: [174, 205, 112]" in MAP_JS
    assert "f: [62, 132, 73]" in MAP_JS
    assert "d: [226, 192, 112]" in MAP_JS
    assert "body[data-map-view=\"overlay\"] .terrainlegend" not in MAP_CSS
    assert "var waterShade = 1 - depth * 0.32;" in MAP_JS


def test_traced_roads_replace_straight_road_chords_and_use_color():
    assert "roadGeometrySpec = roadGeometries || []" in MAP_JS
    assert "roadNetwork.segments.forEach(function (road)" in MAP_JS
    assert "tracedRoadLegs[routeLegKey(roadSpec)] = true" in MAP_JS
    assert "if (tracedRoadLegs[routeLegKey(r)]" in MAP_JS
    assert "r.kind === 'road' || r.kind === 'trail'" in MAP_JS
    assert "road: 'rgba(190, 72, 28, .98)'" in MAP_JS
    assert "sea: 'rgba(0, 110, 196, .96)'" in MAP_JS
    assert "ctx.lineWidth = width + 2.4" in MAP_JS


def test_bezier_routes_preserve_waypoints_and_hidden_globe_gaps():
    import shutil
    import subprocess

    import pytest

    node = shutil.which("node")
    if not node:
        pytest.skip("Node.js is required for the geometry check")
    helper = MAP_JS[MAP_JS.index("function routeBezierSegments(points)"):
                    MAP_JS.index("function drawRoutes()")]
    script = "const assert = require('node:assert/strict');\n" + helper + """
const points = [[0,0],[100,0],[100,100]];
const segments = routeBezierSegments(points);
assert.equal(segments.length,2);
segments.forEach((segment,index) => {
  assert.deepEqual(routeBezierPoint(segment,0),points[index]);
  assert.deepEqual(routeBezierPoint(segment,1),points[index+1]);
  assert.ok(Math.hypot(segment[1][0]-segment[0][0],segment[1][1]-segment[0][1])<=12.000001);
  assert.ok(Math.hypot(segment[2][0]-segment[3][0],segment[2][1]-segment[3][1])<=12.000001);
});
assert.ok(routeBezierPoint(segments[0],0.5)[1]<0);
assert.deepEqual(routeBezierPoint(routeBezierSegments([[0,0],[100,0]])[0],0.5),[50,0]);
assert.ok(routeBezierSegments([[0,0],[0,0],[1,1]]).flat(2).every(Number.isFinite));
assert.deepEqual(routeBezierSegments([]),[]);
var state = {exag:1,globe:true};
const projectionBuffer = [0,0];
function project(horizontal,height,depth) {
    projectionBuffer[0]=horizontal;
    projectionBuffer[1]=depth;
    return horizontal===2 ? null : projectionBuffer;
}
const line = {xs:[0,1,2,3,4],hs:[0,0,0,0,0],zs:[0,0,0,0,0]};
const runs = projectedRouteCurves(line);
assert.equal(runs.length,2);
assert.deepEqual(runs[0][0][3],[1,0]);
assert.deepEqual(runs[1][0][0],[3,0]);
state.globe=false;
assert.deepEqual(projectedRouteCurves(line),[]);
"""
    subprocess.run([node, "-e", script], check=True, capture_output=True, text=True)
    assert "ctx.bezierCurveTo(segment[1][0]" in MAP_JS
    assert "routeBezierPoint(segment, step / 8)" in MAP_JS


def test_inferred_caravan_routes_are_hidden_unless_enabled():
    import shutil
    import subprocess

    import pytest

    node = shutil.which("node")
    if not node:
        pytest.skip("Node.js is required for the route visibility check")
    helper = MAP_JS[MAP_JS.index("function routeMatchesFilter(line)"):
                    MAP_JS.index("function routeConnectedLocationIds()")]
    script = "const assert = require('node:assert/strict');\n" + helper + """
var state = {routeTypes: [], inferredRoads: false};
const caravan = {kind:'track',inferredRoad:true,details:{modes:['track']}};
assert.equal(routeMatchesFilter(caravan),false);
assert.equal(routeMatchesFilter({kind:'trail',traced:true}),true);
state.inferredRoads=true;
assert.equal(routeMatchesFilter(caravan),true);
state.routeTypes=['sea'];
assert.equal(routeMatchesFilter(caravan),false);
"""
    subprocess.run([node, "-e", script], check=True, capture_output=True, text=True)
    assert "inferredRoad: !!r.inferred ||" in MAP_JS
    assert "Model-generated connection (not a mapped road or trail)" in MAP_JS
    assert "Inferred routes" in MAP_HTML


def test_traced_network_splits_corridors_and_deduplicates_reversed_traces():
    import shutil
    import subprocess

    import pytest

    node = shutil.which("node")
    if not node:
        pytest.skip("Node.js is required for the geometry check")
    helper = MAP_JS[MAP_JS.index("function tracedRoadNetwork(roads)"):
                    MAP_JS.index("function buildRoutes(list")]
    script = """
const assert = require('node:assert/strict');
""" + helper + """
const network = tracedRoadNetwork([
  {name:'West road',surface:'road',locations:['west','junction','east'],
   anchors:[0,2,4],points:[[0,0],[1,2],[2,0],[3,2],[4,0]]},
  {name:'Renamed duplicate',surface:'road',locations:['east','junction'],
   anchors:[0,2],points:[[4,0],[3,2],[2,0]]},
  {name:'Branch',surface:'road',locations:['junction','south'],
   anchors:[0,2],points:[[2,0],[2,-1],[2,-2]]}
]);
assert.equal(network.segments.length,3);
assert.deepEqual(network.segments[0].points,[[0,0],[1,2],[2,0]]);
assert.equal(network.segments[0].a,'west');
assert.equal(network.segments[0].b,'junction');
assert.equal(network.connects('west','south'),true);
assert.equal(network.connects('south','west'),true);
assert.equal(network.connects('east','untraced'),false);
"""
    subprocess.run([node, "-e", script], check=True, capture_output=True, text=True)
    assert "r.kind === 'road' && roadNetwork.connects(r.a, r.b)" in MAP_JS
    assert "if (line.inferredRoad && !state.inferredRoads) { return false; }" in MAP_JS


def test_water_routed_sea_and_air_geometry_replaces_straight_chords():
    assert "seaAirGeometrySpec = seaAirGeometries || []" in MAP_JS
    assert "seaAirGeometrySpec.forEach(function (route)" in MAP_JS
    assert "function routeLegKey(spec)" in MAP_JS
    assert "tracedSeaAirLegs[routeLegKey(tracedSpec)]" in MAP_JS
    assert "tracedSeaAirLegs[routeLegKey(r)]" in MAP_JS
    assert "mode === 'sea' || mode === 'air'" in MAP_JS
    assert "state.map.seaAirGeometries || []" in MAP_JS
    assert "air: 'rgba(189, 36, 123, .92)'" in MAP_JS
    assert "var crest = clamp(span * 0.12, 0.035, 0.18);" in MAP_JS
    assert "var arc = Math.sin(Math.PI * progress);" in MAP_JS
    assert "lifts[i] = arc * crest" in MAP_JS
    assert "line.hs[index] * state.exag + lift + 0.004" in MAP_JS


def test_generated_sea_lanes_are_routed_over_water_without_a_straight_fallback():
    assert "function waterRoute(startX, startY, endX, endY)" in MAP_JS
    assert "code === 'o' || code === 'w'" in MAP_JS
    assert "function waterCoastDistance(column, row, radius)" in MAP_JS
    assert "waterCoastDistance(next[0], next[1], 4) * 3" in MAP_JS
    assert "function smoothWaterCells(cells)" in MAP_JS
    assert "fractionalWaterSegmentIsClear(before, after)" in MAP_JS
    assert "!fractionalWaterSegmentIsClear(smooth[segment - 1], smooth[segment])" in MAP_JS
    assert "!fractionalWaterSegmentIsClear(cells[from], cells[to])" in MAP_JS
    assert "Math.min(cells.length - 1, from + 8)" in MAP_JS
    assert "function plausibleCoastingRoute(spec, points)" in MAP_JS
    assert "polylineMiles(points) <= Number(spec.distance) * 2" in MAP_JS
    assert "if (!plausibleCoastingRoute(r, waterPoints)) { return; }" in MAP_JS
    assert "return simple.map(function (cell)" in MAP_JS
    assert "var waterXs = new Array(waterPoints.length)" in MAP_JS
    assert "var waterZs = new Array(waterPoints.length)" in MAP_JS
    assert "var waterGoing = r.kind === 'sea' || r.kind === 'ferry'" in MAP_JS
    assert "var waterPoints = waterGoing ? waterRoute" in MAP_JS
    assert "if (waterGoing && !waterPoints) { return; }" in MAP_JS
    assert "waterRouted: true" in MAP_JS


def test_generated_land_routes_are_routed_without_water_fallbacks():
    assert "function isLandCell(column, row)" in MAP_JS
    assert "function landRoute(startX, startY, endX, endY)" in MAP_JS
    assert "fractionalLandSegmentIsClear(cells[from], cells[to])" in MAP_JS
    assert "var overland = r.kind === 'road' || r.kind === 'trail'" in MAP_JS
    assert "var landPoints = overland ? landRoute" in MAP_JS
    assert "if (overland && !landPoints) { return; }" in MAP_JS
    assert "isFootRoute ? rawPoints : anchorRoutePoints" in MAP_JS
    assert "if (!points || points.length < 2) { return; }" in MAP_JS
    assert "if (tracedRoadLegs[routeLegKey(r)]" in MAP_JS
    assert "rawPoints = landRoute(trailStart.wx" not in MAP_JS
    assert "landPoints = anchorRoutePoints(landPoints" not in MAP_JS
    assert "if (isLandCell(startColumn, startRow)) { points[0] = [startX, startY]; }" in MAP_JS
    assert "if (isLandCell(endColumn, endRow)) { points[points.length - 1] = [endX, endY]; }" in MAP_JS
    assert "landRouted: true" in MAP_JS
