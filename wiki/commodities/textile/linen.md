# Linen cloth

[Commodity index](../README.md) · [Textiles](README.md)

**Status:** In the engine  
**Engine ID:** `linen`  
**Category:** textile  
**Trade unit:** bolt (25 lb)  
**Base price:** 5 gp per bolt (about 0.2 gp per lb)  
**Production type:** raw  
**Aurora's Whole Realms Catalogue:** listed (see below)

## Engine Description

> Linen cloth is a textile good in Faerûn, traded in bolt lots for daily use, craft, and commerce. A woven textile valued for clothing, furnishing, and caravan gear.

This is a model input stored in the catalogue, not a sourced lore claim.

## Engine Inputs

| Field | Value |
| --- | --- |
| Produced by (industry tags) | `textile`, `farm` |
| Demand index | 1.1 |
| Luxury (wealth elasticity) | 0 |
| Perishable | 0 |
| Storage | 400 days capacity, 0.04% stock loss a day, 45 reserve days |

## Recipe Links

Used as an input for: [Dyed cloth](../textile/cloth-dyed.md) (1 per unit), [Common clothing](../product/clothing-common.md) (0.15 per unit), [Sailcloth and canvas](../product/sailcloth.md) (1.2 per unit).

## Where the Engine Places It

Settlements carrying each producer tag: `textile` 23, `farm` 50 (of 325 stored settlements).

## Aurora's Whole Realms Catalogue

### Catalogue entry: Linen cloth (component)

| Catalogue section | Printed page | Variant | Unit | Catalogue price | Price per lb |
| --- | --- | --- | --- | --- | --- |
| Priests' Alcove (spell components) | 38 | Linen cloth | 5 in sq | 1 cp |  |
| Priests' Alcove (spell components) | 38 | gold wefted | 5 in sq | 10 gp |  |

Component rows are priced for small laboratory or altar quantities, so they are not compared with the engine's bulk price.

### Catalogue entry: Daerlunian linen

| Catalogue section | Printed page | Variant | Unit | Catalogue price | Price per lb |
| --- | --- | --- | --- | --- | --- |
| Tailors' Corner | 75 |  | sq yd | 8 sp |  |

## Related Catalogue Goods (Proposed)

Aurora's entries with no engine equivalent whose closest engine commodity is Linen cloth:

[Daerlunian wool cloth](../textile/daerlunian-wool-cloth.md), [Homespun](../textile/homespun.md), [Lace](../textile/lace.md), [Maztican white cloth](../textile/maztican-white-cloth.md), [Thread](../textile/thread.md), [Ticking](../textile/ticking.md), [Velvet](../textile/velvet.md), [Wool flannel](../textile/wool-flannel.md), [Yarn](../textile/yarn.md).

## Sources

- Engine record: [`faerun/data/store/commodities.json`](../../../faerun/data/store/commodities.json), with storage and recipe values as applied at load time by [`faerun/data/commodities.py`](../../../faerun/data/commodities.py). Read 2026-10-04.
- Settlement placements: [`faerun/data/store/settlements.json`](../../../faerun/data/store/settlements.json), read 2026-10-04.
- *Aurora's Whole Realms Catalogue* (TSR 9358, 1992, AD&D 2nd edition), J. Robert King and Co., design concept Anne Brown. Primary source, consulted directly from the project copy in [`.guides/`](../../../.guides/tsr09358%20-%20Aurora's_Whole_Realms_Catalogue.pdf) on 2026-10-04. Page numbers are the printed folios. Prices are the catalogue's retail mail-order prices; descriptions here are paraphrased.
