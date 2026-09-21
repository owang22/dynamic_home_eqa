"""Assemble the follow-on results page: a live chart over the per-day aggregates, the lists, the notes.

    python3 -m baselines.patrol.followon_page --root results/confidence_shift_2026-09-20 --out results/.../followon/page.html

The chart reads DATA (per line, per split, per group, per day, pooled and
per household: confidence, accuracy, n, and for the conformal lines set
size, coverage, threshold), built by :func:`followon_figs.collect` for each
patrol density.
"""
from __future__ import annotations

import argparse
import datetime as dt
import html
import json
import pathlib
import re
from typing import List

from baselines.patrol.affected_llm import score as score_lists
from baselines.patrol.followon_figs import KINDS, KIND_COLOR, collect


def md_table(md: str) -> str:
    """Markdown pipe tables and headings -> HTML (just enough for our notes)."""
    out: List[str] = []
    rows: List[List[str]] = []

    def flush():
        nonlocal rows
        if not rows:
            return
        head, body = rows[0], rows[2:] if len(rows) > 1 and set(rows[1][0]) <= set("-: ") else rows[1:]
        out.append('<div class="tbl"><table><thead><tr>' + "".join(f"<th>{inline(c)}</th>" for c in head) + "</tr></thead><tbody>")
        for r in body:
            out.append("<tr>" + "".join(f"<td>{inline(c)}</td>" for c in r) + "</tr>")
        out.append("</tbody></table></div>")
        rows = []

    for line in md.splitlines():
        if line.startswith("|"):
            rows.append([c.strip() for c in line.strip().strip("|").split("|")])
            continue
        flush()
        if line.startswith("### "):
            out.append(f"<h4>{inline(line[4:])}</h4>")
        elif line.startswith("## "):
            out.append(f"<h3>{inline(line[3:])}</h3>")
        elif line.startswith("# "):
            continue
        elif re.match(r"^\d+\. ", line):
            out.append(f"<p class='note'>{inline(line)}</p>")
        elif line.startswith("- "):
            out.append(f"<p class='note'>{inline(line[2:])}</p>")
        elif line.strip():
            out.append(f"<p>{inline(line)}</p>")
    flush()
    return "\n".join(out)


def inline(s: str) -> str:
    s = html.escape(s)
    s = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", s)
    s = re.sub(r"`(.+?)`", r"<code>\1</code>", s)
    return s


