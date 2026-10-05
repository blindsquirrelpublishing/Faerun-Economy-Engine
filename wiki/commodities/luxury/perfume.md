# Perfume

[Commodity index](../README.md) · [Luxury goods](README.md)

**Status:** In the engine  
**Engine ID:** `perfume`  
**Category:** luxury  
**Trade unit:** vial (0.5 lb)  
**Base price:** 12 gp per vial (about 24 gp per lb)  
**Production type:** processed or manufactured  
**Aurora's Whole Realms Catalogue:** listed (see below)

## Engine Description

> Perfume is a luxury good in Faerûn, traded in vial lots for daily use, craft, and commerce. A refined luxury good sought by elites, merchants, and collectors.

This is a model input stored in the catalogue, not a sourced lore claim.

## Engine Inputs

| Field | Value |
| --- | --- |
| Produced by (industry tags) | `alch`, `spice` |
| Demand index | 0.1 |
| Luxury (wealth elasticity) | 0.95 |
| Perishable | 0 |
| Demand traits | `noble` 3.5, `cosmopolitan` 2 |
| Storage | 365 days capacity, 0.01% stock loss a day, 15 reserve days |

## Recipe Links

Inputs for one vial: [Exotic spices](../luxury/spices-exotic.md) 0.1, [Olive oil](../food/olive-oil.md) 0.02.

## Where the Engine Places It

Settlements carrying each producer tag: `alch` 17, `spice` 4 (of 325 stored settlements).

**Specialty at:** Athkatla (2), Calimport (3).

## Aurora's Whole Realms Catalogue

Westgate scent-makers' perfumes in four grades, from simple cover scents to the single peerless grade; also scented face and body powders.

**Origin given:** Westgate.

| Catalogue section | Printed page | Variant | Unit | Catalogue price | Price per lb |
| --- | --- | --- | --- | --- | --- |
| Personal Supplies | 100 | simple | vial | 1 gp |  |
| Personal Supplies | 100 | fine | vial | 3 gp |  |
| Personal Supplies | 100 | very fine | vial | 5 gp |  |
| Personal Supplies | 100 | peerless (Sune's Fire) | vial | 10 gp |  |
| Personal Supplies | 100 | face and body powder | oz | 5 sp | 8 gp |

Engine price per lb is **3 times** the median catalogue price per lb for this entry (engine 24 gp/lb; catalogue median 8 gp/lb). The two are within a factor of five.

## Related Catalogue Goods (Proposed)

Aurora's entries with no engine equivalent whose closest engine commodity is Perfume:

[Bath oil](../luxury/bath-oil.md), [Sachets](../luxury/sachets.md).

## Sources

- Engine record: [`faerun/data/store/commodities.json`](../../../faerun/data/store/commodities.json), with storage and recipe values as applied at load time by [`faerun/data/commodities.py`](../../../faerun/data/commodities.py). Read 2026-10-04.
- Settlement placements: [`faerun/data/store/settlements.json`](../../../faerun/data/store/settlements.json), read 2026-10-04.
- *Aurora's Whole Realms Catalogue* (TSR 9358, 1992, AD&D 2nd edition), J. Robert King and Co., design concept Anne Brown. Primary source, consulted directly from the project copy in [`.guides/`](../../../.guides/tsr09358%20-%20Aurora's_Whole_Realms_Catalogue.pdf) on 2026-10-04. Page numbers are the printed folios. Prices are the catalogue's retail mail-order prices; descriptions here are paraphrased.
