# Bronze

[Commodity index](../README.md) · [Metals](README.md)

**Status:** In the engine  
**Engine ID:** `bronze`  
**Category:** metal  
**Trade unit:** ingot (10 lb)  
**Base price:** 8.5 gp per ingot (about 0.85 gp per lb)  
**Production type:** raw  
**Aurora's Whole Realms Catalogue:** listed (see below)

## Engine Description

> An alloy from Chessentan foundries with a closely guarded tin ratio.

This is a model input stored in the catalogue, not a sourced lore claim.

## Engine Inputs

| Field | Value |
| --- | --- |
| Produced by (industry tags) | `tag_bronze` |
| Demand index | 1 |
| Luxury (wealth elasticity) | 0 |
| Perishable | 0 |
| Storage | 365 days capacity, 0.01% stock loss a day, 15 reserve days |

## Where the Engine Places It

Settlements carrying each producer tag: `tag_bronze` 1 (of 325 stored settlements).

**Dedicated `tag_bronze` industry at:** Mordulkin (2).

## Aurora's Whole Realms Catalogue

| Catalogue section | Printed page | Variant | Unit | Catalogue price | Price per lb |
| --- | --- | --- | --- | --- | --- |
| Priests' Alcove (spell components) | 36 | Bronze die | 3 oz | 6 sp | 3.2 gp |
| Wizards' Laboratory (components cache) | 48 | Bronze, disk | 2 oz | 5 sp | 4 gp |
| Laborers' List (metals) | 60 | bar | 1 lb | 7 cp | 0.07 gp |
| Laborers' List (metals) | 60 | ingot | 5 lb | 2 sp | 0.04 gp |
| Laborers' List (metals) | 60 | sheet | 16 in sq | 1 sp |  |
| Laborers' List (metals) | 60 | strip | 4 by 2 in | 2 cp |  |
| Laborers' List (metals) | 60 | wire | 1 ft | 3 cp |  |

Engine price per lb is **15.5 times** the median catalogue price per lb for this entry (engine 0.85 gp/lb; catalogue median 0.055 gp/lb). The catalogue is below the engine here; worth a look during the commodity review.

## Sources

- Engine record: [`faerun/data/store/commodities.json`](../../../faerun/data/store/commodities.json), with storage and recipe values as applied at load time by [`faerun/data/commodities.py`](../../../faerun/data/commodities.py). Read 2026-10-04.
- Settlement placements: [`faerun/data/store/settlements.json`](../../../faerun/data/store/settlements.json), read 2026-10-04.
- *Aurora's Whole Realms Catalogue* (TSR 9358, 1992, AD&D 2nd edition), J. Robert King and Co., design concept Anne Brown. Primary source, consulted directly from the project copy in [`.guides/`](../../../.guides/tsr09358%20-%20Aurora's_Whole_Realms_Catalogue.pdf) on 2026-10-04. Page numbers are the printed folios. Prices are the catalogue's retail mail-order prices; descriptions here are paraphrased.
