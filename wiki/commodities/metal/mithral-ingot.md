# Mithral

[Commodity index](../README.md) · [Metals](README.md)

**Status:** In the engine  
**Engine ID:** `mithral_ingot`  
**Category:** metal  
**Trade unit:** ingot (5 lb)  
**Base price:** 500 gp per ingot (about 100 gp per lb)  
**Production type:** raw  
**Aurora's Whole Realms Catalogue:** listed (see below)

## Engine Description

> Mithral is a metal good in Faerûn, traded in ingot lots for daily use, craft, and commerce. A mined or refined metal valued for armor, tools, and industry.

This is a model input stored in the catalogue, not a sourced lore claim.

## Engine Inputs

| Field | Value |
| --- | --- |
| Produced by (industry tags) | `mine_mithral` |
| Demand index | 0.04 |
| Luxury (wealth elasticity) | 0.7 |
| Perishable | 0 |
| Demand traits | `dwarven` 3, `elven` 2, `military` 2, `arcane` 1.5 |
| Storage | 365 days capacity, 0.01% stock loss a day, 15 reserve days |

## Where the Engine Places It

Settlements carrying each producer tag: `mine_mithral` 1 (of 325 stored settlements).

**Specialty at:** Mithral Hall (3).

## Aurora's Whole Realms Catalogue

**Note:** Catalogue mithral is priced well below the engine; the catalogue gives no source or purity, so this is not evidence for a change on its own.

| Catalogue section | Printed page | Variant | Unit | Catalogue price | Price per lb |
| --- | --- | --- | --- | --- | --- |
| Laborers' List (metals) | 60 | bar | 1/4 lb | 10 gp | 40 gp |
| Laborers' List (metals) | 60 | ingot | 2 lb | 35 gp | 17.5 gp |
| Laborers' List (metals) | 60 | sheet | 3 in sq | 6 gp |  |
| Laborers' List (metals) | 60 | strip | 2 by 1 in | 4 gp |  |
| Laborers' List (metals) | 60 | wire | 1 ft | 7 gp |  |

Engine price per lb is **3.48 times** the median catalogue price per lb for this entry (engine 100 gp/lb; catalogue median 28.75 gp/lb). The two are within a factor of five.

## Sources

- Engine record: [`faerun/data/store/commodities.json`](../../../faerun/data/store/commodities.json), with storage and recipe values as applied at load time by [`faerun/data/commodities.py`](../../../faerun/data/commodities.py). Read 2026-10-04.
- Settlement placements: [`faerun/data/store/settlements.json`](../../../faerun/data/store/settlements.json), read 2026-10-04.
- *Aurora's Whole Realms Catalogue* (TSR 9358, 1992, AD&D 2nd edition), J. Robert King and Co., design concept Anne Brown. Primary source, consulted directly from the project copy in [`.guides/`](../../../.guides/tsr09358%20-%20Aurora's_Whole_Realms_Catalogue.pdf) on 2026-10-04. Page numbers are the printed folios. Prices are the catalogue's retail mail-order prices; descriptions here are paraphrased.
