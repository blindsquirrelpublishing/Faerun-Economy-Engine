"""Market board: customers post commodity requests, other parties bid on them."""


BOARD_HTML = """<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Faerun Market Board — Commodity Requests</title>
<link rel="stylesheet" href="app.css"><link rel="stylesheet" href="detail.css"><link rel="stylesheet" href="trade.css">
<style>.board-row{cursor:pointer}.board-row:hover,.board-row:focus-visible{background:var(--cp-surface-soft)}.topbar .brand h1{font-size:50px;line-height:1.05;overflow-wrap:anywhere}.topbar .date-tile,.topbar [data-world-date]{display:grid;gap:2px;min-width:210px;min-height:72px;padding:9px 16px;text-align:center;line-height:1.15;white-space:nowrap}.date-line{display:block}.date-line-day{font-size:16px;font-weight:700}.date-line-season{font-size:13px;text-transform:capitalize}.date-line-moon{font-size:12px;opacity:.78}</style>
</head><body>
<header class="topbar"><div class="brand"><div><h1>Market board — commodity requests</h1><p class="tagline">Post a commodity request; other parties bid on it. Accepting a bid closes the request.</p></div></div>
<div class="worldbar"><div class="date-controls"><span class="pill" id="board-date">Loading world date...</span></div><nav class="nav-links" aria-label="Main navigation"><a class="navlink" href="index.html">Markets</a><a class="navlink" href="location.html">Locations</a><a class="navlink" href="business.html">Businesses</a><a class="navlink" href="product.html">Products</a><a class="navlink" href="route.html">Routes</a><a class="navlink" href="map.html">Map</a><a class="navlink" href="planner.html">Route planner</a><a class="navlink" href="mobile.html">Travelling companies</a><a class="navlink" href="trade.html">Merchant guild &amp; POs</a><a class="navlink" href="events.html">Events</a><span class="navlink navlink-current" aria-current="page">Request board</span></nav></div></header>
<main class="detail-shell trade-shell">
<h1 class="detail-title">Commodity request board</h1>
<p class="detail-subtitle">A public bulletin board for wanted commodities. Fulfilment, payment and delivery happen outside this board once a bid is accepted.</p>
<div id="status" class="status" role="status" aria-live="polite">Loading market board options...</div>

<section aria-labelledby="post-heading">
<h2 id="post-heading">1. Post a commodity request</h2>
<form id="request-form" aria-label="Post commodity request">
<fieldset id="request-inputs" disabled><legend>Request details</legend>
<div class="trade-fields">
<label>Your name / party<input id="requester_name" name="requester_name" autocomplete="organization" required></label>
<label>Commodity<select id="commodity" name="commodity" required></select></label>
<label>Quantity (units)<input id="quantity" name="quantity" type="number" min="1" step="1" required></label>
<label>Quality<select id="quality" name="quality" required></select></label>
<label>Delivery settlement<select id="settlement_id" name="settlement_id" required></select></label>
<label>Needed by<input id="needed_by" name="needed_by" type="text" placeholder="1492-01-01" pattern="[0-9]{4}-[0-9]{2}-[0-9]{2}" required aria-describedby="board-harptos-help"></label>
<label>Maximum price (gp / unit, optional)<input id="max_price_gp" name="max_price_gp" type="number" min="0" step="any"></label>
<label class="trade-wide">Notes<textarea id="notes" name="notes" rows="2"></textarea></label>
</div>
<p class="trade-help" id="board-harptos-help">Use Harptos YYYY-MM-DD, not a Gregorian calendar date.</p>
<button id="post-button" class="primary" type="submit">Post request</button>
</fieldset></form>
</section>

<section aria-labelledby="requests-heading">
<div class="trade-heading"><h2 id="requests-heading">2. Open requests</h2>
<label>Filter<select id="status-filter"><option value="open">Open</option><option value="accepted">Accepted</option><option value="cancelled">Cancelled</option><option value="">All</option></select></label>
<button id="refresh-requests" type="button">Refresh requests &amp; world date</button></div>
<div id="request-list"><p class="empty">No requests loaded.</p></div>
<div class="trade-pager"><button id="previous-requests" type="button" disabled>Previous</button><span id="request-page" role="status" aria-live="polite"></span><button id="next-requests" type="button" disabled>Next</button></div>
</section>

<section id="request-detail-section" aria-labelledby="request-heading" hidden><h2 id="request-heading">Request details</h2><div id="request-detail"></div>

<form id="bid-form" aria-label="Place a bid"><fieldset id="bid-inputs" disabled><legend>Place a bid</legend>
<div class="trade-fields">
<label>Your name / party<input id="bidder_name" name="bidder_name" autocomplete="organization" required></label>
<label>Price (gp / unit)<input id="bid_price" name="price_gp" type="number" min="0" step="any" required></label>
<label>Quantity you can supply<input id="bid_quantity" name="quantity" type="number" min="1" step="1" required></label>
<label>Delivery by<input id="bid_delivery_by" name="delivery_by" type="text" placeholder="1492-01-01" pattern="[0-9]{4}-[0-9]{2}-[0-9]{2}" required></label>
<label class="trade-wide">Notes<textarea id="bid_notes" name="notes" rows="2"></textarea></label>
</div>
<button id="bid-button" class="primary" type="submit">Submit bid</button>
</fieldset></form>

<fieldset id="request-actions" disabled><legend>Request actions</legend>
<label class="trade-check"><input id="cancel_confirmed" type="checkbox">I confirm cancellation of this request.</label>
<button id="cancel-request-button" type="button">Cancel this request</button>
</fieldset>
</section>
<details class="trade-assumptions"><summary>Market board assumptions</summary><div id="board-assumptions"></div></details>
</main><script src="board.js"></script></body></html>"""


