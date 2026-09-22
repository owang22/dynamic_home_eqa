"""LLM confidence channels on the naive patrol agent: verbalized vs token probability vs sample agreement.

    python3 -m baselines.patrol.uq_llm --bank hh_s10_t03.jsonl --out DIR [--days 2] [--samples 5]

Same prompt as ``patrol.llm --format conf`` (naive memory, not told).  Per question three calls:

* verbalized: the greedy JSON answer with its stated confidence (temperature 0);
* agreement:  ``--samples`` answers at temperature 0.7 in one request (``n``); confidence = share that
              agree with the greedy answer (semantic entropy reduces to answer entropy for exact-match
              spots; both logged);
* token probability (Ren et al. / KnowNo multiple-choice form): the question re-asked as a choice among
  the 9 spots the 24 h counter ranks highest plus "J) somewhere else", answered with one letter under
  constrained decoding with ``logprobs``; confidence = the letter's probability after renormalizing over
  the option letters.

Rows: classical format with ``answer`` = the greedy spot, ``top_prob`` = verbalized confidence, plus
``conf_agree``, ``entropy``, ``mcq_answer``, ``conf_token``, ``mcq_options``.  Local vLLM only.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import pathlib
import random
import sys
import time
import urllib.request
from collections import Counter, defaultdict
from typing import Dict, List, Optional, Tuple

from baselines.bank import JsonlBank
from baselines.patrol.bocpd import NEGATIVE, DiscountedMostFrequent
from baselines.patrol.llm import CONF_SCHEMA, ENDPOINT, MODEL, Memory, parse_conf, question_messages
from baselines.patrol.run import spots_only
from baselines.types import ON_PERSON, OUT_OF_HOUSE, Observation, SenseResult

LETTERS = "ABCDEFGHIJ"


class Client:
    def __init__(self, cache_dir: pathlib.Path, endpoint: str = ENDPOINT, model: str = MODEL):
        self.cache_dir, self.endpoint, self.model = cache_dir, endpoint, model
        cache_dir.mkdir(parents=True, exist_ok=True)
        self.stats = {"calls": 0, "cached": 0, "prompt_tokens": 0, "completion_tokens": 0, "seconds": 0.0}

    def chat(self, messages: List[dict], max_tokens: int, temperature: float = 0.0, n: int = 1,
             schema: Optional[dict] = None, logprobs: bool = False) -> dict:
        body = {"model": self.model, "messages": messages, "max_tokens": max_tokens, "temperature": temperature, "n": n,
                "seed": 0, "chat_template_kwargs": {"enable_thinking": False}}
        if schema is not None:
            body["response_format"] = {"type": "json_schema", "json_schema": {"name": "answer", "schema": schema}}
        if logprobs:
            body["logprobs"] = True
            body["top_logprobs"] = 20
        key = hashlib.sha256(json.dumps(body, sort_keys=True).encode()).hexdigest()
        path = self.cache_dir / f"{key}.json"
        if path.exists():
            self.stats["cached"] += 1
            return json.loads(path.read_text())
        req = urllib.request.Request(f"{self.endpoint}/v1/chat/completions", data=json.dumps(body).encode(),
                                     headers={"Content-Type": "application/json"})
        t0 = time.time()
        with urllib.request.urlopen(req, timeout=600) as r:
            d = json.load(r)
        self.stats["calls"] += 1
        self.stats["seconds"] += time.time() - t0
        u = d.get("usage") or {}
        self.stats["prompt_tokens"] += int(u.get("prompt_tokens", 0))
        self.stats["completion_tokens"] += int(u.get("completion_tokens", 0))
        path.write_text(json.dumps(d))
        return d


def letter_probs(choice: dict) -> Dict[str, float]:
    """Probability of each option letter from the first generated token's top logprobs."""
    lp = (choice.get("logprobs") or {}).get("content") or []
    if not lp:
        return {}
    first = lp[0]
    out: Dict[str, float] = {}
    for alt in first.get("top_logprobs", []):
        tok = alt["token"].strip().strip('"').upper()
        if len(tok) == 1 and tok in LETTERS:
            out[tok] = out.get(tok, 0.0) + math.exp(alt["logprob"])
    z = sum(out.values())
    return {k: v / z for k, v in out.items()} if z > 0 else {}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--bank", type=pathlib.Path, required=True)
    ap.add_argument("--out", type=pathlib.Path, required=True)
    ap.add_argument("--days", type=int, default=2, help="answer questions on days 1..N")
    ap.add_argument("--day-list", default=None, help="answer only these days (comma list), e.g. 13,14; evidence before them is still folded")
    ap.add_argument("--samples", type=int, default=5)
    ap.add_argument("--endpoint", default=ENDPOINT)
    ap.add_argument("--model", default=MODEL)
    ap.add_argument("--memory", default="naive", help="mem_kind passed to question_messages (naive, retrieval, longcontext, ...); "
                     "only kinds that don't need nightly-written notes are usable here (retrieval, longcontext, naive, recent)")
    a = ap.parse_args(argv)
    day_list = {int(x) for x in a.day_list.split(",")} if a.day_list else None
    a.out.mkdir(parents=True, exist_ok=True)
    client = Client(a.out / "cache", a.endpoint, a.model)
    lines = a.bank.read_text().splitlines()
    header = json.loads(lines[0])
    qmeta = {}
    for l in lines[1:]:
        if '"question"' in l:
            r = json.loads(l)
            if r.get("kind") == "question":
                qmeta[r["question_id"]] = {k: r[k] for k in ("stage", "moment") if k in r}
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
    context = episode.agent_view()
    counter.reset(context)
    for obs in episode.initial_observations:
        counter.update(obs)
    tour_t = int(header["tour_t"])
    evidence = list(episode.evidence_stream())
    cursor = 0
    memory.update_group(tour_t, list(episode.initial_observations) + [e for e in evidence if e.t == tour_t], day_names)
    while cursor < len(evidence) and evidence[cursor].t <= tour_t:
        counter.update(evidence[cursor])
        cursor += 1
    tag = {"household": header["household_id"], "agent": "llm_naive_channels", "belief": "llm_naive_channels",
           "patrol_label": header.get("patrol_label", "")}
    out_path = a.out / f"{header['household_id']}.jsonl"
    done = {json.loads(l)["question_id"] for l in out_path.open()} if out_path.exists() else set()
    fh = out_path.open("a")
    n_done = 0
    for day_questions in episode.questions_by_day:
        for q in day_questions:
            if day_list is not None:
                if q.day_index > max(day_list):
                    break
            elif q.day_index > a.days:
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
            if q.question_id in done or (day_list is not None and q.day_index not in day_list):
                continue
            counter.ensure_object(q.object_id, q.object_class)
            msgs = question_messages(memory, a.memory, q, day_names, cards, rooms, int(header["patrol_hours"]), False, [], None, None,
                                     "conf", header.get("patrol_times") or None, header.get("protocol", {}).get("question_moments", ""),
                                     header.get("protocol", {}).get("feedback_delay_min"))
            truth = episode.true_location(q.object_id, q.t_query)
            # (a) verbalized, greedy
            d = client.chat(msgs, 260, 0.0, 1, CONF_SCHEMA)
            text = d["choices"][0]["message"]["content"]
            loc, conf, why, status = parse_conf(text, allowed)
            answer = loc or memory.last_spot(q.object_id) or sorted(allowed)[0]
            # (b) agreement over samples
            d2 = client.chat(msgs, 260, 0.7, a.samples, CONF_SCHEMA)
            sampled = []
            for ch in d2["choices"]:
                l2, _, _, _ = parse_conf(ch["message"]["content"], allowed)
                sampled.append(l2 or "?")
            cnt = Counter(sampled)
            agree = cnt.get(answer, 0) / len(sampled)
            entropy = -sum(c / len(sampled) * math.log(c / len(sampled)) for c in cnt.values())
            # (c) multiple-choice token probability
            dist, _ = spots_only(dict(counter.predict(q.object_id, q.t_query).distribution))
            options = [s for s, _ in sorted(dist.items(), key=lambda kv: (-kv[1], kv[0]))[:9]]
            if answer in allowed and answer not in options:
                options[-1] = answer
            mcq = msgs[-1]["content"].split("\nReply with JSON")[0] if "Reply with JSON" in msgs[-1]["content"] else msgs[-1]["content"]
            mcq += "\n\nChoose the single most likely spot:\n" + "\n".join(f"{LETTERS[i]}) {s}" for i, s in enumerate(options)) + \
                   f"\n{LETTERS[9]}) somewhere else\nAnswer with the letter only."
            mmsgs = msgs[:-1] + [{"role": "user", "content": mcq}]
            # no JSON schema here: under a JSON-string schema the tokenizer merges the opening quote with the
            # letter ('"A' .. '"I' are single tokens, '"J' is not), so a bare '"' first token forces J = "somewhere
            # else" and the letter mass is never read (uq/problems_found.md P3); the bare letter is its own token
            d3 = client.chat(mmsgs, 2, 0.0, 1, None, logprobs=True)
            ch3 = d3["choices"][0]
            letter = ch3["message"]["content"].strip().strip('"').strip("*").upper()[:1]
            lps = letter_probs(ch3)
            mcq_answer = options[LETTERS.index(letter)] if letter in LETTERS[:9] else "other"
            conf_token = lps.get(letter, 0.0)
            p_truth_token = lps.get(LETTERS[options.index(truth)], 0.0) if truth in options else lps.get("J", 0.0)
            rec = {**tag, **qmeta.get(q.question_id, {}), "day_index": q.day_index, "question_id": q.question_id, "object_id": q.object_id, "object_class": q.object_class,
                   "t_query": q.t_query, "answer": answer, "top_prob": round(conf if conf is not None else 0.0, 4), "truth": truth,
                   "correct": answer == truth, "parse_status": status, "reasoning": why,
                   "samples": sampled, "conf_agree": round(agree, 3), "entropy": round(entropy, 4),
                   "mcq_options": options, "mcq_answer": mcq_answer, "mcq_correct": mcq_answer == truth,
                   "conf_token": round(conf_token, 4), "p_truth_token": round(p_truth_token, 4), "letter_probs": {k: round(v, 4) for k, v in lps.items()}}
            fh.write(json.dumps(rec, sort_keys=True) + "\n")
            fh.flush()
            n_done += 1
            if n_done % 10 == 0:
                print(f"  {q.question_id} greedy {answer} ({rec['top_prob']}) agree {agree:.2f} token {conf_token:.2f} truth {truth} {'OK' if rec['correct'] else 'no'}",
                      file=sys.stderr, flush=True)
    (a.out / "stats.json").write_text(json.dumps(client.stats, indent=1))
    print(json.dumps(client.stats), file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
