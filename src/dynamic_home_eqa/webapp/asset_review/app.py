"""
app.py — external-prop candidate review webapp.

Serves the tabletop renders under data/objects/external_props_candidates/
and records per-candidate curation decisions to review_decisions.json in
that same folder:

  verdict  keep | reject | (unset = undecided)
  rename   corrected category name for this asset ("scissors" -> "shears").
           A rename is per-ASSET: it can split a category (some scissors
           candidates become shears) — the promotion step groups keeps by
           their FINAL name (rename or original category).
  tags     free-text descriptors ("red", "over-ear", "kids", "ornate",
           "old-fashioned"). These are the input to the LLM-informed asset
           binder (Strategy 2+): at realized-day build, the binder gets each
           kept asset's tags alongside the occupant/household context and
           assigns owner-bound items in character (teen -> the gaming
           headphones) instead of a blind seeded draw. Tag with that use in
           mind: appearance + who it suits.
  note     free text.
  Per CATEGORY: want_more (+ note) — ask for another sourcing round with
  guidance ("closed umbrellas, not open ones").

Binds to 127.0.0.1 by default (same standing rule as realism_eval):
  python -m uvicorn dynamic_home_eqa.webapp.asset_review.app:app --port 8010
Decisions are flat JSON, safe to hand-edit; the app upserts on every change
(no save button).
"""
from __future__ import annotations

import json
import pathlib
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from dynamic_home_eqa.paths import REPO_ROOT

CAND_DIR = REPO_ROOT / "data" / "objects" / "external_props_candidates"
MAPPING = CAND_DIR / "candidates_mapping.json"
DECISIONS = CAND_DIR / "review_decisions.json"

app = FastAPI(title="asset review")
app.mount("/renders", StaticFiles(directory=str(CAND_DIR / "renders")), name="renders")


def _load_decisions() -> dict:
    if DECISIONS.exists():
        return json.loads(DECISIONS.read_text())
    return {"items": {}, "categories": {}}


def _save_decisions(d: dict) -> None:
    DECISIONS.write_text(json.dumps(d, indent=1, sort_keys=True))


class ItemDecision(BaseModel):
    uid: str
    verdict: Optional[str] = None          # "keep" | "reject" | None
    rename: Optional[str] = None
    tags: Optional[list[str]] = None
    note: Optional[str] = None


class CategoryDecision(BaseModel):
    category: str
    want_more: Optional[bool] = None
    note: Optional[str] = None


@app.get("/api/state")
def state() -> dict:
    if not MAPPING.exists():
        raise HTTPException(404, "candidates_mapping.json missing — run the sourcing script")
    return {"mapping": json.loads(MAPPING.read_text()), "decisions": _load_decisions()}


@app.post("/api/item")
def set_item(d: ItemDecision) -> dict:
    dec = _load_decisions()
    entry = dec["items"].setdefault(d.uid, {})
    for field in ("verdict", "rename", "tags", "note"):
        v = getattr(d, field)
        if v is not None:
            if v == "" or v == []:
                entry.pop(field, None)
            else:
                entry[field] = v
    if not entry:
        dec["items"].pop(d.uid, None)
    _save_decisions(dec)
    return {"ok": True}


@app.post("/api/category")
def set_category(d: CategoryDecision) -> dict:
    dec = _load_decisions()
    entry = dec["categories"].setdefault(d.category, {})
    if d.want_more is not None:
        entry["want_more"] = d.want_more
    if d.note is not None:
        if d.note == "":
            entry.pop("note", None)
        else:
            entry["note"] = d.note
    if not entry:
        dec["categories"].pop(d.category, None)
    _save_decisions(dec)
    return {"ok": True}


@app.get("/api/export")
def export() -> dict:
    """Kept assets grouped by FINAL category name (rename wins) — the shape
    the promotion step consumes. Categories with want_more are listed with
    their guidance notes for the next sourcing round."""
    mapping = {e["uid"]: e for e in json.loads(MAPPING.read_text())}
    dec = _load_decisions()
    keeps: dict[str, list] = {}
    for uid, d in dec["items"].items():
        if d.get("verdict") != "keep" or uid not in mapping:
            continue
        e = dict(mapping[uid])
        final = d.get("rename") or e["category"]
        e["tags"] = d.get("tags", [])
        if d.get("note"):
            e["note"] = d["note"]
        keeps.setdefault(final, []).append(e)
    more = {c: v for c, v in dec["categories"].items() if v.get("want_more")}
    return {"keep_by_category": keeps, "want_more": more}


