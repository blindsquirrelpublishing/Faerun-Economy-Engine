# Sugar loaf

[Commodity index](../README.md) · [Food](README.md)

**Status:** In the engine  
**Engine ID:** `sugar`  
**Category:** food  
**Trade unit:** cone (10 lb)  
**Base price:** 6 gp per cone (about 0.6 gp per lb)  
**Production type:** raw  
**Aurora's Whole Realms Catalogue:** listed (see below)

## Engine Description

> Sugar loaf is a food good in Faerûn, traded in cone lots for daily use, craft, and commerce. A staple trade good prized for daily sustenance and household use.

This is a model input stored in the catalogue, not a sourced lore claim.

## Engine Inputs

| Field | Value |
| --- | --- |
| Produced by (industry tags) | `sugar` |
| Demand index | 0.4 |
| Luxury (wealth elasticity) | 0.6 |
| Perishable | 0 |
| Demand traits | `noble` 2, `jungle` 0.5 |
| Storage | 730 days capacity, 0.005% stock loss a day, 45 reserve days |

## Where the Engine Places It

Settlements carrying each producer tag: `sugar` 1 (of 325 stored settlements).

**Specialty at:** Calimport (2), Port Nyanzaru (2).

## Aurora's Whole Realms Catalogue

| Catalogue section | Printed page | Variant | Unit | Catalogue price | Price per lb |
| --- | --- | --- | --- | --- | --- |
| Priests' Alcove (spell components) | 38 | cube | 25 | 2 gp |  |
| Priests' Alcove (spell components) | 38 | granular | 1/2 lb | 6 gp | 12 gp |
| Aurora's Larder | 117 | brown | lb. | 1 gp | 1 gp |
| Aurora's Larder | 117 | lavender | lb. | 10 gp | 10 gp |
| Aurora's Larder | 117 | loaf | lb. | 3 gp | 3 gp |
| Aurora's Larder | 117 | lemon | lb. | 15 gp | 15 gp |
| Aurora's Larder | 117 | mace | lb. | 35 gp | 35 gp |
| Aurora's Larder | 117 | orange | lb. | 15 gp | 15 gp |
| Aurora's Larder | 118 | powdered | lb. | 5 gp | 5 gp |
| Aurora's Larder | 118 | raw | lb. | 5 sp | 0.5 gp |
| Aurora's Larder | 118 | rose | lb. | 7 gp | 7 gp |
| Aurora's Larder | 118 | violet | lb. | 8 gp | 8 gp |

Engine price per lb is **0.08 times** the median catalogue price per lb for this entry (engine 0.6 gp/lb; catalogue median 7.5 gp/lb). The catalogue is far above the engine here, which is normal for its retail luxury pricing.

## Related Catalogue Goods (Proposed)

Aurora's entries with no engine equivalent whose closest engine commodity is Sugar loaf:

[Marzipan](../food/marzipan.md), [Molasses](../food/molasses.md), [Sorghum](../food/sorghum.md).

## Sources

- Engine record: [`faerun/data/store/commodities.json`](../../../faerun/data/store/commodities.json), with storage and recipe values as applied at load time by [`faerun/data/commodities.py`](../../../faerun/data/commodities.py). Read 2026-10-04.
- Settlement placements: [`faerun/data/store/settlements.json`](../../../faerun/data/store/settlements.json), read 2026-10-04.
- *Aurora's Whole Realms Catalogue* (TSR 9358, 1992, AD&D 2nd edition), J. Robert King and Co., design concept Anne Brown. Primary source, consulted directly from the project copy in [`.guides/`](../../../.guides/tsr09358%20-%20Aurora's_Whole_Realms_Catalogue.pdf) on 2026-10-04. Page numbers are the printed folios. Prices are the catalogue's retail mail-order prices; descriptions here are paraphrased.
