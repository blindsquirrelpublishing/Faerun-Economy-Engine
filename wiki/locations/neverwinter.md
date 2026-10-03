# Neverwinter

[Location index](../README.md)

**Region:** Sword Coast North  
**Reference period:** Circa 1372 DR inferred for history; fifth-edition institutional reference without an exact setting year  
**Evidence reviewed:** 2026-10-01  
**Engine ID:** `neverwinter`  
**Status:** Historical economy and primary-source Alliance reference reviewed; 1492 continuity unresolved

## Overview and Period

[Realms Helps: The North][north] describes Neverwinter in its Sword Coast North
section under Lord Nasher Alagondar. Third-edition-style character statistics and
surrounding regional chronology indicate an older, late-14th-century snapshot:
the page discusses Alustriel's 1369 transition and describes the confederation's
formation as three years earlier. Circa 1372 is therefore an inferred context,
not an explicitly dated Neverwinter census or a claim about 1492.

This is a directly reviewed secondary web reference. An underlying published
sourcebook was not independently consulted. The broad request for all available
information is only partially addressed by this historical economic first pass.

## Historical Economy

The city's craftspeople were known for decorative glass lamps, water clocks,
and jewelry. River-warmed gardens supplied fruit in summer and flowers in winter.
These are useful craft and horticulture leads, not production measurements or
proof of continuous operation into the project baseline. [Source][north]

No workshop names, employment counts, crop acreage, import volumes, harbor
throughput, or current freight services were established in the reviewed passage.
Regional import/export lists cannot be assigned wholesale to Neverwinter.

## Historical Population and Government

The entry reports **23,192 inhabitants** and names **Lord Nasher Alagondar**.
The number belongs to this historical account; no precise local census date
is attached to it. It is not evidence to replace the current engine's 23,000
residents or Neverember leadership. A resemblance between two population numbers
does not establish shared provenance or continuity. [Source][north]

## Water and Named Infrastructure

The warm Neverwinter River is associated with the gardens. The account names
the Dolphin, Winged Wyvern, and Sleeping Dragon bridges. These provide historical
identities only: present condition, dimensions, carrying capacity, water quality,
and supply yield remain unverified. No water or routing inputs were changed.
[Source][north]

## Fifth-edition Institutions

The official [Basic Rules (2014), Appendix C: The Five Factions][factions],
under Lords' Alliance, explicitly includes Neverwinter with Waterdeep and
Silverymoon among the coalition's leading cities. It describes an association
of rulers seeking security and prosperity while prioritizing their individual
settlements. This passage was directly consulted on D&D Beyond, making it a
primary setting reference rather than a fan account or an unexamined citation.

The passage supplies neither an exact in-world year nor Neverwinter's ruler's
name. It supports a fifth-edition institutional connection, not a dated 1492
membership guarantee. Economic relevance is qualitative: an institution concerned
with regional security and prosperity. Inferring guaranteed caravan escorts,
lower tolls, a security multiplier, or additional workers would require separate
evidence and model review. None is applied.

## Engine Record

The [stored settlement](../../faerun/data/store/settlements.json) uses the stable
ID `neverwinter`, population `23000`, region Sword Coast North, zone
`swordcoast_north`, terrain `coast`, port `Sea of Swords`, and `river: true`.
Its ruler is `Lord Protector Neverember`; its description calls the city rebuilt
around its warm river. These are model inputs, not validated by the older account.

Configured industries are `craft: 3.0`, `fish: 2.0`, `glass: 2.0`, `log: 1.0`,
`ship: 2.0`, `smith: 2.0`, `tag_volcanic_ash: 2.0`, `tag_wolfsbane: 2.0`, and
`trade: 2.0`. Specialties are `glassware: 2.0` and `clothing_fine: 1.0`.
Historical glasscraft is qualitatively relevant but does not validate those
weights. The other industries and fine clothing remain unverified by this source,
not disproved.

The [runtime lore catalogue](../../faerun/data/lore.py) separates historical
lore from the fifth-edition Alliance reference and from model context.
No economic catalogue, map, routes, workforce,
or live state was altered; no simulation outputs were measured.

## Discrepancies and Next Leads

- **Modern continuity:** seek late-15th-century published descriptions of rebuilding,
  current businesses, and civic leadership before carrying older details forward.
