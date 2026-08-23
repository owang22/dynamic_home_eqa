#!/usr/bin/env python3
"""Pure expander: routine_program.yaml -> the dated-calendar structures
(`acts`, `motions`) that profiles/revamp_v1/simulate_activities.py already
consumes. No randomness, no I/O in expand() — realization owns every draw.

Semantics:
- weekly_blocks fire on every episode day whose weekday is in their `days`
  (day 0 = Monday). `start` "HH:MM" may carry "+1": the moment falls past
  midnight of the block's day but belongs to that day's sequence (the v1
  authoring convention for night wraps).
- arc_events patch single days: `drop` removes that day's realizations of
  an activity, `add` appends one-off blocks, `after_override` becomes a
  v1 `day_overrides` entry.
- `end` is honoured by synthesizing a `linger_<at>` gap block at the end
  time whenever the same resident's next block starts later: the v1
  simulator runs every block until the resident's next block, so the
  linger block is what makes an authored `end` the moment the activity's
  `after` rules fire, with the resident staying put. When `end` reaches
  into the next block (an arc appointment splitting a sleep), the next
  block truncates as in v1 and no linger is inserted. Linger blocks carry
  no rules; if a block is skipped at realization, its linger goes with it
  (the `_follows` tag below).

The expansion is deterministic: expand(program) depends on nothing else.
"""
from __future__ import annotations

import argparse
import hashlib
import pathlib

DAY_ABBREV = ["Mo", "Tu", "We", "Th", "Fr", "Sa", "Su"]
DAY_NAMES = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
ELSEWHERE = "ELSEWHERE"
PERSON = "person:"
LINGER_PREFIX = "linger_"
LINGER_JITTER = "routine"


def _minutes(text: str) -> int:
    """"07:05+1" -> absolute minutes within the block's day frame (1865)."""
    plus = text.count("+")
    clock = text.split("+")[0]
    h, m = clock.split(":")
    return int(h) * 60 + int(m) + 1440 * plus


def _fmt(minute_of_day: int) -> str:
    return f"{minute_of_day // 60:02d}:{minute_of_day % 60:02d}"


SLEEP_TOKENS = ("sleep", "nap")


def sleep_activity_name(name: str) -> str:
    """The name a sleep block must carry downstream. export_bank's
    awake_spans and the v1 simulator's misplacement window both detect
    sleep by substring, so a block the author flagged `sleep: true` is
    renamed to satisfy that convention rather than trusting the label
    (models name a block for what it MEANS — "morning_rest" — not for a
    convention they cannot see)."""
    return name if any(s in name for s in SLEEP_TOKENS) else f"sleep_{name}"


NO_OP = "NO_OP"


def _rule_to_v1(rule: dict) -> dict | None:
    """One object_rules entry -> the v1 rule dict, cites/activity/phase
    stripped. A `p` with no `else` would be a branch that resolves to
    `dest` either way, so it is dropped rather than kept as a no-op.

    v3 rules carry NO_OP mass in their dist: the chance this firing
    leaves the object where it is. The v1 sampler knows only locations,
    so the NO_OP mass is lifted out into `noop_p` (an extra key v1's
    validate ignores) and the remaining dist renormalized to sum to 1;
    simulate.py wraps sample_after to draw the no-op branch first. A dist
    that is ENTIRELY NO_OP describes a rule that never does anything and
    returns None (dropped, counted by the caller)."""
    out: dict = {}
    if rule.get("dist"):
        dist = {d["dest"]: d["p"] for d in rule["dist"]}
        noop = dist.pop(NO_OP, 0.0)
        if not dist or noop >= 1.0:
            return None
        total = sum(dist.values())
        if total <= 0:
            return None
        if len(dist) == 1 and noop <= 0:
            out["dest"] = next(iter(dist))
        else:
            # real destinations renormalized to sum to 1; the no-op
            # branch is drawn separately by the simulate wrapper. NO
            # per-entry rounding: round(1/3, 6) * 3 = 0.999999 sits
            # exactly ON v1 validate's 1e-6 tolerance and fails it
            # (measured: hh2's toy_1 relax dist, three equal outcomes).
            out["dist"] = {k: v / total for k, v in dist.items()}
            if noop > 0:
                out["noop_p"] = noop / (noop + total)
    else:
        out["dest"] = rule["dest"]
        if rule.get("p") is not None and rule.get("else") is not None:
            out["p"] = rule["p"]
            out["else"] = rule["else"]
    if rule.get("only_from"):
        out["only_from"] = list(rule["only_from"])
    return out


