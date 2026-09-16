"""Source-specific town analyses without modifying the live economy."""

from pathlib import Path

from .daggerford import daggerford_analysis_report
from .models import Settlement


DAGGERFORD_PREVIEW = (
    Path(__file__).resolve().parent.parent
    / "daggerford_diagnostics" / "daggerford_schley_public_lightbox.jpg"
)


def settlement_analysis_report(settlement: Settlement) -> dict:
    if settlement.id != "daggerford":
        raise KeyError(f"No town analysis for {settlement.id!r}")
    image_available = DAGGERFORD_PREVIEW.is_file()
    report = daggerford_analysis_report(
        settlement, image_path=DAGGERFORD_PREVIEW if image_available else None,
    )
    report["map"]["local_image_available"] = image_available
    report["map"]["local_image_url"] = "daggerford-map.jpg" if image_available else None
    return report
