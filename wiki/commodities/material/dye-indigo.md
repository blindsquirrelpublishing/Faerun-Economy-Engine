# Indigo and common dyes

[Commodity index](../README.md) · [Materials](README.md)

**Status:** In the engine  
**Engine ID:** `dye_indigo`  
**Category:** material  
**Trade unit:** pound (1 lb)  
**Base price:** 8 gp per pound (about 8 gp per lb)  
**Production type:** raw  
**Aurora's Whole Realms Catalogue:** listed (see below)

## Engine Description

> Indigo and common dyes is a material good in Faerûn, traded in pound lots for daily use, craft, and commerce. A bulk material that serves as the foundation of building, crafting, and repair.

This is a model input stored in the catalogue, not a sourced lore claim.

## Engine Inputs

| Field | Value |
| --- | --- |
| Produced by (industry tags) | `dye`, `herb` |
| Demand index | 0.25 |
| Luxury (wealth elasticity) | 0.4 |
| Perishable | 0 |
| Storage | 365 days capacity, 0.01% stock loss a day, 15 reserve days |

## Recipe Links

Used as an input for: [Dyed cloth](../textile/cloth-dyed.md) (0.25 per unit).

## Where the Engine Places It

Settlements carrying each producer tag: `dye` 2, `herb` 8 (of 325 stored settlements).

## Aurora's Whole Realms Catalogue

| Catalogue section | Printed page | Variant | Unit | Catalogue price | Price per lb |
| --- | --- | --- | --- | --- | --- |
| Tailors' Corner | 76 |  | 8 oz | 3 gp | 6 gp |

Engine price per lb is **1.33 times** the median catalogue price per lb for this entry (engine 8 gp/lb; catalogue median 6 gp/lb). The two are within a factor of five.

## Related Catalogue Goods (Proposed)

Aurora's entries with no engine equivalent whose closest engine commodity is Indigo and common dyes:

[Calimshan blue dye](../material/calimshan-blue-dye.md), [Cochineal red dye](../material/cochineal-red-dye.md), [Copper blue dye](../material/copper-blue-dye.md), [Iron red dye](../material/iron-red-dye.md), [Mollusk green dye](../material/mollusk-green-dye.md), [Mollusk red dye](../material/mollusk-red-dye.md), [Ocher dye](../material/ocher-dye.md), [Safflower dye](../material/safflower-dye.md), [Sulfur yellow dye](../material/sulfur-yellow-dye.md), [Ultramarine blue dye](../material/ultramarine-blue-dye.md), [Vermilion dye](../material/vermilion-dye.md).

## Sources

- Engine record: [`faerun/data/store/commodities.json`](../../../faerun/data/store/commodities.json), with storage and recipe values as applied at load time by [`faerun/data/commodities.py`](../../../faerun/data/commodities.py). Read 2026-10-04.
- Settlement placements: [`faerun/data/store/settlements.json`](../../../faerun/data/store/settlements.json), read 2026-10-04.
- *Aurora's Whole Realms Catalogue* (TSR 9358, 1992, AD&D 2nd edition), J. Robert King and Co., design concept Anne Brown. Primary source, consulted directly from the project copy in [`.guides/`](../../../.guides/tsr09358%20-%20Aurora's_Whole_Realms_Catalogue.pdf) on 2026-10-04. Page numbers are the printed folios. Prices are the catalogue's retail mail-order prices; descriptions here are paraphrased.
