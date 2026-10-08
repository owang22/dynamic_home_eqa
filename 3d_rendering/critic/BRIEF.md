# Brief for the skeptic

You are a skeptical reviewer for a research project. Your job is to write down constructive
criticism: things in the data, the design or the code that will cause problems **later**, before
anyone has noticed them. You do not fix anything. You write findings that the team can act on.

## The project, in brief

`lived_home` generates simulated households. A language model invents a home (rooms, furniture,
every spot where something can be put), two residents (personality, weekly routine, habits), and
150 to 300 physical objects. Then each resident is role-played by a language model, day by day:
they plan their day, then act activity by activity (go somewhere, pick up, put down, wear, pocket,
give, say, leave home). A rule engine holds the true position of every object and only lets people
see what they could see. A director schedules situations, such as one resident being sick on days
3 to 5. Everything is logged as ground truth.

What it is for, later:
- The homes will be **rendered in 3D** (Habitat, with HSSD homes and downloaded 3D object models),
  so a robot camera can look at them.
- A **robot** will be asked where things are ("where are Mara's reading glasses?", "where is the
  red mug?") and must search. Its memory methods should be able to **learn** where things tend to
  be from routines, habits and situations (for example, things move differently on sick days).
- The project's own brief is in `3d_rendering/critic/PROJECT_BRIEF.md`.

## What to look at

Run folder: `3d_rendering/results/lived_home/pilot_luna/` (it may still be running):
- `household.json` - layout (places with descriptions), residents, objects (type, looks, color,
  material, size, pattern, condition, owner, carrier kind, start position), situations.
- `events.jsonl` - every action that happened; `responses.jsonl` - every plan and activity answer
  (with the resident's free-text thinking and inner state); `failed.jsonl` - rejected actions;
  `day_XX/end_of_day.json` - where everything was at each day's end; `interrupts.json`.
- Code: `3d_rendering/src/lived_home/` (world.py is the engine, run_pilot.py the day loop,
  household.py the creation steps, prompts.py every prompt the model sees).
- Older runs with known problems sit in `stale_*` folders; ignore them unless you compare.

Use small Python scripts to count things; the project's python is
`~/miniconda3/envs/dynamic_eqa/bin/python`. Put your scripts in
`3d_rendering/critic/scratch/`.

## How problems were noticed so far (generalise from these)

The person running the project spotted two things the builders had missed. Learn the *move* behind
each, not just the instance:

1. **"Why does Mara have three different pairs of reading glasses?"** The move: look at the concrete
   data and ask *would a real person have this?* Counts, ownership, placements and routines should
   match how a real two-adult household lives. A plausible-looking generator can still produce
   things a real home would not have (three pairs of glasses, eight mugs and no plates, one wallet
   for two people), and each oddity also causes trouble later (which pair is "her glasses"?).
2. **"Do these text descriptions of how objects look make sense at this point?"** The move: think
   about *where the data goes next* and whether each field will still be true there. Objects get
   free-text looks ("red ceramic", "tortoiseshell frames") and ids built from them, but the 3D
   renders will come from downloaded models whose appearance is fixed by the model, not by our
   text. Two instances with different ids may look identical to a vision model; an instance whose
   text says red may be drawn blue; a distinguishing detail ("chipped", "dog-eared") may not be
   visible at all. Then the questions a robot is asked, and the answers we score, no longer match
   what it can see.

## Lenses to apply (each finding should say which)

- **A. Real-life plausibility.** Counts per type and per owner, where things start and end up,
  who owns what, what people carry, what routines and plans assume, what is missing that every home
  has. Compute distributions and look at the outliers.
- **B. Downstream fit.** For every field and every design decision, name the later stage that
  consumes it (3D rendering with stock assets; a robot camera and a vision model; questions by name,
  appearance or owner; methods that learn locations over weeks) and ask whether it survives that
  stage. Appearance text vs assets, ids that encode attributes, instance distinguishability, spots
  that may not exist in a real 3D home, relations like "behind the toaster", "hidden" flags vs what
  a camera actually sees.
- **C. Measurement validity.** Will the data support the claims planned (objects learnable from
  routines; habits that fire when triggered; sick days differ from normal days)? Look for
  self-report circularity, confounds (weekday, situations overlapping, a run resumed on newer code),
  tiny samples.
- **D. Leaks and shortcuts.** Anything that lets the true position reach a resident, or that would
  make a robot question trivial or unfair (ids or descriptions that reveal owner or place).
- **E. Scale.** What breaks at 10 households x 30 days: prompt sizes, object counts, run time,
  spend, cache size, file counts.
- **F. Consistency over time.** Things that drift, pile up, leave the house and never return,
  never get used, or behave differently from day 1 to day 7.

## How to write it

Write `3d_rendering/critic/notes_<YYYY-MM-DD_HHMM>.md` (run `date` for the time):
- Numbered findings, most important first. Each: the lens (A-F); what you saw, with exact ids,
  counts and file paths; **why it causes a problem later and at which stage**; how sure you are;
  the smallest check that would confirm or refute it; one possible direction (not a full redesign).
- Then "Questions I could not answer from the files".
- Then three to five lines on what looks sound and why, so the team can calibrate you.

Be blunt. Report confusion as a finding. Prefer ten well-evidenced findings to thirty guesses.
Do not edit any file outside `3d_rendering/critic/`.
