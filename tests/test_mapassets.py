from faerun.mapassets import MAP_ASSETS, MAP_CSS, MAP_HTML, MAP_JS, TERRAIN_HTML


def test_map_defaults_to_2d_and_surface_routes():
        import shutil
        import subprocess

        import pytest

        node = shutil.which('node')
        if not node:
                pytest.skip('Node.js is required for map behavior checks')
        assert 'data-map-view="planar"' in MAP_HTML
        assert 'name="map-view" value="planar" checked' in MAP_HTML
        for html in (MAP_HTML, TERRAIN_HTML):
            assert '<option value="none" selected>None</option><option value="hex">Hex</option>' in html
        start = MAP_JS.index('var MAP_VIEW =')
        end = MAP_JS.index('\n};', MAP_JS.index('var state =', start)) + 3
        code = MAP_JS[start:end]
        visible = MAP_JS[MAP_JS.index('function planarLegVisible('):]
        visible = visible[:visible.index('\n}') + 2]
        script = """
const assert = require('node:assert/strict');
const vm = require('node:vm');
function initialize(search, view='planar') {
    const context = {URLSearchParams, GLOBE_HOME_TILT:0, window:{location:{search}},
        document:{body:{getAttribute:()=>view,setAttribute:()=>{}}}};
    vm.createContext(context);
    vm.runInContext(CODE + '\\n' + VISIBLE, context);
    return context;
}
let context=initialize('');
assert.equal(context.MAP_VIEW,'planar');
assert.equal(context.state.planarGrid,'none');
for (const kind of ['road','trail','track','sea','river','barge','ferry','portage','tunnel']) {
    assert(context.planarLegVisible({kind}),kind);
}
for (const kind of ['air','skyship','teleport']) {
    assert(!context.planarLegVisible({kind}),kind);
    assert(!context.state.routeTypes.includes(kind),kind);
}
context=initialize('?view=overlay&routeTypes=sea,air');
assert.equal(context.MAP_VIEW,'overlay');
assert(context.planarLegVisible({kind:'air'}));
assert(!context.planarLegVisible({kind:'road'}));
context=initialize('?routeTypes=');
assert(context.planarLegVisible({kind:'teleport'}));
assert.equal(initialize('', 'terrain').MAP_VIEW,'terrain');
"""
        import json

        script = 'const CODE=' + json.dumps(code) + ';const VISIBLE=' + json.dumps(visible) + ';' + script
        subprocess.run([node, '--check'], input=MAP_JS, encoding='utf-8', check=True)
        subprocess.run([node, '-e', script], encoding='utf-8', check=True)


def test_verified_visibility_and_catalog_location_type_controls():
    import json
    import shutil
    import subprocess

    import pytest

    node = shutil.which('node')
    if not node:
        pytest.skip('Node.js is required for map behavior checks')
    def source(name):
        start = MAP_JS.index('function ' + name + '(')
        return MAP_JS[start:MAP_JS.index('\n}', start) + 2]
    code = '\n'.join(source(name) for name in ('locationType', 'locationIsPort', 'locationVisible', 'syncLocationEditor', 'editableLocations'))
    script = """
const assert=require('node:assert/strict');
const state={verifiedOnly:true,map:{settlements:[{id:'town',verified:false}],places:[]}};
const controls={};
const document={getElementById(id){return controls[id] ||= {setAttribute(){}};}};
const locationEditor={enabled:true,busy:false,draft:{id:'town',name:'Town',placeType:'mine',verified:true}};
const legEditor={ready:true,saving:false};
""" + code + """
assert(!locationVisible({}));
assert(!locationVisible({verified:false}));
assert(locationVisible({verified:true}));
assert(locationVisible({mobile:true}));
assert.equal(editableLocations().length,1);
state.verifiedOnly=false;assert(locationVisible({}));
syncLocationEditor();
assert.equal(controls['location-edit-type'].disabled,false);
assert.equal(controls['location-edit-type'].value,'mine');
assert.equal(controls['location-edit-verified'].disabled,false);
assert.equal(controls['location-edit-verified'].checked,true);
assert.equal(controls['location-edit-port'].disabled,false);
locationEditor.draft.isPort=true;syncLocationEditor();
assert.equal(controls['location-edit-port'].checked,true);
assert.equal(controls['location-edit-type'].value,'mine');
for (const [control,attribute] of [['portal','portalGate'],['gryphon','gryphonPort']]) {
 assert.equal(controls['location-edit-'+control].disabled,false);
 assert.equal(controls['location-edit-'+control].checked,false);
 locationEditor.draft[attribute]=true;syncLocationEditor();
 assert.equal(controls['location-edit-'+control].checked,true);
}
assert.equal(controls['location-edit-type'].value,'mine');
locationEditor.busy=true;syncLocationEditor();
assert.equal(controls['location-edit-type'].disabled,true);
locationEditor.busy=false;locationEditor.draft=null;syncLocationEditor();
assert.equal(controls['location-edit-type'].disabled,true);
"""
    subprocess.run([node, '--check'], input=MAP_JS, encoding='utf-8', check=True)
    subprocess.run([node, '-e', script], encoding='utf-8', check=True)
    assert 'verifiedOnly: true' in MAP_JS
    assert 'if (!locationVisible(pin.data)) { continue; }' in MAP_JS
    assert 'if (!locationVisible(d.data)) { continue; }' in MAP_JS
    assert 'verified: !!draft.verified' in MAP_JS
    assert 'portalGate: !!draft.portalGate, gryphonPort: !!draft.gryphonPort' in MAP_JS


def test_location_type_choices_match_saved_types():
    import re

    from faerun.locationedits import PLACE_TYPES

    start = MAP_JS.index('var PLACE_TYPES =')
    choices = dict(re.findall(r"(\w+): '([^']+)'", MAP_JS[start:MAP_JS.index('};', start)]))
    assert set(choices) == PLACE_TYPES
    assert choices["caravan_stop"] == "Caravan Stop"
    assert choices["trading_post"] == "Trading Post"


def test_poster_location_icons_are_cached_and_fit_inside_circles():
    import shutil
    import subprocess

    import pytest

    node = shutil.which('node')
    if not node:
        pytest.skip('Node.js is required for map behavior checks')
    start = MAP_JS.index('var PLACE_TYPES =')
    code = MAP_JS[start:MAP_JS.index('function nearestRoadsidePoint(', start)]
    script = """
const assert=require('node:assert/strict');
let crops=0, draws=0, clips=0, depth=0;
const state={under:{width:4763,height:3185}};
const document={createElement(){return {getContext(){return {
 drawImage(image,x,y,width,height){assert(x>=0 && x+width<=image.width);assert(y>=0 && y+height<=image.height);crops++;},
 getImageData(){const data=new Uint8ClampedArray(60*32*4).fill(255);
  for(let row=10;row<22;row++)for(let column=24;column<36;column++){
   const offset=(row*60+column)*4;data[offset]=data[offset+1]=data[offset+2]=0;
  }return {data};},
 putImageData(pixels){assert.equal(pixels.data[(10*60+24)*4+3],255);assert.equal(pixels.data[7],0);}
};}};}};
const ctx={save(){depth++;},restore(){depth--;},beginPath(){},arc(){},clip(){clips++;},
 drawImage(image,sx,sy,sw,sh,x,y,width,height){assert.deepEqual([sx,sy,sw,sh],[24,10,12,12]);
  assert.equal(width,14);assert.equal(height,14);assert.equal(x,13);assert.equal(y,13);draws++;}};
""" + code + """
assert.equal(locationType({port:true}),'city');
assert.equal(locationIconType({port:true}),'port');
assert.equal(locationIconType({placeType:'capital',isPort:true}),'port_capital');
assert.equal(locationIconType({placeType:'capital',port:'Sea',isPort:false}),'capital');
assert.equal(locationIconType({placeType:'fortress',isPort:true}),'fortress');
assert(!('port' in PLACE_TYPES));assert(!('port_capital' in PLACE_TYPES));
assert.equal(locationType({}),'city');
assert.equal(locationType({port:true,placeType:'capital'}),'capital');
for(const kind of ['city','port','fortress','ruin','site','capital','port_capital','temple','bridge']) {
 assert(LOCATION_LEGEND_ROWS[kind]);
 drawLocationTypeIcon({placeType:kind},20,20,10);
 drawLocationTypeIcon({placeType:kind},20,20,10);
}
assert.equal(crops,9);assert.equal(draws,18);assert.equal(clips,18);assert.equal(depth,0);
drawLocationTypeIcon({placeType:'cave'},20,20,10);assert.equal(draws,18);
state.under=null;drawLocationTypeIcon({placeType:'city'},20,20,10);assert.equal(draws,18);
state.under={width:4763,height:3185};drawLocationTypeIcon({placeType:'city'},20,20,10);
assert.equal(crops,10);
"""
    subprocess.run([node, '-e', script], encoding='utf-8', check=True)


def test_tracks_are_red_dashed_and_trails_yellow_dotted_half_width():
    import shutil
    import subprocess

    import pytest

    node = shutil.which('node')
    if not node:
        pytest.skip('Node.js is required for map behavior checks')
    def source(name):
        start = MAP_JS.index('function ' + name + '(')
        return MAP_JS[start:MAP_JS.index('\n}', start) + 2]
    code = '\n'.join(source(name) for name in ('routeDisplayColor', 'routeLineDash', 'strokePlanarLeg'))
    script = """
const assert=require('node:assert/strict');
const state={planarRadius:200};const strokes=[];
const ctx={setLineDash(values){this.dash=values;},stroke(){strokes.push(this.lineWidth);}};
""" + code + """
assert.equal(routeDisplayColor({kind:'track',multi:true}),'#d52323');
assert.equal(routeDisplayColor({kind:'trail',multi:true}),'#ffcd44');
assert.deepEqual(routeLineDash({kind:'track',multi:true}),[7,14]);
assert.deepEqual(routeLineDash({kind:'trail',multi:true}),[0,8]);
for(const radius of [50,100,200,500]) {
 state.planarRadius=radius;strokes.length=0;
 strokePlanarLeg('#d52323',4,routeLineDash({kind:'track'}));const normal=strokes.splice(0);
 assert(ctx.dash[1]>normal[0]);
 strokePlanarLeg('#ffcd44',4,[0,8],0.5);
 assert.deepEqual(strokes,normal.map(width=>width/2));
 assert.equal(ctx.lineCap,'round');assert.deepEqual(ctx.dash,[0,8*200/radius]);
}
"""
    subprocess.run([node, '-e', script], encoding='utf-8', check=True)


