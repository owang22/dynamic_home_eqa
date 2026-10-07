#!/usr/bin/env python3
"""First guess right in the two return windows of the 50-day second-illness run, from the
answer files already on disk. No model is run.

    cd /home/oliver/robot/dynamic_home_eqa
    PYTHONPATH=src python3 coordination/study1_from_existing_runs.py

What it reads
  results/self_improve/wave_the_second_illness/cells/<method>/<household>/searches.jsonl
  results/self_improve/wave_the_second_illness_ACE_fixed/cells/ACE_as_published/<household>/searches.jsonl
  results/self_improve/wave_the_second_illness_ACE_rerun/cells/ACE_as_published/<household>/searches.jsonl
  results/self_improve/wave_last_seen_no_first_illness/cells/last_seen_no_model/<household>/searches.jsonl
  results/self_improve/varied_homes/all_generated_v2_twice/banks/<household>.jsonl   (for the mover sets)

How it scores
  "first guess right" is `found_at_step == 1` on a `kind == "search"` row, exactly as
  results/self_improve/paper/scripts/paper_data.py:share(..., "first") does, and as
  questions_answered.md section 6 says (searches only ever open rooms, so it is room level).
  The denominator is every search row in the window; `found_at_step` is always filled
  (questions_answered.md section 13), so nothing is dropped.

Object slices
  all           every question
  spell-1 mover `is_a_mover` on the row: search_driven.the_movers, fixed once per run from days
                14-23 at spot level (questions_answered.md sections 4 and 14)
  both-spell    paper_data.both_spell_movers: commonest daytime ROOM differs from settled in both
                illnesses (14 objects over the three homes)
  A per-question "moved since the method last saw it" slice is NOT exposed by the scoring code.
"""
import collections
import json
import pathlib
import statistics
import sys

ROOT = pathlib.Path("/home/oliver/robot/dynamic_home_eqa")
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "results/self_improve/paper/scripts"))
import paper_data as D  # noqa: E402

WAVES = {
    "original": ROOT / "results/self_improve/wave_the_second_illness/cells",
    "ACE_fixed": ROOT / "results/self_improve/wave_the_second_illness_ACE_fixed/cells",
    "ACE_rerun": ROOT / "results/self_improve/wave_the_second_illness_ACE_rerun/cells",
}
WAVE_LS_NO_FIRST = ROOT / "results/self_improve/wave_last_seen_no_first_illness/cells"
HOMES = list(D.HOMES_50)
WINDOWS = {"days 24-28": range(24, 29), "days 42-46": range(42, 47)}
BASELINE = "last_seen_no_model"

# Every method the task asked about, whether or not it is in the run.
ASKED_FOR = ["last_seen_no_model", "prior_only_no_notes", "the_log_and_notes_about_the_routine",
             "claim_store_told_if_it_was_right", "a_small_working_memory_and_an_archive",
             "incremental_edits", "ACE_as_published", "ours_told_the_night_before",
             "log_only", "the_log_only"]


def load(wave_dir, method, home):
    f = wave_dir / method / home / "searches.jsonl"
    if not f.exists():
        return None, f"missing: {f.relative_to(ROOT)}"
    rows = []
    try:
        for line in f.open():
            if line.strip():
                r = json.loads(line)
                if r.get("kind") == "search":
                    rows.append(r)
    except (json.JSONDecodeError, OSError) as e:
        return None, f"unreadable: {f.relative_to(ROOT)} ({e})"
    return rows, None


def first_right(rows):
    return sum(1 for r in rows if r.get("found_at_step") == 1)


