# Knucklehead scrimshaw

[Commodity index](../README.md) · [Exotic goods](README.md)

**Status:** In the engine  
**Engine ID:** `scrimshaw`  
**Category:** exotic  
**Trade unit:** piece (5 lb)  
**Base price:** 30 gp per piece (about 6 gp per lb)  
**Production type:** processed or manufactured  
**Aurora's Whole Realms Catalogue:** no matching entry in the sections reviewed

## Engine Description

> Carved knucklehead trout ivory out of Icewind Dale.

This is a model input stored in the catalogue, not a sourced lore claim.

## Engine Inputs

| Field | Value |
| --- | --- |
| Produced by (industry tags) | `craft`, `fish` |
| Demand index | 0.05 |
| Luxury (wealth elasticity) | 0.9 |
| Perishable | 0 |
| Demand traits | `noble` 2.2, `cold` 0.5, `cosmopolitan` 1.8 |
| Requires | `tundra`, `taiga`, `cold` |
| Storage | 365 days capacity, 0.01% stock loss a day, 15 reserve days |

## Recipe Links

Inputs for one piece: [Ivory](../luxury/ivory.md) 0.1.

## Where the Engine Places It

Settlements carrying each producer tag: `craft` 82, `fish` 36 (of 325 stored settlements).

**Specialty at:** Bryn Shander (2), Targos (1).

## Sources

- Engine record: [`faerun/data/store/commodities.json`](../../../faerun/data/store/commodities.json), with storage and recipe values as applied at load time by [`faerun/data/commodities.py`](../../../faerun/data/commodities.py). Read 2026-10-04.
- Settlement placements: [`faerun/data/store/settlements.json`](../../../faerun/data/store/settlements.json), read 2026-10-04.
