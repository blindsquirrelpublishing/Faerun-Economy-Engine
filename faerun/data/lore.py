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
}