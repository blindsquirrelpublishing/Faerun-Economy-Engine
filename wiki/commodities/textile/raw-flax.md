# Raw flax

[Commodity index](../README.md) · [Textiles](README.md)

**Status:** In the engine  
**Engine ID:** `raw_flax`  
**Category:** textile  
**Trade unit:** bale (90 lb)  
**Base price:** 2.5 gp per bale (about 0.028 gp per lb)  
**Production type:** raw  
**Aurora's Whole Realms Catalogue:** listed (see below)

## Engine Description

> Amn's river-bottom flax fields feed the region's own linen trade before any of it ships raw. Cormyr's river-bottom farms grow a comparable crop, though Amn's fields still feed most of the export trade.

This is a model input stored in the catalogue, not a sourced lore claim.

## Engine Inputs

| Field | Value |
| --- | --- |
| Produced by (industry tags) | `tag_raw_flax` |
| Demand index | 1 |
| Luxury (wealth elasticity) | 0 |
| Perishable | 0 |
| Storage | 365 days capacity, 0.01% stock loss a day, 15 reserve days |

## Where the Engine Places It

Settlements carrying each producer tag: `tag_raw_flax` 2 (of 325 stored settlements).

**Dedicated `tag_raw_flax` industry at:** Athkatla (2), Suzail (2).

## Aurora's Whole Realms Catalogue

| Catalogue section | Printed page | Variant | Unit | Catalogue price | Price per lb |
| --- | --- | --- | --- | --- | --- |
| Tailors' Corner | 75 |  |  | 3 cp |  |

## Sources

- Engine record: [`faerun/data/store/commodities.json`](../../../faerun/data/store/commodities.json), with storage and recipe values as applied at load time by [`faerun/data/commodities.py`](../../../faerun/data/commodities.py). Read 2026-10-04.
- Settlement placements: [`faerun/data/store/settlements.json`](../../../faerun/data/store/settlements.json), read 2026-10-04.
- *Aurora's Whole Realms Catalogue* (TSR 9358, 1992, AD&D 2nd edition), J. Robert King and Co., design concept Anne Brown. Primary source, consulted directly from the project copy in [`.guides/`](../../../.guides/tsr09358%20-%20Aurora's_Whole_Realms_Catalogue.pdf) on 2026-10-04. Page numbers are the printed folios. Prices are the catalogue's retail mail-order prices; descriptions here are paraphrased.
