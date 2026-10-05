# Starflower

[Commodity index](../README.md) · [Arcane goods](README.md)

**Status:** In the engine  
**Engine ID:** `starflower`  
**Category:** arcane  
**Trade unit:** bundle (1 lb)  
**Base price:** 6 gp per bundle (about 6 gp per lb)  
**Production type:** raw  
**Aurora's Whole Realms Catalogue:** no matching entry in the sections reviewed

## Engine Description

> Grown in Silverymoon's terraced gardens for minor enchantments and healing draughts.

This is a model input stored in the catalogue, not a sourced lore claim.

## Engine Inputs

| Field | Value |
| --- | --- |
| Produced by (industry tags) | `tag_starflower` |
| Demand index | 1 |
| Luxury (wealth elasticity) | 0.3 |
| Perishable | 0.1 |
| Storage | 365 days capacity, 0.01% stock loss a day, 15 reserve days |

## Where the Engine Places It

Settlements carrying each producer tag: `tag_starflower` 1 (of 325 stored settlements).

**Dedicated `tag_starflower` industry at:** Silverymoon (2).

## Sources

- Engine record: [`faerun/data/store/commodities.json`](../../../faerun/data/store/commodities.json), with storage and recipe values as applied at load time by [`faerun/data/commodities.py`](../../../faerun/data/commodities.py). Read 2026-10-04.
- Settlement placements: [`faerun/data/store/settlements.json`](../../../faerun/data/store/settlements.json), read 2026-10-04.
