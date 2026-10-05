# Tin

[Commodity index](../README.md) · [Metals](README.md)

**Status:** In the engine  
**Engine ID:** `tin_ingot`  
**Category:** metal  
**Trade unit:** ingot (10 lb)  
**Base price:** 6 gp per ingot (about 0.6 gp per lb)  
**Production type:** raw  
**Aurora's Whole Realms Catalogue:** listed (see below)

## Engine Description

> Tin is a metal good in Faerûn, traded in ingot lots for daily use, craft, and commerce. A mined or refined metal valued for armor, tools, and industry.

This is a model input stored in the catalogue, not a sourced lore claim.

## Engine Inputs

| Field | Value |
| --- | --- |
| Produced by (industry tags) | `mine_tin`, `smith` |
| Demand index | 0.35 |
| Luxury (wealth elasticity) | 0 |
| Perishable | 0 |
| Storage | 365 days capacity, 0.01% stock loss a day, 15 reserve days |

## Where the Engine Places It

Settlements carrying each producer tag: `mine_tin` 0, `smith` 33 (of 325 stored settlements).

## Aurora's Whole Realms Catalogue

| Catalogue section | Printed page | Variant | Unit | Catalogue price | Price per lb |
| --- | --- | --- | --- | --- | --- |
| Wizards' Laboratory (components cache) | 48 | Tin square | 1 in | 5 cp |  |
| Laborers' List (metals) | 60 | bar | 1 lb | 2 sp | 0.2 gp |
| Laborers' List (metals) | 60 | ingot | 5 lb | 5 sp | 0.1 gp |
| Laborers' List (metals) | 60 | sheet | 1 ft sq | 2 sp |  |
| Laborers' List (metals) | 60 | strip | 6 by 1 in | 3 cp |  |
| Laborers' List (metals) | 60 | wire | 1 ft | 1 cp |  |

Engine price per lb is **4 times** the median catalogue price per lb for this entry (engine 0.6 gp/lb; catalogue median 0.15 gp/lb). The two are within a factor of five.

## Sources

- Engine record: [`faerun/data/store/commodities.json`](../../../faerun/data/store/commodities.json), with storage and recipe values as applied at load time by [`faerun/data/commodities.py`](../../../faerun/data/commodities.py). Read 2026-10-04.
- Settlement placements: [`faerun/data/store/settlements.json`](../../../faerun/data/store/settlements.json), read 2026-10-04.
- *Aurora's Whole Realms Catalogue* (TSR 9358, 1992, AD&D 2nd edition), J. Robert King and Co., design concept Anne Brown. Primary source, consulted directly from the project copy in [`.guides/`](../../../.guides/tsr09358%20-%20Aurora's_Whole_Realms_Catalogue.pdf) on 2026-10-04. Page numbers are the printed folios. Prices are the catalogue's retail mail-order prices; descriptions here are paraphrased.
