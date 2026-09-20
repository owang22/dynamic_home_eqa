"""LLM agents on a patrol bank, against the local vLLM server.

    python3 -m baselines.patrol.llm --bank banks/hh_s0_p4.jsonl --out llm/ \
        --memory naive recent summary --told told not_told --look on off

Three memories, each in a told and a not-told arm, each with the free
look on or off:

* ``naive``: the object's sighting history (newest 60) and the spots
  checked empty since its last sighting. The old llm_belief floor, in
  the plain prompt format of this study.
* ``recent``: the object's last 10 sightings plus the most recent patrol
  listing of every room. Nothing older.
* ``summary``: once per day the model writes short notes (each resident's
  routine, each moving object's usual spots) from that day's movements
  plus the previous notes; questions are answered from the notes plus
  the object's last 3 sightings.

The told arm sees the residents' dated messages (bank header
``hint_messages``) from each shift day's first question on. Every agent
sees the identical patrol stream the classical agents see. Prompts are
checked for hidden state before they are sent (``leak_check``); a leak
aborts the run. Completions are cached by prompt hash, so a rerun with
the same bank and arm replays byte-identically without the server.
Temperature 0, seeded. A completion that does not parse falls back to
the last sighting with confidence 0 and is counted (``fallback``).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import pathlib
import sys
import threading
import time
import urllib.request
from collections import defaultdict
from typing import Any, Dict, List, Optional, Sequence, Tuple

from baselines.bank import JsonlBank
from baselines.patrol.bank import card_sentences
from baselines.patrol.leak_check import check_prompt
from baselines.types import DAY_SECONDS, ON_PERSON, OUT_OF_HOUSE, Episode, Observation, SenseResult

ENDPOINT = os.environ.get("PATROL_LLM_ENDPOINT", "http://127.0.0.1:8300")
MODEL = os.environ.get("PATROL_LLM_MODEL", "Qwen/Qwen3.8-27B")
MEMORIES = ("naive", "recent", "summary")
ABSTAIN = "ABSTAIN"
WEEK = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

ANSWER_SCHEMA_LOOK: Dict[str, Any] = {
    "type": "object",
    "properties": {
        "ranking": {"type": "array", "items": {"type": "string"}, "minItems": 1, "maxItems": 3},
        "confidence": {"type": "number"},
        "look_room": {"type": ["string", "null"]},
    },
    "required": ["ranking", "confidence", "look_room"], "additionalProperties": False}
ANSWER_SCHEMA: Dict[str, Any] = {
    "type": "object",
    "properties": {
        "ranking": {"type": "array", "items": {"type": "string"}, "minItems": 1, "maxItems": 3},
        "confidence": {"type": "number"},
    },
    "required": ["ranking", "confidence"], "additionalProperties": False}


# ------------------------------------------------------------------ client --

class LLMClient:
    """Chat completions against vLLM with a file cache keyed by prompt hash.
    Local server: the spend is zero dollars; tokens are still counted."""

    def __init__(self, cache_dir: pathlib.Path, endpoint: str = ENDPOINT, model: str = MODEL,
                 replay_only: bool = False) -> None:
        self.cache_dir = cache_dir
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.endpoint, self.model, self.replay_only = endpoint, model, replay_only
        self.lock = threading.Lock()
        self.stats = {"calls": 0, "cached": 0, "prompt_tokens": 0, "completion_tokens": 0, "seconds": 0.0}

    def key(self, messages: List[dict], schema: Optional[dict], max_tokens: int) -> str:
        blob = json.dumps({"model": self.model, "messages": messages, "schema": schema,
                           "max_tokens": max_tokens, "temperature": 0, "seed": 0}, sort_keys=True)
        return hashlib.sha256(blob.encode()).hexdigest()

    def complete(self, messages: List[dict], schema: Optional[dict], max_tokens: int) -> Tuple[Optional[str], dict]:
        key = self.key(messages, schema, max_tokens)
        path = self.cache_dir / f"{key}.json"
        if path.exists():
            rec = json.loads(path.read_text())
            with self.lock:
                self.stats["cached"] += 1
            return rec["text"], rec.get("usage", {})
        if self.replay_only:
            return None, {}
        body: Dict[str, Any] = {"model": self.model, "messages": messages, "max_tokens": max_tokens,
                                "temperature": 0, "seed": 0,
                                "chat_template_kwargs": {"enable_thinking": False}}
        if schema is not None:
            body["response_format"] = {"type": "json_schema", "json_schema": {"name": "answer", "schema": schema}}
        req = urllib.request.Request(f"{self.endpoint}/v1/chat/completions", data=json.dumps(body).encode(),
                                     headers={"Content-Type": "application/json"})
        t0 = time.time()
        text, usage = None, {}
        for attempt in range(4):
            try:
                with urllib.request.urlopen(req, timeout=600) as r:
                    d = json.load(r)
                text = d["choices"][0]["message"]["content"]
                usage = d.get("usage") or {}
                break
            except Exception as e:  # noqa: BLE001 - server hiccup: retry, then give up (fallback answer)
                print(f"llm call failed ({attempt + 1}/4): {type(e).__name__}: {e}", file=sys.stderr, flush=True)
                time.sleep(2 * (attempt + 1))
        dt = time.time() - t0
        with self.lock:
            self.stats["calls"] += 1
            self.stats["prompt_tokens"] += int(usage.get("prompt_tokens", 0))
            self.stats["completion_tokens"] += int(usage.get("completion_tokens", 0))
            self.stats["seconds"] += dt
        if text is not None:
            # per-thread temp name: two arms can ask the identical prompt at once
            tmp = path.with_name(f"{path.stem}.{threading.get_ident()}.tmp")
            tmp.write_text(json.dumps({"text": text, "usage": usage, "model": self.model}))
            try:
                tmp.replace(path)
            except OSError:
                tmp.unlink(missing_ok=True)
        return text, usage


# ------------------------------------------------------------------ memory --

def clock(t: int, day_names: Dict[int, str]) -> str:
    day, rem = divmod(int(t), DAY_SECONDS)
    hh, mm = divmod(rem // 60, 60)
    return f"{day_names.get(day, f'day {day}')[:3]} {hh:02d}:{mm:02d}"


class Memory:
    """What an LLM agent has seen: the same stream the classical beliefs
    get, kept in the forms the three prompts read from."""

    def __init__(self, rooms: Dict[str, List[str]], rec_room: Dict[str, str], names: Dict[str, str]) -> None:
        self.rooms, self.rec_room, self.names = rooms, rec_room, names
        self.sightings: Dict[str, List[Tuple[int, str]]] = defaultdict(list)
        self.empties: Dict[str, Dict[str, int]] = defaultdict(dict)      # obj -> rec -> newest empty time
        self.snapshot: Dict[str, Dict[str, Any]] = {}                    # room -> latest listing
        self.moves: Dict[int, List[str]] = defaultdict(list)             # day -> plain-word movement lines
        self.presence: Dict[int, List[str]] = defaultdict(list)          # day -> who was home per pass
        self.classes: Dict[str, str] = {}

    def last_spot(self, obj: str) -> Optional[str]:
        s = self.sightings.get(obj)
        return s[-1][1] if s else None

    def update_group(self, t: int, items: Sequence[Any], day_names: Dict[int, str], is_look: bool = False) -> None:
        """One instant's evidence: observations and/or per-spot listings."""
        listed_rooms = set()
        seen_now: Dict[str, str] = {}
        residents_now: List[str] = []
        for it in items:
            if isinstance(it, Observation):
                seen_now[it.object_id] = it.receptacle_id
                self.classes.setdefault(it.object_id, it.object_class)
                continue
            room = self.rec_room.get(it.receptacle_id)
            if room is None:
                continue
            listed_rooms.add(room)
            snap = self.snapshot.get(room)
            if snap is None or snap["t"] != t:
                snap = {"t": t, "contents": {}, "residents": []}
                self.snapshot[room] = snap
            snap["contents"][it.receptacle_id] = list(it.contents)
            for res in it.residents_present:
                nm = self.names.get(res, res)
                if nm not in snap["residents"]:
                    snap["residents"].append(nm)
                if nm not in residents_now:
                    residents_now.append(nm)
            for o in it.contents:
                seen_now[o] = it.receptacle_id
                self.classes.setdefault(o, it.object_classes.get(o, ""))
        day = t // DAY_SECONDS
        walkthrough = not self.sightings         # the walkthrough itself is not a movement
        for o, rec in sorted(seen_now.items()):
            prev = self.last_spot(o)
            if prev != rec and not walkthrough:
                self.moves[day].append(f"{clock(t, day_names)} {o}: {prev or 'not seen before'} -> {rec}")
            self.sightings[o].append((t, rec))
        # empties: every known object absent from a listed spot
        for it in items:
            if isinstance(it, SenseResult):
                for o in self.sightings:
                    if o not in it.contents:
                        self.empties[o][it.receptacle_id] = t
        full_pass = listed_rooms and listed_rooms >= set(self.rooms)
        if full_pass and not is_look:
            self.presence[day].append(f"{clock(t, day_names)}: {', '.join(residents_now) or 'nobody'}")
            for o in sorted(self.sightings):
                prev = self.last_spot(o)
                if o not in seen_now and prev not in (None, "gone"):
                    self.moves[day].append(f"{clock(t, day_names)} {o}: {prev} -> not in any room")
                    self.sightings[o].append((t, "gone"))   # marker: last full pass did not find it

    def history(self, obj: str) -> List[Tuple[int, str]]:
        return [(t, r) for t, r in self.sightings.get(obj, []) if r != "gone"]

    def checked_since_last_sighting(self, obj: str) -> List[Tuple[int, str]]:
        """(t, spot) listings after the object's last sighting that did not
        show it (the newest per spot)."""
        h = self.history(obj)
        t_last = h[-1][0] if h else -1
        return sorted((t, r) for r, t in self.empties.get(obj, {}).items() if t > t_last)

    def checked_lines(self, obj: str, day_names: Dict[int, str], limit: int = 12) -> List[str]:
        """The same, one line per instant: a full patrol that found nothing
        is one line, a whole room is one item, single spots are listed."""
        by_t: Dict[int, List[str]] = defaultdict(list)
        for t, r in self.checked_since_last_sighting(obj):
            by_t[t].append(r)
        all_spots = {r for recs in self.rooms.values() for r in recs}
        lines = []
        for t in sorted(by_t):
            spots = set(by_t[t])
            if spots >= all_spots:
                lines.append(f"- {clock(t, day_names)}: full patrol, not found in any room")
                continue
            parts = []
            for room, recs in sorted(self.rooms.items()):
                if set(recs) <= spots:
                    parts.append(f"{room} (all spots)")
                else:
                    parts += [r for r in recs if r in spots]
            lines.append(f"- {clock(t, day_names)}: " + ", ".join(parts))
        return lines[-limit:]

    def last_spot_real(self, obj: str) -> Optional[str]:
        h = self.history(obj)
        return h[-1][1] if h else None


