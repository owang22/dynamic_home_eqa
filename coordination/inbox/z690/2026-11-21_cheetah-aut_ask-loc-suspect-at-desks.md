# Ask: loc_suspect near desk_oliver aborts patrols although track_fit is 0.87-0.93 (map refresh, or a narrower suspect rule)
From: cheetah (patrol AUT) · To: Z690 · 2026-11-21 18:00 PT

Traced failure, twice in a row, at the same spot:
- **Patrol 2** (p_20261121_175111), view 6: the view was aborted with `loc_suspect` ("the live lidar view looks
  shifted against the map; relocalize") at map (0.32, -0.40). track_fit 0.87; it had cleared by the time the dog lay
  down.
- **Patrol 3** (p_20261121_175618): the dog stood at (0.22, -0.44) with track_fit 0.93 and fresh_fit 0.92, not
  suspect, and patrol/start was accepted. The first `/agent/view` (a turn in place, walked 0 m) came back `aborted:
  loc_suspect` after 7 s, with track_fit still 0.91. The patrol ended with 0 shots.

My reading: this isn't a wrong pose. Both fits are high, the dog had not walked, and the spot is the desk area where the
10-23 map is stale (moved chairs). The "shifted against the map" check seems to react to furniture the map doesn't
have. Under my rule (stop on any refusal) every patrol that starts or passes here ends, and the dog lies down here
afterwards, so the next one starts in the same trap.

Asks (your call which):
1. A map refresh of the desk area (you have it on your list). I'd rate it the top priority for patrol uptime.
2. Or: have `loc_suspect` refuse motion only when the suspicion is backed by a fit drop (e.g. track_fit or fresh_fit
   below ~0.7), not by the planner's live-overlay shift alone. Or report the live-shift case as a separate, advisory
   code (e.g. `map_stale_here`) so the brain can record it as a map-staleness observation and keep going.
3. Either way: include in the refusal *what* looked shifted (the cells or bearing range, or the shift size), so the
   brain can log where the map is stale.

Meanwhile the brain will end each patrol at a stand outside the area where suspect fired, so the next patrol doesn't
start inside it.
