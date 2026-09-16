"""Mobile-location profile page served by :mod:`faerun.web`."""

from typing import Dict, Tuple


MOBILE_HTML = """<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Faerun Travelling Company</title>
<link rel="stylesheet" href="app.css"><link rel="stylesheet" href="detail.css"><link rel="stylesheet" href="mobile.css"></head>
<body><header class="topbar"><div class="brand"><span class="mark">&#9672;</span><div>
<h1>Travelling Company</h1><p class="tagline">A dated mobile household, caravan and market participant.</p>
</div></div><nav class="worldbar" aria-label="Main"><span class="pill" data-world-date>&#8230;</span>
<a class="navlink" href="index.html">Commodity board</a><a class="navlink" href="map.html">World map</a>
<a class="navlink" href="planner.html">Route planner</a></nav></header>
<main class="detail-shell mobile-shell"><form id="controls" class="detail-controls"><label>Company
<input id="mobile-location" list="mobile-locations" autocomplete="off"></label>
<datalist id="mobile-locations"></datalist><button class="primary" type="submit">Open</button></form>
<div id="status" class="status" role="status">Loading travelling company...</div>
<section id="hero"></section>
<div class="mobile-report-controls">
<button id="generate-report" type="button" class="primary" disabled>Generate economic report</button>
<button id="download-report" type="button" class="ghost" disabled>Download report JSON</button>
</div>
<section id="economic-report" aria-label="Economic report" aria-busy="false" hidden></section>
<div id="content"></div></main>
<script src="date.js"></script><script src="mobile.js"></script></body></html>"""


MOBILE_CSS = """
.mobile-shell .mobile-hero { padding: 28px 0 24px; }
.mobile-shell .mobile-hero h2 { font-size: 30px; font-weight: 600; margin: 8px 0; overflow-wrap: anywhere; }
.mobile-shell .mobile-hero p { max-width: 76ch; margin: 0 0 16px; color: var(--cp-text-muted); line-height: 1.7; }
.mobile-shell .chips { display: flex; flex-wrap: wrap; gap: 8px; }
.mobile-shell .chip { padding: 4px 9px; border: 1px solid var(--cp-border); border-radius: 6px; font-size: 12px; background: var(--cp-surface-soft); }
.mobile-shell .detail-grid { margin-top: 28px; }
.mobile-shell .detail-section h3 { font-size: 18px; font-weight: 600; margin: 0 0 16px; }
.mobile-shell .detail-section p { line-height: 1.7; color: var(--cp-text-muted); overflow-wrap: anywhere; }
.mobile-shell .detail-section ul { padding-left: 20px; margin: 0 0 24px; line-height: 1.7; }
.mobile-shell .detail-section li { margin-bottom: 6px; overflow-wrap: anywhere; }
.mobile-shell .table-scroll { max-width: 100%; }
.mobile-shell .detail-table { min-width: 0; }
.mobile-shell .detail-table th, .mobile-shell .detail-table td { vertical-align: top; }
.mobile-shell .mobile-table td:first-child { overflow-wrap: anywhere; }
.mobile-shell .mobile-table td:last-child, .mobile-shell .mobile-table th:last-child { text-align: right; white-space: nowrap; font-variant-numeric: tabular-nums; }
.mobile-shell .mobile-itinerary { min-width: 760px; }
.mobile-shell .mobile-itinerary tr.active { background: var(--cp-accent-soft); box-shadow: inset 3px 0 var(--cp-accent); }
.mobile-report-controls { display: flex; gap: 10px; flex-wrap: wrap; margin: 0 0 16px; }
.mobile-report-controls button { white-space: normal; }
.mobile-shell #economic-report { margin-bottom: 32px; }
.mobile-shell #economic-report h2 { font-size: 22px; margin: 0 0 8px; }
.mobile-shell #economic-report > p { color: var(--cp-text-muted); line-height: 1.7; overflow-wrap: anywhere; }
@media (max-width: 760px) {
  .mobile-shell .mobile-hero { padding: 24px 0 20px; }
  .mobile-shell .mobile-hero h2 { font-size: 28px; }
  .mobile-report-controls button { width: 100%; }
}
"""


