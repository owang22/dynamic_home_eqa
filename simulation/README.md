# simulation/

**Owner: the H100 agent (Claude Code on the lab's H100 machine).** Only that agent edits this folder and pushes
it. Others propose changes with a message in `coordination/inbox/h100/` (see `../COORDINATION.md`).

What goes here: simulation experiments run on the H100 machine: their configs, launch scripts, small results
and write-ups. Large run outputs (caches, per-call dumps, renders, weights) stay on the H100 machine and out of
git; add ignore rules for them.

## Existing code to build on (stays where it is)

- `../go2/lab_routine_sim/`: the lab routine study (2026-10-17). 10 simulated labs x 30 days with hidden routines;
  a local Qwen3.8-27B writes and maintains hypotheses. Methods: no memory, full log, free notes, hypotheses,
  plus simple rules. Read `README.md`, `DESIGN.md`, `RESULTS.md` there. Result: hypotheses beat free notes but
  not the full log or the "same weekday as last time" rule, and Qwen never wrote a rule other than "always here".
- `../3d_rendering/`: the lived-home generator (`src/lived_home/`: model-driven residents in an HSSD home, every
  object position snapshotted every 2 h) and Habitat + HSSD renders from robot viewpoints. Read its `README.md`.
- `../go2/evidence_memory/`: which memory keeps the right scenes (simulation plus the lab tool).

Import or wrap these from here; do not move them. If you need to change them, say so in a message to cheetah
first (they are cheetah's).

## First experiment: the routine study again, with Opus writing the rules and a routine shift

1. Rerun `go2/lab_routine_sim/` with Opus as the rule writer instead of Qwen3.8-27B.
2. Stage a routine shift partway through each lab's run (a routine changes; the old rule becomes wrong).
3. Four memory arms:
   - **full log**: the model reads the whole history each time;
   - **stored rules**: rules written once and kept;
   - **rules re-derived on demand**: rules rebuilt from the log when a question comes;
   - **verified rules**: stored rules that are checked against new evidence and revised when contradicted.
4. Run every arm with a strong model (Opus) and a small model (e.g. Qwen3-VL-8B or a similar local model).
5. Report first-look accuracy before and after the shift, how fast each arm recovers, and cost per answer.

Write the design to `simulation/routine_shift/DESIGN.md` and send cheetah a message before spending on the
full grid.

## Later option

Evaluate the same memory arms on EmbodiedMemory-Bench (AI2-THOR; arXiv 2609.28236).

## Constraints

- **cheetah's GPU is shared with another user (gaofeng); never start jobs on cheetah or disturb that user.**
  Run models on the H100 machine.
- Never touch the dog or the console (`172.17.40.64:8080`); simulation needs neither.
- Never commit secrets, robot data or large outputs.

## Lab history generator (`lab_history/`, started 2026-10-25)

Asked for by cheetah (overnight list, item 3). It writes synthetic multi-week histories of a lab: people and
objects moving between the 16 lab places on hidden routines, and what the dog would have seen on its patrols. The
output is meant for cheetah's memory tests, which can currently only use real pictures re-timed (so they are capped
at what the dog actually saw). With a generator, those tests can run on 30–90 day histories with exact ground truth.

**Inputs**
- The 16 places, with names and map x, y, from
  `go2/memory_lab/places_2026-10-25.json`, read in place. A stand-in list is kept for tests.
- Days, seed, and the routine mix (below).

**The hidden world, all from the seed**
- **People** (4–6): arrive and leave around their own times on weekdays, sit at their own desk, and have lunch,
  meetings and a weekly event (e.g. group meeting on Tuesday 14:00). Some work from home on fixed weekdays.
  Holidays and sick days at random.
- **Objects** (15–25), each following one routine type:
  fixed place; weekday pattern; rotation; follows its owner (a backpack goes home with its person); used and put
  back (a mug goes to the sink after lunch, back to the desk next morning); drifts (one step to a nearby place
  now and then); leaves the lab on some days.
- **Routine shifts:** on chosen days a routine changes without notice (a person changes desks, an object gets a new
  home). That covers the stale-sightings case.
- **Noise:** off-routine moves, and objects left out overnight.
- **Truth:** the full state (every person's and object's place) every 10 minutes, plus a plain-text statement of
  each routine and each shift, with dates.

**What the dog sees (the events)**
- Patrols at set times (e.g. 3 a day on weekdays) visit some places in order, plus occasional unplanned visits.
- One event per place visited, in the event format of cheetah's `go2/memory_lab/data.py`. Its `seen` is a
  description like the vision model's, listing what is visible there, with set rates for missed objects, wrong names
  ("black bag" for "black backpack") and an occasional object that isn't there.
- Also written: questions with answers taken from the truth ("where is the red umbrella now?", "when was Alice's
  backpack last in the lab?", "which desk does Bob use since the 3rd week?"), for scoring.

**Output:** see `lab_history/README.md`. Ready-made runs (30/60/90 days x 3 seeds) are in git under
`lab_history/runs/`, since cheetah reads them from there.
