"""Focused, dependency-free Node checks for the standalone wholesale desk."""

import json
import subprocess
from html.parser import HTMLParser

import pytest

from faerun.tradeassets import TRADE_ASSETS, TRADE_CSS, TRADE_HTML, TRADE_JS


NODE_HARNESS = r"""
const assert = require('node:assert/strict');
const elements = new Map(), requests = [], timers = new Map();
let timerId=0;
class Element {
  constructor(id) {
    this.id=id; this.value=''; this.checked=false; this.disabled=false; this.hidden=false;
    this.required=false; this.innerHTML=''; this.textContent=''; this.className='';
    this.attributes={}; this.listeners={}; this.dataset={};
  }
  addEventListener(name,callback) { (this.listeners[name] ||= []).push(callback); }
  emit(name) { for (const callback of this.listeners[name]||[]) callback({target:this,preventDefault(){}}); }
  setAttribute(name,value) { this.attributes[name]=value; }
}
function element(id) {
  if (!elements.has(id)) elements.set(id,new Element(id));
  return elements.get(id);
}
globalThis.document={getElementById:element,querySelectorAll:()=>[]};
globalThis.location={search:''};
globalThis.setTimeout=callback=>{timers.set(++timerId,callback);return timerId;};
globalThis.clearTimeout=id=>timers.delete(id);
const clone=value=>JSON.parse(JSON.stringify(value));
const options={
  enabled:true,date:{iso:'1492-02-30',label:'30 Alturiak 1492 DR'},
  settlements:[{id:'berdusk',name:'Berdusk'},{id:'proskur',name:'Proskur'},{id:'waterdeep',name:'Waterdeep'}],
  commodities:[{id:'wine_fine',name:'Fine wine',unit:'bottle',weight:2},{id:'grain',name:'Grain',unit:'bushel',weight:10}],
  qualities:['basic','standard','fine','masterwork'],
  defaults:{origin:'berdusk',destination:'proskur',commodity:'wine_fine',quantity:1000,
    quality:'standard',supply_mode:'allocated_export',purchase_channel:'producer',
    delivery_terms:'pickup',transport_mode:'own_caravan',daily_gp:5,fixed_gp:0,
    contingency_pct:10,return_trip:true,customer_price_mode:'retail',tax_terms:'included',
    deposit_percent:50,payment_terms:'on_delivery',acceptance_terms:'Inspect on arrival.'},
  assumptions:['Quota is a forecast, not physical stock.']
};
const quote={
  id:'quote-1',created_at:'2026-01-01T00:00:00Z',expires_at:'2999-01-01T00:00:00Z',
  origin:{id:'berdusk',name:'Berdusk'},destination:{id:'proskur',name:'Proskur'},
  commodity:{id:'wine_fine',name:'Fine wine',unit:'bottle',weight:2},quantity:1000,
  quality:'standard',pickup_date:'1492-02-30',delivery_date:'1492-03-10',
  prices:{producer_gate_gp:2,guild_wholesale_gp:2.2,delivered_wholesale_gp:2.5,retail_gp:4,
    merchant_buyback_gp:1.8,minimum_quantity:100,lot_size:50,margin_discount_pct:20,guild_markup_pct:10},
  supply:{mode:'allocated_export',capacity_units:2000,claimed_units:100,available_units:1900,
    window:{start:'1492-02-30',end:'1492-03-09'},basis:'Dated destination allocation.',takeover_requires_ack:true},
  shipping:{mode:'own_caravan',terms:'pickup',path:['Berdusk','Proskur'],one_way_days:5,cost_days:10,
    cost_gp:55,cargo_lb:2000,capacity_lb:4000,carrier:'One horse wagon',basis:'Empty return budget included.',
    earliest_delivery_date:'1492-03-05'},
  terms:{customer_price_mode:'retail',customer_unit_price_gp:4,tax_terms:'included',deposit_percent:50,
    payment_terms:'on_delivery',acceptance_terms:'Inspect on arrival.',supplier_tax_exempt:false,tax_exemption_reason:''},
  amounts:{supplier_net_gp:2000,supplier_tax_gp:100,supplier_total_gp:2100,shipping_paid_separately_gp:55,
    customer_net_gp:3800,customer_tax_gp:200,customer_total_gp:4000,customer_deposit_due_gp:2000,
    customer_deposit_usable_gp:1800,customer_deposit_tax_reserve_gp:200,
    estimated_cost_gp:2155,estimated_profit_gp:1845},
  assumptions:['Forecast quota for this window.'],warnings:['Confirm the allocation authorization.'],reservable:true
};
function makeOrder() {
  return {id:'order-1',quote_id:quote.id,customer_name:'Customer',po_reference:'PO-001',status:'reserved',
    version:7,created_at:'2026-01-01T01:00:00Z',quote:clone(quote),payments:[],audit:[],
    balance:{customer_paid_gp:2000,customer_due_gp:2000,supplier_paid_gp:2100,supplier_due_gp:0,
      expenses_gp:55,recorded_cash_gp:-155,deposit_remaining_gp:0,
      can_dispatch:true,can_deliver:false,can_cancel:false,warnings:[]}};
}
function reply(data, ok=true, status=200) { return {ok,status,json:async()=>clone(data)}; }
let order=makeOrder();
async function standardResponse(path,request) {
  if (path==='/api/trade/options') return reply(options);
  if (path.startsWith('/api/trade/orders?')) return reply({orders:[order],total:1,offset:0,limit:50});
  if (path==='/api/trade/quote') return reply({quote});
  if (path.startsWith('/api/trade/order?id=')) return reply({order});
  if (['/api/trade/order','/api/trade/payment','/api/trade/status'].includes(path)) return reply({order});
  throw new Error('Unexpected request: '+path);
}
let responder=standardResponse;
globalThis.fetch=async(path,request)=>{requests.push({path,request});return responder(path,request);};
function postRequests() { return requests.filter(row=>row.request.method==='POST'); }
"""


