import pytest

from faerun import regions
from faerun.regions import RegionError

SQUARE = [[0, 0], [10, 0], [10, 10], [0, 10]]


@pytest.fixture
def store(tmp_path, monkeypatch):
    monkeypatch.setattr(regions, "regions_path", lambda: tmp_path / "regions.json")
    monkeypatch.setattr(regions, "STORE_DIR", tmp_path)
    regions._CACHE.update(stamp=None, revision=0, regions=[])
    return tmp_path


def island(**values):
    return regions.upsert_region("Isle", {"kind": "island_nation", "borders": [SQUARE], **values})


def test_island_nation_defaults_to_ten_mile_sea_margin(store):
    assert island().sea_margin_miles == 10.0


def test_territory_is_land_plus_sea_margin(store):
    region = island()
    assert region.contains(5, 5)
    assert region.contains(15, 5)       # 5 miles off the east shore
    assert region.contains(20, 5)       # exactly the margin
    assert not region.contains(20.5, 5)
    assert region.contains(-7, -7)      # corner distance ~9.9
    assert not region.contains(-8, -8)  # corner distance ~11.3


def test_mainland_region_has_no_margin(store):
    region = regions.upsert_region("Realm", {"kind": "kingdom", "borders": [SQUARE]})
    assert region.sea_margin_miles == 0
    assert region.contains(5, 5)
    assert not region.contains(10.5, 5)


def test_region_at_prefers_land_over_a_neighbours_sea(store):
    island()
    regions.upsert_region("Next", {"kind": "kingdom", "borders": [[[12, 0], [30, 0], [30, 10], [12, 10]]]})
    assert regions.region_at(15, 5).name == "Next"
    assert regions.region_at(11, 5).name == "Isle"
    assert regions.region_at(100, 100) is None


def test_multiple_polygons_form_one_territory(store):
    region = regions.upsert_region("Chain", {"kind": "island_nation", "sea_margin_miles": 0,
                                             "borders": [SQUARE, [[50, 50], [60, 50], [60, 60], [50, 60]]]})
    assert region.contains(55, 55) and region.contains(5, 5)
    assert not region.contains(30, 30)
    assert region.land_square_miles() == 200.0


@pytest.mark.parametrize("borders,message", [
    ([[[0, 0], [1, 1]]], "between 3"),
    ([[[0, 0], [5, 5], [10, 10]]], "no area"),
    ([[[0, 0], [10, 10], [10, 0], [0, 10]]], "crosses itself"),
    ([[[0, 0], [1, "x"], [2, 2]]], "finite"),
    ([[[0, 0], [1, float("nan")], [2, 2]]], "finite"),
])
def test_invalid_polygons_are_rejected(store, borders, message):
    with pytest.raises(RegionError, match=message):
        regions.upsert_region("Bad", {"borders": borders})
    assert regions.load_regions()[1] == []


def test_closing_point_and_repeats_are_dropped(store):
    region = regions.upsert_region("Tidy", {"borders": [SQUARE + [[0, 0]]]})
    assert region.borders == [SQUARE]


def test_profile_validation(store):
    with pytest.raises(RegionError, match="kind"):
        regions.upsert_region("A", {"kind": "planet"})
    with pytest.raises(RegionError, match="trade_dependence"):
        regions.upsert_region("A", {"trade_dependence": "magic"})
    with pytest.raises(RegionError, match="Unknown commodity"):
        regions.upsert_region("A", {"exports": ["nope"]}, commodities={"grain"})
    with pytest.raises(RegionError, match="sea_margin"):
        regions.upsert_region("A", {"sea_margin_miles": 500})
    saved = regions.upsert_region("A", {"exports": ["grain"]}, commodities={"grain"})
    assert saved.exports == ["grain"]


def test_update_changes_only_given_fields_and_bumps_revision(store):
    island(summary="First", ruler="Queen")
    before = regions.regions_revision()
    regions.upsert_region("isle", {"summary": "Second"})
    region = regions.find_region("ISLE")
    assert (region.summary, region.ruler, region.borders) == ("Second", "Queen", [SQUARE])
    assert regions.regions_revision() == before + 1


def test_duplicate_names_are_refused(store):
    island()
    regions.upsert_region("Other", {})
    with pytest.raises(RegionError, match="already exists"):
        regions.upsert_region("Other", {"name": "isle"})


