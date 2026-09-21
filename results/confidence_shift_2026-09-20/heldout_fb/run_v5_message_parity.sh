#!/bin/bash
# v5 (03:20): told arms only, message-triggered documents enter at parity with the leading document
# (HYPOTHESIS_MESSAGE_ENTRY=parity); everything else as v4. Output kept apart from the v4 study.
cd ~/robot/dynamic_home_eqa/src
R=../results/confidence_shift_2026-09-20
export PARTICLE_NEGATIVE_HALF_LIFE_H=1e-9 TIMETABLE_INTERIOR_MIN_EDGE=0.9 TIMETABLE_PRIOR_DECAYS=0 HYPOTHESIS_ENTRY=share_cap HYPOTHESIS_MIN_LIKELIHOOD=1e-3 TIMETABLE_RECENCY_HALF_LIFE_H=4 HYPOTHESIS_DECAY=0.998 HYPOTHESIS_LL_TEMPER=0.03 CLAIM_TRIGGER_RELATIVE=1 TIMETABLE_FALLBACK_BIN_H=2 TIMETABLE_EVIDENCE_BLEND=0.7 TIMETABLE_EVIDENCE_MIN_COUNT=1 LONGLEAF_SCHEDULED_DAYS=2,3,4,5,6,7 HYPOTHESIS_MESSAGE_ENTRY=parity
OUT=$R/heldout_fb/hyp_v5_message_parity
mkdir -p $OUT/study $OUT/logs
run(){ s=$1
  python3 -m baselines.llm_hypotheses.run_tour_start --household hh_s${s}_t03 --arm passive:longleaf:longleaf_named --bank-dir /home/oliver/robot/dynamic_home_eqa/banks/patrol --room-look --endpoint http://127.0.0.1:8300 --model Qwen/Qwen3.8-27B --out-dir $OUT/study --hyp-subdir patrol --told > $OUT/arm_s${s}_told.log 2>&1; echo "v5 arm s$s told exit $? $(date +%H:%M)"; }
for s in $HH; do run $s & done; wait
for s in $HH; do python3 - <<PY
import sys, pathlib, json
sys.argv = ["x"]
from baselines.patrol.hyp import convert_passive
R = pathlib.Path("$OUT"); B = pathlib.Path("$R/heldout_fb/banks")
bank = B / "hh_s${s}_t03.jsonl"; header = json.loads(bank.read_text().splitlines()[0])
arm_dir = R / "study/hh_s${s}_t03__bank0/arms/passive/passive__longleaf__longleaf_named__told"
if (arm_dir / "per_question.jsonl.gz").exists():
    out = R / "logs" / "hh_s${s}_t03_longleaf_told.jsonl"
    print("converted", convert_passive(arm_dir, bank, header, "longleaf", True, out), "->", out)
PY
done
echo "V5 ARMS DONE $(date +%H:%M)"
