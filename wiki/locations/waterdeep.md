# Waterdeep

[Location index](../README.md)

**Region:** Sword Coast North (engine region `Sword Coast`, zone `waterdeep`)  
**Settlement type:** Metropolis; oligarchic city-state  
**Reference period:** 1492 DR planning baseline; lore spans 1372 to 1492 DR  
**Evidence reviewed:** 2026-10-03  
**Engine ID:** `waterdeep`

This entry paraphrases the [Forgotten Realms Wiki article][frwiki] (a secondary
source mixing 2nd- to 5th-edition material) and the engine's curated city
directory from *Volo's Guide to Waterdeep* (1992). Neither is verified for
1492 DR unless a 5th-edition source is cited.

## Overview

Waterdeep, the City of Splendors or Crown of the North, is the most important
city in the North: a cosmopolitan trade hub and a leading member of the Lords'
Alliance. It is governed by sixteen masked Lords of Waterdeep with an Open Lord
in public; in 1492 DR that is Laeral Silverhand, after Dagult Neverember was
ousted. [Source][frwiki], citing *Waterdeep: Dragon Heist* (2018).

## Geography

- Built on the slopes of Mount Waterdeep over a natural deep-water harbor,
  the source of the city's name. Undermountain lies beneath.
- Wards: Castle, Dock, North, Sea, Southern ("South"), Trades, the walled City of
  the Dead, and later Field Ward, Mountainside, Undercliff (by 1479 DR),
  Mistshore and Downshadow.
- Claims land about 100 miles beyond its walls; its authority is elsewhere
  given as 30 to 40 miles. The two figures are unreconciled.
- Major roads: the Trade Way south, the Long Road inland north and the High
  Road along the coast. [Source][frwiki], citing *City of Splendors: Waterdeep*
  (2005), p. 15.

## Population

| Figure | Scope | Year | Source cited by the wiki |
| --- | --- | --- | --- |
| 132,661 | City proper | 1372 DR | *Forgotten Realms Campaign Setting* 3e (2001) |
| 1,347,680 | City and farmland territory | 1372 DR | Same |
| Up to 2,000,000 | Probably the region | 15th century DR | WotC web article; the wiki's note suggests about 200,000 for the city |

The races are humans 64%, dwarves 10%, elves 10%, halflings 5%, half-elves 5%,
gnomes 3%, half-orcs 2%. In 1395 DR the Putrescent Anathema plague cut the
population, hitting the poor hardest.

**Engine:** 200,000 residents, a user-selected 1492 DR planning scenario already
recorded in [populations.py](../../faerun/data/populations.py). No change proposed.

## Economy and Trade

The city is the trading hub between the mineral-rich North, Amn and Calimshan,
the Inner Sea and the western sea kingdoms.

| Direction | Goods (wiki infobox) |
| --- | --- |
| Imports | Grain, livestock, leather, ore, timber, exotic goods |
| Exports | Ale, arms, cloth, fish, furnishings, leather goods, pottery, refined metals, finished goods |

