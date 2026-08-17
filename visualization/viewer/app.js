/* object-trace viewer — self-contained, no external libraries.
 *
 * Loads a trace.json produced by visualization/spatialize.py (plus the baked
 * map.png it references) and renders a topdown replay: one object's position
 * through the days with a time slider, its path so far, a dwell-weighted
 * trace build-up ("which locations does it frequent"), and autoplay.
 *
 * The household picker in the header is driven by visualization/traces.json
 * (see datasets.js); ?trace=<url of trace.json> overrides it for a timeline
 * that has not been published to the manifest yet.
 */
"use strict";

const DAY_NAMES = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"];
const ROOM_FILLS = ["#3d5a80", "#5a8a5e", "#8a5a72", "#7a6a3d", "#5a7a8a",
                    "#6a5a8a", "#8a6a4a"];
const SEG = {T0: 0, T1: 1, REC: 2, ROOM: 3, REL: 4, X: 5, Z: 6, CAUSE: 7};

const $ = id => document.getElementById(id);
const params = new URLSearchParams(location.search);
let TRACE_URL = params.get("trace");   // resolved against the manifest in boot()

let trace = null, mapImg = null;
let t = 0, horizon = 1;
let playing = false, lastFrame = 0;
let view = null;  // {px0, py0, pw, ph, scale, ox, oy} map-pixel crop -> canvas

// ---------------------------------------------------------------- helpers

function fmtTime(min) {
  const d = Math.floor(min / 1440), m = Math.floor(min % 1440);
  const hh = String(Math.floor(m / 60)).padStart(2, "0");
  const mm = String(m % 60).padStart(2, "0");
  return `d${String(d).padStart(2, "0")} ${DAY_NAMES[d % 7]} ${hh}:${mm}`;
}

function worldToCanvas(x, z) {
  const m = trace.map;
  const px = (x - m.bounds_min[0]) / m.meters_per_pixel;
  const py = (z - m.bounds_min[2]) / m.meters_per_pixel;
  return [(px - view.px0) * view.scale + view.ox,
          (py - view.py0) * view.scale + view.oy];
}

function segmentsOf(obj) { return trace.objects[obj].segments; }

function segmentAt(obj, time) {
  const segs = segmentsOf(obj);
  for (const s of segs) if (time >= s[SEG.T0] && time < s[SEG.T1]) return s;
  return segs[segs.length - 1];
}

function currentObject() { return $("object-select").value; }

// ---------------------------------------------------------------- layout

function computeView() {
  const canvas = $("map");
  const dpr = window.devicePixelRatio || 1;
  const cw = canvas.clientWidth * dpr, ch = canvas.clientHeight * dpr;
  canvas.width = cw; canvas.height = ch;

  const m = trace.map, bb = trace.view_bbox;
  const px0 = (bb[0][0] - m.bounds_min[0]) / m.meters_per_pixel;
  const py0 = (bb[0][1] - m.bounds_min[2]) / m.meters_per_pixel;
  const pw = (bb[1][0] - bb[0][0]) / m.meters_per_pixel;
  const ph = (bb[1][1] - bb[0][1]) / m.meters_per_pixel;
  const scale = Math.min(cw / pw, ch / ph) * 0.97;
  view = {px0, py0, pw, ph, scale,
          ox: (cw - pw * scale) / 2, oy: (ch - ph * scale) / 2};
}

// ---------------------------------------------------------------- drawing

function drawRooms(ctx) {
  trace.rooms.forEach((room, i) => {
    if (!room.poly.length) return;
    ctx.beginPath();
    room.poly.forEach(([x, z], j) => {
      const [cx, cy] = worldToCanvas(x, z);
      j ? ctx.lineTo(cx, cy) : ctx.moveTo(cx, cy);
    });
    ctx.closePath();
    ctx.fillStyle = ROOM_FILLS[i % ROOM_FILLS.length] + "3d";
    ctx.strokeStyle = ROOM_FILLS[i % ROOM_FILLS.length];
    ctx.lineWidth = 1.5;
    ctx.fill(); ctx.stroke();

    const cx = room.poly.reduce((a, p) => a + p[0], 0) / room.poly.length;
    const cz = room.poly.reduce((a, p) => a + p[1], 0) / room.poly.length;
    const [lx, ly] = worldToCanvas(cx, cz);
    ctx.fillStyle = "#dfe3ea";
    ctx.font = `600 ${12 * (window.devicePixelRatio || 1)}px system-ui`;
    ctx.textAlign = "center";
    ctx.fillText(room.id, lx, ly);
    ctx.fillStyle = "#8b93a1";
    ctx.font = `${10 * (window.devicePixelRatio || 1)}px system-ui`;
    ctx.fillText(room.region, lx, ly + 13 * (window.devicePixelRatio || 1));
  });

  // ELSEWHERE landing zone
  const [ex, ey] = worldToCanvas(...trace.elsewhere.pos);
  const dpr = window.devicePixelRatio || 1;
  ctx.setLineDash([5, 4]);
  ctx.strokeStyle = "#8b93a1";
  ctx.beginPath(); ctx.arc(ex, ey, 26 * dpr, 0, Math.PI * 2); ctx.stroke();
  ctx.setLineDash([]);
  ctx.fillStyle = "#8b93a1";
  ctx.font = `${10 * dpr}px system-ui`;
  ctx.textAlign = "center";
  ctx.fillText(trace.elsewhere.label, ex, ey + 38 * dpr);
}

