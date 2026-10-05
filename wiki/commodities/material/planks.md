# Sawn planks

[Commodity index](../README.md) · [Materials](README.md)

**Status:** In the engine  
**Engine ID:** `planks`  
**Category:** material  
**Trade unit:** load (300 lb)  
**Base price:** 5 gp per load (about 0.017 gp per lb)  
**Production type:** processed or manufactured  
**Aurora's Whole Realms Catalogue:** no matching entry in the sections reviewed

## Engine Description

> Sawn planks is a material good in Faerûn, traded in load lots for daily use, craft, and commerce. A bulk material that serves as the foundation of building, crafting, and repair.

This is a model input stored in the catalogue, not a sourced lore claim.

## Engine Inputs

| Field | Value |
| --- | --- |
| Produced by (industry tags) | `log`, `craft` |
| Demand index | 1.4 |
| Luxury (wealth elasticity) | 0 |
| Perishable | 0 |
| Storage | 365 days capacity, 0.01% stock loss a day, 15 reserve days |

## Recipe Links

Inputs for one load: [Timber](../material/timber.md) 0.65.

Used as an input for: [Arrows](../arms/arrows.md) (0.003 per unit), [Battleaxe](../arms/axe-battle.md) (0.01 per unit), [Barrel (empty)](../product/barrel.md) (0.2 per unit), [Longbow](../arms/bow-long.md) (0.007 per unit), [Shortbow](../arms/bow-short.md) (0.005 per unit), [Cart](../product/cart.md) (0.5 per unit), [Crossbow](../arms/crossbow.md) (0.01 per unit), [Iron-shod plow](../product/plow.md) (0.15 per unit), [Shield](../arms/shield.md) (0.015 per unit), [River boat](../product/ship-boat.md) (8 per unit), [Spear](../arms/spear.md) (0.01 per unit), [Artisan's tools](../product/tools-carpenter.md) (0.02 per unit), [Wagon](../product/wagon.md) (1 per unit).

## Where the Engine Places It

Settlements carrying each producer tag: `log` 15, `craft` 82 (of 325 stored settlements).

**Specialty at:** Alaghôn (2), Essembra (2), Everlund (2), Phlan (2).

## Sources

- Engine record: [`faerun/data/store/commodities.json`](../../../faerun/data/store/commodities.json), with storage and recipe values as applied at load time by [`faerun/data/commodities.py`](../../../faerun/data/commodities.py). Read 2026-10-04.
- Settlement placements: [`faerun/data/store/settlements.json`](../../../faerun/data/store/settlements.json), read 2026-10-04.