CSS = """
:root{ --paper:#f7f5f0; --panel:#ffffff; --ink:#1c1a17; --muted:#6b6560; --line:#e3ded4; --grid:#ece8e0; --tag:#eee9df;
  --aff:#2a78d6; --ok:#1a9e6f; --bad:#c9463d; --warn:#c98500; --shade:rgba(242,196,109,.28); }
@media (prefers-color-scheme: dark){ :root:not([data-theme="light"]){ --paper:#211f1b; --panel:#2a2723; --ink:#e6e1d8; --muted:#a8a196; --line:#3c3831; --grid:#353129; --tag:#33302a; --aff:#9ec5f0; --ok:#8fd3b6; --bad:#e79c9c; --warn:#e3cf8a; --shade:rgba(242,196,109,.16); } }
:root[data-theme="dark"]{ --paper:#211f1b; --panel:#2a2723; --ink:#e6e1d8; --muted:#a8a196; --line:#3c3831; --grid:#353129; --tag:#33302a; --aff:#9ec5f0; --ok:#8fd3b6; --bad:#e79c9c; --warn:#e3cf8a; --shade:rgba(242,196,109,.16); }
*{box-sizing:border-box}
body{background:var(--paper);color:var(--ink);font-family:"Source Sans 3",system-ui,sans-serif;font-size:15px;line-height:1.5;margin:0}
.wrap{max-width:1140px;margin:0 auto;padding-inline:16px;padding-block:0 56px}
h1,h2,h3,h4{font-family:Fraunces,Georgia,serif;font-weight:500;text-wrap:balance;margin:0}
h1{font-size:30px;line-height:1.1} h2{font-size:22px;margin-block:40px 10px} h3{font-size:17px;margin-block:22px 6px} h4{font-size:15px;margin-block:14px 4px}
.bar{position:sticky;top:env(safe-area-inset-top,0px);z-index:5;background:var(--paper);border-bottom:1px solid var(--line);padding-block:10px;display:flex;flex-wrap:wrap;gap:8px 18px;align-items:baseline}
.muted{color:var(--muted)}
.lead{max-width:68ch;margin-block:18px 6px}
p{max-width:78ch} .note{max-width:88ch;margin-block:6px}
code,.mono{font-family:"IBM Plex Mono",ui-monospace,monospace;font-size:12.5px} code{background:var(--tag);padding:0 4px;border-radius:3px}
.tbl{overflow-x:auto;margin-block:8px}
table{border-collapse:collapse;width:100%;font-size:13px}
th,td{text-align:left;padding:5px 8px;border-bottom:1px solid var(--line);vertical-align:top}
th{font-weight:600;color:var(--muted);font-size:11.5px;letter-spacing:.04em;text-transform:uppercase}
td{font-variant-numeric:tabular-nums} td.num,th.num{text-align:right}
details{margin-block:8px} summary{cursor:pointer;font-weight:600}
a{color:var(--ink)}
button.lnk{background:none;border:0;color:var(--ink);text-decoration:underline;cursor:pointer;font:inherit;padding:0;text-align:left}
button.lnk:focus-visible,button.close:focus-visible,.ctl input:focus-visible{outline:2px solid var(--aff);outline-offset:2px}
dialog{background:var(--panel);color:var(--ink);border:1px solid var(--line);border-radius:6px;max-width:min(680px,92vw);padding:18px 20px}
dialog::backdrop{background:rgba(0,0,0,.35)} dialog .msg{font-style:italic;font-size:16px}
button.close{margin-top:12px;font:inherit;padding:4px 12px;border:1px solid var(--line);border-radius:4px;background:var(--tag);color:var(--ink);cursor:pointer}
.chart{background:var(--panel);border:1px solid var(--line);border-radius:6px;padding:12px 12px 6px;margin-block:12px}
.ctl{display:flex;flex-wrap:wrap;gap:6px 14px;align-items:center;font-size:13px;margin-block:4px}
.ctl .grp{display:flex;flex-wrap:wrap;gap:4px 10px;align-items:center;padding:4px 8px;border:1px solid var(--line);border-radius:4px}
.ctl .grp b{font-weight:600;color:var(--muted);font-size:11.5px;letter-spacing:.04em;text-transform:uppercase;margin-right:4px}
.ctl label{display:inline-flex;align-items:center;gap:5px;cursor:pointer;white-space:nowrap}
.ctl input{margin:0}
.ctl select{font:inherit;font-size:13px;padding:2px 6px;background:var(--panel);color:var(--ink);border:1px solid var(--line);border-radius:4px}
.sw{width:16px;height:3px;border-radius:2px;display:inline-block}
.sw.dash{background:repeating-linear-gradient(90deg,var(--ink) 0 4px,transparent 4px 7px)}
.sw.solid{background:var(--ink)}
svg{display:block;max-width:100%;height:auto}
svg text{font-family:"IBM Plex Mono",monospace;font-size:10.5px;fill:var(--muted)}
svg .ttl{font-family:"Source Sans 3",sans-serif;font-size:12.5px;fill:var(--ink)}
.grid-panels{display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:10px}
.tip{position:fixed;pointer-events:none;background:var(--ink);color:var(--paper);padding:6px 9px;border-radius:4px;font-size:12.5px;max-width:340px;z-index:9;display:none;line-height:1.35}
@media (max-width:640px){ .grid-panels{grid-template-columns:1fr} }
"""

