# Iron ore

[Commodity index](../README.md) · [Metals](README.md)

**Status:** In the engine  
**Engine ID:** `iron_ore`  
**Category:** metal  
**Trade unit:** load (100 lb)  
**Base price:** 2 gp per load (about 0.02 gp per lb)  
**Production type:** raw  
**Aurora's Whole Realms Catalogue:** no matching entry in the sections reviewed

## Engine Description

> Iron ore is a metal good in Faerûn, traded in load lots for daily use, craft, and commerce. A mineral or refined metal traded for tools, industry, and coinage.

This is a model input stored in the catalogue, not a sourced lore claim.

## Engine Inputs

| Field | Value |
| --- | --- |
| Produced by (industry tags) | `mine_iron` |
| Demand index | 0.8 |
| Luxury (wealth elasticity) | 0 |
| Perishable | 0 |
| Storage | 365 days capacity, 0.01% stock loss a day, 15 reserve days |

## Recipe Links

Used as an input for: [Wrought iron](../metal/iron-ingot.md) (0.15 per unit).

## Where the Engine Places It

Settlements carrying each producer tag: `mine_iron` 13 (of 325 stored settlements).

**Specialty at:** Leilon (1), Llorkh (2), Nashkel (3).

**Configured shortage at:** Athkatla, Baldur's Gate, Calimport, Selgaunt, [Waterdeep](../../../locations/waterdeep.md).

## Sources

- Engine record: [`faerun/data/store/commodities.json`](../../../faerun/data/store/commodities.json), with storage and recipe values as applied at load time by [`faerun/data/commodities.py`](../../../faerun/data/commodities.py). Read 2026-10-04.
- Settlement placements: [`faerun/data/store/settlements.json`](../../../faerun/data/store/settlements.json), read 2026-10-04.
