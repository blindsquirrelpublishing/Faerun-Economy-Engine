"""Shared supplier breakdown rendering for market quotes."""

SOURCING_JS = """
function supplyNumber(value) {
  return Number(value || 0).toLocaleString(undefined, {maximumFractionDigits: 2});
}
function sourceSummary(quote) {
  if (!Array.isArray(quote.sources)) return quote.source || 'local';
  var parts = [], imports = quote.sources.filter(function(row) { return row.supply_type === 'import'; });
  var local = quote.sources.find(function(row) { return row.supply_type === 'local'; });
  if (local) parts.push('Local ' + supplyNumber(local.share * 100) + '%');
  if (imports.length) parts.push(imports.length + (imports.length === 1 ? ' supplier' : ' suppliers'));
  if (quote.unmet_demand_per_day > 0.001) parts.push('Shortfall ' + supplyNumber(quote.unmet_demand_per_day) + '/day');
  return parts.join(' + ') || 'No allocated supply';
}
function sourceBreakdown(quote) {
  if (!Array.isArray(quote.sources)) return '';
  var rows = quote.sources.map(function(row) {
    return '<tr><td><a href="location.html?settlement=' + encodeURIComponent(row.source_id) + '">' +
      esc(row.source) + '</a></td><td>' + esc(row.supply_type) + '</td><td>' +
      supplyNumber(row.quantity_per_day) + '</td><td>' + supplyNumber(row.share * 100) +
      '%</td><td>' + supplyNumber(row.days) + ' d / ' + supplyNumber(row.distance) +
      ' mi</td><td>' + supplyNumber(row.unit_cost) + ' gp</td></tr>';
  }).join('');
  var backups = quote.backup_sources || [];
  var backupRows = backups.map(function(row) {
    return '<tr><td>' + esc(row.source) + '</td><td>' + supplyNumber(row.available_per_day) +
      '</td><td>' + supplyNumber(row.days) + ' d</td><td>' + supplyNumber(row.unit_cost) + ' gp</td></tr>';
  }).join('');
  return '<details class="supply-breakdown"><summary>Daily supply: ' + esc(sourceSummary(quote)) +
    '</summary><div class="table-scroll" style="overflow-x:auto" tabindex="0" role="region" aria-label="Active suppliers">' +
    '<table><thead><tr><th>Source</th><th>Type</th><th>' + esc(quote.unit) +
    '/day</th><th>Demand share</th><th>Delivery</th><th>Unit cost</th></tr></thead><tbody>' + rows +
    '</tbody></table></div><p>Unmet demand: ' + supplyNumber(quote.unmet_demand_per_day) + ' ' + esc(quote.unit) +
    '/day · Exports: ' + supplyNumber(quote.exports_per_day) + ' ' + esc(quote.unit) + '/day</p>' + materialBreakdown(quote) +
    (backups.length ? '<details><summary>Backup suppliers (unreserved): ' + backups.length +
      '</summary><div class="table-scroll" style="overflow-x:auto" tabindex="0" role="region" aria-label="Backup suppliers">' +
      '<table><thead><tr><th>Source</th><th>Available/day</th><th>Delivery</th><th>Unit cost</th></tr></thead><tbody>' +
      backupRows + '</tbody></table></div></details>' : '') + '</details>';
}
function materialBreakdown(quote) {
  if (!quote.production_inputs?.length && !quote.processing_demand_per_day) return '';
  var inputs = (quote.production_inputs || []).map(function(row) {
    return '<tr><td><a href="product.html?commodity=' + encodeURIComponent(row.commodity) + '&settlement=' +
      encodeURIComponent(quote.settlement) + '">' + esc(row.commodity) + '</a> (' + esc(row.unit) + ')</td><td>' +
      supplyNumber(row.required_per_day) + '</td><td>' + supplyNumber(row.reserved_per_day) +
      '</td><td>' + supplyNumber(row.consumed_per_day) + '</td></tr>';
  }).join('');
  return '<h3>Daily material balance</h3><p>Output: ' + supplyNumber(quote.production_per_day) +
    ' / Capacity: ' + supplyNumber(quote.production_capacity_per_day) + ' ' + esc(quote.unit) + '/day</p>' +
    '<p>Households: ' + supplyNumber(quote.household_consumption_per_day) + ' / ' + supplyNumber(quote.household_demand_per_day) +
    ' · Processing: ' + supplyNumber(quote.processing_consumption_per_day) + ' / ' + supplyNumber(quote.processing_demand_per_day) +
    ' · Unused today: ' + supplyNumber(quote.material_closing_stock) + ' ' + esc(quote.unit) + '</p>' +
    (inputs ? '<div class="table-scroll" style="overflow-x:auto" tabindex="0" role="region" aria-label="Production inputs"><table>' +
      '<thead><tr><th>Input</th><th>Required/day</th><th>Reserved/day</th><th>Consumed/day</th></tr></thead><tbody>' +
      inputs + '</tbody></table></div>' : '');
}
"""