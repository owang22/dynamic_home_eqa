#!/usr/bin/env python3
"""Build the Regime Search page: one panel per regime dir (per-day accuracy curves, all questions and the
moved-since-round half, stages shaded; per-stage table; per-class table for the timetable)."""
import collections, glob, html, json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from analyze import load, SHORT  # noqa
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UQ_ROOT = os.path.join(os.path.dirname(ROOT), "confidence_shift_2026-09-20", "uq", "regime")
UQ_AGENTS = [("mart_tt72", "#c94f7c", "e-detector + reset on timetable 3 d"), ("ocp_tt", "#b08a2e", "online conformal on timetable (answer = argmax)"),
             ("bma_tt", "#5a9e4b", "BMA over half-lives on timetable")]
AGENTS = [("timetable", "#4a7fb0", "timetable (2 h bins)"), ("timetable_hl3d", "#2f9bd6", "timetable, 3-day half-life"),
          ("mostfreq", "#3fae87", "most frequent"), ("mostfreq_hl3d", "#7fd0a8", "most frequent, 3-day half-life"), ("perpetua", "#8e7fd0", "Perpetua*"),
          ("periodic", "#e08a5a", "periodic"), ("lastseen", "#8e8a84", "last seen")]
STAGE_FILL = {"lead": "none", "return": "#cfe8d6", "shifts": "#f3d9a0", "sick": "#f3d9a0", "home": "#dfe6f2", "work": "none", "holiday": "#f3d9a0", "plain": "none"}
NAMES = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]


def collect(d, label="t03", uq=True):
    acc = collections.defaultdict(lambda: collections.defaultdict(lambda: [0, 0]))
    per_hh = collections.defaultdict(lambda: collections.defaultdict(lambda: [0, 0]))   # agent -> (hh, day, split) -> [n, ok]
    stage_of = {}; cls = collections.defaultdict(lambda: collections.defaultdict(lambda: [0, 0])); ndays = 0; day0 = "Monday"; n_hh = 0
    for bp in sorted(glob.glob(f"{d}/banks/hh_s*_{label}.jsonl")):
        hh = os.path.basename(bp).split("_" + label)[0]; h, qs = load(bp, 2); ndays = h["n_days"]; day0 = h.get("day0_weekday", "Monday"); n_hh += 1
        for dd, st in (h.get("stages") or {}).items(): stage_of[int(dd)] = st
        sources = [(f"{d}/classical/{hh}_{label}.jsonl", None)]
        if uq:
            sources += [(f"{UQ_ROOT}/{os.path.basename(d)}/{a}/{hh}_{label}.jsonl", a) for a, _, _ in UQ_AGENTS]
        for cp, forced in sources:
          if not os.path.exists(cp): continue
          for l in open(cp):
            r = json.loads(l); q = qs.get(r["question_id"]); ag = forced or SHORT.get(r["belief"])
            if not q or not ag: continue
            if ag not in {a for a, _, _ in AGENTS} | {a for a, _, _ in UQ_AGENTS}: continue
            for sp in (("moved" if q["moved"] else "still"), "all"):
                x = acc[ag][(q["day"], sp)]; x[0] += 1; x[1] += int(r["correct"])
                x = per_hh[ag][(hh, q["day"], sp)]; x[0] += 1; x[1] += int(r["correct"])
            st = stage_of.get(q["day"], "plain")
            x = cls[ag][(q["cls"], st)]; x[0] += 1; x[1] += int(r["correct"])
            x = acc[ag][("stage", st, "moved" if q["moved"] else "still")]; x[0] += 1; x[1] += int(r["correct"])
    # mean and sd across households of the per-household daily accuracy
    band = {}
    for ag in per_hh:
        by = collections.defaultdict(list)
        for (hh, d, sp), v in per_hh[ag].items():
            if v[0] >= 4: by[(d, sp)].append(100 * v[1] / v[0])
        for k, vals in by.items():
            m = sum(vals) / len(vals); sd = (sum((v - m) ** 2 for v in vals) / max(1, len(vals) - 1)) ** 0.5
            band[(ag, k[0], k[1])] = (m, sd, len(vals))
    return dict(acc=acc, stage_of=stage_of, cls=cls, ndays=ndays, day0=day0, n_hh=n_hh, band=band, per_hh=per_hh)