function drawReceptacles(ctx) {
  const dpr = window.devicePixelRatio || 1;
  ctx.font = `${9 * dpr}px system-ui`;
  for (const [rid, r] of Object.entries(trace.receptacles)) {
    const [cx, cy] = worldToCanvas(...r.pos);
    ctx.strokeStyle = "#aab2c0";
    ctx.lineWidth = 1;
    const s = 3.5 * dpr;
    ctx.beginPath();
    ctx.moveTo(cx - s, cy); ctx.lineTo(cx + s, cy);
    ctx.moveTo(cx, cy - s); ctx.lineTo(cx, cy + s);
    ctx.stroke();
    ctx.fillStyle = "#aab2c07d";
    ctx.textAlign = "center";
    ctx.fillText(rid.replace(/_[a-z]\d$/, ""), cx, cy - 6 * dpr);
  }
}

function drawTraceBuildup(ctx, obj) {
  // dwell-weighted discs: which spots has this object occupied, and how long
  const dwell = new Map();  // "x,z" -> {x, z, minutes}
  for (const s of segmentsOf(obj)) {
    if (s[SEG.T0] >= t) break;
    const mins = Math.min(s[SEG.T1], t) - s[SEG.T0];
    const key = `${s[SEG.X]},${s[SEG.Z]}`;
    const cur = dwell.get(key) || {x: s[SEG.X], z: s[SEG.Z], minutes: 0};
    cur.minutes += mins;
    dwell.set(key, cur);
  }
  const max = Math.max(...[...dwell.values()].map(d => d.minutes), 1);
  const dpr = window.devicePixelRatio || 1;
  for (const d of dwell.values()) {
    const [cx, cy] = worldToCanvas(d.x, d.z);
    const r = (5 + 22 * Math.sqrt(d.minutes / max)) * dpr;
    ctx.beginPath(); ctx.arc(cx, cy, r, 0, Math.PI * 2);
    ctx.fillStyle = "rgba(255,184,77,0.16)";
    ctx.fill();
    ctx.strokeStyle = "rgba(255,184,77,0.45)";
    ctx.lineWidth = 1;
    ctx.stroke();
  }
}

function drawPath(ctx, obj) {
  const dpr = window.devicePixelRatio || 1;
  const pts = [];
  for (const s of segmentsOf(obj)) {
    if (s[SEG.T0] > t) break;
    pts.push(worldToCanvas(s[SEG.X], s[SEG.Z]));
  }
  if (pts.length < 2) return;
  ctx.strokeStyle = "rgba(110,193,255,0.55)";
  ctx.lineWidth = 1.5 * dpr;
  ctx.beginPath();
  pts.forEach(([x, y], i) => i ? ctx.lineTo(x, y) : ctx.moveTo(x, y));
  ctx.stroke();
  ctx.fillStyle = "rgba(110,193,255,0.5)";
  for (const [x, y] of pts.slice(0, -1)) {
    ctx.beginPath(); ctx.arc(x, y, 2 * dpr, 0, Math.PI * 2); ctx.fill();
  }
}

function drawResidents(ctx) {
  // small diamonds: where each resident is right now (from their realized
  // activity blocks; carried objects ride these positions)
  const dpr = window.devicePixelRatio || 1;
  for (const [res, segs] of Object.entries(trace.residents || {})) {
    const seg = segs.find(s => t >= s[0] && t < s[1]) || segs[segs.length - 1];
    if (!seg) continue;
    const [, , , , x, z, activity] = seg;
    const [cx, cy] = worldToCanvas(x, z);
    const r = 5 * dpr;
    ctx.fillStyle = "#7ee08a";
    ctx.strokeStyle = "#14161a";
    ctx.lineWidth = 1.2 * dpr;
    ctx.beginPath();
    ctx.moveTo(cx, cy - r); ctx.lineTo(cx + r, cy); ctx.lineTo(cx, cy + r);
    ctx.lineTo(cx - r, cy); ctx.closePath();
    ctx.fill(); ctx.stroke();
    ctx.fillStyle = "#7ee08a";
    ctx.font = `${9 * dpr}px system-ui`;
    ctx.textAlign = "center";
    ctx.fillText(`${res.replace("resident_", "R")}·${activity}`, cx, cy + r + 9 * dpr);
  }
}

