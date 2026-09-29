from faerun import cli
from faerun.data.commodities import COMMODITIES
from faerun.models import S
from faerun.web import api_market
from faerun.world import EconomyConfig
from faerun.world import World


def test_serve_category_opens_filtered_location_page(monkeypatch):
    seen = {}

    def fake_serve(**kwargs):
        seen.update(kwargs)

    monkeypatch.setattr("faerun.web.serve", fake_serve)
    args = cli.build_parser().parse_args(["serve", "--category", "food", "--no-browser"])

    args.func(args, World())

    assert seen["page"] == "location.html?category=food"
    assert seen["open_browser"] is False


def test_location_category_preserves_settlement_in_start_page(monkeypatch):
    seen = {}

    def fake_serve(**kwargs):
        seen.update(kwargs)

    monkeypatch.setattr("faerun.web.serve", fake_serve)
    args = cli.build_parser().parse_args(["location", "Waterdeep", "--category", "food", "--no-browser"])

    args.func(args, World())

    assert seen["page"] == "location.html?settlement=waterdeep&category=food"


def test_market_api_simple_mode_bypasses_expanded_requirements(monkeypatch):
    def forbidden_requirements(_world):
        raise AssertionError("expanded requirements should not run in simple mode")

    monkeypatch.setattr("faerun.materials.requirements_markets", forbidden_requirements)
    world = World(
        settlements=[S("Town", "Test", "test", 1000, 0, 0, ind="farm3")],
        commodities=COMMODITIES,
        businesses=[],
        config=EconomyConfig(expanded_requirements=True, seasonal_inventory=True, noise=0),
    )

    report = api_market(world, {"settlement": ["Town"], "simple": ["1"]})

    assert report["simple_price_mode"] is True
    assert report["prices"]
    assert world.config.expanded_requirements is True
    assert world.config.seasonal_inventory is True
