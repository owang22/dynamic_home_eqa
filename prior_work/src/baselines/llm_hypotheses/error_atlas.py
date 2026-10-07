"""Error atlas: what each arm gets wrong, on which questions, and why.

Reads every arm of one run (``results/llm_hypotheses/runs/main/<household>__bank<seed>/``),
tags every wrong top-1 answer with an error type and the question's
attributes, and writes three things into the run's ``figures/``:

    errors.csv          one row per (arm, wrong question), every tag
    error_atlas.png     four static panels for the active named arms
    error_atlas.html    the interactive atlas: tick arms, error types,
                        objects, days, hours; pick a breakdown dimension;
                        see which questions only one arm got right

Error types (exact scoring: ON_PERSON and OUT_OF_HOUSE are different answers):

    missed away        truth OUT_OF_HOUSE, answer a spot in the house
    missed carried     truth ON_PERSON,    answer a spot in the house
    false away         truth in the house, answer OUT_OF_HOUSE or ON_PERSON
    carried/away swap  ON_PERSON and OUT_OF_HOUSE swapped either way
    wrong room         both in the house, different rooms
    wrong spot         same room, different spot (bed vs nightstand)

Rooms come from the household's ``program.yaml`` (``receptacles: [{id, room}]``);
if it cannot be found the suffix of the spot id (``_b1``, ``_k1`` ...) is used.

    python -m baselines.llm_hypotheses.error_atlas [--household hh_001__bank0]
"""

from __future__ import annotations

import argparse
import collections
import csv
import json
import math
import pathlib
import re
from typing import Any, Dict, List, Optional, Sequence, Tuple

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import yaml
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.patches import Patch

from baselines.household_analysis import GENERATED, MODEL_SLUG
from baselines.llm_hypotheses.analyze_tour_start import STUDY_DIR, load
from baselines.llm_hypotheses.story_figures import ARMS as STORY_ARMS
from baselines.types import DAY_SECONDS

AWAY = ("OUT_OF_HOUSE", "ON_PERSON")
DAY_NAMES = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]   # day 0 is a Monday
HOUR_BINS = [(0, 6, "night 0-6"), (6, 12, "morning 6-12"),
             (12, 18, "afternoon 12-18"), (18, 24, "evening 18-24")]

# Fixed order and colour per error type (categorical slots 1-6 of the
# reference palette; the order never changes with the data).
ERROR_TYPES: List[Tuple[str, str, str]] = [
    ("missed_away", "missed away", "#2a78d6"),
    ("missed_carried", "missed carried", "#eb6834"),
    ("false_away", "false away", "#1baf7a"),
    ("swap", "carried/away swap", "#eda100"),
    ("wrong_room", "wrong room", "#e87ba4"),
    ("wrong_spot", "right room, wrong spot", "#008300"),
]
ET_LABEL = {k: lab for k, lab, _ in ERROR_TYPES}
ET_COLOR = {k: c for k, _, c in ERROR_TYPES}
ET_ORDER = [k for k, _, _ in ERROR_TYPES]

SURF, INK, INK2, MUTED, GRID = "#fcfcfb", "#0b0b0b", "#52514e", "#898781", "#e1e0d9"
BLUES = LinearSegmentedColormap.from_list(
    "blues", [SURF, "#cde2fb", "#86b6ef", "#3987e5", "#1c5cab", "#0d366b"])
plt.rcParams.update({"font.size": 9, "axes.edgecolor": INK2, "axes.labelcolor": INK2,
                     "xtick.color": INK2, "ytick.color": INK2, "axes.spines.top": False,
                     "axes.spines.right": False, "figure.facecolor": SURF,
                     "axes.facecolor": SURF, "axes.titlelocation": "left",
                     "axes.titleweight": "bold", "axes.titlesize": 10})

# Labels: the story figure's names first, then the arms it does not cover.
LABEL: Dict[str, str] = {k: lab for k, lab, _, _ in STORY_ARMS}
LABEL.update({
    "active__longleaf__longleaf_named__f0": "treeLongLeaf, re-asking",
    "active__longleaf_fixed__longleaf_named__f0": "treeLongLeaf, fixed library",
    "active__log_reader_aided__named__f0": "log reader, aided",
    "active__tree_fixed__tree_named__f0__b0.5": "tree LLM, fixed roots, beta 0.5",
    "active__perpetua__f0": "perpetua (no LLM)",
})
# Default rows of the static figure, in this order.
PNG_ARMS = [
    "active__routine_posterior__f0",
    "active__longleaf__longleaf_named__f0",
    "active__longleaf_fixed__longleaf_named__f0",
    "active__tree__tree_named__f0",
    "active__tree_fixed__tree_named__f0",
    "active__graph_fixed__graph_named__f0",
    "active__llm__tour_named__f0",
    "active__llm_fixed__tour_named__f0",
    "active__log_reader_aided__named__f0",
    "active__log_reader__named__f0",
    "active__mostfreq72__f0",
]

_KIND_WORDS = {"llm": "flat LLM", "llm_fixed": "flat LLM, fixed set", "tree": "tree LLM, re-asking",
               "tree_fixed": "tree LLM, fixed roots", "graph_fixed": "graph LLM, fixed set",
               "longleaf": "treeLongLeaf, re-asking", "longleaf_fixed": "treeLongLeaf, fixed library",
               "log_reader": "log reader", "log_reader_aided": "log reader, aided",
               "mostfreq72": "most-frequent 72 h (no LLM)", "routine_posterior": "routine posterior",
               "perpetua": "perpetua (no LLM)"}


def label(key: str) -> str:
    """Readable arm name; falls back to parsing ``protocol__kind__condition[__f0]``."""
    if key in LABEL:
        return LABEL[key]
    parts = key.split("__")
    proto, kind = parts[0], parts[1] if len(parts) > 1 else ""
    name = _KIND_WORDS.get(kind, kind)
    cond = parts[2] if len(parts) > 2 and not parts[2].startswith("f") else ""
    if "anonymized" in cond:
        name += ", anonymized"
    extra = [p for p in parts[3:] if p.startswith("b")]
    if extra:
        name += f", beta {extra[0][1:]}"
    return f"{name} [{proto}]" if proto != "active" else name


# ---------------------------------------------------------------- rooms

def room_map(household: str, spots: Sequence[str]) -> Dict[str, str]:
    """spot id -> room name from program.yaml; suffix fallback (``desk_b1`` -> ``b``)."""
    rooms: Dict[str, str] = {}
    prog = GENERATED / MODEL_SLUG / household / "program.yaml"
    if prog.exists():
        try:
            recs = yaml.safe_load(prog.read_text()).get("receptacles") or []
            rooms = {r["id"]: r["room"] for r in recs if "id" in r and "room" in r}
        except Exception:
            rooms = {}
    for s in spots:
        if s in AWAY:
            rooms[s] = s.lower().replace("_", " ")
        elif s not in rooms:
            m = re.search(r"_([a-z]+)\d*$", s)
            rooms[s] = m.group(1) if m else "?"
    return rooms


# ---------------------------------------------------------------- tagging