function drawMarker(ctx, seg, faint, label) {
  const dpr = window.devicePixelRatio || 1;
  const [cx, cy] = worldToCanvas(seg[SEG.X], seg[SEG.Z]);
  const rel = seg[SEG.REL];
  ctx.globalAlpha = faint ? 0.35 : 1;
  ctx.fillStyle = rel === "away" ? "#8b93a1" : "#ffb84d";
  ctx.strokeStyle = rel === "carried" ? "#7ee08a" : "#14161a";        // carried = green ring
  ctx.lineWidth = (rel === "carried" ? 2.5 : 1.5) * dpr;
  const r = (faint ? 4 : 7) * dpr;
  ctx.beginPath();
  if (rel === "floor") ctx.rect(cx - r, cy - r, 2 * r, 2 * r);        // floor = square
  else if (rel === "hook") {                                          // hook = triangle
    ctx.moveTo(cx, cy - r); ctx.lineTo(cx + r, cy + r); ctx.lineTo(cx - r, cy + r);
    ctx.closePath();
  } else ctx.arc(cx, cy, r, 0, Math.PI * 2);                          // surface/away/carried = disc
  ctx.fill(); ctx.stroke();
  if (label) {
    ctx.fillStyle = faint ? "#8b93a1" : "#ffe1b3";
    ctx.font = `600 ${10 * dpr}px system-ui`;
    ctx.textAlign = "center";
    ctx.fillText(label, cx, cy - r - 4 * dpr);
  }
  ctx.globalAlpha = 1;
}

function draw() {
  const canvas = $("map"), ctx = canvas.getContext("2d");
  ctx.fillStyle = "#14161a";
  ctx.fillRect(0, 0, canvas.width, canvas.height);

  ctx.globalAlpha = 0.55;
  ctx.drawImage(mapImg, view.px0, view.py0, view.pw, view.ph,
                view.ox, view.oy, view.pw * view.scale, view.ph * view.scale);
  ctx.globalAlpha = 1;

  drawRooms(ctx);
  if ($("show-recs").checked) drawReceptacles(ctx);
  drawResidents(ctx);

  const obj = currentObject();
  if ($("show-trace").checked) drawTraceBuildup(ctx, obj);
  if ($("show-path").checked) drawPath(ctx, obj);

  if ($("show-others").checked)
    for (const o of Object.keys(trace.objects))
      if (o !== obj) drawMarker(ctx, segmentAt(o, t), true, null);

  drawMarker(ctx, segmentAt(obj, t), false, obj);
  updateReadout();
}

// ---------------------------------------------------------------- readout

function updateReadout() {
  const obj = currentObject();
  const seg = segmentAt(obj, t);
  $("clock").textContent = fmtTime(t);
  $("whereabouts").textContent =
    `${obj} — ${seg[SEG.ROOM]} / ${seg[SEG.REC]} (${seg[SEG.REL]})`;
  $("st-room").textContent = seg[SEG.ROOM];
  $("st-rec").textContent = seg[SEG.REC] === "ELSEWHERE"
    ? trace.elsewhere.label
    : seg[SEG.REC].startsWith("person:")
      ? `with ${seg[SEG.REC].slice(7)}` : seg[SEG.REC];
  $("st-rel").textContent = seg[SEG.REL];
  $("st-cause").textContent = seg[SEG.CAUSE].replace("activity:", "")
                                            .replace("reset:", "reset: ");
  $("st-since").textContent = fmtTime(seg[SEG.T0]);

  const segs = segmentsOf(obj);
  const i = segs.indexOf(seg);
  $("event-info").textContent =
    `segment ${i + 1}/${segs.length} · ${fmtTime(seg[SEG.T0])} → ${fmtTime(seg[SEG.T1])}`;
}

