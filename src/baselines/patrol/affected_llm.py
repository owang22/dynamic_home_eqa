"""The affected list: one local-LLM call per resident message, scored against the labels.

    python3 -m baselines.patrol.affected_llm --banks DIR/heldout/banks --labels DIR/followon/affected/labels.jsonl \
        --out DIR/followon/affected_llm [--seeds 10-29] [--endpoint http://127.0.0.1:8300] [--model Qwen/Qwen3.8-27B]

At each message day the model sees the residents' cards, the rooms and
spots, the object list and the message, and returns the objects and rooms
whose usual weekday whereabouts the message plausibly changes.  Every list
is logged (``lists.jsonl``) and scored per household-day against the
generator-derived labels: with T = objects that have at least one affected
question that day and U = objects questioned that day,
precision = |L ∩ U ∩ T| / |L ∩ U| and recall = |L ∩ T| / |T|
(``scores.md``).  Local vLLM only; no paid API.
"""
from __future__ import annotations

import argparse
import json
import pathlib
import sys
from collections import defaultdict
from typing import Dict, List, Tuple

from baselines.llm_hypotheses.protocol_text import QUESTIONS_ACTIVITY
from baselines.patrol.llm import ENDPOINT, MODEL, LLMClient, card_sentences, rooms_block
from baselines.patrol.sweep import parse_seeds

MAX_OBJECTS = 20
"""Cap on the list, most likely first; a list of everything is the trust-nothing control, not an interpretation."""

SYSTEM = ("You help a home robot decide which of its learned beliefs about where household objects usually are "
          "should be doubted today, given a short message from the residents.")


def prompt(header: dict, message: dict) -> Tuple[List[dict], dict]:
    cards = header["protocol"]["residents"]
    rooms: Dict[str, List[str]] = defaultdict(list)
    for rec, room in sorted(header["receptacle_rooms"].items()):
        if room and rec not in ("ON_PERSON", "OUT_OF_HOUSE"):
            rooms[room].append(rec)
    objects = sorted(header["object_classes"])
    L = ["Residents:"] + [f"- {card_sentences(c)}" for c in cards]
    L += ["", "Rooms and spots:"] + rooms_block(dict(rooms))
    L += ["", "Objects in the house (id = class_owner; 'shared' has no owner):", ", ".join(objects)]
    L += ["", QUESTIONS_ACTIVITY]
    L += ["", f"Message from the residents this morning ({message['weekday']}): \"{message['text']}\"", "",
          "The robot has learned, from a week of patrols, where each object usually is at each time of a weekday. "
          "Which objects are likely to be somewhere different today because of what the message says, so that the "
          "robot should trust its usual-weekday belief about them less when asked? Think about which activities "
          "happen today that do not happen on a normal weekday, or happen at other times or with other people, and "
          "which objects those activities use and leave out (a resident who stays home eats, works and relaxes at "
          "home; guests change what is out in the rooms they use; a weekend changes who is home and what they do). "
          f"List at most {MAX_OBJECTS} objects, most likely first, and only objects the message gives a reason to doubt. "
          "Also list the rooms most likely to look different."]
    schema = {"type": "object",
              "properties": {"why": {"type": "string", "maxLength": 400},
                             "objects": {"type": "array", "maxItems": MAX_OBJECTS, "items": {"type": "string", "enum": objects}},
                             "rooms": {"type": "array", "items": {"type": "string", "enum": sorted(rooms)}}},
              "required": ["why", "objects", "rooms"], "additionalProperties": False}
    return [{"role": "system", "content": SYSTEM}, {"role": "user", "content": "\n".join(L)}], schema


