"""The commodity and product catalogue of Faerûn.

Base prices are expressed in gold pieces for the stated trade unit in a
notional "average" market with balanced supply and demand.  The engine then
adjusts them per settlement.

`produced_by` lists the industry tags that can create the good locally.
`demand` is a per-capita consumption index (1.0 == an everyday staple).
`luxury` is the wealth elasticity: 0 = necessity, 1 = pure luxury.
`perishable` drives spoilage losses over long trade routes.

Harvest, final-demand and warehouse settings below are explicit fictional
modeling assumptions, not canonical Forgotten Realms agricultural research.
Monthly weights run from Hammer through Nightal; the seasonality helpers
normalize them by Harptos month length. Legacy `season` price flags are retained
for the non-inventory model and are not crop consumption calendars.
"""

from __future__ import annotations

from ..models import C

COMMODITIES = [
    # ------------------------------------------------------------------ food
    C("grain", "Grain (wheat)", "food", 0.6, "bushel", 60, "farm", demand=3.0,
      perishable=0.15, season={"autumn": 0.8, "winter": 1.15, "spring": 1.25},
      description="The bread of the Heartlands; the price of everything else follows it."),
    C("corn", "Corn (maize)", "food", 0.7, "bushel", 56, "farm", demand=1.4,
      perishable=0.15, season={"autumn": 0.8, "winter": 1.15, "spring": 1.2},
      description="A common field crop grown wherever the local climate supports farming."),
    C("rice", "Rice", "food", 0.9, "bushel", 60, "farm", demand=1.2, perishable=0.1,
      traits={"jungle": 2.0, "desert": 0.6}, season={"spring": 1.15},
      requires="jungle marsh desert",
      description="Staple of Halruaa, Mulhorand and the southern river deltas."),
    C("flour", "Milled flour", "food", 0.9, "sack", 50, "farm craft", demand=2.2,
      perishable=0.2, season={"spring": 1.2}),
    C("bread", "Bread", "food", 0.02, "loaf", 1, "farm craft", demand=3.2,
      perishable=0.9, season={"spring": 1.2}),
    C("vegetables", "Vegetables", "food", 0.6, "crate", 40, "farm", demand=2.0,
      perishable=0.8, season={"summer": 0.75, "autumn": 0.7, "winter": 1.6}),
    C("fruit", "Fruit", "food", 1.0, "crate", 30, "orchard farm", demand=1.2,
      perishable=0.85, luxury=0.2,
      season={"summer": 0.7, "autumn": 0.65, "winter": 1.9, "spring": 1.4}),
    C("nuts", "Nuts and dried fruit", "food", 2.0, "sack", 40, "orchard", demand=0.7,
      perishable=0.15, season={"autumn": 0.8}),
    C("cheese", "Cheese", "food", 1.2, "wheel", 20, "herd cattle", demand=1.4,
      perishable=0.35),
    C("butter", "Butter", "food", 2.0, "firkin", 25, "cattle", demand=0.9,
      perishable=0.7, season={"summer": 0.85, "winter": 1.3}),
    C("eggs", "Eggs", "food", 0.5, "crate", 15, "farm", demand=1.3, perishable=0.9,
      season={"winter": 1.4}),
    C("meat_fresh", "Fresh meat", "food", 2.0, "side", 40, "cattle herd hunt",
      demand=1.6, perishable=0.95, season={"autumn": 0.85, "spring": 1.2}),
    C("meat_salt", "Salt meat", "food", 6.0, "barrel", 100, "cattle herd salt",
      demand=1.5, perishable=0.1, traits={"port": 1.5, "military": 1.8, "cold": 1.4},
      description="Voyage rations: the lifeblood of fleets, caravans and armies."),
    C("fish_fresh", "Fresh fish", "food", 1.5, "barrel", 60, "fish", demand=1.3,
      perishable=1.0, season={"winter": 1.35}),
    C("fish_salt", "Salted fish", "food", 4.0, "barrel", 100, "fish salt", demand=1.6,
      perishable=0.1, traits={"port": 1.3, "temple": 1.2}),
    C("honey", "Honey", "food", 1.5, "crock", 10, "farm orchard", demand=0.6,
      luxury=0.2, perishable=0.05),
    C("olives", "Olives", "food", 2.5, "barrel", 60, "orchard", demand=0.5,
      perishable=0.3, traits={"desert": 1.4}),
    C("olive_oil", "Olive oil", "food", 4.0, "amphora", 30, "orchard oil", demand=0.8,
      perishable=0.15),
    C("salt", "Salt", "food", 2.5, "sack", 50, "salt", demand=1.4,
      description="Preserves the harvest; whoever holds the salt pans holds the winter."),
    C("sugar", "Sugar loaf", "food", 6.0, "cone", 10, "sugar", demand=0.4,
      luxury=0.6, traits={"noble": 2.0, "jungle": 0.5}),
    C("spices_common", "Common spices", "food", 2.0, "pound", 1, "spice farm",
      demand=0.5, luxury=0.4, traits={"cosmopolitan": 1.5, "noble": 1.8}),
    C("spices_exotic", "Exotic spices", "luxury", 15.0, "pound", 1, "spice", demand=0.12,
      luxury=0.9, traits={"noble": 3.0, "cosmopolitan": 2.0, "mercantile": 1.5},
      description="Saffron, cloves and cinnamon out of Chult, Durpar and the Shining South."),
    C("black_pepper", "Black pepper", "food", 6.0, "pound", 1, "spice",
      demand=0.35, luxury=0.55, traits={"cosmopolitan": 1.5, "mercantile": 1.3},
      requires="jungle"),
    C("long_pepper", "Long pepper", "luxury", 9.0, "pound", 1, "spice",
      demand=0.12, luxury=0.75, traits={"noble": 1.8, "cosmopolitan": 1.5},
      requires="jungle"),
    C("cinnamon", "Cinnamon", "luxury", 12.0, "pound", 1, "spice orchard",
      demand=0.18, luxury=0.8, traits={"noble": 2.0, "cosmopolitan": 1.5},
      requires="jungle"),
    C("cassia", "Cassia bark", "food", 7.0, "pound", 1, "spice orchard",
      demand=0.2, luxury=0.6, traits={"cosmopolitan": 1.4}, requires="jungle"),
    C("cloves", "Cloves", "luxury", 14.0, "pound", 1, "spice orchard",
      demand=0.1, luxury=0.85, traits={"noble": 2.2, "mercantile": 1.4},
      requires="jungle"),
    C("nutmeg", "Nutmeg", "luxury", 16.0, "pound", 1, "spice orchard",
      demand=0.09, luxury=0.9, traits={"noble": 2.4, "cosmopolitan": 1.5},
      requires="jungle"),
    C("mace_spice", "Mace", "luxury", 18.0, "pound", 1, "spice orchard",
      demand=0.07, luxury=0.9, traits={"noble": 2.5, "mercantile": 1.5},
      requires="jungle"),
    C("cardamom", "Cardamom", "luxury", 11.0, "pound", 1, "spice",
      demand=0.13, luxury=0.75, traits={"noble": 1.9, "cosmopolitan": 1.6},
      requires="jungle"),
    C("ginger", "Ginger", "food", 5.0, "pound", 1, "spice farm",
      demand=0.32, luxury=0.45, perishable=0.15,
      traits={"cosmopolitan": 1.4}, requires="jungle"),
    C("turmeric", "Turmeric", "food", 3.5, "pound", 1, "spice farm",
      demand=0.3, luxury=0.35, traits={"temple": 1.3, "cosmopolitan": 1.3},
      requires="jungle desert"),
    C("cumin", "Cumin seed", "food", 2.5, "pound", 1, "spice farm",
      demand=0.4, luxury=0.25, traits={"desert": 1.6, "cosmopolitan": 1.2}),
    C("coriander", "Coriander seed", "food", 2.0, "pound", 1, "spice farm",
      demand=0.42, luxury=0.2, traits={"desert": 1.4, "cosmopolitan": 1.2}),
    C("mustard_seed", "Mustard seed", "food", 1.4, "pound", 1, "farm herb",
      demand=0.55, luxury=0.1, traits={"agrarian": 1.3}),
    C("fennel_seed", "Fennel seed", "food", 1.8, "pound", 1, "farm herb",
      demand=0.35, luxury=0.2, traits={"port": 1.3, "cosmopolitan": 1.2}),
    C("anise", "Anise seed", "food", 2.4, "pound", 1, "herb spice",
      demand=0.25, luxury=0.35, traits={"cosmopolitan": 1.3}),
    C("star_anise", "Star anise", "luxury", 8.0, "pound", 1, "spice orchard",
      demand=0.1, luxury=0.7, traits={"noble": 1.7, "cosmopolitan": 1.5},
      requires="jungle"),
    C("fenugreek", "Fenugreek", "food", 2.2, "pound", 1, "farm herb",
      demand=0.3, luxury=0.2, traits={"desert": 1.5}),
    C("saffron", "Saffron", "luxury", 35.0, "pound", 1, "spice herb",
      demand=0.035, luxury=1.0, traits={"noble": 3.5, "temple": 1.6},
      requires="desert"),
    C("sumac", "Sumac", "food", 2.8, "pound", 1, "herb spice",
      demand=0.28, luxury=0.3, traits={"desert": 1.5, "port": 1.2}),
    C("allspice", "Allspice", "luxury", 10.0, "pound", 1, "spice orchard",
      demand=0.1, luxury=0.75, traits={"noble": 1.8, "mercantile": 1.4},
      requires="jungle"),
    C("vanilla", "Vanilla beans", "luxury", 24.0, "pound", 1, "spice orchard",
      demand=0.06, luxury=0.95, traits={"noble": 3.0, "cosmopolitan": 1.7},
      requires="jungle"),
    C("chili_pepper", "Chili pepper", "food", 3.0, "pound", 1, "spice farm",
      demand=0.38, luxury=0.25, perishable=0.1,
      traits={"jungle": 1.5, "cosmopolitan": 1.2}),
    C("paprika", "Paprika", "food", 3.4, "pound", 1, "spice farm",
      demand=0.34, luxury=0.3, traits={"cosmopolitan": 1.3}),
    C("juniper_berry", "Juniper berries", "food", 2.0, "pound", 1, "herb orchard",
      demand=0.2, luxury=0.2, traits={"cold": 1.5, "frontier": 1.3}),
    C("asafoetida", "Asafoetida", "luxury", 7.5, "pound", 1, "spice herb",
      demand=0.08, luxury=0.65, traits={"desert": 1.6, "cosmopolitan": 1.4},
      requires="desert"),
    C("tea", "Tea and herbal infusions", "food", 3.0, "pound", 1, "herb spice",
      demand=0.3, luxury=0.5, traits={"noble": 1.8, "academic": 1.5}),
    C("coffee", "Coffee beans", "food", 4.0, "pound", 1, "spice orchard",
      demand=0.35, luxury=0.5, perishable=0.1,
      traits={"cosmopolitan": 1.6, "mercantile": 1.4, "academic": 1.3},
      requires="jungle",
      description="Roasted southern beans brewed into a dark, stimulating drink."),

    # ----------------------------------------------------------------- drink
    C("ale", "Ale", "drink", 1.6, "keg", 80, "brew farm", demand=2.4, perishable=0.3,
      traits={"dwarven": 1.8, "military": 1.4, "frontier": 1.3},
      season={"summer": 1.2}),
    C("mead", "Mead", "drink", 2.5, "keg", 80, "brew farm", demand=0.6, luxury=0.2,
      perishable=0.15, traits={"cold": 1.5, "elven": 1.2}),
    C("wine_common", "Table wine", "drink", 4.0, "cask", 100, "vint", demand=1.4,
      luxury=0.3, perishable=0.2, traits={"cosmopolitan": 1.4},
      season={"autumn": 0.8}),
    C("wine_fine", "Fine vintage wine", "luxury", 12.0, "bottle", 3, "vint", demand=0.15,
      luxury=0.95, traits={"noble": 3.5, "elven": 2.0, "cosmopolitan": 1.8},
      description="Saerloonian Glowfire, Berduskan Dark, Evermeet vintages."),
    C("brandy", "Brandy and firewine", "drink", 8.0, "bottle", 3, "distill vint",
      demand=0.3, luxury=0.6, traits={"cold": 1.6, "noble": 1.5}),
    C("dwarven_spirits", "Dwarven spirits", "luxury", 10.0, "jack", 5, "distill brew",
      demand=0.2, luxury=0.7, traits={"dwarven": 3.0, "military": 1.4}),
    C("elverquisst", "Elverquisst", "luxury", 250.0, "bottle", 3, "vint arcane",
      demand=0.02, luxury=1.0, traits={"elven": 4.0, "noble": 2.5}, requires="elven",
      description="Ruby elven liqueur distilled from sunlight and rare fruits."),

    # --------------------------------------------------------------- textile
    C("wool", "Raw wool", "textile", 3.0, "bale", 100, "herd", demand=1.2,
      season={"spring": 0.8, "winter": 1.25}),
    C("linen", "Linen cloth", "textile", 5.0, "bolt", 25, "textile farm", demand=1.1),
    C("cotton", "Cotton", "textile", 4.0, "bale", 100, "farm textile", demand=0.9,
      traits={"desert": 0.7, "jungle": 0.7}),
    C("silk", "Silk", "luxury", 60.0, "bolt", 8, "silk", demand=0.1, luxury=0.95,
      traits={"noble": 3.5, "cosmopolitan": 2.0, "magocracy": 1.6}),
    C("cloth_dyed", "Dyed cloth", "textile", 15.0, "bolt", 20, "textile dye",
      demand=0.6, luxury=0.5, traits={"noble": 2.0, "cosmopolitan": 1.4}),
    C("dye_indigo", "Indigo and common dyes", "material", 8.0, "pound", 1, "dye herb",
      demand=0.25, luxury=0.4),
    C("dye_purple", "Royal purple dye", "luxury", 45.0, "pound", 1, "dye pearl",
      demand=0.05, luxury=1.0, traits={"noble": 4.0, "temple": 1.6}),
    C("clothing_common", "Common clothing", "product", 0.5, "outfit", 4, "textile craft",
      demand=1.8, season={"winter": 1.2}),
    C("clothing_fine", "Fine clothing", "luxury", 15.0, "outfit", 6, "textile craft silk",
      demand=0.12, luxury=0.9, traits={"noble": 3.5, "cosmopolitan": 2.0}),
    C("furs", "Furs", "textile", 20.0, "bundle", 25, "hunt", demand=0.4, luxury=0.6,
      traits={"cold": 2.5, "noble": 2.0},
      season={"winter": 1.5, "autumn": 1.2, "summer": 0.7}),
    C("leather", "Tanned leather", "material", 2.0, "hide", 10, "tan cattle herd",
      demand=1.3),

    # ----------------------------------------------------------------- metal
    C("coal", "Coal", "metal", 0.5, "sack", 60, "mine_coal", demand=1.4,
      traits={"dwarven": 1.6, "cold": 1.5}, season={"winter": 1.5, "autumn": 1.15}),
    C("charcoal", "Charcoal", "material", 1.0, "sack", 40, "log craft", demand=1.2,
      season={"winter": 1.35}),
    C("iron_ore", "Iron ore", "metal", 2.0, "load", 100, "mine_iron", demand=0.8),
    C("iron_ingot", "Wrought iron", "metal", 1.0, "ingot", 10, "smith mine_iron",
      demand=1.5, traits={"dwarven": 1.5, "military": 1.5}),
    C("steel_ingot", "Steel billet", "metal", 3.0, "ingot", 10, "smith", demand=1.0,
      traits={"military": 2.0, "dwarven": 1.6, "frontier": 1.3}),
    C("copper_ingot", "Copper", "metal", 5.0, "ingot", 10, "mine_copper smith",
      demand=0.5),
    C("tin_ingot", "Tin", "metal", 6.0, "ingot", 10, "mine_tin smith", demand=0.35),
    C("lead_ingot", "Lead", "metal", 1.5, "ingot", 10, "mine_copper mine_silver",
      demand=0.3),
    C("silver_ingot", "Silver", "metal", 50.0, "ingot", 10, "mine_silver", demand=0.2,
      luxury=0.6, traits={"temple": 1.8, "noble": 1.6, "mercantile": 1.5}),
    C("gold_ingot", "Gold", "metal", 500.0, "ingot", 10, "mine_gold", demand=0.08,
      luxury=0.8, traits={"noble": 2.5, "mercantile": 2.0, "temple": 1.6}),
    C("mithral_ingot", "Mithral", "metal", 500.0, "ingot", 5, "mine_mithral",
      demand=0.04, luxury=0.7,
      traits={"dwarven": 3.0, "elven": 2.0, "military": 2.0, "arcane": 1.5}),
    C("adamantine_ingot", "Adamantine", "metal", 800.0, "ingot", 5,
      "mine_adamantine", demand=0.02, luxury=0.7,
      traits={"dwarven": 3.0, "military": 2.2, "drow": 2.5}),
    C("nails", "Nails and fittings", "product", 3.0, "keg", 30, "smith", demand=1.0,
      traits={"frontier": 1.5, "port": 1.3}),

    # ------------------------------------------------------------------ gems
    C("gem_agate", "Agate and quartz", "gem", 10.0, "stone", 0.1, "mine_gem", demand=0.15,
      luxury=0.7, traits={"mercantile": 1.5, "arcane": 1.4}),
    C("gem_moonstone", "Moonstone", "gem", 50.0, "stone", 0.1, "mine_gem", demand=0.07,
      luxury=0.9, traits={"elven": 2.0, "arcane": 1.8, "noble": 1.6}),
    C("amber", "Amber", "gem", 100.0, "stone", 0.1, "amber", demand=0.05, luxury=0.95,
      traits={"noble": 2.0, "arcane": 1.6}),
    C("pearl", "Pearls", "gem", 100.0, "pearl", 0.1, "pearl", demand=0.05,
      luxury=0.95, traits={"noble": 2.5, "port": 1.4, "arcane": 1.5}),
    C("gem_emerald", "Emerald", "gem", 1000.0, "stone", 0.1, "mine_gem", demand=0.012,
      luxury=1.0, traits={"noble": 3.0, "arcane": 2.0, "mercantile": 1.8}),
    C("gem_ruby", "Ruby", "gem", 1000.0, "stone", 0.1, "mine_gem", demand=0.012,
      luxury=1.0, traits={"noble": 3.0, "arcane": 2.0, "mercantile": 1.8}),
    C("gem_diamond", "Diamond", "gem", 5000.0, "stone", 0.1, "mine_gem", demand=0.004,
      luxury=1.0, traits={"noble": 3.5, "arcane": 3.0, "temple": 2.0},
      description="Also the component for raise dead — temples buy at any price."),
    C("ivory", "Ivory", "luxury", 100.0, "tusk", 40, "ivory", demand=0.05,
      luxury=0.95, traits={"noble": 2.5, "cosmopolitan": 1.6}),

    # -------------------------------------------------------------- material
    C("timber", "Timber", "material", 3.0, "load", 500, "log", demand=1.6,
      traits={"port": 1.6, "frontier": 1.4}, season={"winter": 1.2}),
    C("planks", "Sawn planks", "material", 5.0, "load", 300, "log craft", demand=1.4),
    C("pitch", "Pitch and tar", "material", 4.0, "barrel", 60, "log ship", demand=0.5,
      traits={"port": 2.5}),
    C("rope", "Hemp rope", "product", 1.0, "coil", 10, "rope farm", demand=0.9,
      traits={"port": 2.0, "mining": 1.5}),
    C("sailcloth", "Sailcloth and canvas", "product", 12.0, "bolt", 30, "textile rope",
      demand=0.3, traits={"port": 3.0}),
    C("bricks", "Bricks", "material", 2.0, "load", 500, "pottery quarry", demand=0.9),
    C("granite", "Dressed granite", "material", 15.0, "block", 800, "quarry", demand=0.5,
      traits={"dwarven": 1.6, "temple": 1.5}),
    C("marble", "Marble", "material", 40.0, "block", 800, "quarry", demand=0.15,
      luxury=0.8, traits={"noble": 2.5, "temple": 2.2, "magocracy": 1.8}),
    C("glassware", "Glassware", "product", 25.0, "crate", 20, "glass", demand=0.3,
      luxury=0.6, perishable=0.05, traits={"noble": 2.0, "alchemy": 1.8, "arcane": 1.5}),
    C("pottery", "Pottery", "product", 3.0, "crate", 40, "pottery", demand=1.1,
      perishable=0.05),
    C("soap", "Soap", "product", 2.0, "box", 10, "craft oil", demand=0.6, luxury=0.3),
    C("candles", "Candles", "product", 2.5, "box", 15, "craft oil temple", demand=1.0,
      traits={"temple": 2.0, "academic": 1.5},
      season={"winter": 1.45, "autumn": 1.15, "summer": 0.8}),
    C("lamp_oil", "Lamp oil", "product", 0.1, "flask", 2, "whale orchard craft", demand=1.2,
      traits={"mining": 1.8, "academic": 1.5},
      season={"winter": 1.4, "summer": 0.85}),
    C("wax", "Beeswax", "material", 3.0, "block", 10, "farm orchard", demand=0.4,
      traits={"temple": 1.8}),
    C("parchment", "Parchment", "material", 0.1, "sheet", 0.05, "tan craft", demand=0.5,
      traits={"academic": 3.0, "arcane": 2.5, "mercantile": 1.8, "temple": 1.6}),
    C("paper", "Paper", "material", 0.2, "sheet", 0.05, "paper craft", demand=0.5,
      traits={"academic": 3.0, "arcane": 2.0, "mercantile": 2.0}),
    C("ink", "Ink", "product", 8.0, "vial", 0.5, "craft alch", demand=0.2,
      luxury=0.4, traits={"academic": 3.5, "arcane": 2.5, "mercantile": 2.0}),
    C("book", "Bound book", "luxury", 25.0, "volume", 3, "paper craft", demand=0.1,
      luxury=0.85, traits={"academic": 4.0, "arcane": 2.5, "noble": 2.0, "temple": 1.8}),
    C("incense", "Incense", "luxury", 5.0, "block", 1, "spice temple", demand=0.3,
      luxury=0.6, traits={"temple": 3.5, "arcane": 2.0}),
    C("perfume", "Perfume", "luxury", 12.0, "vial", 0.5, "alch spice", demand=0.1,
      luxury=0.95, traits={"noble": 3.5, "cosmopolitan": 2.0}),

    # ------------------------------------------------------------- livestock
    C("chicken", "Chickens", "livestock", 0.02, "bird", 3, "farm", demand=1.4,
      perishable=0.4),
    C("sheep", "Sheep", "livestock", 2.0, "head", 8, "herd", demand=0.7),
    C("pig", "Swine", "livestock", 3.0, "head", 12, "farm herd", demand=0.8),
    C("cow", "Cattle", "livestock", 10.0, "head", 15, "cattle", demand=0.6),
    C("ox", "Ox", "livestock", 15.0, "head", 15, "cattle farm", demand=0.5,
      traits={"agrarian": 2.0, "frontier": 1.5}),
    C("mule", "Mule", "livestock", 8.0, "head", 10, "farm horse", demand=0.6,
      traits={"mining": 2.0, "mercantile": 1.8, "frontier": 1.6}),
    C("pony", "Pony", "livestock", 30.0, "head", 12, "horse", demand=0.3,
      traits={"halfling": 2.5, "gnome": 2.0}),
    C("horse_draft", "Draft horse", "livestock", 50.0, "head", 15, "horse", demand=0.5,
      traits={"agrarian": 1.8, "mercantile": 1.6}),
    C("horse_riding", "Riding horse", "livestock", 75.0, "head", 15, "horse", demand=0.4,
      luxury=0.3, traits={"military": 1.8, "noble": 2.0, "frontier": 1.5}),
    C("warhorse", "Warhorse", "livestock", 400.0, "head", 20, "horse", demand=0.08,
      luxury=0.5, traits={"military": 3.5, "noble": 2.5, "mercenary": 2.5}),
    C("camel", "Camel", "livestock", 50.0, "head", 15, "herd horse", demand=0.15,
      traits={"desert": 4.0, "mercantile": 1.4}, requires="desert"),
    C("hunting_dog", "Trained dog", "livestock", 25.0, "head", 6, "hunt farm",
      demand=0.15, traits={"noble": 1.8, "frontier": 1.5}),

    # ---------------------------------------------------------------- tools
    C("tools_carpenter", "Artisan's tools", "product", 8.0, "kit", 15, "craft smith",
      demand=0.5, traits={"frontier": 1.5}),
    C("plow", "Iron-shod plow", "product", 12.0, "plow", 100, "smith craft", demand=0.3,
      traits={"agrarian": 3.0}, season={"spring": 1.35, "winter": 0.85}),
    C("cart", "Cart", "product", 15.0, "cart", 200, "craft", demand=0.25),
    C("wagon", "Wagon", "product", 35.0, "wagon", 400, "craft smith", demand=0.15,
      traits={"mercantile": 2.5, "frontier": 1.5}),
    C("barrel", "Barrel (empty)", "product", 2.0, "barrel", 70, "craft log", demand=0.9,
      traits={"port": 1.6, "mercantile": 1.5}),
    C("saddle", "Saddle and tack", "product", 10.0, "saddle", 25, "tan craft",
      demand=0.25, traits={"military": 1.8, "frontier": 1.5}),
    C("lantern", "Hooded lantern", "product", 5.0, "lantern", 2, "smith glass",
      demand=0.3, traits={"mining": 2.0, "port": 1.4}),
    C("fishing_net", "Fishing net", "product", 4.0, "net", 20, "rope textile",
      demand=0.2, traits={"port": 2.5}),
    C("ship_boat", "River boat", "product", 800.0, "boat", 4000, "ship", demand=0.01,
      traits={"port": 3.0, "mercantile": 2.0}),

    # ------------------------------------------------------------------ arms
    C("dagger", "Dagger", "arms", 2.0, "blade", 1, "weapon smith", demand=0.5,
      traits={"military": 2.0, "frontier": 1.6, "mercenary": 2.0}),
    C("sword", "Longsword", "arms", 15.0, "blade", 3, "weapon smith", demand=0.25,
      traits={"military": 3.0, "mercenary": 3.0, "frontier": 1.8, "noble": 1.5}),
    C("axe_battle", "Battleaxe", "arms", 10.0, "axe", 4, "weapon smith", demand=0.2,
      traits={"military": 2.5, "dwarven": 2.5, "orc": 2.5, "mercenary": 2.5}),
    C("spear", "Spear", "arms", 1.0, "spear", 3, "weapon smith craft", demand=0.5,
      traits={"military": 3.0, "frontier": 2.0}),
    C("bow_short", "Shortbow", "arms", 25.0, "bow", 2, "weapon craft", demand=0.15,
      traits={"military": 2.0, "elven": 2.5, "hunt": 2.0}),
    C("bow_long", "Longbow", "arms", 50.0, "bow", 2, "weapon craft", demand=0.1,
      traits={"military": 2.5, "elven": 3.0}),
    C("crossbow", "Crossbow", "arms", 25.0, "crossbow", 5, "weapon smith craft",
      demand=0.12, traits={"military": 2.5, "dwarven": 2.0, "gnome": 2.0}),
    C("arrows", "Arrows", "arms", 1.0, "sheaf", 1, "weapon craft", demand=0.8,
      traits={"military": 3.5, "frontier": 2.0, "mercenary": 2.5}),
    C("armor_leather", "Leather armor", "arms", 10.0, "suit", 10, "tan armor",
      demand=0.3, traits={"military": 2.5, "mercenary": 2.5, "frontier": 1.8}),
    C("armor_chain", "Chain mail", "arms", 75.0, "suit", 55, "armor smith", demand=0.1,
      traits={"military": 3.0, "mercenary": 3.0, "dwarven": 2.0}),
    C("armor_plate", "Plate armor", "arms", 1500.0, "suit", 65, "armor smith",
      demand=0.015, luxury=0.6,
      traits={"military": 3.0, "noble": 3.0, "temple": 1.6}),
    C("shield", "Shield", "arms", 10.0, "shield", 6, "armor smith craft", demand=0.3,
      traits={"military": 3.0, "mercenary": 2.5}),

    # ---------------------------------------------------------------- arcane
    C("herbs_healing", "Medicinal herbs", "arcane", 3.0, "bundle", 2, "herb farm",
      demand=0.6, traits={"temple": 2.0, "military": 1.8, "wartorn": 2.5}),
    C("antitoxin", "Antitoxin", "arcane", 25.0, "vial", 0.5, "alch herb", demand=0.06,
      luxury=0.5, traits={"jungle": 2.5, "arcane": 1.6, "drow": 2.5}),
    C("potion_healing", "Potion of healing", "arcane", 50.0, "vial", 0.5, "alch arcane",
      demand=0.05, luxury=0.6,
      traits={"arcane": 2.5, "temple": 2.5, "military": 2.0, "wartorn": 3.0,
              "frontier": 1.8}),
    C("holy_water", "Holy water", "arcane", 25.0, "flask", 1, "temple", demand=0.05,
      traits={"temple": 4.0, "frontier": 1.5}),
    C("spell_components", "Spell components", "arcane", 25.0, "pouch", 2,
      "arcane alch herb", demand=0.06, luxury=0.5,
      traits={"arcane": 4.0, "magocracy": 3.5, "academic": 2.0}),
    C("arcane_focus", "Arcane focus", "arcane", 10.0, "focus", 1, "arcane craft",
      demand=0.04, traits={"arcane": 4.0, "academic": 2.0}),
    C("reagents_rare", "Rare reagents", "arcane", 150.0, "case", 5, "arcane alch",
      demand=0.02, luxury=0.8,
      traits={"arcane": 4.0, "magocracy": 4.0, "academic": 2.0}),
    C("spellbook_blank", "Blank spellbook", "arcane", 50.0, "book", 3, "paper",
      demand=0.02, luxury=0.7, traits={"arcane": 4.0, "academic": 3.0},
      description="A durable vellum or prepared-paper volume made by specialist binders in major scribal and magical centers."),
    C("smokepowder", "Smokepowder", "exotic", 400.0, "keg", 20, "alch arcane",
      demand=0.01, luxury=0.6,
      traits={"military": 3.0, "gnome": 2.5, "mercantile": 1.5}, requires="gnome",
      description="A Lantanna secret; illegal or terrifying nearly everywhere else."),

    # ---------------------------------------------------------------- exotic
    C("teak", "Chultan teak", "exotic", 25.0, "load", 400, "log", demand=0.1,
      luxury=0.6, traits={"port": 2.0, "noble": 2.0, "jungle": 0.4}, requires="jungle"),
    C("dinosaur_hide", "Dinosaur hide", "exotic", 60.0, "hide", 30, "hunt tan",
      demand=0.04, luxury=0.8, traits={"jungle": 0.5, "noble": 2.0, "military": 1.5},
      requires="jungle"),
    C("chultan_fruit", "Chultan fruit", "exotic", 6.0, "crate", 30, "orchard", demand=0.1,
      luxury=0.7, perishable=0.95, traits={"jungle": 0.3, "noble": 2.0}, requires="jungle"),
    C("whale_oil", "Whale oil", "exotic", 12.0, "barrel", 60, "whale", demand=0.25,
      traits={"cold": 1.6, "port": 1.6, "academic": 1.4},
      season={"winter": 1.4, "summer": 0.85}),
    C("scrimshaw", "Knucklehead scrimshaw", "exotic", 30.0, "piece", 5, "craft fish",
      demand=0.05, luxury=0.9, traits={"noble": 2.2, "cold": 0.5, "cosmopolitan": 1.8},
      requires="tundra taiga cold",
      description="Carved knucklehead trout ivory out of Icewind Dale."),
    C("spider_silk", "Underdark spider silk", "exotic", 90.0, "bolt", 6, "silk",
      demand=0.03, luxury=0.9, traits={"drow": 3.0, "noble": 1.6, "arcane": 1.5},
      requires="cavern drow"),
    C("faerzress_crystal", "Faerzress crystal", "exotic", 220.0, "crystal", 3,
      "mine_gem arcane", demand=0.015, luxury=0.85,
      traits={"drow": 3.0, "arcane": 3.0, "magocracy": 2.5}, requires="cavern drow"),
]

