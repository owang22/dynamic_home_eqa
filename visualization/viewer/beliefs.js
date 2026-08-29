/* belief-vs-truth viewer — what each belief model thinks, at any moment,
 * against where the object actually is.
 *
 * Data source: `belief_trace.json` beside the household's trace.json,
 * written by `python -m baselines.belief_trace`. It holds, per belief
 * model and per object, run-length-encoded segments of the model's argmax
 * under the PASSIVE observation diet (initial tour + the bank's scripted
 * sightings, no sensing), plus the bank's own truth segments. Both are
 * piecewise-constant in minutes, so any slider position resolves to an
 * exact (belief, truth) pair — the comparison is available at every
 * moment, not only at the instants the bank asked a question.
 *
 * Correctness here means exactly what it means in the harness: identical
 * receptacle ids, exact match, including the pseudo-receptacles
 * OUT_OF_HOUSE and ON_PERSON. Those two have no anchor of their own on
 * the map and are drawn at the AWAY circle / the resident's position.
 *
 * Three tabs: the focus object on the map, a table of every object right
 * now, and the same instant scored across all models at once.
 *
 * URL params (optional): ?trace=<trace.json>&belief=<belief_trace.json>
 * &model=<model name>&object=<object id>
 */
"use strict";

const DAY_NAMES = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"];
const SEG = {T0: 0, T1: 1, REC: 2, ROOM: 3, REL: 4, X: 5, Z: 6};
const GOOD = "#7ee08a", BAD = "#ff8a8a", TRUTH = "#ffb84d";
// one hue per belief model, panel first — same order as the reports
const MODEL_HUES = ["#4d9de0", "#eb6834", "#1baf7a", "#8a5cd6", "#c2312e",
                    "#d8a015", "#9aa0a6"];

const $ = id => document.getElementById(id);
const params = new URLSearchParams(location.search);
let TRACE_URL = params.get("trace");
let BELIEF_URL = params.get("belief");

let trace = null, belief = null, mapImg = null;
let t = 0, horizon = 1, playing = false, lastFrame = 0, view = null;
let tab = "map";
let accuracySeries = null;      // per-model share-correct over the grid

function fmtTime(min) {
  const d = Math.floor(min / 1440), m = Math.floor(min % 1440);
  return `d${String(d).padStart(2, "0")} ${DAY_NAMES[d % 7]} ` +
         `${String(Math.floor(m / 60)).padStart(2, "0")}:` +
         `${String(m % 60).padStart(2, "0")}`;
}

function fmtAge(min) {
  if (min == null) return "never seen";
  if (min < 60) return `${Math.round(min)} min ago`;
  if (min < 1440) return `${(min / 60).toFixed(1)} h ago`;
  return `${(min / 1440).toFixed(1)} days ago`;
}

// ------------------------------------------------------------ data access

/* Segments are [t0, t1, value, ...] sorted and gapless, so a linear scan
 * from the end is enough; the arrays are short (a stable belief is one
 * segment) and this runs per object per frame. */
function segAt(segments, min) {
  for (let i = segments.length - 1; i >= 0; i--)
    if (min >= segments[i][0]) return segments[i];
  return segments[0];
}

const currentModel = () =>
  belief.models.find(m => m.name === $("model-select").value) ||
  belief.models[0];

function beliefAt(model, object, min) { return segAt(model.objects[object], min); }
function truthAt(object, min) { return segAt(belief.truth[object], min); }

/* The last time this object was actually SEEN, and where. Belief segment
 * boundaries are not sightings (a belief also shifts as counts decay and
 * time-of-day bins roll over), so this reads the trace's own evidence
 * stream. Returns null before the object's first sighting. */
function lastSighting(object, min) {
  const seen = (belief.sightings || {})[object] || [];
  let last = null;
  for (const s of seen) { if (s[0] <= min) last = s; else break; }
  return last;
}

function houseScore(model, min) {
  let right = 0;
  for (const o of belief.objects)
    if (beliefAt(model, o, min)[2] === truthAt(o, min)[2]) right++;
  return {right, total: belief.objects.length};
}

// ------------------------------------------------------------- geometry

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

function residentPosAt(min) {
  const residents = Object.values(trace.residents || {});
  if (!residents.length) return trace.elsewhere.pos;
  const segs = residents[0];
  const s = segs.find(s => min >= s[0] && min < s[1]) || segs[segs.length - 1];
  return [s[4], s[5]];
}

/* Pseudo-receptacles have no anchor of their own: OUT_OF_HOUSE draws at
 * the AWAY circle, ON_PERSON at the resident the viewer tracks. */
function anchorOf(receptacle, min) {
  if (receptacle === "OUT_OF_HOUSE") return trace.elsewhere.pos;
  if (receptacle === "ON_PERSON") return residentPosAt(min);
  const r = trace.receptacles[receptacle];
  return r ? r.pos : trace.elsewhere.pos;
}

