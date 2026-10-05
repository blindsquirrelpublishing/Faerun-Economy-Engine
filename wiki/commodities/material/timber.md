# Timber

[Commodity index](../README.md) · [Materials](README.md)

**Status:** In the engine  
**Engine ID:** `timber`  
**Category:** material  
**Trade unit:** load (500 lb)  
**Base price:** 3 gp per load (about 0.006 gp per lb)  
**Production type:** raw  
**Aurora's Whole Realms Catalogue:** no matching entry in the sections reviewed

## Engine Description

> Timber is a material good in Faerûn, traded in load lots for daily use, craft, and commerce. A bulk material that serves as the foundation of building, crafting, and repair.

This is a model input stored in the catalogue, not a sourced lore claim.

## Engine Inputs

| Field | Value |
| --- | --- |
| Produced by (industry tags) | `log` |
| Demand index | 1.6 |
| Luxury (wealth elasticity) | 0 |
| Perishable | 0 |
| Demand traits | `port` 1.6, `frontier` 1.4 |
| Legacy season multipliers | `winter` 1.2 |
| Storage | 400 days capacity, 0.01% stock loss a day, 45 reserve days |

## Recipe Links

Used as an input for: [Charcoal](../material/charcoal.md) (0.12 per unit), [Paper](../material/paper.md) (0.0002 per unit), [Pitch and tar](../material/pitch.md) (0.12 per unit), [Sawn planks](../material/planks.md) (0.65 per unit).

## Where the Engine Places It

Settlements carrying each producer tag: `log` 15 (of 325 stored settlements).

**Specialty at:** Alaghôn (2), Essembra (3), Everlund (1), Harrowdale Town (1), Loudwater (1), Phlan (3).

**Configured shortage at:** Athkatla, Baldur's Gate, Calimport, Halarahh, Memnon, Parnast, Selgaunt, [Waterdeep](../../../locations/waterdeep.md), Westgate.

## Sources

- Engine record: [`faerun/data/store/commodities.json`](../../../faerun/data/store/commodities.json), with storage and recipe values as applied at load time by [`faerun/data/commodities.py`](../../../faerun/data/commodities.py). Read 2026-10-04.
- Settlement placements: [`faerun/data/store/settlements.json`](../../../faerun/data/store/settlements.json), read 2026-10-04.
