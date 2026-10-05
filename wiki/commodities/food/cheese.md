# Cheese

[Commodity index](../README.md) · [Food](README.md)

**Status:** In the engine  
**Engine ID:** `cheese`  
**Category:** food  
**Trade unit:** wheel (20 lb)  
**Base price:** 1.2 gp per wheel (about 0.06 gp per lb)  
**Production type:** raw  
**Aurora's Whole Realms Catalogue:** no matching entry in the sections reviewed

## Engine Description

> Cheese is a food good in Faerûn, traded in wheel lots for daily use, craft, and commerce. A staple trade good prized for daily sustenance and household use.

This is a model input stored in the catalogue, not a sourced lore claim.

## Engine Inputs

| Field | Value |
| --- | --- |
| Produced by (industry tags) | `herd`, `cattle` |
| Demand index | 1.4 |
| Luxury (wealth elasticity) | 0 |
| Perishable | 0.35 |
| Storage | 90 days capacity, 0.4% stock loss a day, 10 reserve days |

## Where the Engine Places It

Settlements carrying each producer tag: `herd` 11, `cattle` 7 (of 325 stored settlements).

**Specialty at:** Ashabenford (2), Caer Calidyrr (2).

## Related Catalogue Goods (Proposed)

Aurora's entries with no engine equivalent whose closest engine commodity is Cheese:

[Arabellan cheddar](../food/arabellan-cheddar.md), [Chessentan lotus cheese](../food/chessentan-lotus-cheese.md), [Damarite red](../food/damarite-red.md), [Death cheese](../food/death-cheese.md), [Elturian grey](../food/elturian-grey.md), [Farmer's cheese](../food/farmers-cheese.md), [Green Calishite](../food/green-calishite.md), [Luiren spring cheese](../food/luiren-spring-cheese.md), [Mist cheese](../food/mist-cheese.md), [Nut cheese](../food/nut-cheese.md), [Pepper cheese](../food/pepper-cheese.md), [Turmish brick](../food/turmish-brick.md), [Vilhon blanc](../food/vilhon-blanc.md), [Waterdhavian cheese](../food/waterdhavian-cheese.md), [Yak butter](../food/yak-butter.md).

## Sources

- Engine record: [`faerun/data/store/commodities.json`](../../../faerun/data/store/commodities.json), with storage and recipe values as applied at load time by [`faerun/data/commodities.py`](../../../faerun/data/commodities.py). Read 2026-10-04.
- Settlement placements: [`faerun/data/store/settlements.json`](../../../faerun/data/store/settlements.json), read 2026-10-04.
