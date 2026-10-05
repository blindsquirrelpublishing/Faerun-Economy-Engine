# Moonstone

[Commodity index](../README.md) · [Gems](README.md)

**Status:** In the engine  
**Engine ID:** `gem_moonstone`  
**Category:** gem  
**Trade unit:** stone (0.1 lb)  
**Base price:** 50 gp per stone (about 500 gp per lb)  
**Production type:** raw  
**Aurora's Whole Realms Catalogue:** no matching entry in the sections reviewed

## Engine Description

> Moonstone is a gem good in Faerûn, traded in stone lots for daily use, craft, and commerce. A prized mineral or gemstone traded for ornament, wealth, and arcane study.

This is a model input stored in the catalogue, not a sourced lore claim.

## Engine Inputs

| Field | Value |
| --- | --- |
| Produced by (industry tags) | `mine_gem` |
| Demand index | 0.07 |
| Luxury (wealth elasticity) | 0.9 |
| Perishable | 0 |
| Demand traits | `elven` 2, `arcane` 1.8, `noble` 1.6 |
| Storage | 365 days capacity, 0.01% stock loss a day, 15 reserve days |

## Where the Engine Places It

Settlements carrying each producer tag: `mine_gem` 9 (of 325 stored settlements).

**Specialty at:** Blingdenstone (2), Evereska (1), Myth Drannor (2), Secomber (1).

## Sources

- Engine record: [`faerun/data/store/commodities.json`](../../../faerun/data/store/commodities.json), with storage and recipe values as applied at load time by [`faerun/data/commodities.py`](../../../faerun/data/commodities.py). Read 2026-10-04.
- Settlement placements: [`faerun/data/store/settlements.json`](../../../faerun/data/store/settlements.json), read 2026-10-04.
