from types import SimpleNamespace

import pytest

from faerun.transport import plan_shipment
from faerun.world import Edge, World


def network():
    world = World.__new__(World)
    world.date = "Baseline"
    world.settlements = {name: SimpleNamespace(id=name, name=name, security=1, traits=[])
                         for name in ("start", "middle", "end", "island")}
    world._edges = {"start": [Edge("start", "middle", 24, 1, "road"),
                               Edge("start", "end", 144, 1, "sea")],
                    "middle": [Edge("middle", "end", 24, 1, "road")]}
    world.find_settlement = lambda name: world.settlements[name]
    world.edge_risk = lambda edge: 1
    return world


def test_shipment_costs_follow_weight_minimums_and_allowances():
    world = network()
    result = plan_shipment(world, "start", "end", minimum=2, handling=3, daily=4,
                           fixed=5, contingency=10)
    land = next(row for row in result["options"] if "Land only" in row["labels"])
    assert land["travel_days"] == 2
    assert land["connections"] == 1
    assert land["costs"]["line_haul_gp"] == pytest.approx(0.288)
    assert land["costs"]["minimum_topup_gp"] == pytest.approx(3.712)
    assert land["costs"]["subtotal_gp"] == 20
    assert land["costs"]["total_gp"] == 22
    heavier = plan_shipment(world, "start", "end", pounds=200)
    assert next(row for row in heavier["options"] if "Land only" in row["labels"])["costs"]["line_haul_gp"] == pytest.approx(0.576)


def test_landed_cost_includes_goods_once_and_preserves_transport_contingency():
    params = dict(minimum=2, handling=3, daily=4, fixed=5, contingency=10)
    for purchase_per_lb in (None, 0, 4):
        result = plan_shipment(network(), "start", "end", purchase_per_lb=purchase_per_lb, **params)
        land = next(row for row in result["options"] if "Land only" in row["labels"])
        costs = land["costs"]
        assert costs["total_gp"] == 22
        assert result["assumptions"]["purchase_per_lb"] == purchase_per_lb
        if purchase_per_lb is None:
            assert costs["purchase_value_gp"] is None
            assert costs["landed_total_gp"] is None
            assert costs["landed_gp_per_lb"] is None
        else:
            assert costs["purchase_value_gp"] == 100 * purchase_per_lb
            assert costs["landed_total_gp"] == 100 * purchase_per_lb + 22
            assert costs["landed_gp_per_lb"] == pytest.approx(purchase_per_lb + 0.22)


def test_options_risk_exclusions_and_unreachable():
    world = network()
    quiet = plan_shipment(world, "start", "end")
    active = plan_shipment(world, "start", "end", include_events=True)
    assert active["options"][0]["costs"]["line_haul_gp"] == 2 * quiet["options"][0]["costs"]["line_haul_gp"]
    assert plan_shipment(world, "start", "island")["options"] == []
    world._edges["start"][0].inferred = True
    assert "Land only" in plan_shipment(world, "start", "end")["unavailable"]
    assert "Land only" not in plan_shipment(world, "start", "end", include_inferred=True)["unavailable"]
    world._edges["start"].append(Edge("start", "island", 10, 1, "teleport"))
    assert not plan_shipment(world, "start", "island")["options"]
    assert plan_shipment(world, "start", "island", allow_special=True)["options"]


@pytest.mark.parametrize("kwargs", [{"pounds": 0}, {"pounds": -1}, {"daily": float("nan")},
                                   {"fixed": float("inf")}, {"contingency": 101},
                                   {"purchase_per_lb": -1}, {"purchase_per_lb": float("nan")},
                                   {"purchase_per_lb": float("inf")}, {"purchase_per_lb": 1e10}])
def test_invalid_cost_inputs_are_rejected(kwargs):
    with pytest.raises(ValueError):
        plan_shipment(network(), "start", "end", **kwargs)


@pytest.mark.parametrize("pounds,companies", [(100, 1), (1000, 1), (1000.01, 2), (40000, 40)])
def test_carrier_shipments_round_up_per_leg(pounds, companies):
    world = network()
    world._edges = {"start": [Edge("start", "middle", 24, 1, "trail")],
                    "middle": [Edge("middle", "end", 24, 1, "river+barge")]}
    route = plan_shipment(world, "start", "end", pounds=pounds)["options"][0]
    trail, water = route["legs"]
    porter = next(carrier for carrier in trail["carrier_loads"] if carrier["name"] == "Porter company")
    assert porter["capacity_lb"] == 1000
    assert porter["shipments_required"] == companies
    assert {carrier["mode"] for carrier in water["carrier_loads"]} == {"river", "barge"}
    for leg in route["legs"]:
        for carrier in leg["carrier_loads"]:
            count, capacity = carrier["shipments_required"], carrier["capacity_lb"]
            assert (count - 1) * capacity < pounds <= count * capacity
    assert route["costs"]["total_gp"] == route["costs"]["line_haul_gp"]


