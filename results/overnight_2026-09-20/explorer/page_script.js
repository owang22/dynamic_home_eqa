const HH = D.households, DAYS = D.days;
const $ = id => document.getElementById(id);
const short = a => a.replace(/\(.*?\)\|/, "|").replace("LastObservation","last seen").replace("MostFrequentLocation","most frequent").replace("TimetableLookup","timetable").replace("PeriodicPersistence","periodic").replace("SmoothedRecency","smoothed recency").replace("HierarchyBackoff","hierarchy backoff").replace("DaytypeMixture","daytype mixture").replace("PerpetuaStar","perpetua*").replace("Perpetua|","perpetua|").replace("|look off","").replace("|look voi"," + look").replace("llm_","LLM ").replace("/look_on","").replace("/look_off"," (no look)").replace("/not_told"," · not told").replace("/told"," · told");
const group = a => a.startsWith("llm_") ? "llm" : a.endsWith("|look voi") ? "voi" : "classical";
const state = {hh: HH[0].id, spot: false, groups: {classical: true, voi: true, llm: true}, sel: null, selQ: null, noteDay: 1, noteLook: "lookon", diff: true};
const tip = $("tip");
function showTip(e, html) { tip.innerHTML = html; tip.style.display = "block"; moveTip(e); }
function moveTip(e) { const w = tip.offsetWidth, h = tip.offsetHeight; let x = e.clientX + 14, y = e.clientY + 14; if (x + w > innerWidth - 8) x = e.clientX - w - 10; if (y + h > innerHeight - 8) y = e.clientY - h - 10; tip.style.left = x + "px"; tip.style.top = y + "px"; }
function hideTip() { tip.style.display = "none"; }
function heat(v) { if (v !== v) return "var(--grid)"; const s = ["--h0","--h1","--h2","--h3","--h4","--h5"]; const i = v < .7 ? 0 : v < .78 ? 1 : v < .85 ? 2 : v < .9 ? 3 : v < .95 ? 4 : 5; return `var(${s[i]})`; }
function hhObj() { return HH.find(h => h.id === state.hh); }
function recsFor(hh, agent) { const r = D.records[hh][agent]; return r || null; }
function qmeta(hh, i) { return D.questions[hh][i]; }
function keep(hh, rec) { if (!state.spot) return true; const t = D.locs[hh][rec[1]]; return t !== "ON_PERSON" && t !== "OUT_OF_HOUSE"; }
function acc(hh, agent, filter) { const rs = recsFor(hh, agent); if (!rs) return NaN; let n = 0, k = 0; for (const r of rs) { if (!keep(hh, r) || !filter(r)) continue; n++; k += r[3]; } return n ? k / n : NaN; }
function agentsShown() { return D.agents.filter(a => state.groups[group(a)]); }
function pct(v) { return v !== v ? "–" : Math.round(100 * v) + "%"; }

function renderHeader() {
  const h = hhObj();
  const nq = D.questions[state.hh].length;
  $("kpis").innerHTML = `<div class="kpi"><b>${HH.length}</b><span>households (seeds 0–9)</span></div><div class="kpi"><b>${D.agents.length}</b><span>agents on the 4 h bank</span></div><div class="kpi"><b>${nq}</b><span>questions per household</span></div><div class="kpi"><b>${h.n_objects}</b><span>objects in ${h.id}</span></div>`;
  const ev = DAYS.map(d => { const names = h.names[d].slice(0, 3); const e = (h.events[d] || []).map(x => x.replace("_", " ")).join(", "); const sh = h.shift.includes(d); return `<span class="${sh ? "shift" : ""}">${names}${sh ? " ▲" : ""}${e ? ": " + e : ""}</span>`; }).join("");
  $("events").innerHTML = `<span style="background:transparent;color:var(--muted)">▲ shift day</span>` + ev;
  $("residents").innerHTML = h.residents.map(r => "• " + r).join("<br>");
}