COMMODITIES_BY_ID = {c.id: c for c in COMMODITIES}

# Input quantities make one trade unit of the output. They are deliberately
# simple economic recipes rather than workshop-level instructions.
SIMPLE_BOMS = {
  "flour": {"grain": 0.9},
  "bread": {"flour": 0.02, "salt": 0.001},
  "meat_salt": {"meat_fresh": 2.5, "salt": 0.2},
  "fish_salt": {"fish_fresh": 1.7, "salt": 0.2},
  "olive_oil": {"olives": 0.7},
  "ale": {"grain": 0.8},
  "mead": {"honey": 0.6},
  "wine_common": {"fruit": 3.5},
  "wine_fine": {"wine_common": 0.03},
  "brandy": {"wine_common": 0.08},
  "dwarven_spirits": {"grain": 0.08},
  "cloth_dyed": {"linen": 1.0, "dye_indigo": 0.25},
  "clothing_common": {"linen": 0.15},
  "clothing_fine": {"cloth_dyed": 0.25, "silk": 0.1},
  "charcoal": {"timber": 0.12},
  "iron_ingot": {"iron_ore": 0.15, "charcoal": 0.04},
  "steel_ingot": {"iron_ingot": 1.0, "coal": 0.04},
  "nails": {"iron_ingot": 3.0},
  "planks": {"timber": 0.65},
  "pitch": {"timber": 0.12},
  "sailcloth": {"linen": 1.2, "rope": 0.5},
  "glassware": {"coal": 0.05},
  "soap": {"olive_oil": 0.25, "salt": 0.03},
  "candles": {"wax": 1.5},
  "lamp_oil": {"olive_oil": 0.07},
  "parchment": {"leather": 0.005},
  "paper": {"timber": 0.0002},
  "ink": {"charcoal": 0.01, "olive_oil": 0.01},
  "book": {"paper": 100.0, "leather": 0.25, "ink": 0.25},
  "incense": {"spices_common": 0.5, "charcoal": 0.01},
  "perfume": {"spices_exotic": 0.1, "olive_oil": 0.02},
  "warhorse": {"horse_riding": 1.0, "grain": 20.0, "saddle": 1.0},
  "tools_carpenter": {"steel_ingot": 1.0, "planks": 0.02},
  "plow": {"iron_ingot": 5.0, "planks": 0.15},
  "cart": {"planks": 0.5, "nails": 0.2},
  "wagon": {"planks": 1.0, "nails": 0.5, "iron_ingot": 1.0},
  "barrel": {"planks": 0.2, "iron_ingot": 0.1},
  "saddle": {"leather": 2.0, "iron_ingot": 0.2},
  "lantern": {"iron_ingot": 0.15, "glassware": 0.05},
  "fishing_net": {"rope": 2.0},
  "ship_boat": {"planks": 8.0, "nails": 4.0, "rope": 5.0, "sailcloth": 2.0},
  "dagger": {"steel_ingot": 0.12, "leather": 0.03},
  "sword": {"steel_ingot": 0.3, "leather": 0.08},
  "axe_battle": {"steel_ingot": 0.35, "planks": 0.01},
  "spear": {"steel_ingot": 0.08, "planks": 0.01},
  "bow_short": {"planks": 0.005, "rope": 0.01},
  "bow_long": {"planks": 0.007, "rope": 0.012},
  "crossbow": {"steel_ingot": 0.2, "planks": 0.01, "rope": 0.01},
  "arrows": {"planks": 0.003, "steel_ingot": 0.03},
  "armor_leather": {"leather": 1.0},
  "armor_chain": {"steel_ingot": 5.5},
  "armor_plate": {"steel_ingot": 6.5, "leather": 0.5},
  "shield": {"planks": 0.015, "iron_ingot": 0.4, "leather": 0.1},
  "antitoxin": {"herbs_healing": 0.1, "ink": 0.02},
  "potion_healing": {"herbs_healing": 0.2, "honey": 0.02},
  "arcane_focus": {"gem_agate": 0.1, "silver_ingot": 0.02},
  "spellbook_blank": {"paper": 150.0, "leather": 1.0, "ink": 1.0},
  "smokepowder": {"charcoal": 0.2, "salt": 0.1},
  "scrimshaw": {"ivory": 0.1},
}

