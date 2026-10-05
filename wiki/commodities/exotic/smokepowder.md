# Smokepowder

[Commodity index](../README.md) · [Exotic goods](README.md)

**Status:** In the engine  
**Engine ID:** `smokepowder`  
**Category:** exotic  
**Trade unit:** keg (20 lb)  
**Base price:** 400 gp per keg (about 20 gp per lb)  
**Production type:** processed or manufactured  
**Aurora's Whole Realms Catalogue:** no matching entry in the sections reviewed

## Engine Description

> A Lantanna secret; illegal or terrifying nearly everywhere else.

This is a model input stored in the catalogue, not a sourced lore claim.

## Engine Inputs

| Field | Value |
| --- | --- |
| Produced by (industry tags) | `alch`, `arcane` |
| Demand index | 0.01 |
| Luxury (wealth elasticity) | 0.6 |
| Perishable | 0 |
| Demand traits | `military` 3, `gnome` 2.5, `mercantile` 1.5 |
| Requires | `gnome` |
| Storage | 365 days capacity, 0.01% stock loss a day, 15 reserve days |

## Recipe Links

Inputs for one keg: [Charcoal](../material/charcoal.md) 0.2, [Salt](../food/salt.md) 0.1.

## Where the Engine Places It

Settlements carrying each producer tag: `alch` 17, `arcane` 24 (of 325 stored settlements).

**Specialty at:** Blingdenstone (1).

## Sources

- Engine record: [`faerun/data/store/commodities.json`](../../../faerun/data/store/commodities.json), with storage and recipe values as applied at load time by [`faerun/data/commodities.py`](../../../faerun/data/commodities.py). Read 2026-10-04.
- Settlement placements: [`faerun/data/store/settlements.json`](../../../faerun/data/store/settlements.json), read 2026-10-04.
