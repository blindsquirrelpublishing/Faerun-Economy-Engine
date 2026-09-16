"""Standalone merchant guild quotes and manually recorded purchase orders."""


TRADE_HTML = """<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Faerun Merchant Guild Trade Desk</title>
<link rel="stylesheet" href="app.css"><link rel="stylesheet" href="detail.css"><link rel="stylesheet" href="trade.css">
</head><body>
<header class="topbar"><div class="brand"><div><h1>Merchant guild trade desk</h1><p class="tagline">Wholesale quotes, purchase orders and a manual cash ledger.</p></div></div>
<nav class="worldbar" aria-label="Main"><span class="pill" id="trade-date">Loading world date...</span><a class="navlink" href="index.html">Markets &amp; world date</a><a class="navlink" href="planner.html">Route planner</a><a class="navlink" href="map.html">World map</a></nav></header>
<main class="detail-shell trade-shell">
<h1 class="detail-title">Merchant guild (wholesale)</h1>
<p class="detail-subtitle">Compare supplier prices, reserve a dated supply allocation, then record your own payments and shipment milestones. No external purchase or payment is made.</p>
<div class="trade-notice" id="trade-basis"><strong>Forecast quota, not physical on-hand stock.</strong> Supply belongs to a dated window. Allocated exports take over an existing destination allocation; they are not added demand. Takeovers support standard grade only; choose uncommitted stock for other grades. Quotes expire after 24 hours and do not reserve anything until you explicitly confirm.</div>
<div id="status" class="status" role="status" aria-live="polite">Loading trade options...</div>
<form id="quote-form" aria-label="Build wholesale quote">
<fieldset id="quote-inputs" disabled><legend>1. Build a quote</legend>
<div class="trade-fields">
<label>Origin<select id="origin" name="origin" required></select></label>
<label>Destination<select id="destination" name="destination" required></select></label>
<label>Commodity<select id="commodity" name="commodity" required></select></label>
<label>Quantity (units)<input id="quantity" name="quantity" type="number" min="1" step="1" required></label>
<label>Quality<select id="quality" name="quality" required></select></label>
<label>Supply planning date<input id="supply_date" name="supply_date" type="text" placeholder="1492-01-01" pattern="[0-9]{4}-[0-9]{2}-[0-9]{2}" required aria-describedby="harptos-help"></label>
<label>Requested delivery date (optional)<input id="delivery_date" name="delivery_date" type="text" placeholder="Earliest feasible date" pattern="[0-9]{4}-[0-9]{2}-[0-9]{2}" aria-describedby="harptos-help"></label>
<label>Supply basis<select id="supply_mode" name="supply_mode" required><option value="allocated_export">Allocated export takeover</option><option value="uncommitted">Uncommitted forecast quota</option></select></label>
<label>Purchase channel<select id="purchase_channel" name="purchase_channel" required><option value="producer">Producer gate</option><option value="guild">Merchant guild (wholesale)</option></select></label>
<label>Supplier delivery terms<select id="delivery_terms" name="delivery_terms" required><option value="pickup">Pickup</option><option value="delivered">Supplier delivered</option></select></label>
<label>Transport mode<select id="transport_mode" name="transport_mode" required><option value="own_caravan">Own caravan — one horse wagon</option><option value="shared_freight">Shared freight — hired / mixed-mode route</option></select></label>
</div>
<p class="trade-help" id="harptos-help">Use Harptos YYYY-MM-DD, not a Gregorian calendar date. Pickup is at the end of the selected supply window, as shown in the quote. Use the world date controls on Markets to advance the simulation; this desk never advances time automatically.</p>
<p class="trade-help" id="transport-help">Own caravan uses one 4,000 lb horse wagon. Operating days cover travel, not loading or trading; budget those activities with fixed charges. Shared freight may use a hired mixed-mode route, with no own-caravan daily charge or empty return trip. Supplier-delivered quotes require shared freight.</p>
<fieldset><legend>Shipment allowances</legend><div class="trade-fields">
<label>Fixed charges (gp)<input id="fixed_gp" name="fixed_gp" type="number" min="0" step="any" required></label>
<label>Contingency (%)<input id="contingency_pct" name="contingency_pct" type="number" min="0" max="100" step="any" required></label>
</div></fieldset>
<fieldset id="own-budget"><legend>Own-caravan budget</legend><div class="trade-fields">
<label>Daily operating cost (gp)<input id="daily_gp" name="daily_gp" type="number" min="0" step="any" required></label>
<label class="trade-check"><input id="return_trip" name="return_trip" type="checkbox">Budget an empty return trip</label>
</div></fieldset>
<fieldset><legend>Customer and supplier terms</legend><div class="trade-fields">
<label>Customer pricing<select id="customer_price_mode" name="customer_price_mode" required><option value="retail">Retail</option><option value="wholesale">Merchant guild (wholesale)</option><option value="agreed">Agreed unit price</option></select></label>
<label id="agreed-field" hidden>Agreed customer price (gp / unit)<input id="customer_unit_price" name="customer_unit_price" type="number" min="0" step="any" disabled></label>
<label>Customer tax terms<select id="tax_terms" name="tax_terms" required><option value="included">Tax included</option><option value="extra">Tax added separately</option></select></label>
<label>Customer deposit (%)<input id="deposit_percent" name="deposit_percent" type="number" min="0" max="100" step="any" required></label>
<label>Customer payment terms<select id="payment_terms" name="payment_terms" required><option value="on_delivery">Balance on delivery</option><option value="before_dispatch">Full prepayment before dispatch</option></select></label>
<label class="trade-check"><input id="supplier_tax_exempt" name="supplier_tax_exempt" type="checkbox">Supplier tax exemption claimed</label>
<label id="exemption-field" hidden>Tax exemption reason<input id="tax_exemption_reason" name="tax_exemption_reason" type="text" disabled></label>
<label class="trade-wide">Delivery / acceptance terms<textarea id="acceptance_terms" name="acceptance_terms" rows="3" required></textarea></label>
</div></fieldset>
<button id="quote-button" class="primary" type="submit">Get dated quote</button>
</fieldset></form>
<section aria-labelledby="quote-heading"><h2 id="quote-heading">2. Review the quote</h2>
<p id="quote-state" class="trade-help" role="status" aria-live="polite">No quote yet.</p>
<div id="quote-summary"><p class="empty">Complete the fields above to compare costs and availability.</p></div>
<form id="reserve-form" aria-label="Confirm purchase order"><fieldset id="reservation-inputs" disabled><legend>Explicit reservation</legend>
<div class="trade-fields">
<label>Customer name<input id="customer_name" name="customer_name" autocomplete="organization" required></label>
<label>Purchase order reference<input id="po_reference" name="po_reference" required></label>
</div>
<label class="trade-check"><input id="terms_accepted" name="terms_accepted" type="checkbox" required>I have reviewed and accept the quoted supplier and customer terms, prices, taxes and delivery / acceptance terms.</label>
<label id="takeover-ack" class="trade-check" hidden><input id="allocation_authorized" name="allocation_authorized" type="checkbox">I am authorized to take over this existing destination export allocation, not create additional demand.</label>
<button id="reserve-button" class="primary" type="submit" disabled>Confirm and reserve purchase order</button>
</fieldset></form></section>
<section aria-labelledby="orders-heading"><div class="trade-heading"><h2 id="orders-heading">3. Persisted purchase orders</h2><button id="refresh-orders" type="button">Refresh orders &amp; world date</button></div>
<p class="trade-help">Orders and ledger entries persist across restarts. Quoted summaries are read-only. Recorded cash is not automatically profit; projected profit remains an estimate.</p>
<div id="order-list"><p class="empty">No orders loaded.</p></div>
<div class="trade-pager"><button id="previous-orders" type="button" disabled>Previous orders</button><span id="order-page" role="status" aria-live="polite"></span><button id="next-orders" type="button" disabled>Next orders</button></div>
</section>
<section id="order-detail-section" aria-labelledby="order-heading" hidden><h2 id="order-heading">Purchase order details</h2><div id="order-detail"></div>
<form id="payment-form" aria-label="Record manual cash movement"><fieldset id="payment-inputs" disabled><legend>Manually record cash</legend>
<p class="trade-notice">This is a manual cash ledger, not a payment processor. References are idempotent: reuse the same reference when retrying the same entry; use a new reference for a new movement. Refunds cannot exceed recorded payments.</p>
<div class="trade-fields">
<label>Movement<select id="payment_kind" name="kind" required><option value="customer_payment">Customer payment received</option><option value="customer_refund">Customer refund paid</option><option value="supplier_payment">Supplier payment paid</option><option value="supplier_refund">Supplier refund received</option><option value="expense">Other expense paid</option></select></label>
<label>Amount (gp)<input id="payment_amount" name="amount_gp" type="number" min="0" step="any" required></label>
<label>Unique movement reference<input id="payment_reference" name="reference" required></label>
</div><label class="trade-check"><input id="payment_confirmed" type="checkbox" required>I confirm this cash movement actually occurred and should be recorded manually.</label>
<button id="payment-button" type="submit">Record cash movement</button>
</fieldset></form>
<fieldset id="action-inputs" disabled><legend>Shipment milestones</legend>
<p class="trade-help">Dispatch needs the pickup window, sufficient supply, a paid supplier and the customer deposit or prepayment. Delivery needs the arrival date. If not yet due, use Markets world date controls and refresh here. Cancellation is only before dispatch and after refunding recorded funds; it releases quota. Dispatched or delivered quantities do not immediately return to stock.</p>
<div class="trade-actions"><button id="dispatch-button" type="button">Record dispatch</button><button id="deliver-button" type="button">Record accepted delivery</button><button id="cancel-button" type="button">Cancel reservation &amp; release quota</button></div>
<label class="trade-check"><input id="delivery_accepted" type="checkbox">The customer explicitly accepted delivery under the quoted acceptance terms.</label>
<label class="trade-check"><input id="cancel_confirmed" type="checkbox">I confirm cancellation and release of this order's reserved quota.</label>
</fieldset></section>
<details class="trade-assumptions"><summary>Trade model assumptions</summary><div id="trade-assumptions"></div></details>
</main><script src="trade.js"></script></body></html>"""


