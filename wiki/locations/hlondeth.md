# Hlondeth

[Location index](../README.md)

**Region:** Vilhon Reach (engine region `Vilhon Reach`, zone `vilhon`)  
**Settlement type:** Independent city-state; metropolis  
**Reference period:** 1357 to 1373 DR lore; 1492 DR planning baseline unverified  
**Evidence reviewed:** 2026-10-03  
**Engine ID:** `hlondeth`

This entry paraphrases the [Forgotten Realms Wiki article][frwiki], a secondary
source that mixes 2nd- and 3rd-edition material. The underlying publications
were not consulted directly. The article stops in 1373 DR, so nothing below is
verified for 1492 DR.

## Overview

Hlondeth, the City of Serpents, is a walled city-state ruled by House
Extaminos, a noble family of yuan-ti blood. It broke from Chondath in 614 DR
and was independent in the 1370s DR. [Source][frwiki], citing *Serpent Kingdoms*
(2004), pp. 94 to 95.

## Geography

- Sits on the Churning Bay on the northern shore of the Vilhon Reach, opposite
  Sespech. The volcanic Mount Ugruth is close enough to threaten it.
- Its territory runs about 50 miles from the city and holds roughly a dozen
  villages and numerous vineyards. [Source][frwiki], citing *Serpent Kingdoms*, p. 92.
- Founded in 50 DR as a port at the end of the Turmway from Alaghôn.
- Built largely of emerald-hued marble from nearby quarries, with ramps in place
  of stairs and a working sewer system.

## Population

The infobox gives **453,600 for the city and its environs in 1372 DR**, citing
*Forgotten Realms Campaign Setting* 3rd edition (2001), p. 216. That figure covers
the 50-mile territory, not the city alone. No city-only count and no figure after
1373 DR was found.

The demographic breakdown is humans 84% (Chondathan 56%, Turami 41%, Shaaran 3%),
kobolds 15%, yuan-ti 1% and halflings under 1%, citing *The Vilhon Reach* (1996),
p. 21. The article describes the kobold population as enslaved.

**The engine's 60,000 residents is a user-selected planning scenario**, set on a
par with Arrabar's sourced 1372 DR count. It is recorded in
[populations.py](../../faerun/data/populations.py) with the 453,600 figure as its
comparison.

## Economy and Trade

The article calls Hlondeth very prosperous and one of the busiest ports on the
Reach. It carried goods into southern Turmish, traded with the Shining Plains,
and traded heavily with the nagas and yuan-ti of Sespech.

| Direction | Goods |
| --- | --- |
| Exports | Green marble, basalt, statuary, mosaic tiles, tough textiles (for awnings), aloe-based liniments, seafood, wines |
| Imports | Sespechian wine, perfume, herbs, spices, poisons, timber, weapons, slaves, flying snakes from the Mhair Jungles |

Several of these items cite a 2022 Ed Greenwood social-media post, not a
sourcebook. None of them establish volumes, prices or which goods still moved
in 1492 DR.

## Government

House Extaminos rules. Dediana Extaminos is matriarch in 1370 to 1373 DR, with
her son Dmetrio as heir and a spirit naga, Ssibalentanamas, as First Consort.
[Source][frwiki], citing *Powers & Pantheons* (1997) and *Serpent Kingdoms*. The
1492 ruler is unknown; the engine's `ruler` field is left empty.

## Infrastructure and Named Places

- **Harbor:** the article describes a busy port but gives no harbor size,
  berths or depth.
- **Mortal Coil:** a tavern in a waterfront warehouse basement (*Venom's Taste*, 2004).
- **Slithering Serpent Inn:** popular with visitors for black adder stew.
- **Great Aviary of Extaminos:** completed 1368 DR.
- **Cathedral of Emerald Scales:** the city's central temple, to Sseth as Varae.
- Temples of Helm and Silvanus, and the Sacellum of Slumbering Fire (Talos) at the
  foot of Mount Ugruth.

These are source-backed names, not additional businesses or workers in the
simulation.

## Chronology

| Date | Event |
| --- | --- |
| 50 DR | Founded as a port at the end of the Turmway |
| 145 DR | Withstands a siege from Alaghôn with the help of 60 pirate ships offered safe harbor |
| 257 DR | Mount Ugruth erupts; Chondath seizes the city |
| 527 DR | Kobold and drow attack through the sewers; governor's palace burned |
| 614 DR | Independence from Chondath under House Extaminos |
| 1020 DR | House Extaminos takes full control |
| 1373 DR | Plague (the Pox) among human residents; last dated event in the article |

## Engine Record

Updated 2026-10-03 with the MCP `update_settlement` tool. Before this, Hlondeth
was an automatically generated surveyed market that copied Arrabar's profile
at one twenty-fifth of its population (1,680 residents, no port, no industries).

| Field | Value | Basis |
| --- | --- | --- |
| Region | Vilhon Reach | Article region; independent of Chondath since 614 DR |
| Population | 60,000 | User-selected planning scenario |
| Port | Sea of Fallen Stars | Busiest-port description |
| Traits | `port`, `mercantile`, `noble`, `temple`, `cosmopolitan` | Port and trade; ruling noble house; many temples; welcomes visitors of most races |
| Industries | `trade` 3, `quarry` 3, `craft` 2, `textile` 2, `vint` 2, `fish` 2, `pottery` 1, `herb` 1, `farm` 1 | Mapped from the export list, the vineyards and the villages |
| Specialties | `marble` 2, `wine_common` 1, `fish_fresh` 1, `herbs_healing` 1 | Green marble; wines; seafood; aloe liniments |
| Wealth / tax / security | 1.2 / 0.09 / 0.8 | Engine judgment: "very prosperous", well-run walled city with extensive patrols |

Industry levels and the wealth, tax and security values are engine inputs
chosen to reflect the description, not sourced quantities.

## Discrepancies and Open Questions

- **1492 DR status.** No account after 1373 DR was found. Whether House
  Extaminos still rules, and how the Spellplague and the Reach's later
  restoration affected the city, are unresolved.
- **Population scope.** 453,600 includes the environs. The 60,000 city figure
  has no source.
- **Gryphon eyrie.** At 60,000 residents with the `noble` trait, the engine now
  gives Hlondeth an automatic gryphon port. The article says residents feared
  birds of prey and giant birds (*Warriors and Priests of the Realms*, 1996,
  pp. 52 to 54), yet the city also built a Great Aviary. Preserved for review.
- **Shortages not set.** Timber and weapons are listed imports, but import is not
  the same as being unable to supply, so `shortages` is left empty.
- **Slaves and poisons.** Listed imports with no matching engine commodities;
  not modeled.

## Sources

**Directly consulted, secondary:** [Forgotten Realms Wiki: Hlondeth][frwiki],
accessed 2026-10-03. Publications cited above are the wiki's references, not
independently checked.

[frwiki]: https://forgottenrealms.fandom.com/wiki/Hlondeth
