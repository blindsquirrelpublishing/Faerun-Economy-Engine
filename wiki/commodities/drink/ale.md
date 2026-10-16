# Ale

[Commodity index](../README.md) · [Drink](README.md)

**Status:** In the engine  
**Engine ID:** `ale`  
**Category:** drink  
**Trade unit:** keg (80 lb)  
**Base price:** 1.6 gp per keg (about 0.02 gp per lb)  
**Production type:** processed or manufactured  
**Aurora's Whole Realms Catalogue:** no matching entry in the sections reviewed

## Engine Description

> Ale is a drink good in Faerûn, traded in keg lots for daily use, craft, and commerce. A prepared beverage prized for hospitality, ceremony, and everyday refreshment.

This is a model input stored in the catalogue, not a sourced lore claim.

## Engine Inputs

| Field | Value |
| --- | --- |
| Produced by (industry tags) | `brew`, `farm` |
| Demand index | 2.4 |
| Luxury (wealth elasticity) | 0 |
| Perishable | 0.3 |
| Demand traits | `dwarven` 1.8, `military` 1.4, `frontier` 1.3 |
| Legacy season multipliers | `summer` 1.2 |
| Storage | 60 days capacity, 0.6% stock loss a day, 7 reserve days |
| Demand calendar | Hammer 8%, Alturiak 8%, Ches 8%, Tarsakh 8%, Mirtul 8%, Kythorn 9%, Flamerule 9%, Eleasis 9%, Eleint 8%, Marpenoth 8%, Uktar 8%, Nightal 8% |

## Recipe Links

Inputs for one keg: [Barley](../food/barley.md) 0.8 bushel. The proposed formulation below predates the barley substitution; other fuel/malt proposals remain open.

## Formulation (Proposed)

Proposed 2026-10-04. Documentation only: the engine still uses the single recipe line above until a separate,
validated data change says otherwise.

**Batch basis.** One engine keg is 80 lb. Read as contents only, at 8.34 lb a gallon (the figure the Waterdeep
Trading Company buttload guide uses), that is about **9.6 gallons of ale**, with the cask returned and refilled
rather than sold with it. The catalogue does not say whether the 80 lb includes the cask; this page assumes it
does not.

| Line | Input | Quantity per keg | Engine commodity | Cost at base price | Basis |
| --- | --- | --- | --- | --- | --- |
| 1 | Grain, malted | 0.8 bushel (48 lb raw, about 38 lb after malting) | [`grain`](../food/grain.md) (wheat) | 0.48 gp | Engine recipe. About 4 lb of malt a gallon for an ordinary-strength ale, so 38 lb gives roughly 9.5 gallons, which agrees with the keg |
| 2 | Water | about 15 gallons | none | 0 | Covers about 9.6 gal of ale, roughly 4 gal soaked up by spent grain and 1.5 gal lost to the boil |
| 3 | Fuel (firewood) | 0.06 load (about 30 lb) | [`timber`](../material/timber.md) | 0.18 gp | Kiln-drying the malt plus heating the mash and boil. Charcoal at 0.375 sack (0.375 gp) is the dearer alternative |
| 4 | Bittering and flavouring herbs | about 0.5 lb | none (see C6) | 0.02 gp (placeholder) | Gruit herbs or hops; neither is an engine commodity |
| 5 | Yeast (barm) | skimmed from the previous batch | none | 0 | Repitched, not bought |
| 6 | Cask | 1 keg, returnable | none (see [Keg](../../equipment/brewing/keg.md)) | in line 8 | Not consumed; carried as equipment |

