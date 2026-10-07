#!/bin/bash
# The 24-questions wave. ONE LAUNCHER OWNS EVERY CELL, in the order the specs are given:
# a priority order is only real if one queue owns every cell - two launchers each honouring
# their own cap is how MemGPT held nine of fourteen slots while ACE had none.
#   ./launch.sh <wave> <max-parallel> "<arm>|<household>" ...
cd /home/oliver/robot/dynamic_home_eqa
export PYTHONPATH=src
OUT=results/self_improve/overnight_wave_24_questions
QPD=24
WAVE="$1"; shift
MAXP="$1"; shift
LOGS="$OUT/logs/$WAVE"
mkdir -p "$LOGS"; : > "$LOGS/pids.txt"
for spec in "$@"; do
  arm="${spec%%|*}"; hh="${spec##*|}"
  # Throttled on every overnight_wave process ON THE MACHINE, so this wave and any cell of
  # the 8-a-day wave still finishing share one cap rather than two.
  while [ "$(pgrep -fc 'self_improve\.overnight_wave' || echo 0)" -ge "$MAXP" ]; do sleep 5; done
  safe="${arm// /_}"; safe="${safe//,/}"
  ( exec python3 -m self_improve.overnight_wave --arm "$arm" --household "$hh" \
      --questions-per-day "$QPD" --out "$OUT" \
      > "$LOGS/${safe}__${hh}.log" 2>&1 ) &
  pid=$!
  echo "$pid $arm $hh qpd=$QPD" >> "$LOGS/pids.txt"
  sleep 1
  if [ -e "/proc/$pid/cmdline" ]; then
    if ! tr '\0' ' ' < "/proc/$pid/cmdline" 2>/dev/null | grep -q overnight_wave; then
      echo "RECORDED PID $pid IS NOT THE PYTHON PROCESS for $arm $hh" >> "$LOGS/pids.txt"
    fi
  elif ! kill -0 "$pid" 2>/dev/null; then
    echo "note: $pid ($arm $hh) had already exited when checked - fine for a no-model arm" \
      >> "$LOGS/pids.txt"
  fi
done
wait
echo "WAVE $WAVE DONE $(date -Is)" >> "$LOGS/pids.txt"
