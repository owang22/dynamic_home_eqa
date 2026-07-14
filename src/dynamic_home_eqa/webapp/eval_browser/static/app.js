/* eval_browser SPA — W-1 read-only views (EventCard, DayTimeline, debug Aggregate).
 *
 * Consumes ONLY /api/runs + /api/index/{run}/{folder}. Blinding is enforced
 * server-side (rater sessions never receive judge fields / condition); the
 * debug checkbox here is presentation-only for sessions that DO get them.
 */

"use strict";

const state = {
  token: null,
  role: "rater",
  runs: [],            // /api/runs payload
  runRef: null,
  folder: null,
  index: null,         // current folder's index JSON
  runIndexes: {},      // folder -> index (lazily filled for aggregate view)
  view: "cards",
  cardPos: 0,
  trajObject: null,
};

const $ = (id) => document.getElementById(id);
const esc = (s) => String(s ?? "").replace(/[&<>"']/g, (c) =>
  ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));

const OCC_COLORS = ["#2563eb", "#d97706", "#059669", "#db2777", "#7c3aed", "#0891b2"];

// ── session ─────────────────────────────────────────────────────────────

async function startSession() {
  const name = $("name-input").value.trim();
  if (!name) return;
  // Local/owner default is a debug session; if this deployment requires an
  // admin key for debug, fall back to a (blinded) rater session.
  let resp = await fetch("/api/session", {
    method: "POST", headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ name, role: "debug" }),
  });
  if (resp.status === 403) {
    resp = await fetch("/api/session", {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ name, role: "rater" }),
    });
  }
  if (!resp.ok) { alert("session failed: " + (await resp.text())); return; }
  const data = await resp.json();
  state.token = data.token;
  state.role = data.role;
  localStorage.setItem("eval_browser_session", JSON.stringify({ token: data.token, role: data.role, name }));
  await boot();
}

async function boot() {
  const resp = await fetch("/api/runs?session=" + encodeURIComponent(state.token || ""));
  if (!resp.ok) { localStorage.removeItem("eval_browser_session"); location.reload(); return; }
  const data = await resp.json();
  state.role = data.role;
  state.runs = data.runs;
  $("start-screen").style.display = "none";
  $("main").style.display = "block";
  if (state.role === "debug") {
    $("debug-label").style.display = "inline";
    $("tab-agg").style.display = "inline-block";
  }
  const rs = $("run-select");
  rs.innerHTML = state.runs.map((r) =>
    `<option value="${esc(r.run_ref)}">${esc(r.run_ref)}</option>`).join("");
  await onRunChange();
}

function currentRun() {
  return state.runs.find((r) => r.run_ref === state.runRef);
}

async function onRunChange() {
  state.runRef = $("run-select").value || (state.runs[0] && state.runs[0].run_ref);
  state.runIndexes = {};
  const run = currentRun();
  if (!run) return;
  $("condition-badge").textContent = run.condition || "";
  const fs = $("folder-select");
  fs.innerHTML = run.folders.map((f) =>
    `<option value="${esc(f.folder)}">${esc(f.folder)} (day ${f.day}, ${f.n_events} ev, ${f.n_rendered} rendered)</option>`
  ).join("");
  await onFolderChange();
}

async function onFolderChange() {
  state.folder = $("folder-select").value;
  state.cardPos = 0;
  state.trajObject = null;
  const resp = await fetch(`/api/index/${encodeURIComponent(state.runRef)}/${encodeURIComponent(state.folder)}?session=${encodeURIComponent(state.token || "")}`);
  if (!resp.ok) { alert("failed to load index"); return; }
  state.index = await resp.json();
  state.runIndexes[state.folder] = state.index;
  populateFilterOptions();
  renderAll();
}

// ── filters (debug only) ────────────────────────────────────────────────

function debugOn() { return state.role === "debug" && $("debug-toggle").checked; }

