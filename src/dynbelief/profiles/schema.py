"""Profile schema v1: loader + structural validator (rules V1-V5).

Spec: profile_schema_v1.yaml (Section A). Semantics decisions made here and
flagged for researcher review:

  * Blocks with end <= start wrap past midnight into the NEXT calendar day
    (sleep "23:00"->"06:45" on Mo covers Mo 23:00 - Tu 06:45).
  * V3 severity split: nominal overlap of two DIFFERENT activities is FAIL;
    overlap only after jitter expansion is WARN (the generator clamps sampled
    starts so realized blocks never overlap); overlapping blocks of the SAME
    activity merge (INFO) — the spec's own single_adult draft has a weekday
    sleep wrap meeting the weekend sleep block, and return_home/cook_dinner
    within joint jitter reach. A strict reading of V3 would fail the spec's
    own profile, so the strict version is reported as WARN, not FAIL.
  * Schedule activities with no entry in `activities` (sleep, away_at_work)
    are legal no-ops: they occupy time but bind no objects (INFO lists them).
  * `class` is an optional placements field (defaults to the object id with
    any trailing "_<suffix>" of length <=2 stripped, so phone_a/phone_b share
    class "phone"). Multi-resident profiles need per-resident object
    instances to satisfy V1; class is what hazard stats aggregate over.

V5 (alias normalization) is applied AT LOAD: every alias occurrence in
during/after/placements/misplace_set is rewritten to the canonical
receptacle id before anything downstream sees the profile. This is the
dining/dining_room fix done at the source, per the hard rules.
"""
from __future__ import annotations

import copy
import pathlib
import re
from dataclasses import dataclass, field
from typing import Optional

import yaml

DAYS = ["Mo", "Tu", "We", "Th", "Fr", "Sa", "Su"]  # day 0 = Monday (bank convention)
DAY_IDX = {d: i for i, d in enumerate(DAYS)}
MIN_PER_DAY = 1440
MIN_PER_WEEK = 7 * MIN_PER_DAY


def parse_hhmm(s: str) -> int:
    m = re.fullmatch(r"(\d{1,2}):(\d{2})", str(s).strip())
    if not m:
        raise ValueError(f"bad time {s!r} (want HH:MM)")
    h, mi = int(m.group(1)), int(m.group(2))
    if not (0 <= h <= 24 and 0 <= mi < 60) or (h == 24 and mi != 0):
        raise ValueError(f"time out of range: {s!r}")
    return h * 60 + mi


# ── dataclasses ──────────────────────────────────────────────────────────────

@dataclass
class Receptacle:
    id: str
    room: str
    aliases: list[str] = field(default_factory=list)


ANCHORS = ("clock", "wake", "shift_start", "shift_end")


@dataclass
class ScheduleBlock:
    activity: str
    days: list[str]
    start_min: int
    end_min: int          # if <= start_min, wraps into next day
    # How this block re-anchors under a shift-remapping transform (T1/T2).
    # "clock" (default, matches all pre-anchor profiles) = fixed wall-clock time.
    # "wake"/"shift_start"/"shift_end" = start is offset-from that reference;
    # transforms recompute the clock time, the generator only ever sees clock.
    anchor: str = "clock"

    @property
    def duration(self) -> int:
        d = self.end_min - self.start_min
        return d if d > 0 else d + MIN_PER_DAY

    def week_intervals(self, pad: int = 0) -> list[tuple[int, int, str]]:
        """[(t0, t1, activity)] absolute minutes in the week, t1 exclusive.
        Wrapping blocks split at the week boundary. pad expands both ends
        (jitter expansion for V3)."""
        out = []
        for d in self.days:
            t0 = (DAY_IDX[d] * MIN_PER_DAY + self.start_min - pad) % MIN_PER_WEEK
            t1 = t0 + self.duration + 2 * pad
            if t1 <= MIN_PER_WEEK:
                out.append((t0, t1, self.activity))
            else:
                out.append((t0, MIN_PER_WEEK, self.activity))
                out.append((0, t1 - MIN_PER_WEEK, self.activity))
        return out


@dataclass
class Resident:
    id: str
    description: str
    schedule: list[ScheduleBlock]