def svg(c, split):
    W, H, L, R, T, B = 760, 260, 42, 12, 14, 34; nd = c["ndays"]; days = list(range(1, nd))
    x = lambda d: L + (d - 1) * (W - L - R) / max(1, nd - 2); y = lambda v: T + (100 - v) * (H - T - B) / 100
    out = [f'<svg viewBox="0 0 {W} {H}" role="img" aria-label="accuracy per day, {split}">']
    # stage bands
    cur = None; start = None
    for d in days + [nd]:
        st = c["stage_of"].get(d, "plain") if d < nd else None
        if st != cur:
            if cur is not None and STAGE_FILL.get(cur, "#eee") != "none":
                out.append(f'<rect x="{x(start)-6:.1f}" y="{T}" width="{x(d-1)-x(start)+12:.1f}" height="{H-T-B}" fill="{STAGE_FILL.get(cur, "#eee")}" opacity="0.45"/>')
            if cur is not None:
                out.append(f'<text x="{(x(start)+x(d-1))/2:.1f}" y="{T+11}" text-anchor="middle" class="stg">{html.escape(cur)}</text>')
            cur, start = st, d
    for v in (0, 20, 40, 60, 80, 100):
        out.append(f'<line x1="{L}" x2="{W-R}" y1="{y(v):.1f}" y2="{y(v):.1f}" class="grid"/><text x="{L-6}" y="{y(v)+4:.1f}" text-anchor="end" class="tick">{v}</text>')
    i0 = NAMES.index(c["day0"])
    for d in days:
        wd = NAMES[(i0 + d) % 7][0]
        out.append(f'<text x="{x(d):.1f}" y="{H-B+14}" text-anchor="middle" class="tick">{wd}</text>')
        if d % 7 == 0 or d == 1: out.append(f'<text x="{x(d):.1f}" y="{H-B+27}" text-anchor="middle" class="tick">d{d}</text>')
    for ag, col, _ in AGENTS + [u for u in UQ_AGENTS if any(k[0] == u[0] for k in c["band"])]:
        bd = [(x(d),) + c["band"][(ag, d, split)][:2] for d in days if (ag, d, split) in c["band"]]
        if len(bd) >= 2:
            up = " ".join(f"{a:.1f},{y(min(100, m + sd)):.1f}" for a, m, sd in bd); lo = " ".join(f"{a:.1f},{y(max(0, m - sd)):.1f}" for a, m, sd in reversed(bd))
            out.append(f'<polygon points="{up} {lo}" fill="{col}" opacity="0.13" stroke="none"/>')
        pts = [(x(d), y(100 * c["acc"][ag][(d, split)][1] / c["acc"][ag][(d, split)][0])) for d in days if c["acc"][ag].get((d, split), [0, 0])[0]]
        if not pts: continue
        out.append(f'<polyline fill="none" stroke="{col}" stroke-width="2.2" points="{" ".join(f"{a:.1f},{b:.1f}" for a, b in pts)}"/>')
        out.append(f'<circle cx="{pts[-1][0]:.1f}" cy="{pts[-1][1]:.1f}" r="3" fill="{col}"/>')
    out.append("</svg>"); return "\n".join(out)


