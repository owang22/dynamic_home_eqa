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
// resident tracks are shorter: no placement relation, and the last field is
// the activity they are doing rather than what caused a move
const RSEG = {T0: 0, T1: 1, REC: 2, ROOM: 3, X: 4, Z: 5, ACT: 6};

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

/* A carried object gets a new SEGMENT every time its carrier walks to a new
 * spot, but it has only MOVED when its receptacle changes (put down, picked
 * up, taken out). Everything user-facing — the tick strip, the ◀/▶ jumps,
 * the "N moves" labels — counts receptacle transitions, or a wallet riding
 * in a pocket all week claims hundreds of moves while its strip stays
 * blank. */
function transitionsOf(obj) {
  const segs = segmentsOf(obj), times = [];
  for (let i = 1; i < segs.length; i++)
    if (segs[i][SEG.REC] !== segs[i - 1][SEG.REC]) times.push(segs[i][SEG.T0]);
  return times;
}

function segmentAt(obj, time) {
  const segs = segmentsOf(obj);
  for (const s of segs) if (time >= s[SEG.T0] && time < s[SEG.T1]) return s;
  return segs[segs.length - 1];
}

/* Two expander artifacts should not reach the reader:
 *   linger_<receptacle>  — a synthesized block holding a resident in place
 *                          between authored activities; nobody "does" it
 *   <activity>__<rec>    — a per-location variant, split so four people can
 *                          share one "sleep" in four different beds
 * Both name a place the panel already shows on the row below. */
function prettyActivity(name) {
  const s = String(name);
  if (s.startsWith("linger_")) return "idle";
  const cut = s.indexOf("__");
  return cut > 0 ? s.slice(0, cut) : s;
}

function currentObject() { return $("object-select").value; }
function currentResident() { return $("resident-select").value; }

function residentTracks() { return trace.residents || {}; }

function residentSegmentAt(res, time) {
  const segs = residentTracks()[res] || [];
  for (const s of segs) if (time >= s[RSEG.T0] && time < s[RSEG.T1]) return s;
  return segs[segs.length - 1] || null;
}

/* Which objects is this resident holding right now — the readout answer to
 * "what has she got on her", which the object list alone cannot give. */
function carriedBy(res, time) {
  const held = [];
  for (const obj of Object.keys(trace.objects)) {
    const seg = segmentAt(obj, time);
    if (seg && seg[SEG.REC] === `person:${res}`) held.push(obj);
  }
  return held;
}

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

function drawResidentMarker(ctx, res, seg, selected) {
  // diamonds: where a resident is now, from their realized activity blocks.
  // The selected one is drawn larger and fully opaque so it can be followed
  // through a busy household without hunting for it.
  const dpr = window.devicePixelRatio || 1;
  const [cx, cy] = worldToCanvas(seg[RSEG.X], seg[RSEG.Z]);
  const r = (selected ? 8 : 5) * dpr;
  ctx.globalAlpha = selected ? 1 : 0.5;
  ctx.fillStyle = "#7ee08a";
  ctx.strokeStyle = selected ? "#e6ffe9" : "#14161a";
  ctx.lineWidth = (selected ? 2 : 1.2) * dpr;
  ctx.beginPath();
  ctx.moveTo(cx, cy - r); ctx.lineTo(cx + r, cy); ctx.lineTo(cx, cy + r);
  ctx.lineTo(cx - r, cy); ctx.closePath();
  ctx.fill(); ctx.stroke();
  ctx.fillStyle = selected ? "#c9f7d0" : "#7ee08a";
  ctx.font = `${(selected ? 10 : 9) * dpr}px system-ui`;
  ctx.textAlign = "center";
  ctx.fillText(`${res.replace("resident_", "R")}·${prettyActivity(seg[RSEG.ACT])}`,
               cx, cy + r + 10 * dpr);
  ctx.globalAlpha = 1;
}

function drawResidents(ctx) {
  const selected = currentResident();
  const showAll = $("show-all-res").checked;
  for (const [res, segs] of Object.entries(residentTracks())) {
    if (!showAll && res !== selected) continue;
    const seg = residentSegmentAt(res, t);
    if (seg) drawResidentMarker(ctx, res, seg, res === selected);
  }
}

