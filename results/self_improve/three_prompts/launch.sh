#!/bin/bash
# Launch three_prompts cells. Each cell is one process; the client is synchronous, so
# parallelism means processes. `setsid` + `wait` because a bare `nohup ... &` from a
# tool shell dies with the shell. PIDs are recorded rather than pkill'd later: pkill -f
# matches the shell running it.
#
#   ./launch.sh <wave-name> <max-parallel> <arm>:<household> [<arm>:<household> ...]
cd /home/oliver/robot/dynamic_home_eqa
export PYTHONPATH=src
WAVE="$1"; shift
MAXP="$1"; shift
LOGS="results/self_improve/three_prompts/logs/$WAVE"
mkdir -p "$LOGS"
: > "$LOGS/pids.txt"
for spec in "$@"; do
  arm="${spec%%:*}"; hh="${spec##*:}"
  # Throttle on ALL three_prompts cells on the machine, not just this wave's jobs.
  # Counting only `jobs -rp` let two waves each run their own MAXP and together push the
  # server past its concurrency knee. MAXP is now a machine-wide cap.
  # Count EVERY three_prompts python process, cells and diagnostics alike. Counting only
  # the cells meant that once the follow-on driver started launching frozen and re-answer
  # passes, this loop would happily add cells on top of them and push the total past the
  # cap. The dot is escaped because pgrep -f takes a regex and an unescaped dot matches the
  # '/' in this script's own path - which would make the launcher count itself.
  while [ "$(pgrep -fc 'self_improve\.three_prompts' || echo 0)" -ge "$MAXP" ]; do sleep 5; done
  # `exec` so the subshell BECOMES python and $! is the python pid. Wrapping python in a
  # subshell made $! the subshell's pid, and killing that orphaned python instead of
  # stopping it - which left two processes writing one cell. Never reintroduce the wrapper.
  ( exec python3 -m self_improve.three_prompts --arm "$arm" --household "$hh" \
      > "$LOGS/${arm}__${hh}.log" 2>&1 ) &
  pid=$!
  echo "$pid $arm $hh" >> "$LOGS/pids.txt"
  # prove the recorded pid is python and not a shell, once per cell
  sleep 1
  if ! tr '\0' ' ' < "/proc/$pid/cmdline" 2>/dev/null | grep -q three_prompts; then
    echo "RECORDED PID $pid IS NOT THE PYTHON PROCESS for $arm $hh" >> "$LOGS/pids.txt"
  fi
  sleep 1
done
wait
echo "WAVE $WAVE DONE $(date -Is)" >> "$LOGS/pids.txt"
