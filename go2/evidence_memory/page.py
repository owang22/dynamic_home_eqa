"""Build the results page (out/page.html): scores, the question explorer with the pictures, and place timelines.

    python page.py
Reads out/questions.json, out/answers_*.json, out/scores_*.json, out/memory_*.json and RESULTS_PAGE.json (the
written summary and in-person method). Pictures are embedded as small JPEG thumbnails.
"""
from __future__ import annotations

import base64
import html
import io
import json

from PIL import Image

import answer as AN
import common as C

LABEL = {"A": "Captions only", "B": "Captions + every picture", "F": "Change notes only",
         "D": "Change notes + every picture", "C": "Change notes + important pictures",
         "E": "Change notes + evenly spaced pictures", "O": "Shown the right picture (perception ceiling)",
         "Bf": "Captions + every picture, fresh look", "Cf": "Change notes + important pictures, fresh look",
         "Df": "Change notes + every picture, fresh look", "Z": "Fixed answers, no memory",
         "Ep": "Change notes + random before/after pairs (same budget as important)",
         "Ep2": "Random pairs, second draw", "Ep3": "Random pairs, third draw"}
ORDER = ["Z", "A", "B", "Bf", "F", "D", "Df", "C", "Cf", "Ep", "Ep2", "Ep3", "O"]
KINDS = [("lookback", "Look back for a detail"), ("when", "When did it change"), ("happened", "What was going on"),
         ("left", "Left something behind"), ("unseen", "Never visited: says cannot tell")]
_thumbs = {}


def thumb(path, w=220):
    if not path:
        return None
    if path not in _thumbs:
        im = Image.open(path).convert("RGB")
        im.thumbnail((w, w))
        buf = io.BytesIO()
        im.save(buf, "JPEG", quality=68)
        _thumbs[path] = "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode()
    return path


def load(p):
    try:
        return json.loads((C.OUT / p).read_text())
    except FileNotFoundError:
        return None


def main():
    qs = load("questions.json")
    summary = json.loads((C.HERE / "RESULTS_PAGE.json").read_text())
    mems = {h: load(f"memory_{h}.json") for h in ("1.0", "0.4")}
    vis = {h: {v["id"]: v for v in m["visits"]} for h, m in mems.items() if m}
    runs = [("1.0", "", "Qwen, camera 1.0 m"), ("1.0", "_opus", "Opus, camera 1.0 m"),
            ("0.4", "", "Qwen, camera 0.4 m (Go2)"), ("0.4", "_opus", "Opus, camera 0.4 m (Go2)")]
    flags = json.loads((C.OUT / "question_flags.json").read_text())
    scores, answers = {}, {}
    qtruth = {q["id"]: q["truth"].get("answer") for q in qs}
    for h, tag, name in runs:
        s = load(f"scores_{h}{tag}_clean.json")
        full = load(f"scores_{h}{tag}.json") or {}
        if not s:
            continue
        def look_yes(arm):
            rs = [r for r in s["_rows"][arm] if r["kind"] == "lookback" and qtruth[r["id"]] == "yes"]
            return {"right": sum(r["right"] for r in rs), "n": len(rs)}
        scores[name] = {arm: {"overall": s[arm]["overall_kinds_equal"], "by_kind": s[arm]["by_kind"], "kept": s[arm]["kept"],
                              "who": s[arm].get("happened_who"), "look_yes": look_yes(arm)} for arm in ORDER if arm in s}
        for arm in ORDER:
            a = load(f"answers_{h}_{arm}{tag}.json")
            rows = {r["id"]: r for r in full.get("_rows", {}).get(arm, [])}
            rows.update({r["id"]: r for r in s.get("_rows", {}).get(arm, [])})
            if a:
                for r in a:
                    sc = rows.get(r["id"], {})
                    looked = [x for x in (r.get("looked") or []) if isinstance(x, str)]
                    if tag == "_opus":   # Opus reports short ids; map them back through the same memory text
                        looked = []
                    answers.setdefault(r["id"], []).append({
                        "run": name, "arm": arm, "right": sc.get("right"), "doing": sc.get("doing"),
                        "answer": r.get("answer"), "looked": [thumb(vis[h][x]["picture"]) and x for x in looked
                                                             if x in vis.get(h, {})][:6], "h": h})
    # the right pictures for each question (from the 1.0 m and 0.4 m sets)
    qrows = []
    for q in qs:
        right = {}
        for h in ("1.0", "0.4"):
            if h in vis:
                vs = AN.oracle_visits(q, list(vis[h].values()))
                if q["kind"] == "left":
                    places = {i["place"] for i in q["truth"]["items"]}
                    vs = [v for v in vs if v["spot"] in places][:4]
                right[h] = [{"id": v["id"], "cap": f"{C.hhmm(v['time'])} day {v['day']}", "src": thumb(v["picture"]) and v["id"]}
                            for v in vs]
        qrows.append({"id": q["id"], "kind": q["kind"], "question": q["question"], "truth": q["truth"],
                      "flags": flags[q["id"]]["reasons"], "clean": flags[q["id"]]["clean_1.0"],
                      "right": right, "answers": answers.get(q["id"], [])})
    # place timelines: day 7 at three places, both heights
    tl = []
    for spot in ["kitchen_kitchen_island_island_countertop", "entryway_floor", "living_room_living_room_coffee_table_top",
                 "office_office_desk_desk_top"]:
        for h in ("1.0", "0.4"):
            if h not in vis:
                continue
            keep = AN.kept_pictures(mems[h]["visits"], "important")
            row = []
            for t in C.TIMES:
                v = vis[h].get(f"d7_{t}_{spot}")
                if not v:
                    continue
                e = v.get("evidence") or {}
                row.append({"time": C.hhmm(t), "src": thumb(v["picture"]) and v["id"], "kept": v["id"] in keep,
                            "importance": e.get("importance"), "changes": "; ".join(f"{c['thing']} {c['change']}" for c in e.get("changes", [])),
                            "guess": e.get("guess"), "caption": (v.get("caption") or {}).get("things")})
            tl.append({"place": C.spot_name(spot), "height": h, "visits": row,
                       "usual": mems[h]["usual"].get("7", {}).get(spot)})
    pics = {}
    for h in vis:
        for vid, v in vis[h].items():
            if v["picture"] in _thumbs:
                pics[f"{h}|{vid}"] = _thumbs[v["picture"]]
    data = {"summary": summary, "scores": scores, "labels": LABEL, "order": ORDER, "kinds": KINDS,
            "questions": qrows, "timelines": tl, "pics": pics}
    page = TEMPLATE.replace("__DATA__", json.dumps(data).replace("</", "<\\/"))
    (C.OUT / "page.html").write_text(page)
    print(f"out/page.html: {len(page) / 1e6:.1f} MB, {len(pics)} pictures, {len(qrows)} questions")


