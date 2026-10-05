# Glassware

[Commodity index](../README.md) · [Manufactured products](README.md)

**Status:** In the engine  
**Engine ID:** `glassware`  
**Category:** product  
**Trade unit:** crate (20 lb)  
**Base price:** 25 gp per crate (about 1.25 gp per lb)  
**Production type:** processed or manufactured  
**Aurora's Whole Realms Catalogue:** listed (see below)

## Engine Description

> Glassware is a product good in Faerûn, traded in crate lots for daily use, craft, and commerce. A practical manufactured good made for everyday trade and labor.

This is a model input stored in the catalogue, not a sourced lore claim.

## Engine Inputs

| Field | Value |
| --- | --- |
| Produced by (industry tags) | `glass` |
| Demand index | 0.3 |
| Luxury (wealth elasticity) | 0.6 |
| Perishable | 0.05 |
| Demand traits | `noble` 2, `alchemy` 1.8, `arcane` 1.5 |
| Storage | 365 days capacity, 0.01% stock loss a day, 15 reserve days |

## Recipe Links

Inputs for one crate: [Coal](../metal/coal.md) 0.05.

Used as an input for: [Hooded lantern](../product/lantern.md) (0.05 per unit).

<!-- formulation:start -->
## Formulation (Proposed)

Proposed 2026-10-04. Documentation only; nothing here changes the engine.

**Batch basis.** One engine crate is 20 lb of finished glass (bottles, cups, phials) packed in straw. About 32 lb of batch melts to 26 lb of glass, and offcuts and breakage (about 6 lb) go back into the next melt as cullet.

| Line | Input | Quantity per crate | Engine commodity | Cost at base price | Basis |
| --- | --- | --- | --- | --- | --- |
| 1 | Sand | about 20 lb | none | 0.03 gp | Dug and washed; labour only |
| 2 | Plant ash (soda or potash flux) | about 10 lb | none | 0.20 gp (placeholder) | Burnt seaweed, saltwort or bracken; no engine commodity |
| 3 | Lime | about 2 lb | none | 0.02 gp | Burnt shell or limestone |
| 4 | Cullet | about 6 lb, from the last melt | none | 0 | Recycled |
| 5 | Fuel (firewood) | 0.6 load (about 300 lb) | [`timber`](../material/timber.md) | 1.80 gp | About 15 lb of wood a lb of glass, for fritting, melting and annealing |
| 6 | Packing (crate and straw) | 0.02 load of planks | [`planks`](../material/planks.md) | 0.10 gp | No crate commodity yet (proposed at Waterdeep) |

| Line | Conversion cost | Basis | Cost per crate |
| --- | --- | --- | --- |
| 7 | Labour | A master glassblower (0.975 gp, `smiths` wage) and two assistants (0.325 gp, `general`) blow about 4 crates a day | 0.41 gp |
| 8 | Furnace and crucible wear | Clay crucibles replaced every few weeks; furnace relined each year | 0.10 gp |

**Rolled-up cost: about 2.66 gp per crate** (materials 2.15 gp, conversion 0.51 gp), against the 25 gp base price, which leaves 22.3 gp (89%). Glass is priced as a scarce skill, not as its materials.

The engine recipe is 0.05 sack of coal (3 lb) per crate: a fiftieth of the fuel a furnace burns, and no sand, flux or lime. In coal, the fuel above would be about 2.5 sacks (150 lb, 1.25 gp). Quantities, batch sizes, staffing and equipment lives are model assumptions from general pre-industrial practice, not a Realms source.

## Production Route (Proposed)

**Route: Glassware**

