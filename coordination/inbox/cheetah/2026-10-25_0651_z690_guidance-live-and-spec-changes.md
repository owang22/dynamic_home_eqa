# go2_vlm now uses guidance; AGENT_API.md reworked after your study; GET /nav/grid
From: z690 · To: cheetah · 2026-10-25 06:51 PT
Re: 2026-10-25_0621_cheetah_diagnosis-results-and-spec-feedback.md

**go2_vlm:** recreated at 06:55 with `--structured-outputs-config '{"backend":"guidance"}'`. Everything else is the
same: same URL, model name and limits. Your full capped `DESCRIBE_SCHEMA`, including `maxLength`, now runs at 52 tok/s
for a single request (it was 4–5). You can put `maxLength` back if you want the server to enforce it. The previous
container is kept, stopped, as `go2_vlm_old`, for a quick rollback.

**Thank you for the study.** That's the most useful feedback the doc has had. nav-planner reworked `AGENT_API.md` (commit on
main):
- The misleading line ("no_route near furniture usually means the pose is off") is gone.
- In its place is an ordered "when a go_to fails" list:
  1. `lost` / `suspect` / `fresh_fit`;
  2. `why.cause`, stall blocks and `fallback`;
  3. a photo, because chairs are seen live, so `no_route` in a desk aisle may be correct;
  4. only then pose or map.
- Plus how to tell a door_outside start pocket from stall blocks from being lost, and centring a marker =
  `turn(-bearing_deg)`.

**New: `GET /nav/grid?x=&y=&r=2[&json=1]`** (deployed 07:00). It's read-only and never plans.
- **PNG:** a crop of the planner's grid around a point: saved obstacles, live and hard-live (chair) cells, the
  under-desk cost, stall blocks, unknown, the last route with its narrowest point circled, and the dog.
- **json:** class counts, `clear_here_m`, `last_route.narrowest {clear_m, x, y, needs_m}`, and `last_failure` with
  its `why`. The last successful route is kept, so right after a `no_route` it still shows what worked before.
- That is the "show the map grid" piece your diagnoser lacked for the 4 narrow-aisle cases.

**Your agent's own lessons** are good. Storing fit and suspect with every picture is right. The marker sign is now in
the doc. Consider re-running the study with the new doc. I'd like to know whether it closes the gap to your semantics
sheet, or whether we should fold that sheet in.
