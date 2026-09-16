"""Historical records must remain traceable and outside the live economy."""

import json
from dataclasses import asdict

import pytest

from faerun import cli, web
from faerun.city import city_directory
from faerun.cityassets import WATERDEEP_DIRECTORY_JS
from faerun.data.waterdeep import BUSINESSES, PEOPLE, SOURCE, WARDS
from faerun.models import slugify
from faerun.waterdeepassets import WATERDEEP_HTML


def test_catalogue_has_cross_ward_businesses_people_and_valid_citations():
    assert len(BUSINESSES) >= 30
    assert len(PEOPLE) >= 20
    assert len({b.ward for b in BUSINESSES}) >= 6
    assert len({b.id for b in BUSINESSES}) == len(BUSINESSES)
    assert len({p.id for p in PEOPLE}) == len(PEOPLE)
    assert len({(b.name, b.ward) for b in BUSINESSES}) == len(BUSINESSES)
    assert len({p.name for p in PEOPLE}) == len(PEOPLE)
    assert SOURCE["id"] == "volos_guide_to_waterdeep"
    assert SOURCE["publication_year"] < 2026
    assert SOURCE["era_note"]
    business_ids = {b.id for b in BUSINESSES}
    for record in (*BUSINESSES, *PEOPLE):
        assert record.id == slugify(record.id)
        assert record.name and record.summary and record.citations
        references = list(record.citations)
        if record in BUSINESSES:
            assert record.ward in WARDS
            assert record.category and record.services
        else:
            assert record.affiliations
            assert len({a.business_id for a in record.affiliations}) == len(record.affiliations)
            for affiliation in record.affiliations:
                assert affiliation.business_id in business_ids
                assert affiliation.role and affiliation.citations
                references.extend(affiliation.citations)
        for citation in references:
            assert citation.source_id == SOURCE["id"]
            assert 1 <= citation.printed_page <= SOURCE["pdf_page_count"]
            assert 1 <= citation.pdf_page <= SOURCE["pdf_page_count"]
            assert citation.pdf_page == citation.printed_page + 1


def test_directory_metadata_and_bidirectional_links():
    result = city_directory()
    assert result["historical"] is True
    assert result["live_market_integration"] is False
    assert result["totals"] == result["counts"] == {
        "businesses": len(BUSINESSES), "people": len(PEOPLE),
    }
    businesses = {b["id"]: b for b in result["businesses"]}
    for person in result["people"]:
        assert person["wards"] == sorted({a["ward"] for a in person["affiliations"]})
        for affiliation in person["affiliations"]:
            business = businesses[affiliation["business_id"]]
            backlink = next(p for p in business["people"] if p["person_id"] == person["id"])
            assert backlink["role"] == affiliation["role"]
            assert backlink["citations"] == affiliation["citations"]
            assert affiliation["business_name"] == business["name"]
    assert sum(w["business_count"] for w in result["wards"]) == len(BUSINESSES)
    for ward in result["wards"]:
        assert ward["people_count"] == sum(ward["name"] in p["wards"] for p in result["people"])
    assert json.loads(json.dumps(result))["totals"] == result["totals"]


def test_filter_types_wards_categories_and_linked_search():
    person = PEOPLE[0]
    affiliation = person.affiliations[0]
    business = next(b for b in BUSINESSES if b.id == affiliation.business_id)
    found = city_directory(" WATERDEEP ", search=person.name.upper())
    assert person.id in {p["id"] for p in found["people"]}
    assert business.id in {b["id"] for b in found["businesses"]}
    found = city_directory(search=business.name, kind="person")
    assert found["businesses"] == []
    assert person.id in {p["id"] for p in found["people"]}
    found = city_directory(ward=slugify(business.ward), category=business.category, kind="business")
    assert found["people"] == []
    assert found["businesses"]
    assert all(b["ward"] == business.ward and b["category"] == business.category for b in found["businesses"])
    found = city_directory(ward=business.ward, category=business.category, kind="person")
    assert person.id in {p["id"] for p in found["people"]}
    assert all(any(a["ward"] == business.ward and a["category"] == business.category
                   for a in p["affiliations"]) for p in found["people"])


def test_south_ward_atlas_alias_and_empty_results():
    assert city_directory(ward="South Ward") == city_directory(ward="Southern Ward")
    empty = city_directory(search="no-such-entry-984614")
    assert empty["counts"] == {"businesses": 0, "people": 0}
    assert empty["totals"]["businesses"] == len(BUSINESSES)
    assert empty["source"]["id"] == SOURCE["id"]


