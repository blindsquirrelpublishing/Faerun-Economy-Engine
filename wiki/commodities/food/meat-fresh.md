# Fresh meat

[Commodity index](../README.md) · [Food](README.md)

**Status:** In the engine  
**Engine ID:** `meat_fresh`  
**Category:** food  
**Trade unit:** side (40 lb)  
**Base price:** 2 gp per side (about 0.05 gp per lb)  
**Production type:** raw  
**Aurora's Whole Realms Catalogue:** no matching entry in the sections reviewed

## Engine Description

> Fresh meat is a food good in Faerûn, traded in side lots for daily use, craft, and commerce. A staple trade good prized for daily sustenance and household use.

This is a model input stored in the catalogue, not a sourced lore claim.

## Engine Inputs

| Field | Value |
| --- | --- |
| Produced by (industry tags) | `cattle`, `herd`, `hunt` |
| Demand index | 1.6 |
| Luxury (wealth elasticity) | 0 |
| Perishable | 0.95 |
| Legacy season multipliers | `autumn` 0.85, `spring` 1.2 |
| Storage | 2 days capacity, 35% stock loss a day, 0.25 reserve days |

## Recipe Links

Used as an input for: [Salt meat](../food/meat-salt.md) (2.5 per unit).

## Where the Engine Places It

Settlements carrying each producer tag: `cattle` 7, `herd` 11, `hunt` 6 (of 325 stored settlements).

**Configured shortage at:** Blingdenstone, Candlekeep, Messemprar, Sshamath.

## Sources

- Engine record: [`faerun/data/store/commodities.json`](../../../faerun/data/store/commodities.json), with storage and recipe values as applied at load time by [`faerun/data/commodities.py`](../../../faerun/data/commodities.py). Read 2026-10-04.
- Settlement placements: [`faerun/data/store/settlements.json`](../../../faerun/data/store/settlements.json), read 2026-10-04.
