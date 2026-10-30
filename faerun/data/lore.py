"""Reviewed canon summaries, separate from economy inputs and estimates."""

LORE_SOURCE_POLICY = {
    "preferred_source": "Forgotten Realms Wiki",
    "url": "https://forgottenrealms.fandom.com/",
    "kind": "secondary",
    "role": "canonical_lore_reference",
    "usage": "Supplement missing location information with reviewed, cited lore; do not overwrite economy inputs or outputs.",
    "conflicts": "Prefer directly verified published sources for the applicable era; retain unresolved conflicts and date qualifications.",
    "retrieval": "Curated local summaries, not automatic live retrieval. Unreviewed locations remain unresearched.",
}

LORE = {
    "neverwinter": {
        "status": "researched",
        "paragraphs": [
            "Historical reference only: Realms Helps' The North describes Neverwinter under Lord Nasher Alagondar as a city known for decorative glass lamps, precision water clocks, and jewelry, with gardens on the warm river supplying summer fruit and winter flowers, and the Dolphin, Winged Wyvern and Sleeping Dragon bridges. The historical entry reports 23,192 inhabitants. Its third-edition-style statistics indicate a late-14th-century snapshot, and none of it proves that the same workshops, gardens, bridges or population exist in 1492 DR.",
            "The Forgotten Realms Wiki places Neverwinter on the High Road between Leilon and Port Llast, with the Neverwinter Wood and the volcano Mount Hotenow to the east. The river, warmed by fire elementals under the volcano, keeps river and harbour ice-free in winter. In the mid to late 14th century DR the city handled much of the mining trade from dwarf and gnome outposts in the Underdark through its warehouses, had a large fishing economy and traded timber from the Neverwinter Wood; its water clocks, multicoloured glass lamps and fine jewellery were sold across Faerun, mostly through Waterdeep's merchants, and hothouse gardens supplied fruit to the markets. The Alagondar line ruled, with a standing force of 400 Graycloaks and a navy.",
            "The eruption of Mount Hotenow in 1451 DR destroyed most of the city, killed the Alagondar family and halted trade. From 1467 DR Dagult Neverember, then Open Lord of Waterdeep, styled himself Lord Protector and brought workers and Mintarn mercenaries to rebuild; in 1479 DR the Winged Wyvern was the only bridge in use. Around 1491 DR merchants from north and south were returning, Neverember was forming a trading alliance with the restored Gauntlgrym, and without guilds restricting trade newcomers could open businesses freely, although after losing Waterdeep in 1489 DR he barred new guilds and limited existing ones. Walls and neighbourhoods around the Chasm, sealed around 1484 or 1485 DR, were still in ruins in 1491 DR; a local watch, the Wintershield Watchmen, was added in the late 1480s DR. No population figure was found for the rebuilt city. These describe trade character, not volumes or prices.",
            "The official fifth-edition Basic Rules, Appendix C, identifies Neverwinter alongside Waterdeep and Silverymoon as a leading city in the Lords' Alliance, a coalition of rulers pursuing their settlements' security and prosperity. This directly consulted institutional reference does not name Neverwinter's ruler, date its membership to 1492 DR, or establish guaranteed caravan protection, staffing, tolls, or trade volumes.",
        ],
        "sources": [{
            "title": "Realms Helps: The North - Sword Coast North, Neverwinter",
            "url": "https://www.realmshelps.net/faerun/north.shtml",
            "accessed": "2026-10-01",
            "kind": "secondary",
        }, {
            "title": "D&D Beyond: Basic Rules (2014), Appendix C: The Five Factions - Lords' Alliance",
            "url": "https://www.dndbeyond.com/sources/dnd/basic-rules-2014/appendix-c-the-five-factions",
            "accessed": "2026-10-01",
            "kind": "primary",
        }, {
            "title": "Forgotten Realms Wiki: Neverwinter",
            "url": "https://forgottenrealms.fandom.com/wiki/Neverwinter",
            "accessed": "2026-10-13",
            "kind": "secondary",
        }, {
            "title": "Forgotten Realms Wiki: Category: Inhabitants of Neverwinter",
            "url": "https://forgottenrealms.fandom.com/wiki/Category:Inhabitants_of_Neverwinter",
            "accessed": "2026-10-13",
            "kind": "secondary",
        }, {
            "title": "Forgotten Realms Wiki: Map:Neverwinter",
            "url": "https://forgottenrealms.fandom.com/wiki/Map:Neverwinter",
            "accessed": "2026-10-13",
            "kind": "secondary",
        }],
        "era_note": "Historical Nasher-era account, consistent with a circa-1372 DR / third-edition regional snapshot inferred from surrounding chronology and rules notation; the local census date is not explicit. Not verified for 1492 DR. The 14th-century trade, crafts and government come from 1st- to 3rd-edition books cited by the Forgotten Realms Wiki (Cyclopedia of the Realms, 1987; Waterdeep and the North, 1987; The Savage Frontier, 1988; Volo's Guide to the North, 1993). The destruction and rebuilding come from Neverwinter Campaign Setting (2011, set in 1479 DR), and the circa 1491 DR state from Sword Coast Adventurer's Guide (2015), Storm King's Thunder (2016) and Princes of the Apocalypse (2015). No population figure exists for the rebuilt city; the 23,192 figure predates the 1451 DR eruption and the engine's 23,000 is a gazetteer estimate. Whether the glass lamp, water clock and jewellery crafts were restored, and whether the Gauntlgrym alliance was in force in 1492 DR, are not verified. Underlying publications were not independently consulted. The Lords' Alliance paragraph instead comes from direct consultation of the official fifth-edition Basic Rules (2014) on D&D Beyond; its passage supplies no exact in-world date.",
    },
    "triboar": {
        "status": "researched",
        "paragraphs": [
            "Triboar is a prosperous trading town and frontier crossroads in the Dessarin Valley, where the Evermoor Way crosses the Long Road, nicknamed the Town Where Only Gwaeron Sleeps after a grove to the west where the god of rangers is said to sleep. It stands on flat, fertile land about 60 miles west of Yartar; in 1358 DR a wagon took about 13 days to reach Waterdeep and 2 to reach Yartar. Sources give about 2,500 inhabitants in 1357, 1368 and 1370 DR; by the late 15th century DR nearly half the residents lived on outlying farms and ranches.",
            "Its trade character is wagons, caravan services and guides, horses and cattle, forged ironware and leather goods; the infobox lists caravan supplies, horses, leatherwork, ironware and wagons as exports. In the 14th century DR Skulner Wainwright built the valley's finest wagons, ranches west of town bred riding and draft horses, mules and ponies, two smithies sold metalwork across the North, and hired guides charged 7 gp a day. After 1485 DR the businesses include Wainwright's Wagons, Othovir's Harness Shop (engraved elk-skin harness), Foehammer's Forge, Uldinath's Arms, Happy Horse Ranch, Merivold Pony Park, the Cart and Coin caravan outfitter, the Triboar Travelers wagon company, the Lionshield Coster's Lion's Share (run by Narth Tezrin and Alaestra Ulgar), an apothecary and inns including Northshield House under Urgala Meltimer. These describe trade character, not output volumes or prices.",
            "An elected Lord Protector commands the militia and rules by decree, aided by a mounted patrol called the Twelve. Faurael Blackhammer held the office for about three decades until his death in 1369 DR, Jalimin Frindos by 1370 DR, and Darathra Shendrel, a retired adventurer and secret Harper, by 1491 DR. After 1485 DR fire giants attacked the town and were driven off; Harpers and Zhentarim were both active there around 1491 DR.",
        ],
        "sources": [{
            "title": "Forgotten Realms Wiki: Triboar",
            "url": "https://forgottenrealms.fandom.com/wiki/Triboar",
            "accessed": "2026-10-08",
            "kind": "secondary",
        }, {
            "title": "Forgotten Realms Wiki: Category: Inhabitants of Triboar",
            "url": "https://forgottenrealms.fandom.com/wiki/Category:Inhabitants_of_Triboar",
            "accessed": "2026-10-08",
            "kind": "secondary",
        }, {
            "title": "Forgotten Realms Wiki: Map:Triboar (15th Century DR)",
            "url": "https://forgottenrealms.fandom.com/wiki/Map:Triboar_(15th_Century_DR)",
            "accessed": "2026-10-08",
            "kind": "secondary",
        }, {
            "title": "Forgotten Realms Wiki: Wainwright's Wagons",
            "url": "https://forgottenrealms.fandom.com/wiki/Wainwright%27s_Wagons",
            "accessed": "2026-10-08",
            "kind": "secondary",
        }, {
            "title": "Power Score: Dungeons & Dragons - A Guide to Storm King's Thunder (Sean McGovern)",
            "url": "https://thecampaign20xx.blogspot.com/2016/08/dungeons-dragons-guide-to-storm-kings.html",
            "accessed": "2026-10-01",
            "kind": "secondary",
        }],
        "era_note": "Population, guides, wagon prices, the earlier Lords Protector and the export list come from 1st- and 2nd-edition books (Waterdeep and the North, 1987; The Savage Frontier, 1988; Volo's Guide to the North, 1993; The North, 1996), 1357 to 1370 DR. The operating businesses and most named people come from Storm King's Thunder (2016), set after 1485 DR without an exact year, and Darathra Shendrel's 1491 DR date from Princes of the Apocalypse (2015). No population figure later than 1370 DR was found; the engine's 2,500 residents matches the 14th-century count but is a gazetteer estimate. The wiki's distance of 200 miles from Red Larch conflicts with other figures. Business continuity and the ruler are not verified for 1492 DR itself. Underlying publications were not independently consulted; the Power Score guide is kept from the earlier limited review and its names are consistent with the wiki.",
    },
    "griffon_s_nest": {
        "status": "researched",
        "paragraphs": [
            "Griffon's Nest is a permanent settlement of the Uthgardt Griffon tribe in the Surbrin Hills of the Savage Frontier, northeast of Longsaddle, with Shining Creek farther east. Its inhabitants are described as human Uthgardt who worship Uthgar. The site began as a camp of half-orc bandits under Azglyn, whom the Uthgardt destroyed before settling there.",
            "The latest documented snapshot is 1485 DR: a hamlet of approximately 300 inhabitants under Great Chief Halric Bonesnapper, marked by poverty, hostility to outsiders and small, bold raids on homesteads in the Dessarin Valley. Halric receives other chieftains in his longhouse and fears the tribe has lost Uthgar's favour. This is the closest documented account before the project's 1492 DR planning baseline, not proof of unchanged conditions in 1492.",
            "Historical notes: Kralgar Bonesnapper became chief in 1348 DR and made the tribe the most educated, skilled and organized of the Uthgardt, open to outside trade while he planned to conquer a great city of the North. The article records 900 residents in both 1358 and 1366 DR, then 6,713 in 1372 DR during the settlement's prosperous small-city period, when un-allied clans joined the tribe. Kralgar was later killed by orcs and the settlement declined under his heirs. The article calls Halric Kralgar's great-grandson; Halric's own page calls him the grandson. Chief Targ Keifer is separately named circa 1484 DR, when he discussed an alliance with Nesme and, with his son Keyl, aided the Companions of the Hall; the source leaves the relationship between the Targ and Halric dates unresolved.",
            "The infobox trade summary, cited to 1358 to 1366 DR sources, lists steel weapons as imports and woven rush goods, cane baskets, and trunks as exports. These details do not establish current output, trade volumes, or named operating businesses in the later, more isolated hamlet, and no business is named for any period.",
            "The mid-14th-century settlement had approximately twenty thatched wood-and-earth huts, a central longhouse, two warehouses, a log palisade hung with enemies' heads, and roughly a dozen hillside farms. These are historical building counts, not a surveyed later layout. Adalfus Stormgatherer is named as a shaman under Kralgar. The tribe's ancestral mound in 1372 DR was Shining White.",
        ],
        "sources": [{
            "title": "Forgotten Realms Wiki: Griffon's Nest",
            "url": "https://forgottenrealms.fandom.com/wiki/Griffon%27s_Nest",
            "accessed": "2026-10-21",
            "kind": "secondary",
        }, {
            "title": "Forgotten Realms Wiki: Halric Bonesnapper",
            "url": "https://forgottenrealms.fandom.com/wiki/Halric_Bonesnapper",
            "accessed": "2026-10-21",
            "kind": "secondary",
        }, {
            "title": "Forgotten Realms Wiki: Kralgar Bonesnapper",
            "url": "https://forgottenrealms.fandom.com/wiki/Kralgar_Bonesnapper",
            "accessed": "2026-10-21",
            "kind": "secondary",
        }, {
            "title": "Forgotten Realms Wiki: Targ Keifer",
            "url": "https://forgottenrealms.fandom.com/wiki/Targ_Keifer",
            "accessed": "2026-10-21",
            "kind": "secondary",
        }, {
            "title": "Forgotten Realms Wiki: Griffon tribe",
            "url": "https://forgottenrealms.fandom.com/wiki/Griffon_tribe",
            "accessed": "2026-10-21",
            "kind": "secondary",
        }, {
            "title": "Realms Helps: The North (summary of The North: Guide to the Savage Frontier)",
            "url": "https://www.realmshelps.net/faerun/north.shtml",
            "accessed": "2026-10-21",
            "kind": "secondary",
        }],
        "era_note": "Use 1485 DR, the latest documented snapshot before the 1492 DR project baseline (Storm King's Thunder, 2016, pp. 67, 74, 89), while retaining 1358, 1366, and 1372 DR history separately (The Savage Frontier, 1988, pp. 24, 29; Volo's Guide to the North, 1993, pp. 45, 221; The North, 1996, p. 73; Forgotten Realms Campaign Setting, 3rd edition, 2001, p. 169). Approximately 300 residents and Halric Bonesnapper are dated to 1485 and not verified for 1492. Targ Keifer circa 1484 (Rise of the King, 2014, pp. 114, 134) and Halric in 1485 remain an unresolved source qualification, as does whether Halric is Kralgar's grandson or great-grandson. The rush, cane basket and trunk exports date from 1358 to 1366 DR; nothing shows they continued after the decline. The real-world access date is not a setting date. These are reviewed secondary summaries (wiki pages and a fan summary of The North), not independent verification of the cited publications.",
    },
    "phandalin": {
        "status": "researched",
        "paragraphs": [
            "Phandalin is a small frontier village in the Lost Hills of the Sword Mountains, south of Neverwinter Wood and north-east of Leilon, where the road from the High Road toward Triboar fades into the Triboar Trail. The first town prospered in the 10th century DR as a member of Phandelver's Pact, with access to Wave Echo Cave and the Forge of Spells, and was overrun by orcs in 951 DR. A short-lived resettlement worked cold-iron mines before 1374 DR. Settlers from Neverwinter and Waterdeep began rebuilding around 1486 DR, and by 1491 DR the town had about fifty log and flagstone buildings, three deep wells, an apple orchard to the west and the ruined Tresendar Manor to the east. No resident count was found; the building count is not a census.",
            "Its people are farmers, woodcutters, trappers and miners, and most of its wealth comes from mining gold and platinum in the Sword Mountains; the wiki's export list also names timber, skins and cold iron. In 1491 DR the main businesses were Barthen's Provisions (general goods, wagon loading and livestock brokering), the Lionshield Coster's weapons and armour post under Linene Graywind, the Zhentarim-run Phandalin Miner's Exchange under Halia Thornton (which weighs and buys ore and gems, records claims and sells carts and wagons), Edermath Orchard (apples, juice and cider), the Stonehill Inn (a bed 5 sp a night) and the Sleeping Giant tap house. In the early 1490s DR the expected mineral wealth often failed to arrive, the Exchange went months without income, and tourism grew after Volo wrote about the area. These describe trade character, not output volumes or prices.",
            "An annually elected Townmaster, Harbin Wester in 1491 DR, served as judge and record keeper. During the early 1490s DR, after the Redbrand bandits and the white dragon Cryovain, the townsfolk replaced him with a three-member Town Council of Harbin Wester, Sildar Hallwinter and Trilena Stonehill; the year of the change is not given. By 1496 DR Barthen's Provisions had become the Temple of the Coinmaiden, Sharna Quirstiron ran the Miner's Exchange, Acquisitions Incorporated held Tresendar Manor, and the town held its first mayoral election. Those 1496 DR changes come after the planning baseline.",
        ],
        "sources": [{
            "title": "Forgotten Realms Wiki: Phandalin",
            "url": "https://forgottenrealms.fandom.com/wiki/Phandalin",
            "accessed": "2026-10-09",
            "kind": "secondary",
        }, {
            "title": "Forgotten Realms Wiki: Category: Inhabitants of Phandalin",
            "url": "https://forgottenrealms.fandom.com/wiki/Category:Inhabitants_of_Phandalin",
            "accessed": "2026-10-09",
            "kind": "secondary",
        }, {
            "title": "Forgotten Realms Wiki: Map:Phandalin (1491 DR)",
            "url": "https://forgottenrealms.fandom.com/wiki/Map:Phandalin_(1491_DR)",
            "accessed": "2026-10-09",
            "kind": "secondary",
        }, {
            "title": "Forgotten Realms Wiki: Barthen's Provisions",
            "url": "https://forgottenrealms.fandom.com/wiki/Barthen%27s_Provisions",
            "accessed": "2026-10-09",
            "kind": "secondary",
        }, {
            "title": "Forgotten Realms Wiki: Phandalin Miner's Exchange",
            "url": "https://forgottenrealms.fandom.com/wiki/Phandalin_Miner%27s_Exchange",
            "accessed": "2026-10-09",
            "kind": "secondary",
        }],
        "era_note": "The 1491 DR snapshot comes from Lost Mine of Phandelver (2014), which the wiki dates to 1491 DR despite a conflicting 1481 DR implication; gold and platinum come from Dragon of Icespire Peak (2019) and the council and tourism from In Volo's Wake (2016), both early 1490s DR without an exact year. Acquisitions Incorporated (2019) is dated 1496 DR by the wiki from a creator statement, after the baseline. Cold iron, skins and timber in the export list come from the video game Neverwinter Nights 2: Storm of Zehir (first resettlement, before 1374 DR). No population figure was found; the engine's 500 residents is a gazetteer estimate. The ruler in 1492 DR (Townmaster or council) and the operation of the 1491 DR businesses in 1492 DR itself are not verified. Underlying publications were not independently consulted.",
    },
    "waterdeep": {
        "status": "researched",
        "paragraphs": [
            "Waterdeep occupies a deep-water harbor on the Sword Coast, with the city spreading around Mount Waterdeep. Its waterfront and named wards give it the character of a metropolis assembled from distinct neighborhoods rather than a single market town.",
            "Its commercial importance reaches well beyond the harbor. The Trade Way, Long Road, and High Road connect maritime traffic with inland caravans and the northern hinterlands, making Waterdeep a meeting point for goods arriving from several directions.",
        ],
        "sources": [{
            "title": "Forgotten Realms Wiki: Waterdeep",
            "url": "https://forgottenrealms.fandom.com/wiki/Waterdeep",
            "accessed": "2026-09-11",
            "kind": "secondary",
        }],
        "era_note": "The source combines multiple editions and historical periods. This geographic overview is not a verification of every detail in 1492 DR; no direct Volo attribution is claimed.",
    },
    "hlondeth": {
        "status": "researched",
        "paragraphs": [
            "Hlondeth, the City of Serpents, is a walled city-state on the Churning Bay of the Vilhon Reach's northern shore, opposite Sespech, with the volcanic Mount Ugruth close by. Its territory reaches about 50 miles from the city and holds roughly a dozen villages and numerous vineyards. That describes territory, not modeled farmland or separate village markets.",
            "The city is built largely of emerald-hued marble from nearby quarries, and the wiki calls it one of the busiest ports in the Reach, carrying goods into southern Turmish and trading with the Shining Plains. Listed exports include green marble, basalt, statuary, mosaic tiles, tough textiles, aloe-based liniments, seafood and wines; listed imports include Sespechian wine, perfume, herbs, spices, poisons, timber, weapons and slaves. Several trade items come from a 2022 Ed Greenwood social-media post rather than a sourcebook. None of this establishes volumes or prices.",
            "House Extaminos, a family of yuan-ti blood, rules the city, which won independence from Chondath in 614 DR; Dediana Extaminos is matriarch in the early 1370s DR. The only population given, 453,600 in 1372 DR, covers the city and its environs, not the city alone. Residents are described as fearing birds of prey and giant birds, which sits awkwardly with any modeled gryphon eyrie but does not by itself rule one out.",
        ],
        "sources": [{
            "title": "Forgotten Realms Wiki: Hlondeth",
            "url": "https://forgottenrealms.fandom.com/wiki/Hlondeth",
            "accessed": "2026-10-03",
            "kind": "secondary",
        }],
        "era_note": "Mixed-edition article; most detail dates from 1357 to 1373 DR (The Vilhon Reach, 1996; Forgotten Realms Campaign Setting 3rd edition, 2001; Serpent Kingdoms, 2004). It has no history after 1373 DR, so ruler, population and trade are not verified for 1492 DR. The 453,600 figure covers city and environs; the engine's 60,000 residents is a user-selected planning scenario. Underlying publications were not independently consulted.",
    },
    "arrabar": {
        "status": "researched",
        "paragraphs": [
            "Arrabar, capital of Chondath, is a sprawling port metropolis on the south-eastern shore of the Vilhon Reach, laid out in Port, Warehouse, Merchants and Living districts around the Governor District and the gold-domed Generon palace. Canals honeycomb the Port District and run to a turning basin. Only a few Reach harbors, Arrabar's and Hlath's among them, were deep enough for deep-draft ships.",
            "The city stands at the end of the Golden Road and the Emerald Way, and its people worked in trade, crafting, fishing and mercenary companies. Lumber is listed as an export; Mulhorandi ale, Tashalaran coffee, Tethyrian tea and peppers appear among imports. Sea trade with Cormyr is traced back to 389 DR. These describe the city's trade character, not volumes.",
            "The wiki gives 5,000 residents in 1357 DR and 61,012 in 1372 DR, the latter citing the third-edition campaign setting; Lord Eles Wianar ruled around 1372 DR. The Spellplague of 1385 DR ruined Chondath and seemingly destroyed Arrabar, and the Chondath article adds that most of the country was exchanged with Shyr of Abeir in 1386 DR. After the Second Sundering the land was healed, and by the late 15th century DR Arrabar was back on the map as a port stop for travelers across the Reach and the Golden Road.",
        ],
        "sources": [{
            "title": "Forgotten Realms Wiki: Arrabar",
            "url": "https://forgottenrealms.fandom.com/wiki/Arrabar",
            "accessed": "2026-10-03",
            "kind": "secondary",
        }, {
            "title": "Forgotten Realms Wiki: Chondath",
            "url": "https://forgottenrealms.fandom.com/wiki/Chondath",
            "accessed": "2026-10-03",
            "kind": "secondary",
        }],
        "era_note": "Most detail is late 14th century (1357 to 1373 DR). The late-15th-century restoration rests on one source cited by the wiki, the Adventurers League adventure Foreign Affairs (2020), which confirms an operating port but gives no population, ruler or industry; those are not verified for 1492 DR. The engine's 61,012 residents adopts the 1372 DR count as a planning scenario. Underlying publications were not independently consulted.",
    },
    "amphail": {
        "status": "researched",
        "paragraphs": [
            "Amphail is a village on the Long Road between Waterdeep and Red Larch, about three days' ride north of Waterdeep. It sits on the western edge of the Dessarin Valley, where a 5th-edition source lists it among the valley's villages. It is named for Amphail the Just, an early warlord of Waterdeep who held estates there. It keeps no standing militia and relies on Waterdhavian guards who patrol from Rassalantar.",
            "Its main trade is growing food for Waterdeep, and it is known for its horses, including Amphail grays and glossy black chargers. Wealthy landowners do most of the breeding; the Roaringhorn family of Waterdeep is the largest breeder, with the Amcathra, Ilzimmer, Jhansczil and Tarm families and several individual breeders. The Eagleshield family make tack and treat sick animals, and the Stag-Horned Flagon brews a dark barley beer and a spicy purple mushroom wine. These describe the village's trade character, not output volumes or prices.",
            "A 3rd-edition source gives 850 inhabitants, 600 in the village and 250 on outlying farms, with Chauntea as the main deity. Briiathor Alougarr was Lord Warder in 1372 DR and Dauner Ilzimmer held the post in 1485 DR. The Stag-Horned Flagon, the village tavern, is still operating around 1490 DR under Arleosa Starhenge. Other named inns, a festhall, a smithy and a dozen shops come mostly from 2nd-edition material and are not confirmed as operating in 1492 DR.",
        ],
        "sources": [{
            "title": "Forgotten Realms Wiki: Amphail (village)",
            "url": "https://forgottenrealms.fandom.com/wiki/Amphail_(village)",
            "accessed": "2026-10-04",
            "kind": "secondary",
        }, {
            "title": "Forgotten Realms Wiki: Dessarin Valley",
            "url": "https://forgottenrealms.fandom.com/wiki/Dessarin_Valley",
            "accessed": "2026-10-04",
            "kind": "secondary",
        }, {
            "title": "Forgotten Realms Wiki: Stag-Horned Flagon",
            "url": "https://forgottenrealms.fandom.com/wiki/Stag-Horned_Flagon",
            "accessed": "2026-10-04",
            "kind": "secondary",
        }],
        "era_note": "Trade, breeders and businesses come from Volo's Guide to the North (1993) and The North (1996), and the 850 population from the Environs of Waterdeep web enhancement (2006), all late 14th century DR. Only the 1485 DR Lord Warder, Dauner Ilzimmer, the Dessarin Valley placement (Princes of the Apocalypse, 2015, p. 31, via the Dessarin Valley article) and the Stag-Horned Flagon's circa 1490 DR owner (Storm King's Thunder, p. 72) come from 5th-edition sources. The leader, population and businesses are not verified for 1492 DR. The engine's 850 residents adopts the circa 1372 DR count (village plus farms) as a planning scenario. Underlying publications were not independently consulted.",
    },
    "goldenfields": {
        "status": "researched",
        "paragraphs": [
            "Goldenfields, the Granary of the North, is a walled abbey-farm of Chauntea on raised ground in the Dessarin Valley, on the western side of the River Dessarin south of Bargewright Inn. It was founded around 1355 DR by Tolgar Anuvien, a Chauntean cleric and retired adventurer from Waterdeep, and grew from about 20 to nearly 30 square miles by 1370 DR. A mortared stone wall about 60 feet high on the outside encloses it, with towers and barracks every mile or two.",
            "It is the North's foremost grower of food. Its farms grow grain including rice, maize, barley and hops; it has apple and orange orchards and herb and vegetable gardens, and keeps oxen and cattle in paddocks with smaller pens of sheep, pigs, turkeys and chickens. Much of Waterdeep's food and that of nearby settlements comes from Goldenfields, which a 3rd-edition source says gives it without seeking payment, in Chauntea's honour. The Goldengulp Brewery, with about 60 workers, brews the namesake beer served at the inn, Northfurrow's End. These describe the abbey's trade character, not output volumes or prices.",
            "Sources give over 5,000 residents around 1366 DR, 7,988 in 1372 DR and about 5,000 in 1491 DR. Ellardin Darovik is abbot in 1491 DR, the Emerald Enclave has gained influence alongside the Chauntean clergy, and a castellan appointed by the Lords of Waterdeep holds a largely ceremonial command. In the late 15th century DR, after the War of the Silver Marches, the hill giant chief Guh and allied goblinoids attacked the abbey.",
        ],
        "sources": [{
            "title": "Forgotten Realms Wiki: Goldenfields",
            "url": "https://forgottenrealms.fandom.com/wiki/Goldenfields",
            "accessed": "2026-10-05",
            "kind": "secondary",
        }, {
            "title": "Forgotten Realms Wiki: Goldengulp Brewery",
            "url": "https://forgottenrealms.fandom.com/wiki/Goldengulp_Brewery",
            "accessed": "2026-10-05",
            "kind": "secondary",
        }, {
            "title": "Forgotten Realms Wiki: Ellardin Darovik",
            "url": "https://forgottenrealms.fandom.com/wiki/Ellardin_Darovik",
            "accessed": "2026-10-05",
            "kind": "secondary",
        }],
        "era_note": "Founding, early size and the 5,000 (circa 1366 DR) figure come from Volo's Guide to the North (1993); the 7,988 figure and the free gift of food from the Forgotten Realms Campaign Setting (2001), both 14th century DR. Crops, livestock, the brewery, the abbot and the giant attack come from Storm King's Thunder (2016), set in the late 1480s or early 1490s DR, and the 1491 DR population of about 5,000 from Princes of the Apocalypse (2015), p. 33. None is verified for 1492 DR itself, and the state of the abbey after Guh's attack is unknown. A plague around 1395 DR is uncited on the wiki and is left out. The engine's 3,000 residents is a gazetteer estimate, not a sourced figure. Underlying publications were not independently consulted.",
    },
    "red_larch": {
        "status": "researched",
        "paragraphs": [
            "Red Larch is a waystop village on the Long Road about seven days' ride north of Waterdeep, on a low ridge at the western edge of the Dessarin Valley. Trails meet there from Bargewright Inn (the Cairn Road), from the logging thorp of Kheldell, and from ruined keeps in the hills. It is named for a stand of red larches the first settlers felled, and they chose the site for a spring-fed pond that could water draft animals. Sources give about 600 inhabitants; the year of that figure is not stated.",
            "Its trade character is stone, harness, wagons and poultry. Around 1366 DR the dwarf Jarth Oneshield ran four quarries in the hills east of town, three harness-makers worked there, Thelorn's Safe Journeys sold wagons, and Mhandyvver's Poultry sold fowl, eggs and chicks; there were farmers' and cattle markets, and Kheldell's loggers sold timber in the town. The village is known for crumblecake, a plain, filling loaf of nuts, chickpeas, roots and fowl scraps. These describe trade character, not output volumes or prices.",
            "In 1491 DR Red Larch has a constable, Harburk Tuthmarillar, but no named lord. Businesses then operating include Mhandyvver's Poultry under Minthra Mhandyvver, Chansyrl Fine Harness, Thelorn's Safe Journeys and its rival Waelvur's Wagonworks, Luruth's Tannery, a stoneworks, a smithy, a bakery, a butcher, Ironhead Arms (opened 1488 DR), the Swinging Sword inn and the Helm at Highsun tavern. That year a secret society of leading merchants, the Believers, was drawn toward the Cult of the Black Earth, committed murders and was exposed and shunned.",
        ],
        "sources": [{
            "title": "Forgotten Realms Wiki: Red Larch",
            "url": "https://forgottenrealms.fandom.com/wiki/Red_Larch",
            "accessed": "2026-10-06",
            "kind": "secondary",
        }, {
            "title": "Forgotten Realms Wiki: Category: Inhabitants of Red Larch",
            "url": "https://forgottenrealms.fandom.com/wiki/Category:Inhabitants_of_Red_Larch",
            "accessed": "2026-10-06",
            "kind": "secondary",
        }, {
            "title": "Forgotten Realms Wiki: Mhandyvver's Poultry",
            "url": "https://forgottenrealms.fandom.com/wiki/Mhandyvver%27s_Poultry",
            "accessed": "2026-10-06",
            "kind": "secondary",
        }, {
            "title": "Forgotten Realms Wiki: Believers",
            "url": "https://forgottenrealms.fandom.com/wiki/Believers",
            "accessed": "2026-10-06",
            "kind": "secondary",
        }],
        "era_note": "Quarries, harness-makers, wagons, poultry, markets and crumblecake come from Volo's Guide to the North (1993) and The North (1996), circa 1366 DR; farms north of town from Dragon #300 (2002), circa 1372 DR. The constable, operating businesses and the Believers come from Princes of the Apocalypse (2015), set in 1491 DR, the closest source to the 1492 DR baseline. The 600 population is cited to all three books together, so its year is uncertain; the engine's 1,100 residents is an unsourced gazetteer estimate. Who governs after the Believers fell, and the state of the village in 1492 DR itself, are not verified. Underlying publications were not independently consulted.",
    },
    "daggerford": {
        "status": "researched",
        "paragraphs": [
            "Daggerford is a small walled town and duchy on the Trade Way at the north bank of the Delimbiyr, the Shining River, the largest settlement between Waterdeep and Baldur's Gate. Most of its people live on outlying hamlets, farms and estates rather than inside the walls. Goods pass here between river boats and Trade Way caravans, because the river is too shallow for ships to go further upstream, and rivermen carry passengers downriver to Secomber. It is named for the boy Tyndal, who in 931 DR killed six lizardfolk raiders with a dagger at the crossing; every later duke claimed descent from him.",
            "Its trade character is farming with a craft and river trade. Sources name furs and garments as exports and lumber, from Andalor's Mill in Bowshot, as the import. A twice-a-tenday market, a tannery moved outside the walls in the 15th century DR, and guilds of tanners, leatherworkers, carpenters, animal handlers, farmers and mariners are recorded. Late 15th century DR businesses include Sullerton Shipbuilders (river boats only), Daggerthrust Ales, Miller's Dry Goods (its owner also had three grain mills), Gublin's Cloth & Cordage, Derval's Smithy (weapons and militia metalwork), Cromach's Smithy (tools, horseshoes, wheels), the Sword Coast Traders' Bank and several taverns and boarding houses. These describe trade character, not output volumes or prices.",
            "A Duke or Duchess of Tyndal's line rules with a Council of Guilds of the town's guildmasters. Duke Maldwyn held the title before 1485 DR; after primogeniture was suspended Lady Morwen became duchess, though the succubus Pencheska may have imprisoned her and ruled in her likeness, and a Morwen still ruled in 1489 DR. Daggerford joined the Lords' Alliance before the Second Sundering. Recorded populations rise from 300 in the town in 1347 DR to 891 in 1372 DR and 1,200 in 1485 DR.",
        ],
        "sources": [{
            "title": "Forgotten Realms Wiki: Daggerford",
            "url": "https://forgottenrealms.fandom.com/wiki/Daggerford",
            "accessed": "2026-10-07",
            "kind": "secondary",
        }, {
            "title": "Forgotten Realms Wiki: Category: Inhabitants of Daggerford",
            "url": "https://forgottenrealms.fandom.com/wiki/Category:Inhabitants_of_Daggerford",
            "accessed": "2026-10-07",
            "kind": "secondary",
        }, {
            "title": "Forgotten Realms Wiki: Sullerton Shipbuilders",
            "url": "https://forgottenrealms.fandom.com/wiki/Sullerton_Shipbuilders",
            "accessed": "2026-10-07",
            "kind": "secondary",
        }, {
            "title": "Forgotten Realms Wiki: Map:Daggerford (14th Century DR)",
            "url": "https://forgottenrealms.fandom.com/wiki/Map:Daggerford_(14th_Century_DR)",
            "accessed": "2026-10-07",
            "kind": "secondary",
        }],
        "era_note": "Exports, imports, the founding legend and most guilds come from 2nd-edition books (Under Illefarn, 1987; Volo's Guide to the Sword Coast, 1994; The North, 1996), circa 1347 to 1372 DR. The operating businesses, the tannery move, the rulers Maldwyn and Morwen and the river-to-caravan role come from Scourge of the Sword Coast (2014), set around 1485 DR, and the 1489 DR ruler from the Sword Coast Adventurer's Guide (2015). The infobox cites its population figures as a group, so the book and scope behind 1,200 (1485 DR) are not confirmed; the engine's 900 residents is an unsourced gazetteer estimate. Whether the real Morwen rules, and the state of the town in 1492 DR after the dragon Karrnsyrrl's release around 1489 DR, are not verified. Underlying publications were not independently consulted.",
    },
    "stone_bridge": {
        "status": "researched",
        "paragraphs": [
            "Stone Bridge is an ancient dwarven bridge over the River Dessarin, a single granite arch built by the realm of Besilmer to join the two halves of its lands, and also a temple to Moradin. The wiki, citing Dwarves Deep (1990), gives it as about 2 miles long, 400 feet high and six paces wide with no railings; that size has not been checked against the books. As of 1368 DR it was a place of pilgrimage for dwarves, and with the Halls of the Hunting Axe it was one of the only works of Besilmer still standing.",
            "The bridge carries the Stone Trail, a rough dirt road from Westbridge on the Long Road, a farming village named for its place at the bridge's west side, to Beliard, a cattle-ranchers' trading village where the trail meets the Dessarin Road a few miles to the east. Legend ties the bridge to the death of Besilmer's founder Torhild Flametongue in combat with a hill giant, to the fall of the Ironstar king Daurvos Frostbeard to orcs in 207 DR and the rescue of his clan by an avatar of Moradin, and to the avatar guarding it during the Time of Troubles.",
            "No village, population, ruler, trade or business is recorded at the bridge itself. Its economic role in the sources is a river crossing and a pilgrimage site; the nearby markets, stockyards and warehouses belong to Westbridge and Beliard.",
        ],
        "sources": [{
            "title": "Forgotten Realms Wiki: Stone Bridge",
            "url": "https://forgottenrealms.fandom.com/wiki/Stone_Bridge",
            "accessed": "2026-10-10",
            "kind": "secondary",
        }, {
            "title": "Forgotten Realms Wiki: Stone Trail",
            "url": "https://forgottenrealms.fandom.com/wiki/Stone_Trail",
            "accessed": "2026-10-10",
            "kind": "secondary",
        }, {
            "title": "Forgotten Realms Wiki: Westbridge",
            "url": "https://forgottenrealms.fandom.com/wiki/Westbridge",
            "accessed": "2026-10-10",
            "kind": "secondary",
        }, {
            "title": "Forgotten Realms Wiki: Beliard",
            "url": "https://forgottenrealms.fandom.com/wiki/Beliard",
            "accessed": "2026-10-10",
            "kind": "secondary",
        }, {
            "title": "Forgotten Realms Wiki: Besilmer",
            "url": "https://forgottenrealms.fandom.com/wiki/Besilmer",
            "accessed": "2026-10-10",
            "kind": "secondary",
        }],
        "era_note": "The description, temple and pilgrimage come from Dwarves Deep (1990), circa 1368 DR; the history is legendary (Besilmer founded -4420 DR, Ironstar clan fall 207 DR). Princes of the Apocalypse (2015, circa 1491 DR) and Storm King's Thunder (2016) are cited by the wiki only for the bridge's size and route. Verified for 1492 DR: nothing beyond the bridge standing on the Stone Trail. Not verified: whether the temple is tended or pilgrims still come, and any settlement at the bridge. The engine's 80-person market is a surveyed placeholder, not a sourced village. Underlying publications were not independently consulted.",
    },
    "leilon": {
        "status": "researched",
        "paragraphs": [
            "Leilon is a small mining town and rest stop on the High Road between Neverwinter and Waterdeep, on a shallow mudflat at the edge of the Sea of Swords below the Sword Mountains, with the Mere of Dead Men to the south. In the 14th century DR it was an ally of Waterdeep in the Lords' Alliance under Lord Pelindar Filmarya, with about 3,000 people in 1357 and 1370 DR, an earthen rampart and palisade, and about 200 mounted Lances of Leilon guarding the town and its mines.",
            "Its eastern mines yielded copper, nickel and silver sold to Waterdeep merchants. Sea trade was perilous: a dozen warded barges were poled out to ships and cargo moved by cranes that failed in high winds, so most imports came by caravan from Waterdeep. Gnomes from Ieirithymbul came to trade monthly except in winter. A 1358 DR longship raid burned farms, sank eight of the twelve barges and cost three months of ore.",
            "The Spellplague of 1385 DR broke the wards on Thalivar's tower and the town was abandoned. From 1485 DR Dagult Neverember of Neverwinter had the tower pulled down and the town resettled; about 200 people lived there in 1491 DR under a council loyal to him. The resettled town revived fishing at Quayside and the Fishery, hired out barges at the barge yard, bred giant goats for milk, meat and hair, and had a general store (Torver's Post), a smith's stall, two inns and shrines to Lathander, Tymora and Tyr. Rival cults of Talos and Myrkul then fought the Battle of Leilon over the rebuilt tower.",
        ],
        "sources": [{
            "title": "Forgotten Realms Wiki: Leilon",
            "url": "https://forgottenrealms.fandom.com/wiki/Leilon",
            "accessed": "2026-10-11",
            "kind": "secondary",
        }, {
            "title": "Forgotten Realms Wiki: Category: Inhabitants of Leilon",
            "url": "https://forgottenrealms.fandom.com/wiki/Category:Inhabitants_of_Leilon",
            "accessed": "2026-10-11",
            "kind": "secondary",
        }, {
            "title": "Forgotten Realms Wiki: Pinchwit Wigglehoof",
            "url": "https://forgottenrealms.fandom.com/wiki/Pinchwit_Wigglehoof",
            "accessed": "2026-10-11",
            "kind": "secondary",
        }, {
            "title": "Forgotten Realms Wiki: Fishery (Leilon)",
            "url": "https://forgottenrealms.fandom.com/wiki/Fishery_(Leilon)",
            "accessed": "2026-10-11",
            "kind": "secondary",
        }],
        "era_note": "Mines, exports, caravan imports, barges, defences and the 3,000 population come from Waterdeep and the North (1987) and The North: Guide to the Savage Frontier (1996), 1357 to 1370 DR. Abandonment after 1385 DR, the 1485 DR resettlement, the 1491 DR population of 200 and the council, fishing, goats and businesses come from Storm King's Thunder (2016) and the D&D Essentials Kit adventures (2019), circa 1491 DR. Infobox exports of ore, timber and animal skins come from a video game only. Verified for 1492 DR: nothing; the Battle of Leilon in the early 1490s DR may have changed the town, and whether the copper and silver mines were worked again is not stated. The engine's 900 residents have no source. Underlying publications were not independently consulted.",
    },
    "yartar": {
        "status": "researched",
        "paragraphs": [
            "Yartar is a walled trading city of the Dessarin Valley on the east bank of the River Surbrin, near the Dessarin, where the Evermoor Way between Triboar and Silverymoon crosses the Surbrin by a fortified bridge to the Shield Tower on the west bank. It is a member of the Lords' Alliance and a busy crossroads: rival caravans and river barges pass through day and night, and merchants, smugglers, mercenaries and spies from across the North meet there. It had about 6,000 people in 1366 DR, and by the late 15th century DR it was crowded enough that old buildings were rebuilt up to four storeys.",
            "The city lives by trade and the rivers. Its fishermen land crab, eel, catfish and other catch, sold in the Fishyard market even in deep winter, and it is known for building barges, its listed export. Food is its listed import, and a trade agreement with Goldenfields supplies grain and produce. The Lionshield Coster, a merchant company based in Yartar, ships finished goods such as arms and armour to posts at Phandalin, Nightstone and Triboar. Every three years between Shieldmeets a Hiring Fair north of the city draws thousands seeking work, and the temple of Tymora sponsors a Shieldmeet festival.",
            "Yartar is ruled by a Waterbaron elected for life: Alahar Khaumfros, secretly head of the Kraken Society, until illithids killed him around 1366 DR; Belleethe Kheldorna in 1366 DR; and Nestra Ruthiol, a Tethyrian noblewoman loyal to the Lords' Alliance, around 1491 DR. About 150 mounted Shields of Yartar defend it. The Hand of Yartar thieves' guild, the Kraken Society, the Zhentarim and the Harpers all work in the city; in 1491 DR the Hand stole and auctioned a devastation orb and Lord Khaspere Drylund schemed to become Waterbaron.",
        ],
        "sources": [{
            "title": "Forgotten Realms Wiki: Yartar",
            "url": "https://forgottenrealms.fandom.com/wiki/Yartar",
            "accessed": "2026-10-12",
            "kind": "secondary",
        }, {
            "title": "Forgotten Realms Wiki: Category: Inhabitants of Yartar",
            "url": "https://forgottenrealms.fandom.com/wiki/Category:Inhabitants_of_Yartar",
            "accessed": "2026-10-12",
            "kind": "secondary",
        }, {
            "title": "Forgotten Realms Wiki: Lionshield Coster",
            "url": "https://forgottenrealms.fandom.com/wiki/Lionshield_Coster",
            "accessed": "2026-10-12",
            "kind": "secondary",
        }, {
            "title": "Forgotten Realms Wiki: Fishyard",
            "url": "https://forgottenrealms.fandom.com/wiki/Fishyard",
            "accessed": "2026-10-12",
            "kind": "secondary",
        }],
        "era_note": "The 6,000 population, the Fishyard, the shops and inns, and the Waterbarons Khaumfros and Kheldorna come from Volo's Guide to the North (1993) and The North (1996), 1361 to 1372 DR. The infobox imports and exports, fishing, barge-building, caravan trade, the Hiring Fair and the Shields come from the Sword Coast Adventurer's Guide (2015); the Goldenfields agreement, crowding, Nestra Ruthiol and the 1491 DR events from Princes of the Apocalypse (2015) and Storm King's Thunder (2016), circa 1491 DR. A 1492 DR nautiloid attack comes from a video game only. Verified for 1492 DR: nothing directly; the ruler and population for 1492 DR are not stated. The engine's 3,800 residents have no source. Underlying publications were not independently consulted.",
    },
    "secomber": {
        "status": "researched",
        "paragraphs": [
            "Secomber is a small town on three stone hills on the north bank of the River Delimbiyr where the Unicorn Run joins it, with the dangerous High Moor directly to the south. It was settled in 516 DR by halflings of the Delimbiyr Vale and humans of Delimbiyran on the western ruins of Hastarl, the ancient capital of Athalantar, and creatures loosed from those ruins still draw adventurers. Its people are mostly human with nearly as many halflings, plus some Ironeater dwarves, gnomes and moon elves. The town had 900 people in 1358 and 1367 DR and 1,417 in 1372 DR; The North (1996) splits its 900 into about 200 in the village and 700 in surrounding hamlets.",
            "Farming, fishing and stone-cutting are the main occupations, and locals who know the High Forest hire out as guides and guards. The town is a stop on the Delimbiyr Route between the Trade Way and Loudwater, with the Secomber Trail north-west to Uluvin, and it caters to caravans and to adventurers exploring the High Moor and High Forest. Around 1372 DR ale and Moon Rum from the halfling Moon Mountain Brewery, two days north, were sold there; later sources name a halfling weapon-finishing workshop, a dwarf metal workshop and halfling vineyards making sour vinegar, without dates. Its best-known houses face each other across a muddy crossing at the lowest point of town: the sprawling Seven-Stringed Harp tavern, where bards play for free and the Ballad of the Dream Weaver was first heard, and the Singing Sprite inn, owned by the gnome Windfeather family, one of whom is on duty as innkeeper at any time (1367 DR, Volo's Guide to the Sword Coast).",
            "Around 1367 DR the town was ruled by Lord Traskar Selarn, a ranger who watched over it for the Lords' Alliance; a garrison of about 30 Alliance soldiers held a hilltop fort and the militia numbered over 100. Justice is kept by six to nine elected Rods of Justice and juries of nine landowners, under laws based on Waterdeep's. The sage and alchemist Amelior Amanitas lived in a leaning tower among hillside gardens and lent the town his golems. By 1479 DR the walled town suffered constant hobgoblin raids and left tribute for the Urshani clan, and by about 1491 DR that tribute had left it poor. The raids and tribute are historical descriptions: no tribute amount, 1492 DR rate, or modeled price and security adjustment is established.",
        ],
        "sources": [{
            "title": "Forgotten Realms Wiki: Secomber",
            "url": "https://forgottenrealms.fandom.com/wiki/Secomber",
            "accessed": "2026-10-14",
            "kind": "secondary",
        }, {
            "title": "Forgotten Realms Wiki: Category: Inhabitants of Secomber",
            "url": "https://forgottenrealms.fandom.com/wiki/Category:Inhabitants_of_Secomber",
            "accessed": "2026-10-14",
            "kind": "secondary",
        }, {
            "title": "Forgotten Realms Wiki: Delimbiyr Route",
            "url": "https://forgottenrealms.fandom.com/wiki/Delimbiyr_Route",
            "accessed": "2026-10-14",
            "kind": "secondary",
        }, {
            "title": "Forgotten Realms Wiki: Moon Mountain Brewery",
            "url": "https://forgottenrealms.fandom.com/wiki/Moon_Mountain_Brewery",
            "accessed": "2026-10-14",
            "kind": "secondary",
        }, {
            "title": "Forgotten Realms Wiki: Samril's Fine Blades",
            "url": "https://forgottenrealms.fandom.com/wiki/Samril%27s_Fine_Blades",
            "accessed": "2026-10-14",
            "kind": "secondary",
        }, {
            "title": "Volo's Guide to the Sword Coast (1994), Secomber, pp. 79 to 85",
            "url": "https://housegriffon.com/RPG/Games/DnD/add2/ForgottenRealms/Volo%27s%20Guide%20to%20the%20Sword%20Coast.pdf",
            "accessed": "2026-10-15",
            "kind": "primary",
        }, {
            "title": "The North: Guide to the Savage Frontier (1996), Secomber, pp. 63 to 64, 76",
            "url": "https://housegriffon.com/RPG/Games/DnD/add2/ForgottenRealms/The%20North%20-%20Guide%20to%20the%20Savage%20Frontier.pdf",
            "accessed": "2026-10-15",
            "kind": "primary",
        }],
        "era_note": "Geography, occupations, the garrison, the inns and Lord Traskar Selarn come from The Savage Frontier (1988), Volo's Guide to the Sword Coast (1994, set 1367 DR) and The North (1996), 1358 to 1396 DR; the last two were read directly on 2026-10-15, including the Windfeather innkeepers, the inn prices and the 200 village and 700 hamlet split of the 900 people; the 1,417 population and the caravan and adventurer trade from the 3rd-edition Forgotten Realms Campaign Setting (2001), 1372 DR; the Moon Mountain Brewery from Dragon #299 (2002), circa 1372 DR; the Rods of Justice from Ed Greenwood Presents Elminster's Forgotten Realms (2012), undated; the workshops from Forging the Realms (2013) and the vinegar from Heroes' Feast (2020), both undated. Hobgoblin raids and tribute come from the Forgotten Realms Campaign Guide (2008), 1479 DR, and poverty from Storm King's Thunder (2016), circa 1491 DR. Verified for 1492 DR: nothing; no ruler or population is given after 1372 DR. The engine's 1,300 residents and its gem mining have no source. Underlying publications were not independently consulted.",
    },
    "orlumbor": {
        "status": "researched",
        "paragraphs": [
            "Orlumbor is a small, rocky and barren island city-state in the Sea of Swords, west of the Trollbark Forest between Daggerford and Baldur's Gate and about 300 miles south of Waterdeep. Its town is cut into the rock around a natural harbour facing the mainland, with cave-like buildings linked by tunnels and stairs, and the harbour approach is treacherous, so few outsiders visit. The island was wooded long ago but had been logged bare by 1367 DR. No population figure is recorded.",
            "Its people are goat-herders, fishers and some of the most renowned shipwrights in Faerun. Large yards able to lay the keels of very big ships take most of the Sword Coast's shipbuilding: small merchant vessels take about two months, large trade ships six and warships four or more, and most ocean-going ships of the North have been repaired there at least once. Fish, goats and ships are its exports and timber its import. Local families privately own all docks and warehouses and have resisted Amnian attempts to buy control.",
            "Orlumbor keeps its independence through demand for its shipwrights and Waterdeep's patronage; it fought Mintarn, Luskan, Baldur's Gate and Amn at various times but was a close ally of Baldur's Gate by 1364 DR and is listed among the Lords' Alliance members around 1491 DR. In 1358 DR its leader was Tulgar Wrighttson. Temples of Umberlee (Stormhaven House) and Gond stood there, and in the 14th century DR the mage Delshara Windhair, the Witch of the Waves, drove off raiders from Luskan and the Pirate Isles.",
        ],
        "sources": [{
            "title": "Forgotten Realms Wiki: Orlumbor",
            "url": "https://forgottenrealms.fandom.com/wiki/Orlumbor",
            "accessed": "2026-10-15",
            "kind": "secondary",
        }, {
            "title": "Forgotten Realms Wiki: Category: Inhabitants of Orlumbor",
            "url": "https://forgottenrealms.fandom.com/wiki/Category:Inhabitants_of_Orlumbor",
            "accessed": "2026-10-15",
            "kind": "secondary",
        }, {
            "title": "Forgotten Realms Wiki: Order of Master Shipwrights",
            "url": "https://forgottenrealms.fandom.com/wiki/Order_of_Master_Shipwrights",
            "accessed": "2026-10-15",
            "kind": "secondary",
        }, {
            "title": "Forgotten Realms Wiki: Lords' Alliance",
            "url": "https://forgottenrealms.fandom.com/wiki/Lords%27_Alliance",
            "accessed": "2026-10-15",
            "kind": "secondary",
        }],
        "era_note": "Geography, trade, build times and the exports and imports come from the Forgotten Realms Campaign Set (1987), the 2nd-edition Forgotten Realms Campaign Setting and A Grand Tour of the Realms (1993), circa 1367 DR; the share of Sword Coast shipbuilding from Waterdeep and the North (1987) and City of Splendors (1994), circa 1357 to 1368 DR; Tulgar Wrighttson and the 1358 DR shops from the video game Treasures of the Savage Frontier only; private dock ownership from undated So Saith Ed posts; the Baldur's Gate alliance from Passage to Dawn, 1364 DR. Lords' Alliance membership comes from Storm King's Thunder (2016), circa 1491 DR, and the shipwright reputation from the Sword Coast Adventurer's Guide (2015). Verified for 1492 DR: nothing; no ruler or population is given after 1358 DR. The engine's 3,000 residents have no source. Underlying publications were not independently consulted.",
    },
    "longsaddle": {
        "status": "researched",
        "paragraphs": [
            "Longsaddle is a small, sleepy hamlet on an isolated stretch of the Long Road in the Savage Frontier, east of the Crags and west of the Evermoors. It was founded in 1042 DR by Shardra Harpell, an escaped Calishite slave turned mage, and is home to the Harpells, a large family of eccentric wizards whose spells often misfire, living in the Ivy Mansion on a hill above the village. About 130 people lived in the hamlet and some 1,100 in the surrounding area in 1358 DR; about 1,000 with the countryside were counted in 1368 DR. No later figure is recorded.",
            "Ranchers graze the grassland around the village, and beef and mutton are its recorded exports. Around 1367 DR the Long Road trade supported inns and festhalls (the Gilded Horseshoe, the Harpells' Fuzzy Quarterstaff, the Gambling Golem, the Night Cloak and the rough Horn and Hoof), the Leaping Hooves Trade Stables horse trader, Nalathar's Fine Stirrups & Spurs, a bell-smith, Ostever's Slaughterhouse, the Rolling Wheel outfitters and Sixhorns Select Wares. From the 1360s until 1370 DR Perfectone Mercantile ran a teleport freight service from Longsaddle to cities across Faerun.",
            "A council of elders led by the Harpells governs, and the hamlet is a member of the Lords' Alliance because of them: Ardanac Harpell was spokesman in 1358 and 1370 DR and Dowell Harpell represented Longsaddle on the Alliance council in 1489 DR. Werewolf descendants of Bidderdoo Harpell, the Bidderdoos, lived in the woods nearby by 1479 DR, and the reincarnated Catti-brie studied magic at the Ivy Mansion from 1479 to 1482 DR.",
        ],
        "sources": [{
            "title": "Forgotten Realms Wiki: Longsaddle",
            "url": "https://forgottenrealms.fandom.com/wiki/Longsaddle",
            "accessed": "2026-10-16",
            "kind": "secondary",
        }, {
            "title": "Forgotten Realms Wiki: Category: Inhabitants of Longsaddle",
            "url": "https://forgottenrealms.fandom.com/wiki/Category:Inhabitants_of_Longsaddle",
            "accessed": "2026-10-16",
            "kind": "secondary",
        }, {
            "title": "Forgotten Realms Wiki: Harpell",
            "url": "https://forgottenrealms.fandom.com/wiki/Harpell",
            "accessed": "2026-10-16",
            "kind": "secondary",
        }, {
            "title": "Forgotten Realms Wiki: Perfectone Mercantile",
            "url": "https://forgottenrealms.fandom.com/wiki/Perfectone_Mercantile",
            "accessed": "2026-10-16",
            "kind": "secondary",
        }],
        "era_note": "Population, exports, government and the 1358 DR ruler come from The Savage Frontier (1988) and Volo's Guide to the North (1993), 1358 to 1368 DR; the businesses from Volo's Guide to the North and The North: Guide to the Savage Frontier (1996), circa 1367 DR; Perfectone Mercantile from The North and Cloak & Dagger (2000), 1360s to 1370 DR. Dowell Harpell's role comes from the Sword Coast Adventurer's Guide (2015), 1489 DR, Lords' Alliance membership from Storm King's Thunder (2016), circa 1491 DR, and the Bidderdoos and Catti-brie from the novel The Companions (2013), 1479 to 1482 DR. Verified for 1492 DR: nothing; no population is given after 1368 DR and no business is shown operating near 1492 DR. The engine's 700 residents have no source. Underlying publications were not independently consulted.",
    },
    "port_llast": {
        "status": "researched",
        "paragraphs": [
            "Port Llast is a small town of low stone houses and narrow streets on the High Road north of Neverwinter, on the Sword Coast North. Founded as Grath's Hold by the Northman Grath Erlkar in 127 DR and later called Last Port, it was sacked by orcs in 175 DR, served as Witch-Queen Laeral's capital of Stornanter from 806 to 841 DR, and took its present name after its last noble line, the Adreum family, was killed by its own townsfolk following an orc siege in the late 11th century DR. Around 1365 DR it held about 700 people and was known for skilled stonecutters and an excellent harbour, a small bay sheltered by a high rocky spit.",
            "Stone is its recorded export: the main land industry was stonecutting in quarries on the coastal headlands just south of town. Twelve fishing boats, two in poor repair, worked the harbour around 1365 DR, and by the 1480s DR most of the townsfolk were fishers. The town was once famed for an ale called the finest in the North, but production had stopped by the mid to late 15th century DR. A tanner, Bannaeras Thaelok, ran Thaelok's Fine Leathers in a small bay south of the main harbour in the late 15th century DR.",
            "A First Captain rules: the retired stonemason Haeromos Dothwintyl around 1365 DR until his death fighting sahuagin in 1369 DR, and his descendant Dovos Dothwintyl in 1463 DR. The town was closely allied to Neverwinter and a member of the Lords' Alliance, and around 1365 DR a local militia of 50 was backed by 50 Neverwinter men-at-arms and 30 Alliance troops against Luskan, which coveted the harbour. After the Spellplague of 1385 DR silt filled the harbour, trade died and raids by bandits and sahuagin left only holdouts, until lost districts were retaken and resettled in 1463 DR. Tidescourge Pirates held the town in 1479 DR, drow raiders struck in 1484 DR, and frost giants raided it twice after the War of the Silver Marches of 1485 to 1486 DR.",
        ],
        "sources": [{
            "title": "Forgotten Realms Wiki: Port Llast",
            "url": "https://forgottenrealms.fandom.com/wiki/Port_Llast",
            "accessed": "2026-10-17",
            "kind": "secondary",
        }, {
            "title": "Forgotten Realms Wiki: Category: Inhabitants of Port Llast",
            "url": "https://forgottenrealms.fandom.com/wiki/Category:Inhabitants_of_Port_Llast",
            "accessed": "2026-10-17",
            "kind": "secondary",
        }, {
            "title": "Forgotten Realms Wiki: Haeromos Dothwintyl",
            "url": "https://forgottenrealms.fandom.com/wiki/Haeromos_Dothwintyl",
            "accessed": "2026-10-17",
            "kind": "secondary",
        }, {
            "title": "Forgotten Realms Wiki: Bannaeras Thaelok",
            "url": "https://forgottenrealms.fandom.com/wiki/Bannaeras_Thaelok",
            "accessed": "2026-10-17",
            "kind": "secondary",
        }],
        "era_note": "The 700 population, stone export, stonecutting, fishing fleet, militia and First Captain Haeromos Dothwintyl come from The Savage Frontier (1988), Volo's Guide to the North (1993), City of Splendors (1994) and The North: Guide to the Savage Frontier (1996), circa 1358 to 1369 DR; early history from The Grand History of the Realms (2007); the 1385 DR silting from the Neverwinter Campaign Setting (2011); the 1463 DR resettlement and Dovos Dothwintyl from The Last Threshold (2013); the 1479 and 1484 DR events from Talon of Umberlee (2011) and Night of the Hunter (2014); the fishers majority and frost giant raids from Storm King's Thunder (2016), p. 104; Thaelok's tannery from Forging the Realms (2013). Verified for 1492 DR: nothing directly; the latest facts describe the town just before the planning baseline. No population after 1374 DR was found, and the engine's 800 residents have no source. Underlying publications were not independently consulted.",
    },
    "warlock_s_crypt": {
        "status": "researched",
        "paragraphs": [
            "Warlock's Crypt, also called Warlock's Keep, is a city of undead in the western Troll Hills on the Sword Coast, near the mouth of the Winding Water. It was built from the ruins of Orbedal, a Netherese flying enclave once called Sanctuary, which crashed there when magic failed in Netheril in -339 DR. The lich Larloch, the Shadow King, claimed the ruins months later, and the name is a corruption of Larloch's Crypt and Larloch's Keep. Its towers, shaped like taloned hands in black mail, are joined by narrow bridges without rails over walled gardens and courtyards, and a polluted spring that glows at night rises in the cellars of Larloch's tower.",
            "By 1374 DR about sixty liches lived there, many of them Netherese survivors, with vampires, wraiths, wights and many lesser undead. A troop of trolls guarded the city and undead riders on bonebats hunted travelers. Larloch's first servitor was the archlich Rhaugilath, once Lich-King of Orbedal, who wrote a history of Netheril whose chapters were sent to Candlekeep. Explorers who found the city in 1351 DR carried back a plague that struck Baldur's Gate that year, and around 1366 DR Szass Tam of Thay traded treasures with Larloch for magic items and undead servants.",
            "No living community, market, trade or business is recorded at the crypt. Travelers were warned to stay out of sight of it. The gold and silver the wiki lists as imports and exports belong to ancient Orbedal, which traded the output of the Netherese mining village of Bandor, not to the crypt. Larloch was still active in 1487 DR, when he tried and failed to drain the mythal of Myth Drannor, and after the death curse of about 1489 DR Rhaugilath escaped his control.",
        ],
        "sources": [{
            "title": "Forgotten Realms Wiki: Warlock's Crypt",
            "url": "https://forgottenrealms.fandom.com/wiki/Warlock%27s_Crypt",
            "accessed": "2026-10-18",
            "kind": "secondary",
        }, {
            "title": "Forgotten Realms Wiki: Larloch",
            "url": "https://forgottenrealms.fandom.com/wiki/Larloch",
            "accessed": "2026-10-18",
            "kind": "secondary",
        }, {
            "title": "Forgotten Realms Wiki: Rhaugilath",
            "url": "https://forgottenrealms.fandom.com/wiki/Rhaugilath",
            "accessed": "2026-10-18",
            "kind": "secondary",
        }, {
            "title": "Forgotten Realms Wiki: Troll Hills",
            "url": "https://forgottenrealms.fandom.com/wiki/Troll_Hills",
            "accessed": "2026-10-18",
            "kind": "secondary",
        }, {
            "title": "Forgotten Realms Wiki: Winding Water",
            "url": "https://forgottenrealms.fandom.com/wiki/Winding_Water",
            "accessed": "2026-10-18",
            "kind": "secondary",
        }],
        "era_note": "The description, the sixty liches and the trolls come from the Forgotten Realms Campaign Setting, 2nd edition revised (1993), p. 102, Volo's Guide to the Sword Coast (1994), pp. 49, 63 to 64 and 220 to 221, the 3rd-edition Forgotten Realms Campaign Setting (2001), p. 296, Lords of Darkness (2001), pp. 161 to 162, and Lost Empires of Faerun (2005), pp. 102, 108; Orbedal's history from Netheril: Empire of Magic (1996); the Szass Tam visits from Spellbound (1995) and Volo's Guide to All Things Magical (1996). Larloch's 1487 DR attempt on the Myth Drannor mythal is from The Herald (2014) and Rhaugilath's escape after the death curse from Turn Back the Endless Night (2018). Verified for 1492 DR: nothing directly; Larloch was active in 1487 DR, but the crypt itself is described no later than 1374 DR. No living population is recorded, so the engine's 120 residents are a surveyed-market placeholder copied from Orlumbor at 1/25 of its population. Underlying publications were not independently consulted.",
    },
    "dragonspear_castle": {
        "status": "researched",
        "paragraphs": [
            "Dragonspear Castle is a ruined dwarven fortress built across three low hills on the south-western edge of the High Moor in the Western Heartlands, east of the Trollbark Forest and just north of where the Coast Way joins the Trade Way. The half-dwarf adventurer Daeros Dragonspear came up from the dwarven city of Kanaglym in 1255 DR and built it around the lair of his copper dragon companion Halatathlaer, and for a time it was a refuge for dwarves of the region. Tunnels beneath the keep reach the underground Nepenthe River, the ruins of Kanaglym and the Underdark, and a labyrinth below once held the artifact called the Dragonspear.",
            "In 1290 DR the wizard Ithtaerus Casalia opened a portal to Avernus beneath the castle, tricked Daeros into it and lured rival dragons whose fighting wrecked most of the fortress. Bandits and humanoids followed; hobgoblins raided the Trade Way from it from 1305 DR until expeditions from Waterdeep and Baldur's Gate cleared it in 1315 DR and built the Tempuran temple called the Hold of Battle Lions to guard the portal. Devils took the castle in 1354 DR, causing the First Dragonspear War (1356 DR), and returned under the pit fiend Baazka in the Second Dragonspear War (1363 DR), when a humanoid horde destroyed the Way Inn and attacked Daggerford. In 1368 DR Caelar Argent's Shining Crusade held the castle until a coalition of Baldur's Gate, Waterdeep and Daggerford besieged it.",
            "No living community, market, trade or business is recorded at the castle. Some time before 1479 DR undead led by the boneclaw Born rose from the Nepenthe River, overran the shrine of Tempus and kept the ruin in fog. Around 1484 to 1485 DR a coven of Shar-worshipping vampires, the Szarlnaxi, laired there under the influence of the rakshasa Nadir and briefly reopened the portal to Avernus before Sir Isteval and his companions closed it. Nothing read describes the castle between 1485 and 1492 DR.",
        ],
        "sources": [{
            "title": "Forgotten Realms Wiki: Dragonspear Castle",
            "url": "https://forgottenrealms.fandom.com/wiki/Dragonspear_Castle",
            "accessed": "2026-10-19",
            "kind": "secondary",
        }, {
            "title": "Forgotten Realms Wiki: Szarlnaxi",
            "url": "https://forgottenrealms.fandom.com/wiki/Szarlnaxi",
            "accessed": "2026-10-19",
            "kind": "secondary",
        }, {
            "title": "Forgotten Realms Wiki: Born",
            "url": "https://forgottenrealms.fandom.com/wiki/Born",
            "accessed": "2026-10-19",
            "kind": "secondary",
        }, {
            "title": "Forgotten Realms Wiki: Hold of Battle Lions",
            "url": "https://forgottenrealms.fandom.com/wiki/Hold_of_Battle_Lions",
            "accessed": "2026-10-19",
            "kind": "secondary",
        }, {
            "title": "Forgotten Realms Wiki: Category:Inhabitants of Dragonspear Castle",
            "url": "https://forgottenrealms.fandom.com/wiki/Category:Inhabitants_of_Dragonspear_Castle",
            "accessed": "2026-10-19",
            "kind": "secondary",
        }],
        "era_note": "The site, the three hills and the Coast Way and Trade Way junction come from the Forgotten Realms Campaign Set (1987), Cyclopedia of the Realms, p. 39, and Ghosts of Dragonspear Castle (2013), p. 116; the 1255 to 1368 DR history from Volo's Guide to the Sword Coast (1994), pp. 73 to 75, the Forgotten Realms Campaign Setting, 2nd edition revised (1993), p. 91, Hordes of Dragonspear (1992), The Grand History of the Realms (2007), pp. 127 to 146, Elminster's Ecologies (1995) and the video game Baldur's Gate: Siege of Dragonspear (2016); the undead under Born before 1479 DR from the Forgotten Realms Campaign Guide (2008), p. 36, and the Sword Coast Adventurer's Guide (2015), p. 83; the Szarlnaxi vampires and the reopened portal of about 1485 DR from Ghosts of Dragonspear Castle (2013), pp. 122 to 130. All were cited by the Forgotten Realms Wiki and not independently consulted. Not verified for 1492 DR: no source read describes the castle after about 1485 DR, and no living population, ruler or trade is recorded for any period after 1368 DR.",
    },
    "loudwater": {
        "status": "researched",
        "paragraphs": [
            "Loudwater, the City of Grottos, stands where the Grayflow joins the River Delimbiyr in the Gray Vale (Delimbiyr Vale), with lands claimed for two days' ride up and down the river. The town spreads over both banks around the arching stone Flying Fish Bridge, built by the dwarf Iirikos Stoneshoulder in 149 DR: High Town on the craggy north bank holds the High Lord's Hall, guild halls and the old elven houses, and Low Town on the south bank holds the markets, taverns, workshops, warehouses and a dug-out river harbour used by barges, coracles and fishing skiffs. It is famed as a garden town of vine-covered wood and stone buildings and for its many grottos, and was home to Mielikki's Green Regents. About 4,000 people lived there in 1357 to 1370 DR, almost a quarter of them half-elves; 8,137 were recorded in 1372 DR.",
            "Its people farmed, fished (the river fish szorp was a local staple) and served caravans and riverboats; the Loudwater Vale was known for rich cave-ripened cheeses such as mist cheese, and its hardwoods were carved for a chess set sold by Aurora's Emporium in the 1360s DR. In the 14th century DR it was a key stop on the Delimbiyr Route, with trade running east to Llorkh under tight Zhentarim control, and Jolym's shop sold barrels, kegs and packing crates around 1366 DR. These describe trade character, not volumes or prices.",
            "Trade collapsed after the Spellplague of 1385 DR. By 1479 DR Loudwater was a frontier town of about 2,000, mostly humans and half-elves, behind a stone and timber wall over 20 feet high whose gates charged 5 sp per cart or wagon; it was led by the half-elf warlock Lady Moonfire, with the Loudwater Patrol under Captain Harrowleaf. In the late 1480s DR the retired adventurer Telbor Zazrek ruled as High Lord, secretly a Zhentarim puppet; the cost of living was high and goods not supplied by the Zhentarim were heavily taxed, and refugees from stone giant raids on Llorkh and Orlbar sheltered in riverside warehouses. The town was then largely human. A later Lady of Loudwater is placed around the 1490s DR by comics published in 2025 and 2026, without a year.",
        ],
        "sources": [{
            "title": "Forgotten Realms Wiki: Loudwater",
            "url": "https://forgottenrealms.fandom.com/wiki/Loudwater",
            "accessed": "2026-10-22",
            "kind": "secondary",
        }, {
            "title": "Forgotten Realms Wiki: Category:Inhabitants of Loudwater",
            "url": "https://forgottenrealms.fandom.com/wiki/Category:Inhabitants_of_Loudwater",
            "accessed": "2026-10-22",
            "kind": "secondary",
        }, {
            "title": "Forgotten Realms Wiki: Telbor Zazrek",
            "url": "https://forgottenrealms.fandom.com/wiki/Telbor_Zazrek",
            "accessed": "2026-10-22",
            "kind": "secondary",
        }, {
            "title": "Forgotten Realms Wiki: Jolym",
            "url": "https://forgottenrealms.fandom.com/wiki/Jolym",
            "accessed": "2026-10-22",
            "kind": "secondary",
        }],
        "era_note": "Geography, occupations, the 4,000 population, the Gauntlets and the Loudwater Guard come from Waterdeep and the North (1987), p. 7, The Savage Frontier (1988), p. 30, Volo's Guide to the North (1993), pp. 190 to 191, City of Splendors (1994), pp. 17 to 18, and The North (1996), pp. 61 to 62, 1357 to 1370 DR; the cheeses from Marco Volo: Departure (1994), p. 22, and Aurora's Whole Realms Catalogue (1992), pp. 112, 124; the 8,137 population and racial counts from the Forgotten Realms Campaign Setting, 3rd edition (2001), p. 169, and Legacy of the Green Regent: Extermination (2003), pp. 20 to 21, 1372 DR; the 2,000 population, wall, toll, Lady Moonfire and Harrowleaf from the Forgotten Realms Campaign Guide (2008), 1479 DR; Telbor Zazrek, the Zhentarim taxes, the refugees and the largely human population from Storm King's Thunder (2016), p. 97, late 1480s DR (the infobox dates Telbor to 1491 DR). All were cited by the Forgotten Realms Wiki and not independently consulted. Not verified for 1492 DR: no population figure is given after 1479 DR, and Honor Among Thieves (2023) and The Fallbacks comics (2025 to 2026) are undated within the 1490s DR.",
    },
    "grandfather_tree": {
        "status": "researched",
        "paragraphs": [
            "Grandfather Tree is an arakhor, an elder form of treant, that looks like an enormous gnarled oak more than 350 feet tall and 50 feet across at the base, standing deep in the heart of the High Forest. Two rings of raised earth surround it: four mature oaks on the inner ring mark the quarters of the inner cairn, and the outer ring covers the bones of Uthgardt barbarians, most of them of the Tree Ghost tribe. The gold elves of Aryvandaar summoned it around -12,500 DR to guard the Hall of Mists beneath its roots. Its wards block detection near it and teleportation toward it, speed the healing of its protectors and turn away the evil with bad omens, and it can send out guardian spirits the Uthgardt call tree ghosts. It is hallowed to the northern tribes, to wood elves, satyrs, dryads and treants, and to Eldath, Mielikki, Rillifane Rallathil and Silvanus.",
            "The tree was the ancestral mound of the Blue Bear tribe until the annis Tanta Hagara corrupted it from 1311 DR; the guardian spirits banished the Blue Bears, and the tribesmen who rejected her split off as the Tree Ghosts in 1313 DR. Mintiper Moonsilver found the tree in 1343 DR, and the crippled shaman Chungred Ghostheart, reading his epic Tree Ghosts as a hidden map, led the tribe back to it on Shieldmeet 1368 DR. The tribe built Ghostand, a hamlet raised on platforms in a stand of tall oaks close to the tree, with backing from Alustriel of Silverymoon and help from wild elves; it became a trading place for the folk of the forest. In 1372 DR it held 224 people by one count and more than 350 by another, under Chieftain Gunther Longtooth and the shaman Hala Spiritwalk, with a wood elf envoy and about twenty ceremonial guards. These describe the late 14th century DR; no goods, volumes or prices are recorded.",
            "By the late 15th century DR Uthgardt from other tribes had come to live among the Tree Ghosts as pledged protectors of the tree, and around 1485 DR Great Chief Boorvald Orcbane led the tribe in raids on Iceshield orc settlements along the forest edge. After 1486 DR the Red Tiger tribe began searching for the tree to claim it. The tree itself is a holy site rather than a market, and the population, trade and condition of Ghostand after 1372 DR are not described.",
        ],
        "sources": [{
            "title": "Forgotten Realms Wiki: Grandfather Tree",
            "url": "https://forgottenrealms.fandom.com/wiki/Grandfather_Tree",
            "accessed": "2026-10-23",
            "kind": "secondary",
        }, {
            "title": "Forgotten Realms Wiki: Ghostand",
            "url": "https://forgottenrealms.fandom.com/wiki/Ghostand",
            "accessed": "2026-10-23",
            "kind": "secondary",
        }, {
            "title": "Forgotten Realms Wiki: Tree Ghost tribe",
            "url": "https://forgottenrealms.fandom.com/wiki/Tree_Ghost_tribe",
            "accessed": "2026-10-23",
            "kind": "secondary",
        }, {
            "title": "Forgotten Realms Wiki: Boorvald Orcbane",
            "url": "https://forgottenrealms.fandom.com/wiki/Boorvald_Orcbane",
            "accessed": "2026-10-23",
            "kind": "secondary",
        }],
        "era_note": "The tree's description, wards and history come from The Savage Frontier (1988), pp. 25, 54, The North: Guide to the Savage Frontier (1996), \"The Wilderness\", pp. 19, 31 to 32, 54 to 55, Mintiper's Chapbook parts 8 and 9 (2001), Silver Marches (2002), p. 27, Serpent Kingdoms (2004), pp. 96 to 97, and The Grand History of the Realms (2007), p. 12; Ghostand's 224 residents and racial mix are from Silver Marches, p. 27, and the figure of more than 350 from Mintiper's Chapbook part 8, both 1372 DR; Boorvald Orcbane, the pledged protectors, the post-1370 DR wards and the Red Tiger search are from Storm King's Thunder (2016), pp. 58, 67 to 68, 86 to 87, late 1480s DR. All were cited by the Forgotten Realms Wiki and not independently consulted. Not verified for 1492 DR: no population, ruler or trade is recorded for Ghostand after 1372 DR, and the tribe's leader is dated only to about 1485 DR.",
    },
    "mintarn": {
        "status": "researched",
        "paragraphs": [
            "Mintarn is an island in the Sea of Swords about 400 miles south-west of Waterdeep, with the red dragon Hoondarrh laired on Skadaurak Island to its north-west. It is a free port and a haven that asks no questions and turns no one away: fugitives and pirates do business there, rival parties meet on its neutral ground, and its taverns and festhalls were famous for their food, service and danger. Its people call themselves Tarnians. Seats and sites named by the sources are Castle Mintarn, home of the ruler, the hidden pirate harbour-temple of Umberlee called the Cove of the Queen, and Mintarn Mountain, said to hold a small dwarven population with remnants of Clan Ironstar. No population figure is recorded for any period.",
            "Mintarn is ruled by a tyrant. Tarnheel Embuirhan, a celebrated swordsman, ruled from about 1357 DR with a light hand, ended the island's quarrels with Orlumbor and used force against pirates; later tyrants rose every five or six years but kept the free port. Around 1489 DR the tyrant was Bloeth Embuirhan, thought to be a descendant of Tarnheel, during the island's most prosperous days. Since 896 DR the island has bought Hoondarrh's protection with a large yearly tribute.",
            "Its exports are skilled mercenaries, ships, food and drink: golden Mintarn lager sold along the Sword Coast (served at the Blushing Mermaid in Baldur's Gate), a cold green wine rarely seen off the island, almond brandy (almonds are grown there) and Best Old Mintarn whisky. Rock salt is mined in its northern islands. It imported Moonshae wood and Mabadann oysters from the Shining Sea, shipped live in water-filled barrels. Dagult Neverember, while Open Lord of Waterdeep, invested in a shipbuilding business, training grounds and the White Sails mercenary company, and hired a Mintarn navy for Waterdeep and soldiers for Neverwinter, the latter recorded there in 1479 DR. In the 1480s DR Hoondarrh toppled two towers of Castle Mintarn and raised the tribute; once Neverember lost Waterdeep and replaced his mercenaries, the island feared by 1489 DR that it could no longer pay. These describe trade character, not volumes or prices.",
        ],
        "sources": [{
            "title": "Forgotten Realms Wiki: Mintarn",
            "url": "https://forgottenrealms.fandom.com/wiki/Mintarn",
            "accessed": "2026-10-24",
            "kind": "secondary",
        }, {
            "title": "Forgotten Realms Wiki: Hoondarrh",
            "url": "https://forgottenrealms.fandom.com/wiki/Hoondarrh",
            "accessed": "2026-10-24",
            "kind": "secondary",
        }, {
            "title": "Forgotten Realms Wiki: White Sails",
            "url": "https://forgottenrealms.fandom.com/wiki/White_Sails",
            "accessed": "2026-10-24",
            "kind": "secondary",
        }, {
            "title": "Forgotten Realms Wiki: Salt",
            "url": "https://forgottenrealms.fandom.com/wiki/Salt",
            "accessed": "2026-10-24",
            "kind": "secondary",
        }, {
            "title": "Forgotten Realms Wiki: Category: Inhabitants of Mintarn",
            "url": "https://forgottenrealms.fandom.com/wiki/Category:Inhabitants_of_Mintarn",
            "accessed": "2026-10-24",
            "kind": "secondary",
        }],
        "era_note": "Geography, the free port and Tarnheel Embuirhan come from the Forgotten Realms Campaign Set (1987) and the 2nd-edition Forgotten Realms Campaign Setting (1993), circa 1357 to 1368 DR; the drinks from the Volo's Guides (1993 and 1994), 14th century DR, with the lager also in Murder in Baldur's Gate (2013), circa 1484 DR; ships and Moonshae wood from Moonshae (1987); rock salt from Power of Faerun (2006); the Cove of the Queen from Faiths and Avatars (1996), circa 1369 DR; Bloeth Embuirhan, Neverember's investment, the toppled towers and the tribute crisis from the Sword Coast Adventurer's Guide (2015), pp. 66 to 67, circa 1489 DR; the Mintarn mercenaries in Neverwinter from Dungeon 195 and Storm over Neverwinter, circa 1479 DR. All were cited by the Forgotten Realms Wiki and not independently consulted. Not verified for 1492 DR: no population is given for any period, and no ruler or trade is recorded after about 1489 DR. The engine's 5,000 residents have no source.",
    },
    "luskan": {
        "status": "researched",
        "paragraphs": [
            "Luskan, the City of Sails, is a port at the mouth of the River Mirar on the Sword Coast North, built over the ruins of the older magical city of Illusk. The river splits it into a walled North Bank of warehouses, the Mirabar merchants' fortified compound and the navy's Whitesails Harbor, and a South Bank holding most residents and shops inside a semicircular towered wall, with the Market, the High Captains' Court and Dragon Beach, the original harbour. Five islands lie at the river mouth: Cutlass Island, once the site of the Host Tower of the Arcane, Closeguard Island (Ship Kurth), Blood Island (the garrison), and the uninhabited Fang and Harbor Arm Islands. The city counted about 16,000 people in 1370 DR and 14,173 in 1372 DR, but only about 4,000 in 1480 DR after the Spellplague; no later figure is recorded. Its people were mostly human, with drow present in the late 15th century DR.",
            "Five High Captains, former pirate lords each leading a faction called a Ship, ruled formally while the wizards of the Host Tower held real power until Lord Brambleberry and Captain Deudermont destroyed the tower in 1376 DR; Luskan then became a free port. By 1480 DR it had no working government and gangs held territories. Some time after 1485 DR the five High Captains took up legal sea trade along the Sword Coast, defended the city and raided the island kingdoms to the west, while secretly serving Jarlaxle and Bregan D'aerthe; around 1489 DR the captains of Ships Rethnor, Suljack, Taerl and Baram were Hartouchen Rethnor, Dagmaer Suljack, Throa Taerl and Barri Baram, with Kurth's seat held by the disguised drow Beniago, the First Captain. The Host Tower, a haunted ruin for more than a century, was rebuilt in 1486 DR (1487 DR in one account) and the Arcane Brotherhood returned under the Archmage Arcane Cashaan, promising to stay out of politics.",
            "Luskan was the gateway to the north: a market for ore from the Spine of the World and scrimshaw from the Ten Towns, a trader in Mirabar silver, Lurkwood timber and dwarven-made weapons, and in 1370 DR Mirabar's main shipyard. Southern partners met its ships on neutral water off Mintarn rather than be seen with Luskan. The 1370 DR market sold fresh food, firewood and trinkets by permit only. Weapons are listed as an export, and under Bregan D'aerthe Netherese artifacts went to Menzoberranzan; piracy, smuggling and quiet trades in drugs and slaves ran alongside. These describe trade character, not volumes or prices.",
        ],
        "sources": [{
            "title": "Forgotten Realms Wiki: Luskan",
            "url": "https://forgottenrealms.fandom.com/wiki/Luskan",
            "accessed": "2026-10-25",
            "kind": "secondary",
        }, {
            "title": "Forgotten Realms Wiki: Category: Inhabitants of Luskan",
            "url": "https://forgottenrealms.fandom.com/wiki/Category:Inhabitants_of_Luskan",
            "accessed": "2026-10-25",
            "kind": "secondary",
        }, {
            "title": "Forgotten Realms Wiki: Hartouchen Rethnor",
            "url": "https://forgottenrealms.fandom.com/wiki/Hartouchen_Rethnor",
            "accessed": "2026-10-25",
            "kind": "secondary",
        }],
        "era_note": "Geography, districts, the market, the military and the 16,000 figure come from Volo's Guide to the North (1993), pp. 111 to 130, circa 1370 DR; the 14,173 figure from the 3rd-edition Forgotten Realms Campaign Setting (2001), p. 176; the trade goods from A Reader's Guide to R. A. Salvatore's The Legend of Drizzt (2008), pp. 142 to 143, and Tangled Webs (1998), p. 27; the fall of the Host Tower from The Pirate King (2008); the 1480 DR anarchy and 4,000 figure from Shadowbane (2011); Bregan D'aerthe from Night of the Hunter (2014) and The Companions (2013); the legal sea trade after 1485 DR from Storm King's Thunder (2016), pp. 97 to 98; the circa 1489 DR captains, the rebuilt Host Tower (1486 DR) and Cashaan from the Sword Coast Adventurer's Guide (2015), pp. 17, 95 to 98; the weapons export from Icewind Dale II (2002, video game). All were cited by the Forgotten Realms Wiki and not independently consulted. Not verified for 1492 DR: no population is recorded after 1480 DR and no ruler or trade after about 1489 DR. The engine's 16,000 residents match the 1370 DR figure, not the late 15th century DR city.",
    },
    "nesme": {
        "status": "researched",
        "paragraphs": [
            "Nesme is a walled trading town in the Savage Frontier beside the River Surbrin, with the Lurkwood to the north, Uthgardt lands to the north and west and the troll-haunted Evermoors to the south-east. It grew on the site of Thaurog's Keep, a half-orc bandit hold of 1269 DR, which Algraetha the Enchantress cleared of wyverns and refounded as Nesme in 1307 DR. Silverymoon lies about 165 miles away by barge, and a road runs south to Mornbryn's Shield in the Surbrin Hills. The town stands on the east bank, with a fortified bridge to a stronghold of the Riders of Nesme on the west bank.",
            "A First Speaker ruled with a council dominated by merchants; in 1358 DR the town was a theocracy under Jygil Zelnathra, High Priestess of Waukeen, until an election made Tessarin Alaurun First Speaker. The economy rested on trade, with almost all east and west traffic passing through the town, and its profits went into defence, above all the mounted Riders of Nesme. Around 1371 DR it exported iron ore, steel weapons and armor and was known for its exceptional steel. The town held about 6,000 people, more in the trade season; 1372 DR figures of 6,140 and 1,966 conflict.",
            "A troll army ruined Nesme in 1370 DR; Silverymoon paid for a larger town with a double wall over the winter of 1371 to 1372 DR. In 1484 DR the orcs of Many-Arrows, backed by drow and the white dragon Arauthator, took it under First Speaker Jolen Firth, leaving about 600 survivors as prisoners. The drow later abandoned it, and in 1485 DR the town was a ruin whose rebuilding was blocked by monsters from the Evermoors.",
        ],
        "sources": [{
            "title": "Forgotten Realms Wiki: Nesme",
            "url": "https://forgottenrealms.fandom.com/wiki/Nesm%C3%A9",
            "accessed": "2026-10-26",
            "kind": "secondary",
        }, {
            "title": "Forgotten Realms Wiki: Category: Inhabitants of Nesme",
            "url": "https://forgottenrealms.fandom.com/wiki/Category:Inhabitants_of_Nesm%C3%A9",
            "accessed": "2026-10-26",
            "kind": "secondary",
        }, {
            "title": "Forgotten Realms Wiki: River Surbrin",
            "url": "https://forgottenrealms.fandom.com/wiki/River_Surbrin",
            "accessed": "2026-10-26",
            "kind": "secondary",
        }],
        "era_note": "The founding comes from The Grand History of the Realms (2007), pp. 128 to 134; the 1358 DR theocracy and election from The Savage Frontier (1988), pp. 31, 62; the wall, the 6,000 figure and the trade season from The North (1996), pp. 31 to 32; trade, defence and the 6,140 figure from The City of Nesme (web article, 2001); the 1,966 figure from Silver Marches (2002), p. 24; the exports, steel and 1370 DR sack from Dungeon 144 (2007), pp. 17 to 19; the rebuilding from The Orc King (2007); the 1484 DR fall from Rise of the King (2014); the 1485 DR ruins from Storm King's Thunder (2016), p. 101. All were cited by the Forgotten Realms Wiki and not independently consulted. Not verified for 1492 DR: no source read describes Nesme after 1485 DR, when it was in ruins, so the engine's living town of 1,800 residents is not supported for the planning year. A deep research pass on 2026-10-26 found no official source, novel or designer statement describing Nesme between 1486 and 1492 DR. The east bank and the fortified bridge come from the wiki's River Surbrin article, whose printed source was not traced.",
    },
    "jalanthar": {
        "status": "researched",
        "paragraphs": [
            "Jalanthar is a hamlet on the River Rauvin in the Silver Marches, on the trail between Everlund and Sundabar. The trail runs up the north bank of the Rauvin from Everlund past Lhuvenhead (about forty miles upriver) to Jalanthar, then on through the Moon Pass to Rauvincross, where it crosses the river to Sundabar; a branch to Hilltop leaves it between Lhuvenhead and Jalanthar. The Staunt Pools, deep holes in the river said to hide a freshwater giant squid, lie to the west. The wiki's 1489 DR map describes it as a riverside village at the southern end of the Moon Pass.",
            "Around 1372 DR the hamlet held 226 people, not counting soldiers: humans 89%, lightfoot halflings 6%, half-elves 4%. Most were trappers and hunters who lived by the fur trade and by hiring out as guides, and many had fought orcs and other raiders. A council of elders led by Elder Storn Crommarth ran the village. Its houses were half buried and turfed like green hills against fire, with strong doors against battering. After repeated orc raids it had moved from the south bank of the river to the foothills north of it; the old site, with the Crowing Cockatrice inn (burned three times and known for Jalanthar Amber), was abandoned, and a company of 50 Argent Legion soldiers under Badel Kilmander camped in the old ruins.",
            "Jalanthar's leaders joined the 1369 DR conference in Silverymoon that led to the Silver Marches alliance, but when Luruar was formed the larger cities took away its vote, and it became a protectorate without signatory rights. Blue Bear Uthgardt raided it before 1369 DR, and the barlgura Scauuont terrorized it in 1374 DR. After the War of the Silver Marches a retired ranger of the Emerald Enclave, Quinn Nardrosz, headed the village council and Myles Heldruin kept the Crowing Cockatrice.",
            "The earliest description (Volo's Guide to the North, 1993, set before the 1369 DR conference) puts just over 200 people on the south bank of the Rauvin about halfway between Everlund and Sundabar, in near-ruined buildings with stone foundations and fire-proofed turf roofs. Villagers hired out as guides into the wilderness for about 12 gp a day plus a deposit left with their kin, and the whole village avenged any guide who was cheated or harmed. The Crowing Cockatrice was then a ramshackle fieldstone roadhouse whose taproom served Jalanthar Amber, a very strong local cider, at 4 cp a tankard.",
        ],
        "sources": [{
            "title": "Forgotten Realms Wiki: Jalanthar",
            "url": "https://forgottenrealms.fandom.com/wiki/Jalanthar",
            "accessed": "2026-10-27",
            "kind": "secondary",
        }, {
            "title": "Forgotten Realms Wiki: Trail between Everlund and Sundabar",
            "url": "https://forgottenrealms.fandom.com/wiki/Trail_between_Everlund_and_Sundabar",
            "accessed": "2026-10-27",
            "kind": "secondary",
        }, {
            "title": "Forgotten Realms Wiki: Quinn Nardrosz",
            "url": "https://forgottenrealms.fandom.com/wiki/Quinn_Nardrosz",
            "accessed": "2026-10-27",
            "kind": "secondary",
        }, {
            "title": "Forgotten Realms Wiki: Map: Western Faerun (1489 DR)",
            "url": "https://forgottenrealms.fandom.com/wiki/Map:Western_Faer%C3%BBn_(1489_DR)",
            "accessed": "2026-10-27",
            "kind": "secondary",
        }],
        "era_note": "The description, population, races, economy, council, relocation, inn and Argent Legion company come from Silver Marches (2002), p. 19, circa 1372 DR; the trail from the Silver Marches map and Lhuvenhead's distance from p. 18; the Staunt Pools from p. 20; the 1369 DR conference and lost vote from pp. 99 to 100 and The North (1996), Cities and Civilization, p. 55, which names Speaker Ychram Peregyn of Jalanthar; the Blue Bear raids from Volo's Guide to the North (1993), p. 206; Scauuont from Lost Empires of Faerun (2005), p. 93; Quinn Nardrosz and Myles Heldruin from Storm King's Thunder (2016), p. 94, set after 1485 DR. All were cited by the Forgotten Realms Wiki and not independently consulted. A deep research pass on 2026-10-27 read Volo's Guide to the North, p. 206, in an unofficial online scan for the earliest description, the guide fees and Jalanthar Amber as a strong cider; the 3rd-edition Forgotten Realms Campaign Setting (2001), p. 172, calls it a small town. Not verified for 1492 DR: no population, trade or ruler is recorded after the late 1480s DR, and no source says how the fall of neighbouring Sundabar in the War of the Silver Marches or the end of Luruar in 1488 DR affected it. The engine's 600 residents are not sourced, and its stored position (beside Nesme, 29 miles away) does not match the sources, which put Jalanthar on the River Rauvin between Lhuvenhead and the Moon Pass, east of Everlund.",
    },
    "everlund": {
        "status": "researched",
        "paragraphs": [
            "Everlund is a walled city of merchant traders and caravan companies on the north bank of the River Rauvin in the Silver Marches, about fifty miles south to south-east of Silverymoon. Once a Rauvin crossing used by traders in the days of Delzoun, it was refounded in 515 DR when the folk of Ascalhorn refurbished an old dwarf-keep there (Besander's Blockhouse), and it grew from a fortified trading post and bridgehead into the second largest city of the Silver Marches and one of its most active trading communities. Two bridges, the Knightbridge to the west and the Dwarfbridge to the east, cross the Rauvin, and five gates (clockwise from the north: Silverymoon, Mountain, Upriver, Bridge and Downriver) open from dawn to dusk, with broad straight streets running like spokes to the centre. The Bell Market at the centre, named for the alarm bell beside the barracks, is its economic and social heart.",
            "Everlund is the eastern end of the Evermoor Way, the main trade road from the south and west; a road runs north through the Everlund Pass to Silverymoon and a trail follows the Rauvin east to Sundabar. The Striding Giant Rapids block boats downstream, but the river is navigable about 170 miles upstream to Sundabar. Around 1372 DR the city exported amber, charcoal, furniture, furs, stone, syrup, timber and valuable ores (no ore or syrup is named), and imported ale, armor, cheese, clothing, fruit, grain, sugar, weapons and wine; the sweet strong wine evershimmer is made there too. The city hires mercenaries and adventurers to keep the Evermoor Way safe as far as Calling Horns, and caravans arriving after the gates close stay at inns outside the walls. Its people numbered about 12,000 in the 1350s and 1360s DR, 21,388 in 1372 DR (humans 48%, elves 21%, half-elves 14%, lightfoot halflings 9%, shield dwarves 7%) and about 23,000 in 1479 DR.",
            "For about five centuries a Council of Six Elders has governed the city: the holders of its chief offices (High Captain of the army, High Priest of Corellon Larethian, Keeper of the Bridges, High Sorcerer, Master of the Guilds and an elected Speaker of the Town), led by a First Elder chosen by the others. High Captain Kayl Moorwalker was First Elder in 1372 DR. The Army of the Vale (over 1,300 foot, archers and cavalry in 1372 DR) is quartered in the Great Armory south of the river, and Moongleam Tower, a black stone keep of four joined towers on a knoll near the centre, is a Harper base. In the late 1480s or early 1490s DR the council, then High Captain Horix Zoar, Keeper of the Bridges Kythora Shen, High Sorcerer Vaeril Rhuidhen, Master of the Guilds Boldor Steelshield and Speaker Vatrice Stormwright, voted three to two to withdraw from the Lords' Alliance; the Zoar family had also bought Danivarr's House, one of the city's oldest inns.",
        ],
        "sources": [{
            "title": "Forgotten Realms Wiki: Everlund",
            "url": "https://forgottenrealms.fandom.com/wiki/Everlund",
            "accessed": "2026-10-28",
            "kind": "secondary",
        }, {
            "title": "Forgotten Realms Wiki: Council of Elders",
            "url": "https://forgottenrealms.fandom.com/wiki/Council_of_Elders",
            "accessed": "2026-10-28",
            "kind": "secondary",
        }, {
            "title": "Forgotten Realms Wiki: Danivarr's House",
            "url": "https://forgottenrealms.fandom.com/wiki/Danivarr%27s_House",
            "accessed": "2026-10-28",
            "kind": "secondary",
        }, {
            "title": "Forgotten Realms Wiki: Army of the Vale",
            "url": "https://forgottenrealms.fandom.com/wiki/Army_of_the_Vale",
            "accessed": "2026-10-28",
            "kind": "secondary",
        }, {
            "title": "Silver Marches (2002), Everlund web excerpt, fan-site copy at RealmsHelps",
            "url": "https://www.realmshelps.net/faerun/everlund.shtml",
            "accessed": "2026-10-28",
            "kind": "primary",
        }],
        "era_note": "The founding comes from Lost Empires of Faerun (2005), p. 84; the gates, bridges, Bell Market, temples, river navigation, imports, exports, council and 1372 DR population and races from Silver Marches (2002), pp. 74 to 78 and the book's map; the Army of the Vale from Silver Marches, pp. 76, 89 and 90; the 1358 and 1366 DR populations from earlier 2nd-edition sources (Waterdeep and the North, The Savage Frontier, Volo's Guide to the North, The North); the 1479 DR population from the Forgotten Realms Campaign Guide (2008), p. 146; evershimmer from Volo's Guide to the North (1993), p. 68; the late 15th century council, the Lords' Alliance vote and Danivarr's House from Storm King's Thunder (2016), pp. 81 to 82. All were cited by the Forgotten Realms Wiki and not independently consulted, except that a deep research pass on 2026-10-28 read the Silver Marches web excerpt (2002) in a fan-site copy (realmshelps.net) and confirmed the population, races, trade lists, Council of Six Elders, gates and the tower's position; that excerpt lists no evershimmer, which the wiki takes from Volo's Guide to the North, p. 68. Not verified for 1492 DR: no population is recorded after 1479 DR, the vote to leave the Lords' Alliance is dated only to the late 1480s or early 1490s DR, the First Elder after 1485 DR is not named, and the 1372 DR trade lists and racial shares are not assumed to hold. The engine's 21,000 residents are close to the 1372 DR count but are not tied to a year.",
    },
    "mirabar": {
        "status": "researched",
        "paragraphs": [
            "Mirabar is a walled mining city on a knoll on the north bank of the River Mirar in the Sword Coast North, below the Spine of the World, and was called the richest city north of Waterdeep in 1368 DR. Prince Ereskas Torlath of Amn built it in 626 DR on the foundations of an older dwarven tower; goblins sacked it in 753 DR, and from 812 DR its trade with Illusk and Stornanter made all three prosperous. Its surface is squat stone buildings and a few towers behind very thick, sloping walls that are iced in winter. Beneath it lies the Undercity, the dwarves' mining and forging city, reached by a guarded stair and lift from Undercity Square; open pits and rock heaps surround the city, and guarded roads run to its main mines in the Spine of the World, which yield many metals and gems.",
            "Shield dwarves work the mines and forges and make metal goods for export in the region and beyond, while humans help with the mining, carry the ore to market and defend the city. Cut stone and metal go down the Mirar to Luskan on magically floating barges at high cost and are shipped south; buildings in Amn, Baldur's Gate and Waterdeep use Mirabar stone. Silver from Mirabar is traded through Luskan, where in 1370 DR Mirabar's trading companies (Anvilfist Banner, the Golden Hand and Thalorin's Manymetals) held a whole district and Luskan built Mirabar's ships. Ground minerals and gems colour a brightly glazed local pottery, worthless stone is crushed to surface the roads, and in 1491 DR the city made its own trade bars, one-foot iron spindles worth 5 gp. The reopening of Mithral Hall took customers from Mirabar's mines in the 1370s DR. The city numbered about 23,000 in 1357 and 1370 DR (23,700 with 4,100 dwarves in 1358 DR) and 10,307 in 1372 DR.",
            "A hereditary marchion holds nominal rule and acts as chief justice, but real power lies with the Council of Sparkling Stones, an elected council of dwarves and humans (42 members in 1368 DR) that meets each autumn to set production quotas and trade agreements. Marchion Elastul Raurym ruled around 1368 to 1370 DR, with the sceptrana Shoudra Stargleam holding authority over trade from 1367 DR; after 1485 DR Marchion Selin Ramur handled only foreign policy and was a key member of the Lords' Alliance. The Axe of Mirabar, about 2,000 soldiers including 500 dwarves in 1370 DR, guards the city and keeps the mines clear of monsters, and mapping the city was forbidden to keep information from Luskan. Mirabarran dwarves helped reseal the primordial beneath Gauntlgrym in 1462 DR, and around 1486 DR (date inferred) Mirabar sent about a thousand dwarf soldiers to join Bruenor's army from Mithral Hall, a reversal of the 1370s DR rivalry.",
        ],
        "sources": [{
            "title": "Forgotten Realms Wiki: Mirabar",
            "url": "https://forgottenrealms.fandom.com/wiki/Mirabar",
            "accessed": "2026-10-29",
            "kind": "secondary",
        }, {
            "title": "Forgotten Realms Wiki: Council of Sparkling Stones",
            "url": "https://forgottenrealms.fandom.com/wiki/Council_of_Sparkling_Stones",
            "accessed": "2026-10-29",
            "kind": "secondary",
        }, {
            "title": "Forgotten Realms Wiki: Axe of Mirabar",
            "url": "https://forgottenrealms.fandom.com/wiki/Axe_of_Mirabar",
            "accessed": "2026-10-29",
            "kind": "secondary",
        }, {
            "title": "Forgotten Realms Wiki: Selin Ramur",
            "url": "https://forgottenrealms.fandom.com/wiki/Selin_Ramur",
            "accessed": "2026-10-29",
            "kind": "secondary",
        }, {
            "title": "Forgotten Realms Wiki: Luskan (silver trade, Mirabar District)",
            "url": "https://forgottenrealms.fandom.com/wiki/Luskan",
            "accessed": "2026-10-25",
            "kind": "secondary",
        }],
        "era_note": "The site, mines, walls, council, stone barges, Luskan district and laws come from Volo's Guide to the North (1993), pp. 111, 115 and 151 to 154; the Undercity, dwarven numbers, Axe of Mirabar and Mithral Hall rivalry from The Thousand Orcs (2002); the populations from Waterdeep and the North (1987), p. 8 (1357 DR), Dwarves Deep (1990), p. 61 (1358 DR), The North (1996), p. 27 (1370 DR) and the Forgotten Realms Campaign Setting (2001), p. 176 (1372 DR); the founding and early history from The Grand History of the Realms (2007); the silver trade from A Reader's Guide to R.A. Salvatore's The Legend of Drizzt (2008), pp. 142 to 143, and Tangled Webs (1998), p. 27; Selin Ramur from Storm King's Thunder (2016), p. 98; the Gauntlgrym episode from the novel Gauntlgrym (2010, via Wikipedia) and the soldiers for Bruenor from the novel Archmage (2015, via the wiki), both found in a deep research pass on 2026-10-29; the trade bars from Princes of the Apocalypse (2015), p. 159; the glazed pottery from the video game Baldur's Gate III. All were cited by the Forgotten Realms Wiki and not independently consulted. Not verified for 1492 DR: no population is recorded after 1372 DR, Selin Ramur is dated only to after 1485 DR, the trade bars are the latest economic detail (1491 DR), and the 14th century DR trade companies, council and production pattern are not assumed to hold. The engine's 19,000 residents match no sourced figure.",
    },
    "silverymoon": {
        "status": "researched",
        "paragraphs": [
            "Silverymoon, the Gem of the North, is the largest city of the Interior North and the leading city of the Silver Marches, built on a site sacred to Mielikki and Lurue where a bend of the River Rauvin splits it in two. The older Northbank is a walled half circle with three gates (the Moorgate to the west, Hunter's Gate to the north and the Sundabar Gate to the east), the Market running from the wall to the Docks, and the High Palace, most temples and noble houses on its eastern side. The Southbank, reached by the magical Moonbridge (raised in 843 DR, invisible except in moonlight and able to be dispelled to let tall masts pass), began as a caravan and warehouse quarter and grew nearly as large, holding most schools of the Conclave of Silverymoon and the Blacklar Gate and Mulgate. The city numbered about 26,000 in 1357 and 1366 DR, 29,990 in the late 1350s DR (4,200 of them dwarves), 37,073 in 1372 DR and about 40,000 in 1479 DR.",
            "Its economy rests on the arts and learning: music schools, magical study and the humbler craft of forestry are its main industries. Its exports are books, paper, inks, herbs, glass and glassware, furs, timber, unnamed valuable ores and Silverymoon Blue, a blue-tinted white wine fashionable in Ravens Bluff in the late 14th century DR; it imports food (especially grain and livestock), armor, weapons, footwear, textiles and clothing. Much overland trade comes from Sundabar by the Silver Road (about 165 miles), carrying the wealth of Citadel Adbar, while Everlund's folk dominated the short haul south to Yartar on the Evermoor Way (Everlund about 50 miles, Yartar 320, Waterdeep about 600). Small barges run down the Rauvin to Nesme (about 165 miles) and beyond. Named shops of the 14th century DR include Theldymir's Crystal (fine glass and lenses), Flamebar Canvas (flame silk sails for local barges), Mornbright's Dyes, Lyndal's Ropes and Cables, Dornsar Leathers and the Blue Bottle winery, and the city mints its own moon coin.",
            "High Mages ruled the city from Ecamane Truesilver's election in 637 DR; Alustriel Silverhand ruled from 1235 to 1369 DR, then gave the office to Taern Hornblade and in 1371 DR became High Lady of the new Confederation of the Silver Marches. The Knights in Silver (704 strong under Mazillor Shatterstave in 1372 DR) patrol about 50 miles around the city, and the Spellguard (32 in 1372 DR) guards it by magic. The Spellplague broke the city's mythal, which later returned dormant in the Moonbridge. Silverymoon fought in the War of the Silver Marches in 1484 to 1485 DR, but its weak help to Sundabar hurt its reputation, and the League of the Silver Marches, already left by Citadel Adbar, Citadel Felbarr and Mithral Hall by 1479 DR, disbanded in 1488 DR. By 1489 DR Taern had stepped down and Methrammar Aerasume, Alustriel's half-elf son and former High Marshal of the Argent Legion, ruled as Lord of Silverymoon, while Taern still spoke for the city at the Council of Waterdeep and in the Lords' Alliance because Methrammar was too blunt a diplomat. No source names a city council.",
        ],
        "sources": [{
            "title": "Forgotten Realms Wiki: Silverymoon",
            "url": "https://forgottenrealms.fandom.com/wiki/Silverymoon",
            "accessed": "2026-10-30",
            "kind": "secondary",
        }, {
            "title": "Forgotten Realms Wiki: Map:Silverymoon 15th century DR (interactive map)",
            "url": "https://forgottenrealms.fandom.com/wiki/Map:Silverymoon_15th_century_DR",
            "accessed": "2026-10-30",
            "kind": "secondary",
        }, {
            "title": "Forgotten Realms Wiki: Methrammar Aerasume",
            "url": "https://forgottenrealms.fandom.com/wiki/Methrammar_Aerasum%C3%A9",
            "accessed": "2026-10-30",
            "kind": "secondary",
        }, {
            "title": "Forgotten Realms Wiki: Luruar (League of the Silver Marches)",
            "url": "https://forgottenrealms.fandom.com/wiki/Luruar",
            "accessed": "2026-10-30",
            "kind": "secondary",
        }],
        "era_note": "The layout, gates and Docks come from Volo's Guide to the North (1993), pp. 170 to 173, Silver Marches (2002), pp. 54 to 63, and The North: Guide to the Savage Frontier (1996), pp. 45 to 55; the trade text, imports and exports from Silver Marches and The North; Silverymoon Blue from the RPGA Living City adventure Before Its Time (1999), p. 25; the populations from Waterdeep and the North (1987), p. 9, Dwarves Deep (1990), p. 61, Volo's Guide to the North, p. 170, Silver Marches, p. 54 (1372 DR) and the Forgotten Realms Campaign Guide (2008), p. 147 (1479 DR); the Spellplague from the Campaign Guide, p. 53; the war, the 1488 DR dissolution of the League, Taern and Methrammar from Vengeance of the Iron Dwarf (2015), the Forgotten Realms Campaign Guide, p. 146, the Sword Coast Adventurer's Guide (2015), pp. 17, 18 and 54, Storm King's Thunder (2016), p. 108, and The Rise of Tiamat (2014), p. 18. All were cited by the Forgotten Realms Wiki and not independently consulted; a deep research pass on 2026-10-30 found no population after 1479 DR, no ruler after 1489 DR and no named ore or 1490s DR business. Not verified for 1492 DR: no population is recorded after 1479 DR, Methrammar is dated only to 1489 DR, and the 14th century DR trade goods, shops and military strengths are not assumed to hold. The engine's 37,000 residents match the 1372 DR figure, not the 1479 DR one.",
    },
}