function populateFilterOptions() {
  const evs = (state.index && state.index.events) || [];
  const fill = (id, values) => {
    const sel = $(id), prev = sel.value;
    sel.innerHTML = '<option value="">all</option>' +
      [...new Set(values.filter(Boolean))].sort().map((v) => `<option>${esc(v)}</option>`).join("");
    sel.value = prev;
  };
  fill("f-occupant", evs.map((e) => e.occupant));
  fill("f-category", evs.map((e) => e.category));
  fill("f-anchor", evs.map((e) => e.to_semantic));
}

function clearFilters() {
  ["f-occupant", "f-category", "f-anchor"].forEach((id) => { $(id).value = ""; });
  ["f-jmin", "f-jmax"].forEach((id) => { $(id).value = ""; });
  $("f-rendered").checked = false;
  renderAll();
}

function filteredEvents() {
  let evs = (state.index && state.index.events) || [];
  if (!debugOn()) return evs;
  const occ = $("f-occupant").value, cat = $("f-category").value, anc = $("f-anchor").value;
  const jmin = parseFloat($("f-jmin").value), jmax = parseFloat($("f-jmax").value);
  const rendered = $("f-rendered").checked;
  return evs.filter((e) =>
    (!occ || e.occupant === occ) &&
    (!cat || e.category === cat) &&
    (!anc || e.to_semantic === anc) &&
    (isNaN(jmin) || (e.judge_score ?? -1) >= jmin) &&
    (isNaN(jmax) || (e.judge_score ?? 2) <= jmax) &&
    (!rendered || e.render.url));
}

// ── view switching ──────────────────────────────────────────────────────

function setView(v) {
  state.view = v;
  renderAll();
}

function renderAll() {
  const dbg = debugOn();
  $("filter-bar").style.display = dbg ? "flex" : "none";
  $("condition-badge").style.display = dbg ? "inline-block" : "none";
  for (const [tab, view] of [["tab-cards", "cards"], ["tab-timeline", "timeline"], ["tab-agg", "agg"]])
    $(tab).classList.toggle("active", state.view === view);
  if (state.view === "agg" && state.role !== "debug") state.view = "cards";
  $("card-view").style.display = state.view === "cards" ? "block" : "none";
  $("timeline-view").style.display = state.view === "timeline" ? "block" : "none";
  $("agg-view").style.display = state.view === "agg" ? "block" : "none";
  if (!state.index) return;
  if (state.view === "cards") renderCard();
  else if (state.view === "timeline") renderTimeline();
  else renderAggregate();
}

// ── EventCard view ──────────────────────────────────────────────────────

function occupantByName(name) {
  return ((state.index && state.index.occupants) || []).find((o) => o.name === name);
}

function renderImage(ev, cls) {
  if (!ev.render.url)
    return `<div class="no-render">not rendered in this batch</div>`;
  const bad = ev.render.mask_status && ev.render.mask_status !== "ok";
  const overlay = bad
    ? `<div class="mask-overlay">&#9888; automated view check flagged this render
       (<b>${esc(ev.render.mask_status)}</b>) — the object may not be clearly visible.</div>`
    : "";
  return `<div class="render-wrap ${cls || ""}">${overlay}<img src="${esc(ev.render.url)}" alt="before/after render" /></div>`;
}