def test_carrier_selection_recalculates_cost_time_and_landed_value():
    world = network()
    world._edges = {"start": [Edge("start", "middle", 24, 1, "trail")],
                    "middle": [Edge("middle", "end", 24, 1, "river+barge")]}
    baseline = plan_shipment(world, "start", "end", pounds=1001, daily=2, purchase_per_lb=4)
    route = baseline["options"][0]
    trail, water = route["legs"]
    porter = next(carrier for carrier in trail["carrier_loads"] if carrier["name"] == "Porter company")
    choices = {trail["id"]: {"trail": "Porter company"}, water["id"]: {"river": "Keelboat"}}
    result = plan_shipment(world, "start", "end", pounds=1001, daily=2, purchase_per_lb=4,
                           carrier_choices=choices)["options"][0]
    assert result["id"] == route["id"]
    assert result["legs"][0]["line_haul_gp"] == porter["full_load_cost_gp"] * 2
    assert result["legs"][0]["travel_days"] == porter["travel_days"]
    assert result["legs"][1]["transport_stages"][1] == water["transport_stages"][1]
    assert result["costs"]["daily_gp"] == 2 * result["travel_days"]
    assert result["costs"]["landed_total_gp"] == 4004 + result["costs"]["total_gp"]
    assert sum(stage["distance_miles"] for stage in water["transport_stages"]) == water["distance_miles"]
    for edge, leg in zip([world._edges["start"][0], world._edges["middle"][0]], route["legs"]):
        assert leg["travel_days"] == pytest.approx(edge.days)
        assert leg["line_haul_gp"] == pytest.approx(edge.freight_units(0) * 0.00006 * 1001)
    active = plan_shipment(world, "start", "end", pounds=1001, carrier_choices=choices,
                           include_events=True)["options"][0]
    assert active["legs"][0]["line_haul_gp"] == 2 * result["legs"][0]["line_haul_gp"]
    for invalid in ([], {"obsolete": {}}, {trail["id"]: {"sea": "Keelboat"}},
                    {trail["id"]: {"trail": "Unknown"}}, {trail["id"]: "Porter company"}):
        with pytest.raises(ValueError):
            plan_shipment(world, "start", "end", carrier_choices=invalid)


def test_planner_api_assets_and_javascript():
    import json
    import subprocess
    from faerun import web
    from faerun.plannerassets import PLANNER_JS

    assert {"planner.html", "planner.js", "planner.css"} <= web.STATIC.keys()
    assert "/api/transport-plan" in web.GET_ROUTES
    params = {"origin": ["start"], "destination": ["end"], "pounds": ["100"]}
    assert web.api_transport_plan(network(), params)["options"]
    leg = web.api_transport_plan(network(), params)["options"][0]["legs"][0]
    carrier = leg["carrier_loads"][0]
    choices = {leg["id"]: {carrier["mode"]: carrier["name"]}}
    configured = web.api_transport_plan(network(), {**params, "carrier_choices": [json.dumps(choices)]})
    assert configured["assumptions"]["carrier_choices"] == choices
    priced = web.api_transport_plan(network(), {**params, "purchase_per_lb": ["4"]})
    for option in priced["options"]:
        assert option["costs"]["landed_total_gp"] == 400 + option["costs"]["total_gp"]
    assert web.api_transport_plan(network(), {**params, "purchase_per_lb": [""]})["options"][0]["costs"]["landed_total_gp"] is None
    for field, value in [("pounds", "nan"), ("include_events", "true"), ("destination", "missing"),
                         ("purchase_per_lb", "nan"), ("purchase_per_lb", "invalid"),
                         ("carrier_choices", "[1]"), ("carrier_choices", "{invalid")]:
        with pytest.raises(web.ApiError):
            web.api_transport_plan(network(), {**params, field: [value]})
    subprocess.run(["node", "-"], input="new Function(" + json.dumps(PLANNER_JS) + ");",
                   text=True, check=True, capture_output=True)