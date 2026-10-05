# Surplus grain

[Commodity index](../README.md) · [Food](README.md)

**Status:** In the engine  
**Engine ID:** `surplus_grain`  
**Category:** food  
**Trade unit:** bushel (60 lb)  
**Base price:** 0.55 gp per bushel (about 0.0092 gp per lb)  
**Production type:** raw  
**Aurora's Whole Realms Catalogue:** no matching entry in the sections reviewed

## Engine Description

> Waterdeep's breadbasket; the temple-farmed surplus at Goldenfields undercuts common grain on price alone.

This is a model input stored in the catalogue, not a sourced lore claim.

## Engine Inputs

| Field | Value |
| --- | --- |
| Produced by (industry tags) | `tag_surplus_grain` |
| Demand index | 1 |
| Luxury (wealth elasticity) | 0 |
| Perishable | 0.15 |
| Storage | 365 days capacity, 0.01% stock loss a day, 15 reserve days |

## Where the Engine Places It

Settlements carrying each producer tag: `tag_surplus_grain` 1 (of 325 stored settlements).

**Dedicated `tag_surplus_grain` industry at:** Goldenfields (2).

## Sources

- Engine record: [`faerun/data/store/commodities.json`](../../../faerun/data/store/commodities.json), with storage and recipe values as applied at load time by [`faerun/data/commodities.py`](../../../faerun/data/commodities.py). Read 2026-10-04.
- Settlement placements: [`faerun/data/store/settlements.json`](../../../faerun/data/store/settlements.json), read 2026-10-04.
