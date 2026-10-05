# Wagon

[Commodity index](../README.md) · [Manufactured products](README.md)

**Status:** In the engine  
**Engine ID:** `wagon`  
**Category:** product  
**Trade unit:** wagon (400 lb)  
**Base price:** 35 gp per wagon (about 0.087 gp per lb)  
**Production type:** processed or manufactured  
**Aurora's Whole Realms Catalogue:** no matching entry in the sections reviewed

## Engine Description

> Wagon is a product good in Faerûn, traded in wagon lots for daily use, craft, and commerce. A practical manufactured good made for everyday trade and labor.

This is a model input stored in the catalogue, not a sourced lore claim.

## Engine Inputs

| Field | Value |
| --- | --- |
| Produced by (industry tags) | `craft`, `smith` |
| Demand index | 0.15 |
| Luxury (wealth elasticity) | 0 |
| Perishable | 0 |
| Demand traits | `mercantile` 2.5, `frontier` 1.5 |
| Storage | 365 days capacity, 0.01% stock loss a day, 15 reserve days |

## Recipe Links

Inputs for one wagon: [Sawn planks](../material/planks.md) 1, [Nails and fittings](../product/nails.md) 0.5, [Wrought iron](../metal/iron-ingot.md) 1.

## Where the Engine Places It

Settlements carrying each producer tag: `craft` 82, `smith` 33 (of 325 stored settlements).

**Specialty at:** Proskur (1), Scornubel (2).

## Sources

- Engine record: [`faerun/data/store/commodities.json`](../../../faerun/data/store/commodities.json), with storage and recipe values as applied at load time by [`faerun/data/commodities.py`](../../../faerun/data/commodities.py). Read 2026-10-04.
- Settlement placements: [`faerun/data/store/settlements.json`](../../../faerun/data/store/settlements.json), read 2026-10-04.
