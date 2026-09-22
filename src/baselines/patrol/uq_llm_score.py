"""Conformal prediction over the REAL label space: score every receptacle, don't make the model pick a letter.

Why this exists (uq/problems_found.md, 22 Sept; uq/regime/EXPECTATIONS.md E37). The multiple-choice channel offered
the 9 likeliest spots plus "J) somewhere else" and the model took the catch-all on 1480 of 1480 questions, so
``conf_token`` was simply P(catch-all). Widening the list to every spot made the model answer in the JSON format the
surrounding prompt asks for instead ('{"' wins the first token at p=0.98 on two households of three). Both are
instrumentation faults. Worse, the server caps ``top_logprobs`` at 20 while these houses have 32-46 receptacles, so a
letter-based distribution can never assign a score to 26+ of the labels: if the truth falls outside the visible 20 it
is uncoverable BY CONSTRUCTION, which on a plot is indistinguishable from "conformal failed to widen".

Conformal needs a nonconformity score for EVERY candidate label. So we compute one: each receptacle name is scored as
a continuation of the same prompt (``prompt_logprobs`` on a prefilled assistant turn, so the long prefix is a cache
hit and only the few candidate tokens are new), and the K sequence probabilities are renormalised over the candidate
set into a proper categorical distribution. From that we build sets two ways:

* **LAC / THR**  s(y) = 1 - p(y).  Smallest sets, weakest conditional coverage.
* **APS** (Romano, Sesia, Candes 2020)  s(y) = cumulative mass of labels ranked above y, plus p(y).  Trades size
  for ADAPTIVITY - set size is supposed to grow with difficulty, which is the property under test here, so
  reporting only LAC would under-test the claim.

Thresholds are adapted online exactly as the classical agents do (DecayingStepConformal), so the comparison with the
counters on the page is like-for-like.

    python3 -m baselines.patrol.uq_llm_score --bank BANK --out DIR --memory longcontext --days 31 [--pilot 2]
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
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
from typing import Dict, List, Sequence

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

    def _post(self, body: dict) -> dict:
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

    def chat(self, messages, max_tokens, temperature=0.0, n=1, schema=None):
        body = {"model": self.model, "messages": messages, "max_tokens": max_tokens, "temperature": temperature,
                "n": n, "seed": 0, "chat_template_kwargs": {"enable_thinking": False}}
        if schema is not None:
            body["response_format"] = {"type": "json_schema", "json_schema": {"name": "answer", "schema": schema}}
        return self._post(body)

    def logprob_of(self, messages, candidate: str) -> float:
        """log P(candidate | prompt), summed over the candidate's own tokens. The prefix is identical across
        candidates so it is a prefix-cache hit on the server; only the few candidate tokens are new work."""
        body = {"model": self.model, "messages": list(messages) + [{"role": "assistant", "content": candidate}],
                "max_tokens": 1, "temperature": 0.0, "seed": 0,
                "chat_template_kwargs": {"enable_thinking": False},
                "continue_final_message": True, "add_generation_prompt": False, "prompt_logprobs": 0}
        d = self._post(body)
        pl = d.get("prompt_logprobs") or []
        toks = [e for e in pl if e]
        # the candidate's tokens are the tail of the prompt; count them by tokenising nothing - instead walk back
        # while the decoded tokens still reconstruct the candidate from the right.
        acc, total, used = "", 0.0, 0
        for e in reversed(toks):
            info = next(iter(e.values()))
            dec = info.get("decoded_token") or ""
            if dec.strip() in ("</think>", "") and not acc:
                continue
            acc = dec + acc
            total += float(info.get("logprob") or 0.0)
            used += 1
            if acc.strip().endswith(candidate) and candidate in acc:
                return total
            if used > 40:
                break
        return total if used else -60.0


def distribution(client: Client, msgs, spots: Sequence[str], workers: int = 24) -> Dict[str, float]:
    """-> renormalised categorical distribution over the candidate spots."""
    with ThreadPoolExecutor(max_workers=workers) as ex:
        lps = list(ex.map(lambda s: client.logprob_of(msgs, s), spots))
    m = max(lps)
    w = [math.exp(x - m) for x in lps]
    z = sum(w) or 1.0
    return {s: v / z for s, v in zip(spots, w)}


def aps_scores(dist: Dict[str, float]) -> Dict[str, float]:
    """Romano et al. 2020: the score of y is the cumulative mass of everything ranked at or above it."""
    out, run = {}, 0.0
    for s, p in sorted(dist.items(), key=lambda kv: -kv[1]):
        run += p
        out[s] = run
    return out


class Assay:
    """Fail loudly rather than complete quietly. A suspiciously constant metric is a bug until proven otherwise."""

    def __init__(self):
        self.rows: List[dict] = []

    def add(self, row):
        self.rows.append(row)

    def verdict(self) -> List[str]:
        r = self.rows
        if len(r) < 8:
            return []
        bad = []
        sigs = {json.dumps(x["dist_top"], sort_keys=True) for x in r}
        if len(sigs) == 1:
            bad.append(f"IDENTICAL distribution on all {len(r)} questions")
        args = [x["argmax"] for x in r]
        top_share = max(args.count(a) for a in set(args)) / len(args)
        if top_share > 0.8:
            bad.append(f"one spot is the argmax on {100*top_share:.0f}% of questions")
        mean_top1 = sum(x["p_argmax"] for x in r) / len(r)
        if mean_top1 > 0.9:
            bad.append(f"mean top-1 probability {mean_top1:.2f} - distribution is degenerate")
        sizes = [x["lac_size"] for x in r]
        if len(set(sizes)) == 1:
            bad.append(f"LAC set size pinned at {sizes[0]} on every question")
        agree = sum(x["argmax"] == x["greedy"] for x in r) / len(r)
        if agree < 0.30:
            bad.append(f"scored argmax agrees with the model's own greedy answer only {100*agree:.0f}% "
                       f"of the time - the scoring is probably wrong, not the model")
        return bad

    def summary(self) -> str:
        r = self.rows
        if not r:
            return "(no rows)"
        n = len(r)
        agree = sum(x["argmax"] == x["greedy"] for x in r) / n
        acc_s = sum(x["argmax"] == x["truth"] for x in r) / n
        acc_g = sum(x["greedy"] == x["truth"] for x in r) / n
        right = [x["p_truth"] for x in r if x["greedy"] == x["truth"]]
        wrong = [x["p_truth"] for x in r if x["greedy"] != x["truth"]]
        return (f"  n={n}  distinct argmax spots={len({x['argmax'] for x in r})}  "
                f"mean top-1 p={sum(x['p_argmax'] for x in r)/n:.3f}\n"
                f"  scored argmax == greedy free-text: {100*agree:.0f}%\n"
                f"  accuracy  scored argmax {100*acc_s:.0f}%   greedy free-text {100*acc_g:.0f}%\n"
                f"  p(truth) when greedy right {sum(right)/len(right):.3f} (n={len(right)}) vs "
                f"wrong {sum(wrong)/len(wrong) if wrong else float('nan'):.3f} (n={len(wrong)})\n"
                f"  LAC set size  mean {sum(x['lac_size'] for x in r)/n:.2f}  "
                f"range {min(x['lac_size'] for x in r)}-{max(x['lac_size'] for x in r)}\n"
                f"  APS set size  mean {sum(x['aps_size'] for x in r)/n:.2f}  "
                f"range {min(x['aps_size'] for x in r)}-{max(x['aps_size'] for x in r)}")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--bank", type=pathlib.Path, required=True)
    ap.add_argument("--out", type=pathlib.Path, required=True)
    ap.add_argument("--memory", default="longcontext")
    ap.add_argument("--days", type=int, default=31)
    ap.add_argument("--pilot", type=int, default=0, help="stop after N questions and print the assay")
    ap.add_argument("--alpha", type=float, default=0.1)
    ap.add_argument("--workers", type=int, default=24)
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
    spots = sorted(allowed)
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
    print(f"{header['household_id']}: {len(spots)} receptacles, alpha={a.alpha}", flush=True)

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

            dist = distribution(client, msgs, spots, a.workers)
            ranked = sorted(dist.items(), key=lambda kv: -kv[1])
            argmax, p_argmax = ranked[0]
            p_truth = dist.get(truth, 0.0)
            apsc = aps_scores(dist)

            lac_set = {y for y, p in dist.items() if (1.0 - p) <= lac.q}
            aps_set = {y for y, s in apsc.items() if s <= aps.q}
            lac.update(truth not in lac_set, 1.0 - p_truth)
            aps.update(truth not in aps_set, apsc.get(truth, 1.0))

            rec = {"household": header["household_id"], "question_id": q.question_id, "day_index": q.day_index,
                   "object_id": q.object_id, "t_query": q.t_query, "truth": truth, "greedy": greedy,
                   "verbalized": round(conf or 0.0, 4), "argmax": argmax, "p_argmax": round(p_argmax, 5),
                   "p_truth": round(p_truth, 5), "n_spots": len(spots),
                   "lac_size": len(lac_set), "lac_covered": truth in lac_set, "lac_q": round(lac.q, 4),
                   "aps_size": len(aps_set), "aps_covered": truth in aps_set, "aps_q": round(aps.q, 4),
                   "dist_top": {k: round(v, 4) for k, v in ranked[:8]}}
            fh.write(json.dumps(rec, sort_keys=True) + "\n")
            fh.flush()
            assay.add(rec)
            n += 1
            if n <= 6 or n % 25 == 0:
                print(f"  d{q.day_index:02d} {q.object_id:<18s} truth={truth:<20s} greedy={greedy:<20s} "
                      f"argmax={argmax:<20s} p={p_argmax:.2f} lac={len(lac_set)} aps={len(aps_set)}", flush=True)
            if a.pilot and n >= a.pilot:
                break
        if a.pilot and n >= a.pilot:
            break

    print("\n--- assay ---")
    print(assay.summary(), flush=True)
    bad = assay.verdict()
    if bad:
        print("\n*** DEGENERATE OUTPUT - NOT A RESULT ***")
        for b in bad:
            print("   -", b)
        print(json.dumps(client.stats))
        return 2
    print("\nassay clean.", json.dumps(client.stats))
    return 0


if __name__ == "__main__":
    sys.exit(main())
