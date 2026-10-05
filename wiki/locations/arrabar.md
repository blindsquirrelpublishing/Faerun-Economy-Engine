# Arrabar

[Location index](../README.md)

**Region:** Chondath, Vilhon Reach (engine zone `vilhon`)  
**Settlement type:** Port metropolis; capital of Chondath  
**Reference period:** 1357 to 1373 DR lore, plus a late-15th-century status note  
**Evidence reviewed:** 2026-10-03  
**Engine ID:** `arrabar`

This entry paraphrases the Forgotten Realms Wiki articles on [Arrabar][frwiki]
and [Chondath][chondath], secondary sources. The underlying publications were
not consulted directly.

## Overview

Arrabar, "Shining Arrabar", is the capital of Chondath and one of the main
ports of the Vilhon Reach, known in the 14th century for crime and corruption.
It was destroyed in the Spellplague and is described as back on the map by the
late 15th century DR. [Source][frwiki]

## Geography and Layout

- On the south-eastern shore of the Reach, founded in 50 DR alongside Mussum
  and Samra.
- Districts: Port (west), Warehouse (north), Merchants (south) and Living (east)
  around the central Governor District and the gold-domed Generon palace.
- Canals honeycomb the Port District and run to a turning basin. Most are now
  roofed over and serve as storm drains; fishing from them was forbidden to keep
  them clear (2022 Ed Greenwood social-media post).
- Only a few Reach harbors, Arrabar's and Hlath's among them, were deep enough
  for deep-draft ships (*Pirates of the Fallen Stars*, 1992, pp. 47 to 48).

## Population

| Year | Figure | Source cited by the wiki |
| --- | --- | --- |
| 1357 DR | 5,000 | *Old Empires* (1990), p. 10 |
| 1372 DR | 61,012 | *Forgotten Realms Campaign Setting* 3rd edition (2001), pp. 217 to 218 |

The two figures are hard to reconcile; the 1357 count is not adopted. No count
after the city's restoration was found. The races are mostly human
(Chondathans and Blade Kingdomers).

**The engine now uses 61,012**, the 1372 DR count, as a planning scenario for
1492 DR (previously 42,000). It is recorded in
[populations.py](../../faerun/data/populations.py) with 42,000 as the comparison.

## Economy and Trade

The city sits at the end of the Golden Road and the Emerald Way, which made it
the center of the Vilhon trade. Its people worked in trade, crafting, fishing
and mercenary companies, including permanent private armies; House Wianar's
mercenaries were said to exceed 25,000. Sea trade with Cormyr dates to 389 DR.

| Direction | Goods |
| --- | --- |
| Exports | Lumber |
| Imports | Mulhorandi ale, Tashalaran coffee, Tethyrian tea, peppers |

These describe trade character, not volumes. The import list comes mostly from
the novel *The Sapphire Crescent* (2003).

## Government

The Lord of Arrabar rules from the Generon and hosts an annual assembly of the
free cities of Chondath. Lord Simon Dessino is named for 1370 DR and Lord Eles
Wianar for 1372 DR. The 1492 ruler is unknown; the engine's `ruler` field is
left empty.

## Named Places

- **Crying Claw:** a waterfront tavern for captains and adventurers, run by a
  Harper agent circa 1370 DR.
- **Seaside:** an expensive waterfront tavern.
- **Silver Fish:** a rough tavern in the docks.
- Temples of Lliira and Waukeen, Tempus, Tymora, Silvanus, Lathander and Ilmater.
- **Academia Vilhonus:** a college with a large library.
- **Merchants' Guild:** independent, feuding with Lord Wianar circa 1370 DR. The
  engine also infers a Merchant Guild for the city; the two are not linked.

## Chronology

| Date | Event |
| --- | --- |
| 50 DR | Founded |
| 139 DR | Chondath formed under Anthony Illistine |
| 900 to 902 DR | The Rotting War breaks Chondath into city-states |
| 1358 DR | War with the arcanaloth Yrkhetep wrecks Arrabar's troops and navy |
| 1385 DR | Spellplague ruins Chondath; Arrabar seemingly destroyed |
| 1386 DR | Most of Chondath exchanged with Shyr of Abeir ([Chondath][chondath], citing *Forgotten Realms Campaign Guide*, 2008, p. 90) |
| Late 15th century DR | Land healed after the Second Sundering; Arrabar a port stop on the Reach and the Golden Road (*Foreign Affairs*, DDAL-DRW04, 2020, p. 5) |

## Engine Record

Updated 2026-10-03 with the MCP `update_settlement` tool, in two passes: population
and description first, then industries reviewed against the sources above.

| Field | Value | Basis |
| --- | --- | --- |
| Population | 61,012 (was 42,000) | 1372 DR count, user-selected planning scenario |
| `trade` | 3 | Hub of the Vilhon trade at the end of two trade roads; sea trade with Cormyr |
| `craft` | 2 | One of four named occupations |
| `merc` | 2 | Mercenary companies and private armies; could justify 3 for the 1370s |
| `tag_oak_timber` | 2 | Lumber is the only listed export; the Chondalwood is near, though the Emerald Enclave barred expansion into it in 1356 DR |
| `fish` | 2 (was 0) | One of four named occupations |
| `temple` | 1 (was 0) | Temples to Lliira and Waukeen, Tempus, Tymora, Silvanus, Lathander and Ilmater |
| `ship` | 1 (was 2) | Deep-water harbor documented; no shipbuilding mentioned; navy wrecked in 1358 DR |
| `textile` | 1 (was 2) | Not mentioned for Arrabar |
| `vint` | 1 (was 2) | Not mentioned for Arrabar; nearby wine comes from Nimpeth and Hlondeth |
| Specialties | `wine_common` 1 (was 2); `sword` removed (was 1) | Wine lowered to match `vint`; no smithing industry or sword trade in the sources |
| Region, port, traits | Chondath; Sea of Fallen Stars; `port`, `mercantile`, `mercenary`, `noble` | Unchanged |

Industry levels are engine inputs chosen to reflect the description, not
sourced quantities.

## Discrepancies and Open Questions

- **1492 DR conditions.** The restoration note confirms a working port but gives
  no population, ruler or industry. Every engine value is a planning input
  based mostly on 1370s descriptions.
- **Population gap.** 5,000 in 1357 DR against 61,012 in 1372 DR.
- **Hlath's harbor.** The wiki names Hlath as one of the Reach's few deep-water
  harbors, but the engine has Hlath with no port. Not reviewed here.
- **Wine and Red Cask Hulls.** Wine is not supported by the reviewed articles.
  `wine_common` was kept at 1 rather than removed because the invented carrier
  Red Cask Hulls ships Arrabar's common wine to Hlondeth. If wine is dropped,
  the carrier should source from Hlondeth or Nimpeth instead.

## Sources

**Directly consulted, secondary:** [Forgotten Realms Wiki: Arrabar][frwiki] and
[Forgotten Realms Wiki: Chondath][chondath], accessed 2026-10-03. Publications
cited above are the wiki's references, not independently checked.

[frwiki]: https://forgottenrealms.fandom.com/wiki/Arrabar
[chondath]: https://forgottenrealms.fandom.com/wiki/Chondath
