"""World events browser and editor assets."""

from typing import Dict, Tuple


EVENTS_HTML = """<!DOCTYPE html>
<html lang=\"en\"><head><meta charset=\"utf-8\"><meta name=\"viewport\" content=\"width=device-width,initial-scale=1\">
<title>Faerun Events</title><link rel=\"stylesheet\" href=\"app.css\"><link rel=\"stylesheet\" href=\"detail.css\">
<style>
.events-page .events-layout { display:grid; grid-template-columns:minmax(260px,320px) minmax(0,1fr); gap:28px; align-items:start; }
.events-page .event-editor,.events-page .event-card { border:1px solid var(--cp-border); border-radius:18px; padding:22px; background:var(--cp-surface); box-shadow:0 8px 24px rgba(25,35,45,.08); }
.events-page .event-editor { position:sticky; top:20px; background:var(--cp-surface-soft); }
.events-page .event-editor label { display:grid; gap:7px; margin-bottom:14px; color:var(--cp-text-muted); font-size:12px; }
.events-page .event-editor input,.events-page .event-editor select,.events-page .event-editor textarea { width:100%; min-height:42px; box-sizing:border-box; padding:9px 11px; border:1px solid var(--cp-border); border-radius:10px; background:var(--cp-surface); color:var(--cp-text); font:inherit; }
.events-page .event-editor textarea { min-height:100px; resize:vertical; }
.events-page .event-card { margin-bottom:16px; }
.events-page .event-card h2 { margin:0 0 6px; }
.events-page .event-meta { display:flex; flex-wrap:wrap; gap:7px; margin:10px 0; }
.events-page .event-meta span { padding:5px 8px; border-radius:8px; background:var(--cp-accent-soft); color:var(--cp-accent); font-size:12px; }
.events-page .event-description { line-height:1.65; color:var(--cp-text-muted); }
.events-page .event-actions { display:flex; gap:8px; margin-top:16px; }
@media(max-width:760px){.events-page .events-layout{display:block}.events-page .event-editor{position:static;margin-bottom:24px}}
</style></head><body class=\"events-page\">
<header class=\"topbar\"><div class=\"brand\"><div><h1>World Events</h1><p class=\"tagline\">Active events, their stories, and the forces reshaping local markets.</p></div></div>
<div class=\"worldbar\"><div class=\"date-controls\"><span class=\"pill\" data-world-date>&#8230;</span></div><nav class=\"nav-links\" aria-label=\"Main navigation\"><a class=\"navlink\" href=\"index.html\">Markets</a><a class=\"navlink\" href=\"location.html\">Locations</a><a class=\"navlink\" href=\"business.html\">Businesses</a><a class=\"navlink\" href=\"product.html\">Products</a><a class=\"navlink\" href=\"route.html\">Routes</a><a class=\"navlink\" href=\"map.html\">Map</a><a class=\"navlink\" href=\"planner.html\">Route planner</a><a class=\"navlink\" href=\"mobile.html\">Travelling companies</a><a class=\"navlink\" href=\"trade.html\">Merchant guild &amp; POs</a><a class=\"navlink navlink-current\" aria-current=\"page\">Events</a><a class=\"navlink\" href=\"board.html\">Request board</a></nav></div></header>
<main class=\"detail-shell\"><div id=\"status\" class=\"status\" role=\"status\"></div><div class=\"events-layout\"><aside class=\"event-editor\"><h2 id=\"editor-title\">Add event</h2><form id=\"event-form\"><label>Template<select id=\"template\"></select></label><label>Scope<select id=\"scope\"><option value=\"settlement\">Settlement</option><option value=\"region\">Region</option><option value=\"zone\">Zone</option></select></label><label>Target<input id=\"target\" list=\"targets\" required></label><datalist id=\"targets\"></datalist><label>Narrative<textarea id=\"description\" placeholder=\"What is happening, and why does it matter?\"></textarea></label><button class=\"primary\" type=\"submit\">Save event</button><button id=\"cancel-edit\" type=\"button\" hidden>Cancel edit</button></form></aside><section><div id=\"events-list\"></div></section></div></main><script src=\"date.js\"></script><script src=\"events.js\"></script></body></html>"""