# ----------------------------------------------------------------- prompts --

SYSTEM = ("You help a home robot keep track of where household things are. "
          "Read the robot's notes and answer with JSON only.")
SYSTEM_NOTES = ("You help a home robot keep track of where household things are. "
                "You keep short plain-text notes about the home; write the notes as plain text, not JSON.")


def rooms_block(rooms: Dict[str, List[str]]) -> List[str]:
    return [f"- {room}: {', '.join(recs)}" for room, recs in sorted(rooms.items())]


def header_lines(t: int, day_names: Dict[int, str], cards: List[dict], rooms: Dict[str, List[str]],
                 patrol_hours: int, look_on: bool, hints: List[str]) -> List[str]:
    day = t // DAY_SECONDS
    L = [f"Now: {day_names.get(day, 'day ' + str(day))}, {clock(t, day_names)[4:]} (day {day} of the study; "
         f"the walkthrough was on {day_names.get(0, 'day 0')} evening).",
         f"The robot walked through every room on {day_names.get(0, 'day 0')} at 18:00 and since then patrols "
         f"every room every {patrol_hours} hour{'s' if patrol_hours != 1 else ''}, listing what is on every spot "
         f"and who is in the room. Pockets and bags are not looked into."]
    if look_on:
        L.append("Before answering this question the robot may look at ONE room right now, for free.")
    L += ["", "Residents:"] + [f"- {card_sentences(c)}" for c in cards]
    L += ["", "Rooms and spots:"] + rooms_block(rooms)
    L += ["", f"Answer options: a spot name from the list above; {ON_PERSON}:<name> if a resident is carrying it; "
              f"{OUT_OF_HOUSE} if it has been taken out of the home; {ABSTAIN} if you would rather not guess."]
    if hints:
        L += ["", "Messages from the residents:"] + [f"- {h}" for h in hints]
    return L


