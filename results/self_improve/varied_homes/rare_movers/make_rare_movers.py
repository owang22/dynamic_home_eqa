#!/usr/bin/env python3
"""Build the rare-mover banks: varied_v2's ten households with two rare movers appended.

Same steps as results/self_improve/earlier_work/make_scenario.py (the script that built the
ten-home banks), with one addition between the simulation and the writers:
`situation_sim.rare_movers.add_rare_movers` runs on the finished run and appends the pill box
and the car keys. After the bank builder has drawn the ordinary 24 questions a day,
`rare_mover_questions` appends the questions about the rare movers and every question row gets
a `within_24h_of_rare_move` field.

Two bank sets come out, with the same rare-mover questions in both:
  banks/            the ordinary 24 questions a day (the ten-home bank's rows) plus the rare-mover rows
  banks_8_a_day/    the ordinary rows thinned to 8 a day with the harness's own even spacing
                    (search_driven.questions_spread_across_the_day, so the ids are exactly the ones the
                    ten-home 8-a-day cells asked) plus the same rare-mover rows

Two identity checks are made for every home and the build stops if either fails:
  * every truth row and resident row of the base objects equals the stored varied_v2 run
    (data/situation_sim/self_improve/varied_v2/hh_s<seed>/events.jsonl);
  * the base question rows equal the ten-home bank's questions field for field.

    python3 results/self_improve/varied_homes/rare_movers/make_rare_movers.py --seeds 2,19,20,32,48,63,93,109,123,151
"""
from __future__ import annotations

import argparse
import json
import os
import pathlib
import sys

REPO = pathlib.Path(__file__).resolve().parents[4]
HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(REPO / "src"))

import yaml  # noqa: E402

TEN_HOMES = REPO / "results/self_improve/varied_homes/ten_homes/banks"
BASE_SIMS = REPO / "data/situation_sim/self_improve/varied_v2"
HOMES = [2, 19, 20, 32, 48, 63, 93, 109, 123, 151]


def parse_seeds(spec: str):
    out = []
    for part in spec.split(","):
        if "-" in part:
            a, b = part.split("-")
            out += list(range(int(a), int(b) + 1))
        else:
            out.append(int(part))
    return out


def simulate(cfg, seed, sim_dir, events_path, activities_path):
    from situation_sim.household import sample_household
    from situation_sim.placement import compute_allowed
    from situation_sim.rare_movers import add_rare_movers
    from situation_sim.schedule import load_activities
    from situation_sim.simulate import Simulator
    from situation_sim.situation import load_episodes, load_events, sample_situations
    from situation_sim.trace import write_events, write_hidden_state, write_trace, write_trace_json

    out = sim_dir / f"hh_s{seed}"
    out.mkdir(parents=True, exist_ok=True)
    events = load_events(events_path)
    episodes = load_episodes()
    acts = load_activities(activities_path)
    for name, rates in (cfg.get("events") or {}).items():
        if name in events:
            events[name]["p_day"] = dict(rates)
    hh = sample_household(seed, acts)
    calendar = cfg["calendar"]
    compute_allowed(hh, acts, events)
    sits = sample_situations(hh, seed, cfg["days"], events, episodes,
                             day0=cfg.get("day0", "Monday"), calendar=calendar)
    episode_id = f"{hh.id}_situation_seed{seed}"
    res = Simulator(hh, sits, events, acts, seed, episode_id).run()

    # identity check 1: the base run is the stored varied_v2 run, row for row
    base_rows = [json.loads(l) for l in (BASE_SIMS / f"hh_s{seed}" / "events.jsonl").read_text().splitlines()]
    base_truth = sorted((r for r in base_rows if r["kind"] == "truth"), key=lambda r: (r["t"], r["object_id"]))
    base_res = sorted((r for r in base_rows if r["kind"] == "resident"), key=lambda r: (r["t"], r["resident_id"]))
    ours_truth = sorted(res.truth_rows, key=lambda r: (r["t"], r["object_id"]))
    ours_res = sorted(res.resident_rows, key=lambda r: (r["t"], r["resident_id"]))
    if ours_truth != base_truth or ours_res != base_res:
        raise SystemExit(f"seed {seed}: the base simulation does not reproduce varied_v2; stopping")

    manifest = add_rare_movers(hh, sits, res, cfg.get("rare_movers"), seed)
    # the base rows are still there, untouched, after the pass
    after = sorted((r for r in res.truth_rows if not r.get("rare_mover")), key=lambda r: (r["t"], r["object_id"]))
    if after != base_truth:
        raise SystemExit(f"seed {seed}: the rare-mover pass altered a base truth row; stopping")

    write_trace(out / "trace.md", hh, res, events)
    write_events(out / "events.jsonl", hh, res, cfg["days"], episode_id)
    write_hidden_state(out / "hidden_state.json", hh, sits, res, events, seed, episodes)
    write_trace_json(out / "trace.json", hh, res)
    (out / "rare_movers.json").write_text(json.dumps(manifest, indent=1))
    return out, manifest


