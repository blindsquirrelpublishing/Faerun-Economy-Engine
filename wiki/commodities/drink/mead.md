# Mead

[Commodity index](../README.md) · [Drink](README.md)

**Status:** In the engine  
**Engine ID:** `mead`  
**Category:** drink  
**Trade unit:** keg (80 lb)  
**Base price:** 2.5 gp per keg (about 0.031 gp per lb)  
**Production type:** processed or manufactured  
**Aurora's Whole Realms Catalogue:** listed (see below)

## Engine Description

> Mead is a drink good in Faerûn, traded in keg lots for daily use, craft, and commerce. A prepared beverage prized for hospitality, ceremony, and everyday refreshment.

This is a model input stored in the catalogue, not a sourced lore claim.

## Engine Inputs

| Field | Value |
| --- | --- |
| Produced by (industry tags) | `brew`, `farm` |
| Demand index | 0.6 |
| Luxury (wealth elasticity) | 0.2 |
| Perishable | 0.15 |
| Demand traits | `cold` 1.5, `elven` 1.2 |
| Storage | 365 days capacity, 0.05% stock loss a day, 30 reserve days |

## Recipe Links

Inputs for one keg: [Honey](../food/honey.md) 0.6.

<!-- formulation:start -->
## Formulation (Proposed)

Proposed 2026-10-04. Documentation only; nothing here changes the engine.

**Batch basis.** One engine keg is 80 lb, read as about **9.6 gallons** of contents at 8.34 lb a gallon, with the keg returned and refilled (the same assumption as [Ale](ale.md)).

| Line | Input | Quantity per keg | Engine commodity | Cost at base price | Basis |
| --- | --- | --- | --- | --- | --- |
| 1 | Honey | 2.88 crock (29 lb) | [`honey`](../food/honey.md) | 4.32 gp | 3 lb a gallon |
| 2 | Water | about 9 gallons | none | 0.00 gp | Honey supplies the rest of the volume |
| 3 | Fuel (firewood) | 0.019 load (about 10 lb) | [`timber`](../material/timber.md) | 0.06 gp | Warming the must to dissolve and skim the honey |

| Line | Conversion cost | Basis | Cost per keg |
| --- | --- | --- | --- |
| 4 | Labour | A brewer and a labourer mix about 10 kegs a day; the rest is waiting | 0.10 gp |
| 5 | Equipment and cask wear | Vats, aging tuns held for months, and kegs | 0.06 gp |

**Rolled-up cost: about 4.54 gp per keg** (materials 4.38 gp, conversion 0.16 gp). The engine base price is 2.5 gp, so at a normal strength mead **costs more to make than it sells for**.

Strength is the problem. Mead is usually made with about 3 lb of honey a gallon. The engine recipe uses 0.6 crock (6 lb) for the whole keg, about 0.6 lb a gallon, a fifth of that: a small mead nearer ale strength. At the engine recipe the roll-up is about 1.12 gp (honey 0.90 gp plus the same conversion), well inside 2.5 gp. Quantities, batch sizes, staffing and equipment lives are model assumptions from general pre-industrial practice, not a Realms source.

## Production Route (Proposed)

Lead time is three to seven months, most of it waiting. The vats and tuns tied up for that long are why mead is "slow and fussy", as the catalogue puts it.

**Route: Mead**

| Op | Operation | Duration | Resource | Equipment |
| --- | --- | --- | --- | --- |
| 10 | Warm water in the copper; dissolve the honey; skim | 2 hours | Brewer | [Brewing copper](../../equipment/brewing/brewing-copper.md) |
| 20 | Cool and run into the vat | hours | Labourer | [Fermenting vat](../../equipment/brewing/fermenting-vat.md) |
| 30 | Ferment | 2 to 4 weeks | Brewer | [Fermenting vat](../../equipment/brewing/fermenting-vat.md) |
| 40 | Rack off the lees into aging tuns; age | 2 to 6 months | none | [Aging tun](../../equipment/vinting/aging-tun.md) |
| 50 | Rack into kegs | hours | Labourer | [Keg](../../equipment/brewing/keg.md) |

## Required Equipment

From the [equipment wiki](../../equipment/README.md). None of it is in the engine.