def run_trade_script(assertions):
    script = (
        NODE_HARNESS
        + TRADE_JS.replace("\nstartTrade();\n", "\n")
        + """
function ready() {
  updateOptions(clone(options),true);
  bindTrade();
  syncControls();
}
function readyQuote(q=clone(quote)) {
  adoptQuote(q,fingerprint());
  el('customer_name').value='Customer';
  el('po_reference').value='PO-001';
  el('terms_accepted').checked=true;
  el('allocation_authorized').checked=true;
  syncControls();
}
(async()=>{
ready();
"""
        + assertions
        + "\n})().catch(error=>{console.error(error);process.exitCode=1;});\n"
    )
    result = subprocess.run(
        ["node", "-"], input=script, capture_output=True, text=True,
        encoding="utf-8", timeout=20,
    )
    assert result.returncode == 0, result.stdout + result.stderr


def test_trade_assets_compile_and_export_correct_content_types():
    assert set(TRADE_ASSETS) == {"trade.html", "trade.js", "trade.css"}
    assert TRADE_ASSETS["trade.html"] == (TRADE_HTML, "text/html; charset=utf-8")
    assert TRADE_ASSETS["trade.css"] == (TRADE_CSS, "text/css; charset=utf-8")
    assert TRADE_ASSETS["trade.js"] == (TRADE_JS, "application/javascript; charset=utf-8")
    result = subprocess.run(
        ["node", "--check"], input=TRADE_JS, capture_output=True, text=True,
        encoding="utf-8", timeout=20,
    )
    assert result.returncode == 0, result.stderr


def test_accessible_fields_harptos_dates_and_no_external_payment_promises():
    class Tags(HTMLParser):
        def __init__(self):
            super().__init__()
            self.by_id = {}

        def handle_starttag(self, tag, attrs):
            attrs = dict(attrs)
            if "id" in attrs:
                assert attrs["id"] not in self.by_id
                self.by_id[attrs["id"]] = (tag, attrs)

    tags = Tags()
    tags.feed(TRADE_HTML)
    for name in ("supply_date", "delivery_date"):
        assert tags.by_id[name][1]["type"] == "text"
        assert tags.by_id[name][1]["aria-describedby"] == "harptos-help"
    for name in ("quantity", "supply_date", "customer_name", "po_reference",
                 "terms_accepted", "acceptance_terms", "payment_amount",
                 "payment_reference", "payment_confirmed"):
        assert "required" in tags.by_id[name][1]
    assert tags.by_id["status"][1]["aria-live"] == "polite"
    assert 'href="app.css"' in TRADE_HTML and 'href="detail.css"' in TRADE_HTML
    assert "Merchant guild (wholesale)" in TRADE_HTML
    assert "not physical on-hand stock" in TRADE_HTML
    assert "not added demand" in TRADE_HTML
    assert "persist across restarts" in TRADE_HTML
    assert "not a payment processor" in TRADE_HTML
    assert "never advances time automatically" in TRADE_HTML
    assert "after refunding recorded funds" in TRADE_HTML
    assert "not immediately return to stock" in TRADE_HTML
    assert "[hidden]" in TRADE_CSS
    assert ":focus-visible" in TRADE_CSS
    assert "@media" in TRADE_CSS


