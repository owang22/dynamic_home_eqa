"""ATUS diary timings by (employment group x schedule group x age band).

Derived from src/icc/load_atus.py and atus/read_extract.py (commit
571638f3) per the plan's "copy it in": the ~40 lines of extract-format
knowledge (record layout, HMS parsing) are copied below rather than
imported, so src/households stays self-contained. Owned copy: edit in
place.

What this adds over the icc loader: PERSON-LEVEL GROUPING. Four person
fields were decoded from the extract 2026-08-28 by the same
distributional-validation method the repo used for the diary date
(atus/README.md "No codebook"): AGE at [80:83] (top-code spike at 80,
mean 45.2), SEX at [84] (57% female — ATUS's known respondent skew),
TELFS labor-force status at [103:105] (62% employed / 32% NILF,
employed mean age 41.9 vs NILF 55.7), TRDPFTPT full/part-time at
[136:138] (79/21 among employed, 99 otherwise — matches the national
80/20). `_validate_person_fields()` re-checks those signatures at load
and raises if the extract stops matching.

Two honest limits, stated rather than papered over:
- ATUS is ONE diary per respondent, so "rotating_shift" is unobservable;
  a rotating household borrows the fixed day/evening/night distributions
  per phase. Schedule group is the DIARY'S OWN work timing, not a coded
  shift variable.
- "retired" is approximated as NILF and age >= 65 (no retirement-reason
  field in this extract).

Output: per-group EMPIRICAL JOINT TUPLES (wake, sleep_min, work_start,
work_end, work_min, n_out_spans), reservoir-sampled per group, seeded.
Generation samples whole tuples, never independent marginals, so a
sampled day is a day some real respondent actually reported.
Written to profiles/households/grounding/atus_group_stats.json by
`python -m households.grounding.load_atus`.
"""
from __future__ import annotations

import collections
import gzip
import json
import pathlib
import random
import statistics

REPO_ROOT = pathlib.Path(__file__).resolve().parents[3]
EXTRACT = REPO_ROOT / "atus" / "atus_00002.dat.gz"
OUT_JSON = (REPO_ROOT / "profiles" / "households" / "grounding"
            / "atus_group_stats.json")

# ---- extract format, copied from atus/read_extract.py (82-char layout) --
ACT = {"caseid": (6, 20), "activity": (29, 35), "where": (35, 39),
       "start": (66, 74), "stop": (74, 82)}
PERSON = {"caseid": (6, 20), "date": (40, 48),
          "age": (80, 83), "sex": (84, 85), "telfs": (103, 105),
          "ftpt": (136, 138)}
DAY_START_MIN = 4 * 60
DAY_MINUTES = 1440
HOME = 101                        # TEWHERE: respondent's home or yard
SLEEP_PREFIX = "0101"       # 010101 sleeping, 010102 sleeplessness
WORK_MAJOR = "05"
EXCLUDED_YEARS = ("2020",)        # same two reasons as src/icc/load_atus.py


def _hms_to_min(hms: str) -> int:
    return int(hms[:2]) * 60 + int(hms[3:5])


AGE_BANDS = ((15, 24, "15-24"), (25, 44, "25-44"),
             (45, 64, "45-64"), (65, 200, "65+"))


def _age_band(age: int) -> str:
    for lo, hi, name in AGE_BANDS:
        if lo <= age <= hi:
            return name
    return "unknown"


def _employment_group(telfs: str, ftpt: str, age: int) -> str:
    if telfs in ("01", "02"):
        return "part_time" if ftpt == "02" else "full_time"
    if age >= 65:
        return "retired"
    return "nonworking_adult"