BOARD_JS = r"""
'use strict';
const el = id => document.getElementById(id);
const state = {enabled:false, options:null, requests:[], total:0, offset:0, limit:50,
  status:'open', request:null};
function esc(value) {
  return String(value == null ? '' : value).replace(/&/g,'&amp;').replace(/</g,'&lt;')
    .replace(/>/g,'&gt;').replace(/"/g,'&quot;').replace(/'/g,'&#39;');
}
function text(value) { return value == null || value === '' ? 'Not provided' : String(value); }
function money(value) {
  return typeof value === 'number' && Number.isFinite(value)
    ? value.toLocaleString(undefined,{minimumFractionDigits:2,maximumFractionDigits:6})+' gp' : 'Not set';
}
function status(message, error=false) { el('status').textContent=message; el('status').className='status'+(error?' error':''); }
function list(items) { return '<ul>'+(items||[]).map(item=>'<li>'+esc(item)+'</li>').join('')+'</ul>'; }
async function api(path, body) {
  const options = {headers:{'Accept':'application/json'},cache:'no-store'};
  if (body !== undefined) { options.method='POST'; options.headers['Content-Type']='application/json'; options.body=JSON.stringify(body); }
  const response = await fetch(path, options);
  let data;
  try { data = await response.json(); }
  catch (_) { throw new Error('The server returned an unreadable response. Refresh before retrying; a submitted change may have been recorded.'); }
  if (!response.ok) throw new Error(data && typeof data.error === 'string' ? data.error : 'Market board request failed ('+response.status+').');
  return data;
}
function required(id, name) {
  const value = el(id).value.trim();
  if (!value) throw new Error(name+' is required.');
  return value;
}
function numeric(id, name, minimum=0, maximum=Infinity, integer=false) {
  const value = Number(required(id, name));
  if (!Number.isFinite(value) || value<minimum || value>maximum || (integer && !Number.isSafeInteger(value)))
    throw new Error(name+' must be '+(integer?'a whole number':'a number')+' from '+minimum+(maximum===Infinity?' or greater':' to '+maximum)+'.');
  return value;
}
function choice(id, name, values) {
  const value = required(id, name);
  if (!values.includes(value)) throw new Error('Choose a valid '+name.toLowerCase()+'.');
  return value;
}
function harptos(id, name) {
  const value = el(id).value.trim();
  if (!/^[0-9]{4}-[0-9]{2}-[0-9]{2}$/.test(value)) throw new Error(name+' must use Harptos YYYY-MM-DD.');
  return value;
}
async function loadOptions() {
  const options = await api('/api/board/options');
  state.enabled = options.enabled;
  state.options = options;
  el('board-date').innerHTML = '<span class="date-line date-line-day">' + options.date.label + '</span><span class="date-line date-line-season">' + (options.date.season || '') + '</span><span class="date-line date-line-moon">' + (options.date.moon_phase || options.date.iso || '') + '</span>';
  el('board-assumptions').innerHTML = list(options.assumptions);
  el('commodity').innerHTML = options.commodities.map(c=>'<option value="'+esc(c.id)+'">'+esc(c.name)+'</option>').join('');
  el('quality').innerHTML = options.qualities.map(q=>'<option value="'+esc(q)+'">'+esc(q)+'</option>').join('');
  el('settlement_id').innerHTML = options.settlements.map(s=>'<option value="'+esc(s.id)+'">'+esc(s.name)+'</option>').join('');
  el('request-inputs').disabled = !options.enabled;
  if (!options.enabled) status('Market board is not enabled for this world.', true);
  else status('Ready.');
}
function settlementName(id) {
  const match = (state.options && state.options.settlements || []).find(s=>s.id===id);
  return match ? match.name : id;
}
function commodityName(id) {
  const match = (state.options && state.options.commodities || []).find(c=>c.id===id);
  return match ? match.name : id;
}
function requestSummary(request) {
  const closed = request.status !== 'open';
  return '<tr data-id="'+esc(request.id)+'" class="board-row" tabindex="0" role="button">'
    +'<td>'+esc(commodityName(request.commodity))+'</td>'
    +'<td>'+esc(request.quantity)+'</td>'
    +'<td>'+esc(request.quality)+'</td>'
    +'<td>'+esc(settlementName(request.settlement_id))+'</td>'
    +'<td>'+esc(request.needed_by)+(request.is_expired?' (expired)':'')+'</td>'
    +'<td>'+esc(request.max_price_gp!=null?money(request.max_price_gp):'Not set')+'</td>'
    +'<td>'+esc(request.status)+(closed?'':' · '+request.bids.length+' bid(s)')+'</td>'
    +'<td>'+esc(request.requester_name)+'</td></tr>';
}
async function loadRequests() {
  const data = await api('/api/board/requests?status='+encodeURIComponent(state.status)
    +'&offset='+state.offset+'&limit='+state.limit);
  state.requests = data.requests;
  state.total = data.total;
  el('request-list').innerHTML = state.requests.length
    ? '<div class="table-scroll" tabindex="0" role="region" aria-label="Open requests"><table class="detail-table">'
      +'<thead><tr><th>Commodity</th><th>Qty</th><th>Quality</th><th>Settlement</th><th>Needed by</th><th>Max price</th><th>Status</th><th>Requester</th></tr></thead>'
      +'<tbody>'+state.requests.map(requestSummary).join('')+'</tbody></table></div>'
    : '<p class="empty">No requests match this filter.</p>';
  for (const row of el('request-list').querySelectorAll('.board-row')) {
    row.addEventListener('click', () => openRequest(row.dataset.id));
    row.addEventListener('keydown', event => { if (event.key==='Enter' || event.key===' ') { event.preventDefault(); openRequest(row.dataset.id); } });
  }
  el('previous-requests').disabled = state.offset<=0;
  el('next-requests').disabled = state.offset+state.requests.length>=state.total;
  el('request-page').textContent = state.total
    ? 'Showing '+(state.offset+1)+'-'+(state.offset+state.requests.length)+' of '+state.total : 'No requests';
}
function bidRow(request, bidItem) {
  const pending = bidItem.status==='pending' && request.status==='open';
  return '<tr>'
    +'<td>'+esc(bidItem.bidder_name)+'</td>'
    +'<td>'+esc(money(bidItem.price_gp))+'</td>'
    +'<td>'+esc(bidItem.quantity)+'</td>'
    +'<td>'+esc(bidItem.delivery_by)+'</td>'
    +'<td>'+esc(bidItem.notes||'')+'</td>'
    +'<td>'+esc(bidItem.status)+'</td>'
    +'<td>'+(pending?('<button type="button" class="accept-bid" data-bid="'+esc(bidItem.id)+'">Accept</button> '
      +'<button type="button" class="withdraw-bid" data-bid="'+esc(bidItem.id)+'">Withdraw</button>'):'')+'</td></tr>';
}
function renderRequestDetail() {
  const request = state.request;
  const closed = request.status !== 'open';
  el('request-detail').innerHTML =
    '<dl class="trade-metrics">'
    +'<div><dt>Commodity</dt><dd>'+esc(commodityName(request.commodity))+'</dd></div>'
    +'<div><dt>Quantity</dt><dd>'+esc(request.quantity)+' ('+esc(request.quality)+')</dd></div>'
    +'<div><dt>Settlement</dt><dd>'+esc(settlementName(request.settlement_id))+'</dd></div>'
    +'<div><dt>Needed by</dt><dd>'+esc(request.needed_by)+(request.is_expired?' (expired)':'')+'</dd></div>'
    +'<div><dt>Max price</dt><dd>'+esc(request.max_price_gp!=null?money(request.max_price_gp):'Not set')+'</dd></div>'
    +'<div><dt>Status</dt><dd>'+esc(request.status)+'</dd></div>'
    +'<div><dt>Requester</dt><dd>'+esc(request.requester_name)+'</dd></div>'
    +'<div><dt>Notes</dt><dd>'+esc(text(request.notes))+'</dd></div>'
    +'</dl>'
    +'<h3>Bids</h3>'
    +(request.bids.length
      ? '<div class="table-scroll" tabindex="0" role="region" aria-label="Bids"><table class="detail-table">'
        +'<thead><tr><th>Bidder</th><th>Price</th><th>Qty</th><th>Delivery by</th><th>Notes</th><th>Status</th><th>Actions</th></tr></thead>'
        +'<tbody>'+request.bids.map(b=>bidRow(request, b)).join('')+'</tbody></table></div>'
      : '<p class="empty">No bids yet.</p>');
  for (const button of el('request-detail').querySelectorAll('.accept-bid'))
    button.addEventListener('click', () => acceptBid(button.dataset.bid));
  for (const button of el('request-detail').querySelectorAll('.withdraw-bid'))
    button.addEventListener('click', () => withdrawBid(button.dataset.bid));
  el('bid-inputs').disabled = closed;
  el('request-actions').disabled = closed;
  el('cancel-request-button').disabled = closed;
}
async function openRequest(id) {
  try {
    const data = await api('/api/board/request?id='+encodeURIComponent(id));
    state.request = data.request;
    el('request-detail-section').hidden = false;
    renderRequestDetail();
    status('Loaded request '+id+'.');
  } catch (error) { status(error.message, true); }
}
async function refreshOpenRequest() {
  if (!state.request) return;
  try {
    const data = await api('/api/board/request?id='+encodeURIComponent(state.request.id));
    state.request = data.request;
    renderRequestDetail();
  } catch (error) { status(error.message, true); }
}
el('request-form').addEventListener('submit', async event => {
  event.preventDefault();
  try {
    const body = {
      requester_name: required('requester_name','Your name / party'),
      commodity: choice('commodity','Commodity', state.options.commodities.map(c=>c.id)),
      quantity: numeric('quantity','Quantity',1,Infinity,true),
      quality: choice('quality','Quality', state.options.qualities),
      settlement_id: choice('settlement_id','Delivery settlement', state.options.settlements.map(s=>s.id)),
      needed_by: harptos('needed_by','Needed by'),
      notes: el('notes').value.trim(),
    };
    const maxPrice = el('max_price_gp').value.trim();
    if (maxPrice) body.max_price_gp = numeric('max_price_gp','Maximum price',0);
    status('Posting request...');
    await api('/api/board/request', body);
    event.target.reset();
    status('Request posted.');
    state.offset = 0;
    await loadRequests();
  } catch (error) { status(error.message, true); }
});
el('bid-form').addEventListener('submit', async event => {
  event.preventDefault();
  if (!state.request) return;
  try {
    const body = {
      request_id: state.request.id,
      bidder_name: required('bidder_name','Your name / party'),
      price_gp: numeric('bid_price','Price',0.01),
      quantity: numeric('bid_quantity','Quantity',1,Infinity,true),
      delivery_by: harptos('bid_delivery_by','Delivery by'),
      notes: el('bid_notes').value.trim(),
    };
    status('Submitting bid...');
    await api('/api/board/bid', body);
    event.target.reset();
    status('Bid submitted.');
    await refreshOpenRequest();
    await loadRequests();
  } catch (error) { status(error.message, true); }
});
async function acceptBid(bidId) {
  try {
    status('Accepting bid...');
    await api('/api/board/bid/accept', {request_id: state.request.id, bid_id: bidId, version: state.request.version});
    status('Bid accepted; request closed.');
    await refreshOpenRequest();
    await loadRequests();
  } catch (error) { status(error.message, true); }
}
async function withdrawBid(bidId) {
  try {
    status('Withdrawing bid...');
    await api('/api/board/bid/withdraw', {request_id: state.request.id, bid_id: bidId});
    status('Bid withdrawn.');
    await refreshOpenRequest();
    await loadRequests();
  } catch (error) { status(error.message, true); }
}
el('cancel-request-button').addEventListener('click', async () => {
  if (!state.request || !el('cancel_confirmed').checked) { status('Confirm cancellation first.', true); return; }
  try {
    status('Cancelling request...');
    await api('/api/board/request/cancel', {request_id: state.request.id, version: state.request.version});
    status('Request cancelled.');
    el('cancel_confirmed').checked = false;
    await refreshOpenRequest();
    await loadRequests();
  } catch (error) { status(error.message, true); }
});
el('status-filter').addEventListener('change', () => { state.status = el('status-filter').value; state.offset = 0; loadRequests().catch(e=>status(e.message,true)); });
el('refresh-requests').addEventListener('click', () => { loadOptions().then(loadRequests).catch(e=>status(e.message,true)); });
el('previous-requests').addEventListener('click', () => { state.offset = Math.max(0, state.offset-state.limit); loadRequests().catch(e=>status(e.message,true)); });
el('next-requests').addEventListener('click', () => { state.offset += state.limit; loadRequests().catch(e=>status(e.message,true)); });
(async function init() {
  try {
    await loadOptions();
    await loadRequests();
  } catch (error) { status(error.message, true); }
})();
"""


BOARD_ASSETS = {
    "board.html": (BOARD_HTML, "text/html; charset=utf-8"),
    "board.js": (BOARD_JS, "application/javascript; charset=utf-8"),
}
