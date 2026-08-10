# visualization/ — topdown object-trace viewer

Human-debugging visualizer for revamp_v1 household timelines: grounds a
symbolic timeline in a real HSSD scene at **room level** and replays any
object's movement on the scene's topdown map — slider, path, dwell-weighted
trace build-up, autoplay.

Self-contained by design: nothing here imports from the legacy
`dynamic_home_eqa` package or `EXPRESS-Bench` (they were read for
conventions — topdown pixel transform, region annotations, the
`SLOT_ANCHORS` on-surface/floor placement vocabulary — but all code is
rewritten). habitat_sim is needed **only** by the offline bake step.

## Pipeline

1. **`bake_scene.py`** (once per scene; needs habitat_sim — use the
   `fine-eqa` conda env; the `dynamic_eqa` env currently has a broken
   numpy/quaternion ABI):

       /home/nesl/anaconda3/envs/fine-eqa/bin/python bake_scene.py \
           --scene 102343992 --out assets/102343992

   Writes `assets/<scene>/map.png` (navmesh topdown occupancy; light =
   navigable) and `scene.json` (world↔pixel transform, verified against
   sampled navigable points, + room polygons from the scene's
   `semantic_config.json`).

2. **`spatialize.py`** (stdlib + PyYAML; no habitat): grounds one timeline
   using a per-household spatial config (`configs/*.yaml`) that maps
   symbolic rooms → scene regions and places each receptacle at a
   hand-picked fraction of its room's bbox with a placement `relation`
   (`on_surface` / `floor` / `hook` — the ON-the-table vs beside-it-on-the-
   floor distinction; receptacles are NOT yet matched to real scene
   furniture). Regenerates the timeline dir in place:

       python spatialize.py configs/hh_001_102343992.yaml \
           --timeline ../profiles/revamp_v1/claude-fable-5/timelines/hh_001_seed0

   - `events.jsonl` — gains `room_from` / `room_to` / `relation` / `pos`
   - `hourly_rooms.csv` — hourly.csv shape, values are rooms (`outside`
     for ELSEWHERE)
   - `trace.json` — everything the viewer consumes (map transform, room
     polys, receptacle anchors, per-object segments with activity causes)

3. **`serve.py` + `viewer/`** (static HTML/JS/CSS, no external libraries):

       python serve.py            # -> http://127.0.0.1:8710/

   Redirects to the hh_001 pilot. The header dropdown switches between the
   households listed in `traces.json` — add a line there when you publish a
   new timeline. Arbitrary traces also work via
   `viewer/index.html?trace=/profiles/.../trace.json`.

   A second page, **`viewer/beliefs.html`**, overlays a baselines run
   (src/baselines) on the same map: gold disc = the object's true location
   now, ring = the agent's prediction at the last question (green right /
   red wrong, dashed line on a miss), with per-question readout
   (distribution, budget, running accuracy) and a correctness strip under
   the slider. Defaults to the hh_001 grid run
   (`smoke_results/baselines_hh001/`, bank exported by
   `python -m baselines.export_bank`); override via
   `?run=<run_log.jsonl>&trace=<trace.json>&agent=...&object=...`.
   Pseudo-receptacles map back for drawing: OUT_OF_HOUSE at the AWAY
   circle, ON_PERSON at the resident's current position.

## Viewer features

- topdown map cropped to the household's suite, room polygons labeled with
  symbolic id + real region name; receptacle anchors as crosses
- object picker; marker shape encodes placement (disc = on_surface,
  square = floor, triangle = hook); carried-away objects sit at the dashed
  **AWAY (outside)** circle past the entry
- time slider (5-min steps) with per-object event ticks and weekend-tinted
  day boundaries; readout shows time, room, receptacle, placement relation,
  the activity that caused the current placement, and since-when
- **path so far** (polyline of anchor visits) and **trace build-up**
  (translucent discs, radius ∝ √dwell-minutes — which spots the object
  frequents)
- autoplay ▶ with speed control (0.5–15 sim-hours per real second);
  space = play/pause, ←/→ = jump between the object's events

## Scene choice for hh_001

hh_001's narrative is a one-bedroom apartment. The only HSSD scene with its
mesh on disk is `102343992` (the big legacy family house — the other 167
scenes have configs/semantics but no stage GLB), so hh_001 maps onto a
coherent **ground-floor one-bedroom suite** of it: `bedroom.004`,
`bathroom.001`, `kitchen`, `tv` (as living), `hallway.003` (as entry), with
ELSEWHERE in the blank apron outside the suite. To move to a true 1-bed
scene later (e.g. `108736689_177263340`, 4 rooms / 35.6 m²): download its
stage GLB, re-run the bake, copy the config with new room_map/anchors, and
re-run spatialize — nothing else changes.
