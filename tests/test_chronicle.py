"""The standing history: is it deterministic, plausible and bounded?

These tests build worlds directly rather than through `get_world()` where the
subject is the chronicle itself, so a failure points at the generator instead of
at global state.
"""

import pytest

from faerun.chronicle import (
    CHRONICLE_FIRST_YEAR,
    CHRONICLE_LAST_YEAR,
    CHRONICLE_PREFIX,
    build_chronicle,
    chronicle_months,
    chronicle_summary,
    chronicle_window,
    clear_chronicle,
    event_span,
    install_chronicle,
    is_chronicle_event,
    month_labels,
    month_of,
    settlement_timeline,
    _absolute,
    _from_absolute,
)
from faerun.events import EVENT_TEMPLATES, make_event
from faerun.location import (
    basket_for,
    clear_detail_cache,
    location_detail,
    location_timeline,
    _without_events,
)
from faerun.world import World, get_world, reset_world


@pytest.fixture(scope="module")
def chronicled():
    """One world with history, shared across the read-only tests."""
    world = World()
    install_chronicle(world)
    return world


# ---------------------------------------------------------------------------
# Calendar arithmetic
# ---------------------------------------------------------------------------

def test_absolute_month_round_trips():
    for year in (CHRONICLE_FIRST_YEAR, 1492, CHRONICLE_LAST_YEAR):
        for month in range(1, 13):
            stamp = _absolute(year, month)
            date = _from_absolute(stamp)
            assert (date.year, date.month) == (year, month)
            assert date.absolute_month() == stamp
            assert month_of(stamp) == month


def test_window_covers_seven_whole_years():
    first, last = chronicle_window()
    assert _from_absolute(first).year == CHRONICLE_FIRST_YEAR
    assert _from_absolute(first).month == 1
    assert _from_absolute(last).year == CHRONICLE_LAST_YEAR
    assert _from_absolute(last).month == 12
    assert chronicle_months() == 7 * 12
    assert len(month_labels()) == chronicle_months()


# ---------------------------------------------------------------------------
# Determinism and shape
# ---------------------------------------------------------------------------

def test_chronicle_is_reproducible():
    """The same world must always get the same history, run after run."""
    def fingerprint(events):
        return [(e.id, e.name, e.start_month, e.duration_months,
                 round(e.supply, 4), round(e.demand, 4)) for e in events]

    assert fingerprint(build_chronicle(World())) == fingerprint(build_chronicle(World()))


def test_event_ids_are_unique(chronicled):
    ids = [e.id for e in chronicled.events.values() if is_chronicle_event(e)]
    assert len(ids) == len(set(ids))


def test_chronicle_is_substantial_but_not_absurd(chronicled):
    summary = chronicle_summary(chronicled)
    # Every settlement should have picked up some history, but nowhere near
    # one disaster a month.
    assert summary["events"] > len(chronicled.settlements)
    assert summary["events"] < len(chronicled.settlements) * 12
    assert summary["by_kind"]


def test_every_event_sits_inside_the_window(chronicled):
    first, last = chronicle_window()
    for event in chronicled.events.values():
        if not is_chronicle_event(event):
            continue
        start, _end = event_span(event)
        assert start is not None, f"{event.id} has no start month"
        assert first <= start <= last, f"{event.id} starts outside the window"


def test_durations_are_positive(chronicled):
    for event in chronicled.events.values():
        if is_chronicle_event(event):
            assert event.duration_months is None or event.duration_months >= 1


def test_modifiers_stay_the_right_side_of_one(chronicled):
    """Severity scales an event's bite; it must never flip its direction."""
    for event in chronicled.events.values():
        if not is_chronicle_event(event):
            continue
        assert event.supply > 0
        assert event.demand > 0
        assert event.price > 0
        assert event.risk >= 0


# ---------------------------------------------------------------------------
# Plausibility
# ---------------------------------------------------------------------------

def _local_events(world, s):
    prefix = f"{CHRONICLE_PREFIX}-{s.id}-"
    return [e for e in world.events.values() if str(e.id).startswith(prefix)]


def test_the_underdark_has_no_weather(chronicled):
    """No sky, no drought, no floods, and certainly no hard winter."""
    banned = ("Drought", "Flood", "Hard Winter", "Bumper Harvest")
    for s in chronicled.settlements.values():
        if not s.underdark:
            continue
        for event in _local_events(chronicled, s):
            assert not event.name.startswith(banned), \
                f"{s.name} (Underdark) got {event.name!r}"


def test_landlocked_towns_have_no_pirates(chronicled):
    for s in chronicled.settlements.values():
        if s.is_port:
            continue
        for event in _local_events(chronicled, s):
            assert not event.name.startswith(("Pirates", "Blockade")), \
                f"{s.name} is not a port but got {event.name!r}"


