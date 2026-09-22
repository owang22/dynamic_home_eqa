// Run the PAGE'S OWN drawing code over the published file. There is no browser here, so this is the only way to
// check that a figure RENDERS rather than merely that its data exists. The page script runs inside new Function()
// so its names cannot collide with the harness's.
const fs = require("fs");
const html = fs.readFileSync("story.html", "utf8");
const js = [...html.matchAll(/<script>([\s\S]*?)<\/script>/g)].map(m => m[1]).sort((a, b) => b.length - a.length)[0];
const stub = new Proxy(function () {}, {
  get: (t, k) => (k === Symbol.toPrimitive ? () => "" : stub), set: () => true, apply: () => stub });
global.document = { querySelector: () => stub, querySelectorAll: () => [], getElementById: () => stub,
                    createElement: () => stub, addEventListener: () => {}, body: stub,
                    documentElement: { style: {}, getAttribute: () => null, setAttribute: () => {},
                                       classList: { add() {}, remove() {}, toggle() {} } } };
global.window = { addEventListener: () => {}, matchMedia: () => ({ matches: false, addEventListener() {} }),
                  location: { hash: "" }, localStorage: { getItem: () => null, setItem() {} } };
global.requestAnimationFrame = f => f();
let api;
try { api = new Function(js + "\n; return {drawPanel, PANELS, panelState, state, cellsOf, DATA, EXTRA, SERIES, metricsFor, popOf};")(); }
catch (e) { console.log("page script threw:", e.message); process.exit(1); }
const { drawPanel, PANELS, panelState, state, metricsFor, DATA } = api;
const POPS = [...Object.keys(DATA), "partial"];
const SPLITS = ["all", "cold", "moved"];
let cells = 0, drew = 0, empty = [], threw = [], dirty = [];
for (const p of PANELS) {
  for (const pop of POPS) for (const sp of SPLITS) for (const m of metricsFor(p)) {
    state.regime = pop; state.split = sp; panelState.metric[p.id] = m; cells++;
    let out;
    try { out = drawPanel(p); } catch (e) { threw.push(`${p.id}/${pop}/${sp}/${m}: ${e.message}`); continue; }
    const n = [...out.matchAll(/<path d="[^"]*"[^>]*stroke="var\(--/g)].length;
    if (n) drew++; else empty.push(`${p.id}/${pop}/${sp}/${m}`);
    if (/undefined|NaN|\[object/.test(out)) dirty.push(`${p.id}/${pop}/${sp}/${m}`);
  }
}
console.log(`${cells} panel/population/split/metric combinations`);
console.log(`  drew at least one line : ${drew}`);
console.log(`  drew nothing           : ${empty.length}${empty.length ? " -> " + empty.slice(0, 8).join(" ") : ""}`);
console.log(`  threw                  : ${threw.length}${threw.length ? "\n    " + threw.slice(0, 8).join("\n    ") : ""}`);
console.log(`  undefined/NaN in output: ${dirty.length}${dirty.length ? " -> " + dirty.slice(0, 8).join(" ") : ""}`);
// every "drew nothing" must SAY why, never just be blank
let silent = [];
for (const k of empty) {
  const [id, pop, sp, m] = k.split("/");
  state.regime = pop; state.split = sp; panelState.metric[id] = m;
  const out = drawPanel(PANELS.find(x => x.id === id));
  if (!/Nothing to draw here|Not on this figure/.test(out)) silent.push(k);
}
console.log(`  blank WITHOUT saying why: ${silent.length}${silent.length ? " -> " + silent.slice(0, 8).join(" ") : ""}`);
console.log(threw.length || dirty.length || silent.length ? "\nPROBLEMS" : "\nALL COMBINATIONS OK");