def test_quote_currency_preserves_locked_six_decimal_unit_prices():
    run_trade_script("""
assert.notEqual(money(1.234567),money(1.234568));
assert.notEqual(money(0.000001),money(0.000002));
""")


def test_initial_options_and_prefill_use_ids_current_simulation_date_and_no_auto_quote():
    run_trade_script("""
location.search='?origin=Waterdeep&settlement=berdusk&commodity=grain';
await startTrade();
assert.equal(el('origin').value,'waterdeep');
assert.equal(el('destination').value,'berdusk');
assert.equal(el('commodity').value,'grain');
assert.equal(el('supply_date').value,'1492-02-30');
assert.equal(quoteBody().supply_date,'1492-02-30','Harptos is not Gregorian February');
assert.equal(el('trade-date').textContent,'30 Alturiak 1492 DR · 1492-02-30');
el('supply_date').value='1492-01-31';
assert.equal(quoteBody().supply_date,'1492-01-31','Harptos festival day 31 is accepted');
assert.equal(postRequests().length,0);
assert.equal(el('quote-inputs').disabled,false);
location.search='?settlement=berdusk&destination=proskur';
updateOptions(clone(options),true);
assert.equal(el('destination').value,'proskur');
location.search='?commodity=unknown';
updateOptions(clone(options),true);
assert.equal(el('commodity').value,'');
assert.throws(()=>quoteBody(),/Commodity is required/);
""")


@pytest.mark.parametrize(
    "field",
    ["origin", "destination", "commodity", "quantity", "quality", "supply_date",
     "daily_gp", "fixed_gp", "contingency_pct", "deposit_percent", "acceptance_terms"],
    ids=["origin", "dest", "item", "qty", "grade", "date", "daily", "fixed", "risk", "deposit", "terms"],
)
def test_missing_required_quote_fields_never_silently_become_zero(field):
    run_trade_script(
        "el(" + json.dumps(field) + ").value='   ';\n"
        + """
await quoteNow();
assert.equal(postRequests().length,0);
assert.equal(el('status').className,'status error');
assert.equal(state.quote,null);
assert.equal(el('reserve-button').disabled,true);
"""
    )


@pytest.mark.parametrize(
    ("field", "value"),
    [("quantity", "1.5"), ("quantity", "0"), ("daily_gp", "-1"),
     ("fixed_gp", "Infinity"), ("contingency_pct", "101"),
     ("deposit_percent", "-1"), ("delivery_date", "tomorrow")],
    ids=["fraction", "zero", "negative", "infinity", "risk-max", "deposit-min", "bad-date"],
)
def test_invalid_quote_values_are_rejected_before_request(field, value):
    run_trade_script(
        f"el({json.dumps(field)}).value={json.dumps(value)};\n"
        + "assert.throws(()=>quoteBody()); assert.equal(postRequests().length,0);"
    )


def test_agreed_price_tax_exemption_and_takeover_grade_are_explicit():
    run_trade_script("""
el('customer_price_mode').value='agreed'; inputChanged();
assert.equal(el('customer_unit_price').required,true);
assert.equal(el('customer_unit_price').disabled,false);
assert.throws(()=>quoteBody(),/Agreed customer price is required/);
el('customer_unit_price').value='0';
assert.equal(quoteBody().customer_unit_price,0);
el('supplier_tax_exempt').checked=true; inputChanged();
assert.throws(()=>quoteBody(),/Tax exemption reason is required/);
el('tax_exemption_reason').value='Guild exemption certificate';
assert.equal(quoteBody().supplier_tax_exempt,true);
assert.equal(quoteBody().tax_exemption_reason,'Guild exemption certificate');
el('quality').value='fine';
assert.throws(()=>quoteBody(),/standard grade only/);
el('supply_mode').value='uncommitted';
assert.equal(quoteBody().quality,'fine');
el('customer_price_mode').value='retail'; el('supplier_tax_exempt').checked=false; inputChanged();
assert.equal(el('customer_unit_price').disabled,true);
assert.ok(!('customer_unit_price' in quoteBody()));
assert.ok(!('tax_exemption_reason' in quoteBody()));
""")


