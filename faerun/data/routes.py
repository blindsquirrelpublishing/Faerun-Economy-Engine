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

from ..data_store import load_routes, load_sea_lanes

# (road name, [settlement ids in order], quality, kind). Editable at runtime
# via the MCP server's route tools; persisted to faerun/data/store/routes.json
# and faerun/data/store/sea_lanes.json rather than defined here.
NAMED_ROUTES = load_routes()
NAMED_SEA_LANES = load_sea_lanes()
