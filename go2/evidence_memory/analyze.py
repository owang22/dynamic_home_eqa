"""Extra cuts of the scores: look-back split by yes/no, the questions the oracle gets right (answer readable
from the right picture: memory vs perception), happened strict, who, and the left-behind cases.

    python analyze.py  -> prints, and writes out/analysis.json
"""
from __future__ import annotations

import json
import math
import statistics as st

import common as C

RUNS = [("1.0", ""), ("0.4", ""), ("1.0", "_opus"), ("1.0", "_opus_alldays"), ("0.4", "_opus_n61")]


def load(h, tag):
    f = C.OUT / f"scores_{h}{tag}.json"
    return json.loads(f.read_text()) if f.exists() else None


def main():
    qs = {q["id"]: q for q in json.loads((C.OUT / "questions.json").read_text())}
    out = {}
    oracle = {}
    for h in ("1.0", "0.4"):
        s = load(h, "")
        if s and "O" in s["_rows"]:
            oracle[h] = {r["id"]: r["right"] for r in s["_rows"]["O"]}
    for h, tag in RUNS:
        s = load(h, tag)
        if not s:
            continue
        name = f"{h}{tag}"
        out[name] = {}
        orc = oracle.get(h, oracle.get("1.0"))
        print(f"\n== {name}   (oracle-right subset uses the Qwen oracle at {h if h in oracle else '1.0'} m)")
        print(f"{'arm':4s} {'look yes':>9s} {'look no':>8s} {'when':>6s} {'happ.':>6s} {'specific':>8s} {'who':>5s} "
              f"{'unseen':>7s} | {'oracle-right: n':>15s} {'right':>6s}")
        for arm, rows in s["_rows"].items():
            r = {x["id"]: x for x in rows}
            def share(sel):
                xs = [float(r[i]["right"]) for i in r if sel(qs[i])]
                return st.mean(xs) if xs else float("nan")
            ly = share(lambda q: q["kind"] == "lookback" and q["truth"]["answer"] == "yes")
            ln = share(lambda q: q["kind"] == "lookback" and q["truth"]["answer"] == "no")
            wh = share(lambda q: q["kind"] == "when")
            hp = share(lambda q: q["kind"] == "happened")
            un = share(lambda q: q["kind"] == "unseen")
            hs = [float(r[i].get("doing") == "right") for i in r if qs[i]["kind"] == "happened"]
            who = [float(r[i].get("who_right")) for i in r if qs[i]["kind"] == "happened"]
            sub = [i for i in r if qs[i]["kind"] not in ("left", "unseen") and orc.get(i)]
            sr = st.mean(float(r[i]["right"]) for i in sub) if sub else float("nan")
            left = {i: r[i]["right"] for i in r if qs[i]["kind"] == "left"}
            out[name][arm] = {"lookback_yes": ly, "lookback_no": ln, "when": wh, "happened": hp,
                              "happened_specific": st.mean(hs) if hs else None, "who": st.mean(who) if who else None,
                              "unseen": un, "oracle_right_n": len(sub), "oracle_right_share": sr, "left": left}
            print(f"{arm:4s} {ly:9.2f} {ln:8.2f} {wh:6.2f} {hp:6.2f} {(st.mean(hs) if hs else float('nan')):7.2f} "
                  f"{(st.mean(who) if who else float('nan')):5.2f} {un:7.2f} | {len(sub):15d} {sr:6.2f}")
    C.dump(out, C.OUT / "analysis.json")


if __name__ == "__main__":
    main()