function renderCard() {
  const evs = filteredEvents();
  $("filter-count").textContent = `${evs.length} events`;
  if (state.cardPos >= evs.length) state.cardPos = Math.max(0, evs.length - 1);
  $("card-pos").textContent = evs.length ? `${state.cardPos + 1} / ${evs.length}` : "0 / 0";
  const ev = evs[state.cardPos];
  if (!ev) { $("event-card").innerHTML = `<p class="hint">No events match.</p>`; return; }

  const occ = occupantByName(ev.occupant);
  const occHtml = occ
    ? `<span class="occupant-chip"><b>${esc(occ.name)}</b> — ${esc(occ.role)}, ${esc(occ.age_band)},
       tidiness ${occ.tidiness}${occ.owned_items && occ.owned_items.length ? `, owns: ${esc(occ.owned_items.join(", "))}` : ""}</span>`
    : (ev.occupant ? `<span class="occupant-chip"><b>${esc(ev.occupant)}</b></span>` : "");
  const from = ev.from_semantic ? `<span class="slot">${esc(ev.from_semantic)}</span>` : "<i>(new in scene)</i>";
  const cap = ev.capability_ok === false
    ? ` <span class="badge" style="background:var(--warn-bg);color:var(--warn-ink)">capability?</span>` : "";

  let dbgBox = "";
  if (debugOn()) {
    const lines = [
      `event_id:    ${ev.event_id}`,
      `judge_score: ${ev.judge_score ?? "—"}`,
      `stage_tag:   ${ev.stage_tag ?? "—"}`,
      `change_type: ${ev.change_type}`,
      `mask_status: ${ev.render.mask_status ?? "—"}`,
      ev.judge_think_excerpt ? `\njudge think:\n${ev.judge_think_excerpt}` : "",
    ];
    dbgBox = `<div class="debug-box" style="display:block">${esc(lines.filter(Boolean).join("\n"))}</div>`;
  }

  $("event-card").innerHTML = `
    <div class="event-card">
      <div class="ev-head">
        <span class="ev-time">${esc(ev.t_clock)}</span>
        <span class="ev-activity">${esc(ev.activity || "")}</span>
      </div>
      ${occHtml}
      <div class="move-line">
        <span class="obj">${esc(ev.object)}</span>
        <span class="badge">${esc(ev.category)}</span>${cap}<br/>
        ${from} <span class="arrow">&rarr;</span>
        <span class="slot">${esc(ev.to_semantic ?? "")}</span>
        ${ev.relation ? `<span class="badge">${esc(ev.relation)}</span>` : ""}
      </div>
      <div class="reason">${esc(ev.reason)}</div>
      ${renderImage(ev)}
      ${dbgBox}
    </div>`;
}

function prevCard() { if (state.cardPos > 0) { state.cardPos--; renderCard(); } }
function nextCard() { if (state.cardPos < filteredEvents().length - 1) { state.cardPos++; renderCard(); } }

document.addEventListener("keydown", (e) => {
  if (state.view !== "cards" || $("main").style.display === "none") return;
  if (e.target.tagName === "INPUT" || e.target.tagName === "TEXTAREA" || e.target.tagName === "SELECT") return;
  if (e.key === "ArrowLeft") prevCard();
  if (e.key === "ArrowRight") nextCard();
});

// ── DayTimeline view ────────────────────────────────────────────────────

function occColor(name) {
  const occs = (state.index.occupants || []).map((o) => o.name);
  const i = Math.max(0, occs.indexOf(name));
  return OCC_COLORS[i % OCC_COLORS.length];
}

