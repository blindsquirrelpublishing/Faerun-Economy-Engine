"""Route planner and shipment cost calculator assets."""

from .detailassets import COMMON_JS


PLANNER_HTML = """<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<script>(()=>{const theme=new URLSearchParams(location.search).get('scoutTheme')||(matchMedia('(prefers-color-scheme: dark)').matches?'dark':'light');document.documentElement.dataset.theme=theme;})();</script>
<title>Faerun Route Planner</title><link rel="stylesheet" href="app.css"><link rel="stylesheet" href="planner.css"></head>
<body><header class="topbar"><div class="brand"><div><span class="planner-eyebrow">Faerun / Trade desk</span><h1>Route Planner</h1></div></div>
<nav class="worldbar" aria-label="Main"><span class="pill" data-world-date>&#8230;</span><a class="navlink" href="index.html">Markets</a><a class="navlink" href="map.html">World map</a><a class="navlink" href="route.html">Route detail</a></nav></header>
<main class="planner-shell"><form id="planner-form">
<section class="shipment-band" aria-label="Shipment"><div class="shipment-grid">
<label>Origin<input id="origin" name="origin" list="places" required autocomplete="off" value="Waterdeep"></label>
<button id="swap" type="button" title="Swap origin and destination" aria-label="Swap origin and destination">&#8644;</button>
<label>Destination<input id="destination" name="destination" list="places" required autocomplete="off" value="Well of Dragons"></label>
<label>Cargo<input id="cargo" name="cargo" maxlength="120" value="Coffee beans"></label>
<label>Weight (lb)<input id="pounds" name="pounds" type="number" min="0.01" max="1000000000" step="any" required value="100"></label>
<button id="calculate" class="primary" type="submit">Calculate routes</button></div><datalist id="places"></datalist>
<div class="route-settings"><label><input type="checkbox" id="include_events" name="include_events"> Active event risk</label>
<label><input type="checkbox" id="include_inferred" name="include_inferred"> Inferred connections</label>
<label><input type="checkbox" id="allow_special" name="allow_special"> Air and teleport</label></div></section>
<details class="allowances" open><summary>Purchase and cost allowances <span>gp</span></summary><div class="allowance-grid">
<label>Cargo purchase price (gp/lb)<input type="number" id="purchase_per_lb" name="purchase_per_lb" min="0" max="1000000000" step="any" placeholder="Not supplied"></label>
<label>Minimum per leg<input type="number" id="minimum" name="minimum" min="0" max="1000000000" step="any" required value="0"></label>
<label>Handling per connection<input type="number" id="handling" name="handling" min="0" max="1000000000" step="any" required value="0"></label>
<label>Additional cost per travel day<input type="number" id="daily" name="daily" min="0" max="1000000000" step="any" required value="0"></label>
<label>Other fixed charges<input type="number" id="fixed" name="fixed" min="0" max="1000000000" step="any" required value="0"></label>
<label>Contingency (%)<input type="number" id="contingency" name="contingency" min="0" max="100" step="any" required value="0"></label></div></details>
</form><div class="result-bar"><p id="status" role="status" aria-live="polite">Loading locations...</p><button id="download" type="button" disabled>Download estimate</button></div>
<p class="estimate-notice">Planning estimates, not carrier quotes. Shared-cargo line-haul basis; carrier availability, shipment minimums, tariffs, spoilage and waiting times are unverified. Zero allowances mean not budgeted.</p>
<section id="results" aria-label="Route alternatives"></section><div id="selected-route" class="selected-layout"></div>
</main><script src="date.js"></script><script src="planner.js"></script></body></html>"""


