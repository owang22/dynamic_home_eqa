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
const SEG = {T0: 0, T1: 1, REC: 2, ROOM: 3, REL: 4, X: 5, Z: 6, CAUSE: 7,
             KIND: 8};
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

// -------------------------------------------------------- why it moved

/* The provenance behind the segment the slider is sitting in.
 *
 * trace.json records WHAT moved and which activity moved it; spatialize.py
 * bakes in the RATIONALE beside it (trace.provenance) — the `cites` line
 * the generator wrote for each object and each rule, plus which activities
 * are trips. This turns "caused by: work_away" into the actual answer.
 *
 * The distinction that matters, and the reason `kind` is carried on every
 * segment: most carries are NOT authored. An object whose rule names any
 * leg of its owner's trips is promoted to a "traveller" and then rides
 * every trip that owner takes — which is why suitcase_elena leaves with
 * work_away on the strength of a rule about study. Reporting the trip's
 * own (nonexistent) rule there would be a fabrication, so a derived move
 * is labelled derived and names the rule that actually qualified it.
 */

function provenance() { return (trace && trace.provenance) || {}; }
function objProvenance(obj) { return (provenance().objects || {})[obj] || null; }

/* Trips, as the set of names a rule might use: the expander splits
 * per-person variants ("study__resident_1"), but a rule names the base
 * ("study"), and the same household can run `study` at home too. */
function tripNames() {
  const out = new Set();
  for (const a of provenance().away_activities || []) {
    out.add(a);
    out.add(prettyActivity(a));
  }
  return out;
}

/* Matched the way the expander matched it: on the activity base, since
 * rules name `study` while the timeline runs `study__resident_1`. */
function ruleFor(info, activity, phase) {
  const base = prettyActivity(activity);
  return (info.rules || []).find(
    r => (r.activity === activity || r.activity === base) &&
         (!phase || r.phase === phase)) || null;
}

function residentName(rid) {
  const r = (trace.resident_info || {})[rid] || {};
  return r.name || rid;
}

/* The rule's destinations, with the one this move actually took marked.
 * A rule is a weighted draw, so the odds are half the explanation: "it
 * went to the entry" reads very differently at p=0.15 than at p=0.85. */
function distTable(rule, took) {
  if (!rule.dist || !rule.dist.length) return "";
  const rows = rule.dist.map(([dest, p]) => {
    const hit = dest === took;
    const label = dest === "NO_OP" ? "stay where it is" : dest;
    return `<tr class="${hit ? "took" : ""}"><td>${escapeHtml(label)}` +
           `${hit ? " ←" : ""}</td>` +
           `<td class="p">${p == null ? "" : Number(p).toFixed(2)}</td></tr>`;
  }).join("");
  return `<table class="dist">${rows}</table>`;
}

function badge(cls, text) {
  return `<span class="why-how ${cls}">${escapeHtml(text)}</span>`;
}

function line(html) { return `<div class="why-line">${html}</div>`; }

function quote(text) { return `<q>${escapeHtml(text)}</q>`; }

/* Everything the generator said about this object, as the closing note —
 * the per-object `cites` is the standing intent ("keys belong in the entry
 * dish") that the per-rule cites are variations on. */
function objectNote(info) {
  if (!info.cites) return "";
  return line(`<span class="muted">about this object:</span>`) +
         quote(info.cites);
}