def pivot_object_rules(program: dict, known: set | None = None,
                       drop_rules_for: set | None = None,
                       renames: dict | None = None) -> dict:
    """object_rules (keyed BY OBJECT) -> {activity: {during: {}, after: {}}}.

    The authoring shape and the simulator's shape differ on purpose: the
    model is asked "what happens to this object?", one object at a time,
    because organising the same content by activity let it silently omit
    objects. The simulator wants the transpose, and this is it.
    """
    # Order matters: the simulator applies an activity's rules in dict
    # order and draws one random number per rule as it goes, so a
    # different order is a different timeline. The object-keyed authoring
    # shape cannot express a per-activity order, so a rule may carry an
    # optional `seq` (used by the revamp_v1 translation to reproduce that
    # world exactly); without it, order is the object's position in the
    # inventory, then the rule's own index — deterministic either way.
    orphaned: list[str] = []
    collected: dict[str, list] = {}
    for i, entry in enumerate(program.get("object_rules") or []):
        for j, rule in enumerate(entry.get("rules") or []):
            # A rule names the activity as the AUTHOR wrote it; sleep
            # renaming happens after. Comparing the raw name against the
            # renamed block set dropped every rule on a renamed activity as
            # a dangling reference — which is how a phone flagged
            # `sleep: true` at wake_up lost its only pick-up rule.
            activity = (renames or {}).get(rule["activity"], rule["activity"])
            if known is not None and activity not in known:
                # A rule on an activity no block runs can never fire — the
                # household was written with a meal or a chore the weekly
                # pattern never scheduled. Counted, not fatal; an object
                # left with nothing that reaches a second place is still
                # caught by the reachability gate.
                orphaned.append(f"{entry['object']}@{rule['activity']}")
                continue
            collected.setdefault(activity, []).append(
                (rule.get("seq", float("inf")), i, j, entry["object"], rule))
    per_activity: dict[str, dict[str, dict]] = {"__orphaned__": orphaned}
    for activity, rules in collected.items():
        slot = per_activity.setdefault(activity, {"during": {}, "after": {}})
        for _, _, _, obj, rule in sorted(rules, key=lambda r: r[:3]):
            if obj in (drop_rules_for or set()):
                continue
            if rule["phase"] == "during":
                slot["during"][obj] = rule["dest"]
            else:
                v1 = _rule_to_v1(rule)
                if v1 is None:      # a dist that is entirely NO_OP: the
                    continue        # rule never does anything — dropped
                slot["after"][obj] = v1
    return per_activity


def placements_of(program: dict) -> list[dict]:
    """The per-object entries, whatever section they live in.

    `home`/`p_misplace` moved INTO `object_rules` so the model keeps one
    list per object instead of two it has to hold in sync (a separate
    `placements` array came back with one object duplicated and another
    missing). Older programs with a standalone `placements` still expand.
    """
    if program.get("placements"):
        by_obj = {e["object"]: e for e in program.get("object_rules") or []}
        return [dict(p, rules=by_obj.get(p["object"], {}).get("rules") or [])
                for p in program["placements"]]
    return list(program.get("object_rules") or [])


def _placement_to_v1(p: dict, static: bool) -> dict:
    """Schema placement -> v1 placement. `static` is derived from the
    program's object_plan (see expand), never carried on the placement
    itself. A zero `p_misplace` is the ABSENCE of the drift mechanism, not
    a zero-probability instance of it: the v1 lint tests `"p_misplace" in
    p` by presence, so keeping a 0.0 would make a declared-static object
    read as mobile and fail reachability."""
    out = {"home": p["home"]}
    if static:
        out["static"] = True
    # Drift needs somewhere to drift TO: a p_misplace with no
    # misplace_set (which the guided-decoding backend accepts however the
    # schema is written) describes nothing, so it is dropped rather than
    # crashing the simulator on a missing key.
    if not static and (p.get("p_misplace") or 0) > 0 and p.get("misplace_set"):
        out["p_misplace"] = p["p_misplace"]
        out["misplace_set"] = list(p["misplace_set"])
    return out


