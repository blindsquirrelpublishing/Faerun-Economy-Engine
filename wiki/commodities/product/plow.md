# Iron-shod plow

[Commodity index](../README.md) · [Manufactured products](README.md)

**Status:** In the engine  
**Engine ID:** `plow`  
**Category:** product  
**Trade unit:** plow (100 lb)  
**Base price:** 12 gp per plow (about 0.12 gp per lb)  
**Production type:** processed or manufactured  
**Aurora's Whole Realms Catalogue:** no matching entry in the sections reviewed

## Engine Description

> Iron-shod plow is a product good in Faerûn, traded in plow lots for daily use, craft, and commerce. A mineral or refined metal traded for tools, industry, and coinage.

This is a model input stored in the catalogue, not a sourced lore claim.

## Engine Inputs

| Field | Value |
| --- | --- |
| Produced by (industry tags) | `smith`, `craft` |
| Demand index | 0.3 |
| Luxury (wealth elasticity) | 0 |
| Perishable | 0 |
| Demand traits | `agrarian` 3 |
| Legacy season multipliers | `spring` 1.35, `winter` 0.85 |
| Storage | 365 days capacity, 0.01% stock loss a day, 15 reserve days |
| Demand calendar | Hammer 7%, Alturiak 8%, Ches 10%, Tarsakh 11%, Mirtul 10%, Kythorn 8%, Flamerule 8%, Eleasis 8%, Eleint 8%, Marpenoth 8%, Uktar 7%, Nightal 7% |

## Recipe Links

Inputs for one plow: [Wrought iron](../metal/iron-ingot.md) 5, [Sawn planks](../material/planks.md) 0.15.

## Where the Engine Places It

Settlements carrying each producer tag: `smith` 33, `craft` 82 (of 325 stored settlements).

## Sources

- Engine record: [`faerun/data/store/commodities.json`](../../../faerun/data/store/commodities.json), with storage and recipe values as applied at load time by [`faerun/data/commodities.py`](../../../faerun/data/commodities.py). Read 2026-10-04.
- Settlement placements: [`faerun/data/store/settlements.json`](../../../faerun/data/store/settlements.json), read 2026-10-04.