PLANNER_CSS = """
body {height:auto;min-height:100dvh;overflow:auto;background:var(--cp-surface);color:var(--cp-text);}
body > .topbar {height:auto;min-height:94px;display:flex;flex-wrap:wrap;justify-content:space-between;gap:20px;padding:20px clamp(16px,3%,64px);background:var(--cp-surface-soft);border-top:3px solid var(--cp-accent);border-bottom:1px solid var(--cp-border);}
.topbar .brand {min-width:0;}
.topbar h1 {font-size:25px;line-height:1.25;font-weight:600;letter-spacing:0;margin:4px 0 0;}
.planner-eyebrow {font-size:11px;text-transform:uppercase;color:var(--cp-text-muted);}
.topbar .worldbar {display:flex;flex-wrap:wrap;gap:20px;min-width:0;}
.topbar .navlink {font-size:13px;color:var(--cp-text-muted);text-decoration:none;padding:8px 0;border-bottom:2px solid transparent;}
.topbar .navlink:hover {color:var(--cp-accent);border-color:var(--cp-accent);}
main.planner-shell {display:block;flex:none;width:100%;max-width:none;padding:0 clamp(16px,3%,64px) 48px;margin:0;min-height:0;background:transparent;box-sizing:border-box;}
.planner-shell * {box-sizing:border-box;letter-spacing:0;}
.shipment-band {padding:28px 0 22px;border-bottom:1px solid var(--cp-border);}
.shipment-grid {display:grid;grid-template-columns:minmax(0,1.3fr) 44px minmax(0,1.3fr) minmax(0,1fr) minmax(110px,.55fr) auto;align-items:end;gap:16px;}
.planner-shell label {display:grid;gap:9px;font-size:12px;font-weight:500;color:var(--cp-text-muted);min-width:0;}
.planner-shell input:not([type=checkbox]):not([type=radio]) {width:100%;min-width:0;height:44px;border:1px solid var(--cp-border);border-radius:6px;background:var(--cp-surface-soft);color:var(--cp-text);padding:10px 12px;font:inherit;font-size:14px;font-variant-numeric:tabular-nums;}
.planner-shell input:hover {border-color:var(--cp-border-strong);}
.planner-shell :is(input,button,summary,a,.planner-scroll):focus-visible {outline:2px solid var(--cp-accent);outline-offset:3px;}
.planner-shell input:focus {background:var(--cp-surface);}
.planner-shell button {min-height:44px;border-radius:6px;white-space:normal;padding:10px 16px;font-weight:600;}
.planner-shell button.primary {background:var(--cp-accent);color:var(--cp-accent-fg);border:1px solid var(--cp-accent);}
.planner-shell button.primary:hover {background:var(--cp-accent-hover);}
.planner-shell button:disabled {opacity:.5;cursor:default;}
#swap {width:44px;font-size:22px;padding:0;background:transparent;border:1px solid var(--cp-border);color:var(--cp-link);}
.route-settings {display:flex;flex-wrap:wrap;gap:24px;margin-top:20px;}
.route-settings label {display:flex;align-items:center;gap:8px;font-size:13px;}
.planner-shell input[type=checkbox],.planner-shell input[type=radio] {accent-color:var(--cp-accent);width:16px;height:16px;flex-shrink:0;}
.allowances {padding:20px 0 24px;border-bottom:1px solid var(--cp-border);}
.allowances summary {cursor:pointer;font-size:14px;font-weight:600;}
.allowances summary::marker {color:var(--cp-accent);}
.allowances summary span {font-size:12px;color:var(--cp-text-muted);margin-left:8px;}
.allowance-grid {display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,175px),1fr));gap:16px 24px;margin-top:20px;align-items:end;}
.result-bar {display:flex;flex-wrap:wrap;justify-content:space-between;gap:12px;align-items:center;margin-top:22px;min-height:44px;}
#status {margin:0;font-size:13px;color:var(--cp-text-muted);overflow-wrap:anywhere;flex:1 1 280px;}
#status.error {color:var(--cp-danger);}
#download {background:transparent;border:1px solid var(--cp-border);color:var(--cp-text);}
.estimate-notice {font-size:12px;line-height:1.6;color:var(--cp-text-muted);border-left:3px solid var(--cp-warning);padding:4px 0 4px 14px;margin:16px 0 30px;max-width:120ch;}
.planner-shell h2 {font-size:18px;font-weight:600;margin:0 0 18px;}
.planner-shell h3 {font-size:15px;margin:20px 0 12px;}
.planner-scroll {width:100%;overflow-x:auto;scrollbar-color:var(--cp-border-strong) var(--cp-surface-soft);}
.planner-table {border-collapse:collapse;width:100%;font-size:13px;}
.planner-table th {color:var(--cp-text-muted);font-size:11px;font-weight:600;text-transform:uppercase;background:var(--cp-surface-soft);}
.planner-table td,.planner-table th {text-align:left;padding:14px 12px;border-bottom:1px solid var(--cp-border);vertical-align:top;line-height:1.5;}
.planner-table th.num,.planner-table td.num {text-align:right;white-space:nowrap;font-variant-numeric:tabular-nums;}
.planner-table td small {display:block;font-size:12px;margin-top:5px;color:var(--cp-text-muted);line-height:1.5;}
.option-table {min-width:840px;}
.option-table td:nth-child(3) {min-width:160px;max-width:420px;}
.option-table tr[data-option] {cursor:pointer;}
.option-table tr[data-option]:hover {background:var(--cp-surface-soft);}
.option-table tr.chosen {background:var(--cp-accent-soft);}
.option-table tr.chosen td:first-child {box-shadow:inset 3px 0 var(--cp-accent);}
.selected-layout {display:grid;grid-template-columns:minmax(0,1fr) minmax(280px,24%);gap:32px;margin-top:28px;align-items:start;}
.selected-layout section,.selected-layout aside {min-width:0;border-top:1px solid var(--cp-border);padding-top:22px;}
.selected-layout aside {border-top:3px solid var(--cp-accent);}
.route-metrics {grid-column:1 / -1;display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:24px;margin:0;padding:24px 0;border-block:1px solid var(--cp-border);background:linear-gradient(90deg,var(--cp-surface-soft),var(--cp-surface));}
.route-metrics div {min-width:0;padding:0 20px;border-left:2px solid var(--cp-border);}
.route-metrics div:last-child {border-color:var(--cp-accent);}
.route-metrics dt {font-size:12px;color:var(--cp-text-muted);margin-bottom:10px;}
.route-metrics dd {font-size:22px;font-weight:600;line-height:1.3;margin:0;overflow-wrap:anywhere;font-variant-numeric:tabular-nums;}
.leg-table {min-width:680px;}
.leg-table > tbody > .carrier-detail-row > td {padding:0;border-bottom:1px solid var(--cp-border-strong);background:var(--cp-surface);}
.leg-carriers {padding:0 14px 14px;}
.leg-carriers > summary {padding:12px 0;cursor:pointer;font-size:13px;font-weight:600;color:var(--cp-link);}
.carrier-stages {display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,360px),1fr));gap:24px;}
.carrier-stage {min-width:0;padding:12px 0;border-top:1px solid var(--cp-border);}
.carrier-stage label {font-size:13px;}
.planner-shell .carrier-stage select {width:100%;min-width:0;height:44px;margin:6px 0 12px;background:var(--cp-surface-soft);color:var(--cp-text);border:1px solid var(--cp-border);border-radius:6px;font:inherit;}
.carrier-table {min-width:580px;}
.carrier-table tr.carrier-chosen {background:var(--cp-accent-soft);}
.carrier-table td:first-child {min-width:140px;}
.carrier-note {max-width:100ch;white-space:normal;}
.load-table {min-width:680px;}
.load-table td[rowspan] {background:var(--cp-surface-soft);}
.load-table tr:hover {background:var(--cp-accent-soft);}
.load-table td:last-child strong {color:var(--cp-link);font-size:15px;}
.selected-layout .shipment-loads {grid-column:1 / -1;}
.planner-shell a {color:var(--cp-link);}
.costs {margin:0;}
.costs div {display:flex;flex-wrap:wrap;justify-content:space-between;gap:6px 16px;padding:11px 0;border-bottom:1px solid var(--cp-border);font-size:13px;}
.costs dt {overflow-wrap:anywhere;color:var(--cp-text-muted);}
.costs dd {margin:0;overflow-wrap:anywhere;max-width:100%;font-variant-numeric:tabular-nums;}
.costs .cost-total {font-size:20px;font-weight:600;border-top:2px solid var(--cp-accent);border-bottom:0;padding:18px 0 12px;}
.cost-total dt {font-size:13px;flex-basis:100%;color:var(--cp-text);}
.planner-warning,.unavailable {font-size:12px;line-height:1.6;color:var(--cp-text-muted);}
.shipment-loads > .planner-warning {max-width:120ch;margin-bottom:20px;}
.empty-state {padding:30px 0;border-block:1px solid var(--cp-border);color:var(--cp-text-muted);}
@media(max-width:1200px){.shipment-grid{grid-template-columns:minmax(0,1fr) 44px minmax(0,1fr);}.shipment-grid label:nth-of-type(3){grid-column:1;}.shipment-grid label:nth-of-type(4){grid-column:2 / 4;}.shipment-grid #calculate{grid-column:1 / -1;}.selected-layout{grid-template-columns:minmax(0,1fr);}.selected-layout aside{display:block;}.costs{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:0 32px;}.costs .cost-total{grid-column:1 / -1;}}
@media(max-width:600px){.topbar .worldbar{gap:16px;}.shipment-grid{grid-template-columns:minmax(0,1fr) 44px;gap:16px 12px;}.shipment-grid label,.shipment-grid label:nth-of-type(4){grid-column:1 / -1;}.shipment-grid label:first-child{grid-column:1;}.shipment-grid #swap{grid-column:2;grid-row:1;}.allowance-grid{grid-template-columns:repeat(2,minmax(0,1fr));gap:18px 12px;}.allowance-grid label{align-content:space-between;}.planner-shell input:not([type=checkbox]):not([type=radio]){font-size:16px;}.route-metrics{grid-template-columns:repeat(2,minmax(0,1fr));gap:24px 12px;}.route-metrics div{padding:0 12px;}.route-metrics dd{font-size:19px;}.route-settings{gap:16px;}.costs{display:block;}.selected-layout{gap:24px;}.result-bar{align-items:flex-start;}}
@media(max-width:600px){.shipment-grid label:nth-of-type(3){grid-column:1 / -1;}}
@media(max-width:600px){.leg-carriers{width:calc(100vw - 64px);max-width:100%;padding-inline:10px;}.planner-shell .carrier-stage select{font-size:16px;}}
@media(prefers-reduced-motion:no-preference){.selected-layout{animation:planner-reveal .2s ease-out;}@keyframes planner-reveal{from{opacity:.6;transform:translateY(4px);}to{opacity:1;transform:none;}}}
"""