for commodity_id, components in SIMPLE_BOMS.items():
  COMMODITIES_BY_ID[commodity_id].bom = dict(components)

# Surface harvests change timing, not annual potential or production eligibility.
# Cold harvests are later/shorter, irrigated arid harvests avoid high summer, and
# tropical districts can supply several harvest windows. Underground agriculture
# uses its existing resource gates without inheriting a surface winter.
_HARVEST_CALENDARS = {
    "grain": {
        "temperate": [0, 0, 0, 0, 0, 0, 0.5, 3, 5, 1.5, 0, 0],
        "cold": [0, 0, 0, 0, 0, 0, 0, 0, 3, 7, 0, 0],
        "arid": [0, 0, 1, 4, 4, 1, 0, 0, 0, 0, 0, 0],
        "tropical": [0, 1, 3, 1, 0, 0, 0, 1, 3, 1, 0, 0],
    },
    "corn": {
        "temperate": [0, 0, 0, 0, 0, 0, 0, 1, 4, 4, 1, 0],
        "cold": [0, 0, 0, 0, 0, 0, 0, 0, 1, 7, 2, 0],
        "arid": [0, 0, 0, 1, 3, 1, 0, 0, 0, 1, 3, 1],
        "tropical": [0, 0, 1, 3, 1, 0, 0, 0, 1, 3, 1, 0],
    },
    "rice": {
        "temperate": [0, 0, 0, 0, 0, 0, 0, 0, 4, 5, 1, 0],
        "cold": [0, 0, 0, 0, 0, 0, 0, 0, 2, 8, 0, 0],
        "arid": [0, 0, 0, 1, 4, 1, 0, 0, 0, 1, 4, 1],
        "tropical": [0, 0, 1, 3, 1, 0, 0, 1, 3, 1, 0, 0],
    },
    "vegetables": {
        "temperate": [0, 0, 0.1, 0.4, 1, 2, 3, 3, 3, 2, 0.5, 0],
        "cold": [0, 0, 0, 0, 0, 0.3, 2, 4, 3, 0.7, 0, 0],
        "arid": [1, 2, 3, 2, 1, 0.2, 0.1, 0.2, 1, 2, 3, 2],
        "tropical": [1, 1, 1.5, 2, 1.5, 1, 1, 1, 1.5, 2, 1.5, 1],
    },
    "fruit": {
        "temperate": [0, 0, 0, 0, 0.2, 1, 2, 3, 4, 2, 0, 0],
        "cold": [0, 0, 0, 0, 0, 0, 0.5, 2, 4, 1, 0, 0],
        "arid": [0.3, 0.5, 1, 2, 2, 1, 0.2, 0.5, 2, 3, 2, 0.5],
        "tropical": [1, 1, 2, 2, 1, 1, 1, 1, 2, 2, 1, 1],
    },
    "nuts": {
        "temperate": [0, 0, 0, 0, 0, 0, 0, 0.5, 3, 5, 1.5, 0],
        "cold": [0, 0, 0, 0, 0, 0, 0, 0, 1, 7, 2, 0],
        "arid": [0, 0, 0, 0, 0, 0, 1, 3, 4, 2, 0, 0],
        "tropical": [0.5, 1, 2, 1, 0.5, 0.5, 0.5, 1, 2, 1, 0.5, 0.5],
    },
    "olives": {
        "temperate": [0.5, 0, 0, 0, 0, 0, 0, 0, 0, 2, 5, 2.5],
        "cold": [0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 6, 3],
        "arid": [0, 0, 0, 0, 0, 0, 0, 0, 1, 4, 4, 1],
        "tropical": [1, 1, 2, 1, 0.5, 0.5, 1, 1, 2, 1, 0.5, 0.5],
    },
    "herbs": {
        "temperate": [0, 0, 0.2, 0.8, 2, 3, 3, 2, 1, 0.2, 0, 0],
        "cold": [0, 0, 0, 0, 0, 1, 3, 4, 2, 0, 0, 0],
        "arid": [0.5, 1, 3, 3, 1, 0.1, 0.1, 0.2, 1, 2, 1, 0.5],
        "tropical": [1, 1, 2, 2, 1, 1, 1, 1, 2, 2, 1, 1],
    },
    "seed_spices": {
        "temperate": [0, 0, 0, 0, 0, 1, 2, 3, 3, 1, 0, 0],
        "cold": [0, 0, 0, 0, 0, 0, 0, 1, 5, 4, 0, 0],
        "arid": [0, 1, 3, 4, 2, 0, 0, 0, 0, 0, 0, 0],
        "tropical": [0, 1, 2, 2, 0, 0, 0, 1, 2, 2, 0, 0],
    },
    "tropical_spices": {
        "temperate": [0, 0, 0, 0, 0.5, 1, 2, 3, 2, 1, 0.5, 0],
        "cold": [0, 0, 0, 0, 0, 0, 1, 3, 4, 2, 0, 0],
        "arid": [0.5, 1, 2, 2, 0.5, 0, 0, 0, 0.5, 1, 2, 0.5],
        "tropical": [1, 2, 3, 2, 1, 0.5, 1, 2, 3, 2, 1, 0.5],
    },
    "coffee": {
        "temperate": [0, 0, 0, 0, 0, 0, 0.5, 2, 4, 3, 0.5, 0],
        "cold": [0, 0, 0, 0, 0, 0, 0, 0, 2, 5, 3, 0],
        "arid": [1, 3, 3, 1, 0, 0, 0, 0, 0, 0, 1, 1],
        "tropical": [1, 3, 4, 2, 0.5, 0.2, 1, 3, 4, 2, 0.5, 0.2],
        "chult": [1, 3, 4, 2, 0.5, 0.2, 1, 3, 4, 2, 0.5, 0.2],
        "halruaa": [0.5, 0.2, 1, 3, 4, 2, 0.5, 0.2, 1, 3, 4, 2],
    },
    "cotton": {
        "temperate": [0, 0, 0, 0, 0, 0, 0, 1, 3, 4, 2, 0],
        "cold": [0, 0, 0, 0, 0, 0, 0, 0, 1, 5, 4, 0],
        "arid": [0, 0, 0, 0, 0, 0, 0, 0.5, 2, 4, 3, 0.5],
        "tropical": [2, 3, 2, 0.5, 0, 0, 0, 0, 0, 0.5, 1, 2],
    },
    "wool": {
        "temperate": [0, 0, 0, 1, 5, 4, 0, 0, 0, 0, 0, 0],
        "cold": [0, 0, 0, 0, 1, 5, 4, 0, 0, 0, 0, 0],
        "arid": [0, 1, 4, 4, 1, 0, 0, 0, 0, 0, 0, 0],
        "tropical": [0, 0, 1, 3, 1, 0, 0, 0, 1, 3, 1, 0],
    },
}
_HARVEST_GOODS = {
    "grain": "grain",
    "corn": "corn",
    "rice": "rice",
    "vegetables": "vegetables",
    "fruit": "fruit chultan_fruit",
    "nuts": "nuts",
    "olives": "olives",
    "herbs": "herbs_healing tea spices_common",
    "seed_spices": "cumin coriander mustard_seed fennel_seed anise fenugreek",
    "tropical_spices": (
        "spices_exotic black_pepper long_pepper cinnamon cassia cloves nutmeg "
        "mace_spice cardamom ginger turmeric star_anise allspice vanilla"
    ),
    "coffee": "coffee",
    "cotton": "cotton",
    "wool": "wool",
}
_HARVEST_GOODS["fruit"] += " chili_pepper juniper_berry sumac"
_HARVEST_GOODS["herbs"] += " asafoetida"
_HARVEST_CALENDARS["saffron"] = {
    "temperate": [0, 0, 0, 0, 0, 0, 0, 0, 1, 5, 4, 0],
    "arid": [0, 0, 0, 0, 0, 0, 0, 0, 2, 5, 3, 0],
}
_HARVEST_GOODS["saffron"] = "saffron"