def takes_along(household: str, obj: str, activity: str,
                carry_p: float) -> bool:
    """Does this person take THIS item on THIS kind of trip? A stable,
    hash-derived choice (expand() owns no randomness): with carry_p 0.85,
    roughly one (item, trip-type) pairing in seven is a standing omission
    — she never takes her wallet on the morning walk — so not everything
    is carried everywhere, without any per-day bookkeeping. Per-day
    forgetting comes separately from p_misplace setting the item down
    somewhere before the trip."""
    if carry_p >= 1.0:
        return True
    digest = hashlib.sha256(f"{household}:{obj}:{activity}".encode())
    return int.from_bytes(digest.digest()[:4], "little") % 1000 \
        < carry_p * 1000


AFTER_ONLY_V3 = "after_only_v3"


def expand(program: dict, carry_on_departure: bool = True,
           carry_p: float = 0.85) -> tuple[dict, dict]:
    """routine_program dict -> (acts, motions) for the v1 simulator.

    Programs marked `object_semantics: after_only_v3` (stamped by
    generate.py, never authored) get the v3 behaviours: the during leg is
    SYNTHESIZED (an object with an after rule on an activity is with the
    resident while it runs — at the block's receptacle at home, on the
    person out of the house), and `misplace_set` is DERIVED from the
    rooms the household actually occupies rather than authored. Unmarked
    programs — every existing household and the v1 regression fixture —
    expand exactly as before, byte for byte."""
    days = int(program["days"])
    v3 = program.get("object_semantics") == AFTER_ONLY_V3

    # -- occurrences ------------------------------------------------------
    occs: list[dict] = []          # insertion order is the tie-break order
    def add_occ(day: int, block: dict, uid: str) -> dict:
        occ = {
            "day": day, "uid": uid,
            "resident": block["resident"], "activity": block["activity"],
            "t": block["start"], "note": block.get("note", ""),
            "skip_p": float(block.get("skip_p") or 0.0),
            "end": block.get("end"),
            "at": block["at"], "jitter": block["jitter"],
            "abs": day * 1440 + _minutes(block["start"]),
        }
        occs.append(occ)
        return occ

    # sleep_schedule entries ARE weekly blocks; they live in their own
    # section purely so the schema can require one per resident.
    weekly = [dict(s, sleep=True, skip_p=0.0)
              for s in program.get("sleep_schedule") or []]
    weekly += program["weekly_blocks"]

    # Renaming happens once, up front, so every later reference (arc
    # drops, bindings, per-location variants) sees one consistent name.
    renames = {b["activity"]: sleep_activity_name(b["activity"])
               for b in weekly if b.get("sleep")}
    for i, wb in enumerate(weekly):
        wb = dict(wb, activity=renames.get(wb["activity"], wb["activity"]))
        for d in range(days):
            if DAY_ABBREV[d % 7] in wb["days"]:
                add_occ(d, wb, f"w{i}d{d}")

    day_overrides: list[dict] = []
    vacuous_drops: list[dict] = []
    for j, arc in enumerate(program.get("arc_events") or []):
        d, patch = int(arc["day"]), arc.get("patch") or {}
        for name in [renames.get(n, n) for n in patch.get("drop") or []]:
            hit = [o for o in occs if o["day"] == d and o["activity"] == name]
            if not hit:
                # The activity exists but does not run on this weekday: the
                # patch is simply vacuous. Counted (never silent — see
                # vacuous_drops in meta.json) rather than fatal, because
                # rejecting the whole program over a beat that changes
                # nothing protects no invariant.
                if not any(o["activity"] == name for o in occs):
                    raise ValueError(
                        f"arc day {d}: drop {name!r} names no activity in "
                        f"this program")
                vacuous_drops.append({"day": d, "activity": name})
                continue
            occs = [o for o in occs if o not in hit]
        for k, blk in enumerate(patch.get("add") or []):
            blk = dict(blk, activity=renames.get(blk["activity"],
                                                 blk["activity"]))
            add_occ(d, blk, f"a{j}k{k}")
        for ov in patch.get("after_override") or []:
            rule = ov["rule"]
            day_overrides.append({
                "days": [d], "activity": ov["activity"],
                "reason": arc.get("note", ""),
                "after": {rule["object"]: _rule_to_v1(rule)}})

    # -- away-chain merge (v3) --------------------------------------------
    # An `after` rule fires when its block ENDS, so a resident whose next
    # block is ALSO away gets their things put down mid-trip: measured on
    # hh1, commute_out ended 20:18, work_away ran to 07:00, and keys_1
    # jumped off its owner onto the entry hook for the whole night shift.
    # 36-44% of away blocks are followed by more away time, so this is the
    # common case. Consecutive ELSEWHERE occurrences of one resident are
    # therefore merged into a single away block, keeping the FIRST one
    # (the trip's own reason: work_away, errands) and dropping the rest —
    # the survivor's `after` then fires at the true homecoming. Counted in
    # `merged_away_blocks`, never silent, and v3-only so unmarked
    # programs keep v1 behaviour byte for byte.
    merged_away: list[str] = []
    skipped_away_lingers: list[str] = []
    if v3:
        keep: list[dict] = []
        by_res: dict[str, list[dict]] = {}
        for o in occs:
            by_res.setdefault(o["resident"], []).append(o)
        drop_uids: set[str] = set()
        for rid in sorted(by_res):
            mine = sorted(by_res[rid], key=lambda o: o["abs"])
            i = 0
            while i < len(mine):
                if mine[i]["at"] != ELSEWHERE:
                    i += 1
                    continue
                j = i + 1
                while j < len(mine) and mine[j]["at"] == ELSEWHERE:
                    drop_uids.add(mine[j]["uid"])
                    merged_away.append(
                        f"{mine[j]['activity']}->{mine[i]['activity']}")
                    j += 1
                i = j
        if drop_uids:
            occs = [o for o in occs if o["uid"] not in drop_uids]

    # -- activity table ---------------------------------------------------
    # The v1 simulator reads one `at`/`jitter` per activity NAME, but a
    # multi-resident household legitimately shares one activity across
    # people who do it in different places — four residents each sleeping
    # in their own bed is one "sleep", not four differently-named ones.
    # Blocks are therefore grouped by (activity, at, jitter) and each group
    # beyond the first becomes a per-location variant carrying the same
    # bindings. Single-location activities keep their name untouched, so a
    # program that never needed this expands exactly as before.
    # Going OUT also splits per resident, not just per place: leaving the
    # house is the moment a person's carried things go with them, and two
    # people running their own errands must not pick up each other's phone.
    def _key(o: dict) -> tuple:
        return ((o["at"], o["jitter"], o["resident"])
                if o["at"] == ELSEWHERE else (o["at"], o["jitter"]))

    variants: dict[str, dict[tuple, str]] = {}
    for o in occs:
        key = _key(o)
        group = variants.setdefault(o["activity"], {})
        if key not in group:
            suffix = (o["resident"] if o["at"] == ELSEWHERE else o["at"])
            group[key] = (o["activity"] if not group
                          else f"{o['activity']}__{suffix}")
    activity_info: dict[str, dict] = {}
    away_resident: dict[str, str] = {}      # away variant -> who is out
    for o in occs:
        o["base_activity"] = o["activity"]
        o["activity"] = variants[o["activity"]][_key(o)]
        activity_info[o["activity"]] = {"at": o["at"], "jitter": o["jitter"]}
        if o["at"] == ELSEWHERE:
            away_resident[o["activity"]] = o["resident"]

    # -- linger synthesis (see module docstring) --------------------------
    horizon = days * 1440
    lingers: list[dict] = []
    by_resident: dict[str, list[dict]] = {}
    for o in occs:
        by_resident.setdefault(o["resident"], []).append(o)
    for rid in sorted(by_resident):
        mine = sorted(by_resident[rid], key=lambda o: o["abs"])
        for i, o in enumerate(mine):
            if not o.get("end"):
                continue
            # `end` names a clock time, read as its NEXT occurrence after
            # the block's start. Authors (and models) carry "+1" across a
            # block that already starts past midnight inconsistently; the
            # unambiguous reading is "runs until the clock next says this",
            # which also bounds any block to under 24 h.
            end_abs = o["day"] * 1440 + _minutes(o["end"])
            while end_abs <= o["abs"]:
                end_abs += 1440
            nxt = mine[i + 1]["abs"] if i + 1 < len(mine) else horizon
            if end_abs >= min(nxt, horizon):
                continue                     # truncated by the next block
            if v3 and o["at"] == ELSEWHERE:
                # A linger after an AWAY block splits one trip in two: the
                # away activity ends at its authored `end` and a
                # `linger_out` covers the rest, so the activity's `after`
                # rules fire mid-trip and put things down at home while
                # their owner is still out (measured on hh1: work_away
                # ended 12:03, linger_out ran to 17:45, and the phone was
                # "put on the desk" at 12:03 from four hours away).
                # Occupancy is unchanged either way — both blocks are
                # ELSEWHERE — so the away block simply runs to the
                # resident's next block, and its `after` fires at the real
                # homecoming. This is the away-chain merge above, for the
                # chain the expander itself creates.
                skipped_away_lingers.append(o["activity"])
                continue
            at = o["at"] if o["at"] != ELSEWHERE else None
            name = f"{LINGER_PREFIX}{at}" if at else f"{LINGER_PREFIX}out"
            activity_info.setdefault(
                name, {"at": at or ELSEWHERE, "jitter": LINGER_JITTER})
            # A linger is its own (single-location, binding-free) activity.
            variants.setdefault(name, {(at or ELSEWHERE, LINGER_JITTER): name})
            lingers.append({
                "day": end_abs // 1440, "uid": f"{o['uid']}L",
                "resident": rid, "activity": name,
                "t": _fmt(end_abs % 1440), "note": "",
                "skip_p": 0.0, "end": None, "at": at or ELSEWHERE,
                "jitter": LINGER_JITTER, "abs": end_abs,
                "_follows": o["uid"],
            })
    occs += lingers

    # -- calendar ---------------------------------------------------------
    by_day: dict[int, list[dict]] = {}
    for o in occs:
        by_day.setdefault(o["day"], []).append(o)
    calendar = []
    for d in sorted(by_day):
        items = sorted(by_day[d], key=lambda o: o["abs"])
        entries = []
        for o in items:
            item = {"t": o["t"], "a": o["activity"], "r": o["resident"],
                    "uid": o["uid"]}
            if o["note"]:
                item["note"] = o["note"]
            if o["skip_p"]:
                item["skip_p"] = o["skip_p"]
            if o.get("_follows"):
                item["_follows"] = o["_follows"]
            entries.append(item)
        calendar.append({"day": d, "weekday": DAY_NAMES[d % 7],
                         "activities": entries})

    acts = {"household": program["household"], "days": days,
            "day0": program.get("day0", "Monday"), "calendar": calendar,
            "vacuous_drops": vacuous_drops}

    # -- motions ----------------------------------------------------------
    # Mobility is structural: an object moves iff some rule takes it
    # somewhere other than where it already lives. An object whose every
    # rule names its own home has written a journey that goes nowhere —
    # its rules are dropped and it becomes a declared static, counted as
    # `inert_objects` (validate.py gates on how MANY end up that way: one
    # lazy object should not cost a household, a home that is mostly
    # furniture is not a household).
    # Mobility is judged on the rules that SURVIVE pivoting, never the
    # authored ones: a rule naming an activity nothing schedules is
    # dropped there, and an object whose only real destination came from
    # such a rule is left immobile. Judging before the drop marked it
    # mobile and then handed the v1 lint an object that never moves — the
    # "static=False contradicts its rules" failure.
    # Two entries for one activity are merged rather than rejected: they
    # carry only extras (a tidy walk, a fragment), so the union is exactly
    # what the author meant. Easier to hit now that names come from a
    # closed list, and never worth losing a program over.
    bindings: dict[str, dict] = {}
    for a in program.get("activities") or []:
        name = renames.get(a["name"], a["name"])
        merged = dict(bindings.get(name, {}))
        merged.update(a)
        bindings[name] = merged
    raw_pivot = pivot_object_rules(program, known=set(variants),
                                   renames=renames)
    entries = placements_of(program)
    homes = {p["object"]: p["home"] for p in entries}
    dests_by_obj: dict[str, set] = {p["object"]: set() for p in entries}
    for name, act in raw_pivot.items():
        if name == "__orphaned__":
            continue
        for obj, dest in (act.get("during") or {}).items():
            dests_by_obj[obj].add(dest)
        for obj, rule in (act.get("after") or {}).items():
            dests_by_obj[obj] |= (set(rule["dist"]) if "dist" in rule
                                  else {rule["dest"]}
                                  | ({rule["else"]} if "else" in rule
                                     else set()))
    statics = {o for o, d in dests_by_obj.items() if not d - {homes.get(o)}}
    inert = sorted(statics & {e["object"] for e in entries if e.get("rules")})
    # An inert object must appear in NO rule (the v1 lint's contract for a
    # static), so its dead rules come back out of the pivot.
    for act in raw_pivot.values():
        if isinstance(act, dict):
            for obj in inert:
                act.get("during", {}).pop(obj, None)
                act.get("after", {}).pop(obj, None)
    orphaned_rules = raw_pivot.pop("__orphaned__", [])
    pivoted = raw_pivot          # already keyed by the renamed activity
    # An `activities` entry naming something no block runs carries extras
    # (a tidy walk, a fragment) for an activity that never happens —
    # vacuous in exactly the way an orphaned object rule is. Dropped and
    # counted, same as the rest.
    unused = sorted((set(bindings) | set(pivoted)) - set(variants))
    for name in unused:
        bindings.pop(name, None)
        pivoted.pop(name, None)
    # variant -> the base activity whose bindings it inherits
    base_of = {v: base for base, group in variants.items()
               for v in group.values()}
    all_locations = ([r["id"] for r in program["receptacles"]] + [ELSEWHERE]
                     + [f"person:{r['id']}" for r in program["residents"]])
    program_homes = {e["object"]: e["home"] for e in entries}
    if v3:
        # Drift needs somewhere to drift TO, and under v3 the model
        # authors only the RATE: the candidate spots are derived from the
        # rooms this household actually occupies (the `at` receptacles of
        # its own blocks), most-lived-in first, minus the object's home —
        # an approximation of "set down near wherever the owner is" that
        # stays inside the unforked v1 simulator (whose misplace draw is
        # pre-scheduled; truly time-correlated placement needs a new
        # engine). Deterministic: frequency then receptacle order.
        room_of = {r["id"]: r["room"] for r in program["receptacles"]}
        room_use: dict[str, int] = {}
        for o in occs:
            room = room_of.get(o["at"])
            if room:
                room_use[room] = room_use.get(room, 0) + 1
        rec_rank = {r["id"]: i for i, r in enumerate(program["receptacles"])}
        lived = sorted((r["id"] for r in program["receptacles"]
                        if room_use.get(r["room"])),
                       key=lambda rid: (-room_use[room_of[rid]],
                                        rec_rank[rid]))
        entries = [dict(e) for e in entries]        # never mutate input
        for e in entries:
            if (e.get("p_misplace") or 0) > 0 and not e.get("misplace_set"):
                e["misplace_set"] = [r for r in lived
                                     if r != e.get("home")][:6]
    picked_up: list[str] = []
    left_behind: list[str] = []
    putdown_normalized: list[str] = []
    synthesized_during: list[str] = []
    # ---- v3 person invariant (pre-pass) --------------------------------
    # THE invariant the cross-resident teleports violated: an object ON a
    # person may only be moved by that person's own activity. Measured
    # before this existed: 340 of 349 mid-trip teleports were another
    # resident's shared-name block (resident_1's tidy_up yanking
    # phone_elena off resident_2 at work). Three consequences below:
    #   (a) travellers are never paraded to HOME activity sites (a home
    #       `during` is unguardable in the v1 loop, so the only safe home
    #       during entries are for objects that can never be person-held);
    #   (b) home-variant `after` rules get only_from restricted to
    #       receptacles (a person-held or out-of-house object is out of
    #       reach of anyone's home activity);
    #   (c) person legs are OWNER-AWARE, and an object that rides one kind
    #       of trip rides ALL its owner's trips (keys go along on the walk,
    #       not only to work — per-person behaviour, which per-activity
    #       rules cannot express), with a synthesized homecoming putdown to
    #       `home` on trips whose activity has no authored after rule.
    owners = program.get("object_owners") or {}
    away_base = {o.get("base_activity", o["activity"])
                 for o in occs if o["at"] == ELSEWHERE}
    travellers: dict[str, set] = {}       # obj -> owners' ids that carry it
    if v3:
        for entry_ in placements_of(program):
            obj_ = entry_["object"]
            for r_ in entry_.get("rules") or []:
                if r_["activity"] in away_base:
                    own = owners.get(obj_)
                    if own and own != "shared":
                        travellers.setdefault(obj_, set()).add(own)
    object_motions: dict[str, dict] = {}
    dropped_sleep_resets: list[str] = []
    dropped_sleep_fragments: list[str] = []
    derived_gates: list[str] = []
    for name, info in activity_info.items():
        base = base_of[name]
        b = bindings.get(base, {})
        rules = pivoted.get(base, {"during": {}, "after": {}})
        entry: dict = {"at": info["at"], "jitter": info["jitter"],
                       "during": dict(rules["during"]),
                       "after": {o: dict(r) for o, r in rules["after"].items()}}
        if b.get("reset_all"):
            if any(s in name for s in SLEEP_TOKENS):
                # A reset_all is a WALK through the house; a sleeping
                # resident cannot take it. The model attaches one anyway
                # (its intent is "things get put away around this sleep"),
                # so it is dropped and counted rather than rejected — the
                # tidying it describes could not have happened either way.
                dropped_sleep_resets.append(name)
            else:
                entry["reset_all"] = {k: v for k, v in b["reset_all"].items()
                                      if k in ("p", "objects")}
        # Leaving the house takes your things with you. Authored rules can
        # only cover the going-out activities the author thought to name,
        # and a household has several — so every block that starts at
        # ELSEWHERE picks up the departing resident's person-homed items.
        # This is a general behaviour, not a per-household judgement, and
        # it is what makes ON_PERSON mean anything once somebody is out.
        # Forgetting is still modelled: p_misplace can leave an item on a
        # table before the trip, and it stays there.
        # For a carried object, a put-down on a HOME activity fires when
        # the activity STARTS ("sits down to study, sets the phone on the
        # desk") rather than when it ends. This is truer to how phones are
        # set down — and it is load-bearing: the v1 event loop fires a
        # boundary minute's `during` before its `after`, so an end-of-block
        # put-down landed one tick after the next block's departure pickup
        # and silently overrode it; the phone was picked up and instantly
        # back on the nightstand. Away activities keep their put-down at
        # the end — that is the return home. Stochastic put-downs use their
        # modal destination; drift stays with p_misplace.
        if carry_on_departure and info["at"] != ELSEWHERE and not v3:
            for obj in list(entry["after"]):
                if not str(program_homes.get(obj, "")).startswith(PERSON):
                    continue
                rule = entry["after"].pop(obj)
                dest = (rule.get("dest") or
                        max(rule["dist"], key=rule["dist"].get))
                entry["during"].setdefault(obj, dest)
                putdown_normalized.append(f"{obj}@{name}")
        if v3:
            # v3 during synthesis: an object with an after rule on this
            # activity is WITH the resident while it runs — visible at
            # the block's receptacle at home, on the person when out —
            # then the authored after-dist decides where it lands.
            if info["at"] == ELSEWHERE and name in away_resident:
                rid = away_resident[name]
                carrier = f"{PERSON}{rid}"
                # (c) owner-aware person legs: only the OWNER's variant
                # carries the object (owner-blind synthesis put keys_elias
                # on whoever left the house first), and an object that
                # rides one kind of its owner's trip rides them ALL —
                # "takes the keys when leaving" is a property of the
                # person, which no per-activity rule set expresses.
                for obj, rid_set in travellers.items():
                    if rid not in rid_set:
                        continue
                    entry["during"].setdefault(obj, carrier)
                    synthesized_during.append(f"{obj}@{name}")
                    if obj not in entry["after"]:
                        # homecoming putdown for trips whose activity has
                        # no authored after rule: the thing comes off the
                        # person when they walk in, to its usual spot.
                        entry["after"][obj] = {"dest": homes.get(obj)
                                               or program_homes.get(obj),
                                               "only_from": [carrier]}
                        synthesized_during.append(f"{obj}@{name}:putdown")
            elif info["at"] != ELSEWHERE:
                site = info["at"]
                for obj, rule in entry["after"].items():
                    # (a) travellers are NEVER paraded to home sites: a
                    # home `during` fires unguarded in the v1 loop, so it
                    # would yank a person-held object off an absent owner
                    # (and "keys follow her to watch_tv" reads wrong even
                    # when she is home). Non-travellers can never be
                    # person-held, so their parade is provably safe.
                    if obj in travellers:
                        continue
                    if rule.get("noop_p", 0) >= 0.5:
                        continue
                    entry["during"].setdefault(obj, site)
                    synthesized_during.append(f"{obj}@{name}")
                # (b) a home activity's after rules reach RECEPTACLES
                # only: an object on a person, or out of the house, is out
                # of anyone's reach at home. Synthesize the gate when the
                # author left it off; intersect when present.
                receptacle_only = [r["id"] for r in program["receptacles"]]
                fragmented = bool(b.get("fragment")) and \
                    not any(s in name for s in SLEEP_TOKENS)
                for obj, rule in entry["after"].items():
                    targets = (set(rule["dist"]) if "dist" in rule
                               else {rule.get("dest")}
                               | ({rule["else"]} if "else" in rule
                                  else set()))
                    base_from = (receptacle_only if not fragmented
                                 # a fragmented rule fires once per bout:
                                 # keep the derived no-refire property by
                                 # excluding its own destinations too
                                 else [x for x in receptacle_only
                                       if x not in targets])
                    if "only_from" in rule:
                        kept = [x for x in rule["only_from"]
                                if x in base_from]
                        rule["only_from"] = kept or list(base_from)
                    else:
                        rule["only_from"] = list(base_from)
        if carry_on_departure and info["at"] == ELSEWHERE \
                and name in away_resident:
            carrier = f"{PERSON}{away_resident[name]}"
            for obj, place in program_homes.items():
                if place != carrier:
                    continue
                if takes_along(program["household"], obj, base, carry_p):
                    entry["during"].setdefault(obj, carrier)
                    picked_up.append(f"{obj}@{name}")
                else:
                    left_behind.append(f"{obj}@{name}")
        if b.get("fragment"):
            if any(s in name for s in SLEEP_TOKENS):
                # Sleep is one bout by definition; a fragmented sleep is
                # the model reaching for the mechanism where it cannot
                # apply. Dropped and counted, like the sleep reset_all.
                dropped_sleep_fragments.append(name)
            else:
                entry["fragment"] = dict(b["fragment"])
                # `only_from` on a fragmented activity's after-rules exists
                # for exactly one reason: those rules fire once per bout,
                # and a rule that can re-fire from its OWN result bounces
                # an object back and forth all evening. When the author
                # leaves it off, that purpose is derivable rather than
                # invented — gate the rule on the object not already being
                # at one of its own destinations.
                for obj, rule in entry["after"].items():
                    if "only_from" not in rule:
                        targets = (set(rule["dist"]) if "dist" in rule
                                   else {rule["dest"]}
                                   | ({rule["else"]} if "else" in rule
                                      else set()))
                        rule["only_from"] = [loc for loc in all_locations
                                             if loc not in targets]
                        derived_gates.append(f"{name}.{obj}")
        object_motions[name] = entry

    motions = {
        "household": program["household"],
        "household_type": program.get("household_type"),
        "source_persona": program.get("source_persona", "persona.yaml"),
        "residents": [{"id": r["id"], "jitter_scale": r["jitter_scale"]}
                      for r in program["residents"]],
        "receptacles": [{"id": r["id"], "room": r["room"]}
                        for r in program["receptacles"]],
        "placements": {p["object"]: _placement_to_v1(p, p["object"] in statics)
                       for p in entries},
        "object_motions": object_motions,
    }
    if day_overrides:
        motions["day_overrides"] = day_overrides
    acts["dropped_sleep_resets"] = sorted(set(dropped_sleep_resets))
    acts["dropped_sleep_fragments"] = sorted(set(dropped_sleep_fragments))
    acts["derived_only_from"] = sorted(set(derived_gates))
    acts["orphaned_rules"] = sorted(set(orphaned_rules))
    acts["unscheduled_activities"] = unused
    acts["inert_objects"] = inert
    acts["carried_on_departure"] = sorted(set(picked_up))
    acts["left_behind_by_trip"] = sorted(set(left_behind))
    acts["carried_putdowns_at_start"] = sorted(set(putdown_normalized))
    acts["synthesized_during"] = sorted(set(synthesized_during))
    acts["merged_away_blocks"] = sorted(merged_away) if v3 else []
    acts["skipped_away_lingers"] = sorted(set(skipped_away_lingers))
    return acts, motions


def main() -> None:
    import yaml
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("program", type=pathlib.Path,
                    help="routine_program.yaml (or a household dir holding one)")
    args = ap.parse_args()
    path = args.program
    if path.is_dir():
        path = path / "routine_program.yaml"
    acts, motions = expand(yaml.safe_load(path.read_text()))
    print(yaml.safe_dump({"acts": acts, "motions": motions},
                         sort_keys=False, width=100))


if __name__ == "__main__":
    main()
