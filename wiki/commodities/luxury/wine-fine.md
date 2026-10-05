# Fine vintage wine

[Commodity index](../README.md) · [Luxury goods](README.md)

**Status:** In the engine  
**Engine ID:** `wine_fine`  
**Category:** luxury  
**Trade unit:** bottle (3 lb)  
**Base price:** 12 gp per bottle (about 4 gp per lb)  
**Production type:** processed or manufactured  
**Aurora's Whole Realms Catalogue:** no matching entry in the sections reviewed

## Engine Description

> Saerloonian Glowfire, Berduskan Dark, Evermeet vintages.

This is a model input stored in the catalogue, not a sourced lore claim.

## Engine Inputs

| Field | Value |
| --- | --- |
| Produced by (industry tags) | `vint` |
| Demand index | 0.15 |
| Luxury (wealth elasticity) | 0.95 |
| Perishable | 0 |
| Demand traits | `noble` 3.5, `elven` 2, `cosmopolitan` 1.8 |
| Storage | 730 days capacity, 0.01% stock loss a day, 30 reserve days |

## Recipe Links

Inputs for one bottle: [Table wine](../drink/wine-common.md) 0.03.

## Where the Engine Places It

Settlements carrying each producer tag: `vint` 13 (of 325 stored settlements).

**Specialty at:** Berdusk (3), Evereska (2), Nimbral (2), Saerloon (3), Tashluta (2), Velprintalar (1).

**Configured shortage at:** Luskan.

## Related Catalogue Goods (Proposed)

Aurora's entries with no engine equivalent whose closest engine commodity is Fine vintage wine:

[Arabellan dry](../luxury/arabellan-dry.md), [Berduskan dark](../luxury/berduskan-dark.md), [Blood wine](../luxury/blood-wine.md), [Clarry](../luxury/clarry.md), [Evermead](../luxury/evermead.md), [Saerloonian glowfire](../luxury/saerloonian-glowfire.md), [Saerloonian Special Vat](../luxury/saerloonian-special-vat.md), [Saerloonian topaz](../luxury/saerloonian-topaz.md), [Spiced wine](../luxury/spiced-wine.md), [Undermountain alurlyath](../luxury/undermountain-alurlyath.md), [Westgate ruby](../luxury/westgate-ruby.md), [Winter wine](../luxury/winter-wine.md).

## Sources

- Engine record: [`faerun/data/store/commodities.json`](../../../faerun/data/store/commodities.json), with storage and recipe values as applied at load time by [`faerun/data/commodities.py`](../../../faerun/data/commodities.py). Read 2026-10-04.
- Settlement placements: [`faerun/data/store/settlements.json`](../../../faerun/data/store/settlements.json), read 2026-10-04.
