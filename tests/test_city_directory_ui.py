import json
import subprocess

from faerun.cityassets import WATERDEEP_DIRECTORY_JS
from test_requirements_ui import run_location_script


HARNESS = r"""
const assert = require('node:assert/strict');
const nodes = new Map(), requests = [], downloads = [];
class Element {
  constructor(tag) {
    this.tag = tag; this.textContent = ''; this.children = []; this.listeners = {};
    this.value = ''; this.disabled = false; this.open = false;
    this.classList = {add() {}, remove() {}};
  }
  addEventListener(name, callback) { this.listeners[name] = callback; }
  appendChild(node) { this.children.push(node); return node; }
  replaceChildren() { this.children = []; }
  add(option) { this.children.push(option); }
  querySelector(tag) { return this.children.find(node => node.tag === tag); }
  click() { if (this.listeners.click) this.listeners.click(); }
  focus() {}
  scrollIntoView() {}
}
function node(id) {
  if (nodes.has(id)) return nodes.get(id);
  for (const root of nodes.values()) {
    const child = root.children.find(item => item.id === id);
    if (child) return child;
  }
  const item = new Element('div'); nodes.set(id, item); return item;
}
globalThis.document = {getElementById: node, createElement: tag => new Element(tag)};
globalThis.Option = function(text, value) { this.textContent = text; this.value = value; };
globalThis.location = new URL('http://localhost/waterdeep.html?scoutTheme=dark#castle-ward');
globalThis.history = {replaceState(_state, _title, url) { globalThis.location = new URL(url); }};
globalThis.fetch = (url, options) => new Promise(resolve => { requests.push({url, options, resolve}); });
URL.createObjectURL = blob => { downloads.push(blob); return 'blob:test'; };
URL.revokeObjectURL = () => {};
node('directory-kind').value = 'all';
function payload() {
  const citation = {printed_page: 12, pdf_page: 14};
  return {
    source: {title: 'Historical guide', publication_year: 1992, era_note: 'Not current.'},
    scope_note: 'No coordinates inferred.',
    filters: {search: '', ward: null, category: null, kind: 'all'},
    wards: [{id: 'dock_ward', name: 'Dock Ward'}], categories: ['shop'],
    counts: {businesses: 1, people: 1}, totals: {businesses: 1, people: 1},
    businesses: [{id: 'shop', name: '<Test shop>', record_kind: 'business', ward: 'Dock Ward',
      category: 'shop', summary: '<Not HTML>', services: ['books'], citations: [citation],
      people: [{person_id: 'owner', name: '<Owner>', role: 'keeper', citations: [citation]}]}],
    people: [{id: 'owner', name: '<Owner>', record_kind: 'person', wards: ['Dock Ward'],
      summary: 'Historical keeper.', citations: [citation],
      affiliations: [{business_id: 'shop', business_name: '<Test shop>', role: 'keeper', citations: [citation]}]}]
  };
}
const tick = () => new Promise(resolve => setImmediate(resolve));
async function respond(request, data, ok = true) {
  request.resolve({ok, status: ok ? 200 : 400, json: async () => data});
  await tick();
}
function findButton(root) {
  for (const child of root.children) {
    if (child.tag === 'button') return child;
    const nested = findButton(child);
    if (nested) return nested;
  }
}
"""


def run_directory_script(body, setup=""):
    script = HARNESS + "\n" + setup + "\n" + WATERDEEP_DIRECTORY_JS
    script += "\n(async () => {\n" + body
    script += "\n})().catch(error => { console.error(error); process.exitCode = 1; });"
    result = subprocess.run(
        ["node", "-"], input=script, text=True, encoding="utf-8",
        capture_output=True, timeout=20,
    )
    assert result.returncode == 0, result.stdout + result.stderr