function renderTimeline() {
  const idx = state.index;

  // trajectory strip
  const objs = Object.keys(idx.trajectories || {}).sort();
  $("obj-chips").innerHTML = objs.map((o) =>
    `<span class="obj-chip ${state.trajObject === o ? "active" : ""}" onclick="showTrajectory('${esc(o)}')">${esc(o)}
     <small>(${idx.trajectories[o].length})</small></span>`).join("");
  renderTrajPath();

  // per-occupant 24h activity tracks
  const H0 = 5, H1 = 25;  // display window 05:00 → 01:00
  const pct = (t) => `${(100 * (Math.min(Math.max(t, H0), H1) - H0) / (H1 - H0)).toFixed(2)}%`;
  const tracks = (idx.activities || []).map((a) => {
    const spans = (a.spans || []).map((s) => {
      const away = s.location === "away";
      return `<div class="track-span" title="${esc(s.activity)} (${esc(s.location || "")}) ${fmtT(s.start)}–${fmtT(s.end)}"
        style="left:${pct(s.start)};width:calc(${pct(s.end)} - ${pct(s.start)});
               background:${away ? "#c3c9d4" : occColor(a.occupant)}"></div>`;
    }).join("");
    return `<div class="track-row"><div class="track-name" style="color:${occColor(a.occupant)}">${esc(a.occupant)}</div>
            <div class="track-bar">${spans}</div></div>`;
  }).join("");
  const axisMarks = [];
  for (let h = H0; h <= H1; h += 4) axisMarks.push(`<span>${String(h % 24).padStart(2, "0")}:00</span>`);
  $("tracks").innerHTML = tracks
    ? tracks + `<div class="track-axis">${axisMarks.join("")}</div>`
    : `<p class="hint">no activity traces</p>`;

  // chronological feed: activity starts + events, merged
  const items = [];
  for (const a of idx.activities || [])
    for (const s of a.spans || [])
      items.push({ t: s.start, kind: "act", occupant: a.occupant, span: s });
  const evs = filteredEvents();
  for (const e of evs) items.push({ t: e.t, kind: "ev", ev: e });
  items.sort((x, y) => x.t - y.t);

  $("feed").innerHTML = items.map((it) => {
    if (it.kind === "act") {
      const s = it.span;
      return `<div class="feed-item" style="border-left-color:${occColor(it.occupant)}">
        <span class="ft">${fmtT(s.start)}–${fmtT(s.end)}</span>
        <span><b style="color:${occColor(it.occupant)}">${esc(it.occupant)}</b>
          ${esc(s.activity)} <span class="badge">${esc(s.location || "")}</span></span></div>`;
    }
    const e = it.ev;
    const thumb = e.render.url
      ? `<span class="thumb" onclick="jumpToEvent('${esc(e.event_id)}')"><img src="${esc(e.render.url)}" /></span>` : "";
    const score = debugOn() && e.judge_score != null ? `<span class="score">judge ${e.judge_score}</span>` : "";
    return `<div class="feed-item ev">
      <span class="ft">${esc(e.t_clock)}</span>
      ${thumb}
      <span><b>${esc(e.occupant || "")}</b> moved
        <span class="obj-link" onclick="showTrajectory('${esc(e.object)}')">${esc(e.object)}</span>
        ${e.from_semantic ? `from <span class="slot">${esc(e.from_semantic)}</span>` : "(new)"}
        to <span class="slot">${esc(e.to_semantic ?? "")}</span>
        <span class="badge">${esc(e.activity || "")}</span> ${score}<br/>
        <span class="reason" style="font-size:13px">${esc(e.reason)}</span></span></div>`;
  }).join("") || `<p class="hint">nothing to show</p>`;
}

function fmtT(t) {
  t = ((t % 24) + 24) % 24;
  return `${String(Math.floor(t)).padStart(2, "0")}:${String(Math.round((t % 1) * 60)).padStart(2, "0")}`;
}

function showTrajectory(obj) {
  state.trajObject = state.trajObject === obj ? null : obj;
  if (state.view !== "timeline") { state.view = "timeline"; renderAll(); return; }
  renderTimeline();
  $("traj-path").scrollIntoView({ behavior: "smooth", block: "nearest" });
}

function renderTrajPath() {
  const el = $("traj-path");
  const obj = state.trajObject;
  if (!obj || !state.index.trajectories[obj]) { el.style.display = "none"; return; }
  const hops = state.index.trajectories[obj];
  const start = hops.length ? hops[0].from : null;
  let html = `<b>${esc(obj)}</b>: `;
  html += `<span class="hop"><span class="hop-t">start</span><span class="slot">${esc(start ?? "not in scene")}</span></span>`;
  for (const h of hops)
    html += `<span class="hop-arrow">&rarr;</span><span class="hop"><span class="hop-t">${esc(h.t_clock)}</span><span class="slot">${esc(h.to)}</span></span>`;
  el.innerHTML = html;
  el.style.display = "block";
}

function jumpToEvent(eventId) {
  const evs = filteredEvents();
  const i = evs.findIndex((e) => e.event_id === eventId);
  if (i >= 0) { state.cardPos = i; state.view = "cards"; renderAll(); }
}

// ── Aggregate view (debug only) ─────────────────────────────────────────

const TOD_BUCKETS = [
  ["night", 0, 6], ["morning", 6, 11], ["midday", 11, 14],
  ["afternoon", 14, 18], ["evening", 18, 24],
];

function todBucket(t) {
  t = ((t % 24) + 24) % 24;
  for (const [name, a, b] of TOD_BUCKETS) if (t >= a && t < b) return name;
  return "night";
}

function roomOf(slot) {
  if (!slot) return "—";
  return String(slot).split(".")[0];
}

