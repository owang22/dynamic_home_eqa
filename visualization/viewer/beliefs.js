/* belief-vs-truth viewer — overlays a baselines run (predicted locations at
 * question times) on the household topdown map, against the object's true
 * trajectory from the same timeline's trace.json.
 *
 * URL params:
 *   ?run=<url of baselines run_log.jsonl>   (default: hh_001 grid run)
 *   &trace=<url of trace.json>              (default: hh_001 timeline)
 *   &agent=<agent name>&object=<object id>  (optional preselects)
 *
 * The run's bank projects virtual locations to pseudo-receptacles; this
 * page maps them back for drawing: OUT_OF_HOUSE at the AWAY circle,
 * ON_PERSON at the (solo) resident's current position.
 */
"use strict";

const DAY_NAMES = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"];
const SEG = {T0: 0, T1: 1, REC: 2, ROOM: 3, REL: 4, X: 5, Z: 6};
const GOOD = "#7ee08a", BAD = "#ff8a8a", TRUTH = "#ffb84d";

const $ = id => document.getElementById(id);
const params = new URLSearchParams(location.search);
const RUN_URL = params.get("run") ||
  "../../smoke_results/baselines_hh001/run_log.jsonl";
const TRACE_URL = params.get("trace") ||
  "../../profiles/revamp_v1/claude-fable-5/timelines/hh_001_seed0/trace.json";

let trace = null, mapImg = null, records = [];
let t = 0, horizon = 1, playing = false, lastFrame = 0, view = null;

function fmtTime(min) {
  const d = Math.floor(min / 1440), m = Math.floor(min % 1440);
  return `d${String(d).padStart(2, "0")} ${DAY_NAMES[d % 7]} ` +
         `${String(Math.floor(m / 60)).padStart(2, "0")}:` +
         `${String(m % 60).padStart(2, "0")}`;
}

function worldToCanvas(x, z) {
  const m = trace.map;
  const px = (x - m.bounds_min[0]) / m.meters_per_pixel;
  const py = (z - m.bounds_min[2]) / m.meters_per_pixel;
  return [(px - view.px0) * view.scale + view.ox,
          (py - view.py0) * view.scale + view.oy];
}

function computeView() {
  const canvas = $("map");
  const dpr = window.devicePixelRatio || 1;
  canvas.width = canvas.clientWidth * dpr;
  canvas.height = canvas.clientHeight * dpr;
  const m = trace.map, bb = trace.view_bbox;
  const px0 = (bb[0][0] - m.bounds_min[0]) / m.meters_per_pixel;
  const py0 = (bb[0][1] - m.bounds_min[2]) / m.meters_per_pixel;
  const pw = (bb[1][0] - bb[0][0]) / m.meters_per_pixel;
  const ph = (bb[1][1] - bb[0][1]) / m.meters_per_pixel;
  const scale = Math.min(canvas.width / pw, canvas.height / ph) * 0.97;
  view = {px0, py0, pw, ph, scale,
          ox: (canvas.width - pw * scale) / 2,
          oy: (canvas.height - ph * scale) / 2};
}

// ------------------------------------------------------------ data access

function selectedRecords() {
  const agent = $("agent-select").value, obj = $("object-select").value;
  return records.filter(r => r.agent === agent && r.object_id === obj)
                .sort((a, b) => a.t_query - b.t_query);
}

function residentPosAt(min) {
  const residents = Object.values(trace.residents || {});
  if (!residents.length) return trace.elsewhere.pos;
  const segs = residents[0];
  const s = segs.find(s => min >= s[0] && min < s[1]) || segs[segs.length - 1];
  return [s[4], s[5]];
}

function anchorOf(receptacle, questionMin) {
  if (receptacle === "OUT_OF_HOUSE") return trace.elsewhere.pos;
  if (receptacle === "ON_PERSON") return residentPosAt(questionMin);
  const r = trace.receptacles[receptacle];
  return r ? r.pos : trace.elsewhere.pos;
}

function truthSegAt(obj, min) {
  const segs = trace.objects[obj].segments;
  return segs.find(s => min >= s[SEG.T0] && min < s[SEG.T1]) ||
         segs[segs.length - 1];
}

function lastQuestionAt(min) {
  const rs = selectedRecords();
  let last = null;
  for (const r of rs) {
    if (r.t_query / 60 <= min) last = r;
    else break;
  }
  return last;
}

// ---------------------------------------------------------------- drawing

