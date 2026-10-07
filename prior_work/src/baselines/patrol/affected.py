"""Affected / unaffected labels for patrol-bank questions.

    python3 -m baselines.patrol.affected --banks DIR/banks --sim-dir ../data/situation_sim/confshift/ev10 --out DIR/affected

A question is *affected* when the object's location at question time was
changed by something the told message covers (a major event or the weekend
schedule).  Three components, any one of them makes the label true:

* ``event``    -- the placement in force carries an active major-event cause
                  (``bank.MAJOR_EVENTS``: guest_visit, sick_day) in the
                  generator's cause log;
* ``weekend``  -- the placement in force was made on a Saturday/Sunday by a
                  resident doing an activity that is on their weekend
                  template (blocks, slot defaults, their habits) and not on
                  their weekday template;
* ``absence``  -- the object's owner has a routine weekday activity that
                  uses this object (on their weekday template and done on at
                  least half the weekdays in this household's trace), and
                  that activity is off the schedule today and did not happen:
                  it is not on the weekend template, or the owner's sick day
                  or the household's guest visit removes it.  This is how a sick day or a
                  weekend mostly acts on a routine belief: the commute that
                  would have taken the laptop away never happens.

Every row also carries one ``kind`` (priority order): ``event_moved`` and
``weekend_moved`` while the move is *fresh* (the placement was made after
the last patrol pass before the question, so nothing has seen it there yet),
``stayed_put`` (affected only through absence: the object did not move, the
routine belief is wrong about it, a recency belief is not), ``after_shift``
(a shift move the patrol has since seen), ``other_event``, ``small_cause``,
``plain``.  Affected = the first three.  Freshness depends on the patrol
times, so the labels are written per bank set (``--suffix p8``).

Everything else is *unaffected*.  Two further flags are logged but do not
enter the main split: ``other_event`` (laundry_day, late_work, ... -- the
robot is never told about these) and ``small_cause`` (episodes and mood
flags from ``episodes.yaml``).  ``cause_log_only`` is the narrow label
(event or weekend, household-level) kept for comparison.

The activity behind a placement comes from the truth row's ``cause``
(``bring:<activity>`` / ``trip:<activity>`` / ``pickup:<activity>``) or, for
``placement:*`` rows, from the enclosing "<name> finishes <words>" /
"<name> is back from <words>" line in the generator's ``trace.json`` at the
same minute; the resident comes from that line (or the ``start`` line for
bring/pickup).  Nothing in ``src/situation_sim`` is touched.

Output: ``<out>/labels.jsonl`` (one row per question), ``<out>/shares.md``
(affected share per day, pooled and per household).
"""
from __future__ import annotations

import argparse
import bisect
import json
import pathlib
from collections import Counter, defaultdict
from typing import Dict, List, Optional, Tuple

import yaml

from baselines.patrol.bank import MAJOR_EVENTS, WEEKEND

REPO = pathlib.Path(__file__).resolve().parents[3]
SIM = REPO / "src" / "situation_sim"
DAY = 86400
ROUTINE_SHARE = 0.5
"""An owner's activity counts as routine when it happens on at least this
share of the household's weekdays."""


def _load_yaml(name: str) -> dict:
    with (SIM / name).open() as fh:
        return yaml.safe_load(fh)


def possible_activities(acts: dict, res: dict, daytype: str) -> set:
    """Everything this resident's template allows on a weekday / weekend:
    fixed blocks, slot defaults, and the resident's habits that may fill a
    slot (with their ``then`` follow-ups)."""
    hob, cho = acts["habits"]["hobbies"], acts["habits"]["chores"]
    names: set = set()
    for raw in acts["schedules"][res["role"]][daytype]:
        if "activity" in raw:
            names.add(raw["activity"])
            continue
        names |= slot_activities(acts, res, raw["slot"])
    return names


def slot_activities(acts: dict, res: dict, slot: str) -> set:
    hob, cho = acts["habits"]["hobbies"], acts["habits"]["chores"]
    names = {o["activity"] for o in acts["slot_defaults"][slot] if o["activity"] != "none"}
    for h in sorted(res.get("hobbies", [])):
        spec = hob.get(h)
        if spec and slot in spec["slots"]:
            names.add(spec["activity"])
    for c in sorted(res.get("chores", [])):
        spec = cho.get(c)
        if spec and slot in spec["slots"]:
            names.add(spec["activity"])
            if spec.get("then"):
                names.add(spec["then"])
    return names


