import json
import subprocess

from faerun.buildingassets import BUILDING_GENERATOR_JS
from faerun.buildinggen import generate_buildings
from faerun.waterdeepassets import WATERDEEP_ASSETS, WATERDEEP_HTML
from test_city_directory_ui import HARNESS


def run_generator_script(body, setup=""):
    defaults = r"""
node('building-ward').value = 'Trades Ward';
node('building-count').value = '20';
node('building-seed').value = '1357';
node('building-building_class').value = '';
node('building-footprint_sqft').value = '1000';
node('building-scenario').value = 'central';
"""
    sample = "const generated = " + json.dumps(generate_buildings(count=2)) + ";"
    script = HARNESS + defaults + sample + setup + BUILDING_GENERATOR_JS
    script += "\n(async () => {\n" + body
    script += "\n})().catch(error => { console.error(error); process.exitCode = 1; });"
    result = subprocess.run(
        ["node", "-"], input=script, text=True, encoding="utf-8",
        capture_output=True, timeout=20,
    )
    assert result.returncode == 0, result.stdout + result.stderr


def test_generator_controls_and_separate_evidence_labels():
    for field in ("ward", "count", "seed", "building_class", "footprint_sqft", "scenario"):
        assert f'id="building-{field}"' in WATERDEEP_HTML
    assert "building-generator.js" in WATERDEEP_ASSETS
    assert "Generated, not surveyed" in WATERDEEP_HTML
    assert "No invented names" in WATERDEEP_HTML
    assert 'max="100"' in WATERDEEP_HTML
    assert "innerHTML" not in BUILDING_GENERATOR_JS


def test_generator_load_render_export_and_invalidation():
    run_generator_script(r"""
assert.equal(requests.length, 0, 'generation is opt-in, unlike the historical directory');
node('building-count').value = '2';
node('building-generator-form').listeners.submit({preventDefault() {}});
assert.ok(requests[0].url.includes('/api/generated-buildings?'));
assert.ok(requests[0].url.includes('count=2'));
await respond(requests[0], generated);
assert.equal(node('building-generator-results').children.length, 2);
assert.ok(node('building-generator-status').textContent.includes('No census or live population changes'));
assert.ok(node('building-generator-source').textContent.includes('printed pp. 10-11'));
assert.equal(node('building-generator-download').disabled, false);
assert.equal(location.hash, '#building-generator');
assert.ok(location.search.includes('scoutTheme=dark'));
node('building-generator-download').click();
assert.deepEqual(JSON.parse(await downloads[0].text()), generated);
node('building-count').value = '3';
node('building-generator-form').listeners.input();
assert.equal(node('building-generator-download').disabled, true);
assert.equal(node('building-generator-results').children.length, 0);
""")


def test_generator_failure_retry_and_out_of_order_response():
    run_generator_script(r"""
node('building-generator-form').listeners.submit({preventDefault() {}});
await respond(requests[0], {error: 'Invalid class'}, false);
assert.ok(node('building-generator-status').textContent.includes('Invalid class'));
assert.equal(node('building-generator-download').disabled, true);
node('building-generator-form').listeners.submit({preventDefault() {}});
node('building-generator-form').listeners.submit({preventDefault() {}});
await respond(requests[2], generated);
await respond(requests[1], {error: 'Stale failure'}, false);
assert.equal(node('building-generator-results').children.length, 2);
assert.equal(node('building-generator-download').disabled, false);
assert.ok(!node('building-generator-status').textContent.includes('Stale failure'));
""")


def test_generator_url_passes_raw_invalid_class_for_validation():
    run_generator_script(r"""
assert.equal(requests.length, 1);
assert.ok(requests[0].url.includes('building_class=A'));
await respond(requests[0], {error: 'Class A requires individual authoring'}, false);
assert.ok(node('building-generator-status').textContent.includes('Class A'));
assert.equal(node('building-generator-download').disabled, true);
""", setup="globalThis.location = new URL('http://localhost/waterdeep.html?building-building_class=A');")


def test_generator_unresolved_south_records_are_visible_without_zero_occupants():
    south = generate_buildings("Southern Ward", count=100)
    unresolved = next(row for row in south["buildings"] if row["occupants"] is None)
    south["buildings"] = [unresolved]
    run_generator_script(r"""
node('building-generator-form').listeners.submit({preventDefault() {}});
await respond(requests[0], southern);
const card = node('building-generator-results').children[0];
assert.ok(card.children[0].textContent.includes('Unresolved source roll'));
assert.ok(card.children.some(child => child.textContent.includes('No reroll')));
assert.ok(!card.children.some(child => child.textContent.includes('Modeled residents: 0')));
""", setup="const southern = " + json.dumps(south) + ";")
