"""
app.py — eval-index browser webapp (W-0 architecture, W-1 read-only views).

Frontend consumes ONLY the versioned eval_index/{run_id}/{folder}.json
artifacts written by scripts/build_eval_index.py — never raw pipeline
output. If pipeline output formats change, only the ingest script changes.

Single-file backend, deliberately minimal (no database):
  GET  /api/runs                 — run/folder catalog for the pickers
  GET  /api/index/{run}/{folder} — one index JSON, render refs rewritten to
                                   servable /api/media URLs
  POST /api/session              — create a session token (JSONL on disk)
  POST /api/rating               — append one rating (JSONL on disk; the
                                   endpoint is part of the W-0 contract —
                                   the rating UI itself is deliberately NOT
                                   built until the W1 UX checkpoint passes)
  GET  /api/media/{run}/{file}   — render PNGs, resolved per-run via the
                                   index's own media_dir field
  GET  /                         — the static SPA

Blinding is enforced SERVER-SIDE, not by CSS: a session created with
role="rater" gets payloads with the judge fields (judge_score,
judge_think_excerpt, stage_tag), the run/config label (condition), and the
real run ids stripped/aliased before serialization — a volunteer's client
never receives what it must not show. The debug checkbox in the UI only
toggles presentation for sessions that ARE allowed to see debug fields.

Creating a debug session requires the admin key when
EVAL_BROWSER_ADMIN_KEY is set in the server's environment. Unset (the
loopback/owner case) any session may be debug — same trust model as the
rest of this repo's loopback-only tooling. Set it whenever the app is
tunneled to volunteers.

Standing rules shared with webapp/realism_eval: binds to 127.0.0.1 by
default; collects first name only, no other PII anywhere in the schema.
"""
from __future__ import annotations

import datetime
import json
import os
import pathlib
import re
import secrets
import threading
from typing import Optional

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from dynamic_home_eqa.paths import REPO_ROOT, RESULTS_DIR

BASE_DIR = pathlib.Path(__file__).parent.resolve()
INDEX_DIR = pathlib.Path(os.environ.get("EVAL_INDEX_DIR", str(REPO_ROOT / "eval_index")))
DATA_DIR = pathlib.Path(os.environ.get("EVAL_BROWSER_DATA_DIR", str(RESULTS_DIR / "eval_browser")))
SESSIONS_PATH = DATA_DIR / "sessions.jsonl"
RATINGS_PATH = DATA_DIR / "ratings.jsonl"
ADMIN_KEY = os.environ.get("EVAL_BROWSER_ADMIN_KEY", "")

# Stripped from every event before a rater-session payload is serialized.
DEBUG_EVENT_FIELDS = ("judge_score", "judge_think_excerpt", "stage_tag")
# Stripped from the top level for rater sessions (run identity is aliased,
# the config label removed entirely).
DEBUG_TOP_FIELDS = ("condition", "run_id")

_SAFE_NAME = re.compile(r"^[A-Za-z0-9._-]+$")


# ---------------------------------------------------------------------------
# Index catalog
# ---------------------------------------------------------------------------

def _list_runs() -> list[str]:
    if not INDEX_DIR.exists():
        return []
    return sorted(d.name for d in INDEX_DIR.iterdir() if d.is_dir() and any(d.glob("*.json")))


def _run_alias_map() -> dict[str, str]:
    """Stable opaque alias per run for rater sessions ('run-1', 'run-2', ...
    in sorted-run order). Sorted order is deterministic across requests, so
    an alias means the same run for every rater — required for cross-rater
    aggregation later — while never leaking the model slug."""
    return {run: f"run-{i + 1}" for i, run in enumerate(_list_runs())}


def _resolve_run_ref(ref: str) -> Optional[str]:
    """Accept either a real run_id (debug sessions) or a rater alias."""
    runs = _list_runs()
    if ref in runs:
        return ref
    for run, alias in _run_alias_map().items():
        if alias == ref:
            return run
    return None


