"""Out-of-house accuracy over days, and the life of a treeLongLeaf library.

Two outputs into the run's ``figures/``:

    out_of_house_by_day.png   per-day top-1 accuracy on the questions whose
                              truth is OUT_OF_HOUSE, every main arm, with
                              95% intervals; plus, for the library arm, the
                              split inside / outside the documents' stated
                              away window and the hour-of-day profile
    library_timeline.html     interactive: stacked document weights over
                              days with every call, birth and retirement;
                              a ledger of documents x days whose cells can
                              show weight, the document's own accuracy, its
                              accuracy on out-of-house questions, or its
                              p(truth); click a document to read it

    python -m baselines.llm_hypotheses.library_timeline [--household hh_001__bank0]
        [--arm active__longleaf__longleaf_named__f0] [--window 9 14]
"""

from __future__ import annotations

import argparse
import collections
import json
import math
import pathlib
import re
from typing import Any, Dict, List, Optional, Sequence, Tuple

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from baselines.llm_hypotheses.analyze_tour_start import STUDY_DIR, load
from baselines.llm_hypotheses.error_atlas import PNG_ARMS, label
from baselines.llm_hypotheses.story_figures import COLOR as STORY_COLOR
from baselines.types import DAY_SECONDS

SURF, INK, INK2, MUTED, GRID = "#fcfcfb", "#0b0b0b", "#52514e", "#898781", "#e1e0d9"
plt.rcParams.update({"font.size": 9, "axes.edgecolor": INK2, "axes.labelcolor": INK2,
                     "xtick.color": INK2, "ytick.color": INK2, "axes.spines.top": False,
                     "axes.spines.right": False, "figure.facecolor": SURF,
                     "axes.facecolor": SURF, "axes.titlelocation": "left",
                     "axes.titleweight": "bold", "axes.titlesize": 10})
COLOR = dict(STORY_COLOR)
COLOR.update({"active__longleaf__longleaf_named__f0": "#4a3aa7",
              "active__longleaf_fixed__longleaf_named__f0": "#4a3aa7",
              "active__log_reader_aided__named__f0": "#e87ba4"})
AWAY = ("OUT_OF_HOUSE", "ON_PERSON")
DAY_NAMES = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]


def wilson(k: int, n: int, z: float = 1.96) -> Tuple[float, float, float]:
    if n == 0:
        return float("nan"), float("nan"), float("nan")
    p = k / n; d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return p, c - h, c + h


def hour_of(r: dict) -> float:
    return (r["t_query"] % DAY_SECONDS) / 3600.0


# ---------------------------------------------------------------- figure

def out_rows(rows: Sequence[dict]) -> List[dict]:
    return [r for r in rows if r["truth"] == "OUT_OF_HOUSE"]