MOBILE_JS = """
function esc(v){return String(v==null?'':v).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');}
function query(k){return new URLSearchParams(location.search).get(k)||'';}
function label(v){return String(v).replace(/_/g,' ').replace(/\\b\\w/g,function(c){return c.toUpperCase();});}
function number(v,d){return Number(v).toLocaleString(undefined,{maximumFractionDigits:d==null?1:d});}
function fact(name,value){return '<div class="fact"><b>'+esc(value)+'</b><span>'+esc(name)+'</span></div>';}
function rows(obj,suffix){return Object.keys(obj||{}).map(function(k){return '<tr><td>'+esc(label(k))+'</td><td>'+number(obj[k])+(suffix||'')+'</td></tr>';}).join('');}
function table(head,body,name){return '<div class="table-scroll" tabindex="0" role="region" aria-label="'+esc(name)+'"><table class="detail-table '+(head.length>2?'mobile-itinerary':'mobile-table')+'"><thead><tr>'+head.map(function(h){return '<th scope="col">'+esc(h)+'</th>';}).join('')+'</tr></thead><tbody>'+body+'</tbody></table></div>';}
async function get(path){var response=await fetch(path);var data=await response.json();if(!response.ok)throw new Error(data.error||response.statusText);return data;}
function setStatus(text,error){var node=document.getElementById('status');node.textContent=text||'';node.className='status'+(error?' error':'');}
function render(data){
  var pos=data.position, host=pos.host;
  history.replaceState(null,'','mobile.html?id='+encodeURIComponent(data.id));
  document.getElementById('mobile-location').value=data.name;
  document.getElementById('hero').innerHTML='<div class="mobile-hero"><p>'+esc(pos.status==='encamped'?'Encamped':'On the road')+' &middot; '+esc(data.date)+'</p><h2>'+esc(data.name)+'</h2><p>'+esc(data.description)+'</p><div class="chips">'+data.traits.map(function(v){return '<span class="chip">'+esc(label(v))+'</span>';}).join('')+'</div></div>'+
    '<div class="facts">'+fact('Population',number(data.population,0))+fact('Households',number(data.households,0))+fact('Wagons',number(data.wagons.living+data.wagons.freight,0))+fact('Horses',number(data.animals.draft_horses+data.animals.riding_horses+data.animals.remount_horses,0))+'</div>';
  var position='<p><b>'+esc(pos.status==='encamped'?'Camped at '+host.name:'Travelling from '+pos.origin.name+' to '+pos.destination.name)+'</b></p>'+
    (pos.camp?'<p>Camp: '+esc(pos.camp)+'</p>':'')+(pos.route?'<p>Route: '+esc(pos.route)+' &middot; '+number(pos.progress*100,0)+'% complete</p>':'')+
    (host?'<p><a href="location.html?settlement='+encodeURIComponent(host.id)+'">Open host settlement</a> &middot; <a href="index.html?settlement='+encodeURIComponent(host.id)+'">Open host market</a></p>':'')+
    '<p>'+esc(data.market_access.notes)+'</p>';
  var itinerary=data.itinerary.map(function(row){var where=row.kind==='camp'?label(row.origin):(label(row.origin)+' to '+label(row.destination));return '<tr class="'+(row.active?'active':'')+'"><td>'+esc(row.start)+'</td><td>'+esc(row.end)+'</td><td>'+esc(label(row.kind))+'</td><td>'+esc(where)+'</td><td>'+esc(row.camp||row.route||'')+'</td></tr>';}).join('');
  var req=data.requirements;
  var requirements='<tr><td>Food</td><td>'+number(req.food_lb_per_day.low)+'-'+number(req.food_lb_per_day.high)+' lb/day</td></tr>'+
    '<tr><td>Essential human water</td><td>'+number(req.essential_water_gallons_per_day)+' gal/day</td></tr>'+
    '<tr><td>Total domestic water</td><td>'+number(req.domestic_water_gallons_per_day)+' gal/day</td></tr>'+
    '<tr><td>Animal water</td><td>'+number(req.animal_water_gallons_per_day)+' gal/day</td></tr>'+
    '<tr><td>Fodder</td><td>'+number(req.fodder_lb_per_day.low)+'-'+number(req.fodder_lb_per_day.high)+' lb/day</td></tr>'+
    '<tr><td>Fuel</td><td>'+number(req.fuel_lb_per_day.low)+'-'+number(req.fuel_lb_per_day.high)+' lb/day</td></tr>';
  document.getElementById('content').innerHTML='<div class="detail-grid">'+
    '<section class="detail-section"><h3>Current position</h3>'+position+'</section>'+
    '<section class="detail-section"><h3>Daily requirements</h3>'+table(['Need','Quantity'],requirements,'Daily requirements')+'</section>'+
    '<section class="detail-section"><h3>People and roles</h3>'+table(['Role','People'],rows(data.roles),'People and roles')+'</section>'+
    '<section class="detail-section"><h3>Wagons and animals</h3>'+table(['Asset','Count'],rows(Object.assign({},data.wagons,data.animals)),'Wagons and animals')+'</section>'+
    '<section class="detail-section"><h3>Carried inventory</h3>'+table(['Stock','Quantity'],rows(data.inventory),'Carried inventory')+'</section>'+
    '<section class="detail-section"><h3>Services offered</h3><ul>'+data.services.map(function(v){return '<li>'+esc(v)+'</li>';}).join('')+'</ul><h3>Specialties</h3><ul>'+data.specialties.map(function(v){return '<li>'+esc(v)+'</li>';}).join('')+'</ul></section>'+
    '<section class="detail-section wide"><h3>Dated itinerary</h3>'+table(['From','Through','State','Location','Camp or route'],itinerary,'Dated itinerary')+'</section></div>';
}
var reportState={profile:null,report:null,generation:0,busy:false};
function money(value){return value==null?'Not available':number(value,3)+' gp';}
function reportControls(){
  document.getElementById('generate-report').disabled=!reportState.profile||reportState.busy;
  document.getElementById('download-report').disabled=!reportState.report||reportState.busy;
  document.getElementById('economic-report').setAttribute('aria-busy',String(reportState.busy));
}
function clearReport(){
  reportState.report=null;
  var panel=document.getElementById('economic-report');panel.hidden=true;panel.innerHTML='';
}
function invalidateSelection(){
  reportState.generation++;reportState.profile=null;reportState.busy=false;clearReport();reportControls();
  setStatus('Load the selected company to generate its economic report.');
}
function rangeText(range,unit){
  if(range.low==null||range.high==null)return 'Not available';
  return number(range.low,2)+(range.low===range.high?'':' - '+number(range.high,2))+' '+unit;
}
function renderEconomicReport(report){
  var economy=report.economy, accounts=economy.accounts, limit=economy.limiting_supply;
  var supplies=economy.supplies.map(function(row){return '<tr><td>'+esc(row.name)+'</td><td>'+
    (row.stock==null?'Not recorded':number(row.stock)+' '+esc(row.unit))+'</td><td>'+
    rangeText(row.daily_need,esc(row.unit)+'/day')+'</td><td>'+rangeText(row.days_of_cover,'days')+
    '</td><td>'+rangeText(row.additional_for_tenday,esc(row.unit))+'</td></tr>';}).join('');
  var household=economy.household_requirements.map(function(row){return '<tr><td>'+esc(row.commodity)+
    '</td><td>'+number(row.quantity_per_day,4)+' '+esc(row.unit||'catalogue units')+'</td><td>'+
    money(row.unit_price_gp)+'</td><td>'+money(row.cost_gp_per_day)+'</td><td>'+esc(row.availability)+'</td></tr>';}).join('');
  var inventory=economy.inventory.map(function(row){return '<tr><td>'+esc(row.name)+'</td><td>'+
    number(row.quantity)+' '+esc(row.unit)+'</td><td>'+money(row.unit_price_gp)+'</td><td>'+
    money(row.replacement_value_gp)+'</td><td>'+esc(row.valuation_note)+'</td></tr>';}).join('');
  var panel=document.getElementById('economic-report');
  panel.innerHTML='<h2>Economic report</h2><p>'+esc(report.location.name)+' &middot; '+esc(report.date)+
    '</p><p>'+esc(economy.valuation.description)+' Read-only estimates, not recorded transactions.</p>'+
    '<div class="facts">'+fact('Household benchmark / day',money(accounts.priced_household_cost_gp_per_day))+
    fact('Household benchmark / tenday',money(accounts.priced_household_cost_gp_per_tenday))+
    fact('Priced stock subtotal',money(accounts.priced_inventory_replacement_value_gp))+
    fact('Shortest known supply cover',limit?number(limit.days_of_cover,2)+' days':'Not available')+'</div>'+
    '<div class="detail-grid"><section class="detail-section wide"><h3>Supply cover and tenday resupply</h3>'+
    '<p>Starting stores, with no replenishment or losses. Water includes domestic and horse needs.'+
    (limit?' The first known constraint is '+esc(limit.name.toLowerCase())+'.':'')+
    ' Missing stores are unknown, not zero; zero demand has no finite cover estimate.</p>'+
    table(['Supply','Starting stock','Daily need','Days of cover','Extra needed for 10 days'],supplies,'Supply cover')+
    '</section><section class="detail-section wide"><h3>Household provisioning benchmark</h3><p>'+
    esc(label(economy.living_standard))+' living standard. '+accounts.priced_household_items+
    ' priced items; '+accounts.unpriced_household_items+' unpriced. This is not the full operating budget.'+
    ' It uses the shared household basket, not the caravan ration weights; do not add the two.</p>'+
    table(['Commodity','Daily quantity','Price / trade unit','Estimated cost / day','Availability'],household,'Household provisioning')+
    '</section><section class="detail-section wide"><h3>Carried stock valuation</h3><p>'+
    accounts.priced_inventory_items+' priced lines; '+accounts.unpriced_inventory_items+
    ' unvalued. The subtotal is not the value of all cargo or company assets. Wagons and animals remain unvalued.</p>'+
    table(['Stock','Quantity','Reference price','Replacement estimate','Basis'],inventory,'Carried stock valuation')+
    '</section><section class="detail-section"><h3>Accounts and income</h3><p>'+
    'Revenue, profit, gross local product, imports and exports: <b>not modeled</b>. '+
    'The company has no transaction ledger or quantified service deliveries. These are unknown, not zero.</p>'+
    '</section><section class="detail-section"><h3>Service capabilities</h3><ul>'+
    economy.services.map(function(row){return '<li>'+esc(row.name)+' &mdash; '+esc(row.delivery)+'</li>';}).join('')+
    '</ul></section><section class="detail-section wide"><h3>Assumptions and exclusions</h3><ul>'+
    economy.assumptions.map(function(note){return '<li>'+esc(note)+'</li>';}).join('')+'</ul></section></div>';
  panel.hidden=false;
}
async function generateReport(){
  if(!reportState.profile||reportState.busy){setStatus('Load a company and wait for the current request to finish.',true);return;}
  var id=reportState.profile.id, request=++reportState.generation;
  clearReport();reportState.busy=true;reportControls();setStatus('Generating economic report...');
  try{
    var report=await get('/api/mobile-economy?id='+encodeURIComponent(id));
    if(request!==reportState.generation)return;
    if(report.location.id!==id)throw new Error('The report does not match the selected company. Please reload.');
    render(report.location);showWorldDate(report);reportState.profile=report.location;
    renderEconomicReport(report);reportState.report=report;
    setStatus('Economic report ready for '+report.date+'. Download JSON to save the complete report.');
  }catch(error){if(request===reportState.generation){clearReport();setStatus(error.message,true);}}
  finally{if(request===reportState.generation){reportState.busy=false;reportControls();}}
}
function downloadReport(){
  if(!reportState.report||reportState.busy){setStatus('Generate an economic report before downloading it.',true);return;}
  var report=reportState.report;
  var blob=new Blob([JSON.stringify(report,null,2)],{type:'application/json'});
  var url=URL.createObjectURL(blob), link=document.createElement('a');
  link.href=url;link.download='mobile-economy-'+report.location.id+'-'+report.date_iso+'.json';
  document.body.appendChild(link);link.click();link.remove();
  window.setTimeout(function(){URL.revokeObjectURL(url);},1000);
}
async function load(){
  var wanted=document.getElementById('mobile-location').value||query('id')||'silver_wheel';
  var request=++reportState.generation;
  reportState.profile=null;clearReport();reportState.busy=true;reportControls();
  document.getElementById('hero').innerHTML='';document.getElementById('content').innerHTML='';
  setStatus('Loading travelling company...');
  try{
    var profile=await get('/api/mobile-location?id='+encodeURIComponent(wanted));
    if(request!==reportState.generation)return;
    render(profile);reportState.profile=profile;setStatus('');
  }catch(error){if(request===reportState.generation)setStatus(error.message,true);}
  finally{if(request===reportState.generation){reportState.busy=false;reportControls();}}
}
async function start(){
  var boot=await get('/api/bootstrap');showWorldDate(boot);
  var list=boot.mobile_locations||[];document.getElementById('mobile-locations').innerHTML=list.map(function(v){return '<option value="'+esc(v.name)+'">'+esc(v.status)+'</option>';}).join('');
  document.getElementById('mobile-location').value=query('id')||'Silver Wheel Company';await load();
}
document.getElementById('controls').addEventListener('submit',function(event){event.preventDefault();load();});
document.getElementById('mobile-location').addEventListener('input',invalidateSelection);
document.getElementById('generate-report').addEventListener('click',generateReport);
document.getElementById('download-report').addEventListener('click',downloadReport);
start().catch(function(error){setStatus(error.message,true);});
"""


MOBILE_ASSETS: Dict[str, Tuple[str, str]] = {
    "mobile.html": (MOBILE_HTML, "text/html; charset=utf-8"),
    "mobile.css": (MOBILE_CSS, "text/css; charset=utf-8"),
    "mobile.js": (MOBILE_JS, "application/javascript; charset=utf-8"),
}