def error_type(truth: str, pred: str, rooms: Dict[str, str]) -> Optional[str]:
    if pred == truth:
        return None
    t_away, p_away = truth in AWAY, pred in AWAY
    if t_away and p_away:
        return "swap"
    if t_away:
        return "missed_away" if truth == "OUT_OF_HOUSE" else "missed_carried"
    if p_away:
        return "false_away"
    return "wrong_room" if rooms.get(truth) != rooms.get(pred) else "wrong_spot"


def hour_bin(hour: float) -> str:
    for lo, hi, name in HOUR_BINS:
        if lo <= hour < hi:
            return name
    return HOUR_BINS[-1][2]


def tag_rows(arms: Dict[str, Dict[str, Any]], rooms: Dict[str, str]) -> None:
    """Adds pred / et / p_truth / hour / dow / weekend / kind to every row in place."""
    for key, arm in arms.items():
        for r in arm["rows"]:
            dist = r.get("dist") or {}
            r["pred"] = max(dist, key=dist.get) if dist else r["argmax"]
            r["et"] = error_type(r["truth"], r["pred"], rooms)
            r["p_truth"] = float(dist.get(r["truth"], 0.0))
            r["p_pred"] = float(dist.get(r["pred"], 0.0))
            r["hour"] = (r["t_query"] % DAY_SECONDS) / 3600.0
            r["dow"] = DAY_NAMES[r["day"] % 7]
            r["weekend"] = r["day"] % 7 >= 5
            r["kind"] = "shared" if "_shared_" in r["object_id"] else "personal"
            r["room_truth"] = rooms.get(r["truth"], "?")
            r["room_pred"] = rooms.get(r["pred"], "?")


def groups_of(study_dir: pathlib.Path, household: str) -> Dict[str, str]:
    """arm key -> group folder (active / passive / anonymized)."""
    out = {}
    for diag in (study_dir / household / "arms").rglob("diagnostics.json"):
        rel = diag.parent.relative_to(study_dir / household / "arms").parts
        out[diag.parent.name] = rel[0] if len(rel) > 1 else "ungrouped"
    return out


# ---------------------------------------------------------------- CSV

CSV_COLS = ["arm", "arm_label", "group", "question_id", "object", "object_kind", "tour_seen",
            "day", "weekday", "weekend", "hour", "hour_bin", "truth", "truth_room",
            "prediction", "prediction_room", "error_type", "p_truth", "p_prediction",
            "n_selected_arms_wrong"]


