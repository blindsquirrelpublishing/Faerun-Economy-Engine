# Arcane focus

[Commodity index](../README.md) · [Arcane goods](README.md)

**Status:** In the engine  
**Engine ID:** `arcane_focus`  
**Category:** arcane  
**Trade unit:** focus (1 lb)  
**Base price:** 10 gp per focus (about 10 gp per lb)  
**Production type:** processed or manufactured  
**Aurora's Whole Realms Catalogue:** no matching entry in the sections reviewed

## Engine Description

> A compact magical implement, such as a crystal prism, rune stone, or metal spindle, used by spellcasters and scholars to focus and stabilize incantations. It is a common trade good in academic and arcane centers.

This is a model input stored in the catalogue, not a sourced lore claim.

## Engine Inputs

| Field | Value |
| --- | --- |
| Produced by (industry tags) | `arcane`, `craft` |
| Required skill | `arcane` 2 |
| Demand index | 0.04 |
| Luxury (wealth elasticity) | 0 |
| Perishable | 0 |
| Demand traits | `arcane` 4, `academic` 2 |
| Storage | 365 days capacity, 0.01% stock loss a day, 15 reserve days |

## Recipe Links

Inputs for one focus: [Agate and quartz](../gem/gem-agate.md) 0.1, [Silver](../metal/silver-ingot.md) 0.02.

## Where the Engine Places It

Settlements carrying each producer tag: `arcane` 24, `craft` 82 (of 325 stored settlements).

**Specialty at:** Silverymoon (2), Thentia (2).

## Sources

- Engine record: [`faerun/data/store/commodities.json`](../../../faerun/data/store/commodities.json), with storage and recipe values as applied at load time by [`faerun/data/commodities.py`](../../../faerun/data/commodities.py). Read 2026-10-04.
- Settlement placements: [`faerun/data/store/settlements.json`](../../../faerun/data/store/settlements.json), read 2026-10-04.
