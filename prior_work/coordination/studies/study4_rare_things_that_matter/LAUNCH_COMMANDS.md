# Study 4: commands to run the memory methods on the 8-a-day rare-mover banks (prepared, not launched)

Updated 2026-10-02 (last batch): the cache is a fresh subdirectory `llm_prior_cache/self_improve_rare_movers`, and two
rerun cells (log-and-notes on hh_s2 and hh_s48, same seed and settings) go to the sibling wave
`results/self_improve/wave_rare_movers_8_a_day_rerun/` with a cache of their own
(`llm_prior_cache/self_improve_rare_movers_rerun`): a rerun that shared the main cache would replay the first run
byte for byte and measure no floor. The banks were rebuilt the same day with random-time background questions;
the launcher reads the bank directory, so nothing in it changed for that.

Written 2026-10-02 by sim-builder-rare-things. Nothing below has been run. Needs the vLLM server
at `http://127.0.0.1:8300` serving `Qwen/Qwen3.8-27B` (`src/baselines/patrol/llm.py`); it is down
at the time of writing and starting it is posted on the board first.

## How cells are launched (what I read)

* `results/self_improve/overnight_wave/launch.sh`: `exec python3 -m self_improve.overnight_wave
  --arm "<arm>" --household <hh>` per cell, backgrounded, throttled by counting every
  `self_improve.overnight_wave` process on the machine against `<max-parallel>`; pids and
  per-cell logs under `logs/<wave>/`. It passes no `--banks`, so the pilot banks apply; the
  2026-09-26 queue (`the_queue_2026-09-26/run_the_queue.sh`) made every field explicit after a
  default `--out` truncated finished cells (household names repeat across bank sets and
  `cell_dir` is arm + household only). `src/self_improve/run_one_cell.py` is the older
  two-by-three harness and is not what the waves use.
* Parallelism actually used: the ten `the log and notes about the routine` cells of the ten-home
  run started within one minute of each other (wave4, 02:31-02:32 on 2026-09-25) and ran ten at
  once; the ten `prior only, no notes` cells ran ten at once alongside other arms (onequeue).
* Response cache: the ten-home run's is `llm_prior_cache/self_improve/` (777 MB), key = sha256 of model, messages,
  schema, max_tokens, temperature, seed. This wave writes to a fresh `llm_prior_cache/self_improve_rare_movers/`
  (and the rerun cells to `..._rerun/`), so nothing replays and every call is fresh.
* `--questions-per-day 99` asks every row of the bank. The default 8 would take 8 evenly spaced
  rows per day from the ordinary-plus-rare list and thin the rare-mover questions away.

## The commands

The launcher file, written and executable but not run:
`results/self_improve/wave_rare_movers_8_a_day/launch_memory_methods.sh <wave-name> <max-parallel>`

    cd /home/oliver/robot/dynamic_home_eqa
    ./results/self_improve/wave_rare_movers_8_a_day/launch_memory_methods.sh memory_methods 10

which runs, for each arm in `"the log and notes about the routine"`, `"prior only, no notes"` and
each home in hh_s2, s19, s20, s32, s48, s63, s93, s109, s123, s151 (`_t03`):

    PYTHONPATH=src python3 -m self_improve.overnight_wave \
        --arm "the log and notes about the routine" --household hh_s2_t03 \
        --banks results/self_improve/varied_homes/rare_movers/banks_8_a_day \
        --last-day 31 --questions-per-day 99 --budget 3 --seed 0 \
        --out results/self_improve/wave_rare_movers_8_a_day \
        --cache llm_prior_cache/self_improve_rare_movers \
        > results/self_improve/wave_rare_movers_8_a_day/logs/memory_methods/the_log_and_notes_about_the_routine__hh_s2_t03__wave_rare_movers_8_a_day.log 2>&1

    PYTHONPATH=src python3 -m self_improve.overnight_wave \
        --arm "prior only, no notes" --household hh_s2_t03 \
        --banks results/self_improve/varied_homes/rare_movers/banks_8_a_day \
        --last-day 31 --questions-per-day 99 --budget 3 --seed 0 \
        --out results/self_improve/wave_rare_movers_8_a_day \
        --cache llm_prior_cache/self_improve_rare_movers \
        > results/self_improve/wave_rare_movers_8_a_day/logs/memory_methods/prior_only_no_notes__hh_s2_t03__wave_rare_movers_8_a_day.log 2>&1

and, for the rerun floor, the first command again for hh_s2_t03 and hh_s48_t03 with
`--out results/self_improve/wave_rare_movers_8_a_day_rerun --cache llm_prior_cache/self_improve_rare_movers_rerun`.

Cells land in `results/self_improve/wave_rare_movers_8_a_day/cells/<arm_dir>/<home>/` beside the
four no-model cells already there (last-seen, most frequent, same time of day, alternate room). Score with
`python3 coordination/studies/study4_rare_things_that_matter/score_rare_movers.py --load 8 --arm the_log_and_notes_about_the_routine`
(and `--arm prior_only_no_notes`); the unseen flag is computed per cell from that cell's own looks.

## Expected cost per cell

From the ten-home cells at 8 a day (248 questions, `arm.json`: `n_model_calls_timed`, `seconds`;
`heartbeat.jsonl` for start times):

| arm | ten-home calls per cell | per question (after 32 nightly writes) | ten-home wall time, ten at once |
|---|---|---|---|
| the log and notes about the routine | 309-378 (median 336) | about 1.2 | 83-124 min (median 115) |
| prior only, no notes | 413-658 (median 575) | about 2.3 (it is asked on every room it opens and answers from nothing) | 92-182 min (median 154), shared with other arms |

The 8-a-day rare-mover banks ask 304-336 questions per cell (mean 326, 31% more than 248), so
expect per cell about **430-450 model calls and 150 min** for the log-and-notes arm and about
**750 calls and 200 min** for prior-only, at ten cells at once on the same server; 20 cells
total plus the two rerun cells (another ~900 calls), roughly 13,000 model calls, 3 to 4 hours wall time
if both arms run ten at once in sequence. The rebuilt banks ask 320-368 questions per cell (mean 348,
the random background added about 40), so scale the per-cell figures up by about 7% from those above. Check at 3, 5 and 10 minutes after launch (`heartbeat.jsonl` in each cell, `CRASHED.txt`
on failure, `RUNNING.lock` while running).
