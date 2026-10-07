#!/bin/bash
# THE OBSERVATION BUDGET SWEEP, 2026-09-27. Same launcher shape as run_the_queue.sh, with the
# questions a day as a per-spec field, because that IS the treatment here.
#   ./run_the_budget_sweep.sh <name> <max-parallel> "<arm>|<hh>|<banks>|<last-day>|<out>|<qpd>" ...
cd /home/oliver/robot/dynamic_home_eqa
export PYTHONPATH=src
WAVE="$1"; shift
MAXP="$1"; shift
LOGS=results/self_improve/the_queue_2026-09-26/logs/$WAVE
mkdir -p "$LOGS"; : > "$LOGS/pids.txt"
for spec in "$@"; do
  IFS='|' read -r arm hh banks lastday out qpd <<< "$spec"
  for field in "$arm" "$hh" "$banks" "$lastday" "$out" "$qpd"; do
    [ -z "$field" ] && { echo "SPEC MISSING A FIELD, refusing: $spec" >> "$LOGS/pids.txt"; continue 2; }
  done
  [ -d "$banks" ] || { echo "NO SUCH BANKS, refusing: $spec" >> "$LOGS/pids.txt"; continue; }
  while [ "$(pgrep -fc 'self_improve\.overnight_wave' || echo 0)" -ge "$MAXP" ]; do sleep 5; done
  safe="${arm// /_}"; safe="${safe//,/}"
  ( exec python3 -m self_improve.overnight_wave --arm "$arm" --household "$hh" \
      --questions-per-day "$qpd" --last-day "$lastday" --banks "$banks" --out "$out" \
      > "$LOGS/${safe}__${hh}__q${qpd}.log" 2>&1 ) &
  echo "$! $arm | $hh | qpd=$qpd | last_day=$lastday | banks=$banks | out=$out" >> "$LOGS/pids.txt"
  sleep 1
done
wait
echo "SWEEP $WAVE DONE $(date -Is)" >> "$LOGS/pids.txt"
