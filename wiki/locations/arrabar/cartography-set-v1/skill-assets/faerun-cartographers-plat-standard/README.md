# Faerûn Cartographers Plat Standard v1.8

A reusable format/composition skill, complementary to the Fantasy Land-Water Boundary Master and specialized map-drawing skills.

Contents:
- `SKILL.md` — authoritative skill behavior and QA gates.
- `references/plat-spec-v1.8.json` — machine-readable dimensions and typesetting.
- `references/example-plate-metadata.json` — example to adapt per map.
- `templates/blank-plat-v1.8.svg` — physical-size SVG frame, 17×16 *square* grid, and official unchanged seal referenced as a relative asset.
- `assets/faerun-cartographers-official-red-seal.png` — official circular stamp source, copied without altering its pixels.
- `scripts/validate_plat.py` — structural layout and actual numeric scale validation.

To view the SVG with the stamp visible, retain the package directory structure because the template references the stamp PNG via a relative path. No source geography is baked into the blank frame. For detailed maps, fill the map area from a separately approved boundary master.
