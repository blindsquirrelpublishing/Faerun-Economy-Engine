# Batiri dart venom

[Commodity index](../README.md) · [Arcane goods](README.md)

**Status:** In the engine  
**Engine ID:** `batiri_dart_venom`  
**Category:** arcane  
**Trade unit:** vial (0.3 lb)  
**Base price:** 30 gp per vial (about 100 gp per lb)  
**Production type:** raw  
**Aurora's Whole Realms Catalogue:** no matching entry in the sections reviewed

## Engine Description

> Batiri-brewed paralytic dart poison; the recipe doesn't survive the trip out of Chult's jungle intact.

This is a model input stored in the catalogue, not a sourced lore claim.

## Engine Inputs

| Field | Value |
| --- | --- |
| Produced by (industry tags) | `tag_batiri_dart_venom` |
| Demand index | 1 |
| Luxury (wealth elasticity) | 0.4 |
| Perishable | 0.2 |
| Demand traits | `noble` 1.3 |
| Storage | 365 days capacity, 0.01% stock loss a day, 15 reserve days |

## Where the Engine Places It

Settlements carrying each producer tag: `tag_batiri_dart_venom` 1 (of 325 stored settlements).

**Dedicated `tag_batiri_dart_venom` industry at:** Port Nyanzaru (2).

## Sources

- Engine record: [`faerun/data/store/commodities.json`](../../../faerun/data/store/commodities.json), with storage and recipe values as applied at load time by [`faerun/data/commodities.py`](../../../faerun/data/commodities.py). Read 2026-10-04.
- Settlement placements: [`faerun/data/store/settlements.json`](../../../faerun/data/store/settlements.json), read 2026-10-04.
