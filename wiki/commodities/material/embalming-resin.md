# Embalming resin

[Commodity index](../README.md) · [Materials](README.md)

**Status:** In the engine  
**Engine ID:** `embalming_resin`  
**Category:** material  
**Trade unit:** block (5 lb)  
**Base price:** 22 gp per block (about 4.4 gp per lb)  
**Production type:** raw  
**Aurora's Whole Realms Catalogue:** no matching entry in the sections reviewed

## Engine Description

> Preservation resin used in Mulhorandi funerary rites; the source tree grows only along the River of Swords.

This is a model input stored in the catalogue, not a sourced lore claim.

## Engine Inputs

| Field | Value |
| --- | --- |
| Produced by (industry tags) | `tag_embalming_resin` |
| Demand index | 1 |
| Luxury (wealth elasticity) | 0.4 |
| Perishable | 0 |
| Demand traits | `noble` 1.3 |
| Storage | 365 days capacity, 0.01% stock loss a day, 15 reserve days |

## Where the Engine Places It

Settlements carrying each producer tag: `tag_embalming_resin` 1 (of 325 stored settlements).

**Dedicated `tag_embalming_resin` industry at:** Skuld (2).

## Sources

- Engine record: [`faerun/data/store/commodities.json`](../../../faerun/data/store/commodities.json), with storage and recipe values as applied at load time by [`faerun/data/commodities.py`](../../../faerun/data/commodities.py). Read 2026-10-04.
- Settlement placements: [`faerun/data/store/settlements.json`](../../../faerun/data/store/settlements.json), read 2026-10-04.
