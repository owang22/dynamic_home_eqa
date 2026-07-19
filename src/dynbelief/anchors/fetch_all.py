"""Anchor 1-4 acquisition (idempotent). Anchor 5 is human-transcribed.

Clones the four GitHub-family anchor repos into third_party/ (shallow,
read-only) and prepares data/anchors/<name>/raw/ landing dirs. ATUS lives on
bls.gov, which is NOT reachable from the build environment; this script
checks data/anchors/atus/raw/ for manually placed zips and, if absent, prints
the exact NEEDS_DATA instruction and continues (never fails the whole run).

Run:  python -m dynbelief.anchors.fetch_all [--depth N]

Idempotent: existing clones are `git -C <dir> pull --ff-only` (or skipped if
offline); existing raw dirs are left untouched. Everything it writes is under
third_party/ and data/anchors/, both gitignored.
"""
from __future__ import annotations

import argparse
import pathlib
import subprocess
import sys

from dynamic_home_eqa.paths import REPO_ROOT  # single source of truth for paths

THIRD_PARTY = REPO_ROOT / "third_party"
DATA_ANCHORS = REPO_ROOT / "data" / "anchors"

# Anchors 2-4: GitHub-family, clonable. name -> (url, reuse_if_present)
GIT_ANCHORS = {
    "HOMER_PLUS":  "https://github.com/Maithili/HOMER_PLUS",
    "bddl":        "https://github.com/StanfordVL/bddl",
    "housekeep":   "https://github.com/yashkant/housekeep",
    "parsec":      "https://github.com/kartikvrama/parsec",
}
# An earlier phase may have cloned P&C22's tracker; reuse it as a HOMER+ source.
REUSE_HINTS = {
    "HOMER_PLUS": ["SpatioTemporalObjectTracking"],
}

ATUS_FILES = [
    "atusact_2003-2023.zip   (Activity file: activity codes + start/stop times)",
    "atusresp_2003-2023.zip  (Respondent file: labor-force status for the FT-employed filter)",
    "ATUS activity coding lexicon (code -> description), from the same page",
]
ATUS_URL = "https://www.bls.gov/tus/data.htm"


def _run(cmd: list[str]) -> tuple[int, str]:
    p = subprocess.run(cmd, capture_output=True, text=True)
    return p.returncode, (p.stdout + p.stderr).strip()


def clone_or_update(name: str, url: str, depth: int) -> str:
    dest = THIRD_PARTY / name
    # reuse an existing sibling checkout if the brief flagged one
    for hint in REUSE_HINTS.get(name, []):
        cand = THIRD_PARTY / hint
        if cand.exists() and not dest.exists():
            return f"REUSE {name}: found existing {cand.name} (link/inspect manually)"
    if dest.exists():
        rc, out = _run(["git", "-C", str(dest), "pull", "--ff-only"])
        return f"UPDATE {name}: {'ok' if rc == 0 else 'skipped (offline?) ' + out.splitlines()[-1] if out else 'ok'}"
    THIRD_PARTY.mkdir(parents=True, exist_ok=True)
    rc, out = _run(["git", "clone", "--depth", str(depth), url, str(dest)])
    if rc != 0:
        return f"FAIL  {name}: clone error -> {out.splitlines()[-1] if out else '?'}"
    return f"CLONE {name}: {url} -> third_party/{name}"


def ensure_atus() -> str:
    raw = DATA_ANCHORS / "atus" / "raw"
    raw.mkdir(parents=True, exist_ok=True)
    zips = list(raw.glob("*.zip"))
    if zips:
        return f"ATUS: found {len(zips)} zip(s) in {raw.relative_to(REPO_ROOT)} -> OK"
    lines = [
        "ATUS: NEEDS_DATA — bls.gov is not reachable from this environment.",
        f"      Download these from {ATUS_URL} (free, no registration) and place in:",
        f"        {raw}",
        *(f"        - {f}" for f in ATUS_FILES),
        "      Then re-run fetch_all + compile_envelope. Until present, V6a (schedule",
        "      timing) reports NEEDS_DATA and is non-gating.",
    ]
    return "\n".join(lines)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--depth", type=int, default=1, help="git clone depth (0 = full)")
    args = ap.parse_args(argv)
    depth = args.depth or 1000000

    print(f"[fetch_all] third_party = {THIRD_PARTY}")
    print(f"[fetch_all] data/anchors = {DATA_ANCHORS}\n")
    for name, url in GIT_ANCHORS.items():
        print(" ", clone_or_update(name, url, depth))
        (DATA_ANCHORS / name.lower() / "raw").mkdir(parents=True, exist_ok=True)
    print()
    print(ensure_atus())
    print("\n[fetch_all] done. Next: python -m dynbelief.anchors.compile_envelope")
    return 0


if __name__ == "__main__":
    sys.exit(main())