Other trade notes:
- Building stone was magically shipped from Mirabar via Luskan in the early
  1370s DR, at great expense (*Volo's Guide to the North*, p. 152).
- It is Faerûn's largest spelljamming port; ships must land at sea and come in
  by water. Docking costs 1 cp per 10 feet of keel per week (*Realmspace*, 1991).
- The 1395 DR plague destroyed much of Goldenfields' grain, the city's main
  supply.
- Public transport: drays (2 to 4 nibs), two-seat hire-coaches (rarely over
  6 shards) and hired carriages by the day.

## Government and Factions

- The Lords of Waterdeep (masked council) with an Open Lord; Magisters
  ("Black Robes") run the courts. City Guard (soldiery) and City Watch (police);
  Force Grey; the Griffon Cavalry.
- Guilds control much of the city's trade. Guild masters seized the city after
  1248 DR and the Lords' system replaced them in 1273 DR; the infobox dates the
  Guildwars to 1256 to 1262 DR. 76 noble families.
- Crime in 1492 DR: the Xanathar Guild competes with Zhentarim factions.

## Businesses

### In the live market (engine `businesses.json`)

| Business | Type | Offers | Note |
| --- | --- | --- | --- |
| The Halls of Hilmer, Master Armorer | Armorer | Plate (masterwork), chain, shields | Volo, Castle Ward |
| Hriiat Fine Pastries | Bakery | Bread, flour, salted meat | Volo, North Ward |
| The House of Good Spirits | Vintners' guildhall and inn | Ale, wines, bread | Volo, Southern Ward |
| Phalantar's Philtres & Components | Apothecary | Herbs, spell components, healing potions | Volo, Castle Ward |
| Serpentil Books & Folios | Bookseller | Books, parchment, ink, blank spellbooks | Volo, Dock Ward |
| Halambar Lutes & Harps | Instrument maker | Books, dyed cloth | Offers are stand-ins; no instrument commodity |
| Balthorr's Rare and Wondrous Treasures | Curios and gems | Gems | Volo, Castle Ward |
| The Old Xoblob Shop | Curios | Wine, tools, saddles, potions | Volo, Dock Ward |
| The Old Monster Shop | Live creatures and remains | Riding horses, potions, herbs | Offers are stand-ins; no monster commodity |
| Pelauvir's Counter | General goods | Barrels, tools, cloth, paper | Volo, Southern Ward |
| Gelfuril the Trader | Used goods | Tools, saddles, cloth | Volo, Dock Ward |
| Orsabbas's Fine Imports | Imports and costumes | Fine cloth and clothing, silk, perfume | Volo, Trades Ward |
| Helmstar Warehouse | Packing and forwarding | Barrels, carts, `crate` | `crate` is not a commodity |
| Red Sails Warehouse | Storage | None | Service only |
| The Jade Jug | Luxury inn | Ale, fine wine, bread, salted meat | Volo, Castle Ward |
| Deepwater Scribes' Exchange | Scribal supplies (multi-city) | Paper, parchment, ink, books | Engine-authored; source not recorded |
| Golden Sheaf Provisions | Provisions (HQ Goldenfields) | Grain, flour, bread, meat, ale | Engine-authored |
| Ironstar Forge Company | Arms (HQ Sundabar) | Steel, swords, axes, armor, tools | Engine-authored |
| Amphail Remount Company | Horses (HQ Amphail) | Horses, warhorses, saddles | Engine-authored |
| Five carriers | Freight | None | HQ Waterdeep: Vilhon Reach Milk Run, Sword Coast Coasters, Waterdeep-Daggerford Caravan Company, North Coast High Road Freight, Sword Coast Overland Exchange. Reviewed in the routes phase |

### In the city directory only (Volo, 1992; not yet market businesses)

31 entries: six Aurora's Realms Shop catalogue counters (one per ward),
Belmonder's Meats, Dacer's Inn, Gounar's Tavern, Halazar's Fine Gems, Maerados
Fine Furs, Nueth's Fine Nets, Olmhazan's Jewels, Riautar's Weaponry, Saern's Fine
Swords, Selchoun's Sundries Shop, Sulmest's Splendid Shoes & Boots, The Blue
Mermaid, The Cliffwatch, The Galloping Minotaur, The Golden Key, The House of
Pride, The Inn of the Dripping Dagger, The Jade Dancer, The Misty Beard, The
Pampered Traveler, The Rearing Hippocampus, The Riven Shield Shop, The Ship's
Wheel, Thentavva's Boots and Warm Beds. Use `get_city_directory` for ward,
address, people and page citations.

## Engine Record

| Field | Value |
| --- | --- |
| Population | 200,000 |
| Wealth / tax / security | 1.35 / 0.10 / 0.85 |
| Port | Sea of Swords |
| Traits | `port`, `cosmopolitan`, `noble`, `arcane`, `military`, `mercantile`, `academic`, `temple` |
| Industries | `trade` 3, `craft` 3, `arcane` 3, `alch` 2, `brew` 2, `paper` 2, `ship` 2, `smith` 2, `temple` 2, `textile` 2, `tag_barding` 2, `tag_carriage` 2, `tag_homing_pigeon` 2, `glass` 1 |
| Specialties | `clothing_fine` 2, `spellbook_blank` 2, `book` 1, `spell_components` 1, `ale` 1 |
| Shortages | `grain`, `timber`, `iron_ore`, `wool` |
| Ruler | The Lords of Waterdeep |
| Guilds (inferred) | Merchant; Farmers' and Millers'; Fishers' and Watermen's; Smiths' and Armorers'; Artisans'; Alchemists' and Apothecaries' |

Observed 2026-10-03 (`get_trade_summary`): gross local product 692.8 million gp
a year (3,464 gp per resident); goods imports 9.19 million gp a day against
exports of 0.86 million; 1.30 million gp a day of inbound freight assigned to
no carrier.

## Discrepancies and Proposed Engine Changes

Proposals only; nothing below has been applied.

| # | Issue | Proposal |
| --- | --- | --- |
| W1 | Fish is a listed export and the city has a Fishers' guild, but there is no `fish` industry | Add `fish` 2 |
| W2 | Leather goods and pottery are listed exports with no matching industry | Add `tan` 1 and `pottery` 1 |
| W3 | Arms are a listed export and there is a master armorer, but no `weapon` or `armor` industry | Add `weapon` 1 and `armor` 1 |
| W4 | Tag industries export about 5,000 homing pigeons, carriages and barding suits a day each (an identical 5,382 surplus) | Review tag-industry output scaling; consider lowering these tags to 1 |
| W5 | Unavailable exotic goods (pineapple, pears, citrus, yak, camel, even longships) each show a flat 400-a-day import need | Review the default import need for unavailable goods |
| W6 | Imports are about 10 times exports, and output per resident (3,464 gp a year) is very high | Review valuation of goods output and imports |
| W7 | `wool` shortage is not supported by the import list, which names grain, livestock, leather, ore and timber | Keep (plausible), or swap for `leather` |
| W8 | Helmstar Warehouse offers `crate`, which is not a commodity | Add `crate` or change the offer to `barrel` |
| W9 | Halambar Lutes & Harps and The Old Monster Shop sell stand-in goods | Add instrument and monster-remains commodities (below) |
| W10 | 31 directory businesses have no market record | Promote selectively, starting with those that sell modeled goods (Saern's Fine Swords, Riautar's Weaponry, Belmonder's Meats, Maerados Fine Furs, Nueth's Fine Nets, Olmhazan's Jewels) |

## Proposed New Commodities

| Candidate | Evidence | Producers |
| --- | --- | --- |
| Furniture / furnishings | Listed export | `craft`, `log` |
| Musical instruments | Halambar Lutes & Harps | `craft` |
| Locks and fastenings | The Golden Key | `smith` |
| Boots and shoes | Sulmest's; Thentavva's Boots | `tan`, `craft` |
| Jewelry | Olmhazan's Jewels; fashion section | `craft`, `mine_gem` |
| Maps and sea charts | Serpentil Books & Folios | `paper` |
| Zzar and sluth | Made at the House of Good Spirits | `vint` (to check) |
| Crate | Helmstar Warehouse | `log` |
| Monster remains | The Old Monster Shop | `hunt` |
| Waterdhavian cheese | The wiki's disambiguation note names it; not yet read | `cattle`, `herd` |

## Lore Follow-ups

1. **Named guilds.** Read the wiki's "Guilds of Waterdeep" article and map
   real guilds onto the engine's six inferred ones.
2. **Volo's businesses in 1492.** The directory is 1992 material. Check which
   survive in *Dragon Heist* (2018); add Dragon Heist establishments such as
   the Yawning Portal.
3. **Aurora's Realms Shop.** A North-wide catalogue chain; decide whether it is
   one multi-city business.
4. **Spelljamming port.** Docking rules and fees could become a trade route type.
5. **Territory.** Reconcile 100 miles against 30 to 40 miles of authority, and
   decide which nearby villages the city's farmland includes.
6. **Missing nearby settlements.** Rassalantar (Belmonder's estates), Kheldell,
   Zelbross, Westbridge, Bargewright Inn, Liam's Hold, Gillian's Hill, Womford,
   Julkoun, Thornhold and Carnath Roadhouse are not in the engine.
7. **Grain dependency.** Confirm Goldenfields' recovery after 1395 DR (next:
   Goldenfields entry).
8. **Runtime lore.** The `waterdeep` entry in `lore.py` is a short geographic
   summary; expand it once these follow-ups are settled.

## Sources

**Directly consulted, secondary:** [Forgotten Realms Wiki: Waterdeep][frwiki],
accessed 2026-10-03. Publications cited above are the wiki's references, not
independently checked.

**Engine:** `get_settlement`, `get_trade_summary`, `get_city_directory` (Volo's
Guide to Waterdeep, 1992, with PDF page citations), and
[businesses.json](../../faerun/data/store/businesses.json), observed 2026-10-03.

[frwiki]: https://forgottenrealms.fandom.com/wiki/Waterdeep
