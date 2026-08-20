/* shared dataset manifest — loaded by both viewer pages.
 *
 * visualization/traces.json is the single source of truth: one entry per
 * published timeline, each optionally listing the baselines runs recorded
 * against it:
 *
 *   {"label": "hh1 — ...", "trace": "/profiles/.../trace.json",
 *    "runs": [{"label": "baselines grid", "run": "/archive/.../run_log.jsonl"}]}
 *
 * index.html picks a timeline from it; beliefs.html picks a (timeline, run)
 * pair. Publishing a new dataset is one line there — no URL editing and no
 * hardcoded paths in either page. Fails soft: if the manifest is missing or
 * malformed the pages still honour their ?trace=/?run= params.
 */
"use strict";

async function loadDatasets() {
  try {
    // repo-absolute, not relative to the page: the viewer is reachable
    // both at /visualization/viewer/ and at the short / URL, and a
    // relative path resolves to the wrong place from the latter
    const url = "/visualization/traces.json";
    const manifest = await (await fetch(url)).json();
    return (manifest.traces || []).filter(d => d && d.trace);
  } catch (e) {
    return [];
  }
}

/* Compare URLs the way the picker must: same file, however it was spelled
 * (manifest paths are repo-absolute, params may be relative). */
function samePath(a, b) {
  return new URL(a, location.href).pathname === new URL(b, location.href).pathname;
}

/* Fill a <select> with rows [{label, search}], preselect `currentIndex`, and
 * reload the page with that row's query string on change. */
function wirePicker(sel, rows, currentIndex) {
  rows.forEach((row, i) => {
    const opt = document.createElement("option");
    opt.value = String(i);
    opt.textContent = row.label;
    opt.selected = i === currentIndex;
    sel.appendChild(opt);
  });
  sel.disabled = rows.length < 2;
  sel.addEventListener("change", () => {
    location.search = rows[Number(sel.value)].search;
  });
}