PLANNER_JS = COMMON_JS + """
const form = document.getElementById('planner-form');
const fields = ['origin','destination','cargo','pounds','purchase_per_lb','minimum','handling','daily','fixed','contingency'];
const flags = ['include_events','include_inferred','allow_special'];
let estimate = null, selected = 0, requestNumber = 0;
let carrierChoices = {};
function number(value) { return Number(value).toLocaleString(undefined,{maximumFractionDigits:2}); }
function price(value) { return value == null ? 'Pending' : Number(value).toLocaleString(undefined,{minimumFractionDigits:2,maximumFractionDigits:3})+' gp'; }
function inputs() {
  const params = {};
  fields.forEach(key => params[key] = document.getElementById(key).value);
  flags.forEach(key => params[key] = document.getElementById(key).checked ? '1' : '0');
  if(Object.keys(carrierChoices).length)params.carrier_choices=JSON.stringify(carrierChoices);
  return params;
}
function table(headers, rows, extra) {
  return '<div class="planner-scroll" tabindex="0" role="region" aria-label="'+esc(extra)+'"><table class="planner-table '+extra+'"><thead><tr>'+headers.map(text=>'<th>'+esc(text)+'</th>').join('')+'</tr></thead><tbody>'+rows+'</tbody></table></div>';
}
function carrierDetails(leg, index) {
  const stages = leg.transport_stages.map(stage=>{
    const selector = '<label>Leg '+(index+1)+' / '+esc(stage.mode)+' carrier<select data-leg="'+esc(leg.id)+'" data-mode="'+esc(stage.mode)+'"><option value="">Shared freight (modeled)</option>'+stage.carriers.map(carrier=>'<option value="'+esc(carrier.name)+'"'+(carrier.selected?' selected':'')+'>'+esc(carrier.name)+' / '+number(carrier.shipments_required)+' loads</option>').join('')+'</select></label>';
    const rows = stage.carriers.map(carrier=>'<tr'+(carrier.selected?' class="carrier-chosen"':'')+'><td>'+esc(carrier.name)+'</td><td class="num">'+number(carrier.capacity_lb)+'</td><td class="num">'+number(carrier.shipments_required)+'</td><td class="num">'+price(carrier.full_load_cost_gp)+'</td><td class="num">'+price(carrier.shipment_cost_gp)+'</td><td class="num">'+number(carrier.travel_days)+'</td></tr>').join('');
    return '<div class="carrier-stage">'+selector+'<p class="planner-warning">'+number(stage.distance_miles)+' mi / Shared freight: '+price(stage.shared_cost_gp)+' / '+number(stage.shared_travel_days)+' days</p>'+table(['Carrier','Capacity (lb)','Loads','Cost / load','Shipment cost','Days'],rows,'carrier-table')+'</div>';
  }).join('');
  return '<tr class="carrier-detail-row"><td colspan="7"><details class="leg-carriers" data-leg-details="'+esc(leg.id)+'" open><summary>Leg '+(index+1)+' carriers / capacity &amp; cost</summary><p class="planner-warning carrier-note">Full-load hire charges every required load, including unused capacity. Loads travel concurrently; availability and return trips are unverified.'+(leg.transport_stages.length>1?' Mixed-mode distances are split equally; transfer adjustments are included.':'')+' Costs include the current risk premium, before per-leg minimums and shipment allowances.</p><div class="carrier-stages">'+stages+'</div></details></td></tr>';
}
function renderSelection() {
  const option = estimate.options[selected];
  document.querySelectorAll('[data-option]').forEach(row=>{
    row.classList.toggle('chosen',Number(row.dataset.option)===selected);
    row.querySelector('input').checked=Number(row.dataset.option)===selected;
  });
  const legs = option.legs.map((leg,index)=>'<tr><td>'+ (index+1) +'</td><td><a href="location.html?settlement='+encodeURIComponent(leg.origin)+'">'+esc(leg.origin)+'</a><small>to '+esc(leg.destination)+'</small></td><td>'+esc(leg.mode)+'<small>'+esc(leg.connection)+(leg.inferred?' (inferred)':'')+'</small><small>'+esc(leg.transport_stages.map(stage=>stage.selected_carrier||'Shared '+stage.mode).join(' + '))+'</small></td><td class="num">'+number(leg.distance_miles)+'</td><td class="num">'+number(leg.travel_days)+'</td><td class="num">'+price(leg.line_haul_gp)+'</td><td class="num">'+price(leg.minimum_topup_gp)+'</td></tr>'+carrierDetails(leg,index)).join('');
  const costLabels = {line_haul_gp:'Modeled line-haul',minimum_topup_gp:'Per-leg minimum top-ups',handling_gp:'Connection handling',daily_gp:'Travel-day allowance',fixed_gp:'Other fixed charges',subtotal_gp:'Transport subtotal',contingency_gp:'Transport contingency',total_gp:'Transport total',purchase_value_gp:'Cargo purchase value',landed_total_gp:'Total landed cost',landed_gp_per_lb:'Landed cost / lb'};
  const costs = Object.entries(costLabels).map(([key,label])=>'<div'+(key==='landed_total_gp'?' class="cost-total"':'')+'><dt>'+label+'</dt><dd>'+price(option.costs[key])+'</dd></div>').join('');
  document.getElementById('selected-route').innerHTML='<section><h2>Itinerary</h2>'+table(['Leg','From / to','Transport / connection','Miles','Days','Line-haul','Minimum top-up'],legs,'leg-table')+'</section><aside><h2>Shipment estimate</h2><dl class="costs">'+costs+'</dl><p class="planner-warning">'+esc(estimate.pounds)+' lb '+esc(estimate.cargo)+'. No confirmed carrier booking.</p>'+(estimate.profile_inferred?'<p class="planner-warning">Endpoint economic/security profile is inferred. Destination access and security require review.</p>':'')+(option.uses_inferred?'<p class="planner-warning">This itinerary uses inferred connections.</p>':'')+'</aside>';
  const loads = option.legs.map((leg,index)=>leg.carrier_loads.map((carrier,carrierIndex)=>'<tr>'+(carrierIndex===0?'<td rowspan="'+leg.carrier_loads.length+'">'+(index+1)+'</td><td rowspan="'+leg.carrier_loads.length+'">'+esc(leg.origin)+'<small>to '+esc(leg.destination)+'</small></td>':'')+'<td>'+esc(carrier.mode)+'</td><td>'+esc(carrier.name)+'</td><td class="num">'+number(carrier.capacity_lb)+'</td><td class="num"><strong>'+number(carrier.shipments_required)+'</strong></td></tr>').join('')).join('');
  const metrics = [['Travel time',number(option.travel_days)+' days'],['Connections',number(option.connections)],['Transport total',price(option.costs.total_gp)],['Landed total',price(option.costs.landed_total_gp)]];
  document.getElementById('selected-route').insertAdjacentHTML('afterbegin','<dl class="route-metrics" aria-label="Selected route summary">'+metrics.map(([label,value])=>'<div><dt>'+esc(label)+'</dt><dd>'+esc(value)+'</dd></div>').join('')+'</dl>');
  document.querySelector('#selected-route aside').insertAdjacentHTML('beforeend','<p class="planner-warning">'+(estimate.assumptions.purchase_per_lb == null ? 'Purchase price not supplied. Landed cost pending.' : 'Landed cost includes cargo purchase value plus transport and entered allowances. Unbudgeted charges and losses are excluded.')+'</p>');
  document.getElementById('selected-route').insertAdjacentHTML('beforeend','<section class="shipment-loads"><h2>Shipments required by leg</h2><p class="planner-warning">'+number(estimate.pounds)+' lb per leg. Carrier rows are alternative capacity scenarios; counts are rounded up. Porter company counts are company-loads, not individual people. Only selected carriers affect the estimate. Mixed-mode components use equal distance shares; carriers are not guaranteed through services.</p>'+table(['Leg','From / to','Mode','Carrier','Capacity / load (lb)','Shipments (loads)'],loads,'load-table')+'</section>');
}
function render(preferredOptionId) {
  const options = estimate.options;
  document.getElementById('selected-route').innerHTML='';
  if (!options.length) {
    document.getElementById('results').innerHTML='<div class="empty-state">No eligible route connects these locations under the selected restrictions.</div>';
    return;
  }
  const rows = options.map((option,index)=>'<tr data-option="'+index+'"><td><input type="radio" name="itinerary" aria-label="Select option '+(index+1)+'" value="'+index+'"></td><td><strong>'+esc(option.labels.join(' / '))+'</strong><small>'+esc([...new Set(option.legs.map(leg=>leg.mode))].join(', '))+'</small></td><td>'+ (option.connections ? esc(option.path.slice(1,-1).join(' > ')) : 'Direct') +'<small>'+option.connections+' connections</small></td><td class="num">'+number(option.travel_days)+'</td><td class="num">'+number(option.distance_miles)+'</td><td class="num">'+price(option.costs.line_haul_gp)+'</td><td class="num">'+price(option.costs.total_gp)+'</td><td class="num"><strong>'+price(option.costs.landed_total_gp)+'</strong></td></tr>').join('');
  document.getElementById('results').innerHTML='<h2>Route alternatives</h2>'+table(['','Selection / modes','Via','Days','Miles','Line-haul','Transport total','Landed total'],rows,'option-table')+'<p class="unavailable">'+(estimate.unavailable.length?'Unavailable: '+esc(estimate.unavailable.join(', '))+'. ':'')+'Route labels reflect baseline shared-freight searches. Carrier choices update these itineraries, not the path search. Times exclude connection waits.</p>';
  selected=Math.max(0,options.findIndex(option=>option.id===preferredOptionId)); renderSelection();
}
async function calculate(event) {
  if(event)event.preventDefault();
  if(!form.reportValidity()) return;
  const request=++requestNumber, params=inputs();
  const preferredOptionId=estimate?.options[selected]?.id;
  estimate=null;
  document.getElementById('results').innerHTML='';
  document.getElementById('selected-route').innerHTML='';
  document.getElementById('download').disabled=true;
  document.getElementById('calculate').disabled=true;
  setStatus('Calculating routes...');
  try {
    const data=await get('/api/transport-plan',params);
    if(request!==requestNumber)return;
    estimate={...data,cargo:params.cargo};
    history.replaceState(null,'','planner.html?'+new URLSearchParams(params));
    render(preferredOptionId);
    setStatus(data.origin+' to '+data.destination+' | '+data.options.length+' alternatives | '+(data.include_events?'Event risk: '+data.date:'Baseline security risk'));
    document.getElementById('download').disabled=!data.options.length;
  } catch(error) { if(request===requestNumber)setStatus(error.message,true); }
  finally { if(request===requestNumber)document.getElementById('calculate').disabled=false; }
}
document.getElementById('results').addEventListener('click',event=>{
  const row=event.target.closest('[data-option]');
  if(row){selected=Number(row.dataset.option);renderSelection();}
});
document.getElementById('results').addEventListener('change',event=>{
  if(event.target.name==='itinerary'){selected=Number(event.target.value);renderSelection();}
});
document.getElementById('selected-route').addEventListener('change',async event=>{
  const control=event.target.closest('select[data-leg]');
  if(!control)return;
  const legId=control.dataset.leg, mode=control.dataset.mode;
  const closed=[...document.querySelectorAll('.leg-carriers:not([open])')].map(detail=>detail.dataset.legDetails);
  carrierChoices[legId]={...(carrierChoices[legId]||{}),[mode]:control.value};
  if(!control.value)delete carrierChoices[legId][mode];
  if(!Object.keys(carrierChoices[legId]).length)delete carrierChoices[legId];
  await calculate();
  document.querySelectorAll('.leg-carriers').forEach(detail=>{if(closed.includes(detail.dataset.legDetails))detail.open=false;});
  const replacement=[...document.querySelectorAll('select[data-leg]')].find(select=>select.dataset.leg===legId&&select.dataset.mode===mode);
  if(replacement){replacement.focus({preventScroll:true});replacement.scrollIntoView({block:'nearest'});}
});
form.addEventListener('submit',calculate);
form.addEventListener('input',event=>{
  if(['origin','destination','include_inferred','allow_special'].includes(event.target.id))carrierChoices={};
  requestNumber++;
  estimate=null;
  document.getElementById('results').innerHTML='';
  document.getElementById('selected-route').innerHTML='';
  document.getElementById('download').disabled=true;
  document.getElementById('calculate').disabled=false;
  setStatus('Shipment changed. Estimate pending.');
});
document.getElementById('swap').addEventListener('click',()=>{
  carrierChoices={};
  const origin=document.getElementById('origin'), destination=document.getElementById('destination');
  [origin.value,destination.value]=[destination.value,origin.value]; calculate();
});
document.getElementById('download').addEventListener('click',()=>{
  if(!estimate)return;
  const url=URL.createObjectURL(new Blob([JSON.stringify({...estimate,selected_option:selected},null,2)],{type:'application/json'}));
  const link=document.createElement('a');link.href=url;link.download='shipment-estimate.json';
  document.body.appendChild(link);link.click();link.remove();
  setTimeout(()=>URL.revokeObjectURL(url),1000);
});
async function startPlanner() {
  const params=new URLSearchParams(location.search);
  carrierChoices=JSON.parse(params.get('carrier_choices')||'{}');
  fields.forEach(key=>{if(params.has(key))document.getElementById(key).value=params.get(key);});
  flags.forEach(key=>{document.getElementById(key).checked=params.get(key)==='1';});
  const bootstrap=await get('/api/bootstrap');
  showWorldDate(bootstrap);
  document.getElementById('places').innerHTML=bootstrap.settlements.map(place=>'<option value="'+esc(place.name)+'">'+esc(place.region)+'</option>').join('');
  await calculate();
}
startPlanner().catch(error=>setStatus(error.message,true));
"""

PLANNER_ASSETS = {
    "planner.html": (PLANNER_HTML, "text/html; charset=utf-8"),
    "planner.css": (PLANNER_CSS, "text/css; charset=utf-8"),
    "planner.js": (PLANNER_JS, "application/javascript; charset=utf-8"),
}