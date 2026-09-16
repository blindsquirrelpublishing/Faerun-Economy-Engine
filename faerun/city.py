"""Read-only, source-linked city directories; never added to live stock or prices."""

from copy import deepcopy
from dataclasses import asdict

from .models import slugify


def city_directory(
    settlement: str = "Waterdeep",
    *,
    search: str = "",
    ward: str = "",
    kind: str = "all",
    category: str = "",
) -> dict:
    """Query the historical catalogue, including bidirectional affiliations.

    Ward and category filters are exact names or underscore IDs. Search matches
    an entry's own fields and its directly affiliated people or businesses.
    Person wards describe affiliations, not verified home addresses.
    """
    from .data.waterdeep import BUSINESSES, PEOPLE, SOURCE, WARDS

    if slugify(settlement) != "waterdeep":
        raise KeyError(f"No historical city directory for {settlement!r}")
    kind = kind.strip().lower()
    if kind not in {"all", "business", "person"}:
        raise ValueError("kind must be all, business, or person")
    ward_names = {slugify(name): name for name in WARDS}
    # The existing atlas uses South Ward; the guide calls it Southern Ward.
    if "southern_ward" in ward_names:
        ward_names["south_ward"] = ward_names["southern_ward"]
    ward_id = slugify(ward)
    if ward_id and ward_id not in ward_names:
        raise ValueError(f"Unknown directory ward: {ward}")
    selected_ward = ward_names.get(ward_id)
    categories = sorted({business.category for business in BUSINESSES})
    category_names = {slugify(name): name for name in categories}
    category_id = slugify(category)
    if category_id and category_id not in category_names:
        raise ValueError(f"Unknown directory category: {category}")
    selected_category = category_names.get(category_id)
    businesses = {entry.id: asdict(entry) for entry in BUSINESSES}
    people = {entry.id: asdict(entry) for entry in PEOPLE}

    for business in businesses.values():
        business["people"] = []
        business["record_kind"] = "business"
    for person in people.values():
        person["record_kind"] = "person"
        for affiliation in person["affiliations"]:
            business = businesses[affiliation["business_id"]]
            affiliation["business_name"] = business["name"]
            affiliation["ward"] = business["ward"]
            affiliation["category"] = business["category"]
            business["people"].append({
                "person_id": person["id"],
                "name": person["name"],
                "role": affiliation["role"],
                "citations": deepcopy(affiliation["citations"]),
            })
        person["wards"] = sorted({a["ward"] for a in person["affiliations"]})

    wanted = slugify(search)

    def matches_text(parts: list[str]) -> bool:
        return not wanted or wanted in slugify(" ".join(parts))

    def business_matches(business: dict) -> bool:
        return (
            (not selected_ward or business["ward"] == selected_ward)
            and (not selected_category or business["category"] == selected_category)
            and matches_text([
                business["id"], business["name"], business["ward"],
                business["category"], business["summary"], business["address"] or "",
                *business["services"],
                *[p["name"] + " " + p["role"] for p in business["people"]],
            ])
        )

    def person_matches(person: dict) -> bool:
        affiliations = person["affiliations"]
        return (
            any(
                (not selected_ward or a["ward"] == selected_ward)
                and (not selected_category or a["category"] == selected_category)
                for a in affiliations
            )
            and matches_text([
                person["id"], person["name"], person["summary"],
                *[
                    " ".join((
                        a["business_name"], a["role"], a["ward"], a["category"],
                        *businesses[a["business_id"]]["services"],
                    ))
                    for a in affiliations
                ],
            ])
        )

    selected_businesses = sorted(
        (b for b in businesses.values() if business_matches(b) and kind != "person"),
        key=lambda b: b["name"],
    )
    selected_people = sorted(
        (p for p in people.values() if person_matches(p) and kind != "business"),
        key=lambda p: p["name"],
    )
    return {
        "settlement_id": "waterdeep",
        "name": "Waterdeep historical city directory",
        "historical": True,
        "live_market_integration": False,
        "source": deepcopy(SOURCE),
        "scope_note": (
            "A curated selection, not an exhaustive census of the guide or city. "
            "Roles describe the guide's account, not verified activity in 1492 DR. "
            "People's wards are business affiliations, not residential addresses. "
            "Categories and service labels are editorial classifications. "
            "No stock, prices, revenue, staffing totals or exact map coordinates "
            "are inferred; existing atlas markers are a separate illustrative layer."
        ),
        "filters": {"search": search.strip(), "ward": selected_ward,
                    "kind": kind, "category": selected_category},
        "wards": [
            {"id": slugify(name), "name": name,
             "business_count": sum(b.ward == name for b in BUSINESSES),
             "people_count": sum(name in p["wards"] for p in people.values())}
            for name in WARDS
        ],
        "categories": categories,
        "totals": {"businesses": len(BUSINESSES), "people": len(PEOPLE)},
        "counts": {"businesses": len(selected_businesses), "people": len(selected_people)},
        "businesses": selected_businesses,
        "people": selected_people,
    }