- **Candidate modern account:** the reviewed Paul Joyce compilation below supplies
  leads, not a verified 1492 snapshot. Resolve its dates and source attribution
  before promoting its harbor, market, or bridge claims to runtime lore.
- **Population:** obtain a dated modern figure and its geographic coverage. Do not
  recalibrate the model from the historical 23,192 figure.
- **Glasscraft and horticulture:** verify surviving or restored workshops and
  gardens. Identifying existing capacity is preferable to adding unsupported labor
  or production; no capacity change is proposed yet.
- **Access and water:** verify harbor condition, road connections and river use
  for the relevant era. Named historical bridges are not a current transport graph.

## Follow-up Source Assessment

[Paul Joyce's Neverwinter overview][joyce], published July 30, 2018 and accessed
2026-10-01, is a secondary fan research compilation for a fifth-edition campaign.
It explicitly describes itself as a working article and invites corrections.
It recommends *Neverwinter Campaign Setting* but does not attach sourcebook
pages to the economic and infrastructure claims reviewed here. That recommendation
is not direct consultation of the book or proof of each claim's provenance.

Economically useful leads are an unfrozen river and harbor in winter, markets in
Protector's Enclave, and civic administration at the Hall of Justice. These could
inform seasonal access and the location of existing commercial services if
corroborated. They do not establish year-round freight reliability, quantities,
market staffing, or extra productive capacity. No named operating workshop or
dated modern census was established by this review.

The article requires particular caution for the 1492 baseline:

- Its timeline tentatively places the present around 1491 DR rather than supplying
  a firm reference date for each description.
- It attributes approximately 23,200 residents to Wikipedia without a census date.
  This is not independent evidence of population recovery or a reason to replace
  the model's 23,000 residents.
- Its body dates the Hotenow eruption to 1451 DR, while an image caption says
  1452 DR. This internal discrepancy is retained, not silently reconciled.
- The author explicitly qualifies the rebuilding of two bridges as a belief.
  Their restored condition must not become a verified road or bridge connection.
- Its 1484 DR Chasm-sealing and near-bankruptcy claims lack passage-level
  attribution. They do not justify a fiscal, security, or reconstruction modifier.

**Disposition:** retain the Joyce claims as research leads only. They do not
enter the runtime summary; the separately verified Alliance paragraph above
does not corroborate them. No economic correction, map placement, or transport
change is applied. The next discriminating check is
a dated published account or the preferred wiki's attributed modern infrastructure
passage, especially harbor seasonality and bridge condition.

## Sources

**Directly consulted:** [Realms Helps: The North][north], Sword Coast North /
Important Sites / Neverwinter and surrounding chronology, accessed 2026-10-01.
Unofficial secondary reference; historical, third-edition-style context.
Publication date and exact sourcebook attribution are not established by the
consulted passage. No independently consulted primary publication is claimed.

**Directly consulted primary reference:** [D&D Beyond: Basic Rules (2014),
Appendix C: The Five Factions][factions], Lords' Alliance subsection, accessed
2026-10-01. Official fifth-edition setting text; exact in-world year unstated.
Only the institutional claim above was adopted from this passage.

**Directly consulted for provenance assessment only:** [Paul Joyce: The city of
Neverwinter. Features, Facts & Timeline (Forgotten Realms)][joyce], published
2018-07-30, accessed 2026-10-01. Secondary fan compilation mixing historical
material with a tentative circa-1491 DR present; no primary publication was
independently consulted. Claims above remain unverified leads, not adopted lore.

**Attempted again, unavailable:** [Forgotten Realms Wiki: Neverwinter][frwiki],
2026-10-01; fetch returned an advertising redirect and normal browser access
displayed a security-verification page. Not used as evidence. The D&D Beyond
[Lost Mine of Phandelver introduction][lmop] redirected to an unavailable
promotion/claim page on the same date; no adventure passage was consulted.

[north]: https://www.realmshelps.net/faerun/north.shtml
[frwiki]: https://forgottenrealms.fandom.com/wiki/Neverwinter
[joyce]: https://www.pauljoyce.co.uk/2018/neverwinter-city-facts-features-timline-dnd-forgotten-realms/
[factions]: https://www.dndbeyond.com/sources/dnd/basic-rules-2014/appendix-c-the-five-factions
[lmop]: https://www.dndbeyond.com/sources/dnd/lmop/introduction