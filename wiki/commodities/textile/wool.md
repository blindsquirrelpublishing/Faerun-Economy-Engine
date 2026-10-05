# Raw wool

[Commodity index](../README.md) · [Textiles](README.md)

**Status:** In the engine  
**Engine ID:** `wool`  
**Category:** textile  
**Trade unit:** bale (100 lb)  
**Base price:** 3 gp per bale (about 0.03 gp per lb)  
**Production type:** raw  
**Aurora's Whole Realms Catalogue:** no matching entry in the sections reviewed

## Engine Description

> Raw wool is a textile good in Faerûn, traded in bale lots for daily use, craft, and commerce. A woven textile valued for clothing, furnishing, and caravan gear.

This is a model input stored in the catalogue, not a sourced lore claim.

## Engine Inputs

| Field | Value |
| --- | --- |
| Produced by (industry tags) | `herd` |
| Demand index | 1.2 |
| Luxury (wealth elasticity) | 0 |
| Perishable | 0 |
| Legacy season multipliers | `spring` 0.8, `winter` 1.25 |
| Storage | 400 days capacity, 0.04% stock loss a day, 45 reserve days |
| Harvest or production calendar | Tarsakh 10%, Mirtul 50%, Kythorn 40% |
| Regional calendar (cold) | Mirtul 10%, Kythorn 50%, Flamerule 40% |
| Regional calendar (arid) | Alturiak 10%, Ches 40%, Tarsakh 40%, Mirtul 10% |
| Regional calendar (tropical) | Ches 10%, Tarsakh 30%, Mirtul 10%, Eleint 10%, Marpenoth 30%, Uktar 10% |
| Demand calendar | Hammer 10%, Alturiak 10%, Ches 9%, Tarsakh 8%, Mirtul 7%, Kythorn 6%, Flamerule 6%, Eleasis 6%, Eleint 8%, Marpenoth 9%, Uktar 10%, Nightal 10% |

## Where the Engine Places It

Settlements carrying each producer tag: `herd` 11 (of 325 stored settlements).

**Specialty at:** Ashabenford (2), Caer Calidyrr (3), Caer Corwell (2), Hill's Edge (1).

**Configured shortage at:** Menzoberranzan, Mithral Hall, Port Nyanzaru, [Waterdeep](../../../locations/waterdeep.md).

## Sources

- Engine record: [`faerun/data/store/commodities.json`](../../../faerun/data/store/commodities.json), with storage and recipe values as applied at load time by [`faerun/data/commodities.py`](../../../faerun/data/commodities.py). Read 2026-10-04.
- Settlement placements: [`faerun/data/store/settlements.json`](../../../faerun/data/store/settlements.json), read 2026-10-04.