def test_seasonal_events_land_in_their_season(chronicled):
    """Hard winters start in winter, droughts in summer.

    Events beginning in the final year are exempt: the snapper refuses to push
    a start date past the end of the window, so it may leave one unsnapped.
    """
    _first, last = chronicle_window()
    seasons = {"Hard Winter": (11, 12, 1), "Drought": (5, 6, 7),
               "Flood": (3, 4, 5)}
    for s in chronicled.settlements.values():
        for event in _local_events(chronicled, s):
            for label, months in seasons.items():
                if not event.name.startswith(label):
                    continue
                if event.start_month > last - 12:
                    continue
                assert month_of(event.start_month) in months, \
                    f"{event.name} starts in month {month_of(event.start_month)}"


def test_local_episodes_do_not_overlap_each_other(chronicled):
    """One market, one disaster at a time -- regional layers may still stack."""
    for s in chronicled.settlements.values():
        spans = sorted(event_span(e) for e in _local_events(chronicled, s))
        for (start_a, end_a), (start_b, _end_b) in zip(spans, spans[1:]):
            if end_a is None:
                continue
            assert start_b > end_a, f"{s.name} has two events running at once"


def test_curated_events_reach_real_regions(chronicled):
    """A misspelt region would silently vanish, so check they all landed."""
    lore = [e for e in chronicled.events.values()
            if str(e.id).startswith(f"{CHRONICLE_PREFIX}-lore-")]
    assert len(lore) >= 6
    known = {s.region for s in chronicled.settlements.values()}
    for event in lore:
        assert event.regions
        assert set(event.regions) <= known


# ---------------------------------------------------------------------------
# Installing and removing
# ---------------------------------------------------------------------------

def test_install_is_idempotent():
    world = World()
    first = install_chronicle(world)
    total = len(world.events)
    second = install_chronicle(world)
    assert first == second
    assert len(world.events) == total


def test_clear_leaves_hand_placed_events_alone():
    world = World()
    world.add_event(make_event(template="siege", settlements=["waterdeep"],
                               world=world, event_id="dm-siege"))
    install_chronicle(world)
    assert "dm-siege" in world.events
    removed = clear_chronicle(world)
    assert removed > 0
    assert list(world.events) == ["dm-siege"]


def test_the_default_world_has_history():
    reset_world()
    try:
        world = get_world()
        assert chronicle_summary(world)["events"] > 0
        assert any(is_chronicle_event(e) for e in world.events.values())
    finally:
        reset_world()


def test_a_bare_world_has_no_history():
    """Tests that build `World()` directly must not inherit the chronicle."""
    assert not any(is_chronicle_event(e) for e in World().events.values())


# ---------------------------------------------------------------------------
# Reading it back
# ---------------------------------------------------------------------------

def test_settlement_timeline_only_reports_relevant_events(chronicled):
    timeline = settlement_timeline("waterdeep", world=chronicled)
    assert timeline["settlement"] == "Waterdeep"
    assert timeline["months"] == chronicle_months()
    s = chronicled.find_settlement("waterdeep")
    for row in timeline["events"]:
        event = chronicled.events[row["id"]]
        assert event.applies_to_settlement(s)


def test_basket_is_real_goods(chronicled):
    for name in ("Waterdeep", "Mithral Hall", "Calimport"):
        s = chronicled.find_settlement(name)
        basket = basket_for(chronicled, s)
        assert basket
        for c in basket:
            assert c.id in chronicled.commodities


def test_timeline_walks_the_whole_window(chronicled):
    data = location_timeline("waterdeep", world=chronicled,
                             commodities=["grain", "ale"])
    assert len(data["series"]) == chronicle_months()
    assert data["series"][0]["month"] == data["first_month"]
    assert data["series"][-1]["month"] == data["last_month"]
    for row in data["series"]:
        assert row["index"] > 0
        assert row["label"]
    analysis = data["analysis"]
    assert analysis["months"] == chronicle_months()
    assert analysis["quiet_months"] + analysis["troubled_months"] == chronicle_months()
    assert analysis["dearest"]["index"] >= analysis["cheapest"]["index"]


def test_timeline_leaves_the_world_date_alone(chronicled):
    before = chronicled.date
    location_timeline("Neverwinter", world=chronicled, commodities=["grain"])
    assert chronicled.date == before


def test_detail_prices_a_counterfactual(chronicled):
    detail = location_detail("waterdeep", world=chronicled,
                             month=_absolute(1492, 6))
    assert detail["market"]["prices"]
    priced = {q["commodity"] for q in detail["market"]["prices"]}
    assert priced == set(detail["quiet"])
    for mover in detail["movers"]:
        assert mover["commodity_id"] in priced
        assert abs(mover["change"]) >= 0.005


def test_detail_restores_the_world(chronicled):
    date_before = chronicled.date
    events_before = dict(chronicled.events)
    location_detail("waterdeep", world=chronicled, month=_absolute(1490, 2))
    assert chronicled.date == date_before
    assert chronicled.events == events_before


def test_history_actually_moves_prices(chronicled):
    """If the chronicle changed nothing there would be no point to it."""
    data = location_timeline("waterdeep", world=chronicled,
                             commodities=["grain", "ale", "iron_ingot"])
    values = {row["index"] for row in data["series"]}
    assert len(values) > 1, "prices are flat across seven years of history"