for calendar_id, goods in _HARVEST_GOODS.items():
    calendar = _HARVEST_CALENDARS[calendar_id]
    for commodity_id in goods.split():
        commodity = COMMODITIES_BY_ID[commodity_id]
        commodity.production_profile = list(calendar["temperate"])
        commodity.regional_production_profiles = {
            climate: list(weights) for climate, weights in calendar.items()
            if climate != "temperate"
        }
        commodity.regional_production_profiles["underdark"] = []

# Consumption curves are deliberately limited to uses with seasonal demand.
# Crop scarcity price flags do NOT imply that people eat less bread in winter.
# Workshops, mills, roasters-as-workshops, brewers and alchemists have no annual
# shutdown: only the harvested aggregate coffee good above follows crop supply;
# the existing catalogue has no separate green-bean/roasting production chain.
_DEMAND_CALENDARS = {
    "heating": [1.5, 1.4, 1.15, 1, 0.85, 0.7, 0.65, 0.7, 0.9, 1.1, 1.3, 1.45],
    "lighting": [1.35, 1.25, 1.1, 1, 0.9, 0.8, 0.75, 0.8, 1, 1.1, 1.2, 1.35],
    "warm_goods": [1.25, 1.2, 1.1, 1, 0.9, 0.8, 0.75, 0.8, 1, 1.15, 1.25, 1.3],
    "summer_drink": [0.95, 0.95, 1, 1, 1, 1.1, 1.15, 1.1, 1, 1, 0.95, 0.95],
    "spring_tools": [0.9, 1, 1.25, 1.3, 1.2, 1, 0.95, 0.95, 1, 1, 0.9, 0.85],
}
for calendar_id, goods in {
    "heating": "coal charcoal",
    "lighting": "candles lamp_oil whale_oil",
    "warm_goods": "clothing_common furs wool",
    "summer_drink": "ale",
    "spring_tools": "plow",
}.items():
    for commodity_id in goods.split():
        COMMODITIES_BY_ID[commodity_id].demand_profile = list(_DEMAND_CALENDARS[calendar_id])

