"""Router evaluation from the recorded runs (no model calls): quality vs escalation rate vs time, per policy.

    python3 analyze.py [--small 8b_v2] [--mid 27b_v1]     -> results/router_eval.json + printed tables

Scores: judge verdict agree = 1, partial = 0.5, disagree = 0 (27B judge; generated questions against the answer key
checked by eye, logged turns against Opus's logged answer). Opus on logged turns is the reference (score 1 by
construction; its re-runs score 0.70 against itself, the practical ceiling there).
A turn sent to the big model takes the small model's time up to the first escalation signal plus the big model's
time (cold start: the escalated turn starts over). Random escalation at the same rate is the expected value.
"""
from __future__ import annotations

import argparse
import json
import random
import statistics
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
from router import classify, replay_signals  # noqa: E402

RES = HERE / "results"
V = {"agree": 1.0, "partial": 0.5, "disagree": 0.0}
P_IDS = list(json.loads((HERE / "data" / "places_snapshot.json").read_text()))


def load(name):
    return {r["case"]: r for r in json.load(open(RES / f"{name}.json"))}


def table(small, mid):
    gen = {c["id"]: c for c in json.load(open(HERE / "cases_generated.json"))}
    log = {c["id"]: c for c in json.load(open(HERE / "cases_logged.json")) if c["kind"] == "memory"}
    rows = []
    for which, cases, tr_s, tr_m, j_s, j_m in (
            ("generated", gen, load(f"generated_{small}"), load(f"generated_{mid}"),
             load(f"judge_generated_{small}"), load(f"judge_generated_{mid}")),
            ("logged", log, load(f"memory_{small}"), load(f"memory_{mid}"),
             load(f"judge_memory_{small}"), load(f"judge_memory_{mid}"))):
        if which == "generated":
            ob, oj = load("opus_generated"), load("judge_generated_opus")
        for cid, c in cases.items():
            route = classify(c["text"], P_IDS)
            r = {"case": cid, "set": which, "kind": c.get("kind", "memory"), "route": route.name, "route_why": route.why,
                 "s_small": V[j_s[cid]["verdict"]], "s_mid": V[j_m[cid]["verdict"]],
                 "t_small": tr_s[cid]["secs"], "t_mid": tr_m[cid]["secs"]}
            if which == "generated":
                r["s_big"], r["t_big"] = V[oj[cid]["verdict"]], ob[cid]["secs"]
                r["big_calls"] = len(ob[cid]["calls"])
            else:
                r["s_big"], r["t_big"], r["big_calls"] = 1.0, c["opus_secs"], len(c["opus_calls"])
            for tier, tr in (("small", tr_s[cid]), ("mid", tr_m[cid])):
                for rule in ("strict", "neg_ok"):
                    sig = replay_signals(tr, route, max_steps=4, answer_rule=rule)
                    r[f"sig_{tier}_{rule}"] = [s["why"] for s in sig]
                    r[f"tsig_{tier}_{rule}"] = sig[0]["t"] if sig and sig[0].get("t") is not None else tr["secs"]
            for tier, j in (("small", j_s[cid]), ("mid", j_m[cid])):
                r[f"seen_{tier}"] = j.get("candidate_says_seen")
            vf = RES / f"verify_{small}.json"
            if vf.exists():
                v = {x["case"]: x for x in json.load(open(vf))}[cid]
                # no pictures to look at -> the verifier cannot judge (it invents scenes when given none)
                r["verify"] = "cannot tell" if v["n_pics"] == 0 else v["verdict"]
                r["t_verify"] = v["secs"] if v["n_pics"] else 0.0
            rows.append(r)
    return rows


def policy(rows, name, fn):
    """fn(row) -> (score, secs, used_big)"""
    out = [fn(r) for r in rows]
    n = len(rows)
    return {"policy": name, "n": n, "quality": round(sum(o[0] for o in out) / n, 3),
            "big_rate": round(sum(o[2] for o in out) / n, 3),
            "mean_s": round(sum(o[1] for o in out) / n, 1), "median_s": round(statistics.median(o[1] for o in out), 1)}


