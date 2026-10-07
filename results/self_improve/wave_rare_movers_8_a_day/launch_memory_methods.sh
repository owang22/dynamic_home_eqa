#!/bin/bash
# PREPARED 2026-10-02, NOT LAUNCHED. The two memory methods on the rare-mover banks at 8 ordinary
# questions a day, plus two rerun cells for the rerun floor. Same shape as
# results/self_improve/overnight_wave/launch.sh (exec so the pid is python; throttle on every
# overnight_wave process on the machine), with every field explicit: --banks (household names
# repeat across bank sets), --out (cell_dir is arm+household only, so a default --out would
# truncate the ten-home cells), --questions-per-day 99 (ask every row; the default 8 would thin
# the rare-mover questions away with the rest), --cache a FRESH subdirectory so nothing replays
# from the ten-home run's cache and the rerun cells get a cache of their own (a rerun that hits
# the main cache would replay the first run byte for byte and measure nothing).
# Needs the vLLM server at http://127.0.0.1:8300 serving Qwen/Qwen3.8-27B (src/baselines/patrol/llm.py).
#   ./launch_memory_methods.sh <wave-name> <max-parallel>
cd /home/oliver/robot/dynamic_home_eqa
export PYTHONPATH=src
WAVE="${1:-memory_methods}"; MAXP="${2:-10}"
BANKS=results/self_improve/varied_homes/rare_movers/banks_8_a_day
OUT=results/self_improve/wave_rare_movers_8_a_day
OUT_RERUN=results/self_improve/wave_rare_movers_8_a_day_rerun
CACHE=llm_prior_cache/self_improve_rare_movers
CACHE_RERUN=llm_prior_cache/self_improve_rare_movers_rerun
LOGS="$OUT/logs/$WAVE"
mkdir -p "$LOGS" "$OUT_RERUN/logs"; : > "$LOGS/pids.txt"
launch () {   # arm, household, out-dir, cache-dir
  local arm="$1" hh="$2" out="$3" cache="$4"
  while [ "$(pgrep -fc 'self_improve\.overnight_wave' || echo 0)" -ge "$MAXP" ]; do sleep 5; done
  local safe="${arm// /_}"; safe="${safe//,/}"
  ( exec python3 -m self_improve.overnight_wave --arm "$arm" --household "$hh" \
      --banks "$BANKS" --last-day 31 --questions-per-day 99 --budget 3 --seed 0 \
      --out "$out" --cache "$cache" \
      > "$LOGS/${safe}__${hh}__$(basename "$out").log" 2>&1 ) &
  echo "$! $arm | $hh | qpd=99 | banks=$BANKS | out=$out | cache=$cache" >> "$LOGS/pids.txt"
  sleep 1
}
for arm in "the log and notes about the routine" "prior only, no notes"; do
  for hh in hh_s2_t03 hh_s19_t03 hh_s20_t03 hh_s32_t03 hh_s48_t03 hh_s63_t03 hh_s93_t03 hh_s109_t03 hh_s123_t03 hh_s151_t03; do
    launch "$arm" "$hh" "$OUT" "$CACHE"
  done
done
# the rerun floor: the same arm, bank, seed and settings twice, with a cache of its own
for hh in hh_s2_t03 hh_s48_t03; do
  launch "the log and notes about the routine" "$hh" "$OUT_RERUN" "$CACHE_RERUN"
done
wait
echo "WAVE $WAVE DONE $(date -Is)" >> "$LOGS/pids.txt"