function drawRooms(ctx) {
  const dpr = window.devicePixelRatio || 1;
  trace.rooms.forEach((room, i) => {
    if (!room.poly.length) return;
    ctx.beginPath();
    room.poly.forEach(([x, z], j) => {
      const [cx, cy] = worldToCanvas(x, z);
      j ? ctx.lineTo(cx, cy) : ctx.moveTo(cx, cy);
    });
    ctx.closePath();
    ctx.fillStyle = "#3d5a8022";
    ctx.strokeStyle = "#3d5a80";
    ctx.lineWidth = 1;
    ctx.fill(); ctx.stroke();
    const cx = room.poly.reduce((a, p) => a + p[0], 0) / room.poly.length;
    const cz = room.poly.reduce((a, p) => a + p[1], 0) / room.poly.length;
    const [lx, ly] = worldToCanvas(cx, cz);
    ctx.fillStyle = "#8b93a1";
    ctx.font = `600 ${11 * dpr}px system-ui`;
    ctx.textAlign = "center";
    ctx.fillText(room.id, lx, ly);
  });
  const [ex, ey] = worldToCanvas(...trace.elsewhere.pos);
  ctx.setLineDash([5, 4]);
  ctx.strokeStyle = "#8b93a1";
  ctx.beginPath(); ctx.arc(ex, ey, 24 * dpr, 0, Math.PI * 2); ctx.stroke();
  ctx.setLineDash([]);
  ctx.fillStyle = "#8b93a1";
  ctx.font = `${10 * dpr}px system-ui`;
  ctx.textAlign = "center";
  ctx.fillText(trace.elsewhere.label, ex, ey + 34 * dpr);
}

function drawReceptacles(ctx) {
  const dpr = window.devicePixelRatio || 1;
  for (const r of Object.values(trace.receptacles)) {
    const [cx, cy] = worldToCanvas(...r.pos);
    ctx.strokeStyle = "#aab2c07d";
    ctx.lineWidth = 1;
    const s = 3 * dpr;
    ctx.beginPath();
    ctx.moveTo(cx - s, cy); ctx.lineTo(cx + s, cy);
    ctx.moveTo(cx, cy - s); ctx.lineTo(cx, cy + s);
    ctx.stroke();
  }
}

function draw() {
  const canvas = $("map"), ctx = canvas.getContext("2d");
  const dpr = window.devicePixelRatio || 1;
  ctx.fillStyle = "#14161a";
  ctx.fillRect(0, 0, canvas.width, canvas.height);
  ctx.globalAlpha = 0.5;
  ctx.drawImage(mapImg, view.px0, view.py0, view.pw, view.ph,
                view.ox, view.oy, view.pw * view.scale, view.ph * view.scale);
  ctx.globalAlpha = 1;
  drawRooms(ctx);
  drawReceptacles(ctx);

  const obj = $("object-select").value;
  const truthSeg = truthSegAt(obj, t);
  const [tx, ty] = worldToCanvas(truthSeg[SEG.X], truthSeg[SEG.Z]);
  const q = lastQuestionAt(t);

  if (q) {
    const [px, py] = worldToCanvas(...anchorOf(q.answer_receptacle,
                                              q.t_query / 60));
    const color = q.correct ? GOOD : BAD;
    if (!q.correct) {
      ctx.setLineDash([6, 5]);
      ctx.strokeStyle = color;
      ctx.lineWidth = 1.5 * dpr;
      ctx.beginPath(); ctx.moveTo(px, py); ctx.lineTo(tx, ty); ctx.stroke();
      ctx.setLineDash([]);
    }
    ctx.strokeStyle = color;
    ctx.lineWidth = 3 * dpr;
    ctx.beginPath(); ctx.arc(px, py, 10 * dpr, 0, Math.PI * 2); ctx.stroke();
    ctx.fillStyle = color;
    ctx.font = `600 ${10 * dpr}px system-ui`;
    ctx.textAlign = "center";
    ctx.fillText(`predicted: ${q.answer_receptacle}`, px, py - 14 * dpr);
  }

  ctx.fillStyle = TRUTH;
  ctx.strokeStyle = "#14161a";
  ctx.lineWidth = 1.5 * dpr;
  ctx.beginPath(); ctx.arc(tx, ty, 7 * dpr, 0, Math.PI * 2);
  ctx.fill(); ctx.stroke();
  ctx.fillStyle = "#ffe1b3";
  ctx.font = `600 ${10 * dpr}px system-ui`;
  ctx.textAlign = "center";
  ctx.fillText(obj, tx, ty + 20 * dpr);

  updateReadout(truthSeg, q);
}

function updateReadout(truthSeg, q) {
  const obj = $("object-select").value;
  $("clock").textContent = fmtTime(t);
  $("whereabouts").textContent =
    `${obj} — truth: ${truthSeg[SEG.ROOM]} / ${truthSeg[SEG.REC]}`;
  $("st-truth").textContent = `${truthSeg[SEG.REC]} (${truthSeg[SEG.ROOM]})`;
  if (!q) {
    for (const id of ["st-q", "st-pred", "st-conf", "st-verdict", "st-budget", "st-acc"])
      $(id).textContent = "–";
    $("dist").textContent = "no question asked yet";
    return;
  }
  $("st-q").textContent = `${q.question_id} @ ${fmtTime(q.t_query / 60)}`;
  $("st-pred").textContent = q.answer_receptacle;
  $("st-conf").textContent = q.confidence.toFixed(2);
  $("st-verdict").innerHTML = q.correct
    ? `<span style="color:${GOOD}">correct</span>`
    : `<span style="color:${BAD}">wrong — was ${q.truth_receptacle}</span>`;
  $("st-budget").textContent = `${q.budget_spent} (day budget left: ${q.budget_after})`;
  const asked = selectedRecords().filter(r => r.t_query <= q.t_query);
  const right = asked.filter(r => r.correct).length;
  $("st-acc").textContent = `${right}/${asked.length} (${(right / asked.length).toFixed(2)})`;
  const top = Object.entries(q.distribution).sort((a, b) => b[1] - a[1]).slice(0, 4);
  $("dist").innerHTML = top.map(([r, p]) =>
    `${r}: ${p.toFixed(2)}`).join("<br>");
}