def test_curved_leg_geometry_preserves_waypoints_and_bounds():
    import shutil
    import subprocess

    import pytest

    node = shutil.which('node')
    if not node:
        pytest.skip('Node.js is required for map behavior checks')
    code = MAP_JS[MAP_JS.index('function curvedLegGeometry('):MAP_JS.index('function insertLegWaypoint(')]
    script = """
const assert = require('node:assert/strict');
const mesh = {bounds:[0,0],cellW:5,cellH:5};
let clear=true;
function fractionalWaterSegmentIsClear(){return clear;}
""" + code + """
const points=[[0,0],[20,20],[40,0]];
const curved=curvedLegGeometry(points,0.8,false);
assert.deepEqual(curved.points,points);
assert(curved.path.length>points.length);
assert.deepEqual(curved.pointIndices.map(index=>curved.path[index]),points);
assert(curved.path.some(point=>point[0]>0 && point[0]<20 && point[1]>point[0]));
assert.deepEqual(curvedLegGeometry(points,0,false).points,points);
assert.deepEqual(curvedLegGeometry(points,0.8,true),curved);
clear=false;
assert.deepEqual(curvedLegGeometry(points,0.8,true).path,points);
assert.deepEqual(points,[[0,0],[20,20],[40,0]]);
assert.throws(()=>curvedLegGeometry([[0,0],[30000,0]],1,false),/limit/);
"""
    subprocess.run([node, '--check'], input=MAP_JS, encoding='utf-8', check=True)
    subprocess.run([node, '-e', script], encoding='utf-8', check=True)


def test_coastal_leg_targets_fifteen_miles_and_avoids_land():
    import shutil
    import subprocess

    import pytest

    node = shutil.which('node')
    if not node:
        pytest.skip('Node.js is required for map behavior checks')
    water = MAP_JS[MAP_JS.index('function waterCellsNear('):MAP_JS.index('function polylineMiles(')]
    curves = MAP_JS[MAP_JS.index('function curvedLegGeometry('):MAP_JS.index('function reshapeLeg(')]
    script = """
const assert = require('node:assert/strict');
let mesh={W:40,H:16,cellW:5,cellH:5,bounds:[0,0,200,80]};
function isWaterCell(column,row){return column>=0 && column<mesh.W && row>=1 && row<mesh.H;}
""" + water + curves + """
let route=routedWaterPath(12.5,7.5,187.5,7.5,15);
assert(route.some((point,index)=>index>0 && route[index-1][0]<100 && point[0]>100 &&
    Math.abs(point[1]-20)<=2.5 && Math.abs(route[index-1][1]-20)<=2.5));
assert(route.every(point=>point[1]>=5));
const curved=coastalLegGeometry([[12.5,7.5],[187.5,7.5]],0.8);
assert.deepEqual(curved.path[0],[12.5,7.5]);
assert.deepEqual(curved.path.at(-1),[187.5,7.5]);
assert.deepEqual(curved.pointIndices.map(index=>curved.path[index]),curved.points);
assert(curved.path.every(point=>point[1]>=5));
const waterCell=isWaterCell;
isWaterCell=(column,row)=>waterCell(column,row) && !(column>=18 && column<=21 && row<=7);
delete mesh.coastDistances;
route=routedWaterPath(12.5,7.5,187.5,7.5,15);
for(let index=1;index<route.length;index++){
  assert(fractionalWaterSegmentIsClear(route[index-1].map(value=>value/5-0.5),route[index].map(value=>value/5-0.5)));
}
isWaterCell=(column,row)=>waterCell(column,row) && column!==20;
delete mesh.coastDistances;
assert.equal(routedWaterPath(12.5,7.5,187.5,7.5,15),null);
assert.throws(()=>coastalLegGeometry([[12.5,7.5],[187.5,7.5]],0.8),/No connected water/);
mesh={W:5,H:5,cellW:5,cellH:5,bounds:[0,0,25,25]};
isWaterCell=(column,row)=>column>=0 && column<5 && row===column;
assert(routedWaterPath(2.5,2.5,22.5,22.5,15));
"""
    subprocess.run([node, '-e', script], encoding='utf-8', check=True)


def test_reshape_leg_is_undoable_and_coasting_is_sea_only():
    import shutil
    import subprocess

    import pytest

    for html in (MAP_HTML, TERRAIN_HTML):
        for identifier in ('leg-curve', 'leg-coast', 'leg-curvature'):
            assert html.count(f'id="{identifier}"') == 1
    node = shutil.which('node')
    if not node:
        pytest.skip('Node.js is required for map behavior checks')
    curves = MAP_JS[MAP_JS.index('function curvedLegGeometry('):MAP_JS.index('function insertLegWaypoint(')]
    history = MAP_JS[MAP_JS.index('function rememberLeg('):MAP_JS.index('function legWorldPoint(')]
    script = """
const assert = require('node:assert/strict');
const original={id:'road',kind:'road',points:[[0,0],[20,20],[40,0]]};
const legEditor={draft:structuredClone(original),saving:false,undo:[],redo:[],dirty:false};
const document={getElementById:()=>({value:'75'})};
let message=''; function legMessage(value){message=value;}
function syncLegEditor(){} function invalidate(){}
function routedWaterPath(){return null;}
""" + curves + history + """
reshapeLeg(true); assert.deepEqual(legEditor.draft,original); assert.equal(legEditor.undo.length,0);
reshapeLeg(false); assert(legEditor.draft.path.length>3); assert(legEditor.dirty);
const result=structuredClone(legEditor.draft);
legHistory(true); assert.deepEqual(legEditor.draft,original);
legHistory(false); assert.deepEqual(legEditor.draft,result);
legEditor.saving=true; reshapeLeg(false); assert.deepEqual(legEditor.draft,result);
legEditor.saving=false; legEditor.draft.kind='sea'; const before=structuredClone(legEditor.draft);
const undoCount=legEditor.undo.length;
reshapeLeg(true); assert.deepEqual(legEditor.draft,before); assert.equal(legEditor.undo.length,undoCount);
assert(message.includes('No connected water route'));
"""
    subprocess.run([node, '-e', script], encoding='utf-8', check=True)


def test_planned_route_doubles_only_used_locations_and_respects_reduced_motion():
    import shutil
    import subprocess

    import pytest

    node = shutil.which('node')
    if not node:
        pytest.skip('Node.js is required for map behavior checks')
    code = MAP_JS[MAP_JS.index('function plannedLocation('):MAP_JS.index('function caravanIconPosition(')]
    script = """
const assert=require('node:assert/strict');
let MAP_VIEW='planar',reduced=false;
const window={matchMedia:()=>({matches:reduced})};
const legEditor={enabled:false};
const state={animateRoutes:null,planRoute:{legs:[{from:'Waterdeep',to:'Junction'},{from:'Junction',to:'Llewellyn'}]}};
function planarScale(){return 2;}
""" + code + """
const used={data:{name:'Waterdeep'},radius:3},other={data:{name:'Other'},radius:3};
assert.equal(mapPinRadius(used,false,false),15);
assert.equal(mapPinRadius(other,false,false),7.5);
assert(plannedLocation('Junction'));assert(routeAnimationActive());
reduced=true;assert(!routeAnimationActive());assert.equal(mapPinRadius(used,false,false),15);
MAP_VIEW='terrain';assert.equal(mapPinRadius(used,false,false),4.5);
assert.equal(mapPinRadius(other,false,false),2.25);
legEditor.enabled=true;assert.equal(mapPinRadius(used,false,false),2.25);
legEditor.enabled=false;state.planRoute=null;assert.equal(mapPinRadius(used,false,false),2.25);
assert(!routeAnimationActive());
"""
    subprocess.run([node, '-e', script], encoding='utf-8', check=True)


def test_route_animation_toggle_defaults_overrides_and_persists():
    import shutil
    import subprocess

    import pytest

    node = shutil.which('node')
    if not node:
        pytest.skip('Node.js is required for map behavior checks')
    for html in (MAP_HTML, TERRAIN_HTML):
        assert html.count('id="animate-routes"') == 1
        assert '> Animate routes</label>' in html
    assert '  wireRouteAnimation();' in MAP_JS
    code = MAP_JS[MAP_JS.index('function routeAnimationsEnabled('):MAP_JS.index('function drawRoutePulse(')]
    script = """
const assert=require('node:assert/strict');
let reduced=true,saved=null,storageFailure=false,invalidations=0;
const errors=[],messages=[];
const state={animateRoutes:null,planRoute:{legs:[]}};
const legEditor={enabled:false};
const input={checked:false,addEventListener(name,callback){this[name]=callback;}};
const media={get matches(){return reduced;},addEventListener(name,callback){this[name]=callback;}};
const document={getElementById(id){assert.equal(id,'animate-routes');return input;}};
const window={matchMedia:()=>media,localStorage:{
 getItem(key){assert.equal(key,'faerun-map-animate-routes');
  if(storageFailure)throw Error('Storage blocked');return saved;},
 setItem(key,value){assert.equal(key,'faerun-map-animate-routes');
  if(storageFailure)throw Error('Storage blocked');saved=value;}
}};
const console={error(...args){errors.push(args);}};
function showStatus(message,error){assert(error);messages.push(message);}
function invalidate(){invalidations++;}
""" + code + """
wireRouteAnimation();assert(!input.checked);assert(!routeAnimationActive());
assert.equal(saved,null);
reduced=false;media.change();assert(input.checked);assert(routeAnimationActive());
reduced=true;media.change();assert(!input.checked);
input.checked=true;input.change();assert(routeAnimationActive());assert.equal(saved,'true');
state.animateRoutes=null;wireRouteAnimation();assert(input.checked);assert(routeAnimationActive());
legEditor.enabled=true;assert(!routeAnimationActive());legEditor.enabled=false;
state.planRoute=null;assert(!routeAnimationActive());state.planRoute={legs:[]};
input.checked=false;input.change();assert(!routeAnimationActive());assert.equal(saved,'false');
reduced=false;media.change();assert(!input.checked);assert(!routeAnimationActive());
state.animateRoutes=null;wireRouteAnimation();assert(!input.checked);assert(!routeAnimationActive());
saved='invalid';state.animateRoutes=null;wireRouteAnimation();assert(input.checked);
assert.equal(errors.length,1);assert.equal(messages.length,1);
storageFailure=true;wireRouteAnimation();assert.equal(errors.length,2);
input.checked=false;input.change();assert(!routeAnimationActive());
assert.equal(errors.length,3);assert(messages[2].includes('only to this page'));
assert(invalidations>=5);
"""
    subprocess.run([node, '--check'], input=MAP_JS, encoding='utf-8', check=True)
    subprocess.run([node, '-e', script], encoding='utf-8', check=True)


