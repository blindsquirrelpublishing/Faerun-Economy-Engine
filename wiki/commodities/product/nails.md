# Nails and fittings

[Commodity index](../README.md) · [Manufactured products](README.md)

**Status:** In the engine  
**Engine ID:** `nails`  
**Category:** product  
**Trade unit:** keg (30 lb)  
**Base price:** 3 gp per keg (about 0.1 gp per lb)  
**Production type:** processed or manufactured  
**Aurora's Whole Realms Catalogue:** listed (see below)

## Engine Description

> Nails and fittings is a product good in Faerûn, traded in keg lots for daily use, craft, and commerce. A practical manufactured good made for everyday trade and labor.

This is a model input stored in the catalogue, not a sourced lore claim.

## Engine Inputs

| Field | Value |
| --- | --- |
| Produced by (industry tags) | `smith` |
| Demand index | 1 |
| Luxury (wealth elasticity) | 0 |
| Perishable | 0 |
| Demand traits | `frontier` 1.5, `port` 1.3 |
| Storage | 365 days capacity, 0.01% stock loss a day, 15 reserve days |

## Recipe Links

Inputs for one keg: [Wrought iron](../metal/iron-ingot.md) 3.

Used as an input for: [Cart](../product/cart.md) (0.2 per unit), [River boat](../product/ship-boat.md) (4 per unit), [Wagon](../product/wagon.md) (0.5 per unit).

## Where the Engine Places It

Settlements carrying each producer tag: `smith` 33 (of 325 stored settlements).

## Aurora's Whole Realms Catalogue

Finishing nails, joiners' nails and iron spikes for wood, metal and stone.

| Catalogue section | Printed page | Variant | Unit | Catalogue price | Price per lb |
| --- | --- | --- | --- | --- | --- |
| Laborers' List | 56 | 1 in finishing nails | lb | 2 sp | 0.2 gp |
| Laborers' List | 56 | 2-3 in joiners' nails | lb | 1 sp | 0.1 gp |
| Laborers' List | 56 | 6 in spikes | dozen | 3 gp |  |
| Laborers' List | 56 | 12 in spikes | dozen | 5 gp |  |

Engine price per lb is **0.667 times** the median catalogue price per lb for this entry (engine 0.1 gp/lb; catalogue median 0.15 gp/lb). The two are within a factor of five.

## Related Catalogue Goods (Proposed)

Aurora's entries with no engine equivalent whose closest engine commodity is Nails and fittings:

[Bolts and nuts](../product/bolts-and-nuts.md), [Mortar](../product/mortar.md), [Smith's fat and wax](../product/smiths-fat-and-wax.md), [Wood glue](../product/wood-glue.md), [Wooden peg stock](../product/wooden-peg-stock.md).

## Sources

- Engine record: [`faerun/data/store/commodities.json`](../../../faerun/data/store/commodities.json), with storage and recipe values as applied at load time by [`faerun/data/commodities.py`](../../../faerun/data/commodities.py). Read 2026-10-04.
- Settlement placements: [`faerun/data/store/settlements.json`](../../../faerun/data/store/settlements.json), read 2026-10-04.
- *Aurora's Whole Realms Catalogue* (TSR 9358, 1992, AD&D 2nd edition), J. Robert King and Co., design concept Anne Brown. Primary source, consulted directly from the project copy in [`.guides/`](../../../.guides/tsr09358%20-%20Aurora's_Whole_Realms_Catalogue.pdf) on 2026-10-04. Page numbers are the printed folios. Prices are the catalogue's retail mail-order prices; descriptions here are paraphrased.
