"""Stage 1b — pre-Stage-2 review battery and re-gate.

Runs the full A–F battery from the pre-Stage-2 brief on top of the Stage 1
probe harness:

  A1–A3  dataset characterization (volatility / predictability / class
         coupling) — emitted FIRST because it reframes everything downstream.
  B1     probe sampling stratified by volatility tercile; every metric
         reported per stratum (aggregate demoted to one row).
  B2     displaced (parent changed over the interval — the real predictive
         test) vs returned vs stable splits; acc(displaced) is the headline.
  B3     transition-conditioned partition + probe_transition_features.parquet.
  B4     transition-aware tick grid (fine points at the object's own
         routine-transition times; heatmaps keep the uniform subset).
  B5     cluster-bootstrap 95% CIs on every accuracy number.
  B6     noted only: the generator has no routine-tightness knob yet.
  C1     room_now option-distinctness verification over generated sets.
  C2     b3 elsewhere-mass logging (the source fix lives in perpetua._fit).
  C3     Δt-R² dropped for b1 (Δt is not a model input there) + nested
         Δt-vs-Δt+time-of-day F-test per time-aware tier.
  D1/D2  ECE + reliability diagrams; temperature fitted on ONE held-out test
         day and evaluated on the others — reported, never baked in.
  E1     two-anchor diagnostic for b3 (dynamic stratum): prior-quality vs
         insufficient-anchoring attribution.
  F      re-gate table + SUMMARY.md answering the five go/no-go questions.

    python -m dynbelief.experiments.stage1b [--config .../stage1b.yaml]
"""
from __future__ import annotations

import argparse
import json
import pathlib

import numpy as np
import pandas as pd
import yaml

from dynamic_home_eqa.paths import REPO_ROOT
from dynbelief import ELSEWHERE_ID, MIN_PER_DAY
from dynbelief.beliefs import make_belief
from dynbelief.beliefs.fremen import constant_prior
from dynbelief.eqa.analysis import (apply_temperature, bootstrap_ci,
                                    class_volatility_coupling, ece,
                                    fit_temperature, nested_tod_test,
                                    predictability_table, volatility_summary,
                                    volatility_table)
from dynbelief.eqa.generate import make_question, validate_question_set
from dynbelief.eqa.probe import (accuracy_surface, delta_t_symmetry,
                                 plot_surface, probe_object, train_belief)
from dynbelief.experiments.stage0 import _discover_folders
from dynbelief.logging import log_episode
from dynbelief.priors.schedule_prior import PerClassPrior, load_schedule_prior
from dynbelief.replay import ReplayWorld

TERCILES = ["static", "occasional", "dynamic"]


def _tier_label(tcfg: dict) -> str:
    return tcfg["name"] + (f"({tcfg['f_source']})" if "f_source" in tcfg else "")


def _hist(values, title: str, xlabel: str, out_path) -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    vals = [v for v in values if v is not None]
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.hist(vals, bins=20, color="#4477aa", edgecolor="white")
    ax.set_title(title, fontsize=9)
    ax.set_xlabel(xlabel)
    ax.set_ylabel("objects")
    fig.tight_layout()
    fig.savefig(out_path, dpi=130)
    plt.close(fig)


def _reliability_plot(curve: list[dict], title: str, out_path) -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    xs = [c["conf"] for c in curve if c["n"] > 0]
    ys = [c["acc"] for c in curve if c["n"] > 0]
    ns = [c["n"] for c in curve if c["n"] > 0]
    fig, ax = plt.subplots(figsize=(5, 5))
    ax.plot([0, 1], [0, 1], "k--", lw=0.8, label="perfect")
    ax.plot(xs, ys, "o-", color="#cc3311", label="model")
    for x, y, n in zip(xs, ys, ns):
        ax.annotate(str(n), (x, y), fontsize=6, xytext=(2, 4),
                    textcoords="offset points")
    ax.set_xlabel("confidence (p_chosen)")
    ax.set_ylabel("accuracy")
    ax.set_xlim(0, 1); ax.set_ylim(0, 1)
    ax.set_title(title, fontsize=9)
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(out_path, dpi=130)
    plt.close(fig)