def test_planar_itinerary_stays_visible_at_wide_zoom():
    import shutil
    import subprocess

    import pytest

    node = shutil.which('node')
    if not node:
        pytest.skip('Node.js is required for map behavior checks')
    code = MAP_JS[MAP_JS.index('function drawPlanarItinerary('):MAP_JS.index('function drawPlanar()')]
    script = """
const assert=require('node:assert/strict');
const state={planarRadius:500,planRoute:{mapRoads:true,legs:[
    {points:[[600,1200],[872,1580]]},{points:[[872,1580],[442,1670]]},
    {points:[[442,1670],[509,1825]]}]}};
const legEditor={enabled:false}; const strokes=[],vertices=[];
let animated=false;
function routeAnimationActive(){return animated;}
function planarPoint(x,y){return [x,y];}
const ctx={save(){},restore(){},setLineDash(){},beginPath(){},
    moveTo(x,y){vertices.push([x,y]);},lineTo(x,y){vertices.push([x,y]);},
    stroke(){strokes.push([this.lineWidth,this.strokeStyle]);}};
""" + code + """
drawPlanarItinerary();
assert.deepEqual(vertices,state.planRoute.legs.flatMap(leg=>leg.points));
assert.equal(strokes.length,9);
assert.deepEqual(strokes[2],[4,'#d62f39']);
state.planarRadius=50; drawPlanarItinerary(); assert.deepEqual(strokes[11],[32,'#d62f39']);
legEditor.enabled=true; drawPlanarItinerary(); assert.equal(strokes.length,18);
legEditor.enabled=false; state.planRoute=null; drawPlanarItinerary();assert.equal(strokes.length,18);
state.planRoute={mapRoads:true,legs:[{points:[[0,0],[10,10]]}]}; animated=true;
drawPlanarItinerary();assert.equal(strokes.length,22);assert.deepEqual(strokes[21],[16,'#ffffff']);
"""
    subprocess.run([node, '--check'], input=MAP_JS, encoding='utf-8', check=True)
    subprocess.run([node, '-e', script], encoding='utf-8', check=True)


def test_planner_map_link_loads_current_leg_geometry():
        import shutil
        import subprocess

        import pytest

        node = shutil.which('node')
        if not node:
                pytest.skip('Node.js is required for map behavior checks')
        code = MAP_JS[MAP_JS.index('async function showPlanPath('):MAP_JS.index('function publishedMapPath(')]
        script = """
const assert = require('node:assert/strict');
const panel={}; const document={getElementById:()=>panel};
const state={planRequest:0}; let rendered, requests=0, reachable=true;
function invalidate(){} function collectPlanRoute(){} function fitPlanRoute(){}
function renderPlannedRoute(data){rendered=data;}
async function getJson(url){
    requests++; const query=new URL(url,'http://localhost').searchParams;
    return {reachable,distance:10,days:1,legs:[{from:query.get('origin'),to:query.get('destination'),
        mode:'ferry',points:[[0,0],[10,0]],id:'saved-leg'}]};
}
""" + code + """
(async()=>{
    await showPlanPath(['Town','Junction','Other']);
    assert.equal(requests,2); assert.equal(rendered.mapRoads,true);
    assert.deepEqual(rendered.path,['Town','Junction','Other']);
    assert.equal(rendered.distance,20); assert.equal(rendered.legs[0].id,'saved-leg');
    reachable=false; await showPlanPath(['Town','Other']);
    assert.equal(state.planRoute,null); assert(panel.textContent.includes('no longer connects'));
})().catch(error=>{console.error(error);process.exitCode=1;});
"""
        subprocess.run([node, '-e', script], encoding='utf-8', check=True)


def test_mapped_route_can_cross_ferry_and_respects_filter():
        import shutil
        import subprocess

        import pytest

        node = shutil.which('node')
        if not node:
                pytest.skip('Node.js is required for map behavior checks')
        routing = MAP_JS[MAP_JS.index('function junctionRoadPlan('):MAP_JS.index('async function showPlannedRoute(')]
        script = """
const assert = require('node:assert/strict');
const mapLegEdits = {junctions:{}};
const pins = [
    {wx:0,wy:0,data:{name:'Waterdeep'}}, {wx:20,wy:0,data:{name:'Praka'}},
    {wx:30,wy:0,data:{name:"Trail's End"}}, {wx:50,wy:0,data:{name:'Peltarch'}}
];
const routeLines = [
    {editId:'west',kind:'road',sourcePoints:[[0,0],[20,0]],details:{name:'West road'}},
    {editId:'crossing',kind:'ferry',sourcePoints:[[20,0],[30,0]],details:{name:'Ferry'}},
    {editId:'east',kind:'trail',sourcePoints:[[30,0],[50,0]],details:{name:'East trail'}}
];
let allowFerry = true;
function planarLegVisible(line){return allowFerry || line.kind !== 'ferry';}
""" + routing + """
const route = junctionRoadPlan('Waterdeep','Peltarch');
assert.deepEqual(route.path,['Waterdeep','Praka',"Trail's End",'Peltarch']);
assert.deepEqual(route.legs.map(leg=>leg.mode),['road','ferry','trail']);
assert.equal(route.distance,50);
assert.deepEqual(route.legs[1].points,[[20,0],[30,0]]);
assert.equal(junctionRoadPlan('Peltarch','Waterdeep').distance,50);
allowFerry=false;
assert.equal(junctionRoadPlan('Waterdeep','Peltarch'),null);
"""
        subprocess.run([node, '-e', script], encoding='utf-8', check=True)


def test_planar_cost_request_uses_edited_route_geometry():
        import shutil
        import subprocess

        import pytest

        node = shutil.which('node')
        if not node:
                pytest.skip('Node.js is required for map behavior checks')
        planner = MAP_JS[MAP_JS.index('async function showPlannedRoute('):MAP_JS.index('function supplyChainRows(')]
        script = """
const assert = require('node:assert/strict');
const panel = {innerHTML:''};
const document = {getElementById: () => panel};
const MAP_VIEW = 'planar';
const state = {planarLegTypes:['road','trail','ferry'], planRequest:0, planRouteKeys:{old:true}};
const mapLegEdits = {junctions:{join:{}}};
const mapped = {origin:'Crimmor', destination:'Eshpurta', mapRoads:true, reachable:true,
    path:['Crimmor','Eshpurta'], distance:315.2,
    legs:[{from:'Crimmor',to:'Eshpurta',via:'Edited road',mode:'road',miles:315.2,points:[[0,0],[315.2,0]]}]};
let available = true, fitted = false;
function junctionLocations(){return [];}
function junctionRoadPlan(){return available ? mapped : null;}
function fitPlanRoute(){fitted=true;} function invalidate(){}
function esc(value){return value;}
function routeTypeLabel(mode){return {road:'Road',ferry:'Ferry'}[mode];}
const window = {location:{href:'http://localhost/map.html?view=planar'}};
const history = {replaceState(){}};
state.routeTypes=[];
function collectPlanRoute(data){assert.equal(data,mapped);}
function renderPlannedRoute(data){panel.innerHTML=data.legs.map(leg=>leg.mode).join(',');}
async function getJson(url){
    assert(url.includes('/api/route?')); assert(url.includes('optimise='));
    assert(url.includes('route_type=road%2Ctrail%2Cferry'));
    return available ? mapped : {reachable:false};
}
""" + planner + """
(async () => {
    await showPlannedRoute('Crimmor','Eshpurta','cost');
    assert.equal(state.planRoute,mapped); assert(fitted);
    assert.equal(state.planOptimise,'cost'); assert.deepEqual(state.planRouteKeys,{});
    assert.equal(panel.innerHTML,'road');
    mapped.legs.push({from:'Praka',to:"Trail's End",via:'New leg',mode:'ferry',miles:12.6});
    await showPlannedRoute('Crimmor','Eshpurta','days');
    assert.equal(panel.innerHTML,'road,ferry');
    available=false;
    await showPlannedRoute('Crimmor','Eshpurta','cost');
    assert.equal(state.planRoute,null); assert(panel.innerHTML.includes('No route connects'));
})().catch(error => {console.error(error); process.exitCode=1;});
"""
        subprocess.run([node, '-e', script], encoding='utf-8', check=True)


def test_leaving_leg_saves_before_clearing_and_keeps_failed_draft():
        import shutil
        import subprocess

        import pytest

        node = shutil.which('node')
        if not node:
                pytest.skip('Node.js is required for map behavior checks')
        subprocess.run([node, '--check'], input=MAP_JS, encoding='utf-8', check=True)
        discard = MAP_JS[MAP_JS.index('async function discardLegDraft()'):MAP_JS.index('function rememberLeg()')]
        script = """
const assert = require('node:assert/strict');
const draft = {name:'Changed trail'};
const legEditor = {draft, dirty:true, saving:false, undo:['edit'], redo:[]};
let accepted=false, fail=false, finish, saves=0;
const window = {confirm: message => {assert.equal(message,'Save route leg changes before continuing?'); return accepted;}};
function syncLegEditor(){} function invalidate(){}
async function saveLegDraft(deleted){
    assert.equal(deleted,false); saves++; legEditor.saving=true;
    await new Promise(resolve => {finish=resolve;});
    legEditor.saving=false; if(!fail) legEditor.dirty=false;
}
""" + discard + """
(async () => {
    assert.equal(await discardLegDraft(),false); assert.equal(saves,0);
    assert.equal(legEditor.draft,draft); assert.deepEqual(legEditor.undo,['edit']);
    accepted=true; fail=true;
    let pending=discardLegDraft(); assert.equal(legEditor.draft,draft);
    assert.equal(await discardLegDraft(),false); assert.equal(saves,1);
    finish(); assert.equal(await pending,false); assert.equal(legEditor.draft,draft);
    assert.equal(legEditor.dirty,true);
    fail=false; pending=discardLegDraft(); assert.equal(legEditor.draft,draft);
    finish(); assert.equal(await pending,true); assert.equal(legEditor.draft,null);
    assert.deepEqual(legEditor.undo,[]); assert.equal(await discardLegDraft(),true);
    assert.equal(saves,2);
})().catch(error => {console.error(error); process.exitCode=1;});
"""
        subprocess.run([node, '-e', script], encoding='utf-8', check=True)


def test_rename_junction_refreshes_map_and_preserves_failed_edits():
        import shutil
        import subprocess

        import pytest

        node = shutil.which('node')
        if not node:
                pytest.skip('Node.js is required for map behavior checks')
        rename = MAP_JS[MAP_JS.index('async function renameJunction('):MAP_JS.index('function focusJunction(')]
        script = """
const assert = require('node:assert/strict');
let mapLegEdits = {revision:3, legs:{main:{name:'Road'}}, junctions:{join:{
    name:'Old Junction', point:[10,10], legs:['main']}}};
const legEditor = {saving:false, dirty:false, draft:{id:'main', name:'Road'}};
const state = {selected:'junction:join'};
const inputs = {'route-plan-origin':{value:'Old Junction'}, 'route-plan-destination':{value:'Goldenfields'}};
const document = {getElementById: id => inputs[id]};
let requests=0, refreshes=0, fail=false, focused;
function syncLegEditor(){} function invalidate(){}
function applyMapLegEdits(){refreshes++;} function syncJunctionLocations(){} function clearPlannedRoute(){}
function junctionLocations(){return [{id:'junction:join', name:mapLegEdits.junctions.join.name}];}
function focusJunction(location){focused=location;}
async function postJson(url, body){
    requests++; assert.equal(url,'/api/map-junction'); assert.equal(body.id,'join');
    assert.equal(body.revision,3); assert.deepEqual(body.point,[10,10]); assert.deepEqual(body.legs,['main']);
    if(fail) throw new Error('A junction with that name already exists');
    assert.equal(body.name,'Goldenfields Junction');
    return {...mapLegEdits, junctions:{join:{...mapLegEdits.junctions.join,name:body.name}}};
}
""" + rename + """
(async () => {
    legEditor.dirty=true;
    await assert.rejects(renameJunction('join','Goldenfields Junction'), /Save or cancel/);
    assert.equal(requests,0); legEditor.dirty=false; fail=true;
    await assert.rejects(renameJunction('join','Goldenfields Junction'), /already exists/);
    assert.equal(mapLegEdits.junctions.join.name,'Old Junction'); assert.equal(legEditor.saving,false);
    assert.equal(refreshes,0); fail=false;
    await renameJunction('join',' Goldenfields Junction ');
    assert.equal(focused.name,'Goldenfields Junction'); assert.equal(refreshes,1);
    assert.equal(inputs['route-plan-origin'].value,'Goldenfields Junction');
    assert.equal(inputs['route-plan-destination'].value,'Goldenfields'); assert.equal(legEditor.saving,false);
})().catch(error => {console.error(error); process.exitCode=1;});
"""
        subprocess.run([node, '-e', script], encoding='utf-8', check=True)


