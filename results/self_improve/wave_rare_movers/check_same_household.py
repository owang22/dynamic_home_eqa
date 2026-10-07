#!/usr/bin/env python3
"""Is the rare-mover bank the same household as the ten-home bank, apart from the added objects?
Replays last-seen on the rare-mover bank with every rare-mover question removed (patched onto
FrozenHousehold in this process only) at 24 questions a day, and compares each search with the
ten-home 24-a-day last-seen cell. Run 2026-10-02: all ten households, every search identical
(744 of 744; hh_s93 743 of 743).

    PYTHONPATH=src python3 results/self_improve/wave_rare_movers/check_same_household.py [out_dir]
"""
import json, pathlib, sys
sys.path.insert(0, "src")
from self_improve import overnight_wave as ow
from self_improve.frozen_household import FrozenHousehold

OUT = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "results/self_improve/wave_rare_movers/check_same_household")
HOMES = ["hh_s2_t03", "hh_s19_t03", "hh_s20_t03", "hh_s32_t03", "hh_s48_t03", "hh_s63_t03",
         "hh_s93_t03", "hh_s109_t03", "hh_s123_t03", "hh_s151_t03"]
_orig = FrozenHousehold.__init__


def base_only(self, bank_path):
    _orig(self, bank_path)
    self.questions = [q for q in self.questions if not q.get("rare_mover")]
    self.asked_objects = sorted({q["object_id"] for q in self.questions})


FrozenHousehold.__init__ = base_only


def load(p):
    return {json.loads(l)["question_id"]: json.loads(l) for l in open(p) if '"kind": "search"' in l}


for home in HOMES:
    if not (OUT / "cells/last_seen_no_model" / home / "cell.json").exists():
        ow.main(["--arm", "last seen, no model", "--household", home,
                 "--banks", "results/self_improve/varied_homes/rare_movers/banks", "--last-day", "31",
                 "--questions-per-day", "24", "--budget", "3", "--seed", "0", "--out", str(OUT),
                 "--cache", "llm_prior_cache/self_improve"])
    ref = load(f"results/self_improve/overnight_wave_24_questions/cells/last_seen_no_model/{home}/searches.jsonl")
    ours = load(OUT / "cells/last_seen_no_model" / home / "searches.jsonl")
    same = sum(1 for q in ref if q in ours and ref[q]["rooms_opened"] == ours[q]["rooms_opened"]
               and ref[q]["answer_place"] == ours[q]["answer_place"])
    print(f"{home}: {same} of {len(ref)} searches identical to the ten-home 24/day cell; first guess right "
          f"ref {sum(r.get('found_at_step') == 1 for r in ref.values())}, ours {sum(r.get('found_at_step') == 1 for r in ours.values())}")