def memory_lines(memory: Memory, mem_kind: str, obj: str, day_names: Dict[int, str], notes: Optional[str]) -> List[str]:
    h = memory.history(obj)
    L: List[str] = []
    if mem_kind == "naive":
        shown = h[-60:]
        L.append(f"Sightings of {obj} (oldest first{'; newest 60 of ' + str(len(h)) if len(h) > 60 else ''}):")
        L += [f"- {clock(t, day_names)}: {r}" for t, r in shown] or ["- none"]
        L += ["", "Listings since the last sighting that did NOT show it:"]
        L += memory.checked_lines(obj, day_names, 40) or ["- none"]
    elif mem_kind == "recent":
        L.append(f"Last sightings of {obj} (oldest first, at most 10):")
        L += [f"- {clock(t, day_names)}: {r}" for t, r in h[-10:]] or ["- none"]
        L += ["", "Most recent patrol listing of each room:"]
        for room in sorted(memory.rooms):
            snap = memory.snapshot.get(room)
            if snap is None:
                L.append(f"- {room}: not listed yet")
                continue
            who = f"; present: {', '.join(snap['residents'])}" if snap["residents"] else "; nobody present"
            spots = "; ".join(f"{rec}: {', '.join(objs) if objs else 'empty'}" for rec, objs in sorted(snap["contents"].items()))
            L.append(f"- {room} ({clock(snap['t'], day_names)}{who}): {spots}")
    elif mem_kind == "summary":
        L.append("Your notes on this home (written at the end of each day so far):")
        L.append(notes.strip() if notes else "(no notes yet: only the walkthrough has happened)")
        L += ["", f"Last sightings of {obj} (at most 3):"]
        L += [f"- {clock(t, day_names)}: {r}" for t, r in h[-3:]] or ["- none"]
        chk = memory.checked_lines(obj, day_names, 6)
        if chk:
            L += ["", "Listings since the last sighting that did NOT show it:"] + chk
    else:
        raise ValueError(mem_kind)
    return L