def test_transport_delivery_constraints_and_json_quote_intent():
    run_trade_script("""
const own=quoteBody();
assert.equal(own.transport_mode,'own_caravan'); assert.equal(own.return_trip,true);
assert.equal(own.fixed_gp,0); assert.equal(own.daily_gp,5); assert.equal(own.contingency_pct,10);
el('purchase_channel').value='guild';
el('delivery_terms').value='delivered'; el('delivery_terms').emit('change');
// Events normally bubble from the field to the form.
el('quote-form').emit('change');
assert.equal(el('transport_mode').value,'shared_freight');
assert.equal(el('transport_mode').disabled,true);
assert.equal(el('return_trip').checked,false);
assert.equal(el('daily_gp').value,'0');
assert.equal(el('own-budget').hidden,true);
el('daily_gp').value=''; el('fixed_gp').value='12'; el('contingency_pct').value='7';
await quoteNow();
const sent=postRequests()[0];
assert.equal(sent.path,'/api/trade/quote');
assert.equal(sent.request.headers['Content-Type'],'application/json');
assert.equal(sent.request.headers.Accept,'application/json');
const body=JSON.parse(sent.request.body);
assert.equal(body.transport_mode,'shared_freight');
assert.equal(body.purchase_channel,'guild');
assert.equal(body.return_trip,false);
assert.equal(body.daily_gp,0);
assert.equal(body.fixed_gp,12);
assert.equal(body.contingency_pct,7);
assert.ok(!('customer_unit_price' in body));
assert.ok(!('delivery_date' in body));
assert.equal(body.supplier_tax_exempt,false);
assert.equal(state.quote.id,'quote-1');
assert.equal(el('reserve-button').disabled,true,'fresh quotes reset acknowledgments');
""")


def test_shared_freight_switch_and_defaults_clear_own_daily_and_return_trip():
    run_trade_script("""
readyQuote();
el('transport_mode').value='shared_freight';
el('quote-form').emit('change');
assert.equal(el('daily_gp').value,'0');
assert.equal(el('return_trip').checked,false);
assert.equal(el('own-budget').disabled,true);
assert.equal(state.quote,null);
assert.equal(quoteBody().daily_gp,0);
assert.equal(quoteBody().return_trip,false);
updateOptions({...options,defaults:{...options.defaults,transport_mode:'shared_freight'}},true);
syncControls();
assert.equal(el('daily_gp').value,'0','shared options must not retain default daily 5');
assert.equal(el('return_trip').checked,false,'shared options must not retain default return true');
assert.equal(el('own-budget').disabled,true);
el('transport_mode').value='own_caravan'; el('quote-form').emit('change');
assert.equal(el('own-budget').disabled,false);
el('daily_gp').value='8'; el('return_trip').checked=true;
assert.equal(quoteBody().daily_gp,8);
assert.equal(quoteBody().return_trip,true);
""")


def test_projected_deposit_shows_duty_reserve_and_usable_cash_separately():
    run_trade_script("""
const html=renderQuote(quote);
assert.ok(html.includes('<dt>Customer duty held back from deposit</dt><dd>'+money(200)+'</dd>'));
assert.ok(html.includes('<dt>Usable customer deposit (after duty reserve)</dt><dd>'+money(1800)+'</dd>'));
assert.ok(html.includes('not money already collected'));
assert.ok(html.includes('Own-caravan operating days exclude loading and trading'));
setOrder(makeOrder());
assert.ok(el('order-detail').innerHTML.includes('Usable customer deposit (after duty reserve)'));
const missing=clone(quote);
delete missing.amounts.customer_deposit_usable_gp;
assert.ok(renderQuote(missing).includes('<dt>Usable customer deposit (after duty reserve)</dt><dd>Not provided</dd>'));
""")


