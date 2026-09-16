"""City System generation controls; kept separate from surveyed map evidence."""

BUILDING_GENERATOR_JS = r"""
(function () {
  'use strict';
  var form = document.getElementById('building-generator-form');
  var status = document.getElementById('building-generator-status');
  var results = document.getElementById('building-generator-results');
  var download = document.getElementById('building-generator-download');
  var fields = ['ward', 'count', 'seed', 'building_class', 'footprint_sqft', 'scenario'];
  var snapshot = null, controller = null, initialPending = true;
  var initial = new URLSearchParams(location.search);
  fields.forEach(function (field) {
    var value = initial.get('building-' + field);
    if (value !== null) { document.getElementById('building-' + field).value = value; }
  });

  function element(tag, text) {
    var node = document.createElement(tag);
    if (text !== undefined) { node.textContent = text; }
    return node;
  }
  function render(data) {
    document.getElementById('building-generator-source').textContent =
      data.source.title + ' (' + data.source.publication_year + '). ' + data.source.era_note +
      ' Rules: printed pp. 10-11 / PDF pp. 11-12.';
    var notes = document.getElementById('building-generator-assumptions');
    notes.replaceChildren();
    data.assumptions.forEach(function (text) { notes.appendChild(element('li', text)); });
    results.replaceChildren();
    data.buildings.forEach(function (row) {
      var card = element('details');
      card.className = 'directory-entry';
      card.appendChild(element('summary', row.label + ' - ' +
        (row.building_class ? 'Class ' + row.building_class + ' / ' + row.use.label : 'Unresolved source roll')));
      card.appendChild(element('p', 'Generated scenario; not a mapped or canonical building.'));
      card.appendChild(element('p', 'Assumed footprint: ' + row.assumed_footprint_sqft + ' sq ft.'));
      if (row.structure) {
        card.appendChild(element('p', row.structure.stories + ' stories; ' +
          (row.structure.basement ? 'with basement' : 'no basement') + '; ' + row.condition + '.'));
        var people = row.occupants;
        card.appendChild(element('p', 'Modeled residents: ' + people.residents +
          '; lodging guests: ' + people.lodging_guests + '; staff: ' + people.staff +
          '. Staff may also be residents; these counts are not additive.'));
        Object.keys(people.staff_roles).forEach(function (role) {
          card.appendChild(element('p', role + ': ' + people.staff_roles[role]));
        });
      }
      row.warnings.forEach(function (text) { card.appendChild(element('p', text)); });
      var evidence = element('details');
      evidence.appendChild(element('summary', 'Source dice and modeled occupant breakdown'));
      evidence.appendChild(element('pre', JSON.stringify({id: row.id, rolls: row.rolls,
        occupants: row.occupants, citations: row.citations}, null, 2)));
      card.appendChild(evidence);
      results.appendChild(card);
    });
    var summary = data.summary;
    status.textContent = summary.resolved_buildings + ' resolved / ' + summary.buildings +
      ' generated; ' + summary.unresolved_buildings + ' unresolved. Resolved buildings only: ' +
      summary.modeled_residents_in_resolved_buildings + ' modeled residents, ' +
      summary.modeled_guests_in_resolved_buildings + ' lodging guests and ' +
      summary.modeled_staff_in_resolved_buildings + ' staff (may overlap residents). No census or live population changes.';
  }

  async function generate() {
    if (controller) { controller.abort(); }
    var request = new AbortController();
    controller = request;
    snapshot = null; download.disabled = true;
    status.textContent = 'Generating a separate building scenario...';
    status.classList.remove('directory-error');
    results.replaceChildren();
    var params = new URLSearchParams();
    fields.forEach(function (field) {
      var value = initialPending && initial.has('building-' + field)
        ? initial.get('building-' + field) : document.getElementById('building-' + field).value;
      if (value !== '') { params.set(field, value); }
    });
    initialPending = false;
    try {
      var response = await fetch('/api/generated-buildings?' + params, {signal: request.signal});
      var data = await response.json();
      if (!response.ok) { throw new Error(data.error || 'Building generation failed (' + response.status + ')'); }
      if (controller !== request || request.signal.aborted) { return; }
      fields.forEach(function (field) {
        document.getElementById('building-' + field).value = data.parameters[field] === null ? '' : data.parameters[field];
      });
      render(data);
      snapshot = data; download.disabled = false;
      var url = new URL(location.href);
      fields.forEach(function (field) {
        var value = params.get(field);
        if (value !== null) { url.searchParams.set('building-' + field, value); }
        else { url.searchParams.delete('building-' + field); }
      });
      url.hash = 'building-generator';
      history.replaceState(null, '', url);
    } catch (error) {
      if (error.name === 'AbortError' || request.signal.aborted || controller !== request) { return; }
      status.textContent = 'Could not generate buildings: ' + error.message;
      status.classList.add('directory-error');
    }
  }
  form.addEventListener('submit', function (event) { event.preventDefault(); generate(); });
  form.addEventListener('input', function () {
    if (controller) { controller.abort(); }
    snapshot = null; download.disabled = true;
    results.replaceChildren();
    status.textContent = 'Settings changed. Generate to update this scenario.';
  });
  download.addEventListener('click', function () {
    if (!snapshot) { status.textContent = 'Generate a scenario before downloading.'; return; }
    var url = URL.createObjectURL(new Blob([JSON.stringify(snapshot, null, 2)], {type: 'application/json'}));
    var link = element('a'); link.href = url; link.download = 'waterdeep-generated-buildings.json';
    link.click();
    setTimeout(function () { URL.revokeObjectURL(url); }, 1000);
  });
  if (fields.some(function (field) { return initial.has('building-' + field); })) { generate(); }
}());
"""