function drawEventStrip() {
  const strip = $("event-strip");
  const dpr = window.devicePixelRatio || 1;
  strip.width = strip.clientWidth * dpr;
  strip.height = 14 * dpr;
  const ctx = strip.getContext("2d");
  ctx.clearRect(0, 0, strip.width, strip.height);
  // day boundaries
  for (let d = 0; d <= trace.days; d++) {
    const x = (d * 1440 / horizon) * strip.width;
    ctx.fillStyle = d % 7 >= 5 ? "#5a5340" : "#2c313a";   // weekend tint
    ctx.fillRect(x, 0, 1.5, strip.height);
  }
  // one tick per segment start (an event that moved this object)
  ctx.fillStyle = "#6ec1ff";
  for (const s of segmentsOf(currentObject())) {
    if (s[SEG.CAUSE] === "initial") continue;
    const x = (s[SEG.T0] / horizon) * strip.width;
    ctx.fillRect(x, 2 * dpr, 1.5 * dpr, 10 * dpr);
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
  const mps = Number($("speed").value);
  let nt = t + mps * dt;
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

function jumpEvent(dir) {
  const segs = segmentsOf(currentObject());
  const times = segs.filter(s => s[SEG.CAUSE] !== "initial").map(s => s[SEG.T0]);
  const next = dir > 0 ? times.find(x => x > t)
                       : [...times].reverse().find(x => x < t);
  if (next !== undefined) setTime(next);
}

// ---------------------------------------------------------------- boot

function populateTracePicker(datasets) {
  // Household switcher: every timeline published in traces.json, plus — when
  // the page was opened on an unpublished one via ?trace= — that trace as its
  // own row, so the picker always shows what is actually on screen.
  const rows = datasets.map(d => ({
    label: d.label,
    search: `?trace=${encodeURIComponent(d.trace)}`,
  }));
  let current = datasets.findIndex(d => samePath(d.trace, TRACE_URL));
  if (current < 0) {
    rows.unshift({
      label: `${new URL(TRACE_URL, location.href).pathname} (not in traces.json)`,
      search: `?trace=${encodeURIComponent(TRACE_URL)}`,
    });
    current = 0;
  }
  wirePicker($("trace-select"), rows, current);
}

function linkToBeliefs(datasets) {
  // Carry the household across to the belief page instead of making the user
  // retype it. Households with no run recorded against them just link over
  // plainly and let that page open on its own first dataset.
  const d = datasets.find(x => samePath(x.trace, TRACE_URL));
  const run = d && d.runs && d.runs.length ? d.runs[0] : null;
  const link = $("beliefs-link");
  if (!run) {
    link.title = "no baselines run published for this household";
    return;
  }
  link.href = `beliefs.html?run=${encodeURIComponent(run.run)}` +
              `&trace=${encodeURIComponent(d.trace)}`;
  link.title = run.label;
}

async function boot() {
  const datasets = await loadDatasets();
  if (!TRACE_URL) {
    if (!datasets.length)
      throw new Error("no ?trace= given and visualization/traces.json is missing or empty");
    TRACE_URL = datasets[0].trace;
  }
  populateTracePicker(datasets);
  linkToBeliefs(datasets);

  trace = await (await fetch(TRACE_URL)).json();
  horizon = trace.days * 1440;

  const traceDirNote = `${trace.household} · scene ${trace.scene_id} · ` +
    `${trace.days} days · seed ${trace.seed}`;
  $("run-label").textContent = traceDirNote;
  document.title = `${trace.household} — object-trace viewer`;

  mapImg = new Image();
  mapImg.src = new URL(`../assets/${trace.scene_id}/map.png`,
                       location.href).href;
  await mapImg.decode();

  const sel = $("object-select");
  for (const [oid, o] of Object.entries(trace.objects)) {
    const opt = document.createElement("option");
    opt.value = oid;
    opt.textContent = `${oid} (${o.class})`;
    sel.appendChild(opt);
  }

  $("time").max = horizon;
  $("time").addEventListener("input", e => setTime(Number(e.target.value), true));
  sel.addEventListener("change", () => { drawEventStrip(); draw(); });
  for (const id of ["show-path", "show-trace", "show-others", "show-recs"])
    $(id).addEventListener("change", draw);
  $("play").addEventListener("click", () => togglePlay());
  $("prev-event").addEventListener("click", () => jumpEvent(-1));
  $("next-event").addEventListener("click", () => jumpEvent(+1));
  window.addEventListener("resize", () => { computeView(); drawEventStrip(); draw(); });
  document.addEventListener("keydown", e => {
    if (e.key === " ") { e.preventDefault(); togglePlay(); }
    if (e.key === "ArrowRight") jumpEvent(+1);
    if (e.key === "ArrowLeft") jumpEvent(-1);
  });

  computeView();
  drawEventStrip();
  setTime(0);
}

boot().catch(err => {
  document.body.innerHTML =
    `<pre style="padding:2em;color:#ff8a8a">failed to load trace:\n${err}\n\n` +
    `URL tried: ${TRACE_URL || "(none — no manifest entry, no ?trace=)"}\n` +
    `Serve via visualization/serve.py, not file://</pre>`;
});