@pytest.mark.parametrize(
    "field",
    ["origin", "destination", "commodity", "quantity", "quality", "supply_date",
     "delivery_date", "supply_mode", "purchase_channel", "delivery_terms",
     "transport_mode", "daily_gp", "fixed_gp", "contingency_pct", "return_trip",
     "customer_price_mode", "customer_unit_price", "tax_terms", "deposit_percent",
     "payment_terms", "acceptance_terms", "supplier_tax_exempt", "tax_exemption_reason"],
    ids=["origin", "dest", "item", "qty", "grade", "pickup", "arrival", "supply",
         "channel", "delivery", "transport", "daily", "fixed", "risk", "return",
         "pricing", "agreed", "tax", "deposit", "payment", "accept", "exempt", "reason"],
)
def test_every_quote_edit_invalidates_quote_and_reservation(field):
    run_trade_script(
        "const field=" + json.dumps(field) + ";\n"
        + """
readyQuote();
assert.equal(el('reserve-button').disabled,false);
if (booleanFields.has(field)) el(field).checked=!el(field).checked;
else el(field).value+=' edited';
el('quote-form').emit('input');
assert.equal(state.quote,null);
assert.equal(el('terms_accepted').checked,false);
assert.equal(el('allocation_authorized').checked,false);
assert.equal(el('reserve-button').disabled,true);
await reserve();
assert.equal(postRequests().length,0);
assert.match(el('status').textContent,/stale or expired/);
"""
    )


def test_quote_race_double_submit_expiry_and_programmatic_edits_are_safe():
    run_trade_script("""
let finish;
responder=()=>new Promise(resolve=>finish=resolve);
const pending=quoteNow();
assert.equal(el('quote-inputs').disabled,true);
await quoteNow();
assert.equal(postRequests().length,1,'no double submission');
el('quantity').value='2000'; inputChanged();
finish(reply({quote})); await pending;
assert.equal(state.quote,null,'late quote cannot restore stale reservation');
assert.equal(el('reserve-button').disabled,true);
responder=standardResponse;
readyQuote();
el('deposit_percent').value='20';
await reserve();
assert.equal(postRequests().length,1,'fingerprint catches edits without a DOM event');
assert.match(el('status').textContent,/stale or expired/);
readyQuote({...clone(quote),expires_at:'2000-01-01T00:00:00Z'});
assert.equal(el('reserve-button').disabled,true);
await reserve();
assert.equal(postRequests().length,1);
readyQuote();
const realNow=Date.now;
Date.now=()=>Date.parse(quote.expires_at)+1000;
for (const callback of timers.values()) callback();
assert.equal(el('reserve-button').disabled,true);
assert.match(el('quote-state').textContent,/expired/);
Date.now=realNow;
""")


@pytest.mark.parametrize("field", ["customer_name", "po_reference", "terms_accepted", "allocation_authorized"],
                         ids=["customer", "po", "terms", "takeover"])
def test_reservation_requires_customer_reference_and_separate_acknowledgments(field):
    run_trade_script(
        "const field=" + json.dumps(field) + ";\n"
        + """
readyQuote();
if (field.endsWith('accepted') || field.endsWith('authorized')) el(field).checked=false;
else el(field).value=' ';
syncControls();
assert.equal(el('reserve-button').disabled,true);
await reserve();
assert.equal(postRequests().length,0);
assert.equal(el('status').className,'status error');
"""
    )


def test_confirm_reserves_exact_quote_and_refreshes_persisted_list_without_another_booking():
    run_trade_script("""
readyQuote();
await reserve();
const posts=postRequests();
assert.equal(posts.length,1);
assert.equal(posts[0].path,'/api/trade/order');
assert.deepEqual(JSON.parse(posts[0].request.body),{
  quote_id:'quote-1',customer_name:'Customer',po_reference:'PO-001',
  terms_accepted:true,allocation_authorized:true
});
assert.equal(state.order.id,'order-1');
assert.equal(state.quote,null);
assert.equal(el('reserve-button').disabled,true);
assert.ok(requests.some(row=>row.path==='/api/trade/options'));
assert.ok(requests.some(row=>row.path.startsWith('/api/trade/orders?')));
assert.match(el('status').textContent,/No external purchase or payment/);
readyQuote({...clone(quote),supply:{...quote.supply,takeover_requires_ack:false,mode:'uncommitted'}});
el('allocation_authorized').checked=false;
await reserve();
assert.ok(!('allocation_authorized' in JSON.parse(postRequests()[1].request.body)));
""")