| Op | Operation | Duration | Resource | Equipment |
| --- | --- | --- | --- | --- |
| 10 | Wash sand; burn plants for ash | days, ahead of time | Labourer | |
| 20 | Frit: roast sand, ash and lime together | about 1 day | Assistant | [Glass furnace](../../equipment/glassmaking/glass-furnace.md) |
| 30 | Melt frit and cullet | 1 to 2 days | Assistant (stoking) | [Glass furnace](../../equipment/glassmaking/glass-furnace.md), [Crucible](../../equipment/glassmaking/crucible.md) |
| 40 | Gather, blow and shape | daily | Master glassblower | [Glassblower's tools](../../equipment/glassmaking/glassblowers-tools.md) |
| 50 | Anneal (cool slowly) | about 1 day | Assistant | [Annealing oven](../../equipment/glassmaking/annealing-oven.md) |
| 60 | Inspect; break rejects for cullet; pack in straw | hours | Labourer | Crate, straw |

The furnace burns day and night once lit; letting it go cold cracks the crucibles.

## Required Equipment

From the [equipment wiki](../../equipment/README.md). None of it is in the engine.

| Equipment | Estimated cost | Ops |
| --- | --- | --- |
| [Glass furnace](../../equipment/glassmaking/glass-furnace.md) | 11 gp | 20, 30 |
| [Crucible](../../equipment/glassmaking/crucible.md) | 0.7 gp each, about 4 in use | 30 |
| [Glassblower's tools](../../equipment/glassmaking/glassblowers-tools.md) | 6 gp a set | 40 |
| [Annealing oven](../../equipment/glassmaking/annealing-oven.md) | 3 gp | 50 |

## Cost Roll-up Cross-check

Observed output, 3 Marpenoth 1492 DR, live server, standard quality. Fuel at the local asking price, 0.6 load of timber or 2.5 sacks of coal, whichever is cheaper.

| Producer | Glassware producer gate | Timber asking price | Coal asking price | Fuel per crate (cheaper) | Rolled-up cost at local fuel |
| --- | --- | --- | --- | --- | --- |
| Neverwinter | 20.29 gp | 2.80 gp (common) | 12.83 gp (rare) | 1.68 gp (timber) | 2.54 gp |
| Calimport | 19.95 gp | 11.44 gp (rare) | 15.70 gp (rare) | 6.86 gp (timber) | 7.72 gp |
| Waterdeep | 24.22 gp | 24.13 gp (rare) | 11.58 gp (rare) | 14.48 gp (timber) | 15.34 gp |
| Athkatla | 19.24 gp | 48.82 gp (rare) | 11.47 gp (rare) | 28.66 gp (coal) | 29.52 gp |
| Almraiven | 14.23 gp | 59.09 gp (rare) | 16.22 gp (rare) | 40.54 gp (coal) | 41.40 gp |
| Halarahh | 19.12 gp | 63.31 gp (rare) | 16.53 gp (rare) | 41.32 gp (coal) | 42.18 gp |
| Base prices | 25 gp | 3 gp | 0.5 gp | 1.25 gp (coal) | 2.11 gp |

- **The roll-up covers the price easily at base prices**: glass costs about a ninth of what it sells for.
- **Five of the six glassworks have no local fuel.** Only Neverwinter has firewood in common supply. The other five import timber or coal at 11 to 63 gp a load or sack, and at a real furnace's fuel use Athkatla, Almraiven and Halarahh would spend 1.5 to 2.8 times their gate price on fuel alone. The engine recipe's 3 lb of coal hides this (C13).
- Waterdeep, Calimport and Halarahh are also configured short of timber.
- *Aurora's* sells glass beads at 2 cp an ounce (0.32 gp a lb) as a spell component, a quarter of the engine's 1.25 gp a lb; component prices are not compared with bulk on this wiki, so this is a pointer only.

<!-- formulation:end -->

## Where the Engine Places It

Settlements carrying each producer tag: `glass` 6 (of 325 stored settlements).

**Specialty at:** Almraiven (2), Athkatla (2), [Neverwinter](../../../locations/neverwinter.md) (2).

## Aurora's Whole Realms Catalogue

| Catalogue section | Printed page | Variant | Unit | Catalogue price | Price per lb |
| --- | --- | --- | --- | --- | --- |
| Priests' Alcove (spell components) | 37 | beads | 1 oz | 2 cp | 0.32 gp |
| Priests' Alcove (spell components) | 37 | marbles | 1/2 in | 2 cp |  |
| Wizards' Laboratory (components cache) | 48 | bead | 10 | 1 gp |  |
| Wizards' Laboratory (components cache) | 48 | cone | 10 | 5 gp |  |
| Wizards' Laboratory (components cache) | 48 | rod | 1 ft | 5 gp |  |
| Wizards' Laboratory (components cache) | 48 | sheet | 1 ft sq | 2 gp |  |
| Wizards' Laboratory (components cache) | 48 | sphere | 6 in | 5 gp |  |

Component rows are priced for small laboratory or altar quantities, so they are not compared with the engine's bulk price.

## Sources

- Engine record: [`faerun/data/store/commodities.json`](../../../faerun/data/store/commodities.json), with storage and recipe values as applied at load time by [`faerun/data/commodities.py`](../../../faerun/data/commodities.py). Read 2026-10-04.
- Settlement placements: [`faerun/data/store/settlements.json`](../../../faerun/data/store/settlements.json), read 2026-10-04.
- *Aurora's Whole Realms Catalogue* (TSR 9358, 1992, AD&D 2nd edition), J. Robert King and Co., design concept Anne Brown. Primary source, consulted directly from the project copy in [`.guides/`](../../../.guides/tsr09358%20-%20Aurora's_Whole_Realms_Catalogue.pdf) on 2026-10-04. Page numbers are the printed folios. Prices are the catalogue's retail mail-order prices; descriptions here are paraphrased.
