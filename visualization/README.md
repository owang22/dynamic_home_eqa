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

   No flags, nothing to register, and no restarting. The household list is
   rebuilt from disk on every request, labelled from the trace itself
   (household, type, object and resident counts), and the viewer polls it
   every 5s: a household that finishes while you watch appears by itself,
   and the one you are looking at reloads in place when it is rebuilt
   (a green note says which happened). Starting a second copy simply
   takes the port over from the older one — pass `--keep-existing` if you
   would rather it refuse.

   The panel carries TWO pickers, an object and a resident, each with its
   own live readout — where it is, what it is doing, since when, and for a
   resident what they are carrying. The selected resident is drawn larger
   with an optional dashed path; the strip under the slider shows that
   object's moves (blue, upper) against that resident's activity changes
   (green, lower), so "did she move it, or did it drift while she was out"
   is answerable by eye. The ◀/▶ buttons follow whichever track the little
   dropdown between them names.

   A second page, **`viewer/beliefs.html`**, answers "where does the model
   think this is, and where is it really?" at **any** moment on the slider
   — not only at question times. It reads `belief_trace.json` from beside
   the household's trace.json (written by `python -m baselines.belief_trace`;
   `serve.py` discovers it and publishes the household automatically, so
   there is nothing to register). Three tabs: the focus object on the map
   (gold disc = truth now, ring = what the selected model believes, green
   when they agree and red plus a dashed link when they do not, with an
   optional every-object overlay), a table of all objects scored right now
   sorted wrong-first, and the same instant scored across every model in
   the trace. The strip under the slider plots the share of objects the
   model has right over the whole episode — dips are where the house got
   ahead of what the model had been told. Beliefs are PASSIVE (tour +
   scripted sightings, no sensing), so the picture is the model's own, not
   an artifact of which objects some policy chose to look at.
   Pseudo-receptacles map back for drawing: OUT_OF_HOUSE at the AWAY
   circle, ON_PERSON at the resident's current position.

### The dataset list — `traces.json`, rebuilt by `serve.py`

Both pages read `visualization/traces.json` (via `viewer/datasets.js`) and
build their header dropdown from it; neither has a hardcoded path, and
`serve.py` pins no trace either. Nothing is selected by hand-editing a URL.
`serve.py` regenerates the file at startup and per request. One entry per
timeline; `belief_trace` appears on its own whenever that file exists next
to the trace (a hand-maintained `runs` list, from the older run-log
overlay, is still preserved if present):

```json
{"label": "hh_001 · working_professional_solo · 30 objects, 1 resident · 21d seed 0",
 "trace": "/profiles/revamp_v2/storyfirst/gpt-5.6-terra/hh1/timeline_seed0/trace.json",
 "belief_trace": "/profiles/revamp_v2/storyfirst/gpt-5.6-terra/hh1/timeline_seed0/belief_trace.json"}
```

- `index.html` — one dropdown row per entry; the first is the default. The
  **belief vs truth ▸** link carries the current household AND the object
  you are looking at across, and is inert (with a tooltip saying how to
  generate one) for a household with no belief trace.
- `beliefs.html` — one row per household that has a belief trace, so a
  household with nothing to show is not offered. Generate one with
  `python -m baselines.belief_trace`; its bank comes from
  `python -m baselines.export_bank` or a `baselines.cli fleet` run.

Unpublished files still load through `?trace=&belief=` (plus optional
`&model=&object=` preselects) — the picker then shows that file as a
`(not in traces.json)` row so the dropdown always reflects what is on
screen. Paths may be repo-absolute or relative; the picker matches either
spelling. A missing or broken manifest is not fatal: the pages fall back
to their URL params.

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
