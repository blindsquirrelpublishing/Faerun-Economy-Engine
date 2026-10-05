# Steel billet

[Commodity index](../README.md) · [Metals](README.md)

**Status:** In the engine  
**Engine ID:** `steel_ingot`  
**Category:** metal  
**Trade unit:** ingot (10 lb)  
**Base price:** 3 gp per ingot (about 0.3 gp per lb)  
**Production type:** processed or manufactured  
**Aurora's Whole Realms Catalogue:** listed (see below)

## Engine Description

> Steel billet is a metal good in Faerûn, traded in ingot lots for daily use, craft, and commerce. A mineral or refined metal traded for tools, industry, and coinage.

This is a model input stored in the catalogue, not a sourced lore claim.

## Engine Inputs

| Field | Value |
| --- | --- |
| Produced by (industry tags) | `smith` |
| Required skill | `smith` 2 |
| Demand index | 1 |
| Luxury (wealth elasticity) | 0 |
| Perishable | 0 |
| Demand traits | `military` 2, `dwarven` 1.6, `frontier` 1.3 |
| Storage | 365 days capacity, 0.01% stock loss a day, 15 reserve days |

## Recipe Links

Inputs for one ingot: [Wrought iron](../metal/iron-ingot.md) 1, [Coal](../metal/coal.md) 0.04.

Used as an input for: [Chain mail](../arms/armor-chain.md) (5.5 per unit), [Plate armor](../arms/armor-plate.md) (6.5 per unit), [Arrows](../arms/arrows.md) (0.03 per unit), [Battleaxe](../arms/axe-battle.md) (0.35 per unit), [Crossbow](../arms/crossbow.md) (0.2 per unit), [Dagger](../arms/dagger.md) (0.12 per unit), [Spear](../arms/spear.md) (0.08 per unit), [Longsword](../arms/sword.md) (0.3 per unit), [Artisan's tools](../product/tools-carpenter.md) (1 per unit).

## Where the Engine Places It

Settlements carrying each producer tag: `smith` 33 (of 325 stored settlements).

**Specialty at:** Citadel Adbar (3), Gracklstugh (3), Melvaunt (2), Mirabar (2), Mithral Hall (2).

## Aurora's Whole Realms Catalogue

| Catalogue section | Printed page | Variant | Unit | Catalogue price | Price per lb |
| --- | --- | --- | --- | --- | --- |
| Priests' Alcove (spell components) | 36 | chunk | 1 oz | 1 sp | 1.6 gp |
| Priests' Alcove (spell components) | 36 | cube | 1 in | 3 sp |  |
| Priests' Alcove (spell components) | 36 | sheet | 1 ft sq | 1 gp |  |
| Wizards' Laboratory (components cache) | 48 | Steel sheet | 1 ft sq | 1 gp |  |
| Laborers' List (metals) | 60 | bar | 1 lb | 3 sp | 0.3 gp |
| Laborers' List (metals) | 60 | ingot | 5 lb | 8 sp | 0.16 gp |
| Laborers' List (metals) | 60 | sheet | 1 ft sq | 3 sp |  |
| Laborers' List (metals) | 60 | strip | 6 by 1 in | 5 cp |  |
| Laborers' List (metals) | 60 | wire | 1 ft | 3 cp |  |

Engine price per lb is **1.3 times** the median catalogue price per lb for this entry (engine 0.3 gp/lb; catalogue median 0.23 gp/lb). The two are within a factor of five.

## Sources

- Engine record: [`faerun/data/store/commodities.json`](../../../faerun/data/store/commodities.json), with storage and recipe values as applied at load time by [`faerun/data/commodities.py`](../../../faerun/data/commodities.py). Read 2026-10-04.
- Settlement placements: [`faerun/data/store/settlements.json`](../../../faerun/data/store/settlements.json), read 2026-10-04.
- *Aurora's Whole Realms Catalogue* (TSR 9358, 1992, AD&D 2nd edition), J. Robert King and Co., design concept Anne Brown. Primary source, consulted directly from the project copy in [`.guides/`](../../../.guides/tsr09358%20-%20Aurora's_Whole_Realms_Catalogue.pdf) on 2026-10-04. Page numbers are the printed folios. Prices are the catalogue's retail mail-order prices; descriptions here are paraphrased.