def _main_work_block(work_eps: list) -> tuple:
    """(start_clock, end_clock) of the longest work block after merging
    gaps <= 90 min ON A CIRCULAR DAY — diaries run 04:00->04:00, so a
    night shift (23:00-07:00) arrives split across the window boundary
    and naive first-start/last-end reads as a 04:00-07:00 job."""
    if not work_eps:
        return (None, None)
    eps = sorted((s % DAY_MINUTES, d) for s, d in work_eps)
    blocks = []
    for s, d in eps:
        if blocks and s - blocks[-1][1] <= 90:
            blocks[-1][1] = max(blocks[-1][1], s + d)
        else:
            blocks.append([s, s + d])
    # circular join: last block wrapping to the first
    if len(blocks) > 1 and (blocks[0][0] + DAY_MINUTES
                            - blocks[-1][1]) <= 90:
        blocks[0][0] = blocks[-1][0] - DAY_MINUTES
        blocks.pop()
    s, e = max(blocks, key=lambda b: b[1] - b[0])
    return (int(s % DAY_MINUTES), int(e % DAY_MINUTES))


def _schedule_group(work_eps: list) -> str:
    """The diary day's own work timing. Minutes of work in each window
    decide; diaries under 2h of work are a non-workday."""
    total = sum(d for _s, d in work_eps)
    if total < 120:
        return "non_workday"
    windows = {"daytime": 0, "evening": 0, "night": 0}
    for start, dur in work_eps:
        for m in range(int(start), int(start + dur), 15):
            clock = m % DAY_MINUTES
            if 8 * 60 <= clock < 18 * 60:
                windows["daytime"] += 15
            elif 18 * 60 <= clock < 23 * 60:
                windows["evening"] += 15
            else:
                windows["night"] += 15
    best = max(windows, key=lambda k: windows[k])
    return best if windows[best] >= total * 0.5 else "split_irregular"


def _validate_person_fields(people: dict) -> None:
    ages = [p["age"] for p in people.values()]
    telfs = collections.Counter(p["telfs"] for p in people.values())
    emp = telfs["01"] + telfs["02"]
    share_emp = emp / len(ages)
    mean_age = statistics.mean(a for a in ages if a < 90)
    if not (0.5 < share_emp < 0.75 and 40 < mean_age < 52):
        raise RuntimeError(
            f"person-field signatures broke: employed {share_emp:.0%}, "
            f"mean age {mean_age:.1f} — re-derive the offsets before "
            f"trusting any group statistic")


