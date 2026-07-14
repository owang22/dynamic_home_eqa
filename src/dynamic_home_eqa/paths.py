"""
paths.py — single source of truth for repo-layout paths.

PACKAGE_ROOT is the dynamic_home_eqa package directory (src/dynamic_home_eqa).
REPO_ROOT is the repo checkout (two levels up), where all data and output
directories live. Every module that needs a data/output path imports from
here instead of computing its own __file__-relative anchor, so outputs land
in the repo regardless of the caller's working directory.

External inputs that live outside the repo (HSSD scenes, conda envs) are
env-var overridable; defaults are this machine's layout.
"""
from __future__ import annotations

import os
import pathlib

PACKAGE_ROOT = pathlib.Path(__file__).resolve().parent  # .../src/dynamic_home_eqa
REPO_ROOT = pathlib.Path(
    os.environ.get("DYNAMIC_HOME_EQA_ROOT", str(PACKAGE_ROOT.parent.parent))
).resolve()

# Data inputs (tracked or machine-local, under the repo)
DATA_DIR = REPO_ROOT / "data"
ANCHOR_ADMISSION_MAPS = DATA_DIR / "anchor_admission_maps"
ANCHOR_CENSUS_DIR = DATA_DIR / "anchor_census"
SENSABILITY_MAPS = DATA_DIR / "sensability_maps"
REALIZED_DAYS_DIR = DATA_DIR / "realized_days"
EXTERNAL_PROPS_DIR = DATA_DIR / "objects" / "external_props"

# Pipeline / experiment outputs
GENERATION_OUT = REPO_ROOT / "generation_out"
EMBODIED_RESULTS = REPO_ROOT / "embodied_results"
RESULTS_DIR = REPO_ROOT / "results"
REPORTS_DIR = RESULTS_DIR / "reports"
E1E4_RESULTS = RESULTS_DIR / "e1e4"
DIAGNOSTICS_DIR = RESULTS_DIR / "diagnostics"
LLM_PRIOR_CACHE = REPO_ROOT / "llm_prior_cache"

# Superseded/stale outputs live here, untracked (see .gitignore)
ARCHIVE_DIR = REPO_ROOT / "archive"

# External inputs outside the repo
# (the old /mnt/nvme/oliver/... locations are gone from this machine — HSSD
# now lives under the EXPRESS-Bench checkout and models in the shared HF
# cache on /data; both still env-var overridable as before)
HSSD_DIR = pathlib.Path(
    os.environ.get(
        "HSSD_DIR", "/data/oliver/robot/EXPRESS-Bench/data/versioned_data/hssd-hab"
    )
)
# HF model cache used as HF_HOME by llm_prior and serve_llm (large-model
# downloads land on the big /data array, not the default ~/.cache).
MODEL_CACHE_DIR = os.environ.get("DYNAMIC_EQA_HF_HOME", "/data/oliver/huggingface_cache")
