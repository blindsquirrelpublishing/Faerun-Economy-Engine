"""Reproduce Daggerford evidence checks and optional local visual annotations.

Run from the project root:
    .venv\\Scripts\\python.exe tools\\survey_daggerford.py
    .venv\\Scripts\\python.exe tools\\survey_daggerford.py --download --annotate

The optional download is the image already publicly linked by its cartographer.
It does not seek an unlinked high-resolution asset or download licensed books.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys
from urllib.request import urlopen

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from faerun.daggerford import daggerford_analysis_report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--download", action="store_true", help="Download the author-linked public preview")
    parser.add_argument("--annotate", action="store_true", help="Create local audit overlays (requires existing Pillow)")
    parser.add_argument("--output-dir", type=Path, default=Path("daggerford_diagnostics"))
    args = parser.parse_args(argv)
    output = args.output_dir.resolve()
    if not output.is_relative_to(Path.cwd().resolve()):
        parser.error("Diagnostic output must remain inside the current project directory")
    report = daggerford_analysis_report()
    image_path = output / "daggerford_schley_public_lightbox.jpg"
    if args.download:
        with urlopen(report["map"]["image_url"], timeout=45) as response:
            content = response.read()
        if hashlib.sha256(content).hexdigest() != report["map"]["sha256"]:
            raise ValueError("Author preview changed: do not reuse the existing coordinate survey")
        output.mkdir(parents=True, exist_ok=True)
        image_path.write_bytes(content)
    if image_path.exists():
        report = daggerford_analysis_report(image_path=image_path)
    if args.annotate:
        if not image_path.exists():
            parser.error("Annotation requires the existing public preview or --download")
        from PIL import Image, ImageDraw, ImageFont

        image = Image.open(image_path).convert("RGB")
        if list(image.size) != [report["map"]["width_px"], report["map"]["height_px"]]:
            raise ValueError("Source dimensions changed")
        image = image.resize((image.width * 3, image.height * 3))
        draw = ImageDraw.Draw(image)
        font = ImageFont.load_default(size=15)
        for sector, rows in report["roof_groups"].items():
            for identity, x, y, _ in rows:
                color = "#ff00ff" if sector == "riverfront" else "#003cff"
                x, y = x * 3, y * 3
                draw.ellipse((x - 5, y - 5, x + 5, y + 5), fill=color)
                draw.text((x + 5, y - 12), identity, fill=color, font=font,
                          stroke_width=1, stroke_fill="white")
        for item in report["unresolved_symbols"]:
            x, y = (coordinate * 3 for coordinate in item["point"])
            draw.text((x, y), item["id"], fill="#b00000", font=font, stroke_width=1, stroke_fill="white")
        output.mkdir(parents=True, exist_ok=True)
        image.save(output / "daggerford_roof_groups_audit.jpg", quality=95)
        image = Image.open(image_path).convert("RGB").resize((2592, 3630))
        draw = ImageDraw.Draw(image)
        for polygon in report["scope"]["polygons_px"].values():
            points = [(x * 3, y * 3) for x, y in polygon]
            draw.line(points + [points[0]], fill="#a600e0", width=4)
        for street in report["streets"]:
            draw.line([(x * 3, y * 3) for x, y in street["points"]], fill="#0050d0", width=4)
        image.save(output / "daggerford_streets_boundary_audit.jpg", quality=95)
    output.mkdir(parents=True, exist_ok=True)
    (output / "daggerford_report.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "active_residents": report["active_baseline"]["resident_population"],
        "inventory": report["inventory_summary"],
        "geometry": report["geometry"],
        "source_hash": report["map"]["source_hash_verification"]["status"],
        "report": str(output / "daggerford_report.json"),
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
