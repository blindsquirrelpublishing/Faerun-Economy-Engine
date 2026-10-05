# Hooded lantern

[Commodity index](../README.md) · [Manufactured products](README.md)

**Status:** In the engine  
**Engine ID:** `lantern`  
**Category:** product  
**Trade unit:** lantern (2 lb)  
**Base price:** 5 gp per lantern (about 2.5 gp per lb)  
**Production type:** processed or manufactured  
**Aurora's Whole Realms Catalogue:** no matching entry in the sections reviewed

## Engine Description

> Hooded lantern is a product good in Faerûn, traded in lantern lots for daily use, craft, and commerce. A practical manufactured good made for everyday trade and labor.

This is a model input stored in the catalogue, not a sourced lore claim.

## Engine Inputs

| Field | Value |
| --- | --- |
| Produced by (industry tags) | `smith`, `glass` |
| Demand index | 0.3 |
| Luxury (wealth elasticity) | 0 |
| Perishable | 0 |
| Demand traits | `mining` 2, `port` 1.4 |
| Storage | 365 days capacity, 0.01% stock loss a day, 15 reserve days |

## Recipe Links

Inputs for one lantern: [Wrought iron](../metal/iron-ingot.md) 0.15, [Glassware](../product/glassware.md) 0.05.

## Where the Engine Places It

Settlements carrying each producer tag: `smith` 33, `glass` 6 (of 325 stored settlements).

## Sources

- Engine record: [`faerun/data/store/commodities.json`](../../../faerun/data/store/commodities.json), with storage and recipe values as applied at load time by [`faerun/data/commodities.py`](../../../faerun/data/commodities.py). Read 2026-10-04.
- Settlement placements: [`faerun/data/store/settlements.json`](../../../faerun/data/store/settlements.json), read 2026-10-04.
