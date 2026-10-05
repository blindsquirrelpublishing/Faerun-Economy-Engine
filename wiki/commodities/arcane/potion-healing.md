# Potion of healing

[Commodity index](../README.md) · [Arcane goods](README.md)

**Status:** In the engine  
**Engine ID:** `potion_healing`  
**Category:** arcane  
**Trade unit:** vial (0.5 lb)  
**Base price:** 50 gp per vial (about 100 gp per lb)  
**Production type:** processed or manufactured  
**Aurora's Whole Realms Catalogue:** no matching entry in the sections reviewed

## Engine Description

> Potion of healing is a arcane good in Faerûn, traded in vial lots for daily use, craft, and commerce. A magical trade good used by spellcasters, scholars, and ritualists.

This is a model input stored in the catalogue, not a sourced lore claim.

## Engine Inputs

| Field | Value |
| --- | --- |
| Produced by (industry tags) | `alch`, `arcane` |
| Required skill | `alch` 2 |
| Demand index | 0.05 |
| Luxury (wealth elasticity) | 0.6 |
| Perishable | 0 |
| Demand traits | `arcane` 2.5, `temple` 2.5, `military` 2, `wartorn` 3, `frontier` 1.8 |
| Storage | 730 days capacity, 0.01% stock loss a day, 30 reserve days |

## Recipe Links

Inputs for one vial: [Medicinal herbs](../arcane/herbs-healing.md) 0.2, [Honey](../food/honey.md) 0.02.

## Where the Engine Places It

Settlements carrying each producer tag: `alch` 17, `arcane` 24 (of 325 stored settlements).

**Specialty at:** Eltabbar (2), Halarahh (3), Ravens Bluff (1).

## Sources

- Engine record: [`faerun/data/store/commodities.json`](../../../faerun/data/store/commodities.json), with storage and recipe values as applied at load time by [`faerun/data/commodities.py`](../../../faerun/data/commodities.py). Read 2026-10-04.
- Settlement placements: [`faerun/data/store/settlements.json`](../../../faerun/data/store/settlements.json), read 2026-10-04.
