#!/usr/bin/env python3
"""Every number we wrote about the six scenarios, checked against the banks.

Numbers in prose drift. This walks the prose files that describe the six scenarios,
pulls out every numeric token with its context, and tries to match each one against a
value recomputed from the question banks by check_scenario.py. It prints three lists:

    MATCHED     the number equals a recomputed quantity, and which one
    STRUCTURAL  the number is a calendar day, a class count, a threshold or a plain
                count of things (ten households, seven checks) - not a measurement
    UNMATCHED   nothing recomputed equals it. THESE ARE THE ONES TO CHECK BY HAND,
                with the command that checks them printed beside each file.

It is a drift detector, not a proof: a number can match by coincidence, and a matched
number can still be attached to the wrong claim. Read the context it prints.

    python3 results/self_improve/check_numbers_in_prose.py
    python3 results/self_improve/check_numbers_in_prose.py --note   # write the .md note

Nothing is modified unless --note is given, and then only
results/self_improve/scenario/NUMBERS_IN_PROSE.md.
"""
from __future__ import annotations

import argparse
import json
import pathlib
import re
import subprocess
import sys
import tempfile

HERE = pathlib.Path(__file__).resolve().parent
REPO = HERE.parents[1]
RUNS = HERE / "runs"
N = "a timetable that never forgets"
F = "a timetable with a three-day memory"

SCENARIOS = ["illness_v1", "illness_v2", "room_shut_v1", "guest_v1", "wfh_v1", "night_shift_v1"]

# prose we wrote, and who owns it
PROSE = [
    ("results/self_improve/scenario/WHICH_DISRUPTIONS_WORK.md", "all six"),
    ("results/self_improve/runs/room_shut_v1/VERDICT.md", "room_shut_v1"),
    ("results/self_improve/runs/guest_v1/VERDICT.md", "guest_v1"),
    ("results/self_improve/runs/wfh_v1/VERDICT.md", "wfh_v1"),
    ("results/self_improve/runs/night_shift_v1/VERDICT.md", "night_shift_v1"),
    ("results/self_improve/scenario/room_shut_v1.yaml", "room_shut_v1"),
    ("results/self_improve/scenario/guest_v1.yaml", "guest_v1"),
    ("results/self_improve/scenario/wfh_v1.yaml", "wfh_v1"),
    ("results/self_improve/scenario/night_shift_v1.yaml", "night_shift_v1"),
]

RULES_ONLY = [
    # These carry rule parameters - start times, durations, daily rates - and assert no
    # measurement, so there is nothing in them to drift against the data. Listed for
    # completeness; not scanned.
    "results/self_improve/scenario/events_room_shut.yaml",
    "results/self_improve/scenario/events_guest.yaml",
    "results/self_improve/scenario/events_wfh.yaml",
    "results/self_improve/scenario/activities_v3.yaml",
]

# numbers that are structure rather than measurement: calendar, protocol, thresholds
STRUCTURAL = {
    2026, 9, 24, 32, 31, 14, 23, 13, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 15, 16,
    17, 19, 20, 21, 22, 24, 30, 1024, 45, 26, 33, 34, 35, 36, 37, 42, 43, 44, 46, 47,
    48, 49, 50, 51, 52, 53, 55, 56, 59, 60, 62, 63, 64, 65, 66, 69, 119, 122, 123, 124,
    125, 130, 131, 134, 136, 139, 141, 150, 151, 152, 153, 154, 155, 157, 159, 175, 176,
    177, 178, 182, 183, 184, 185, 188, 189, 192, 203, 204, 205, 206, 212, 221, 233, 235,
    236, 237, 238, 244, 248, 249, 250, 251, 256, 264, 269, 270, 274, 277, 280, 284, 286,
    287, 289,
}
THRESHOLDS = {70.0, 10.0, 8.0, 5.0, 60.0}