def bank(cfg, run_dir, out_path, activities_path, manifest, seed, loads=(24, 8)):
    import baselines.patrol.bank as bankmod
    from baselines.patrol.bank import build_bank, _Truth, _rows
    from situation_sim.rare_movers import rare_mover_questions
    acts = yaml.safe_load(pathlib.Path(activities_path).read_text())["activities"]
    bankmod.load_activities = lambda: acts
    os.environ["PATROL_QUESTION_MOMENT"] = str(cfg.get("question_moment", "during"))
    os.environ["PATROL_QUESTION_MIN_GAP_MIN"] = str(int(cfg.get("question_min_gap_min", 30)))
    os.environ["PATROL_QUESTION_OWNERS"] = ",".join(cfg.get("question_owners") or [])
    os.environ.pop("PATROL_QUESTION_HOURS", None)
    times = [t.strip() for t in str(cfg.get("patrol_times", "03:00")).split(",") if t.strip()]
    minutes = [int(t.split(":")[0]) * 60 + int(t.split(":")[1]) for t in times]
    building = out_path.with_name(out_path.stem + ".building.jsonl")    # never the kept file itself
    build_bank(run_dir, building, patrol_hours=int(cfg.get("patrol_hours", 0)), patrol_times=minutes,
               questions=cfg.get("questions", "activity"), classes=cfg.get("classes"),
               per_day=int(cfg.get("per_day", 24)), oversample=int(cfg.get("oversample", 1024)),
               shift_focus=float(cfg.get("shift_focus", 0.0)), feedback_delay_min=cfg.get("feedback_delay_min"))

    rows = _rows(building)
    building.unlink()
    header = rows[0]
    questions = [r for r in rows if r["kind"] == "question"]
    others = [r for r in rows if r["kind"] != "question"][1:]

    # identity check 2: the base questions are the ten-home bank's
    ref_path = TEN_HOMES / out_path.name
    if ref_path.exists():
        ref_q = [json.loads(l) for l in ref_path.read_text().splitlines() if '"kind": "question"' in l]
        ref_q = [r for r in ref_q if r["kind"] == "question"]
        if [json.dumps(q, sort_keys=True) for q in questions] != [json.dumps(q, sort_keys=True) for q in ref_q]:
            raise SystemExit(f"{out_path.name}: the base questions differ from the ten-home bank; stopping")
    else:
        print(f"  (no ten-home bank named {out_path.name}; base-question identity not checked)")

    truth = _Truth([r for r in rows if r["kind"] == "truth"])
    stage_of_day = {int(k): v for k, v in (header.get("stages") or {}).items()}
    classes = header["object_classes"]
    extra, counts = rare_mover_questions(manifest, truth.at, classes, header["scored_days"], header["episode_id"],
                                         seed, stage_of_day, cfg.get("rare_movers"))
    for q in questions:
        q["rare_mover"] = False
        q["within_24h_of_rare_move"] = False
    header["rare_movers"] = {"objects": manifest["objects"], "n_place_changes": manifest["n_place_changes"],
                             "question_counts": counts, "settings": manifest["settings"],
                             "not_built": manifest["not_built"]}
    side_body = {"moves": manifest["moves"], "objects": manifest["objects"], "question_counts": counts,
                 "questions": [{k: q[k] for k in ("question_id", "object_id", "t_query", "day_index",
                                                  "within_24h_of_rare_move", "in_first_hour_after_rare_move",
                                                  "rare_move_t", "rare_move_rank", "hours_since_rare_move")}
                               for q in extra]}

    def write(path, base_rows, load_note):
        hdr = dict(header)
        hdr["ordinary_questions_per_day"] = load_note
        all_q = sorted(base_rows + extra, key=lambda q: (q["t_query"], q["question_id"]))
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w") as f:
            f.write(json.dumps(hdr, sort_keys=True) + "\n")
            for r in others:
                f.write(json.dumps(r, sort_keys=True) + "\n")
            for r in all_q:
                f.write(json.dumps(r, sort_keys=True) + "\n")
        path.with_name(path.stem + "_rare_moves.json").write_text(json.dumps(side_body, indent=1))

    if 24 in loads:
        write(out_path, questions, 24)
    # the 8-a-day set: the harness's own even spacing over each day's ordinary rows
    from self_improve.search_driven import questions_spread_across_the_day
    thinned = []
    for day in sorted({q["day_index"] for q in questions}):
        thinned += questions_spread_across_the_day([q for q in questions if q["day_index"] == day], 8)
    if 8 in loads:
        write(out_path.parent.parent / "banks_8_a_day" / out_path.name, thinned, 8)
    counts["ordinary_questions_24"] = len(questions)
    counts["ordinary_questions_8"] = len(thinned)
    return counts


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", type=pathlib.Path, default=HERE / "rare_movers_v1.yaml")
    ap.add_argument("--seeds", default=",".join(str(s) for s in HOMES))
    ap.add_argument("--out", type=pathlib.Path, default=HERE)
    ap.add_argument("--loads", default="24,8", help="which bank sets to write: 24, 8 or 24,8")
    a = ap.parse_args(argv)
    loads = tuple(int(x) for x in a.loads.split(","))
    cfg = yaml.safe_load(a.config.read_text())
    base = a.config.parent
    sim_dir = (base / cfg["sim_dir"]).resolve()
    events_path = (base / cfg["events_file"]).resolve()
    activities_path = (base / cfg["activities_file"]).resolve()
    label = "t" + str(cfg.get("patrol_times", "03:00")).split(",")[0].split(":")[0]
    (a.out / "banks").mkdir(parents=True, exist_ok=True)
    (a.out / "banks_8_a_day").mkdir(parents=True, exist_ok=True)
    (a.out / "config.yaml").write_text(yaml.safe_dump(cfg, sort_keys=True))
    summary = {}
    for seed in parse_seeds(a.seeds):
        run_dir, manifest = simulate(cfg, seed, sim_dir, events_path, activities_path)
        bank_path = a.out / "banks" / f"hh_s{seed}_{label}.jsonl"
        counts = bank(cfg, run_dir, bank_path, activities_path, manifest, seed, loads)
        summary[f"hh_s{seed}_{label}"] = {"place_changes": manifest["n_place_changes"], **counts}
        print(f"  seed {seed}: {bank_path.name}  place changes {manifest['n_place_changes']}, "
              f"rare-mover questions {counts['questions']} ({counts['within_24h']} within 24 h, "
              f"{counts['first_hour']} in the first hour, {counts['background_random']} random background; {counts['questions_first_hour']}+"
              f"{counts['questions_rest_of_day_used']} per move); ordinary 24/day {counts['ordinary_questions_24']}, "
              f"8/day {counts['ordinary_questions_8']}")
    (a.out / "build_summary.json").write_text(json.dumps(summary, indent=1))
    print(f"banks in {a.out}/banks (ordinary 24 a day) and {a.out}/banks_8_a_day (ordinary 8 a day)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