@pytest.mark.parametrize("kwargs,exception", [
    ({"settlement": "Neverwinter"}, KeyError),
    ({"settlement": ""}, KeyError),
    ({"ward": "Made-up Ward"}, ValueError),
    ({"category": "unverified category"}, ValueError),
    ({"kind": "resident"}, ValueError),
])
def test_invalid_filters_are_explicit(kwargs, exception):
    with pytest.raises(exception):
        city_directory(**kwargs)


def test_result_mutations_do_not_change_catalogue_or_other_responses():
    baseline = city_directory()
    result = city_directory()
    result["source"]["era_note"] = "changed"
    result["businesses"][0]["summary"] = "changed"
    result["people"][0]["affiliations"][0]["role"] = "changed"
    assert city_directory() == baseline
    assert asdict(BUSINESSES[0])["summary"] != "changed"


def test_http_endpoint_is_read_only_and_does_not_price_world():
    class NoWorldAccess:
        def __getattribute__(self, name):
            raise AssertionError(f"Directory must not access world.{name}")

    route = web.GET_ROUTES["/api/city-directory"]
    assert route(NoWorldAccess(), {}) == city_directory()
    assert route(NoWorldAccess(), {
        "settlement": ["Waterdeep"], "kind": ["person"], "search": [PEOPLE[0].name],
    }) == city_directory(kind="person", search=PEOPLE[0].name)
    assert "/api/city-directory" not in web.POST_ROUTES


def test_live_business_catalogue_is_unchanged():
    from faerun.data.businesses import BUSINESSES as LIVE_BUSINESSES

    live_before = [asdict(b) for b in LIVE_BUSINESSES]
    city_directory()
    assert [asdict(b) for b in LIVE_BUSINESSES] == live_before
    assert {b.id for b in LIVE_BUSINESSES}.isdisjoint({b.id for b in BUSINESSES})


@pytest.mark.parametrize("query,status", [
    ("?kind=person", 200),
    ("?settlement=Neverwinter", 404),
    ("?ward=Unknown", 400),
    ("?kind=resident", 400),
])
def test_http_status_codes(monkeypatch, query, status):
    handler = web.Handler.__new__(web.Handler)
    handler.path = "/api/city-directory" + query
    replies = []
    handler._send_json = lambda payload, code=200: replies.append((payload, code))
    monkeypatch.setattr(web, "get_world", lambda: object())
    handler.do_GET()
    assert replies[0][1] == status
    assert ("error" in replies[0][0]) == (status != 200)


def test_cli_json_text_and_errors_without_world_or_ledger(monkeypatch, capsys):
    def no_world(_args):
        raise AssertionError("Historical CLI must not construct a live world or ledger")

    monkeypatch.setattr(cli, "build_world", no_world)
    assert cli.main(["--json", "city-directory", "--kind", "person"]) == 0
    data = json.loads(capsys.readouterr().out)
    assert data["counts"]["people"] == len(PEOPLE)
    assert data["businesses"] == []
    assert cli.main(["city-directory", "--search", PEOPLE[0].name]) == 0
    assert "PDF" in capsys.readouterr().out
    assert cli.main(["city-directory", "Neverwinter"]) == 2
    assert "No historical city directory" in capsys.readouterr().err


def test_mcp_directory_uses_same_filters_and_errors():
    pytest.importorskip("mcp")
    from faerun.mcp_server import get_city_directory

    assert get_city_directory(kind="person", search=PEOPLE[0].name) == city_directory(
        kind="person", search=PEOPLE[0].name,
    )
    assert "error" in get_city_directory(kind="resident")
    assert "error" in get_city_directory("Neverwinter")


def test_directory_ui_has_filters_citations_export_and_safe_rendering():
    for name in ("search", "ward", "kind", "category", "download", "status", "results"):
        assert f'id="directory-{name}"' in WATERDEEP_HTML
    assert "waterdeep-directory.js" in web.STATIC
    assert "/api/city-directory?" in WATERDEEP_DIRECTORY_JS
    assert "c.printed_page" in WATERDEEP_DIRECTORY_JS
    assert "c.pdf_page" in WATERDEEP_DIRECTORY_JS
    assert "JSON.stringify(snapshot, null, 2)" in WATERDEEP_DIRECTORY_JS
    assert "node.textContent = text" in WATERDEEP_DIRECTORY_JS
    assert "innerHTML" not in WATERDEEP_DIRECTORY_JS
    assert "Could not load the historical directory" in WATERDEEP_DIRECTORY_JS
    assert "requestController !== controller" in WATERDEEP_DIRECTORY_JS