def scan(path: pathlib.Path = EXTRACT, reservoir: int = 500,
         seed: int = 0) -> dict:
    """One streaming pass. Returns {group_key: {stats..., days:[...]}}
    where group_key = employment|schedule|age_band|daytype."""
    rng = random.Random(seed)
    people: dict = {}
    groups: dict = collections.defaultdict(
        lambda: {"n": 0, "weight": 0.0, "days": []})

    def flush(case: str, eps: list) -> None:
        p = people.get(case)
        if p is None or p["year"] in EXCLUDED_YEARS:
            return
        work = [(s, d) for code, s, d, _w in eps
                if code[:2] == WORK_MAJOR]
        main = _main_work_block(work)
        sleep_min = sum(d for code, _s, d, _w in eps
                        if code.startswith(SLEEP_PREFIX))
        # wake = end of the sleep run in progress at the 04:00 window
        # start; a diary already awake at 04:00 has no observable wake
        wake = None
        if eps and eps[0][0].startswith(SLEEP_PREFIX):
            t = eps[0][1]
            for code, s, d, _w in eps:
                if not code.startswith(SLEEP_PREFIX) or s > t:
                    break
                t = s + d
            wake = int(t % DAY_MINUTES)
        away, prev_away = 0, False
        for code, _s, _d, where in eps:
            out = (where != HOME and where < 9000)
            if out and not prev_away:
                away += 1
            prev_away = out
        day = {
            "wake": wake, "sleep_min": int(sleep_min),
            "work_start": main[0], "work_end": main[1],
            "work_min": int(sum(d for _s, d in work)),
            "n_out_spans": away,
        }
        sched = _schedule_group(work)
        key = "|".join((p["emp"], sched, p["band"], p["daytype"]))
        g = groups[key]
        g["n"] += 1
        g["weight"] += p["wt"]
        if len(g["days"]) < reservoir:
            g["days"].append(day)
        else:
            j = rng.randrange(g["n"])
            if j < reservoir:
                g["days"][j] = day

    with gzip.open(path, "rt") as f:
        cur, eps = None, []
        for raw in f:
            t = raw[0]
            if t == "2":
                case = raw[PERSON["caseid"][0]:PERSON["caseid"][1]]
                age = int(raw[PERSON["age"][0]:PERSON["age"][1]])
                telfs = raw[PERSON["telfs"][0]:PERSON["telfs"][1]]
                ftpt = raw[PERSON["ftpt"][0]:PERSON["ftpt"][1]]
                d = raw[PERSON["date"][0]:PERSON["date"][1]]
                import datetime
                dow = datetime.date(int(d[:4]), int(d[4:6]),
                                    int(d[6:8])).weekday()
                import re
                m = re.match(r"(\d+\.\d{6})", raw[48:])
                people[case] = {
                    "year": raw[1:5] if raw[1:5].isdigit() else d[:4],
                    "age": age, "telfs": telfs,
                    "emp": _employment_group(telfs, ftpt, age),
                    "band": _age_band(age),
                    "daytype": "weekend" if dow >= 5 else "weekday",
                    "wt": float(m.group(1)) if m else 1.0,
                }
                people[case]["year"] = d[:4]
            elif t == "3":
                case = raw[ACT["caseid"][0]:ACT["caseid"][1]]
                if case != cur:
                    if cur is not None:
                        flush(cur, eps)
                    cur, eps = case, []
                start = _hms_to_min(raw[ACT["start"][0]:ACT["start"][1]])
                stop = _hms_to_min(raw[ACT["stop"][0]:ACT["stop"][1]])
                dur = (stop - start) % DAY_MINUTES or DAY_MINUTES
                # absolute minutes from the 04:00 window start, so
                # cross-midnight ordering survives
                idx = len(eps)
                abs_start = ((start - DAY_START_MIN) % DAY_MINUTES
                             + DAY_START_MIN) if idx == 0 else (
                    eps[-1][1] + eps[-1][2])
                eps.append((raw[ACT["activity"][0]:ACT["activity"][1]],
                            abs_start, dur,
                            int(raw[ACT["where"][0]:ACT["where"][1]])))
        if cur is not None:
            flush(cur, eps)
    _validate_person_fields(people)
    return dict(groups)


def summarize(groups: dict) -> dict:
    """Group -> medians and quartiles for the summary tables; the raw
    tuples ride along for the sampler."""
    def q(vals, p):
        vals = sorted(v for v in vals if v is not None)
        return vals[int(p * (len(vals) - 1))] if vals else None
    out = {}
    for key, g in sorted(groups.items()):
        if g["n"] < 30:
            continue                  # too thin to ground anything on
        days = g["days"]
        out[key] = {
            "n_diaries": g["n"],
            "wake_q25_med_q75": [q([d["wake"] for d in days], p)
                                 for p in (.25, .5, .75)],
            "work_start_med": q([d["work_start"] for d in days], .5),
            "work_end_med": q([d["work_end"] for d in days], .5),
            "work_min_med": q([d["work_min"] for d in days], .5),
            "sleep_min_med": q([d["sleep_min"] for d in days], .5),
            "days": days,
        }
    return out


def _main() -> None:
    import argparse
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out", type=pathlib.Path, default=OUT_JSON)
    ap.add_argument("--seed", type=int, default=0)
    args = ap.parse_args()
    groups = summarize(scan(seed=args.seed))
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(
        {"source": str(EXTRACT.name), "seed": args.seed,
         "excluded_years": list(EXCLUDED_YEARS), "groups": groups},
        indent=1))
    for key, g in groups.items():
        print(f"{key:55s} n={g['n_diaries']:6d} wake_med="
              f"{g['wake_q25_med_q75'][1]} work="
              f"{g['work_start_med']}-{g['work_end_med']}")


if __name__ == "__main__":
    _main()
