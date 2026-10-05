# Sumac

[Commodity index](../README.md) · [Food](README.md)

**Status:** In the engine  
**Engine ID:** `sumac`  
**Category:** food  
**Trade unit:** pound (1 lb)  
**Base price:** 2.8 gp per pound (about 2.8 gp per lb)  
**Production type:** raw  
**Aurora's Whole Realms Catalogue:** no matching entry in the sections reviewed

## Engine Description

> Sumac is a food good in Faerûn, traded in pound lots for daily use, craft, and commerce. A staple trade good prized for daily sustenance and household use.

This is a model input stored in the catalogue, not a sourced lore claim.

## Engine Inputs

| Field | Value |
| --- | --- |
| Produced by (industry tags) | `herb`, `spice` |
| Demand index | 0.28 |
| Luxury (wealth elasticity) | 0.3 |
| Perishable | 0 |
| Demand traits | `desert` 1.5, `port` 1.2 |
| Storage | 365 days capacity, 0.08% stock loss a day, 45 reserve days |
| Harvest or production calendar | Mirtul 2%, Kythorn 8%, Flamerule 16%, Eleasis 25%, Eleint 33%, Marpenoth 16% |
| Regional calendar (cold) | Flamerule 7%, Eleasis 27%, Eleint 53%, Marpenoth 13% |
| Regional calendar (arid) | Hammer 2%, Alturiak 3%, Ches 7%, Tarsakh 13%, Mirtul 13%, Kythorn 7%, Flamerule 1%, Eleasis 3%, Eleint 13%, Marpenoth 20%, Uktar 13%, Nightal 3% |
| Regional calendar (tropical) | Hammer 6%, Alturiak 6%, Ches 12%, Tarsakh 12%, Mirtul 6%, Kythorn 6%, Flamerule 6%, Eleasis 6%, Eleint 12%, Marpenoth 12%, Uktar 6%, Nightal 6% |

## Where the Engine Places It

Settlements carrying each producer tag: `herb` 8, `spice` 4 (of 325 stored settlements).

## Sources

- Engine record: [`faerun/data/store/commodities.json`](../../../faerun/data/store/commodities.json), with storage and recipe values as applied at load time by [`faerun/data/commodities.py`](../../../faerun/data/commodities.py). Read 2026-10-04.
- Settlement placements: [`faerun/data/store/settlements.json`](../../../faerun/data/store/settlements.json), read 2026-10-04.
