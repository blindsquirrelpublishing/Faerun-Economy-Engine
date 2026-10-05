# Stabilized lotus extract

[Commodity index](../README.md) · [Arcane goods](README.md)

**Status:** In the engine  
**Engine ID:** `stabilized_lotus_extract`  
**Category:** arcane  
**Trade unit:** vial (0.3 lb)  
**Base price:** 55 gp per vial (about 183 gp per lb)  
**Production type:** raw  
**Aurora's Whole Realms Catalogue:** no matching entry in the sections reviewed

## Engine Description

> Alchemically fixed within hours of harvest. The raw pollen loses potency before it clears Chult's border; this is the only form most buyers outside the jungle ever see.

This is a model input stored in the catalogue, not a sourced lore claim.

## Engine Inputs

| Field | Value |
| --- | --- |
| Produced by (industry tags) | `tag_stabilized_lotus_extract` |
| Demand index | 1 |
| Luxury (wealth elasticity) | 0.5 |
| Perishable | 0 |
| Demand traits | `noble` 1.3 |
| Storage | 365 days capacity, 0.01% stock loss a day, 15 reserve days |

## Where the Engine Places It

Settlements carrying each producer tag: `tag_stabilized_lotus_extract` 1 (of 325 stored settlements).

**Dedicated `tag_stabilized_lotus_extract` industry at:** Port Nyanzaru (2).

## Sources

- Engine record: [`faerun/data/store/commodities.json`](../../../faerun/data/store/commodities.json), with storage and recipe values as applied at load time by [`faerun/data/commodities.py`](../../../faerun/data/commodities.py). Read 2026-10-04.
- Settlement placements: [`faerun/data/store/settlements.json`](../../../faerun/data/store/settlements.json), read 2026-10-04.
