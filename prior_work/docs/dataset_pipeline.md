# How the household dataset is generated

`src/revamp_v2/generate_dataset.py` builds one household with three LLM
calls per resident-household, then realizes it deterministically.

    L0  places      no LLM      furniture list: a shared template scaled
                                by bedroom count, plus a few pieces
                                particular to the household type
    L1  persona     1 call      residents (name, age, occupation,
                                personality) and the object inventory
    L2  story       1 call      that resident's every day: activity,
                    per         start, end, and where — 8 to 18 blocks
                    resident    per day, for all 21 days
    L3  movement    1 call      per object: where it lives, how often it
                                drifts, and where it lands after each
                                activity
    L4  realize     no LLM      the story becomes a dated calendar, the
                                movement rules fire against it, a seeded
                                simulator writes the timeline

## Why this order

The story is the schedule. Residents are written one at a time, each
call seeing everyone written before it, so they eat together, hand things
over and leave the house at compatible times — coordination the model
does directly, rather than a merge step guessing at it.

Object movement is authored last, against a digest of the activities the
story actually contains. A rule can therefore only name something that
happens. The digest reports activities as realization will see them: a
resident's consecutive out-of-house blocks are one trip named for its
longest leg, so a rule attached to `work_away` still fires when the trip
began with `traveling`.

## What constrains the model

Every response is shaped by a JSON schema, not by asking nicely:

- activity names, receptacle ids, object ids and resident ids are closed
  enums — an id that does not exist cannot be written;
- the story's day slots are pinned positionally, so a missing or
  duplicated day is unrepresentable, and the 8-block-per-day floor is
  part of the grammar;
- object entries are pinned one per inventory item, so the model answers
  for every object rather than keeping its own tally;
- each response opens with a free-text field the model fills before
  committing to any decision, kept in the build log and stripped from the
  artifact.

## Gates

An accepted household must pass, in `validate.py`:

- **referential** — placements match the inventory, residents match the
  persona, no repeated weekday in a block;
- **reachability** — the rules reach the life the story describes: every
  probability distribution resolves, objects declared mobile can move,
  and no rule names an activity that never happens;
- **coverage** — most at-home activities move something. A few genuinely
  object-free activities are fine; a majority is not.

A household that fails is retried with the specific gap named, up to
three attempts, and every attempt is recorded in `build_log.json`.

## Reproducibility

Each call is seeded from the household, the stage, and a hash of the
prompt, schema and reasoning effort that shape it, so editing any of
those invalidates exactly the responses it affects and nothing else.
Responses are cached by seed: re-running replays the original generation
byte for byte and costs nothing.

## Requirements

An OpenAI-compatible endpoint with strict structured outputs. Schema
support was probed on Google Gemini and found insufficient at this scale
— see `gemini-compat-findings.md`.

    GENERATION_ENDPOINT=https://api.openai.com \
    OPENAI_API_KEY=...      # or ~/.config/dynamic_eqa/openai_key
    HOSTED_SPEND_CAP=15     # aborts the run if exceeded

    python src/revamp_v2/generate_dataset.py --all --model gpt-5.6-terra

Then, to view a household in the scene viewer:

    python src/revamp_v2/make_viewer_configs.py --slug storyfirst/<model>
    python visualization/spatialize.py <config> --timeline <hh>/timeline_seed0
    python visualization/serve.py        # http://127.0.0.1:8710
