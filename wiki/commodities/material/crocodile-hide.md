# Crocodile hide

[Commodity index](../README.md) · [Materials](README.md)

**Status:** In the engine  
**Engine ID:** `crocodile_hide`  
**Category:** material  
**Trade unit:** hide (12 lb)  
**Base price:** 8 gp per hide (about 0.667 gp per lb)  
**Production type:** raw  
**Aurora's Whole Realms Catalogue:** no matching entry in the sections reviewed

## Engine Description

> Tannable jungle hide, priced well under the exotic dinosaur hide it's often sold alongside. Tashalar's spice-coast wetlands support a smaller parallel hunt.

This is a model input stored in the catalogue, not a sourced lore claim.

## Engine Inputs

| Field | Value |
| --- | --- |
| Produced by (industry tags) | `tag_crocodile_hide` |
| Demand index | 1 |
| Luxury (wealth elasticity) | 0.1 |
| Perishable | 0 |
| Storage | 365 days capacity, 0.01% stock loss a day, 15 reserve days |

## Where the Engine Places It

Settlements carrying each producer tag: `tag_crocodile_hide` 2 (of 325 stored settlements).

**Dedicated `tag_crocodile_hide` industry at:** Port Nyanzaru (2), Tashluta (2).

## Sources

- Engine record: [`faerun/data/store/commodities.json`](../../../faerun/data/store/commodities.json), with storage and recipe values as applied at load time by [`faerun/data/commodities.py`](../../../faerun/data/commodities.py). Read 2026-10-04.
- Settlement placements: [`faerun/data/store/settlements.json`](../../../faerun/data/store/settlements.json), read 2026-10-04.
