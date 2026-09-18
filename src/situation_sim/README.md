# situation_sim — situation-driven household generator

Clean-break replacement for the per-activity destination distributions in
`src/households` / `src/revamp_v2`. Nothing from those packages (or from
`profiles/`) is imported; the only reuse is the numeric timing constants,
copied with their calibration notes into `timing_constants.py`.

**Idea.** A hidden per-day *situation* (external events such as rain or a
guest visit, internal states such as low energy or running late) shifts
many object placements at once. A cause is modelled explicitly only if it
moves more than one object; single-object noise is the *whim* term of the
placement decision, whose size depends on the resident's traits and the
day's hurriedness.

## Layout

| file | what |
|---|---|
| `household.py` | samples residents, rooms, receptacles (old bank id conventions), objects, traits, object groups; the `ACCEPTS` table of what each receptacle kind can hold |
| `situation.py` | per-day causes: event rolls from `events.yaml` + internal states with carryover; extreme bands become active causes |
| `events.yaml` | the six hand-written event types (schedule edits, blocked receptacles, placement rules, rates) |
| `activities.yaml` | activity templates and per-role weekday/weekend schedules |
| `schedule.py` | realizes bouts: event edits, skip, jitter (copied sigmas × punctuality), anchor commutes, fragmentation with kitchen breaks |
| `placement.py` | the placement decision function + `compute_allowed` (the rule set check 5 verifies against) |
| `simulate.py` | the loop: bring objects to activity surfaces, decide where they go afterwards, trips out, tidy passes, group riding |
| `trace.py` | writers for `trace.md`, `events.jsonl`, `hidden_state.json` |
| `checks.py` | the five checkpoint checks (+ a bank-loader smoke test) |
| `run.py` | CLI |

## Run

```bash
cd src && python3 -m situation_sim.run --seed 0 --out ../data/situation_sim/hh_s0_wed-sun
```

Outputs: `trace.md` (human, day by day), `events.jsonl` (bank-format
`episode_header` + `truth` + `resident` rows, plus extra `cause`/`causes`/
`whim`/`reason` fields on truth rows), `hidden_state.json` (household,
per-day causes and states, placement parameters, timing constants, stats).
Same seed → byte-identical files.

## Object model

While an activity runs, the objects it uses sit at the activity surface
(a laptop on the desk); pocket items ride `ON_PERSON`. When it ends, every
used object the next activity does not need goes through `decide()`:
event rule → tidy pass → arriving home (put away / dumped at the door) →
home activity (carried into the next room if distracted / left where used /
sink for dirty dishes / put back) → occupied-or-blocked fallback → whim.
A decision whose destination is where the object already is produces no
move but still counts as a decision (whim share is reported both ways).
Attribution to causes is exact: only the probability mass a cause *added*
is credited to it.
