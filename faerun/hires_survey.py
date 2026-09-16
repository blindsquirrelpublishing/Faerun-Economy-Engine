"""Dependency-free access to the separately estimated high-resolution roof survey.

The original census, City System observations, household assumptions and world
population are deliberately neither imported nor changed by this module.
"""

from __future__ import annotations

from importlib.resources import files
import json
import math
from statistics import mean, variance


def estimate_from_sample(cells: list[dict], strata: list[dict]) -> dict:
    """Finite-population stratified difference estimate, conditional on tallies.

Auxiliary candidate counts are known for every area unit and fixed before the
sample. Each stratum is sampled without replacement. Observer interpretation
uncertainty is deliberately NOT passed off as random sampling uncertainty.
    """
    by_id = {cell["id"]: cell for cell in cells}
    if len(by_id) != len(cells):
        raise ValueError("Duplicate sampling cell")
    totals = {key: 0.0 for key in ("lower_interpretation", "preferred_count", "upper_interpretation")}
    total_variance = 0.0
    error_square_total = 0.0
    stratum_results = []
    dfs = []
    for stratum in strata:
        group = [c for c in cells if c["stratum"] == stratum["id"]]
        population_n = stratum["population_cells"]
        sample_ids = stratum["sample_ids"]
        n = stratum["sample_cells"]
        if len(group) != population_n or n != len(sample_ids) or len(set(sample_ids)) != n:
            raise ValueError("Inconsistent sampling frame")
        if not 1 <= n <= population_n:
            raise ValueError("Invalid sample size")
        selected = [by_id[key] for key in sample_ids]
        if any(c["stratum"] != stratum["id"] for c in selected):
            raise ValueError("Sample assigned to wrong stratum")
        if any(not c.get("manual") for c in selected):
            raise ValueError("Every probability-sample cell must be visually reviewed")
        for cell in selected:
            values = [cell["manual"][key] for key in totals]
            if any(isinstance(v, bool) or not isinstance(v, int) or v < 0 for v in values):
                raise ValueError("Manual counts must be nonnegative integers")
            if values != sorted(values):
                raise ValueError("Interpretation counts are out of order")
        known_count = sum(c["candidate_count"] for c in group)
        if known_count != stratum["candidate_count"]:
            raise ValueError("Stratum auxiliary total mismatch")
        for key in totals:
            residuals = [c["manual"][key] - c["candidate_count"] for c in selected]
            totals[key] += known_count + population_n * mean(residuals)
        residuals = [c["manual"]["preferred_count"] - c["candidate_count"] for c in selected]
        if n < population_n and n < 2:
            raise ValueError("At least two sampled cells required for variance")
        sample_var = variance(residuals) if n > 1 else 0.0
        component = population_n ** 2 * (1 - n / population_n) * sample_var / n
        total_variance += component
        error_square_total += population_n * mean([r * r for r in residuals])
        if component > 0:
            dfs.append(n - 1)
        stratum_results.append({
            "id": stratum["id"], "population_cells": population_n, "sample_cells": n,
            "sample_candidate_count": sum(c["candidate_count"] for c in selected),
            "sample_preferred_roof_count": sum(c["manual"]["preferred_count"] for c in selected),
            "mean_correction_per_cell": mean(residuals),
            "sample_residual_variance": sample_var,
            "variance_contribution": component,
            "estimated_roof_count": known_count + population_n * mean(residuals),
        })
    if sum(s["population_cells"] for s in strata) != len(cells):
        raise ValueError("Strata do not partition the complete sampling frame")
    # Conservative choice rather than claiming exact t-distributed survey errors.
    criticals = {1: 12.706205, 2: 4.302653, 3: 3.182446, 4: 2.776445,
                 5: 2.570582, 6: 2.446912, 7: 2.364625, 8: 2.306005,
                 9: 2.262157, 10: 2.228139}
    df = min(dfs) if dfs else None
    critical = criticals[min(df, 10)] if df else 0.0
    se = math.sqrt(total_variance)
    preferred = totals["preferred_count"]
    return {
        "status": "provisional_probability_sample_estimate",
        "unit": "depicted_roof_structures_building_proxy",
        "value": round(preferred, 2),
        "rounded_estimate": round(preferred),
        "exact_building_count": None,
        "population_estimate": None,
        "method": "T_hat = C_total + sum_h N_h * mean_sample(y_i - c_i)",
        "variance_method": "sum_h N_h^2 * (1 - n_h/N_h) * s_h^2(y-c) / n_h",
        "standard_error": round(se, 3),
        "sampling_interval": {
            "lower": round(max(0, preferred - critical * se), 2),
            "upper": round(preferred + critical * se, 2),
            "nominal_confidence_level": 0.95,
            "method": "Approximate design-based t interval; conservative minimum stratum degrees of freedom",
            "degrees_of_freedom": df,
            "critical_value": critical,
            "conditional_on": "Fixed visual preferred-count interpretation and traced inclusion boundary; not a guarantee of true building-count coverage.",
            "includes_observer_or_map_omission_error": False,
        },
        "interpretation_sensitivity": {
            "lower": round(totals["lower_interpretation"], 2),
            "upper": round(totals["upper_interpretation"], 2),
            "is_confidence_interval": False,
            "is_rigorous_bound": False,
            "meaning": "Recalculate the same estimator with every sample's coarser/finer plausible roof interpretation. Labels, wings and edge-centers affect this range.",
        },
        "strata": stratum_results,
        "weighted_count_error_rmse_per_cell": round(math.sqrt(error_square_total / len(cells)), 3),
        "warning": "A citywide estimate of map roof symbols, NOT a complete visual building enumeration, cadastral census, or population estimate.",
    }


def waterdeep_hires_report() -> dict:
    """Return native-pixel feature list and boundary geometry, without image deps.

    Richer audit, source and uncertainty metadata is retained alongside the UI
    contract. Unknown candidate wards remain null rather than inferred.
    """
    resource = files("faerun").joinpath("data", "waterdeep_hires_survey.json")
    report = json.loads(resource.read_text(encoding="utf-8"))
    if report.get("schema_version") != 2:
        raise ValueError("Unsupported high-resolution survey schema")
    if report.get("coordinate_system", {}).get("name") != "original_image_pixels":
        raise ValueError("Survey geometry must use original image pixels")
    if report.get("coordinate_space") != {
        "width": 3560, "height": 7256, "units": "image_pixels", "origin": "top_left"
    }:
        raise ValueError("Unexpected survey coordinate space")
    if report["boundary"]["type"] not in ("Polygon", "MultiPolygon"):
        raise ValueError("Survey boundary must be polygon geometry")
    features = report["features"]
    if not isinstance(features, list):
        raise ValueError("Survey features must be a list")
    if any(feature["type"] != "Feature" or feature["geometry"]["type"] not in ("Polygon", "MultiPolygon")
           for feature in features):
        raise ValueError("Survey candidates must be polygon features")
    if len(features) != report["detector"]["candidate_count"]:
        raise ValueError("Survey candidate count mismatch")
    if len({feature["id"] for feature in features}) != len(features):
        raise ValueError("Duplicate survey candidate ID")
    if any(feature["properties"].get("verified") for feature in features):
        raise ValueError("Automatic survey candidates must not be marked verified")
    return report
