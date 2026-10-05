# Commodity Wiki

[Wiki index](../README.md)

One page for each of the engine's 278 commodities and for each of the 371 candidate goods found in the
commodity sections of *Aurora's Whole Realms Catalogue* (TSR 9358, 1992, AD&D 2nd edition). 93 engine commodities also carry the matching catalogue entries.
Proposed pages are documentation only: nothing here changes the simulation, and a proposal enters the engine
only through a separate, validated data change.

## Categories

| Category | Engine | Proposed | Total |
| --- | --- | --- | --- |
| [Arcane goods](arcane/README.md) | 28 | 143 | 171 |
| [Arms and armour](arms/README.md) | 15 | 0 | 15 |
| [Drink](drink/README.md) | 9 | 13 | 22 |
| [Exotic goods](exotic/README.md) | 9 | 0 | 9 |
| [Food](food/README.md) | 63 | 120 | 183 |
| [Gems](gem/README.md) | 22 | 0 | 22 |
| [Livestock](livestock/README.md) | 20 | 0 | 20 |
| [Luxury goods](luxury/README.md) | 23 | 49 | 72 |
| [Manufactured products](product/README.md) | 34 | 7 | 41 |
| [Materials](material/README.md) | 29 | 11 | 40 |
| [Metals](metal/README.md) | 15 | 1 | 16 |
| [Textiles](textile/README.md) | 11 | 27 | 38 |
| **All** | **278** | **371** | **649** |

## Page Types

- **Engine pages** record the stored catalogue row as the engine loads it: description, unit, weight, base price,
  producer tags, demand and luxury indices, perishability, storage, harvest calendars and recipe links, plus where
  settlements specialise in it, carry a dedicated industry tag, or are configured short of it. When Aurora's lists
  the same good, its prices and a price comparison follow. These values are model inputs, not canon.
- **Proposed pages** record an Aurora's entry that has no engine equivalent: the catalogue's description (paraphrased),
  stated origin, every printed price and quantity, a scaled price estimate and the closest engine commodity.

## What Was Taken From Aurora's

Included: Aurora's Larder, Breads, Cheese Shop, Wines and Ales, Exotics (including the Additional Exotics list), the
Laborers' List metals table and building consumables, Tailors' Corner fabrics, skins, dyes, feathers and raw fibres,
Illuminations (candles, wax, lamp oil, wicks, torches), Personal Supplies consumables, Priests' Alcove incense, and
the spell-component tables in the Priests' Alcove and Wizards' Laboratory.

Left out as finished goods or equipment rather than commodities: weapons, tools, clothing, furniture, tableware,
lamps and lanterns, laboratory apparatus, sewing tools and patterns, wilderness gear, vehicles and the fashion armour
of Boom's Garden.

Grouping rule: a page is one catalogue item; the catalogue's own sub-entries (flavours, grades, named regional
varieties, container sizes) are rows in that page's price table. Where several sections list the same material (for
example salt in the Larder and both component tables) the rows share one page. Named regional cheeses, beers and
wines are separate pages because the catalogue treats them as distinct products.

## Price Scaling

Aurora's prices are retail mail-order prices with magical delivery built in. Staple foods run about 200 times the
engine's prices, while herbs, base metals and fabrics are much closer. A single conversion would distort everything,
so each kind of good gets its own factor: the median, across catalogue entries that match an engine commodity one to
one, of engine price per lb divided by catalogue price per lb. Liquids assume 8.3 lb per gallon. Spell components
are sold in laboratory quantities and are not scaled.

