# Olive oil

[Commodity index](../README.md) · [Food](README.md)

**Status:** In the engine  
**Engine ID:** `olive_oil`  
**Category:** food  
**Trade unit:** amphora (30 lb)  
**Base price:** 4 gp per amphora (about 0.133 gp per lb)  
**Production type:** processed or manufactured  
**Aurora's Whole Realms Catalogue:** listed (see below)

## Engine Description

> Olive oil is a food good in Faerûn, traded in amphora lots for daily use, craft, and commerce. A staple trade good prized for daily sustenance and household use.

This is a model input stored in the catalogue, not a sourced lore claim.

## Engine Inputs

| Field | Value |
| --- | --- |
| Produced by (industry tags) | `orchard`, `oil` |
| Demand index | 0.8 |
| Luxury (wealth elasticity) | 0 |
| Perishable | 0.15 |
| Storage | 365 days capacity, 0.08% stock loss a day, 30 reserve days |

## Recipe Links

Inputs for one amphora: [Olives](../food/olives.md) 0.7.

Used as an input for: [Ink](../product/ink.md) (0.01 per unit), [Lamp oil](../product/lamp-oil.md) (0.07 per unit), [Perfume](../luxury/perfume.md) (0.02 per unit), [Soap](../product/soap.md) (0.25 per unit).

## Where the Engine Places It

Settlements carrying each producer tag: `orchard` 4, `oil` 0 (of 325 stored settlements).

## Aurora's Whole Realms Catalogue

| Catalogue section | Printed page | Variant | Unit | Catalogue price | Price per lb |
| --- | --- | --- | --- | --- | --- |
| Aurora's Larder | 117 |  | gal | 5 gp | 0.602 gp |

Engine price per lb is **0.221 times** the median catalogue price per lb for this entry (engine 0.133 gp/lb; catalogue median 0.602 gp/lb). The two are within a factor of five.

## Related Catalogue Goods (Proposed)

Aurora's entries with no engine equivalent whose closest engine commodity is Olive oil:

[Almond oil](../food/almond-oil.md), [Hazelnut oil](../food/hazelnut-oil.md), [Mixed herb oil](../food/mixed-herb-oil.md), [Rapeseed oil](../food/rapeseed-oil.md), [Safflower oil](../food/safflower-oil.md), [Sesame oil](../food/sesame-oil.md), [Sunflower oil](../food/sunflower-oil.md), [Walnut oil](../food/walnut-oil.md).

## Sources

- Engine record: [`faerun/data/store/commodities.json`](../../../faerun/data/store/commodities.json), with storage and recipe values as applied at load time by [`faerun/data/commodities.py`](../../../faerun/data/commodities.py). Read 2026-10-04.
- Settlement placements: [`faerun/data/store/settlements.json`](../../../faerun/data/store/settlements.json), read 2026-10-04.
- *Aurora's Whole Realms Catalogue* (TSR 9358, 1992, AD&D 2nd edition), J. Robert King and Co., design concept Anne Brown. Primary source, consulted directly from the project copy in [`.guides/`](../../../.guides/tsr09358%20-%20Aurora's_Whole_Realms_Catalogue.pdf) on 2026-10-04. Page numbers are the printed folios. Prices are the catalogue's retail mail-order prices; descriptions here are paraphrased.
