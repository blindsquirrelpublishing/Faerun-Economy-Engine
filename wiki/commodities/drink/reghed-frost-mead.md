# Reghed frost mead

[Commodity index](../README.md) · [Drink](README.md)

**Status:** In the engine  
**Engine ID:** `reghed_frost_mead`  
**Category:** drink  
**Trade unit:** keg (80 lb)  
**Base price:** 6.5 gp per keg (about 0.081 gp per lb)  
**Production type:** raw  
**Aurora's Whole Realms Catalogue:** no matching entry in the sections reviewed

## Engine Description

> A tundra-herb mead brewed by the Reghed barbarians.

This is a model input stored in the catalogue, not a sourced lore claim.

## Engine Inputs

| Field | Value |
| --- | --- |
| Produced by (industry tags) | `tag_reghed_frost_mead` |
| Demand index | 1 |
| Luxury (wealth elasticity) | 0.15 |
| Perishable | 0.15 |
| Storage | 365 days capacity, 0.01% stock loss a day, 15 reserve days |

<!-- formulation:start -->
## Formulation (Proposed)

Proposed 2026-10-04. Documentation only; nothing here changes the engine.

**Batch basis.** One engine keg is 80 lb, read as about **9.6 gallons** of contents at 8.34 lb a gallon, with the keg returned and refilled (the same assumption as [Ale](ale.md)).

| Line | Input | Quantity per keg | Engine commodity | Cost at base price | Basis |
| --- | --- | --- | --- | --- | --- |
| 1 | Honey | 2.88 crock (29 lb) | [`honey`](../food/honey.md) | 4.32 gp | 3 lb a gallon |
| 2 | Water | about 9 gallons | none | 0.00 gp | Honey supplies the rest of the volume |
| 3 | Fuel (firewood) | 0.019 load (about 10 lb) | [`timber`](../material/timber.md) | 0.06 gp | Warming the must to dissolve and skim the honey |
| 4 | Tundra herbs | about 1 lb, gathered | none | 0.03 gp | Gathering time only; which herbs is unrecorded |

| Line | Conversion cost | Basis | Cost per keg |
| --- | --- | --- | --- |
| 5 | Labour | A brewer and a labourer mix about 10 kegs a day; the rest is waiting | 0.10 gp |
| 6 | Equipment and cask wear | Vats, aging tuns held for months, and kegs | 0.06 gp |

**Rolled-up cost: about 4.57 gp per keg** (materials 4.41 gp, conversion 0.16 gp). Against the 6.5 gp base price that leaves about 1.9 gp (30%).

The engine gives this mead no recipe at all: it is produced from a dedicated industry tag with no inputs. Honey is the open question. Bryn Shander is tundra; any honey there is almost certainly imported, which would push the real cost well above the base-price roll-up. Firewood is equally scarce in Icewind Dale. Quantities, batch sizes, staffing and equipment lives are model assumptions from general pre-industrial practice, not a Realms source.

## Production Route (Proposed)

Same route as [Mead](mead.md) with an herb steep.

**Route: Frost mead**

| Op | Operation | Duration | Resource | Equipment |
| --- | --- | --- | --- | --- |
| 10 | Warm water; dissolve the honey; skim | 2 hours | Brewer | [Brewing copper](../../equipment/brewing/brewing-copper.md) |
| 20 | Steep the tundra herbs in the warm must | hours | Brewer | [Brewing copper](../../equipment/brewing/brewing-copper.md) |
| 30 | Ferment | 2 to 4 weeks | Brewer | [Fermenting vat](../../equipment/brewing/fermenting-vat.md) |
| 40 | Age | 2 to 6 months | none | [Aging tun](../../equipment/vinting/aging-tun.md) |
| 50 | Rack into kegs | hours | Labourer | [Keg](../../equipment/brewing/keg.md) |

## Required Equipment

From the [equipment wiki](../../equipment/README.md). None of it is in the engine.

| Equipment | Estimated cost | Ops |
| --- | --- | --- |
| [Brewing copper](../../equipment/brewing/brewing-copper.md) | 60 gp | 10, 20 |
| [Fermenting vat](../../equipment/brewing/fermenting-vat.md) | 8 gp | 30 |
| [Aging tun](../../equipment/vinting/aging-tun.md) | 8 gp | 40 |
| [Keg](../../equipment/brewing/keg.md) | 1 gp | 50 |
| [Brewer's hand tools](../../equipment/brewing/brewers-hand-tools.md) | 2 gp | 10, 50 |

## Cost Roll-up Cross-check

- **No engine recipe to check.** The industry tag `tag_reghed_frost_mead` makes it from nothing, so its price never sees the cost of honey.
- **Output is a flat 6,972.86 kegs a day at Bryn Shander**, against local demand of 2.4. Every single-tag drink in the engine (duergar grey ale, kelp ale, fire-wine, starflower wine) shows the same 6,972.86 a day whatever the place or population (C10, see W4).
- At base prices the proposed formulation fits inside the price. With imported honey at the Citadel Adbar asking price (2.74 gp a crock), honey alone would be 7.88 gp a keg, above the 6.5 gp price.
<!-- formulation:end -->

## Where the Engine Places It

Settlements carrying each producer tag: `tag_reghed_frost_mead` 1 (of 325 stored settlements).

**Dedicated `tag_reghed_frost_mead` industry at:** Bryn Shander (2).

## Sources

- Engine record: [`faerun/data/store/commodities.json`](../../../faerun/data/store/commodities.json), with storage and recipe values as applied at load time by [`faerun/data/commodities.py`](../../../faerun/data/commodities.py). Read 2026-10-04.
- Settlement placements: [`faerun/data/store/settlements.json`](../../../faerun/data/store/settlements.json), read 2026-10-04.
