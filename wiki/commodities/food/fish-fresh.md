# Fresh fish

[Commodity index](../README.md) · [Food](README.md)

**Status:** In the engine  
**Engine ID:** `fish_fresh`  
**Category:** food  
**Trade unit:** barrel (60 lb)  
**Base price:** 1.5 gp per barrel (about 0.025 gp per lb)  
**Production type:** raw  
**Aurora's Whole Realms Catalogue:** no matching entry in the sections reviewed

## Engine Description

> Fresh fish is a food good in Faerûn, traded in barrel lots for daily use, craft, and commerce. A staple trade good prized for daily sustenance and household use.

This is a model input stored in the catalogue, not a sourced lore claim.

## Engine Inputs

| Field | Value |
| --- | --- |
| Produced by (industry tags) | `fish` |
| Demand index | 1.3 |
| Luxury (wealth elasticity) | 0 |
| Perishable | 1 |
| Legacy season multipliers | `winter` 1.35 |
| Storage | 2 days capacity, 35% stock loss a day, 0.25 reserve days |

## Recipe Links

Used as an input for: [Salted fish](../food/fish-salt.md) (1.7 per unit).

## Where the Engine Places It

Settlements carrying each producer tag: `fish` 36 (of 325 stored settlements).

**Specialty at:** Bryn Shander (1), Easthaven (1), Elmwood (2), [Hlondeth](../../../locations/hlondeth.md) (1), Marsember (2), Targos (2).

## Sources

- Engine record: [`faerun/data/store/commodities.json`](../../../faerun/data/store/commodities.json), with storage and recipe values as applied at load time by [`faerun/data/commodities.py`](../../../faerun/data/commodities.py). Read 2026-10-04.
- Settlement placements: [`faerun/data/store/settlements.json`](../../../faerun/data/store/settlements.json), read 2026-10-04.
