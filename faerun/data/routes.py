"""Named trade arteries of Faerûn.

Explicit routes override or supplement the auto-generated caravan tracks.
`quality` scales freight cost and travel speed:
    1.30 great paved road   (the Trade Way, the High Road, Cormyrean roads)
    1.00 ordinary road
    0.75 poor road / trail
    0.50 wilderness track
`kind` selects the travel mode. The vocabulary is defined by `MODES` in
`faerun.world`:
    teleport permanent portal circles -- near-instant, restricted and costly
    air      skyships and other flying freight -- fast, scarce and dear
    sea      deep-water hulls
    river    river craft
    ferry    short crossings: estuaries, lakes, island hops
    barge    slow bulk haulage on still water
    road     a maintained, drained highway
    trail    unpaved but established going
    track    wilderness caravan going
    tunnel   Underdark passages
    portage  cargo hauled overland between navigable waters

A route may be several of these at once -- join them with `+`, most prominent
first, as in `river+portage` or `tunnel+trail`. That means a single artery the
cargo cannot traverse without changing carrier, so it is charged a transhipment
surcharge, loses time to handling and inherits risk from every mode involved.
It does *not* mean two parallel routes between the same pair; where those
exist the engine simply picks the cheaper.
"""

from __future__ import annotations

# (road name, [settlement ids in order], quality, kind)
NAMED_ROUTES = [
    ("The High Road", [
        "luskan", "port_llast", "neverwinter", "leilon", "waterdeep",
    ], 1.25, "road"),
    ("The Long Road", [
        "mirabar", "longsaddle", "triboar", "red_larch", "amphail", "waterdeep",
    ], 1.1, "road"),
    ("The Trade Way", [
        "waterdeep", "daggerford", "baldur_s_gate", "beregost", "nashkel",
        "athkatla", "zazesspur", "myratma", "memnon", "calimport",
    ], 1.3, "road"),
    ("The Coast Way", ["baldur_s_gate", "candlekeep", "beregost"], 1.05, "road"),
    ("The Dusk Road", [
        "baldur_s_gate", "soubar", "boareskyr_bridge", "triel", "llorkh",
    ], 0.85, "road"),
    ("The Chionthar Road", [
        "baldur_s_gate", "elturel", "scornubel", "hill_s_edge", "berdusk",
        "iriaebor", "proskur", "elversult", "teziir", "westgate",
    ], 1.15, "road"),
    ("The Dawnpost", ["westgate", "suzail", "marsember"], 1.15, "road"),
    ("The Calantar's Way", ["arabel", "suzail", "wheloon"], 1.3, "road"),
    ("The Moonsea Ride", [
        "arabel", "tilverton", "shadowdale", "hillsfar", "zhentil_keep",
    ], 1.05, "road"),
    ("The Way of the Manticore", [
        "highmoon", "essembra", "ashabenford", "archenbridge", "wheloon",
    ], 1.0, "road"),
    ("The North Ride", ["silverymoon", "everlund", "sundabar"], 1.1, "road"),
    ("The Evermoor Way", ["everlund", "nesme", "yartar", "triboar"], 0.95, "road"),
    ("The Silver Way", ["silverymoon", "citadel_felbarr", "citadel_adbar"], 0.95, "road"),
    ("The Mithral Road", ["mithral_hall", "nesme", "silverymoon"], 0.95, "road"),
    ("The Delimbiyr Route", [
        "waterdeep", "secomber", "loudwater", "llorkh", "parnast",
    ], 0.85, "road"),
    ("The Golden Way", ["telflamm", "phsant", "eltabbar"], 1.1, "road"),
    ("The Eastern Shaar Road", ["skuld", "messemprar", "luthcheq", "cimbar"], 1.0, "road"),
    ("The Vilhon Road", ["hlath", "arrabar", "ormpetarr"], 1.0, "road"),
    ("The Amnian Coast Road", [
        "athkatla", "crimmor", "purskul", "esmeltaran", "riatavin",
    ], 1.1, "road"),
    ("The Tethyrian Roads", [
        "zazesspur", "darromar", "saradush",
    ], 1.05, "road"),
    ("The Ten Towns Track", [
        "bryn_shander", "targos", "termalaine", "lonelywood", "easthaven",
        "good_mead",
    ], 0.7, "trail"),
    # Icewind Dale's lifeline: a hard trail that is a frozen sledge road for
    # part of the year and open water across Maer Dualdon for the rest.
    ("The Ten Trail", ["bryn_shander", "luskan"], 0.55, "trail+ferry"),
    ("The Vast Road", [
        "procampur", "tsurlagol", "ravens_bluff", "tantras", "lyrabar",
    ], 1.05, "road"),
    ("The Sembian Roads", [
        "urmlaspyr", "saerloon", "selgaunt", "ordulin", "yhaunn", "procampur",
    ], 1.2, "road"),
    ("The Dalelands Trail", [
        "shadowdale", "ashabenford", "essembra", "myth_drannor", "harrowdale_town",
    ], 0.9, "trail"),

    # ----------------------------------------------------------------- air
    # Halruaa's skyships, and the flying craft of Lantan and Nimbral. Freight
    # is ruinous by the pound but it crosses country nothing else can.
    ("The Halruaan Skyroad", ["halarahh", "innarlith"], 1.0, "air"),
    ("The Lantanna Skybridge", ["lantan", "halarahh"], 0.9, "air"),
    # Chult: cut track through jungle, with river stretches where the trail
    # simply stops at the water and the porters take to canoes.
    ("The Jungle Track", ["port_nyanzaru", "tashluta"], 0.5, "track+river"),

    # ------------------------------------------------------------- rivers
    # The Chionthar is deep and slow enough for barge trains as far as Berdusk,
    # which is why the whole Western Heartlands hangs off it.
    ("The Chionthar", ["baldur_s_gate", "elturel", "scornubel", "berdusk"],
     1.2, "river+barge"),
    # The Shining Falls break the Delimbiyr: everything must come out of the
    # water and go round on waggons before it can float again.
    ("The Delimbiyr", ["daggerford", "secomber", "loudwater"], 1.1, "river+portage"),
    # The Dessarin does not reach the sea at Waterdeep; the last stage is road.
    ("The Dessarin", ["yartar", "red_larch", "waterdeep"], 1.05, "river+road"),
    ("The River Rauvin", ["silverymoon", "everlund", "nesme"], 1.05, "river"),
    # Out of the Moonsea and down the Dragon Reach: river craft, then hulls.
    ("The River Lis", ["mulmaster", "harrowdale_town"], 1.0, "river+sea"),
    ("The Starwater", ["wheloon", "marsember"], 1.1, "river+barge"),
    ("The Alamber Run", ["skuld", "messemprar"], 1.1, "sea"),
    ("The Tesh", ["zhentil_keep", "hillsfar"], 0.95, "river"),

    # -------------------------------------------------------------- tunnels
    ("The Dark Dominion", ["menzoberranzan", "blingdenstone"], 0.7, "tunnel"),
    ("The Duergar Deeps", ["menzoberranzan", "gracklstugh"], 0.6, "tunnel"),
    ("The Derith Run", ["menzoberranzan", "mantol_derith"], 0.6, "tunnel"),
    ("The Deepdark Road", ["mantol_derith", "sshamath"], 0.5, "tunnel"),
    ("Gracklstugh Ore Road", ["gracklstugh", "mantol_derith"], 0.6, "tunnel"),
    # Surface contacts of the Underdark: smugglers' ways. Every one of these is
    # deep passage *and* a furtive overland trail at the far end, and the goods
    # change hands at the cave mouth -- dear, slow and thoroughly dangerous.
    ("Mirabar Underway", ["gracklstugh", "mirabar"], 0.4, "tunnel+trail"),
    ("Menzoberranzan Surface Way", ["menzoberranzan", "nesme"], 0.35, "tunnel+trail"),
    ("Blingdenstone Trail", ["blingdenstone", "silverymoon"], 0.45, "tunnel+trail"),
    ("Sshamath Smugglers' Road", ["sshamath", "secomber"], 0.35, "tunnel+trail"),
    ("Sshamath Deep Way", ["sshamath", "llorkh"], 0.35, "tunnel+trail"),
    # A sunless river runs through the Deepdark; the duergar barge ore on it.
    ("The Darklake Barges", ["gracklstugh", "menzoberranzan"], 0.55, "barge+tunnel"),
]

