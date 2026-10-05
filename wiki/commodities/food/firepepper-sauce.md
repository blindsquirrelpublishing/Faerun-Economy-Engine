# Firepepper sauce

[Commodity index](../README.md) · [Food](README.md)

**Status:** In the engine  
**Engine ID:** `firepepper_sauce`  
**Category:** food  
**Trade unit:** jar (3 lb)  
**Base price:** 5 gp per jar (about 1.67 gp per lb)  
**Production type:** raw  
**Aurora's Whole Realms Catalogue:** no matching entry in the sections reviewed

## Engine Description

> Fermented jungle pepper sauce, bottled at Port Nyanzaru and Tashluta alike.

This is a model input stored in the catalogue, not a sourced lore claim.

## Engine Inputs

| Field | Value |
| --- | --- |
| Produced by (industry tags) | `tag_firepepper_sauce` |
| Demand index | 1 |
| Luxury (wealth elasticity) | 0.2 |
| Perishable | 0.2 |
| Storage | 365 days capacity, 0.01% stock loss a day, 15 reserve days |

## Where the Engine Places It

Settlements carrying each producer tag: `tag_firepepper_sauce` 2 (of 325 stored settlements).

**Dedicated `tag_firepepper_sauce` industry at:** Port Nyanzaru (2), Tashluta (2).

## Sources

- Engine record: [`faerun/data/store/commodities.json`](../../../faerun/data/store/commodities.json), with storage and recipe values as applied at load time by [`faerun/data/commodities.py`](../../../faerun/data/commodities.py). Read 2026-10-04.
- Settlement placements: [`faerun/data/store/settlements.json`](../../../faerun/data/store/settlements.json), read 2026-10-04.