_PAGE = """<!doctype html><meta charset="utf-8"><title>asset review</title>
<style>
 body{font:14px system-ui;margin:0;background:#f4f5f7;color:#1a1a1a}
 header{position:sticky;top:0;background:#fff;border-bottom:1px solid #ddd;padding:10px 16px;z-index:5;display:flex;gap:16px;align-items:center}
 h1{font-size:16px;margin:0} .count{color:#666}
 .cat{margin:18px 16px} .cat h2{font-size:15px;margin:6px 0;display:flex;gap:12px;align-items:center}
 .cards{display:flex;flex-wrap:wrap;gap:10px}
 .card{background:#fff;border:1px solid #ddd;border-radius:8px;padding:8px;width:392px}
 .card img{width:376px;border-radius:4px;background:#dfe2e5}
 .card.keep{outline:3px solid #2e9e44} .card.reject{outline:3px solid #c33;opacity:.55}
 .row{display:flex;gap:6px;margin-top:6px;align-items:center}
 button{border:1px solid #bbb;background:#fafafa;border-radius:5px;padding:3px 10px;cursor:pointer}
 button.on-keep{background:#2e9e44;color:#fff;border-color:#2e9e44}
 button.on-reject{background:#c33;color:#fff;border-color:#c33}
 input[type=text]{flex:1;border:1px solid #ccc;border-radius:5px;padding:3px 6px;font:13px system-ui}
 .uid{font:11px monospace;color:#777} .src{font-size:11px;padding:1px 6px;border-radius:8px;background:#e6e9ef}
 .src.existing{background:#ffe9c2}
 label.more{font-weight:400;font-size:13px;display:flex;gap:4px;align-items:center}
</style>
<header><h1>External-prop candidate review</h1><span class="count" id="count"></span>
<span style="flex:1"></span><a href="/api/export" target="_blank">export JSON</a></header>
<div id="root"></div>
<script>
let S;
const dbc = {};
function debounce(k, fn){ clearTimeout(dbc[k]); dbc[k]=setTimeout(fn, 500); }
async function post(url, body){ await fetch(url,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body)}); refreshCount(); }
function refreshCount(){
  fetch('/api/state').then(r=>r.json()).then(s=>{
    const items = Object.values(s.decisions.items||{});
    document.getElementById('count').textContent =
      `${items.filter(d=>d.verdict==='keep').length} keep / ${items.filter(d=>d.verdict==='reject').length} reject / ${s.mapping.length} total`;
  });
}
function card(e, d){
  const div = document.createElement('div');
  div.className = 'card' + (d.verdict ? ' ' + d.verdict : '');
  const img = e.category + '__' + (e.source === 'existing'
      ? e.uid.split('_').slice(1).join('_').slice(0,8) + '_ACCEPTED'
      : (e.objaverse_uid||'').slice(0,8)) + '.png';
  div.innerHTML = `
    <img loading="lazy" src="/renders/${img}">
    <div class="row"><span class="uid">${e.uid}</span>
      <span class="src ${e.source}">${e.source}</span><span style="flex:1"></span>
      <button class="k ${d.verdict==='keep'?'on-keep':''}">keep</button>
      <button class="r ${d.verdict==='reject'?'on-reject':''}">reject</button></div>
    <div class="row"><input type="text" class="rename" placeholder="rename category (optional)" value="${d.rename||''}"></div>
    <div class="row"><input type="text" class="tags" placeholder="tags, comma separated (color, style, who it suits)" value="${(d.tags||[]).join(', ')}"></div>
    <div class="row"><input type="text" class="note" placeholder="note" value="${d.note||''}"></div>`;
  const upd = v => { post('/api/item', {uid:e.uid, verdict:v});
    div.className='card'+(v?' '+v:'');
    div.querySelector('.k').className='k'+(v==='keep'?' on-keep':'');
    div.querySelector('.r').className='r'+(v==='reject'?' on-reject':''); };
  div.querySelector('.k').onclick = () => upd(d.verdict==='keep'?(d.verdict=null,null):(d.verdict='keep','keep'));
  div.querySelector('.r').onclick = () => upd(d.verdict==='reject'?(d.verdict=null,null):(d.verdict='reject','reject'));
  div.querySelector('.rename').oninput = ev => debounce(e.uid+'r', ()=>post('/api/item',{uid:e.uid, rename:ev.target.value.trim()}));
  div.querySelector('.tags').oninput = ev => debounce(e.uid+'t', ()=>post('/api/item',{uid:e.uid, tags:ev.target.value.split(',').map(s=>s.trim()).filter(Boolean)}));
  div.querySelector('.note').oninput = ev => debounce(e.uid+'n', ()=>post('/api/item',{uid:e.uid, note:ev.target.value.trim()}));
  return div;
}
fetch('/api/state').then(r=>r.json()).then(s=>{
  S = s; const root = document.getElementById('root');
  const bycat = {};
  s.mapping.forEach(e => (bycat[e.category] = bycat[e.category]||[]).push(e));
  Object.keys(bycat).sort().forEach(cat => {
    const cd = (s.decisions.categories||{})[cat] || {};
    const sec = document.createElement('div'); sec.className='cat';
    sec.innerHTML = `<h2>${cat} <label class="more"><input type="checkbox" ${cd.want_more?'checked':''}> fetch more candidates</label>
      <input type="text" style="width:340px" class="catnote" placeholder="guidance for next round (e.g. closed umbrellas)" value="${cd.note||''}"></h2>`;
    sec.querySelector('input[type=checkbox]').onchange = ev => post('/api/category',{category:cat, want_more:ev.target.checked});
    sec.querySelector('.catnote').oninput = ev => debounce(cat, ()=>post('/api/category',{category:cat, note:ev.target.value.trim()}));
    const cards = document.createElement('div'); cards.className='cards';
    bycat[cat].forEach(e => cards.appendChild(card(e, (s.decisions.items||{})[e.uid]||{})));
    sec.appendChild(cards); root.appendChild(sec);
  });
  refreshCount();
});
</script>"""


@app.get("/", response_class=HTMLResponse)
def page() -> str:
    return _PAGE