JS = r"""
const DAYN = {1:'Wed',2:'Thu',3:'Fri',4:'Sat',5:'Sun',6:'Mon',7:'Tue'};
const METRICS = {conf:'confidence', acc:'accuracy', set:'prediction-set size (spots)', cov:'coverage (target 0.9)', n:'questions that day'};
const state = {tag:'p8', split:'affected', metric:'conf', hh:'all', lines:new Set(DEFAULT_LINES), groups:new Set(['affected','unaffected']), kinds:new Set(['event_moved','weekend_moved','stayed_put','after_shift','plain'])};
const $ = s => document.querySelector(s);
const tip = $('#tip');
function esc(s){ return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/"/g,'&quot;'); }
function households(){ const hs = new Set(); for (const d of Object.values(DATA[state.tag])) for (const h of Object.keys(d.by_household)) hs.add(h); return [...hs].sort((a,b)=>parseInt(a.slice(4))-parseInt(b.slice(4))); }

function buildControls(){
  const data = DATA[state.tag];
  const lines = $('#lines'); lines.innerHTML = '<b>lines</b>';
  for (const name of Object.keys(data)){
    const d = data[name];
    const on = state.lines.has(name);
    lines.insertAdjacentHTML('beforeend', `<label title="${esc(d.arm)} arm, ${d.households} households"><input type="checkbox" data-line="${esc(name)}" ${on?'checked':''}><span class="sw" style="background:${d.color}"></span>${esc(name)} <span class="muted">(${d.households})</span></label>`);
  }
  lines.querySelectorAll('input').forEach(i => i.addEventListener('change', e => { const n=e.target.dataset.line; e.target.checked ? state.lines.add(n) : state.lines.delete(n); draw(); }));
  const g = $('#groups'); g.innerHTML = '<b>show</b>';
  if (state.split === 'affected'){
    for (const [k, cls] of [['affected','solid'],['unaffected','dash'],['all','solid']]){
      g.insertAdjacentHTML('beforeend', `<label><input type="checkbox" data-g="${k}" ${state.groups.has(k)?'checked':''}><span class="sw ${cls}"></span>${k}${k==='all'?' questions':''}</label>`);
    }
    g.querySelectorAll('input').forEach(i => i.addEventListener('change', e => { const n=e.target.dataset.g; e.target.checked ? state.groups.add(n) : state.groups.delete(n); draw(); }));
  } else {
    for (const k of KINDS){
      g.insertAdjacentHTML('beforeend', `<label><input type="checkbox" data-k="${k}" ${state.kinds.has(k)?'checked':''}><span class="sw" style="background:${KIND_COLOR[k]}"></span>${k.replace('_',' ')}</label>`);
    }
    g.querySelectorAll('input').forEach(i => i.addEventListener('change', e => { const n=e.target.dataset.k; e.target.checked ? state.kinds.add(n) : state.kinds.delete(n); draw(); }));
  }
  const sel = $('#hh'); const cur = state.hh; sel.innerHTML = '<option value="all">all households (pooled)</option>' + households().map(h => `<option value="${h}">${h}</option>`).join('');
  sel.value = [...sel.options].some(o => o.value === cur) ? cur : 'all'; state.hh = sel.value;
}

function yDomain(metric, series){
  if (metric === 'conf' || metric === 'acc' || metric === 'cov') return [0, 1];
  let m = 0; for (const s of series) for (const p of s.pts) m = Math.max(m, p.v);
  return [0, Math.ceil(m * 1.1 / 5) * 5 || 1];
}

function panelSVG(series, metric, opts){
  const W = opts.w || 900, H = opts.h || 340, L = 44, R = 12, T = opts.title ? 26 : 12, B = 26;
  const [y0, y1] = yDomain(metric, series);
  const x = d => L + (d - 1) / 6 * (W - L - R);
  const y = v => T + (1 - (v - y0) / (y1 - y0)) * (H - T - B);
  let s = `<svg viewBox="0 0 ${W} ${H}" role="img" aria-label="${esc(METRICS[metric])} per day">`;
  s += `<rect x="${x(3.5)}" y="${T}" width="${x(5.5)-x(3.5)}" height="${H-T-B}" fill="var(--shade)"/>`;
  const ticks = (metric==='conf'||metric==='acc'||metric==='cov') ? [0,.2,.4,.6,.8,1] : [0, y1/4, y1/2, 3*y1/4, y1];
  for (const t of ticks){ s += `<line x1="${L}" x2="${W-R}" y1="${y(t)}" y2="${y(t)}" stroke="var(--grid)"/><text x="${L-6}" y="${y(t)+3.5}" text-anchor="end">${(metric==='n'||metric==='set')?Math.round(t):t.toFixed(1)}</text>`; }
  if (metric === 'cov') s += `<line x1="${L}" x2="${W-R}" y1="${y(0.9)}" y2="${y(0.9)}" stroke="var(--muted)" stroke-dasharray="2 3"/>`;
  for (let d = 1; d <= 7; d++) s += `<text x="${x(d)}" y="${H-8}" text-anchor="middle">${DAYN[d]}</text>`;
  if (opts.title) s += `<text class="ttl" x="${L}" y="16">${esc(opts.title)}</text>`;
  for (const sr of series){
    const pts = sr.pts.filter(p => p.v !== undefined && p.n >= (opts.minN||1));
    if (!pts.length) continue;
    const path = pts.map((p,i) => `${i?'L':'M'}${x(p.d).toFixed(1)},${y(p.v).toFixed(1)}`).join(' ');
    s += `<path d="${path}" fill="none" stroke="${sr.color}" stroke-width="2" ${sr.dash?'stroke-dasharray="6 4"':''} stroke-linejoin="round"/>`;
    for (const p of pts){
      const val = metric==='n' ? p.v : (metric==='set' ? p.v.toFixed(1) : p.v.toFixed(3));
      const info = `${sr.label} · ${DAYN[p.d]} · ${METRICS[metric]} ${val} · n=${p.n}${p.extra||''}`;
      s += `<circle cx="${x(p.d)}" cy="${y(p.v)}" r="3.5" fill="${sr.color}" stroke="var(--panel)" stroke-width="1.5"/><circle cx="${x(p.d)}" cy="${y(p.v)}" r="10" fill="transparent" data-tip="${esc(info)}"/>`;
    }
  }
  s += '</svg>';
  return s;
}

function seriesFor(name, split, group, metric){
  const d = DATA[state.tag][name]; if (!d) return null;
  const src = state.hh === 'all' ? d.series : (d.by_household[state.hh] || null); if (!src) return null;
  const g = (src[split]||{})[group]; if (!g) return null;
  const pts = [];
  for (let day = 1; day <= 7; day++){
    const p = g[String(day)]; if (!p) continue;
    const v = p[metric]; if (v === undefined) continue;
    let extra = '';
    if (p.set !== undefined) extra = ` · set ${p.set.toFixed(1)} · coverage ${p.cov.toFixed(2)}`;
    pts.push({d: day, v, n: p.n, extra});
  }
  return pts;
}

function draw(){
  const host = $('#plot'); const data = DATA[state.tag];
  const metric = state.metric;
  $('#metric-note').textContent = (METRIC_NOTES[metric] || '') + (state.hh === 'all' ? '' : ` Showing ${state.hh} only: per-day points rest on a handful of questions.`);
  const minN = state.hh === 'all' ? (state.split === 'kind' ? 8 : 1) : 1;
  if (state.split === 'affected'){
    const series = [];
    for (const name of Object.keys(data)){
      if (!state.lines.has(name)) continue;
      for (const g of ['affected','unaffected','all']){
        if (!state.groups.has(g)) continue;
        const pts = seriesFor(name, 'affected', g, metric); if (!pts) continue;
        series.push({label: `${name}, ${g}`, color: data[name].color, dash: g === 'unaffected', pts});
      }
    }
    host.className = '';
    host.innerHTML = series.length ? panelSVG(series, metric, {w: 960, h: 380, minN}) : '<p class="muted">nothing selected</p>';
  } else {
    host.className = 'grid-panels';
    let out = '';
    for (const name of Object.keys(data)){
      if (!state.lines.has(name)) continue;
      const series = [];
      for (const k of KINDS){
        if (!state.kinds.has(k)) continue;
        const pts = seriesFor(name, 'kind', k, metric); if (!pts) continue;
        series.push({label: `${name}, ${k.replace('_',' ')}`, color: KIND_COLOR[k], dash: false, pts});
      }
      out += `<div>${panelSVG(series, metric, {w: 420, h: 260, title: `${name} (${state.hh === 'all' ? data[name].households + ' households' : state.hh})`, minN})}</div>`;
    }
    host.innerHTML = out || '<p class="muted">nothing selected</p>';
  }
  host.querySelectorAll('[data-tip]').forEach(el => {
    el.addEventListener('mouseenter', () => { tip.textContent = el.dataset.tip; tip.style.display = 'block'; });
    el.addEventListener('mousemove', e => { tip.style.left = Math.min(e.clientX + 14, window.innerWidth - 330) + 'px'; tip.style.top = (e.clientY + 14) + 'px'; });
    el.addEventListener('mouseleave', () => { tip.style.display = 'none'; });
  });
}
document.querySelectorAll('input[name=tag]').forEach(i => i.addEventListener('change', e => { state.tag = e.target.value; buildControls(); draw(); }));
document.querySelectorAll('input[name=split]').forEach(i => i.addEventListener('change', e => { state.split = e.target.value; buildControls(); draw(); }));
document.querySelectorAll('input[name=metric]').forEach(i => i.addEventListener('change', e => { state.metric = e.target.value; draw(); }));
$('#hh').addEventListener('change', e => { state.hh = e.target.value; draw(); });
document.querySelectorAll('button[data-dialog]').forEach(b => b.addEventListener('click', () => { const d = document.getElementById(b.dataset.dialog); if (d && d.showModal) d.showModal(); else if (d) d.setAttribute('open',''); }));
buildControls(); draw();
"""