// ---------------------------------------------------------------- drawing

function drawRooms(ctx) {
  const dpr = window.devicePixelRatio || 1;
  trace.rooms.forEach(room => {
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

/* Small marker per object: gold dot at truth, hollow ring at the belief,
 * joined when they disagree. Deliberately unlabeled — with 30-50 objects
 * labels overlap into mush; the table tab is where names are read. */
function drawAllObjects(ctx, model) {
  const dpr = window.devicePixelRatio || 1;
  const focus = $("object-select").value;
  const onlyWrong = $("only-wrong").checked;
  for (const o of belief.objects) {
    if (o === focus) continue;
    const truth = truthAt(o, t)[2], guess = beliefAt(model, o, t)[2];
    const ok = truth === guess;
    if (onlyWrong && ok) continue;
    const [tx, ty] = worldToCanvas(...anchorOf(truth, t));
    const [bx, by] = worldToCanvas(...anchorOf(guess, t));
    ctx.globalAlpha = 0.55;
    if (!ok) {
      ctx.setLineDash([3, 3]);
      ctx.strokeStyle = BAD;
      ctx.lineWidth = 1 * dpr;
      ctx.beginPath(); ctx.moveTo(bx, by); ctx.lineTo(tx, ty); ctx.stroke();
      ctx.setLineDash([]);
    }
    ctx.fillStyle = TRUTH;
    ctx.beginPath(); ctx.arc(tx, ty, 2.5 * dpr, 0, Math.PI * 2); ctx.fill();
    ctx.strokeStyle = ok ? GOOD : BAD;
    ctx.lineWidth = 1.5 * dpr;
    ctx.beginPath(); ctx.arc(bx, by, 5 * dpr, 0, Math.PI * 2); ctx.stroke();
    ctx.globalAlpha = 1;
  }
}

function draw() {
  const canvas = $("map"), ctx = canvas.getContext("2d");
  const dpr = window.devicePixelRatio || 1;
  ctx.fillStyle = "#14161a";
  ctx.fillRect(0, 0, canvas.width, canvas.height);
  if (mapImg) {
    ctx.globalAlpha = 0.5;
    ctx.drawImage(mapImg, view.px0, view.py0, view.pw, view.ph,
                  view.ox, view.oy, view.pw * view.scale, view.ph * view.scale);
    ctx.globalAlpha = 1;
  }
  drawRooms(ctx);
  drawReceptacles(ctx);

  const model = currentModel();
  if ($("show-all").checked) drawAllObjects(ctx, model);

  const obj = $("object-select").value;
  const truthRec = truthAt(obj, t)[2];
  const guess = beliefAt(model, obj, t);
  const ok = truthRec === guess[2];
  const [tx, ty] = worldToCanvas(...anchorOf(truthRec, t));
  const [bx, by] = worldToCanvas(...anchorOf(guess[2], t));

  // Where the object was last actually SEEN — the evidence every model in
  // this file is working from. Drawn faintly and behind the two live
  // markers: when it coincides with the belief the model is simply
  // trusting its last look, and when it coincides with neither, the
  // object has moved twice since anyone saw it.
  const seen = lastSighting(obj, t);
  if (seen) {
    const [sx, sy] = worldToCanvas(...anchorOf(seen[1], seen[0]));
    ctx.globalAlpha = 0.75;
    ctx.strokeStyle = TRUTH;
    ctx.lineWidth = 1.2 * dpr;
    ctx.setLineDash([2, 2]);
    const r = 13 * dpr;
    ctx.strokeRect(sx - r, sy - r, 2 * r, 2 * r);
    ctx.setLineDash([]);
    ctx.fillStyle = TRUTH;
    ctx.font = `${9 * dpr}px system-ui`;
    ctx.textAlign = "center";
    ctx.fillText(`last seen ${fmtAge(t - seen[0])}`, sx, sy + r + 10 * dpr);
    ctx.globalAlpha = 1;
  }

  if (!ok) {
    ctx.setLineDash([6, 5]);
    ctx.strokeStyle = BAD;
    ctx.lineWidth = 1.5 * dpr;
    ctx.beginPath(); ctx.moveTo(bx, by); ctx.lineTo(tx, ty); ctx.stroke();
    ctx.setLineDash([]);
  }
  ctx.strokeStyle = ok ? GOOD : BAD;
  ctx.lineWidth = 3 * dpr;
  ctx.beginPath(); ctx.arc(bx, by, 10 * dpr, 0, Math.PI * 2); ctx.stroke();
  ctx.fillStyle = ok ? GOOD : BAD;
  ctx.font = `600 ${10 * dpr}px system-ui`;
  ctx.textAlign = "center";
  ctx.fillText(`believes: ${guess[2]}`, bx, by - 14 * dpr);

  ctx.fillStyle = TRUTH;
  ctx.strokeStyle = "#14161a";
  ctx.lineWidth = 1.5 * dpr;
  ctx.beginPath(); ctx.arc(tx, ty, 7 * dpr, 0, Math.PI * 2);
  ctx.fill(); ctx.stroke();
  ctx.fillStyle = "#ffe1b3";
  ctx.font = `600 ${10 * dpr}px system-ui`;
  ctx.fillText(obj, tx, ty + 20 * dpr);

  updateReadout(model, obj, truthRec, guess, ok);
  captionStrip(model);
  if (tab !== "map") renderSheet(model);
}

function updateReadout(model, obj, truthRec, guess, ok) {
  $("clock").textContent = fmtTime(t);
  $("whereabouts").textContent =
    `${obj} — truth ${truthRec} · ${model.display} says ${guess[2]}`;
  $("st-truth").textContent = truthRec;
  $("st-belief").textContent = guess[2];
  $("st-verdict").innerHTML = ok
    ? `<span style="color:${GOOD}">correct</span>`
    : `<span style="color:${BAD}">wrong</span>`;
  $("st-conf").textContent = guess[3] == null ? "–" : guess[3].toFixed(2);
  // The evidence behind the belief: a model is rarely "wrong" so much as
  // working from a sighting that has gone stale, and the staleness is the
  // number that explains the verdict above.
  const seen = lastSighting(obj, t);
  const moved = seen && seen[1] !== truthRec;
  $("st-seen").innerHTML = !seen
    ? `<span class="muted">never seen yet</span>`
    : `${seen[1]} · ${fmtAge(t - seen[0])}` +
      (moved ? `<br><span class="muted">it has moved since</span>`
             : `<br><span class="muted">still there</span>`);
  const {right, total} = houseScore(model, t);
  $("st-house").innerHTML =
    `${right}/${total} <span class="muted">(${(right / total * 100).toFixed(0)}%)</span>`;
}

// ------------------------------------------------------------- the sheet

function renderSheet(model) {
  const head = $("sheet-head"), body = $("sheet-body");
  if (tab === "patrols") { renderPatrols(head, body); return; }
  if (tab === "sweep") { renderBudgetSweep(head, body); return; }
  if (tab === "table") {
    const onlyWrong = $("only-wrong").checked;
    const rows = belief.objects.map(o => {
      const truth = truthAt(o, t)[2], g = beliefAt(model, o, t);
      return {o, truth, guess: g[2], conf: g[3], ok: truth === g[2]};
    }).filter(r => !onlyWrong || !r.ok)
      // wrong first: the interesting rows should never need scrolling to
      .sort((a, b) => (a.ok - b.ok) || a.o.localeCompare(b.o));
    const {right, total} = houseScore(model, t);
    head.innerHTML =
      `<strong>${model.display}</strong> at ${fmtTime(t)} — ` +
      `<span style="color:${GOOD}">${right}</span>/${total} objects right` +
      (onlyWrong ? ` · showing the ${total - right} wrong` : "");
    body.innerHTML =
      `<table class="sheet"><tr><th>object</th><th>truth now</th>` +
      `<th>belief now</th><th>conf</th></tr>` +
      rows.map(r =>
        `<tr class="${r.ok ? "ok" : "bad"}"><td>${r.o}</td>` +
        `<td>${r.truth}</td><td>${r.guess}</td>` +
        `<td>${r.conf == null ? "–" : r.conf.toFixed(2)}</td></tr>`).join("") +
      `</table>`;
    return;
  }
  // models tab: the same instant scored across every model in the trace
  const scored = belief.models.map(m => ({m, ...houseScore(m, t)}))
                              .sort((a, b) => b.right - a.right);
  head.innerHTML = `every model at ${fmtTime(t)} — objects located correctly`;
  body.innerHTML =
    `<table class="sheet"><tr><th>model</th><th>panel</th><th>right</th>` +
    `<th>share</th><th>focus object</th></tr>` +
    scored.map(({m, right, total}) => {
      const obj = $("object-select").value;
      const g = beliefAt(m, obj, t)[2], truth = truthAt(obj, t)[2];
      const ok = g === truth;
      return `<tr><td>${m.display}</td>` +
             `<td class="muted small">${m.panel}</td>` +
             `<td>${right}/${total}</td>` +
             `<td>${(right / total * 100).toFixed(0)}%</td>` +
             `<td class="${ok ? "ok" : "bad"}">${g}</td></tr>`;
    }).join("") + `</table>`;
}

// ------------------------------------------------- patrol & sweep charts

function modelHue(name) {
  const order = belief.models.map(m => m.name);
  const i = order.indexOf(name);
  return MODEL_HUES[(i >= 0 ? i : order.length) % MODEL_HUES.length];
}

/* Minimal inline SVG line chart. xs/series values are plotted in a fixed
 * viewBox and the element scales to the sheet's width; no libraries.
 * refLine ({value, label}) draws one dashed gray horizontal reference —
 * used for the routine oracle, which must not look like a model curve. */
function lineChartSVG(xs, seriesByName, yMin, yMax, xLabel, refLine) {
  const W = 860, H = 190, L = 44, R = 12, T = 10, B = 30;
  const px = i => L + (W - L - R) * (xs.length < 2 ? 0 : i / (xs.length - 1));
  const py = v => T + (H - T - B) * (1 - (v - yMin) / (yMax - yMin));
  let grid = "";
  for (let v = Math.ceil(yMin * 10) / 10; v <= yMax + 1e-9; v += 0.1) {
    const y = py(v);
    grid += `<line x1="${L}" y1="${y}" x2="${W - R}" y2="${y}"
             stroke="#2c313a" stroke-width="1"/>` +
            `<text x="${L - 6}" y="${y + 3}" text-anchor="end"
             font-size="10" fill="#8b93a1">${v.toFixed(1)}</text>`;
  }
  let ticks = "";
  xs.forEach((x, i) => {
    ticks += `<text x="${px(i)}" y="${H - 10}" text-anchor="middle"
              font-size="10" fill="#8b93a1">${x}</text>`;
  });
  let paths = "";
  for (const [name, values] of Object.entries(seriesByName)) {
    const d = values.map((v, i) =>
      `${i ? "L" : "M"}${px(i).toFixed(1)},${py(v).toFixed(1)}`).join(" ");
    paths += `<path d="${d}" fill="none" stroke="${modelHue(name)}"
              stroke-width="2"/>`;
    values.forEach((v, i) => {
      paths += `<circle cx="${px(i)}" cy="${py(v)}" r="2.6"
                fill="${modelHue(name)}"/>`;
    });
  }
  let ref = "";
  if (refLine && refLine.value >= yMin && refLine.value <= yMax) {
    const y = py(refLine.value);
    ref = `<line x1="${L}" y1="${y}" x2="${W - R}" y2="${y}"
           stroke="#8b93a1" stroke-width="1.5" stroke-dasharray="7 5"/>` +
          `<text x="${W - R - 4}" y="${y - 4}" text-anchor="end"
           font-size="10" fill="#8b93a1">${refLine.label}</text>`;
  }
  return `<svg class="chart" viewBox="0 0 ${W} ${H}"
          role="img">${grid}${ticks}${paths}${ref}
          <text x="${(L + W - R) / 2}" y="${H - 0.5}" text-anchor="middle"
          font-size="10" fill="#8b93a1">${xLabel}</text></svg>`;
}

function legendHTML(names) {
  return `<div class="chart-legend">` + names.map(n =>
    `<span><span class="swatch" style="background:${modelHue(n)}"></span>` +
    `${n}</span>`).join("") + `</div>`;
}

/* One row per patrol schedule: the accuracy-over-time chart for the panel
 * models, with the schedule's visit count and mean accuracy in the
 * heading. The section exists in the trace only when it was generated
 * with --timeline/--spec. */
function renderPatrols(head, body) {
  const section = belief.patrols;
  if (!section) {
    head.textContent = "patrol comparison";
    body.innerHTML = `<p class="muted">This trace has no patrol section. ` +
      `Regenerate it with:<br><code>python -m baselines.belief_trace ` +
      `--candidates --bank &lt;bank&gt; --timeline &lt;timeline_dir&gt; ` +
      `--spec &lt;program.yaml&gt; --out &lt;belief_trace.json&gt;</code></p>`;
    return;
  }
  head.innerHTML =
    `<strong>ambient observation schedules</strong> — the three ` +
    `budget-taking schedules run at ${section.visits_per_day} visits/day, ` +
    `but morning_evening_sweep and stationed_observer set their own visit ` +
    `counts by construction, so schedules differ in OBSERVATION VOLUME as ` +
    `well as route; read accuracy against each schedule's realized ` +
    `visits/day, not its name alone. Curves are the share of all ` +
    `${belief.objects.length} objects each model localizes correctly, ` +
    `over the ${belief.days} days`;
  let html = legendHTML(section.models);
  html += accuracyVsVolumeSVG(section);
  const G = section.accuracy_grid_minutes;
  for (const [name, sch] of Object.entries(section.schedules)) {
    const means = section.models.map(m => {
      const s = sch.accuracy[m];
      return `${m.split("_")[0]} ${(s.reduce((a, b) => a + b, 0)
              / s.length).toFixed(3)}`;
    }).join(" · ");
    const st = sch.stats || {};
    const realized = st.visits_per_day == null ? "" :
      `realized ${st.visits_per_day} visits/day · ` +
      `${st.sightings_per_day} sightings/day · `;
    // x labels at three-day marks; series plotted at full resolution
    const stride = Math.round(1440 * 3 / G);
    const xs = sch.accuracy[section.models[0]].map((_, i) =>
      (i % stride === 0) ? "d" + Math.round(i * G / 1440) : "");
    html += `<div class="chart-block"><h3>${name}</h3>` +
      `<div class="sub">${realized}${sch.visits.length} visits over the ` +
      `episode · mean accuracy: ${means}</div>` +
      lineChartSVG(xs, Object.fromEntries(
        section.models.map(m => [m, sch.accuracy[m]])), 0, 1, "time") +
      `</div>`;
  }
  body.innerHTML = html;
}

/* Mean accuracy against realized visits/day, one point per
 * (schedule, model): the volume-fairness view of the patrol comparison.
 * Two schedules generate their own visit counts, so same-colored points
 * at different x ARE the same model under different observation volume —
 * vertical spread at one x is what the route itself contributes. */
function accuracyVsVolumeSVG(section) {
  const entries = Object.entries(section.schedules)
    .filter(([, s]) => s.stats && s.stats.visits_per_day != null);
  if (!entries.length) return "";
  const W = 860, H = 230, L = 44, R = 12, T = 26, B = 34;
  const xsAll = entries.map(([, s]) => s.stats.visits_per_day);
  const xMin = Math.min(...xsAll) - 1, xMax = Math.max(...xsAll) + 1;
  const px = x => L + (W - L - R) * (x - xMin) / (xMax - xMin);
  const py = v => T + (H - T - B) * (1 - v);
  let grid = "";
  for (let v = 0; v <= 1.001; v += 0.2) {
    const y = py(v);
    grid += `<line x1="${L}" y1="${y}" x2="${W - R}" y2="${y}"
             stroke="#2c313a" stroke-width="1"/>` +
            `<text x="${L - 6}" y="${y + 3}" text-anchor="end"
             font-size="10" fill="#8b93a1">${v.toFixed(1)}</text>`;
  }
  let marks = "";
  for (const [name, sch] of entries) {
    const x = px(sch.stats.visits_per_day);
    marks += `<line x1="${x}" y1="${T}" x2="${x}" y2="${H - B}"
              stroke="#2c313a" stroke-width="1" stroke-dasharray="2 4"/>` +
             `<text x="${x}" y="${T - 6}" text-anchor="middle"
              font-size="9" fill="#8b93a1">${name.split("_")[0]}</text>` +
             `<text x="${x}" y="${H - B + 12}" text-anchor="middle"
              font-size="10" fill="#8b93a1">${sch.stats.visits_per_day}</text>`;
    for (const m of section.models) {
      const s = sch.accuracy[m];
      const mean = s.reduce((a, b) => a + b, 0) / s.length;
      marks += `<circle cx="${x}" cy="${py(mean)}" r="4"
                fill="${modelHue(m)}"><title>${name} · ${m}: ` +
               `${mean.toFixed(3)}</title></circle>`;
    }
  }
  return `<div class="chart-block"><h3>mean accuracy vs realized ` +
    `observation volume</h3>` +
    `<svg class="chart" viewBox="0 0 ${W} ${H}" role="img">${grid}${marks}
     <text x="${(L + W - R) / 2}" y="${H - 2}" text-anchor="middle"
     font-size="10" fill="#8b93a1">realized visits per day</text></svg></div>`;
}

/* Accuracy on the bank's questions vs the observation budget, every
 * registered model — the floor / separation / saturation picture. */
function renderBudgetSweep(head, body) {
  const sweep = belief.budget_sweep;
  if (!sweep) {
    head.textContent = "observation-budget sweep";
    body.innerHTML = `<p class="muted">This trace has no budget-sweep ` +
      `section. Regenerate it with --timeline/--spec (see the patrol ` +
      `tab's note).</p>`;
    return;
  }
  const names = Object.keys(sweep.accuracy);
  head.innerHTML =
    `<strong>observation budget vs accuracy</strong> — each point: one ` +
    `${sweep.patrol.replace(/_/g, " ")} stream at that many room visits ` +
    `per day; y = accuracy on the bank's ${sweep.n_questions} questions, ` +
    `answered passively (no paid senses)`;
  let lo = 1, hi = 0;
  for (const vs of Object.values(sweep.accuracy)) {
    lo = Math.min(lo, ...vs); hi = Math.max(hi, ...vs);
  }
  const oracle = sweep.oracle;
  if (oracle) { lo = Math.min(lo, oracle.accuracy); hi = Math.max(hi, oracle.accuracy); }
  let html = legendHTML(names);
  html += lineChartSVG(sweep.visit_budgets, sweep.accuracy,
                       Math.max(0, lo - 0.05), Math.min(1, hi + 0.05),
                       "room visits per day",
                       oracle && {value: oracle.accuracy,
                                  label: `routine oracle ${oracle.accuracy.toFixed(3)} (no observations)`});
  html += `<table class="sheet" style="margin-top:12px"><tr><th>model</th>` +
    sweep.visit_budgets.map(b => `<th>${b}/day</th>`).join("") + `</tr>` +
    names.map(n => `<tr><td>` +
      `<span class="swatch" style="background:${modelHue(n)};display:inline-block;width:10px;height:10px;border-radius:2px;margin-right:6px"></span>` +
      `${n}</td>` +
      sweep.accuracy[n].map(v => `<td>${v.toFixed(3)}</td>`).join("") +
      `</tr>`).join("");
  if (oracle) {
    html +=
      `<tr><td class="muted">routine oracle (${oracle.n_seeds} MC seeds)</td>` +
      sweep.visit_budgets.map(() =>
        `<td class="muted">${oracle.accuracy.toFixed(3)}</td>`).join("") +
      `</tr>` +
      `<tr><td class="muted">headroom (oracle − best model)</td>` +
      oracle.headroom_per_budget.map(v =>
        `<td class="muted">${v >= 0 ? "+" : ""}${v.toFixed(3)}</td>`)
        .join("") + `</tr>`;
  }
  html += `</table>`;
  if (oracle) {
    html += `<p class="muted small">The routine oracle is a diagnostic, ` +
      `not a competitor: the modal receptacle over ${oracle.n_seeds} ` +
      `re-realizations of the household's own program (seeds ` +
      `${oracle.seed_range[0]}–${oracle.seed_range[1]}) — perfect routine ` +
      `knowledge, zero observations, so it is flat across budgets and is ` +
      `NOT a hard ceiling. Positive headroom is residual error ` +
      `explainable by routine knowledge alone; negative headroom means ` +
      `observation-fed models beat routine knowledge there (recency is ` +
      `carrying the load). Stability: the two disjoint halves of the seed ` +
      `set score ${oracle.accuracy_halves[0].toFixed(3)} and ` +
      `${oracle.accuracy_halves[1].toFixed(3)} ` +
      `(delta ${oracle.half_split_delta.toFixed(3)}).</p>`;
  }
  html += recencyTableHTML(sweep, names);
  body.innerHTML = html;
  const select = body.querySelector("#recency-budget");
  if (select) select.addEventListener("change", () => {
    sweepRecencyBudget = Number(select.value);
    renderBudgetSweep(head, body);
  });
}

let sweepRecencyBudget = null;   // sticky across re-renders of the sheet

/* Accuracy by time-since-last-sighting at one budget level, with the
 * question count beside every accuracy — bins with tiny counts are the
 * usual way this kind of table lies, so n never leaves the number. */
function recencyTableHTML(sweep, names) {
  if (!sweep.recency) return "";
  const budgets = sweep.visit_budgets;
  if (sweepRecencyBudget == null || !budgets.includes(sweepRecencyBudget)) {
    sweepRecencyBudget = budgets.includes(6) ? 6 : budgets[0];
  }
  const bi = budgets.indexOf(sweepRecencyBudget);
  const bins = sweep.recency_bins.filter(label =>
    names.some(n => sweep.recency[n][bi][label]));
  let html = `<h3 style="margin-top:16px">accuracy by time since last ` +
    `sighting · <select id="recency-budget">` +
    budgets.map(b => `<option value="${b}"` +
      (b === sweepRecencyBudget ? " selected" : "") +
      `>${b} visits/day</option>`).join("") + `</select></h3>` +
    `<table class="sheet"><tr><th>model</th>` +
    bins.map(label => `<th>${label}</th>`).join("") + `</tr>`;
  for (const n of names) {
    html += `<tr><td>` +
      `<span class="swatch" style="background:${modelHue(n)};display:inline-block;width:10px;height:10px;border-radius:2px;margin-right:6px"></span>` +
      `${n}</td>` +
      bins.map(label => {
        const cell = sweep.recency[n][bi][label];
        return cell == null ? `<td class="muted">–</td>`
          : `<td>${cell.accuracy.toFixed(3)} ` +
            `<span class="muted small">(n=${cell.n})</span></td>`;
      }).join("") + `</tr>`;
  }
  return html + `</table>`;
}

// ---------------------------------------------------------------- strip

/* Share of objects the model has right, sampled on the belief grid. This
 * is the belief's health over the episode: dips are moments the house got
 * ahead of what the model had been told. Computed once per model. */
function accuracyFor(model) {
  if (!accuracySeries[model.name]) {
    const step = belief.grid_minutes, out = [];
    for (let min = 0; min <= horizon; min += step) {
      const {right, total} = houseScore(model, min);
      out.push(right / total);
    }
    accuracySeries[model.name] = out;
  }
  return accuracySeries[model.name];
}

function drawEventStrip() {
  const strip = $("event-strip");
  const dpr = window.devicePixelRatio || 1;
  strip.width = strip.clientWidth * dpr;
  strip.height = 14 * dpr;
  const ctx = strip.getContext("2d");
  ctx.fillStyle = "#191c22";
  ctx.fillRect(0, 0, strip.width, strip.height);
  for (let d = 0; d <= trace.days; d++) {
    const x = (d * 1440 / horizon) * strip.width;
    ctx.fillStyle = d % 7 >= 5 ? "#5a5340" : "#2c313a";
    ctx.fillRect(x, 0, 1.5, strip.height);
  }
  const model = currentModel();
  const series = accuracyFor(model);
  ctx.strokeStyle = GOOD;
  ctx.lineWidth = 1.2 * dpr;
  ctx.beginPath();
  series.forEach((v, i) => {
    const x = (i * belief.grid_minutes / horizon) * strip.width;
    const y = strip.height - v * strip.height;
    i ? ctx.lineTo(x, y) : ctx.moveTo(x, y);
  });
  ctx.stroke();

  // Gold ticks: when the focus object was actually seen. Read together
  // with the line, this is the whole passive story — accuracy for this
  // object can only be earned just after a tick, and decays between them.
  const obj = $("object-select").value;
  ctx.fillStyle = TRUTH;
  for (const [minute] of (belief.sightings || {})[obj] || []) {
    const x = (minute / horizon) * strip.width;
    ctx.fillRect(x, strip.height - 4 * dpr, 1.5 * dpr, 4 * dpr);
  }
}

/* The strip is two unrelated series in one lane, so it says what it is
 * rather than relying on the legend in the side panel. */
function captionStrip(model) {
  const nowShare = houseScore(model, t);
  const sightings = ((belief.sightings || {})[$("object-select").value] || []).length;
  $("strip-caption").innerHTML =
    `<span style="color:${GOOD}">▬</span> share of all ${belief.objects.length} ` +
    `objects ${model.display} has right (0–100%), over the ${belief.days} days ` +
    `— now ${(nowShare.right / nowShare.total * 100).toFixed(0)}% &nbsp;·&nbsp; ` +
    `<span style="color:${TRUTH}">▮</span> the ${sightings} times ` +
    `${$("object-select").value} was actually seen`;
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

/* ←/→ jump to the focus object's next belief OR truth change — the moments
 * where the comparison actually changes are what one wants to step through. */
function jumpChange(dir) {
  const obj = $("object-select").value;
  const times = [...currentModel().objects[obj].map(s => s[0]),
                 ...belief.truth[obj].map(s => s[0])]
    .sort((a, b) => a - b);
  const next = dir > 0 ? times.find(x => x > t + 1)
                       : [...times].reverse().find(x => x < t - 1);
  if (next !== undefined) setTime(next);
}

/* The two table views are overlays; "map" is the closed state. Clicking
 * an already-open table tab closes it again (a toggle), and Esc / the
 * sheet's ✕ button do the same — three ways out, because an overlay a
 * viewer cannot dismiss reads as the page being stuck. */
function setTab(name) {
  tab = (name === tab && name !== "map") ? "map" : name;
  document.querySelectorAll(".tab").forEach(
    b => b.classList.toggle("active", b.dataset.tab === tab));
  $("sheet").classList.toggle("open", tab !== "map");
  draw();
}

// -------------------------------------------------------------------- boot

/* One row per household that has a belief trace on disk. serve.py adds
 * `belief_trace` to a manifest row whenever belief_trace.json sits beside
 * that household's trace.json, so publishing is running the generator. */
function beliefRows(datasets) {
  return datasets.filter(d => d.belief_trace).map(d => ({
    label: d.label,
    trace: d.trace,
    belief: d.belief_trace,
    search: `?trace=${encodeURIComponent(d.trace)}` +
            `&belief=${encodeURIComponent(d.belief_trace)}`,
  }));
}

function populateDatasetPicker(rows) {
  let current = rows.findIndex(r => samePath(r.trace, TRACE_URL));
  if (current < 0) {
    rows.unshift({
      label: `${new URL(TRACE_URL, location.href).pathname} (not in traces.json)`,
      trace: TRACE_URL, belief: BELIEF_URL,
      search: `?trace=${encodeURIComponent(TRACE_URL)}` +
              `&belief=${encodeURIComponent(BELIEF_URL)}`,
    });
    current = 0;
  }
  wirePicker($("dataset-select"), rows, current);
  $("traces-link").href = peerViewer("traces", "index.html") +
                          `?trace=${encodeURIComponent(TRACE_URL)}`;
}

function fillSelect(sel, values, labels, preset) {
  values.forEach((v, i) => {
    const opt = document.createElement("option");
    opt.value = v;
    opt.textContent = labels ? labels[i] : v;
    sel.appendChild(opt);
  });
  if (preset && values.includes(preset)) sel.value = preset;
}

async function boot() {
  const rows = beliefRows(await loadDatasets());
  if (!TRACE_URL || !BELIEF_URL) {
    if (!rows.length)
      throw new Error(
        "no household has a belief trace yet.\n\n" +
        "Generate one:\n  python -m baselines.belief_trace \\\n" +
        "      --bank banks/baselines/fleet/<household>_bank.jsonl \\\n" +
        "      --out <that household>/timeline_seed0/belief_trace.json");
    TRACE_URL = rows[0].trace;
    BELIEF_URL = rows[0].belief;
  }

  const load = async url => {
    const res = await fetch(url);
    if (!res.ok) throw new Error(`${res.status} ${res.statusText} for ${url}`);
    return res.json();
  };
  try {
    [trace, belief] = await Promise.all([load(TRACE_URL), load(BELIEF_URL)]);
  } catch (err) {
    // The URL's ?trace=/?belief= have gone stale — the household (or its
    // belief trace) was rebuilt or renamed since the URL was minted, which
    // is exactly the state a reload lands in after regenerating. Fall back
    // to the first live household and rewrite the address bar to it, so
    // the next reload starts from a URL that works, instead of dying and
    // looking like the whole viewer needs restarting.
    const fallback = rows.find(r => !samePath(r.trace, TRACE_URL));
    if (!fallback) throw err;
    console.warn(`stale trace/belief URL (${err.message}) — showing ${fallback.trace}`);
    TRACE_URL = fallback.trace;
    BELIEF_URL = fallback.belief;
    history.replaceState(null, "", fallback.search);
    [trace, belief] = await Promise.all([load(TRACE_URL), load(BELIEF_URL)]);
  }
  populateDatasetPicker(rows);
  horizon = trace.days * 1440;
  accuracySeries = {};
  $("time").max = horizon;

  // Repo-absolute, NOT relative to the page: this viewer is reachable both
  // at /visualization/viewer/beliefs.html and at the short / URL on its own
  // port, and a relative `../assets/` resolves against location.href — from
  // the short URL that is /assets/…, which 404s and surfaces as the
  // baffling "source image cannot be decoded".
  const mapUrl = `/visualization/assets/${trace.scene_id}/map.png`;
  mapImg = new Image();
  mapImg.src = mapUrl;
  try {
    await mapImg.decode();
  } catch (e) {
    // the belief comparison is readable without the floor plan behind it
    console.warn("map failed to decode", mapUrl, e);
    mapImg = null;
  }

  fillSelect($("model-select"), belief.models.map(m => m.name),
             belief.models.map(m => `${m.display}${m.panel === "candidate" ? " ·cand" : ""}`),
             params.get("model"));
  fillSelect($("object-select"), belief.objects, null, params.get("object"));
  $("model-select").addEventListener("change", () => { drawEventStrip(); draw(); });
  $("object-select").addEventListener("change", () => { drawEventStrip(); draw(); });
  for (const id of ["show-all", "only-wrong"])
    $(id).addEventListener("change", draw);
  document.querySelectorAll(".tab").forEach(
    b => b.addEventListener("click", () => setTab(b.dataset.tab)));

  $("run-label").textContent =
    `${belief.household} · ${belief.objects.length} objects · ` +
    `${belief.models.length} models · ${belief.days}d`;
  $("src-note").innerHTML =
    `passive diet (tour + scripted sightings, no sensing)<br>` +
    `sampled every ${belief.grid_minutes} min · seed ${belief.seed}<br>` +
    `bank <span class="muted">${belief.bank_manifest_hash.slice(0, 12)}…</span>`;

  $("time").addEventListener("input", e => setTime(Number(e.target.value), true));
  $("play").addEventListener("click", () => togglePlay());
  window.addEventListener("resize", () => { computeView(); drawEventStrip(); draw(); });
  $("sheet-close").addEventListener("click", () => setTab("map"));
  document.addEventListener("keydown", e => {
    if (e.target.tagName === "SELECT") return;
    if (e.key === "Escape" && tab !== "map") { setTab("map"); return; }
    if (e.key === " ") { e.preventDefault(); togglePlay(); }
    if (e.key === "ArrowRight") jumpChange(+1);
    if (e.key === "ArrowLeft") jumpChange(-1);
  });

  computeView();
  drawEventStrip();
  // Open on the first question day, when the belief has some history.
  setTime(3 * 1440 + 600);
}

boot().catch(err => {
  document.body.innerHTML =
    `<pre style="padding:2em;color:#ff8a8a;white-space:pre-wrap">failed to load:\n${err.message || err}\n\n` +
    `trace URL: ${TRACE_URL || "(none)"}\nbelief URL: ${BELIEF_URL || "(none)"}\n` +
    `Serve via visualization/serve.py, not file://</pre>`;
});