def test_junction_selection_in_route_editor_without_a_leg_draft():
    import shutil
    import subprocess

    import pytest

    node = shutil.which('node')
    if not node:
        pytest.skip('Node.js is required for map behavior checks')
    code = MAP_JS[MAP_JS.index('function junctionAt('):MAP_JS.index('async function saveLegDraft(')]
    script = """
const assert=require('node:assert/strict');
const MAP_VIEW='planar', legEditor={enabled:true,saving:false,draft:null};
const canvas={getBoundingClientRect:()=>({left:5,top:5})};
const junction={id:'junction:join',x:100,y:100};
function junctionLocations(){return [junction];}
function planarPoint(x,y){return [x,y];} function planarScale(){return 1;}
let selected=null, edited=false;
function focusJunction(location){selected=location;}
function editLegAt(){edited=true;}
""" + code + """
assert(legPointerDown({button:0,clientX:105,clientY:105}));
assert.equal(selected,junction);assert.equal(edited,false);
selected=null;
assert(legPointerDown({button:0,clientX:300,clientY:300}));
assert.equal(selected,null);assert.equal(edited,true);
assert.equal(legPointerDown({button:0,shiftKey:true,clientX:105,clientY:105}),false);
"""
    subprocess.run([node, '-e', script], encoding='utf-8', check=True)


def test_delete_junction_confirms_preserves_failed_edits_and_clears_selection():
    import shutil
    import subprocess

    import pytest

    node = shutil.which('node')
    if not node:
        pytest.skip('Node.js is required for map behavior checks')
    code = MAP_JS[MAP_JS.index('async function deleteJunction('):MAP_JS.index('function focusJunction(')]
    script = """
const assert=require('node:assert/strict');
let mapLegEdits={revision:3,legs:{road:{points:[[0,0],[10,0]]}},
 junctions:{join:{name:'Crossroads',point:[10,0],legs:['road']}}};
const legEditor={saving:false,dirty:false};
const locationEditor={draft:null,busy:false};
const state={selected:'junction:join'};
let confirmed=false, fail=false, requests=0, refreshes=0;
const window={confirm(message){assert(message.includes('roads and waypoints will be kept'));return confirmed;}};
const elements={'route-plan-origin':{value:'Crossroads'},'route-plan-destination':{value:'Town'},
 'place-head':{},'place-stats':{},'place-notes':{},'place-prices':{}};
const document={getElementById:id=>elements[id]};
function syncLegEditor(){} function invalidate(){} function updateRouteSelection(){}
function applyMapLegEdits(){refreshes++;} function syncJunctionLocations(){}
function clearPlannedRoute(){}
async function postJson(url,body){
 requests++;assert.equal(url,'/api/map-junction');
 assert.deepEqual(body,{id:'join',deleted:true,revision:3});
 if(fail) throw new Error('Changed elsewhere');
 return {...mapLegEdits,revision:4,junctions:{}};
}
""" + code + """
(async()=>{
 await deleteJunction('join');assert.equal(requests,0);
 confirmed=true;legEditor.dirty=true;
 await assert.rejects(deleteJunction('join'),/Save or cancel/);assert.equal(requests,0);
 legEditor.dirty=false;locationEditor.draft={};
 await assert.rejects(deleteJunction('join'),/Save or cancel/);locationEditor.draft=null;
 fail=true;await assert.rejects(deleteJunction('join'),/Changed elsewhere/);
 assert.equal(state.selected,'junction:join');assert(mapLegEdits.junctions.join);
 assert.equal(refreshes,0);assert.equal(legEditor.saving,false);
 fail=false;await deleteJunction('join');
 assert.equal(state.selected,null);assert.equal(refreshes,1);assert.equal(legEditor.saving,false);
 assert.deepEqual(mapLegEdits.legs.road.points,[[0,0],[10,0]]);
 assert.equal(elements['route-plan-origin'].value,'');
 assert.equal(elements['route-plan-destination'].value,'Town');
 assert(elements['place-head'].textContent.includes('Junction deleted'));
})().catch(error=>{console.error(error);process.exitCode=1;});
"""
    subprocess.run([node, '-e', script], encoding='utf-8', check=True)
    assert "deleteButton.textContent = 'Delete junction'" in MAP_JS
    assert "var junction = junctionAt(screenX, screenY);" in MAP_JS
    assert "var junction = junctionAt(mx, my);" in MAP_JS


def test_single_waypoint_junction_conversion_and_routing():
        import shutil
        import subprocess

        import pytest

        node = shutil.which('node')
        if not node:
                pytest.skip('Node.js is required for map behavior checks')
        subprocess.run([node, '--check'], input=MAP_JS, encoding='utf-8', check=True)
        for html in (MAP_HTML, TERRAIN_HTML):
                assert '>Convert to junction</button>' in html
        handler = MAP_JS[MAP_JS.index("  document.getElementById('leg-junction').addEventListener"):
                                         MAP_JS.index("  var legFilter = document.getElementById('planar-leg-type')")]
        routing = MAP_JS[MAP_JS.index('function junctionRoadPlan('):
                                         MAP_JS.index('async function showPlannedRoute(')]
        script = """
const assert = require('node:assert/strict');
let convert, saved = 0, redrawn = 0, locations = 0, failSave = false;
const document = {getElementById: () => ({addEventListener: (_, handler) => {convert = handler;}})};
const legEditor = {draft: {id:'main', name:'Red Larch Trail', kind:'trail',
    points:[[0,0],[10,10],[20,20]]}, point:1, dirty:false, saving:false};
let mapLegEdits = {revision:0, legs:{}};
function syncLegEditor(){} function invalidate(){redrawn++;} function legMessage(){}
function applyMapLegEdits(){} function syncJunctionLocations(){locations++;} function clearPlannedRoute(){}
async function saveLegDraft(){
    saved++; if(failSave) return;
    mapLegEdits.legs.main = {...legEditor.draft}; mapLegEdits.revision++; legEditor.dirty=false;
}
async function postJson(url, body){
    assert.equal(url, '/api/map-junction'); assert.deepEqual(body.legs, ['main']);
    assert.deepEqual(body.point, [10,10]); assert.equal(body.revision, mapLegEdits.revision);
    assert(!('name' in body));
    return {...mapLegEdits, revision:mapLegEdits.revision+1, junctions:{join:{
        name:'Red Larch Trail Junction', point:body.point, legs:body.legs}}};
}
const pins = [{wx:0, wy:0, data:{name:'Secomber'}}, {wx:20, wy:20, data:{name:'Red Larch'}}];
const routeLines = [{editId:'main', kind:'trail', sourcePoints:legEditor.draft.points,
    details:{name:'Red Larch Trail'}}];
function planarLegVisible(){return true;}
""" + handler + routing + """
(async () => {
    await convert(); assert.equal(saved,1); assert.equal(locations,1); assert(redrawn);
    assert.equal(legEditor.saving,false);
    const plan = junctionRoadPlan('Secomber','Red Larch');
        assert.deepEqual(plan.path, ['Secomber','Red Larch']);
        assert.equal(plan.legs.length,1);
        assert.deepEqual(plan.legs[0].points, legEditor.draft.points);
        assert.equal(plan.distance, plan.legs[0].miles);
        assert.deepEqual(junctionRoadPlan('Red Larch','Secomber').legs[0].points,
            legEditor.draft.points.slice().reverse());
        assert.deepEqual(junctionRoadPlan('Secomber','Red Larch Trail Junction').path,
            ['Secomber','Red Larch Trail Junction']);
        pins.push({wx:30, wy:10, data:{name:'Goldenfields'}});
        routeLines.push({editId:'branch', kind:'trail', sourcePoints:[[10,10],[30,10]],
            details:{name:'Goldenfields Trail'}});
        mapLegEdits.junctions.join.legs.push('branch');
        const branchPlan = junctionRoadPlan('Secomber','Goldenfields');
        assert.deepEqual(branchPlan.path, ['Secomber','Red Larch Trail Junction','Goldenfields']);
        assert.equal(branchPlan.legs.length,2);
        assert.equal(branchPlan.distance, branchPlan.legs.reduce((total, leg) => total + leg.miles, 0));
    await convert(); assert.equal(saved,1);
    legEditor.dirty=true; failSave=true; await convert(); assert.equal(locations,2);
    assert.equal(legEditor.dirty,true);
})().catch(error => {console.error(error); process.exitCode=1;});
"""
        subprocess.run([node, '-e', script], encoding='utf-8', check=True)


