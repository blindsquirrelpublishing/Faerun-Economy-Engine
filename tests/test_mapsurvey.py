from copy import deepcopy

import pytest

from faerun import mapsurvey, web
from faerun.calendar import HarptosDate
from faerun.data.settlements import SETTLEMENTS
from faerun.world import World


@pytest.fixture
def evidence(monkeypatch):
    data = {
        "coordinate_space": {
            "width": 3560, "height": 7256, "units": "image_pixels", "origin": "top_left",
        },
        "source": {"id": "fixture"},
        "coverage": {"complete": False},
        "limitations": ["Test evidence only"],
        "features": [
            {
                "id": identifier, "properties": {"name": name, "status": "candidate"},
                "geometry": {"type": "LineString", "coordinates": [[100, 200], [300, 400]]},
            }
            for identifier, name in [
                ("s1", "High Road"), ("s2", "High Street"), ("s3", None),
            ]
        ],
    }
    monkeypatch.setattr(mapsurvey, "_load_survey", lambda layer: data)
    return data


@pytest.fixture
def world():
    return World(
        settlements=[deepcopy(s) for s in SETTLEMENTS if s.id in ("waterdeep", "goldenfields")],
        date=HarptosDate(1492, 9, 16),
    )


def test_paged_search_retains_full_coverage_and_does_not_mutate_evidence(evidence):
    before = deepcopy(evidence)
    report = mapsurvey.map_survey_report("streets", search="HIGH", limit=1)
    assert report["coverage"] == evidence["coverage"]
    assert report["selection"]["total_records"] == 3
    assert report["selection"]["matched_records"] == 2
    assert report["selection"]["returned_records"] == 1
    assert report["selection"]["next_offset"] == 1
    assert report["features"][0]["id"] == "s1"
    last = mapsurvey.map_survey_report("streets", search="HIGH", limit=1, offset=1)
    assert last["features"][0]["id"] == "s2"
    assert last["selection"]["next_offset"] is None
    assert mapsurvey.map_survey_report("streets", search="s3")["features"][0]["properties"]["name"] is None
    assert mapsurvey.map_survey_report("streets", offset=20)["features"] == []
    assert evidence == before


def test_metadata_only_is_not_presented_as_zero_total_records(evidence):
    report = mapsurvey.map_survey_report("roofs", include_features=False)
    assert report["features"] == []
    assert report["selection"]["features_included"] is False
    assert report["selection"]["total_records"] == 3
    assert report["selection"]["next_offset"] is None


@pytest.mark.parametrize("kwargs", [
    {"offset": -1}, {"offset": True}, {"offset": 1.1},
    {"limit": 0}, {"limit": -1}, {"limit": False}, {"limit": 1.5},
    {"search": None}, {"include_features": "false"},
])
def test_invalid_paging_is_rejected(evidence, kwargs):
    with pytest.raises(ValueError):
        mapsurvey.map_survey_report("streets", **kwargs)


def test_unknown_layer_and_city_are_rejected(evidence):
    with pytest.raises(ValueError):
        mapsurvey.map_survey_report("generated")
    with pytest.raises(KeyError):
        mapsurvey.map_survey_report("streets", "goldenfields")


def test_web_and_mcp_map_reports_are_consistent_and_read_only(evidence, world, monkeypatch):
    revision = world.revision
    params = {"settlement": ["Waterdeep"], "limit": ["1"], "search": ["High"]}
    report = web.GET_ROUTES["/api/streets"](world, params)
    assert report["active_resident_population"] == 200_000
    assert report["active_population_unchanged"] is True
    assert report["date"] == "16 Eleint 1492 DR"
    assert report["selection"]["returned_records"] == 1
    roofs = web.GET_ROUTES["/api/census/hires"](world, {"settlement": ["Waterdeep"]})
    assert roofs["selection"]["total_records"] == 3
    assert world.revision == revision
    with pytest.raises(KeyError):
        web.api_streets(world, {"settlement": ["Goldenfields"]})
    with pytest.raises(ValueError):
        web.api_streets(world, {"settlement": ["Waterdeep"], "limit": ["0"]})
    pytest.importorskip("mcp")
    from faerun import mcp_server

    monkeypatch.setattr(mcp_server, "world", lambda: world)
    assert mcp_server.get_city_map_survey(
        search="High", limit=1, include_features=True,
    ) == report
    metadata = mcp_server.get_city_map_survey("roofs")
    assert metadata["features"] == []
    assert metadata["selection"]["total_records"] == 3
    assert "error" in mcp_server.get_city_map_survey("not-a-layer")
    assert world.revision == revision


def test_high_resolution_image_and_survey_script_are_served():
    path, content_type = web.BINARY_STATIC["waterdeep-map-hires.jpg"]
    assert path.is_file()
    assert content_type == "image/jpeg"
    assert "waterdeep-survey.js" in web.STATIC
    assert 'src="waterdeep-map-hires.jpg"' in web.STATIC["waterdeep.html"][0]
