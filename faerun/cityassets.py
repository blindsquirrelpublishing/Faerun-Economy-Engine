"""Historical directory browser embedded in the Waterdeep atlas."""

WATERDEEP_DIRECTORY_JS = r"""
(function () {
  'use strict';
  var form = document.getElementById('directory-form');
  var search = document.getElementById('directory-search');
  var ward = document.getElementById('directory-ward');
  var kind = document.getElementById('directory-kind');
  var category = document.getElementById('directory-category');
  var status = document.getElementById('directory-status');
  var results = document.getElementById('directory-results');
  var download = document.getElementById('directory-download');
  var snapshot = null, controller = null, timer = null, facetsLoaded = false, initialRequest = true;
  var initial = new URLSearchParams(location.search);
  var controls = {search: search, ward: ward, kind: kind, category: category};

  function element(tag, text, className) {
    var node = document.createElement(tag);
    if (text !== undefined) { node.textContent = text; }
    if (className) { node.className = className; }
    return node;
  }

  function citations(rows) {
    return 'Source pages: ' + rows.map(function (c) {
      return 'p. ' + c.printed_page + ' (PDF page ' + c.pdf_page + ')';
    }).join('; ') + '.';
  }

  function relatedLink(id, name, recordKind) {
    var button = element('button', name, 'directory-link');
    button.type = 'button';
    button.addEventListener('click', function () {
      search.value = id;
      ward.value = '';
      category.value = '';
      kind.value = recordKind;
      clearTimeout(timer);
      loadDirectory(id);
    });
    return button;
  }

  function card(record) {
    var item = element('details', undefined, 'directory-entry');
    item.id = 'directory-entry-' + record.id;
    var heading = element('summary', record.name);
    item.appendChild(heading);
    var locationLabel = record.record_kind === 'business'
      ? record.ward + ' / ' + record.category
      : 'Person / affiliations: ' + record.wards.join(', ');
    item.appendChild(element('p', locationLabel, 'directory-meta'));
    item.appendChild(element('p', record.summary));
    if (record.address) { item.appendChild(element('p', 'Address in guide: ' + record.address)); }
    if (record.services) { item.appendChild(element('p', 'Services: ' + record.services.join(', '))); }
    var links = record.record_kind === 'business' ? record.people : record.affiliations;
    item.appendChild(element('h4', record.record_kind === 'business' ? 'Associated people' : 'Business affiliations'));
    if (!links.length) { item.appendChild(element('p', 'No named people captured for this entry.')); }
    links.forEach(function (link) {
      var row = element('p');
      var personLink = record.record_kind === 'business';
      row.appendChild(relatedLink(
        personLink ? link.person_id : link.business_id,
        personLink ? link.name : link.business_name,
        personLink ? 'person' : 'business'
      ));
      row.appendChild(element('span', ' - ' + link.role));
      row.appendChild(element('small', citations(link.citations), 'directory-citation'));
      item.appendChild(row);
    });
    item.appendChild(element('p', citations(record.citations), 'directory-citation'));
    return item;
  }

  function setOptions(select, rows) {
    rows.forEach(function (row) { select.add(new Option(row.name, row.id)); });
  }

  async function loadDirectory(openId) {
    if (controller) { controller.abort(); }
    controller = new AbortController();
    var requestController = controller;
    snapshot = null;
    download.disabled = true;
    status.textContent = 'Loading historical directory...';
    status.classList.remove('directory-error');
    results.replaceChildren();
    var params = new URLSearchParams({settlement: 'Waterdeep'});
    Object.keys(controls).forEach(function (key) {
      var value = initialRequest ? initial.get('directory-' + key) || '' : controls[key].value;
      if (value) { params.set(key, value); }
    });
    initialRequest = false;
    try {
      var response = await fetch('/api/city-directory?' + params, {signal: requestController.signal});
      var data = await response.json();
      if (!response.ok) { throw new Error(data.error || 'Directory request failed (' + response.status + ')'); }
      if (requestController !== controller) { return; }
      if (!facetsLoaded) {
        setOptions(ward, data.wards);
        setOptions(category, data.categories.map(function (name) { return {id: name, name: name}; }));
        search.value = data.filters.search;
        kind.value = data.filters.kind;
        ward.value = (data.wards.find(function (row) { return row.name === data.filters.ward; }) || {}).id || '';
        category.value = data.filters.category || '';
        facetsLoaded = true;
      }
      document.getElementById('directory-source').textContent =
        data.source.title + ' (' + data.source.publication_year + '). ' + data.source.era_note;
      document.getElementById('directory-scope').textContent = data.scope_note;
      status.textContent = data.counts.businesses + ' of ' + data.totals.businesses +
        ' businesses; ' + data.counts.people + ' of ' + data.totals.people + ' people.';
      data.businesses.concat(data.people).forEach(function (record) { results.appendChild(card(record)); });
      if (!data.businesses.length && !data.people.length) {
        results.appendChild(element('p', 'No matching records. Clear filters to browse the directory.'));
      }
      var url = new URL(location.href);
      Object.keys(controls).forEach(function (key) {
        var value = controls[key].value;
        if (value && value !== 'all') { url.searchParams.set('directory-' + key, value); }
        else { url.searchParams.delete('directory-' + key); }
      });
      history.replaceState(null, '', url);
      snapshot = data;
      download.disabled = false;
      if (openId) {
        var target = document.getElementById('directory-entry-' + openId);
        if (target) {
          target.open = true;
          target.querySelector('summary').focus();
          target.scrollIntoView({block: 'nearest'});
        }
      }
    } catch (error) {
      if (error.name === 'AbortError') { return; }
      status.textContent = 'Could not load the historical directory: ' + error.message + '. Use Find to retry or Clear filters to reset.';
      status.classList.add('directory-error');
    }
  }

  form.addEventListener('submit', function (event) {
    event.preventDefault();
    clearTimeout(timer);
    loadDirectory();
  });
  search.addEventListener('input', function () {
    download.disabled = true;
    if (controller) { controller.abort(); }
    clearTimeout(timer);
    timer = setTimeout(function () { loadDirectory(); }, 200);
  });
  [ward, kind, category].forEach(function (control) {
    control.addEventListener('change', function () { clearTimeout(timer); loadDirectory(); });
  });
  document.getElementById('directory-clear').addEventListener('click', function () {
    clearTimeout(timer);
    initial = new URLSearchParams();
    search.value = ''; ward.value = ''; category.value = ''; kind.value = 'all';
    loadDirectory();
  });
  download.addEventListener('click', function () {
    if (!snapshot) { status.textContent = 'Load directory results before downloading.'; return; }
    var url = URL.createObjectURL(new Blob([JSON.stringify(snapshot, null, 2)], {type: 'application/json'}));
    var link = element('a');
    link.href = url;
    link.download = 'waterdeep-historical-directory.json';
    link.click();
    setTimeout(function () { URL.revokeObjectURL(url); }, 1000);
  });
  loadDirectory();
}());
"""
