"""Add OracleBelief (sweep-selected config) to the existing
household_analysis cells without recomputing the other models.

Runs household_analysis for the single oracle_program_posterior spec
(config from results/oracle_program_posterior/selected.json) over every
fleet bank, then merges the new cells into
reports/baselines/household_analysis/cells.csv.gz. Per-model results are
independent (the rng is derived per spec name), so the merge equals a
joint run. Idempotent: existing OracleBelief rows are dropped first.

Usage:
  python scratch_runs/oracle_v2/add_oracle_to_household_analysis.py \
      [--households hh_001] [--seeds 0] [--workers 8] [--dry-run]
"""
from __future__ import annotations

import argparse
import csv
import datetime
import gzip
import json
import pathlib
import shutil
import sys

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "src"))

from baselines.household_analysis import COLUMNS, SEEDS, run_analysis  # noqa: E402

REPORT_DIR = REPO_ROOT / "reports" / "baselines" / "household_analysis"
SELECTED = REPO_ROOT / "results" / "oracle_program_posterior" / "selected.json"
TMP_DIR = REPO_ROOT / "scratch_runs" / "oracle_v2" / "household_analysis_oracle"


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--households", nargs="*", default=None)
    ap.add_argument("--seeds", type=int, nargs="*", default=list(SEEDS))
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--dry-run", action="store_true",
                    help="run the analysis into the temp dir, skip the merge")
    args = ap.parse_args()

    cfg = json.loads(SELECTED.read_text())
    spec = {"name": "oracle_program_posterior", "eps": cfg["eps"],
            "half_life_h": cfg["half_life_h"]}
    print(f"OracleBelief spec: {spec}")

    run_analysis(households=args.households, seeds=args.seeds, specs=[spec],
                 oracle_seeds=0, rng_seed=0, workers=args.workers,
                 out_dir=TMP_DIR)
    if args.dry_run:
        return

    new_rows = _load(TMP_DIR / "cells.csv.gz")
    oracle_models = {r[2] for r in new_rows}
    print(f"new rows: {len(new_rows)} for models {sorted(oracle_models)}")
    old_rows = _load(REPORT_DIR / "cells.csv.gz")
    kept = [r for r in old_rows if r[2] not in oracle_models]
    dropped = len(old_rows) - len(kept)
    if dropped:
        print(f"dropped {dropped} stale OracleBelief rows")

    backup = REPORT_DIR / "cells.csv.gz.bak"
    shutil.copy2(REPORT_DIR / "cells.csv.gz", backup)
    with gzip.open(REPORT_DIR / "cells.csv.gz", "wt", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(COLUMNS)
        w.writerows(kept + new_rows)

    prov = json.loads((REPORT_DIR / "provenance.json").read_text())
    prov["models"] = [m for m in prov["models"]
                      if m != "oracle_program_posterior"] + [
                      "oracle_program_posterior"]
    prov["n_cells"] = len(kept) + len(new_rows)
    prov["oracle_belief_merge"] = {
        "spec": spec,
        "merged_at": datetime.datetime.now(
            datetime.timezone.utc).isoformat(),
        "source": str(TMP_DIR),
        "selected_json": str(SELECTED),
    }
    (REPORT_DIR / "provenance.json").write_text(json.dumps(prov, indent=2))
    print(f"merged -> {REPORT_DIR / 'cells.csv.gz'} "
          f"({prov['n_cells']} cells); backup at {backup}")


def _load(path: pathlib.Path):
    with gzip.open(path, "rt") as fh:
        reader = csv.reader(fh)
        header = next(reader)
        assert tuple(header) == COLUMNS, header
        return list(reader)


if __name__ == "__main__":
    main()