function drawResidentPath(ctx) {
  const res = currentResident();
  const segs = residentTracks()[res] || [];
  const dpr = window.devicePixelRatio || 1;
  const pts = [];
  for (const s of segs) {
    if (s[RSEG.T0] > t) break;
    pts.push(worldToCanvas(s[RSEG.X], s[RSEG.Z]));
  }
  if (pts.length < 2) return;
  ctx.strokeStyle = "rgba(126,224,138,0.5)";
  ctx.lineWidth = 1.5 * dpr;
  ctx.setLineDash([4, 3]);
  ctx.beginPath();
  pts.forEach(([x, y], i) => i ? ctx.lineTo(x, y) : ctx.moveTo(x, y));
  ctx.stroke();
  ctx.setLineDash([]);
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

  if (mapImg) {
    ctx.globalAlpha = 0.55;
    ctx.drawImage(mapImg, view.px0, view.py0, view.pw, view.ph,
                  view.ox, view.oy, view.pw * view.scale, view.ph * view.scale);
    ctx.globalAlpha = 1;
  }

  drawRooms(ctx);
  if ($("show-recs").checked) drawReceptacles(ctx);

  const obj = currentObject();
  if ($("show-trace").checked) drawTraceBuildup(ctx, obj);
  if ($("show-res-path").checked) drawResidentPath(ctx);
  if ($("show-path").checked) drawPath(ctx, obj);
  drawResidents(ctx);

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

  updateResidentReadout();

  const following = $("jump-what").value;
  if (following === "resident") {
    const rsegs = residentTracks()[currentResident()] || [];
    const rseg = residentSegmentAt(currentResident(), t);
    const j = rsegs.indexOf(rseg);
    $("event-info").textContent = rseg
      ? `activity ${j + 1}/${rsegs.length} · ${fmtTime(rseg[RSEG.T0])} → ${fmtTime(rseg[RSEG.T1])}`
      : "no resident blocks";
    return;
  }
  const segs = segmentsOf(obj);
  const i = segs.indexOf(seg);
  $("event-info").textContent =
    `segment ${i + 1}/${segs.length} · ${fmtTime(seg[SEG.T0])} → ${fmtTime(seg[SEG.T1])}`;
}