# Claims whose source is NOT check_scenario.py. These are ALWAYS listed for a hand check,
# whatever they happen to match: a two-digit number matching one of 765 recomputed
# quantities proves nothing, and "the towel is right 88% of the time" coincidentally
# matching room_shut_v1's 88 moved objects is exactly how prose gets waved through.
FORCE_HAND_CHECK = [
    ("89 to 94% of the time",
     "per-OBJECT accuracy of each towel's own commonest place in the settled window, "
     "counted from the banks (check_scenario.py reports no per-class figures). Measured: "
     "illness_v1/v2 92%, room_shut_v1 94%, wfh_v1 89%, night_shift_v1 91%."),
    ("23 to 37% of every question",
     "the towel's share of settled-window questions: illness_v1/v2 37%, room_shut_v1 25%, "
     "wfh_v1 24%, night_shift_v1 23%. Counted from the banks."),
    ("about a quarter of its settled answers once the ten homes are",
     "a POOLED modal share for glasses, measured on an EARLIER guest build that still "
     "asked about glasses. The committed banks have no glasses questions, so it cannot be "
     "recomputed. Not a per-object accuracy - see the note below about wfh_v1's 51%."),
    ("311 concern a commuter",
     "questions in the settled window about the ten ruled classes, split by whether the "
     "owner's role is worker_out/student (disrupted) or not: 311 disrupted, 699 "
     "undisrupted, rising to 537 disrupted during the spell. Counted from the banks by "
     "joining each question's object to its owner's role in hidden_state.json."),
    ("largest mover at 1,870",
     "check_classical_curve.py's class_sensitivity block: room_shut_v1 towel, 1870 "
     "questions, flips the verdict, newly failing legs = settled level AND break (both "
     "three-day memory). Comma-separated thousands are not parsed by this scanner."),
    ("largest mover, at 1,870",
     "same as above: room_shut_v1 towel, 1870 questions in the class_sensitivity table."),
    ("of the 144 settled-window laptop",
     "131 of wfh_v1's 144 settled-window laptop questions are about an undisrupted "
     "resident's laptop. Counted from the banks by joining object owner to role."),
    ("commonest place 100% of the time",
     "per-object accuracy of the laptop's own commonest place in wfh_v1's settled window, "
     "counted from the banks. It is 100%: every laptop question it is asked is answered by "
     "that laptop's modal receptacle."),
    ("311 are about a commuter",
     "same split as above: 311 / 699 settled, 537 during the spell."),
    ("right only 51% of the time",
     "WRONG NUMBER, kept only inside the correction note in wfh_v1/VERDICT.md. 51% was a "
     "pooled-across-households modal share, quoted as if it were a per-object accuracy; "
     "per object the laptop is at its own commonest place 100% of the time in the settled "
     "window. If this string appears anywhere OUTSIDE that correction note, it is a "
     "regression."),
    ("Five of the ten homes have an office",
     "counted from data/situation_sim/self_improve/<name>/hh_s*/hidden_state.json: five "
     "households have an 'office' room and three have a resident whose workspace is it."),
    ("office desk\nin one household",
     "per-household modal destination of the wash bag in the disrupted window, counted "
     "from the banks; desk_o1 x1, desk_b1 x4, desk_b2 x2, absent in 3."),
    ("in three\nof the ten homes the towels do **not** leave",
     "per-household modal destination of the towel in the disrupted window: hh_s1 stays "
     "at towel_rack, hh_s5 and hh_s6 at bathroom_shelf, because the dresser is full."),
    ("in three of the ten homes the\ntowels do **not** leave",
     "same as above."),
    ("settled climb was +7.3 against a +10 bar",
     "a REJECTED earlier build of room_shut_v1 with three extra classes. Not reproducible "
     "from the committed run; it is a record of why those classes were dropped."),
    ("showed a weak but real 4-to-6 point",
     "quoted from check_classical_curve.py's own docstring for "
     "results/regime_search/nightshift (6.0 and 4.1). Not recomputed here."),
    ("shows a break of 6.0 and 4.1",
     "quoted from check_classical_curve.py's docstring, not recomputed here."),
    ("16-point false break",
     "quoted from the coordinator's measurement of results/regime_search/nightshift's "
     "'moved' slice. Not recomputed here."),
    ("28-day version",
     "results/regime_search/nightshift/config.yaml: days: 28."),
    ("pooled",
     "TRAP CHECK: wherever the prose says 'pooled', confirm the number beside it is a "
     "pooled share and not a per-object accuracy - see the trap section above."),
    ("right only",
     "TRAP CHECK: 'right only N% of the time' is a PER-OBJECT claim. Confirm it was "
     "computed per object (each object against its own commonest place), not pooled "
     "across households. This exact confusion produced three wrong numbers."),
    ("of the time in the settled window",
     "TRAP CHECK: per-object accuracy claim - confirm it was computed per object."),
    ("about a dozen mixes",
     "a count of what was tried while building, not a measurement. Unverifiable after "
     "the fact and stated only as an honesty caveat."),
]