def figure(arms, keys: Sequence[str], lib_key: str, window: Tuple[float, float],
           out: pathlib.Path, household: str) -> None:
    keys = [k for k in keys if k in arms]
    days = sorted({r["day"] for r in arms[keys[0]]["rows"]})
    n_out = collections.Counter(r["day"] for r in out_rows(arms[keys[0]]["rows"]))
    lo_h, hi_h = window

    def daily(k):
        by = collections.defaultdict(lambda: [0, 0])
        for r in out_rows(arms[k]["rows"]):
            by[r["day"]][0] += r["top1"]; by[r["day"]][1] += 1
        return by

    ncol = 3; nrow = math.ceil(len(keys) / ncol)
    fig = plt.figure(figsize=(16, 4.2 + 2.3 * nrow + 4.5))
    gs = fig.add_gridspec(2 + nrow, ncol, height_ratios=[1.6] + [1] * nrow + [1.5],
                          hspace=0.75, wspace=0.25)

    # A: everyone overlaid (no bands: the small multiples below carry them)
    ax = fig.add_subplot(gs[0, :])
    for k in keys:
        by = daily(k); xs = [d for d in days if by[d][1] >= 3]
        ax.plot(xs, [by[d][0] / by[d][1] for d in xs], color=COLOR.get(k, MUTED),
                lw=2.4 if k == lib_key else 1.2, alpha=1 if k in (lib_key, "active__routine_posterior__f0") else 0.75,
                marker="o", ms=3, label=label(k))
    for d in days:
        if d % 7 >= 5:
            ax.axvspan(d - 0.5, d + 0.5, color=GRID, zorder=0)
    ax2 = ax.twinx(); ax2.bar(days, [n_out[d] for d in days], color=GRID, width=0.8, zorder=0)
    ax2.set_ylim(0, max(n_out.values()) * 4); ax2.set_yticks([]); ax2.spines["right"].set_visible(False)
    for d in days:
        if n_out[d]:
            ax2.text(d, n_out[d] + 0.5, str(n_out[d]), ha="center", va="bottom", fontsize=6.5, color=MUTED)
    ax.set_ylim(0, 1.02); ax.set_xlim(days[0] - 0.6, days[-1] + 0.6)
    ax.set_ylabel("top-1 accuracy on out-of-house questions"); ax.set_xlabel("day (grey = weekend; grey bars and numbers = questions that day; days with < 3 hidden)")
    ax.legend(ncol=3, fontsize=7.5, frameon=False, loc="upper left")
    ax.grid(axis="y", color=GRID, lw=0.8); ax.set_axisbelow(True); ax.tick_params(length=0)
    ax.set_title("A  Accuracy on questions whose answer is OUT_OF_HOUSE, per day (intervals in B)")

    # B: small multiples with Wilson 95% bands
    for i, k in enumerate(keys):
        ax = fig.add_subplot(gs[1 + i // ncol, i % ncol])
        by = daily(k); xs = [d for d in days if by[d][1] >= 3]
        p, lo, hi = zip(*[wilson(*by[d]) for d in xs]) if xs else ([], [], [])
        ax.fill_between(xs, lo, hi, color=COLOR.get(k, MUTED), alpha=0.18, lw=0)
        ax.plot(xs, p, color=COLOR.get(k, MUTED), lw=1.6, marker="o", ms=2.5)
        for d in days:
            if d % 7 >= 5:
                ax.axvspan(d - 0.5, d + 0.5, color=GRID, zorder=0)
        tot = sum(v[0] for v in by.values()); n = sum(v[1] for v in by.values())
        ax.set_title(f"{label(k)}  ·  {tot}/{n} = {tot / n:.2f}", fontsize=8.5)
        ax.set_ylim(0, 1); ax.set_xlim(days[0] - 0.6, days[-1] + 0.6); ax.tick_params(length=0)
        ax.grid(axis="y", color=GRID, lw=0.8); ax.set_axisbelow(True)
        if i % ncol:
            ax.set_yticklabels([])
    first_small = fig.axes[2]   # axes[0] is A, axes[1] its twin
    fig.text(first_small.get_position().x0, first_small.get_position().y1 + 0.012,
             "B  Same, per arm, with 95% Wilson intervals", fontsize=10, fontweight="bold")

    # C: library arm — inside vs outside the stated window, and by hour
    lib = arms[lib_key]["rows"]
    ax = fig.add_subplot(gs[1 + nrow, :2])
    for name, cond, col in [(f"inside the documents' away window ({lo_h:g}–{hi_h:g} h)",
                             lambda r: lo_h <= hour_of(r) < hi_h, COLOR[lib_key]),
                            ("outside it", lambda r: not (lo_h <= hour_of(r) < hi_h), "#eb6834")]:
        by = collections.defaultdict(lambda: [0, 0])
        for r in out_rows(lib):
            if cond(r):
                by[r["day"]][0] += r["top1"]; by[r["day"]][1] += 1
        xs = [d for d in days if by[d][1] >= 3]
        p, lo, hi = zip(*[wilson(*by[d]) for d in xs]) if xs else ([], [], [])
        ax.fill_between(xs, lo, hi, color=col, alpha=0.15, lw=0)
        tot = sum(v[0] for v in by.values()); n = sum(v[1] for v in by.values())
        ax.plot(xs, p, color=col, lw=1.8, marker="o", ms=3, label=f"{name}: {tot}/{n} = {tot / n:.2f}")
    calls = [e["day"] for e in arms[lib_key]["diag"].get("reask", {}).get("events", [])]
    for d in calls:
        ax.axvline(d + 0.5, color=MUTED, lw=0.8, ls=(0, (2, 2)))
    ax.set_ylim(0, 1); ax.set_xlim(days[0] - 0.6, days[-1] + 0.6); ax.tick_params(length=0)
    ax.grid(axis="y", color=GRID, lw=0.8); ax.set_axisbelow(True)
    ax.legend(frameon=False, fontsize=8, loc="upper left"); ax.set_xlabel("day (dotted = a revision call)")
    ax.set_title(f"C  {label(lib_key)}: out-of-house accuracy inside vs outside the window the documents state")

    ax = fig.add_subplot(gs[1 + nrow, 2])
    hours = list(range(24))
    for k, col, lab in [(lib_key, COLOR[lib_key], label(lib_key)),
                        ("active__routine_posterior__f0", INK2, "routine posterior")]:
        if k not in arms:
            continue
        by = collections.defaultdict(lambda: [0, 0])
        for r in out_rows(arms[k]["rows"]):
            by[int(hour_of(r))][0] += r["top1"]; by[int(hour_of(r))][1] += 1
        xs = [h for h in hours if by[h][1] >= 3]
        p, lo, hi = zip(*[wilson(*by[h]) for h in xs]) if xs else ([], [], [])
        ax.errorbar(xs, p, yerr=[np.array(p) - np.array(lo), np.array(hi) - np.array(p)],
                    color=col, lw=1.6, marker="o", ms=3, capsize=2, label=lab)
    ax.axvspan(lo_h, hi_h, color=COLOR[lib_key], alpha=0.08, lw=0)
    n_by_h = collections.Counter(int(hour_of(r)) for r in out_rows(lib))
    for h in hours:
        if n_by_h[h]:
            ax.text(h, 1.06, str(n_by_h[h]), ha="center", va="bottom", fontsize=6.5, color=MUTED)
    ax.set_ylim(0, 1.16); ax.set_xlim(4.5, 19.5); ax.tick_params(length=0)
    ax.set_yticks([0, 0.25, 0.5, 0.75, 1.0])
    ax.grid(axis="y", color=GRID, lw=0.8); ax.set_axisbelow(True)
    ax.legend(frameon=False, fontsize=8, loc="center right"); ax.set_xlabel("hour the question is asked (numbers above = questions)")
    ax.set_title("D  By hour of day (shaded = stated window)")

    fig.suptitle(f"Out-of-house questions · {household} · exact scoring", x=0.02, ha="left",
                 fontsize=13, fontweight="bold", y=0.995)
    fig.savefig(out, dpi=140, bbox_inches="tight")
    plt.close(fig)


# ---------------------------------------------------------------- library payload

def parse_doc(path: pathlib.Path) -> Dict[str, Any]:
    """Prose (without the JSON block) and the away schedule from a document."""
    text = path.read_text()
    m = re.search(r"```json\s*(\{.*?\})\s*```", text, re.S)
    prose = (text[:m.start()] + text[m.end():]).strip() if m else text.strip()
    away: Dict[str, List[str]] = collections.defaultdict(list)
    claims: List[str] = []
    if m:
        try:
            j = json.loads(m.group(1))
            for obj, blocks in (j.get("targets") or {}).items():
                for b in blocks:
                    if b.get("at") in AWAY:
                        away[f"{b.get('days', '?')} {b.get('from', '?')}–{b.get('to', '?')} h → {b['at']}"].append(
                            obj.split("_mara")[0].replace("_shared", " (shared)"))
            claims = [f"{c.get('target', '?').split('_mara')[0]}: {c.get('claim', '')}"
                      for c in (j.get("claims") or [])]
        except Exception:
            pass
    return {"prose": prose[:6000], "away": {k: sorted(v) for k, v in away.items()}, "claims": claims}


def library_payload(arm: Dict[str, Any], key: str, household: str,
                    arm_dir: pathlib.Path, window: Tuple[float, float]) -> dict:
    diag = arm["diag"]; lib = diag.get("library") or {}
    rows = arm["rows"]
    days = sorted({r["day"] for r in rows})
    trace = {int(d): w for d, w in (lib.get("weight_trace") or {}).items()}
    status = lib.get("status") or {}
    births: Dict[str, dict] = {}
    for e in lib.get("edit_log") or []:
        births[e["hypothesis_id"]] = e
    retire = {e["hypothesis_id"]: e for e in lib.get("prune_log") or []}
    ids: List[str] = []
    seen = set()
    for d in sorted(trace):
        for h in trace[d]:
            if h not in seen:
                seen.add(h); ids.append(h)
    for h in status:
        if h not in seen:
            seen.add(h); ids.append(h)
    ids = [h for h in ids if h.startswith("p_")]

    # per-document, per-day own accuracy from the particle rows
    stat = {h: collections.defaultdict(lambda: [0, 0, 0, 0, 0.0, 0.0]) for h in ids}
    mix = collections.defaultdict(lambda: [0, 0, 0, 0, 0.0])
    for r in rows:
        d = r["day"]; is_out = r["truth"] == "OUT_OF_HOUSE"
        m = mix[d]; m[0] += 1; m[1] += r["top1"]
        if is_out:
            m[2] += 1; m[3] += r["top1"]; m[4] += r["dist"].get("OUT_OF_HOUSE", 0.0)
        for name, dist in (r.get("particles") or {}).items():
            if not name.startswith("HypothesisProgram("):
                continue
            h = name[len("HypothesisProgram("):-1]
            if h not in stat:
                continue
            s = stat[h][d]; top = max(dist, key=dist.get) if dist else None
            s[0] += 1; s[1] += int(top == r["truth"]); s[4] += dist.get(r["truth"], 0.0)
            if is_out:
                s[2] += 1; s[3] += int(top == r["truth"]); s[5] += dist.get("OUT_OF_HOUSE", 0.0)
    titles = {}
    for e in births.values():
        titles[e["hypothesis_id"]] = e.get("title", "")
    for h in diag.get("final_hypotheses") or []:
        titles.setdefault(h.get("hypothesis_id"), h.get("title", ""))
    docs = []
    for h in ids:
        md = arm_dir / "library" / f"{h}.md"
        parsed = parse_doc(md) if md.exists() else {"prose": "", "away": {}, "claims": []}
        if not titles.get(h) and parsed["prose"].startswith("#"):
            titles[h] = parsed["prose"].split("\n", 1)[0].lstrip("# ").split(" — ", 1)[-1]
        b = births.get(h)
        docs.append({
            "id": h, "title": titles.get(h, h), "parent": (b or {}).get("forked_from"),
            "birth_day": (b or {}).get("day", 0), "birth_call": (b or {}).get("call_index", 0),
            "op": (b or {}).get("op", "elicited"),
            "retire_day": retire[h]["day"] if h in retire else None,
            "status": (status.get(h) or {}).get("status", "retired" if h in retire else "live"),
            "final_w": (status.get(h) or {}).get("weight", 0.0),
            "peak_w": max([trace[d].get(h, 0.0) for d in trace] or [0.0]),
            "weights": [round(trace.get(d, {}).get(h, 0.0), 5) for d in days],
            "stat": {str(d): [s[0], s[1], s[2], s[3], round(s[4], 3), round(s[5], 3)]
                     for d, s in stat[h].items()},
            **parsed})
    calls = [{"day": e["day"], "t": e["t"], "trigger": e.get("trigger"), "reason": e.get("reason", ""),
              "n_live_after": e.get("n_live_after"), "ops": e.get("operations"),
              "call_index": e.get("call_index")} for e in (diag.get("reask") or {}).get("events", [])]
    return {"arm": key, "label": label(key), "household": household, "days": days,
            "window": list(window), "docs": docs, "calls": calls,
            "mix": {str(d): [m[0], m[1], m[2], m[3], round(m[4], 3)] for d, m in mix.items()},
            "day_names": DAY_NAMES}


HTML_TEMPLATE = r"""<title>Library Timeline __LABEL__</title>
<style>
:root{color-scheme:light;--page:#f9f9f7;--surface:#fcfcfb;--ink:#0b0b0b;--ink2:#52514e;--muted:#898781;--grid:#e1e0d9;
--line:#c3c2b7;--ring:rgba(11,11,11,.10);--accent:#4a3aa7;--wash:rgba(74,58,167,.08);--heat0:#fcfcfb;--heatmid:#5598e7;--heat1:#0d366b;
--good:#0ca30c}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){color-scheme:dark;--page:#0d0d0d;--surface:#1a1a19;--ink:#fff;--ink2:#c3c2b7;
--muted:#898781;--grid:#2c2c2a;--line:#383835;--ring:rgba(255,255,255,.10);--accent:#9085e9;--wash:rgba(144,133,233,.14);--heat0:#1a1a19;--heatmid:#256abf;--heat1:#9ec5f4}}
:root[data-theme="dark"]{color-scheme:dark;--page:#0d0d0d;--surface:#1a1a19;--ink:#fff;--ink2:#c3c2b7;--muted:#898781;--grid:#2c2c2a;--line:#383835;
--ring:rgba(255,255,255,.10);--accent:#9085e9;--wash:rgba(144,133,233,.14);--heat0:#1a1a19;--heatmid:#256abf;--heat1:#9ec5f4}
*{box-sizing:border-box}
body{margin:0;background:var(--page);color:var(--ink);font:14px/1.45 system-ui,-apple-system,"Segoe UI",sans-serif;padding-block:0 32px}
.wrap{display:grid;grid-template-columns:minmax(0,1fr) 380px;gap:0;min-height:100vh}
main{padding:16px 24px;min-width:0}
aside{background:var(--surface);border-left:1px solid var(--grid);padding:16px;position:sticky;top:env(safe-area-inset-top,0px);height:100vh;overflow-y:auto}
h1{font-size:18px;margin:0 0 2px;letter-spacing:-.01em}
.sub{color:var(--muted);font-size:12px;margin-bottom:12px}
h2{font-size:12px;margin:18px 0 6px;text-transform:uppercase;letter-spacing:.06em;color:var(--ink2);font-weight:600}
section.panel{background:var(--surface);border:1px solid var(--ring);border-radius:4px;padding:14px 16px;margin-bottom:18px}
section.panel h3{margin:0 0 2px;font-size:14px}
.note{font-size:12px;color:var(--muted);margin-bottom:10px}
.toolbar{display:flex;gap:14px;align-items:center;flex-wrap:wrap;font-size:12px;color:var(--ink2);margin-bottom:8px}
select{font:12px system-ui;padding:2px 6px;border:1px solid var(--line);background:var(--surface);color:var(--ink);border-radius:3px}
label.row{display:flex;gap:6px;align-items:center;cursor:pointer}
label.row input{margin:0;accent-color:var(--accent)}
.scroll{overflow-x:auto}
svg{display:block;max-width:100%}
#ledger svg{max-width:none}
svg text{fill:var(--ink2);font-family:system-ui,sans-serif}
svg .band{stroke:var(--surface);stroke-width:.6;cursor:pointer}
svg .band:hover{stroke:var(--ink);stroke-width:1.2}
svg .band.dim{opacity:.25}
svg .band.sel{stroke:var(--ink);stroke-width:1.6}
svg .cell{cursor:pointer}
svg .cell:hover rect{stroke:var(--ink);stroke-width:1.2}
svg .rowlab{cursor:pointer}
svg .rowlab:hover{fill:var(--ink)}
svg .rowlab.sel{fill:var(--ink);font-weight:600}
.legend{display:flex;gap:14px;flex-wrap:wrap;font-size:12px;color:var(--ink2);margin:6px 0}
.legend i{display:inline-block;width:10px;height:10px;border-radius:2px;margin-right:5px;vertical-align:-1px}
#tip{position:fixed;pointer-events:none;background:var(--ink);color:var(--page);font-size:12px;padding:6px 9px;border-radius:3px;max-width:360px;z-index:9;display:none;line-height:1.35}
.doc h3{font-size:14px;margin:0 0 4px}
.doc .meta{font-size:12px;color:var(--muted);margin-bottom:8px}
.doc .away{font-size:12px;background:var(--wash);padding:6px 8px;border-radius:3px;margin:6px 0}
.doc .claims li{font-size:12px;margin-bottom:3px}
.doc .prose{font-size:12.5px;white-space:pre-wrap;line-height:1.45;max-width:65ch}
.pill{display:inline-block;padding:0 6px;border-radius:9px;font-size:11px;color:#fff;background:var(--muted)}
.pill.live{background:var(--good)}
.kpis{display:flex;gap:18px;flex-wrap:wrap;margin:6px 0 14px}
.kpi b{display:block;font-size:20px;font-weight:600}.kpi span{font-size:12px;color:var(--muted)}
button.mini{font:12px system-ui;margin-top:8px;padding:2px 8px;border:1px solid var(--line);background:transparent;color:var(--ink2);border-radius:3px;cursor:pointer}
input:focus-visible,select:focus-visible,button:focus-visible{outline:2px solid var(--accent);outline-offset:1px}
@media (max-width:900px){.wrap{grid-template-columns:1fr}aside{position:static;height:auto;border-left:0;border-top:1px solid var(--grid)}main{padding:16px}}
</style>
<div class="wrap">
<main>
  <h1>Library timeline</h1>
  <div class="sub">__LABEL__ · __HOUSEHOLD__ · exact scoring. Weights are end-of-day snapshots; day 0 starts uniform.</div>
  <div class="kpis" id="kpis"></div>

  <section class="panel">
    <h3>Document weights over the run</h3>
    <div class="note">Each band is one document; bands stack to the mixture's total (the statistical particle is the grey band on top). Vertical lines are revision calls. ▲ marks a document's birth day. Click a band to read the document.</div>
    <div class="toolbar">
      <span>colour by</span>
      <select id="colourBy"><option value="call">birth call (older = lighter)</option><option value="family">family (root document)</option><option value="status">status at the end</option><option value="away">how much of the personal kit it sends out</option></select>
      <label class="row"><input type="checkbox" id="showRetired" checked> show retired documents in the ledger</label>
    </div>
    <div class="legend" id="legendA"></div>
    <div class="scroll" id="stack"></div>
  </section>

  <section class="panel">
    <h3>Ledger: documents × days</h3>
    <div class="note">One row per document, in birth order; a row runs from birth to retirement (✕). A bracket at the row's start points to its parent's row. Accuracy cells are the document's <em>own</em> top-1 answer on that day's questions, i.e. how it would have scored alone.</div>
    <div class="toolbar">
      <span>cells show</span>
      <select id="metric"><option value="w">weight (end of day)</option><option value="acc">own accuracy, all questions</option><option value="accout">own accuracy, out-of-house questions</option><option value="pout">own mean p(OUT_OF_HOUSE) on out-of-house questions</option><option value="pt">own mean p(truth)</option></select>
      <span id="mixline" style="color:var(--muted)"></span>
    </div>
    <div class="scroll" id="ledger"></div>
  </section>

  <section class="panel">
    <h3>Mixture vs the best single document, out-of-house questions per day</h3>
    <div class="note">Bars: the mixture's accuracy on that day's out-of-house questions (number of questions above). Dots: the best-scoring live document that day, alone. When the dot sits well above the bar, the library held a right answer that the weights did not use.</div>
    <div class="scroll" id="bestdoc"></div>
  </section>
</main>
<aside>
  <h2>Revision calls</h2>
  <div id="calls" style="font-size:12px"></div>
  <h2>Document</h2>
  <div id="doc" class="doc"><div class="note">Click a band, a ledger row or a call to read it here.</div></div>
</aside>
</div>
<div id="tip"></div>
<script>
const D=__DATA__;
const docs=D.docs, days=D.days, ND=days.length;
const byId={}; docs.forEach(d=>byId[d.id]=d);
const rootOf=d=>{let x=d; const seen=new Set(); while(x.parent&&byId[x.parent]&&!seen.has(x.id)){seen.add(x.id);x=byId[x.parent];} return x.id;};
docs.forEach(d=>{ d.family=rootOf(d); d.kitn=Object.values(d.away||{}).reduce((s,v)=>s+v.length,0); d.kit=d.kitn>0; });
const $=s=>document.querySelector(s);
const el=(t,a={},...ch)=>{const e=document.createElement(t);for(const k in a){if(k==='class')e.className=a[k];else e.setAttribute(k,a[k]);}for(const c of ch)e.append(c);return e;};
const svgEl=(t,a={})=>{const e=document.createElementNS('http://www.w3.org/2000/svg',t);for(const k in a)e.setAttribute(k,a[k]);return e;};
const tip=$('#tip');
function hover(node, html){ node.addEventListener('mousemove',e=>{tip.innerHTML=html();tip.style.display='block';tip.style.left=Math.min(e.clientX+14,window.innerWidth-370)+'px';tip.style.top=(e.clientY+14)+'px';}); node.addEventListener('mouseleave',()=>tip.style.display='none'); }
function hex(h){h=h.replace('#','');return [0,2,4].map(i=>parseInt(h.slice(i,i+2),16));}
function lerp(a,b,t){return a.map((v,i)=>Math.round(v+(b[i]-v)*t));}
function css(v){return getComputedStyle(document.documentElement).getPropertyValue(v).trim();}
function heat(t){const a=hex(css('--heat0')),m=hex(css('--heatmid')),b=hex(css('--heat1'));const c=t<0.5?lerp(a,m,t*2):lerp(m,b,(t-0.5)*2);return `rgb(${c.join(',')})`;}
const CAT=['#2a78d6','#eb6834','#1baf7a','#eda100','#e87ba4','#008300','#4a3aa7','#e34948'];
const S={colourBy:'call',metric:'w',showRetired:true,sel:null};
try{const s=JSON.parse(localStorage.getItem('lib-timeline-'+D.arm)||'null');if(s)Object.assign(S,s);}catch(e){}
function persist(){try{localStorage.setItem('lib-timeline-'+D.arm,JSON.stringify(S));}catch(e){}}

// ---- colour assignment --------------------------------------------------
const calls=[...new Set(docs.map(d=>d.birth_call))].sort((a,b)=>a-b);
const famPeak={}; docs.forEach(d=>{famPeak[d.family]=Math.max(famPeak[d.family]||0,d.peak_w);});
const topFam=Object.keys(famPeak).sort((a,b)=>famPeak[b]-famPeak[a]).slice(0,7);
function colour(d){
  if(S.colourBy==='call'){const i=calls.indexOf(d.birth_call);return heat(0.15+0.85*(calls.length>1?i/(calls.length-1):0));}
  if(S.colourBy==='family'){const i=topFam.indexOf(d.family);return i<0?css('--grid'):CAT[i];}
  if(S.colourBy==='status'){return d.status==='live'?CAT[2]:css('--line');}
  return d.kit?heat(0.35+0.6*Math.min(1,d.kitn/11)):css('--grid');
}
function legend(){
  const L=$('#legendA'); L.innerHTML='';
  const add=(c,t)=>{const i=el('i');i.style.background=c;L.append(el('span',{},i,t));};
  if(S.colourBy==='call'){ add(heat(0.15),'elicited on day 0'); calls.slice(1).forEach(c=>{const d=docs.find(x=>x.birth_call===c);add(colour(d),`call ${c} (day ${d.birth_day})`);}); }
  if(S.colourBy==='family'){ topFam.forEach((f,i)=>add(CAT[i],`${f}: ${(byId[f].title||'').slice(0,40)}`)); add(css('--grid'),'other families'); }
  if(S.colourBy==='status'){ add(CAT[2],'live at the end'); add(css('--line'),'retired'); }
  if(S.colourBy==='away'){ add(css('--grid'),'no away block'); add(heat(0.4),'a few objects out'); add(heat(0.95),'the whole personal kit out'); }
}
const order=[...docs].sort((a,b)=>a.birth_day-b.birth_day||a.birth_call-b.birth_call||a.id.localeCompare(b.id));

// ---- stacked weights ----------------------------------------------------
function drawStack(){
  const box=$('#stack'); box.innerHTML='';
  const W=Math.max(700,Math.min(1300,box.clientWidth||1000)), H=320, L=40, R=16, T=26, B=30;
  const pw=W-L-R, ph=H-T-B; const x=i=>L+pw*(i/ND); // i = 0..ND, snapshot at end of day i-1
  const svg=svgEl('svg',{viewBox:`0 0 ${W} ${H}`,width:W,height:H});
  [0,0.25,0.5,0.75,1].forEach(v=>{const y=T+ph*(1-v);svg.append(svgEl('line',{x1:L,x2:W-R,y1:y,y2:y,stroke:'var(--grid)'}));const t=svgEl('text',{x:L-6,y:y+4,'font-size':10,'text-anchor':'end'});t.textContent=v;svg.append(t);});
  days.forEach((d,i)=>{ if(d%7>=5) svg.append(svgEl('rect',{x:x(i),y:T,width:pw/ND,height:ph,fill:'var(--grid)',opacity:.5}));
    const t=svgEl('text',{x:x(i)+pw/ND/2,y:H-B+14,'font-size':10,'text-anchor':'middle'}); t.textContent=d; svg.append(t); });
  const elic=order.filter(d=>d.birth_call===0).length;
  let base=new Array(ND+1).fill(0);
  const wAt=(d,i)=>i===0?(d.birth_call===0?1/elic:0):(d.weights[i-1]||0);
  order.forEach(d=>{
    const top=base.map((b,i)=>b+wAt(d,i));
    let path='M'+x(0)+','+(T+ph*(1-base[0]));
    for(let i=1;i<=ND;i++) path+=' L'+x(i)+','+(T+ph*(1-base[i]));
    for(let i=ND;i>=0;i--) path+=' L'+x(i)+','+(T+ph*(1-top[i]));
    path+='Z';
    const p=svgEl('path',{d:path,fill:colour(d),class:'band'+(S.sel&&S.sel!==d.id?' dim':'')+(S.sel===d.id?' sel':'')});
    p.addEventListener('click',()=>select(d.id));
    hover(p,()=>`<b>${d.id}</b> ${d.title}<br>born day ${d.birth_day} (${d.op}${d.parent?' of '+d.parent:''}) · ${d.status}${d.retire_day!==null?' day '+d.retire_day:''}<br>peak weight ${d.peak_w.toFixed(2)} · final ${d.final_w.toFixed(3)}`);
    svg.append(p); base=top;
  });
  let path='M'+x(0)+','+(T+ph*(1-base[0])); for(let i=1;i<=ND;i++) path+=' L'+x(i)+','+(T+ph*(1-base[i])); for(let i=ND;i>=0;i--) path+=' L'+x(i)+','+T; path+='Z';
  const mf=svgEl('path',{d:path,fill:'var(--line)',class:'band'}); hover(mf,()=>'most-frequent statistical particle (what the documents failed to earn)'); svg.append(mf);
  order.forEach(d=>{ if(d.birth_call>0){ const i=d.birth_day; const t=svgEl('text',{x:x(i)+pw/ND/2,y:T-6,'font-size':9,'text-anchor':'middle'}); t.textContent='▲'; hover(t,()=>`born day ${d.birth_day}: ${d.id} ${d.title}`); svg.append(t);} });
  D.calls.forEach(c=>{ const xx=x(c.day)+pw/ND*0.5; svg.append(svgEl('line',{x1:xx,x2:xx,y1:T,y2:T+ph,stroke:'var(--ink2)','stroke-dasharray':'3 3'})); const t=svgEl('text',{x:xx+2,y:T+10,'font-size':9}); t.textContent=c.call_index; svg.append(t); });
  const yl=svgEl('text',{x:8,y:T+ph/2,'font-size':10,transform:`rotate(-90 8 ${T+ph/2})`,'text-anchor':'middle'}); yl.textContent='weight'; svg.append(yl);
  box.append(svg);
}

// ---- ledger --------------------------------------------------------------
function cellVal(d,day){ const s=d.stat[String(day)]; const i=days.indexOf(day);
  switch(S.metric){ case 'w': return i>=0?d.weights[i]:null;
    case 'acc': return s&&s[0]?s[1]/s[0]:null; case 'accout': return s&&s[2]?s[3]/s[2]:null;
    case 'pout': return s&&s[2]?s[5]/s[2]:null; default: return s&&s[0]?s[4]/s[0]:null; } }
function cellText(d,day){ const v=cellVal(d,day); if(v===null||v===undefined) return ''; const s=d.stat[String(day)]||[0,0,0,0,0,0];
  if(S.metric==='w') return v>=0.005?(v<0.1?v.toFixed(2).slice(1):v.toFixed(2)):''; if(S.metric==='acc') return s[1]+'/'+s[0]; if(S.metric==='accout') return s[3]+'/'+s[2]; return v.toFixed(2); }
function drawLedger(){
  const box=$('#ledger'); box.innerHTML='';
  let rows=S.showRetired?order:order.filter(d=>d.status==='live');
  const rowIdx={}; rows.forEach((d,i)=>rowIdx[d.id]=i);
  const L=330, cw=34, ch=18, T=26, W=L+ND*cw+20, H=T+rows.length*ch+10;
  const svg=svgEl('svg',{viewBox:`0 0 ${W} ${H}`,width:W,height:H});
  days.forEach((d,i)=>{ const t=svgEl('text',{x:L+i*cw+cw/2,y:T-8,'font-size':10,'text-anchor':'middle'}); t.textContent=d; svg.append(t); if(d%7>=5) svg.append(svgEl('rect',{x:L+i*cw,y:T,width:cw,height:rows.length*ch,fill:'var(--grid)',opacity:.4})); });
  D.calls.forEach(c=>{ const i=days.indexOf(c.day); if(i<0) return; svg.append(svgEl('line',{x1:L+i*cw+cw/2,x2:L+i*cw+cw/2,y1:T-4,y2:T+rows.length*ch,stroke:'var(--ink2)','stroke-dasharray':'3 3',opacity:.7})); });
  const vmax=S.metric==='w'?Math.max(0.05,...docs.flatMap(d=>d.weights)):1;
  rows.forEach((d,r)=>{ const y=T+r*ch;
    const lab=svgEl('text',{x:L-10,y:y+ch/2+4,'font-size':10.5,'text-anchor':'end',class:'rowlab'+(S.sel===d.id?' sel':'')}); lab.textContent=`${d.id} ${d.title.length>34?d.title.slice(0,33)+'…':d.title}`; lab.addEventListener('click',()=>select(d.id)); hover(lab,()=>`<b>${d.id}</b> ${d.title}<br>${d.op}${d.parent?' of '+d.parent:''}, day ${d.birth_day} · ${d.status}${d.retire_day!==null?' day '+d.retire_day:''}`); svg.append(lab);
    svg.append(svgEl('rect',{x:L-6,y:y+3,width:3,height:ch-6,fill:colour(d)}));
    if(d.parent&&rowIdx[d.parent]!==undefined){ const pi=days.indexOf(d.birth_day); const py=T+rowIdx[d.parent]*ch+ch/2; const xx=L+pi*cw+2; svg.append(svgEl('path',{d:`M${xx+6},${py} L${xx},${py} L${xx},${y+ch/2} L${xx+6},${y+ch/2}`,fill:'none',stroke:'var(--ink2)','stroke-width':1})); }
    days.forEach((day,i)=>{ if(day<d.birth_day||(d.retire_day!==null&&day>d.retire_day)) return;
      const v=cellVal(d,day); const g=svgEl('g',{class:'cell'});
      const fill=v===null||v===undefined?'var(--surface)':heat(Math.min(1,v/vmax));
      g.append(svgEl('rect',{x:L+i*cw+1,y:y+1,width:cw-2,height:ch-2,rx:2,fill,stroke:'var(--grid)','stroke-width':.5}));
      const tx=cellText(d,day); if(tx){ const t=svgEl('text',{x:L+i*cw+cw/2,y:y+ch/2+3.5,'font-size':8.5,'text-anchor':'middle'}); t.setAttribute('style',`fill:${(v||0)/vmax>0.55?'#fff':'var(--ink)'}`); t.textContent=tx; g.append(t); }
      if(d.retire_day===day){ const t=svgEl('text',{x:L+i*cw+cw-3,y:y+ch/2+3.5,'font-size':9,'text-anchor':'end'}); t.setAttribute('style','fill:var(--ink)'); t.textContent='✕'; g.append(t); }
      g.addEventListener('click',()=>select(d.id));
      hover(g,()=>{ const s=d.stat[String(day)]||[0,0,0,0,0,0]; const w=d.weights[i]; return `<b>${d.id}</b> day ${day} (${D.day_names[day%7]})<br>weight at end of day ${w.toFixed(3)}<br>own top-1: ${s[1]}/${s[0]} all · ${s[3]}/${s[2]} out-of-house<br>own mean p(truth) ${s[0]?(s[4]/s[0]).toFixed(2):'–'} · mean p(OUT) on out-of-house ${s[2]?(s[5]/s[2]).toFixed(2):'–'}`; });
      svg.append(g); });
  });
  box.append(svg);
  const tot=days.reduce((a,d)=>{const m=D.mix[String(d)]||[0,0,0,0,0];return [a[0]+m[0],a[1]+m[1],a[2]+m[2],a[3]+m[3]];},[0,0,0,0]);
  $('#mixline').textContent=`mixture: ${tot[1]}/${tot[0]} = ${(tot[1]/tot[0]).toFixed(3)} all questions · ${tot[3]}/${tot[2]} = ${(tot[3]/tot[2]).toFixed(2)} out-of-house`;
}

// ---- best single doc vs mixture ------------------------------------------
function drawBest(){
  const box=$('#bestdoc'); box.innerHTML='';
  const W=Math.max(700,Math.min(1300,box.clientWidth||1000)), H=220, L=40, R=16, T=24, B=30, pw=W-L-R, ph=H-T-B, bw=pw/ND;
  const svg=svgEl('svg',{viewBox:`0 0 ${W} ${H}`,width:W,height:H});
  [0,0.5,1].forEach(v=>{const y=T+ph*(1-v);svg.append(svgEl('line',{x1:L,x2:W-R,y1:y,y2:y,stroke:'var(--grid)'}));const t=svgEl('text',{x:L-6,y:y+4,'font-size':10,'text-anchor':'end'});t.textContent=v;svg.append(t);});
  days.forEach((day,i)=>{ const m=D.mix[String(day)]||[0,0,0,0,0]; const x=L+i*bw;
    if(day%7>=5) svg.append(svgEl('rect',{x,y:T,width:bw,height:ph,fill:'var(--grid)',opacity:.5}));
    const t=svgEl('text',{x:x+bw/2,y:H-B+14,'font-size':10,'text-anchor':'middle'}); t.textContent=day; svg.append(t);
    if(m[2]<1) return;
    const n=svgEl('text',{x:x+bw/2,y:T-6,'font-size':9,'text-anchor':'middle'}); n.textContent=m[2]; svg.append(n);
    const acc=m[3]/m[2]; const bar=svgEl('rect',{x:x+3,y:T+ph*(1-acc),width:bw-6,height:Math.max(1,ph*acc),rx:2,fill:'var(--accent)',opacity:.85});
    let best=null; docs.forEach(d=>{const s=d.stat[String(day)]; if(s&&s[2]>=1){const a=s[3]/s[2]; if(!best||a>best.a) best={a,d,s};}});
    hover(bar,()=>`day ${day}: mixture ${m[3]}/${m[2]} right on out-of-house questions · mean p(OUT) ${(m[4]/m[2]).toFixed(2)}`+(best?`<br>best single document ${best.d.id}: ${best.s[3]}/${best.s[2]}`:''));
    svg.append(bar);
    if(best){ const c=svgEl('circle',{cx:x+bw/2,cy:T+ph*(1-best.a),r:4,fill:'var(--surface)',stroke:'var(--ink)','stroke-width':1.5,style:'cursor:pointer'}); hover(c,()=>`best single document on day ${day}: <b>${best.d.id}</b> ${best.d.title}<br>${best.s[3]}/${best.s[2]} out-of-house right alone · its weight ${best.d.weights[i].toFixed(3)}`); c.addEventListener('click',()=>select(best.d.id)); svg.append(c); }
  });
  box.append(svg);
}

// ---- side panel ----------------------------------------------------------
function drawCalls(){
  const box=$('#calls'); box.innerHTML='';
  if(!D.calls.length){ box.append(el('div',{class:'note'},'no revision calls')); return; }
  D.calls.forEach(c=>{ const born=docs.filter(d=>d.birth_call===c.call_index);
    const row=el('div',{style:'padding:5px 0;border-bottom:1px solid var(--grid);cursor:pointer'},
      el('b',{},`call ${c.call_index} · day ${c.day} (${D.day_names[c.day%7]}) · ${c.trigger}`),
      el('div',{style:'color:var(--muted)'},c.reason.slice(0,140)),
      el('div',{},`${born.length} new: ${born.map(d=>d.id).join(', ')}${c.n_live_after!==undefined&&c.n_live_after!==null?' · live after: '+c.n_live_after:''}`));
    row.addEventListener('click',()=>{ if(born[0]) select(born[0].id); });
    box.append(row); });
}
function select(id){ S.sel=(S.sel===id?null:id); persist(); drawStack(); drawLedger(); showDoc(); }
function showDoc(){
  const box=$('#doc'); box.innerHTML='';
  const d=S.sel&&byId[S.sel]; if(!d){ box.append(el('div',{class:'note'},'Click a band, a ledger row or a call to read it here.')); return; }
  const pill=el('span',{class:'pill'+(d.status==='live'?' live':'')},d.status+(d.retire_day!==null?' day '+d.retire_day:''));
  box.append(el('h3',{},`${d.id} — ${d.title}`));
  box.append(el('div',{class:'meta'},`${d.op}${d.parent?' of '+d.parent:''} · born day ${d.birth_day}${d.birth_call?' (call '+d.birth_call+')':''} · peak weight ${d.peak_w.toFixed(2)} · final ${d.final_w.toFixed(3)} · `,pill));
  const kids=docs.filter(x=>x.parent===d.id); if(kids.length) box.append(el('div',{class:'meta'},'children: '+kids.map(k=>k.id).join(', ')));
  const away=Object.entries(d.away||{}); if(away.length){ const a=el('div',{class:'away'},el('b',{},'Away blocks: ')); away.forEach(([k,v])=>a.append(el('div',{},`${k}: ${v.join(', ')}`))); box.append(a);} else box.append(el('div',{class:'away'},'No away blocks: this document never sends anything out of the house.'));
  if(d.claims&&d.claims.length){ const ul=el('ul',{class:'claims'}); d.claims.forEach(c=>ul.append(el('li',{},c))); box.append(el('b',{style:'font-size:12px'},'Claims'),ul); }
  box.append(el('div',{class:'prose'},d.prose||'(document text not found)'));
  const p=d.parent&&byId[d.parent]; if(p){ const b=el('button',{class:'mini'},'open parent '+p.id); b.addEventListener('click',()=>select(p.id)); box.append(b); }
}
function drawKPIs(){
  const box=$('#kpis'); box.innerHTML='';
  const live=docs.filter(d=>d.status==='live').length, forks=docs.filter(d=>d.op==='fork').length, fresh=docs.filter(d=>d.op!=='fork'&&d.birth_call>0).length;
  const lateW=docs.filter(d=>d.birth_day>=14).reduce((s,d)=>s+d.final_w,0);
  [[docs.length,'documents ever'],[live,'live at the end'],[forks,'forks'],[fresh,'fresh (not forked)'],[D.calls.length,'revision calls'],[lateW.toFixed(2),'final weight on documents born day 14+']].forEach(([v,l])=>box.append(el('div',{class:'kpi'},el('b',{},String(v)),el('span',{},l))));
}
function all(){ legend(); drawStack(); drawLedger(); drawBest(); drawCalls(); showDoc(); drawKPIs(); }
$('#colourBy').value=S.colourBy; $('#colourBy').addEventListener('change',e=>{S.colourBy=e.target.value;persist();all();});
$('#metric').value=S.metric; $('#metric').addEventListener('change',e=>{S.metric=e.target.value;persist();drawLedger();});
$('#showRetired').checked=S.showRetired; $('#showRetired').addEventListener('change',e=>{S.showRetired=e.target.checked;persist();drawLedger();});
all();
window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change',all);
</script>
"""


def write_html(path: pathlib.Path, payload: dict) -> None:
    data = json.dumps(payload, separators=(",", ":"))
    path.write_text(HTML_TEMPLATE.replace("__DATA__", data).replace("__LABEL__", payload["label"])
                    .replace("__HOUSEHOLD__", payload["household"]))


# ---------------------------------------------------------------- main

def main(argv: Optional[Sequence[str]] = None) -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--household", default="hh_001__bank0")
    ap.add_argument("--study-dir", type=pathlib.Path, default=STUDY_DIR / "main")
    ap.add_argument("--arm", default="active__longleaf__longleaf_named__f0",
                    help="library arm for the timeline and panels C/D")
    ap.add_argument("--window", type=float, nargs=2, default=(9.0, 14.0),
                    help="the away window the documents state, hours")
    args = ap.parse_args(argv)

    arms = load(args.household, args.study_dir)
    if args.arm not in arms:
        raise SystemExit(f"{args.arm} not found under {args.study_dir / args.household}")
    fig_dir = args.study_dir / args.household / "figures"
    fig_dir.mkdir(exist_ok=True)
    window = (args.window[0], args.window[1])

    keys = [k for k in PNG_ARMS if k in arms]
    if args.arm not in keys:
        keys.insert(1, args.arm)
    figure(arms, keys, args.arm, window, fig_dir / "out_of_house_by_day.png", args.household)

    arm_dir = next(p.parent for p in (args.study_dir / args.household / "arms").rglob("diagnostics.json")
                   if p.parent.name == args.arm)
    payload = library_payload(arms[args.arm], args.arm, args.household, arm_dir, window)
    write_html(fig_dir / "library_timeline.html", payload)

    n_docs = len(payload["docs"]); n_live = sum(d["status"] == "live" for d in payload["docs"])
    print(f"{args.arm}: {n_docs} documents ({n_live} live), {len(payload['calls'])} calls")
    print(f"  {fig_dir / 'out_of_house_by_day.png'}\n  {fig_dir / 'library_timeline.html'}")


if __name__ == "__main__":
    main()
