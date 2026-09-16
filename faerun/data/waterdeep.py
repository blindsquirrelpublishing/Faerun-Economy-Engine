"""Source-linked historical directory; these records are not live economy actors."""

from ..citymodels import Affiliation, Citation, HistoricalBusiness, HistoricalPerson


SOURCE = {
    "id": "volos_guide_to_waterdeep",
    "title": "Volo's Guide to Waterdeep",
    "author": "Ed Greenwood",
    "publication_year": 1992,
    "publisher": "TSR, Inc.",
    "edition": "AD&D / Forgotten Realms, second-edition publication era",
    "local_path": r"volo\Volo's Guide to Waterdeep.pdf",
    "pdf_page_count": 243,
    "product_number": "9379",
    "isbn": "1-56076-335-3",
    "era_note": (
        "Historical accounts from a 1992 AD&D-era guide, not verified current in "
        "1492 DR. The exact in-world year is not established here. People, roles, "
        "ownership, prices and business survival must not be carried into the live "
        "economy without separate evidence or an explicit campaign adaptation."
    ),
    "publication_citations": [
        {"printed_page": 2, "pdf_page": 3, "source_id": "volos_guide_to_waterdeep"}
    ],
    "publication_note": "The credits identify Ed Greenwood and the 1992 TSR copyright.",
    "pagination_note": (
        "Citations use 1-based physical PDF positions. Printed pages 2-240 correspond "
        "to PDF pages 3-241: PDF page = printed page + 1. Every record-cited printed "
        "page numeral was checked in the text layer. PDF page 2 is the title page "
        "without a confirmed printed numeral; no printed numbers are assigned here "
        "to PDF pages 1, 242 or 243."
    ),
    "narrator_note": (
        "The preface and people appendix warn that Volo's accounts and probable "
        "character details can be mistaken. These are verified source attributions, "
        "not independent confirmation of every narrated claim."
    ),
    "narrator_citations": [
        {"printed_page": 4, "pdf_page": 5, "source_id": "volos_guide_to_waterdeep"},
        {"printed_page": 214, "pdf_page": 215, "source_id": "volos_guide_to_waterdeep"},
    ],
    "ward_note": (
        "Southern Ward is the chapter heading; the guide explicitly says locals "
        "call it South Ward. Its index lists six wards. The City of the Dead is a "
        "separately named area around which Trades Ward wraps, not an additional "
        "ward in that index; no business in this selection is assigned there."
    ),
    "ward_citations": [
        {"printed_page": 105, "pdf_page": 106, "source_id": "volos_guide_to_waterdeep"},
        {"printed_page": 135, "pdf_page": 136, "source_id": "volos_guide_to_waterdeep"},
        {"printed_page": 235, "pdf_page": 236, "source_id": "volos_guide_to_waterdeep"},
    ],
    "extraction_note": (
        "239 of 243 PDF pages contain extractable text. Broken columns, line-end "
        "hyphenation and inconsistent name spellings require care. Source variants "
        "are retained in relevant summaries; no wholesale extracted text is included."
    ),
}

WARDS: tuple[str, ...] = (
    "Castle Ward",
    "Sea Ward",
    "North Ward",
    "Trades Ward",
    "Southern Ward",
    "Dock Ward",
)


def _cite(*printed_pages: int) -> tuple[Citation, ...]:
    return tuple(Citation(page, page + 1) for page in printed_pages)


def _person(
    identifier: str,
    name: str,
    summary: str,
    printed_pages: tuple[int, ...],
    business_id: str,
    role: str,
) -> HistoricalPerson:
    citations = _cite(*printed_pages)
    return HistoricalPerson(
        identifier,
        name,
        summary,
        citations,
        (Affiliation(business_id, role, citations),),
    )


