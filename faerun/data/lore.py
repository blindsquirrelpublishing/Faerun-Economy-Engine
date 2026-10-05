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
            "Historical reference only: Realms Helps' The North describes Neverwinter under Lord Nasher Alagondar as a city known for decorative glass lamps, precision water clocks, and jewelry. This older account supplies craft-history evidence, not proof that the same workshops or production levels exist in 1492 DR.",
            "In that account, the warm Neverwinter River supports gardens providing summer fruit and winter flowers. The city's named bridges include the Dolphin, Winged Wyvern, and Sleeping Dragon. Neither the gardening description nor the bridge names establish water yield, cultivated acreage, freight capacity, or the condition of infrastructure in 1492.",
            "The historical entry reports 23,192 inhabitants. Its third-edition-style statistics and surrounding late-14th-century chronology indicate an older setting snapshot; the exact date of the Neverwinter census is not explicitly attached to the passage. It must not replace a modern population estimate or establish current leadership. The reviewed subset does not verify the later city's reconstruction, operating businesses, or port throughput.",
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
        }],
        "era_note": "Historical Nasher-era account, consistent with a circa-1372 DR / third-edition regional snapshot inferred from surrounding chronology and rules notation; the local census date is not explicit. Not verified for 1492 DR. Historical crafts, gardens, bridges, and population come from the secondary Realms Helps reference, not an independently consulted underlying sourcebook. The Lords' Alliance paragraph instead comes from direct consultation of the official fifth-edition Basic Rules (2014) on D&D Beyond; its passage supplies no exact in-world date. Modern business and infrastructure continuity remain unresolved.",
    },
    "triboar": {
        "status": "researched",
        "paragraphs": [
            "A limited review of Power Score's guide to Storm King's Thunder identifies Othovir as a harness-maker, Urgala Meltimer as proprietor of the Northshield House inn, and Narth Tezrin as associated with the Lionshield Coster. These provide named leads for local crafts, lodging, and merchant services, not measured staffing or productive capacity.",
            "The guide identifies Darathra Shendrel as Triboar's Lord Protector in its faction list. It places the adventure after 1485 DR by reference to the sourcebook's dating sidebar; that does not establish an exact year or verify these people and businesses for the project's 1492 DR baseline.",
            "This is a limited secondary-source review, not direct consultation of Storm King's Thunder or the blocked Forgotten Realms Wiki article. The reviewed passages do not verify a resident census, agricultural specialization, caravan throughput, water supply, or continuing business operation in 1492. Named establishments are not additional workers or production to add to the economy model.",
        ],
        "sources": [{
            "title": "Power Score: Dungeons & Dragons - A Guide to Storm King's Thunder (Sean McGovern)",
            "url": "https://thecampaign20xx.blogspot.com/2016/08/dungeons-dragons-guide-to-storm-kings.html",
            "accessed": "2026-10-01",
            "kind": "secondary",
        }],
        "era_note": "Fifth-edition Storm King's Thunder context, after 1485 DR according to the guide's reference to page 13; not verified for 1492. The guide mixes sourcebook summaries with personal campaign suggestions and contains inconsistent name spellings. Only the limited attributed business and civic details above were adopted; campaign suggestions, outcomes, and unverified quantities were excluded. The underlying publication was not independently consulted.",
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
            "Phandalin is a rebuilt frontier village in the Lost Hills of the Sword Mountains, south of Neverwinter Wood and northeast of Leilon. It lies near the route connecting the High Road with Triboar. The late-15th-century account describes roughly fifty buildings, an orchard to the west, Tresendar Manor to the east, a town square and green, and three deep wells. The building count does not establish a resident census, and the wells have no verified daily yield in this project.",
            "Farmers and prospectors form the basis of the community. The source emphasizes nearby gold and platinum mining, with farming, ranching, logging, and trapping also contributing. Cold iron appears in an earlier resettlement account. These descriptions supplement the economy model; they do not verify its silver specialization, production quantities, prices, or configured population of 500.",
            "Named places in the late-15th-century accounts include Stonehill Inn (Toblen Stonehill), the Sleeping Giant (Grista), Barthen's Provisions (Elmar Barthen), Edermath Orchard (Daran Edermath), Lionshield Coster (Linene Graywind), the Miner's Exchange (Halia Thornton), and Alderleaf Farm (Qelline Alderleaf). These are source-backed names, not additional generated businesses or workforce counts.",
            "The Shrine of Luck is dedicated to Tymora and tended by Sister Garaele. The Townmaster's Hall provides civic administration. Harbin Wester is identified as townmaster in 1491 DR; an early-1490s council initially included Wester, Sildar Hallwinter, and Trilena Stonehill. The precise transition date is unresolved for the 1492 planning baseline.",
            "The older settlement was associated with Phandelver's Pact, Wave Echo Cave, and the Forge of Spells. The modern resettlement began around 1486 DR with arrivals from Neverwinter and Waterdeep and was established by 1491. Later accounts describe tourism after Volo's visit and disappointing mining income; neither supplies measured current visitor numbers or production.",
            "The conversion of Barthen's Provisions into the Temple of the Coinmaiden, dedicated to Waukeen, and a mayoral election with council expansion are dated to 1496 DR in the wiki. They are later developments, not automatic facts for 1492. Earlier businesses and subsequent changes in personnel likewise require date checks.",
        ],
        "sources": [{
            "title": "Forgotten Realms Wiki: Phandalin",
            "url": "https://forgottenrealms.fandom.com/wiki/Phandalin",
            "accessed": "2026-10-01",
            "kind": "secondary",
        }],
        "era_note": "Reviewed as supplemental canon reference, not an independently verified primary publication. The article combines historical periods. It adopts 1491 DR for Lost Mine of Phandelver despite a conflicting 1481 implication, and 1496 for Acquisitions Incorporated from a creator statement. Government transitions, mine operation, and later establishments must not be assumed current in 1492.",
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
}