# Bread

[Commodity index](../README.md) · [Food](README.md)

**Status:** In the engine  
**Engine ID:** `bread`  
**Category:** food  
**Trade unit:** loaf (1 lb)  
**Base price:** 0.02 gp per loaf (about 0.02 gp per lb)  
**Production type:** processed or manufactured  
**Aurora's Whole Realms Catalogue:** no matching entry in the sections reviewed

## Engine Description

> Bread is a food good in Faerûn, traded in loaf lots for daily use, craft, and commerce. A staple trade good prized for daily sustenance and household use.

This is a model input stored in the catalogue, not a sourced lore claim.

## Engine Inputs

| Field | Value |
| --- | --- |
| Produced by (industry tags) | `farm`, `craft` |
| Demand index | 3.2 |
| Luxury (wealth elasticity) | 0 |
| Perishable | 0.9 |
| Legacy season multipliers | `spring` 1.2 |
| Storage | 3 days capacity, 25% stock loss a day, 0.5 reserve days |

## Recipe Links

Inputs for one loaf: [Milled flour](../food/flour.md) 0.02, [Salt](../food/salt.md) 0.001.

## Where the Engine Places It

Settlements carrying each producer tag: `farm` 50, `craft` 82 (of 325 stored settlements).

## Related Catalogue Goods (Proposed)

Aurora's entries with no engine equivalent whose closest engine commodity is Bread:

[Blackbread](../food/blackbread.md), [Elven bread](../food/elven-bread.md), [Fruitcake](../food/fruitcake.md), [Gingerbread](../food/gingerbread.md), [Hard-tack](../food/hard-tack.md), [Herb crackers](../food/herb-crackers.md), [Noodles](../food/noodles.md), [Sourdough](../food/sourdough.md), [Tarts](../food/tarts.md), [Tortillas](../food/tortillas.md).

## Sources

- Engine record: [`faerun/data/store/commodities.json`](../../../faerun/data/store/commodities.json), with storage and recipe values as applied at load time by [`faerun/data/commodities.py`](../../../faerun/data/commodities.py). Read 2026-10-04.
- Settlement placements: [`faerun/data/store/settlements.json`](../../../faerun/data/store/settlements.json), read 2026-10-04.
