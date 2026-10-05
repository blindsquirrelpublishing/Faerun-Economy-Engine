# Incense

[Commodity index](../README.md) · [Luxury goods](README.md)

**Status:** In the engine  
**Engine ID:** `incense`  
**Category:** luxury  
**Trade unit:** block (1 lb)  
**Base price:** 5 gp per block (about 5 gp per lb)  
**Production type:** processed or manufactured  
**Aurora's Whole Realms Catalogue:** listed (see below)

## Engine Description

> Incense is a luxury good in Faerûn, traded in block lots for daily use, craft, and commerce. A refined luxury good sought by elites, merchants, and collectors.

This is a model input stored in the catalogue, not a sourced lore claim.

## Engine Inputs

| Field | Value |
| --- | --- |
| Produced by (industry tags) | `spice`, `temple` |
| Demand index | 0.3 |
| Luxury (wealth elasticity) | 0.6 |
| Perishable | 0 |
| Demand traits | `temple` 3.5, `arcane` 2 |
| Storage | 365 days capacity, 0.01% stock loss a day, 15 reserve days |

## Recipe Links

Inputs for one block: [Common spices](../food/spices-common.md) 0.5, [Charcoal](../material/charcoal.md) 0.01.

## Where the Engine Places It

Settlements carrying each producer tag: `spice` 4, `temple` 16 (of 325 stored settlements).

**Specialty at:** Bezantur (3), Skuld (2), Tantras (2).

## Aurora's Whole Realms Catalogue

### Catalogue entry: Incense stick

| Catalogue section | Printed page | Variant | Unit | Catalogue price | Price per lb |
| --- | --- | --- | --- | --- | --- |
| Wizards' Laboratory (components cache) | 50 | Incense (stick) | 1 lg | 5 sp |  |

Component rows are priced for small laboratory or altar quantities, so they are not compared with the engine's bulk price.

### Catalogue entry: Temple incense

Ritual incense sold in bundles of 12 sticks (or 12 oz loose), each stick burning about half an hour. Most varieties carry game effects in the catalogue; only names and prices are recorded here.

| Catalogue section | Printed page | Variant | Unit | Catalogue price | Price per lb |
| --- | --- | --- | --- | --- | --- |
| Priests' Alcove | 34-36 | air | 12 sticks | 5 gp |  |
| Priests' Alcove | 34-36 | chance | 12 sticks | 9 gp |  |
| Priests' Alcove | 34-36 | charisma | 12 sticks | 10 gp |  |
| Priests' Alcove | 34-36 | constitution | 12 sticks | 10 gp |  |
| Priests' Alcove | 34-36 | dexterity | 12 sticks | 10 gp |  |
| Priests' Alcove | 34-36 | dream | 12 sticks | 12 gp |  |
| Priests' Alcove | 34-36 | earth | 12 sticks | 12 gp |  |
| Priests' Alcove | 34-36 | fire | 12 sticks | 12 gp |  |
| Priests' Alcove | 34-36 | lycanthropy | 12 sticks | 8 gp |  |
| Priests' Alcove | 34-36 | protection | 12 sticks | 15 gp |  |
| Priests' Alcove | 34-36 | psionic | 12 sticks | 10 gp |  |
| Priests' Alcove | 34-36 | rain | 12 sticks | 10 gp |  |
| Priests' Alcove | 34-36 | strength | 12 sticks | 10 gp |  |
| Priests' Alcove | 34-36 | study | 12 sticks | 12 gp |  |
| Priests' Alcove | 34-36 | temple | 12 sticks | 5 gp |  |
| Priests' Alcove | 34-36 | vision | 12 sticks | 10 gp |  |
| Priests' Alcove | 34-36 | divination, general, healing, honors, intelligence, love, purification, water, wisdom | 12 sticks | no price printed |  |

## Related Catalogue Goods (Proposed)

Aurora's entries with no engine equivalent whose closest engine commodity is Incense:

[Aloeswood](../arcane/aloeswood.md), [Ambergris](../arcane/ambergris.md), [Basil](../luxury/basil.md), [Benzoin](../arcane/benzoin.md), [Betony](../arcane/betony.md), [Calamus](../arcane/calamus.md), [Camphor](../arcane/camphor.md), [Citronella](../arcane/citronella.md), [Civet](../arcane/civet.md), [Elemi](../arcane/elemi.md), [Frankincense](../arcane/frankincense.md), [Galbanum](../arcane/galbanum.md), [Jasmine oil](../arcane/jasmine-oil.md), [Lavender buds](../arcane/lavender-buds.md), [Magnolia](../arcane/magnolia.md), [Musk](../arcane/musk.md), [Myrrh](../arcane/myrrh.md), [Onycha](../arcane/onycha.md), [Orchid](../arcane/orchid.md), [Patchouli](../arcane/patchouli.md), [Putchuk](../arcane/putchuk.md), [Rosewater](../arcane/rosewater.md), [Sandalwood oil](../arcane/sandalwood-oil.md), [Storax](../arcane/storax.md).

## Sources

- Engine record: [`faerun/data/store/commodities.json`](../../../faerun/data/store/commodities.json), with storage and recipe values as applied at load time by [`faerun/data/commodities.py`](../../../faerun/data/commodities.py). Read 2026-10-04.
- Settlement placements: [`faerun/data/store/settlements.json`](../../../faerun/data/store/settlements.json), read 2026-10-04.
- *Aurora's Whole Realms Catalogue* (TSR 9358, 1992, AD&D 2nd edition), J. Robert King and Co., design concept Anne Brown. Primary source, consulted directly from the project copy in [`.guides/`](../../../.guides/tsr09358%20-%20Aurora's_Whole_Realms_Catalogue.pdf) on 2026-10-04. Page numbers are the printed folios. Prices are the catalogue's retail mail-order prices; descriptions here are paraphrased.