function renderGrid() {
  const h = hhObj(), agents = agentsShown();
  const L = 250, cw = 62, rh = 20, top = 34, W = L + cw * (DAYS.length + 1) + 30, H = top + rh * agents.length + 8;
  let s = `<svg width="${W}" height="${H}" viewBox="0 0 ${W} ${H}">`;
  DAYS.forEach((d, j) => { const x = L + j * cw; if (h.shift.includes(d)) s += `<rect x="${x}" y="${top - 18}" width="${cw}" height="${H - top + 14}" fill="var(--shift)"/>`; s += `<text x="${x + cw / 2}" y="${top - 6}" font-size="11" text-anchor="middle">${h.names[d].slice(0, 3)}${h.shift.includes(d) ? " ▲" : ""}</text>`; });
  s += `<text x="${L + DAYS.length * cw + cw / 2}" y="${top - 6}" font-size="11" text-anchor="middle">shift − non</text>`;
  agents.forEach((a, i) => {
    const y = top + i * rh;
    s += `<text x="${L - 6}" y="${y + 14}" font-size="11" text-anchor="end">${short(a)}</text>`;
    DAYS.forEach((d, j) => {
      const v = acc(state.hh, a, r => qmeta(state.hh, r[0]).day === d);
      const sel = state.sel && state.sel.agent === a && state.sel.day === d;
      s += `<g class="cell${sel ? " sel" : ""}" data-a="${a}" data-d="${d}"><rect x="${L + j * cw + 1}" y="${y + 1}" width="${cw - 2}" height="${rh - 2}" fill="${heat(v)}" stroke="var(--surface)" stroke-width=".6"/><text x="${L + j * cw + cw / 2}" y="${y + 14}" font-size="10.5" text-anchor="middle" fill="${v >= .9 ? "#ffffff" : "var(--ink)"}" font-weight="${v >= .9 ? 500 : 400}">${pct(v)}</text></g>`;
    });
    const sh = acc(state.hh, a, r => h.shift.includes(qmeta(state.hh, r[0]).day)), non = acc(state.hh, a, r => !h.shift.includes(qmeta(state.hh, r[0]).day));
    const dlt = sh - non;
    s += `<text x="${L + DAYS.length * cw + cw / 2}" y="${y + 14}" font-size="11" text-anchor="middle" fill="${dlt < 0 ? "var(--bad)" : "var(--good)"}" font-weight="600">${dlt !== dlt ? "–" : (dlt > 0 ? "+" : "") + (100 * dlt).toFixed(1)}</text>`;
  });
  s += "</svg>";
  $("grid").innerHTML = s;
  $("legendA").innerHTML = ["<70%", "70–78", "78–85", "85–90", "90–95", "≥95%"].map((t, i) => `<span><i style="background:var(--h${i})"></i>${t}</span>`).join("");
  $("grid").querySelectorAll(".cell").forEach(g => {
    g.addEventListener("click", () => { state.sel = {agent: g.dataset.a, day: +g.dataset.d}; state.selQ = null; renderGrid(); renderQuestions(); });
    g.addEventListener("mousemove", e => { const a = g.dataset.a, d = +g.dataset.d; const rs = recsFor(state.hh, a).filter(r => qmeta(state.hh, r[0]).day === d && keep(state.hh, r)); const k = rs.filter(r => r[3]).length; const looks = rs.filter(r => r[5]).length; showTip(e, `<b>${short(a)}</b> · ${h.names[d]}<br>${k}/${rs.length} right${looks ? ` · ${looks} looks, ${rs.filter(r => r[6]).length} found it` : ""}`); });
    g.addEventListener("mouseleave", hideTip);
  });
}

function renderPaired() {
  const agents = agentsShown();
  const L = 250, W0 = 520, rh = 18, top = 26, W = L + W0 + 40, H = top + rh * agents.length + 10, xmin = -.25, xmax = .25;
  const X = v => L + (Math.max(xmin, Math.min(xmax, v)) - xmin) / (xmax - xmin) * W0;
  let s = `<svg width="${W}" height="${H}" viewBox="0 0 ${W} ${H}">`;
  [-.2, -.1, 0, .1, .2].forEach(v => { s += `<line x1="${X(v)}" x2="${X(v)}" y1="${top - 4}" y2="${H - 6}" stroke="var(--grid)" stroke-width="${v === 0 ? 1.4 : .6}"/><text x="${X(v)}" y="${top - 8}" font-size="10" text-anchor="middle">${v > 0 ? "+" : ""}${Math.round(100 * v)}</text>`; });
  agents.forEach((a, i) => {
    const y = top + i * rh + rh / 2;
    const ds = [];
    HH.forEach(h => { const sh = acc(h.id, a, r => h.shift.includes(qmeta(h.id, r[0]).day)), non = acc(h.id, a, r => !h.shift.includes(qmeta(h.id, r[0]).day)); if (sh === sh && non === non) ds.push({h: h.id, v: sh - non}); });
    if (!ds.length) return;
    const m = ds.reduce((p, q) => p + q.v, 0) / ds.length;
    s += `<text x="${L - 6}" y="${y + 4}" font-size="11" text-anchor="end">${short(a)}</text>`;
    s += `<rect x="${Math.min(X(0), X(m))}" y="${y - 5}" width="${Math.abs(X(m) - X(0))}" height="10" fill="${m < 0 ? "var(--bad)" : "var(--good)"}" opacity=".35"/>`;
    ds.forEach(d => s += `<circle cx="${X(d.v)}" cy="${y}" r="3.2" fill="${d.h === state.hh ? "var(--accent)" : "var(--ink2)"}" opacity="${d.h === state.hh ? 1 : .55}"><title>${d.h}: ${(d.v > 0 ? "+" : "") + (100 * d.v).toFixed(1)} points</title></circle>`);
    s += `<text x="${L + W0 + 6}" y="${y + 4}" font-size="11" fill="${m < 0 ? "var(--bad)" : "var(--good)"}">${(m > 0 ? "+" : "") + (100 * m).toFixed(1)} · ${ds.filter(d => d.v < 0).length}/${ds.length} drop</text>`;
  });
  s += "</svg>";
  $("paired").innerHTML = s;
}

