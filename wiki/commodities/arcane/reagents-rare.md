# Rare reagents

[Commodity index](../README.md) · [Arcane goods](README.md)

**Status:** In the engine  
**Engine ID:** `reagents_rare`  
**Category:** arcane  
**Trade unit:** case (5 lb)  
**Base price:** 150 gp per case (about 30 gp per lb)  
**Production type:** raw  
**Aurora's Whole Realms Catalogue:** no matching entry in the sections reviewed

## Engine Description

> Rare reagents is a arcane good in Faerûn, traded in case lots for daily use, craft, and commerce. A magical trade good used for ritual practice, scholarship, and spellcraft.

This is a model input stored in the catalogue, not a sourced lore claim.

## Engine Inputs

| Field | Value |
| --- | --- |
| Produced by (industry tags) | `arcane`, `alch` |
| Demand index | 0.02 |
| Luxury (wealth elasticity) | 0.8 |
| Perishable | 0 |
| Demand traits | `arcane` 4, `magocracy` 4, `academic` 2 |
| Storage | 730 days capacity, 0.01% stock loss a day, 30 reserve days |

## Where the Engine Places It

Settlements carrying each producer tag: `arcane` 24, `alch` 17 (of 325 stored settlements).

**Specialty at:** Almraiven (2), Eltabbar (3), Halarahh (3), Nimbral (2), Silverymoon (2), Sshamath (3).

## Sources

- Engine record: [`faerun/data/store/commodities.json`](../../../faerun/data/store/commodities.json), with storage and recipe values as applied at load time by [`faerun/data/commodities.py`](../../../faerun/data/commodities.py). Read 2026-10-04.
- Settlement placements: [`faerun/data/store/settlements.json`](../../../faerun/data/store/settlements.json), read 2026-10-04.