def test_zero_availability_nonreservable_quote_keeps_useful_basis_and_amounts():
    run_trade_script("""
const unavailable={...clone(quote),reservable:false,supply:{...quote.supply,available_units:0},warnings:['No available quota.']};
responder=async(path,request)=>path==='/api/trade/quote'?reply({quote:unavailable}):standardResponse(path,request);
await quoteNow();
assert.equal(state.quote.reservable,false);
assert.equal(el('reserve-button').disabled,true);
assert.equal(el('reservation-inputs').disabled,true);
assert.ok(el('quote-summary').innerHTML.includes('<dd>0</dd>'));
assert.ok(el('quote-summary').innerHTML.includes('No available quota.'));
for (const basis of ['Merchant guild (wholesale)','Merchant buyback (reference only; not wholesale)',
  'Producer gate','Modeled delivered wholesale reference','Retail','not surveyed stock',
  'not added demand','one 4,000 lb horse wagon','hired mixed-mode route',
  'Carriage cost basis','Projected profit (estimate)','not recorded cash']) {
  assert.ok(el('quote-summary').innerHTML.includes(basis),basis);
}
await reserve();
assert.equal(postRequests().length,1,'no reservation call for a nonreservable quote');
""")


def test_carried_inventory_claim_scope_and_lifetime_are_visible():
    run_trade_script("""
const q=clone(quote);
q.supply.mode='uncommitted';
q.supply.claim_scope='carried_inventory';
q.supply.flow_basis='daily inventory window';
readyQuote(q);
assert.ok(el('quote-summary').innerHTML.includes('Carried inventory across dates'));
assert.ok(el('quote-summary').innerHTML.includes('daily inventory window'));
assert.ok(el('quote-summary').innerHTML.includes('persist across dates and after delivery'));
assert.ok(el('quote-summary').innerHTML.includes('only cancellation releases them'));
""")


def test_untrusted_quote_order_options_and_audit_text_is_escaped():
    run_trade_script("""
const evil='<img src=x onerror="alert(1)"> & \\' <script>evil</script>';
const safe=esc(evil);
assert.equal(safe,'&lt;img src=x onerror=&quot;alert(1)&quot;&gt; &amp; &#39; &lt;script&gt;evil&lt;/script&gt;');
const q=clone(quote);
q.id=evil; q.origin.name=evil; q.destination.name=evil; q.commodity.name=evil; q.commodity.unit=evil;
q.shipping.path=[evil]; q.shipping.carrier=evil; q.shipping.basis=evil; q.supply.basis=evil;
q.terms.acceptance_terms=evil; q.terms.tax_exemption_reason=evil; q.assumptions=[evil]; q.warnings=[evil];
const rendered=renderQuote(q);
assert.ok(rendered.includes(safe));
assert.ok(!rendered.includes('<img')); assert.ok(!rendered.includes('<script>'));
const o=makeOrder();
o.id=evil; o.po_reference=evil; o.customer_name=evil; o.status=evil; o.quote=q;
o.payments=[{kind:evil,amount_gp:10,reference:evil,simulation_date:evil,created_at:evil}];
o.audit=[{action:evil,simulation_date:evil,created_at:evil,details:{note:evil}}];
o.balance.warnings=[evil];
state.orders=[o]; state.total=1; renderOrders(); setOrder(o);
for (const id of ['order-list','order-detail']) {
  assert.ok(el(id).innerHTML.includes(safe),id);
  assert.ok(!el(id).innerHTML.includes('<img'),id);
  assert.ok(!el(id).innerHTML.includes('<script>'),id);
}
assert.ok(!el('order-detail').innerHTML.includes('<input'),'saved quote is read-only');
populateSelect('origin',[{id:evil,name:evil}]);
assert.ok(el('origin').innerHTML.includes('value="'+safe+'"'));
assert.ok(!el('origin').innerHTML.includes('<img'));
updateOptions({...options,assumptions:[evil]});
assert.ok(el('trade-assumptions').innerHTML.includes(safe));
""")


def test_missing_balances_are_not_rendered_as_zero_and_capabilities_fail_closed():
    run_trade_script("""
const o=makeOrder(); o.balance={};
setOrder(o);
assert.ok(el('order-detail').innerHTML.includes('<dd>Not provided</dd>'));
assert.equal(money(null),'Not provided');
assert.equal(money(undefined),'Not provided');
assert.equal(money(''),'Not provided');
assert.equal(money('0'),'Not provided');
assert.equal(money(0),'0.00 gp');
assert.equal(el('dispatch-button').disabled,true);
assert.equal(el('deliver-button').disabled,true);
assert.equal(el('cancel-button').disabled,true);
await changeStatus('dispatch');
assert.equal(postRequests().length,0);
assert.match(el('status').textContent,/not currently available/);
""")


