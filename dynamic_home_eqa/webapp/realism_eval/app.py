"""
app.py — realism human-eval webapp.

Adapted from a reference time-series QA webapp (same FastAPI + SQLite-WAL
+ joint-quota-sampling architecture — see sampling.py's docstring), not
rewritten from scratch: item pool loading + static-file serving replace
the reference's HDF5/time-series machinery, but the assignment/response/
storage shape follows the same pattern (shared deterministic assignment,
composite-key upsert responses, a hidden debug box gated behind a
checkbox).

Standing rule this app exists to enforce: automatic signals (geometric
placement check, deterministic plausibility flags, LLM self-graded
realism) are correlation candidates ONLY — never shown to an annotator
while rating. They're included in each item payload only under a `debug`
key the frontend gates behind an opt-in "show debug info" checkbox,
exactly mirroring the reference app's own debug box.

Standing rules for serving: binds to 127.0.0.1 by default (override only
via --host, not silently). A cloudflared-style tunnel is acceptable for
THIS app specifically (holds no model access, no secrets) — unlike the
LLM server (scripts/serve_llm.py), which stays loopback-only,
unconditionally, with no override flag at all. Collect first name only;
no other PII field exists anywhere in this schema.
"""
from __future__ import annotations

import json
import os
import pathlib
import sqlite3
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from .sampling import assign_items_joint, assignment_seed, make_joint_sampling_quotas

from dynamic_home_eqa.paths import REPO_ROOT as _DYNAMIC_EQA, RESULTS_DIR

BASE_DIR = pathlib.Path(__file__).parent.resolve()
# Overridable via env var (not a module-attribute patch after import) so
# tests can point at a fixture pool/DB — StaticFiles captures its
# directory at mount time, so a post-import attribute assignment would
# not actually change what "/media" serves.
MEDIA_DIR = pathlib.Path(os.environ.get("REALISM_MEDIA_DIR", str(_DYNAMIC_EQA / "results" / "reports" / "realism_eval_media")))
DATA_DIR = pathlib.Path(os.environ.get("REALISM_DATA_DIR", str(RESULTS_DIR / "realism_eval")))
DB_PATH = DATA_DIR / "realism_eval.db"

DATASET_VERSION = "v1"
ASSIGNMENT_MODE = "shared"   # every annotator sees the identical item set/order
SHARED_SEED = 20260707
TOTAL_ITEMS = 80             # overridable per deployment; must not exceed the rendered pool size

# suspicion_stratum (a fixed 50/50 tail/random_baseline quota) was removed
# — it only fed sampling stratification and a per-stratum quality-rate
# comparison, both retired along with the suspicion scoring that fed
# them (see scripts/realism_render_job.py's own docstring). change_type
# is the sole remaining axis, and it's uncontrolled (proportional to the
# pool, not a fixed target): a fixed ratio here can raise at assignment
# time (assign_items_joint refuses to silently short-fill a quota) if the
# actual render batch's mix doesn't match it exactly — confirmed
# concretely for change_type itself (state events were a thin slice of
# the first production batch), which is exactly why it stays proportional
# rather than fixed.
SAMPLING_DISTRIBUTIONS: dict[str, Optional[dict[str, float]]] = {
    "change_type": None,
    # profile is intentionally NOT a quota axis: this pool has 8+ distinct
    # profile values, and crossing it with change_type needs more items
    # per cell than a small render pool reliably has. profile is still
    # recorded per-response for post-hoc reporting; it's just not
    # hard-quota'd. Revisit if/when the render pool is scaled up
    # materially.
}

# "not_applicable" is only legal for placement/visibility, and only when
# the item itself is a state-change event (validated server-side against
# the item's own change_type, not just accepted on request — an
# annotator's client can't mark a location item's placement axis N/A).
ALLOWED_PLACEMENT = {"resting_naturally", "slightly_off", "clearly_wrong", "cannot_tell", "not_applicable"}
ALLOWED_BEHAVIOR = {"plausible", "unusual_but_possible", "implausible", "cannot_judge"}
ALLOWED_VISIBILITY = {"clearly_visible", "visible_but_hard", "not_visible", "not_applicable"}
ALLOWED_ISSUES = {
    "clipping_or_intersecting", "floating", "wrong_surface_for_category",
    "reason_does_not_match_move", "mover_capability_violation",
    "before_and_after_look_identical", "viewpoint_problem", "other",
}

