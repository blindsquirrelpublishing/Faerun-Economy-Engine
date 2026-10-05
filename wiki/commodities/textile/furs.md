# Furs

[Commodity index](../README.md) · [Textiles](README.md)

**Status:** In the engine  
**Engine ID:** `furs`  
**Category:** textile  
**Trade unit:** bundle (25 lb)  
**Base price:** 20 gp per bundle (about 0.8 gp per lb)  
**Production type:** raw  
**Aurora's Whole Realms Catalogue:** no matching entry in the sections reviewed

## Engine Description

> Furs is a textile good in Faerûn, traded in bundle lots for daily use, craft, and commerce. A woven or worked textile valued for clothing, shelter, and travel.

This is a model input stored in the catalogue, not a sourced lore claim.

## Engine Inputs

| Field | Value |
| --- | --- |
| Produced by (industry tags) | `hunt` |
| Demand index | 0.4 |
| Luxury (wealth elasticity) | 0.6 |
| Perishable | 0 |
| Demand traits | `cold` 2.5, `noble` 2 |
| Legacy season multipliers | `winter` 1.5, `autumn` 1.2, `summer` 0.7 |
| Storage | 400 days capacity, 0.04% stock loss a day, 45 reserve days |
| Demand calendar | Hammer 10%, Alturiak 10%, Ches 9%, Tarsakh 8%, Mirtul 7%, Kythorn 6%, Flamerule 6%, Eleasis 6%, Eleint 8%, Marpenoth 9%, Uktar 10%, Nightal 10% |

## Where the Engine Places It

Settlements carrying each producer tag: `hunt` 6 (of 325 stored settlements).

**Configured shortage at:** Halarahh.

## Related Catalogue Goods (Proposed)

Aurora's entries with no engine equivalent whose closest engine commodity is Furs:

[Bear skin](../textile/bear-skin.md), [Black sable skin](../textile/black-sable-skin.md), [Deer skin](../textile/deer-skin.md), [Feathers](../textile/feathers.md), [Fox skin](../textile/fox-skin.md), [Horsehide](../textile/horsehide.md), [Jaguar skin](../textile/jaguar-skin.md), [Leopard skin](../textile/leopard-skin.md), [Lion skin](../textile/lion-skin.md), [Marten skin](../textile/marten-skin.md), [Mink skin](../textile/mink-skin.md), [Panther skin](../textile/panther-skin.md), [Raccoon skin](../textile/raccoon-skin.md), [Shark skin](../textile/shark-skin.md), [Sheep skin](../textile/sheep-skin.md), [Squirrel skin](../textile/squirrel-skin.md), [Tiger skin](../textile/tiger-skin.md), [Wolf skin](../textile/wolf-skin.md).

## Sources

- Engine record: [`faerun/data/store/commodities.json`](../../../faerun/data/store/commodities.json), with storage and recipe values as applied at load time by [`faerun/data/commodities.py`](../../../faerun/data/commodities.py). Read 2026-10-04.
- Settlement placements: [`faerun/data/store/settlements.json`](../../../faerun/data/store/settlements.json), read 2026-10-04.