def question_messages(memory: Memory, mem_kind: str, q, day_names, cards, rooms, patrol_hours, look_on, hints,
                      notes, look_result: Optional[str]) -> List[dict]:
    L = header_lines(q.t_query, day_names, cards, rooms, patrol_hours, look_on and look_result is None, hints)
    L += ["", f"Question: where is {q.object_id} (a {q.object_class.replace('_', ' ')}) right now?", ""]
    L += memory_lines(memory, mem_kind, q.object_id, day_names, notes)
    if look_result is not None:
        L += ["", look_result]
        L += ["", 'Reply with JSON: {"ranking": [up to 3 answer options, most likely first], '
                  '"confidence": probability from 0 to 1 that the first one is right}']
    elif look_on:
        L += ["", 'Reply with JSON: {"ranking": [up to 3 answer options, most likely first], '
                  '"confidence": probability from 0 to 1 that the first one is right, '
                  '"look_room": a room name to look at right now before you answer, or null to answer without looking}']
    else:
        L += ["", 'Reply with JSON: {"ranking": [up to 3 answer options, most likely first], '
                  '"confidence": probability from 0 to 1 that the first one is right}']
    return [{"role": "system", "content": SYSTEM}, {"role": "user", "content": "\n".join(L)}]


def notes_messages(memory: Memory, day: int, day_names, cards, rooms, patrol_hours, hints, notes: Optional[str],
                   walkthrough: Optional[str]) -> List[dict]:
    t_end = (day + 1) * DAY_SECONDS - 60
    L = header_lines(t_end, day_names, cards, rooms, patrol_hours, False, hints)
    L += ["", f"It is the end of {day_names.get(day, 'day ' + str(day))}. Update your notes on this home.", ""]
    L += ["Your previous notes:", notes.strip() if notes else "(none yet)", ""]
    if walkthrough:
        L += ["What the walkthrough found:", walkthrough, ""]
    L.append(f"Movements the patrol noticed on {day_names.get(day, 'day ' + str(day))} (an object listed on a new spot, "
             f"or not found in any room):")
    L += [f"- {m}" for m in memory.moves.get(day, [])] or ["- none"]
    L += ["", "Who was home at each patrol:"]
    L += [f"- {p}" for p in memory.presence.get(day, [])] or ["- no full patrol yet"]
    L += ["", "Write the updated notes in plain text, at most 350 words: each resident's routine as you now "
              "understand it (when they are out, where they spend time, by weekday and weekend), and for each "
              "object that moves, where it usually is by time of day and what tends to take it out of the house. "
              "Keep what is still true from the previous notes, drop what turned out wrong."]
    return [{"role": "system", "content": SYSTEM_NOTES}, {"role": "user", "content": "\n".join(L)}]


