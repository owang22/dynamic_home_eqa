"""Published LLM-memory designs on the frozen regime banks, beside the in-house arms of ``llm.py``.

    python3 -m baselines.patrol.llm_sota --bank B1 B2 --out results/sota_memory/nottold \
        --cache results/sota_memory/cache --memory pinned --told not_told

The question loop is ``llm.run_arm``'s ``conf`` path, copied rather than
patched so ``llm.py`` stays untouched for the arms already run on it: same
header, same answer format, same nightly noticing call, same scoring. What
differs is only the memory block — and, for stores with a write policy,
the LLM calls that maintain the store as evidence arrives (``Store.on_group``).

Degenerate check: ``--memory naive`` here must reproduce ``llm.py``'s naive
arm prompt-for-prompt (run it with ``--replay-only`` against that arm's
cache: every call must be a cache hit and every answer identical).

Memories
* ``naive``   passthrough to ``llm.memory_lines`` (the check above).
* ``pinned``  the naive block unchanged, with the most recent sighting of the
  object at about this time of day (within PIN_TOD_WINDOW_S of the query's
  clock time, any earlier moment) repeated at the top under its own heading.
  Same contents, same write policy; only the salience of one line changes.
  It isolates read-time failure: the answer is often already in the buffer.
"""
from __future__ import annotations

import argparse
import json
import pathlib
import sys
from collections import defaultdict
from typing import Any, Dict, List, Optional, Sequence, Tuple

from baselines.bank import JsonlBank
from baselines.patrol import llm as L
from baselines.patrol.leak_check import check_prompt
from baselines.types import DAY_SECONDS, ON_PERSON, OUT_OF_HOUSE, Episode

PIN_TOD_WINDOW_S = 3600


class Store:
    """A memory design: what it keeps (``on_group`` may call the LLM to
    maintain it) and what the question prompt shows (``lines``)."""
    kind = "base"
    in_house = None      # llm.memory_lines kind to delegate to, if any

    def __init__(self, ask, day_names: Dict[int, str]) -> None:
        self.ask, self.day_names = ask, day_names

    def on_group(self, t: int, items: Sequence[Any], memory: L.Memory) -> None:
        """Called after ``memory.update_group`` for every evidence instant."""

    def lines(self, memory: L.Memory, obj: str, t_query: int) -> List[str]:
        return L.memory_lines(memory, self.in_house, obj, self.day_names, None, query_t=t_query)

    def budget(self, memory: L.Memory, obj: str, t_query: int) -> int:
        """Facts shown at answer time (reported beside accuracy: prompt length alone moves it)."""
        return sum(1 for s in self.lines(memory, obj, t_query) if s.startswith("- ") and s != "- none")


class Naive(Store):
    kind, in_house = "naive", "naive"


class Pinned(Store):
    kind, in_house = "pinned", "naive"

    def lines(self, memory, obj, t_query):
        base = L.memory_lines(memory, "naive", obj, self.day_names, None, query_t=t_query)
        same = [(t, r) for t, r in memory.history(obj) if L._tod_gap(t, t_query) <= PIN_TOD_WINDOW_S]
        head = [f"Most recent sighting of {obj} at about this time of day (within an hour of {L.hhmm(t_query)}):"]
        head += [f"- {L.clock(same[-1][0], self.day_names)}: {same[-1][1]}"] if same else ["- none"]
        return head + [""] + base


STORES = {c.kind: c for c in (Naive, Pinned)}


