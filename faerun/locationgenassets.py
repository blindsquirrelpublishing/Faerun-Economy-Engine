"""Standalone City System location scenarios, separate from live and source data."""

LOCATION_GENERATOR_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Faerun Location Generator</title>
<link rel="stylesheet" href="location-generator.css">
<script src="location-generator.js" defer></script>
</head>
<body>
<header>
  <p class="eyebrow">Faerun Economy Engine / City System</p>
  <h1>Location generator</h1>
  <nav aria-label="Main navigation">
    <a href="index.html">Commodity board / home</a>
    <a href="map.html">World map</a>
    <a href="waterdeep.html">Waterdeep atlas</a>
  </nav>
</header>
<main>
  <section class="notice" aria-labelledby="scope-title">
    <h2 id="scope-title">Generated, not surveyed</h2>
    <p>Generate ordinary buildings for <strong>any named location</strong>, including your own.
      The name is a user-supplied label, not a verified identification or lore claim.</p>
    <p>Settlement profiles are <strong>engine assumptions, not source facts</strong> for that destination.
      City System building rules are adapted from Waterdeep; applying them elsewhere is a modeling choice.</p>
    <p><strong>No invented names.</strong> No named occupants, automatic population fitting, or changes to the
      live economy, population, census, or lore. Modeled residents, lodging guests, and staff are separate
      counts; staff may overlap residents and these counts are not additive.</p>
    <p>The fortress profile models supporting ordinary buildings only. It excludes a unique keep,
      fortifications, and the garrison.</p>
  </section>
  <section aria-labelledby="settings-title">
    <h2 id="settings-title">Scenario settings</h2>
    <p id="defaults">Defaults: town profile, 20 buildings, seed 1357, 1,000 sq ft per building, central
      occupancy scenario. The class mix and condition modifier come from the profile catalog below.</p>
    <form id="location-generator-form" novalidate aria-describedby="defaults">
      <div class="fields">
        <label for="location-location">Location name (required, up to 120 characters)
          <input id="location-location" name="location" type="text" required maxlength="120"
            placeholder="Neverwinter, a village, or your own location" autocomplete="off">
        </label>
        <label for="location-profile">Settlement profile (assumption)
          <select id="location-profile" name="profile">
            <option value="village">Village</option><option value="town" selected>Town</option>
            <option value="city">City</option><option value="port">Port</option>
            <option value="fortress">Fortress</option>
          </select>
        </label>
        <label for="location-count">Buildings (1&ndash;100)
          <input id="location-count" name="count" type="number" min="1" max="100" step="1" value="20" required>
        </label>
        <label for="location-seed">Seed (0&ndash;4294967295)
          <input id="location-seed" name="seed" type="number" min="0" max="4294967295" step="1" value="1357" required>
        </label>
        <label for="location-footprint_sqft">Assumed footprint per building (1&ndash;1,000,000 sq ft)
          <input id="location-footprint_sqft" name="footprint_sqft" type="number"
            min="1" max="1000000" step="1" value="1000" required>
        </label>
        <label for="location-scenario">Occupancy scenario (assumption)
          <select id="location-scenario" name="scenario">
            <option value="low">Low</option><option value="central" selected>Central</option>
            <option value="high">High</option>
          </select>
        </label>
      </div>
      <aside class="notice" aria-labelledby="profile-title">
        <h3 id="profile-title">Selected profile defaults (engine assumptions)</h3>
        <p id="location-profile-defaults" role="status" aria-live="polite">Loading profile catalog...</p>
        <button id="location-profiles-retry" type="button" hidden>Retry profile catalog</button>
      </aside>
      <details id="location-advanced">
        <summary>Advanced assumption overrides</summary>
        <p>Custom B/C/D percentages must all be supplied as integers from 0 to 100 and sum to 100.
          Blank condition modifier uses the selected profile default.</p>
        <label class="check" for="location-custom-mix">
          <input id="location-custom-mix" type="checkbox">Use custom class percentages
        </label>
        <fieldset id="location-mix-fields" disabled hidden>
          <legend>Custom ordinary-building mix (not source facts)</legend>
          <div class="fields">
            <label for="location-class_b_weight">Class B (%)
              <input id="location-class_b_weight" name="class_b_weight" type="number" min="0" max="100" step="1">
            </label>
            <label for="location-class_c_weight">Class C (%)
              <input id="location-class_c_weight" name="class_c_weight" type="number" min="0" max="100" step="1">
            </label>
            <label for="location-class_d_weight">Class D (%)
              <input id="location-class_d_weight" name="class_d_weight" type="number" min="0" max="100" step="1">
            </label>
          </div>
        </fieldset>
        <label for="location-condition_modifier">Condition modifier override (integer &minus;1, 0, or 1; optional)
          <input id="location-condition_modifier" name="condition_modifier" type="number" min="-1" max="1" step="1"
            placeholder="Use profile default">
        </label>
      </details>
      <p>Generate explicitly after changing settings. A successful result URL pins the effective mix and
        modifier so it can be reopened and reproduced. Invalid settings are reported by the API.</p>
      <div class="actions">
        <button type="submit">Generate location scenario</button>
        <button id="location-generator-download" type="button" disabled>Download scenario JSON</button>
      </div>
    </form>
  </section>
  <p id="location-generator-status" role="status" aria-live="polite">Choose a location and generate a separate scenario.</p>
  <section id="location-generator-output" aria-busy="false" aria-labelledby="result-title" hidden>
    <h2 id="result-title">Generated scenario</h2>
    <p id="location-generator-summary"></p>
    <p id="location-generator-effective"></p>
    <h3>Assumptions and scope</h3>
    <ul id="location-generator-assumptions"></ul>
    <h3>Source provenance</h3>
    <p id="location-generator-source"></p>
    <details><summary>Full source and occupancy assumptions</summary><pre id="location-generator-provenance"></pre></details>
    <div class="table-scroll" role="region" tabindex="0" aria-label="Generated buildings">
      <table>
        <caption>Generated ordinary buildings &mdash; not mapped, surveyed, or canonical records</caption>
        <thead><tr>
          <th scope="col">Building / evidence</th><th scope="col">Class / use</th>
          <th scope="col">Structure / condition</th><th scope="col">Modeled residents</th>
          <th scope="col">Lodging guests</th><th scope="col">Staff (may overlap)</th>
        </tr></thead>
        <tbody id="location-generator-results"></tbody>
      </table>
    </div>
  </section>