# ------------------------------------------------------------------ parsing --

def parse_answer(text: Optional[str], allowed: set, rooms: set) -> Tuple[Optional[List[str]], Optional[float], Optional[str], Optional[str], str]:
    """(ranking normalized to bank tokens, confidence, look_room, on_person_resident, status)."""
    if not text:
        return None, None, None, None, "no_json"
    try:
        obj = json.loads(text)
    except ValueError:
        start, end = text.find("{"), text.rfind("}")
        try:
            obj = json.loads(text[start:end + 1])
        except ValueError:
            return None, None, None, None, "no_json"
    if not isinstance(obj, dict) or not isinstance(obj.get("ranking"), list) or not obj["ranking"]:
        return None, None, None, None, "bad_shape"
    conf = obj.get("confidence")
    conf = min(1.0, max(0.0, float(conf))) if isinstance(conf, (int, float)) else None
    look = obj.get("look_room")
    look = look if isinstance(look, str) and look in rooms else None
    names: List[str] = []
    carrier = None
    for name in obj["ranking"]:
        if not isinstance(name, str):
            return None, conf, look, None, "bad_shape"
        name = name.strip()
        up = name.upper()
        if up.startswith(ON_PERSON):
            carrier = carrier or name[len(ON_PERSON):].strip(" :()") or None
            name = ON_PERSON
        elif up.startswith(OUT_OF_HOUSE):
            name = OUT_OF_HOUSE
        elif up == ABSTAIN:
            name = ABSTAIN
        if name not in names:
            names.append(name)
    if names[0] not in allowed and names[0] != ABSTAIN:
        return None, conf, look, carrier, "off_list"
    return names, conf, look, carrier, "ok"


# --------------------------------------------------------------------- run --