_RESPONSE_COLUMNS = [
    "participant_id", "item_id", "dataset_version",
    "scene_id", "profile", "day", "category", "change_type",
    "placement", "behavior", "visibility", "issues", "comment", "time_spent_sec",
    "degenerate_viewpoint",
    # explicit per-panel status (scripts/realism_render_job.py's STATUS_OK /
    # STATUS_ANCHOR_UNRESOLVED / STATUS_ENCLOSED /
    # STATUS_AIM_FAILED) — degenerate_viewpoint above is kept as a collapsed
    # boolean for any consumer that just wants pass/fail; these two let the
    # analysis script decompose a bad rate by cause instead of guessing.
    "before_status", "after_status",
    "geometric_after_supported", "geometric_after_embedded",
    "deterministic_plausibility_confidence", "llm_self_graded_realism_day_mean",
]


# ---------------------------------------------------------------------------
# Item pool
# ---------------------------------------------------------------------------

def load_item_pool() -> list[dict]:
    """render_manifest.json (scripts/realism_render_job.py's output) is the
    item pool. Each entry's automatic signals live in a sibling per-item
    JSON — loaded here too so quota matching and the "frozen at render
    time" storage requirement both have everything in one place."""
    manifest_path = MEDIA_DIR / "render_manifest.json"
    if not manifest_path.exists():
        return []
    entries = json.loads(manifest_path.read_text())
    items = []
    for e in entries:
        detail_path = MEDIA_DIR / e["json"]
        detail = json.loads(detail_path.read_text()) if detail_path.exists() else {}
        signals = detail.get("automatic_signals", {})
        png_path = MEDIA_DIR / e["png"]
        # Cache-bust with the file's own mtime: realism_render_job.py can
        # be re-run with the same seed (same item_id/png filename, new
        # bytes — e.g. after a viewpoint-resolution fix) and browsers
        # aggressively cache image responses by URL. Without this, a
        # human annotator's browser can keep showing a stale render after
        # a real fix landed on disk, with nothing server-side to blame —
        # confirmed as the actual cause of an "it's still broken" report
        # that turned out to be a fully-caught-up browser cache.
        version = int(png_path.stat().st_mtime) if png_path.exists() else 0
        items.append({
            **e,
            "png_url": f"/media/{e['png']}?v={version}",
            "automatic_signals": signals,
        })
    return items


_ITEM_POOL: list[dict] = load_item_pool()
_ITEM_BY_ID: dict[str, dict] = {it["item_id"]: it for it in _ITEM_POOL}


def get_assigned_items(participant_id: str) -> list[dict]:
    if not _ITEM_POOL:
        return []
    n = min(TOTAL_ITEMS, len(_ITEM_POOL))
    quotas = make_joint_sampling_quotas(n, SAMPLING_DISTRIBUTIONS, _ITEM_POOL)
    seed = assignment_seed(participant_id, ASSIGNMENT_MODE, SHARED_SEED)
    ids = assign_items_joint(_ITEM_POOL, quotas, seed)
    return [_ITEM_BY_ID[i] for i in ids]


# ---------------------------------------------------------------------------
# Storage
# ---------------------------------------------------------------------------

def get_conn() -> sqlite3.Connection:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH, timeout=30)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA busy_timeout=30000")
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    conn = get_conn()
    conn.execute(
        """CREATE TABLE IF NOT EXISTS participants (
            participant_id TEXT PRIMARY KEY,
            display_name TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )"""
    )
    conn.execute(
        f"""CREATE TABLE IF NOT EXISTS responses_{DATASET_VERSION} (
            participant_id TEXT NOT NULL,
            item_id TEXT NOT NULL,
            dataset_version TEXT NOT NULL,
            scene_id TEXT, profile TEXT, day INTEGER, category TEXT,
            change_type TEXT,
            placement TEXT, behavior TEXT, visibility TEXT,
            issues TEXT, comment TEXT, time_spent_sec REAL,
            degenerate_viewpoint INTEGER,
            before_status TEXT, after_status TEXT,
            geometric_after_supported INTEGER, geometric_after_embedded INTEGER,
            deterministic_plausibility_confidence REAL,
            llm_self_graded_realism_day_mean REAL,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (participant_id, item_id, dataset_version)
        )"""
    )
    conn.commit()
    conn.close()


def save_response(row: dict) -> None:
    conn = get_conn()
    cols = _RESPONSE_COLUMNS
    placeholders = ",".join("?" for _ in cols)
    updates = ",".join(f"{c}=excluded.{c}" for c in cols if c not in ("participant_id", "item_id", "dataset_version"))
    conn.execute(
        f"""INSERT INTO responses_{DATASET_VERSION} ({",".join(cols)})
            VALUES ({placeholders})
            ON CONFLICT(participant_id, item_id, dataset_version) DO UPDATE SET {updates}, updated_at=CURRENT_TIMESTAMP""",
        [row.get(c) for c in cols],
    )
    conn.commit()
    conn.close()


