import pytest

from faerun.models import S
from faerun.requirements import settlement_profile
from faerun.wages import daily_wage_gp, location_wage_modifier


def settlement(**kwargs):
    return S("Example", "Test", "test", kwargs.pop("population", 1000), 0, 0, **kwargs)


def test_wage_model_exposes_allocation_and_daily_payroll():
    profile = settlement_profile(settlement(population=1000, wealth=1.0))

    assert profile["wage_modifier"] > 0
    assert profile["unallocated_daily_wage_gp"] == pytest.approx(
        daily_wage_gp("general", profile["wage_modifier"])
    )
    assert profile["wage_bill_gp_per_day"] > 0
    assert all("daily_wage_gp" in row for row in profile["establishments"])
    assert all("wage_bill_gp_per_day" in row for row in profile["establishments"])


def test_wages_change_with_local_prosperity_and_labor_tightness():
    poor = settlement(population=1000, wealth=.65, sec=1.0)
    rich = settlement(population=1000, wealth=1.4, sec=1.0)

    poor_modifier = location_wage_modifier(poor, 500, 250)
    rich_modifier = location_wage_modifier(rich, 500, 0)

    assert rich_modifier > poor_modifier
    assert daily_wage_gp("carpenters", rich_modifier) > daily_wage_gp(
        "carpenters", poor_modifier
    )


def test_dynamic_extraction_roles_use_the_extraction_wage_class():
    assert daily_wage_gp("extraction_mine_iron") == daily_wage_gp("extraction")


def test_mcp_wage_crud_round_trip():
    pytest.importorskip("mcp")
    from faerun import mcp_server

    occupation_id = "test_wage_role"
    mcp_server.delete_wage(occupation_id)
    try:
        assert any(row["id"] == "carpenters" for row in mcp_server.list_wages()["wages"])
        assert mcp_server.create_wage(occupation_id, .27)["created"]["daily_wage_gp"] == .27
        assert mcp_server.get_wage(occupation_id)["wage"]["daily_wage_gp"] == .27
        assert mcp_server.update_wage(occupation_id, .31)["updated"]["daily_wage_gp"] == .31
        assert mcp_server.get_wage(occupation_id)["wage"]["daily_wage_gp"] == .31
    finally:
        assert mcp_server.delete_wage(occupation_id)["removed"] is True
