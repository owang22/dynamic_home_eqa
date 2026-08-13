"""Build the ICC table from both sources.

    python -m icc.cli build --out reports/icc

Writes ``icc_table.csv`` (one row per activity x measure) and
``provenance.json`` (input checksums, crosswalk version and hash, seeds,
row counts, drop reports, library versions). Every number that reaches a
figure or a paper should be traceable to these two files plus the seed.
"""

from __future__ import annotations

import argparse
import collections
import csv
import datetime
import hashlib
import json
import pathlib
import subprocess
import sys
from typing import Dict, List, Tuple

import numpy as np

from icc import crosswalk
from icc.estimate import MEASURES, Estimate, estimate
from icc.load_atus import iter_day_rows
from icc.load_casas import load as load_casas
from icc.schema import DropReport


def _sha256(path: pathlib.Path, limit: int = 1 << 24) -> str:
    """Checksum of an input file (first 16 MiB for the multi-GB extract, so
    provenance stays cheap; the length is recorded alongside)."""
    h = hashlib.sha256()
    read = 0
    with open(path, "rb") as f:
        while read < limit:
            chunk = f.read(min(1 << 20, limit - read))
            if not chunk:
                break
            h.update(chunk)
            read += len(chunk)
    return f"{h.hexdigest()[:16]}:{path.stat().st_size}"


def atus_arrays(seed: int, report: DropReport
                ) -> Tuple[Dict[Tuple[str, str], Tuple[np.ndarray, np.ndarray,
                                                       np.ndarray]], int]:
    """Stream ATUS once, accumulating per (activity, measure) arrays.

    Streaming rather than materializing: 1.9 M day rows as objects is
    gigabytes, and the estimator only needs (value, weight, regime).
    """
    acc: Dict[Tuple[str, str], Tuple[List[float], List[float], List[str]]] = \
        collections.defaultdict(lambda: ([], [], []))
    diaries = set()
    import math
    for r in iter_day_rows(seed=seed, report=report):
        if not r.valid_day:
            continue
        diaries.add(r.person_id)
        for measure in MEASURES:
            if measure == "participation":
                value = float(r.participated)
            elif not r.participated:
                continue
            elif measure == "start_min":
                value = r.start_min
            else:
                value = (math.log(r.duration_min)
                         if r.duration_min and r.duration_min > 0 else None)
            if value is None:
                continue
            v, w, d = acc[(r.activity, measure)]
            v.append(float(value))
            w.append(r.weight)
            d.append(r.dow_type)
    return ({k: (np.asarray(v), np.asarray(w), np.asarray(d))
             for k, (v, w, d) in acc.items()}, len(diaries))


SENSITIVITY_SHIFT = 0.15


def _write_sensitivity(out_dir: pathlib.Path, rows: List[Estimate]) -> None:
    """ICC shifted +/- 0.15 for downstream stability checks.

    The CASAS testbeds skew single-occupant and older than the ATUS
    population, so every ICC carries an unquantified bias of unknown sign.
    Rather than pretend a point estimate, downstream consumers should run
    with these shifted tables and show their conclusions do not turn on
    which column they used. Shifts are clipped to [0, 1]: an ICC is a
    variance ratio and cannot leave that interval.
    """
    with open(out_dir / "sensitivity.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["activity", "measure", "status", "icc",
                    f"icc_minus_{SENSITIVITY_SHIFT:g}",
                    f"icc_plus_{SENSITIVITY_SHIFT:g}"])
        for e in rows:
            if e.icc != e.icc:                     # NaN: nothing to shift
                w.writerow([e.activity, e.measure, e.status, "", "", ""])
                continue
            lo = min(max(e.icc - SENSITIVITY_SHIFT, 0.0), 1.0)
            hi = min(max(e.icc + SENSITIVITY_SHIFT, 0.0), 1.0)
            w.writerow([e.activity, e.measure, e.status,
                        f"{e.icc:.4f}", f"{lo:.4f}", f"{hi:.4f}"])


def build(out_dir: pathlib.Path, seed: int) -> List[Estimate]:
    casas_rows, casas_report = load_casas()
    atus_report = DropReport(source="atus")
    atus, n_diaries = atus_arrays(seed, atus_report)
    rng = np.random.default_rng(seed)

    rows: List[Estimate] = []
    for m in crosswalk.included():
        for measure in MEASURES:
            if measure == "start_min" and m.start_rule.value == "none":
                continue          # the crosswalk says a start time is not a
            if measure == "log_duration" and m.is_event:   # meaningful
                continue          # quantity for this activity
            rows.append(estimate(m.activity, measure, casas_rows, atus, rng))

    out_dir.mkdir(parents=True, exist_ok=True)
    _write_sensitivity(out_dir, rows)
    table = out_dir / "icc_table.csv"
    with open(table, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(Estimate.FIELDS)
        for e in rows:
            w.writerow([getattr(e, k) for k in Estimate.FIELDS])

    try:
        commit = subprocess.run(["git", "rev-parse", "HEAD"], check=True,
                                capture_output=True, text=True).stdout.strip()
        dirty = bool(subprocess.run(["git", "status", "--porcelain"],
                                    check=True, capture_output=True,
                                    text=True).stdout.strip())
    except (subprocess.CalledProcessError, FileNotFoundError):
        commit, dirty = "unknown", True
    import statsmodels
    import scipy
    provenance = {
        "generated": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "git_commit": commit, "git_dirty": dirty, "seed": seed,
        "crosswalk_version": crosswalk.version(),
        "crosswalk_sha256": crosswalk.content_hash(),
        "inputs": {
            "atus_extract": _sha256(pathlib.Path("atus/atus_00002.dat.gz")),
            **{f"casas_{t}": _sha256(pathlib.Path(f"casas/{t}/activities.csv"))
               for t in ("aruba", "cairo", "milan", "tulum2")},
        },
        "counts": {"casas_day_rows": len(casas_rows),
                   "atus_diaries_used": n_diaries},
        "drops": {"casas": casas_report.counts, "atus": atus_report.counts},
        "libraries": {"numpy": np.__version__, "scipy": scipy.__version__,
                      "statsmodels": statsmodels.__version__,
                      "python": sys.version.split()[0]},
        "icc_table_sha256": hashlib.sha256(table.read_bytes()).hexdigest()[:16],
    }
    (out_dir / "provenance.json").write_text(json.dumps(provenance, indent=2))
    print(casas_report.render())
    print(atus_report.render())
    print(f"\nwrote {table} and {out_dir / 'provenance.json'}")
    return rows


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("command", choices=["build"])
    ap.add_argument("--out", type=pathlib.Path,
                    default=pathlib.Path("reports/icc"))
    ap.add_argument("--seed", type=int, default=0)
    args = ap.parse_args()
    rows = build(args.out, args.seed)
    print(f"\n{'activity':<14}{'measure':<14}{'status':<20}"
          f"{'within':>10}{'total':>10}{'ICC':>8}{'95% CI':>18}{'phi':>7}")
    for e in rows:
        ci = (f"[{e.icc_lo:.2f},{e.icc_hi:.2f}]"
              if e.icc_lo == e.icc_lo else "—")
        print(f"{e.activity:<14}{e.measure:<14}{e.status:<20}"
              f"{e.sigma2_within:>10.1f}{e.sigma2_total:>10.1f}"
              f"{e.icc:>8.3f}{ci:>18}{e.phi_ar1:>7.2f}")


if __name__ == "__main__":
    main()