def test_stale_revision_is_refused(store):
    island()
    with pytest.raises(RegionError, match="changed elsewhere"):
        regions.upsert_region("Isle", {"summary": "x"}, revision=regions.regions_revision() - 1)


def test_map_border_save_replaces_polygons_and_marks_manual(store):
    island()
    body = {"id": "isle", "borders": [[[0, 0], [20, 0], [20, 20]]], "seaMarginMiles": 4,
            "revision": regions.regions_revision()}
    payload = regions.save_region_border(body)
    entry = payload["regionBorders"][0]
    assert entry["seaMarginMiles"] == 4 and entry["source"] == "manual"
    assert payload["regionRevision"] == body["revision"] + 1
    with pytest.raises(RegionError, match="changed elsewhere"):
        regions.save_region_border(body)


def test_map_border_save_creates_profile_only_for_known_labels(store):
    revision = regions.regions_revision()
    with pytest.raises(RegionError, match="Unknown region"):
        regions.save_region_border({"id": "Atlantis", "borders": [SQUARE], "revision": revision}, labels=["Amn"])
    regions.save_region_border({"id": "Amn", "borders": [SQUARE], "revision": revision}, labels=["Amn"])
    assert regions.find_region("amn").borders == [SQUARE]


def test_delete_region(store):
    island()
    assert regions.delete_region("isle") is True
    assert regions.delete_region("isle") is False


def test_aliases_match_settlement_labels(store):
    regions.upsert_region("Sea of Swords", {"aliases": ["Swordmeet Isles"]})
    assert regions.region_for_label("swordmeet isles").name == "Sea of Swords"


class Market:
    def __init__(self, id, name, region, x, y, population=100):
        self.id, self.name, self.region, self.x, self.y, self.population = id, name, region, x, y, population


class FakeWorld:
    def __init__(self, *markets):
        self.settlements = {m.id: m for m in markets}

    @property
    def regions(self):
        return sorted({m.region for m in self.settlements.values()})


def test_describe_reports_border_and_label_mismatches(store):
    island()
    world = FakeWorld(Market("a", "Alpha", "Isle", 5, 5), Market("b", "Bravo", "Isle", 500, 500),
                      Market("c", "Charlie", "Elsewhere", 14, 5))
    report = regions.describe_region(world, "isle")
    assert report["settlements"] == ["Alpha", "Bravo"]
    assert report["labelled_outside_border"] == ["Bravo"]
    assert report["inside_border_not_labelled"] == ["Charlie"]
    with pytest.raises(KeyError):
        regions.describe_region(world, "nowhere")


def test_region_rows_include_profiles_and_unlabelled_regions(store):
    island()
    world = FakeWorld(Market("a", "Alpha", "Isle", 5, 5), Market("c", "Charlie", "Elsewhere", 14, 5))
    rows = {row["region"]: row for row in regions.region_rows(world)}
    assert rows["Isle"]["profile"]["has_border"] is True
    assert rows["Elsewhere"]["profile"] is None
    regions.upsert_region("Empty", {})
    assert any(row["region"] == "Empty" and row["markets"] == 0 for row in regions.region_rows(world))


def stairs(width, height, step):
    ring, x = [[0.0, 0.0]], 0.0
    while x < width:
        ring += [[x + step, 0.0 if len(ring) % 2 else 0.5]]
        x += step
    return ring + [[width, height], [0.0, height]]