function explainSegment(obj, seg) {
  const info = objProvenance(obj);
  if (!info) {
    const pv = provenance();
    return `<div class="muted small">` +
      (pv.program
        ? `no movement rules were authored for ${escapeHtml(obj)}.`
        : `this set carries no authored rationale — its households were ` +
          `built before the movement pass wrote one.`) + `</div>`;
  }
  const cause = String(seg[SEG.CAUSE] || "");
  const kind = String(seg[SEG.KIND] || "");
  // Causes are "<mechanism>:<activity>" — activity: for a rule or a carry,
  // tidy: for a tidy-walk return. Both name the activity that was running.
  const activity = cause.includes(":") ? cause.slice(cause.indexOf(":") + 1) : "";
  const act = prettyActivity(activity);
  const landed = seg[SEG.REC];

  if (kind === "initial" || cause === "initial")
    return badge("", "starting placement") +
      line(`It began the episode at its home, ` +
           `<strong>${escapeHtml(info.home || landed)}</strong>, and had not ` +
           `been moved yet.`) +
      objectNote(info);

  if (kind === "misplace") {
    // Once per day, at a random waking minute, into a random member of the
    // object's misplace_set — see the drift block in
    // profiles/revamp_v1/simulate_activities.py. Not tied to an activity,
    // which is exactly why the cause column reads "misplace" and no rule
    // can be quoted for it.
    const p = info.p_misplace;
    const set = info.misplace_set || [];
    return badge("chance", "chance drift") +
      line(`No rule and no activity put it here. ${escapeHtml(obj)} is ` +
           `absent-minded: on any given day it has a ` +
           `<strong>${p == null ? "small" : Number(p).toFixed(2)}</strong> ` +
           `chance of being set down at a random waking moment somewhere ` +
           `other than home. Today it was, so it is at ` +
           `<strong>${escapeHtml(landed)}</strong> instead of ` +
           `<strong>${escapeHtml(info.home || "?")}</strong>.`) +
      (set.length
        ? line(`<span class="muted">drifts only into: ` +
               `${escapeHtml(set.join(", "))}</span>`)
        : "") +
      objectNote(info);
  }

  if (kind === "tidy")
    // The tidy walk is a property of the ACTIVITY, not of the object: any
    // out-of-place thing in scope gets walked home during it, so there is
    // no per-object rule to quote and the object's own `cites` (which
    // names its home) is the whole of the rationale.
    return badge("derived", `tidied during ${act}`) +
      line(`No rule of ${escapeHtml(obj)}'s fired. ` +
           `<strong>${escapeHtml(act)}</strong> includes a tidy walk, which ` +
           `collects whatever is out of place and puts it back — so it was ` +
           `carried home to <strong>${escapeHtml(landed)}</strong>.`) +
      objectNote(info);

  if (kind === "carry_pickup") {
    const who = info.owner ? residentName(info.owner) : "its owner";
    // A pickup can only be AUTHORED by a `during` rule ("this thing is with
    // her while she does X"). Every rule these sets carry is `after`, which
    // describes the homecoming, not the leaving — quoting one here would
    // credit the model with a decision the expander actually made.
    const authored = ruleFor(info, activity, "during");
    const trips = tripNames();
    const own = (info.rules || []).filter(r => trips.has(r.activity));
    // Prefer the rule for THIS trip when it has one: "its own work_away
    // rule" is a better answer than some other trip that also qualifies.
    const qualifier = own.find(r => r.activity === activity ||
                                    r.activity === act) || own[0];
    let html = badge(authored ? "authored" : "derived",
                     authored ? "carried · authored" : "carried · derived") +
      line(`<strong>${escapeHtml(who)}</strong> took it along on ` +
           `<strong>${escapeHtml(act)}</strong>.`);
    if (authored) {
      html += quote(authored.cites || "(no cites on that rule)");
    } else if (qualifier) {
      const sameTrip = qualifier.activity === activity ||
                       qualifier.activity === act;
      html += line(`No rule says to take it: rules only say where things ` +
                   `LAND. ${escapeHtml(obj)} is one of ` +
                   `${escapeHtml(who)}'s <em>travelling</em> things — it has ` +
                   `a rule about a trip, so it rides <em>every</em> trip ` +
                   `${escapeHtml(who)} takes` +
                   (sameTrip
                     ? `, this one included:`
                     : `. Here it is riding <strong>${escapeHtml(act)}</strong>` +
                       ` on the strength of its rule for ` +
                       `<strong>${escapeHtml(qualifier.activity)}</strong>:`)) +
              quote(qualifier.cites || "(no cites on that rule)");
    } else {
      // It travels, but no rule of its own names a trip in the FINAL
      // calendar. That is the chain merge: legs get folded into the trip
      // they happened on (a coffee stop absorbed into the walk), and the
      // absorbed leg is what the object was promoted on. The qualifying
      // occurrence no longer exists to point at, so say that plainly
      // rather than inventing a rule for it.
      const named = (info.rules || []).map(r => r.activity);
      html += line(`<span class="muted">It travels, but no rule of ` +
                   `${escapeHtml(obj)}'s names a trip in the final ` +
                   `calendar` +
                   (named.length
                     ? ` (its rules are for ${escapeHtml(named.join(", "))})`
                     : ``) +
                   `. It was promoted on a trip leg that the expander ` +
                   `merged into a larger trip — a coffee stop folded into ` +
                   `the walk it happened on — so the occurrence that ` +
                   `qualified it is no longer in the calendar to point ` +
                   `at.</span>`);
    }
    return html + objectNote(info);
  }

  if (kind === "carry_putdown") {
    const rule = ruleFor(info, activity, "after");
    const who = info.owner ? residentName(info.owner) : "its owner";
    let html = badge(rule ? "authored" : "derived",
                     rule ? "homecoming · authored" : "homecoming · derived") +
      line(`It came off ${escapeHtml(who)} on the way back in from ` +
           `<strong>${escapeHtml(act)}</strong>, and was left at ` +
           `<strong>${escapeHtml(landed)}</strong>.`);
    if (rule) {
      if (rule.cites) html += quote(rule.cites);
      html += distTable(rule, landed);
    } else {
      html += line(`No after-rule was written for ${escapeHtml(act)}, so the ` +
                   `expander synthesized the putdown: a travelling object ` +
                   `goes back to its home, ` +
                   `<strong>${escapeHtml(info.home || landed)}</strong>, when ` +
                   `its owner comes home.`);
    }
    return html + objectNote(info);
  }

  // kind "rule" (and anything a future engine adds): an authored after-rule
  const rule = ruleFor(info, activity, "after") || ruleFor(info, activity, null);
  if (rule) {
    let html = badge("authored", `after ${act}`) +
      line(`<strong>${escapeHtml(act)}</strong> fired ${escapeHtml(obj)}'s ` +
           `own rule, which drew ` +
           `<strong>${escapeHtml(landed)}</strong>:`);
    if (rule.cites) html += quote(rule.cites);
    return html + distTable(rule, landed) + objectNote(info);
  }
  return badge("", prettyActivity(cause)) +
    line(`<span class="muted">${escapeHtml(act || cause)} moved it to ` +
         `${escapeHtml(landed)}, but no rule of ${escapeHtml(obj)}'s names ` +
         `that activity.</span>`) +
    objectNote(info);
}

