# Raw wool

[Commodity index](../README.md) · [Textiles](README.md)

**Status:** In the engine  
**Engine ID:** `raw_wool`  
**Category:** textile  
**Trade unit:** bale (100 lb)  
**Base price:** 2.5 gp per bale (about 0.025 gp per lb)  
**Production type:** raw  
**Aurora's Whole Realms Catalogue:** listed (see below)

## Engine Description

> The Vast's open grasslands support herding on a scale most of the Sword Coast can't match. Western Heartlands flocks add meaningfully to supply during good grazing years.

This is a model input stored in the catalogue, not a sourced lore claim.

## Engine Inputs

| Field | Value |
| --- | --- |
| Produced by (industry tags) | `tag_raw_wool` |
| Demand index | 1 |
| Luxury (wealth elasticity) | 0 |
| Perishable | 0 |
| Storage | 365 days capacity, 0.01% stock loss a day, 15 reserve days |

## Where the Engine Places It

Settlements carrying each producer tag: `tag_raw_wool` 2 (of 325 stored settlements).

**Dedicated `tag_raw_wool` industry at:** Ravens Bluff (2), Scornubel (2).

## Aurora's Whole Realms Catalogue

| Catalogue section | Printed page | Variant | Unit | Catalogue price | Price per lb |
| --- | --- | --- | --- | --- | --- |
| Tailors' Corner | 75 |  | sq yd | 2 cp/lb | 0.02 gp |

Engine price per lb is **1.25 times** the median catalogue price per lb for this entry (engine 0.025 gp/lb; catalogue median 0.02 gp/lb). The two are within a factor of five.

## Sources

- Engine record: [`faerun/data/store/commodities.json`](../../../faerun/data/store/commodities.json), with storage and recipe values as applied at load time by [`faerun/data/commodities.py`](../../../faerun/data/commodities.py). Read 2026-10-04.
- Settlement placements: [`faerun/data/store/settlements.json`](../../../faerun/data/store/settlements.json), read 2026-10-04.
- *Aurora's Whole Realms Catalogue* (TSR 9358, 1992, AD&D 2nd edition), J. Robert King and Co., design concept Anne Brown. Primary source, consulted directly from the project copy in [`.guides/`](../../../.guides/tsr09358%20-%20Aurora's_Whole_Realms_Catalogue.pdf) on 2026-10-04. Page numbers are the printed folios. Prices are the catalogue's retail mail-order prices; descriptions here are paraphrased.