BUSINESSES: tuple[HistoricalBusiness, ...] = (
    HistoricalBusiness(
        "castle_aurora", "Aurora's Whole Realms Shop Catalogue Counter", "Castle Ward", "shop",
        ("Catalogue retail", "Local home delivery"),
        "Catalogue branch with a coach and six-person delivery team serving Castle Ward; four guards work in pairs.",
        _cite(14, 15), "First shopfront west of the Jade Jug, north side of Waterdeep Way.",
    ),
    HistoricalBusiness(
        "castle_balthorr", "Balthorr's Rare and Wondrous Treasures", "Castle Ward", "shop",
        ("Curios", "Coins and gems", "Regalia", "Buying valuables"),
        "Sells coins, gems and regalia. Its proprietor knows currencies and military insignia; a footnote describes buying stolen goods at 40% of street value.",
        _cite(15), "East side of the Street of the Sword, south of Selduth Street.",
    ),
    HistoricalBusiness(
        "castle_golden_key", "The Golden Key", "Castle Ward", "service",
        ("Custom locks", "Fastenings"),
        "Makes custom locks and fastenings, including multi-key mechanisms; most products are made on site.",
        _cite(15, 16), "East side of Warriors' Way, north of Waterdeep Way.",
    ),
    HistoricalBusiness(
        "castle_halambar", "Halambar Lutes & Harps", "Castle Ward", "shop",
        ("Stringed instruments", "Secondhand instruments", "Musical boxes"),
        "Sells stringed instruments, apprentice and secondhand pieces, and enchanted musical boxes. Its self-playing harp is an attraction, not sale stock.",
        _cite(16, 17), "East side of the Street of the Sword, north of Waterdeep Way.",
    ),
    HistoricalBusiness(
        "castle_hilmer", "The Halls of Hilmer, Master Armorer", "Castle Ward", "service",
        ("Custom plate armor", "Armor fitting", "Replacement armor pieces"),
        "Specializes in fitted plate armor, with fitting, practice and workshop areas. Custom suits typically cost 4,000-6,000 gp in this source.",
        _cite(17, 18, 19), "West side of the Street of Bells, north of Waterdeep Way.",
    ),
    HistoricalBusiness(
        "castle_olmhazan", "Olmhazan's Jewels", "Castle Ward", "shop",
        ("Gemstones",),
        "Sells a broad selection of ordinary gemstones, excluding exceptionally rare or magical kinds; two trained mimics guard the shop.",
        _cite(19), "West side of the High Road, opposite the mouth of Spendthrift Alley.",
    ),
    HistoricalBusiness(
        "castle_phalantar", "Phalantar's Philtres & Components", "Castle Ward", "shop",
        ("Medicines and herbs", "Spell components", "Buying adventuring finds"),
        "Sells medicines, herbs and unusual ingredients. A footnote describes financing adventurers and buying stolen goods at 35% of street price.",
        _cite(19, 20), "East side of the Street of Bells, just north of Waterdeep Way.",
    ),
    HistoricalBusiness(
        "castle_jade_jug", "The Jade Jug", "Castle Ward", "inn",
        ("Luxury lodging", "Personal attendants", "Guest transport", "Baths"),
        "Luxury lodging with personal servants, baths and guest transport. Source prices are 12-30 gp per night for rooms and 25-50 gp for suites.",
        _cite(31, 32), "Northwest corner of the High Road and Waterdeep Way.",
    ),
    HistoricalBusiness(
        "castle_pampered_traveler", "The Pampered Traveler", "Castle Ward", "inn",
        ("Lodging", "Meals", "Meeting rooms", "Library"),
        "Rooms, meeting rooms, a children's nursery and a staff-copied library serve wealthy travelers and scholars. The room fee includes specified meals and drinks.",
        _cite(32, 33, 34), "Northeast corner of Selduth Street and the Street of Bells.",
    ),
    HistoricalBusiness(
        "sea_aurora", 'Aurora\'s Realms Shop "Singing Dolphin" Catalogue Counter', "Sea Ward", "shop",
        ("Catalogue retail",),
        "Sea Ward catalogue branch with six guards working in two groups of three.",
        _cite(58, 59),
        "Third shopfront north of Grimwald's Way, west side of the Street of the Singing Dolphin.",
    ),
    HistoricalBusiness(
        "sea_halazar", "Halazar's Fine Gems", "Sea Ward", "shop",
        ("Fine gemstones", "Mounted gems"),
        "Exclusive gems sell at four times Volo's comparison value; the costly presentation attracts buyers. The text-layer heading says 'Pine Gems', but the index confirms 'Fine Gems'.",
        _cite(59, 60, 237),
    ),
    HistoricalBusiness(
        "sea_selchoun", "Selchoun's Sundries Shop", "Sea Ward", "shop",
        ("Sundries", "Souvenirs", "Travel supplies"),
        "Sells tourist souvenirs alongside useful small goods such as string, flint, kindling, clay pipes and carrysacks.",
        _cite(60),
    ),
    HistoricalBusiness(
        "sea_gounar", "Gounar's Tavern", "Sea Ward", "tavern",
        ("Drinks", "Social venue"),
        "Bright, conspicuous drinking venue for fashionable social visibility. Drinks are quoted at 6 gp per glass, with quality wines twice that.",
        _cite(60, 61),
    ),
    HistoricalBusiness(
        "sea_ships_wheel", "The Ship's Wheel", "Sea Ward", "tavern",
        ("Drinks", "Quiet social venue"),
        "Quiet, costly and notably safe tavern catering to older affluent patrons; a huge ship's wheel decorates the lobby.",
        _cite(61), "On a corner just inside West Gate.",
    ),
    HistoricalBusiness(
        "sea_dacers", "Dacer's Inn", "Sea Ward", "inn",
        ("Lodging", "Simple meals", "Stabling", "Delivered food"),
        "Serves prosperous sailors and visitors to Gond's temple. Rooms have practical innovations including pumped water and food lifts; lodging includes simple meals and stabling.",
        _cite(61, 62), "Seawatch Street, south of the temple of Gond.",
    ),
    HistoricalBusiness(
        "north_misty_beard", "The Misty Beard", "North Ward", "tavern",
        ("Drinks", "Meals", "Private meeting rooms"),
        "Former inn turned tavern, staffed by many different kinds of beings. Offers meals, an unusually broad drinks cellar and private negotiation rooms.",
        _cite(90, 91, 92), "A corner near the city's east wall.",
    ),
    HistoricalBusiness(
        "north_aurora", "Aurora's Realms Shop Catalogue Counter", "North Ward", "shop",
        ("Catalogue retail",),
        "Catalogue branch occupying the lower part of a converted house, with luxury apartments above and four guards working in pairs.",
        _cite(93, 94), "High Road, next to the House of Healing.",
    ),
    HistoricalBusiness(
        "north_maerados", "Maerados Fine Furs", "North Ward", "shop",
        ("Fur clothing", "Winter garments", "Custom scenting"),
        "Sells fashionable furs, winter clothing and custom scenting; concealed pockets are a standard feature.",
        _cite(94),
    ),
    HistoricalBusiness(
        "north_hriiat", "Hriiat Fine Pastries", "North Ward", "shop",
        ("Sweet pastries", "Savory pastries", "Takeaway meals"),
        "Busy bakery selling sweets, meat or fish bite-pies and substantial filled rolls intended to be eaten while walking.",
        _cite(94),
    ),
    HistoricalBusiness(
        "north_sulmest", "Sulmest's Splendid Shoes & Boots", "North Ward", "service",
        ("Custom footwear", "Ready-made footwear", "Footwear repairs"),
        "Fashionable custom footwear, cheaper ready-made sizes and reduced-price repairs; some boots include replacement guarantees.",
        _cite(94, 95),
    ),
    HistoricalBusiness(
        "north_cliffwatch", "The Cliffwatch", "North Ward", "inn",
        ("Lodging", "Local information"),
        "Worn but welcoming inn valued for its helpful keeper, local information and informal refuge; the text also acknowledges smugglers' cellars.",
        _cite(97, 98), "Northeast corner of Endcliff Lane and Nindabar Street.",
    ),
    HistoricalBusiness(
        "north_galloping_minotaur", "The Galloping Minotaur", "North Ward", "inn",
        ("Lodging", "Advance bookings", "Private meeting rooms"),
        "Merchant-oriented inn with advance bookings, private meeting rooms and an expansion into adjacent buildings; Volo criticizes its declining service.",
        _cite(98),
    ),
    HistoricalBusiness(
        "trades_dripping_dagger", "The Inn of the Dripping Dagger", "Trades Ward", "inn",
        ("Lodging", "Food and drink", "Stabling", "Mercenary introductions", "Equipment rental"),
        "Mercenary lodging and hiring hub with stabling, a private meeting room and equipment rental or sale; treated by patrons as neutral ground.",
        _cite(111, 114),
        "East side of the High Road, south of Selduth Street and north of the Coffinmarch.",
    ),
    HistoricalBusiness(
        "trades_aurora", 'Aurora\'s Realms Shop "High Road" Catalogue Counter', "Trades Ward", "shop",
        ("Catalogue retail",),
        "Catalogue branch with six guards working in groups of three.",
        _cite(120), "Northwest corner of the Street of the Tusks and the High Road.",
    ),
    HistoricalBusiness(
        "trades_belmonder", "Belmonder's Meats", "Trades Ward", "shop",
        ("Retail meat", "Wholesale meat", "Cooked skewers", "Carcass cutting"),
        "Retail and wholesale meat business selling ready-cooked skewers and supplying inns and households; smoked or aged meat comes from its estates near Rassalantar.",
        _cite(120),
    ),
    HistoricalBusiness(
        "trades_thentavva", "Thentavva's Boots", "Trades Ward", "service",
        ("Custom boots", "Shoes and slippers"),
        "Makes durable custom footwear; sought-after thigh-high boots are quoted at 10 gp with a wait of at least nine days.",
        _cite(121), "Vellarr's Lane.",
    ),
    HistoricalBusiness(
        "trades_orsabbas", "Orsabbas's Fine Imports", "Trades Ward", "shop",
        ("Imported goods", "Costume sales and rental", "Special orders"),
        "Sells far-traveled goods and rents or sells regional clothing for costumes and disguises; special orders can take a season.",
        _cite(121, 122, 123), "Vellarr's Lane, just east of the Street of the Tusks.",
    ),
    HistoricalBusiness(
        "trades_riautar", "Riautar's Weaponry", "Trades Ward", "shop",
        ("Secondhand weapons", "Bows", "Arrows and bowstrings"),
        "Carries mainly secondhand weapons and makes highly regarded arrows, bowstrings and longbows on site.",
        _cite(123), "High Road, just east of the Street of the Tusks, as stated in the text.",
    ),
    HistoricalBusiness(
        "trades_riven_shield", "The Riven Shield Shop", "Trades Ward", "shop",
        ("Secondhand arms", "Secondhand armor", "Adventuring relics"),
        "Large secondhand arms and armor stock combines affordable practical weapons with expensive or unavailable famous relics.",
        _cite(123, 124),
    ),
    HistoricalBusiness(
        "trades_saern", "Saern's Fine Swords", "Trades Ward", "shop",
        ("Sword sales", "Blade sharpening"),
        "Large sword stock and sharpening service; an agreement permits the city to requisition its arms and use the building in an emergency.",
        _cite(125), "Southeast corner of the High Road and Burnt Wagon Way.",
    ),
    HistoricalBusiness(
        "south_old_monster", "The Old Monster Shop", "Southern Ward", "shop",
        ("Live creatures", "Monster remains", "Guarded crate storage"),
        "Sells live creatures and preserved remains to varied buyers; separately rents guarded storage for crated goods on the upper floors.",
        _cite(146, 220), "The Jar, a close off Tilman's Lane near the Trollwall.",
    ),
    HistoricalBusiness(
        "south_good_spirits", "The House of Good Spirits", "Southern Ward", "guildhall",
        ("Lodging", "Food and drink", "Stabling", "Wine and beer production", "Spirits trading", "Guild meetings"),
        "Guild-owned production, retail, hospitality and meeting complex; makes sluth and zzar, has a brewery, and includes a 40-bed inn and stables.",
        _cite(152, 153),
        "Northwest side of the Rising Ride between Juth Alley and Robin's Way; extends along Tornsar Alley toward Buckle Street.",
    ),
    HistoricalBusiness(
        "south_jade_dancer", "The Jade Dancer", "Southern Ward", "festhall",
        ("Drinks", "Music and dancing", "Room rental", "Festhall"),
        "Music, dancing, drinks and rented rooms attract fashionable young patrons. Its famous dancer is a magically animated jade figure.",
        _cite(155, 156), "Dancing Court, just north of Slop Street, in the Tween Run.",
    ),
    HistoricalBusiness(
        "south_nueth", "Nueth's Fine Nets", "Southern Ward", "shop",
        ("Ropes and nets", "Rigging lines", "Hammocks", "Climbing cable"),
        "Supplies ropes, nets, hammocks, rigging lines, rope bridges and mesh, including reinforced climbing cable.",
        _cite(159),
    ),
    HistoricalBusiness(
        "south_pelauvir", "Pelauvir's Counter", "Southern Ward", "shop",
        ("General merchandise", "Household goods"),
        "Former warehouse offering a wide variety of household and practical goods, but not food or drink.",
        _cite(159),
    ),
    HistoricalBusiness(
        "south_aurora", "Aurora's Realms Shop Catalogue Counter", "Southern Ward", "shop",
        ("Catalogue retail",),
        "Catalogue branch in a deteriorating tenement, with four guards working in pairs.",
        _cite(159), "Way of the Dragon, next to the Red Gauntlet tavern.",
    ),
    HistoricalBusiness(
        "dock_helmstar", "Helmstar Warehouse", "Dock Ward", "warehouse",
        ("Cargo packing", "Cargo forwarding", "Buying carvings and statuary"),
        "Handles small cargo and forwarding with careful packing and discreet service; much business is described as handling stolen goods.",
        _cite(173, 174), "Dock Street, northeast corner of Crookedclaw Alley.",
    ),
    HistoricalBusiness(
        "dock_xoblob", "The Old Xoblob Shop", "Dock Ward", "shop",
        ("Curios", "Unusual adventuring gear", "Buying finds", "House wine"),
        "Curios, unusual equipment and house-made wine; buys assorted finds. Upper storage has an Undermountain teleport connection, not ordinary rental lodging. These historical owners are not verified current.",
        _cite(176, 177, 178, 179),
        "Northwest corner of Fillet Lane and Slut Street, next to the Purple Palace and two doors from Aurora's.",
    ),
    HistoricalBusiness(
        "dock_serpentil", "Serpentil Books & Folios", "Dock Ward", "shop",
        ("Rare books", "Maps and charts", "Magical texts", "Buying written lore"),
        "Buys and sells written lore, especially magical books and Sword Coast maps. A 30% buying rate applies to known stolen works. The entry's footnote confirms 'Serpentil', despite the truncated text-layer heading.",
        _cite(180), "East side of Book Street.",
    ),
    HistoricalBusiness(
        "dock_red_sails", "Red Sails Warehouse", "Dock Ward", "warehouse",
        ("Cargo storage", "Ice-cooled storage"),
        "Rents storage by coffin-sized longbox volume; excludes living and flammable cargo and charges extra for ice-cooled storage.",
        _cite(199),
    ),
    HistoricalBusiness(
        "dock_gelfuril", "Gelfuril the Trader", "Dock Ward", "shop",
        ("Used goods", "Barter"),
        "Trades mainly used goods for barter or coin at reasonable prices; explicitly not a pawnshop.",
        _cite(199, 200),
    ),
    HistoricalBusiness(
        "dock_house_pride", "The House of Pride", "Dock Ward", "shop",
        ("Perfumes",),
        "Two sisters sell exotic perfumes; trained dogs and magic preventing glass breakage protect the displays. Repeated references confirm 'House', despite the text-layer heading 'Rouse'.",
        _cite(200),
    ),
    HistoricalBusiness(
        "dock_aurora", "Aurora's Realms Shop Catalogue Counter", "Dock Ward", "shop",
        ("Catalogue retail",),
        "Catalogue branch open dawn to dusk; two guards flank its order clerk. A footnote supplies staff names unavailable to Volo.",
        _cite(200), "Slut Street, just north of the Purple Palace across a narrow side alley.",
    ),
    HistoricalBusiness(
        "dock_blue_mermaid", "The Blue Mermaid", "Dock Ward", "tavern",
        ("Drinks",),
        "Clean but worn drinking house described as safe, with good ale and less successful wine.",
        _cite(200),
    ),
    HistoricalBusiness(
        "dock_warm_beds", "Warm Beds", "Dock Ward", "inn",
        ("Basic lodging", "Hot washing water", "Quiet meeting space"),
        "Basic rooms with stone-warmed beds and hot washing water; no food or stabling. Guests may use rooms for quiet meetings.",
        _cite(205, 206),
    ),
    HistoricalBusiness(
        "dock_rearing_hippocampus", "The Rearing Hippocampus", "Dock Ward", "inn",
        ("Private lodging", "Food"),
        "Secure lodging popular with caravan masters and harbor merchants; offers canopied beds and broth and toast. The guide says it reverted from the Hidden Blade tavern to its former owner and reputation.",
        _cite(206, 207),
    ),
)