| Equipment | Estimated cost | Ops |
| --- | --- | --- |
| [Brewing copper](../../equipment/brewing/brewing-copper.md) | 60 gp | 10 |
| [Fermenting vat](../../equipment/brewing/fermenting-vat.md) | 8 gp | 20, 30 |
| [Aging tun](../../equipment/vinting/aging-tun.md) | 8 gp | 40 |
| [Keg](../../equipment/brewing/keg.md) | 1 gp | 50 |
| [Brewer's hand tools](../../equipment/brewing/brewers-hand-tools.md) | 2 gp | 10, 50 |

## Cost Roll-up Cross-check

Observed output, 3 Marpenoth 1492 DR, live server, standard quality; inputs at the asking price in the same market, the drink at its producer gate price before merchant markup.

| Market | Honey asking price | Honey at engine recipe (0.6 crock) | Honey at 3 lb a gallon (2.88 crocks) | Mead producer gate | Mead retail |
| --- | --- | --- | --- | --- | --- |
| Goldenfields | 1.020 gp | 0.612 gp | 2.94 gp | 1.346 gp | 1.646 gp |
| Beregost | 1.276 gp | 0.766 gp | 3.67 gp | 1.239 gp | 1.606 gp |
| Caer Calidyrr | 1.314 gp | 0.788 gp | 3.78 gp | 1.406 gp | 1.548 gp |
| Purskul | 1.379 gp | 0.827 gp | 3.97 gp | 1.591 gp | 1.935 gp |
| Caer Corwell | 1.386 gp | 0.832 gp | 3.99 gp | 1.158 gp | 1.437 gp |
| Suzail | 1.690 gp | 1.014 gp | 4.87 gp | 2.012 gp | 2.355 gp |
| Lyrabar | 2.232 gp | 1.339 gp | 6.43 gp | 1.936 gp | 2.358 gp |
| Citadel Adbar | 2.737 gp | 1.642 gp | 7.88 gp | 1.891 gp | 2.422 gp |
| Base prices | 1.5 gp | 0.90 gp | 4.32 gp | 2.5 gp | |

- **The engine recipe covers its honey everywhere**, with 0.25 to 0.73 gp left at the gate; Citadel Adbar is tightest because it imports 93% of its honey.
- **At a normal strength no market breaks even**: honey alone runs 2.9 to 7.9 gp a keg against gate prices of 1.16 to 2.01 gp.
- **The catalogue agrees mead is dear.** *Aurora's* Neverwinter mead is 6 gp a 12-gallon cask, 0.50 gp a gallon, about 4.8 gp for an engine keg, nearly twice the engine's 0.26 gp a gallon and close to the full-strength roll-up of 4.54 gp.
- Either the recipe stays at 0.6 crock and the page calls it small mead, or honey goes to about 2.9 crocks and the base price to about 5 to 6 gp (C7).
<!-- formulation:end -->

## Where the Engine Places It

Settlements carrying each producer tag: `brew` 18, `farm` 50 (of 325 stored settlements).

**Specialty at:** Caer Corwell (1), Good Mead (3).

## Aurora's Whole Realms Catalogue

Delicate honey wine; scarce because mead is slow and fussy to make. The honey comes from Neverwinter's garden bees.

**Origin given:** Neverwinter.

| Catalogue section | Printed page | Variant | Unit | Catalogue price | Price per lb |
| --- | --- | --- | --- | --- | --- |
| Wines and Ales | 130 |  | hand keg (2 gal) | 25 sp | 0.151 gp |
| Wines and Ales | 130 |  | cask (12 gal) | 6 gp | 0.06 gp |
| Wines and Ales | 130 |  | barrel (30 gal) | 20 gp | 0.08 gp |
| Wines and Ales | 130 |  | butt (100 gal) | 48 gp | 0.058 gp |

Engine price per lb is **0.445 times** the median catalogue price per lb for this entry (engine 0.031 gp/lb; catalogue median 0.07 gp/lb). The two are within a factor of five.

## Sources

- Engine record: [`faerun/data/store/commodities.json`](../../../faerun/data/store/commodities.json), with storage and recipe values as applied at load time by [`faerun/data/commodities.py`](../../../faerun/data/commodities.py). Read 2026-10-04.
- Settlement placements: [`faerun/data/store/settlements.json`](../../../faerun/data/store/settlements.json), read 2026-10-04.
- *Aurora's Whole Realms Catalogue* (TSR 9358, 1992, AD&D 2nd edition), J. Robert King and Co., design concept Anne Brown. Primary source, consulted directly from the project copy in [`.guides/`](../../../.guides/tsr09358%20-%20Aurora's_Whole_Realms_Catalogue.pdf) on 2026-10-04. Page numbers are the printed folios. Prices are the catalogue's retail mail-order prices; descriptions here are paraphrased.
