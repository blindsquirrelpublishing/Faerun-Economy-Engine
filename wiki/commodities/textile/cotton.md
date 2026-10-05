# Cotton

[Commodity index](../README.md) · [Textiles](README.md)

**Status:** In the engine  
**Engine ID:** `cotton`  
**Category:** textile  
**Trade unit:** bale (100 lb)  
**Base price:** 4 gp per bale (about 0.04 gp per lb)  
**Production type:** raw  
**Aurora's Whole Realms Catalogue:** no matching entry in the sections reviewed

## Engine Description

> Cotton is a textile good in Faerûn, traded in bale lots for daily use, craft, and commerce. A woven or worked textile valued for clothing, shelter, and travel.

This is a model input stored in the catalogue, not a sourced lore claim.

## Engine Inputs

| Field | Value |
| --- | --- |
| Produced by (industry tags) | `farm`, `textile` |
| Demand index | 0.9 |
| Luxury (wealth elasticity) | 0 |
| Perishable | 0 |
| Demand traits | `desert` 0.7, `jungle` 0.7 |
| Storage | 400 days capacity, 0.04% stock loss a day, 45 reserve days |
| Harvest or production calendar | Eleasis 10%, Eleint 30%, Marpenoth 40%, Uktar 20% |
| Regional calendar (cold) | Eleint 10%, Marpenoth 50%, Uktar 40% |
| Regional calendar (arid) | Eleasis 5%, Eleint 20%, Marpenoth 40%, Uktar 30%, Nightal 5% |
| Regional calendar (tropical) | Hammer 18%, Alturiak 27%, Ches 18%, Tarsakh 5%, Marpenoth 5%, Uktar 9%, Nightal 18% |

## Where the Engine Places It

Settlements carrying each producer tag: `farm` 50, `textile` 23 (of 325 stored settlements).

**Specialty at:** Myratma (3).

## Sources

- Engine record: [`faerun/data/store/commodities.json`](../../../faerun/data/store/commodities.json), with storage and recipe values as applied at load time by [`faerun/data/commodities.py`](../../../faerun/data/commodities.py). Read 2026-10-04.
- Settlement placements: [`faerun/data/store/settlements.json`](../../../faerun/data/store/settlements.json), read 2026-10-04.
