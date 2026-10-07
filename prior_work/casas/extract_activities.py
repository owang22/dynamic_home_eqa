#!/usr/bin/env python3
"""Extract labeled activity intervals from a raw CASAS free-living file.

CASAS raw format is one sensor event per line:

    2010-11-04 00:03:50.209589 M003 ON Sleeping begin
    2010-11-04 00:03:57.399391 M003 OFF
    2010-11-04 00:15:08.984841 T002 21.5

Activity annotations ("<Activity> begin" / "<Activity> end") ride on sensor
event lines. This keeps ONLY those annotations — every motion/door/
temperature reading is discarded — and pairs begin/end into intervals.

Pairing rules (CASAS annotation quirks handled explicitly, counted in the
summary rather than silently patched):
  * begin with no matching end before the next begin of the SAME activity:
    closed at the next begin (counted as `reopened`)
  * end with no open begin: dropped (counted as `orphan_end`)
  * intervals may overlap across activities (annotator labels can nest);
    they are kept as-is — downstream decides.

Output (to --out):
  activities.csv   start_iso, end_iso, day, t0_min, t1_min, activity
                   (day 0 = first calendar date; t in minutes from day 0
                   00:00, same clock the revamp_v1 timelines use)
  summary.json     vocabulary, counts, durations, anomaly counts

Usage:
  python extract_activities.py /path/to/aruba.txt --out aruba
"""

from __future__ import annotations

import argparse
import collections
import csv
import datetime as dt
import json
import pathlib


def parse(path: pathlib.Path):
    """Yield (datetime, activity, begin|end) from annotation-bearing lines."""
    with open(path) as f:
        for line in f:
            parts = line.split()
            if len(parts) < 6 or parts[-1] not in ("begin", "end"):
                continue
            stamp = f"{parts[0]} {parts[1]}"
            # fractional seconds are sometimes missing or short
            fmt = "%Y-%m-%d %H:%M:%S.%f" if "." in parts[1] else "%Y-%m-%d %H:%M:%S"
            when = dt.datetime.strptime(stamp, fmt)
            yield when, parts[-2], parts[-1]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("raw", type=pathlib.Path)
    ap.add_argument("--out", type=pathlib.Path, required=True)
    args = ap.parse_args()

    marks = list(parse(args.raw))
    assert marks, "no activity annotations found"
    day0 = marks[0][0].date()

    intervals = []
    open_at = {}                       # activity -> datetime it began
    anomalies = collections.Counter()
    for when, act, kind in marks:
        if kind == "begin":
            if act in open_at:         # unclosed previous begin: close it here
                intervals.append((open_at[act], when, act))
                anomalies["reopened"] += 1
            open_at[act] = when
        else:
            if act in open_at:
                intervals.append((open_at.pop(act), when, act))
            else:
                anomalies["orphan_end"] += 1
    for act, t0 in open_at.items():    # dangling opens at end of data
        anomalies["unclosed_at_eof"] += 1
    intervals.sort(key=lambda iv: iv[0])

    args.out.mkdir(parents=True, exist_ok=True)
    with open(args.out / "activities.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["start", "end", "day", "t0_min", "t1_min", "activity"])
        for t0, t1, act in intervals:
            base = dt.datetime.combine(day0, dt.time())
            m0 = (t0 - base).total_seconds() / 60
            m1 = (t1 - base).total_seconds() / 60
            w.writerow([t0.isoformat(sep=" ", timespec="seconds"),
                        t1.isoformat(sep=" ", timespec="seconds"),
                        int(m0 // 1440), round(m0, 2), round(m1, 2), act])

    durs = collections.defaultdict(list)
    for t0, t1, act in intervals:
        durs[act].append((t1 - t0).total_seconds() / 60)
    ndays = (intervals[-1][1].date() - day0).days + 1
    summary = {
        "source": args.raw.name,
        "day0": str(day0),
        "days_spanned": ndays,
        "n_intervals": len(intervals),
        "anomalies": dict(anomalies),
        "activities": {
            act: {"count": len(ds),
                  "per_day": round(len(ds) / ndays, 2),
                  "median_min": round(sorted(ds)[len(ds) // 2], 1),
                  "total_hours": round(sum(ds) / 60, 1)}
            for act, ds in sorted(durs.items(), key=lambda kv: -len(kv[1]))},
    }
    (args.out / "summary.json").write_text(json.dumps(summary, indent=2))
    print(f"{args.raw.name}: {len(intervals)} intervals over {ndays} days, "
          f"{len(durs)} activities, day0={day0}, anomalies={dict(anomalies)}")


if __name__ == "__main__":
    main()
