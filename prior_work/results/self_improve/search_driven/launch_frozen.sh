#!/usr/bin/env bash
# The frozen-memory pass: freeze the notes, stop all looking, answer from the notes
# alone. The ONLY memory measurement this framework produces, because every answer
# inside a live cell may have been obtained by finding the object.
#
# Launched through a wrapper that ends in `wait` rather than as a bare `nohup ... &`:
# backgrounded children of a tool shell are killed with their process group when that
# shell exits, which silently truncated the first attempt after one cell with no error
# in the log.
set -u
cd /home/oliver/robot/dynamic_home_eqa
OUT=results/self_improve/search_driven/logs
for h in hh_s0_t03 hh_s1_t03 hh_s2_t03; do
  PYTHONPATH=src python3 -m self_improve.frozen_answers_for_search_cells \
    --max-questions 30 --only-household "$h" > "$OUT/frozen_$h.log" 2>&1 &
  echo "launched frozen pass for $h (pid $!)"
done
wait
echo "ALL FROZEN PASSES DONE"