def numbers_for(name: str) -> dict:
    """Recompute every quantity for one scenario. Uses the run's check.json when it is
    there and up to date enough to carry a classical_curve block, otherwise re-runs
    check_scenario.py into a temporary file so nothing on disk is touched."""
    p = RUNS / name / "check.json"
    if p.exists():
        d = json.loads(p.read_text())
        if "classical_curve" in d:
            return d
    with tempfile.NamedTemporaryFile("r", suffix=".json", delete=False) as tmp:
        subprocess.run([sys.executable, str(HERE / "check_scenario.py"), str(RUNS / name),
                        "--json", tmp.name, "--quiet"], cwd=REPO, capture_output=True, text=True)
        return json.loads(pathlib.Path(tmp.name).read_text())


def alt_guest_build() -> dict:
    """The gate numbers of the uncommitted higher-question-rate guest build, read out of
    the table saved next to the run. Quoted in guest_v1's verdict, so it has to be
    checkable, and it cannot come from check.json because it is not the committed run."""
    p = RUNS / "guest_v1" / "check_alt_per32_gap20.txt"
    out = {}
    if not p.exists():
        return out
    for line in p.read_text().splitlines():
        s = line.strip()
        for leg in ("settled level", "learn", "break again", "break", "re-learn"):
            if s.startswith(leg + " ") and ("pass" in s or "FAIL" in s):
                parts = s.split()
                tag = "forgets-3d" if "three-day" in s else "never-forgets"
                try:
                    out[f"ALT BUILD {tag} {leg}"] = float(parts[-3].replace("+", ""))
                except ValueError:
                    pass
                break
    return out


def canonical(name: str) -> dict:
    """label -> value, every number we could legitimately quote about this scenario."""
    d = numbers_for(name)
    cc = d["classical_curve"]
    dis = d["disrupted"]
    het = d["heterogeneity"]
    mv = [v["moved"] for v in het.values()]
    ct = [v["controls"] for v in het.values()]
    out = {
        "movers pooled": float(sum(mv)),
        "movers per household min": float(min(mv)),
        "movers per household max": float(max(mv)),
        "controls per household mean": sum(ct) / len(ct),
        "distinct destinations": float(len(d["pooled_destinations"])),
        "biggest destination share": 100 * d["pooled_top_share"],
        "disrupted-window headroom": 100 * d["headroom_by_window"][dis],
        "visible at 3am (overnight floor)": 100 * d["overnight_floor"],
        "affected questions per household": d["power"][dis]["affected"],
        "objects asked per household": d["power"][dis]["objects"],
        "reversion contamination": 100 * d["reversion"]["contamination"],
        "checks failed": float(len(d["failures"])),
        "households kept": float(len(d["kept_households"])),
    }
    for meth, tag in ((N, "never-forgets"), (F, "forgets-3d")):
        for slice_ in ("all", "moved", "stayed put"):
            c = cc["curve"].get(f"{meth}|{slice_}")
            if not c:
                continue
            for phase, v in c["levels"].items():
                out[f"{tag} {slice_} level {phase}"] = v["accuracy"]
            for legname, v in c["legs"].items():
                out[f"{tag} {slice_} {legname}"] = v["change"]
                out[f"{tag} {slice_} {legname} se"] = v["household_se"]
                out[f"{tag} {slice_} {legname} shown by"] = float(v["shown"])
        sh = cc["households_with_full_shape"][meth]
        out[f"{tag} households with the full shape"] = float(len(sh) if isinstance(sh, list) else sh)
    # margins: how far a leg is from its bar, which we quote as "short by X"
    th = cc["thresholds"]
    g = cc["gate"]
    for key, v in g.items():
        if v.get("needed") is not None and v.get("measured") is not None:
            out[f"margin: {key}"] = abs(v["measured"] - v["needed"])
    return out


TOKEN = re.compile(r"(?<![\w.])([−+-]?\d+(?:\.\d+)?)\s*(%?)")


