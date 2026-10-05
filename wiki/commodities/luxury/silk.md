# Silk

[Commodity index](../README.md) · [Luxury goods](README.md)

**Status:** In the engine  
**Engine ID:** `silk`  
**Category:** luxury  
**Trade unit:** bolt (8 lb)  
**Base price:** 60 gp per bolt (about 7.5 gp per lb)  
**Production type:** raw  
**Aurora's Whole Realms Catalogue:** listed (see below)

## Engine Description

> Silk is a luxury good in Faerûn, traded in bolt lots for daily use, craft, and commerce. A woven textile valued for clothing, furnishing, and caravan gear.

This is a model input stored in the catalogue, not a sourced lore claim.

## Engine Inputs

| Field | Value |
| --- | --- |
| Produced by (industry tags) | `silk` |
| Demand index | 0.1 |
| Luxury (wealth elasticity) | 0.95 |
| Perishable | 0 |
| Demand traits | `noble` 3.5, `cosmopolitan` 2, `magocracy` 1.6 |
| Storage | 365 days capacity, 0.01% stock loss a day, 15 reserve days |

## Recipe Links

Used as an input for: [Fine clothing](../luxury/clothing-fine.md) (0.1 per unit).

## Where the Engine Places It

Settlements carrying each producer tag: `silk` 4 (of 325 stored settlements).

**Specialty at:** Calimport (2), Selgaunt (1), Telflamm (1).

**Configured shortage at:** Caer Calidyrr, Goldenfields, Hillsfar, [Phandalin](../../../locations/phandalin.md).

## Aurora's Whole Realms Catalogue

| Catalogue section | Printed page | Variant | Unit | Catalogue price | Price per lb |
| --- | --- | --- | --- | --- | --- |
| Tailors' Corner | 75 |  | sq yd | 7 gp |  |

## Sources

- Engine record: [`faerun/data/store/commodities.json`](../../../faerun/data/store/commodities.json), with storage and recipe values as applied at load time by [`faerun/data/commodities.py`](../../../faerun/data/commodities.py). Read 2026-10-04.
- Settlement placements: [`faerun/data/store/settlements.json`](../../../faerun/data/store/settlements.json), read 2026-10-04.
- *Aurora's Whole Realms Catalogue* (TSR 9358, 1992, AD&D 2nd edition), J. Robert King and Co., design concept Anne Brown. Primary source, consulted directly from the project copy in [`.guides/`](../../../.guides/tsr09358%20-%20Aurora's_Whole_Realms_Catalogue.pdf) on 2026-10-04. Page numbers are the printed folios. Prices are the catalogue's retail mail-order prices; descriptions here are paraphrased.
