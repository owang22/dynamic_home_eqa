// Run the PAGE'S OWN drawing code against the published file, so this checks what a reader gets, not a replica.
// The page script runs inside new Function() to give it its own scope - eval'd in module scope it collides with
// the harness's own names.
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
try { api = new Function(js + "\n; return {drawPanel, PANELS, panelState};")(); }
catch (e) { console.log("page script threw:", e.message); process.exit(1); }
const { drawPanel, PANELS, panelState } = api;
let bad = 0;
for (const id of ["SAMP", "D", "ACC4", "C2"]) {
  const p = PANELS.find(x => x.id === id);
  if (!p) { console.log(id, "MISSING from PANELS"); bad++; continue; }
  for (const fl of ["acc", "conf"]) {
    panelState.flavour = fl;
    let out;
    try { out = drawPanel(p); } catch (e) { console.log(`${id} [${fl}] THREW: ${e.message}`); bad++; continue; }
    const paths = [...out.matchAll(/<path d="([^"]*)"[^>]*stroke="var\((--[a-z0-9-]+)\)"[^>]*opacity="([\d.]+)"/g)];
    const pts = paths.map(m => (m[1].match(/[ML]/g) || []).length);
    const u = (out.match(/undefined/g) || []).length, n = (out.match(/NaN/g) || []).length;
    if (!paths.length || pts.some(v => v < 5) || u || n) bad++;
    console.log(`${id} [${fl}] lines=${paths.length} pts=${JSON.stringify(pts)} ` +
                `col=${JSON.stringify(paths.map(m => m[2]))} op=${JSON.stringify(paths.map(m => m[3]))} ` +
                `undefined=${u} NaN=${n}`);
  }
}
const samp = PANELS.find(x => x.id === "SAMP");
console.log("\nSAMP note:", samp && samp.note);
console.log(bad ? `\n${bad} PROBLEM(S)` : "\nALL PANELS DRAW");