@pytest.mark.parametrize(
    "kind", ["customer_payment", "customer_refund", "supplier_payment", "supplier_refund", "expense"],
    ids=["customer-pay", "customer-refund", "supplier-pay", "supplier-refund", "expense"],
)
def test_each_manual_payment_intent_is_explicit_and_records_only_once(kind):
    run_trade_script(
        "const kind=" + json.dumps(kind) + ";\n"
        + """
setOrder(makeOrder()); readyQuote();
el('payment_kind').value=kind; el('payment_amount').value='12.5'; el('payment_reference').value='cash-unique-001';
await recordPayment();
assert.equal(postRequests().length,0);
assert.match(el('status').textContent,/Confirm that this cash movement/);
el('payment_confirmed').checked=true;
let finish;
responder=async(path,request)=>path==='/api/trade/payment'?new Promise(resolve=>finish=resolve):standardResponse(path,request);
const pending=recordPayment();
assert.equal(el('payment-inputs').disabled,true);
assert.equal(el('action-inputs').disabled,true);
await recordPayment();
assert.equal(postRequests().length,1);
const request=postRequests()[0];
assert.equal(request.path,'/api/trade/payment');
assert.equal(request.request.headers['Content-Type'],'application/json');
assert.deepEqual(JSON.parse(request.request.body),{order_id:'order-1',kind,amount_gp:12.5,reference:'cash-unique-001'});
finish(reply({order:makeOrder()})); await pending;
assert.equal(el('payment_confirmed').checked,false);
assert.equal(el('payment_amount').value,'');
assert.equal(el('payment_reference').value,'');
assert.equal(state.quote,null);
assert.match(el('status').textContent,/No money was transferred/);
assert.ok(el('order-detail').innerHTML.includes('Recorded cash (not profit)'));
assert.ok(el('order-detail').innerHTML.includes('Projected profit (estimate)'));
"""
    )


@pytest.mark.parametrize(
    ("amount", "reference"), [("", "ref"), ("0", "ref"), ("-5", "ref"), ("NaN", "ref"), ("5", " ")],
    ids=["blank", "zero", "negative", "nan", "reference"],
)
def test_invalid_manual_cash_entries_are_not_sent(amount, reference):
    run_trade_script(
        f"""
setOrder(makeOrder());
el('payment_kind').value='expense';
el('payment_amount').value={json.dumps(amount)};
el('payment_reference').value={json.dumps(reference)};
el('payment_confirmed').checked=true;
await recordPayment();
assert.equal(postRequests().length,0);
assert.equal(el('status').className,'status error');
"""
    )


@pytest.mark.parametrize("action", ["dispatch", "deliver", "cancel"], ids=["dispatch", "deliver", "cancel"])
def test_status_intents_send_version_acceptance_and_never_advance_time(action):
    run_trade_script(
        "const action=" + json.dumps(action) + ";\n"
        + """
const o=makeOrder();
o.balance.can_dispatch=true; o.balance.can_deliver=true; o.balance.can_cancel=true;
setOrder(o); readyQuote();
if (action==='deliver' || action==='cancel') {
  await changeStatus(action);
  assert.equal(postRequests().length,0,'explicit acceptance or cancellation confirmation required');
}
el('delivery_accepted').checked=true;
el('cancel_confirmed').checked=true;
await changeStatus(action);
assert.equal(postRequests().length,1);
const posted=postRequests()[0];
assert.equal(posted.path,'/api/trade/status');
const expected={order_id:'order-1',action,version:7};
if (action==='deliver') expected.accepted=true;
assert.deepEqual(JSON.parse(posted.request.body),expected);
assert.ok(requests.every(row=>row.path.startsWith('/api/trade/')));
assert.equal(state.quote,null);
assert.equal(el('delivery_accepted').checked,false);
assert.equal(el('cancel_confirmed').checked,false);
assert.match(el('status').textContent,/world clock was not advanced/);
"""
    )


