# three_prompts: what is running, and how it finishes

Operational notes only. The findings live in `THE_WRITING_PROMPTS_WERE_NOT_THE_SAME.md`,
the pre-registration in `PREDICTION.md`, and the results in `COMPLIANCE_REPORT.txt` and
`OUTCOMES_REPORT.txt` once they exist.

## The design in one paragraph

Six arms on the ten `varied_homes/ten_homes/banks/` homes: `control`, `rival_beliefs`,
`describe_the_person`, `told_unwell`, `rival_and_describe`, and `control_wholesale`. All
but the last use the claim store; `control_wholesale` is the memory-style contrast.
**Only the nightly note-writing prompt differs between arms** — the homes, the searches
(memory-guided, 3 rooms a question, 8 questions a day), the answer step and the question
sets are identical. **There is no memory length limit**, in writing or in reading. **The
asked-object list is OFF** in every arm, and the nightly edit allowance is two per
asked-about object with a token budget that cannot truncate.

## Two checks that must pass before any number is read, both on the artifact

`run_one_arm` enforces both and refuses to write a cell that fails either:

1. **the cell's own `searches.jsonl` header says `name_the_objects_it_will_be_quizzed_on:
   false`.** A 42-cell wave ran a third of the way through with it true because nothing ever
   read the artifact, only the code meant to produce it.
2. **no night that saw an asked-about object applied zero edits.** The shared token budget
   `200 + 120 * cap` truncates the edits mid-JSON at every allowance from 22 up; the text
   then does not parse, `edits` comes back empty and the whole night writes nothing, while
   `model_call_failed` stays False because text was returned. Arms here pass
   `edit_max_tokens = 300 + 260 * cap` instead. The nightly report carries
   `the_completion_did_not_parse`.

To check by hand:

    python3 -c "import json; print(json.loads(open('cells/control/hh_s2_t03/searches.jsonl').readline())['name_the_objects_it_will_be_quizzed_on'])"


## It finishes on its own

Three things run detached, each of which must be exactly one process:

| what | module | job |
|---|---|---|
| the launcher | `launch.sh nolist 42 <specs>` | starts cells, machine-wide cap of 42 |
| the stall watcher | `self_improve.watch_the_heartbeats --every 60` | rewrites `HEARTBEAT.md`; flags anything silent over 15 minutes |
| the diagnostics driver | `self_improve.three_prompts_follow_on --max-total 42` | runs each cell's diagnostics as it lands, then **writes the three reports** |

The driver's last act is to produce `COMPLIANCE_REPORT.txt`,
`THE_RERUN_NOISE_FLOOR.txt`, `the_answer_step_token_budget.txt` and
`OUTCOMES_REPORT.txt` -- **in that order**, because the outcomes report reads
`the_rerun_noise_floor.json` and annotates every contrast with whether it clears the
floor. Run the other way round, every verdict silently loses that line. **Compliance is written
first and should be read first: an arm that did not do what its prompt asked is not an
arm, and its outcome numbers mean nothing.**

## If you are picking this up by hand

None of these needs a model call except where noted:

    python3 -m self_improve.three_prompts_compliance          # compliance, read this first
    python3 -m self_improve.three_prompts_noise_floor         # the rerun floor, BEFORE outcomes
    python3 -m self_improve.three_prompts_outcomes            # the four end-to-end measures
    python3 -m self_improve.three_prompts_reanswer --gather    # the token-budget contrast
    python3 -m self_improve.watch_the_heartbeats --once       # rewrite HEARTBEAT.md now

    # these DO call the model
    python3 -m self_improve.three_prompts --arm <arm> --household <home>
    python3 -m self_improve.three_prompts_frozen --arms <arm> --households <home>

To relaunch whatever is missing, list the cells that are neither running nor finished and
pass them to `launch.sh`. The accounting table in `HEARTBEAT.md` gives the count per arm,
and says whether a launcher is alive — so a non-zero "neither" reads as *queued* rather
than *lost*.

## The rerun noise floor is free, and it is not optional

`control` and `told_unwell` get **byte-identical prompts on days 0-13** -- the told-it arm
differs only by one sentence on the night of day 14 and one on day 24. So over that window
the two arms are the same experiment run twice, and their difference is rerun noise.
Measured on seven homes: **1.5 to 2.2 points** mean absolute difference on the accuracy and
find-rate measures, up to **7.3 points** in the worst home, and answer agreement as low as
**68.8%**.

The cause: two cells miss the prompt cache at the same moment, each calls the server, and
vLLM returns different completions at temperature 0. Demonstrated on `hh_s2_t03` day 4,
where the rebuilt answer prompts are byte-identical and the cache key is the same while the
two recorded answers are `bedroom_floor_b1` and `dining_table_d1`.

**So the day-13 freeze point is a noise measurement, not the exact null "by construction"
it was described as** -- it is exact in the prompts only. And any arm difference below the
floor for its own measure is not evidence, however tight its standard error: the standard
error measures spread across homes and this does not.

## Three traps that cost time tonight

**Never wrap a cell in `( ... ) &` in the launcher.** `$!` is then the subshell's pid, so
killing the recorded pid orphans python instead of stopping it. That left five cells with
two processes appending to one `looks.jsonl`. The launcher now `exec`s python, checks the
recorded pid against `/proc/<pid>/cmdline`, and `run_one_arm` additionally takes a lock in
the cell directory and refuses to be a second writer.

**Never match a process with `pgrep -f` or a substring of `ps` output.** A tool shell's
own command line contains whatever script it was asked to run, so the pattern matches the
checker. This killed my own shell twice. Match on parsed argv: `argv[0]` must be python and
the module must be an exact argv element — `scratchpad/one_driver.py` does it correctly.

**The heartbeat's `day` is the night being written, not the last one finished**, because
`beat()` is called before `write_the_notes`. So a cell reporting night *n* has
`notes.json` written through *n-1*. Harmless for progress, but do not read it as a
completed-night count.

## Superseded directories, none deleted

* `superseded_8_line_budget_2026-09-24/` — the first wave, run while the 8-line read cap
  was still applied at answer time. Stopped deliberately.
* `superseded_2400_char_summary_schema/` — wholesale cells whose schema still capped the
  whole month's memory at 2400 characters.
* `superseded_two_writers_same_cell/` — the cells the subshell-pid bug corrupted.
* `../superseded_the_asked_list_was_in_the_prompt_2026-09-24/` — the 42-cell wave that ran
  with the asked-object list enumerated in the note-writing prompt. Its compliance gate and
  the rerun noise floor measured on it remain valid as measurements of the prompts; no
  outcome number from it is usable.

Each has its own `WHY.md`. Nothing in them may be used.

## Open questions for the coordinator, recorded so they are not lost

* **The edit allowance binds on the first night.** Two per asked-about object gives 22 for
  `hh_s2_t03`; night 1 saw 47 distinct objects and offered exactly 22 edits. With the quiz
  list off the writer describes the house, not the quiz, so the natural denominator is
  objects observed rather than objects asked about.
* **`DRAFT_a_variant_that_asks_for_a_real_condition.md`** is drafted and deliberately not
  wired into `ARMS`. 96.3% of 270 claims record `holds_under` as exactly `"current"`, so two
  kept rival beliefs carry the same condition and nothing tells them apart.