def test_planar_land_overlay_opacity_and_stacking():
        import shutil
        import subprocess

        import pytest

        node = shutil.which('node')
        if not node:
                pytest.skip('Node.js is required for map behavior checks')
        for html in (MAP_HTML, TERRAIN_HTML):
                assert 'id="planar-terrain"' in html
                assert 'aria-label="Land type opacity"' in html
                assert 'id="planar-poster-alpha"' in html
                assert 'aria-label="Poster opacity"' in html
        draw = MAP_JS[MAP_JS.index('function drawPlanar()'):MAP_JS.index('function draw()')]
        script = """
const assert = require('node:assert/strict');
const state={tx:0,tz:0,planarRadius:200,planarPoster:true,planarPosterAlpha:1,under:{width:1,height:1},
    underX:0,underY:0,underMpp:1,underStretch:1,planarTerrain:true,planarTerrainAlpha:0.5,routes:true};
const mesh={cx:0,cy:0,bounds:[0,0],W:1,H:1,cellW:1,cellH:1};
const cam={cx:1,cy:1}; const SCALE=1; const PALETTE={f:[62,132,73]};
const legEditor={enabled:false}; const calls=[]; const stack=[];
const crops=[]; let clipped=false;
const ctx={globalAlpha:1,save(){stack.push(this.globalAlpha);},restore(){this.globalAlpha=stack.pop();},
    rect(...bounds){crops.push(bounds);},clip(){clipped=true;},
    fillRect(){calls.push(['fill',this.globalAlpha,this.fillStyle]);},drawImage(){calls.push(['poster',this.globalAlpha]);},
    beginPath(){},arc(){},stroke(){},setLineDash(){},measureText(){return {width:1};},fillText(){}};
function drawSky(){} function planarScale(){return 1;} function planarPoint(x,y){return [x,y];}
function terrainCodeAt(){return 'f';} function drawPlanarGrid(){calls.push(['grid',ctx.globalAlpha]);}
function drawPlanarBoundaries(){}
function drawPlaces(){} function drawPins(){calls.push(['pins']);} function drawMapJunctions(){}
function drawPlanarLegs(){calls.push(['legs']);} function drawLocationDraft(){}
function drawPlanarItinerary(){}
function drawPlanarRuler(){}
""" + draw + """
drawPlanar();
assert.deepEqual(crops,[[0,0,1,1]]); assert(clipped); assert.equal(stack.length,0);
assert.deepEqual(calls.slice(0,6),[['fill',1,'rgb(62,132,73)'],['poster',1],
 ['fill',0.5,'rgb(62,132,73)'],['grid',1],['legs'],['pins']]);
calls.length=0; state.planarTerrain=false; drawPlanar();
assert.equal(calls.filter(call=>call[0]==='fill' && call[2]==='rgb(62,132,73)').length,1);
calls.length=0; state.planarTerrain=true; state.planarTerrainAlpha=0; drawPlanar();
assert.equal(calls.filter(call=>call[0]==='fill' && call[2]==='rgb(62,132,73)').length,1);
calls.length=0; state.planarTerrainAlpha=1; drawPlanar();
assert.deepEqual(calls[2],['fill',1,'rgb(62,132,73)']);
for (const opacity of [0,0.5,1]) {
 calls.length=0;state.planarPosterAlpha=opacity;drawPlanar();
 assert.deepEqual(calls.find(call=>call[0]==='poster'),['poster',opacity]);
 assert.deepEqual(calls.find(call=>call[0]==='grid'),['grid',1]);
 assert.equal(ctx.globalAlpha,1);assert.equal(stack.length,0);
}
state.planarPoster=false;calls.length=0;drawPlanar();
assert(!calls.some(call=>call[0]==='poster'));
state.rasterLayers={
 elevation:{on:true,alpha:0.35,image:{width:2,height:2}},
 'ground-cover':{on:true,alpha:0.6,image:{width:3,height:3}}
};
state.planarPoster=true;state.planarPosterAlpha=1;calls.length=0;drawPlanar();
assert.deepEqual(calls.filter(call=>call[0]==='poster'),
 [['poster',1],['poster',0.35],['poster',0.6]]);
state.planarPoster=false;calls.length=0;drawPlanar();
assert.deepEqual(calls.filter(call=>call[0]==='poster'),[['poster',0.35],['poster',0.6]]);
state.rasterLayers.elevation.on=false;calls.length=0;drawPlanar();
assert.deepEqual(calls.filter(call=>call[0]==='poster'),[['poster',0.6]]);
state.rasterLayers['ground-cover'].alpha=0;calls.length=0;drawPlanar();
assert(!calls.some(call=>call[0]==='poster'));assert.equal(ctx.globalAlpha,1);
"""
        subprocess.run([node, '-e', script], encoding='utf-8', check=True)


def test_reference_overlays_share_projection_and_respect_poster_only():
    import shutil
    import subprocess

    import pytest

    node = shutil.which("node")
    if not node:
        pytest.skip("Node.js is required for map behavior checks")
    for html in (MAP_HTML, TERRAIN_HTML):
        for source in ("elevation", "ground-cover"):
            assert html.count('id="layer-' + source + '"') == 1
            assert html.count('id="layer-' + source + '-alpha"') == 1
    wrapper = MAP_JS[MAP_JS.index("function drawUnderlay()"):
                     MAP_JS.index("function drawUnderlayLayer(")]
    projection = MAP_JS[MAP_JS.index("function drawUnderlayLayer("):
                        MAP_JS.index("function routeBezierSegments(")]
    script = """
const assert=require('node:assert/strict');
const poster={width:100,height:50}, elevation={width:20,height:10}, vegetation={width:30,height:15};
const state={under:poster,underOn:true,underAlpha:0.55,underMpp:2,underStretch:1.5,underX:10,underY:20,
 rasterLayers:{elevation:{on:true,alpha:0.35,image:elevation},vegetation:{on:true,alpha:0.6,image:vegetation}},
 step:2,underDrape:false};
let only=false;function posterOnlyActive(){return only;}
const calls=[];function drawUnderlayLayer(image,alpha,posterOnly){calls.push([image,alpha,posterOnly]);}
""" + wrapper + """
drawUnderlay();assert.deepEqual(calls,[[poster,0.55,false],[elevation,0.35,false],[vegetation,0.6,false]]);
calls.length=0;state.underOn=false;drawUnderlay();
assert.deepEqual(calls,[[elevation,0.35,false],[vegetation,0.6,false]]);
calls.length=0;only=true;drawUnderlay();assert.deepEqual(calls,[[poster,1,true]]);
calls.length=0;only=false;state.rasterLayers.elevation.on=false;state.rasterLayers.vegetation.alpha=0;
drawUnderlay();assert.deepEqual(calls,[]);
"""
    subprocess.run([node, "-e", script], check=True, capture_output=True, text=True)
    script = """
const assert=require('node:assert/strict');
const state={under:{width:100,height:50},underMpp:2,underStretch:1.5,underX:10,underY:20,
 step:2,underDrape:false};
const underCanvas={width:1000,height:1000},cam={cx:500,cy:500,dpr:1};
let positions=[];function toScene(x,y){positions.push([x,y]);return [x,y];}
function project(x,h,y){return [x,y];}
let underPx,underPy,underOk;function underlayGrid(n){
 underPx=new Float64Array((n+1)**2);underPy=new Float64Array((n+1)**2);underOk=new Uint8Array((n+1)**2);
}
const underCtx={setTransform(){},clearRect(){},drawImage(){}};
const ctx={globalAlpha:0.9,globalCompositeOperation:'source-over',drawImage(){
 assert.equal(this.globalAlpha,0.35);assert.equal(this.globalCompositeOperation,'multiply');
}};
""" + projection + """
for(const img of [{width:100,height:50},{width:20,height:10},{width:30,height:15}]){
 positions=[];drawUnderlayLayer(img,0.35,false);
 assert.deepEqual(positions[0],[10,20]);assert.deepEqual(positions.at(-1),[210,170]);
 assert.equal(ctx.globalAlpha,0.9);assert.equal(ctx.globalCompositeOperation,'source-over');
}
"""
    subprocess.run([node, "-e", script], check=True, capture_output=True, text=True)


def test_reference_overlay_loading_preferences_and_errors():
    import shutil
    import subprocess

    import pytest

    node = shutil.which("node")
    if not node:
        pytest.skip("Node.js is required for map behavior checks")
    helpers = MAP_JS[MAP_JS.index("var RASTER_LAYERS_KEY"):
                     MAP_JS.index("function underlayStorageKey(")]
    script = """
const assert=require('node:assert/strict');
const state={under:{width:100,height:50},
 underInfo:{options:[{id:'elevation'},{id:'ground-cover'}]},
 rasterLayers:{elevation:{on:false,alpha:0.35,image:null,loading:false},
 'ground-cover':{on:false,alpha:0.35,image:null,loading:false}}};
const controls={},storage={},errors=[],requests=[];
const window={localStorage:{getItem(key){return storage[key] || null;},setItem(key,value){storage[key]=value;}}};
function underlayEl(id){return controls[id] || (controls[id]={});}
function showStatus(message,isError){errors.push([message,isError]);} function invalidate(){}
let available=true,decode=true;
async function getJson(url){requests.push(url);return {available,url,name:'reference.png'};}
class Image {set src(url){queueMicrotask(()=> decode ? this.onload() : this.onerror());}}
""" + helpers + """
(async()=>{
 storage[RASTER_LAYERS_KEY]=JSON.stringify({elevation:{on:true,alpha:0.6},'ground-cover':{on:false,alpha:-1}});
 restoreRasterLayers();await loadRasterLayer('elevation');await new Promise(resolve=>setImmediate(resolve));
 assert.equal(requests.length,1);assert.equal(state.rasterLayers.elevation.alpha,0.6);
 assert(state.rasterLayers.elevation.image);assert.equal(state.rasterLayers['ground-cover'].alpha,0);
 assert.equal(controls['layer-elevation'].checked,true);assert.equal(controls['layer-elevation-alpha'].disabled,false);
 await loadRasterLayer('elevation');assert.equal(requests.length,1);
 state.rasterLayers['ground-cover'].on=true;
 const pending=loadRasterLayer('ground-cover');state.rasterLayers['ground-cover'].on=false;await pending;
 assert.equal(state.rasterLayers['ground-cover'].on,false);
 state.rasterLayers['ground-cover'].image=null;state.rasterLayers['ground-cover'].on=true;available=false;
 await loadRasterLayer('ground-cover');assert.equal(state.rasterLayers['ground-cover'].on,false);
 assert.equal(state.rasterLayers['ground-cover'].loading,false);assert.equal(errors.at(-1)[1],true);
 assert(errors.at(-1)[0].includes('unavailable'));
 available=true;decode=false;state.rasterLayers['ground-cover'].on=true;
 await loadRasterLayer('ground-cover');assert.equal(state.rasterLayers['ground-cover'].on,false);
 assert(errors.at(-1)[0].includes('decoded'));
 assert.equal(JSON.parse(storage[RASTER_LAYERS_KEY])['ground-cover'].on,false);
 state.underInfo.options=[];syncRasterLayerControls();
 assert.equal(controls['layer-elevation'].disabled,true);assert.equal(controls['layer-elevation-alpha'].disabled,true);
})().catch(error=>{console.error(error);process.exitCode=1;});
"""
    subprocess.run([node, "-e", script], check=True, capture_output=True, text=True)


def test_roadside_waypoints_snap_to_saved_visible_land_geometry():
        import shutil
        import subprocess

        import pytest

        node = shutil.which('node')
        if not node:
                pytest.skip('Node.js is required for map behavior checks')
        helper = MAP_JS[MAP_JS.index('function nearestRoadsidePoint('):MAP_JS.index('function drawLocationDraft()')]
        script = """
const assert = require('node:assert/strict');
const planarPoint = (east, south) => [east, south];
const planarLegVisible = line => !line.hidden;
const routeLines = [{kind:'road',editId:'road'}, {kind:'sea',editId:'sea'},
    {kind:'track',editId:'hidden',hidden:true}, {kind:'road',editId:'unsaved'}];
const mapLegEdits = {legs:{
    road:{name:'Trade Way',points:[[0,0],[100,0]],path:[[0,0],[50,50],[100,0]]},
    sea:{name:'Sea',points:[[0,10],[100,10]]},
    hidden:{name:'Hidden',points:[[0,10],[100,10]]}}};
""" + helper + """
const snap=nearestRoadsidePoint(25,27);
assert.deepEqual(snap,{roadLegId:'road',roadName:'Trade Way',x:26,y:26});
assert.equal(nearestRoadsidePoint(25,100),null);
assert.equal(nearestRoadsidePoint(50,10),null);
mapLegEdits.legs.road.deleted=true;
assert.equal(nearestRoadsidePoint(25,27),null);
"""
        subprocess.run([node, '-e', script], encoding='utf-8', check=True)


