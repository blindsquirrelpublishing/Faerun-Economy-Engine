# Peaches

[Commodity index](../README.md) · [Food](README.md)

**Status:** In the engine  
**Engine ID:** `peaches`  
**Category:** food  
**Trade unit:** crate (30 lb)  
**Base price:** 2.2 gp per crate (about 0.073 gp per lb)  
**Production type:** raw  
**Aurora's Whole Realms Catalogue:** no matching entry in the sections reviewed

## Engine Description

> Grown under the same weather-magic as starflower wine; they ripen on a schedule no ordinary orchard can match. Halarahh's binding-towers keep the technique in-house, so this is the only place in Faerûn the trees fruit at all.

This is a model input stored in the catalogue, not a sourced lore claim.

## Engine Inputs

| Field | Value |
| --- | --- |
| Produced by (industry tags) | `orchard_halruaa_peach` |
| Demand index | 0.3 |
| Luxury (wealth elasticity) | 0.2 |
| Perishable | 0.75 |
| Demand traits | `noble` 1.3 |
| Legacy season multipliers | `autumn` 1.1, `spring` 1.2, `summer` 0.75, `winter` 1.35 |
| Storage | 365 days capacity, 0.01% stock loss a day, 15 reserve days |

## Where the Engine Places It

Settlements carrying each producer tag: `orchard_halruaa_peach` 1 (of 325 stored settlements).

## Sources

- Engine record: [`faerun/data/store/commodities.json`](../../../faerun/data/store/commodities.json), with storage and recipe values as applied at load time by [`faerun/data/commodities.py`](../../../faerun/data/commodities.py). Read 2026-10-04.
- Settlement placements: [`faerun/data/store/settlements.json`](../../../faerun/data/store/settlements.json), read 2026-10-04.
