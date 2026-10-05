# Common clothing

[Commodity index](../README.md) · [Manufactured products](README.md)

**Status:** In the engine  
**Engine ID:** `clothing_common`  
**Category:** product  
**Trade unit:** outfit (4 lb)  
**Base price:** 0.5 gp per outfit (about 0.125 gp per lb)  
**Production type:** processed or manufactured  
**Aurora's Whole Realms Catalogue:** no matching entry in the sections reviewed

## Engine Description

> Common clothing is a product good in Faerûn, traded in outfit lots for daily use, craft, and commerce. A woven textile valued for clothing, furnishing, and caravan gear.

This is a model input stored in the catalogue, not a sourced lore claim.

## Engine Inputs

| Field | Value |
| --- | --- |
| Produced by (industry tags) | `textile`, `craft` |
| Demand index | 1.8 |
| Luxury (wealth elasticity) | 0 |
| Perishable | 0 |
| Legacy season multipliers | `winter` 1.2 |
| Storage | 365 days capacity, 0.01% stock loss a day, 15 reserve days |
| Demand calendar | Hammer 10%, Alturiak 10%, Ches 9%, Tarsakh 8%, Mirtul 7%, Kythorn 6%, Flamerule 6%, Eleasis 6%, Eleint 8%, Marpenoth 9%, Uktar 10%, Nightal 10% |

## Recipe Links

Inputs for one outfit: [Linen cloth](../textile/linen.md) 0.15.

## Where the Engine Places It

Settlements carrying each producer tag: `textile` 23, `craft` 82 (of 325 stored settlements).

## Sources

- Engine record: [`faerun/data/store/commodities.json`](../../../faerun/data/store/commodities.json), with storage and recipe values as applied at load time by [`faerun/data/commodities.py`](../../../faerun/data/commodities.py). Read 2026-10-04.
- Settlement placements: [`faerun/data/store/settlements.json`](../../../faerun/data/store/settlements.json), read 2026-10-04.