@dataclass
class AfterBranch:
    dest: Optional[str]        # None = ELSEWHERE (leaves tracked set)
    p: float
    else_dest: Optional[str] = None   # None = stays in place


@dataclass
class Activity:
    name: str
    jitter_min: int = 0
    objects: list[str] = field(default_factory=list)
    during: dict[str, str] = field(default_factory=dict)
    after: dict[str, AfterBranch] = field(default_factory=dict)


@dataclass
class Placement:
    home: str
    p_misplace: float = 0.0
    misplace_set: list[str] = field(default_factory=list)
    volatility_class_hint: Optional[str] = None
    cls: str = ""


@dataclass
class Profile:
    household: str
    status: str
    derived_from: Optional[str]
    transformation: Optional[dict]
    receptacles: list[Receptacle]
    residents: list[Resident]
    activities: dict[str, Activity]
    placements: dict[str, Placement]
    raw: dict = field(repr=False, default_factory=dict)  # normalized dict form

    @property
    def receptacle_ids(self) -> list[str]:
        return [r.id for r in self.receptacles]

    def room_of(self, recep_id: str) -> Optional[str]:
        for r in self.receptacles:
            if r.id == recep_id:
                return r.room
        return None


@dataclass
class Finding:
    check: str        # "V1".."V5" | "load"
    severity: str     # "FAIL" | "WARN" | "INFO"
    message: str

    def __str__(self) -> str:
        return f"[{self.check} {self.severity}] {self.message}"


_SUFFIX = re.compile(r"_(?:[a-z]\d?|[a-z]{2}|\d+)$")


def default_class(obj_id: str) -> str:
    """phone_a / mug_b / keys_p1 -> phone / mug / keys."""
    return _SUFFIX.sub("", obj_id)


# ── V5: alias normalization at load ─────────────────────────────────────────

def _alias_map(receps: list[dict], findings: list[Finding]) -> dict[str, str]:
    canon = {r["id"] for r in receps}
    amap: dict[str, str] = {}
    for r in receps:
        for a in r.get("aliases") or []:
            if a in canon:
                findings.append(Finding("V5", "FAIL",
                    f"alias {a!r} of {r['id']!r} collides with a canonical receptacle id"))
            elif a in amap and amap[a] != r["id"]:
                findings.append(Finding("V5", "FAIL",
                    f"alias {a!r} claimed by both {amap[a]!r} and {r['id']!r}"))
            else:
                amap[a] = r["id"]
    return amap


def _normalize(node, amap: dict[str, str], hits: list[str]):
    """Rewrite alias receptacle references to canonical ids, recursively."""
    if isinstance(node, str):
        if node in amap:
            hits.append(node)
            return amap[node]
        return node
    if isinstance(node, list):
        return [_normalize(v, amap, hits) for v in node]
    if isinstance(node, dict):
        return {k: _normalize(v, amap, hits) for k, v in node.items()}
    return node


# ── loading ─────────────────────────────────────────────────────────────────

