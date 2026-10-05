# Medicinal herbs

[Commodity index](../README.md) · [Arcane goods](README.md)

**Status:** In the engine  
**Engine ID:** `herbs_healing`  
**Category:** arcane  
**Trade unit:** bundle (2 lb)  
**Base price:** 3 gp per bundle (about 1.5 gp per lb)  
**Production type:** raw  
**Aurora's Whole Realms Catalogue:** no matching entry in the sections reviewed

## Engine Description

> Medicinal herbs is a arcane good in Faerûn, traded in bundle lots for daily use, craft, and commerce. A magical trade good used by spellcasters, scholars, and ritualists.

This is a model input stored in the catalogue, not a sourced lore claim.

## Engine Inputs

| Field | Value |
| --- | --- |
| Produced by (industry tags) | `herb`, `farm` |
| Demand index | 0.6 |
| Luxury (wealth elasticity) | 0 |
| Perishable | 0 |
| Demand traits | `temple` 2, `military` 1.8, `wartorn` 2.5 |
| Storage | 270 days capacity, 0.15% stock loss a day, 60 reserve days |
| Harvest or production calendar | Ches 2%, Tarsakh 7%, Mirtul 16%, Kythorn 25%, Flamerule 25%, Eleasis 16%, Eleint 8%, Marpenoth 2% |
| Regional calendar (cold) | Kythorn 10%, Flamerule 30%, Eleasis 40%, Eleint 20% |
| Regional calendar (arid) | Hammer 4%, Alturiak 7%, Ches 22%, Tarsakh 22%, Mirtul 7%, Kythorn 1%, Flamerule 1%, Eleasis 1%, Eleint 7%, Marpenoth 15%, Uktar 7%, Nightal 4% |
| Regional calendar (tropical) | Hammer 6%, Alturiak 6%, Ches 12%, Tarsakh 12%, Mirtul 6%, Kythorn 6%, Flamerule 6%, Eleasis 6%, Eleint 12%, Marpenoth 12%, Uktar 6%, Nightal 6% |

## Recipe Links

Used as an input for: [Antitoxin](../arcane/antitoxin.md) (0.1 per unit), [Potion of healing](../arcane/potion-healing.md) (0.2 per unit).

## Where the Engine Places It

Settlements carrying each producer tag: `herb` 8, `farm` 50 (of 325 stored settlements).

**Specialty at:** [Hlondeth](../../../locations/hlondeth.md) (1), Shadowdale (2), Velprintalar (3).

## Sources

- Engine record: [`faerun/data/store/commodities.json`](../../../faerun/data/store/commodities.json), with storage and recipe values as applied at load time by [`faerun/data/commodities.py`](../../../faerun/data/commodities.py). Read 2026-10-04.
- Settlement placements: [`faerun/data/store/settlements.json`](../../../faerun/data/store/settlements.json), read 2026-10-04.
