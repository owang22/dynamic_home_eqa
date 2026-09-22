cd ~/robot/dynamic_home_eqa/src || exit 1
R=../results/confidence_shift_2026-09-20/uq/llm_strategies
OUT=$R/chain_person; LOG=$R/chain_progress.log; CACHE=$OUT/cache
FM=/home/oliver/robot/dynamic_home_eqa_fm/results/fm_memory
B10=""; B5=""; B10R=""; B5R=""; B3=""; B3R=""; B2X=""
for s in 0 1 2 3 4 5 6 7 8 9; do B10="$B10 $FM/banks_f1/hh_s${s}_t03.jsonl"; B10R="$B10R $FM/banks_f1_return/hh_s${s}_t03.jsonl"; done
for s in 0 1 2 3 4; do B5="$B5 $FM/banks_f1/hh_s${s}_t03.jsonl"; B5R="$B5R $FM/banks_f1_return/hh_s${s}_t03.jsonl"; done
for s in 0 1 2; do B3="$B3 $FM/banks_f1/hh_s${s}_t03.jsonl"; B3R="$B3R $FM/banks_f1_return/hh_s${s}_t03.jsonl"; B2X="$B2X ../results/regime_search/sick2x_owner/banks/hh_s${s}_t03.jsonl"; done
run(){ local sub=$1 tag=$2 banks=$3 mems=$4 told=$5 w=$6; mkdir -p "$OUT/$sub"
  python3 -m baselines.patrol.llm --bank $banks --out "$OUT/$sub" --cache "$CACHE" --memory $mems --told $told --look off --workers $w --format conf > "$OUT/${sub}_${tag}.log" 2>&1
  echo "$(date +%H:%M) person chain $sub [$tag] exit=$?" >> "$LOG"; }
chk(){ python3 -m baselines.patrol.llm_strategy_check --dir "$OUT/$1" --shift-days $2 >> "$LOG" 2>&1; }