def _load_index(run_id: str, folder: str) -> dict:
    if not _SAFE_NAME.match(folder) or not _SAFE_NAME.match(run_id):
        raise HTTPException(400, "bad run/folder name")
    path = INDEX_DIR / run_id / f"{folder}.json"
    if not path.exists():
        raise HTTPException(404, f"no index for {run_id}/{folder}")
    return json.loads(path.read_text())


def _media_dir_for_run(run_id: str) -> Optional[pathlib.Path]:
    """A run's media dir comes from its own index files (media_dir field,
    added at ingest). Indexes built before that field existed fall back to
    the legacy shared media dir."""
    for f in sorted((INDEX_DIR / run_id).glob("*.json")):
        try:
            ref = json.loads(f.read_text()).get("media_dir")
        except Exception:
            continue
        if ref:
            p = pathlib.Path(ref)
            return p if p.is_absolute() else REPO_ROOT / p
    legacy = REPO_ROOT / "results" / "reports" / "realism_eval_media"
    return legacy if legacy.exists() else None


# ---------------------------------------------------------------------------
# Sessions (JSONL on disk, dict in memory)
# ---------------------------------------------------------------------------

_sessions_lock = threading.Lock()
_sessions: dict[str, dict] = {}


def _load_sessions() -> None:
    if not SESSIONS_PATH.exists():
        return
    for line in SESSIONS_PATH.read_text().splitlines():
        if line.strip():
            rec = json.loads(line)
            _sessions[rec["token"]] = rec


def _session_for(token: Optional[str]) -> dict:
    """No token at all = anonymous debug browsing (loopback owner use).
    A PRESENT token must be valid — a typo'd volunteer link should fail
    loudly, not silently fall back to unblinded output."""
    if not token:
        return {"token": None, "name": "local", "role": "debug"}
    sess = _sessions.get(token)
    if sess is None:
        raise HTTPException(403, "unknown session token")
    return sess


def _append_jsonl(path: pathlib.Path, rec: dict) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with _sessions_lock:
        with path.open("a") as f:
            f.write(json.dumps(rec) + "\n")


# ---------------------------------------------------------------------------
# Payload shaping (blinding lives HERE, not in the frontend)
# ---------------------------------------------------------------------------

def _rewrite_render_urls(idx: dict, run_ref: str, media_dir: Optional[pathlib.Path]) -> None:
    """render.png filename -> servable URL (+ mtime cache-bust, same rationale
    as webapp/realism_eval: re-rendered same-name PNGs must not be served
    stale from browser cache). media_dir itself never leaves the server."""
    for e in idx.get("events", []):
        rend = e.get("render") or {}
        png = rend.get("png")
        url = None
        if png and media_dir is not None:
            p = media_dir / png
            if p.exists():
                url = f"/api/media/{run_ref}/{png}?v={int(p.stat().st_mtime)}"
        e["render"] = {"url": url, "mask_status": rend.get("mask_status")}
    idx.pop("media_dir", None)


def _blind_for_rater(idx: dict, alias: str) -> dict:
    for field in DEBUG_TOP_FIELDS:
        idx.pop(field, None)
    idx["run_ref"] = alias
    for e in idx.get("events", []):
        for field in DEBUG_EVENT_FIELDS:
            e.pop(field, None)
    return idx


# ---------------------------------------------------------------------------
# API
# ---------------------------------------------------------------------------

class SessionRequest(BaseModel):
    name: str
    role: str = "rater"
    admin_key: str = ""


class RatingRequest(BaseModel):
    session: str
    run_ref: str
    folder: str
    event_id: str
    axes: dict = {}
    comment: str = ""
    time_spent_sec: float = 0.0


app = FastAPI()
_load_sessions()


