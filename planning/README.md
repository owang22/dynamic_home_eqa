# planning/

**Owner: the control-PC agent (Claude Code on Z690).** Only that agent edits this folder and pushes it. Others
propose changes with a message in `coordination/inbox/z690/` (see `../COORDINATION.md`).

What goes here: how the dog chooses and carries out a route, and the records of when that fails.

- the route planner (`go2_nav.py`, `planner.plan()`): A* on a 10 cm grid, 0.28 m clearance with a 0.20 m
  `tight` retry, a graded cost to stay 0.60 m from obstacles, the live-lidar overlay within 3 m, goal snapping
  and start step-out (board #12, #14, #21);
- `go_to` behaviour in `go2_agent.py`: leg following, replans, speeds (#24, #42);
- gait and turn changes in `go2_agent.py`: rocking turns (`TURN_ROCK_V/S`), the re-plant step (`REPLANT_V/S`),
  shuffle-and-retry on a stall (`SHUFFLES`) (#38);
- place tidying (`go2_tidy.py`) (#42);
- failure logs: `/maps/lab_nav_failures.jsonl` on Z690 (`no_route` / `blocked` records with the live cells that
  closed the route, #28), with summaries and any fixes. Commit summaries and small samples; keep large or
  raw logs on Z690.

As of 2026-10-23 this code lives only on Z690, in `~/oliver/`. The Z690 agent will add it.

**The split is unclear and is the Z690 agent's to settle.** `go2_agent.py` holds both the agent API
(`navigation/`) and the gait and `go_to` logic (here). Put each file where it fits best, or keep `go2_agent.py`
in one place and point to it from the other README.

Related on cheetah: `go2/console/nav_proto.py` is cheetah's offline prototype of a graded-clearance planner and
stand selection (proposed in board #18), not the control PC's code.
