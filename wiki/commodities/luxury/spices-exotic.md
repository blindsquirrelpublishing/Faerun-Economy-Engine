# Exotic spices

[Commodity index](../README.md) · [Luxury goods](README.md)

**Status:** In the engine  
**Engine ID:** `spices_exotic`  
**Category:** luxury  
**Trade unit:** pound (1 lb)  
**Base price:** 15 gp per pound (about 15 gp per lb)  
**Production type:** raw  
**Aurora's Whole Realms Catalogue:** no matching entry in the sections reviewed

## Engine Description

> Saffron, cloves and cinnamon out of Chult, Durpar and the Shining South.

This is a model input stored in the catalogue, not a sourced lore claim.

## Engine Inputs

| Field | Value |
| --- | --- |
| Produced by (industry tags) | `spice` |
| Demand index | 0.12 |
| Luxury (wealth elasticity) | 0.9 |
| Perishable | 0 |
| Demand traits | `noble` 3, `cosmopolitan` 2, `mercantile` 1.5 |
| Storage | 365 days capacity, 0.08% stock loss a day, 45 reserve days |
| Harvest or production calendar | Mirtul 5%, Kythorn 10%, Flamerule 20%, Eleasis 30%, Eleint 20%, Marpenoth 10%, Uktar 5% |
| Regional calendar (cold) | Flamerule 10%, Eleasis 30%, Eleint 40%, Marpenoth 20% |
| Regional calendar (arid) | Hammer 5%, Alturiak 10%, Ches 20%, Tarsakh 20%, Mirtul 5%, Eleint 5%, Marpenoth 10%, Uktar 20%, Nightal 5% |
| Regional calendar (tropical) | Hammer 5%, Alturiak 11%, Ches 16%, Tarsakh 11%, Mirtul 5%, Kythorn 3%, Flamerule 5%, Eleasis 11%, Eleint 16%, Marpenoth 11%, Uktar 5%, Nightal 3% |

## Recipe Links

Used as an input for: [Perfume](../luxury/perfume.md) (0.1 per unit).

## Where the Engine Places It

Settlements carrying each producer tag: `spice` 4 (of 325 stored settlements).

**Specialty at:** Athkatla (1), Calimport (3), Phsant (1), Port Nyanzaru (3), Suldolphor (1), Tashluta (2).

**Configured shortage at:** Caer Calidyrr, Hillsfar, Silverymoon.

## Related Catalogue Goods (Proposed)

Aurora's entries with no engine equivalent whose closest engine commodity is Exotic spices:

[Black walnuts](../luxury/black-walnuts.md), [Butternuts](../luxury/butternuts.md), [Cannella](../luxury/cannella.md), [Cigars](../luxury/cigars.md), [Cocoa](../luxury/cocoa.md), [Coconut](../luxury/coconut.md), [Cubeb](../luxury/cubeb.md), [Dried lotus fruit](../luxury/dried-lotus-fruit.md), [Dried pineapple](../luxury/dried-pineapple.md), [Dried tomato](../luxury/dried-tomato.md), [Fagara](../luxury/fagara.md), [Galingale](../luxury/galingale.md), [Garum](../luxury/garum.md), [Ground artichokes](../luxury/ground-artichokes.md), [Groundnuts](../luxury/groundnuts.md), [Hickory nuts](../luxury/hickory-nuts.md), [Jujubes](../luxury/jujubes.md), [Ketjap](../luxury/ketjap.md), [Litchi fruit](../luxury/litchi-fruit.md), [Long beans](../luxury/long-beans.md), [Manioc flour](../luxury/manioc-flour.md), [Maple sugar](../luxury/maple-sugar.md), [Myrobalans](../luxury/myrobalans.md), [Pecans](../luxury/pecans.md), [Pimento](../luxury/pimento.md), [Potato rootstock](../luxury/potato-rootstock.md), [Pumpkin seeds](../luxury/pumpkin-seeds.md), [Rice candies](../luxury/rice-candies.md), [Sasparilla](../luxury/sasparilla.md), [Scented geranium](../luxury/scented-geranium.md), [Soya sauce](../luxury/soya-sauce.md), [Tamarind pulp](../luxury/tamarind-pulp.md), [Tobacco](../luxury/tobacco.md), [Zedoary](../luxury/zedoary.md).

## Sources

- Engine record: [`faerun/data/store/commodities.json`](../../../faerun/data/store/commodities.json), with storage and recipe values as applied at load time by [`faerun/data/commodities.py`](../../../faerun/data/commodities.py). Read 2026-10-04.
- Settlement placements: [`faerun/data/store/settlements.json`](../../../faerun/data/store/settlements.json), read 2026-10-04.
