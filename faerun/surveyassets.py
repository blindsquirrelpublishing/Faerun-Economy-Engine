"""City-map evidence layers, kept separate from generated building scenarios."""

SURVEY_CSS = """
.survey-layer {
  position: absolute; inset: 0; width: 768px; height: 1536px;
  pointer-events: none; overflow: hidden;
}
.survey-layer[hidden] { display: none; }
.survey-feature { vector-effect: non-scaling-stroke; cursor: pointer; }
.survey-street {
  fill: none; stroke: #007da8; stroke-width: 1.3; stroke-opacity: .8;
  stroke-linecap: round; stroke-linejoin: round; pointer-events: stroke;
}
.survey-roof {
  fill: rgba(220, 135, 25, .25); stroke: #9c5c00; stroke-width: .55;
  pointer-events: visiblePainted;
}
.survey-feature.selected { stroke: #de2156; stroke-width: 3; stroke-opacity: 1; }
.survey-feature.selected.survey-roof { fill: rgba(222, 33, 86, .4); }
.survey-label-anchor { fill: #007da8; stroke: white; stroke-width: .8; pointer-events: all; }
.survey-boundary { fill: none; stroke: #1f8060; stroke-width: 1; stroke-dasharray: 5 3; }
.measuring .survey-feature { pointer-events: none; }
.survey-switches { display: flex; gap: 12px; flex-wrap: wrap; margin: 12px 0; }
.survey-switches label { display: flex; align-items: center; gap: 5px; font-size: 13px; }
#street-search { display: flex; gap: 5px; margin: 12px 0; }
#street-query { min-width: 0; flex: 1; }
#street-results { max-height: 220px; overflow-y: auto; list-style: none; padding: 0; }
#street-results button { width: 100%; text-align: left; margin: 2px 0; }
#city-survey pre { white-space: pre-wrap; overflow-wrap: anywhere; font-size: 11px; max-height: 300px; overflow-y: auto; }
#survey-selection { border-left: 3px solid var(--cp-accent); padding-left: 10px; }
#city-survey .survey-status { font-size: 12px; }
"""