def test_directory_render_links_filters_and_json_export():
    run_directory_script(r"""
await respond(requests[0], payload());
assert.equal(node('directory-results').children.length, 2);
assert.equal(node('directory-results').children[0].children[0].textContent, '<Test shop>');
assert.equal(node('directory-results').children[0].children[2].textContent, '<Not HTML>');
assert.equal(node('directory-download').disabled, false);
assert.ok(node('directory-status').textContent.includes('1 of 1 businesses'));
assert.ok(node('directory-source').textContent.includes('Not current.'));
assert.equal(location.search, '?scoutTheme=dark');
assert.equal(location.hash, '#castle-ward');
node('directory-download').click();
assert.deepEqual(JSON.parse(await downloads[0].text()), payload());
findButton(node('directory-results').children[0]).click();
assert.equal(node('directory-search').value, 'owner');
assert.equal(node('directory-kind').value, 'person');
assert.equal(node('directory-download').disabled, true);
assert.ok(requests[1].url.includes('search=owner'));
assert.ok(requests[1].url.includes('kind=person'));
const filtered = payload();
filtered.businesses = []; filtered.counts.businesses = 0;
filtered.filters = {search: 'owner', kind: 'person', ward: null, category: null};
await respond(requests[1], filtered);
assert.equal(node('directory-entry-owner').open, true);
assert.ok(location.search.includes('directory-search=owner'));
node('directory-ward').value = 'dock_ward';
node('directory-category').value = 'shop';
node('directory-category').listeners.change();
assert.ok(requests[2].url.includes('ward=dock_ward'));
assert.ok(requests[2].url.includes('category=shop'));
node('directory-clear').click();
await respond(requests[3], payload());
assert.equal(node('directory-search').value, '');
assert.equal(node('directory-kind').value, 'all');
assert.equal(location.search, '?scoutTheme=dark');
""")


def test_directory_empty_failure_retry_and_stale_response():
    run_directory_script(r"""
await respond(requests[0], payload());
node('directory-search').value = 'no match';
node('directory-form').listeners.submit({preventDefault() {}});
const empty = payload(); empty.businesses = []; empty.people = [];
empty.counts = {businesses: 0, people: 0};
await respond(requests[1], empty);
assert.ok(node('directory-results').children[0].textContent.includes('No matching records'));
node('directory-form').listeners.submit({preventDefault() {}});
await respond(requests[2], {error: 'Unknown directory ward'}, false);
assert.equal(node('directory-download').disabled, true);
assert.equal(node('directory-results').children.length, 0);
assert.ok(node('directory-status').textContent.includes('Unknown directory ward'));
node('directory-clear').click();
node('directory-kind').value = 'person';
node('directory-kind').listeners.change();
const newest = payload(); newest.counts.businesses = 0; newest.businesses = [];
await respond(requests[4], newest);
await respond(requests[3], payload());
assert.equal(node('directory-results').children.length, 1, 'stale request must not replace latest result');
assert.equal(node('directory-download').disabled, false);
""")


def test_directory_url_filter_error_can_be_corrected_without_reload():
    run_directory_script(r"""
assert.ok(requests[0].url.includes('ward=invalid'));
await respond(requests[0], {error: 'Unknown directory ward: invalid'}, false);
node('directory-search').value = 'books';
node('directory-form').listeners.submit({preventDefault() {}});
assert.ok(!requests[1].url.includes('ward=invalid'));
assert.ok(requests[1].url.includes('search=books'));
const data = payload(); data.filters.search = 'books';
await respond(requests[1], data);
assert.equal(node('directory-search').value, 'books');
assert.equal(node('directory-ward').children.length, 1);
""", setup="globalThis.location = new URL(" + json.dumps(
        "http://localhost/waterdeep.html?directory-ward=invalid"
    ) + ");")


def test_location_link_only_shows_for_waterdeep_and_hides_on_navigation():
    run_location_script(r"""
ui.renderBusinesses({settlement_id: 'waterdeep', businesses: []});
assert.equal(element('historical-directory-link').hidden, false);
ui.renderBusinesses({settlement_id: 'baldur_s_gate', businesses: []});
assert.equal(element('historical-directory-link').hidden, true);
ui.renderBusinesses({settlement_id: 'waterdeep', businesses: []});
ui.loadSettlement('Neverwinter');
assert.equal(element('historical-directory-link').hidden, true);
""")
