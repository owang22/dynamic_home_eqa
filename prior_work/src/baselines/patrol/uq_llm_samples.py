"""Sampling-based uncertainty and conformal sets for an LLM memory — no logits, no multiple choice.

Route chosen 22 Sept after the multiple-choice channel failed twice (catch-all bucket, then JSON fallback) and
after establishing that the server caps ``top_logprobs`` at 20 while these houses have 32-46 receptacles, which
makes any letter-based distribution structurally unable to score most of the label space.

This channel uses only what the model emits. For each question we draw ``--samples`` answers at temperature 0.7 in
a single request and read the empirical distribution over spots:

* **agreement**  share of samples equal to the greedy answer (self-consistency, Wang et al. 2022)
* **entropy**    over the sampled answers. Spot ids are exact-match, so semantic entropy (Kuhn et al. 2023;
                 Farquhar et al. 2024) reduces to plain answer entropy here - no clustering needed.
* **conformal**  the empirical frequency IS the nonconformity score, which is the published no-logit-access
                 construction (Su et al. 2024, "API Is Enough"). Sets are built two ways and both thresholds are
                 adapted online with the same DecayingStepConformal the classical agents use, so the curves are
                 comparable with the counters already on the page:
                   LAC/THR  s(y) = 1 - p_hat(y)
                   APS      s(y) = cumulative mass of everything ranked at or above y (Romano et al. 2020)

k matters: at k=5 the agreement statistic takes six values and sits saturated at 1.0 on ~two thirds of questions,
and a conformal set can never name more than 5 places. k=20 is the point of this run.

    python3 -m baselines.patrol.uq_llm_samples --bank BANK --out DIR --memory longcontext --days 31 --samples 20
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import pathlib
import random
import sys
import urllib.request
from collections import Counter, defaultdict
from typing import Dict, List

from baselines.bank import JsonlBank
from baselines.patrol.bocpd import NEGATIVE, DiscountedMostFrequent
from baselines.patrol.llm import CONF_SCHEMA, ENDPOINT, MODEL, Memory, parse_conf, question_messages
from baselines.patrol.uq_agents import DecayingStepConformal
from baselines.types import ON_PERSON, OUT_OF_HOUSE, SenseResult


class Client:
    def __init__(self, cache_dir: pathlib.Path, endpoint: str = ENDPOINT, model: str = MODEL):
        self.cache_dir = cache_dir
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.endpoint, self.model = endpoint, model
        self.stats = {"calls": 0, "cached": 0}

    def chat(self, messages, max_tokens, temperature=0.0, n=1, schema=None):
        body = {"model": self.model, "messages": messages, "max_tokens": max_tokens, "temperature": temperature,
                "n": n, "seed": 0, "chat_template_kwargs": {"enable_thinking": False}}
        if schema is not None:
            body["response_format"] = {"type": "json_schema", "json_schema": {"name": "answer", "schema": schema}}
        key = hashlib.sha256(json.dumps(body, sort_keys=True).encode()).hexdigest()
        path = self.cache_dir / f"{key}.json"
        if path.exists():
            self.stats["cached"] += 1
            return json.loads(path.read_text())
        req = urllib.request.Request(self.endpoint.rstrip("/") + "/v1/chat/completions",
                                     data=json.dumps(body).encode(), headers={"Content-Type": "application/json"})
        d = json.loads(urllib.request.urlopen(req, timeout=900).read())
        path.write_text(json.dumps(d))
        self.stats["calls"] += 1
        return d


def aps_scores(dist: Dict[str, float]) -> Dict[str, float]:
    """Romano et al. 2020: the score of y is the cumulative mass of everything ranked at or above it, y included."""
    out, run = {}, 0.0
    for s, p in sorted(dist.items(), key=lambda kv: -kv[1]):
        run += p
        out[s] = run
    return out


def aps_set(dist: Dict[str, float], q: float) -> set:
    """Add classes in descending probability until the cumulative mass reaches q, ALWAYS keeping the top one.

    Two bugs found on 22 Sept by watching the live rows, which together emptied 26% of the sets:
    (1) a bare ``score <= q`` test drops the top class whenever q < p(top), and an APS set that cannot contain the
        model's own best guess is not an APS set;
    (2) the boundary is float-fragile - the cumulative sum of a single-class distribution lands on 1.0000000002,
        which is not <= 1.0, so a completely confident answer produced an EMPTY set.
    The prefix rule below is the standard construction and is immune to both.
    """
    out, run = set(), 0.0
    for y, p in sorted(dist.items(), key=lambda kv: -kv[1]):
        out.add(y)
        run += p
        if run >= q - 1e-9:
            break
    return out


class Assay:
    """A suspiciously constant metric is a bug until proven otherwise. Fail loudly, do not complete quietly."""

    def __init__(self):
        self.rows: List[dict] = []

    def add(self, r):
        self.rows.append(r)

    def problems(self) -> List[str]:
        r = self.rows
        if len(r) < 15:
            return []
        bad = []
        if len({json.dumps(x["dist"], sort_keys=True) for x in r}) == 1:
            bad.append(f"IDENTICAL sampled distribution on all {len(r)} questions")
        gs = [x["greedy"] for x in r]
        share = max(gs.count(g) for g in set(gs)) / len(gs)
        # compare against how concentrated the TRUTH actually is: some objects really do sit in one place all day,
        # so an absolute threshold cries wolf (workshop session's assay note, 22 Sept).
        ts = [x["truth"] for x in r]
        tshare = max(ts.count(t) for t in set(ts)) / len(ts)
        if tshare > 0 and share / tshare > 1.6 and share > 0.5:
            bad.append(f"one answer given on {100*share:.0f}% of questions vs truth concentration "
                       f"{100*tshare:.0f}% (ratio {share/tshare:.1f})")
        if len({x["n_distinct"] for x in r}) == 1 and r[0]["n_distinct"] == 1:
            bad.append("every question produced exactly one distinct sampled answer - sampling may not be random")
        for k in ("lac_size", "aps_size"):
            v = {x[k] for x in r}
            if len(v) == 1:
                bad.append(f"{k} pinned at {v.pop()} on every question")
        u = sum(x["agreement"] >= 0.999 for x in r) / len(r)
        if u > 0.95:
            bad.append(f"{100*u:.0f}% of questions unanimous - k too small to discriminate")
        return bad

    def summary(self) -> str:
        r = self.rows
        if not r:
            return "(none)"
        n = len(r)
        acc = 100 * sum(x["correct"] for x in r) / n
        return (f"  n={n}  accuracy {acc:.0f}%  mean agreement {sum(x['agreement'] for x in r)/n:.2f}  "
                f"unanimous {100*sum(x['agreement']>=0.999 for x in r)/n:.0f}%\n"
                f"  distinct sampled answers per question: mean {sum(x['n_distinct'] for x in r)/n:.2f} "
                f"(max {max(x['n_distinct'] for x in r)})\n"
                f"  LAC set  mean {sum(x['lac_size'] for x in r)/n:.2f} range {min(x['lac_size'] for x in r)}-"
                f"{max(x['lac_size'] for x in r)}   coverage {100*sum(x['lac_covered'] for x in r)/n:.0f}%\n"
                f"  APS set  mean {sum(x['aps_size'] for x in r)/n:.2f} range {min(x['aps_size'] for x in r)}-"
                f"{max(x['aps_size'] for x in r)}   coverage {100*sum(x['aps_covered'] for x in r)/n:.0f}%")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--bank", type=pathlib.Path, required=True)
    ap.add_argument("--out", type=pathlib.Path, required=True)
    ap.add_argument("--memory", default="longcontext")
    ap.add_argument("--days", type=int, default=31)
    ap.add_argument("--samples", type=int, default=20)
    ap.add_argument("--alpha", type=float, default=0.1)
    ap.add_argument("--pilot", type=int, default=0)
    ap.add_argument("--endpoint", default=ENDPOINT)
    a = ap.parse_args(argv)
    a.out.mkdir(parents=True, exist_ok=True)

    header = json.loads(a.bank.read_text().splitlines()[0])
    episode = next(iter(JsonlBank(a.bank).episodes()))
    day_names = {int(k): v for k, v in header["day_names"].items()}
    cards = header["protocol"]["residents"]
    names = {c["resident_id"]: c["name"] for c in cards}
    rooms: Dict[str, List[str]] = defaultdict(list)
    for rec, room in sorted(episode.receptacle_rooms.items()):
        if rec not in (ON_PERSON, OUT_OF_HOUSE):
            rooms[room].append(rec)
    rooms = {r: sorted(v) for r, v in rooms.items()}
    rec_room = {rec: room for room, recs in rooms.items() for rec in recs}
    allowed = {r for r in episode.receptacle_ids if r not in (ON_PERSON, OUT_OF_HOUSE)}
    memory = Memory(rooms, rec_room, names)
    counter = DiscountedMostFrequent(random.Random(0), half_life_h=24.0, **NEGATIVE["off"])
    counter.reset(episode.agent_view())
    for obs in episode.initial_observations:
        counter.update(obs)
    tour_t = int(header["tour_t"])
    evidence = list(episode.evidence_stream())
    cursor = 0
    memory.update_group(tour_t, list(episode.initial_observations) + [e for e in evidence if e.t == tour_t], day_names)
    while cursor < len(evidence) and evidence[cursor].t <= tour_t:
        counter.update(evidence[cursor])
        cursor += 1

    client = Client(a.out / "cache", a.endpoint)
    lac = DecayingStepConformal(alpha=a.alpha)
    aps = DecayingStepConformal(alpha=a.alpha)
    assay = Assay()
    out_path = a.out / f"{header['household_id']}.jsonl"
    done = {json.loads(l)["question_id"] for l in out_path.open()} if out_path.exists() else set()
    fh = out_path.open("a")
    print(f"{header['household_id']}: {len(allowed)} receptacles, k={a.samples}, alpha={a.alpha}", flush=True)

    n = 0
    for day_questions in episode.questions_by_day:
        for q in day_questions:
            if q.day_index > a.days:
                break
            while cursor < len(evidence) and evidence[cursor].t <= q.t_query:
                t = evidence[cursor].t
                grp = []
                while cursor < len(evidence) and evidence[cursor].t == t:
                    grp.append(evidence[cursor])
                    cursor += 1
                memory.update_group(t, grp, day_names)
                for e in grp:
                    if isinstance(e, SenseResult):
                        for o in e.contents:
                            counter.ensure_object(o, e.object_classes.get(o, ""))
                    counter.update(e)
            if q.question_id in done:
                continue
            counter.ensure_object(q.object_id, q.object_class)
            msgs = question_messages(memory, a.memory, q, day_names, cards, rooms, int(header["patrol_hours"]),
                                     False, [], None, None, "conf", header.get("patrol_times") or None,
                                     header.get("protocol", {}).get("question_moments", ""),
                                     header.get("protocol", {}).get("feedback_delay_min"))
            truth = episode.true_location(q.object_id, q.t_query)
            d = client.chat(msgs, 260, 0.0, 1, CONF_SCHEMA)
            loc, conf, _, _ = parse_conf(d["choices"][0]["message"]["content"], allowed)
            greedy = loc or sorted(allowed)[0]

            d2 = client.chat(msgs, 260, 0.7, a.samples, CONF_SCHEMA)
            sampled = []
            for ch in d2["choices"]:
                l2, _, _, _ = parse_conf(ch["message"]["content"], allowed)
                sampled.append(l2 or "?")
            cnt = Counter(sampled)
            k = len(sampled)
            dist = {s: c / k for s, c in cnt.items()}
            agreement = dist.get(greedy, 0.0)
            entropy = -sum(p * math.log(p) for p in dist.values() if p > 0)
            apsc = aps_scores(dist)

            lac_set = {y for y, p in dist.items() if (1.0 - p) <= lac.q}
            aps_sel = aps_set(dist, aps.q)
            lac.update(truth not in lac_set, 1.0 - dist.get(truth, 0.0))
            aps.update(truth not in aps_sel, apsc.get(truth, 1.0))

            rec = {"household": header["household_id"], "question_id": q.question_id, "day_index": q.day_index,
                   "object_id": q.object_id, "t_query": q.t_query, "truth": truth, "greedy": greedy,
                   "correct": greedy == truth, "verbalized": round(conf or 0.0, 4),
                   "agreement": round(agreement, 4), "entropy": round(entropy, 4), "k": k,
                   "n_distinct": len(cnt), "dist": {s: round(p, 4) for s, p in sorted(dist.items(), key=lambda kv: -kv[1])},
                   "p_truth": round(dist.get(truth, 0.0), 4),
                   "lac_size": len(lac_set), "lac_covered": truth in lac_set, "lac_q": round(lac.q, 4),
                   "aps_size": len(aps_sel), "aps_covered": truth in aps_sel, "aps_q": round(aps.q, 4)}
            fh.write(json.dumps(rec, sort_keys=True) + "\n")
            fh.flush()
            assay.add(rec)
            n += 1
            if n <= 5 or n % 40 == 0:
                print(f"  d{q.day_index:02d} {q.object_id:<16s} truth={truth:<20s} greedy={greedy:<20s} "
                      f"agree={agreement:.2f} distinct={len(cnt):2d} lac={len(lac_set)} aps={len(aps_sel)}", flush=True)
            if a.pilot and n >= a.pilot:
                break
        if a.pilot and n >= a.pilot:
            break

    print("\n--- assay ---\n" + assay.summary(), flush=True)
    bad = assay.problems()
    if bad:
        print("\n*** DEGENERATE — NOT A RESULT ***")
        for b in bad:
            print("   -", b)
        return 2
    print("\nassay clean.", json.dumps(client.stats), flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
