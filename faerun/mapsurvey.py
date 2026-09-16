"""Read-only, paged access to the two independent city-map evidence layers."""

from __future__ import annotations

def _load_survey(layer: str) -> dict:
    if layer == "streets":
        from .streets import waterdeep_streets_report

        return waterdeep_streets_report()
    from .hires_survey import waterdeep_hires_report

    return waterdeep_hires_report()


def map_survey_report(
    layer: str, settlement_id: str = "waterdeep", *, search: str = "",
    offset: int = 0, limit: int | None = None, include_features: bool = True,
) -> dict:
    if settlement_id != "waterdeep":
        raise KeyError(f"No city-map survey for {settlement_id!r}")
    if layer not in ("streets", "roofs"):
        raise ValueError("Map layer must be streets or roofs")
    if not isinstance(search, str):
        raise ValueError("Survey search must be text")
    if isinstance(offset, bool) or not isinstance(offset, int) or offset < 0:
        raise ValueError("Survey offset must be a nonnegative integer")
    if limit is not None and (isinstance(limit, bool) or not isinstance(limit, int) or limit < 1):
        raise ValueError("Survey limit must be a positive integer")
    if not isinstance(include_features, bool):
        raise ValueError("include_features must be a boolean")
    report = _load_survey(layer)
    query = search.strip().casefold()
    matched = [
        feature for feature in report["features"]
        if not query or query in feature["id"].casefold()
        or query in (feature["properties"].get("name") or "").casefold()
    ]
    page = matched[offset:None if limit is None else offset + limit] if include_features else []
    next_offset = offset + len(page)
    return {
        **report,
        "features": page,
        "selection": {
            "layer": layer, "search": search, "total_records": len(report["features"]),
            "matched_records": len(matched), "returned_records": len(page),
            "features_included": include_features, "offset": offset, "limit": limit,
            "next_offset": next_offset if include_features and next_offset < len(matched) else None,
            "note": "Coverage describes the full source layer, not just this filtered page.",
        },
    }
