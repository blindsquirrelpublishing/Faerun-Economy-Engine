import pytest

from faerun.calendar import HarptosDate
from faerun.models import C, S
from faerun.visitors import DAY_VISIT_FOOD_SHARE, plan_visitors
from faerun.world import World


@pytest.fixture
def world(monkeypatch):
    from faerun import visitors

    def food(s, goods, **kwargs):
        return {c.id: {"household": s.population * .1 * s.wealth} for c in goods}

    monkeypatch.setattr(visitors, "final_requirements", food)
    return World(
        settlements=[
            S("Home", "Test", "test", 10000, 0, 0, wealth=1.4, ind="trade2"),
            S("Shrine", "Test", "test", 1000, 30, 0, traits="temple academic", ind="temple3"),
            S("Port", "Test", "test", 3000, 60, 0, port="Test", traits="cosmopolitan mercantile"),
        ], commodities=[C("grain", "Grain", "food", 1, "bushel", 60)]
    )


def test_domestic_visitors_and_home_reductions_are_conserved(world):
    result = plan_visitors(world, {sid: 1000 for sid in world.settlements})
    assert result["flows"]
    places = result["places"]
    assert sum(p["visitors_per_day"] for p in places.values()) == pytest.approx(
        sum(p["outbound_visitors_per_day"] for p in places.values()))
    assert sum(p["visitor_food_equivalents"] for p in places.values()) == pytest.approx(
        sum(p["outbound_food_equivalents"] for p in places.values()))
    for sid, p in places.items():
        assert p["residents_at_home"] == pytest.approx(
            world.settlements[sid].population - p["outbound_visitors_per_day"])
        assert p["modeled_present_population"] == pytest.approx(
            p["residents_at_home"] + p["visitors_per_day"])
        assert p["external_visitors_per_day"] is None
        assert p["resident_presence"] >= .9 * world.settlements[sid].population
        assert p["home_food_reduction"]["grain"] == pytest.approx(
            p["outbound_food_equivalents"] * .1 * world.settlements[sid].wealth)
    for flow in result["flows"]:
        assert flow["origin_id"] != flow["destination_id"]
        assert flow["risk_adjusted_days"] <= world.config.visitor_max_days
        assert flow["food_equivalents"] == pytest.approx(
            flow["visitors_per_day"] * (1 if flow["overnight"] else DAY_VISIT_FOOD_SHARE))


def test_beds_limit_admissions_not_desired_visits(world):
    result = plan_visitors(world, {sid: .1 for sid in world.settlements})
    for p in result["places"].values():
        assert p["overnight_visitors_per_day"] <= .1 + 1e-9
        assert p["occupancy"] <= 1 + 1e-9
        assert p["desired_overnight_visitors_per_day"] == pytest.approx(
            p["overnight_visitors_per_day"] + p["unaccommodated_visitors_per_day"])
    assert any(p["unaccommodated_visitors_per_day"] > 0 for p in result["places"].values())


def test_unreachable_and_empty_places_do_not_receive_visitors(world):
    world._edges = {sid: [] for sid in world.settlements}
    result = plan_visitors(world, {sid: 1000 for sid in world.settlements})
    assert not result["flows"]
    assert all(p["visitors_per_day"] == 0 for p in result["places"].values())


def test_seasons_change_volume_without_changing_lodging_capacity(world):
    beds = {sid: 100000 for sid in world.settlements}
    world.date = HarptosDate(1492, 2)
    winter = plan_visitors(world, beds)
    world.date = HarptosDate(1492, 6)
    summer = plan_visitors(world, beds)
    assert sum(p["visitors_per_day"] for p in summer["places"].values()) > sum(
        p["visitors_per_day"] for p in winter["places"].values())
    assert [p["beds"] for p in summer["places"].values()] == list(beds.values())


def test_toggle_zero_scale_and_large_scale_are_safe(world):
    world.config.visitor_economy = False
    disabled = plan_visitors(world, {})
    assert not disabled["flows"]
    assert all(p["modeled_present_population"] == p["residents_at_home"] ==
               p["resident_population"] for p in disabled["places"].values())
    world.config.visitor_economy = True
    world.config.visitor_scale = 0
    assert not plan_visitors(world, {})["flows"]
    world.config.visitor_scale = 100000
    result = plan_visitors(world, {sid: 1e9 for sid in world.settlements})
    assert all(p["outbound_visitors_per_day"] <= world.settlements[sid].population * .1 + 1e-7
               for sid, p in result["places"].items())


def test_day_visitors_are_full_people_but_fractional_food_days(world):
    from faerun.world import Edge

    world._edges = {sid: [] for sid in world.settlements}
    world._edges["home"] = [Edge("home", "shrine", 1, 1, "road")]
    world._edges["shrine"] = [Edge("shrine", "home", 1, 1, "road")]
    result = plan_visitors(world, {sid: 10000 for sid in world.settlements})
    assert any(p["day_visitors_per_day"] > 0 for p in result["places"].values())
    assert sum(p["modeled_present_population"] for p in result["places"].values()) == pytest.approx(
        sum(s.population for s in world.settlements.values()))
    home = result["places"]["home"]
    away_day_visitors = sum(
        row["visitors_per_day"] for row in result["flows"]
        if row["origin_id"] == "home" and not row["overnight"]
    )
    assert away_day_visitors > 0
    assert home["resident_presence"] - home["residents_at_home"] == pytest.approx(
        away_day_visitors * (1 - DAY_VISIT_FOOD_SHARE))


def test_invalid_travel_parameters_are_rejected(world):
    world.config.visitor_scale = float("nan")
    with pytest.raises(ValueError, match="Visitor scale"):
        plan_visitors(world, {})
    world.config.visitor_scale = 1
    with pytest.raises(ValueError, match="beds"):
        plan_visitors(world, {"home": -1})


def test_visitors_keep_their_own_wealth_at_a_poor_destination(world):
    result = plan_visitors(world, {sid: 10000 for sid in world.settlements})
    flow = next(flow for flow in result["flows"]
                if flow["origin_id"] == "home" and flow["destination_id"] == "shrine"
                and flow["segment_id"] == "leisure")
    assert flow["basket_wealth"] > world.settlements["shrine"].wealth
    assert flow["goods_demand"]["grain"] == pytest.approx(
        flow["food_equivalents"] * .1 * flow["basket_wealth"])


def test_economy_cache_key_tracks_configuration_and_explicit_month(world):
    baseline = world.economy_state_key()
    cache = {baseline: "baseline"}
    assert cache[world.economy_state_key()] == "baseline"
    world.config.visitor_scale = 2
    assert world.economy_state_key() != baseline
    before = world.date
    requested = world.economy_state_key(before.absolute_month() + 1)
    assert requested != world.economy_state_key()
    assert world.date == before
    world.config.delivery_limits[("grain", "home", "shrine")] = 4
    assert isinstance(hash(world.economy_state_key()), int)
