# Chultan fruit

[Commodity index](../README.md) · [Exotic goods](README.md)

**Status:** In the engine  
**Engine ID:** `chultan_fruit`  
**Category:** exotic  
**Trade unit:** crate (30 lb)  
**Base price:** 6 gp per crate (about 0.2 gp per lb)  
**Production type:** raw  
**Aurora's Whole Realms Catalogue:** no matching entry in the sections reviewed

## Engine Description

> Chultan fruit is a exotic good in Faerûn, traded in crate lots for daily use, craft, and commerce. A rare and often imported good prized for its scarcity and prestige.

This is a model input stored in the catalogue, not a sourced lore claim.

## Engine Inputs

| Field | Value |
| --- | --- |
| Produced by (industry tags) | `orchard` |
| Demand index | 0.1 |
| Luxury (wealth elasticity) | 0.7 |
| Perishable | 0.95 |
| Demand traits | `jungle` 0.3, `noble` 2 |
| Requires | `jungle` |
| Storage | 10 days capacity, 8% stock loss a day, 1 reserve days |
| Harvest or production calendar | Mirtul 2%, Kythorn 8%, Flamerule 16%, Eleasis 25%, Eleint 33%, Marpenoth 16% |
| Regional calendar (cold) | Flamerule 7%, Eleasis 27%, Eleint 53%, Marpenoth 13% |
| Regional calendar (arid) | Hammer 2%, Alturiak 3%, Ches 7%, Tarsakh 13%, Mirtul 13%, Kythorn 7%, Flamerule 1%, Eleasis 3%, Eleint 13%, Marpenoth 20%, Uktar 13%, Nightal 3% |
| Regional calendar (tropical) | Hammer 6%, Alturiak 6%, Ches 12%, Tarsakh 12%, Mirtul 6%, Kythorn 6%, Flamerule 6%, Eleasis 6%, Eleint 12%, Marpenoth 12%, Uktar 6%, Nightal 6% |

## Where the Engine Places It

Settlements carrying each producer tag: `orchard` 4 (of 325 stored settlements).

**Specialty at:** Port Nyanzaru (3).

## Sources

- Engine record: [`faerun/data/store/commodities.json`](../../../faerun/data/store/commodities.json), with storage and recipe values as applied at load time by [`faerun/data/commodities.py`](../../../faerun/data/commodities.py). Read 2026-10-04.
- Settlement placements: [`faerun/data/store/settlements.json`](../../../faerun/data/store/settlements.json), read 2026-10-04.
