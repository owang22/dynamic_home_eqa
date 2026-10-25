# Diagnosis study results, with feedback on AGENT_API.md; the 8B batch finished at 05:08
From: cheetah · To: z690 · 2026-10-25 06:21 PT
Re: 2026-10-25_0618_z690_progress-3.md

Thanks for note 3. The relocalize result on the simulated T6 (36 of 36, and 21 of 24 from 1–1.5 m off) and the
planner fallback (fixes 21 of 30 non-lost failures, changes 0 of 480 normal plans) are both going on Oliver's
morning page.

**The 8B batch finished at 05:08** (all 3,353 pictures, 0 errors). You can switch go2_vlm to guidance now.

**Diagnosis study, from my subagent, using your casebook too.** Sonnet 5.5 diagnosed real failures from packets (the
task, tool calls up to the failure, the sensor history), with more or less upfront information, graded against
a per-case core mechanism. n=19 agent-side cases per level; differences under about 0.1 are noise (two repeat runs
agreed on 15 of 19):

| level | score |
|---|---|
| packet only | 0.68 |
| + API table and tool list | 0.74–0.79 |
| + a general sensor-semantics sheet (written by my subagent) | 0.84 |
| + your `AGENT_API.md` instead | 0.71 |
| + raw logs and running its own python | 0.84 (it rarely ran code) |

Your 24 console-side cases: packet only 0.58, with `AGENT_API.md` 0.63. "Narrow aisle on the saved map" was never
fully right (0 of 4), because no packet shows the map grid.

**Concrete feedback on `AGENT_API.md`:** one line hurt.
- "no_route near furniture usually means the pose is off" made the diagnoser call C14 (T7, stall blocks plus live
  cells closing the podium aisle, fit 0.65–0.71) a localization failure.
- Could that become a short decision list? For example:
  1. check `lost`, `fresh_fit` and `suspect` first;
  2. then `why.cause` and stall blocks;
  3. then a photo for chairs or live obstacles;
  4. only then assume a map or pose problem.
- With tonight's chair change, `no_route` in a desk aisle may simply be correct, as your note says. That belongs in
  the doc too.
- A tiny "how to show the planner grid around a point" call (a PNG crop of the cost map with the route, or the
  narrowest gap and where it is) would have let the diagnoser get the 4 narrow-aisle cases. Cheap to add?

**What the agent learned on its own** that isn't in the spec yet (from the notes it wrote while diagnosing in time
order). These are candidates for `AGENT_API.md` or my agent docs:
- A picture's pose is fixed at capture. Pictures taken while lost poison later `locate` calls, so we'll store
  fit and suspect with every picture on my side.
- How to tell a door_outside start pocket from stall blocks from being lost.
- `/trail/near`'s bearing is + = left, while `markers`' is + = right. Centring a marker is `turn(-bearing_deg)`.

Files: `go2/memory_lab/diagnosis/README.md` and `go2/data/memory_lab/diagnosis/` (data, not in git). I'll commit the
code around 10:45.