@pytest.mark.parametrize(
    ("operation", "path"),
    [("quote", "/api/trade/quote"), ("reserve", "/api/trade/order"),
     ("payment", "/api/trade/payment"), ("dispatch", "/api/trade/status")],
    ids=["quote", "reserve", "payment", "status"],
)
def test_server_rejections_show_error_without_optimistic_success(operation, path):
    run_trade_script(
        f"const operation={json.dumps(operation)}, path={json.dumps(path)};\n"
        + """
const o=makeOrder(); setOrder(o); readyQuote();
el('payment_kind').value='customer_refund'; el('payment_amount').value='99';
el('payment_reference').value='retry-this-reference'; el('payment_confirmed').checked=true;
const failure='<expired> insufficient allocation or refund exceeds paid amount';
responder=async(requestPath,request)=>requestPath===path?reply({error:failure},false,409):standardResponse(requestPath,request);
if (operation==='quote') await quoteNow();
else if (operation==='reserve') await reserve();
else if (operation==='payment') await recordPayment();
else await changeStatus('dispatch');
assert.equal(el('status').textContent,failure,'server error is plain text');
assert.equal(el('status').className,'status error');
assert.equal(state.order.version,7);
assert.equal(state.order.status,'reserved');
assert.equal(state.order.balance.customer_paid_gp,2000);
assert.equal(state.busy,false);
assert.equal(postRequests().length,1);
if (operation==='payment') {
  assert.equal(el('payment_reference').value,'retry-this-reference','retain idempotency reference for retry');
  assert.equal(el('payment_amount').value,'99');
}
if (operation==='reserve' || operation==='quote') assert.equal(state.quote,null);
"""
    )


def test_network_failure_and_successful_write_followed_by_refresh_failure_are_distinct():
    run_trade_script("""
responder=async()=>{throw new Error('Offline');};
await quoteNow();
assert.equal(el('status').textContent,'Offline');
assert.equal(el('reserve-button').disabled,true);
readyQuote();
responder=async(path,request)=>{
  if (path==='/api/trade/order') return reply({order:makeOrder()});
  throw new Error('Options temporarily unavailable');
};
await reserve();
assert.equal(state.order.id,'order-1');
assert.equal(state.quote,null);
assert.match(el('status').textContent,/Purchase order reserved/);
assert.match(el('status').textContent,/Refresh failed/);
assert.equal(el('status').className,'status error');
responder=async()=>({ok:false,status:500,json:async()=>{throw new Error('not json');}});
await quoteNow();
assert.match(el('status').textContent,/unreadable response/);
assert.equal(state.quote,null);
""")


def test_order_paging_detail_fetch_and_world_refresh_preserve_user_terms():
    run_trade_script("""
responder=async(path,request)=>{
  if (path.startsWith('/api/trade/orders?')) {
    const offset=Number(new URL('http://test'+path).searchParams.get('offset'));
    return reply({orders:offset===0?[makeOrder()]:[{...makeOrder(),id:'order-51'}],total:51,offset,limit:50});
  }
  return standardResponse(path,request);
};
await pageOrders(0);
assert.equal(el('next-orders').disabled,false);
assert.equal(el('previous-orders').disabled,true);
await pageOrders(50);
assert.equal(el('next-orders').disabled,true);
assert.equal(el('previous-orders').disabled,false);
assert.equal(el('order-page').textContent,'Orders 51–51 of 51');
await openOrder('order / "?');
assert.ok(requests.some(row=>row.path==='/api/trade/order?id=order%20%2F%20%22%3F'));
assert.equal(el('order-detail-section').hidden,false);
readyQuote();
el('supply_date').value='1492-04-01';
el('acceptance_terms').value='Keep my chosen terms';
responder=async(path,request)=>path==='/api/trade/options'
  ?reply({...options,date:{iso:'1492-03-15',label:'15 Ches 1492 DR'}}):standardResponse(path,request);
await refreshDesk();
assert.equal(state.quote,null);
assert.equal(el('supply_date').value,'1492-04-01');
assert.equal(el('acceptance_terms').value,'Keep my chosen terms');
assert.match(el('trade-date').textContent,/1492-03-15/);
assert.ok(requests.every(row=>row.path.startsWith('/api/trade/')));
""")


def test_refresh_recovers_initial_options_failure_and_disabled_trade():
    run_trade_script("""
state.initialized=false;
state.enabled=false;
state.options=null;
el('origin').value=''; el('quantity').value='';
responder=async()=>{throw new Error('Options unavailable');};
await startTrade();
assert.equal(el('quote-inputs').disabled,true);
responder=standardResponse;
await refreshDesk();
assert.equal(state.initialized,true);
assert.equal(el('origin').value,'berdusk');
assert.equal(el('quantity').value,'1000');
assert.equal(el('quote-inputs').disabled,false);
updateOptions({...options,enabled:false});
syncControls();
assert.equal(el('quote-inputs').disabled,true);
assert.equal(el('reserve-button').disabled,true);
assert.equal(el('payment-inputs').disabled,true);
assert.equal(el('dispatch-button').disabled,true);
""")