| Scaling group | Factor | Anchors (engine commodity: ratio) |
| --- | --- | --- |
| grains, flours and breads | 0.005 | Rice (rice): 0.003; Wheat berries (grain): 0.005; Wheat flour (flour): 0.006 |
| dried fruit, preserves, nuts, sweeteners and oils | 0.0244 | Sugar (sugar): 0.08; Dried apples (dried_apples): 0.111; Dried dates (dates): 0.0002; Dried figs (dried_figs): 0.000651; Dried peaches (dried_peaches): 0.015; Dried pears (dried_pears): 0.0244; Olives (olives): 0.00641; Olive oil (olive_oil): 0.221; Honey (honey): 0.389 |
| common seasonings (herbs) | 0.938 | Salt (salt): 0.312; Garlic (garlic): 0.938; Anise (anise): 5; Coriander (coriander): 1.25; Cumin (cumin): 0.781; Fennel seed (fennel_seed): 1.12; Fenugreek (fenugreek): 0.458; Juniper (juniper_berry): 0.417; Mustard seed (mustard_seed): 1.75 |
| spices and exotic foodstuffs | 0.0354 | Pepper (black_pepper): 0.0125; Cloves (cloves): 0.025; Cardamom (cardamom): 0.688; Ginger (ginger): 0.0391; Nutmeg (nutmeg): 0.0333; Saffron (saffron): 0.0486; Turmeric (turmeric): 0.00875; Cinnamon (cinnamon): 0.0375; Mace (mace_spice): 0.045; Long pepper (long_pepper): 0.00562; Paprika (paprika): 0.00708; Chilis (chili_pepper): 0.0143; Coffee (roasted, Durpar) (coffee): 0.08; Shou tea (tea): 0.0857 |
| durable meat and fish | 0.0125 | Preserved beef (meat_salt): 0.015; Preserved cod (fish_salt): 0.00667; Preserved herring (fish_salt): 0.01; Preserved pork (meat_salt): 0.0171 |
| cheeses | 0.171 | Waterdhavian cheese (cheese): 0.171 |
| ales, beers and ciders | 3.74 | Elminster's Choice (ale): 2.49; Knee-cracker cider (ale): 4.98 |
| wines, meads and ciders | 2.21 | Neverwinter mead (mead): 0.445; Table wine (Aurora's) barrel (wine_common): 3.98 |
| fabrics, skins, dyes and feathers | 1.33 | Raw wool (raw_wool): 1.25; Indigo dye (dye_indigo): 1.33; Purple dye (dye_purple): 6.82 |
| metals | 3.53 | Bronze (bronze): 15.5; Gold (gold_ingot): 4.65; Iron (iron_ingot): 2.22; Lead (lead_ingot): 3.53; Platinum (platinum_ingot): 7.38; Silver (silver_ingot): 0.835; Steel (steel_ingot): 1.3; Copper (copper_ingot): 10; Tin (tin_ingot): 4; Mithral (mithral_ingot): 3.48  Factor uses non-coinage base metals only (iron, steel, tin, lead, bronze); copper, silver, gold and platinum are valued by the coin standard instead. |
| lighting, toiletries, incense and building supplies | 0.667 | Nails and spikes (nails): 0.667; Pitch (roofing) (pitch): 0.667; Scented beeswax (wax): 0.214; Whale lamp oil (whale_oil): 3.46; Scented lamp oil (lamp_oil): 0.259; Perfume (Westgate) (perfume): 3; Selgauntan soap (soap): 0.5 |

A scaled estimate is a review aid, not an engine value. Several anchors are themselves rough (the engine's own
prices are modelling assumptions), and the spread inside a group is often a factor of ten.

## Coin Standard

Copper, silver, gold and platinum are coinage metals, so their price is pinned by what they mint into, not by catalogue
prices. The assumption: 50 coins weigh a pound (the AD&D 2nd edition and D&D 5th edition standard), and a mint
loses 4% of the metal to casting scrap, blank trimming and assay, so **one pound of ingot yields 48 coins**
and a 10 lb engine ingot yields 480. An ingot's bullion value is the face value of those coins.

| Metal | Coin | Face value | Coins per 10 lb ingot | Bullion value per ingot | Engine price |
| --- | --- | --- | --- | --- | --- |
| [Copper](metal/copper-ingot.md) | copper pieces | 0.01 gp | 480 | 4.8 gp | 4.8 gp |
| [Silver](metal/silver-ingot.md) | silver pieces | 0.1 gp | 480 | 48 gp | 48 gp |
| [Gold](metal/gold-ingot.md) | gold pieces | 1 gp | 480 | 480 gp | 480 gp |
| [Platinum](metal/platinum-ingot.md) | platinum pieces | 5 gp | 480 | 2,400 gp | 2,400 gp |

All four were set to bullion value on 2026-10-04 ([C1](../inventory.md#proposed-economy-changes)). Platinum had been 550 gp,
under a quarter of its coin value; copper, silver and gold had been at face value with no minting loss, 4% higher.
Electrum has no engine commodity.
Mithral and adamantine are not coin metals, so the standard does not apply to them.

Aurora's metal table is inconsistent against this standard. Its silver (about 5.5 to 6 gp per lb against 4.8) agrees, but
copper is a tenth of bullion value, gold about a fifth (10 gp per lb against 48) and platinum a tenth to a sixth. The catalogue
rows stay on the pages for reference and are not used as anchors.

## Known Gaps

- Prices were read from the PDF's text layer and checked against the page layout; a handful of incense varieties
  have no price printed in the catalogue and are recorded that way.
- Mithral has no coin standard and only the catalogue's low price to compare with; see its page.
- The catalogue's origins are its own marketing claims. They are leads for regional sourcing, not verified geography.
- Engine descriptions that read as generic filler are reproduced as stored; rewriting them is a separate data change.

## Sources

- *Aurora's Whole Realms Catalogue* (TSR 9358, 1992, AD&D 2nd edition), J. Robert King and Co., design concept Anne Brown. Primary source, consulted directly from the project copy in [`.guides/`](../../.guides/tsr09358%20-%20Aurora's_Whole_Realms_Catalogue.pdf) on 2026-10-04. Page numbers are the printed folios. Prices are the catalogue's retail mail-order prices; descriptions here are paraphrased.
- Engine catalogue: [`faerun/data/store/commodities.json`](../../faerun/data/store/commodities.json) and [`faerun/data/commodities.py`](../../faerun/data/commodities.py), read 2026-10-04.
