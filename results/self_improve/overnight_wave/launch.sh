#!/bin/bash
# Launch overnight_wave cells. `exec` so the recorded pid IS python: wrapping it in a
# subshell made $! the subshell's pid, and killing that orphaned python instead of stopping
# it, which left two processes writing one cell.
#   ./launch.sh <wave> <max-parallel> "<arm>|<household>" ...
cd /home/oliver/robot/dynamic_home_eqa
export PYTHONPATH=src
WAVE="$1"; shift
MAXP="$1"; shift
LOGS="results/self_improve/overnight_wave/logs/$WAVE"
mkdir -p "$LOGS"; : > "$LOGS/pids.txt"
for spec in "$@"; do
  arm="${spec%%|*}"; hh="${spec##*|}"
  # Throttle on every overnight_wave python process on the machine, not this wave's jobs:
  # two waves each honouring their own cap together push the server past its knee. The dot
  # is escaped because pgrep -f takes a regex and an unescaped dot matches the '/' in this
  # script's own path, which would make the launcher count itself.
  while [ "$(pgrep -fc 'self_improve\.overnight_wave' || echo 0)" -ge "$MAXP" ]; do sleep 5; done
  safe="${arm// /_}"; safe="${safe//,/}"
  ( exec python3 -m self_improve.overnight_wave --arm "$arm" --household "$hh" \
      > "$LOGS/${safe}__${hh}.log" 2>&1 ) &
  pid=$!
  echo "$pid $arm $hh" >> "$LOGS/pids.txt"
  sleep 1
  # Distinguish "the pid is not python" from "the cell already finished". The
  # `newest sighting, no model` arm calls no model and finishes in under a second, so the
  # first version of this check reported all ten of its cells as the wrong process when they
  # had in fact completed cleanly. A check that cries wolf gets ignored, which is worse than
  # no check.
  if [ -e "/proc/$pid/cmdline" ]; then
    if ! tr '\0' ' ' < "/proc/$pid/cmdline" 2>/dev/null | grep -q overnight_wave; then
      echo "RECORDED PID $pid IS NOT THE PYTHON PROCESS for $arm $hh" >> "$LOGS/pids.txt"
    fi
  elif ! kill -0 "$pid" 2>/dev/null; then
    echo "note: $pid ($arm $hh) had already exited when checked - fine for a no-model arm" >> "$LOGS/pids.txt"
  fi
done
wait
echo "WAVE $WAVE DONE $(date -Is)" >> "$LOGS/pids.txt"