/* The movement pass reasons once about the whole household before it
 * writes a single rule; the per-rule cites are notes against that plan.
 * Folded away because it is the same paragraph for every object and every
 * moment — worth reading once, not worth re-reading on every move. */
function householdPlan() {
  const why = provenance().movement_reasoning;
  if (!why) return "";
  return `<details class="why-plan"><summary>the plan for this household` +
         `</summary>${quote(why)}</details>`;
}

function updateWhy() {
  const section = $("why-section");
  if (!section) return;
  if (!$("show-why").checked) { section.style.display = "none"; return; }
  section.style.display = "";
  const obj = currentObject();
  // The <details> is rebuilt with the rest of the panel, so its open/closed
  // state is remembered here rather than lost on every slider tick.
  const open = section.querySelector("details");
  const wasOpen = open ? open.open : false;
  $("why").innerHTML = explainSegment(obj, segmentAt(obj, t)) + householdPlan();
  const now = section.querySelector("details");
  if (now) now.open = wasOpen;
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

  updateWhy();
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
/* The household roster: who resident_N is. Ids are positional and mean
 * nothing on their own, so a multi-resident timeline is otherwise a set
 * of anonymous tracks. Rows are clickable — picking a person here is the
 * same action as choosing them in the resident dropdown. Sets built
 * before trace.resident_info existed fall back to the bare id list. */
function renderRoster() {
  const el = $("roster");
  if (!el) return;
  const info = trace.resident_info || {};
  const ids = Object.keys(residentTracks()).sort();
  el.innerHTML = "";
  const current = currentResident();
  for (const rid of ids) {
    const r = info[rid] || {};
    const tr = document.createElement("tr");
    if (rid === current) tr.className = "sel";
    tr.title = r.personality || "";
    const who = document.createElement("td");
    who.className = "who";
    const name = r.name || rid;
    const age = (r.age === 0 || r.age) ? ` · ${r.age}` : "";
    who.innerHTML = `<div class="name">${escapeHtml(name)}` +
      `<span class="age">${escapeHtml(age)}</span></div>` +
      `<div class="rid">${escapeHtml(rid)}</div>`;
    const role = document.createElement("td");
    role.className = "role";
    role.textContent = r.occupation || "";
    tr.appendChild(who); tr.appendChild(role);
    tr.addEventListener("click", () => {
      const rsel = $("resident-select");
      if (rsel && residentTracks()[rid]) {
        rsel.value = rid;
        rsel.dispatchEvent(new Event("change"));
        renderRoster();
      }
    });
    el.appendChild(tr);
  }
}

function escapeHtml(v) {
  return String(v == null ? "" : v).replace(/[&<>"']/g, c => (
    {"&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;",
     "'": "&#39;"}[c]));
}

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
  const rinfo = trace.resident_info || {};
  for (const res of Object.keys(residentTracks()).sort()) {
    const opt = document.createElement("option");
    opt.value = res;
    const nm = (rinfo[res] || {}).name;
    opt.textContent = nm ? `${nm} (${res})` : res;
    rsel.appendChild(opt);
  }
  if (keepResident && residentTracks()[keepResident])
    rsel.value = keepResident;
  renderRoster();
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
      lastDatasets = datasets;
      populateTracePicker(datasets);      // rebuilds source + household + seed
      flash(`household list updated (${datasets.length} timelines)`);
    }
    knownDatasets = signature;

    const head = await fetch(TRACE_URL, {method: "HEAD"});
    const stamp = head.headers.get("Last-Modified");
    if (traceStamp && stamp && stamp !== traceStamp) {
      const fresh = await (await fetch(TRACE_URL)).json();
      const wasObject = currentObject(), wasResident = currentResident();
      trace = fresh;
      traceCache.set(TRACE_URL, fresh);   // keep the cache truthful
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

/* Seeds of one household are the SAME home with different jitter draws:
 * same scene, same objects, same residents, same length. Switching between
 * them should feel like flipping a page, not like opening a new dataset —
 * so sibling seeds are prefetched into memory and swapped IN PLACE, keeping
 * the clock position, the selected object and the selected resident. A full
 * page reload (what the household picker still does, correctly — a different
 * home is a different dataset) would throw all three away. */
const traceCache = new Map();          // url -> parsed trace.json
let siblingSeeds = [];                 // rows for the open household

async function fetchTrace(url) {
  if (traceCache.has(url)) return traceCache.get(url);
  const res = await fetch(url);
  if (!res.ok) throw new Error(`${res.status} for ${url}`);
  const parsed = await res.json();
  traceCache.set(url, parsed);
  return parsed;
}

function prefetchSiblings(rows) {
  // fire-and-forget: a failed prefetch just means the swap fetches later
  rows.filter(d => !samePath(d.trace, TRACE_URL))
      .forEach(d => { fetchTrace(d.trace).catch(() => {}); });
}

async function switchSeed(url) {
  if (samePath(url, TRACE_URL)) return;
  const keptTime = t, keptObject = currentObject();
  const keptResident = currentResident();
  const seedSel = $("seed-select");
  try {
    const fresh = await fetchTrace(url);
    trace = fresh;
    TRACE_URL = url;
    traceStamp = null;                 // re-baseline the rebuild watcher
    horizon = trace.days * 1440;
    $("time").max = horizon;
    rebuildPickers(keptObject, keptResident);
    computeView();
    drawEventStrip();
    setTime(Math.min(keptTime, horizon - 1));
    history.replaceState(null, "", `?trace=${encodeURIComponent(url)}`);
    $("run-label").textContent =
      `${trace.household} · scene ${trace.scene_id} · ${trace.days} days · ` +
      `seed ${trace.seed}`;
    document.title = `${trace.household} — object-trace viewer`;
    if (lastDatasets) linkToBeliefs(lastDatasets);
    flash(`seed ${trace.seed}`);
  } catch (e) {
    console.warn("seed switch failed", url, e);
    if (seedSel) seedSel.value = TRACE_URL;   // put the picker back
    flash("could not load that seed");
  }
}

let lastDatasets = null;               // for linkToBeliefs after a swap

function populateTracePicker(datasets) {
  // THREE pickers, source then household then seed: every set numbers its
  // households hh1..hh10, so a flat list offers three rows called hh_001
  // with nothing to tell them apart; and one household realized under
  // several seeds is ONE home with several histories, so its seeds belong
  // in their own menu rather than as extra household rows.
  const open = datasets.find(d => samePath(d.trace, TRACE_URL));
  const sourceOf = d => d.source || "other";
  // group key: the household directory when serve.py provides it, else
  // the trace url (older manifests, and any row without the field, then
  // behave exactly as before — one row per timeline)
  const homeOf = d => d.household || d.trace;
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
  const openSeed = open ? (open.seed ?? 0) : 0;
  srcSel.onchange = () => {
    // jump to the first household of the newly chosen set, keeping the
    // seed being looked at when that household has one
    const inSet = datasets.filter(d => sourceOf(d) === srcSel.value);
    const first = inSet.find(d => (d.seed ?? 0) === openSeed) || inSet[0];
    if (first) location.search = `?trace=${encodeURIComponent(first.trace)}`;
  };

  const mine = datasets.filter(d => sourceOf(d) === currentSource);

  // one entry per HOME, holding its seeds in order
  const homes = [];
  const byHome = new Map();
  mine.forEach(d => {
    const key = homeOf(d);
    if (!byHome.has(key)) {
      const entry = {key, seeds: []};
      byHome.set(key, entry);
      homes.push(entry);
    }
    byHome.get(key).seeds.push(d);
  });
  homes.forEach(h => h.seeds.sort(
      (a, b) => (a.seed ?? 0) - (b.seed ?? 0)));

  const openHome = open ? homeOf(open) : null;
  // The household row is labelled by its FIRST seed, with the seed suffix
  // dropped: the seed lives in its own menu now, so repeating it here
  // would say the same thing twice and misname the other seeds.
  const stripSeed = label => label.replace(/\s*seed\s*\d+\s*$/i, "").trim();
  const rows = homes.map(h => {
    const keep = h.seeds.find(d => (d.seed ?? 0) === openSeed) || h.seeds[0];
    return {label: stripSeed(h.seeds[0].label),
            search: `?trace=${encodeURIComponent(keep.trace)}`};
  });
  let current = homes.findIndex(h => h.key === openHome);
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

  // Seed picker: the seeds of the household currently open. Switching
  // household keeps the seed when that home has one of the same number,
  // so stepping through households at seed 2 stays at seed 2.
  const seedSel = $("seed-select");
  if (seedSel) {
    const here = homes.find(h => h.key === openHome);
    const seeds = here ? here.seeds : [];
    seedSel.innerHTML = "";
    seeds.forEach(d => {
      const opt = document.createElement("option");
      opt.value = d.trace;
      opt.textContent = `seed ${d.seed ?? "?"}`;
      opt.selected = samePath(d.trace, TRACE_URL);
      seedSel.appendChild(opt);
    });
    seedSel.disabled = seeds.length < 2;
    if (!seeds.length) {
      const opt = document.createElement("option");
      opt.textContent = "seed —";
      seedSel.appendChild(opt);
    }
    seedSel.onchange = () => { switchSeed(seedSel.value); };
    siblingSeeds = seeds;
    prefetchSiblings(seeds);
  }
}

function linkToBeliefs(datasets) {
  // Carry the household — and the object being looked at — across to the
  // belief page instead of making the user retype either. A household with
  // no belief_trace.json on disk links over plainly and that page opens on
  // its own first dataset (and says how to generate one).
  const d = datasets.find(x => samePath(x.trace, TRACE_URL));
  const link = $("beliefs-link");
  if (!d || !d.belief_trace) {
    link.title = "no belief trace for this household — generate one with " +
                 "python -m baselines.belief_trace";
    return;
  }
  // Resolved at click time, not at boot: the object picker moves while the
  // page is open, and a href frozen at load would carry the wrong object.
  const href = () => {
    const obj = $("object-select") ? $("object-select").value : "";
    return peerViewer("beliefs", "beliefs.html") +
           `?trace=${encodeURIComponent(d.trace)}` +
           `&belief=${encodeURIComponent(d.belief_trace)}` +
           (obj ? `&object=${encodeURIComponent(obj)}` : "");
  };
  link.href = href();
  link.addEventListener("mousedown", () => { link.href = href(); });
  link.title = "belief vs truth for this household";
}

/* Load TRACE_URL, falling back to the first live household when the URL's
 * ?trace= has gone stale — the household was rebuilt, renamed or archived
 * since the URL was minted, which is exactly the state a reload lands in
 * after regenerating a set. Dying here (the old behaviour) looked like the
 * whole viewer being broken and got everything restarted for nothing.
 * The address bar is rewritten to the household actually shown, so the
 * NEXT reload starts from a URL that works. */
async function loadTraceWithFallback(datasets) {
  const load = async url => {
    const res = await fetch(url);
    if (!res.ok) throw new Error(`${res.status} ${res.statusText} for ${url}`);
    return res.json();
  };
  try {
    return await load(TRACE_URL);
  } catch (err) {
    const fallback = datasets.find(d => !samePath(d.trace, TRACE_URL));
    if (!fallback) throw err;
    console.warn(`stale ?trace= (${err.message}) — showing ${fallback.trace}`);
    TRACE_URL = fallback.trace;
    history.replaceState(null, "", `?trace=${encodeURIComponent(TRACE_URL)}`);
    return load(TRACE_URL);
  }
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
  say(`loading ${TRACE_URL}…`);
  trace = await loadTraceWithFallback(datasets);
  horizon = trace.days * 1440;

  // After the fallback above TRACE_URL is final, so the pickers and the
  // cross-link mark the household actually being shown.
  lastDatasets = datasets;
  populateTracePicker(datasets);
  linkToBeliefs(datasets);

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
  rsel.addEventListener("change", () => {
    renderRoster(); drawEventStrip(); draw(); });
  $("jump-what").addEventListener("change", draw);
  for (const id of ["show-path", "show-res-path", "show-trace", "show-others",
                    "show-recs", "show-all-res", "show-why"])
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