def test_detail_does_not_throw_away_the_price_cache():
    """The counterfactual must not invalidate everything on its way out.

    `_without_events` needs a revision of its own, but if it leaves the world
    on a revision the cache has never seen then every entry the board and the
    timeline just paid for is dead, on every single request.
    """
    world = World()
    install_chronicle(world)
    before = world.revision
    location_detail("waterdeep", world=world, month=_absolute(1490, 2))
    assert world.revision == before


def test_the_quiet_world_cannot_shadow_a_real_revision():
    """A later mutation must never land on the quiet world's cache key.

    Real revisions only count upwards, so the quiet world takes the negative
    side. If it ever shared a key with a real state, the engine would quote
    event-free prices for a world that plainly has events in it.
    """
    world = World()
    install_chronicle(world)
    quiet_revisions = []

    with _without_events(world):
        quiet_revisions.append(world.revision)
    # Anything that changes the world bumps the revision; none of those bumps
    # may ever reach the number the quiet world used.
    for _ in range(5):
        world.revision += 1
        with _without_events(world):
            quiet_revisions.append(world.revision)
        assert world.revision not in quiet_revisions

    assert all(r < 0 for r in quiet_revisions)


def test_events_still_bite_after_a_counterfactual():
    """The regression the negative revision guards against, end to end."""
    world = World()
    install_chronicle(world)
    stamp = _absolute(1490, 2)
    # One category keeps this to a handful of goods; the bug is about cache
    # keys, not breadth.
    category = world.find_commodity("grain").category
    first = location_detail("waterdeep", world=world, month=stamp,
                            category=category)
    world.revision += 1  # stand in for any ordinary mutation
    second = location_detail("waterdeep", world=world, month=stamp,
                             category=category)
    assert first["goods_moved"] == second["goods_moved"]
    assert first["event_cost"] == pytest.approx(second["event_cost"])


def test_picking_a_different_month_really_moves_the_prices():
    """The complaint was "the price list does not change with the date".

    If this ever passes trivially the location screen is lying to the reader,
    so assert that a decent share of the catalogue actually moves between two
    ordinary months -- the monthly noise term alone should see to that.
    """
    world = World()
    install_chronicle(world)
    clear_detail_cache(world)
    category = world.find_commodity("grain").category

    first = location_detail("waterdeep", world=world,
                            month=_absolute(1490, 2), category=category)
    second = location_detail("waterdeep", world=world,
                             month=_absolute(1490, 9), category=category)

    assert first["month"] != second["month"]
    assert first["label"] != second["label"]

    was = {q["commodity"]: q["price"] for q in first["market"]["prices"]}
    now = {q["commodity"]: q["price"] for q in second["market"]["prices"]}
    assert was, "no goods priced, so the test proves nothing"
    moved = [cid for cid, price in now.items() if was.get(cid) != price]
    assert len(moved) > len(was) / 2, (
        f"only {len(moved)} of {len(was)} goods moved between months"
    )


def test_scrubbing_back_to_a_month_is_served_from_the_cache():
    """Revisiting a month must not pay for two more full market passes."""
    world = World()
    install_chronicle(world)
    clear_detail_cache(world)
    stamp = _absolute(1490, 2)
    category = world.find_commodity("grain").category

    first = location_detail("waterdeep", world=world, month=stamp,
                            category=category)
    again = location_detail("waterdeep", world=world, month=stamp,
                            category=category)
    assert again is first, "the detail payload was rebuilt from scratch"

    # ...but an edit to the world has to invalidate it.
    world.revision += 1
    fresh = location_detail("waterdeep", world=world, month=stamp,
                            category=category)
    assert fresh is not first
    assert fresh["event_cost"] == pytest.approx(first["event_cost"])


def test_a_quiet_month_skips_the_counterfactual_but_still_agrees():
    """The skip is only sound if it matches what the second pass would say."""
    world = World()
    stamp = _absolute(1490, 2)
    clear_detail_cache(world)
    # No chronicle installed, so nothing is running anywhere.
    assert not world.active_events()
    category = world.find_commodity("grain").category
    detail = location_detail("waterdeep", world=world, month=stamp,
                             category=category)

    assert detail["goods_moved"] == 0
    assert detail["event_cost"] == pytest.approx(0.0)
    for row in detail["market"]["prices"]:
        assert detail["quiet"][row["commodity"]] == pytest.approx(
            round(row["price"], 2)
        )


def test_the_location_screen_is_actually_served():
    """A page missing from STATIC is a page the browser cannot open."""
    from faerun import web

    for name in ("index.html", "map.html", "location.html",
                 "location.css", "location.js", "app.css"):
        assert name in web.STATIC, f"{name} is not served"
    for route in ("/api/timeline", "/api/location", "/api/chronicle"):
        assert route in web.GET_ROUTES, f"{route} is not routed"


def test_every_generated_template_is_a_real_template():
    """`_title` is built from the template name, so names double as a check."""
    labels = {name.replace("_", " ").title() for name in EVENT_TEMPLATES}
    world = World()
    for event in build_chronicle(world):
        if not str(event.id).startswith(f"{CHRONICLE_PREFIX}-lore-"):
            label = event.name.split(" in ")[0]
            assert label in labels, f"unknown template behind {event.name!r}"
