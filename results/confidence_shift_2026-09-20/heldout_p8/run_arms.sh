#!/bin/bash
# run both passive longleaf arms for one household in parallel, then convert the logs
cd ~/robot/dynamic_home_eqa/src
R=../results/confidence_shift_2026-09-20
# method configuration for the confidence study (see problems_found.md)
export PARTICLE_NEGATIVE_HALF_LIFE_H=1e-9 TIMETABLE_INTERIOR_MIN_EDGE=0.9 TIMETABLE_PRIOR_DECAYS=0 HYPOTHESIS_ENTRY=share HYPOTHESIS_DECAY=0.985 HYPOTHESIS_LL_TEMPER=0.03 CLAIM_TRIGGER_RELATIVE=1
s=$1
for told in told nottold; do
  extra=""; [ $told = told ] && extra="--told"
  (python3 -m baselines.llm_hypotheses.run_tour_start --household hh_s${s}_p8 --arm passive:longleaf:longleaf_named --bank-dir /home/oliver/robot/dynamic_home_eqa/banks/patrol --room-look --endpoint http://127.0.0.1:8300 --model Qwen/Qwen3.8-27B --out-dir $R/heldout_p8/hyp/study --hyp-subdir patrol $extra > $R/heldout_p8/arm_s${s}_${told}.log 2>&1; echo "arm s$s $told exit $? $(date +%H:%M)") &
done
wait
python3 -m baselines.patrol.hyp --bank $R/heldout_p8/banks/hh_s${s}_p8.jsonl --out $R/heldout_p8/hyp --arms longleaf --told told not_told --passive --dry-run > /dev/null 2>&1
python3 - <<PY
import sys, pathlib
sys.argv = ["x"]
from baselines.patrol.hyp import convert_passive
import json
R = pathlib.Path("$R/heldout")
bank = R / "banks" / "hh_s${s}_p8.jsonl"
header = json.loads(bank.read_text().splitlines()[0])
for told in ("told", "nottold"):
    arm_dir = R / "hyp/study/hh_s${s}_p8__bank0/arms/passive" / f"passive__longleaf__longleaf_named__{told}"
    out = R / "hyp/logs" / f"hh_s${s}_p8_longleaf_{'told' if told == 'told' else 'not_told'}.jsonl"
    out.parent.mkdir(parents=True, exist_ok=True)
    print("converted", convert_passive(arm_dir, bank, header, "longleaf", told == "told", out), "->", out)
PY
echo "ARMS s$s DONE $(date +%H:%M)"