async function loadRunIndexes() {
  const run = currentRun();
  for (const f of run.folders) {
    if (!state.runIndexes[f.folder]) {
      const resp = await fetch(`/api/index/${encodeURIComponent(state.runRef)}/${encodeURIComponent(f.folder)}?session=${encodeURIComponent(state.token || "")}`);
      if (resp.ok) state.runIndexes[f.folder] = await resp.json();
    }
  }
}

async function renderAggregate() {
  await loadRunIndexes();
  const evs = [];
  for (const [folder, idx] of Object.entries(state.runIndexes))
    for (const e of idx.events || []) evs.push({ ...e, _folder: folder });

  buildMatrix("agg-tod", evs, (e) => todBucket(e.t), TOD_BUCKETS.map((b) => b[0]));
  const rooms = [...new Set(evs.map((e) => roomOf(e.to_semantic)))].sort();
  buildMatrix("agg-room", evs, (e) => roomOf(e.to_semantic), rooms);
}

function buildMatrix(elId, evs, colFn, cols) {
  const cats = [...new Set(evs.map((e) => e.category))].sort();
  const cells = {};
  let maxN = 1;
  for (const e of evs) {
    const k = `${e.category}|${colFn(e)}`;
    (cells[k] = cells[k] || []).push(e);
    maxN = Math.max(maxN, cells[k].length);
  }
  let html = `<table class="agg-table"><tr><th></th>${cols.map((c) => `<th>${esc(c)}</th>`).join("")}<th>total</th></tr>`;
  for (const cat of cats) {
    html += `<tr><td class="rowhead">${esc(cat)}</td>`;
    let tot = 0;
    for (const col of cols) {
      const k = `${cat}|${col}`, n = (cells[k] || []).length;
      tot += n;
      const bg = n ? `background:rgba(37,99,235,${(0.12 + 0.5 * n / maxN).toFixed(2)});color:${n / maxN > 0.6 ? "white" : "inherit"}` : "";
      html += `<td class="cell" style="${bg}" onclick="showAggCell('${esc(elId)}','${esc(cat)}','${esc(col)}')">${n || ""}</td>`;
    }
    html += `<td><b>${tot}</b></td></tr>`;
  }
  html += "</table>";
  $(elId).innerHTML = html;
  $(elId).dataset.cells = "";  // events resolved on click via closure store
  window._aggData = window._aggData || {};
  window._aggData[elId] = { cells, colFn };
}

function showAggCell(elId, cat, col) {
  const { cells } = window._aggData[elId];
  const evs = cells[`${cat}|${col}`] || [];
  $("agg-events").innerHTML = `<h4>${esc(cat)} × ${esc(col)} — ${evs.length} event(s)</h4>` +
    evs.map((e) => `<div class="feed-item ev">
      <span class="ft">${esc(e.t_clock)}</span>
      <span><span class="badge">${esc(e._folder)}</span> <b>${esc(e.occupant || "")}</b>
        ${esc(e.object)} ${e.from_semantic ? `from <span class="slot">${esc(e.from_semantic)}</span>` : "(new)"}
        to <span class="slot">${esc(e.to_semantic ?? "")}</span>
        ${debugOn() && e.judge_score != null ? `<span class="score">judge ${e.judge_score}</span>` : ""}<br/>
        <span class="reason" style="font-size:13px">${esc(e.reason)}</span></span></div>`).join("");
  $("agg-events").scrollIntoView({ behavior: "smooth", block: "nearest" });
}

// ── init ────────────────────────────────────────────────────────────────

(async function init() {
  // volunteer links: ?session=TOKEN skips the start screen entirely
  const urlTok = new URLSearchParams(location.search).get("session");
  if (urlTok) { state.token = urlTok; await boot(); return; }
  const saved = localStorage.getItem("eval_browser_session");
  if (saved) {
    try {
      const s = JSON.parse(saved);
      state.token = s.token;
      await boot();
      return;
    } catch { localStorage.removeItem("eval_browser_session"); }
  }
  $("name-input").addEventListener("keydown", (e) => { if (e.key === "Enter") startSession(); });
})();
