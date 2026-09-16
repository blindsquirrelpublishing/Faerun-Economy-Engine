"""Merchant houses, workshops and their branch networks."""

from ..models import Business


BUSINESSES = [
    Business(
        "deepwater_scribes_exchange", "Deepwater Scribes' Exchange", "waterdeep",
        ["waterdeep", "candlekeep", "silverymoon", "baldur_s_gate"],
        ["books", "scribal supplies", "arcane stationery"],
        {"paper": "fine", "parchment": "fine", "ink": "fine", "book": "fine",
         "spellbook_blank": "masterwork"}, 1.08,
        "A guild-backed bookseller and binder with counters in western centers of learning.",
    ),
    Business(
        "zulkirate_export_house", "Zulkirate Export House", "eltabbar",
        ["eltabbar", "bezanthur", "hlath", "westgate"],
        ["arcane goods", "reagents", "Thayan manufactures"],
        {"spellbook_blank": "fine", "spell_components": "fine",
         "reagents_rare": "masterwork", "potion_healing": "fine", "incense": "standard"},
        1.14, "A licensed Thayan factor selling regulated magical goods through eastern depots.",
    ),
    Business(
        "golden_sheaf_provisions", "Golden Sheaf Provisions", "goldenfields",
        ["goldenfields", "waterdeep", "daggerford", "yartar"],
        ["milled grain", "bread", "caravan provisions"],
        {"grain": "standard", "flour": "fine", "bread": "fine",
         "meat_salt": "standard", "ale": "standard"}, 0.96,
        "A temple-chartered milling and baking concern supplying northern roads and cities.",
    ),
    Business(
        "ironstar_forge_company", "Ironstar Forge Company", "sundabar",
        ["sundabar", "silverymoon", "waterdeep", "neverwinter"],
        ["steel arms", "armor", "smithing tools"],
        {"steel_ingot": "fine", "sword": "masterwork", "axe_battle": "fine",
         "armor_chain": "fine", "shield": "fine", "tools_carpenter": "fine"}, 1.12,
        "A northern forge company known for consistent steel and warranted weapons.",
    ),
    Business(
        "trade_way_cartwrights", "Trade Way Cartwrights", "scornubel",
        ["scornubel", "daggerford", "baldur_s_gate", "iriaebor"],
        ["carts", "wagons", "road repairs"],
        {"cart": "fine", "wagon": "fine", "barrel": "standard",
         "nails": "standard", "planks": "standard"}, 1.03,
        "A network of cart yards positioned along the busiest caravan exchanges.",
    ),
    Business(
        "amphail_remount_company", "Amphail Remount Company", "amphail",
        ["amphail", "waterdeep", "yartar", "silverymoon"],
        ["riding horses", "warhorse training", "tack"],
        {"horse_riding": "fine", "warhorse": "masterwork", "horse_draft": "fine",
         "saddle": "fine"}, 1.18,
        "Breeders, trainers and remount agents serving nobles, guards and caravan masters.",
    ),
    Business(
        "selgaunt_fine_goods", "Selgaunt Fine Goods Consortium", "selgaunt",
        ["selgaunt", "saerloon", "westgate", "athkatla"],
        ["textiles", "luxury clothing", "perfume"],
        {"cloth_dyed": "fine", "clothing_fine": "masterwork", "silk": "fine",
         "perfume": "fine", "wine_fine": "fine"}, 1.16,
        "A consortium of factors representing Sembian clothiers and luxury workshops.",
    ),
    Business(
        "cimbar_stone_and_scroll", "Cimbar Stone and Scroll", "cimbar",
        ["cimbar", "hlath", "airspur", "arrabar"],
        ["books", "paper", "architectural stone"],
        {"paper": "fine", "book": "fine", "ink": "standard",
         "marble": "fine", "granite": "standard"}, 1.05,
        "A Chessentan partnership combining scholarly imports with builders' materials.",
    ),
]