def table_stage(c):
    stages = []
    for d in range(1, c["ndays"]):
        st = c["stage_of"].get(d, "plain")
        if st not in stages: stages.append(st)
    rows = []
    for ag, col, name in AGENTS + [u for u in UQ_AGENTS if any(k[0] == u[0] for k in c["band"])]:
        cells = []
        for st in stages:
            m = c["acc"][ag].get(("stage", st, "moved"), [0, 0]); s = c["acc"][ag].get(("stage", st, "still"), [0, 0])
            a = [m[0] + s[0], m[1] + s[1]]
            # sd across households of each household's accuracy over the whole stage
            hh_acc = collections.defaultdict(lambda: [0, 0])
            for (hh, d, sp), v in c["per_hh"][ag].items():
                if sp == "all" and c["stage_of"].get(d, "plain") == st: hh_acc[hh][0] += v[0]; hh_acc[hh][1] += v[1]
            vals = [100 * v[1] / v[0] for v in hh_acc.values() if v[0]]
            mu = sum(vals) / len(vals) if vals else 0
            sd = ((sum((v - mu) ** 2 for v in vals) / max(1, len(vals) - 1)) ** 0.5) if len(vals) > 1 else 0
            cells.append(f"<td class=num>{100*a[1]/a[0]:.0f} <span class=muted>±{sd:.0f} ({100*m[1]/max(1,m[0]):.0f} / {100*s[1]/max(1,s[0]):.0f})</span></td>" if a[0] else "<td>-</td>")
        rows.append(f'<tr><td><i class=sw style="background:{col}"></i>{name}</td>{"".join(cells)}</tr>')
    return f'<table><thead><tr><th>agent</th>{"".join(f"<th>{html.escape(s)}</th>" for s in stages)}</tr></thead><tbody>{"".join(rows)}</tbody></table>'


def table_class(c, ag="timetable"):
    stages = []
    for d in range(1, c["ndays"]):
        st = c["stage_of"].get(d, "plain")
        if st not in stages: stages.append(st)
    classes = collections.defaultdict(int)
    for (k, st), v in c["cls"][ag].items(): classes[k] += v[0]
    rows = []
    for k in sorted(classes, key=lambda k: -classes[k]):
        cells = []
        for st in stages:
            v = c["cls"][ag].get((k, st), [0, 0])
            cells.append(f"<td class=num>{100*v[1]/v[0]:.0f} <span class=muted>({v[0]})</span></td>" if v[0] else "<td>-</td>")
        rows.append(f"<tr><td>{html.escape(k)}</td>{''.join(cells)}</tr>")
    return f'<table><thead><tr><th>class</th>{"".join(f"<th>{html.escape(s)}</th>" for s in stages)}</tr></thead><tbody>{"".join(rows)}</tbody></table>'