# Sea lanes that must exist regardless of distance heuristics.
# These are plain "sea" unless a fourth element says otherwise.
NAMED_SEA_LANES = [
    ("The Sword Coast Run", ["luskan", "neverwinter", "waterdeep", "baldur_s_gate",
                             "athkatla", "zazesspur", "memnon", "calimport"], 1.2),
    ("The Shining Sea Run", ["calimport", "almraiven", "suldolphor", "lantan",
                             "tashluta", "port_nyanzaru"], 1.0),
    ("The Nelanther Passage", ["baldur_s_gate", "mintarn", "orlumbor", "waterdeep"], 1.0),
    # Deep-water passage out and back, but island-hopping ferries between the
    # Moonshaes themselves.
    ("The Moonshae Crossing", ["waterdeep", "caer_calidyrr", "caer_corwell",
                               "baldur_s_gate"], 0.95, "sea+ferry"),
    ("The Northern Reach", ["luskan", "ruathym"], 0.85),
    # Nimbral's fliers meet the Lantanna hulls: half the run never touches water.
    ("The Nimbral Run", ["lantan", "nimbral", "velen"], 0.9, "sea+air"),
    ("The Inner Sea Run", ["marsember", "suzail", "urmlaspyr", "saerloon", "selgaunt",
                           "yhaunn", "procampur", "tsurlagol", "ravens_bluff",
                           "tantras", "harrowdale_town", "lyrabar", "telflamm",
                           "bezantur", "velprintalar"], 1.2),
    ("The Dragonmere Ferry", ["urmlaspyr", "westgate"], 1.0, "ferry"),
    ("The Dragonmere", ["westgate", "teziir", "suzail", "marsember"], 1.15),
    ("The Vilhon Passage", ["westgate", "alaghon", "arrabar", "airspur", "cimbar",
                            "messemprar", "bezantur"], 1.05),
    ("The Moonsea Run", ["phlan", "melvaunt", "thentia", "mulmaster", "hillsfar",
                         "zhentil_keep", "elmwood"], 1.05),
]
