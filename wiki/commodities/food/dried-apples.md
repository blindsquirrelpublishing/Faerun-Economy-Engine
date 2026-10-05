# Dried apples

[Commodity index](../README.md) · [Food](README.md)

**Status:** In the engine  
**Engine ID:** `dried_apples`  
**Category:** food  
**Trade unit:** crate (18 lb)  
**Base price:** 2 gp per crate (about 0.111 gp per lb)  
**Production type:** raw  
**Aurora's Whole Realms Catalogue:** listed (see below)

## Engine Description

> Ring-sliced and air-dried in the Dalelands before the caravan season starts.

This is a model input stored in the catalogue, not a sourced lore claim.

## Engine Inputs

| Field | Value |
| --- | --- |
| Produced by (industry tags) | `tag_dried_apples` |
| Demand index | 1 |
| Luxury (wealth elasticity) | 0 |
| Perishable | 0.05 |
| Storage | 365 days capacity, 0.01% stock loss a day, 15 reserve days |

## Where the Engine Places It

Settlements carrying each producer tag: `tag_dried_apples` 1 (of 325 stored settlements).

**Dedicated `tag_dried_apples` industry at:** Highmoon (2).

## Aurora's Whole Realms Catalogue

| Catalogue section | Printed page | Variant | Unit | Catalogue price | Price per lb |
| --- | --- | --- | --- | --- | --- |
| Aurora's Larder | 116 |  | lb. | 1 gp | 1 gp |

Engine price per lb is **0.111 times** the median catalogue price per lb for this entry (engine 0.111 gp/lb; catalogue median 1 gp/lb). The catalogue is far above the engine here, which is normal for its retail luxury pricing.

## Sources

- Engine record: [`faerun/data/store/commodities.json`](../../../faerun/data/store/commodities.json), with storage and recipe values as applied at load time by [`faerun/data/commodities.py`](../../../faerun/data/commodities.py). Read 2026-10-04.
- Settlement placements: [`faerun/data/store/settlements.json`](../../../faerun/data/store/settlements.json), read 2026-10-04.
- *Aurora's Whole Realms Catalogue* (TSR 9358, 1992, AD&D 2nd edition), J. Robert King and Co., design concept Anne Brown. Primary source, consulted directly from the project copy in [`.guides/`](../../../.guides/tsr09358%20-%20Aurora's_Whole_Realms_Catalogue.pdf) on 2026-10-04. Page numbers are the printed folios. Prices are the catalogue's retail mail-order prices; descriptions here are paraphrased.
