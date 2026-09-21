#!/bin/bash
# resumable: elicitation is cached by request hash; a finished library is skipped by elicit itself
cd ~/robot/dynamic_home_eqa/src
R=../results/confidence_shift_2026-09-20
E="python3 -m baselines.llm_hypotheses.elicit --longleaf --bank-dir /home/oliver/robot/dynamic_home_eqa/banks/patrol --conditions named --hyp-subdir patrol --endpoint http://127.0.0.1:8300 --model Qwen/Qwen3.8-27B --households"
$E hh_s10_p2 > $R/heldout/elicit_s10.log 2>&1; echo "elicit s10 exit $? $(date +%H:%M)"
python3 -m baselines.patrol.hyp --bank $R/heldout/banks/hh_s10_p2.jsonl --out $R/heldout/hyp --arms longleaf --told told not_told --passive > $R/heldout/hyp_s10.log 2>&1; echo "hyp s10 exit $? $(date +%H:%M)"
($E hh_s11_p2 > $R/heldout/elicit_s11.log 2>&1; echo "elicit s11 exit $?") & ($E hh_s12_p2 > $R/heldout/elicit_s12.log 2>&1; echo "elicit s12 exit $?") & wait
($E hh_s13_p2 > $R/heldout/elicit_s13.log 2>&1; echo "elicit s13 exit $?") & ($E hh_s14_p2 > $R/heldout/elicit_s14.log 2>&1; echo "elicit s14 exit $?") & wait
for s in 11 12 13 14; do python3 -m baselines.patrol.hyp --bank $R/heldout/banks/hh_s${s}_p2.jsonl --out $R/heldout/hyp --arms longleaf --told told not_told --passive > $R/heldout/hyp_s${s}.log 2>&1; echo "hyp s$s exit $? $(date +%H:%M)"; done
echo "HYP QUEUE DONE $(date +%H:%M)"