def uses_obj(tmpl_uses: List[str], obj: dict, groups: dict) -> bool:
    """Mirror of ``situation_sim.placement.uses_obj`` on the hidden-state object record."""
    for tok in tmpl_uses:
        if obj["cls"] in tok.split("|"):
            return True
    if obj.get("pocket") and "pocket" in tmpl_uses:
        return True
    if obj.get("outdoor") and "outdoor" in tmpl_uses:
        return True
    if obj.get("group"):
        if "bag" in tmpl_uses:
            return True
        if "bag_leader" in tmpl_uses and groups[obj["group"]]["leader"] == obj["id"]:
            return True
    return False


def read_trace(trace: dict, words2act: Dict[str, str]):
    """Three lookups from the generator trace:
    enclosing[(day, minute, object)] = (activity, resident) for placement moves,
    starter[(day, minute, object)]   = resident of the activity that picked the object up,
    done[resident][day]              = activities finished / returned from that day."""
    enclosing: Dict[Tuple[int, int, str], Tuple[Optional[str], Optional[str]]] = {}
    starter: Dict[Tuple[int, int, str], str] = {}
    done: Dict[str, Dict[int, set]] = defaultdict(lambda: defaultdict(set))

    def act_of(text: str) -> Optional[str]:
        for sep in (" finishes ", " is back from "):
            if sep in text:
                return words2act.get(text.split(sep, 1)[1])
        return None

    for day in sorted(trace["days"], key=lambda d: d["day_index"]):
        di = day["day_index"]
        cur = None
        for ln in day["lines"]:
            if ln["kind"] == "start":
                for o in ln["objects"]:
                    starter[(di, ln["minute"], o)] = ln["resident"]
            if not ln["indent"]:
                cur = ln
                a = act_of(ln["text"])
                if a and ln["resident"]:
                    done[ln["resident"]][di].add(a)
            elif ln["kind"] in ("move", "whim", "keep") and cur is not None:
                a = act_of(cur["text"])
                for o in ln["objects"]:
                    enclosing[(di, ln["minute"], o)] = (a, cur["resident"])
    return enclosing, starter, done