TEMPLATE = r"""<title>Evidence Memory Trial</title>
<meta name="description" content="Which robot memory keeps the right scenes and can look back at them: simulated patrols, 122 questions">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;500;600&family=IBM+Plex+Mono:wght@400;500&display=swap">
<style>
:root{--bg:#f6f4ef;--panel:#fffdf8;--ink:#1f2421;--muted:#5d655f;--line:#dcd8cc;--accent:#0f6e68;--accent-soft:#d8ece9;
--good:#2f7a3a;--good-soft:#e1f0e1;--bad:#a23b2c;--bad-soft:#f6e1dc;--mid:#8a6a12;--mid-soft:#f4ebcf;--kept:#0f6e68}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){--bg:#141816;--panel:#1c211f;--ink:#e6e8e3;--muted:#a3aba5;
--line:#323a36;--accent:#5cc2b8;--accent-soft:#1d3634;--good:#7fcf8a;--good-soft:#1f3322;--bad:#f0907e;--bad-soft:#3a2420;
--mid:#e3c46a;--mid-soft:#3a3220;--kept:#5cc2b8;color-scheme:dark}}
:root[data-theme="dark"]{--bg:#141816;--panel:#1c211f;--ink:#e6e8e3;--muted:#a3aba5;--line:#323a36;--accent:#5cc2b8;
--accent-soft:#1d3634;--good:#7fcf8a;--good-soft:#1f3322;--bad:#f0907e;--bad-soft:#3a2420;--mid:#e3c46a;--mid-soft:#3a3220;
--kept:#5cc2b8;color-scheme:dark}
*{box-sizing:border-box}
body{background:var(--bg);color:var(--ink);font:15px/1.55 "IBM Plex Sans",system-ui,-apple-system,"Segoe UI",sans-serif;margin:0}
.wrap{max-width:1120px;margin:0 auto;padding-inline:16px;padding-block:28px 64px}
h1{font-size:28px;line-height:1.2;margin:0 0 6px;text-wrap:balance;font-weight:600}
h2{font-size:20px;margin:40px 0 10px;text-wrap:balance;font-weight:600}
h3{font-size:16px;margin:18px 0 8px;font-weight:600}
p,li{max-width:68ch}
.sub{color:var(--muted);margin:0 0 18px}
.mono{font-family:"IBM Plex Mono",ui-monospace,Menlo,monospace;font-size:13px}
.label{font-size:12px;letter-spacing:.06em;text-transform:uppercase;color:var(--muted)}
.answer{background:var(--panel);border:1px solid var(--line);border-left:4px solid var(--accent);padding:14px 18px;border-radius:6px}
.answer li{margin:4px 0}
.scroll{overflow-x:auto}
.hint{display:none;font-size:12px;color:var(--muted)}
@media (max-width:700px){.hint{display:block}}
table{border-collapse:collapse;font-variant-numeric:tabular-nums;min-width:640px;width:100%}
th,td{padding:7px 9px;border-bottom:1px solid var(--line);text-align:right;vertical-align:top}
th:first-child,td:first-child{text-align:left}
th{font-weight:500;color:var(--muted);font-size:13px}
td.best{font-weight:600;color:var(--accent)}
.bar{display:inline-block;height:8px;background:var(--accent);border-radius:2px;vertical-align:middle;margin-left:6px;opacity:.75}
.tabs{display:flex;flex-wrap:wrap;gap:6px;margin:8px 0 14px}
.tabs button,.ctrl select{font:inherit;font-size:13px;border:1px solid var(--line);background:var(--panel);color:var(--ink);
padding:5px 10px;border-radius:999px;cursor:pointer}
.tabs button[aria-pressed="true"]{background:var(--accent);color:var(--bg);border-color:var(--accent)}
.ctrl{display:flex;flex-wrap:wrap;gap:10px;align-items:center;margin:6px 0 12px}
.ctrl select{border-radius:6px}
.q{background:var(--panel);border:1px solid var(--line);border-radius:8px;padding:14px 16px;margin:0 0 12px;min-width:0}
.q .text{font-weight:500}
.truth{color:var(--muted);font-size:14px;margin:4px 0 8px}
.pics{display:flex;flex-wrap:wrap;gap:8px;margin:8px 0}
.pics figure{margin:0;width:150px}
.pics img{width:150px;height:auto;border-radius:4px;border:1px solid var(--line);display:block}
.pics figcaption{font-size:12px;color:var(--muted)}
.arms{display:grid;grid-template-columns:repeat(auto-fill,minmax(250px,1fr));gap:8px}
.arm{border:1px solid var(--line);border-radius:6px;padding:8px 10px;font-size:13.5px;min-width:0}
.arm.ok{background:var(--good-soft);border-color:transparent}
.arm.no{background:var(--bad-soft);border-color:transparent}
.arm .who{font-weight:600;font-size:13px}
.arm .exp{color:var(--muted);font-size:13px;overflow-wrap:anywhere}
.tag{display:inline-block;font-size:11.5px;padding:1px 7px;border-radius:999px;background:var(--accent-soft);color:var(--accent);margin-right:4px}
.tl{display:grid;grid-template-columns:repeat(auto-fill,minmax(160px,1fr));gap:10px}
.tl .v{border:1px solid var(--line);border-radius:6px;padding:6px;background:var(--panel);font-size:12.5px;min-width:0}
.tl .v.kept{outline:2px solid var(--kept);outline-offset:-1px}
.tl img{width:100%;border-radius:4px;display:block}
.imp{font-family:"IBM Plex Mono",monospace;font-size:12px}
.more{color:var(--muted);font-size:13px}
.flag{font-size:12.5px;color:var(--mid);background:var(--mid-soft);border-radius:4px;padding:3px 8px;margin:0 0 6px;display:inline-block}
.method{display:grid;grid-template-columns:repeat(auto-fit,minmax(210px,1fr));gap:10px}
.step{background:var(--panel);border:1px solid var(--line);border-radius:8px;padding:10px 12px;min-width:0}
.step b{display:block;margin-bottom:2px}
@media (max-width:520px){h1{font-size:23px}.pics figure,.pics img{width:120px}}
</style>
<div class="wrap">
<div class="label">Go2 lab · evidence memory · simulation, 19 Oct 2026</div>
<h1>Evidence Memory Trial</h1>
<p class="sub" id="sub"></p>
<div class="answer" id="headline"></div>

<h2>What to run in person</h2>
<div id="inperson"></div>

<h2>Scores</h2>
<p class="more" id="scorenote"></p>
<div class="tabs" id="runtabs" role="group" aria-label="run"></div>
<div class="hint">The table scrolls sideways.</div><div class="scroll"><table id="scoretable"></table></div>

<h2>How each memory is made</h2>
<div class="method" id="method"></div>

<h2>Questions, answers and the pictures</h2>
<div class="ctrl">
<label class="more">Kind <select id="fkind"></select></label>
<label class="more">Run <select id="frun"></select></label>
<label class="more">Show <select id="fshow"><option value="all">all</option><option value="clean">clean questions only</option><option value="split">only where arms disagree</option></select></label>
</div>
<div id="qlist"></div>
<p class="more" id="qcount"></p>

<h2>What the memory kept: one day at four places</h2>
<p class="more">Day 7, every visit. A teal outline marks a picture kept for looking back (importance 2–3, or the picture before one). Notes are the robot's own.</p>
<div class="ctrl"><label class="more">Place <select id="tplace"></select></label></div>
<div id="tlwrap"></div>
</div>
<script>
const D = __DATA__;
const $ = s => document.querySelector(s);
const esc = s => String(s ?? "").replace(/[&<>"]/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]));
const pct = x => x == null ? "–" : Math.round(100 * x) + "%";
$("#sub").textContent = D.summary.sub;
$("#headline").innerHTML = D.summary.headline_html;
$("#inperson").innerHTML = D.summary.inperson_html;
$("#scorenote").textContent = D.summary.score_note;
$("#method").innerHTML = D.summary.method.map(s => `<div class="step"><b>${esc(s[0])}</b>${esc(s[1])}</div>`).join("");
const runs = Object.keys(D.scores);
let run = runs[0];
function scoreTable(){
  const S = D.scores[run], arms = D.order.filter(a => S[a]);
  const kinds = D.kinds.filter(k => arms.some(a => S[a].by_kind[k[0]] != null));
  const best = {};
  for (const k of ["overall", ...kinds.map(k => k[0])]) {
    const vals = arms.filter(a => a !== "O" && a !== "Z").map(a => k === "overall" ? S[a].overall : S[a].by_kind[k]);
    best[k] = Math.max(...vals.filter(v => v != null));
  }
  const ly = arms.filter(a => a !== "O" && a !== "Z").map(a => S[a].look_yes.n ? S[a].look_yes.right / S[a].look_yes.n : 0);
  const bestLy = Math.max(...ly);
  let h = `<tr><th>Memory</th><th>Overall</th><th>Look back: things that were there</th>${kinds.map(k => `<th>${esc(k[0] === "lookback" ? "Look back, all (yes and no)" : k[1])}</th>`).join("")}<th>Pictures kept (of 640)</th><th>Who (not scored)</th></tr>`;
  for (const a of arms) {
    const x = S[a], o = x.overall;
    const free = a === "O" || a === "Z";
    const cell = (v, k) => `<td class="${!free && v === best[k] ? "best" : ""}">${pct(v)}</td>`;
    const lyv = x.look_yes.n ? x.look_yes.right / x.look_yes.n : 0;
    h += `<tr><td>${esc(D.labels[a])}</td><td class="${!free && o === best.overall ? "best" : ""}">${pct(o)}<span class="bar" style="width:${Math.round(60 * o)}px"></span></td>`
      + `<td class="${!free && lyv === bestLy ? "best" : ""}">${x.look_yes.right} of ${x.look_yes.n}</td>`
      + kinds.map(k => cell(x.by_kind[k[0]], k[0])).join("") + `<td>${x.kept == null ? "–" : x.kept}</td><td>${pct(x.who)}</td></tr>`;
  }
  $("#scoretable").innerHTML = h;
  document.querySelectorAll("#runtabs button").forEach(b => b.setAttribute("aria-pressed", b.dataset.run === run));
}
$("#runtabs").innerHTML = runs.map(r => `<button data-run="${esc(r)}">${esc(r)}</button>`).join("");
$("#runtabs").addEventListener("click", e => { if (e.target.dataset.run) { run = e.target.dataset.run; scoreTable(); } });
scoreTable();
$("#fkind").innerHTML = `<option value="">all kinds</option>` + D.kinds.map(k => `<option value="${k[0]}">${esc(k[1])}</option>`).join("");
$("#frun").innerHTML = runs.map(r => `<option>${esc(r)}</option>`).join("");
function truthText(q){
  const t = q.truth;
  if (q.kind === "happened") return `Truth: ${esc(t.who)} · ` + esc((t.doing || []).slice(0, 3).map(s => s.replace(/^\d\d:\d\d \w+: /, "")).join(" / ")).slice(0, 420);
  if (q.kind === "left") return "Truth: " + (t.left_behind ? t.items.map(i => `${esc(i.thing)} at ${esc(i.place.replace(/_/g, " "))}${i.seen_now ? "" : " (not in a picture then)"}`).join("; ") : "nothing left behind");
  return "Truth: " + esc(t.answer);
}
function ansText(a){
  const x = a.answer || {};
  if (x.who !== undefined) return `${esc(x.who)} · ${esc(x.doing)}`;
  if (x.left_behind !== undefined) return `${esc(x.left_behind)}${(x.items || []).length ? ": " + x.items.map(i => esc(i.thing) + " at " + esc(i.place)).join("; ") : ""}`;
  return esc(x.answer);
}
const pic = (h, id) => D.pics[h + "|" + id];
function qlist(){
  const k = $("#fkind").value, r = $("#frun").value, split = $("#fshow").value === "split", cleanOnly = $("#fshow").value === "clean";
  let n = 0, out = [];
  for (const q of D.questions) {
    if (k && q.kind !== k) continue;
    const h = r.includes("0.4") ? "0.4" : "1.0";
    const fl = q.flags.filter(f => h === "0.4" || !f.startsWith("0.4 m"));
    if (cleanOnly && fl.length) continue;
    const as = q.answers.filter(a => a.run === r);
    if (!as.length) continue;
    if (split) { const s = new Set(as.filter(a => a.arm !== "O").map(a => a.right)); if (s.size < 2) continue; }
    n++;
    if (out.length >= 40) continue;
    const rp = (q.right[h] || []).filter(p => pic(h, p.id));
    out.push(`<div class="q"><div class="label">${esc(q.id)} · ${esc(D.kinds.find(x => x[0] === q.kind)[1])}</div>
      <div class="text">${esc(q.question)}</div><div class="truth">${truthText(q)}</div>
      ${fl.length ? `<div class="flag">Left out of the clean scores at ${h} m: ${esc(fl.join("; "))}</div>` : ""}
      ${rp.length ? `<div class="pics">${rp.map(p => `<figure><img loading="lazy" alt="${esc(p.cap)}" src="${pic(h, p.id)}"><figcaption>${esc(p.cap)}</figcaption></figure>`).join("")}</div>` : ""}
      <div class="arms">${D.order.map(a => as.find(x => x.arm === a)).filter(Boolean).map(a => `<div class="arm ${a.right == null ? "" : a.right ? "ok" : "no"}">
        <div class="who">${esc(D.labels[a.arm])} — ${a.right == null ? "not scored" : a.right ? "right" : "wrong"}${a.doing ? " (judge: " + esc(a.doing) + ")" : ""}</div>
        <div>${ansText(a)}</div><div class="exp">${esc((a.answer || {}).explanation || "").slice(0, 380)}</div>
        ${a.looked && a.looked.length ? `<div class="more">looked again at ${a.looked.length} picture${a.looked.length > 1 ? "s" : ""}</div>` : ""}</div>`).join("")}</div></div>`);
  }
  $("#qlist").innerHTML = out.join("");
  $("#qcount").textContent = n > 40 ? `Showing 40 of ${n}. Narrow by kind to see the rest.` : `${n} questions.`;
}
["#fkind", "#frun", "#fshow"].forEach(s => $(s).addEventListener("change", qlist));
qlist();
const places = [...new Set(D.timelines.map(t => t.place))];
$("#tplace").innerHTML = places.map(p => `<option>${esc(p)}</option>`).join("");
function timeline(){
  const p = $("#tplace").value;
  $("#tlwrap").innerHTML = D.timelines.filter(t => t.place === p).map(t => `<h3>Camera at ${t.height} m</h3>
    <p class="more">Usually here (the robot's note): ${esc(t.usual)}</p>
    <div class="tl">${t.visits.map(v => `<div class="v ${v.kept ? "kept" : ""}">
      ${pic(t.height, v.src) ? `<img loading="lazy" alt="${esc(p)} at ${v.time}" src="${pic(t.height, v.src)}">` : `<div class="more">no view</div>`}
      <div><b>${v.time}</b> <span class="imp">importance ${v.importance ?? "–"}</span>${v.kept ? ` <span class="tag">kept</span>` : ""}</div>
      <div>${esc(v.changes || "no change")}</div>${v.guess && v.guess.toLowerCase() !== "unclear" ? `<div class="more">guess: ${esc(v.guess)}</div>` : ""}</div>`).join("")}</div>`).join("");
}
$("#tplace").addEventListener("change", timeline);
timeline();
</script>
"""

if __name__ == "__main__":
    main()