</main>
</body>
</html>
"""

LOCATION_GENERATOR_CSS = """
:root { color-scheme: light dark; font-family: system-ui, sans-serif; line-height: 1.55;
  --paper: #f7f3e9; --ink: #262e34; --panel: #fffcf4; --line: #a9a28f; --accent: #245e70; }
* { box-sizing: border-box; }
body { margin: 0; background: var(--paper); color: var(--ink); }
header, main { width: min(1120px, 100%); margin: auto; padding: 1.5rem; }
header { padding-bottom: 0; }
h1 { margin: 0 0 .6rem; }
h2, h3 { line-height: 1.25; }
.eyebrow { font-size: .85rem; letter-spacing: .05em; }
nav, .actions { display: flex; flex-wrap: wrap; gap: .8rem 1.5rem; }
a { color: var(--accent); }
section { margin-bottom: 1.5rem; }
.notice, details { padding: 1rem; border: 1px solid var(--line); border-radius: .4rem;
  background: var(--panel); margin: 1rem 0; }
.notice h2, .notice h3 { margin-top: 0; }
.notice p:last-child { margin-bottom: 0; }
.fields { display: grid; grid-template-columns: repeat(auto-fit, minmax(min(100%, 260px), 1fr)); gap: 1rem; }
label { display: flex; flex-direction: column; gap: .3rem; }
input, select, button { font: inherit; color: inherit; background: var(--panel);
  border: 1px solid var(--line); border-radius: .25rem; padding: .6rem; min-height: 44px; }
input, select { width: 100%; }
input[type=checkbox] { width: 1.2rem; min-height: 1.2rem; }
.check { flex-direction: row; align-items: center; gap: .6rem; }
button, summary { cursor: pointer; }
button[type=submit] { background: var(--accent); color: white; border-color: var(--accent); }
button:disabled { opacity: .55; cursor: not-allowed; }
fieldset { border: 1px solid var(--line); margin: 1rem 0; min-width: 0; }
summary { font-weight: 600; overflow-wrap: anywhere; }
:focus-visible { outline: 3px solid var(--accent); outline-offset: 3px; }
[hidden] { display: none !important; }
.error { color: #a1261d; font-weight: 600; }
#location-generator-status { padding: .8rem 0; }
.table-scroll { overflow: auto; }
table { border-collapse: collapse; width: 100%; }
caption { text-align: left; font-weight: 600; padding: .7rem 0; }
th, td { text-align: left; vertical-align: top; border-bottom: 1px solid var(--line); padding: .7rem; }
th { background: var(--panel); }
td:first-child { min-width: 220px; max-width: 400px; }
pre { white-space: pre-wrap; overflow-wrap: anywhere; font-size: .85rem; }
p, li { overflow-wrap: anywhere; }
@media (max-width: 600px) {
  header, main { padding: 1rem; }
  .actions { flex-direction: column; }
}
@media (prefers-color-scheme: dark) {
  :root { --paper: #162127; --ink: #ecede8; --panel: #202f36; --line: #73818a; --accent: #93d7e4; }
  button[type=submit] { color: #162127; }
  .error { color: #ffb3a9; }
}
"""

LOCATION_GENERATOR_JS = r"""
(function () {
  'use strict';
  var baseFields = ['location', 'profile', 'count', 'seed', 'footprint_sqft', 'scenario'];
  var weightFields = ['class_b_weight', 'class_c_weight', 'class_d_weight'];
  var fields = baseFields.concat(weightFields, ['condition_modifier']);
  var controls = {}, initialRaw = Object.create(null);
  var initial = new URLSearchParams(location.search);
  var form = document.getElementById('location-generator-form');
  var status = document.getElementById('location-generator-status');
  var output = document.getElementById('location-generator-output');
  var results = document.getElementById('location-generator-results');
  var download = document.getElementById('location-generator-download');
  var mix = document.getElementById('location-custom-mix');
  var mixFields = document.getElementById('location-mix-fields');
  var defaults = document.getElementById('location-profile-defaults');
  var retry = document.getElementById('location-profiles-retry');
  var profiles = [], profileController = null, controller = null, snapshot = null;

  function element(tag, text) {
    var node = document.createElement(tag);
    if (text !== undefined) { node.textContent = text; }
    return node;
  }
  function setValue(field, value) {
    var control = controls[field];
    if ((field === 'profile' || field === 'scenario') &&
        !Array.from(control.options).some(function (option) { return option.value === String(value); })) {
      control.add(new Option('Unsupported value: ' + value, value));
    }
    control.value = value;
  }
  fields.forEach(function (field) {
    controls[field] = document.getElementById('location-' + field);
    if (initial.has(field)) {
      initialRaw[field] = initial.get(field);
      setValue(field, initialRaw[field]);
    }
    ['input', 'change'].forEach(function (eventName) {
      controls[field].addEventListener(eventName, function () { delete initialRaw[field]; });
    });
  });
  mix.checked = weightFields.some(function (field) { return initial.has(field); });
  document.getElementById('location-advanced').open = mix.checked || initial.has('condition_modifier');
  function syncMix() { mixFields.disabled = !mix.checked; mixFields.hidden = !mix.checked; }
  syncMix();
  download.disabled = true;

  function currentValue(field) {
    return Object.prototype.hasOwnProperty.call(initialRaw, field) ? initialRaw[field] : controls[field].value;
  }
  function selectedProfile() {
    return profiles.find(function (profile) { return profile.id === currentValue('profile'); });
  }
  function mixText(profile) {
    return 'Class B: ' + profile.class_weights.B + '%, C: ' + profile.class_weights.C +
      '%, D: ' + profile.class_weights.D + '%; condition modifier: ' + profile.condition_modifier + '.';
  }
  function showDefaults() {
    var profile = selectedProfile();
    defaults.textContent = profile
      ? profile.name + ' — ' + profile.description + ' Profile defaults (engine assumptions): ' + mixText(profile)
      : profiles.length
        ? 'Unsupported profile: ' + currentValue('profile') + '. Choose a profile or submit to see the API validation error.'
        : 'Profile defaults unavailable until the catalog loads. No percentages or modifier have been assumed here.';
    if (profile && !mix.checked) {
      weightFields.forEach(function (field, index) {
        controls[field].value = profile.class_weights[['B', 'C', 'D'][index]];
      });
    }
  }
  async function loadProfiles() {
    if (profileController) { profileController.abort(); }
    var request = new AbortController();
    profileController = request;
    retry.hidden = true;
    defaults.textContent = 'Loading profile catalog...';
    try {
      var response = await fetch('/api/location-profiles', {signal: request.signal});
      var data = await response.json();
      if (!response.ok) { throw new Error(data.error || 'Profile catalog request failed (' + response.status + ')'); }
      if (request !== profileController || request.signal.aborted) { return; }
      profiles = data.profiles;
      showDefaults();
    } catch (error) {
      if (request !== profileController || request.signal.aborted || error.name === 'AbortError') { return; }
      defaults.textContent = 'Could not load profile defaults: ' + error.message +
        '. Retry the catalog or generate using server-validated settings; no default percentages are guessed.';
      retry.hidden = false;
    }
  }
  retry.addEventListener('click', loadProfiles);

  function invalidate(message) {
    if (controller) { controller.abort(); }
    controller = null;
    snapshot = null;
    download.disabled = true;
    output.hidden = true;
    output.setAttribute('aria-busy', 'false');
    results.replaceChildren();
    ['summary', 'effective', 'source', 'provenance'].forEach(function (name) {
      document.getElementById('location-generator-' + name).textContent = '';
    });
    document.getElementById('location-generator-assumptions').replaceChildren();
    status.classList.remove('error');
    status.textContent = message;
  }
  function changed() {
    syncMix();
    showDefaults();
    invalidate('Settings changed. Generate to update this separate scenario.');
  }
  form.addEventListener('input', changed);
  form.addEventListener('change', changed);
  mix.addEventListener('change', function () {
    weightFields.forEach(function (field) { delete initialRaw[field]; });
    syncMix();
  });

  function render(data) {
    document.getElementById('result-title').textContent = data.location.name + ' — generated scenario';
    var summary = data.summary;
    document.getElementById('location-generator-summary').textContent =
      summary.resolved_buildings + ' resolved / ' + summary.buildings + ' generated buildings; ' +
      summary.unresolved_buildings + ' unresolved. Generated classes: ' +
      Object.keys(summary.classes).map(function (key) { return key + ': ' + summary.classes[key]; }).join(', ') +
      '. Resolved buildings only: ' + summary.modeled_residents_in_resolved_buildings +
      ' modeled residents; ' + summary.modeled_guests_in_resolved_buildings + ' lodging guests; ' +
      summary.modeled_staff_in_resolved_buildings + ' staff (may overlap residents; not additive). ' +
      'City population: not estimated. No live economy, population, census, or lore changes.';
    document.getElementById('location-generator-effective').textContent =
      'Effective profile: ' + data.profile.name + ' (engine assumptions, not destination source facts). ' +
      mixText(data.profile) + ' Occupancy scenario: ' + data.parameters.scenario +
      '; seed: ' + data.parameters.seed + '; assumed footprint: ' + data.parameters.footprint_sqft + ' sq ft per building.';
    var assumptions = document.getElementById('location-generator-assumptions');
    assumptions.replaceChildren();
    data.assumptions.forEach(function (note) { assumptions.appendChild(element('li', note)); });
    document.getElementById('location-generator-source').textContent =
      data.source.title + ' (' + data.source.publication_year + '). ' + data.source.era_note +
      ' Building rules: printed pp. 10–11 / PDF pp. 11–12. Individual citations and dice appear with each building.';
    document.getElementById('location-generator-provenance').textContent =
      JSON.stringify({source: data.source, occupancy_scenario: data.occupancy_scenario}, null, 2);
    results.replaceChildren();
    data.buildings.forEach(function (building) {
      var row = element('tr');
      var identity = element('td');
      identity.appendChild(element('strong', building.label));
      identity.appendChild(element('p', 'Generated scenario; profile-assumed class. Not mapped or surveyed.'));
      var evidence = element('details');
      evidence.appendChild(element('summary', 'Dice, occupant breakdown, and source citations'));
      evidence.appendChild(element('pre', JSON.stringify({id: building.id, rolls: building.rolls,
        occupants: building.occupants, citations: building.citations}, null, 2)));
      identity.appendChild(evidence);
      (building.warnings || []).forEach(function (warning) { identity.appendChild(element('p', warning)); });
      row.appendChild(identity);
      row.appendChild(element('td', building.building_class && building.use
        ? 'Class ' + building.building_class + ' / ' + building.use.label : 'Unresolved source roll'));
      var structure = building.structure;
      row.appendChild(element('td', structure
        ? structure.stories + ' stories; ' + (structure.basement ? 'with basement' : 'no basement') +
          (structure.tower_or_partial_upper ? '; tower or partial upper floor' : '') + '; ' + building.condition +
          '. Assumed footprint: ' + building.assumed_footprint_sqft + ' sq ft.'
        : 'Unresolved; assumed footprint: ' + building.assumed_footprint_sqft + ' sq ft.'));
      ['residents', 'lodging_guests', 'staff'].forEach(function (key) {
        var value = building.occupants && building.occupants[key];
        row.appendChild(element('td', value === null || value === undefined ? 'Unknown' : String(value)));
      });
      results.appendChild(row);
    });
    output.hidden = false;
    status.textContent = 'Generated ' + summary.buildings + ' buildings for ' + data.location.name +
      '. Separate scenario ready; no live data changed.';
  }
  async function generate() {
    invalidate('Generating a separate location scenario...');
    var request = new AbortController();
    controller = request;
    output.setAttribute('aria-busy', 'true');
    var params = new URLSearchParams();
    baseFields.forEach(function (field) { params.set(field, currentValue(field)); });
    if (mix.checked) {
      weightFields.forEach(function (field) { params.set(field, currentValue(field)); });
    }
    if (currentValue('condition_modifier') !== '' ||
        Object.prototype.hasOwnProperty.call(initialRaw, 'condition_modifier')) {
      params.set('condition_modifier', currentValue('condition_modifier'));
    }
    try {
      var response = await fetch('/api/generated-location?' + params, {signal: request.signal});
      var data = await response.json();
      if (!response.ok) { throw new Error(data.error || 'Location generation failed (' + response.status + ')'); }
      if (controller !== request || request.signal.aborted) { return; }
      render(data);
      var url = new URL(location.href);
      fields.forEach(function (field) {
        var value = data.parameters[field];
        if (value === null || value === undefined) { url.searchParams.delete(field); value = ''; }
        else { url.searchParams.set(field, value); }
        setValue(field, value);
      });
      initialRaw = Object.create(null);
      mix.checked = true;
      syncMix();
      showDefaults();
      history.replaceState(null, '', url);
      snapshot = data;
      download.disabled = false;
    } catch (error) {
      if (controller !== request || request.signal.aborted || error.name === 'AbortError') { return; }
      invalidate('Could not generate location: ' + error.message);
      status.classList.add('error');
    } finally {
      if (controller === request) { output.setAttribute('aria-busy', 'false'); }
    }
  }
  form.addEventListener('submit', function (event) { event.preventDefault(); generate(); });
  download.addEventListener('click', function () {
    if (!snapshot) { status.textContent = 'Generate a scenario before downloading.'; return; }
    var url = URL.createObjectURL(new Blob([JSON.stringify(snapshot, null, 2)], {type: 'application/json'}));
    var link = element('a');
    link.href = url;
    link.download = 'generated-location.json';
    link.click();
    setTimeout(function () { URL.revokeObjectURL(url); }, 1000);
  });
  loadProfiles();
}());
"""

LOCATION_GENERATOR_ASSETS = {
    "location-generator.html": (LOCATION_GENERATOR_HTML, "text/html; charset=utf-8"),
    "location-generator.css": (LOCATION_GENERATOR_CSS, "text/css; charset=utf-8"),
    "location-generator.js": (LOCATION_GENERATOR_JS, "application/javascript; charset=utf-8"),
}
