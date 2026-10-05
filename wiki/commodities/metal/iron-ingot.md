# Wrought iron

[Commodity index](../README.md) · [Metals](README.md)

**Status:** In the engine  
**Engine ID:** `iron_ingot`  
**Category:** metal  
**Trade unit:** ingot (10 lb)  
**Base price:** 1 gp per ingot (about 0.1 gp per lb)  
**Production type:** processed or manufactured  
**Aurora's Whole Realms Catalogue:** listed (see below)

## Engine Description

> Wrought iron is a metal good in Faerûn, traded in ingot lots for daily use, craft, and commerce. A mineral or refined metal traded for tools, industry, and coinage.

This is a model input stored in the catalogue, not a sourced lore claim.

## Engine Inputs

| Field | Value |
| --- | --- |
| Produced by (industry tags) | `smith`, `mine_iron` |
| Demand index | 1.5 |
| Luxury (wealth elasticity) | 0 |
| Perishable | 0 |
| Demand traits | `dwarven` 1.5, `military` 1.5 |
| Storage | 365 days capacity, 0.01% stock loss a day, 15 reserve days |

## Recipe Links

Inputs for one ingot: [Iron ore](../metal/iron-ore.md) 0.15, [Charcoal](../material/charcoal.md) 0.04.

Used as an input for: [Barrel (empty)](../product/barrel.md) (0.1 per unit), [Hooded lantern](../product/lantern.md) (0.15 per unit), [Nails and fittings](../product/nails.md) (3 per unit), [Iron-shod plow](../product/plow.md) (5 per unit), [Saddle and tack](../product/saddle.md) (0.2 per unit), [Shield](../arms/shield.md) (0.4 per unit), [Steel billet](../metal/steel-ingot.md) (1 per unit), [Wagon](../product/wagon.md) (1 per unit).

## Where the Engine Places It

Settlements carrying each producer tag: `smith` 33, `mine_iron` 13 (of 325 stored settlements).

**Specialty at:** Citadel Felbarr (3), Gracklstugh (3), Melvaunt (3), Memnon (1), Mirabar (3), Nashkel (1).

**Configured shortage at:** Caer Calidyrr, Evereska, Goldenfields, Halarahh, Myth Drannor, Nimbral, Port Nyanzaru.

## Aurora's Whole Realms Catalogue

| Catalogue section | Printed page | Variant | Unit | Catalogue price | Price per lb |
| --- | --- | --- | --- | --- | --- |
| Priests' Alcove (spell components) | 36 | chunk | 5 oz | 5 cp | 0.16 gp |
| Priests' Alcove (spell components) | 36 | coin | 1 | 5 cp |  |
| Priests' Alcove (spell components) | 36 | cube | 1 in | 5 cp |  |
| Priests' Alcove (spell components) | 36 | strip | 5 sq in | 3 cp |  |
| Wizards' Laboratory (components cache) | 48 | chunk | 1 in cu | 5 cp |  |
| Wizards' Laboratory (components cache) | 48 | powder | 6 oz | 2 sp | 0.533 gp |
| Wizards' Laboratory (components cache) | 48 | rod | 1 ft | 3 sp |  |
| Laborers' List (metals) | 60 | bar | 1 lb | 5 cp | 0.05 gp |
| Laborers' List (metals) | 60 | ingot | 10 lb | 4 sp | 0.04 gp |
| Laborers' List (metals) | 60 | sheet | 1 ft sq | 5 cp |  |
| Laborers' List (metals) | 60 | strip | 10 by 1 in | 4 cp |  |
| Laborers' List (metals) | 60 | wire | 1 ft | 5 cp |  |

Engine price per lb is **2.22 times** the median catalogue price per lb for this entry (engine 0.1 gp/lb; catalogue median 0.045 gp/lb). The two are within a factor of five.

## Related Catalogue Goods (Proposed)

Aurora's entries with no engine equivalent whose closest engine commodity is Wrought iron:

[Brass](../metal/brass.md).

## Sources

- Engine record: [`faerun/data/store/commodities.json`](../../../faerun/data/store/commodities.json), with storage and recipe values as applied at load time by [`faerun/data/commodities.py`](../../../faerun/data/commodities.py). Read 2026-10-04.
- Settlement placements: [`faerun/data/store/settlements.json`](../../../faerun/data/store/settlements.json), read 2026-10-04.
- *Aurora's Whole Realms Catalogue* (TSR 9358, 1992, AD&D 2nd edition), J. Robert King and Co., design concept Anne Brown. Primary source, consulted directly from the project copy in [`.guides/`](../../../.guides/tsr09358%20-%20Aurora's_Whole_Realms_Catalogue.pdf) on 2026-10-04. Page numbers are the printed folios. Prices are the catalogue's retail mail-order prices; descriptions here are paraphrased.