EVENTS_JS = """
let boot=null, editing=null;
const $=id=>document.getElementById(id);
function esc(value){return String(value==null?'':value).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/\"/g,'&quot;').replace(/'/g,'&#39;');}
function setStatus(value,error){$('status').textContent=value||'';$('status').className='status'+(error?' error':'');}
async function api(path,body){const options={headers:{'Accept':'application/json'}};if(body){options.method='POST';options.headers['Content-Type']='application/json';options.body=JSON.stringify(body);}const response=await fetch(path,options);const data=await response.json();if(!response.ok)throw new Error(data.error||response.statusText);return data;}
function targets(){const scope=$('scope').value;const values=scope==='settlement'?boot.settlements.map(s=>s.name):scope==='region'?boot.regions:boot.settlements.map(s=>s.zone);$('targets').innerHTML=[...new Set(values)].sort().map(value=>'<option value=\"'+esc(value)+'\">').join('');}
function render(){const events=boot.events||[];$('events-list').innerHTML=events.length?events.map(event=>'<article class=\"event-card\"><h2>'+esc(event.name)+'</h2><div class=\"event-meta\"><span>'+esc(event.kind)+'</span><span>Risk '+Number(event.risk||0).toFixed(2)+'</span><span>Supply '+Number(event.supply||1).toFixed(2)+'x</span><span>Demand '+Number(event.demand||1).toFixed(2)+'x</span></div><p class=\"event-description\">'+esc(event.description||'No narrative recorded.')+'</p><p class=\"muted\">'+esc((event.settlements||[]).join(', ')|| (event.regions||[]).join(', ') || (event.zones||[]).join(', ') || 'World-wide')+'</p><div class=\"event-actions\"><button type=\"button\" data-edit=\"'+esc(event.id)+'\">Edit</button><button type=\"button\" data-remove=\"'+esc(event.id)+'\">Remove</button></div></article>').join(''):'<p class=\"empty\">No active events.</p>';}
function reset(){editing=null;$('editor-title').textContent='Add event';$('event-form').reset();$('cancel-edit').hidden=true;targets();}
async function load(){boot=await api('/api/bootstrap');showWorldDate(boot);$('template').innerHTML=boot.event_templates.map(name=>'<option value=\"'+esc(name)+'\">'+esc(name)+'</option>').join('');targets();render();}
$('scope').addEventListener('change',targets);
$('event-form').addEventListener('submit',async event=>{event.preventDefault();try{if(editing)await api('/api/events/clear',{id:editing});boot=await api('/api/event',{template:$('template').value,scope:$('scope').value,target:$('target').value,description:$('description').value});reset();render();setStatus('Event saved.');}catch(error){setStatus(error.message,true);}});
$('cancel-edit').addEventListener('click',reset);
$('events-list').addEventListener('click',async event=>{const edit=event.target.closest('[data-edit]'),remove=event.target.closest('[data-remove]');try{if(remove){boot=await api('/api/events/clear',{id:remove.dataset.remove});render();}else if(edit){const row=boot.events.find(item=>item.id===edit.dataset.edit);if(!row)return;editing=row.id;$('editor-title').textContent='Edit event';$('template').value=boot.event_templates.includes(row.template)?row.template:boot.event_templates[0];$('scope').value=row.settlements.length?'settlement':row.regions.length?'region':'zone';targets();$('target').value=(row.settlements||row.regions||row.zones||[])[0]||'';$('description').value=row.description||'';$('cancel-edit').hidden=false;window.scrollTo({top:0,behavior:'smooth'});}}catch(error){setStatus(error.message,true);}});
load().catch(error=>setStatus(error.message,true));
"""

EVENTS_ASSETS: Dict[str, Tuple[str, str]] = {
    "events.html": (EVENTS_HTML, "text/html; charset=utf-8"),
    "events.js": (EVENTS_JS, "application/javascript; charset=utf-8"),
}
""