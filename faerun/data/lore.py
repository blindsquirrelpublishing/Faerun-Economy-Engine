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
            "Griffon's Nest is a permanent settlement of the Uthgardt Griffon tribe in the Surbrin Hills of the Savage Frontier, northeast of Longsaddle, with Shining Creek farther east. Its inhabitants are described as human Uthgardt who worship Uthgar.",
            "The latest documented snapshot is 1485 DR: a hamlet of approximately 300 inhabitants under Chief Halric Bonesnapper, marked by poverty and reduced contact with outsiders. This is the closest documented account before the project's 1492 DR planning baseline, not proof of unchanged conditions in 1492.",
            "Historical notes: Kralgar Bonesnapper became chief in 1348 DR. The article records 900 residents in both 1358 and 1366 DR, then 6,713 in 1372 DR during the settlement's prosperous small-city period. Halric is Kralgar's great-grandson. Chief Targ Keifer is separately named circa 1484 DR; the source leaves the relationship between the Targ and Halric dates unresolved.",
            "The multi-period trade summary lists steel weapons as imports and woven rush goods, cane baskets, and trunks as exports. Earlier accounts describe outlying farms and openness to outside trade under Kralgar. These details do not establish current output, trade volumes, or named operating businesses in the later, more isolated hamlet.",
            "The mid-14th-century settlement had approximately twenty thatched wood-and-earth huts, a central longhouse, two warehouses, a log palisade, and roughly a dozen hillside farms. These are historical building counts, not a surveyed later layout. Adalfus Stormgatherer is named as a shaman under Kralgar; Keyl is named as Targ's son.",
            "The stored economy record's 80 inhabitants, Silver Marches region, marsh terrain, unnamed ruler, and inferred Nesme market profile are model inputs awaiting comparison with the sourced hills settlement. This lore entry does not overwrite population, terrain, leadership, production, routes, or map coordinates.",
        ],
        "sources": [{
            "title": "Forgotten Realms Wiki: Griffon's Nest",
            "url": "https://forgottenrealms.fandom.com/wiki/Griffon%27s_Nest",
            "accessed": "2026-10-01",
            "kind": "secondary",
        }],
        "era_note": "Use 1485 DR, the latest documented snapshot before the 1492 DR project baseline, while retaining 1358, 1366, and 1372 DR history separately. Approximately 300 residents and Halric Bonesnapper are dated to 1485, not verified for 1492. Targ Keifer circa 1484 and Halric in 1485 remain an unresolved source qualification. The real-world access date is not a setting date. This is a reviewed secondary summary, not independent verification of the cited publications.",
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
}