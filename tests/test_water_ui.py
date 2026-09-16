from faerun.locationassets import LOCATION_HTML
from test_requirements_ui import run_location_script


def test_water_panel_uses_gallons_and_hides_the_misleading_reference():
    assert 'id="requirements-water-section"' in LOCATION_HTML
    run_location_script("""
const data = requirements();
data.water = {
  unit:'gallon', status:'routine_gap', evidence:'inferred <not measured>',
  total_person_days:100, usable_gallons_per_day:500,
  total_demand_gallons_per_day:600, total_delivered_gallons_per_day:450,
  municipal_capacity_gallons_per_day:200, municipal_delivered_gallons_per_day:200,
  household_capacity_gallons_per_day:250, household_delivered_gallons_per_day:250,
  essential_demand_gallons_per_day:150, essential_gap_gallons_per_day:0,
  routine_gap_gallons_per_day:150, source_gap_gallons_per_day:100,
  access_gap_gallons_per_day:50, operations_gap_gallons_per_day:0,
  unused_usable_gallons_per_day:50, assumptions:['Sources are <estimated>'],
  sources:[{name:'Well <assumed>',raw_gallons_per_day:600,usable_gallons_per_day:500,basis:'Not surveyed'}]
};
data.profile.service_requirements = [
  {scope:'municipal_water_reference',name:'Old water gap',unit:'gallon',required_per_day:600,local_capacity_per_day:200,unmet_per_day:400},
  {scope:'municipal_service_reference',name:'Waste collection',unit:'lb',required_per_day:400,local_capacity_per_day:400,unmet_per_day:0}
];
ui.state.detail = detail('Town', 100, data);
ui.renderRequirements(data);
assert.equal(ui.el['requirements-water-section'].hidden, false);
const html = ui.el['requirements-water'].innerHTML;
assert.ok(html.includes('Essential needs covered'));
assert.ok(html.includes('gallons / day'));
assert.ok(!html.includes('US gallon'));
assert.ok(!html.includes('litres'));
assert.ok(html.includes('Well &lt;assumed&gt;'));
assert.ok(html.includes('inferred &lt;not measured&gt;'));
assert.ok(html.includes('one finite usable-water pool'));
assert.ok(!ui.el['requirements-services'].innerHTML.includes('Old water gap'));
assert.ok(ui.el['requirements-services'].innerHTML.includes('Waste collection'));
delete data.water;
ui.renderRequirements(data);
assert.equal(ui.el['requirements-water-section'].hidden, true);
assert.equal(ui.el['requirements-water'].innerHTML, '');
assert.ok(ui.el['requirements-services'].innerHTML.includes('Old water gap'));
""")