PEOPLE: tuple[HistoricalPerson, ...] = (
    _person(
        "cathal_sunspear", "Cathal Sunspear",
        "Cultured, middle-aged counter clerk at the Castle Ward Aurora's branch.",
        (15,), "castle_aurora", "Counter clerk",
    ),
    _person(
        "xanatrar_hillhorn", "Xanatrar Hillhorn",
        "Service-mage at the Castle Ward Aurora's branch; also known for singing at parties.",
        (15,), "castle_aurora", "Service-mage",
    ),
    _person(
        "balthorr_the_bold_olaskos", 'Balthorr "the Bold" Olaskos',
        "Proprietor and fence specializing in coins, gems and regalia.",
        (15,), "castle_balthorr", "Proprietor; fence",
    ),
    _person(
        "ansilver_the_locksmith", "Ansilver the Locksmith",
        "Makes individually keyed locks at the Golden Key.",
        (15, 16), "castle_golden_key", "Proprietor; locksmith",
    ),
    _person(
        "kriios_halambar", "Kriios Halambar",
        "Owns and runs the instrument shop; guildmaster of the Council of Musicians, Instrument-Makers, and Choristers.",
        (17,), "castle_halambar", "Owner and operator",
    ),
    _person(
        "hilmer", "Hilmer",
        "Master armorer employing apprentices; reserves his maker's mark for custom work.",
        (17, 18, 19), "castle_hilmer", "Proprietor; master armorer",
    ),
    _person(
        "jhauntar_olmhazan", "Jhauntar Olmhazan",
        "Owns and runs the gem shop; Gentleman Speaker for the Jewelers' Guild.",
        (19,), "castle_olmhazan", "Owner and operator",
    ),
    _person(
        "phalantar_orivan", "Phalantar Orivan",
        "Sponsors ventures in exchange for saleable finds or a share of profits, alongside his component shop and stolen-goods dealing.",
        (20,), "castle_phalantar", "Proprietor; fence and adventuring financier",
    ),
    _person(
        "amaratha_ruendarr", "Amaratha Ruendarr",
        "Retired adventuress with one arm; remembers returning guests and invests in attentive service.",
        (32, 215), "castle_jade_jug", "Proprietress",
    ),
    _person(
        "brathan_zilmer", "Brathan Zilmer",
        "Runs the Pampered Traveler and serves as guildmaster of the Fellowship of Innkeepers.",
        (34,), "castle_pampered_traveler", "Operator",
    ),
    _person(
        "orloth_theldarin", "Orloth Theldarin",
        "Counter clerk at the Singing Dolphin Aurora's branch, known for tact and carefully chosen dress.",
        (59,), "sea_aurora", "Counter clerk",
    ),
    _person(
        "saerghon_the_magnificent_alir", 'Saerghon "the Magnificent" Alir',
        "Ostentatious Aurora's service-mage whose confidence exceeds his study habits.",
        (59,), "sea_aurora", "Service-mage",
    ),
    _person(
        "stromquil_halazar", "Stromquil Halazar",
        "Proprietor of the exclusive gem shop and guildmaster of the Jewellers' Guild.",
        (60,), "sea_halazar", "Proprietor",
    ),
    _person(
        "osbrin_selchoun", "Osbrin Selchoun",
        "Short, cheerful shopkeeper selling sundries and souvenirs.",
        (60,), "sea_selchoun", "Proprietor",
    ),
    _person(
        "doblin_gounar", "Doblin Gounar",
        "Tavern proprietor whom Volo describes as cold and egotistical.",
        (61,), "sea_gounar", "Proprietor",
    ),
    _person(
        "olhin_shalut", "Olhin Shalut",
        "Affable elderly proprietor, described as wealthy and equipped with many magic items.",
        (61,), "sea_ships_wheel", "Proprietor",
    ),
    _person(
        "amasanna_vumendir", "Amasanna Vumendir",
        "Directs the inn's well-trained staff with hand gestures.",
        (62,), "sea_dacers", "Proprietress",
    ),
    _person(
        "allet_tzuntzin", "Allet Tzuntzin",
        "Half-elven mage running the Misty Beard with her sister Vindara; uses wands to keep order.",
        (92,), "north_misty_beard", "Co-owner",
    ),
    _person(
        "vindara_tzuntzin", "Vindara Tzuntzin",
        "Half-elven mage running the tavern with Allet; the sisters previously operated the Black Gryphon inn in Elturel.",
        (92,), "north_misty_beard", "Co-owner",
    ),
    _person(
        "munzrim_marlpar", "Munzrim Marlpar",
        "Tall, intelligent lizard man tending bar, often talking with the spectator Thoim Zalamm.",
        (92,), "north_misty_beard", "Bartender",
    ),
    _person(
        "thoim_zalamm", "Thoim Zalamm",
        "Philosophical spectator often seen behind the bar with Munzrim. This documents an association, not employment or ownership.",
        (92, 231), "north_misty_beard", "Documented associate of the bartender; employment unconfirmed",
    ),
    _person(
        "phandalue_tarinthil", "Phandalue Tarinthil",
        "Sharp-tongued counter clerk at the North Ward Aurora's branch.",
        (93, 94), "north_aurora", "Counter clerk",
    ),
    _person(
        "quirtan_ondever", "Quirtan Ondever",
        "Aurora's service-mage who cultivates a mysterious, sinister manner.",
        (94,), "north_aurora", "Service-mage",
    ),
    _person(
        "shalrin_maerados", "Shalrin Maerados",
        "Observant furrier and Gentleman Keeper of the Solemn Order of Recognized Furriers & Woolmen. The shop entry uses Maerados; the appendix heading uses Meraedos.",
        (94, 230), "north_maerados", "Proprietor",
    ),
    _person(
        "relchoz_hriiat", "Relchoz Hriiat",
        "Owns the bakery, samples his baking and offers tastes to customers; public contact for the Bakers' Guild.",
        (94,), "north_hriiat", "Owner and operator",
    ),
    _person(
        "darion_sulmest", "Darion Sulmest",
        "Footwear proprietor and spokesman for the Order of Cobblers & Corvisers; welcomes adventuring stories.",
        (95, 218), "north_sulmest", "Proprietor",
    ),
    _person(
        "felstan_spindrivver", "Felstan Spindrivver",
        "Helpful innkeeper who directs travelers to unusual goods and shares city rumors.",
        (97, 98), "north_cliffwatch", "Proprietor",
    ),
    _person(
        "waendel_uthrund", "Waendel Uthrund",
        "Introduced advance bookings popular with merchants. The main entry and appendix body use Waendel; the appendix heading reads Waesdel.",
        (98, 233), "north_galloping_minotaur", "Proprietor",
    ),
    _person(
        "filiare", "Filiare",
        "Retired mercenary who brokers work and rents or sells spare adventuring equipment.",
        (114,), "trades_dripping_dagger", "Proprietor; mercenary hiring intermediary",
    ),
    _person(
        "orgula_samshroon", "Orgula Samshroon",
        "Counter clerk described as a motherly matron at the High Road Aurora's branch.",
        (120,), "trades_aurora", "Counter clerk",
    ),
    _person(
        "dhaunryl_zalimbar", "Dhaunryl Zalimbar",
        "Tall, kindly service-mage at the High Road Aurora's branch.",
        (120,), "trades_aurora", "Service-mage",
    ),
    _person(
        "morathin_hooks_belmonder", 'Morathin "Hooks" Belmonder',
        "Butcher-shop proprietor, Second Knife and public contact for the Guild of Butchers; the business uses guarded meat deliveries.",
        (120,), "trades_belmonder", "Proprietor",
    ),
    _person(
        "thurve_thentavva", "Thurve Thentavva",
        "Calm, bespectacled maker of custom boots and other footwear.",
        (121,), "trades_thentavva", "Proprietor; cobbler",
    ),
    _person(
        "ildar_the_duke_of_darkness_orsabbas", 'Ildar "the Duke of Darkness" Orsabbas',
        "Importer whose nickname comes from his masked persona at noble festivities.",
        (123,), "trades_orsabbas", "Proprietor",
    ),
    _person(
        "zarondar_the_nimble_riautar", 'Zarondar "the Nimble" Riautar',
        "Makes archery equipment and is public contact for the Fellowship of Bowyers and Fletchers. The entry and appendix body use Zarondar; the appendix heading gives Zaronrar or Zorondar.",
        (123, 234), "trades_riautar", "Proprietor",
    ),
    _person(
        "delborggan_the_blade", "Delborggan the Blade",
        "One-eyed former adventurer who runs the secondhand arms and armor shop.",
        (124,), "trades_riven_shield", "Operator",
    ),
    _person(
        "zygarth_slayer_saern", 'Zygarth "Slayer" Saern',
        "Skilled at judging steel; operates the sword shop with an emergency supply arrangement for the city.",
        (125,), "trades_saern", "Operator",
    ),
    _person(
        "feldyn_goadolfyn", "Feldyn Goadolfyn",
        "Runs an ever-changing stock of creatures and monster-derived materials.",
        (146, 220), "south_old_monster", "Owner and operator",
    ),
    _person(
        "simon_thrithyn", "Simon Thrithyn",
        "Innkeeper within the Vintners', Distillers', and Brewers' Guild complex.",
        (153,), "south_good_spirits", "Innkeeper",
    ),
    _person(
        "dlarna_suone", "Dlarna Suone",
        "Heads resident buying and selling for the Vintners', Distillers', and Brewers' Guild.",
        (153,), "south_good_spirits", "Resident chief guild buyer and seller",
    ),
    _person(
        "gordrym_zhavall", "Gordrym Zhavall",
        "Second to Dlarna Suone, the resident chief buyer and seller at the guild complex.",
        (153,), "south_good_spirits", "Deputy to the resident chief guild buyer and seller",
    ),
    _person(
        "elguth_iramblin", "Elguth Iramblin",
        "Stableboy and guild member who also knows Waterdeep's gambling and entertainment venues; called Elguth in the location entry.",
        (153, 220), "south_good_spirits", "Stableboy",
    ),
    _person(
        "mrorn_black_bracers_halduth", 'Mrorn "Black Bracers" Halduth',
        "Leads seven bouncers at the House of Good Spirits; the appendix joins his nickname as Blackbracers.",
        (153, 226), "south_good_spirits", "Head of seven bouncers",
    ),
    _person(
        "cathalishaera", "Cathalishaera",
        "Sorceress identified by a footnote as the club's owner and hidden animator of its jade dancer.",
        (156,), "south_jade_dancer", "Owner; sorceress",
    ),
    _person(
        "selcharoon_nrim", "Selcharoon Nrim",
        "Wizard employed to protect the Jade Dancer's patrons and staff.",
        (156,), "south_jade_dancer", "Wizard bouncer",
    ),
    _person(
        "thumir_aingahuth", "Thumir Aingahuth",
        "Named operator of Nueth's Fine Nets. The appendix says the namesake Nueth died twelve years before its account; this is not a calendar-date claim.",
        (159, 231), "south_nueth", "Proprietor",
    ),
    _person(
        "braum_pelauvir", "Braum Pelauvir",
        "Tall, sturdy and jovial owner of the general-merchandise counter.",
        (159,), "south_pelauvir", "Owner and operator",
    ),
    _person(
        "mril_juthbuck", "Mril Juthbuck",
        "Half-elven counter clerk at the Aurora's branch beside the Red Gauntlet.",
        (159,), "south_aurora", "Counter clerk",
    ),
    _person(
        "logros_hlandarr", "Logros Hlandarr",
        "Service-mage at the Southern Ward Aurora's branch, described as arrogant.",
        (159,), "south_aurora", "Service-mage",
    ),
    _person(
        "chuldan_helmstar", "Chuldan Helmstar",
        "Third-generation dock trader with fourteen staff; a fence with dual membership in the Fellowship of Salters, Packers, and Joiners and the Guild of Watermen.",
        (173,), "dock_helmstar", "Operator; cargo handler and fence",
    ),
    _person(
        "dandalus_fire_eye_ruell", 'Dandalus "Fire-Eye" Ruell',
        "Former adventurer, curio buyer and winemaker who shares local adventuring lore. His shop ownership is historical, not verified for 1492 DR.",
        (177, 178, 179), "dock_xoblob", "Proprietor",
    ),
    _person(
        "arathka_ruell", "Arathka Ruell",
        "Knowledgeable shopkeeper handling cooking and cleaning; Dandalus's wife, also called Rella.",
        (179,), "dock_xoblob", "Shopkeeper; cook and household operator",
    ),
    _person(
        "hlondaglus_shrim", "Hlondaglus Shrim",
        "Hired wizard protecting the Old Xoblob Shop from inside its hollow stuffed beholder.",
        (178, 179), "dock_xoblob", "Hired wizard; security",
    ),
    _person(
        "jannaxil_serpentil", "Jannaxil Serpentil",
        "Hard-bargaining dealer in rare books, maps and magical texts.",
        (180,), "dock_serpentil", "Proprietor; bookseller",
    ),
    _person(
        "orblaer_thrommox", "Orblaer Thrommox",
        "Warehouse proprietor described as heavily built, bearded and strong.",
        (199,), "dock_red_sails", "Proprietor",
    ),
    _person(
        "gelfuril_the_trader", "Gelfuril the Trader",
        "Soft-spoken trader accepting barter as well as money.",
        (199, 200), "dock_gelfuril", "Proprietor",
    ),
    _person(
        "arleeth_harmeth", "Arleeth Harmeth",
        "Runs the perfume shop with her sister Ilitel.",
        (200,), "dock_house_pride", "Co-proprietress",
    ),
    _person(
        "ilitel_harmeth", "Ilitel Harmeth",
        "Runs the perfume shop with her sister Arleeth.",
        (200,), "dock_house_pride", "Co-proprietress",
    ),
    _person(
        "aglatha_shrey", "Aglatha Shrey",
        "Half-ogre order clerk identified by Elminster's footnote and the people appendix.",
        (200, 214), "dock_aurora", "Order clerk",
    ),
    _person(
        "beradyx_halfwinter", "Beradyx Halfwinter",
        "Footnote identifies him as the mage who teleports goods into the Dock Ward Aurora's branch.",
        (200,), "dock_aurora", "Service-mage",
    ),
    _person(
        "mother_jalyth_hlommorath", "Mother Jalyth Hlommorath",
        "Well-meaning, maternal host of the Blue Mermaid.",
        (200,), "dock_blue_mermaid", "Proprietress",
    ),
    _person(
        "shalath_lythryn", "Shalath Lythryn",
        "Kindly, middle-aged and highly observant innkeeper.",
        (206,), "dock_warm_beds", "Operator",
    ),
    _person(
        "barl_shardrin", "Barl Shardrin",
        "Quiet and attentive host of the Rearing Hippocampus.",
        (207,), "dock_rearing_hippocampus", "Proprietor",
    ),
)
