# Triboar

[Location index](../README.md)

**Region:** Dessarin Valley (engine classification; not independently checked here)  
**Reference period:** Fifth-edition *Storm King's Thunder*, after 1485 DR; exact year unresolved  
**Evidence reviewed:** 2026-10-01  
**Engine ID:** `triboar`  
**Review scope:** Limited alternative-source business and civic notes

## Overview and Evidence Limits

The preferred Forgotten Realms Wiki article was inaccessible during this review.
The notes below instead paraphrase Sean McGovern's [Power Score guide][guide].
This is an unofficial secondary reference, not independent consultation of the
sourcebook. It combines summaries with campaign advice; suggestions and campaign
outcomes are not adopted as canonical conditions.

The guide refers to the sourcebook's page 13 sidebar for an **after 1485 DR**
setting. Its suggested spacing between adventures is personal advice, not a
canonical calendar. Neither that lower date bound nor its 2016 publication date
establishes operation of these businesses in **1492 DR**.

## Economy and Named Places

| Person or establishment | Attributed detail | Evidence and qualification |
| --- | --- | --- |
| Othovir | Harness-making | Guide's Triboar NPC summary; staffing and output unknown. |
| Northshield House / Urgala Meltimer | Inn owned by Urgala | Guide's Triboar NPC summary; beds, occupancy and continued operation unknown. |
| Narth Tezrin / Lionshield Coster | Merchant organization association | Guide's Triboar NPC summary; does not establish freight volume or inventory. |

These names offer possible identities for existing craft, lodging and trade
capacity. They are **not extra businesses or workers** added to the simulation.
The reviewed passages do not substantiate cattle or salted-meat export volumes,
caravan throughput, prices, or a current agricultural production mix. [Source][guide]

## Government

The guide's Harper faction list identifies **Darathra Shendrel** as Lord Protector
of Triboar and points to sourcebook page 53. Its later NPC list spells the surname
"Shenrel"; this entry follows its fuller faction-list spelling without claiming
independent corroboration. Tenure in 1492 remains unverified. [Source][guide]

## Engine Record

The [stored settlement](../../faerun/data/store/settlements.json) configures
2,500 residents, Dessarin Valley / `dessarin`, plains terrain, no port, and
`river: false`. Industries are `cattle: 3.0`, `farm: 2.0`, `trade: 2.0`,
`craft: 1.0`, and `smith: 1.0`; specialties are `cow: 2.0` and `meat_salt: 1.0`.
Ruler and description are empty. These values are model inputs, not verified lore.

The [runtime lore catalogue](../../faerun/data/lore.py) now contains only the
qualified secondary summary. No catalogue economics, map coordinates, routes,
business staffing, or live simulation state were changed. No simulation outputs
were measured.

## Discrepancies and Next Leads

- **Harness-making and lodging:** compare directly with *Storm King's Thunder*'s
  Triboar entries before assigning identities to generated establishments. Any
  later integration should identify existing capacity first, not increase it.
- **Population and agricultural mix:** the model's 2,500 residents and cattle /
  salted-meat emphasis remain unverified, not disproved. Seek a dated census and
  explicit trade descriptions before proposing recalibration.
- **1492 applicability:** verify civic tenure and business continuity. The
  adventure's broad date bound does not resolve either.
- **Roads and water:** obtain directly supported geography and infrastructure
  evidence before proposing routing, water-capacity, or map changes.

### Follow-up: World Anvil Provenance

The [World Anvil Triboar page][worldanvil] was read on 2026-10-01. Its footer
explicitly attributes its material to Forgotten Realms Wiki with additions,
modifications, and filled gaps. It is therefore a derivative fan compilation,
not an independent corroborating source or a substitute for checking the
underlying publications. Which individual claims were modified is not identified.

Useful **unverified leads** include horse and mule provisioning, wagons,
leatherwork, ironware, grain farming, and the Long Road / Evermoor Way crossroads.
Its approximate 2,500 population and guide-service prices are not adopted as
canonical model inputs. The article mixes 14th- and 15th-century material; its
1491 civic claim does not independently resolve the earlier review's date gap.

This follow-up records source quality and research leads only. Runtime lore stays
with the earlier attributed Power Score subset; no new canonical claim, economic
adjustment, or map proposal is supported solely by this compilation. Direct
sourcebook verification remains the next discriminating check.

## Sources

**Directly consulted:** [Power Score: Dungeons & Dragons - A Guide to Storm
King's Thunder][guide], Sean McGovern, posted 2016-08-19; accessed 2026-10-01.
Unofficial secondary adventure guide. Relevant sections: dating discussion,
Harper faction list, and Chapter 2 / Triboar NPC summaries. Confidence is limited
by mixed commentary and inconsistent spelling; no independent corroboration is
claimed.

**Underlying publication, not directly consulted:** *Storm King's Thunder*
(Wizards of the Coast, 2016, fifth edition). Page references above are the guide's
references, not independently checked citations to the book.

**Discovery only:** [Sly Flourish: Getting the Most out of Storm King's Thunder][sly],
Mike Shea, 2018-01-16; accessed 2026-10-01. Its recommendation led to Power Score;
it is not independent corroboration of the business details.

**Unavailable, not cited as evidence:** [Forgotten Realms Wiki: Triboar][frwiki],
attempted 2026-10-01; advertising redirect from fetch and browser verification
block. Search snippets were not adopted as evidence.

**Directly consulted for provenance, not adopted as canon:** [World Anvil:
Triboar, The Forgotten Realms - old version][worldanvil], theaaronw0, accessed
2026-10-01. Derivative fan compilation admitting modifications; mixed historical
periods, underlying publications not independently verified through this page.

[guide]: https://thecampaign20xx.blogspot.com/2016/08/dungeons-dragons-guide-to-storm-kings.html
[sly]: https://slyflourish.com/getting_the_most_out_of_skt.html
[frwiki]: https://forgottenrealms.fandom.com/wiki/Triboar
[worldanvil]: https://www.worldanvil.com/w/the-forgotten-realms---old-version-theaaronw0/a/triboar-settlement