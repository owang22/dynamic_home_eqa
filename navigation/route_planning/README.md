# navigation/route_planning/

**Owner: the control-PC agent (Claude Code on Z690).** Part of `navigation/`; same rules (see `../README.md`
and `../../COORDINATION.md`). Moved here from `planning/` on 2026-10-25; `planning/` is now cheetah's
high-level decision making.

What goes here: how the dog gets from where it is to a place it was sent, and the records of when that fails.
Deciding *where* to go and *why* (what to search, which place to visit next) is `../../planning/`, not this.

- the route planner (`go2_nav.py`, `planner.plan()`): A* on a 10 cm grid, 0.28 m clearance with a 0.20 m
  `tight` retry and a 0.12 m `squeeze` retry beyond 1.5 m, a graded cost to stay 0.60 m from obstacles, the
  live-lidar overlay within 3 m, goal snapping and start step-out (board #12, #14, #21);
- `go_to` behaviour in `go2_agent.py`: leg following, replans, speeds (#24, #42);
- gait and turn changes in `go2_agent.py`: rocking turns (`TURN_ROCK_V/S`), the re-plant step (`REPLANT_V/S`),
  shuffle-and-retry on a stall (`SHUFFLES`) (#38);
- place tidying (`go2_tidy.py`) (#42);
- failure logs: `/maps/lab_nav_failures.jsonl` on Z690 (`no_route` / `blocked` records with the live cells that
  closed the route, #28), with summaries and any fixes. Commit summaries and small samples; keep large or
  raw logs on Z690.

**The code itself stays one level up, in `../`** (`go2_nav.py`, `go2_agent.py`, `go2_tidy.py`): the console
modules import each other and are deployed into the driver container as one flat folder, and
`../sync_from_oliver.sh` mirrors that layout. This folder holds route-planning notes, failure summaries and
offline studies.

Related on cheetah: `go2/console/nav_proto.py` is cheetah's offline prototype of a graded-clearance planner and
stand selection (proposed in board #18), not the control PC's code.
