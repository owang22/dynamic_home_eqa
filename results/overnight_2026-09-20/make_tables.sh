#!/bin/sh
# Rebuild every summary table, figure and the leak report from the run logs.
set -e
cd "$(dirname "$0")/../../src"
R=../results/overnight_2026-09-20
python3 -m baselines.patrol.summary --logs "$R/classical/*.jsonl" --banks "$R/banks/*.jsonl" --out $R/classical_summary.md --title "Classical agents, 20 households, 4 patrol densities, look off / voi / top" > /dev/null
# LLM arms next to the classical agents on the same banks (4 h patrol, households the LLM ran on)
HH=$(ls $R/llm/ | grep _p4_ | sed 's/_p4_.*//' | sort -u | tr '\n' ' ')
LOGS=""; for h in $HH; do LOGS="$LOGS $R/classical/${h}_p4_off.jsonl $R/classical/${h}_p4_voi.jsonl $R/classical/${h}_p4_off_perpetua.jsonl $R/classical/${h}_p4_voi_perpetua.jsonl"; done
python3 -m baselines.patrol.summary --logs "$R/llm/*_p4_*/run_log.jsonl" $LOGS --banks "$R/banks/*_p4.jsonl" --out $R/llm_summary_p4.md --title "LLM agents vs classical agents, 4 h patrol, households: $HH" > /dev/null
# LLM density check (1 h and 8 h banks, look on)
if ls $R/llm/*_p1_* > /dev/null 2>&1; then
  HH=$(ls $R/llm/ | grep -E "_p(1|8)_" | sed 's/_p[18]_.*//' | sort -u | tr '\n' ' ')
  LOGS=""; for h in $HH; do for p in 1 4 8; do LOGS="$LOGS $R/llm/${h}_p${p}_*_lookon/run_log.jsonl $R/classical/${h}_p${p}_off.jsonl $R/classical/${h}_p${p}_voi.jsonl"; done; done
  python3 -m baselines.patrol.summary --logs $LOGS --banks "$R/banks/*.jsonl" --out $R/llm_summary_density.md --title "LLM agents vs patrol density (look on), households: $HH" > /dev/null
fi
python3 -m baselines.patrol.figures --logs "$R/classical/*.jsonl" "$R/llm/*_p4_*/run_log.jsonl" --banks "$R/banks/*.jsonl" --out $R/figs
python3 -m baselines.patrol.leak_check --calls "$R/llm/*/calls.jsonl" --out $R/leak_report.md > /dev/null && echo "leak check: clean" || echo "leak check: LEAKS FOUND"