def profile_from_dict(data: dict, findings: Optional[list[Finding]] = None) -> Profile:
    """Parse + V5-normalize a profile dict. Structural checks are separate
    (validate_structural); parse errors raise."""
    findings = findings if findings is not None else []
    data = copy.deepcopy(data)
    receps_raw = data.get("receptacles") or []
    amap = _alias_map(receps_raw, findings)

    hits: list[str] = []
    for section in ("activities", "placements"):
        if section in data:
            data[section] = _normalize(data[section], amap, hits)
    if hits:
        findings.append(Finding("V5", "INFO",
            f"normalized {len(hits)} alias reference(s) at load: {sorted(set(hits))}"))

    receptacles = [Receptacle(r["id"], r["room"], list(r.get("aliases") or []))
                   for r in receps_raw]

    residents = []
    for rr in data.get("residents") or []:
        blocks = []
        for b in rr.get("schedule") or []:
            days = list(b["days"])
            bad = [d for d in days if d not in DAY_IDX]
            if bad:
                raise ValueError(f"unknown day tokens {bad} in {rr.get('id')}")
            anchor = b.get("anchor", "clock")
            if anchor not in ANCHORS:
                raise ValueError(f"block {b['activity']!r} in {rr.get('id')}: "
                                 f"unknown anchor {anchor!r} (want {ANCHORS})")
            blocks.append(ScheduleBlock(b["activity"], days,
                                        parse_hhmm(b["start"]), parse_hhmm(b["end"]),
                                        anchor=anchor))
        residents.append(Resident(rr["id"], rr.get("description", ""), blocks))

    activities: dict[str, Activity] = {}
    for name, a in (data.get("activities") or {}).items():
        after = {}
        for obj, br in (a.get("after") or {}).items():
            after[obj] = AfterBranch(dest=br.get("dest"), p=float(br.get("p", 1.0)),
                                     else_dest=br.get("else"))
        activities[name] = Activity(name, int(a.get("jitter_min", 0)),
                                    list(a.get("objects") or []),
                                    dict(a.get("during") or {}), after)

    placements: dict[str, Placement] = {}
    for obj, p in (data.get("placements") or {}).items():
        placements[obj] = Placement(
            home=p["home"], p_misplace=float(p.get("p_misplace", 0.0)),
            misplace_set=list(p.get("misplace_set") or []),
            volatility_class_hint=p.get("volatility_class_hint"),
            cls=p.get("class") or default_class(obj))

    return Profile(
        household=data["household"], status=data.get("status", "DRAFT"),
        derived_from=data.get("derived_from"), transformation=data.get("transformation"),
        receptacles=receptacles, residents=residents,
        activities=activities, placements=placements, raw=data)


def load_profile(path: str | pathlib.Path,
                 findings: Optional[list[Finding]] = None) -> Profile:
    data = yaml.safe_load(pathlib.Path(path).read_text())
    return profile_from_dict(data, findings)


def require_verified(profile: Profile, allow_draft: bool = False) -> None:
    """Bank-build gate (hard rule): refuse DRAFT profiles unless the caller
    passed the explicit dev-mode override — and even then, shout."""
    if profile.status == "VERIFIED":
        return
    if allow_draft:
        import sys
        print(f"[profiles] WARNING: {profile.household} is status={profile.status}; "
              f"proceeding under --allow-draft DEV MODE — results are NOT reportable "
              f"until the profile is human-verified.", file=sys.stderr)
        return
    raise RuntimeError(
        f"profile {profile.household} has status={profile.status}, not VERIFIED. "
        f"Per the hard rules, STOP: a human must verify provenance tags and the "
        f"validator must pass before bank builds. (Dev-mode: allow_draft=True.)")


# ── structural validation V1-V4 (V5 ran at load) ────────────────────────────