def test_caravan_icons_are_drawn_and_selectable_at_shared_camps():
    import shutil
    import subprocess

    import pytest

    node = shutil.which('node')
    if not node:
        pytest.skip('Node.js is required for map behavior checks')
    icon = MAP_JS[MAP_JS.index('function caravanIconPosition('):MAP_JS.index('function drawPins()')]
    picking = MAP_JS[MAP_JS.index('function pick(mx, my)'):MAP_JS.index('function pointSegmentDistanceSquared(')]
    script = """
const assert = require('node:assert/strict');
const calls=[];
const ctx = new Proxy({}, {get: (_,method)=> (...args)=>calls.push([method,...args]),
 set: (_,name,value)=>{calls.push(['set',name,value]);return true;}});
""" + icon + """
drawCaravanIcon(24,10,'brown');
assert(calls.some(call=>call[0]==='quadraticCurveTo'));
assert.equal(calls.filter(call=>call[0]==='arc').length,2);
const MAP_VIEW='planar'; const state={};
const pins=[{px:10,py:10,vis:true,data:{id:'town'}},
 {px:10,py:10,vis:true,data:{id:'company',mobile:true,status:'encamped',host:{id:'town'}}}];
let scale=1;
function planarScale(){return scale;}
function posterOnlyActive(){return false;}
function mapPinRadius(pin){return (pin.data.mobile?2.5:3.75)*scale;}
""" + picking + """
for (const radius of [50,100,200,500]) {
 scale=400/radius;
 const center=caravanIconPosition(pins[1]);
 assert(Math.abs(Math.hypot(center.x-10,center.y-10)/scale-7.5)<1e-12);
 assert(Math.abs(center.x-10)<1e-12 && center.y<10);
 assert.equal(pick(center.x,center.y),1);
 assert.equal(pick(10,10),0);
 calls.length=0; drawCaravanMarker(pins[1]);
 assert.deepEqual(calls.find(call=>call[0]==='arc').slice(1,4),[center.x,center.y,2.5*scale]);
 assert(calls.some(call=>call[0]==='translate' && call[1]===center.x && call[2]===center.y));
 assert(calls.some(call=>call[0]==='set' && call[1]==='fillStyle' && call[2]==='#ffffff'));
 assert(calls.some(call=>call[0]==='set' && call[1]==='strokeStyle' && call[2]==='#000000'));
}
pins.push({px:10,py:10,vis:true,data:{id:'second',mobile:true,status:'encamped',host:{id:'town'}}});
const other=caravanIconPosition(pins[2]);
assert.notDeepEqual(other,caravanIconPosition(pins[1]));
assert(Math.abs(Math.hypot(other.x-10,other.y-10)/scale-7.5)<1e-12);
assert.equal(pick(other.x,other.y),2);
pins[0].px=100; pins[0].py=100;
const moved=caravanIconPosition(pins[1]);
assert(Math.abs(Math.hypot(moved.x-100,moved.y-100)/scale-7.5)<1e-12);
assert.equal(pick(moved.x,moved.y),1);
pins[1].data.status='travelling';
assert.deepEqual(caravanIconPosition(pins[1]),{x:10,y:10});
"""
    subprocess.run([node, '-e', script], encoding='utf-8', check=True)
    assert 'performance.now() - started) / 180000' not in MAP_JS


def test_encamped_companies_chain_clockwise_and_wrap_without_overlapping():
    import shutil
    import subprocess

    import pytest

    node = shutil.which('node')
    if not node:
        pytest.skip('Node.js is required for map behavior checks')
    code = MAP_JS[MAP_JS.index('function caravanIconPosition('):MAP_JS.index('function drawCaravanMarker(')]
    picking = MAP_JS[MAP_JS.index('function pick(mx, my)'):MAP_JS.index('function pointSegmentDistanceSquared(')]
    script = """
const assert=require('node:assert/strict');
let MAP_VIEW='planar',scale=1,emphasized=false;
const state={};
const host={px:100,py:100,vis:true,data:{id:'town'}};
const companies=Array.from({length:40},(_,i)=>({
 px:100,py:100,vis:true,data:{id:'company-'+String(i).padStart(2,'0'),mobile:true,
 status:'encamped',host:{id:'town'}}
}));
const pins=[host,...companies];
function planarScale(){return scale;}
function mapPinRadius(pin){
 return (pin.data.mobile?2.5:3.75)*scale*(emphasized?2:1);
}
function posterOnlyActive(){return false;}
""" + code + picking + """
for(const zoom of [0.8,2,4,8]){
 scale=zoom;
 for(const emphasis of [false,true]){
  emphasized=emphasis;
  const centers=companies.map(caravanIconPosition);
  const hostRadius=mapPinRadius(host),markerRadius=mapPinRadius(companies[0]);
  assert(Math.abs(centers[0].x-host.px)<1e-10);assert(centers[0].y<host.py);
  assert(centers[1].x>host.px);assert(centers[1].y>centers[0].y);
  assert(centers.some(c=>c.x<host.px-1));assert(centers.some(c=>c.y>host.py));
  assert(Math.hypot(centers[39].x-host.px,centers[39].y-host.py)>
   Math.hypot(centers[0].x-host.px,centers[0].y-host.py));
  centers.forEach((center,i)=>{
   assert(Math.hypot(center.x-host.px,center.y-host.py)>=hostRadius+markerRadius);
   assert.equal(pick(center.x,center.y),i+1);
   centers.slice(i+1).forEach(other=>{
    assert(Math.hypot(center.x-other.x,center.y-other.y)>=2*markerRadius+1.25*scale-1e-9);
   });
  });
  assert.equal(pick(host.px,host.py),0);
  pins.reverse();assert.deepEqual(companies.map(caravanIconPosition),centers);pins.reverse();
 }
}
companies[0].vis=false;
assert(Math.abs(caravanIconPosition(companies[1]).x-host.px)<1e-10);
companies[0].vis=true;companies[0].data.status='travelling';
assert.deepEqual(caravanIconPosition(companies[0]),{x:100,y:100});
assert(Math.abs(caravanIconPosition(companies[1]).x-host.px)<1e-10);
companies[0].data.status='encamped';
for(const view of ['overlay','terrain']){
 MAP_VIEW=view;const centers=companies.map(caravanIconPosition);
 assert(Math.abs(centers[0].x-host.px)<1e-10);assert(centers[0].y<host.py);
 centers.forEach((center,i)=>{
  assert.equal(pick(center.x,center.y),i+1);
  centers.slice(i+1).forEach(other=>assert(Math.hypot(center.x-other.x,center.y-other.y)>=42-1e-9));
 });
}
"""
    subprocess.run([node, '--check'], input=MAP_JS, encoding='utf-8', check=True)
    subprocess.run([node, '-e', script], encoding='utf-8', check=True)


def test_planar_zoom_scales_labels_roads_and_acreage_with_distance_ruler():
    import shutil
    import subprocess

    import pytest

    node = shutil.which('node')
    if not node:
        pytest.skip('Node.js is required for map behavior checks')
    def function_source(name):
        start = MAP_JS.index('function ' + name + '(')
        return MAP_JS[start:MAP_JS.index('\n}', start) + 2]

    helpers = '\n'.join(function_source(name) for name in (
        'mapLabelScale', 'mapLabelFont', 'mapPinRadius', 'strokePlanarLeg', 'planarDistanceRuler', 'drawPlanarRuler', 'drawLabels'))
    script = """
const assert = require('node:assert/strict');
let MAP_VIEW='planar';
const state={planarRadius:200,selected:'waterdeep',hover:-1,labels:true};
const planarScale=()=>400/state.planarRadius;
const drawn=[];
const rectangles=[],ticks=[];
const cam={cx:195,cy:300};
function plannedLocation(){return false;}
const ctx={setLineDash(values){this.dash=values;},stroke(){},
    save(){},restore(){},beginPath(){},strokeRect(){},
    moveTo(x,y){ticks.push([x,y]);},lineTo(){},
    fillRect(x,y,width,height){rectangles.push({x,y,width,height,color:this.fillStyle});},
  measureText(text){return {width:parseFloat(this.font.replace('bold ',''))*text.length/2};},
  strokeText(){},fillText(text,x,y){drawn.push({text,x,y,font:this.font,halo:this.lineWidth});}};
const pins=[{px:100,py:100,radius:5,data:{id:'waterdeep',name:'Waterdeep',population:200000,landAcres:640}}];
""" + helpers + """
drawLabels([0]); const base=drawn.pop();
const baseRadius=mapPinRadius(pins[0],false,false);
assert.equal(baseRadius,3.75*planarScale());
strokePlanarLeg('red',4,[6,3]); assert.equal(ctx.lineWidth,4);
state.planarRadius=100;
drawLabels([0]); const zoomed=drawn.pop();
assert.equal(base.font,'bold 24px "Segoe UI", Arial, Helvetica, sans-serif');
assert.equal(zoomed.font,'bold 48px "Segoe UI", Arial, Helvetica, sans-serif');
assert.equal(zoomed.halo,base.halo*2);
assert(Math.abs((zoomed.x-100)-(base.x-100)*2)<1e-9);
assert.equal(mapPinRadius(pins[0],false,false),baseRadius*2);
strokePlanarLeg('red',4,[6,3]); assert.equal(ctx.lineWidth,8); assert.deepEqual(ctx.dash,[12,6]);
pins[0].data.landAcres=2560;
assert.equal(mapPinRadius(pins[0],false,false),baseRadius*2);
delete pins[0].data.landAcres; assert.equal(mapPinRadius(pins[0],false,false),3.75*planarScale());
for (const radius of [50,100,200,500]) {
 state.planarRadius=radius;
 assert.equal(2*mapPinRadius(pins[0],false,false)/planarScale(),7.5);
 assert.equal(2*mapPinRadius(pins[0],true,true)/planarScale(),7.5);
 assert.equal(2*mapPinRadius({data:{mobile:true}},true,true)/planarScale(),5);
 const ruler=planarDistanceRuler(planarScale(),390);
 assert.equal(ruler.pixels,ruler.miles*planarScale()); assert(ruler.pixels<=160);
 rectangles.length=0; ticks.length=0; drawn.length=0;
 drawPlanarRuler();
 const segments=rectangles.filter(rectangle=>rectangle.height===6);
 assert.equal(segments.length,4); assert.equal(ticks.length,5);
 assert.equal(segments.reduce((sum,segment)=>sum+segment.width,0),ruler.pixels);
 assert.deepEqual(segments.map(segment=>segment.color),['#163a45','#ffffff','#163a45','#ffffff']);
 assert.deepEqual(drawn.map(label=>String(label.text)),['0',String(ruler.miles/2),ruler.miles+' mi']);
}
MAP_VIEW='terrain'; assert.equal(mapLabelFont(12,false),'12px "Segoe UI", Arial, Helvetica, sans-serif');
"""
    subprocess.run([node, '-e', script], encoding='utf-8', check=True)
    draw = function_source('drawPlanar')
    assert 'drawPlanarRuler();' in draw
    assert 'mile radius' not in draw