function renderQuestions() {
  if (!state.sel) return;
  const {agent, day} = state.sel, h = hhObj(), locs = D.locs[state.hh];
  const rs = recsFor(state.hh, agent).filter(r => qmeta(state.hh, r[0]).day === day && keep(state.hh, r));
  $("qhead").innerHTML = `<b>${short(agent)}</b> · ${state.hh} · ${h.names[day]}${h.shift.includes(day) ? " (shift day)" : ""} · ${rs.filter(r => r[3]).length}/${rs.length} right`;
  let t = `<table class="qlist"><tr><th>time</th><th>object</th><th>truth</th><th>answer</th><th>conf</th><th>look</th></tr>`;
  rs.forEach(r => { const q = qmeta(state.hh, r[0]); const ans = locs[r[2]]; const cls = ans === "ABSTAIN" ? "ab" : r[3] ? "ok" : "no"; t += `<tr class="q${state.selQ === r[0] ? " sel" : ""}" data-i="${r[0]}"><td class="mono">${String(Math.floor(q.min / 60)).padStart(2, "0")}:${String(q.min % 60).padStart(2, "0")}</td><td class="mono" style="white-space:nowrap">${q.obj}${q.moved ? "" : " <span class='pill' title='did not move in the 24 h before the question'>still</span>"}</td><td class="mono">${locs[r[1]]}</td><td class="mono ${cls}">${ans}${r[7] !== r[3] ? (r[7] ? " (right before look)" : " (wrong before look)") : ""}</td><td>${r[4]}</td><td class="mono">${r[5] ? r[5] + (r[6] ? " ✓" : " ✗") : ""}</td></tr>`; });
  t += "</table>";
  $("qlist").innerHTML = t;
  $("qlist").querySelectorAll("tr.q").forEach(tr => tr.addEventListener("click", () => { state.selQ = +tr.dataset.i; renderQuestions(); renderDoc(); }));
  if (state.selQ === null) $("qdoc").innerHTML = `<div class="note">Click a question to read its prompt and answer.</div>`;
}

function armKey(agent) { const m = agent.match(/^llm_(\w+)\/(told|not_told)\/look_(on|off)$/); return m ? `${m[1]}_${m[2].replace("_", "")}_look${m[3]}` : null; }
function esc(s) { return (s || "").replace(/&/g, "&amp;").replace(/</g, "&lt;"); }
function renderDoc() {
  const {agent} = state.sel, i = state.selQ, q = qmeta(state.hh, i), r = recsFor(state.hh, agent).find(r => r[0] === i), locs = D.locs[state.hh];
  const arm = armKey(agent), pr = arm && D.prompts[state.hh] && D.prompts[state.hh][arm] && D.prompts[state.hh][arm][q.id];
  let s = `<div class="note"><b>${q.id}</b> · ${q.obj} (${q.cls.replace("_", " ")}) · truth <span class="mono">${locs[r[1]]}</span> · answer <span class="mono ${r[3] ? "ok" : "no"}">${locs[r[2]]}</span> · confidence ${r[4]}${r[5] ? ` · looked at ${r[5]} (${r[6] ? "found it" : "not there"})` : ""}</div>`;
  if (!pr) { s += `<div class="note">${arm ? "Prompt not bundled for this arm; the full prompt is in llm/" + state.hh + "_p4_" + arm + "/calls.jsonl." : "Classical belief: no prompt. The answer is the belief's argmax after the patrol stream" + (agent.endsWith("voi") ? " and the VoI look." : ".")}</div>`; }
  else {
    if (pr.h) s += `<div class="hint">Messages in the prompt:\n${esc(pr.h)}</div>`;
    s += `<div class="note">Prompt (the shared header — time, residents, rooms, answer options — is left out):</div><div class="prompt">${esc(pr.q)}</div><div class="compl">${esc(pr.a)}</div>`;
    if (pr.q2) s += `<div class="note">After the look:</div><div class="prompt">${esc(pr.q2.split("\n\n").slice(-3).join("\n\n"))}</div><div class="compl">${esc(pr.a2)}</div>`;
  }
  $("qdoc").innerHTML = s;
}

