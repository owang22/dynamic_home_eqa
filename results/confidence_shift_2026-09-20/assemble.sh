#!/bin/bash
# Final assembly: tables + figures + report.md, then the Longleaf Ledger page (publish separately with the Artifact tool).
cd ~/robot/dynamic_home_eqa/src
R=../results/confidence_shift_2026-09-20
python3 $R/make_report.py || exit 1
python3 -m baselines.patrol.hyp_explorer --study $R/heldout_fb/hyp/study --banks $R/heldout_fb/banks --classical $R/heldout_fb/classical --naive $R/heldout_fb/llm --out $R/ledger_live.html || exit 1
python3 -m baselines.patrol.leak_check --calls $R/heldout_fb/llm/*/calls.jsonl --out $R/heldout_fb/llm/leak_check.md | tail -2
echo "assembled $(date +%H:%M)"