def test_planar_location_borders_are_black_and_three_fifths_mile():
    import shutil
    import subprocess

    import pytest

    node = shutil.which('node')
    if not node:
        pytest.skip('Node.js is required for map behavior checks')
    start = MAP_JS.index("    var scaledBorder =")
    border = MAP_JS[start:MAP_JS.index("    if (MAP_VIEW === 'planar') { drawLocationTypeIcon", start)]
    script = """
const assert = require('node:assert/strict');
let MAP_VIEW='planar', selected=false, scale=1;
const s={data:{},px:0,py:0}; const r=5;
const strokes=[];
const ctx={stroke(){strokes.push({width:this.lineWidth,color:this.strokeStyle});},beginPath(){},arc(){}};
function planarScale(){return scale;}
function drawBorder(){
""" + border + """
}
for (const radius of [50,100,200,500]) {
 scale=400/radius;
 for (selected of [false,true]) {
  strokes.length=0; drawBorder();
  assert.equal(strokes.length,1);
  assert.equal(strokes[0].color,'#000000');
    assert(Math.abs(strokes[0].width/scale-0.6)<1e-12);
 }
}
selected=false; s.data.mobile=true; strokes.length=0; drawBorder();
assert.deepEqual(strokes,[{width:0.6*scale,color:'#000000'}]);
s.data.mobile=false; MAP_VIEW='terrain'; strokes.length=0; drawBorder();
assert.deepEqual(strokes,[{width:3,color:'#ffffff'}]);
"""
    subprocess.run([node, '-e', script], encoding='utf-8', check=True)


def test_junction_names_are_hidden_until_selected_or_all_labels_enabled():
    import shutil
    import subprocess

    import pytest

    node = shutil.which('node')
    if not node:
        pytest.skip('Node.js is required for map behavior checks')
    start = MAP_JS.index('function drawMapJunctions()')
    draw = MAP_JS[start:MAP_JS.index('function planarDistanceRuler(', start)]
    script = """
const assert = require('node:assert/strict');
const state = {selected:null};
const mapLegEdits = {junctions:{first:{name:'First',point:[10,20]},second:{name:'Second',point:[30,40]}}};
const cam = {cx:100,cy:100};
const labels=[]; let dots=0, scale=1;
const radii=[];
const borders=[];
function plannedLocation(){return false;}
const ctx = {save(){},restore(){},setLineDash(){},beginPath(){},arc(x,y,radius){dots++;radii.push(radius);},
 fill(){},stroke(){borders.push(this.lineWidth);},strokeText(){},fillText(text){labels.push(text);}};
function mapLabelScale(){return 1;} function mapLabelFont(){return '12px sans-serif';}
function planarPoint(east,south){return [east,south];} function planarScale(){return scale;}
""" + draw + """
drawMapJunctions(); assert.equal(dots,2); assert.deepEqual(labels,[]);
state.selected='junction:first'; drawMapJunctions();
assert.equal(dots,4); assert.deepEqual(labels,['First']);
labels.length=0; state.selected='waterdeep'; drawMapJunctions(); assert.deepEqual(labels,[]);
state.showAllLocationLabels=true; drawMapJunctions(); assert.deepEqual(labels,['First','Second']);
labels.length=0; state.showAllLocationLabels=false; drawMapJunctions(); assert.deepEqual(labels,[]);
state.junctionLabels='show'; drawMapJunctions(); assert.deepEqual(labels,['First','Second']);
labels.length=0; state.junctionLabels='hide'; state.showAllLocationLabels=true;
state.selected='junction:first'; const beforeHidden=dots;
drawMapJunctions(); assert.deepEqual(labels,[]); assert.equal(dots,beforeHidden+2);
state.showAllLocationLabels=false; drawMapJunctions(); assert.deepEqual(labels,[]);
state.junctionLabels='auto'; drawMapJunctions(); assert.deepEqual(labels,['First']);
state.selected=null; labels.length=0;
for (const radius of [50,100,200,500]) {
 scale=400/radius; radii.length=0;
 drawMapJunctions();
 assert(radii.every(value=>2*value/scale===5));
}
assert(borders.every(width=>width===3));
"""
    subprocess.run([node, '-e', script], encoding='utf-8', check=True)


def test_marker_label_settings_persist_independently():
    import shutil
    import subprocess

    import pytest

    node = shutil.which('node')
    if not node:
        pytest.skip('Node.js is required for map behavior checks')
    for html in (MAP_HTML, TERRAIN_HTML):
        assert html.count('id="junction-labels"') == 1
        assert html.count('id="company-labels"') == 1
        assert '<option value="auto" selected>Automatic</option>' in html
        assert '<option value="show">Show all</option>' in html
        assert '<option value="hide">Hide all</option>' in html
    assert "wireMarkerLabels('junction-labels', 'junctionLabels', 'Junction');" in MAP_JS
    assert "wireMarkerLabels('company-labels', 'companyLabels', 'Travelling company');" in MAP_JS
    code = MAP_JS[MAP_JS.index('function wireMarkerLabels('):MAP_JS.index('function wireControls(')]
    script = """
const assert=require('node:assert/strict');
function checkSetting(id,property,otherProperty){
const state={junctionLabels:'auto',companyLabels:'auto',showAllLocationLabels:true,labels:true};
let saved=null,blocked=false,invalidations=0;
const errors=[],messages=[];
const input={value:'',addEventListener(name,fn){this[name]=fn;}};
const document={getElementById(requested){assert.equal(requested,id);return input;}};
const window={localStorage:{
 getItem(key){assert.equal(key,'faerun-map-'+id);
  if(blocked)throw Error('Storage blocked');return saved;},
 setItem(key,value){assert.equal(key,'faerun-map-'+id);
  if(blocked)throw Error('Storage blocked');saved=value;}
}};
const console={error(...args){errors.push(args);}};
function showStatus(message,error){assert(error);messages.push(message);}
function invalidate(){invalidations++;}
""" + code + """
function wire(){wireMarkerLabels(id,property,'Marker');}
wire();assert.equal(input.value,'auto');assert.equal(saved,null);
for(const choice of ['show','hide','auto']){
 input.value=choice;input.change();assert.equal(state[property],choice);
 assert.equal(saved,choice);state[property]='auto';wire();
 assert.equal(input.value,choice);assert.equal(state[property],choice);
 assert.equal(state[otherProperty],'auto');
 assert(state.showAllLocationLabels);assert(state.labels);
}
saved='invalid';wire();assert.equal(errors.length,1);
blocked=true;wire();assert.equal(errors.length,2);
input.value='hide';input.change();assert.equal(state[property],'hide');
assert.equal(errors.length,3);assert(messages[2].includes('only to this page'));
assert.equal(invalidations,4);
}
checkSetting('junction-labels','junctionLabels','companyLabels');
checkSetting('company-labels','companyLabels','junctionLabels');
"""
    subprocess.run([node, '--check'], input=MAP_JS, encoding='utf-8', check=True)
    subprocess.run([node, '-e', script], encoding='utf-8', check=True)


def test_company_names_can_be_shown_or_hidden_independently_of_other_labels():
    import shutil
    import subprocess

    import pytest

    node = shutil.which('node')
    if not node:
        pytest.skip('Node.js is required for map behavior checks')
    code = MAP_JS[MAP_JS.index('function drawLabels('):MAP_JS.index('function planarScale(')]
    assert "if (state.labels || state.companyLabels === 'show') { drawLabels(order); }" in MAP_JS
    script = """
const assert=require('node:assert/strict');
let MAP_VIEW='planar';
const state={labels:true,showAllLocationLabels:false,companyLabels:'auto',selected:null,hover:-1};
const pins=[
 {px:10,py:10,data:{id:'town',name:'Town',population:50000}},
 {px:10,py:10,data:{id:'company',name:'Company',population:10,mobile:true,status:'encamped'}},
 {px:10,py:10,data:{id:'second',name:'Second company',population:10,mobile:true,status:'travelling'}}
];
const drawn=[];
const ctx={measureText(){return {width:100};},strokeText(){},
 fillText(text,x,y){drawn.push({text,x,y});}};
function mapLabelScale(){return 1;}
function mapLabelFont(){return '12px sans-serif';}
function mapPinRadius(){return 5;}
function caravanIconPosition(){return {x:100,y:50};}
""" + code + """
function names(){drawn.length=0;drawLabels([0,1,2]);return drawn.map(d=>d.text);}
for(const view of ['planar','overlay','terrain']){
 MAP_VIEW=view;state.labels=true;state.selected=null;state.hover=-1;
 state.showAllLocationLabels=false;state.companyLabels='auto';
 assert.deepEqual(names(),['Town']);
 state.companyLabels='show';
 assert.deepEqual(names(),['Second company','Company','Town']);
 assert.equal(drawn[0].x,110);assert.equal(drawn[0].y,46);
 assert.equal(drawn[1].x,110);assert.equal(drawn[1].y,view==='planar'?65:46);
 state.labels=false;assert.deepEqual(names(),['Second company','Company']);
 state.labels=true;state.showAllLocationLabels=true;state.companyLabels='hide';
 state.selected='company';state.hover=2;assert.deepEqual(names(),['Town']);
 state.companyLabels='auto';assert.deepEqual(names(),['Second company','Company','Town']);
 state.showAllLocationLabels=false;state.hover=-1;assert.deepEqual(names(),['Company','Town']);
}
"""
    subprocess.run([node, '-e', script], encoding='utf-8', check=True)


def test_all_location_labels_bypass_population_collisions_and_survey_budget():
    import shutil
    import subprocess

    import pytest

    node = shutil.which('node')
    if not node:
        pytest.skip('Node.js is required for map behavior checks')
    labels = MAP_JS[MAP_JS.index('function drawLabels('):MAP_JS.index('function planarScale(')]
    places = MAP_JS[MAP_JS.index('function paintPlaces('):MAP_JS.index('var routeSpec =')]
    script = """
const assert=require('node:assert/strict');
let MAP_VIEW='planar';
const state={labels:true,showAllLocationLabels:false,exag:0,selected:null,hover:-1};
const drawn=[];
const ctx={measureText(){return {width:100};},strokeText(){},fillText(text){drawn.push(text);},
 beginPath(){},arc(){},fill(){},stroke(){}};
function mapLabelScale(){return 1;}
function mapLabelFont(size,bold){return (bold?'bold ':'')+size+'px sans-serif';}
function mapPinRadius(){return 5;}
function planarScale(){return 1;}
function locationVisible(data){return data.verified;}
function project(x,y,z){return x<0?null:[x,z,1];}
const pins=[
 {data:{id:'small',name:'Small village',population:10},px:10,py:10},
 {data:{id:'large',name:'Large city',population:50000},px:10,py:10},
 {data:{id:'other',name:'Other city',population:50000},px:10,py:10}
];
const placeDots=Array.from({length:100},(_,i)=>({
 data:{verified:true},name:'Site '+i,sx:i*100,sz:0,h:0
}));
placeDots.push({data:{verified:false},name:'Filtered',sx:10,sz:10,h:0},
 {data:{verified:true},name:'Not projected',sx:-1,sz:10,h:0});
""" + labels + places + """
for(const view of ['planar','overlay','terrain']){
 MAP_VIEW=view;drawn.length=0;state.showAllLocationLabels=false;
 drawLabels([0,1,2]);assert.deepEqual(drawn,['Other city']);
 state.selected='small';drawn.length=0;drawLabels([0,1,2]);
 assert.deepEqual(drawn,['Other city','Small village']);state.selected=null;
 state.showAllLocationLabels=true;drawn.length=0;drawLabels([0,1,2]);
 assert.deepEqual(drawn,['Other city','Large city','Small village']);
}
state.showAllLocationLabels=false;drawn.length=0;paintPlaces();assert.equal(drawn.length,80);
state.showAllLocationLabels=true;drawn.length=0;paintPlaces();assert.equal(drawn.length,100);
assert(!drawn.includes('Filtered'));assert(!drawn.includes('Not projected'));
placeDots.forEach(p=>{if(p.sx>=0)p.sx=0;});
state.showAllLocationLabels=false;drawn.length=0;paintPlaces();assert.equal(drawn.length,1);
state.showAllLocationLabels=true;drawn.length=0;paintPlaces();assert.equal(drawn.length,100);
state.labels=false;drawn.length=0;paintPlaces();assert.equal(drawn.length,0);
"""
    subprocess.run([node, '-e', script], encoding='utf-8', check=True)


