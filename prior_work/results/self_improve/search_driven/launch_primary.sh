#!/usr/bin/env bash
# The PRIMARY configuration: the nightly note-writing prompt does NOT enumerate the
# objects the robot will be quizzed on, so the notes have to describe the house
# rather than cache answers to anticipated questions.
#
# Two budget decisions, both on measured grounds:
#
#   the FIXED ROTATION arm is dropped from this configuration. Measured on the
#   told-list wave: 38.9% found against random's 40.5% over 311 questions a cell,
#   and 2.56 rooms a question against 2.62 - indistinguishable. Random alone is a
#   sufficient question-blind control and the rotation is the redundant one.
#
#   the PRIOR-ONLY control runs with ONE memory format. Its chooser never reads the
#   notes, so its room choices and therefore its find rate and search cost are
#   identical whichever way the notes are written and whether or not the quiz list
#   was in the nightly prompt. One run prices the prior for every configuration.
#   The format still affects its ANSWER step, which is why it is named.
#
#   bash results/self_improve/search_driven/launch_primary.sh hh_s0_t03 ...
set -u
cd /home/oliver/robot/dynamic_home_eqa

OUT=results/self_improve/search_driven/no_asked_list
LOGS=$OUT/logs
mkdir -p "$LOGS"

waiting=$(curl -s http://localhost:8300/metrics \
  | grep -E '^vllm:num_requests_waiting\{' | awk '{print int($NF)}')
running=$(curl -s http://localhost:8300/metrics \
  | grep -E '^vllm:num_requests_running\{' | awk '{print int($NF)}')
if [ -z "$waiting" ]; then
  echo "could not read the server's metrics; not launching"; exit 1
fi
echo "server: $running running, $waiting waiting - launching anyway, the primary"
echo "configuration is the one Oliver asked for and the queue only spreads the work"

launch () { # household sensing how extra
  local household=$1 sensing=$2 how=$3
  local tag="${household}__${sensing// /_}__${how// /_}"
  if [ -f "$OUT/$household/${sensing// /_}/${how// /_}/cell.json" ]; then
    echo "  already done: $tag"; return
  fi
  PYTHONPATH=src nohup python3 -m self_improve.search_driven \
    --household "$household" --sensing "$sensing" --how "$how" \
    --last-day 31 --questions-per-day 8 --no-asked-list --out "$OUT" \
    > "$LOGS/$tag.log" 2>&1 &
  echo "  launched $tag (pid $!)"
  sleep 1
}

for household in "$@"; do
  for how in "incremental edits" "wholesale rewrite"; do
    launch "$household" "memory-guided search" "$how"
    launch "$household" "random" "$how"
  done
  # the control that prices the prior; one format, see the header
  launch "$household" "prior only, no notes" "incremental edits"
done
wait