| Line | Conversion cost | Basis | Cost per keg |
| --- | --- | --- | --- |
| 7 | Labour | Two brewers (0.65 gp a day each, engine `brewers` wage) and one labourer (0.325 gp, `general`) brew one batch of 6 kegs a day: 1.625 gp / 6. Turning the malting floor adds about 0.02 gp (`farms` wage) | 0.29 gp |
| 8 | Equipment and cask wear | About 300 gp of brewhouse and cask float written off over its life, spread across about 1,800 kegs a year; see [Required Equipment](#required-equipment) | 0.03 gp |

**Rolled-up cost: about 1.00 gp a keg at base prices**, against the 1.6 gp base price: materials 0.68 gp,
conversion 0.32 gp, and 0.60 gp (37.5% of the price) left for margin, guild dues and rent.

The 6-kegs-a-day batch, staffing, fuel weight, herb quantity and cask life are model assumptions taken from
general pre-industrial brewing practice, not from a Realms source. They are here to be argued with.

## Production Route (Proposed)

Two routes. Malting can run at the brewery or at a separate maltster, which is why it is split out; if a
`malt` intermediate is ever added (C6), route A produces it and route B consumes it.

**Route A: Malting** (per batch of grain)

| Op | Operation | Duration | Resource | Equipment |
| --- | --- | --- | --- | --- |
| 10 | Steep the grain in water, changing the water once or twice | 2 days | Maltster | [Steeping cistern](../../equipment/brewing/steeping-cistern.md) |
| 20 | Germinate on the floor, turning it several times a day | 4 to 5 days | Maltster | Malting floor, [brewer's hand tools](../../equipment/brewing/brewers-hand-tools.md) (malt shovels, rakes) |
| 30 | Kiln-dry to stop growth | 1 day | Maltster | [Malt kiln](../../equipment/brewing/malt-kiln.md), firewood |
| 40 | Crush (grind coarsely) | hours | Miller or brewer | [Malt mill](../../equipment/brewing/malt-mill.md), or a grain mill for a toll |

**Route B: Brewing** (per batch of 6 kegs)

| Op | Operation | Duration | Resource | Equipment |
| --- | --- | --- | --- | --- |
| 50 | Heat water; mash the crushed malt in hot water | 2 to 3 hours | Brewer | [Brewing copper](../../equipment/brewing/brewing-copper.md), [mash tun](../../equipment/brewing/mash-tun.md), mash oar |
| 60 | Run off the wort; sparge the grain with more hot water | 1 hour | Brewer | Mash tun, buckets |
| 70 | Boil the wort with herbs or hops | 1 to 2 hours | Brewer | Brewing copper, firewood |
| 80 | Cool | 3 to 6 hours | Labourer | [Coolship](../../equipment/brewing/coolship.md) |
| 90 | Pitch barm and ferment; skim fresh barm for the next batch | 3 to 5 days | Brewer | [Fermenting vat](../../equipment/brewing/fermenting-vat.md) |
| 100 | Rack into kegs and bung | hours | Labourer | [Keg](../../equipment/brewing/keg.md), funnel, bungs |
| 110 | Condition in the cellar | about 7 days | none | Cellar, kegs |

Lead time from raw grain to saleable keg is about three weeks (8 days malting, 1 day brewing, 4 days fermenting,
7 days conditioning). Brewing daily with a 4-day ferment needs five vats in rotation. Engine storage of 60 days
leaves a little over a month of shelf life once conditioned.

## Required Equipment

Listed in the [equipment wiki](../../equipment/README.md) under [brewing](../../equipment/brewing/README.md).
None of it exists in the engine. Estimates are for a brewhouse making 6 kegs a day.

| Equipment | Count | Estimated cost | Life | Ops |
| --- | --- | --- | --- | --- |
| [Steeping cistern](../../equipment/brewing/steeping-cistern.md) | 1 | 3.5 gp | 10 years | 10 |
| [Malt kiln](../../equipment/brewing/malt-kiln.md) | 1 | priced with the building | building | 30 |
| [Malt mill](../../equipment/brewing/malt-mill.md) | 1, or toll milling | 6 gp (hand quern) | 10 years | 40 |
| [Brewing copper](../../equipment/brewing/brewing-copper.md) | 1 | 60 gp | 20 years | 50, 70 |
| [Mash tun](../../equipment/brewing/mash-tun.md) | 1 | 9.4 gp | 10 years | 50, 60 |
| [Coolship](../../equipment/brewing/coolship.md) | 1 | 4 gp | 10 years | 80 |
| [Fermenting vat](../../equipment/brewing/fermenting-vat.md) | 5 | 8 gp each, 40 gp | 10 years | 90 |
| [Keg](../../equipment/brewing/keg.md) | about 180 (30 days of output in circulation) | 1 gp each, 180 gp | 5 years | 100, 110 |
| [Brewer's hand tools](../../equipment/brewing/brewers-hand-tools.md) | 1 set | 2 gp | 3 years | 20, 50, 60, 100 |

Kegs are the largest item: a month of output sitting in taverns and cellars costs three times the copper.

## Cost Roll-up Cross-check

Does the engine's ale price cover its own recipe? Observed output, 3 Marpenoth 1492 DR, live server, standard
quality. Grain per keg is 0.8 times the grain asking price in the same market, which is what a local brewer would
pay; ale is the producer gate price, before merchant markup.

| Market | Grain asking price | Grain per keg | Ale producer gate | Grain share | Left for everything else | Ale retail |
| --- | --- | --- | --- | --- | --- | --- |
| Beregost | 0.378 gp | 0.302 gp | 1.000 gp | 30% | 0.698 gp | 1.313 gp |
| Goldenfields | 0.405 gp | 0.324 gp | 1.064 gp | 30% | 0.740 gp | 1.380 gp |
| [Amphail](../../locations/amphail/README.md) | 0.546 gp | 0.437 gp | 1.600 gp | 27% | 1.163 gp | 2.612 gp |
| Purskul | 0.643 gp | 0.514 gp | 1.067 gp | 48% | 0.553 gp | 1.261 gp |
| Lyrabar | 0.668 gp | 0.534 gp | 1.262 gp | 42% | 0.728 gp | 1.411 gp |
| Baldur's Gate | 1.811 gp | 1.449 gp | 1.515 gp | 96% | 0.066 gp | 1.750 gp |
| Ravens Bluff | 3.839 gp | 3.071 gp | 1.194 gp | 257% | **minus 1.877 gp** | 1.431 gp |
| [Waterdeep](../../locations/waterdeep/README.md) | 7.072 gp | 5.658 gp | 6.552 gp | 86% | 0.894 gp | 7.458 gp |
| Base prices | 0.6 gp | 0.48 gp | 1.6 gp | 30% | 1.12 gp | |

What the table shows:

- **At base prices the roll-up works.** Grain is 30% of the price and the full formulation above costs about
  1.00 gp, inside 1.6 gp. The grain-belt markets (Beregost, Goldenfields, Amphail) sit in the same place.
- **Where grain is imported, the ale price does not follow it.** Ravens Bluff grows 30% of its grain and buys the
  rest at 1.09 to 3.0 gp a bushel landed (the market asks 3.84 gp), yet its brewers sell at 1.19 gp, below the cost of the grain alone, while
  producing 2,301 kegs a day. Baldur's Gate clears 0.07 gp a keg after grain, which cannot pay fuel or labour.
  The gate price looks as if it is built from local grain cost rather than the blended cost of the grain actually
  consumed (C2).
- **Waterdeep does pass the cost through**, so the rule is inconsistent rather than missing. It brews 8,093 kegs
  a day on grain that is 2% local and averages about 7 gp. That ale then supplies 61% of Neverwinter's at a
  landed 8.64 gp, because Goldenfields (4.03 gp landed) has only about 95 kegs a day to spare (C3).
- **Other price evidence disagrees with the engine and with itself.** *Aurora's* sells comparable ales at 9 to 35
  cp per 2-gallon hand keg (0.045 to 0.175 gp a gallon); the engine's 1.6 gp keg is about 0.167 gp a gallon, at
  the top of that range. The Waterdeep Trading Company buttload guide quotes standard ale at 1.50 FSD a gallon
  wholesale, about nine times the engine if FSD and gp are the same unit, which the guide does not say (C4).

## Where the Engine Places It

Settlements carrying each producer tag: `brew` 18, `farm` 50 (of 325 stored settlements).

**Specialty at:** [Amphail](../../../locations/amphail.md) (1), Beregost (2), Goldenfields (1), Lyrabar (1), Purskul (2), Ravens Bluff (2), [Waterdeep](../../../locations/waterdeep.md) (1).

## Related Catalogue Goods (Proposed)

Aurora's entries with no engine equivalent whose closest engine commodity is Ale:

[Bitter black](../drink/bitter-black.md), [Dragon's Breath beer](../drink/dragons-breath-beer.md), [Elminster's Choice](../drink/elminsters-choice.md), [Golden Sands lager](../drink/golden-sands-lager.md), [Iriaeboran North Brew](../drink/iriaeboran-north-brew.md), [Knee-cracker cider](../drink/knee-cracker-cider.md), [Luiren's Best](../drink/luirens-best.md), [Old One Eye](../drink/old-one-eye.md), [Purple Hill cider](../drink/purple-hill-cider.md), [Shadowdark ale](../drink/shadowdark-ale.md), [Suzale (Purple Dragon ale)](../drink/suzale-purple-dragon-ale.md), [Tanagyr's stout](../drink/tanagyrs-stout.md), [Vilhon cider](../drink/vilhon-cider.md).

## Sources

- Engine record: [`faerun/data/store/commodities.json`](../../../faerun/data/store/commodities.json), with storage and recipe values as applied at load time by [`faerun/data/commodities.py`](../../../faerun/data/commodities.py). Read 2026-10-04.
- Settlement placements: [`faerun/data/store/settlements.json`](../../../faerun/data/store/settlements.json), read 2026-10-04.
- Cross-check prices: live server via MCP `compare_prices` for `ale` and `grain`, game date 3 Marpenoth 1492 DR, read 2026-10-04. Observed output; it moves with inputs, events and the calendar. Wages from `list_wages`, same date.
- Waterdeep Trading Company, "Buttloads in Faerûn" (Dynamics Companions, Blind Squirrel Publishing, 2026): 8.34 lb a gallon, 126-gallon butt, standard ale 1.50 FSD a gallon wholesale. Project document, not canon.
- Formulation quantities, route durations and equipment are model assumptions from general pre-industrial brewing practice, not a Realms source.