SURVEY_JS = r"""
(function () {
  'use strict';
  var ns = 'http://www.w3.org/2000/svg';
  var reports = {streets:null, roofs:null};
  var pending = {streets:null, roofs:null};
  var nodes = {streets:new Map(), roofs:new Map()};
  var selected = null;
  var endpoints = {streets:'/api/streets?settlement=Waterdeep', roofs:'/api/census/hires?settlement=Waterdeep'};
  var viewport = document.getElementById('viewport');

  function element(id) { return document.getElementById(id); }

  function geometryPath(geometry) {
    function line(points, closed) {
      return points.map(function (point, index) {
        return (index ? 'L' : 'M') + point[0] + ',' + point[1];
      }).join(' ') + (closed ? ' Z' : '');
    }
    if (geometry.type === 'LineString') { return line(geometry.coordinates, false); }
    if (geometry.type === 'MultiLineString') {
      return geometry.coordinates.map(function (points) { return line(points, false); }).join(' ');
    }
    if (geometry.type === 'Polygon') {
      return geometry.coordinates.map(function (points) { return line(points, true); }).join(' ');
    }
    if (geometry.type === 'MultiPolygon') {
      return geometry.coordinates.map(function (polygon) {
        return polygon.map(function (points) { return line(points, true); }).join(' ');
      }).join(' ');
    }
    throw new Error('Unsupported survey path geometry: ' + geometry.type);
  }

  function geometryPoints(geometry) {
    if (geometry.type === 'Point') { return [geometry.coordinates]; }
    if (geometry.type === 'LineString') { return geometry.coordinates; }
    if (geometry.type === 'MultiLineString' || geometry.type === 'Polygon') {
      return geometry.coordinates.flat();
    }
    if (geometry.type === 'MultiPolygon') { return geometry.coordinates.flat(2); }
    throw new Error('Unsupported survey geometry: ' + geometry.type);
  }

  function validateReport(report) {
    if (!report || !Array.isArray(report.features) || !report.coverage ||
        !Array.isArray(report.limitations) || !report.coordinate_space ||
        report.coordinate_space.width !== 3560 || report.coordinate_space.height !== 7256 ||
        report.coordinate_space.units !== 'image_pixels' || report.coordinate_space.origin !== 'top_left') {
      throw new Error('Invalid map survey or incompatible image coordinates');
    }
    var ids = new Set();
    report.features.forEach(function (feature) {
      if (typeof feature.id !== 'string' || !feature.id || ids.has(feature.id) ||
          !feature.geometry || !feature.properties) {
        throw new Error('Invalid or duplicate map feature');
      }
      ids.add(feature.id);
      var points = geometryPoints(feature.geometry);
      if (!points.length || points.some(function (point) {
        return !Array.isArray(point) || point.length !== 2 ||
          !Number.isFinite(point[0]) || !Number.isFinite(point[1]) ||
          point[0] < 0 || point[0] > 3560 || point[1] < 0 || point[1] > 7256;
      })) { throw new Error('Map geometry lies outside the source image'); }
    });
    return report;
  }

  function featureName(feature, kind) {
    return feature.properties.name || (kind === 'streets' ? 'Unnamed segment ' : 'Roof record ') + feature.id;
  }

  function renderLayer(kind, report) {
    var layer = element('survey-' + kind + '-layer');
    var fragment = document.createDocumentFragment();
    nodes[kind].clear();
    report.features.forEach(function (feature) {
      var point = feature.geometry.type === 'Point';
      var node = document.createElementNS(ns, point ? 'circle' : 'path');
      if (point) {
        node.setAttribute('cx', feature.geometry.coordinates[0]);
        node.setAttribute('cy', feature.geometry.coordinates[1]);
        node.setAttribute('r', 7);
      } else {
        node.setAttribute('d', geometryPath(feature.geometry));
        node.setAttribute('fill-rule', 'evenodd');
      }
      node.setAttribute('class', 'survey-feature ' +
        (kind === 'streets' ? 'survey-street' : 'survey-roof') + (point ? ' survey-label-anchor' : ''));
      node.dataset.featureId = feature.id;
      node.dataset.layer = kind;
      var title = document.createElementNS(ns, 'title');
      title.textContent = featureName(feature, kind) + ' | ' + (feature.properties.status || 'See evidence');
      node.appendChild(title);
      fragment.appendChild(node);
      nodes[kind].set(feature.id, node);
    });
    layer.replaceChildren(fragment);
    layer.toggleAttribute('hidden', !element('survey-show-' + kind).checked);
    if (kind === 'roofs' && report.boundary) {
      var boundary = document.createElementNS(ns, 'path');
      boundary.setAttribute('class', 'survey-boundary');
      boundary.setAttribute('d', geometryPath(report.boundary));
      element('survey-boundary-layer').replaceChildren(boundary);
    }
  }

  function renderMetadata(kind, report) {
    var summary = {};
    Object.keys(report).forEach(function (key) {
      if (key !== 'features' && key !== 'boundary') { summary[key] = report[key]; }
    });
    element('survey-' + kind + '-metadata').textContent = JSON.stringify(summary, null, 2);
    if (kind === 'streets') {
      var names = report.features.filter(function (feature) { return Boolean(feature.properties.name); })
        .map(function (feature) { return feature.properties.name; });
      element('survey-streets-status').textContent = report.features.length.toLocaleString() +
        ' street-layer segments; ' + names.length.toLocaleString() + ' local name associations (' +
        new Set(names).size.toLocaleString() + ' distinct names). ' +
        (report.coverage.geometric_complete && report.coverage.naming_complete
          ? 'Source reports complete geometry and naming.'
          : 'Street geometry and naming are NOT fully verified or complete.') +
        ' Points mark labels only, not traced roads.';
      var calibration = report.source && report.source.distance_scale;
      element('survey-scale-status').textContent = calibration &&
          calibration.coordinate_transform && calibration.coordinate_transform.verified
        ? 'External map calibration: ' + calibration.source_claim +
          ' (AideDD; raster alignment checked). This does not verify building footprints or occupancy.'
        : 'No registered external map calibration supplied.';
    } else {
      element('survey-roofs-status').textContent = report.features.length.toLocaleString() +
        ' roof candidates, not verified building identities. Complete visual enumeration is not established.';
      var estimate = report.estimate;
      if (estimate && Number.isFinite(estimate.value)) {
        element('survey-estimate').textContent = 'Estimated depicted roof structures: ' +
          Math.round(estimate.value).toLocaleString();
        var interval = estimate.sampling_interval;
        var sensitivity = estimate.interpretation_sensitivity;
        element('survey-estimate-uncertainty').textContent =
          (interval ? 'Approximate sampling-only ' + Math.round(interval.nominal_confidence_level * 100) +
            '% interval: ' + Math.round(interval.lower).toLocaleString() + ' - ' +
            Math.round(interval.upper).toLocaleString() + '. ' : '') +
          (sensitivity ? 'Roof-interpretation sensitivity: ' + Math.round(sensitivity.lower).toLocaleString() +
            ' - ' + Math.round(sensitivity.upper).toLocaleString() + ' (not confidence bounds). ' : '') +
          'This estimates map roof symbols, not residents. Sampling uncertainty excludes observer bias, hidden roofs and boundary errors.';
      } else {
        element('survey-estimate').textContent = 'No citywide structure estimate supplied';
        element('survey-estimate-uncertainty').textContent = 'Unknown does not mean zero. Active resident population is unchanged.';
      }
    }
    element('survey-' + kind + '-download').disabled = false;
  }

  function loadLayer(kind) {
    if (reports[kind]) { return Promise.resolve(reports[kind]); }
    if (pending[kind]) { return pending[kind]; }
    element('survey-' + kind + '-status').textContent = 'Loading ' + kind + ' evidence...';
    pending[kind] = fetch(endpoints[kind]).then(function (response) {
      if (!response.ok) { throw new Error('Request failed (' + response.status + ')'); }
      return response.json();
    }).then(validateReport).then(function (report) {
      renderLayer(kind, report);
      renderMetadata(kind, report);
      reports[kind] = report;
      if (kind === 'streets') { renderStreetResults(); }
      return report;
    }).finally(function () { pending[kind] = null; });
    return pending[kind];
  }

  function showFailure(kind, error) {
    element('survey-' + kind + '-status').textContent = 'Could not load ' + kind + ': ' + error.message;
    element('survey-' + kind + '-download').disabled = true;
    element('survey-' + kind + '-metadata').textContent = '';
    element('survey-' + kind + '-layer').replaceChildren();
    if (selected && Array.from(nodes[kind].values()).includes(selected)) {
      selected = null;
      element('survey-selection').hidden = true;
    }
    nodes[kind].clear();
    reports[kind] = null;
    if (kind === 'streets') {
      element('street-results').replaceChildren();
      element('street-result-count').textContent = 'Street search unavailable until the layer loads.';
      element('survey-scale-status').textContent = '';
    } else {
      element('survey-boundary-layer').replaceChildren();
      element('survey-estimate').textContent = 'Structure estimate unavailable';
      element('survey-estimate-uncertainty').textContent = '';
    }
  }

  function selectFeature(kind, id, focus) {
    var feature = reports[kind].features.find(function (item) { return item.id === id; });
    if (!feature) { throw new Error('Selected survey feature was not found'); }
    if (selected) { selected.classList.remove('selected'); }
    selected = nodes[kind].get(id);
    selected.classList.add('selected');
    element('survey-show-' + kind).checked = true;
    element('survey-' + kind + '-layer').removeAttribute('hidden');
    element('survey-selection').hidden = false;
    element('survey-feature-name').textContent = featureName(feature, kind);
    element('survey-feature-details').textContent = JSON.stringify({
      id:feature.id, geometry_type:feature.geometry.type, evidence:feature.properties
    }, null, 2);
    if (focus) {
      var points = geometryPoints(feature.geometry);
      var bounds = points.reduce(function (box, point) {
        return [Math.min(box[0], point[0]), Math.min(box[1], point[1]),
          Math.max(box[2], point[0]), Math.max(box[3], point[1])];
      }, [Infinity, Infinity, -Infinity, -Infinity]);
      var x = (bounds[0] + bounds[2]) / 2;
      var y = (bounds[1] + bounds[3]) / 2;
      window.dispatchEvent(new CustomEvent('waterdeep-focus-point', {
        detail:{x:x * 768 / 3560, y:y * 1536 / 7256}
      }));
    }
    var url = new URL(location.href);
    url.searchParams.delete('street');
    url.searchParams.delete('roof');
    url.searchParams.set(kind === 'streets' ? 'street' : 'roof', id);
    url.hash = 'city-survey';
    history.replaceState(null, '', url);
  }

  function matchingStreets(query) {
    var wanted = query.trim().toLowerCase();
    return reports.streets.features.filter(function (feature) {
      return !wanted || featureName(feature, 'streets').toLowerCase().includes(wanted) ||
        feature.id.toLowerCase().includes(wanted);
    }).sort(function (a, b) {
      return featureName(a, 'streets').localeCompare(featureName(b, 'streets'));
    });
  }

  function renderStreetResults() {
    var matches = matchingStreets(element('street-query').value);
    var list = element('street-results');
    list.replaceChildren();
    element('street-result-count').textContent = matches.length.toLocaleString() +
      ' matching street records' + (matches.length > 100 ? '; showing the first 100. Refine the search.' : '.');
    matches.slice(0, 100).forEach(function (feature) {
      var item = document.createElement('li');
      var button = document.createElement('button');
      button.type = 'button';
      button.textContent = featureName(feature, 'streets') +
        (feature.geometry.type === 'Point' ? ' (label only)' : '');
      button.addEventListener('click', function () { selectFeature('streets', feature.id, true); });
      item.appendChild(button);
      list.appendChild(item);
    });
  }

  function searchStreet(query) {
    element('street-query').value = query;
    return loadLayer('streets').then(function () {
      renderStreetResults();
      var matches = matchingStreets(query);
      var exact = matches.find(function (feature) {
        return featureName(feature, 'streets').toLowerCase() === query.trim().toLowerCase() ||
          feature.id.toLowerCase() === query.trim().toLowerCase();
      });
      if (exact || matches.length === 1) { selectFeature('streets', (exact || matches[0]).id, true); }
      element('city-survey').scrollIntoView({block:'nearest'});
    }).catch(function (error) { showFailure('streets', error); });
  }

  function loadAll() {
    element('survey-load').disabled = true;
    return Promise.all(['streets', 'roofs'].map(function (kind) {
      return loadLayer(kind).catch(function (error) { showFailure(kind, error); });
    })).finally(function () { element('survey-load').disabled = false; });
  }

  ['streets', 'roofs'].forEach(function (kind) {
    element('survey-show-' + kind).addEventListener('change', function () {
      if (this.checked) {
        loadLayer(kind).then(function () {
          element('survey-' + kind + '-layer').toggleAttribute('hidden', !element('survey-show-' + kind).checked);
        }).catch(function (error) { showFailure(kind, error); });
      } else { element('survey-' + kind + '-layer').setAttribute('hidden', ''); }
    });
    element('survey-' + kind + '-download').addEventListener('click', function () {
      var url = URL.createObjectURL(new Blob([JSON.stringify(reports[kind], null, 2)], {type:'application/json'}));
      var link = document.createElement('a');
      link.href = url;
      link.download = 'waterdeep-' + kind + '-survey.json';
      link.click();
      setTimeout(function () { URL.revokeObjectURL(url); }, 1000);
    });
  });
  element('survey-show-boundary').addEventListener('change', function () {
    element('survey-boundary-layer').toggleAttribute('hidden', !this.checked);
  });
  element('survey-load').addEventListener('click', loadAll);
  element('street-search').addEventListener('submit', function (event) {
    event.preventDefault();
    searchStreet(element('street-query').value);
  });
  element('street-query').addEventListener('input', function () {
    if (reports.streets) { renderStreetResults(); }
  });

  // The atlas captures pointers for panning; select a feature only after a stationary gesture.
  var pressed = null;
  viewport.addEventListener('pointerdown', function (event) {
    var target = event.target.closest('.survey-feature');
    pressed = target && event.button === 0 && !event.shiftKey && !viewport.classList.contains('measuring')
      ? {target:target, x:event.clientX, y:event.clientY, pointer:event.pointerId, moved:false} : null;
  });
  viewport.addEventListener('pointermove', function (event) {
    if (pressed && pressed.pointer === event.pointerId &&
        Math.hypot(event.clientX - pressed.x, event.clientY - pressed.y) >= 4) {
      pressed.moved = true;
    }
  });
  viewport.addEventListener('pointerup', function (event) {
    if (pressed && !pressed.moved && pressed.pointer === event.pointerId &&
        Math.hypot(event.clientX - pressed.x, event.clientY - pressed.y) < 4) {
      selectFeature(pressed.target.dataset.layer, pressed.target.dataset.featureId, false);
    }
    pressed = null;
  });
  viewport.addEventListener('pointercancel', function () { pressed = null; });

  window.WaterdeepSurvey = {searchStreet:searchStreet};
  var params = new URLSearchParams(location.search);
  if (params.has('street') || params.has('roof')) {
    var kind = params.has('street') ? 'streets' : 'roofs';
    var id = params.get(kind === 'streets' ? 'street' : 'roof');
    loadLayer(kind).then(function () { selectFeature(kind, id, true); })
      .catch(function (error) { showFailure(kind, error); });
  } else if (location.hash === '#city-survey' || location.hash === '#housing-census') { loadAll(); }
}());
"""
