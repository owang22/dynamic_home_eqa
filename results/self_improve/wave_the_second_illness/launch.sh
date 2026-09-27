#!/bin/bash
# The reason-first wave. Every schema now puts the reasoning before the decision, which the
# previous wave did not: 55,613 of 55,613 cached room choices there named the room first, with
# thinking disabled, so every room was chosen after zero tokens of deliberation. That wave is
# closed and is this one's ablation.
#
# ONE QUEUE OWNS EVERY CELL. A second launcher honouring its own cap is what produced the
# priority inversion on 2026-09-25, when six low-priority cells held six of ten slots while the
# control queued behind them.
#
#   ./launch.sh <name> <max-parallel> "<arm>|<household>[|<banks>|<last-day>]" ...
#
# The optional third and fourth fields are for the two-illness episodes, which use their own
# banks and run 50 days instead of 32. Everything else takes the pilot banks and 32 days.
cd /home/oliver/robot/dynamic_home_eqa
export PYTHONPATH=src
OUT=results/self_improve/wave_the_second_illness
QPD=24
PILOT=results/self_improve/varied_homes/ten_homes/banks
WAVE="$1"; shift
MAXP="$1"; shift
LOGS="$OUT/logs/$WAVE"
mkdir -p "$LOGS"; : > "$LOGS/pids.txt"
for spec in "$@"; do
  IFS='|' read -r arm hh banks lastday <<< "$spec"
  banks="${banks:-$PILOT}"
  lastday="${lastday:-31}"
  # Throttled on every overnight_wave process ON THE MACHINE, so a cell of the closed wave
  # still finishing shares this cap rather than running beside it.
  while [ "$(pgrep -fc 'self_improve\.overnight_wave' || echo 0)" -ge "$MAXP" ]; do sleep 5; done
  safe="${arm// /_}"; safe="${safe//,/}"
  ( exec python3 -m self_improve.overnight_wave --arm "$arm" --household "$hh" \
      --questions-per-day "$QPD" --last-day "$lastday" --banks "$banks" --out "$OUT" \
      > "$LOGS/${safe}__${hh}__d${lastday}.log" 2>&1 ) &
  pid=$!
  echo "$pid $arm $hh qpd=$QPD last_day=$lastday banks=$banks" >> "$LOGS/pids.txt"
  sleep 1
done
wait
echo "WAVE $WAVE DONE $(date -Is)" >> "$LOGS/pids.txt"