TRADE_CSS = """
.trade-shell { color: var(--cp-text); }
body > .topbar { height: auto; min-height: 90px; flex-wrap: wrap; gap: 16px; padding: 20px clamp(16px,3%,64px); background: var(--cp-surface-soft); border-top: 3px solid var(--cp-accent); }
.topbar .brand { min-width: 0; }
.topbar .worldbar { flex-wrap: wrap; min-width: 0; gap: 16px; }
.trade-shell *, .trade-shell *::before, .trade-shell *::after { box-sizing: border-box; }
.trade-shell [hidden] { display: none !important; }
.trade-shell section { border-top: 1px solid var(--cp-border); padding-top: 24px; margin-top: 28px; }
.trade-shell h2 { font-size: 20px; margin: 0 0 16px; }
.trade-shell h3 { font-size: 16px; margin: 22px 0 12px; }
.trade-shell fieldset { border: 0; min-width: 0; padding: 18px 0; margin: 0; }
.trade-shell fieldset fieldset { border-top: 1px solid var(--cp-border); margin-top: 18px; }
.trade-shell legend { font-size: 16px; font-weight: 600; padding: 0 8px 0 0; }
.trade-fields { display: grid; grid-template-columns: repeat(auto-fit,minmax(min(100%,220px),1fr)); gap: 16px 22px; align-items: start; }
.trade-fields label { display: grid; gap: 8px; min-width: 0; font-size: 13px; color: var(--cp-text-muted); }
.trade-wide { grid-column: 1 / -1; }
.trade-shell :is(input:not([type=checkbox]),select,textarea) { width: 100%; min-width: 0; min-height: 44px; padding: 10px 12px; border: 1px solid var(--cp-border); border-radius: 6px; background: var(--cp-surface-soft); color: var(--cp-text); font: inherit; font-size: 14px; }
.trade-shell textarea { resize: vertical; }
.trade-shell input[type=checkbox] { width: 18px; height: 18px; flex: 0 0 18px; accent-color: var(--cp-accent); }
.trade-shell label.trade-check { display: flex; align-items: flex-start; gap: 10px; margin: 16px 0; font-size: 13px; color: var(--cp-text); line-height: 1.6; }
.trade-shell button { min-height: 44px; white-space: normal; padding: 10px 18px; border-radius: 6px; border: 1px solid var(--cp-border); background: var(--cp-surface-soft); color: var(--cp-text); cursor: pointer; }
.trade-shell button.primary { background: var(--cp-accent); color: var(--cp-accent-fg); border-color: var(--cp-accent); }
.trade-shell button:disabled { opacity: .5; cursor: not-allowed; }
.trade-shell :is(input,select,textarea,button,a,summary,.table-scroll):focus-visible { outline: 2px solid var(--cp-accent); outline-offset: 3px; }
.trade-help, .trade-notice, .trade-assumptions { font-size: 13px; line-height: 1.7; color: var(--cp-text-muted); overflow-wrap: anywhere; }
.trade-notice { margin: 18px 0; border-left: 3px solid var(--cp-warning); padding: 10px 16px; background: var(--cp-surface-soft); }
.trade-warning { border-left-color: var(--cp-danger); }
.trade-heading, .trade-pager, .trade-actions { display: flex; flex-wrap: wrap; align-items: center; gap: 12px; }
.trade-heading { justify-content: space-between; }
.trade-pager { justify-content: center; margin-top: 18px; }
.trade-metrics { display: grid; grid-template-columns: repeat(auto-fit,minmax(min(100%,220px),1fr)); gap: 0 24px; margin: 0; }
.trade-metrics div { min-width: 0; border-bottom: 1px solid var(--cp-border); padding: 12px 0; }
.trade-metrics dt { font-size: 12px; color: var(--cp-text-muted); }
.trade-metrics dd { margin: 6px 0 0; font-variant-numeric: tabular-nums; overflow-wrap: anywhere; }
.trade-shell .table-scroll { max-height: 60dvh; }
.trade-shell .detail-table { min-width: 740px; }
.trade-shell .detail-table td { vertical-align: top; overflow-wrap: anywhere; max-width: 360px; white-space: normal; }
.trade-shell pre { white-space: pre-wrap; overflow-wrap: anywhere; font: inherit; margin: 0; max-width: 70ch; }
.trade-assumptions { margin-top: 28px; border-top: 1px solid var(--cp-border); padding-top: 20px; }
.trade-assumptions summary { cursor: pointer; color: var(--cp-text); font-weight: 600; }
@media (max-width: 760px) {
  .trade-shell .trade-fields { grid-template-columns: minmax(0,1fr); }
  .trade-shell :is(input:not([type=checkbox]),select,textarea) { font-size: 16px; }
  .trade-actions { align-items: stretch; flex-direction: column; }
  .trade-heading { align-items: flex-start; }
  .trade-shell .detail-title { font-size: 26px; }
}
"""


