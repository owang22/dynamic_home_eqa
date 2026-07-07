# Before/after render tool: working, and it already found two real things

**STATUS: the tool works — real egocentric RGB + top-down renders,
suspicion-ranked, not a uniform sample. First real use already
surfaced two genuine findings neither the trace log nor the diversity
counting could have caught, plus one real limitation in the tool's own
fallback path.** This is the first rendered pixel checked in this
project's history (per the task's own framing) — everything below is
from actually looking, not inferring from logs.

## What was built

`scripts/render_suspicious_events.py`: for a validated folder, scores
every location-changing event on four real, available signals — cross-
room move, rare (category, anchor) pairing pool-wide, low grounding
confidence, ping-pong return to a recently-left anchor — and renders a
2x2 grid (egocentric RGB before/after, top-down before/after, both
marked with the anchor position) for the top-N by suspicion score, not a
uniform sample. Captioned with the trace's own claim (label, from->to,
t, reason, mover, confidence).

**Two of the five originally-specified suspicion signals are not
implemented — stated as a gap, not silently dropped.** "Collision/
occupancy failure at anchor" and "capability-flagged" have no backing
per-event field anywhere in the current pipeline: `generation_result.
json`'s `grounding_stats` is an aggregate summary (total/accepted/
rejection-rate counts), not a per-event record, confirmed by direct
inspection. Reconstructing either signal after the fact would require
changing generation to emit it, not something this batch's tooling work
does.

**A real infrastructure gap found and worked around, not hidden:**
`embodied/sensor.py`'s `viewpoint_for` — the function the task list said
to reuse — only resolves furniture/slot-level anchors
(`anchor_world_positions`); confirmed directly that a bare room name
like `"bedroom"` (a real, legal `to_semantic` value this project's own
generation produces) is not in that dict at all. Room-level positions
live in a separate dict, `room_centroids`, that `EmbodiedWorld`'s own
occupant-placement code already reads directly. Worked around locally
in `render_suspicious_events.py`'s `resolve_position_and_viewpoint` (a
room-centroid fallback, snapped to the navmesh) rather than changing
`viewpoint_for` itself, which every real experiment in this project also
calls.

## First real run: 4/20 rendered, and the failures are informative too

Top-20 suspicion-ranked events, frozen scene
(`102343992_family_with_kids`): **4 rendered successfully, 16 skipped
with "no resolvable viewpoint."** The skips are a real, reportable
finding, not just a rendering-tool limitation: `viewpoint_for`'s ring-
sampling (radii 0.8-2.5m) found no navigable-and-visible candidate for
several specific furniture anchors (`bedroom.bed`, confirmed directly —
a real position exists in `anchor_world_positions`, but no sightline to
it resolves within the tried radii) and one anchor
(`living_room.tv` — the specific one `stool_1`'s highest-suspicion event
claims to move FROM) has no recorded position in `anchor_world_positions`
at all. Both are properties of this scene's geometry/anchor data, not of
the render tool.

## Two real findings from the four images that did render

**1. Different-sounding anchors can resolve to visually near-identical
viewpoints.** `book_1`'s `dining.table -> office.desk` event (score 3.0,
cross-room + ping-pong) renders BEFORE and AFTER as the same outdoor
patio/trampoline scene — not two visibly distinct rooms. This does not
prove the move itself is wrong (the object's SEMANTIC anchor did change,
per the trace), but it means "cross-room" as computed from
`rooms.slot_room()` does not always correspond to "visibly different
place" from a camera's actual vantage point at these two anchors' viewpoints
— worth knowing before trusting `slot_room`-based cross-room suspicion
scoring (or any downstream spatial-overlap scoring, `B0_answer_semantics.
md`'s own recommendation) as a proxy for real visual/spatial distinctness
without checking.

**2. The room-centroid fallback can produce a degenerate shot.**
`wallet_1`'s `outdoor -> dining.table` event's BEFORE panel (the
`"outdoor"` bare-room anchor, resolved via this tool's own room-centroid
fallback) is a close-up of a blank wall — the snapped navmesh point
landed the camera facing into geometry, not out over the yard. This is a
real limitation of the simple "snap the centroid, look at the centroid"
fallback (no visibility check, unlike `viewpoint_for`'s careful ring
sampling) — usable for now (the tool doesn't crash or silently show a
wrong scene, it shows a genuinely bad framing that's visually obvious as
bad), but a candidate for a real visibility-aware fallback if room-level
before/after shots become a priority.

## What this does and does not establish

**Establishes:** the render tool works end to end on real data — real
GPU rendering (`create_renderer=True`, confirmed via a direct OpenGL
context creation, `NVIDIA RTX PRO 6000 Blackwell`), real geometry, real
suspicion-ranked selection, informative even in its failure mode (a
skip tells you something, not nothing). Two genuine findings surfaced by
looking that neither `generation_diversity.md`'s counting nor
`realism_score_trace.md`'s code-reading could have caught on their own.

**Does not establish:** whether these two rendered examples are
representative of the pool, or unusual. Four images is a smoke test that
the tool works, not a systematic sweep — the natural next step (not this
batch) is running this across more folders/higher top-N once the
`viewpoint_for` resolution rate is itself understood or improved, and
building the human-correlation harness `realism_score_trace.md` already
named as the actual next phase.

**Traceability:** `scripts/render_suspicious_events.py` (suspicion
scoring is pure Python, tested in `tests/test_render_suspicious_events.py`
without habitat_sim; rendering requires habitat_sim + GPU, run under
explore-eqa). Images: `results/reports/suspicious_events/*.png` (4
committed from this first run).