function updateResidentReadout() {
  const res = currentResident();
  const seg = residentSegmentAt(res, t);
  if (!seg) {
    for (const id of ["rs-room", "rs-rec", "rs-activity", "rs-since", "rs-carrying"])
      $(id).textContent = "–";
    return;
  }
  const away = seg[RSEG.REC] === "ELSEWHERE";
  $("rs-room").textContent = away ? "out of the house" : seg[RSEG.ROOM];
  $("rs-rec").textContent = away ? trace.elsewhere.label : seg[RSEG.REC];
  $("rs-activity").textContent = prettyActivity(seg[RSEG.ACT]);
  $("rs-since").textContent = fmtTime(seg[RSEG.T0]);
  const held = carriedBy(res, t);
  $("rs-carrying").textContent = held.length ? held.join(", ") : "nothing";
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
  // upper half: one tick per receptacle change of the selected object
  ctx.fillStyle = "#6ec1ff";
  const moves = transitionsOf(currentObject());
  for (const t0 of moves) {
    const x = (t0 / horizon) * strip.width;
    ctx.fillRect(x, 2 * dpr, 1.5 * dpr, 5 * dpr);
  }
  if (!moves.length) {
    ctx.fillStyle = "#8b93a1";
    ctx.font = `${9 * dpr}px system-ui`;
    ctx.textAlign = "left";
    ctx.fillText("(this object never changes receptacle)", 4 * dpr, 11 * dpr);
  }
  // lower half: one tick per activity change of the selected resident, so
  // the two tracks can be read against each other — did she move it, or did
  // it drift while she was out?
  ctx.fillStyle = "#7ee08a";
  for (const s of residentTracks()[currentResident()] || []) {
    if (!s[RSEG.T0]) continue;
    const x = (s[RSEG.T0] / horizon) * strip.width;
    ctx.fillRect(x, 7 * dpr, 1.5 * dpr, 5 * dpr);
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
  const times = $("jump-what").value === "resident"
    ? (residentTracks()[currentResident()] || [])
        .map(s => s[RSEG.T0]).filter(Boolean)
    : transitionsOf(currentObject());
  const next = dir > 0 ? times.find(x => x > t)
                       : [...times].reverse().find(x => x < t);
  if (next !== undefined) setTime(next);
}

// ---------------------------------------------------------------- boot

/* Follow the build while it runs.
 *
 * serve.py rebuilds the dataset list from disk on every request, so polling
 * it picks up a household the moment its timeline lands — and re-fetching
 * the open trace when its file changes means a household you are LOOKING at
 * updates in place when it is rebuilt. Both are cheap (the list is a few KB,
 * the trace check is a HEAD), and without them the only way to see new work
 * was to restart the server and reload the page.
 */
/* Fill the object and resident pickers from the loaded trace, keeping the
 * current selections when they still exist (a rebuilt household usually
 * keeps most of its objects, and losing your place on every refresh would
 * make the live updating worse than useless). */
function rebuildPickers(keepObject, keepResident) {
  const sel = $("object-select"), rsel = $("resident-select");
  sel.innerHTML = "";
  // busiest objects first: with 40 in a household, the ones worth watching
  // should not be buried alphabetically behind the ones that never move
  const objects = Object.keys(trace.objects)
    .map(oid => [oid, transitionsOf(oid).length])
    .sort((a, b) => b[1] - a[1]);
  for (const [oid, n] of objects) {
    const opt = document.createElement("option");
    opt.value = oid;
    opt.textContent = `${oid} (${trace.objects[oid].class}) · ` +
      (n ? `${n} moves` : "never moves");
    sel.appendChild(opt);
  }
  if (keepObject && trace.objects[keepObject]) sel.value = keepObject;

  rsel.innerHTML = "";
  for (const res of Object.keys(residentTracks()).sort()) {
    const opt = document.createElement("option");
    opt.value = res;
    opt.textContent = res;
    rsel.appendChild(opt);
  }
  if (keepResident && residentTracks()[keepResident])
    rsel.value = keepResident;
}

const WATCH_INTERVAL_MS = 5000;
let knownDatasets = "";      // JSON of the last list, to spot changes
let traceStamp = null;       // Last-Modified of the open trace

async function watchForChanges() {
  try {
    const datasets = await loadDatasets();
    const signature = JSON.stringify(
        datasets.map(d => [d.label, d.trace, d.source]));
    if (knownDatasets && signature !== knownDatasets) {
      populateTracePicker(datasets);      // rebuilds source + household
      flash(`household list updated (${datasets.length} timelines)`);
    }
    knownDatasets = signature;

    const head = await fetch(TRACE_URL, {method: "HEAD"});
    const stamp = head.headers.get("Last-Modified");
    if (traceStamp && stamp && stamp !== traceStamp) {
      const fresh = await (await fetch(TRACE_URL)).json();
      const wasObject = currentObject(), wasResident = currentResident();
      trace = fresh;
      horizon = trace.days * 1440;
      rebuildPickers(wasObject, wasResident);
      computeView(); drawEventStrip(); setTime(Math.min(t, horizon - 1));
      flash("this household was rebuilt — reloaded");
    }
    traceStamp = stamp;
  } catch (e) {
    /* a mid-build moment can 404 or serve half a file; try again next tick */
  }
}

function flash(message) {
  const el = $("live-note");
  el.textContent = message;
  el.classList.add("show");
  setTimeout(() => el.classList.remove("show"), 4000);
}

function populateTracePicker(datasets) {
  // TWO pickers, source then household: every set numbers its households
  // hh1..hh10, so a flat list offers three rows called hh_001 with nothing
  // to tell them apart. Pick the set first, then the home within it.
  const open = datasets.find(d => samePath(d.trace, TRACE_URL));
  const sourceOf = d => d.source || "other";
  const sources = [...new Set(datasets.map(sourceOf))];
  const currentSource = open ? sourceOf(open) : sources[0];

  const srcSel = $("source-select");
  srcSel.innerHTML = "";
  sources.forEach(src => {
    const n = datasets.filter(d => sourceOf(d) === src).length;
    const opt = document.createElement("option");
    opt.value = src;
    opt.textContent = `${src} (${n})`;
    opt.selected = src === currentSource;
    srcSel.appendChild(opt);
  });
  srcSel.disabled = sources.length < 2;
  srcSel.onchange = () => {
    // jump to the first household of the newly chosen set
    const first = datasets.find(d => sourceOf(d) === srcSel.value);
    if (first) location.search = `?trace=${encodeURIComponent(first.trace)}`;
  };

  const mine = datasets.filter(d => sourceOf(d) === currentSource);
  const rows = mine.map(d => ({
    label: d.label,
    search: `?trace=${encodeURIComponent(d.trace)}`,
  }));
  let current = mine.findIndex(d => samePath(d.trace, TRACE_URL));
  if (current < 0) {
    rows.unshift({
      label: `${new URL(TRACE_URL, location.href).pathname} (not in traces.json)`,
      search: `?trace=${encodeURIComponent(TRACE_URL)}`,
    });
    current = 0;
  }
  const sel = $("trace-select");
  sel.innerHTML = "";
  wirePicker(sel, rows, current);
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
  const say = msg => { $("run-label").textContent = msg; };
  say("loading household list…");
  const datasets = await loadDatasets();
  if (!TRACE_URL) {
    if (!datasets.length)
      throw new Error("no ?trace= given and visualization/traces.json is missing or empty");
    TRACE_URL = datasets[0].trace;
  }
  populateTracePicker(datasets);
  linkToBeliefs(datasets);

  say(`loading ${TRACE_URL}…`);
  const res = await fetch(TRACE_URL);
  if (!res.ok) throw new Error(`${res.status} ${res.statusText} for ${TRACE_URL}`);
  trace = await res.json();
  horizon = trace.days * 1440;

  const traceDirNote = `${trace.household} · scene ${trace.scene_id} · ` +
    `${trace.days} days · seed ${trace.seed}`;
  say(traceDirNote);
  document.title = `${trace.household} — object-trace viewer`;

  const mapUrl = `/visualization/assets/${trace.scene_id}/map.png`;
  say(`loading map ${trace.scene_id}…`);
  mapImg = new Image();
  mapImg.src = mapUrl;
  try {
    await mapImg.decode();
  } catch (e) {
    // draw the household without its floor plan rather than not at all
    console.warn("map failed to decode", mapUrl, e);
    mapImg = null;
  }

  const sel = $("object-select");
  const rsel = $("resident-select");
  rebuildPickers();
  if (!rsel.options.length) {         // a timeline with no resident track
    rsel.appendChild(new Option("(none in this timeline)", ""));
    rsel.disabled = true;
  }

  $("time").max = horizon;
  $("time").addEventListener("input", e => setTime(Number(e.target.value), true));
  sel.addEventListener("change", () => { drawEventStrip(); draw(); });
  rsel.addEventListener("change", () => { drawEventStrip(); draw(); });
  $("jump-what").addEventListener("change", draw);
  for (const id of ["show-path", "show-res-path", "show-trace", "show-others",
                    "show-recs", "show-all-res"])
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

  // follow the build: new households appear, and a household that gets
  // rebuilt while you are watching it reloads in place
  setInterval(watchForChanges, WATCH_INTERVAL_MS);
  watchForChanges();
}

/* A blank dark page is the worst possible failure report: it looks the
 * same whether the trace 404'd, the JSON was half-written, or a draw threw.
 * Anything that escapes gets painted where it can be read. */
function fatal(what, err) {
  document.body.innerHTML =
    `<pre style="padding:2em;color:#ff8a8a;white-space:pre-wrap">` +
    `${what}\n\n${(err && err.stack) || err}\n\n` +
    `trace: ${TRACE_URL || "(none — no manifest entry, no ?trace=)"}\n` +
    `Serve via visualization/serve.py, not file://</pre>`;
}
window.addEventListener("error", e => fatal("viewer error", e.error || e.message));
window.addEventListener("unhandledrejection",
                        e => fatal("viewer error (async)", e.reason));

boot().catch(err => {
  document.body.innerHTML =
    `<pre style="padding:2em;color:#ff8a8a">failed to load trace:\n${err}\n\n` +
    `URL tried: ${TRACE_URL || "(none — no manifest entry, no ?trace=)"}\n` +
    `Serve via visualization/serve.py, not file://</pre>`;
});