def run_arm(bank_path: pathlib.Path, kind: str, told: bool, client: L.LLMClient, out_dir: pathlib.Path,
            max_days: Optional[int] = None) -> List[dict]:
    header = json.loads(bank_path.read_text().splitlines()[0])
    kinds = set((header.get("day_kinds") or {}).values())
    L.FLAT_WEEK = bool(kinds) and kinds == {"weekday"}     # read by header_lines; same for every bank of a regime
    patrol_times = header.get("patrol_times") or None
    question_moments = header.get("protocol", {}).get("question_moments", "")
    feedback_delay_min = header.get("protocol", {}).get("feedback_delay_min")
    episode: Episode = next(iter(JsonlBank(bank_path).episodes()))
    day_names = {int(k): v for k, v in header["day_names"].items()}
    cards = header["protocol"]["residents"]
    names = {c["resident_id"]: c["name"] for c in cards}
    patrol_hours = int(header["patrol_hours"])
    hint_rows = header.get("hint_messages", []) if told else []
    if L.FLAT_WEEK:
        hint_rows = [{**h, "text": f"Day {h['day_index']}: " + h["text"].split(": ", 1)[-1]} for h in hint_rows]
    rooms: Dict[str, List[str]] = defaultdict(list)
    for rec, room in sorted(episode.receptacle_rooms.items()):
        if rec not in (ON_PERSON, OUT_OF_HOUSE):
            rooms[room].append(rec)
    rooms = {r: sorted(v) for r, v in rooms.items()}
    rec_room = {rec: room for room, recs in rooms.items() for rec in recs}
    allowed = {r for r in episode.receptacle_ids if r not in (ON_PERSON, OUT_OF_HOUSE)}
    arm = f"llm_{kind}/{'told' if told else 'not_told'}/look_off"
    tag = {"household": header["household_id"], "patrol_hours": patrol_hours, "look": "off", "agent": arm,
           "belief": arm, "memory": kind, "told": told}
    label = header.get("patrol_label", f"p{patrol_hours}")
    run_dir = out_dir / f"{header['household_id']}_{label}_{kind}_{'told' if told else 'nottold'}_lookoff"
    run_dir.mkdir(parents=True, exist_ok=True)
    calls = open(run_dir / "calls.jsonl", "w")

    def ask(messages, schema, max_tokens, where, llm_authored=()):
        check_prompt(messages, where, llm_authored)
        text, usage = client.complete(messages, schema, max_tokens)
        calls.write(json.dumps({"where": where, "messages": messages, "completion": text, "usage": usage,
                                "llm_authored": [s for s in llm_authored if s]}) + "\n")
        calls.flush()
        return text, usage

    store: Store = STORES[kind](ask, day_names)
    memory = L.Memory(rooms, rec_room, names)
    tour_t = int(header["tour_t"])
    evidence = list(episode.evidence_stream())
    cursor = 0
    first = list(episode.initial_observations) + [e for e in evidence if e.t == tour_t]
    memory.update_group(tour_t, first, day_names)
    store.on_group(tour_t, first, memory)
    while cursor < len(evidence) and evidence[cursor].t <= tour_t:
        cursor += 1

    noticing_day = -1
    noticing: List[dict] = []
    records: List[dict] = []
    n_fallback = 0
    for day_questions in episode.questions_by_day:
        for q in day_questions:
            if max_days is not None and q.day_index > max_days:
                break
            while cursor < len(evidence) and evidence[cursor].t <= q.t_query:
                t = evidence[cursor].t
                grp = []
                while cursor < len(evidence) and evidence[cursor].t == t:
                    grp.append(evidence[cursor]); cursor += 1
                memory.update_group(t, grp, day_names)
                store.on_group(t, grp, memory)
            hints = [h["text"] for h in hint_rows if h["day_index"] <= q.day_index]
            while noticing_day < q.day_index - 1:      # identical to llm.run_arm: every arm self-reports nightly
                noticing_day += 1
                day_hints = [h["text"] for h in hint_rows if h["day_index"] <= noticing_day]
                nmsgs = L.noticing_messages(memory, noticing_day, day_names, cards, rooms, patrol_hours, day_hints)
                ntext, _ = ask(nmsgs, L.NOTICING_SCHEMA, 200, f"noticing day {noticing_day}")
                try:
                    nobj = json.loads(ntext) if ntext else {}
                except ValueError:
                    nobj = {}
                noticing.append({"day": noticing_day, "changed": bool(nobj.get("changed")), "who": nobj.get("who"),
                                 "confidence": nobj.get("confidence")})
            Lh = L.header_lines(q.t_query, day_names, cards, rooms, patrol_hours, False, hints, "conf", patrol_times,
                                question_moments, feedback_delay_min)
            Lh += ["", f"Question: where is {q.object_id} (a {q.object_class.replace('_', ' ')}) right now?", ""]
            mem_lines = store.lines(memory, q.object_id, q.t_query)
            msgs = [{"role": "system", "content": L.SYSTEM}, {"role": "user", "content": "\n".join(Lh + mem_lines)}]
            authored = tuple(getattr(store, "authored", lambda: ())())
            text, usage = ask(msgs, L.CONF_SCHEMA, 260, q.question_id, llm_authored=authored)
            loc, conf, why, status = L.parse_conf(text, allowed)
            fallback = loc is None
            answer = loc if loc else (memory.last_spot_real(q.object_id) or sorted(allowed)[0])
            top = conf if conf is not None and not fallback else 0.0
            truth = episode.true_location(q.object_id, q.t_query)
            n_fallback += int(fallback)
            records.append({**tag, "day_index": q.day_index, "question_id": q.question_id, "object_id": q.object_id,
                            "object_class": q.object_class, "t_query": q.t_query,
                            "prompt_tokens": int(usage.get("prompt_tokens", 0)),
                            "completion_tokens": int(usage.get("completion_tokens", 0)), "reasoning": why,
                            "raw_confidence": conf, "patrol_label": label, "answer_before_look": answer,
                            "top_prob_before_look": round(top, 3), "status_before_look": status, "asked_look": None,
                            "status": status, "answer": answer, "top_prob": round(top, 3), "fallback": fallback,
                            "on_person_resident": None, "truth": truth, "correct": answer == truth,
                            "correct_before_look": answer == truth, "abstain_direct": False,
                            "facts_shown": sum(1 for s in mem_lines if s.startswith("- ") and s != "- none")})
    calls.close()
    n_ok = sum(r["correct"] for r in records)
    print(f"  {tag['household']} {arm:36s} right {n_ok}/{len(records)} fallback {n_fallback} "
          f"calls {client.stats['calls']} cached {client.stats['cached']}", file=sys.stderr, flush=True)
    with open(run_dir / "run_log.jsonl", "w") as f:
        for r in records:
            f.write(json.dumps(r, sort_keys=True) + "\n")
    with open(run_dir / "noticing.jsonl", "w") as f:
        for r in noticing:
            f.write(json.dumps({**tag, **r}, sort_keys=True) + "\n")
    (run_dir / "stats.json").write_text(json.dumps({"arm": arm, "n": len(records), "right": n_ok, "fallback": n_fallback,
                                                     "dollars": 0.0, "model": client.model}, indent=1))
    return records


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--bank", type=pathlib.Path, nargs="+", required=True)
    ap.add_argument("--out", type=pathlib.Path, required=True)
    ap.add_argument("--cache", type=pathlib.Path, required=True)
    ap.add_argument("--memory", nargs="+", required=True, choices=sorted(STORES))
    ap.add_argument("--told", nargs="+", default=["not_told"], choices=["told", "not_told"])
    ap.add_argument("--max-days", type=int, default=None)
    ap.add_argument("--workers", type=int, default=3, help="parallel ARMS (one stream each)")
    ap.add_argument("--replay-only", action="store_true")
    a = ap.parse_args(argv)
    client = L.LLMClient(a.cache, replay_only=a.replay_only)
    jobs = [(b, m, t == "told") for b in a.bank for m in a.memory for t in a.told]
    from concurrent.futures import ThreadPoolExecutor
    failed = 0
    with ThreadPoolExecutor(max_workers=a.workers) as ex:
        futs = {ex.submit(run_arm, b, m, t, client, a.out, a.max_days): (b, m, t) for b, m, t in jobs}
        for f, job in futs.items():
            try:
                f.result()
            except Exception as e:  # noqa: BLE001
                failed += 1
                print(f"ARM FAILED {job[0].name} {job[1:]}: {type(e).__name__}: {e}", file=sys.stderr, flush=True)
    print(f"{failed} of {len(jobs)} arm runs failed; {json.dumps(client.stats)}", file=sys.stderr)
    a.out.mkdir(parents=True, exist_ok=True)
    (a.out / "llm_stats.json").write_text(json.dumps({**client.stats, "dollars": 0.0, "model": client.model}, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