def write_csv(path: pathlib.Path, arms, groups: Dict[str, str], keys: Sequence[str]) -> int:
    wrong_count: Dict[str, int] = collections.Counter()
    for k in keys:
        for r in arms[k]["rows"]:
            if r["et"]:
                wrong_count[r["question_id"]] += 1
    n = 0
    with path.open("w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(CSV_COLS)
        for k in sorted(arms):
            for r in arms[k]["rows"]:
                if not r["et"]:
                    continue
                w.writerow([k, label(k), groups.get(k, ""), r["question_id"], r["object_id"],
                            r["kind"], not r.get("tour_absent", False), r["day"], r["dow"],
                            r["weekend"], f"{r['hour']:.2f}", hour_bin(r["hour"]), r["truth"],
                            r["room_truth"], r["pred"], r["room_pred"], ET_LABEL[r["et"]],
                            f"{r['p_truth']:.4f}", f"{r['p_pred']:.4f}",
                            wrong_count.get(r["question_id"], 0)])
                n += 1
    return n


# ---------------------------------------------------------------- figure

def _heat(ax, M: np.ndarray, rows: Sequence[str], cols: Sequence[str], text: np.ndarray,
          vmax: float, cbar_label: str) -> None:
    im = ax.imshow(M, cmap=BLUES, vmin=0, vmax=vmax, aspect="auto")
    ax.set_xticks(range(len(cols))); ax.set_xticklabels(cols, rotation=30, ha="right")
    ax.set_yticks(range(len(rows))); ax.set_yticklabels(rows)
    ax.tick_params(length=0)
    for s in ax.spines.values():
        s.set_visible(False)
    for i in range(M.shape[0]):
        for j in range(M.shape[1]):
            ax.text(j, i, text[i, j], ha="center", va="center", fontsize=7,
                    color="white" if M[i, j] > 0.55 * vmax else INK)
    cb = plt.colorbar(im, ax=ax, fraction=0.03, pad=0.02)
    cb.set_label(cbar_label); cb.outline.set_visible(False)


def unique_outcomes(arms, keys: Sequence[str]):
    """Questions exactly one of ``keys`` got right (winner, others' modal error
    type) and exactly one got wrong (loser, its error type)."""
    by_q: Dict[str, Dict[str, Optional[str]]] = collections.defaultdict(dict)
    for k in keys:
        for r in arms[k]["rows"]:
            by_q[r["question_id"]][k] = r["et"]
    only_right = collections.Counter(); only_wrong = collections.Counter()
    for q, ets in by_q.items():
        if len(ets) != len(keys):
            continue
        wrong = [k for k, e in ets.items() if e]
        if len(wrong) == len(keys) - 1:
            winner = next(k for k in keys if k not in wrong)
            mode = collections.Counter(ets[k] for k in wrong).most_common(1)[0][0]
            only_right[(winner, mode)] += 1
        elif len(wrong) == 1:
            only_wrong[(wrong[0], ets[wrong[0]])] += 1
    return only_right, only_wrong


def figure(arms, keys: Sequence[str], out: pathlib.Path, household: str) -> None:
    keys = [k for k in keys if k in arms]
    n_q = len(arms[keys[0]]["rows"])
    labels = [label(k) for k in keys]
    fig = plt.figure(figsize=(17, 24))
    gs = fig.add_gridspec(5, 2, height_ratios=[1.0, 1.0, 0.25, 1.9, 1.0], hspace=0.55, wspace=0.08)  # row 2 is a spacer

    # A: arms x error types, rate per question with its standard error
    ax = fig.add_subplot(gs[0, :])
    cols = ["any error"] + [ET_LABEL[e] for e in ET_ORDER]
    M = np.zeros((len(keys), len(cols))); T = np.empty_like(M, dtype=object)
    for i, k in enumerate(keys):
        cnt = collections.Counter(r["et"] for r in arms[k]["rows"] if r["et"])
        vals = [sum(cnt.values())] + [cnt.get(e, 0) for e in ET_ORDER]
        for j, v in enumerate(vals):
            p = v / n_q; se = math.sqrt(p * (1 - p) / n_q)
            M[i, j] = 100 * p; T[i, j] = f"{100 * p:.1f} ±{100 * se:.1f}"
    _heat(ax, M, labels, cols, T, max(M.max(), 1e-9), "% of questions")
    ax.set_title(f"A  Error types per arm (% of {n_q} questions, ± one standard error)")

    # B: arms x objects, error rate; objects sorted by mean error rate
    ax = fig.add_subplot(gs[1, :])
    objs = sorted({r["object_id"] for r in arms[keys[0]]["rows"]})
    absent = set(arms[keys[0]]["diag"].get("tour_absent_objects") or [])
    E = np.zeros((len(keys), len(objs))); N = np.zeros(len(objs))
    for i, k in enumerate(keys):
        by = collections.defaultdict(list)
        for r in arms[k]["rows"]:
            by[r["object_id"]].append(1 if r["et"] else 0)
        for j, o in enumerate(objs):
            E[i, j] = 100 * np.mean(by[o]) if by[o] else 0; N[j] = len(by[o])
    order = np.argsort(-E.mean(axis=0))
    E = E[:, order]; objs = [objs[j] for j in order]; N = N[order]
    cols = [f"{o.replace('_mara', '').replace('_shared', ' (shared)')}{' †' if o in absent else ''} ({int(n)})"
            for o, n in zip(objs, N)]
    T = np.array([[f"{v:.0f}" for v in row] for row in E], dtype=object)
    _heat(ax, E, labels, cols, T, max(E.max(), 1e-9), "% wrong")
    ax.set_xticklabels(cols, rotation=60, ha="right")
    ax.set_title("B  Error rate per object (% wrong; † never seen on the tour; n questions in brackets; "
                 "SE of a cell ≈ ±6 points at n=70)")

    # C: stacked error counts per day, one small panel per arm
    inner = gs[3, :].subgridspec(math.ceil(len(keys) / 3), 3, hspace=0.6, wspace=0.25)
    days = sorted({r["day"] for r in arms[keys[0]]["rows"]})
    ymax = 1
    per_arm = {}
    for k in keys:
        cnt = collections.defaultdict(collections.Counter)
        for r in arms[k]["rows"]:
            if r["et"]:
                cnt[r["day"]][r["et"]] += 1
        per_arm[k] = cnt
        ymax = max(ymax, max((sum(c.values()) for c in cnt.values()), default=0))
    for idx, k in enumerate(keys):
        ax = fig.add_subplot(inner[idx // 3, idx % 3])
        bottom = np.zeros(len(days))
        for e in ET_ORDER:
            h = np.array([per_arm[k][d].get(e, 0) for d in days])
            ax.bar(days, h, bottom=bottom, color=ET_COLOR[e], width=0.8, edgecolor=SURF, lw=0.6)
            bottom += h
        for d in days:
            if d % 7 >= 5:
                ax.axvspan(d - 0.5, d + 0.5, color=GRID, zorder=0)
        ax.set_ylim(0, ymax * 1.05); ax.set_xlim(days[0] - 0.6, days[-1] + 0.6)
        ax.set_title(label(k)); ax.tick_params(length=0)
        ax.grid(axis="y", color=GRID, lw=0.8); ax.set_axisbelow(True)
        if idx % 3 == 0:
            ax.set_ylabel("wrong answers")
        if idx // 3 == (len(keys) - 1) // 3:
            ax.set_xlabel("day (grey = weekend)")
    pos = gs[3, :].get_position(fig)
    fig.text(pos.x0, pos.y1 + 0.035, "C  Wrong answers per day by error type (counts, not estimates; "
             f"≈{n_q // len(days)} questions a day)", fontsize=10, fontweight="bold", ha="left")
    fig.legend(handles=[Patch(color=ET_COLOR[e], label=ET_LABEL[e]) for e in ET_ORDER],
               loc="lower left", bbox_to_anchor=(pos.x0, pos.y1 + 0.012), ncol=6, frameon=False, fontsize=8)

    # D / E: questions exactly one arm got right / wrong (shared row labels)
    only_right, only_wrong = unique_outcomes(arms, keys)
    for col, (title, table) in enumerate([
            ("D  Questions ONLY this arm got right (colour: what the others said)", only_right),
            ("E  Questions ONLY this arm got wrong (colour: its error)", only_wrong)]):
        ax = fig.add_subplot(gs[4, col])
        ys = np.arange(len(keys))[::-1]
        left = np.zeros(len(keys))
        for e in ET_ORDER:
            w = np.array([table.get((k, e), 0) for k in keys])
            ax.barh(ys, w, left=left, color=ET_COLOR[e], height=0.7, edgecolor=SURF, lw=0.6)
            left += w
        xmax = max(left.max() * 1.25, 1)
        for y, tot in zip(ys, left):
            if tot:
                ax.text(tot + xmax * 0.01, y, f"{int(tot)}", va="center", fontsize=8, color=INK2)
        ax.set_yticks(ys); ax.set_yticklabels(labels if col == 0 else []); ax.tick_params(length=0)
        ax.grid(axis="x", color=GRID, lw=0.8); ax.set_axisbelow(True)
        ax.set_xlabel("questions (counts over the same question set)"); ax.set_title(title)
        ax.set_xlim(0, xmax)
    fig.suptitle(f"Error atlas · {household} · {len(keys)} active arms · exact scoring", x=0.02,
                 ha="left", fontsize=13, fontweight="bold", y=0.985)
    fig.savefig(out, dpi=140, bbox_inches="tight")
    plt.close(fig)


# ---------------------------------------------------------------- HTML

def html_payload(arms, groups: Dict[str, str], rooms: Dict[str, str], household: str) -> dict:
    ref = next(iter(arms.values()))["rows"]
    q_index = {r["question_id"]: i for i, r in enumerate(ref)}
    spots = sorted({r["truth"] for r in ref} | {r["pred"] for a in arms.values() for r in a["rows"]})
    sp = {s: i for i, s in enumerate(spots)}
    et_code = {e: i + 1 for i, e in enumerate(ET_ORDER)}
    questions = [{"q": r["question_id"], "o": r["object_id"], "k": r["kind"],
                  "d": r["day"], "h": round(r["hour"], 2), "t": sp[r["truth"]],
                  "a": bool(r.get("tour_absent", False))} for r in ref]
    out_arms = []
    order = {k: i for i, k in enumerate(PNG_ARMS)}
    for k in sorted(arms, key=lambda k: (groups.get(k, "z") != "active", order.get(k, 99), k)):
        pred = [0] * len(ref); et = [0] * len(ref); pt = [0.0] * len(ref)
        for r in arms[k]["rows"]:
            i = q_index.get(r["question_id"])
            if i is None:
                continue
            pred[i] = sp[r["pred"]]; et[i] = et_code[r["et"]] if r["et"] else 0
            pt[i] = round(r["p_truth"], 3)
        out_arms.append({"key": k, "label": label(k), "group": groups.get(k, "ungrouped"),
                         "pred": pred, "et": et, "pt": pt,
                         "partial": len(arms[k]["rows"]) != len(ref)})
    return {"household": household, "spots": spots, "rooms": [rooms.get(s, "?") for s in spots],
            "error_types": [{"key": k, "label": lab, "color": c} for k, lab, c in ERROR_TYPES],
            "questions": questions, "arms": out_arms, "day_names": DAY_NAMES,
            "hour_bins": [[lo, hi, name] for lo, hi, name in HOUR_BINS]}


def write_html(path: pathlib.Path, payload: dict) -> None:
    data = json.dumps(payload, separators=(",", ":"))
    path.write_text(HTML_TEMPLATE.replace("__DATA__", data).replace("__HOUSEHOLD__", payload["household"]))


HTML_TEMPLATE = r"""<title>Error Atlas __HOUSEHOLD__</title>
<style>
:root{color-scheme:light;--page:#f9f9f7;--surface:#fcfcfb;--ink:#0b0b0b;--ink2:#52514e;--muted:#898781;
--grid:#e1e0d9;--line:#c3c2b7;--ring:rgba(11,11,11,.10);--accent:#2a78d6;--heat0:#fcfcfb;--heatmid:#5598e7;--heat1:#0d366b;
--wash:rgba(42,120,214,.08)}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){color-scheme:dark;--page:#0d0d0d;--surface:#1a1a19;
--ink:#fff;--ink2:#c3c2b7;--muted:#898781;--grid:#2c2c2a;--line:#383835;--ring:rgba(255,255,255,.10);--accent:#3987e5;
--heat0:#1a1a19;--heatmid:#256abf;--heat1:#9ec5f4;--wash:rgba(57,135,229,.14)}}
:root[data-theme="dark"]{color-scheme:dark;--page:#0d0d0d;--surface:#1a1a19;--ink:#fff;--ink2:#c3c2b7;--muted:#898781;
--grid:#2c2c2a;--line:#383835;--ring:rgba(255,255,255,.10);--accent:#3987e5;--heat0:#1a1a19;--heatmid:#256abf;--heat1:#9ec5f4;--wash:rgba(57,135,229,.14)}
*{box-sizing:border-box}
body{margin:0;background:var(--page);color:var(--ink);font:14px/1.45 system-ui,-apple-system,"Segoe UI",sans-serif;padding-block:0 32px}
.wrap{display:grid;grid-template-columns:290px minmax(0,1fr);gap:0;min-height:100vh}
aside{background:var(--surface);border-right:1px solid var(--grid);padding:16px;position:sticky;top:env(safe-area-inset-top,0px);
height:100vh;overflow-y:auto}
main{padding:16px 24px;min-width:0}
h1{font-size:18px;margin:0 0 2px;letter-spacing:-.01em}
.sub{color:var(--muted);font-size:12px;margin-bottom:14px}
h2{font-size:13px;margin:22px 0 8px;text-transform:uppercase;letter-spacing:.06em;color:var(--ink2);font-weight:600}
aside h2:first-of-type{margin-top:6px}
.btns{display:flex;gap:6px;flex-wrap:wrap;margin-bottom:6px}
button.mini{font:11px system-ui,sans-serif;padding:2px 8px;border:1px solid var(--line);background:transparent;color:var(--ink2);
border-radius:3px;cursor:pointer}
button.mini:hover{background:var(--wash)}
label.row{display:flex;gap:8px;align-items:center;padding:2px 0;cursor:pointer;font-size:13px}
label.row input{margin:0;accent-color:var(--accent)}
label.row .sw{width:10px;height:10px;border-radius:2px;flex:none}
label.row .dim{color:var(--muted);font-size:11px;margin-left:auto;font-variant-numeric:tabular-nums}
.grp{font-size:11px;color:var(--muted);margin:8px 0 2px;text-transform:uppercase;letter-spacing:.05em}
.objs{max-height:260px;overflow-y:auto;border-top:1px solid var(--grid);border-bottom:1px solid var(--grid);padding:4px 0}
.range{display:flex;gap:6px;align-items:center;font-size:12px;color:var(--ink2)}
.range input{width:56px;font:12px system-ui;padding:2px 4px;border:1px solid var(--line);background:var(--surface);color:var(--ink);border-radius:3px}
select{font:13px system-ui;padding:3px 6px;border:1px solid var(--line);background:var(--surface);color:var(--ink);border-radius:3px}
.kpis{display:flex;gap:18px;flex-wrap:wrap;margin:6px 0 18px}
.kpi{min-width:120px}
.kpi b{display:block;font-size:22px;font-weight:600;letter-spacing:-.01em}
.kpi span{font-size:12px;color:var(--muted)}
section.panel{background:var(--surface);border:1px solid var(--ring);border-radius:4px;padding:14px 16px;margin-bottom:18px}
section.panel h3{margin:0 0 2px;font-size:14px}
section.panel .note{font-size:12px;color:var(--muted);margin-bottom:10px}
.toolbar{display:flex;gap:14px;align-items:center;flex-wrap:wrap;font-size:12px;color:var(--ink2);margin-bottom:8px}
.scroll{overflow-x:auto}
svg{display:block;max-width:100%}
svg text{fill:var(--ink2);font-family:system-ui,sans-serif}
svg text.val{fill:var(--ink);font-variant-numeric:tabular-nums}
svg text.val.inv{fill:#fff}
svg .cell:hover{stroke:var(--ink);stroke-width:1.5}
.legend{display:flex;gap:14px;flex-wrap:wrap;font-size:12px;color:var(--ink2);margin:6px 0}
.legend i{display:inline-block;width:10px;height:10px;border-radius:2px;margin-right:5px;vertical-align:-1px}
#tip{position:fixed;pointer-events:none;background:var(--ink);color:var(--page);font-size:12px;padding:6px 9px;border-radius:3px;
max-width:320px;z-index:9;display:none;line-height:1.35}
table{border-collapse:collapse;width:100%;font-size:12px}
th,td{text-align:left;padding:4px 8px;border-bottom:1px solid var(--grid);white-space:nowrap}
th{color:var(--muted);font-weight:600;position:sticky;top:0;background:var(--surface)}
td.num{font-variant-numeric:tabular-nums;text-align:right}
.pill{display:inline-block;padding:0 6px;border-radius:9px;font-size:11px;color:#fff}
.small{font-size:12px;color:var(--muted)}
input:focus-visible,select:focus-visible,button:focus-visible{outline:2px solid var(--accent);outline-offset:1px}
@media (max-width:820px){.wrap{grid-template-columns:1fr}aside{position:static;height:auto;border-right:0;border-bottom:1px solid var(--grid)}main{padding:16px}}
@media (prefers-reduced-motion:no-preference){svg .cell{transition:opacity .12s}}
</style>
<div class="wrap">
<aside>
  <h1>Error atlas</h1>
  <div class="sub">__HOUSEHOLD__ · exact scoring · top-1 answers</div>

  <h2>Arms</h2>
  <div class="btns"><button class="mini" data-act="arms:active">active named</button><button class="mini" data-act="arms:all">all</button><button class="mini" data-act="arms:none">none</button></div>
  <div id="arms"></div>

  <h2>Error types</h2>
  <div class="btns"><button class="mini" data-act="et:all">all</button><button class="mini" data-act="et:none">none</button></div>
  <div id="ets"></div>

  <h2>Objects</h2>
  <div class="btns"><button class="mini" data-act="obj:all">all</button><button class="mini" data-act="obj:none">none</button><button class="mini" data-act="obj:absent">tour never saw</button><button class="mini" data-act="obj:seen">tour saw</button><button class="mini" data-act="obj:shared">shared</button><button class="mini" data-act="obj:personal">personal</button></div>
  <div class="objs" id="objs"></div>

  <h2>Time</h2>
  <div class="range">days <input type="number" id="d0" min="0" value="0"> to <input type="number" id="d1" min="0" value="27"></div>
  <div id="dows" style="margin-top:6px"></div>
  <div id="hours" style="margin-top:6px"></div>

  <h2>Questions</h2>
  <label class="row"><input type="checkbox" id="onlyDisagree"> only questions the ticked arms disagree on</label>
  <label class="row"><input type="checkbox" id="onlyWrong"> only questions some ticked arm got wrong</label>
</aside>

<main>
  <div class="kpis" id="kpis"></div>

  <section class="panel">
    <h3>Error types per arm</h3>
    <div class="note">Share of the filtered questions each ticked arm gets wrong, by error type. Cells show percent ± one standard error (binomial). Hover for counts.</div>
    <div class="toolbar"><label><input type="radio" name="unitA" value="pct" checked> % of questions</label><label><input type="radio" name="unitA" value="cnt"> counts</label></div>
    <div class="scroll" id="heatA"></div>
  </section>

  <section class="panel">
    <h3>Error rate by <select id="dim"></select></h3>
    <div class="note">Rows are the values of the chosen dimension among the filtered questions; the number in brackets is how many questions sit in that row. Each cell is the share that arm got wrong (ticked error types only), with its standard error in the tooltip. Rows sort by mean error rate.</div>
    <div class="toolbar"><label><input type="checkbox" id="dimStack"> colour cells by dominant error type instead of rate</label></div>
    <div class="scroll" id="heatB"></div>
  </section>

  <section class="panel">
    <h3>Wrong answers per day</h3>
    <div class="note">Counts, not estimates (≈ the same number of questions every day, so the bars compare directly). Weekend days are shaded.</div>
    <div class="legend" id="legendC"></div>
    <div class="scroll" id="daily"></div>
  </section>

  <section class="panel">
    <h3>Questions only one arm got right — and only one got wrong</h3>
    <div class="note">Over the filtered questions all ticked arms answered. Left: the lone correct arm, coloured by what the others answered (their most common error type). Right: the lone wrong arm, coloured by its own error. Counts.</div>
    <div class="scroll" id="unique"></div>
  </section>

  <section class="panel">
    <h3>Filtered errors <span class="small" id="tblCount"></span></h3>
    <div class="note">One row per (arm, wrong answer). p(truth) is the probability the arm gave the true location. Sorted by day, then question.</div>
    <div class="toolbar"><label>show <select id="tblN"><option>100</option><option>300</option><option>1000</option><option value="all">all</option></select> rows</label></div>
    <div class="scroll" style="max-height:520px;overflow-y:auto"><table id="tbl"></table></div>
  </section>
</main>
</div>
<div id="tip"></div>
<script>
const D = __DATA__;
const ET = D.error_types, NET = ET.length;
const etColor = i => ET[i-1].color, etLabel = i => ET[i-1].label;
const Q = D.questions, NQ = Q.length;
const objects = [...new Set(Q.map(q=>q.o))].sort();
const absentObjs = new Set(Q.filter(q=>q.a).map(q=>q.o));
const kindOf = {}; Q.forEach(q=>kindOf[q.o]=q.k);
const maxDay = Math.max(...Q.map(q=>q.d));
const hourBin = h => { for (const [lo,hi,name] of D.hour_bins) if (h>=lo && h<hi) return name; return D.hour_bins[D.hour_bins.length-1][2]; };
const $ = s => document.querySelector(s);
const el = (t,a={},...ch)=>{const e=document.createElement(t);for(const k in a){if(k==='class')e.className=a[k];else if(k.startsWith('on'))e.addEventListener(k.slice(2),a[k]);else e.setAttribute(k,a[k]);}for(const c of ch)e.append(c);return e;};
const svgEl=(t,a={})=>{const e=document.createElementNS('http://www.w3.org/2000/svg',t);for(const k in a)e.setAttribute(k,a[k]);return e;};
const fmtPct=x=>(100*x).toFixed(1);
const se=(p,n)=>n?Math.sqrt(p*(1-p)/n):0;

// ---- state -------------------------------------------------------------
const S = { arms:new Set(), et:new Set(ET.map((_,i)=>i+1)), obj:new Set(objects), d0:0, d1:maxDay,
            dow:new Set([0,1,2,3,4,5,6]), hours:new Set(D.hour_bins.map(h=>h[2])), disagree:false, wrong:false,
            unitA:'pct', dim:'object', dimStack:false, tblN:100 };
try { const s = JSON.parse(localStorage.getItem('error-atlas-'+D.household)||'null'); if (s) { for (const k of ['arms','et','obj','dow','hours']) if (s[k]) S[k]=new Set(s[k]); for (const k of ['d0','d1','disagree','wrong','unitA','dim','dimStack','tblN']) if (s[k]!==undefined) S[k]=s[k]; } } catch(e){}
if (!S.arms.size) D.arms.filter(a=>a.group==='active' && !/anonym/.test(a.key)).forEach(a=>S.arms.add(a.key));
function persist(){ try{ localStorage.setItem('error-atlas-'+D.household, JSON.stringify({arms:[...S.arms],et:[...S.et],obj:[...S.obj],dow:[...S.dow],hours:[...S.hours],d0:S.d0,d1:S.d1,disagree:S.disagree,wrong:S.wrong,unitA:S.unitA,dim:S.dim,dimStack:S.dimStack,tblN:S.tblN})); }catch(e){} }

// ---- sidebar -----------------------------------------------------------
function checkRow(id, checked, labelNode, onchange, extra){ const inp=el('input',{type:'checkbox',id}); inp.checked=checked; inp.addEventListener('change',()=>{onchange(inp.checked);update();}); const l=el('label',{class:'row'},inp,labelNode); if(extra) l.append(extra); return l; }
function buildSidebar(){
  const armsBox=$('#arms'); armsBox.innerHTML='';
  for (const g of ['active','passive','anonymized','ungrouped']) {
    const list=D.arms.filter(a=>a.group===g); if(!list.length) continue;
    armsBox.append(el('div',{class:'grp'},g));
    for (const a of list) armsBox.append(checkRow('arm-'+a.key, S.arms.has(a.key), document.createTextNode(a.label+(a.partial?' (partial)':'')), v=>v?S.arms.add(a.key):S.arms.delete(a.key)));
  }
  const etBox=$('#ets'); etBox.innerHTML='';
  ET.forEach((e,i)=>{ const sw=el('span',{class:'sw'}); sw.style.background=e.color; const lab=el('span',{},sw,' '+e.label); etBox.append(checkRow('et-'+e.key,S.et.has(i+1),lab,v=>v?S.et.add(i+1):S.et.delete(i+1))); });
  const objBox=$('#objs'); objBox.innerHTML='';
  for (const o of objects) objBox.append(checkRow('obj-'+o,S.obj.has(o),document.createTextNode(o),v=>v?S.obj.add(o):S.obj.delete(o), el('span',{class:'dim'},absentObjs.has(o)?'unseen':'')));
  const dowBox=$('#dows'); dowBox.innerHTML='';
  D.day_names.forEach((n,i)=>{ const inp=el('input',{type:'checkbox',id:'dow-'+n}); inp.checked=S.dow.has(i); inp.addEventListener('change',()=>{inp.checked?S.dow.add(i):S.dow.delete(i);update();}); dowBox.append(el('label',{class:'row',style:'display:inline-flex;margin-right:8px'},inp,n)); });
  const hBox=$('#hours'); hBox.innerHTML='';
  for (const [,,name] of D.hour_bins) hBox.append(checkRow('h-'+name,S.hours.has(name),document.createTextNode(name),v=>v?S.hours.add(name):S.hours.delete(name)));
  $('#d0').value=S.d0; $('#d1').value=S.d1; $('#d0').max=maxDay; $('#d1').max=maxDay;
  $('#d0').addEventListener('change',e=>{S.d0=+e.target.value;update();}); $('#d1').addEventListener('change',e=>{S.d1=+e.target.value;update();});
  $('#onlyDisagree').checked=S.disagree; $('#onlyDisagree').addEventListener('change',e=>{S.disagree=e.target.checked;update();});
  $('#onlyWrong').checked=S.wrong; $('#onlyWrong').addEventListener('change',e=>{S.wrong=e.target.checked;update();});
  document.querySelectorAll('button.mini').forEach(b=>b.addEventListener('click',()=>act(b.dataset.act)));
  document.querySelectorAll('input[name=unitA]').forEach(r=>{ r.checked=(r.value===S.unitA); r.addEventListener('change',()=>{S.unitA=r.value;update();}); });
  const dim=$('#dim'); dim.innerHTML='';
  for (const [k,lab] of Object.entries(DIMS)) dim.append(el('option',{value:k},lab));
  dim.value=S.dim; dim.addEventListener('change',()=>{S.dim=dim.value;update();});
  $('#dimStack').checked=S.dimStack; $('#dimStack').addEventListener('change',e=>{S.dimStack=e.target.checked;update();});
  $('#tblN').value=String(S.tblN); $('#tblN').addEventListener('change',e=>{S.tblN=e.target.value==='all'?'all':+e.target.value;update();});
  $('#legendC').innerHTML=''; ET.forEach(e=>{ const i=el('i'); i.style.background=e.color; $('#legendC').append(el('span',{},i,e.label)); });
}
function act(a){
  const [what,how]=a.split(':');
  if (what==='arms'){ S.arms.clear(); if(how==='all') D.arms.forEach(x=>S.arms.add(x.key)); if(how==='active') D.arms.filter(x=>x.group==='active'&&!/anonym/.test(x.key)).forEach(x=>S.arms.add(x.key)); }
  if (what==='et'){ S.et.clear(); if(how==='all') ET.forEach((_,i)=>S.et.add(i+1)); }
  if (what==='obj'){ S.obj.clear(); for (const o of objects){ if(how==='all'||(how==='absent'&&absentObjs.has(o))||(how==='seen'&&!absentObjs.has(o))||(how==='shared'&&kindOf[o]==='shared')||(how==='personal'&&kindOf[o]==='personal')) S.obj.add(o);} }
  buildSidebar(); update();
}

// ---- dimensions --------------------------------------------------------
const DIMS = { object:'object', room:'true room', truth:'true location', hour:'hour of day', dow:'weekday', week:'week', day:'day', seen:'tour saw it', kind:'personal / shared' };
function dimValue(q){
  switch(S.dim){
    case 'object': return q.o;
    case 'room': return D.rooms[q.t];
    case 'truth': return D.spots[q.t];
    case 'hour': return hourBin(q.h);
    case 'dow': return D.day_names[q.d%7];
    case 'week': return 'week '+(Math.floor(q.d/7)+1);
    case 'day': return 'day '+String(q.d).padStart(2,'0');
    case 'seen': return q.a?'tour never saw it':'tour saw it';
    case 'kind': return q.k;
  }
}

// ---- filtering ---------------------------------------------------------
function filtered(){
  const arms=D.arms.filter(a=>S.arms.has(a.key));
  const idx=[];
  for (let i=0;i<NQ;i++){
    const q=Q[i];
    if (!S.obj.has(q.o)) continue;
    if (q.d<S.d0||q.d>S.d1) continue;
    if (!S.dow.has(q.d%7)) continue;
    if (!S.hours.has(hourBin(q.h))) continue;
    if (S.disagree && arms.length>1){ const p=arms[0].pred[i]; if (arms.every(a=>a.pred[i]===p)) continue; }
    if (S.wrong && !arms.some(a=>a.et[i])) continue;
    idx.push(i);
  }
  return {arms, idx};
}
const isErr = (a,i) => a.et[i] && S.et.has(a.et[i]);

// ---- tooltip -----------------------------------------------------------
const tip=$('#tip');
function hover(node, html){ node.addEventListener('mousemove',e=>{tip.innerHTML=html();tip.style.display='block';tip.style.left=Math.min(e.clientX+14,window.innerWidth-330)+'px';tip.style.top=(e.clientY+14)+'px';}); node.addEventListener('mouseleave',()=>tip.style.display='none'); }

// ---- heat drawing ------------------------------------------------------
function heatColor(t){ // one-hue sequential: surface -> mid blue -> the theme's far end
  const cs=getComputedStyle(document.documentElement); const a=hex(cs.getPropertyValue('--heat0').trim()), m=hex(cs.getPropertyValue('--heatmid').trim()), b=hex(cs.getPropertyValue('--heat1').trim());
  const [p,q,u]=t<0.5?[a,m,t*2]:[m,b,(t-0.5)*2]; const c=p.map((v,i)=>Math.round(v+(q[i]-v)*u)); return `rgb(${c[0]},${c[1]},${c[2]})`; }
function hex(h){ h=h.replace('#',''); if(h.length===3) h=h.split('').map(c=>c+c).join(''); return [0,2,4].map(i=>parseInt(h.slice(i,i+2),16)); }
function drawHeat(container, rows, cols, cellFn, opts){
  // cellFn(i,j) -> {v (0..1 for colour), text, tip, color?}
  const maxLen=Math.max(...cols.map(c=>c.length));
  const L=opts.leftW||220, T=Math.min(230, 20+maxLen*4.6), cw=opts.cw||64, ch=opts.ch||26;
  const W=L+cols.length*cw+T*0.8, H=T+rows.length*ch+10;
  const svg=svgEl('svg',{viewBox:`0 0 ${W} ${H}`,width:W,height:H});
  cols.forEach((c,j)=>{ const x=L+j*cw+cw/2; const t=svgEl('text',{x,y:T-6,'font-size':11,'text-anchor':'start',transform:`rotate(-45 ${x} ${T-6})`}); t.textContent=c; svg.append(t); });
  rows.forEach((r,i)=>{ const t=svgEl('text',{x:L-8,y:T+i*ch+ch/2+4,'font-size':11,'text-anchor':'end'}); t.textContent=r.length>34?r.slice(0,33)+'…':r; svg.append(t);
    cols.forEach((c,j)=>{ const cell=cellFn(i,j); const g=svgEl('g',{class:'cell'});
      const rect=svgEl('rect',{x:L+j*cw+1,y:T+i*ch+1,width:cw-2,height:ch-2,rx:2,fill:cell.color||heatColor(cell.v)}); g.append(rect);
      if (cell.text!==undefined){ const tx=svgEl('text',{x:L+j*cw+cw/2,y:T+i*ch+ch/2+4,'font-size':10,'text-anchor':'middle',class:'val'+((cell.color?cell.v>0.3:cell.v>0.55)?' inv':'')}); tx.textContent=cell.text; g.append(tx); }
      hover(g, ()=>cell.tip); svg.append(g); }); });
  container.innerHTML=''; container.append(svg);
}

// ---- panels ------------------------------------------------------------
function panelKPIs(F){
  const box=$('#kpis'); box.innerHTML='';
  const n=F.idx.length; const tot=F.arms.reduce((s,a)=>s+F.idx.filter(i=>isErr(a,i)).length,0);
  const uniq=new Set(); for (const i of F.idx) for (const a of F.arms) if (isErr(a,i)) uniq.add(i);
  const k=[[n,'questions in view'],[F.arms.length,'arms ticked'],[tot,'wrong answers'],[uniq.size,'questions some arm gets wrong'],[n?fmtPct(F.arms.length?tot/(n*F.arms.length):0)+'%':'–','mean error rate']];
  for (const [v,l] of k) box.append(el('div',{class:'kpi'},el('b',{},String(v)),el('span',{},l)));
}
function panelA(F){
  const n=F.idx.length; const cols=['any ticked error',...ET.filter((_,i)=>S.et.has(i+1)).map(e=>e.label)]; const etIds=ET.map((_,i)=>i+1).filter(i=>S.et.has(i));
  const counts=F.arms.map(a=>{ const c=new Array(NET+1).fill(0); for (const i of F.idx) if (isErr(a,i)) { c[a.et[i]]++; c[0]++; } return c; });
  let vmax=1e-9; counts.forEach(c=>{ vmax=Math.max(vmax,c[0]); });
  drawHeat($('#heatA'), F.arms.map(a=>a.label), cols, (i,j)=>{ const e=j===0?0:etIds[j-1]; const c=counts[i][e]; const p=n?c/n:0;
    const text=S.unitA==='pct'?fmtPct(p)+'±'+fmtPct(se(p,n)):String(c);
    return {v:vmax?c/vmax:0,text,tip:`<b>${F.arms[i].label}</b><br>${cols[j]}: ${c} of ${n} (${fmtPct(p)}% ± ${fmtPct(se(p,n))})`}; }, {cw:84});
}
function panelB(F){
  const groups=new Map(); for (const i of F.idx){ const v=dimValue(Q[i]); if(!groups.has(v)) groups.set(v,[]); groups.get(v).push(i); }
  let rows=[...groups.keys()];
  const stats=new Map(); for (const v of rows){ const ids=groups.get(v); stats.set(v, F.arms.map(a=>{ const c=new Array(NET+1).fill(0); for (const i of ids) if (isErr(a,i)) { c[a.et[i]]++; c[0]++; } return c; })); }
  const mean=v=>{ const st=stats.get(v); const n=groups.get(v).length; return st.length?st.reduce((s,c)=>s+c[0],0)/(n*st.length):0; };
  if (S.dim==='day'||S.dim==='week'||S.dim==='hour'||S.dim==='dow') rows.sort((a,b)=>{ if(S.dim==='dow') return D.day_names.indexOf(a)-D.day_names.indexOf(b); if (S.dim==='hour') return D.hour_bins.findIndex(h=>h[2]===a)-D.hour_bins.findIndex(h=>h[2]===b); return a<b?-1:1; });
  else rows.sort((a,b)=>mean(b)-mean(a));
  const rowLabels=rows.map(v=>`${v}${S.dim==='object'&&absentObjs.has(v)?' †':''} (${groups.get(v).length})`);
  drawHeat($('#heatB'), rowLabels, F.arms.map(a=>a.label), (i,j)=>{ const v=rows[i]; const n=groups.get(v).length; const c=stats.get(v)[j]; const p=c[0]/n;
    let color, text=Math.round(100*p)+'', dom=0;
    if (S.dimStack){ for (let e=1;e<=NET;e++) if (c[e]>c[dom]||dom===0) dom=c[e]?e:dom; if (dom){ color=etColor(dom); } else color='var(--surface)'; }
    const parts=[]; for (let e=1;e<=NET;e++) if (c[e]) parts.push(`${etLabel(e)}: ${c[e]}`);
    return {v:p,color,text,tip:`<b>${F.arms[j].label}</b> · ${v}<br>${c[0]} of ${n} wrong (${fmtPct(p)}% ± ${fmtPct(se(p,n))})<br>${parts.join('<br>')||'no errors'}`}; }, {cw:64, leftW:230});
}
function panelC(F){
  const box=$('#daily'); box.innerHTML='';
  const days=[]; for (let d=S.d0; d<=S.d1; d++) days.push(d);
  const per=F.arms.map(a=>{ const m=new Map(days.map(d=>[d,new Array(NET+1).fill(0)])); for (const i of F.idx) if (isErr(a,i)) { const c=m.get(Q[i].d); c[a.et[i]]++; c[0]++; } return m; });
  let ymax=1; per.forEach(m=>m.forEach(c=>ymax=Math.max(ymax,c[0])));
  const pw=Math.max(260, Math.min(420, days.length*12)), ph=120, L=34, B=22, T=20, bw=(pw-L-6)/days.length;
  const cols=Math.max(1,Math.floor(Math.min(box.clientWidth||900, 1400)/(pw+16)));
  const W=cols*(pw+16), rowsN=Math.ceil(F.arms.length/cols), H=rowsN*(ph+T+B+12);
  const svg=svgEl('svg',{viewBox:`0 0 ${W} ${H}`,width:W,height:H});
  F.arms.forEach((a,ai)=>{ const ox=(ai%cols)*(pw+16), oy=Math.floor(ai/cols)*(ph+T+B+12);
    const title=svgEl('text',{x:ox,y:oy+12,'font-size':11,'font-weight':600}); title.textContent=a.label; svg.append(title);
    for (const k of [0,0.5,1]){ const y=oy+T+ph-k*ph; svg.append(svgEl('line',{x1:ox+L,x2:ox+pw,y1:y,y2:y,stroke:'var(--grid)'})); const t=svgEl('text',{x:ox+L-4,y:y+4,'font-size':9,'text-anchor':'end'}); t.textContent=Math.round(k*ymax); svg.append(t); }
    days.forEach((d,di)=>{ const x=ox+L+di*bw; if (d%7>=5) svg.append(svgEl('rect',{x,y:oy+T,width:bw,height:ph,fill:'var(--grid)',opacity:.6}));
      const c=per[ai].get(d); let acc=0; const g=svgEl('g',{class:'cell'});
      for (let e=1;e<=NET;e++){ if(!c[e]) continue; const h=c[e]/ymax*ph; g.append(svgEl('rect',{x:x+1,y:oy+T+ph-(acc+c[e])/ymax*ph,width:Math.max(1,bw-2),height:Math.max(0,h-1),fill:etColor(e)})); acc+=c[e]; }
      if (!c[0]) g.append(svgEl('rect',{x:x+1,y:oy+T,width:Math.max(1,bw-2),height:ph,fill:'transparent'}));
      hover(g,()=>`<b>${a.label}</b> · day ${d} (${D.day_names[d%7]})<br>${c[0]} wrong<br>`+ET.map((e,k)=>c[k+1]?`${e.label}: ${c[k+1]}`:'').filter(Boolean).join('<br>')); svg.append(g);
      if (di%7===0){ const t=svgEl('text',{x:x+bw/2,y:oy+T+ph+13,'font-size':9,'text-anchor':'middle'}); t.textContent=d; svg.append(t); } });
  });
  box.append(svg);
}
function panelD(F){
  const box=$('#unique'); box.innerHTML='';
  const A=F.arms; if (A.length<2){ box.append(el('div',{class:'small'},'Tick at least two arms.')); return; }
  const right=new Map(), wrong=new Map(); A.forEach(a=>{right.set(a.key,new Array(NET+1).fill(0)); wrong.set(a.key,new Array(NET+1).fill(0));});
  for (const i of F.idx){ if (A.some(a=>a.partial && a.pt[i]===0 && !a.et[i] && a.pred[i]===0)) {}
    const w=A.filter(a=>a.et[i]);
    if (w.length===A.length-1){ const win=A.find(a=>!a.et[i]); const cnt=new Array(NET+1).fill(0); w.forEach(a=>cnt[a.et[i]]++); let m=1; for(let e=2;e<=NET;e++) if(cnt[e]>cnt[m]) m=e; if (S.et.has(m)) right.get(win.key)[m]++; }
    else if (w.length===1 && S.et.has(w[0].et[i])) wrong.get(w[0].key)[w[0].et[i]]++; }
  const draw=(title, table)=>{ const L=210, bh=22, pw=300, W=L+pw+50, H=A.length*bh+30; let vmax=1; A.forEach(a=>vmax=Math.max(vmax,table.get(a.key).slice(1).reduce((s,x)=>s+x,0)));
    const svg=svgEl('svg',{viewBox:`0 0 ${W} ${H}`,width:W,height:H}); const t=svgEl('text',{x:0,y:12,'font-size':12,'font-weight':600}); t.textContent=title; svg.append(t);
    A.forEach((a,i)=>{ const y=24+i*bh; const lab=svgEl('text',{x:L-8,y:y+bh/2+4,'font-size':11,'text-anchor':'end'}); lab.textContent=a.label.length>30?a.label.slice(0,29)+'…':a.label; svg.append(lab);
      const c=table.get(a.key); let acc=0; const g=svgEl('g',{class:'cell'});
      for (let e=1;e<=NET;e++){ if(!c[e]) continue; const w=c[e]/vmax*pw; g.append(svgEl('rect',{x:L+acc/vmax*pw,y:y+3,width:Math.max(1,w-1),height:bh-6,rx:2,fill:etColor(e)})); acc+=c[e]; }
      const n=svgEl('text',{x:L+acc/vmax*pw+5,y:y+bh/2+4,'font-size':11,class:'val'}); n.textContent=acc||''; svg.append(g); svg.append(n);
      hover(g,()=>`<b>${a.label}</b><br>${acc} questions<br>`+ET.map((e,k)=>c[k+1]?`${e.label}: ${c[k+1]}`:'').filter(Boolean).join('<br>')); });
    return svg; };
  const wrap=el('div',{style:'display:flex;gap:24px;flex-wrap:wrap'}); wrap.append(draw('only this arm right (colour = what the others said)',right), draw('only this arm wrong (colour = its error)',wrong)); box.append(wrap);
}
function panelTable(F){
  const rows=[]; for (const i of F.idx) for (const a of F.arms) if (isErr(a,i)) rows.push([i,a]);
  $('#tblCount').textContent=`(${rows.length} rows)`;
  const tbl=$('#tbl'); tbl.innerHTML='';
  const head=el('tr'); for (const h of ['question','object','day','weekday','hour','tour saw','arm','truth','answer','error','p(truth)']) head.append(el('th',{},h)); tbl.append(head);
  const N=S.tblN==='all'?rows.length:Math.min(rows.length,S.tblN);
  for (let r=0;r<N;r++){ const [i,a]=rows[r]; const q=Q[i]; const tr=el('tr'); const pill=el('span',{class:'pill'},etLabel(a.et[i])); pill.style.background=etColor(a.et[i]);
    const cells=[q.q,q.o,String(q.d),D.day_names[q.d%7],(Math.floor(q.h)+':'+String(Math.round((q.h%1)*60)).padStart(2,'0')),q.a?'no':'yes',a.label,D.spots[q.t],D.spots[a.pred[i]],pill,a.pt[i].toFixed(3)];
    cells.forEach((c,k)=>tr.append(el('td',{class:(k===2||k===10)?'num':''},c))); tbl.append(tr); }
  if (N<rows.length) tbl.append(el('tr',{},el('td',{colspan:'11',class:'small'},`… ${rows.length-N} more; raise the row count or narrow the filters`)));
}

function update(){ persist(); const F=filtered(); panelKPIs(F); panelA(F); panelB(F); panelC(F); panelD(F); panelTable(F); }
buildSidebar(); update();
window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change',update);
</script>
"""


# ---------------------------------------------------------------- main

def main(argv: Optional[Sequence[str]] = None) -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--household", default="hh_001__bank0", help="run folder under runs/main")
    ap.add_argument("--study-dir", type=pathlib.Path, default=STUDY_DIR / "main")
    ap.add_argument("--arms", nargs="*", default=None,
                    help="arm keys for the static PNG (default: the active named arms)")
    args = ap.parse_args(argv)

    arms = load(args.household, args.study_dir)
    if not arms:
        raise SystemExit(f"no arms under {args.study_dir / args.household}")
    groups = groups_of(args.study_dir, args.household)
    household = next(iter(arms.values()))["diag"].get("household") or args.household.split("__")[0]
    spots = {r["truth"] for a in arms.values() for r in a["rows"]} | \
            {max(r["dist"], key=r["dist"].get) for a in arms.values() for r in a["rows"] if r.get("dist")}
    rooms = room_map(household, sorted(spots))
    tag_rows(arms, rooms)

    fig_dir = args.study_dir / args.household / "figures"
    fig_dir.mkdir(exist_ok=True)
    png_arms = args.arms or [k for k in PNG_ARMS if k in arms]
    n_err = write_csv(fig_dir / "errors.csv", arms, groups, png_arms)
    figure(arms, png_arms, fig_dir / "error_atlas.png", args.household)
    write_html(fig_dir / "error_atlas.html", html_payload(arms, groups, rooms, args.household))

    n_q = len(next(iter(arms.values()))["rows"])
    print(f"{len(arms)} arms, {n_q} questions each, {n_err} tagged errors")
    print(f"  {fig_dir / 'errors.csv'}\n  {fig_dir / 'error_atlas.png'}\n  {fig_dir / 'error_atlas.html'}")
    for k in png_arms:
        cnt = collections.Counter(r["et"] for r in arms[k]["rows"] if r["et"])
        tot = sum(cnt.values())
        print(f"  {label(k):38s} wrong {tot:4d} ({100 * tot / n_q:4.1f}%)  " +
              "  ".join(f"{ET_LABEL[e]} {cnt.get(e, 0)}" for e in ET_ORDER))


if __name__ == "__main__":
    main()