TRADE_JS = r"""
'use strict';
const el = id => document.getElementById(id);
const quoteFields = ['origin','destination','commodity','quantity','quality','supply_date',
  'delivery_date','supply_mode','purchase_channel','delivery_terms','transport_mode','daily_gp',
  'fixed_gp','contingency_pct','return_trip','customer_price_mode','customer_unit_price',
  'tax_terms','deposit_percent','payment_terms','acceptance_terms','supplier_tax_exempt','tax_exemption_reason'];
const booleanFields = new Set(['return_trip','supplier_tax_exempt']);
const state = {enabled:false, initialized:false, busy:false, options:null, quote:null, fingerprint:null,
  revision:0, expiryTimer:null, orders:[], total:0, offset:0, limit:50, order:null};
function esc(value) {
  return String(value == null ? '' : value).replace(/&/g,'&amp;').replace(/</g,'&lt;')
    .replace(/>/g,'&gt;').replace(/"/g,'&quot;').replace(/'/g,'&#39;');
}
function number(value) {
  return typeof value === 'number' && Number.isFinite(value)
    ? value.toLocaleString(undefined,{maximumFractionDigits:3}) : 'Not provided';
}
function money(value) {
  return typeof value === 'number' && Number.isFinite(value)
    ? value.toLocaleString(undefined,{minimumFractionDigits:2,maximumFractionDigits:6})+' gp' : 'Not provided';
}
function percent(value) { return typeof value === 'number' && Number.isFinite(value) ? number(value)+'%' : 'Not provided'; }
function text(value) { return value == null || value === '' ? 'Not provided' : String(value); }
function flag(value) { return value === true ? 'Yes' : value === false ? 'No' : 'Not provided'; }
function status(message, error=false) { el('status').textContent=message; el('status').className='status'+(error?' error':''); }
function label(value, labels) { return labels[value] || text(value); }
const supplyLabels = {allocated_export:'Allocated export takeover (existing destination allocation)',uncommitted:'Uncommitted forecast quota'};
const transportLabels = {own_caravan:'Own caravan — one 4,000 lb horse wagon',shared_freight:'Shared freight — hired / mixed-mode route'};
const customerLabels = {retail:'Retail',wholesale:'Merchant guild (wholesale)',agreed:'Agreed unit price'};
const paymentLabels = {customer_payment:'Customer payment received',customer_refund:'Customer refund paid',
  supplier_payment:'Supplier payment paid',supplier_refund:'Supplier refund received',expense:'Other expense paid'};
function metrics(rows) {
  return '<dl class="trade-metrics">'+rows.map(([name,value])=>'<div><dt>'+esc(name)+'</dt><dd>'+esc(text(value))+'</dd></div>').join('')+'</dl>';
}
function list(items) { return '<ul>'+(items||[]).map(item=>'<li>'+esc(item)+'</li>').join('')+'</ul>'; }
function warnings(items) { return items && items.length ? '<div class="trade-notice trade-warning"><strong>Review before proceeding</strong>'+list(items)+'</div>' : ''; }
function table(headers, rows, name) {
  return '<div class="table-scroll" tabindex="0" role="region" aria-label="'+esc(name)+'"><table class="detail-table"><thead><tr>'
    +headers.map(h=>'<th scope="col">'+esc(h)+'</th>').join('')+'</tr></thead><tbody>'+rows.join('')+'</tbody></table></div>';
}
async function api(path, body) {
  const options = {headers:{'Accept':'application/json'},cache:'no-store'};
  if (body !== undefined) { options.method='POST'; options.headers['Content-Type']='application/json'; options.body=JSON.stringify(body); }
  const response=await fetch(path,options);
  let data;
  try { data=await response.json(); }
  catch (_) { throw new Error('The server returned an unreadable response. Refresh before retrying; a submitted change may have been recorded.'); }
  if (!response.ok) throw new Error(data && typeof data.error==='string' ? data.error : 'Trade request failed ('+response.status+').');
  return data;
}
function required(id, name) {
  const value=el(id).value.trim();
  if (!value) throw new Error(name+' is required.');
  return value;
}
function numeric(id, name, minimum=0, maximum=Infinity, integer=false) {
  const value=Number(required(id,name));
  if (!Number.isFinite(value) || value<minimum || value>maximum || (integer && !Number.isSafeInteger(value)))
    throw new Error(name+' must be '+(integer?'a whole number':'a number')+' from '+minimum+(maximum===Infinity?' or greater':' to '+maximum)+'.');
  return value;
}
function choice(id, name, values) {
  const value=required(id,name);
  if (!values.includes(value)) throw new Error('Choose a valid '+name.toLowerCase()+'.');
  return value;
}
function harptos(id, name, optional=false) {
  const value=el(id).value.trim();
  if (optional && !value) return null;
  if (!/^[0-9]{4}-[0-9]{2}-[0-9]{2}$/.test(value)) throw new Error(name+' must use Harptos YYYY-MM-DD.');
  return value;
}
function fingerprint() {
  return JSON.stringify(quoteFields.map(id=>[id,booleanFields.has(id)?el(id).checked:el(id).value]));
}
function quoteBody() {
  const options=state.options;
  if (!state.enabled || !options) throw new Error('Trade is not enabled.');
  const body={
    origin:choice('origin','Origin',options.settlements.map(p=>p.id)),
    destination:choice('destination','Destination',options.settlements.map(p=>p.id)),
    commodity:choice('commodity','Commodity',options.commodities.map(p=>p.id)),
    quantity:numeric('quantity','Quantity',1,Infinity,true),
    quality:choice('quality','Quality',options.qualities),
    supply_date:harptos('supply_date','Supply date'),
    supply_mode:choice('supply_mode','Supply basis',['uncommitted','allocated_export']),
    purchase_channel:choice('purchase_channel','Purchase channel',['producer','guild']),
    delivery_terms:choice('delivery_terms','Supplier delivery terms',['pickup','delivered']),
    transport_mode:choice('transport_mode','Transport mode',['own_caravan','shared_freight']),
    customer_price_mode:choice('customer_price_mode','Customer pricing',['retail','wholesale','agreed']),
    tax_terms:choice('tax_terms','Customer tax terms',['included','extra']),
    deposit_percent:numeric('deposit_percent','Customer deposit',0,100),
    payment_terms:choice('payment_terms','Customer payment terms',['on_delivery','before_dispatch']),
    acceptance_terms:required('acceptance_terms','Delivery / acceptance terms'),
    supplier_tax_exempt:el('supplier_tax_exempt').checked,
    fixed_gp:numeric('fixed_gp','Fixed charges'),
    contingency_pct:numeric('contingency_pct','Contingency',0,100),
    daily_gp:0,
    return_trip:false
  };
  const delivery=harptos('delivery_date','Delivery date',true);
  if (delivery) body.delivery_date=delivery;
  if (body.supply_mode==='allocated_export' && body.quality!=='standard')
    throw new Error('Allocated export takeover supports standard grade only. Choose standard or uncommitted graded stock.');
  if (body.delivery_terms==='delivered' && body.transport_mode!=='shared_freight')
    throw new Error('Supplier-delivered quotes require shared freight.');
  if (body.transport_mode==='own_caravan') {
    body.daily_gp=numeric('daily_gp','Daily operating cost');
    body.return_trip=el('return_trip').checked;
  }
  if (body.customer_price_mode==='agreed') body.customer_unit_price=numeric('customer_unit_price','Agreed customer price');
  if (body.supplier_tax_exempt) body.tax_exemption_reason=required('tax_exemption_reason','Tax exemption reason');
  return body;
}
function quoteIsCurrent() {
  return !!(state.quote && state.fingerprint===fingerprint() &&
    Number.isFinite(Date.parse(state.quote.expires_at)) && Date.parse(state.quote.expires_at)>Date.now());
}
function reserveReady() {
  return quoteIsCurrent() && state.quote.reservable===true && !!el('customer_name').value.trim() &&
    !!el('po_reference').value.trim() && el('terms_accepted').checked &&
    (!(state.quote.supply||{}).takeover_requires_ack || el('allocation_authorized').checked);
}
function clearAcknowledgments() { el('terms_accepted').checked=false; el('allocation_authorized').checked=false; }
function invalidateQuote(message='Quote inputs changed. Get a fresh dated quote before reserving.') {
  state.revision++;
  state.quote=null; state.fingerprint=null;
  clearTimeout(state.expiryTimer); state.expiryTimer=null;
  clearAcknowledgments();
  el('quote-state').textContent=message;
  el('quote-summary').innerHTML='<p class="empty">No current quote. Availability must be checked again.</p>';
  syncControls();
}
function syncControls() {
  const locked=state.busy || !state.enabled;
  el('quote-inputs').disabled=locked;
  const delivered=el('delivery_terms').value==='delivered';
  const own=el('transport_mode').value==='own_caravan';
  el('transport_mode').disabled=locked || delivered;
  el('own-budget').disabled=locked || !own;
  el('own-budget').hidden=!own;
  const agreed=el('customer_price_mode').value==='agreed';
  el('agreed-field').hidden=!agreed;
  el('customer_unit_price').disabled=locked || !agreed; el('customer_unit_price').required=agreed;
  const exempt=el('supplier_tax_exempt').checked;
  el('exemption-field').hidden=!exempt;
  el('tax_exemption_reason').disabled=locked || !exempt; el('tax_exemption_reason').required=exempt;
  el('quote-button').disabled=locked;
  el('reservation-inputs').disabled=locked || !quoteIsCurrent() || state.quote.reservable!==true;
  const takeover=!!(state.quote && (state.quote.supply||{}).takeover_requires_ack);
  el('takeover-ack').hidden=!takeover; el('allocation_authorized').required=takeover;
  el('reserve-button').disabled=locked || !reserveReady();
  el('refresh-orders').disabled=state.busy;
  el('previous-orders').disabled=state.busy || state.offset<=0;
  el('next-orders').disabled=state.busy || state.offset+state.limit>=state.total;
  el('payment-inputs').disabled=locked || !state.order;
  el('action-inputs').disabled=locked || !state.order;
  const balance=state.order && state.order.balance || {};
  el('dispatch-button').disabled=locked || balance.can_dispatch!==true;
  el('deliver-button').disabled=locked || balance.can_deliver!==true || !el('delivery_accepted').checked;
  el('cancel-button').disabled=locked || balance.can_cancel!==true || !el('cancel_confirmed').checked;
  document.querySelectorAll('[data-order-id]').forEach(button=>button.disabled=state.busy);
  el('quote-form').setAttribute('aria-busy',String(state.busy));
  el('reserve-form').setAttribute('aria-busy',String(state.busy));
  el('order-detail-section').setAttribute('aria-busy',String(state.busy));
}
function normalizeTransport() {
  if (el('delivery_terms').value==='delivered') el('transport_mode').value='shared_freight';
  if (el('transport_mode').value==='shared_freight') {
    el('daily_gp').value='0';
    el('return_trip').checked=false;
  }
}
function inputChanged() {
  normalizeTransport();
  invalidateQuote();
}
function renderQuote(q, persisted=false) {
  const p=q.prices||{}, s=q.supply||{}, w=s.window||{}, ship=q.shipping||{}, t=q.terms||{}, a=q.amounts||{};
  return '<p class="trade-help">'+(persisted?'Read-only saved quote':'Dated quote')+' '+esc(q.id)+' · Created '+esc(text(q.created_at))+' · Expires '+esc(text(q.expires_at))+'</p>'
    +metrics([['Origin',(q.origin||{}).name],['Destination',(q.destination||{}).name],
      ['Commodity',(q.commodity||{}).name],['Quantity / unit',number(q.quantity)+' '+text((q.commodity||{}).unit)],
      ['Quality',q.quality],['Pickup date (Harptos)',q.pickup_date],['Delivery date (Harptos)',q.delivery_date]])
    +'<h3>Price comparison · gp per unit</h3>'
    +metrics([['Producer gate',money(p.producer_gate_gp)],['Merchant guild (wholesale)',money(p.guild_wholesale_gp)],
      ['Modeled delivered wholesale reference',money(p.delivered_wholesale_gp)],['Retail',money(p.retail_gp)],
      ['Merchant buyback (reference only; not wholesale)',money(p.merchant_buyback_gp)],
      ['Minimum quantity',number(p.minimum_quantity)],['Lot size',number(p.lot_size)],
      ['Margin discount',percent(p.margin_discount_pct)],['Guild markup',percent(p.guild_markup_pct)]])
    +'<h3>Dated supply &amp; carriage</h3>'
    +metrics([['Supply basis',label(s.mode,supplyLabels)],['Forecast window',text(w.start)+' — '+text(w.end)],
      ['Capacity (units)',number(s.capacity_units)],['Already claimed (units)',number(s.claimed_units)],
      ['Available forecast quota (units)',number(s.available_units)],['Supply model',s.basis],
      ['Flow calculation',s.flow_basis],
      ['Claim scope',label(s.claim_scope,{carried_inventory:'Carried inventory across dates',dated_flow:'Dated flow allocation'})],
      ['Authorized takeover required',flag(s.takeover_requires_ack)],['Transport',label(ship.mode,transportLabels)],
      ['Supplier delivery terms',label(ship.terms,{pickup:'Pickup',delivered:'Supplier delivered'})],
      ['Route',(ship.path||[]).join(' → ')],['Carrier',ship.carrier],['One-way travel (days)',number(ship.one_way_days)],
      ['Costed travel (days)',number(ship.cost_days)],['Shipping estimate',money(ship.cost_gp)],
      ['Daily operating allowance',money(ship.daily_gp)],['Fixed allowance',money(ship.fixed_gp)],
      ['Contingency allowance',percent(ship.contingency_pct)],['Empty return budgeted',flag(ship.return_trip)],
      ['Cargo weight (lb)',number(ship.cargo_lb)],['Carrier capacity (lb)',number(ship.capacity_lb)],
      ['Earliest delivery (Harptos)',ship.earliest_delivery_date],['Carriage cost basis',ship.basis]])
    +'<p class="trade-notice">Modeled availability, not surveyed stock. Carried-inventory claims persist across dates and after delivery; only cancellation releases them. Dated export takeovers replace an existing destination allocation, not added demand. An own caravan is one 4,000 lb horse wagon; its selected budget may include an empty return. Own-caravan operating days exclude loading and trading; fixed charges can budget those activities. Shared freight can use a hired mixed-mode route.</p>'
    +'<h3>Quoted customer &amp; supplier terms</h3>'
    +metrics([['Supplier purchase channel',label(t.purchase_channel,{producer:'Producer gate',guild:'Merchant guild (wholesale)'})],
      ['Customer pricing',label(t.customer_price_mode,customerLabels)],['Customer unit price',money(t.customer_unit_price_gp)],
      ['Customer tax terms',label(t.tax_terms,{included:'Included',extra:'Added separately'})],['Deposit',percent(t.deposit_percent)],
      ['Customer payment terms',label(t.payment_terms,{on_delivery:'Balance on delivery',before_dispatch:'Full prepayment before dispatch'})],
      ['Delivery / acceptance terms',t.acceptance_terms],['Supplier tax exemption',flag(t.supplier_tax_exempt)],['Exemption reason',t.tax_exemption_reason]])
    +'<h3>Projected economics · not recorded cash</h3>'
    +metrics([['Supplier net',money(a.supplier_net_gp)],['Supplier tax',money(a.supplier_tax_gp)],
      ['Supplier total due',money(a.supplier_total_gp)],['Shipping paid separately',money(a.shipping_paid_separately_gp)],
      ['Customer net',money(a.customer_net_gp)],['Customer tax',money(a.customer_tax_gp)],
      ['Customer total due',money(a.customer_total_gp)],['Customer deposit due',money(a.customer_deposit_due_gp)],
      ['Customer duty held back from deposit',money(a.customer_deposit_tax_reserve_gp)],
      ['Usable customer deposit (after duty reserve)',money(a.customer_deposit_usable_gp)],
      ['Estimated cost',money(a.estimated_cost_gp)],['Projected profit (estimate)',money(a.estimated_profit_gp)]])
    +'<p class="trade-help">Usable deposit is the quoted deposit after holding back customer duty, not money already collected. Actual receipts belong in the manual cash ledger.</p>'
    +warnings(q.warnings)+'<details><summary>Quote assumptions</summary>'+list(q.assumptions)+'</details>';
}
function adoptQuote(q, mark) {
  if (!q || !q.id) throw new Error('The server did not return a quote.');
  state.quote=q; state.fingerprint=mark; clearAcknowledgments();
  el('quote-summary').innerHTML=renderQuote(q);
  const current=quoteIsCurrent();
  el('quote-state').textContent=!current?'This quote is expired or has no valid expiry. Get a fresh quote.'
    :q.reservable===true?'Quote ready for review. No quota reserved yet.':'This quote cannot be reserved. Review the supply and warnings; adjust inputs and quote again.';
  clearTimeout(state.expiryTimer);
  if (current) state.expiryTimer=setTimeout(()=>{
    el('quote-state').textContent='This quote has expired. Get a fresh quote before reserving.';
    clearAcknowledgments(); syncControls();
  },Math.min(Date.parse(q.expires_at)-Date.now()+10,2147483647));
}
async function exclusive(work) {
  if (state.busy) return;
  state.busy=true; syncControls();
  try { await work(); }
  catch (error) { status(error.message || 'Trade request failed.',true); }
  finally { state.busy=false; syncControls(); }
}
async function quoteNow() {
  if (state.busy) return;
  invalidateQuote('Checking dated supply and prices...');
  await exclusive(async()=>{
    const body=quoteBody(), mark=fingerprint(), revision=state.revision;
    status('Calculating quote...');
    const data=await api('/api/trade/quote',body);
    if (revision!==state.revision || mark!==fingerprint()) {
      invalidateQuote('Inputs changed while the quote was loading. Get a fresh quote.');
      return;
    }
    adoptQuote(data.quote,mark);
    status(data.quote.reservable===true?'Quote received. Review all terms before confirming.':'Quote received, but it is not reservable.');
  });
}
function populateSelect(id, items) {
  el(id).innerHTML='<option value="">Choose...</option>'+items.map(item=>'<option value="'+esc(item.id)+'">'+esc(item.name)+'</option>').join('');
}
function choosePrefill(id, value, items) {
  const key=String(value||'').toLowerCase();
  const item=items.find(item=>String(item.id).toLowerCase()===key || String(item.name).toLowerCase()===key);
  el(id).value=item?item.id:'';
}
function updateOptions(data, initial=false) {
  if (!data || typeof data.enabled!=='boolean') throw new Error('The server did not return trade options.');
  state.options=data; state.enabled=data.enabled;
  el('trade-date').textContent=data.date?text(data.date.label)+' · '+text(data.date.iso):'World date unavailable';
  el('trade-assumptions').innerHTML=list(data.assumptions);
  if ((!initial && state.initialized) || !data.enabled) return;
  populateSelect('origin',data.settlements); populateSelect('destination',data.settlements);
  populateSelect('commodity',data.commodities.map(item=>({...item,name:item.name+' / '+item.unit+' / '+number(item.weight)+' lb'})));
  populateSelect('quality',data.qualities.map(value=>({id:value,name:value})));
  const defaults={supplier_tax_exempt:false,...data.defaults};
  for (const id of quoteFields) {
    if (defaults[id]===undefined) continue;
    if (booleanFields.has(id)) el(id).checked=defaults[id]===true;
    else el(id).value=String(defaults[id]);
  }
  el('supply_date').value=(data.date||{}).iso||'';
  const params=new URLSearchParams(location.search);
  for (const id of ['origin','destination','commodity']) {
    const prefill=params.get(id) || (id==='destination'?params.get('settlement'):null);
    if (prefill) choosePrefill(id,prefill,id==='commodity'?data.commodities:data.settlements);
  }
  normalizeTransport();
  state.initialized=true;
}
function renderOrders() {
  const rows=state.orders.map(o=>{
    const q=o.quote||{}, a=q.amounts||{}, b=o.balance||{};
    return '<tr><td><button type="button" data-order-id="'+esc(o.id)+'" aria-label="Open purchase order '+esc(o.po_reference)+'">'+esc(o.po_reference)+'</button><br>'+esc(o.id)+'</td>'
      +'<td>'+esc(o.status)+'</td><td>'+esc(o.customer_name)+'</td>'
      +'<td>'+esc(number(q.quantity))+' '+esc((q.commodity||{}).unit)+' '+esc((q.commodity||{}).name)+'</td>'
      +'<td>'+esc(text(q.pickup_date))+' → '+esc(text(q.delivery_date))+'</td>'
      +'<td>'+esc(money(a.customer_total_gp))+'</td><td>'+esc(money(a.supplier_total_gp))+'</td>'
      +'<td>'+esc(money(b.customer_due_gp))+'</td></tr>';
  });
  el('order-list').innerHTML=rows.length?table(['Reference / details','Status','Customer','Item / quantity','Pickup → delivery','Customer total','Supplier total','Customer balance'],rows,'Persisted purchase orders'):'<p class="empty">No purchase orders on this page.</p>';
  el('order-page').textContent=state.total?'Orders '+(state.offset+1)+'–'+(state.offset+state.orders.length)+' of '+state.total:'No orders';
}
async function loadOrders(offset=state.offset) {
  const data=await api('/api/trade/orders?offset='+encodeURIComponent(offset)+'&limit='+encodeURIComponent(state.limit));
  if (!Array.isArray(data.orders) || !Number.isInteger(data.total) || data.total<0 ||
      !Number.isInteger(data.offset) || data.offset<0 || !Number.isInteger(data.limit) || data.limit<=0)
    throw new Error('The server returned an incomplete order list.');
  if (data.total>0 && data.offset>=data.total) return loadOrders(Math.floor((data.total-1)/data.limit)*data.limit);
  state.orders=data.orders; state.total=data.total; state.offset=data.offset; state.limit=data.limit;
  renderOrders();
}
function detailsText(value) { return typeof value==='object' && value!==null ? JSON.stringify(value,null,2) : text(value); }
function setOrder(o) {
  if (!o || !o.id || !o.quote || !o.balance) throw new Error('The server returned incomplete order details; refresh before making another entry.');
  state.order=o;
  el('order-detail-section').hidden=false;
  el('delivery_accepted').checked=false; el('cancel_confirmed').checked=false; el('payment_confirmed').checked=false;
  const b=o.balance;
  const paymentRows=(o.payments||[]).map(p=>'<tr>'+[label(p.kind,paymentLabels),money(p.amount_gp),p.reference,p.simulation_date,p.created_at].map(v=>'<td>'+esc(text(v))+'</td>').join('')+'</tr>');
  const auditRows=(o.audit||[]).map(a=>'<tr><td>'+esc(a.action)+'</td><td>'+esc(text(a.simulation_date))+'</td><td>'+esc(text(a.created_at))+'</td><td><pre>'+esc(detailsText(a.details))+'</pre></td></tr>');
  el('order-detail').innerHTML=metrics([['Order',o.id],['PO reference',o.po_reference],['Customer',o.customer_name],
    ['Status',o.status],['Version',number(o.version)],['Created',o.created_at]])
    +'<h3>Manual cash ledger · not profit</h3>'
    +metrics([['Customer paid (net of refunds)',money(b.customer_paid_gp)],['Customer balance due',money(b.customer_due_gp)],
      ['Supplier paid (net of refunds)',money(b.supplier_paid_gp)],['Supplier balance due',money(b.supplier_due_gp)],
      ['Expenses recorded',money(b.expenses_gp)],['Recorded cash (not profit)',money(b.recorded_cash_gp)],
      ['Deposit remaining',money(b.deposit_remaining_gp)],['Can dispatch now',flag(b.can_dispatch)],
      ['Can deliver now',flag(b.can_deliver)],['Can cancel now',flag(b.can_cancel)]])
    +warnings(b.warnings)
    +'<h3>Recorded cash movements</h3>'+(paymentRows.length?table(['Movement','Amount','Reference','World date','Recorded at'],paymentRows,'Manual cash movements'):'<p class="empty">No cash movements recorded.</p>')
    +'<h3>Audit history</h3>'+(auditRows.length?table(['Action','World date','Recorded at','Details'],auditRows,'Purchase order audit history'):'<p class="empty">No audit entries supplied.</p>')
    +'<details><summary>Read-only persisted quote &amp; projected profit</summary>'+renderQuote(o.quote,true)+'</details>';
  syncControls();
}
async function loadOrder(id) {
  const data=await api('/api/trade/order?id='+encodeURIComponent(id));
  setOrder(data.order);
}
async function refreshAfterChange(message) {
  invalidateQuote('The ledger changed. Get a new quote to refresh dated availability.');
  try {
    updateOptions(await api('/api/trade/options'));
    await loadOrders();
    status(message+' Orders and world date refreshed; request a new quote for current availability.');
  } catch (error) {
    status(message+' Refresh failed: '+error.message+' Refresh the desk before continuing.',true);
  }
}
async function reserve() {
  await exclusive(async()=>{
    if (!quoteIsCurrent()) throw new Error('This quote is stale or expired. Get a fresh quote before reserving.');
    if (state.quote.reservable!==true) throw new Error('This quote cannot be reserved.');
    const body={quote_id:state.quote.id,customer_name:required('customer_name','Customer name'),
      po_reference:required('po_reference','Purchase order reference'),terms_accepted:el('terms_accepted').checked};
    if (!body.terms_accepted) throw new Error('Explicit acceptance of supplier and customer terms is required.');
    if ((state.quote.supply||{}).takeover_requires_ack) {
      if (!el('allocation_authorized').checked) throw new Error('Separate authorization to take over the existing allocation is required.');
      body.allocation_authorized=true;
    }
    status('Reserving the explicitly confirmed purchase order...');
    let data;
    try { data=await api('/api/trade/order',body); }
    catch (error) { invalidateQuote('Reservation was not confirmed. Refresh orders to check the outcome, then quote again.'); throw error; }
    setOrder(data.order);
    el('payment_amount').value=''; el('payment_reference').value='';
    await refreshAfterChange('Purchase order reserved. No external purchase or payment was made.');
  });
}
async function recordPayment() {
  await exclusive(async()=>{
    if (!state.order) throw new Error('Open a purchase order first.');
    const body={order_id:state.order.id,
      kind:choice('payment_kind','Cash movement',Object.keys(paymentLabels)),
      amount_gp:numeric('payment_amount','Cash movement amount'),
      reference:required('payment_reference','Movement reference')};
    if (body.amount_gp<=0) throw new Error('Cash movement amount must be positive.');
    if (!el('payment_confirmed').checked) throw new Error('Confirm that this cash movement actually occurred before recording it.');
    status('Recording manual cash movement...');
    const data=await api('/api/trade/payment',body);
    setOrder(data.order);
    el('payment_amount').value=''; el('payment_reference').value='';
    await refreshAfterChange('Manual cash movement recorded. No money was transferred by this desk.');
  });
}
async function changeStatus(action) {
  await exclusive(async()=>{
    if (!['dispatch','deliver','cancel'].includes(action) || !state.order) throw new Error('Choose a valid purchase order action.');
    if (state.order.balance['can_'+action]!==true)
      throw new Error('This action is not currently available. Review balances and the world date, then refresh.');
    if (!Number.isInteger(state.order.version)) throw new Error('Order version is unavailable. Refresh the order.');
    const body={order_id:state.order.id,action,version:state.order.version};
    if (action==='deliver') {
      if (!el('delivery_accepted').checked) throw new Error('Explicit customer delivery acceptance is required.');
      body.accepted=true;
    }
    if (action==='cancel' && !el('cancel_confirmed').checked) throw new Error('Confirm cancellation and quota release first.');
    status('Recording '+action+'...');
    const data=await api('/api/trade/status',body);
    setOrder(data.order);
    await refreshAfterChange('Order '+action+' recorded. The world clock was not advanced.');
  });
}
async function openOrder(id) {
  await exclusive(async()=>{
    status('Loading purchase order...');
    state.order=null; el('order-detail-section').hidden=true; syncControls();
    await loadOrder(id);
    el('payment_amount').value=''; el('payment_reference').value='';
    status('Purchase order loaded. Its saved quote is read-only.');
  });
}
async function refreshDesk() {
  if (state.busy) return;
  invalidateQuote('Desk refreshed. Get a new quote for current dated availability.');
  await exclusive(async()=>{
    status('Refreshing world date and persisted orders...');
    updateOptions(await api('/api/trade/options'));
    await loadOrders();
    if (state.order) {
      const id=state.order.id;
      state.order=null; el('order-detail-section').hidden=true; syncControls();
      await loadOrder(id);
    }
    status(state.enabled?'Desk refreshed. The world clock was not advanced.':'Trade is disabled for this world.');
  });
}
async function pageOrders(offset) {
  await exclusive(async()=>{ status('Loading orders...'); await loadOrders(offset); status('Purchase order page loaded.'); });
}
function bindTrade() {
  el('quote-form').addEventListener('submit',event=>{event.preventDefault(); void quoteNow();});
  for (const event of ['input','change']) {
    el('quote-form').addEventListener(event,inputChanged);
    el('reserve-form').addEventListener(event,syncControls);
    el('action-inputs').addEventListener(event,syncControls);
  }
  el('reserve-form').addEventListener('submit',event=>{event.preventDefault(); void reserve();});
  el('payment-form').addEventListener('submit',event=>{event.preventDefault(); void recordPayment();});
  el('refresh-orders').addEventListener('click',()=>void refreshDesk());
  el('previous-orders').addEventListener('click',()=>void pageOrders(Math.max(0,state.offset-state.limit)));
  el('next-orders').addEventListener('click',()=>void pageOrders(state.offset+state.limit));
  el('order-list').addEventListener('click',event=>{
    const button=event.target.closest('[data-order-id]');
    if (button && !button.disabled) void openOrder(button.dataset.orderId);
  });
  for (const action of ['dispatch','deliver','cancel'])
    el(action+'-button').addEventListener('click',()=>void changeStatus(action));
}
async function startTrade() {
  bindTrade();
  await exclusive(async()=>{
    updateOptions(await api('/api/trade/options'),true);
    await loadOrders(0);
    status(state.enabled?'Choose terms and get a dated quote. No reservation is automatic.':'Trade is disabled for this world.');
  });
}
startTrade();
"""


TRADE_ASSETS = {
    "trade.html": (TRADE_HTML, "text/html; charset=utf-8"),
    "trade.js": (TRADE_JS, "application/javascript; charset=utf-8"),
    "trade.css": (TRADE_CSS, "text/css; charset=utf-8"),
}
