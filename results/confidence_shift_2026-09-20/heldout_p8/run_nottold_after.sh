#!/bin/bash
# start the not-told arms once the told arms have finished: their pre-shift revisions replay from cache
cd ~/robot/dynamic_home_eqa/src
R=../results/confidence_shift_2026-09-20
export PARTICLE_NEGATIVE_HALF_LIFE_H=1e-9 TIMETABLE_INTERIOR_MIN_EDGE=0.9 TIMETABLE_PRIOR_DECAYS=0 HYPOTHESIS_ENTRY=share HYPOTHESIS_DECAY=0.985 HYPOTHESIS_LL_TEMPER=0.03 CLAIM_TRIGGER_RELATIVE=1
while ps -o cmd= -C python3 | grep "run_tour_start --household hh_s1[0-4]_p8" | grep -q -- "--told"; do sleep 60; done
echo "told arms finished $(date +%H:%M); starting not-told"
for s in 10 11 12 13 14; do
  (python3 -m baselines.llm_hypotheses.run_tour_start --household hh_s${s}_p8 --arm passive:longleaf:longleaf_named --bank-dir /home/oliver/robot/dynamic_home_eqa/banks/patrol --room-look --endpoint http://127.0.0.1:8300 --model Qwen/Qwen3.8-27B --out-dir $R/heldout_p8/hyp/study --hyp-subdir patrol > $R/heldout_p8/arm_s${s}_nottold.log 2>&1; echo "arm s$s nottold exit $? $(date +%H:%M)") &
done
wait
for s in 10 11 12 13 14; do python3 - <<PY
import sys, pathlib, json
sys.argv = ["x"]
from baselines.patrol.hyp import convert_passive
R = pathlib.Path("$R/heldout_p8")
bank = R / "banks" / "hh_s${s}_p8.jsonl"; header = json.loads(bank.read_text().splitlines()[0])
for told in ("told", "nottold"):
    arm_dir = R / "hyp/study/hh_s${s}_p8__bank0/arms/passive" / f"passive__longleaf__longleaf_named__{told}"
    if not (arm_dir / "per_question.jsonl.gz").exists(): continue
    out = R / "hyp/logs" / f"hh_s${s}_p8_longleaf_{'told' if told == 'told' else 'not_told'}.jsonl"; out.parent.mkdir(parents=True, exist_ok=True)
    print("converted", convert_passive(arm_dir, bank, header, "longleaf", told == "told", out), "->", out)
PY
done
echo "NOT-TOLD DONE $(date +%H:%M)"