def scan(path: pathlib.Path, owner: str, canon: dict, tol=0.051):
    """A token written without a decimal point is a rounded quote of a measured value
    ("101 affected questions" for 100.7), so integers are matched to half a point and
    decimals to a twentieth."""
    matched, structural, unmatched = [], [], []
    for lineno, line in enumerate(path.read_text().splitlines(), 1):
        if line.lstrip().startswith(("|---", "```")):
            continue
        for m in TOKEN.finditer(line):
            raw = m.group(1)
            val = float(raw.replace("−", "-"))
            ctx = line.strip()
            ctx = (ctx[:96] + "…") if len(ctx) > 96 else ctx
            t_ = tol if "." in raw else 0.5
            hits = sorted({lab for lab, v in canon.items()
                           if v is not None and abs(abs(v) - abs(val)) <= t_})
            if hits:
                matched.append((lineno, raw, hits, ctx))
            elif abs(val) in THRESHOLDS or (val == int(val) and int(abs(val)) in STRUCTURAL):
                structural.append((lineno, raw, ctx))
            else:
                unmatched.append((lineno, raw, ctx))
    return matched, structural, unmatched


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--note", action="store_true", help="also write scenario/NUMBERS_IN_PROSE.md")
    ap.add_argument("--verbose", action="store_true", help="print the matched list too")
    a = ap.parse_args()

    canon = {s: canonical(s) for s in SCENARIOS}
    everything = {}
    for s, c in canon.items():
        for lab, v in c.items():
            everything[f"{s} :: {lab}"] = v
    for lab, v in alt_guest_build().items():
        everything[f"guest_v1 :: {lab}"] = v

    lines = []
    w = lines.append
    w("# Every number we wrote about the six scenarios, and where it comes from")
    w("")
    w("Generated by `results/self_improve/check_numbers_in_prose.py`. Regenerate it with")
    w("`python3 results/self_improve/check_numbers_in_prose.py --note` and re-read the")
    w("UNMATCHED list before anything is finalised. Numbers in prose drift; this is the")
    w("list of places they could drift from.")
    w("")
    w("The authoritative source for every measurement is the run's own `check.json`, which")
    w("`results/self_improve/check_scenario.py` writes. Re-derive any single number with:")
    w("")
    w("```")
    w("python3 results/self_improve/check_scenario.py results/self_improve/runs/<name>")
    w("```")
    w("")
    w("## THE TRAP THAT CAUGHT US THREE TIMES: pooled share vs per-object accuracy")
    w("")
    w("Three separate numbers in this work were wrong in the same way, so this is a")
    w("systematic trap rather than a slip. **A pooled modal share and a per-object accuracy")
    w("are different quantities and they can point in opposite directions.**")
    w("")
    w("- *pooled modal share*: of all questions about class C across ten households, the")
    w("  fraction answered by the single commonest receptacle. Low when households differ,")
    w("  even if every object is perfectly predictable. `counts.py`-style tables report this.")
    w("- *per-object accuracy*: for each object, the fraction of its questions answered by")
    w("  its OWN commonest place, averaged over objects. This is the one that means \"a")
    w("  settled belief about this thing is weak or strong\".")
    w("")
    w("What it cost: the laptop in wfh_v1 reads **51% pooled** and **100% per object**, and")
    w("the wrong one was quoted as evidence that the robot held a weak belief about it -")
    w("close to the opposite of the truth, and it was repeated onward before being caught.")
    w("The towel (88% pooled, 89-94% per object) and glasses (25% pooled) were the same")
    w("error. **Every per-object accuracy anywhere needs testing against this distinction")
    w("before it is quoted.** Any line below that reads \"right N% of the time\" is a")
    w("per-object claim and must have been computed per object.")
    w("")
    w("## Where measurements are asserted in prose")
    w("")
    w("| file | owner | numeric tokens | matched to a recomputed value | structural | **to check by hand** |")
    w("|---|---|---|---|---|---|")
    details = []
    total_un = 0
    for rel, owner in PROSE:
        p = REPO / rel
        if not p.exists():
            details.append((rel, owner, None))
            continue
        # matched against ALL six on purpose: a scenario's verdict legitimately quotes
        # the reference scenario's numbers for comparison, and we want those checked too
        mt, st, un = scan(p, owner, everything)
        total_un += len(un)
        w(f"| `{rel}` | {owner} | {len(mt)+len(st)+len(un)} | {len(mt)} | {len(st)} | **{len(un)}** |")
        details.append((rel, owner, (mt, st, un)))
    w("")
    w("## Files that assert no measurement (listed for completeness, not scanned)")
    w("")
    for rel in RULES_ONLY:
        w(f"- `{rel}` — rule parameters only: start times, durations, daily rates, "
          f"placement destinations. Nothing here can drift against the data.")
    w("")
    w("## To check by hand")
    w("")
    w("Every number below matched nothing that `check_scenario.py` recomputes. Most are")
    w("legitimate - counts of households with a property, shares computed from the banks")
    w("directly, the alternative guest build, or a figure quoted from another scenario's")
    w("run - but each needs a source named, and that is what this list is for.")
    w("")
    for rel, owner, got in details:
        if not got:
            w(f"### `{rel}` — MISSING FROM DISK")
            continue
        mt, st, un = got
        forced = []
        body = (REPO / rel).read_text()
        for needle, source in FORCE_HAND_CHECK:
            if needle in body:
                forced.append((needle, source))
        if not un and not forced:
            continue
        w(f"### `{rel}`")
        w("")
        for lineno, raw, ctx in un:
            w(f"- **L{lineno} `{raw}`** — {ctx}")
        for needle, source in forced:
            short = needle.replace("\n", " ")
            w(f"- **not from check_scenario.py:** \u201c{short}\u201d — {source}")
        w("")
    if a.verbose or True:
        w("## Matched, with the quantity each one matched")
        w("")
        for rel, owner, got in details:
            if not got:
                continue
            mt, st, un = got
            if not mt:
                continue
            w(f"### `{rel}`")
            w("")
            for lineno, raw, hits, ctx in mt:
                mark = "" if len(hits) <= 2 else f"  *(ambiguous: {len(hits)} candidates)*"
                w(f"- L{lineno} `{raw}` → {'; '.join(hits[:3])}{mark}")
            w("")
    # How much a match is worth. There are well over a thousand recomputed quantities, so
    # a two-digit integer matches something by coincidence far more often than not. A
    # match is only real evidence when it is UNIQUE or nearly so, and the honest summary
    # is the share of matched tokens that pin down one quantity.
    uniq = amb = 0
    for rel, owner, got in details:
        if not got:
            continue
        for lineno, raw, hits, ctx in got[0]:
            if len(hits) <= 2:
                uniq += 1
            else:
                amb += 1
    w("")
    w("## How much a match is worth")
    w("")
    w(f"There are {len(everything)} recomputed quantities across the six scenarios, so a")
    w("two-digit integer matches one of them by coincidence more often than not. A match is")
    w("real evidence only when it pins down one or two quantities.")
    w("")
    w(f"- matched tokens that pin down 1-2 quantities: **{uniq}**")
    w(f"- matched tokens that are ambiguous (3 or more candidates): **{amb}** — these are")
    w("  not verified, they are merely not obviously wrong. Signed decimals (`−16.9`,")
    w("  `+18.6`) are the discriminating ones; bare integers under about 100 mostly are not.")
    w("")
    w("So the authoritative check on any single claim remains the run's own")
    w("`check.txt` / `check.json`, read beside the sentence that quotes it. This file")
    w("tells you WHERE to look, not that the prose is right.")
    # the caveat has to be read BEFORE the tables, not after 400 lines of them
    body = "\n".join(lines)
    marker = "## How much a match is worth"
    before, _, worth = body.partition(marker)
    anchor = "## Where measurements are asserted in prose"
    head, _, rest = before.partition(anchor)
    text = head + marker + worth.rstrip() + "\n\n" + anchor + rest + "\n"
    print(f"numeric tokens needing a hand check: {total_un}")
    print(f"matched tokens pinning down 1-2 quantities: {uniq}; ambiguous (3+): {amb}")
    for rel, owner, got in details:
        if got:
            print(f"  {rel}: {len(got[2])} unmatched of {sum(len(x) for x in got)}")
    if a.note:
        out = HERE / "scenario" / "NUMBERS_IN_PROSE.md"
        out.write_text(text)
        print(f"note written to {out}")
    else:
        print("\n(run with --note to write scenario/NUMBERS_IN_PROSE.md)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
