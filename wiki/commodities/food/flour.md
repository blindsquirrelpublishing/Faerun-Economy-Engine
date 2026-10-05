# Milled flour

[Commodity index](../README.md) · [Food](README.md)

**Status:** In the engine  
**Engine ID:** `flour`  
**Category:** food  
**Trade unit:** sack (50 lb)  
**Base price:** 0.9 gp per sack (about 0.018 gp per lb)  
**Production type:** processed or manufactured  
**Aurora's Whole Realms Catalogue:** listed (see below)

## Engine Description

> Milled flour is a food good in Faerûn, traded in sack lots for daily use, craft, and commerce. A staple trade good prized for daily sustenance and household use.

This is a model input stored in the catalogue, not a sourced lore claim.

## Engine Inputs

| Field | Value |
| --- | --- |
| Produced by (industry tags) | `farm`, `craft` |
| Demand index | 2.2 |
| Luxury (wealth elasticity) | 0 |
| Perishable | 0.2 |
| Legacy season multipliers | `spring` 1.2 |
| Storage | 120 days capacity, 0.2% stock loss a day, 20 reserve days |

## Recipe Links

Inputs for one sack: [Grain (wheat)](../food/grain.md) 0.9.

Used as an input for: [Bread](../food/bread.md) (0.02 per unit).

## Where the Engine Places It

Settlements carrying each producer tag: `farm` 50, `craft` 82 (of 325 stored settlements).

## Aurora's Whole Realms Catalogue

| Catalogue section | Printed page | Variant | Unit | Catalogue price | Price per lb |
| --- | --- | --- | --- | --- | --- |
| Aurora's Larder | 115 |  | lb | 3 gp | 3 gp |

Engine price per lb is **0.006 times** the median catalogue price per lb for this entry (engine 0.018 gp/lb; catalogue median 3 gp/lb). The catalogue is far above the engine here, which is normal for its retail luxury pricing.

## Related Catalogue Goods (Proposed)

Aurora's entries with no engine equivalent whose closest engine commodity is Milled flour:

[Barley flour](../food/barley-flour.md), [Buckwheat flour](../food/buckwheat-flour.md), [Rye flour](../food/rye-flour.md).

## Sources

- Engine record: [`faerun/data/store/commodities.json`](../../../faerun/data/store/commodities.json), with storage and recipe values as applied at load time by [`faerun/data/commodities.py`](../../../faerun/data/commodities.py). Read 2026-10-04.
- Settlement placements: [`faerun/data/store/settlements.json`](../../../faerun/data/store/settlements.json), read 2026-10-04.
- *Aurora's Whole Realms Catalogue* (TSR 9358, 1992, AD&D 2nd edition), J. Robert King and Co., design concept Anne Brown. Primary source, consulted directly from the project copy in [`.guides/`](../../../.guides/tsr09358%20-%20Aurora's_Whole_Realms_Catalogue.pdf) on 2026-10-04. Page numbers are the printed folios. Prices are the catalogue's retail mail-order prices; descriptions here are paraphrased.