@app.post("/api/session")
def create_session(req: SessionRequest):
    name = req.name.strip()
    if not name:
        raise HTTPException(400, "name required")
    if req.role not in ("debug", "rater"):
        raise HTTPException(400, f"invalid role: {req.role!r}")
    if req.role == "debug" and ADMIN_KEY and req.admin_key != ADMIN_KEY:
        raise HTTPException(403, "debug sessions require the admin key on this deployment")
    rec = {
        "token": secrets.token_urlsafe(16),
        "name": name[:64],
        "role": req.role,
        "created_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    }
    _sessions[rec["token"]] = rec
    _append_jsonl(SESSIONS_PATH, rec)
    return {"token": rec["token"], "role": rec["role"]}


@app.get("/api/runs")
def runs(session: Optional[str] = Query(default=None)):
    sess = _session_for(session)
    aliases = _run_alias_map()
    out = []
    for run_id in _list_runs():
        ref = run_id if sess["role"] == "debug" else aliases[run_id]
        folders = []
        for f in sorted((INDEX_DIR / run_id).glob("*.json")):
            try:
                idx = json.loads(f.read_text())
            except Exception:
                continue
            folders.append({
                "folder": f.stem,
                "scene_id": idx.get("scene_id"),
                "profile": idx.get("profile"),
                "day": idx.get("day"),
                "household_id": idx.get("household_id"),
                "n_events": len(idx.get("events", [])),
                "n_rendered": sum(1 for e in idx.get("events", []) if (e.get("render") or {}).get("png")),
                "n_occupants": len(idx.get("occupants", [])),
            })
        entry = {"run_ref": ref, "folders": folders}
        if sess["role"] == "debug":
            entry["condition"] = _condition_for_run(run_id)
        out.append(entry)
    return {"role": sess["role"], "runs": out}


def _condition_for_run(run_id: str) -> str:
    for f in sorted((INDEX_DIR / run_id).glob("*.json")):
        try:
            return json.loads(f.read_text()).get("condition", "")
        except Exception:
            continue
    return ""


@app.get("/api/index/{run_ref}/{folder}")
def index(run_ref: str, folder: str, session: Optional[str] = Query(default=None)):
    sess = _session_for(session)
    run_id = _resolve_run_ref(run_ref)
    if run_id is None:
        raise HTTPException(404, f"unknown run: {run_ref!r}")
    idx = _load_index(run_id, folder)
    # media URLs use the SAME ref the client addressed us with, so a rater
    # client never sees the real run id even in image URLs.
    _rewrite_render_urls(idx, run_ref, _media_dir_for_run(run_id))
    if sess["role"] != "debug":
        idx = _blind_for_rater(idx, _run_alias_map().get(run_id, run_ref))
    else:
        idx["run_ref"] = run_id
    return idx


@app.get("/api/media/{run_ref}/{filename}")
def media(run_ref: str, filename: str):
    run_id = _resolve_run_ref(run_ref)
    if run_id is None:
        raise HTTPException(404, f"unknown run: {run_ref!r}")
    if not _SAFE_NAME.match(filename) or not filename.endswith(".png"):
        raise HTTPException(400, "bad media filename")
    media_dir = _media_dir_for_run(run_id)
    if media_dir is None or not (media_dir / filename).exists():
        raise HTTPException(404, "no such media file")
    return FileResponse(media_dir / filename)


@app.post("/api/rating")
def rating(req: RatingRequest):
    sess = _session_for(req.session)  # 403s on unknown token
    run_id = _resolve_run_ref(req.run_ref)
    if run_id is None:
        raise HTTPException(404, f"unknown run: {req.run_ref!r}")
    _append_jsonl(RATINGS_PATH, {
        "session": sess["token"],
        "name": sess["name"],
        "role": sess["role"],
        "run_id": run_id,          # real id on disk — analysis needs it
        "folder": req.folder,
        "event_id": req.event_id,
        "axes": req.axes,
        "comment": req.comment[:2000],
        "time_spent_sec": req.time_spent_sec,
        "created_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    })
    return {"ok": True}


app.mount("/", StaticFiles(directory=str(BASE_DIR / "static"), html=True), name="static")