def test_all_location_labels_toggle_persists_and_syncs_label_visibility():
    import shutil
    import subprocess

    import pytest

    node = shutil.which('node')
    if not node:
        pytest.skip('Node.js is required for map behavior checks')
    for html in (MAP_HTML, TERRAIN_HTML):
        assert html.count('id="show-all-location-labels"') == 1
        assert '> Show all location labels</label>' in html
    assert '  wireLocationLabels();' in MAP_JS
    code = MAP_JS[MAP_JS.index('function wireLocationLabels('):MAP_JS.index('function wireControls(')]
    script = """
const assert=require('node:assert/strict');
const state={labels:true,showAllLocationLabels:false};
let saved=null,blocked=false,invalidations=0;
const errors=[],messages=[],controls={};
for(const id of ['show-all-location-labels','opt-labels']){
 controls[id]={checked:false,addEventListener(name,fn){this[name]=fn;}};
}
const document={getElementById(id){return controls[id];}};
const window={localStorage:{
 getItem(key){assert.equal(key,'faerun-map-show-all-location-labels');
  if(blocked)throw Error('Storage blocked');return saved;},
 setItem(key,value){assert.equal(key,'faerun-map-show-all-location-labels');
  if(blocked)throw Error('Storage blocked');saved=value;}
}};
const console={error(...args){errors.push(args);}};
function showStatus(message,error){assert(error);messages.push(message);}
function invalidate(){invalidations++;}
""" + code + """
const all=controls['show-all-location-labels'],labels=controls['opt-labels'];
wireLocationLabels();assert(!all.checked);assert(labels.checked);assert.equal(saved,null);
all.checked=true;all.change();assert(state.showAllLocationLabels);assert.equal(saved,'true');
state.showAllLocationLabels=false;wireLocationLabels();assert(all.checked);
all.checked=false;all.change();assert(!state.showAllLocationLabels);assert(state.labels);
assert.equal(saved,'false');wireLocationLabels();assert(!all.checked);
labels.checked=false;labels.change();assert(!state.labels);
all.checked=true;all.change();assert(state.labels);assert(labels.checked);
labels.checked=false;labels.change();assert(!all.checked);assert(!state.showAllLocationLabels);
assert.equal(saved,'false');
saved='true';wireLocationLabels();assert(state.labels);assert(labels.checked);assert(all.checked);
saved='invalid';wireLocationLabels();assert.equal(errors.length,1);
blocked=true;wireLocationLabels();assert.equal(errors.length,2);
all.checked=false;all.change();assert(!state.showAllLocationLabels);
assert.equal(errors.length,3);assert(messages[2].includes('only to this page'));
assert.equal(invalidations,6);
"""
    subprocess.run([node, '--check'], input=MAP_JS, encoding='utf-8', check=True)
    subprocess.run([node, '-e', script], encoding='utf-8', check=True)


def test_planar_multiple_types_straightening_and_marker_layers():
    import shutil
    import subprocess

    import pytest

    node = shutil.which('node')
    if not node:
        pytest.skip('Node.js is required for map behavior checks')
    subprocess.run([node, '--check'], input=MAP_JS, encoding='utf-8', check=True)
    for html in (MAP_HTML, TERRAIN_HTML):
        assert 'id="planar-leg-options"' in html
        assert 'id="leg-straighten"' in html
    straighten = MAP_JS[MAP_JS.index('function straightenLeg()'):
                        MAP_JS.index('function syncPlanarLegFilter()')]
    visible = MAP_JS[MAP_JS.index('function planarLegVisible('):
                     MAP_JS.index('function strokePlanarLeg(')]
    draw = MAP_JS[MAP_JS.index('function drawPlanar()'):MAP_JS.index('function draw()')]
    history = MAP_JS[MAP_JS.index('function rememberLeg()'):MAP_JS.index('function legWorldPoint(')]
    script = """
const assert = require('node:assert/strict');
const state = {planarLegTypes: ['road', 'track'], tx:0, tz:0, planarRadius:200, routes:true};
const legEditor = {enabled:false, saving:false, undo:[], redo:[],
  draft:{points:[[0,0],[5,5],[10,0]], path:[[0,0],[2,4],[5,5],[8,4],[10,0]], pointIndices:[0,2,4]}};
function syncLegEditor(){} function invalidate(){}
""" + straighten + visible + history + """
assert(planarLegVisible({kind:'road'})); assert(planarLegVisible({kind:'track'}));
assert(!planarLegVisible({kind:'sea'})); assert(!planarLegVisible({kind:'trail'}));
state.planarLegTypes=[]; assert(planarLegVisible({kind:'sea'}));
const original=JSON.parse(JSON.stringify(legEditor.draft));
legEditor.saving=true; straightenLeg(); assert.deepEqual(legEditor.draft,original);
legEditor.saving=false; straightenLeg();
assert.deepEqual(legEditor.draft.points,original.points);
assert(!('path' in legEditor.draft)); assert(!('pointIndices' in legEditor.draft)); assert(legEditor.dirty);
legHistory(true); assert.deepEqual(legEditor.draft,original);
legHistory(false); assert(!legEditor.draft.path);
straightenLeg(); assert.equal(legEditor.undo.length,1);
const calls=[];
const mesh={cx:0,cy:0,bounds:[0,0],W:0,H:0,cellW:1,cellH:1}; const cam={cx:0,cy:0}; const SCALE=1;
const ctx=new Proxy({}, {get:(_,name)=>name==='measureText'?()=>({width:1}):()=>{}});
function drawSky(){} function planarScale(){return 1;} function drawPlanarGrid(){}
function drawPlaces(){calls.push('places');} function drawPins(){calls.push('pins');}
function drawMapJunctions(){calls.push('junctions');} function drawPlanarLegs(){calls.push('legs');}
function strokePlanarLeg(){calls.push('highlight');}
function drawPlanarItinerary(){if(state.planRoute && !legEditor.enabled)calls.push('highlight');}
function drawLocationDraft(){}
function drawPlanarRuler(){}
""" + draw + """
state.planRoute={mapRoads:true,legs:[{points:[]}]};
drawPlanar(); assert.deepEqual(calls,['legs','highlight','places','pins','junctions']); calls.length=0;
legEditor.enabled=true; drawPlanar(); assert.deepEqual(calls,['places','pins','junctions','legs']);
"""
    subprocess.run([node, '-e', script], encoding='utf-8', check=True)


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
    assert "showStatus(detail.cellMiles + '-mile terrain detail')" in MAP_JS
    # Reaching a one-mile cell needs both limits to follow the camera in: the
    # distance floor and the near plane were fixed at 350 and 60 miles.
    assert "function minDistance()" in MAP_JS
    assert "mesh.cellW * 4 / SCALE" in MAP_JS
    assert "clamp(state.dist * factor, minDistance(), 12)" in MAP_JS
    assert "cam.near = Math.min(0.06, state.dist * 0.02)" in MAP_JS
    assert "if (vz < cam.near) { return null; }" in MAP_JS
    # projectVertices is the hot loop and keeps its own copy of the near plane;
    # leaving it at a fixed 0.06 culls the whole mesh once you zoom past it.
    assert "if (d < near) { ok[k] = 0; continue; }" in MAP_JS
    assert "clamp(state.dist, 0.35, 12)" not in MAP_JS


def test_terrain_drawing_is_bounded_by_a_cell_budget_not_by_the_grid_size():
    """A five-mile world field is half a million cells; the canvas can fill
    about sixteen thousand a frame, so the renderer takes a window of the grid
    and walks it on a lattice rather than drawing every cell."""
    assert "var TERRAIN_BUDGET = 16000;" in MAP_JS
    assert "function updateViewWindow()" in MAP_JS
    assert "while (step < 64 && visible / (step * step) > budget) { step++; }" in MAP_JS
    # The lattice is aligned so cells do not shimmer while panning.
    assert "view.i0 -= view.i0 % step;" in MAP_JS
    assert "updateViewWindow();" in MAP_JS
    # Every consumer of the shared vertex arrays has to honour the window.
    for drawer in ("function drawTerrain()", "function drawTowers()",
                   "function drawSquareGrid()"):
        body = MAP_JS[MAP_JS.index(drawer):MAP_JS.index(drawer) + 600]
        assert "view.step" in body, drawer
        assert "state.step" not in body, drawer
    assert "ok.fill(0);" in MAP_JS
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
        switch = MAP_JS[MAP_JS.index("async function setMapView(view)"):
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
(async () => {
await setMapView('terrain');
assert.equal(state.underOn, false);
assert.equal(state.calibOn, false);
assert.equal(checkbox.checked, false);
assert.equal(bodyView, 'terrain');
assert.equal(radios[1].checked, true);
assert.equal(new URL(window.location.href).pathname, '/map.html');
await setMapView('overlay');
assert.equal(state.underOn, true);
assert.equal(bodyView, 'overlay');
assert.equal(radios[0].checked, true);
assert.equal(new URL(window.location.href).searchParams.get('settlement'), 'daggerford');
assert.equal(new URL(window.location.href).searchParams.get('view'), 'overlay');
for (const key of ['selected', 'selectedRoute', 'heat', 'tx', 'tz', 'dist',
                                     'pitch', 'yaw', 'selectedCarrierService', 'detailId', 'exag']) {
    assert.equal(state[key], before[key], key);
}
await setMapView('invalid');
assert.equal(MAP_VIEW, 'overlay');
let leaveAllowed = false;
globalThis.discardLegDraft = async () => leaveAllowed;
MAP_VIEW = 'planar';
await setMapView('overlay');
assert.equal(MAP_VIEW, 'planar');
leaveAllowed = true;
await setMapView('overlay');
assert.equal(MAP_VIEW, 'overlay');
})().catch(error => {console.error(error); process.exitCode=1;});
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
    assert "drawUnderlayLayer(img, posterOnly ? 1 : state.underAlpha, posterOnly)" in MAP_JS
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
