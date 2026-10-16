"""Keep the 1491 DR named-business directory distinct from scenario economics."""

import json
from pathlib import Path

from faerun.data_store import load_businesses, load_settlements


ROOT = Path(__file__).resolve().parents[1]


def test_red_larch_business_directory_matches_packaged_metadata():
    businesses = load_businesses()
    red_larch = [b for b in businesses if "red_larch" in b.locations]
    ids = {b.id for b in red_larch}
    assert len(ids) == len(red_larch) == 17
    assert all(b.headquarters == "red_larch" and b.locations == ["red_larch"] for b in red_larch)
    assert ids == set(json.loads((ROOT / "wiki/locations/red-larch/red-larch.json").read_text(encoding="utf-8"))["engine_record"]["businesses"])
    assert ids == set(json.loads((ROOT / "faerun/data/red_larch_location.json").read_text(encoding="utf-8"))["engine_record"]["businesses"])
    assert {"oneshield_quarries", "old_angraths_smokehouse", "dran_and_courtier", "blackbutter_inn"}.isdisjoint(ids)


def test_new_red_larch_businesses_are_cautious_scenarios_not_industries():
    rows = {b.id: b for b in load_businesses() if b.headquarters == "red_larch"}
    older = {"mhandyvvers_poultry", "chansyrl_fine_harness", "thelorns_safe_journeys", "luruths_tannery"}
    for business in (rows[key] for key in rows.keys() - older):
        assert business.location_addresses["red_larch"]["zip"] == "UNKNOWN"
        assert "scenario" in business.description.lower()
        assert business.employees == {"owners": 1, "managers": 0, "merchants": 0, "warehouse_staff": 0}
        assert all(stock == 1 for stock in business.inventory["red_larch"].values())
    for key in ("albaeri_mellikho_stoneworks", "tantur_smithy", "ironhead_arms", "gaelkurs", "vallivoes_sundries", "helm_at_highsun_red_larch"):
        assert rows[key].offers == {}
    settlement = next(s for s in load_settlements() if s.id == "red_larch")
    assert settlement.industries == {"craft": 1, "farm": 2, "herd": 1, "quarry": 2, "tan": 1}
