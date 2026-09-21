#!/bin/bash
# feedback protocol: told arms for hh_s10-14 in parallel; then not-told (pre-shift revisions replay from cache); then convert
cd ~/robot/dynamic_home_eqa/src
R=../results/confidence_shift_2026-09-20
export PARTICLE_NEGATIVE_HALF_LIFE_H=1e-9 TIMETABLE_INTERIOR_MIN_EDGE=0.9 TIMETABLE_PRIOR_DECAYS=0 HYPOTHESIS_ENTRY=share_cap HYPOTHESIS_MIN_LIKELIHOOD=1e-3 TIMETABLE_RECENCY_HALF_LIFE_H=4 HYPOTHESIS_DECAY=0.998 HYPOTHESIS_LL_TEMPER=0.03 CLAIM_TRIGGER_RELATIVE=1 TIMETABLE_FALLBACK_BIN_H=2 TIMETABLE_EVIDENCE_BLEND=0.7 TIMETABLE_EVIDENCE_MIN_COUNT=1 LONGLEAF_SCHEDULED_DAYS=1,2,3,4,5,6,7
run(){ s=$1; told=$2; extra=""; [ $told = told ] && extra="--told"
  python3 -m baselines.llm_hypotheses.run_tour_start --household hh_s${s}_t03 --arm passive:longleaf:longleaf_named --bank-dir /home/oliver/robot/dynamic_home_eqa/banks/patrol --room-look --endpoint http://127.0.0.1:8300 --model Qwen/Qwen3.8-27B --out-dir $R/heldout_fb/hyp/study --hyp-subdir patrol $extra > $R/heldout_fb/arm_s${s}_${told}.log 2>&1; echo "arm s$s $told exit $? $(date +%H:%M)"; }
for s in 10 11 12 13 14; do run $s told & done; wait
echo "told arms done $(date +%H:%M); starting not-told"
for s in 10 11 12 13 14; do run $s nottold & done; wait
for s in 10 11 12 13 14; do python3 - <<PY
import sys, pathlib, json
sys.argv = ["x"]
from baselines.patrol.hyp import convert_passive
R = pathlib.Path("$R/heldout_fb")
bank = R / "banks" / "hh_s${s}_t03.jsonl"; header = json.loads(bank.read_text().splitlines()[0])
for told in ("told", "nottold"):
    arm_dir = R / "hyp/study/hh_s${s}_t03__bank0/arms/passive" / f"passive__longleaf__longleaf_named__{told}"
    if not (arm_dir / "per_question.jsonl.gz").exists(): continue
    out = R / "hyp/logs" / f"hh_s${s}_t03_longleaf_{'told' if told == 'told' else 'not_told'}.jsonl"; out.parent.mkdir(parents=True, exist_ok=True)
    print("converted", convert_passive(arm_dir, bank, header, "longleaf", told == "told", out), "->", out)
PY
done
echo "FB ARMS DONE $(date +%H:%M)"
