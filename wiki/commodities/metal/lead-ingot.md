# Lead

[Commodity index](../README.md) · [Metals](README.md)

**Status:** In the engine  
**Engine ID:** `lead_ingot`  
**Category:** metal  
**Trade unit:** ingot (10 lb)  
**Base price:** 1.5 gp per ingot (about 0.15 gp per lb)  
**Production type:** raw  
**Aurora's Whole Realms Catalogue:** listed (see below)

## Engine Description

> Lead is a metal good in Faerûn, traded in ingot lots for daily use, craft, and commerce. A mined or refined metal valued for armor, tools, and industry.

This is a model input stored in the catalogue, not a sourced lore claim.

## Engine Inputs

| Field | Value |
| --- | --- |
| Produced by (industry tags) | `mine_copper`, `mine_silver` |
| Demand index | 0.3 |
| Luxury (wealth elasticity) | 0 |
| Perishable | 0 |
| Storage | 365 days capacity, 0.01% stock loss a day, 15 reserve days |

## Where the Engine Places It

Settlements carrying each producer tag: `mine_copper` 1, `mine_silver` 3 (of 325 stored settlements).

## Aurora's Whole Realms Catalogue

| Catalogue section | Printed page | Variant | Unit | Catalogue price | Price per lb |
| --- | --- | --- | --- | --- | --- |
| Priests' Alcove (spell components) | 36 | ball | 1 in | 6 cp |  |
| Priests' Alcove (spell components) | 36 | chunk | 5 oz | 8 cp | 0.256 gp |
| Wizards' Laboratory (components cache) | 48 | Lead chunk | 1 in cu | 6 cp |  |
| Laborers' List (metals) | 60 | bar | 2 lb | 7 cp | 0.035 gp |
| Laborers' List (metals) | 60 | ingot | 10 lb | 5 sp | 0.05 gp |
| Laborers' List (metals) | 60 | sheet | 5 in sq | 4 cp |  |
| Laborers' List (metals) | 60 | strip | 4 by 1 in | 3 cp |  |
| Laborers' List (metals) | 60 | wire | 1 ft | 4 cp |  |

Engine price per lb is **3.53 times** the median catalogue price per lb for this entry (engine 0.15 gp/lb; catalogue median 0.043 gp/lb). The two are within a factor of five.

## Sources

- Engine record: [`faerun/data/store/commodities.json`](../../../faerun/data/store/commodities.json), with storage and recipe values as applied at load time by [`faerun/data/commodities.py`](../../../faerun/data/commodities.py). Read 2026-10-04.
- Settlement placements: [`faerun/data/store/settlements.json`](../../../faerun/data/store/settlements.json), read 2026-10-04.
- *Aurora's Whole Realms Catalogue* (TSR 9358, 1992, AD&D 2nd edition), J. Robert King and Co., design concept Anne Brown. Primary source, consulted directly from the project copy in [`.guides/`](../../../.guides/tsr09358%20-%20Aurora's_Whole_Realms_Catalogue.pdf) on 2026-10-04. Page numbers are the printed folios. Prices are the catalogue's retail mail-order prices; descriptions here are paraphrased.