def main():
    regimes = [x.strip() for x in sys.argv[1].split(",")]; out = sys.argv[2]
    notes = open(f"{ROOT}/NOTES.md").read() if os.path.exists(f"{ROOT}/NOTES.md") else ""
    panels = []
    for rg in regimes:
        d = f"{ROOT}/{rg}"
        if not os.path.exists(f"{d}/banks"): continue
        c = collect(d)
        desc = ""
        cfgp = f"{d}/config.yaml"
        if os.path.exists(cfgp):
            desc = " ".join(l.strip("# ").strip() for l in open(cfgp) if l.startswith("#"))
        panels.append(f'''<section class="panel" id="{html.escape(rg)}">
<h2>{html.escape(rg)} <span class="muted small">{c["n_hh"]} households · {c["ndays"]-1} scored days</span></h2>
<p class="desc">{html.escape(desc)}</p>
<div class="charts"><div><h3>All questions</h3>{svg(c, "all")}</div><div><h3>Objects moved since the 03:00 round</h3>{svg(c, "moved")}</div></div>
<details open><summary>Per stage — accuracy % ± sd across households of each household's stage accuracy (moved / still)</summary><div class="tbl">{table_stage(c)}</div></details>
<details><summary>Per object class — timetable accuracy % by stage (n)</summary><div class="tbl">{table_class(c)}</div></details>
</section>''')
    legend = "".join(f'<span><i class="sw" style="background:{col}"></i>{name}</span>' for _, col, name in AGENTS + UQ_AGENTS)
    page = f'''<title>Regime Search</title>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,500&family=Source+Sans+3:wght@400;600&family=IBM+Plex+Mono:wght@400&display=swap">
<style>
:root{{--paper:#f7f5f0;--panel:#fff;--ink:#1c1a17;--muted:#6b6560;--line:#e3ded4;--grid:#ece8e0;--accent:#4a7fb0}}
@media (prefers-color-scheme: dark){{:root:not([data-theme="light"]){{--paper:#23262b;--panel:#2b2f35;--ink:#e4e2dc;--muted:#a3a49f;--line:#3a3f46;--grid:#33383f;--accent:#9ec5f0}}}}
:root[data-theme="dark"]{{--paper:#23262b;--panel:#2b2f35;--ink:#e4e2dc;--muted:#a3a49f;--line:#3a3f46;--grid:#33383f;--accent:#9ec5f0}}
*{{box-sizing:border-box}} body{{background:var(--paper);color:var(--ink);font-family:"Source Sans 3",system-ui,sans-serif;font-size:15px;line-height:1.45;margin:0}}
.wrap{{max-width:1100px;margin:0 auto;padding-inline:16px;padding-block:0 48px}}
h1,h2,h3{{font-family:Fraunces,Georgia,serif;font-weight:500;text-wrap:balance;margin:0}} h1{{font-size:30px;padding-block:16px 4px}} h2{{font-size:21px;margin-block:8px 4px}} h3{{font-size:14px;color:var(--muted);margin-bottom:4px}}
.muted{{color:var(--muted)}} .small{{font-size:13px;font-family:"Source Sans 3",sans-serif}}
.lead{{max-width:70ch;margin-block:6px 14px}}
.legend{{display:flex;gap:14px;flex-wrap:wrap;font-size:13px;margin-block:6px 18px}} .legend span{{display:inline-flex;align-items:center;gap:6px}}
.sw{{width:18px;height:3px;border-radius:2px;display:inline-block;margin-right:6px}}
.panel{{background:var(--panel);border:1px solid var(--line);border-radius:6px;padding:12px 14px;margin-block:14px}}
.desc{{max-width:80ch;color:var(--muted);font-size:13.5px;margin-block:0 8px}}
.charts{{display:grid;grid-template-columns:repeat(auto-fit,minmax(340px,1fr));gap:14px}}
svg{{display:block;max-width:100%;height:auto}} svg text{{font-family:"IBM Plex Mono",monospace;font-size:10.5px;fill:var(--muted)}} svg .grid{{stroke:var(--grid)}} svg .stg{{font-size:11px;fill:var(--ink)}}
details{{margin-top:10px}} summary{{cursor:pointer;color:var(--muted);font-size:13px}}
.tbl{{overflow-x:auto}} table{{border-collapse:collapse;font-size:13px;margin-top:6px}} th,td{{text-align:left;padding:4px 8px;border-bottom:1px solid var(--line)}} th{{color:var(--muted);font-weight:600;font-size:12px;text-transform:uppercase;letter-spacing:.04em}} td.num{{font-variant-numeric:tabular-nums}}
pre{{white-space:pre-wrap;font-size:12.5px;background:var(--panel);border:1px solid var(--line);padding:10px 12px;border-radius:6px;max-width:100ch}}
</style>
<div class="wrap">
<h1>Regime Search</h1>
<p class="lead">Finding a household regime where cheap learners climb visibly toward 80%, break sharply when the routine shifts, re-learn inside the new regime and break again on the return. Questions are "where is X" asked while X is in use; accuracy per day over 10 households; shaded bands are scripted stages; the translucent band around each line is ±1 standard deviation of the per-household daily accuracy across the households (an effect counts when it clears the band). No LLM methods in this loop.</p>
<div class="legend">{legend}<span><i class="sw" style="background:#f3d9a0;height:10px"></i>shift stage</span><span><i class="sw" style="background:#cfe8d6;height:10px"></i>return</span></div>
{"".join(panels)}
<section class="panel"><h2>Notes</h2><pre>{html.escape(notes)}</pre></section>
</div>'''
    open(out, "w").write(page); print("wrote", out, len(page) // 1024, "KB")


if __name__ == "__main__":
    main()