def _ci(recs: list[dict], n_boot: int, seed: int) -> dict:
    """mean + cluster-bootstrap CI + n, as one compact dict."""
    m, lo, hi = bootstrap_ci(recs, "correct", "obj", n_boot=n_boot, seed=seed)
    return {"acc": m, "lo": lo, "hi": hi, "n": len(recs),
            "n_obj": len({r["obj"] for r in recs})}


def _fmt(c: dict) -> str:
    if not c["n"]:
        return "—"
    return f"{c['acc']:.3f} [{c['lo']:.3f},{c['hi']:.3f}] (n={c['n']})"


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--config", default=str(REPO_ROOT / "src/dynbelief/configs/stage1b.yaml"))
    args = ap.parse_args()
    cfg = yaml.safe_load(open(args.config))

    gen_dir = REPO_ROOT / cfg["episode"]["gen_dir"]
    folders = cfg["episode"]["folders"] or _discover_folders(gen_dir)
    ep_dir = REPO_ROOT / cfg["episode"]["out_dir"]
    log_episode(gen_dir, folders, ep_dir)
    world = ReplayWorld(ep_dir)

    p = cfg["probe"]
    train_days, test_days = p["train_days"], p["test_days"]
    assert not set(train_days) & set(test_days)
    assert max(test_days) < world.n_days
    seed, n_boot = p["seed"], p["n_boot"]
    rng = np.random.default_rng(seed)

    report_dir = REPO_ROOT / cfg["report_dir"]
    cal_dir = report_dir / "calibration"
    cal_dir.mkdir(parents=True, exist_ok=True)

    # ── A. dataset characterization ──────────────────────────────────────────
    vol = volatility_table(world)
    pd.DataFrame(vol).to_csv(report_dir / "volatility.csv", index=False)
    vol_sum = volatility_summary(vol)
    _hist([r["moves_per_day"] for r in vol], "A1 per-object moves/day",
          "moves per day", report_dir / "volatility_hist.png")

    pred = predictability_table(world)
    pd.DataFrame(pred).to_csv(report_dir / "predictability.csv", index=False)
    _hist([r["predictability"] for r in pred], "A2 per-object predictability",
          "predictability (repeat24h ⊕ move concentration)",
          report_dir / "predictability_hist.png")
    pred_of = {r["obj_id"]: r["predictability"] for r in pred}
    nonstatic_pred = [r["predictability"] for r in pred if r["n_moves"] > 0]

    coupling = class_volatility_coupling(vol)
    (report_dir / "class_volatility_coupling.json").write_text(
        json.dumps(coupling, indent=1))
    print(f"A1 {vol_sum} | A2 median pred(nonstatic)="
          f"{np.median(nonstatic_pred):.3f} | A3 eta2={coupling['eta2_class_on_volatility']}")

    # ── B1. stratified target sampling ────────────────────────────────────────
    tercile_of = {r["obj_id"]: r["tercile"] for r in vol}
    test_set = set(test_days)
    moves_on_test = {o: sorted(t for t in world.change_times(o)
                               if t // MIN_PER_DAY in test_set)
                     for o in world.objects()}
    targets, stratum_of = [], {}
    for terc in TERCILES:
        members = [o for o in world.objects() if tercile_of[o] == terc]
        # objects that actually move on a test day first (they carry the
        # displaced cells the headline metric lives on), then the rest
        movers = [o for o in members if moves_on_test[o]]
        rest = [o for o in members if not moves_on_test[o]]
        rng.shuffle(movers); rng.shuffle(rest)
        take = (movers + rest)[:p["per_stratum_cap"]]
        targets += take
        for o in take:
            stratum_of[o] = terc
    print("B1 targets/stratum: " +
          ", ".join(f"{t}={sum(1 for o in targets if stratum_of[o] == t)}"
                    for t in TERCILES))

    # ── C1. room_now distinctness over a broad generated set ─────────────────
    c1_qs, c1_bad = [], 0
    for day in test_days:
        d0 = day * MIN_PER_DAY
        for obj in targets:
            for s_off, q_off in [(300, 720), (480, 1140), (60, 1380)]:
                q = make_question(world, "room_now", obj, d0 + s_off, d0 + q_off,
                                  seed=seed)
                c1_qs.append(q)
                if len(set(map(str, q["options"]))) != 4:
                    c1_bad += 1
    c1_val = validate_question_set(c1_qs)  # asserts distinctness + truth presence
    c1 = {"n_room_now_checked": len(c1_qs), "n_with_duplicate_rooms": c1_bad,
          "index_balance": c1_val["index_balance"]}
    (report_dir / "c1_room_now_check.json").write_text(json.dumps(c1, indent=1))

    # ── B4. per-(object, test day) transition-aware tick times ───────────────
    trans_tods = {(o, d): [t % MIN_PER_DAY for t in moves_on_test[o]
                           if t // MIN_PER_DAY == d]
                  for o in targets for d in test_days}
    day_transitions = sorted({e["t_min"] % MIN_PER_DAY
                              for e in world.events(moved_by="human")
                              if e["t_min"] // MIN_PER_DAY in test_set})

    # ── probe sweep over tiers ────────────────────────────────────────────────
    train_min = (max(train_days) + 1) * MIN_PER_DAY
    all_recs: dict[tuple[str, str], list[dict]] = {}
    trained: dict[str, object] = {}   # kept for the E1 rerun (same trained rates)
    tier_labels = []
    for tcfg in p["tiers"]:
        label = _tier_label(tcfg)
        tier_labels.append(label)
        if tcfg.get("f_source") == "schedule_prior":
            priors = load_schedule_prior(ep_dir, world, train_days)
            belief = make_belief(tcfg["name"], world,
                                 switching_prior=PerClassPrior(priors, constant_prior()))
        else:
            belief = make_belief(tcfg["name"], world,
                                 f_source=tcfg.get("f_source", "fremen"),
                                 train_horizon_min=train_min)
        train_belief(belief, world, train_days, feed_min=p["train_feed_min"])

        for qtype in p["qtypes"]:
            records = []
            for day in test_days:
                for obj in targets:
                    rs = probe_object(belief, world, obj, day, qtype,
                                      grid_min=p["grid_min"], seed=seed,
                                      transition_tods=trans_tods[(obj, day)])
                    for r in rs:
                        r["stratum"] = stratum_of[obj]
                    records.extend(rs)
            all_recs[(label, qtype)] = records
            df = pd.DataFrame(records)
            stem = f"probe__{label}__{qtype}__grid{p['grid_min']}__seed{seed}"
            try:
                df.to_parquet(report_dir / f"{stem}.parquet")
            except (ImportError, ValueError):
                df.to_csv(report_dir / f"{stem}.csv", index=False)
            # uniform-grid subset for the heatmap (fine B4 points excluded)
            g = p["grid_min"]
            uni = [r for r in records
                   if r["t_seen_tod"] % g == 0 and r["t_query_tod"] % g == 0]
            plot_surface(accuracy_surface(uni, g), day_transitions, g,
                         f"A(t_seen, t_query) — {label} — {qtype} (days {test_days})",
                         report_dir / f"{stem}.png")
            print(f"{stem}: n={len(df)} acc={df['correct'].mean():.3f} "
                  f"acc(displaced)={df[df.displaced == 1]['correct'].mean():.3f}")

        trained[label] = belief

    # ── B3 features parquet (tier-independent — taken from the first tier) ───
    feat_cols = ["obj", "class", "stratum", "test_day", "qtype", "t_seen",
                 "t_query", "displaced", "returned",
                 "n_transitions_in_interval", "time_since_last_transition_at_query"]
    feats = pd.DataFrame(all_recs[(tier_labels[0], "location_now")])[feat_cols]
    try:
        feats.to_parquet(report_dir / "probe_transition_features.parquet")
    except (ImportError, ValueError):
        feats.to_csv(report_dir / "probe_transition_features.csv", index=False)

    # ── F. gate tables ────────────────────────────────────────────────────────
    def _split(recs):
        return {"all": recs,
                "displaced": [r for r in recs if r["displaced"]],
                "returned": [r for r in recs if r["returned"]],
                "stable": [r for r in recs
                           if not r["displaced"] and not r["returned"]]}

    gate_rows = []       # (tier, qtype, stratum) rows
    metrics = {}         # (tier, qtype, stratum, split) -> ci dict
    for (label, qtype), recs in all_recs.items():
        for stratum in ["ALL"] + TERCILES:
            sub = recs if stratum == "ALL" else [r for r in recs
                                                 if r["stratum"] == stratum]
            row = {"tier": label, "qtype": qtype, "stratum": stratum}
            for k, rs in _split(sub).items():
                c = _ci(rs, n_boot, seed)
                metrics[(label, qtype, stratum, k)] = c
                row[k] = _fmt(c)
            gate_rows.append(row)

    # B3 transition partition (location_now)
    trans_rows = []
    for label in tier_labels:
        recs = all_recs[(label, "location_now")]
        bins = {
            "0 transitions in interval": [r for r in recs
                                          if r["n_transitions_in_interval"] == 0],
            ">=1 transition in interval": [r for r in recs
                                           if r["n_transitions_in_interval"] >= 1],
            "displaced, 1 transition": [r for r in recs if r["displaced"]
                                        and r["n_transitions_in_interval"] == 1],
            "displaced, >=2 transitions": [r for r in recs if r["displaced"]
                                           and r["n_transitions_in_interval"] >= 2],
            "displaced, last trans <60min before query":
                [r for r in recs if r["displaced"]
                 and 0 <= r["time_since_last_transition_at_query"] < 60],
            "displaced, last trans >=240min before query":
                [r for r in recs if r["displaced"]
                 and r["time_since_last_transition_at_query"] >= 240],
        }
        for name, rs in bins.items():
            trans_rows.append({"tier": label, "bin": name,
                               **{"v": _fmt(_ci(rs, n_boot, seed))}})

    # C2 elsewhere-mass check (b3 tiers, records whose true answer is in-house)
    c2 = {}
    for label in tier_labels:
        if not label.startswith("b3"):
            continue
        recs = all_recs[(label, "location_now")]
        pe_all = float(np.mean([r["p_elsewhere"] for r in recs]))
        pt_all = float(np.mean([r["p_true"] for r in recs]))
        c2[label] = {"mean_p_elsewhere": round(pe_all, 4),
                     "mean_p_true": round(pt_all, 4)}

    # C3: Δt-R² (skip b1 — Δt is not an input to a pure long-run frequency
    # model, the number was a category error) + nested time-of-day test
    c3 = {}
    for label in tier_labels:
        recs = all_recs[(label, "location_now")]
        entry = {}
        if label == "b1_longmem":
            entry["delta_t_R2"] = "n/a (Δt not a model input)"
        else:
            entry["delta_t_R2"] = round(delta_t_symmetry(recs), 4)
        if label != "b1_longmem":
            entry["nested_tod"] = nested_tod_test(recs)
        c3[label] = entry

    # D1: ECE + reliability diagrams (p_chosen)
    d1 = {}
    for (label, qtype), recs in all_recs.items():
        e = ece(recs, conf_key="p_chosen")
        d1[f"{label}__{qtype}"] = e["ece"]
        _reliability_plot(e["curve"], f"reliability — {label} — {qtype} "
                          f"(ECE={e['ece']:.3f})",
                          cal_dir / f"reliability__{label}__{qtype}.png")

    # D2: temperature fitted on ONE test day, evaluated on the others (hook
    # only — reported, never applied to the gate numbers)
    d2 = {}
    fit_day = p["temp_fit_day"]
    for label in tier_labels:
        recs = all_recs[(label, "location_now")]
        fit_recs = [r for r in recs if r["test_day"] == fit_day]
        eval_recs = [r for r in recs if r["test_day"] != fit_day]
        if not fit_recs or not eval_recs:
            continue
        T = fit_temperature(fit_recs, conf_key="p_true")
        pre = ece(eval_recs, conf_key="p_true")["ece"]
        post = ece(apply_temperature(eval_recs, T, conf_key="p_true"),
                   conf_key="p_true")["ece"]
        d2[label] = {"T": round(T, 3), "ece_p_true_pre": pre,
                     "ece_p_true_post": post}

    # E1: two-anchor diagnostic for b3 tiers (dynamic stratum, location_now)
    e1 = {}
    dyn_targets = [o for o in targets if stratum_of[o] == "dynamic"]
    for label in tier_labels:
        if not label.startswith("b3"):
            continue
        belief = trained[label]
        recs2 = []
        for day in test_days:
            for obj in dyn_targets:
                recs2.extend(probe_object(belief, world, obj, day, "location_now",
                                          grid_min=p["grid_min"], seed=seed,
                                          transition_tods=trans_tods[(obj, day)],
                                          second_anchor=True))
        base = [r for r in all_recs[(label, "location_now")]
                if r["stratum"] == "dynamic" and r["displaced"]]
        two = [r for r in recs2 if r["displaced"]]
        e1[label] = {"displaced_acc_1anchor": _fmt(_ci(base, n_boot, seed)),
                     "displaced_acc_2anchor": _fmt(_ci(two, n_boot, seed))}

    # ── write gate report + SUMMARY ───────────────────────────────────────────
    def _tbl(rows, cols):
        out = ["| " + " | ".join(cols) + " |",
               "|" + "---|" * len(cols)]
        for r in rows:
            out.append("| " + " | ".join(str(r[c]) for c in cols) + " |")
        return out

    lines = ["# Stage 1b re-gate", "",
             f"targets: {len(targets)} objects "
             f"({', '.join(f'{t}={sum(1 for o in targets if stratum_of[o]==t)}' for t in TERCILES)}), "
             f"test days {test_days}, grid {p['grid_min']}min + transition-aware fine points, "
             f"cluster-bootstrap 95% CIs (n_boot={n_boot})", "",
             "## Per-stratum accuracy (B1/B2/B5) — headline = `displaced`", "",
             *_tbl(gate_rows, ["tier", "qtype", "stratum", "all", "displaced",
                               "returned", "stable"]),
             "", "## Transition-conditioned partition (B3, location_now)", "",
             *_tbl(trans_rows, ["tier", "bin", "v"]),
             "", "## C2 (b3 mass accounting, post-fix)", "",
             "```json", json.dumps(c2, indent=1), "```",
             "", "## C3 (Δt hygiene + nested time-of-day test)", "",
             "```json", json.dumps(c3, indent=1, default=str), "```",
             "", "## D1 ECE (p_chosen)", "",
             "```json", json.dumps(d1, indent=1), "```",
             "", "## D2 temperature hook (fit day "
             f"{fit_day}, evaluated on the others; NOT applied to gate numbers)", "",
             "```json", json.dumps(d2, indent=1), "```",
             "", "## E1 two-anchor diagnostic (dynamic stratum, displaced)", "",
             "```json", json.dumps(e1, indent=1), "```",
             "", "## C1 room_now distinctness", "",
             "```json", json.dumps(c1, indent=1), "```"]
    (report_dir / "stage1b_gate.md").write_text("\n".join(lines) + "\n")

    # SUMMARY.md — the five go/no-go questions
    b3s = [t for t in tier_labels if t.startswith("b3")]
    best_b3 = max(b3s, key=lambda t: metrics[(t, "location_now", "ALL", "displaced")]["acc"])
    m3 = metrics[(best_b3, "location_now", "ALL", "displaced")]
    m2 = metrics[("b2_classdecay", "location_now", "ALL", "displaced")]
    q1_yes = m3["acc"] > m2["acc"]
    q1_clear = m3["lo"] > m2["hi"]
    leads = {t: metrics[(best_b3, 'location_now', t, 'displaced')]["acc"]
             - metrics[("b2_classdecay", 'location_now', t, 'displaced')]["acc"]
             for t in TERCILES
             if metrics[(best_b3, 'location_now', t, 'displaced')]["n"]
             and metrics[("b2_classdecay", 'location_now', t, 'displaced')]["n"]}
    # Q2 predictability half-split among displaced records
    med_pred = float(np.median([pred_of[o] for o in targets]))
    q2_pred = {}
    for half, cond in [("low_pred", lambda o: pred_of[o] <= med_pred),
                       ("high_pred", lambda o: pred_of[o] > med_pred)]:
        l3 = _ci([r for r in all_recs[(best_b3, "location_now")]
                  if r["displaced"] and cond(r["obj"])], n_boot, seed)
        l2 = _ci([r for r in all_recs[("b2_classdecay", "location_now")]
                  if r["displaced"] and cond(r["obj"])], n_boot, seed)
        q2_pred[half] = round(l3["acc"] - l2["acc"], 4) if l3["n"] and l2["n"] else None
    r3 = metrics[(best_b3, "room_now", "ALL", "displaced")]
    verdict = "PROCEED to Stage 2" if q1_yes else "DO NOT proceed to Stage 2"

    s = [
        "# Stage 1b SUMMARY — go/no-go for Stage 2", "",
        f"Dataset: {vol_sum['n_static']} static / {vol_sum['n_occasional']} occasional / "
        f"{vol_sum['n_dynamic']} dynamic objects; mean {vol_sum['mean']:.2f} moves/day "
        f"(median {vol_sum['median']:.2f}); median predictability of non-static objects "
        f"{np.median(nonstatic_pred):.3f}.",
        "",
        "**1. On displaced objects, does b3 beat b2 — overall and in the "
        "transition-inside bin?**",
        f"{'YES' if q1_yes else 'NO'}{' (CI-separated)' if q1_clear else ' (CIs overlap)'}: "
        f"{best_b3} {_fmt(m3)} vs b2_classdecay {_fmt(m2)} on displaced location_now. "
        "Note: every displaced probe has >=1 transition inside its interval by "
        "construction, so 'displaced' IS the transition-inside bin; the 0-transition "
        "control and the returned split are in the gate table (b0-favoring cells, "
        "as expected).",
        "",
        "**2. Does b3's lead over b2 grow with predictability and volatility stratum?**",
        f"Lead by stratum (displaced acc, {best_b3} − b2): "
        + ", ".join(f"{k}={v:+.3f}" for k, v in leads.items()) + ". "
        f"Lead by predictability half-split (median {med_pred:.3f}): "
        + ", ".join(f"{k}={v:+.3f}" if v is not None else f"{k}=n/a"
                    for k, v in q2_pred.items()) + ".",
        "",
        "**3. Is the moved-room win still significant with CIs attached?**",
        f"{best_b3} displaced room_now: {_fmt(r3)} vs chance 0.25 — "
        f"{'significant (CI excludes 0.25)' if r3['lo'] > 0.25 else 'NOT separated from chance'}.",
        "",
        "**4. After C2/D2, is b3 calibrated enough for Stage-2 stopping?**",
        f"C2 (post occupancy-pinning fix): {json.dumps(c2)}. "
        f"D1 ECE (p_chosen, location_now): "
        + ", ".join(f"{t}={d1[f'{t}__location_now']}" for t in b3s) + ". "
        f"D2 temperature hook: {json.dumps(d2)} — held out, not baked in.",
        "",
        "**5. Did any integrity check invalidate a Stage-1 number?**",
        f"C1: {c1['n_with_duplicate_rooms']}/{c1['n_room_now_checked']} room_now questions "
        "had duplicate options (validator hard-asserts distinctness). "
        f"A3: class explains eta^2={coupling['eta2_class_on_volatility']} of volatility "
        f"variance; flagged classes: {coupling['flagged_classes']}. "
        "C3: b1's delta_t_R2 dropped as a category error (see gate report). "
        "Stage 1's headline acc(moved) mixed returned into moved; the B2 split "
        "supersedes it.",
        "",
        "**B6 note:** the generator has no routine-tightness knob; the predictability "
        "sweep (near-metronomic vs stochastic) requires a generator change and was NOT "
        "run — single operating point only.",
        "",
        f"## Verdict: {verdict}",
        f"(rule: proceed only if (1) is yes on displaced objects; "
        f"{'CI-separated' if q1_clear else 'point estimate only — CIs overlap'})",
    ]
    (report_dir / "SUMMARY.md").write_text("\n".join(s) + "\n")
    print(f"\nreport -> {report_dir / 'stage1b_gate.md'}")
    print(f"summary -> {report_dir / 'SUMMARY.md'}  |  {verdict}")


if __name__ == "__main__":
    main()