def main():
    out = []
    p = out.append

    # ---- which cells exist
    cells = {}          # (label) -> {home: rows}
    notes = []
    present = sorted(d.name for d in WAVES["original"].iterdir() if d.is_dir())
    p(f"cell directories in wave_the_second_illness/cells: {present}")
    for m in ASKED_FOR:
        if m not in present and not (m == "ACE_as_published"):
            notes.append(f"{m}: not in the 50-day run (no cell directory)")
    for m in present:
        cells[m] = {}
        for h in HOMES:
            rows, err = load(WAVES["original"], m, h)
            if err:
                notes.append(err)
            else:
                cells[m][h] = rows
    for tag in ("ACE_fixed", "ACE_rerun"):
        label = f"ACE_as_published [{tag}]"
        cells[label] = {}
        for h in HOMES:
            rows, err = load(WAVES[tag], "ACE_as_published", h)
            if err:
                notes.append(err)
                continue
            days = {r["day"] for r in rows}
            if not all(d in days for w in WINDOWS.values() for d in w):
                notes.append(f"{label} {h}: incomplete, days {min(days)}-{max(days)} only "
                             f"({len(rows)} questions); it does not reach the return windows "
                             f"and is left out")
                continue
            # A rerun that replays the original row for row is not a second observation.
            orig = cells.get("ACE_as_published", {}).get(h)
            if orig is not None and len(orig) == len(rows) and all(
                    a.get("rooms_opened") == b.get("rooms_opened")
                    and a.get("found_at_step") == b.get("found_at_step")
                    for a, b in zip(orig, rows)):
                notes.append(f"{label} {h}: identical to the original ACE_as_published cell on "
                             f"all {len(rows)} rows (rooms opened and found_at_step), a cache "
                             f"replay; left out of the tables")
                continue
            cells[label][h] = rows
        if not cells[label]:
            del cells[label]

    # last-seen with the first illness deleted from its trail: same bank, same questions, no
    # model (results/self_improve/paper/scripts/last_seen_without_the_first_illness.py)
    label = "last_seen_no_model [first illness deleted]"
    cells[label] = {}
    for h in HOMES:
        rows, err = load(WAVE_LS_NO_FIRST, "last_seen_no_model", h)
        if err:
            notes.append(err)
        else:
            cells[label][h] = rows
    if not cells[label]:
        del cells[label]

    # ---- the question schedule is the same for every arm within a home (check, do not assume)
    for h in HOMES:
        ids = None
        for label, by_home in cells.items():
            if h not in by_home:
                continue
            these = [(r["day"], r["question_id"]) for r in by_home[h]]
            if ids is None:
                ids = these
            elif these != ids:
                notes.append(f"question schedule differs between arms in {h}: {label}")

    movers_both = {h: D.both_spell_movers(h) for h in HOMES}

    def window_rows(rows, home, window, slice_name):
        rs = [r for r in rows if r["day"] in window]
        if slice_name == "spell-1 mover":
            rs = [r for r in rs if r.get("is_a_mover")]
        elif slice_name == "both-spell":
            rs = [r for r in rs if r["object_id"] in movers_both[home]]
        return rs

    # ---- per-cell, per-window counts
    SLICES = ("all", "spell-1 mover", "both-spell")
    counts = {}   # (label, home, window, slice) -> (right, n)
    for label, by_home in cells.items():
        for h, rows in by_home.items():
            for wname, w in list(WINDOWS.items()) + [("pooled", None)]:
                for s in SLICES:
                    if wname == "pooled":
                        rs = []
                        for w2 in WINDOWS.values():
                            rs += window_rows(rows, h, w2, s)
                    else:
                        rs = window_rows(rows, h, w, s)
                    counts[(label, h, wname, s)] = (first_right(rs), len(rs))

    labels = [l for l in cells if cells[l]]
    order = [BASELINE] + sorted(l for l in labels if l != BASELINE)

    p("")
    p("## Question counts per window per household (every arm asks the same questions)")
    p("")
    p("| household | slice | days 24-28 | days 42-46 | pooled |")
    p("|---|---|---|---|---|")
    for h in HOMES:
        for s in SLICES:
            row = [counts[(BASELINE, h, w, s)][1] for w in ("days 24-28", "days 42-46", "pooled")]
            p(f"| {h} | {s} | {row[0]} | {row[1]} | {row[2]} |")
    p("")
    p("Both-spell movers per home: " + "; ".join(
        f"{h}: {len(movers_both[h])} ({', '.join(sorted(movers_both[h]))})" for h in HOMES))
    p("Spell-1 movers per home (row field is_a_mover): " + "; ".join(
        f"{h}: {len({r['object_id'] for r in cells[BASELINE][h] if r.get('is_a_mover')})}"
        for h in HOMES))

    # ---- table 1: first guess right
    for s in SLICES:
        p("")
        p(f"## First guess right, percent (right/asked) - {s}")
        p("")
        p("| method | window | " + " | ".join(HOMES) + " | pooled over homes |")
        p("|---|---|" + "---|" * (len(HOMES) + 1))
        for label in order:
            for w in ("days 24-28", "days 42-46", "pooled"):
                cellstrs, R, N = [], 0, 0
                for h in HOMES:
                    if (label, h, w, s) in counts:
                        r, n = counts[(label, h, w, s)]
                        cellstrs.append(f"{100*r/n:.1f} ({r}/{n})" if n else "no questions")
                        R += r; N += n
                    else:
                        cellstrs.append("missing")
                pooled_str = f"{100*R/N:.1f} ({R}/{N})" if N else "-"
                p(f"| {label} | {w} | " + " | ".join(cellstrs) + f" | {pooled_str} |")

    # ---- table 2: paired differences
    def paired(label, ref, w, s):
        diffs = {}
        for h in HOMES:
            if (label, h, w, s) in counts and (ref, h, w, s) in counts:
                r1, n1 = counts[(label, h, w, s)]
                r0, n0 = counts[(ref, h, w, s)]
                if n1 and n0:
                    diffs[h] = 100 * (r1 / n1 - r0 / n0)
        vals = list(diffs.values())
        n = len(vals)
        mean = statistics.fmean(vals) if vals else None
        se = statistics.stdev(vals) / n ** 0.5 if n > 1 else None
        return diffs, mean, se, n

    # the best-performing arm on pooled/all, by pooled share across homes, is the second reference
    pooled_share = {}
    for label in order:
        R = sum(counts[(label, h, "pooled", "all")][0] for h in HOMES if (label, h, "pooled", "all") in counts)
        N = sum(counts[(label, h, "pooled", "all")][1] for h in HOMES if (label, h, "pooled", "all") in counts)
        pooled_share[label] = 100 * R / N if N else None
    best = max((l for l in order if pooled_share[l] is not None), key=lambda l: pooled_share[l])

    for ref, refname in ((BASELINE, "last_seen_no_model"), (best, f"the best arm on pooled first guess, {best}")):
        for s in SLICES:
            p("")
            p(f"## Paired per-household difference against {refname}, points of first guess right - {s}")
            p("")
            p("| method | window | " + " | ".join(HOMES) + " | mean | SE (n homes) | 2 SE | separated? |")
            p("|---|---|" + "---|" * (len(HOMES) + 4))
            for label in order:
                if label == ref:
                    continue
                for w in ("days 24-28", "days 42-46", "pooled"):
                    diffs, mean, se, n = paired(label, ref, w, s)
                    cellstrs = [f"{diffs[h]:+.1f}" if h in diffs else "missing" for h in HOMES]
                    if mean is None:
                        tail = "| - | - | - | no pairs |"
                    elif se is None:
                        tail = f"| {mean:+.1f} | - (n={n}) | - | one home only |"
                    else:
                        sep = "yes" if abs(mean) > 2 * se else "no"
                        tail = f"| {mean:+.1f} | {se:.1f} (n={n}) | {2*se:.1f} | {sep} |"
                    p(f"| {label} | {w} | " + " | ".join(cellstrs) + " " + tail)

    # ---- smallest detectable gap
    p("")
    p("## Smallest gap this setup separates (two standard errors of the paired difference, observed spread)")
    p("")
    p("| method vs last_seen_no_model | slice | 2 SE days 24-28 | 2 SE days 42-46 | 2 SE pooled |")
    p("|---|---|---|---|---|")
    for label in order:
        if label == BASELINE:
            continue
        for s in SLICES:
            vals = []
            for w in ("days 24-28", "days 42-46", "pooled"):
                _, mean, se, n = paired(label, BASELINE, w, s)
                vals.append(f"{2*se:.1f}" if se is not None else "-")
            p(f"| {label} | {s} | " + " | ".join(vals) + " |")

    p("")
    p("## Notes from the loader")
    for nline in notes:
        p(f"- {nline}")
    if not notes:
        p("- every expected file was present and readable")

    text = "\n".join(out)
    print(text)
    (ROOT / "coordination/study1_from_existing_runs.raw.md").write_text(text + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