def label_bank(bank_path: pathlib.Path, sim_dir: pathlib.Path, acts: dict, events: dict) -> List[dict]:
    rows = [json.loads(l) for l in bank_path.open()]
    header = rows[0]
    hh = header["household_id"]
    state = json.load((sim_dir / hh / "hidden_state.json").open())
    trace = json.load((sim_dir / hh / "trace.json").open())
    words2act = {v["words"]: k for k, v in acts["activities"].items()}
    enclosing, starter, done = read_trace(trace, words2act)
    residents = state["household"]["residents"]
    objects = state["household"]["objects"]
    groups = state["household"]["groups"]
    weekend_days = {int(d) for d, name in header["day_names"].items() if name in WEEKEND}
    weekdays = [d for d in range(header["n_days"]) if d not in weekend_days]
    shift_days = set(header["shift_days"])
    all_events = set(events["events"])
    n_weekdays = max(1, len(weekdays))

    poss = {(rid, dt): possible_activities(acts, residents[rid], dt) for rid in sorted(residents) for dt in ("weekday", "weekend")}
    weekend_only_hh = set().union(*(poss[(r, "weekend")] for r in residents)) - set().union(*(poss[(r, "weekday")] for r in residents))
    # routine = on the weekday template and actually done on enough weekdays
    # (event-added activities such as rest_couch never qualify)
    routine = {rid: {a for a in poss[(rid, "weekday")]
                     if sum(a in done[rid][d] for d in weekdays) >= ROUTINE_SHARE * n_weekdays}
               for rid in sorted(residents)}
    # day -> {resident: [major events active for them]}; household-scope events apply to everyone
    active: Dict[int, Dict[str, List[str]]] = defaultdict(lambda: defaultdict(list))
    for day in state["days"]:
        for c in day["causes"]:
            if c["kind"] == "event" and c["event"] in MAJOR_EVENTS:
                for rid in ([c["resident"]] if c.get("resident") else sorted(residents)):
                    active[day["day_index"]][rid].append(c["event"])

    def removed_today(rid: str, d: int) -> set:
        """Routine weekday activities of ``rid`` that the day's schedule does not
        offer and that did not happen that day."""
        base = poss[(rid, "weekend")] if d in weekend_days else poss[(rid, "weekday")]
        gone = routine[rid] - base
        for ev in active[d].get(rid, []):
            for tok in events["events"][ev].get("schedule", {}).get("remove", []):
                if tok.startswith("slot:"):
                    gone |= routine[rid] & slot_activities(acts, residents[rid], tok[5:])
                elif tok in routine[rid]:
                    gone.add(tok)
        return gone - done[rid][d]

    patrol_ts = sorted({int(r["t"]) for r in rows if r["kind"] == "room_visit"})
    truth: Dict[str, List[dict]] = defaultdict(list)
    for r in rows:
        if r["kind"] == "truth":
            truth[r["object_id"]].append(r)
    for o in truth:
        truth[o].sort(key=lambda r: r["t"])
    times = {o: [r["t"] for r in rs] for o, rs in truth.items()}

    def activity_of(r: dict) -> Tuple[Optional[str], Optional[str]]:
        pre, _, rest = r["cause"].partition(":")
        d, s = divmod(r["t"], DAY)
        key = (d, s // 60, r["object_id"])
        if pre in ("bring", "trip", "pickup"):
            return rest, starter.get(key)
        return enclosing.get(key, (None, None))

    out = []
    for q in [r for r in rows if r["kind"] == "question"]:
        o = q["object_id"]
        d = q["day_index"]
        r = truth[o][bisect.bisect_right(times[o], q["t_query"]) - 1]
        pday = r["t"] // DAY
        act, who = activity_of(r)
        cause_events = sorted({c.split(":")[0] for c in r["causes"]})
        major = [c for c in cause_events if c in MAJOR_EVENTS]
        other = [c for c in cause_events if c in all_events and c not in MAJOR_EVENTS]
        small = sorted(c for c in r["causes"] if c.split(":")[0] not in all_events)
        weekend = bool(pday in weekend_days and act and who in residents
                       and act in poss[(who, "weekend")] - poss[(who, "weekday")])
        owner = objects[o].get("owner")
        absent: List[str] = []
        if owner in residents:
            absent = sorted(a for a in removed_today(owner, d)
                            if a in acts["activities"] and uses_obj(acts["activities"][a].get("uses", []), objects[o], groups))
        # fresh = the placement in force was made after the last patrol pass before the question, so no
        # agent can have seen the object there yet; a shift move the patrol has since seen is 'after_shift'
        last_pass = patrol_ts[bisect.bisect_right(patrol_ts, q["t_query"]) - 1] if patrol_ts and patrol_ts[0] <= q["t_query"] else -1
        fresh = r["t"] > last_pass
        # one kind per question, in priority order: what moved it (while the move is fresh), else why it is
        # 'affected' without moving, else the untold reasons it may be off its routine, else plain
        if major and fresh:
            kind = "event_moved"
        elif weekend and fresh:
            kind = "weekend_moved"
        elif absent:
            kind = "stayed_put"
        elif major or weekend:
            kind = "after_shift"
        elif other:
            kind = "other_event"
        elif small:
            kind = "small_cause"
        else:
            kind = "plain"
        out.append({
            "household": hh, "question_id": q["question_id"], "day_index": d, "kind": kind,
            "object_id": o, "object_class": q["object_class"], "t_query": q["t_query"],
            "affected": kind in ("event_moved", "weekend_moved", "stayed_put"),
            "fresh": fresh, "last_pass": last_pass,
            "event": major, "weekend": weekend, "weekend_activity": act if weekend else None,
            "absence": absent,
            "cause_log_only": bool(major) or bool(pday in weekend_days and act and act in weekend_only_hh),
            "other_event": other, "small_cause": small,
            "placement_day": pday, "placement_cause": r["cause"], "placement_activity": act, "placement_by": who,
            "is_weekend": d in weekend_days, "is_shift_day": d in shift_days,
            "truth": r["receptacle_id"],
        })
    return out


def shares_table(labels: List[dict], day_names: Dict[str, str]) -> str:
    days = sorted({l["day_index"] for l in labels})
    lines = ["| | " + " | ".join(f"{day_names[str(d)][:3]} (d{d})" for d in days) + " | all |",
             "|---|" + "---|" * (len(days) + 1)]

    def row(name, pred):
        cells = []
        for d in days + [None]:
            sub = [l for l in labels if d is None or l["day_index"] == d]
            k = sum(1 for l in sub if pred(l))
            cells.append(f"{100 * k / len(sub):.0f}% ({k}/{len(sub)})" if sub else "-")
        lines.append(f"| {name} | " + " | ".join(cells) + " |")

    row("**affected** (fresh event move, fresh weekend move, or stayed put)", lambda l: l["affected"])
    row("  moved by a major event, any freshness (cause log)", lambda l: bool(l["event"]))
    row("  moved by a weekend activity, any freshness (per resident)", lambda l: l["weekend"])
    row("  absence of a routine activity", lambda l: bool(l["absence"]))
    row("cause-log-only label (event or household weekend activity)", lambda l: l["cause_log_only"])
    row("other event (not told; counted unaffected)", lambda l: bool(l["other_event"]))
    row("small cause (episode/mood; counted unaffected)", lambda l: bool(l["small_cause"]))
    row("shift day", lambda l: l["is_shift_day"])
    for k in ("event_moved", "weekend_moved", "stayed_put", "after_shift", "other_event", "small_cause", "plain"):
        row(f"kind: {k}", lambda l, k=k: l["kind"] == k)
    return "\n".join(lines)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--banks", required=True, help="directory of patrol banks (hh_s<seed>_<label>.jsonl)")
    ap.add_argument("--sim-dir", required=True, help="situation_sim household directory (hh_s<seed>/hidden_state.json, trace.json)")
    ap.add_argument("--out", required=True)
    ap.add_argument("--suffix", default="", help="e.g. p8: writes labels_p8.jsonl / shares_p8.md (freshness depends on the patrol times)")
    args = ap.parse_args(argv)
    sfx = f"_{args.suffix}" if args.suffix else ""
    acts, events = _load_yaml("activities.yaml"), _load_yaml("events.yaml")
    out = pathlib.Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    labels: List[dict] = []
    per_hh: List[Tuple[str, List[dict]]] = []
    day_names = None
    for bank in sorted(pathlib.Path(args.banks).glob("*.jsonl")):
        header = json.loads(bank.open().readline())
        day_names = day_names or header["day_names"]
        rows = label_bank(bank, pathlib.Path(args.sim_dir), acts, events)
        labels += rows
        per_hh.append((header["household_id"], rows))
    with (out / f"labels{sfx}.jsonl").open("w") as fh:
        for l in labels:
            fh.write(json.dumps(l, sort_keys=True) + "\n")
    md = ["# Affected share per day", "",
          f"{len(per_hh)} households, {len(labels)} questions. Affected = the object's location at question time was "
          "changed by a major event (guest_visit, sick_day: cause log), by a resident's weekend-only activity, or by the "
          "absence of the owner's routine weekday activity that uses the object (weekend template or sick-day removal).", "",
          "## Pooled", "", shares_table(labels, day_names), "",
          "## Per household", "",
          "| household | shift days | affected on shift days | on non-shift days | all | weekend activities seen | absent activities seen |",
          "|---|---|---|---|---|---|---|"]
    for hh, rows in per_hh:
        sd = sorted({r["day_index"] for r in rows if r["is_shift_day"]})
        on = [r for r in rows if r["is_shift_day"]]
        off = [r for r in rows if not r["is_shift_day"]]
        wk = sorted({r["weekend_activity"] for r in rows if r["weekend"]})
        ab = sorted({a for r in rows for a in r["absence"]})

        def pct(sub):
            return f"{100 * sum(r['affected'] for r in sub) / len(sub):.0f}% ({sum(r['affected'] for r in sub)}/{len(sub)})" if sub else "-"

        md.append(f"| {hh} | {sd} | {pct(on)} | {pct(off)} | {pct(rows)} | {', '.join(wk) or '-'} | {', '.join(ab) or '-'} |")
    md += ["", "## Weekend-affected placements by activity", "", "| activity | questions |", "|---|---|"]
    for act, n in sorted(Counter(l["weekend_activity"] for l in labels if l["weekend"]).items(), key=lambda kv: (-kv[1], kv[0])):
        md.append(f"| {act} | {n} |")
    md += ["", "## Absence-affected questions by missing activity", "", "| activity | questions |", "|---|---|"]
    for act, n in sorted(Counter(a for l in labels for a in l["absence"]).items(), key=lambda kv: (-kv[1], kv[0])):
        md.append(f"| {act} | {n} |")
    (out / f"shares{sfx}.md").write_text("\n".join(md) + "\n")
    print("\n".join(md))


if __name__ == "__main__":
    main()