METRIC_NOTES = {
    "conf": "Confidence = the belief's probability on its answer; for the conformal lines, 1 / prediction-set size (one spot in the set = 1, ten spots = 0.1). Hover a point for the set size and coverage.",
    "acc": "Share of questions answered with the true spot.",
    "set": "Conformal lines only: how many spots the 90% set holds (out of ~38).",
    "cov": "Conformal lines only: how often the true spot was inside the set; the dotted line is the 0.9 target.",
    "n": "How many questions of that group were asked that day.",
}
DEFAULT_LINES = ["most frequent", "BOCPD reset (told)", "most frequent + affected list", "conformal most frequent", "Perpetua*", "mixture (told)"]


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", type=pathlib.Path, required=True)
    ap.add_argument("--out", type=pathlib.Path, required=True)
    ap.add_argument("--ledger", default="https://claude.ai/artifact/KJPMaPPbgv4UmeVakrDSTA")
    a = ap.parse_args(argv)
    F = a.root / "followon"
    now = dt.datetime.now().strftime("%d %b %H:%M")

    def read(p: pathlib.Path) -> str:
        return p.read_text() if p.exists() else ""

    data = {tag: collect(a.root, tag) for tag in ("p8", "p2")}
    shares = read(F / "affected/shares_p8.md")
    problems = read(F / "problems_found.md")
    openq = read(F / "open_questions.md")
    spend = read(F / "spend_log.md")
    checks = {tag: read(F / tag / "checks.md") for tag in ("p8", "p2")}
    tables = {tag: read(F / tag / "figs/tables.md") for tag in ("p8", "p2")}

    # the affected lists, with the full message and the model's reasoning behind a click
    lists_path = F / "affected_llm/lists.jsonl"
    labels = [json.loads(l) for l in (F / "affected/labels_p8.jsonl").open()]
    list_html = '<p class="muted">no lists yet</p>'
    if lists_path.exists():
        lists = [json.loads(l) for l in lists_path.open()]
        rows, pooled = score_lists(lists, labels)
        by_key = {(l["household"], l["day_index"]): l for l in lists}
        f = lambda v: "-" if v is None else f"{v:.2f}"
        parts = [f'<p>Pooled over {len(lists)} message days: precision {pooled["micro_precision"]:.2f}, recall {pooled["micro_recall"]:.2f} '
                 f'(over the objects questioned that day). Click a message to read it in full with the model\'s reasoning and its list.</p>',
                 '<div class="tbl"><table><thead><tr><th>household</th><th>day</th><th>message</th><th class="num">listed</th><th class="num">questioned</th>'
                 '<th class="num">true affected</th><th class="num">precision</th><th class="num">recall</th><th>missed</th><th>false</th></tr></thead><tbody>']
        dialogs = []
        for i, r in enumerate(rows):
            L = by_key[(r["household"], r["day_index"])]
            did = f"m{i}"
            parts.append(f'<tr><td>{r["household"]}</td><td>{r["day_index"]}</td>'
                         f'<td><button class="lnk" data-dialog="{did}">{html.escape(r["message"][:70])}{"…" if len(r["message"]) > 70 else ""}</button></td>'
                         f'<td class="num">{r["n_listed"]}</td><td class="num">{r["n_listed_questioned"]}</td><td class="num">{r["n_true"]}</td>'
                         f'<td class="num">{f(r["precision"])}</td><td class="num">{f(r["recall"])}</td>'
                         f'<td>{html.escape(", ".join(r["missed"]))}</td><td>{html.escape(", ".join(r["false"]))}</td></tr>')
            dialogs.append(f'<dialog id="{did}"><form method="dialog"><h3>{r["household"]}, day {r["day_index"]} ({html.escape(L.get("weekday", ""))})</h3>'
                           f'<p class="msg">“{html.escape(r["message"])}”</p>'
                           f'<h4>Why</h4><p>{html.escape(L.get("why", "") or "(no reasoning returned)")}</p>'
                           f'<h4>Objects listed ({len(L["objects"])})</h4><p class="mono">{html.escape(", ".join(L["objects"]))}</p>'
                           f'<h4>Rooms</h4><p class="mono">{html.escape(", ".join(L["rooms"]))}</p>'
                           f'<h4>Against the generator</h4><p>true affected that day: {r["n_true"]}; missed: <span class="mono">{html.escape(", ".join(r["missed"]) or "-")}</span>; '
                           f'listed but not affected: <span class="mono">{html.escape(", ".join(r["false"]) or "-")}</span></p>'
                           f'<button class="close" value="close">Close</button></form></dialog>')
        parts.append("</tbody></table></div>")
        list_html = "\n".join(parts + dialogs)

    def radio(name, options, checked):
        return "".join(f'<label><input type="radio" name="{name}" value="{v}" {"checked" if v == checked else ""}><span>{html.escape(t)}</span></label>' for v, t in options)

    page = f"""<title>Shift Baselines</title>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,500;9..144,700&family=Source+Sans+3:wght@400;600&family=IBM+Plex+Mono:wght@400;500&display=swap">
<style>{CSS}</style>
<div class="wrap">
<div class="bar"><h1>Shift Baselines</h1><span class="muted">follow-on to the confidence-shift study · updated {now} · <a href="{a.ledger}">mixture arms live on the Longleaf Ledger</a></span></div>

<p class="lead">Three questions a robot faces when a household routine shifts: <b>has something changed</b>, <b>which learned beliefs are now questionable</b>, and <b>how fast do the new regularities get learned</b>. The hypothesis mixture, told about the event, is a claim about the second. This page puts two standard baselines next to it — a change detector that resets everything, and a calibration wrapper that widens everything — on the same 20 held-out households, the same patrol stream and the same questions, with every question labelled by what the generator says moved it.</p>

<h2>Confidence and accuracy per day</h2>
<p class="muted">Pick lines, a split and a household. Solid = affected, dashed = unaffected. The weekend is shaded; event days are household-specific and enter through the split. In the <i>six kinds</i> view each line gets its own panel and, when pooled, points with fewer than 8 questions that day are left out. Hover any point for the value and the count.</p>
<div class="chart">
  <div class="ctl">
    <span class="grp"><b>patrol</b>{radio("tag", [("p8", "every 8 h (frozen)"), ("p2", "every 2 h (earlier freeze)")], "p8")}</span>
    <span class="grp"><b>split</b>{radio("split", [("affected", "affected vs unaffected"), ("kind", "six kinds")], "affected")}</span>
    <span class="grp"><b>metric</b>{radio("metric", [("conf", "confidence"), ("acc", "accuracy"), ("set", "set size"), ("cov", "coverage"), ("n", "questions")], "conf")}</span>
    <span class="grp"><b>household</b><select id="hh"></select></span>
  </div>
  <div class="ctl"><span class="grp" id="lines"></span></div>
  <div class="ctl"><span class="grp" id="groups"></span></div>
  <p class="muted" id="metric-note" style="margin:4px 0 6px;font-size:13px"></p>
  <div id="plot"></div>
</div>
<p class="muted" style="font-size:13px">Kinds: <b>event moved</b> — a guest visit or sick day moved the object and no patrol pass has seen it there yet; <b>weekend moved</b> — same, for a weekend-only activity; <b>stayed put</b> — it did not move, the routine that would have moved it did not happen that day; <b>after shift</b> — a shift move the patrol has since seen (any agent with recency in it gets these); <b>other event</b> — laundry day, late work, rain, delivery (never told to the robot); <b>small cause</b> — the simulator's short moods and episodes (a snack craving, a tidy mood: a handful of questions a day, hence jagged); <b>plain</b> — none of these. Affected = the first three, so it counts a move only while it is fresh; the labels are per patrol density because freshness depends on when the patrol last passed.</p>

<h2>Checks before reporting</h2>
<h3>Patrol every 8 h (frozen)</h3>{md_table(checks["p8"])}
<details><summary>Patrol every 2 h (earlier freeze)</summary>{md_table(checks["p2"])}</details>

<h2>Affected share per day</h2>
{md_table(shares)}

<h2>The affected list against the generator's truth</h2>
{list_html}

<h2>Per-day numbers behind the chart</h2>
<details><summary>Patrol every 8 h</summary>{md_table(tables["p8"])}</details>
<details><summary>Patrol every 2 h</summary>{md_table(tables["p2"])}</details>

<h2>Problems found</h2>
{md_table(problems)}
<h2>Open questions</h2>
{md_table(openq)}
<h2>Spend</h2>
{md_table(spend)}
</div>
<div class="tip" id="tip"></div>
<script>
const DATA = {json.dumps(data, separators=(",", ":"))};
const KINDS = {json.dumps(list(KINDS))};
const KIND_COLOR = {json.dumps(KIND_COLOR)};
const METRIC_NOTES = {json.dumps(METRIC_NOTES)};
const DEFAULT_LINES = {json.dumps(DEFAULT_LINES)};
{JS}
</script>
"""
    a.out.write_text(page)
    print(f"wrote {a.out} ({a.out.stat().st_size / 1e6:.2f} MB)")
    return 0


if __name__ == "__main__":
    main()