def get_progress(participant_id: str) -> dict[str, dict]:
    conn = get_conn()
    rows = conn.execute(
        f"SELECT * FROM responses_{DATASET_VERSION} WHERE participant_id=? AND dataset_version=?",
        (participant_id, DATASET_VERSION),
    ).fetchall()
    conn.close()
    out = {}
    for r in rows:
        d = dict(r)
        d["issues"] = json.loads(d["issues"]) if d.get("issues") else []
        out[d["item_id"]] = d
    return out


# ---------------------------------------------------------------------------
# API
# ---------------------------------------------------------------------------

class StartRequest(BaseModel):
    name: str


class SaveResponseRequest(BaseModel):
    participant_id: str
    item_id: str
    placement: str
    behavior: str
    visibility: str
    issues: list[str] = []
    comment: str = ""
    time_spent_sec: float = 0.0


app = FastAPI()
init_db()


@app.post("/api/start")
def start(req: StartRequest):
    participant_id = req.name.strip().lower()
    if not participant_id:
        raise HTTPException(400, "name required")
    conn = get_conn()
    conn.execute(
        "INSERT OR IGNORE INTO participants (participant_id, display_name) VALUES (?, ?)",
        (participant_id, req.name.strip()),
    )
    conn.commit()
    conn.close()
    return {"participant_id": participant_id}


@app.get("/api/items/{participant_id}")
def items(participant_id: str):
    assigned = get_assigned_items(participant_id)
    # debug signals are included but the frontend must gate them behind
    # the opt-in checkbox — never shown by default.
    return {"dataset_version": DATASET_VERSION, "items": assigned}


@app.get("/api/progress/{participant_id}")
def progress(participant_id: str):
    return get_progress(participant_id)


@app.post("/api/response")
def response(req: SaveResponseRequest):
    item = _ITEM_BY_ID.get(req.item_id)
    if item is None:
        raise HTTPException(404, f"unknown item_id: {req.item_id!r}")
    signals = item.get("automatic_signals", {})

    if req.placement not in ALLOWED_PLACEMENT:
        raise HTTPException(400, f"invalid placement: {req.placement!r}")
    if req.behavior not in ALLOWED_BEHAVIOR:
        raise HTTPException(400, f"invalid behavior: {req.behavior!r}")
    if req.visibility not in ALLOWED_VISIBILITY:
        raise HTTPException(400, f"invalid visibility: {req.visibility!r}")
    for issue in req.issues:
        if issue not in ALLOWED_ISSUES:
            raise HTTPException(400, f"invalid issue: {issue!r}")
    # "not_applicable" is only legal for a real state-change item — a
    # location item's placement/visibility are always visually judgeable
    # in principle (even if the specific render failed, that's
    # cannot_tell/not_visible, a real judgment about this instance, not a
    # blanket "this axis doesn't apply" the item type would justify).
    is_state = item.get("change_type") == "state"
    if not is_state and (req.placement == "not_applicable" or req.visibility == "not_applicable"):
        raise HTTPException(400, "not_applicable is only valid for state-change items")

    row = {
        "participant_id": req.participant_id, "item_id": req.item_id, "dataset_version": DATASET_VERSION,
        "scene_id": item.get("scene_id"), "profile": item.get("profile"), "day": item.get("day"),
        "category": item.get("category"), "change_type": item.get("change_type"),
        "placement": req.placement, "behavior": req.behavior, "visibility": req.visibility,
        "issues": json.dumps(req.issues), "comment": req.comment, "time_spent_sec": req.time_spent_sec,
        # frozen at render time, not re-derived here — the whole point of
        # "frozen" is that a later generation-pipeline change can't retroactively
        # alter what an annotator was actually shown/judged against.
        "degenerate_viewpoint": signals.get("degenerate_viewpoint"),
        "before_status": signals.get("before_status"),
        "after_status": signals.get("after_status"),
        "geometric_after_supported": signals.get("after_supported"),
        "geometric_after_embedded": signals.get("after_embedded"),
        "deterministic_plausibility_confidence": signals.get("deterministic_plausibility_confidence"),
        "llm_self_graded_realism_day_mean": signals.get("llm_self_graded_realism_day_mean"),
    }
    save_response(row)
    return {"ok": True}


app.mount("/media", StaticFiles(directory=str(MEDIA_DIR)), name="media")
app.mount("/", StaticFiles(directory=str(BASE_DIR / "static"), html=True), name="static")
