# Dyed cloth

[Commodity index](../README.md) · [Textiles](README.md)

**Status:** In the engine  
**Engine ID:** `cloth_dyed`  
**Category:** textile  
**Trade unit:** bolt (20 lb)  
**Base price:** 15 gp per bolt (about 0.75 gp per lb)  
**Production type:** processed or manufactured  
**Aurora's Whole Realms Catalogue:** no matching entry in the sections reviewed

## Engine Description

> Dyed cloth is a textile good in Faerûn, traded in bolt lots for daily use, craft, and commerce. A woven textile valued for clothing, furnishing, and caravan gear.

This is a model input stored in the catalogue, not a sourced lore claim.

## Engine Inputs

| Field | Value |
| --- | --- |
| Produced by (industry tags) | `textile`, `dye` |
| Demand index | 0.6 |
| Luxury (wealth elasticity) | 0.5 |
| Perishable | 0 |
| Demand traits | `noble` 2, `cosmopolitan` 1.4 |
| Storage | 400 days capacity, 0.04% stock loss a day, 45 reserve days |

## Recipe Links

Inputs for one bolt: [Linen cloth](../textile/linen.md) 1, [Indigo and common dyes](../material/dye-indigo.md) 0.25.

Used as an input for: [Fine clothing](../luxury/clothing-fine.md) (0.25 per unit).

## Where the Engine Places It

Settlements carrying each producer tag: `textile` 23, `dye` 2 (of 325 stored settlements).

**Specialty at:** Berdusk (2), Elversult (1), Selgaunt (3), Zazesspur (1).

## Sources

- Engine record: [`faerun/data/store/commodities.json`](../../../faerun/data/store/commodities.json), with storage and recipe values as applied at load time by [`faerun/data/commodities.py`](../../../faerun/data/commodities.py). Read 2026-10-04.
- Settlement placements: [`faerun/data/store/settlements.json`](../../../faerun/data/store/settlements.json), read 2026-10-04.