def validate_structural(ch: Profile) -> list[Finding]:
    out: list[Finding] = []

    # V2 — referential integrity ------------------------------------------------
    recep_ids = set(ch.receptacle_ids)
    dup = [r for r in ch.receptacle_ids if ch.receptacle_ids.count(r) > 1]
    if dup:
        out.append(Finding("V2", "FAIL", f"duplicate receptacle ids: {sorted(set(dup))}"))

    def _chk_recep(rid, where):
        if rid is not None and rid not in recep_ids:
            out.append(Finding("V2", "FAIL", f"undeclared receptacle {rid!r} in {where}"))

    for name, a in ch.activities.items():
        for obj in a.objects:
            if obj not in ch.placements:
                out.append(Finding("V2", "FAIL",
                    f"activity {name!r} object {obj!r} missing from placements"))
        for obj, rid in a.during.items():
            _chk_recep(rid, f"activities.{name}.during.{obj}")
            if obj not in a.objects:
                out.append(Finding("V2", "WARN",
                    f"activities.{name}.during key {obj!r} not in its objects list"))
        for obj, br in a.after.items():
            _chk_recep(br.dest, f"activities.{name}.after.{obj}.dest")
            _chk_recep(br.else_dest, f"activities.{name}.after.{obj}.else")
            if obj not in a.objects:
                out.append(Finding("V2", "WARN",
                    f"activities.{name}.after key {obj!r} not in its objects list"))
    for obj, p in ch.placements.items():
        _chk_recep(p.home, f"placements.{obj}.home")
        for rid in p.misplace_set:
            _chk_recep(rid, f"placements.{obj}.misplace_set")

    undefined = sorted({b.activity for r in ch.residents for b in r.schedule}
                       - set(ch.activities))
    if undefined:
        out.append(Finding("V2", "INFO",
            f"schedule activities with no object bindings (legal no-ops): {undefined}"))

    # V4 — probabilities --------------------------------------------------------
    for name, a in ch.activities.items():
        for obj, br in a.after.items():
            if not (0.0 <= br.p <= 1.0):
                out.append(Finding("V4", "FAIL",
                    f"activities.{name}.after.{obj}: p={br.p} outside [0,1]"))
        if a.jitter_min < 0:
            out.append(Finding("V4", "FAIL", f"activities.{name}: negative jitter_min"))
    for obj, p in ch.placements.items():
        if not (0.0 <= p.p_misplace <= 1.0):
            out.append(Finding("V4", "FAIL",
                f"placements.{obj}: p_misplace={p.p_misplace} outside [0,1]"))
        if p.p_misplace > 0 and not p.misplace_set:
            out.append(Finding("V4", "FAIL",
                f"placements.{obj}: p_misplace>0 but empty misplace_set"))

    # V3 — per-resident block overlap (nominal FAIL / jitter WARN / same-act merge)
    for r in ch.residents:
        for pad_name, pad_of in (("nominal", lambda b: 0),
                                 ("jitter-expanded",
                                  lambda b: ch.activities.get(b.activity, Activity(b.activity)).jitter_min)):
            ivs = []
            for b in r.schedule:
                ivs.extend(b.week_intervals(pad=pad_of(b)))
            ivs.sort()
            for (a0, a1, act_a), (b0, b1, act_b) in zip(ivs, ivs[1:]):
                if b0 < a1:  # overlap
                    if act_a == act_b:
                        if pad_name == "nominal":
                            out.append(Finding("V3", "INFO",
                                f"{r.id}: same-activity blocks of {act_a!r} overlap "
                                f"(merged by the generator)"))
                    elif pad_name == "nominal":
                        out.append(Finding("V3", "FAIL",
                            f"{r.id}: {act_a!r} and {act_b!r} overlap nominally "
                            f"(week-min {b0}..{a1})"))
                    else:
                        out.append(Finding("V3", "WARN",
                            f"{r.id}: {act_a!r} and {act_b!r} can overlap under "
                            f"jitter (generator clamps sampled starts)"))

    # V1 — no object required in two receptacles at the same instant ------------
    # Concurrent nominal blocks (across ALL residents) that both bind an object
    # with conflicting `during` receptacles.
    tagged = []  # (t0, t1, resident, activity)
    for r in ch.residents:
        for b in r.schedule:
            for (t0, t1, act) in b.week_intervals():
                tagged.append((t0, t1, r.id, act))
    for i in range(len(tagged)):
        for j in range(i + 1, len(tagged)):
            (a0, a1, ra, act_a), (b0, b1, rb, act_b) = tagged[i], tagged[j]
            if ra == rb and act_a == act_b:
                continue
            if max(a0, b0) >= min(a1, b1):
                continue  # not concurrent
            da = ch.activities.get(act_a, Activity(act_a)).during
            db = ch.activities.get(act_b, Activity(act_b)).during
            for obj in set(da) & set(db):
                if da[obj] != db[obj]:
                    out.append(Finding("V1", "FAIL",
                        f"object {obj!r} required at {da[obj]!r} ({ra}:{act_a}) and "
                        f"{db[obj]!r} ({rb}:{act_b}) concurrently"))
            if act_a != act_b:
                oa = set(ch.activities.get(act_a, Activity(act_a)).objects)
                ob = set(ch.activities.get(act_b, Activity(act_b)).objects)
                shared = (oa & ob) - (set(da) & set(db))
                for obj in sorted(shared):
                    out.append(Finding("V1", "WARN",
                        f"object {obj!r} used by concurrent {ra}:{act_a} and "
                        f"{rb}:{act_b} (no during conflict, but simultaneous use)"))

    # dedupe identical findings (the pairwise loops repeat per weekday)
    seen, uniq = set(), []
    for f in out:
        key = (f.check, f.severity, f.message)
        if key not in seen:
            seen.add(key)
            uniq.append(f)
    return uniq


def has_fail(findings: list[Finding]) -> bool:
    return any(f.severity == "FAIL" for f in findings)