function drawEventStrip() {
  const strip = $("event-strip");
  const dpr = window.devicePixelRatio || 1;
  strip.width = strip.clientWidth * dpr;
  strip.height = 14 * dpr;
  const ctx = strip.getContext("2d");
  for (let d = 0; d <= trace.days; d++) {
    const x = (d * 1440 / horizon) * strip.width;
    ctx.fillStyle = d % 7 >= 5 ? "#5a5340" : "#2c313a";
    ctx.fillRect(x, 0, 1.5, strip.height);
  }
  for (const r of selectedRecords()) {
    ctx.fillStyle = r.correct ? GOOD : BAD;
    const x = (r.t_query / 60 / horizon) * strip.width;
    ctx.fillRect(x, 2 * dpr, 2 * dpr, 10 * dpr);
  }
}

// ---------------------------------------------------------------- control

function setTime(newT, fromSlider = false) {
  t = Math.max(0, Math.min(horizon - 1, newT));
  if (!fromSlider) $("time").value = t;
  draw();
}

function tick(now) {
  if (!playing) return;
  const dt = (now - lastFrame) / 1000;
  lastFrame = now;
  let nt = t + Number($("speed").value) * dt;
  if (nt >= horizon - 1) { nt = horizon - 1; togglePlay(false); }
  setTime(nt);
  requestAnimationFrame(tick);
}

function togglePlay(on = !playing) {
  playing = on;
  $("play").textContent = playing ? "⏸" : "▶";
  $("play").classList.toggle("playing", playing);
  if (playing) {
    if (t >= horizon - 2) setTime(0);
    lastFrame = performance.now();
    requestAnimationFrame(tick);
  }
}

function jumpQuestion(dir) {
  const times = selectedRecords().map(r => r.t_query / 60);
  const next = dir > 0 ? times.find(x => x > t)
                       : [...times].reverse().find(x => x < t);
  if (next !== undefined) setTime(next + 1);
}

// -------------------------------------------------------------------- boot

async function boot() {
  trace = await (await fetch(TRACE_URL)).json();
  horizon = trace.days * 1440;
  const runText = await (await fetch(RUN_URL)).text();
  records = runText.trim().split("\n").map(line => JSON.parse(line));

  mapImg = new Image();
  mapImg.src = new URL(`../assets/${trace.scene_id}/map.png`, location.href).href;
  await mapImg.decode();

  const agents = [...new Set(records.map(r => r.agent))].sort();
  const objects = [...new Set(records.map(r => r.object_id))].sort();
  for (const [sel, values, preset] of
       [[$("agent-select"), agents, params.get("agent")],
        [$("object-select"), objects, params.get("object")]]) {
    for (const v of values) {
      const opt = document.createElement("option");
      opt.value = opt.textContent = v;
      sel.appendChild(opt);
    }
    if (preset && values.includes(preset)) sel.value = preset;
    sel.addEventListener("change", () => { drawEventStrip(); draw(); });
  }
  $("run-label").textContent =
    `${trace.household} · ${records.length} answers · ` +
    `${agents.length} agents · ${objects.length} objects`;

  $("time").max = horizon;
  $("time").addEventListener("input", e => setTime(Number(e.target.value), true));
  $("play").addEventListener("click", () => togglePlay());
  window.addEventListener("resize", () => { computeView(); drawEventStrip(); draw(); });
  document.addEventListener("keydown", e => {
    if (e.key === " ") { e.preventDefault(); togglePlay(); }
    if (e.key === "ArrowRight") jumpQuestion(+1);
    if (e.key === "ArrowLeft") jumpQuestion(-1);
  });

  computeView();
  drawEventStrip();
  // Open on the first question so the page never starts empty.
  const first = selectedRecords()[0];
  setTime(first ? first.t_query / 60 + 1 : 0);
}

boot().catch(err => {
  document.body.innerHTML =
    `<pre style="padding:2em;color:#ff8a8a">failed to load:\n${err}\n\n` +
    `run URL: ${RUN_URL}\ntrace URL: ${TRACE_URL}\n` +
    `Serve via visualization/serve.py, not file://</pre>`;
});