def test_smoothing_removes_jitter_and_keeps_area_and_shape():
    from faerun.territory import smooth_ring

    ring = []
    for i in range(0, 60, 5):
        ring.append([i, 0 if (i // 5) % 2 else 2.5])
    ring += [[60, 30], [0, 30]]
    smoothed = smooth_ring(ring, 8)
    assert not regions.ring_self_intersects(smoothed)
    assert abs(regions.ring_area(smoothed) - regions.ring_area(ring)) / regions.ring_area(ring) < 0.02
    zig = [p for p in ring if 10 <= p[0] <= 50 and p[1] < 8]
    assert all(regions.distance_to_ring(x, y, smoothed) < 2.0 for x, y in zig)
    assert len(smoothed) < len(ring)


def test_smoothing_leaves_degenerate_input_alone():
    from faerun.territory import smooth_ring

    assert smooth_ring(SQUARE, 0) == [[float(a), float(b)] for a, b in SQUARE]
    tiny = [[0, 0], [0.5, 0], [0, 0.5]]
    assert smooth_ring(tiny, 30) == [[0.0, 0.0], [0.5, 0.0], [0.0, 0.5]]


def test_smooth_endpoint_validates_input(store):
    with pytest.raises(RegionError, match="Smoothing"):
        regions.smooth_region_borders({"borders": [SQUARE], "strengthMiles": 0})
    with pytest.raises(RegionError, match="crosses itself"):
        regions.smooth_region_borders({"borders": [[[0, 0], [10, 10], [10, 0], [0, 10]]], "strengthMiles": 5})
    result = regions.smooth_region_borders({"borders": [[[0, 0], [60, 0], [60, 40], [0, 40]]], "strengthMiles": 5})
    assert len(result["borders"]) == 1 and len(result["borders"][0]) >= 3


def bounds(rings):
    xs = [p[0] for ring in rings for p in ring]
    return min(xs), max(xs)


def test_lone_island_territory_reaches_ten_miles_from_the_coast(store):
    regions.upsert_region("Alone", {"kind": "island_nation", "borders": [[[0, 0], [30, 0], [30, 30], [0, 30]]]})
    low, high = bounds(regions.region_territories()["alone"])
    assert -12.5 < low < -7.5 and 37.5 < high < 42.5


def test_neighbouring_island_territories_meet_at_the_midpoint(store):
    regions.upsert_region("West", {"kind": "island_nation", "borders": [[[0, 0], [30, 0], [30, 30], [0, 30]]]})
    regions.upsert_region("East", {"kind": "island_nation", "borders": [[[42, 0], [72, 0], [72, 30], [42, 30]]]})
    territories = regions.region_territories()
    west_high = bounds(territories["west"])[1]
    east_low = bounds(territories["east"])[0]
    assert 34 < west_high < 38 and 34 < east_low < 38     # midpoint of the 12-mile channel is x=36
    assert abs(west_high - east_low) < 3                    # no overlap and no gap beyond smoothing
    assert regions.region_at(33, 15).name == "West" and regions.region_at(39, 15).name == "East"
    assert regions.region_at(36.5, 100) is None


def test_land_is_never_taken_by_a_neighbours_margin(store):
    regions.upsert_region("Isle", {"kind": "island_nation", "borders": [SQUARE]})
    regions.upsert_region("Shore", {"kind": "kingdom", "borders": [[[12, -50], [200, -50], [200, 50], [12, 50]]]})
    isle_high = bounds(regions.region_territories()["isle"])[1]
    assert isle_high <= 13
    assert regions.region_at(11, 5).name == "Isle" and regions.region_at(13, 5).name == "Shore"


def test_map_payload_carries_territories(store):
    island()
    entry = regions.map_region_payload()["regionBorders"][0]
    assert entry["territory"] and entry["borders"] == [SQUARE]


def test_new_region_can_be_created_from_the_map(store):
    revision = regions.regions_revision()
    body = {"id": "Nelanther Isles", "create": True, "kind": "island_nation", "revision": revision,
            "borders": [SQUARE]}
    payload = regions.save_region_border(body, labels=["Amn"])
    entry = payload["regionBorders"][0]
    assert (entry["name"], entry["kind"], entry["seaMarginMiles"], entry["source"]) == (
        "Nelanther Isles", "island_nation", 10.0, "manual")
    with pytest.raises(RegionError, match="already exists"):
        regions.save_region_border({**body, "revision": payload["regionRevision"]}, labels=["Amn"])
    with pytest.raises(RegionError, match="already exists"):
        regions.save_region_border({"id": "amn", "create": True, "revision": payload["regionRevision"],
                                    "borders": [SQUARE]}, labels=["Amn"])


def test_smooth_endpoint_reports_what_moved(store):
    ragged = [[0, 0], [5, 2], [10, 0], [15, 2], [20, 0], [25, 2], [30, 0], [30, 30], [0, 30]]
    result = regions.smooth_region_borders({"borders": [ragged, SQUARE], "strengthMiles": 10})
    first, second = result["reports"]
    assert first["changed"] and first["maxShiftMiles"] > 0.3
    assert (second["pointsBefore"], len(result["borders"])) == (4, 2)


def test_polygon_names_follow_their_polygons(store):
    other = [[50, 0], [60, 0], [60, 10], [50, 10]]
    region = regions.upsert_region("Chain", {"kind": "island_nation", "borders": [SQUARE, other],
                                             "border_names": ["Alaron", "Gwynneth"]})
    assert region.polygon_names() == ["Alaron", "Gwynneth"]
    assert region.polygon_at(5, 5) == 0 and region.polygon_at(55, 5) == 1 and region.polygon_at(30, 5) is None
    regions.upsert_region("Chain", {"borders": [SQUARE]})            # polygon count shrinks
    assert regions.find_region("chain").polygon_names() == ["Alaron"]
    regions.upsert_region("Chain", {"borders": [SQUARE, other, [[80, 0], [90, 0], [90, 9]]]})
    assert regions.find_region("chain").polygon_names() == ["Alaron", "", ""]


@pytest.mark.parametrize("names,message", [
    (["A"], "one name per polygon"),
    (["A", "a"], "different"),
    (["A", 3], "list of text"),
    (["A", "x" * 81], "limited"),
])
def test_bad_polygon_names_are_rejected(store, names, message):
    with pytest.raises(RegionError, match=message):
        regions.upsert_region("Pair", {"borders": [SQUARE, [[50, 0], [60, 0], [60, 10]]], "border_names": names})
    assert regions.find_region("pair") is None


def test_map_save_carries_polygon_names_into_payload_and_report(store):
    revision = regions.regions_revision()
    payload = regions.save_region_border({"id": "Isles", "create": True, "kind": "island_nation", "revision": revision,
                                          "borders": [SQUARE, [[50, 0], [60, 0], [60, 10]]],
                                          "borderNames": ["  Big   Isle ", ""]}, labels=[])
    assert payload["regionBorders"][0]["borderNames"] == ["Big Isle", ""]
    world = FakeWorld(Market("a", "Alpha", "Isles", 5, 5))
    report = regions.describe_region(world, "isles")
    assert [p["name"] for p in report["polygons"]] == ["Big Isle", ""]
    assert report["polygons"][0]["square_miles"] == 100.0


def island_grid(land_boxes, size=80):
    """A one-mile terrain grid for origin (0, size): sea except the (x0, x1, y0, y1) world boxes."""
    rows = {}
    for row in range(0, size):
        line = ["S"] * size
        for x0, x1, y0, y1 in land_boxes:
            if size - y1 <= row < size - y0:
                for column in range(x0, x1):
                    line[column] = "P"
        rows[str(row)] = "".join(line)
    return {"rows": rows, "cell_miles": 1.0, "column_min": 0, "column_max": size - 1, "row_min": 0, "row_max": size - 1}


ORIGIN = (0, 80)


def box(x0, y0, x1, y1):
    return [[x0, y0], [x1, y0], [x1, y1], [x0, y1]]


def test_polygon_drawn_over_the_sea_is_cut_back_to_the_shore():
    from faerun.coast import fit_ring_to_coast

    grid = island_grid([(20, 40, 20, 40)])                      # land spans 20..40 in both axes
    fitted = fit_ring_to_coast(box(12, 12, 48, 48), ORIGIN, 6, [grid])
    assert len(fitted) == 1
    xs = [p[0] for p in fitted[0]]
    ys = [p[1] for p in fitted[0]]
    assert 19.4 <= min(xs) and max(xs) <= 40.6 and 19.4 <= min(ys) and max(ys) <= 40.6
    assert abs(regions.ring_area(fitted[0]) - 400) < 25


def test_polygon_drawn_short_of_the_shore_grows_out_to_it():
    from faerun.coast import fit_ring_to_coast

    grid = island_grid([(20, 40, 20, 40)])
    fitted = fit_ring_to_coast(box(23, 23, 37, 37), ORIGIN, 6, [grid])
    assert abs(regions.ring_area(fitted[0]) - 400) < 25
    none_grown = fit_ring_to_coast(box(23, 23, 37, 37), ORIGIN, 1, [grid])
    assert regions.ring_area(none_grown[0]) < 300             # a 1-mile reach cannot close a 3-mile gap


def test_coast_fit_does_not_absorb_a_neighbouring_island_or_move_inland_borders():
    from faerun.coast import fit_ring_to_coast

    grid = island_grid([(10, 30, 10, 30), (33, 45, 10, 30)])   # a 3-mile channel separates the islands
    west = fit_ring_to_coast(box(8, 8, 32, 32), ORIGIN, 6, [grid])
    assert len(west) == 1 and max(p[0] for p in west[0]) <= 30.6
    mainland = island_grid([(0, 80, 40, 80)])                  # coast along row 40; polygon ends inland at row 70
    held = fit_ring_to_coast(box(10, 30, 50, 70), ORIGIN, 6, [mainland])
    assert abs(max(p[1] for p in held[0]) - 70) < 1.0          # the inland edge stays where it was drawn
    assert abs(min(p[1] for p in held[0]) - 40) < 1.0          # the sea side is pulled to the coast


def test_coast_fit_leaves_unsurveyed_and_open_water_polygons_alone(monkeypatch):
    from faerun import coast
    from faerun.coast import fit_borders_to_coast, fit_ring_to_coast

    grid = island_grid([(20, 40, 20, 40)])
    assert fit_ring_to_coast(box(60, 60, 70, 70), ORIGIN, 6, [grid]) == []
    assert fit_ring_to_coast(box(100, 100, 110, 110), ORIGIN, 6, [grid]) == []
    monkeypatch.setattr(coast, "_grids", lambda: [grid])
    result = fit_borders_to_coast([box(60, 60, 70, 70)], ORIGIN, 6)
    assert result["reports"][0]["changed"] is False


def test_coast_endpoint_validates_reach(store):
    with pytest.raises(RegionError, match="Snap reach"):
        regions.fit_region_borders({"borders": [SQUARE], "snapMiles": 99}, (0, 0))
    with pytest.raises(RegionError, match="finite"):
        regions.fit_region_borders({"borders": [[[0, 0], [1, "x"], [2, 2]]]}, (0, 0))


def test_coast_buffer_pushes_the_outline_ten_miles_out_over_the_sea():
    from faerun.coast import fit_ring_to_coast

    grid = island_grid([(30, 50, 30, 50)])
    land = fit_ring_to_coast(box(28, 28, 52, 52), ORIGIN, 6, [grid])[0]
    buffered = fit_ring_to_coast(box(28, 28, 52, 52), ORIGIN, 6, [grid], 10)[0]
    xs = [p[0] for p in buffered]
    assert 19 <= min(xs) <= 21.5 and 58.5 <= max(xs) <= 61            # 10 miles beyond the 30..50 coast
    assert not regions.ring_self_intersects(buffered)
    assert 1400 < regions.ring_area(buffered) < 1650                   # a rounded 40-mile square (about 1514), not a square
    assert regions.ring_area(buffered) > regions.ring_area(land) * 3
    again = fit_ring_to_coast(buffered, ORIGIN, 6, [grid], 10)[0]      # snapping again does not keep growing it
    assert abs(regions.ring_area(again) - regions.ring_area(buffered)) / regions.ring_area(buffered) < 0.05


def test_coast_buffer_butts_up_to_a_neighbouring_regions_polygon():
    from faerun.coast import fit_ring_to_coast

    grid = island_grid([(20, 40, 30, 50)])
    neighbour = box(48, 20, 70, 60)
    buffered = fit_ring_to_coast(box(18, 28, 42, 52), ORIGIN, 6, [grid], 10, [neighbour])[0]
    assert max(p[0] for p in buffered) <= 48.5                         # stops at the neighbour, not at 50
    assert max(p[0] for p in buffered) > 44                            # but still runs right up to it
    clear = fit_ring_to_coast(box(18, 28, 42, 52), ORIGIN, 6, [grid], 10)[0]
    assert max(p[0] for p in clear) > 49


def test_coast_endpoint_validates_buffer(store):
    with pytest.raises(RegionError, match="Sea buffer"):
        regions.fit_region_borders({"borders": [SQUARE], "bufferMiles": 500}, (0, 0))


def test_shipped_island_regions_are_valid_and_cover_their_settlements():
    from faerun.world import get_world

    regions._CACHE.update(stamp=None, revision=0, regions=[])
    world = get_world()
    shipped = {region.name: region for region in regions.load_regions()[1]}
    assert {"Lantan", "Nimbral", "Moonshae Isles", "Sea of Swords", "Trackless Sea"} <= set(shipped)
    for region in shipped.values():
        if region.kind == "island_nation":
            if region.border_source == "placeholder":
                assert region.sea_margin_miles == 10.0
            else:                               # traced/edited polygons already include their sea buffer
                assert 0.0 <= region.sea_margin_miles <= 10.0
        assert regions.clean_borders(region.borders) == region.borders
        assert set(region.exports + region.imports) <= set(world.commodities)
    assert shipped["Moonshae Isles"].contains(world.settlements["caer_calidyrr"].x, world.settlements["caer_calidyrr"].y)
    assert shipped["Trackless Sea"].contains(world.settlements["ruathym"].x, world.settlements["ruathym"].y)
