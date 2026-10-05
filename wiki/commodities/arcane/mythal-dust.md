# Mythal dust

[Commodity index](../README.md) · [Arcane goods](README.md)

**Status:** In the engine  
**Engine ID:** `mythal_dust`  
**Category:** arcane  
**Trade unit:** vial (0.2 lb)  
**Base price:** 550 gp per vial (about 2,750 gp per lb)  
**Production type:** raw  
**Aurora's Whole Realms Catalogue:** no matching entry in the sections reviewed

## Engine Description

> Residual magic swept from within Myth Drannor's mythal; stocks are effectively fixed.

This is a model input stored in the catalogue, not a sourced lore claim.

## Engine Inputs

| Field | Value |
| --- | --- |
| Produced by (industry tags) | `tag_mythal_dust` |
| Demand index | 1 |
| Luxury (wealth elasticity) | 1 |
| Perishable | 0 |
| Demand traits | `noble` 1.3 |
| Storage | 365 days capacity, 0.01% stock loss a day, 15 reserve days |

## Where the Engine Places It

Settlements carrying each producer tag: `tag_mythal_dust` 1 (of 325 stored settlements).

**Dedicated `tag_mythal_dust` industry at:** Myth Drannor (2).

## Sources

- Engine record: [`faerun/data/store/commodities.json`](../../../faerun/data/store/commodities.json), with storage and recipe values as applied at load time by [`faerun/data/commodities.py`](../../../faerun/data/commodities.py). Read 2026-10-04.
- Settlement placements: [`faerun/data/store/settlements.json`](../../../faerun/data/store/settlements.json), read 2026-10-04.
