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
@media (max-width: 760px) {
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
<body><header class="topbar"><div class="brand"><span class="mark">&#9670;</span><div><h1>Product Detail</h1><p class="tagline">Composition, quality, production and market access.</p></div></div>
<nav class="worldbar"><span class="pill" data-world-date>&#8230;</span><a class="navlink" href="index.html">Commodity board</a><a class="navlink" href="location.html">Locations</a><a class="navlink" href="route.html">Routes</a><a class="navlink" href="map.html">Map</a><a class="navlink" href="trade.html">Merchant guild &amp; POs</a></nav></header>
<main class="detail-shell"><form id="controls" class="detail-controls"><label>Product<input id="product" list="products" autocomplete="off"></label><datalist id="products"></datalist><label>Market<input id="market" list="markets" autocomplete="off"></label><datalist id="markets"></datalist><button class="primary" type="submit">Open</button></form>
<div id="status" class="status" role="status">Loading product details...</div><h1 id="title" class="detail-title">Product</h1><p id="subtitle" class="detail-subtitle"></p><div id="content" class="detail-grid"></div></main><script src="date.js"></script><script src="product.js"></script></body></html>"""


ROUTE_HTML = """<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Faerun Route Detail</title><link rel="stylesheet" href="app.css"><link rel="stylesheet" href="detail.css"></head>
<body><header class="topbar"><div class="brand"><span class="mark">&#8644;</span><div><h1>Route Detail</h1><p class="tagline">Carriage time, freight, hazards and every transfer.</p></div></div>
<nav class="worldbar"><span class="pill" data-world-date>&#8230;</span><a class="navlink" href="index.html">Commodity board</a><a class="navlink" href="location.html">Locations</a><a class="navlink" href="product.html">Products</a><a class="navlink" href="map.html">Map</a><a class="navlink" id="carrier-planner" href="planner.html">Carrier planner</a></nav></header>
<main class="detail-shell"><form id="controls" class="detail-controls"><label>Origin<input id="origin" list="places" autocomplete="off"></label><label>Destination<input id="destination" list="places" autocomplete="off"></label><datalist id="places"></datalist><label>Optimize<select id="optimise"><option value="days">Travel time</option><option value="cost">Freight cost</option></select></label><button class="primary" type="submit">Plan route</button></form>
<div id="status" class="status"></div><h1 id="title" class="detail-title">Route</h1><p id="subtitle" class="detail-subtitle"></p><div id="content" class="detail-grid"></div></main><script src="date.js"></script><script src="route.js"></script></body></html>"""


COMMON_JS = """
function esc(v){return String(v==null?'':v).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/\"/g,'&quot;');}
function coin(v){if(v==null)return '-';var digits=Math.abs(v)<1?3:2;return Number(v).toLocaleString(undefined,{minimumFractionDigits:digits,maximumFractionDigits:3})+' gp';}
function markup(v){return Number.isFinite(v)?v.toFixed(1)+'%':'-';}
function stockUnits(v){return Number.isFinite(v)?v.toLocaleString():'-';}
function query(k){return new URLSearchParams(location.search).get(k)||'';}
async function get(path,params){var u=new URL(path,location.origin);Object.keys(params||{}).forEach(function(k){if(params[k])u.searchParams.set(k,params[k]);});var r=await fetch(u);var d=await r.json();if(!r.ok)throw new Error(d.error||r.statusText);return d;}
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
document.getElementById('content').innerHTML='<section class="detail-section wide"><div class="product-specs"><span>Category <b>'+esc(data.commodity.category)+'</b></span><span>Trade unit <b>'+esc(data.commodity.unit)+'</b></span><span>Weight <b>'+esc(data.commodity.weight)+' lb</b></span><span>Type <b>'+esc(data.commodity.production_type)+'</b></span><span>Base price <b>'+esc(coin(data.commodity.base_price))+'</b></span></div><div class="market-quote"><h2>Standard grade in '+esc(quote.settlement)+'</h2><div class="facts">'+fact('Buy from merchant / '+data.commodity.unit,coin(standard.price))+fact('Sell to merchant / '+data.commodity.unit,coin(standard.buy_price==null?quote.buy_price:standard.buy_price))+fact('Merchant markup',markup(standard.merchant_markup_pct))+fact('Availability',standard.availability)+fact('Modeled grade stock',Number(standard.stock).toLocaleString())+fact('Uncommitted grade stock',stockUnits(standard.uncommitted_stock))+'</div><p>Markup is quoted resale price divided by the merchant purchase offer, minus one; it is before costs and losses. '+esc(seasonalFreeBasis(quote))+'</p><p>'+esc(seasonalStockBasis(quote))+'</p></div></section>'+
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
document.getElementById('controls').addEventListener('submit',function(e){e.preventDefault();load();});start().catch(function(e){setStatus(e.message,true);});
"""


ROUTE_JS = COMMON_JS + """
document.getElementById('carrier-planner').addEventListener('click',function(){this.href='planner.html?'+new URLSearchParams({origin:document.getElementById('origin').value||'Waterdeep',destination:document.getElementById('destination').value||'Daggerford'});});
async function load(){var origin=document.getElementById('origin').value||'Waterdeep';var destination=document.getElementById('destination').value||'Daggerford';var optimise=document.getElementById('optimise').value;setStatus('Planning route...');try{var d=await get('/api/route',{origin:origin,destination:destination,optimise:optimise});if(!d.reachable)throw new Error('No route connects these settlements.');history.replaceState(null,'','route.html?origin='+encodeURIComponent(d.origin)+'&destination='+encodeURIComponent(d.destination)+'&optimise='+optimise);document.getElementById('origin').value=d.origin;document.getElementById('destination').value=d.destination;document.getElementById('title').textContent=d.origin+' to '+d.destination;document.getElementById('subtitle').textContent='Optimized for '+(optimise==='cost'?'freight cost':'travel time')+'.';var legs=d.legs.map(function(l,i){return '<div class="route-leg"><div><b>'+(i+1)+'. '+esc(l.from)+' to '+esc(l.to)+'</b><small>'+esc(l.via||'local track')+' · '+esc(l.mode_label)+'</small></div><div><b>'+Math.round(l.miles).toLocaleString()+' mi</b><small>distance</small></div><div><b>'+Number(l.days).toFixed(1)+' days</b><small>travel</small></div><div><b>'+Number(l.hazard).toFixed(2)+'x</b><small>hazard</small></div></div>';}).join('');document.getElementById('content').innerHTML='<section class="detail-section wide"><div class="facts">'+fact('Distance',Math.round(d.distance).toLocaleString()+' mi')+fact('Travel time',Number(d.days).toFixed(1)+' days')+fact('Freight / 100 lb',coin(d.freight_gp_per_100lb))+fact('Hazard',Number(d.hazard).toFixed(2)+'x')+'</div></section><section class="detail-section wide"><h2>Itinerary</h2>'+legs+'</section><section class="detail-section"><h2>Route profile</h2><div class="facts">'+fact('Modes',d.modes.join(' + '))+fact('Transfers',d.transfers)+fact('Caravan time',Number(d.caravan_days).toFixed(1)+' days')+fact('Stops',d.path.length)+'</div></section><section class="detail-section"><h2>Endpoints</h2><p><a href="location.html?settlement='+encodeURIComponent(d.origin)+'">'+esc(d.origin)+'</a> to <a href="location.html?settlement='+encodeURIComponent(d.destination)+'">'+esc(d.destination)+'</a></p></section>';setStatus('');}catch(e){setStatus(e.message,true);}}
async function start(){var boot=await get('/api/bootstrap');showWorldDate(boot);document.getElementById('places').innerHTML=boot.settlements.map(function(s){return '<option value="'+esc(s.name)+'">'+esc(s.region)+'</option>';}).join('');document.getElementById('origin').value=query('origin')||'Waterdeep';document.getElementById('destination').value=query('destination')||'Daggerford';document.getElementById('optimise').value=query('optimise')||'days';load();}
document.getElementById('controls').addEventListener('submit',function(e){e.preventDefault();load();});start().catch(function(e){setStatus(e.message,true);});
"""


DETAIL_ASSETS: Dict[str, Tuple[str, str]] = {
    "product.html": (PRODUCT_HTML, "text/html; charset=utf-8"),
    "product.js": (PRODUCT_JS, "application/javascript; charset=utf-8"),
    "route.html": (ROUTE_HTML, "text/html; charset=utf-8"),
    "route.js": (ROUTE_JS, "application/javascript; charset=utf-8"),
    "detail.css": (DETAIL_CSS, "text/css; charset=utf-8"),
}