def run_arm(bank_path: pathlib.Path, mem_kind: str, told: bool, look_on: bool, client: LLMClient,
            out_dir: pathlib.Path, max_days: Optional[int] = None) -> List[dict]:
    header = json.loads(bank_path.read_text().splitlines()[0])
    episode: Episode = next(iter(JsonlBank(bank_path).episodes()))
    day_names = {int(k): v for k, v in header["day_names"].items()}
    cards = header["protocol"]["residents"]
    names = {c["resident_id"]: c["name"] for c in cards}
    patrol_hours = int(header["patrol_hours"])
    hint_rows = header.get("hint_messages", []) if told else []
    rooms: Dict[str, List[str]] = defaultdict(list)
    for rec, room in sorted(episode.receptacle_rooms.items()):
        if rec not in (ON_PERSON, OUT_OF_HOUSE):
            rooms[room].append(rec)
    rooms = {r: sorted(v) for r, v in rooms.items()}
    rec_room = {rec: room for room, recs in rooms.items() for rec in recs}
    allowed = set(episode.receptacle_ids)
    arm = f"llm_{mem_kind}/{'told' if told else 'not_told'}/look_{'on' if look_on else 'off'}"
    tag = {"household": header["household_id"], "patrol_hours": patrol_hours,
           "look": "llm" if look_on else "off", "agent": arm, "belief": arm, "memory": mem_kind, "told": told}
    run_dir = out_dir / f"{header['household_id']}_p{patrol_hours}_{mem_kind}_{'told' if told else 'nottold'}_look{'on' if look_on else 'off'}"
    run_dir.mkdir(parents=True, exist_ok=True)
    calls = open(run_dir / "calls.jsonl", "w")

    def ask(messages: List[dict], schema: Optional[dict], max_tokens: int, where: str, llm_authored=()) -> Tuple[Optional[str], dict]:
        check_prompt(messages, where, llm_authored)
        text, usage = client.complete(messages, schema, max_tokens)
        calls.write(json.dumps({"where": where, "messages": messages, "completion": text, "usage": usage,
                                "llm_authored": [s for s in llm_authored if s]}) + "\n")
        calls.flush()
        return text, usage

    memory = Memory(rooms, rec_room, names)
    # walkthrough: initial sightings plus the empty-spot listings at tour_t
    tour_t = int(header["tour_t"])
    evidence = list(episode.evidence_stream())
    cursor = 0
    memory.update_group(tour_t, list(episode.initial_observations) + [e for e in evidence if e.t == tour_t], day_names)
    while cursor < len(evidence) and evidence[cursor].t <= tour_t:
        cursor += 1
    walkthrough_text = "\n".join(
        f"- {room}: " + "; ".join(f"{rec}: {', '.join(objs) if objs else 'empty'}"
                                  for rec, objs in sorted(memory.snapshot[room]["contents"].items()))
        for room in sorted(memory.snapshot)) if memory.snapshot else None
    # the walkthrough listing came in as sightings + empties; rebuild the full listing for the notes prompt
    tour_contents: Dict[str, Dict[str, List[str]]] = {room: {rec: [] for rec in recs} for room, recs in rooms.items()}
    for o in episode.initial_observations:
        if o.receptacle_id in rec_room:
            tour_contents[rec_room[o.receptacle_id]][o.receptacle_id].append(o.object_id)
    walkthrough_text = "\n".join(
        f"- {room}: " + "; ".join(f"{rec}: {', '.join(sorted(objs)) if objs else 'empty'}" for rec, objs in sorted(tour_contents[room].items()))
        for room in sorted(tour_contents))

    notes: Optional[str] = None
    notes_day = -1
    records: List[dict] = []
    n_fallback = 0
    for day_questions in episode.questions_by_day:
        for q in day_questions:
            if max_days is not None and q.day_index > max_days:
                break
            # deliver the stream up to the question, one instant at a time
            while cursor < len(evidence) and evidence[cursor].t <= q.t_query:
                t = evidence[cursor].t
                grp = []
                while cursor < len(evidence) and evidence[cursor].t == t:
                    grp.append(evidence[cursor]); cursor += 1
                memory.update_group(t, grp, day_names)
            hints = [h["text"] for h in hint_rows if h["day_index"] <= q.day_index]
            # daily notes for the summary memory: written at the first question of each day for the day before
            if mem_kind == "summary":
                while notes_day < q.day_index - 1:
                    notes_day += 1
                    day_hints = [h["text"] for h in hint_rows if h["day_index"] <= notes_day]
                    msgs = notes_messages(memory, notes_day, day_names, cards, rooms, patrol_hours, day_hints, notes,
                                          walkthrough_text if notes_day == 0 else None)
                    text, _ = ask(msgs, None, 900, f"notes day {notes_day}", llm_authored=(notes,))
                    if text and text.strip():
                        notes = text.strip()
            msgs = question_messages(memory, mem_kind, q, day_names, cards, rooms, patrol_hours, look_on, hints, notes, None)
            text, usage = ask(msgs, ANSWER_SCHEMA_LOOK if look_on else ANSWER_SCHEMA, 120, q.question_id, llm_authored=(notes,))
            ranking, conf, look_room, carrier, status = parse_answer(text, allowed, set(rooms))
            rec: Dict[str, Any] = {**tag, "day_index": q.day_index, "question_id": q.question_id, "object_id": q.object_id,
                                   "object_class": q.object_class, "t_query": q.t_query, "prompt_tokens": int(usage.get("prompt_tokens", 0))}
            fallback = ranking is None
            answer = ranking[0] if ranking else (memory.last_spot_real(q.object_id) or OUT_OF_HOUSE)
            top = conf if conf is not None and not fallback else 0.0
            rec.update({"answer_before_look": answer, "top_prob_before_look": round(top, 3), "status_before_look": status,
                        "asked_look": look_room})
            if look_on and look_room is not None and not fallback:
                t = q.t_query
                present = episode.residents_in_room(look_room, t)
                results = [SenseResult(receptacle_id=r, t=t, contents=episode.receptacle_contents(r, t),
                                       object_classes={o: episode.object_classes.get(o, "") for o in episode.receptacle_contents(r, t)},
                                       residents_present=present) for r in rooms[look_room]]
                memory.update_group(t, results, day_names, is_look=True)
                found = any(q.object_id in r.contents for r in results)
                who = ", ".join(names.get(p, p) for p in present) or "nobody"
                look_text = (f"You looked at the {look_room} just now ({clock(t, day_names)}); present: {who}. Contents: "
                             + "; ".join(f"{r.receptacle_id}: {', '.join(r.contents) if r.contents else 'empty'}" for r in results))
                msgs2 = question_messages(memory, mem_kind, q, day_names, cards, rooms, patrol_hours, look_on, hints, notes, look_text)
                text2, usage2 = ask(msgs2, ANSWER_SCHEMA, 120, q.question_id + " after look", llm_authored=(notes,))
                ranking2, conf2, _, carrier2, status2 = parse_answer(text2, allowed, set(rooms))
                rec.update({"look_room": look_room, "found_in_look": found, "status": status2,
                            "prompt_tokens": rec["prompt_tokens"] + int(usage2.get("prompt_tokens", 0))})
                if ranking2 is not None:
                    fallback, answer, top, carrier = False, ranking2[0], (conf2 if conf2 is not None else 0.0), carrier2
                else:
                    fallback, answer, top = True, (memory.last_spot_real(q.object_id) or OUT_OF_HOUSE), 0.0
            else:
                rec["status"] = status
            truth = episode.true_location(q.object_id, q.t_query)
            n_fallback += int(fallback)
            rec.update({"answer": answer, "top_prob": round(top, 3), "fallback": fallback,
                        "on_person_resident": carrier, "truth": truth,
                        "correct": answer == truth, "correct_before_look": rec["answer_before_look"] == truth,
                        "abstain_direct": answer == ABSTAIN})
            records.append(rec)
    calls.close()
    n_ok = sum(r["correct"] for r in records)
    n_abs = sum(r["abstain_direct"] for r in records)
    print(f"  {tag['household']} p{patrol_hours} {arm:36s} right {n_ok}/{len(records)}  direct abstain {n_abs}  "
          f"fallback {n_fallback}  calls {client.stats['calls']} cached {client.stats['cached']}", file=sys.stderr, flush=True)
    with open(run_dir / "run_log.jsonl", "w") as f:
        for r in records:
            f.write(json.dumps(r, sort_keys=True) + "\n")
    (run_dir / "stats.json").write_text(json.dumps({"arm": arm, "n": len(records), "right": n_ok, "direct_abstain": n_abs,
                                                     "fallback": n_fallback, "dollars": 0.0, "model": client.model}, indent=1))
    return records


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--bank", type=pathlib.Path, nargs="+", required=True)
    ap.add_argument("--out", type=pathlib.Path, required=True)
    ap.add_argument("--cache", type=pathlib.Path, default=None)
    ap.add_argument("--memory", nargs="+", default=list(MEMORIES), choices=MEMORIES)
    ap.add_argument("--told", nargs="+", default=["told", "not_told"], choices=["told", "not_told"])
    ap.add_argument("--look", nargs="+", default=["on", "off"], choices=["on", "off"])
    ap.add_argument("--max-days", type=int, default=None, help="stop after this day index (smoke test)")
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--replay-only", action="store_true")
    a = ap.parse_args(argv)
    client = LLMClient(a.cache or (a.out / "cache"), replay_only=a.replay_only)
    jobs = [(b, m, t == "told", l == "on") for b in a.bank for m in a.memory for t in a.told for l in a.look]
    # token estimate before the batch (local server: $0)
    est = len(jobs) * 224 * 1.4 * 1800
    print(f"{len(jobs)} arm runs; rough estimate {est / 1e6:.1f}M prompt tokens; hosted spend $0 (local vLLM {client.model})",
          file=sys.stderr, flush=True)
    from concurrent.futures import ThreadPoolExecutor
    with ThreadPoolExecutor(max_workers=a.workers) as ex:
        futs = [ex.submit(run_arm, b, m, t, l, client, a.out, a.max_days) for b, m, t, l in jobs]
        failed = 0
        for f, job in zip(futs, jobs):
            try:
                f.result()
            except Exception as e:  # noqa: BLE001 - one arm failing must not take the others down
                failed += 1
                print(f"ARM FAILED {job[0].name} {job[1:]}: {type(e).__name__}: {e}", file=sys.stderr, flush=True)
        print(f"{failed} of {len(jobs)} arm runs failed", file=sys.stderr, flush=True)
    print(json.dumps(client.stats), file=sys.stderr)
    (a.out / "llm_stats.json").write_text(json.dumps({**client.stats, "dollars": 0.0, "model": client.model}, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