# Storage days are capacity in baseline daily-use units, not a hard expiration
# date. Loss is a fraction of stock per day; reserves are baseline days of use.
# Live animals remain outside warehouse carryover (feeding is not modeled here).
for commodity in COMMODITIES:
    if commodity.category != "livestock":
        commodity.storage_days = 365
        commodity.storage_loss = 0.0001
        commodity.reserve_days = 15

_STORAGE_POLICIES = [
    ("grain corn rice", 400, 0.0003, 75),
    ("flour", 120, 0.002, 20),
    ("bread", 3, 0.25, 0.5),
    ("vegetables", 14, 0.05, 2),
    ("fruit chultan_fruit", 10, 0.08, 1),
    ("nuts", 270, 0.001, 30),
    ("cheese", 90, 0.004, 10),
    ("butter", 14, 0.04, 2),
    ("eggs", 21, 0.025, 3),
    ("meat_fresh fish_fresh", 2, 0.35, 0.25),
    ("meat_salt fish_salt olives", 180, 0.0015, 30),
    ("honey sugar salt", 730, 0.00005, 45),
    ("olive_oil lamp_oil whale_oil", 365, 0.0008, 30),
    ("ale", 60, 0.006, 7),
    ("mead wine_common", 365, 0.0005, 30),
    ("wine_fine brandy dwarven_spirits elverquisst", 730, 0.0001, 30),
    ("herbs_healing tea", 270, 0.0015, 60),
    ("antitoxin potion_healing holy_water reagents_rare spell_components", 730, 0.0001, 30),
    ("coffee", 60, 0.012, 7),
    ("cotton wool linen cloth_dyed furs", 400, 0.0004, 45),
    ("coal charcoal timber wax", 400, 0.0001, 45),
]
_SPICE_GOODS = (
    "spices_common spices_exotic black_pepper long_pepper cinnamon cassia cloves "
    "nutmeg mace_spice cardamom ginger turmeric cumin coriander mustard_seed "
    "fennel_seed anise star_anise fenugreek saffron sumac allspice vanilla "
    "chili_pepper paprika juniper_berry asafoetida"
)
_STORAGE_POLICIES.append((_SPICE_GOODS, 365, 0.0008, 45))
# Coffee's description explicitly says roasted: allow weeks, not the many
# months appropriate to green beans. Do not invent a second catalogue good.
for goods, days, loss, reserve in _STORAGE_POLICIES:
    for commodity_id in goods.split():
        commodity = COMMODITIES_BY_ID[commodity_id]
        commodity.storage_days = days
        commodity.storage_loss = loss
        commodity.reserve_days = reserve

CATEGORIES = sorted({c.category for c in COMMODITIES})
