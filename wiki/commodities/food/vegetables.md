# Vegetables

[Commodity index](../README.md) · [Food](README.md)

**Status:** In the engine  
**Engine ID:** `vegetables`  
**Category:** food  
**Trade unit:** crate (40 lb)  
**Base price:** 0.6 gp per crate (about 0.015 gp per lb)  
**Production type:** raw  
**Aurora's Whole Realms Catalogue:** no matching entry in the sections reviewed

## Engine Description

> Vegetables is a food good in Faerûn, traded in crate lots for daily use, craft, and commerce. A staple trade good prized for daily sustenance and household use.

This is a model input stored in the catalogue, not a sourced lore claim.

## Engine Inputs

| Field | Value |
| --- | --- |
| Produced by (industry tags) | `farm` |
| Demand index | 2 |
| Luxury (wealth elasticity) | 0 |
| Perishable | 0.8 |
| Legacy season multipliers | `summer` 0.75, `autumn` 0.7, `winter` 1.6 |
| Storage | 14 days capacity, 5% stock loss a day, 2 reserve days |
| Harvest or production calendar | Ches 1%, Tarsakh 3%, Mirtul 7%, Kythorn 13%, Flamerule 20%, Eleasis 20%, Eleint 20%, Marpenoth 13%, Uktar 3% |
| Regional calendar (cold) | Kythorn 3%, Flamerule 20%, Eleasis 40%, Eleint 30%, Marpenoth 7% |
| Regional calendar (arid) | Hammer 6%, Alturiak 11%, Ches 17%, Tarsakh 11%, Mirtul 6%, Kythorn 1%, Flamerule 1%, Eleasis 1%, Eleint 6%, Marpenoth 11%, Uktar 17%, Nightal 11% |
| Regional calendar (tropical) | Hammer 6%, Alturiak 6%, Ches 9%, Tarsakh 12%, Mirtul 9%, Kythorn 6%, Flamerule 6%, Eleasis 6%, Eleint 9%, Marpenoth 12%, Uktar 9%, Nightal 6% |

## Where the Engine Places It

Settlements carrying each producer tag: `farm` 50 (of 325 stored settlements).

**Specialty at:** Goldenfields (2).

**Configured shortage at:** Blingdenstone, Boareskyr Bridge, Candlekeep, Citadel Adbar, Gracklstugh, Mantol-Derith, Menzoberranzan, Messemprar, Mirabar, Mithral Hall, Orlumbor, Parnast, Sshamath.

## Related Catalogue Goods (Proposed)

Aurora's entries with no engine equivalent whose closest engine commodity is Vegetables:

[Beetroot relish](../food/beetroot-relish.md), [Brandied fruits](../food/brandied-fruits.md), [Candied fruits and herbs](../food/candied-fruits-and-herbs.md), [Crystallized flowers and fruit](../food/crystallized-flowers-and-fruit.md), [Moonshae chestnuts in syrup](../food/moonshae-chestnuts-in-syrup.md), [Mustard (prepared)](../food/mustard-prepared.md), [Pickles](../food/pickles.md), [Sauerkraut](../food/sauerkraut.md), [Scented water](../food/scented-water.md), [Vinegar](../food/vinegar.md).

## Sources

- Engine record: [`faerun/data/store/commodities.json`](../../../faerun/data/store/commodities.json), with storage and recipe values as applied at load time by [`faerun/data/commodities.py`](../../../faerun/data/commodities.py). Read 2026-10-04.
- Settlement placements: [`faerun/data/store/settlements.json`](../../../faerun/data/store/settlements.json), read 2026-10-04.
