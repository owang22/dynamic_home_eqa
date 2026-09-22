#!/usr/bin/env python3
"""Build the interactive story page (Routine Shift Testbench) from story_data.json."""
import json, os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
data = json.load(open(f"{ROOT}/story_data.json"))
out = sys.argv[1] if len(sys.argv) > 1 else f"{ROOT}/story.html"

HTML = r'''<title>Routine Shift Testbench</title>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,500;9..144,600&family=Source+Sans+3:wght@400;600&family=IBM+Plex+Mono:wght@400;500&display=swap">
<style>
:root{color-scheme:light;
  --paper:#f7f5f0;--panel:#fcfcfb;--ink:#141413;--ink2:#52514e;--muted:#7a776f;--line:#e3ded4;--grid:#ebe7df;
  --shift:#f3d9a0;--return:#cfe8d6;--tip-bg:#141413;--tip-ink:#f7f5f0;
  --s1:#2a78d6;--s2:#eb6834;--s3:#1baf7a;--s4:#eda100;--s5:#e87ba4;--s6:#008300;--s7:#4a3aa7;--s8:#e34948;--sg:#8e8a84;--sv:#4a3aa7}
@media (prefers-color-scheme: dark){:root:not([data-theme="light"]){color-scheme:dark;
  --paper:#1a1a19;--panel:#232322;--ink:#f2f1ec;--ink2:#c3c2b7;--muted:#9c9a91;--line:#3a3936;--grid:#2e2d2b;
  --shift:#5c4a24;--return:#2d4a36;--tip-bg:#f2f1ec;--tip-ink:#1a1a19;
  --s1:#3987e5;--s2:#d95926;--s3:#199e70;--s4:#c98500;--s5:#d55181;--s6:#3aa53a;--s7:#9085e9;--s8:#e66767;--sg:#a5a29b;--sv:#9085e9}}
:root[data-theme="dark"]{color-scheme:dark;
  --paper:#1a1a19;--panel:#232322;--ink:#f2f1ec;--ink2:#c3c2b7;--muted:#9c9a91;--line:#3a3936;--grid:#2e2d2b;
  --shift:#5c4a24;--return:#2d4a36;--tip-bg:#f2f1ec;--tip-ink:#1a1a19;
  --s1:#3987e5;--s2:#d95926;--s3:#199e70;--s4:#c98500;--s5:#d55181;--s6:#3aa53a;--s7:#9085e9;--s8:#e66767;--sg:#a5a29b;--sv:#9085e9}
*{box-sizing:border-box}
body{margin:0;background:var(--paper);color:var(--ink);font-family:"Source Sans 3",system-ui,sans-serif;font-size:15.5px;line-height:1.5}
.wrap{max-width:1120px;margin:0 auto;padding-inline:16px;padding-block:0 56px}
h1,h2,h3{font-family:Fraunces,Georgia,serif;font-weight:500;text-wrap:balance;margin:0}
h1{font-size:34px;line-height:1.1;padding-block:22px 6px} h2{font-size:22px;margin-block:34px 8px} h3{font-size:15px;color:var(--ink2);margin-bottom:4px;font-family:"Source Sans 3",sans-serif;font-weight:600}
p{max-width:72ch} .lead{font-size:17px;color:var(--ink2);margin-block:4px 18px}
.mono{font-family:"IBM Plex Mono",ui-monospace,monospace;font-size:12.5px}
.muted{color:var(--muted)}
.steps{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:10px;margin-block:12px 18px}
.step{background:var(--panel);border:1px solid var(--line);border-left:4px solid var(--line);border-radius:6px;padding:10px 12px;cursor:pointer;text-align:left;font:inherit;color:var(--ink)}
.step b{display:block;font-family:Fraunces,serif;font-size:16px;margin-bottom:2px} .step span{font-size:13.5px;color:var(--ink2)}
.step.on{border-left-color:var(--s1)} .step:focus-visible{outline:2px solid var(--s1);outline-offset:2px}
.controls{display:flex;flex-wrap:wrap;gap:8px 18px;align-items:center;padding-block:8px 6px;position:sticky;top:env(safe-area-inset-top,0px);background:var(--paper);z-index:4;border-bottom:1px solid var(--line)}
.controls label{display:inline-flex;align-items:center;gap:6px;font-size:13.5px;color:var(--ink2)}
select{font:inherit;font-size:13.5px;padding:3px 6px;background:var(--panel);color:var(--ink);border:1px solid var(--line);border-radius:4px}
.legend{display:flex;flex-wrap:wrap;gap:6px 10px;margin-block:10px 6px}
.chip{position:relative;display:inline-flex;align-items:center;gap:7px;padding:4px 10px 4px 8px;border:1px solid var(--line);border-radius:999px;background:var(--panel);font-size:13.5px;cursor:pointer;color:var(--ink)}
.chip input{margin:0;accent-color:var(--ink2)} .chip .sw{width:16px;height:3px;border-radius:2px;display:inline-block}
.chip .sw.dash{background:repeating-linear-gradient(90deg,currentColor 0 4px,transparent 4px 7px)}
.chip .q{width:16px;height:16px;border-radius:50%;border:1px solid var(--muted);color:var(--muted);font-size:11px;display:inline-grid;place-items:center;line-height:1}
.chip:hover .pop,.chip:focus-within .pop,.chip.open .pop{display:block}
.pop{display:none;position:absolute;left:0;top:calc(100% + 8px);z-index:6;width:min(360px,86vw);background:var(--panel);color:var(--ink);border:1px solid var(--line);border-radius:8px;padding:10px 12px;font-size:13.5px;line-height:1.45;box-shadow:0 8px 24px rgba(0,0,0,.18);cursor:default}
.pop b{display:block;font-family:Fraunces,serif;font-size:15px;margin-bottom:4px} .pop .how{color:var(--ink2);margin-top:6px;font-size:12.5px}
.chart-wrap{position:relative;background:var(--panel);border:1px solid var(--line);border-radius:8px;padding:10px 8px 6px}
svg{display:block;width:100%;height:auto} svg text{font-family:"IBM Plex Mono",monospace;font-size:11px;fill:var(--ink2)}
svg .grid{stroke:var(--grid)} svg .axis{stroke:var(--line)} svg .stg{font-size:11.5px;fill:var(--ink);font-family:"Source Sans 3",sans-serif;font-weight:600}
svg .lbl{font-family:"Source Sans 3",sans-serif;font-size:11.5px;fill:var(--ink)}
.tip{position:absolute;pointer-events:none;display:none;background:var(--tip-bg);color:var(--tip-ink);padding:7px 10px;border-radius:6px;font-size:12.5px;line-height:1.4;z-index:7;min-width:170px;box-shadow:0 6px 18px rgba(0,0,0,.2)}
.tip .r{display:flex;justify-content:space-between;gap:12px} .tip .r i{width:10px;height:3px;display:inline-block;border-radius:2px;margin-right:6px;vertical-align:middle}
.small{display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:14px;margin-top:10px}
.panel{background:var(--panel);border:1px solid var(--line);border-radius:8px;padding:10px 12px;position:relative}
.panel p{font-size:13.5px;color:var(--ink2);margin:2px 0 8px}
table{border-collapse:collapse;width:100%;font-size:13.5px} th,td{text-align:left;padding:5px 8px;border-bottom:1px solid var(--line);vertical-align:top}
th{color:var(--muted);font-weight:600;font-size:12px;text-transform:uppercase;letter-spacing:.04em} td.num{text-align:right;font-variant-numeric:tabular-nums}
.tbl{overflow-x:auto} .swatch{width:12px;height:3px;display:inline-block;border-radius:2px;margin-right:8px;vertical-align:middle}
.gloss{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:12px}
.gloss .g{background:var(--panel);border:1px solid var(--line);border-radius:8px;padding:10px 12px;font-size:13.5px} .gloss b{font-family:Fraunces,serif;font-size:15px;display:block;margin-bottom:3px}
.note{font-size:13px;color:var(--muted);max-width:80ch}
@media (max-width:640px){h1{font-size:28px} .controls{gap:6px 12px}}
@media (prefers-reduced-motion:no-preference){.step,.chip{transition:border-color .15s}}
</style>
<div class="wrap">
<h1>Routine Shift Testbench</h1>
<p class="lead">A home robot answers “where is X?” every day. Ten simulated households run a normal routine for two weeks, then everyone (or one person) is off sick for ten days, then life returns to normal. The question is not whether a method answers well — it is whether it <em>learns</em> the routine, <em>notices</em> when the routine breaks, <em>adapts</em> to the new one, and copes when the old routine comes back.</p>

<div class="steps" role="group" aria-label="the story in four steps">
  <button class="step on" data-step="learn"><b>1 · Learn</b><span>Over the first two weeks every learner climbs from ~45% to 80–85%. “Last seen” never learns: it stays at ~50%.</span></button>
  <button class="step" data-step="break"><b>2 · Break</b><span>On the first sick day accuracy falls by 40 points. Things are no longer where the routine puts them.</span></button>
  <button class="step" data-step="relearn"><b>3 · Re-learn</b><span>Methods that forget the past adapt to the sick routine within days; methods that never forget stay stuck.</span></button>
  <button class="step" data-step="return"><b>4 · Break again</b><span>When normal life returns, the adaptive methods break again — and the ones that never forgot are right at once.</span></button>
</div>

<div class="controls">
  <label>households <select id="regime"><option value="household">everyone sick · households 1–10</option><option value="household_rep">everyone sick · households 11–20 (replication)</option><option value="person">one person sick · that person's things</option></select></label>
  <label>questions <select id="split"><option value="all">all questions</option><option value="moved">only objects that moved since the night round</option></select></label>
  <label><input type="checkbox" id="bands" checked> show ±1 sd across households</label>
  <label><input type="checkbox" id="more"> more methods</label>
</div>

<div class="legend" id="legend"></div>
<div class="chart-wrap"><svg id="main" viewBox="0 0 1000 380" role="img" aria-label="accuracy per day"></svg><div class="tip" id="tip"></div></div>
<p class="note" id="mainnote"></p>

<h2>Does the method notice?</h2>
<p>Getting the answer wrong is one thing; knowing that you are probably wrong is another. Three ways of noticing, all sitting on the same “timetable” learner.</p>
<div class="small" id="small"></div>

<h2>By stage</h2>
<p>Mean accuracy over each stage, ± the spread across households (one number per household, then the standard deviation). An effect is only claimed when it clears that spread.</p>
<div class="tbl"><table id="stagetable"></table></div>

<h2>The methods, in plain words</h2>
<div class="gloss" id="gloss"></div>
<p class="note" style="margin-top:14px">Regime: 32 days from a Monday; the walkthrough is day 0; days 1–13 are the lead-up, 14–23 the sick spell, 24–31 the return. The robot does one round at 03:00 and, ten minutes after every question, learns where the object actually was (“found-it feedback”). Questions are asked while the object is in use, about the everyday things the sick routine moves: book, water bottle, tablet, mug, charger, glasses, glass, razor — at most one question per object per half hour, 12–24 a day. No language-model method is in this loop.</p>
</div>

<script>
const DATA = /*DATA*/null;
const DAYNAMES = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"];
const SERIES = [
 {k:"tt3d", name:"timetable, 3-day memory", v:"--s1", core:true, gloss:"Keeps a little diary: for every object and every two-hour slot of the day, where it was seen there. Old entries fade with a half-life of three days, so last week counts half as much as the last three days. Answers with the slot's most common place.", how:"Learns the routine, breaks when it shifts, re-learns the new one, and breaks again when the old one returns — because it forgets."},
 {k:"ttfrozen", name:"timetable, never forgets", v:"--s2", core:true, gloss:"The same diary, but nothing ever fades: every sighting since day one counts the same.", how:"Learns and breaks like the 3-day version, but never quite adapts to the sick routine (two weeks of old entries outvote it) — and is right at once when normal life returns."},
 {k:"detector3d", name:"3-day timetable + change alarm", v:"--s3", core:true, gloss:"The 3-day timetable plus a watchdog. After each answer the robot learns the truth; the watchdog keeps a running tally of how surprising recent mistakes are compared with the usual rate (a statistical test that only sounds when surprise has accumulated beyond a set bar). When it sounds, the diary is mostly wiped so the new routine is learned faster.", how:"Sounds the alarm on the first sick day in 8 of 10 households and on the return in 5 of 10, with no false alarms in the lead-up."},
 {k:"mf3d", name:"most frequent place, 3-day memory", v:"--s4", core:true, gloss:"Ignores the time of day: answers with the place the object was seen most often, with sightings fading over three days.", how:"Cannot learn that the mug is in the kitchen at breakfast and on the desk at noon, so it plateaus lower — but it shows the same break / re-learn / break-again shape."},
 {k:"bma", name:"hedge over memory lengths", v:"--s5", core:true, gloss:"Runs several timetables at once — memories of one day, three days, a week, and forever — and each day gives more say to whichever has been predicting best lately (Bayesian model averaging).", how:"Shifts its trust to the short memories at the sick day and back to the long one on the return, so it adapts in the spell and does not break on the return: it hedges the second break away."},
 {k:"lastseen", name:"last seen", v:"--sg", core:true, gloss:"Answers with the place the object was last seen — at the night round or in the last found-it feedback.", how:"The baseline that does not learn: flat at about 50% throughout, because questions are asked about things in use, away from where the night round saw them."},
 {k:"mffrozen", name:"most frequent place, never forgets", v:"--s6", core:false, gloss:"Most-frequent place with no fading at all.", how:"Stuck for the whole sick spell."},
 {k:"perpetua", name:"Perpetua*", v:"--s7", core:false, gloss:"A model of how often each object moves and where it tends to go, from the literature, with a slow forgetting rate.", how:"Does not learn a time-of-day routine here; sits between last seen and the timetables."},
 {k:"tt1d", name:"timetable, 1-day memory", v:"--s8", core:false, gloss:"The timetable with a one-day half-life.", how:"Adapts fastest and shows the largest second break."},
];
const STEP_LINES = {learn:["tt3d","ttfrozen","lastseen"], break:["tt3d","ttfrozen","mf3d","lastseen"], relearn:["tt3d","ttfrozen","detector3d","bma"], return:["tt3d","ttfrozen","detector3d","bma","lastseen"]};
const STEP_NOTE = {learn:"Lead-up (days 1–13): the timetables climb from ~45% to 80–85% as their diaries fill; last seen stays flat.",
 break:"First sick day (day 14): every learner drops by roughly 40 points — that is the size of the routine change, ~4 standard deviations across households. Most-frequent falls furthest.",
 relearn:"Inside the spell (days 14–23): the 3-day timetable is back near 85–90% within a week; the never-forgets timetable crawls; the change alarm's wipe makes the re-learning faster still; the hedge follows the short memories.",
 return:"Return (days 24–31): the adaptive methods break again (down to 55–60% and re-learn); the never-forgets timetable is right immediately; the hedge moves its trust back to it and shows no second break."};
const css = v => getComputedStyle(document.documentElement).getPropertyValue(v).trim();
const state = {regime:"household", split:"all", bands:true, more:false, on:new Set(STEP_LINES.learn), step:"learn"};
const $ = s => document.querySelector(s);

function daily(reg, key, split){ // -> {mean:[day->%], sd:[day->%], n:[..]} across households
  const R = DATA[reg]; const A = R.agents[key]; if(!A) return null;
  const nd = R.days; const mean=[], sd=[], nn=[];
  for(let d=1; d<nd; d++){ const vals=[]; let N=0;
    for(const hh of Object.keys(A)){ const [n,ok]=A[hh][split][d]; if(n>=3){ vals.push(100*ok/n); N+=n; } }
    if(!vals.length){mean.push(null); sd.push(null); nn.push(0); continue}
    const m = vals.reduce((a,b)=>a+b,0)/vals.length; const s = vals.length>1? Math.sqrt(vals.reduce((a,b)=>a+(b-m)**2,0)/(vals.length-1)) : 0;
    mean.push(m); sd.push(s); nn.push(N);
  } return {mean, sd, n:nn};
}
function pooled(reg, key, split, days){ const A=DATA[reg].agents[key]; if(!A) return null; let n=0,ok=0; for(const hh of Object.keys(A)) for(const d of days){ n+=A[hh][split][d][0]; ok+=A[hh][split][d][1]; } return n? 100*ok/n : null; }
function hhStage(reg, key, split, days){ const A=DATA[reg].agents[key]; if(!A) return null; const vals=[]; for(const hh of Object.keys(A)){ let n=0,ok=0; for(const d of days){ n+=A[hh][split][d][0]; ok+=A[hh][split][d][1]; } if(n) vals.push(100*ok/n);} const m=vals.reduce((a,b)=>a+b,0)/vals.length; const s=vals.length>1?Math.sqrt(vals.reduce((a,b)=>a+(b-m)**2,0)/(vals.length-1)):0; return {m,s,k:vals.length}; }
function stagesOf(reg){ const R=DATA[reg]; const out=[]; let cur=null; for(let d=1; d<R.days; d++){ const st=R.stages[String(d)]||"plain"; if(!cur||cur.name!==st){ cur={name:st,a:d,b:d}; out.push(cur);} else cur.b=d; } return out; }
const STAGE_LABEL = {lead:"lead-up (normal routine)", sick:"sick spell", return:"return to normal"};
const STAGE_FILL = {sick:"--shift", return:"--return"};

function renderLegend(){
  const L=$("#legend"); L.innerHTML="";
  for(const s of SERIES){ if(!s.core && !state.more) continue; if(!DATA[state.regime].agents[s.k]) continue;
    const chip=document.createElement("label"); chip.className="chip"; chip.innerHTML=`<input type="checkbox" ${state.on.has(s.k)?"checked":""} aria-label="${s.name}"><i class="sw" style="background:var(${s.v})"></i>${s.name}<span class="q" tabindex="0" aria-label="what is ${s.name}">?</span><div class="pop" role="tooltip"><b>${s.name}</b>${s.gloss}<div class="how">On this testbench: ${s.how}</div></div>`;
    chip.querySelector("input").addEventListener("change", e=>{ if(e.target.checked) state.on.add(s.k); else state.on.delete(s.k); draw(); });
    chip.querySelector(".q").addEventListener("click", e=>{ e.preventDefault(); chip.classList.toggle("open"); });
    L.appendChild(chip); }
}

function draw(){
  const reg=state.regime, R=DATA[reg], nd=R.days, W=1000,H=380,L=44,Rt=215,T=22,B=40;
  const x=d=>L+(d-1)*(W-L-Rt)/(nd-2), y=v=>T+(100-v)*(H-T-B)/100;
  const svg=$("#main"); let g="";
  for(const st of stagesOf(reg)){ const f=STAGE_FILL[st.name]; if(f) g+=`<rect x="${(x(st.a)-8).toFixed(1)}" y="${T}" width="${(x(st.b)-x(st.a)+16).toFixed(1)}" height="${H-T-B}" fill="var(${f})" opacity="0.5"/>`;
    g+=`<text class="stg" x="${((x(st.a)+x(st.b))/2).toFixed(1)}" y="${T-7}" text-anchor="middle">${STAGE_LABEL[st.name]||st.name}</text>`; }
  for(const v of [0,25,50,75,100]) g+=`<line class="grid" x1="${L}" x2="${W-Rt}" y1="${y(v).toFixed(1)}" y2="${y(v).toFixed(1)}"/><text x="${L-8}" y="${(y(v)+4).toFixed(1)}" text-anchor="end">${v}%</text>`;
  const i0=DAYNAMES.indexOf(R.day0);
  for(let d=1; d<nd; d++){ if(d%2===1) g+=`<text x="${x(d).toFixed(1)}" y="${H-B+16}" text-anchor="middle">${d}</text>`; }
  g+=`<text x="${((L+W-Rt)/2).toFixed(1)}" y="${H-6}" text-anchor="middle" class="lbl">day (weekday routine throughout; day 0 = walkthrough)</text>`;
  const shown=SERIES.filter(s=>state.on.has(s.k)&&DATA[reg].agents[s.k]); const ends=[];
  for(const s of shown){ const D=daily(reg,s.k,state.split); if(!D) continue; const col=`var(${s.v})`;
    if(state.bands){ const up=[],lo=[]; D.mean.forEach((m,i)=>{ if(m==null) return; up.push(`${x(i+1).toFixed(1)},${y(Math.min(100,m+D.sd[i])).toFixed(1)}`); lo.unshift(`${x(i+1).toFixed(1)},${y(Math.max(0,m-D.sd[i])).toFixed(1)}`); }); if(up.length>1) g+=`<polygon points="${up.join(" ")} ${lo.join(" ")}" fill="${col}" opacity="0.12"/>`; }
    const pts=[]; D.mean.forEach((m,i)=>{ if(m!=null) pts.push(`${x(i+1).toFixed(1)},${y(m).toFixed(1)}`); });
    g+=`<polyline fill="none" stroke="${col}" stroke-width="2.2" stroke-linejoin="round" points="${pts.join(" ")}"/>`;
    const last=D.mean.map((m,i)=>[m,i]).filter(a=>a[0]!=null).pop(); if(last) ends.push({s,col,yy:y(last[0]),v:last[0]}); }
  ends.sort((a,b)=>a.yy-b.yy); let prev=-99; for(const e of ends){ let yy=Math.max(e.yy, prev+14); prev=yy; g+=`<circle cx="${(W-Rt).toFixed(1)}" cy="${e.yy.toFixed(1)}" r="3.5" fill="${e.col}"/><text class="lbl" x="${W-Rt+8}" y="${(yy+4).toFixed(1)}" style="fill:var(--ink)">${e.s.name} · ${e.v.toFixed(0)}%</text>`; }
  g+=`<line id="xh" class="axis" x1="0" x2="0" y1="${T}" y2="${H-B}" style="display:none"/>`;
  svg.innerHTML=g; svg.dataset.geom=JSON.stringify({L,Rt,W,nd});
  $("#mainnote").textContent = STEP_NOTE[state.step] + (state.split==="moved" ? " (Showing only the questions whose object had moved since the 03:00 round — the half where learning matters; 'last seen' is right on the other half almost by definition.)" : "");
  renderSmall(); renderTable();
}
function hover(ev){
  const svg=$("#main"); const geom=JSON.parse(svg.dataset.geom||"null"); if(!geom) return; const rect=svg.getBoundingClientRect(); const px=(ev.clientX-rect.left)*geom.W/rect.width;
  const d=Math.round((px-geom.L)/((geom.W-geom.L-geom.Rt)/(geom.nd-2)))+1; if(d<1||d>=geom.nd){ $("#tip").style.display="none"; $("#xh").style.display="none"; return; }
  const xx=geom.L+(d-1)*(geom.W-geom.L-geom.Rt)/(geom.nd-2); const xh=$("#xh"); xh.setAttribute("x1",xx); xh.setAttribute("x2",xx); xh.style.display="";
  const R=DATA[state.regime]; const st=R.stages[String(d)]||"plain"; const i0=DAYNAMES.indexOf(R.day0);
  let rows=`<div style="margin-bottom:4px"><b>day ${d}</b> · ${DAYNAMES[(i0+d)%7]} · ${STAGE_LABEL[st]||st}</div>`;
  for(const s of SERIES){ if(!state.on.has(s.k)) continue; const D=daily(state.regime,s.k,state.split); if(!D||D.mean[d-1]==null) continue; rows+=`<div class="r"><span><i style="background:var(${s.v})"></i>${s.name}</span><span>${D.mean[d-1].toFixed(0)}% ±${D.sd[d-1].toFixed(0)}</span></div>`; }
  const tip=$("#tip"); tip.innerHTML=rows; tip.style.display="block"; const wrap=svg.parentElement.getBoundingClientRect(); let lx=ev.clientX-wrap.left+14; if(lx+230>wrap.width) lx=ev.clientX-wrap.left-240; tip.style.left=lx+"px"; tip.style.top=(ev.clientY-wrap.top+12)+"px";
}
function renderSmall(){
  const reg=state.regime, R=DATA[reg], nd=R.days, host=$("#small"); host.innerHTML="";
  const hasUQ = R.fires && R.fires.detector3d;
  if(!hasUQ){ host.innerHTML=`<div class="panel"><p>The “noticing” methods were run on households 1–10 and on the one-person regime; this replication set has the learners only.</p></div>`; return; }
  const W=460,H=170,L=34,T=16,B=26,Rr=10; const x=d=>L+(d-1)*(W-L-Rr)/(nd-2);
  const bands=()=>{ let g=""; for(const st of stagesOf(reg)){ const f=STAGE_FILL[st.name]; if(f) g+=`<rect x="${(x(st.a)-6).toFixed(1)}" y="${T}" width="${(x(st.b)-x(st.a)+12).toFixed(1)}" height="${H-T-B}" fill="var(${f})" opacity="0.5"/>`; } return g; };
  // 1. alarm raster
  const hh=R.hh; const rowH=(H-T-B)/hh.length; let g=bands();
  hh.forEach((h,i)=>{ const yy=T+i*rowH; g+=`<text x="${L-6}" y="${(yy+rowH*0.7).toFixed(1)}" text-anchor="end" style="font-size:9.5px">${i+1}</text>`;
    for(const d of (R.fires.detector3d[h]||[])) g+=`<rect x="${(x(d)-4).toFixed(1)}" y="${(yy+1).toFixed(1)}" width="8" height="${(rowH-2).toFixed(1)}" rx="2" fill="var(--s3)"><title>household ${i+1}: alarm on day ${d}</title></rect>`;
    for(const d of ((R.fires.detectorfrozen||{})[h]||[])) g+=`<rect x="${(x(d)-4).toFixed(1)}" y="${(yy+rowH*0.55).toFixed(1)}" width="8" height="${(rowH*0.4).toFixed(1)}" rx="1" fill="var(--s2)"><title>household ${i+1}, on the never-forgets timetable: alarm on day ${d}</title></rect>`; });
  for(let d=1; d<nd; d+=4) g+=`<text x="${x(d).toFixed(1)}" y="${H-B+14}" text-anchor="middle">${d}</text>`;
  const f3=R.fires.detector3d, ff=R.fires.detectorfrozen||{}; const cnt=(F,days)=>Object.values(F).filter(a=>a.some(d=>days.includes(d))).length;
  host.innerHTML+=`<div class="panel"><h3>Change alarm — when it sounds, per household</h3><p>Each row is a household; a tall tick is the alarm on the 3-day timetable, a short one the alarm on the never-forgets timetable. Sick spell: ${cnt(f3,[14,15])}/${hh.length} on days 14–15 (never-forgets ${cnt(ff,[14,15])}/${hh.length}); return: ${cnt(f3,[24,25,26])}/${hh.length} on days 24–26 (never-forgets ${cnt(ff,[24,25,26])}/${hh.length}); false alarms in the lead-up: ${cnt(f3,[1,2,3,4,5,6,7,8,9,10,11,12,13])}/${hh.length}.</p><svg viewBox="0 0 ${W} ${H}" role="img" aria-label="alarm days per household">${g}</svg></div>`;
  // 2. conformal set size + coverage
  const C=R.conformal; const days=[...Array(nd-1).keys()].map(i=>i+1);
  const ss=days.map(d=>C[String(d)]? C[String(d)][2]/C[String(d)][0] : null), cv=days.map(d=>C[String(d)]? 100*C[String(d)][1]/C[String(d)][0] : null);
  const ymax=Math.max(...ss.filter(v=>v!=null))*1.1; const ys=v=>T+(ymax-v)*(H-T-B)/ymax;
  let g2=bands(); for(const v of [0,10,20]) if(v<=ymax) g2+=`<line class="grid" x1="${L}" x2="${W-Rr}" y1="${ys(v).toFixed(1)}" y2="${ys(v).toFixed(1)}"/><text x="${L-6}" y="${(ys(v)+4).toFixed(1)}" text-anchor="end">${v}</text>`;
  g2+=`<polyline fill="none" stroke="var(--sv)" stroke-width="2" points="${days.map((d,i)=>ss[i]==null?"":`${x(d).toFixed(1)},${ys(ss[i]).toFixed(1)}`).join(" ")}"/>`;
  for(let d=1; d<nd; d+=4) g2+=`<text x="${x(d).toFixed(1)}" y="${H-B+14}" text-anchor="middle">${d}</text>`;
  const stg=stagesOf(reg); const covStage=stg.map(s=>{ let n=0,c=0; for(let d=s.a; d<=s.b; d++){ const v=C[String(d)]; if(v){ n+=v[0]; c+=v[1]; } } return `${STAGE_LABEL[s.name]||s.name} ${n? (100*c/n).toFixed(0):"-"}%`; }).join(" · ");
  host.innerHTML+=`<div class="panel"><h3>Honest sets — how many places it has to name to be 90% sure</h3><p>Instead of one answer, the method names a set of places sized so the truth is inside about 90% of the time (online conformal prediction on the timetable). Line: the average number of places named per day. Share of days the truth was inside the set: ${covStage}. The set jumps from ~2 places to 15–20 on the first sick days and shrinks back as the new routine is learned.</p><svg viewBox="0 0 ${W} ${H}" role="img" aria-label="conformal set size per day">${g2}</svg></div>`;
  // 3. BMA short-memory weight
  const Bm=R.bma_short; const w=days.map(d=>Bm[String(d)]? 100*Bm[String(d)][1]/Bm[String(d)][0] : null); const yw=v=>T+(100-v)*(H-T-B)/100;
  let g3=bands(); for(const v of [0,50,100]) g3+=`<line class="grid" x1="${L}" x2="${W-Rr}" y1="${yw(v).toFixed(1)}" y2="${yw(v).toFixed(1)}"/><text x="${L-6}" y="${(yw(v)+4).toFixed(1)}" text-anchor="end">${v}%</text>`;
  g3+=`<polyline fill="none" stroke="var(--s5)" stroke-width="2" points="${days.map((d,i)=>w[i]==null?"":`${x(d).toFixed(1)},${yw(w[i]).toFixed(1)}`).join(" ")}"/>`;
  for(let d=1; d<nd; d+=4) g3+=`<text x="${x(d).toFixed(1)}" y="${H-B+14}" text-anchor="middle">${d}</text>`;
  host.innerHTML+=`<div class="panel"><h3>Hedge — how much trust goes to the short memories</h3><p>The hedge runs timetables with 1-day, 3-day, 1-week and unlimited memory and gives each a share of trust. Line: the share held by the short (1- and 3-day) memories. It jumps at the first sick day, drains back to the unlimited memory during the spell, and stays there on the return — which is why the hedge shows no second break.</p><svg viewBox="0 0 ${W} ${H}" role="img" aria-label="share of trust on short memories per day">${g3}</svg></div>`;
}
function renderTable(){
  const reg=state.regime, stg=stagesOf(reg); const T=$("#stagetable");
  let h=`<thead><tr><th>method</th>${stg.map(s=>`<th>${STAGE_LABEL[s.name]||s.name} (days ${s.a}–${s.b})</th>`).join("")}<th>break at day 14</th><th>break at day 24</th></tr></thead><tbody>`;
  for(const s of SERIES){ if(!DATA[reg].agents[s.k]) continue; if(!s.core && !state.more) continue;
    const cells=stg.map(st=>{ const days=[]; for(let d=st.a; d<=st.b; d++) days.push(d); const v=hhStage(reg,s.k,state.split,days); return v? `<td class="num">${v.m.toFixed(0)} <span class="muted">±${v.s.toFixed(0)}</span></td>` : "<td>-</td>"; });
    const D=daily(reg,s.k,state.split); const br=(a,b)=> (D&&D.mean[a-1]!=null&&D.mean[b-1]!=null)? `${(D.mean[b-1]-D.mean[a-1]).toFixed(0)}` : "-";
    h+=`<tr><td><i class="swatch" style="background:var(${s.v})"></i>${s.name}</td>${cells.join("")}<td class="num">${br(13,14)}</td><td class="num">${br(23,24)}</td></tr>`; }
  T.innerHTML=h+"</tbody>";
}
function renderGloss(){ $("#gloss").innerHTML = SERIES.map(s=>`<div class="g"><b><i class="swatch" style="background:var(${s.v})"></i>${s.name}</b>${s.gloss}<div class="muted" style="margin-top:4px">${s.how}</div></div>`).join("") +
 `<div class="g"><b>Change alarm (e-detector)</b>A statistical watchdog on the stream of the robot's own mistakes. Each surprising miss adds to a running score; ordinary misses let it fall back toward zero; the alarm sounds when the score passes a bar chosen so that false alarms are rare. A recent variant from the change-detection literature (2024); the same idea as a fire alarm that ignores one whiff of toast.</div>
  <div class="g"><b>Honest sets (online conformal prediction)</b>Rather than one guess, name enough places that the truth is inside about 9 times in 10, and keep adjusting the bar from the robot's own hit rate (2024 version with steps that shrink over time). When the routine breaks, the sets grow — the method is saying "I am no longer sure" in a way that can be checked.</div>
  <div class="g"><b>Hedge over memory lengths (Bayesian model averaging)</b>Keep several versions of the learner with different memory lengths and let recent performance decide how much to trust each. Adapts without being told, but also cancels the second break — a trade-off, not a free lunch.</div>`; }

document.querySelectorAll(".step").forEach(b=>b.addEventListener("click",()=>{ document.querySelectorAll(".step").forEach(x=>x.classList.remove("on")); b.classList.add("on"); state.step=b.dataset.step; state.on=new Set(STEP_LINES[state.step]); renderLegend(); draw(); }));
$("#regime").addEventListener("change",e=>{ state.regime=e.target.value; renderLegend(); draw(); });
$("#split").addEventListener("change",e=>{ state.split=e.target.value; draw(); });
$("#bands").addEventListener("change",e=>{ state.bands=e.target.checked; draw(); });
$("#more").addEventListener("change",e=>{ state.more=e.target.checked; renderLegend(); draw(); });
$("#main").addEventListener("mousemove",hover); $("#main").addEventListener("mouseleave",()=>{ $("#tip").style.display="none"; const xh=$("#xh"); if(xh) xh.style.display="none"; });
try{ const saved=localStorage.getItem("rst-regime"); if(saved && DATA[saved]) { state.regime=saved; $("#regime").value=saved; } }catch(e){}
$("#regime").addEventListener("change",e=>{ try{ localStorage.setItem("rst-regime", e.target.value); }catch(err){} });
renderLegend(); renderGloss(); draw();
</script>
'''
open(out, "w").write(HTML.replace("/*DATA*/null", json.dumps(data, separators=(",", ":"))))
print("wrote", out, os.path.getsize(out) // 1024, "KB")
