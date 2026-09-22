#!/bin/bash
# Re-sequenced told passes (01:55): waits for the running no-message pass (pid 929420) to exit, then
#   start message:        retrieval+longcontext on hh_s0-9  ||  reflection on hh_s0-4   (two concurrent invocations, shared cache)
#   start + end messages: same split
# then the two-spells arms, reduced to buffer + retrieval (no message, start message) on hh_s0-2.
# Cut agreed with the coordinator to fit the 08:30 deadline at ~46-54 calls/min: reflection told passes on 5 households
# instead of 10; routine table dropped from the two-spells arms.
cd ~/robot/dynamic_home_eqa/src || exit 1
R=../results/confidence_shift_2026-09-20/uq/llm_strategies
OUT=$R/chain_person; LOG=$R/chain_progress.log; CACHE=$OUT/cache
FM=/home/oliver/robot/dynamic_home_eqa_fm/results/fm_memory
B10=""; B5=""; B10R=""; B5R=""
for s in 0 1 2 3 4 5 6 7 8 9; do B10="$B10 $FM/banks_f1/hh_s${s}_t03.jsonl"; B10R="$B10R $FM/banks_f1_return/hh_s${s}_t03.jsonl"; done
for s in 0 1 2 3 4; do B5="$B5 $FM/banks_f1/hh_s${s}_t03.jsonl"; B5R="$B5R $FM/banks_f1_return/hh_s${s}_t03.jsonl"; done
while kill -0 929420 2>/dev/null; do sleep 60; done
echo "$(date +%H:%M) person chain no-message pass exited; running llm_strategy_check" >> "$LOG"
python3 -m baselines.patrol.llm_strategy_check --dir "$OUT/nottold" --shift-days 14,15 >> "$LOG" 2>&1
for pass in told_entry told_entryreturn; do
  if [ $pass = told_entry ]; then BA="$B10"; BB="$B5"; sd="14,15"; label="start-message"; else BA="$B10R"; BB="$B5R"; sd="14,15,24"; label="start-and-end-messages"; fi
  mkdir -p "$OUT/$pass"
  python3 -m baselines.patrol.llm --bank $BA --out "$OUT/$pass" --cache "$CACHE" --memory retrieval longcontext --told told --look off --workers 40 --format conf > "$OUT/${pass}_rl.log" 2>&1 &
  p1=$!
  python3 -m baselines.patrol.llm --bank $BB --out "$OUT/$pass" --cache "$CACHE" --memory reflect --told told --look off --workers 10 --format conf > "$OUT/${pass}_reflect.log" 2>&1 &
  p2=$!
  wait $p1; e1=$?; wait $p2; e2=$?
  echo "$(date +%H:%M) person chain $label exit=$e1 (retrieval+longcontext, 10 hh) / $e2 (reflection, 5 hh)" >> "$LOG"
  python3 -m baselines.patrol.llm_strategy_check --dir "$OUT/$pass" --shift-days $sd >> "$LOG" 2>&1
done
echo "$(date +%H:%M) PERSON CHAIN FINISHED (told passes re-sequenced)" >> "$LOG"
STRATS="naive retrieval" bash $R/run_chain_person2x.sh