def score(lists: List[dict], labels: List[dict]) -> Tuple[List[dict], dict]:
    by_hd: Dict[Tuple[str, int], List[dict]] = defaultdict(list)
    for l in labels:
        by_hd[(l["household"], l["day_index"])].append(l)
    rows = []
    for L in sorted(lists, key=lambda r: (r["household"], r["day_index"])):
        labs = by_hd.get((L["household"], L["day_index"]), [])
        universe = {l["object_id"] for l in labs}
        truth = {l["object_id"] for l in labs if l["affected"]}
        listed = set(L["objects"])
        hit_u = listed & universe
        rows.append({"household": L["household"], "day_index": L["day_index"], "message": L["message"],
                     "n_listed": len(listed), "n_listed_questioned": len(hit_u), "n_true": len(truth),
                     "precision": (len(hit_u & truth) / len(hit_u)) if hit_u else None,
                     "recall": (len(listed & truth) / len(truth)) if truth else None,
                     "missed": sorted(truth - listed), "false": sorted(hit_u - truth)})
    pooled = {}
    for k in ("precision", "recall"):
        v = [r[k] for r in rows if r[k] is not None]
        pooled[k] = sum(v) / len(v) if v else None
    n_tp = n_listed_u = n_true = 0
    for L in lists:
        labs = by_hd.get((L["household"], L["day_index"]), [])
        universe = {l["object_id"] for l in labs}
        truth = {l["object_id"] for l in labs if l["affected"]}
        listed = set(L["objects"])
        n_tp += len(listed & truth)
        n_listed_u += len(listed & universe)
        n_true += len(truth)
    pooled["micro_precision"] = n_tp / n_listed_u if n_listed_u else None
    pooled["micro_recall"] = n_tp / n_true if n_true else None
    return rows, pooled


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--banks", type=pathlib.Path, required=True)
    ap.add_argument("--labels", type=pathlib.Path, required=True)
    ap.add_argument("--out", type=pathlib.Path, required=True)
    ap.add_argument("--seeds", default="10-29")
    ap.add_argument("--endpoint", default=ENDPOINT)
    ap.add_argument("--model", default=MODEL)
    ap.add_argument("--replay-only", action="store_true")
    a = ap.parse_args(argv)
    a.out.mkdir(parents=True, exist_ok=True)
    client = LLMClient(a.out / "cache", a.endpoint, a.model, replay_only=a.replay_only)
    labels = [json.loads(l) for l in a.labels.open()]
    lists: List[dict] = []
    lists_path = a.out / "lists.jsonl"
    done = {(r["household"], r["day_index"]) for r in (json.loads(l) for l in lists_path.open())} if lists_path.exists() else set()
    if lists_path.exists():
        lists = [json.loads(l) for l in lists_path.open()]
    with lists_path.open("a") as fh:
        for s in parse_seeds(a.seeds):
            banks = sorted(a.banks.glob(f"hh_s{s}_*.jsonl"))
            if not banks:
                continue
            header = json.loads(banks[0].open().readline())
            for m in sorted(header.get("hint_messages", []), key=lambda m: int(m["day_index"])):
                key = (header["household_id"], int(m["day_index"]))
                if key in done:
                    continue
                messages, schema = prompt(header, m)
                text, usage = client.complete(messages, schema, 600)
                try:
                    ans = json.loads(text) if text else {}
                except json.JSONDecodeError:
                    ans = {}
                rec = {"household": header["household_id"], "day_index": int(m["day_index"]), "weekday": m["weekday"],
                       "message": m["text"], "objects": sorted(set(ans.get("objects", []))), "rooms": sorted(set(ans.get("rooms", []))),
                       "why": ans.get("why", ""), "usage": usage, "raw": text if not ans else None}
                lists.append(rec)
                fh.write(json.dumps(rec, sort_keys=True) + "\n")
                fh.flush()
                print(f"{rec['household']} d{rec['day_index']} {m['text'][:50]!r}: {len(rec['objects'])} objects, rooms {rec['rooms']}",
                      file=sys.stderr, flush=True)
    rows, pooled = score(lists, labels)
    md = ["# Affected list vs generator truth", "", f"{len(rows)} message days. Precision over listed objects that were "
          "questioned that day; recall over objects with an affected question that day.", "",
          f"Pooled (micro): precision {pooled['micro_precision']:.2f}, recall {pooled['micro_recall']:.2f}; "
          f"mean over message days: precision {pooled['precision']:.2f}, recall {pooled['recall']:.2f}", "",
          "| household | day | message | listed | listed & questioned | true affected | precision | recall | missed | false |",
          "|---|---|---|---|---|---|---|---|---|---|"]
    for r in rows:
        f = lambda v: "-" if v is None else f"{v:.2f}"
        md.append(f"| {r['household']} | {r['day_index']} | {r['message'][:60]} | {r['n_listed']} | {r['n_listed_questioned']} | "
                  f"{r['n_true']} | {f(r['precision'])} | {f(r['recall'])} | {', '.join(r['missed'])[:80]} | {', '.join(r['false'])[:80]} |")
    md += ["", "## Per household", "", "| household | message days | mean precision | mean recall |", "|---|---|---|---|"]
    by_hh: Dict[str, List[dict]] = defaultdict(list)
    for r in rows:
        by_hh[r["household"]].append(r)
    for hh, rs in sorted(by_hh.items()):
        p = [r["precision"] for r in rs if r["precision"] is not None]
        q = [r["recall"] for r in rs if r["recall"] is not None]
        md.append(f"| {hh} | {len(rs)} | {sum(p) / len(p):.2f} | {sum(q) / len(q):.2f} |" if p and q else f"| {hh} | {len(rs)} | - | - |")
    (a.out / "scores.md").write_text("\n".join(md) + "\n")
    (a.out / "stats.json").write_text(json.dumps(client.stats, indent=1))
    print("\n".join(md[:6]))
    print(json.dumps(client.stats))
    return 0


if __name__ == "__main__":
    sys.exit(main())
