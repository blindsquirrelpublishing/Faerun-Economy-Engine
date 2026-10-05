# Raw furs

[Commodity index](../README.md) · [Textiles](README.md)

**Status:** In the engine  
**Engine ID:** `raw_furs`  
**Category:** textile  
**Trade unit:** bundle (25 lb)  
**Base price:** 12 gp per bundle (about 0.48 gp per lb)  
**Production type:** raw  
**Aurora's Whole Realms Catalogue:** no matching entry in the sections reviewed

## Engine Description

> Untreated pelts off the Rashemen border, bundled and sold onward through Thesk's caravan markets. Icewind Dale trappers supply a heavier, colder-climate pelt alongside Thesk's Rashemen-border stock.

This is a model input stored in the catalogue, not a sourced lore claim.

## Engine Inputs

| Field | Value |
| --- | --- |
| Produced by (industry tags) | `tag_raw_furs` |
| Demand index | 1 |
| Luxury (wealth elasticity) | 0.2 |
| Perishable | 0 |
| Storage | 365 days capacity, 0.01% stock loss a day, 15 reserve days |

## Where the Engine Places It

Settlements carrying each producer tag: `tag_raw_furs` 2 (of 325 stored settlements).

**Dedicated `tag_raw_furs` industry at:** Bryn Shander (2), Telflamm (2).

## Sources

- Engine record: [`faerun/data/store/commodities.json`](../../../faerun/data/store/commodities.json), with storage and recipe values as applied at load time by [`faerun/data/commodities.py`](../../../faerun/data/commodities.py). Read 2026-10-04.
- Settlement placements: [`faerun/data/store/settlements.json`](../../../faerun/data/store/settlements.json), read 2026-10-04.
