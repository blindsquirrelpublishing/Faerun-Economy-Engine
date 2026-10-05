# Dried pears

[Commodity index](../README.md) · [Food](README.md)

**Status:** In the engine  
**Engine ID:** `dried_pears`  
**Category:** food  
**Trade unit:** crate (18 lb)  
**Base price:** 2.2 gp per crate (about 0.122 gp per lb)  
**Production type:** raw  
**Aurora's Whole Realms Catalogue:** listed (see below)

## Engine Description

> Halved and dried on racks across the Vast's grassland orchards.

This is a model input stored in the catalogue, not a sourced lore claim.

## Engine Inputs

| Field | Value |
| --- | --- |
| Produced by (industry tags) | `tag_dried_pears` |
| Demand index | 1 |
| Luxury (wealth elasticity) | 0 |
| Perishable | 0.05 |
| Storage | 365 days capacity, 0.01% stock loss a day, 15 reserve days |

## Where the Engine Places It

Settlements carrying each producer tag: `tag_dried_pears` 1 (of 325 stored settlements).

**Dedicated `tag_dried_pears` industry at:** Ravens Bluff (2).

## Aurora's Whole Realms Catalogue

| Catalogue section | Printed page | Variant | Unit | Catalogue price | Price per lb |
| --- | --- | --- | --- | --- | --- |
| Aurora's Larder | 116 |  | lb. | 5 gp | 5 gp |

Engine price per lb is **0.0244 times** the median catalogue price per lb for this entry (engine 0.122 gp/lb; catalogue median 5 gp/lb). The catalogue is far above the engine here, which is normal for its retail luxury pricing.

## Sources

- Engine record: [`faerun/data/store/commodities.json`](../../../faerun/data/store/commodities.json), with storage and recipe values as applied at load time by [`faerun/data/commodities.py`](../../../faerun/data/commodities.py). Read 2026-10-04.
- Settlement placements: [`faerun/data/store/settlements.json`](../../../faerun/data/store/settlements.json), read 2026-10-04.
- *Aurora's Whole Realms Catalogue* (TSR 9358, 1992, AD&D 2nd edition), J. Robert King and Co., design concept Anne Brown. Primary source, consulted directly from the project copy in [`.guides/`](../../../.guides/tsr09358%20-%20Aurora's_Whole_Realms_Catalogue.pdf) on 2026-10-04. Page numbers are the printed folios. Prices are the catalogue's retail mail-order prices; descriptions here are paraphrased.
