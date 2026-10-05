# River boat

[Commodity index](../README.md) · [Manufactured products](README.md)

**Status:** In the engine  
**Engine ID:** `ship_boat`  
**Category:** product  
**Trade unit:** boat (4000 lb)  
**Base price:** 800 gp per boat (about 0.2 gp per lb)  
**Production type:** processed or manufactured  
**Aurora's Whole Realms Catalogue:** no matching entry in the sections reviewed

## Engine Description

> River boat is a product good in Faerûn, traded in boat lots for daily use, craft, and commerce. A practical manufactured good made for everyday trade and labor.

This is a model input stored in the catalogue, not a sourced lore claim.

## Engine Inputs

| Field | Value |
| --- | --- |
| Produced by (industry tags) | `ship` |
| Demand index | 0.01 |
| Luxury (wealth elasticity) | 0 |
| Perishable | 0 |
| Demand traits | `port` 3, `mercantile` 2 |
| Storage | 365 days capacity, 0.01% stock loss a day, 15 reserve days |

## Recipe Links

Inputs for one boat: [Sawn planks](../material/planks.md) 8, [Nails and fittings](../product/nails.md) 4, [Hemp rope](../product/rope.md) 5, [Sailcloth and canvas](../product/sailcloth.md) 2.

## Where the Engine Places It

Settlements carrying each producer tag: `ship` 48 (of 325 stored settlements).

**Specialty at:** Alaghôn (2), Baldur's Gate (2), Lyrabar (2), Marsember (2), Orlumbor (3), Tsurlagol (1), Zazesspur (2).

## Sources

- Engine record: [`faerun/data/store/commodities.json`](../../../faerun/data/store/commodities.json), with storage and recipe values as applied at load time by [`faerun/data/commodities.py`](../../../faerun/data/commodities.py). Read 2026-10-04.
- Settlement placements: [`faerun/data/store/settlements.json`](../../../faerun/data/store/settlements.json), read 2026-10-04.
