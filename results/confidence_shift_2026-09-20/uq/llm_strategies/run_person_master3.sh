#!/bin/bash
# Master sequence for the one-person suite + two-spells (02:00 re-plan, per the coordinator):
#  1. no message:           retrieval + reflection, hh_s0-9 (relaunch without long-context; cache replays every finished call)
#  2. start message:        retrieval hh_s0-9 || reflection hh_s0-4
#  3. start + end messages: retrieval hh_s0-9 || reflection hh_s0-4
#  4. long-context, hh_s0-2 only, no message -> start -> start+end (prefill-bound: the whole log in every prompt defeats
#     the prefix cache and starved the server at 39 concurrent; run last, alone, 3 households)
#  5. two spells: buffer + retrieval, no message -> start message, hh_s0-2
# Each step is its own llm.py invocation (crash-isolated per arm, ARM FAILED printed live); no set -e; exit codes logged.
cd ~/robot/dynamic_home_eqa/src || exit 1
R=../results/confidence_shift_2026-09-20/uq/llm_strategies
OUT=$R/chain_person; LOG=$R/chain_progress.log; CACHE=$OUT/cache
FM=/home/oliver/robot/dynamic_home_eqa_fm/results/fm_memory
B10=""; B5=""; B10R=""; B5R=""; B3=""; B3R=""
for s in 0 1 2 3 4 5 6 7 8 9; do B10="$B10 $FM/banks_f1/hh_s${s}_t03.jsonl"; B10R="$B10R $FM/banks_f1_return/hh_s${s}_t03.jsonl"; done
for s in 0 1 2 3 4; do B5="$B5 $FM/banks_f1/hh_s${s}_t03.jsonl"; B5R="$B5R $FM/banks_f1_return/hh_s${s}_t03.jsonl"; done
for s in 0 1 2; do B3="$B3 $FM/banks_f1/hh_s${s}_t03.jsonl"; B3R="$B3R $FM/banks_f1_return/hh_s${s}_t03.jsonl"; done
run(){ # run <out-subdir> <log-tag> <shift-days> <banks> <memories> <told> <workers>
  local sub=$1 tag=$2 sd=$3 banks=$4 mems=$5 told=$6 w=$7
  mkdir -p "$OUT/$sub"
  python3 -m baselines.patrol.llm --bank $banks --out "$OUT/$sub" --cache "$CACHE" --memory $mems --told $told --look off --workers $w --format conf > "$OUT/${sub}_${tag}.log" 2>&1
  echo "$(date +%H:%M) person chain $sub [$tag] exit=$?" >> "$LOG"
}
# 02:30: retrieval's no-message pass is complete on all 10 hh, so its start-message pass starts NOW (before reflection's
# no-message tail finishes) -- the server had 16 running / 0 waiting. Reflection's start-message waits for its no-message.
run told_entry retrieval 14,15 "$B10" retrieval told 30 &
p1=$!
while kill -0 977666 2>/dev/null; do sleep 60; done
echo "$(date +%H:%M) master3: no-message pass (pid 977666) exited" >> "$LOG"
python3 -m baselines.patrol.llm_strategy_check --dir "$OUT/nottold" --shift-days 14,15 >> "$LOG" 2>&1
run told_entry reflection5 14,15 "$B5" reflect told 10 &
p2=$!
wait $p1; wait $p2
python3 -m baselines.patrol.llm_strategy_check --dir "$OUT/told_entry" --shift-days 14,15 >> "$LOG" 2>&1
run told_entryreturn retrieval 14,15,24 "$B10R" retrieval told 30 &
p1=$!
run told_entryreturn reflection5 14,15,24 "$B5R" reflect told 10 &
p2=$!
wait $p1; wait $p2
python3 -m baselines.patrol.llm_strategy_check --dir "$OUT/told_entryreturn" --shift-days 14,15,24 >> "$LOG" 2>&1
echo "$(date +%H:%M) retrieval/reflection told passes done; long-context next (3 hh)" >> "$LOG"
run nottold longcontext3 14,15 "$B3" longcontext not_told 3
run told_entry longcontext3 14,15 "$B3" longcontext told 3
# two-spells no-message (buffer + retrieval, 3 hh) BEFORE long-context's start+end pass (coordinator, 02:05)
B2X=""; for s in 0 1 2; do B2X="$B2X ../results/regime_search/sick2x_owner/banks/hh_s${s}_t03.jsonl"; done
mkdir -p $R/chain_person2x/nottold $R/chain_person2x/told_entry
python3 -m baselines.patrol.llm --bank $B2X --out $R/chain_person2x/nottold --cache $R/chain_person2x/cache --memory naive retrieval --told not_told --look off --workers 6 --format conf > $R/chain_person2x/nottold.log 2>&1
echo "$(date +%H:%M) person2x chain no-message (buffer+retrieval, 3 hh) exit=$?" >> "$LOG"
python3 -m baselines.patrol.llm_strategy_check --dir $R/chain_person2x/nottold --shift-days 14,15,28,29 >> "$LOG" 2>&1
run told_entryreturn longcontext3 14,15,24 "$B3R" longcontext told 3
echo "$(date +%H:%M) PERSON CHAIN FINISHED (master2 sequence)" >> "$LOG"
python3 -m baselines.patrol.llm --bank $B2X --out $R/chain_person2x/told_entry --cache $R/chain_person2x/cache --memory naive retrieval --told told --look off --workers 6 --format conf > $R/chain_person2x/told_entry.log 2>&1
echo "$(date +%H:%M) person2x chain start-message (buffer+retrieval, 3 hh) exit=$?" >> "$LOG"
python3 -m baselines.patrol.llm_strategy_check --dir $R/chain_person2x/told_entry --shift-days 14,15,28,29 >> "$LOG" 2>&1
echo "$(date +%H:%M) PERSON2X CHAIN FINISHED" >> "$LOG"
