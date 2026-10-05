# Star anise

[Commodity index](../README.md) · [Luxury goods](README.md)

**Status:** In the engine  
**Engine ID:** `star_anise`  
**Category:** luxury  
**Trade unit:** pound (1 lb)  
**Base price:** 8 gp per pound (about 8 gp per lb)  
**Production type:** raw  
**Aurora's Whole Realms Catalogue:** no matching entry in the sections reviewed

## Engine Description

> Star anise is a luxury good in Faerûn, traded in pound lots for daily use, craft, and commerce. A refined luxury good sought by elites, merchants, and collectors.

This is a model input stored in the catalogue, not a sourced lore claim.

## Engine Inputs

| Field | Value |
| --- | --- |
| Produced by (industry tags) | `spice`, `orchard` |
| Demand index | 0.1 |
| Luxury (wealth elasticity) | 0.7 |
| Perishable | 0 |
| Demand traits | `noble` 1.7, `cosmopolitan` 1.5 |
| Requires | `jungle` |
| Storage | 365 days capacity, 0.08% stock loss a day, 45 reserve days |
| Harvest or production calendar | Mirtul 5%, Kythorn 10%, Flamerule 20%, Eleasis 30%, Eleint 20%, Marpenoth 10%, Uktar 5% |
| Regional calendar (cold) | Flamerule 10%, Eleasis 30%, Eleint 40%, Marpenoth 20% |
| Regional calendar (arid) | Hammer 5%, Alturiak 10%, Ches 20%, Tarsakh 20%, Mirtul 5%, Eleint 5%, Marpenoth 10%, Uktar 20%, Nightal 5% |
| Regional calendar (tropical) | Hammer 5%, Alturiak 11%, Ches 16%, Tarsakh 11%, Mirtul 5%, Kythorn 3%, Flamerule 5%, Eleasis 11%, Eleint 16%, Marpenoth 11%, Uktar 5%, Nightal 3% |

## Where the Engine Places It

Settlements carrying each producer tag: `spice` 4, `orchard` 4 (of 325 stored settlements).

## Sources

- Engine record: [`faerun/data/store/commodities.json`](../../../faerun/data/store/commodities.json), with storage and recipe values as applied at load time by [`faerun/data/commodities.py`](../../../faerun/data/commodities.py). Read 2026-10-04.
- Settlement placements: [`faerun/data/store/settlements.json`](../../../faerun/data/store/settlements.json), read 2026-10-04.