def policies(rows, rule="strict"):
    P = []
    P.append(policy(rows, "always small (8B)", lambda r: (r["s_small"], r["t_small"], 0)))
    P.append(policy(rows, "always 27B", lambda r: (r["s_mid"], r["t_mid"], 0)))
    P.append(policy(rows, "always big (Opus)", lambda r: (r["s_big"], r["t_big"], 1)))
    P.append(policy(rows, "question type only -> Opus", lambda r: (r["s_big"], r["t_big"], 1) if r["route"] == "big"
                    else (r["s_small"], r["t_small"], 0)))

    def esc(r, target="big", rule=rule):
        if r["route"] == "big":
            return (r[f"s_{target}"], r[f"t_{target}"], target == "big")
        if r[f"sig_small_{rule}"]:
            return (r[f"s_{target}"], r[f"tsig_small_{rule}"] + r[f"t_{target}"], target == "big")
        return (r["s_small"], r["t_small"], 0)
    P.append(policy(rows, f"rules + signals ({rule}) -> Opus", esc))
    P.append(policy(rows, f"rules + signals ({rule}) -> 27B (no Opus)", lambda r: esc(r, "mid")))

    if "verify" in rows[0]:
        def ver(r, on=("not supported",)):
            if r["route"] == "big":
                return (r["s_big"], r["t_big"], 1)
            if r["sig_small_neg_ok"]:
                return (r["s_big"], r["tsig_small_neg_ok"] + r["t_big"], 1)
            if r["verify"] in on:
                return (r["s_big"], r["t_small"] + r["t_verify"] + r["t_big"], 1)
            return (r["s_small"], r["t_small"] + r["t_verify"], 0)
        P.append(policy(rows, "rules + signals(neg_ok) + 27B verify -> Opus", ver))
        P.append(policy(rows, "  same, also escalate 'cannot tell'", lambda r: ver(r, ("not supported", "cannot tell"))))

    def three(r):   # small -> 27B on signal/type, 27B -> Opus on the 27B's own signals
        if r["route"] != "big" and not r[f"sig_small_{rule}"]:
            return (r["s_small"], r["t_small"], 0)
        t0 = r[f"tsig_small_{rule}"] if r["route"] != "big" else 0.0
        if r[f"sig_mid_{rule}"]:
            return (r["s_big"], t0 + r[f"tsig_mid_{rule}"] + r["t_big"], 1)
        return (r["s_mid"], t0 + r["t_mid"], 0)
    P.append(policy(rows, f"3-tier 8B -> 27B -> Opus ({rule})", three))
    # random / oracle escalation at the rate of each Opus-using router policy
    for base in [p for p in P if "Opus" in p["policy"] and p["policy"] not in ("always big (Opus)",) and p["big_rate"] > 0]:
        k_ = round(base["big_rate"] * len(rows))
        exp = sum(r["s_small"] for r in rows) / len(rows) + k_ / len(rows) * (
            sum(r["s_big"] - r["s_small"] for r in rows) / len(rows))
        base["random_same_rate"] = round(exp, 3)
    # random escalation at the rate of "rules + signals -> Opus": expected value over 2000 draws
    rate = next(p for p in P if p["policy"].startswith(f"rules + signals ({rule})") and "Opus" in p["policy"])["big_rate"]
    k = round(rate * len(rows))
    rnd = random.Random(0)
    qs = []
    for _ in range(2000):
        pick = set(rnd.sample(range(len(rows)), k))
        qs.append(sum(r["s_big"] if i in pick else r["s_small"] for i, r in enumerate(rows)) / len(rows))
    P.append({"policy": f"random escalation at {rate:.2f}", "n": len(rows), "quality": round(sum(qs) / len(qs), 3),
              "big_rate": rate, "mean_s": None, "median_s": None})
    # oracle at the same rate: escalate where big beats small the most
    gain = sorted(range(len(rows)), key=lambda i: rows[i]["s_big"] - rows[i]["s_small"], reverse=True)[:k]
    P.append({"policy": f"oracle escalation at {rate:.2f}", "n": len(rows), "big_rate": rate, "mean_s": None, "median_s": None,
              "quality": round(sum(r["s_big"] if i in gain else r["s_small"] for i, r in enumerate(rows)) / len(rows), 3)})
    return P


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--small", default="8b_v2")
    ap.add_argument("--mid", default="27b_v1")
    a = ap.parse_args()
    rows = table(a.small, a.mid)
    out = {"small": a.small, "mid": a.mid, "rows": rows, "tables": {}}
    for subset in ("generated", "logged", "all"):
        rs = [r for r in rows if subset == "all" or r["set"] == subset]
        for rule in ("strict", "neg_ok"):
            P = policies(rs, rule)
            out["tables"][f"{subset}_{rule}"] = P
            print(f"\n== {subset} ({len(rs)} questions), answer rule {rule}")
            print(f"{'policy':48s} {'quality':>7s} {'Opus rate':>9s} {'mean s':>7s} {'median s':>8s} {'random@rate':>11s}")
            for p in P:
                print(f"{p['policy']:48s} {p['quality']:7.3f} {p['big_rate']:9.2f} {str(p['mean_s']):>7s} {str(p['median_s']):>8s}"
                      f" {str(p.get('random_same_rate', '')):>11s}")
    # signal precision: how often a fired signal marks a turn the small model got wrong (score < 1)
    for rule in ("strict", "neg_ok"):
        smallq = [r for r in rows if r["route"] != "big"]
        fired = [r for r in smallq if r[f"sig_small_{rule}"]]
        bad = [r for r in smallq if r["s_small"] < 1]
        print(f"\nsignals ({rule}) on small-routed turns: fired {len(fired)}/{len(smallq)}; small wrong-or-partial "
              f"{len(bad)}; fired & wrong {sum(r in bad for r in fired)}; missed wrong {sum(r not in fired for r in bad)}")
        out[f"signal_stats_{rule}"] = {"small_routed": len(smallq), "fired": len(fired), "small_not_full": len(bad),
                                       "fired_and_not_full": sum(r in bad for r in fired),
                                       "not_full_missed": sum(r not in fired for r in bad)}
    (RES / "router_eval.json").write_text(json.dumps(out, indent=1))
    print("->", RES / "router_eval.json")


if __name__ == "__main__":
    main()
