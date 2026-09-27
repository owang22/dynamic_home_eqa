#!/bin/bash
# ONE QUEUE for 2026-09-26, and it owns every cell on the machine.
#
# Each spec is  arm|household|banks|last-day|out-dir  and every field is required, because the
# two faults this queue exists to avoid both came from a field being left to a default:
#   - household names REPEAT ACROSS BANK SETS. hh_s32_t03 in headline_five and hh_s32_t03 in
#     ten_homes are different homes with the same name, and `cell_dir` is built from the arm and
#     the household only. A run that inherits the wrong --out truncates a finished cell in place,
#     which is what happened on 2026-09-26 to two reason-first cells.
#   - a launcher with no --banks silently took the pilot banks.
#
# The throttle counts every overnight_wave process ON THE MACHINE, so cells still finishing from
# last night share the cap instead of running beside it.
#
#   ./run_the_queue.sh <name> <max-parallel> "<arm>|<hh>|<banks>|<last-day>|<out>" ...
cd /home/oliver/robot/dynamic_home_eqa
export PYTHONPATH=src
QPD=24
WAVE="$1"; shift
MAXP="$1"; shift
LOGS=results/self_improve/the_queue_2026-09-26/logs/$WAVE
mkdir -p "$LOGS"; : > "$LOGS/pids.txt"
for spec in "$@"; do
  IFS='|' read -r arm hh banks lastday out <<< "$spec"
  if [ -z "$arm" ] || [ -z "$hh" ] || [ -z "$banks" ] || [ -z "$lastday" ] || [ -z "$out" ]; then
    echo "SPEC MISSING A FIELD, refusing: $spec" >> "$LOGS/pids.txt"; continue
  fi
  if [ ! -d "$banks" ]; then
    echo "NO SUCH BANKS, refusing: $spec" >> "$LOGS/pids.txt"; continue
  fi
  while [ "$(pgrep -fc 'self_improve\.overnight_wave' || echo 0)" -ge "$MAXP" ]; do sleep 5; done
  safe="${arm// /_}"; safe="${safe//,/}"
  ( exec python3 -m self_improve.overnight_wave --arm "$arm" --household "$hh" \
      --questions-per-day "$QPD" --last-day "$lastday" --banks "$banks" --out "$out" \
      > "$LOGS/${safe}__${hh}__d${lastday}.log" 2>&1 ) &
  echo "$! $arm | $hh | qpd=$QPD | last_day=$lastday | banks=$banks | out=$out" >> "$LOGS/pids.txt"
  sleep 1
done
wait
echo "QUEUE $WAVE DONE $(date -Is)" >> "$LOGS/pids.txt"
