from faerun import web
from faerun.world import World


def test_detail_pages_and_product_api_are_served():
    for asset in (
        "product.html",
        "product.js",
        "route.html",
        "route.js",
        "detail.css",
    ):
        assert asset in web.STATIC
    assert "/api/product" in web.GET_ROUTES


def test_product_detail_combines_recipe_components_and_sources():
    result = web.api_product(World(), {"commodity": ["warhorse"]})

    assert result["commodity"]["bom"]["horse_riding"] == 1.0
    assert result["commodity"]["production_type"] == "processed/manufactured"
    assert result["components"]["saddle"]["name"] == "Saddle and tack"
    assert result["sourcing"]["sources"]


def test_route_detail_api_returns_an_itinerary():
    result = web.api_route(
        World(),
        {"origin": ["Waterdeep"], "destination": ["Daggerford"]},
    )

    assert result["reachable"] is True
    assert result["legs"][0]["via"] == "The Trade Way"
    assert result["freight_gp_per_100lb"] > 0


def test_legacy_location_businesses_include_branches_and_local_quality_offers():
    from copy import deepcopy

    world = World()
    world.config.expanded_requirements = False
    world.settlements["hlath"] = deepcopy(world.settlements["hlath"])
    world.find_settlement("Hlath").specialties["spellbook_blank"] = 2
    result = web.api_businesses(world, {"settlement": ["Hlath"]})

    assert result["count"] == 2
    thayan = next(
        business for business in result["businesses"]
        if business["id"] == "zulkirate_export_house"
    )
    assert thayan["is_headquarters"] is False
    assert thayan["headquarters_name"] == "Eltabbar"
    spellbooks = [
        offer for offer in thayan["offers"]
        if offer["commodity"] == "spellbook_blank"
    ]
    assert spellbooks
    assert all(offer["quality"] != "masterwork" for offer in spellbooks)
    assert all(offer["price"] > 0 and offer["stock"] > 0 for offer in spellbooks)


def test_existing_views_link_to_the_new_detail_pages():
    from faerun.locationassets import LOCATION_JS
    from faerun.mapassets import MAP_JS
    from faerun.webassets import APP_JS

    assert "product.html?commodity=" in APP_JS
    assert "product.html?commodity=" in LOCATION_JS
    assert "route.html?origin=" in MAP_JS


def test_location_detail_displays_population_based_requirements():
    from faerun.locationassets import LOCATION_HTML, LOCATION_JS

    assert "Baseline / day" in LOCATION_HTML
    assert "Market demand / day" in LOCATION_HTML
    assert 'id="living-standard"' in LOCATION_HTML
    assert "market.daily_requirements" in LOCATION_JS
    assert "per soul" in LOCATION_JS


def test_product_type_is_visible_across_product_views():
    from faerun.detailassets import PRODUCT_JS
    from faerun.locationassets import LOCATION_HTML, LOCATION_JS
    from faerun.mapassets import MAP_JS
    from faerun.webassets import APP_JS, INDEX_HTML

    assert 'data-sort="production_type">Type' in INDEX_HTML
    assert "q.production_type" in APP_JS
    assert "<th>Type</th>" in LOCATION_HTML
    assert "q.production_type" in LOCATION_JS
    assert "data.commodity.production_type" in PRODUCT_JS
    assert "q.production_type" in MAP_JS


def test_supply_chain_traces_processed_inputs_and_routes():
    from faerun.web import api_supply_chain
    from faerun.world import World

    result = api_supply_chain(
        World(), {"settlement": ["Daggerford"], "commodity": ["bread"]}
    )

    bread = result["chain"]
    flour = next(row for row in bread["inputs"] if row["commodity"] == "flour")
    grain = next(row for row in flour["inputs"] if row["commodity"] == "grain")
    assert bread["production_type"] == "processed/manufactured"
    assert flour["quantity"] == 0.02
    assert grain["quantity"] == 0.018
    assert grain["production_type"] == "raw"
    for stage in (bread, flour, grain):
        if not stage["local"]:
            assert stage["route"]["reachable"] is True
            assert stage["route"]["legs"]