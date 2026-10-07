#!/usr/bin/env bash
# Launch the search-driven cells, one process per cell.
#
# The LLM client is synchronous, so parallelism here is many processes, never
# threads. Before launching anything we check the shared vLLM server: if
# num_requests_waiting is above zero, two other jobs are already queueing and we
# back off rather than pile on.
#
#   bash results/self_improve/search_driven/launch.sh hh_s0_t03 [hh_s1_t03 ...]
set -u
cd /home/oliver/robot/dynamic_home_eqa

OUT=results/self_improve/search_driven/ablation_the_notes_alone
LOGS=$OUT/logs
mkdir -p "$LOGS"

waiting=$(curl -s http://localhost:8300/metrics \
  | grep -E '^vllm:num_requests_waiting\{' | awk '{print int($NF)}')
if [ -z "$waiting" ]; then
  echo "could not read the server's metrics; not launching"; exit 1
fi
if [ "$waiting" -gt 0 ]; then
  echo "num_requests_waiting=$waiting - two other jobs share this server; backing off"
  exit 1
fi
echo "server clear (num_requests_waiting=$waiting); launching"

for household in "$@"; do
  for sensing in "memory-guided search" "fixed rotation" "random"; do
    for how in "incremental edits" "wholesale rewrite"; do
      tag="${household}__${sensing// /_}__${how// /_}"
      if [ -f "$OUT/$household/${sensing// /_}/${how// /_}/cell.json" ]; then
        echo "  already done: $tag"; continue
      fi
      PYTHONPATH=src nohup python3 -m self_improve.search_driven \
        --household "$household" --sensing "$sensing" --how "$how" \
        --last-day 31 --questions-per-day 8 --the-notes-alone --out "$OUT" \
        > "$LOGS/$tag.log" 2>&1 &
      echo "  launched $tag (pid $!)"
      sleep 1
    done
  done
done
wait
