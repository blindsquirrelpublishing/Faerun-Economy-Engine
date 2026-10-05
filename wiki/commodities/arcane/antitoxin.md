# Antitoxin

[Commodity index](../README.md) · [Arcane goods](README.md)

**Status:** In the engine  
**Engine ID:** `antitoxin`  
**Category:** arcane  
**Trade unit:** vial (0.5 lb)  
**Base price:** 25 gp per vial (about 50 gp per lb)  
**Production type:** processed or manufactured  
**Aurora's Whole Realms Catalogue:** no matching entry in the sections reviewed

## Engine Description

> Antitoxin is a arcane good in Faerûn, traded in vial lots for daily use, craft, and commerce. A magical trade good used by spellcasters, scholars, and ritualists.

This is a model input stored in the catalogue, not a sourced lore claim.

## Engine Inputs

| Field | Value |
| --- | --- |
| Produced by (industry tags) | `alch`, `herb` |
| Demand index | 0.06 |
| Luxury (wealth elasticity) | 0.5 |
| Perishable | 0 |
| Demand traits | `jungle` 2.5, `arcane` 1.6, `drow` 2.5 |
| Storage | 730 days capacity, 0.01% stock loss a day, 30 reserve days |

## Recipe Links

Inputs for one vial: [Medicinal herbs](../arcane/herbs-healing.md) 0.1, [Ink](../product/ink.md) 0.02.

## Where the Engine Places It

Settlements carrying each producer tag: `alch` 17, `herb` 8 (of 325 stored settlements).

**Specialty at:** Blingdenstone (2), Menzoberranzan (2).

## Sources

- Engine record: [`faerun/data/store/commodities.json`](../../../faerun/data/store/commodities.json), with storage and recipe values as applied at load time by [`faerun/data/commodities.py`](../../../faerun/data/commodities.py). Read 2026-10-04.
- Settlement placements: [`faerun/data/store/settlements.json`](../../../faerun/data/store/settlements.json), read 2026-10-04.