function wordDiff(a, b) {
  const A = a.split(/(\s+)/).filter(x => x.length), B = b.split(/(\s+)/).filter(x => x.length);
  const n = A.length, m = B.length; if (n * m > 4e6) return esc(b);
  const dp = new Uint16Array((n + 1) * (m + 1));
  for (let i = n - 1; i >= 0; i--) for (let j = m - 1; j >= 0; j--) dp[i * (m + 1) + j] = A[i] === B[j] ? dp[(i + 1) * (m + 1) + j + 1] + 1 : Math.max(dp[(i + 1) * (m + 1) + j], dp[i * (m + 1) + j + 1]);
  let i = 0, j = 0, out = [];
  while (i < n && j < m) { if (A[i] === B[j]) { out.push(esc(A[i])); i++; j++; } else if (dp[(i + 1) * (m + 1) + j] >= dp[i * (m + 1) + j + 1]) { if (A[i].trim()) out.push(`<del>${esc(A[i])}</del>`); i++; } else { out.push(B[j].trim() ? `<ins>${esc(B[j])}</ins>` : esc(B[j])); j++; } }
  while (i < n) { if (A[i].trim()) out.push(`<del>${esc(A[i])}</del>`); i++; }
  while (j < m) { out.push(B[j].trim() ? `<ins>${esc(B[j])}</ins>` : esc(B[j])); j++; }
  return out.join("");
}
function renderNotes() {
  const h = hhObj(), notes = D.notes[state.hh] || {};
  const d = state.noteDay;
  const hint = h.hints.find(x => x.startsWith(h.names[d]));
  $("hintBox").innerHTML = hint && h.shift.includes(d) ? `<div class="hint">Told arm received on ${h.names[d]}: “${esc(hint)}”</div>` : "";
  let s = "";
  for (const arm of ["told", "nottold"]) {
    const key = `summary_${arm}_${state.noteLook}`, ns = notes[key] || {};
    const cur = ns[d], prev = ns[d - 1];
    const body = cur == null ? `<span class="note">no notes written for this day (run missing or the day was not reached)</span>` : (state.diff && prev) ? wordDiff(prev, cur) : esc(cur);
    s += `<div><h4>${arm === "told" ? "told" : "not told"} · notes written at the end of ${h.names[d]}</h4><div class="prose">${body}</div></div>`;
  }
  $("notes").innerHTML = s;
}
function fillSelects() {
  $("hh").innerHTML = HH.map(h => `<option value="${h.id}">${h.id} — shift: ${h.shift.map(d => h.names[d].slice(0, 3)).join(", ")}</option>`).join("");
  $("noteDay").innerHTML = [0, ...DAYS].map(d => `<option value="${d}">${hhObj().names[d]} (day ${d})</option>`).join("");
  $("noteDay").value = state.noteDay;
}
function renderAll() { renderHeader(); renderGrid(); renderPaired(); renderNotes(); if (state.sel) renderQuestions(); }
$("hh").addEventListener("change", e => { state.hh = e.target.value; state.sel = null; state.selQ = null; fillSelects(); $("qlist").innerHTML = ""; $("qhead").textContent = "Click a cell in the day grid."; renderAll(); });
$("spotOnly").addEventListener("change", e => { state.spot = e.target.checked; renderAll(); });
for (const [id, g] of [["gClassical", "classical"], ["gVoi", "voi"], ["gLlm", "llm"]]) $(id).addEventListener("click", () => { state.groups[g] = !state.groups[g]; $(id).classList.toggle("on", state.groups[g]); renderGrid(); renderPaired(); });
$("noteDay").addEventListener("change", e => { state.noteDay = +e.target.value; renderNotes(); });
$("noteLook").addEventListener("change", e => { state.noteLook = e.target.value; renderNotes(); });
$("showDiff").addEventListener("change", e => { state.diff = e.target.checked; renderNotes(); });
fillSelects(); renderAll();
// open on something: the summary told arm on the first shift day
(function () { const h = hhObj(); const a = D.agents.find(x => x === "llm_summary/told/look_on"); if (a) { state.sel = {agent: a, day: h.shift[0]}; renderGrid(); renderQuestions(); } })();
