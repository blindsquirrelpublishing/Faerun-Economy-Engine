# Fine clothing

[Commodity index](../README.md) · [Luxury goods](README.md)

**Status:** In the engine  
**Engine ID:** `clothing_fine`  
**Category:** luxury  
**Trade unit:** outfit (6 lb)  
**Base price:** 15 gp per outfit (about 2.5 gp per lb)  
**Production type:** processed or manufactured  
**Aurora's Whole Realms Catalogue:** no matching entry in the sections reviewed

## Engine Description

> Fine clothing is a luxury good in Faerûn, traded in outfit lots for daily use, craft, and commerce. A woven textile valued for clothing, furnishing, and caravan gear.

This is a model input stored in the catalogue, not a sourced lore claim.

## Engine Inputs

| Field | Value |
| --- | --- |
| Produced by (industry tags) | `textile`, `craft`, `silk` |
| Required skill | `textile` 2 |
| Demand index | 0.12 |
| Luxury (wealth elasticity) | 0.9 |
| Perishable | 0 |
| Demand traits | `noble` 3.5, `cosmopolitan` 2 |
| Storage | 365 days capacity, 0.01% stock loss a day, 15 reserve days |

## Recipe Links

Inputs for one outfit: [Dyed cloth](../textile/cloth-dyed.md) 0.25, [Silk](../luxury/silk.md) 0.1.

## Where the Engine Places It

Settlements carrying each producer tag: `textile` 23, `craft` 82, `silk` 4 (of 325 stored settlements).

**Specialty at:** Athkatla (2), Evereska (2), [Neverwinter](../../../locations/neverwinter.md) (1), Selgaunt (2), Suzail (1), [Waterdeep](../../../locations/waterdeep.md) (2).

## Sources

- Engine record: [`faerun/data/store/commodities.json`](../../../faerun/data/store/commodities.json), with storage and recipe values as applied at load time by [`faerun/data/commodities.py`](../../../faerun/data/commodities.py). Read 2026-10-04.
- Settlement placements: [`faerun/data/store/settlements.json`](../../../faerun/data/store/settlements.json), read 2026-10-04.
