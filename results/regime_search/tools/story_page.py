#!/usr/bin/env python3
"""Build the interactive story page (Routine Shift Testbench) from story_data.json."""
import json, os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
data = json.load(open(f"{ROOT}/story_data.json"))
extra = json.load(open(f"{ROOT}/story_extra.json")) if os.path.exists(f"{ROOT}/story_extra.json") else {}
out = sys.argv[1] if len(sys.argv) > 1 else f"{ROOT}/story.html"

HTML = r'''<title>Routine Shift Testbench</title>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,500;9..144,600&family=Source+Sans+3:wght@400;600&family=IBM+Plex+Mono:wght@400;500&display=swap">
<style>
:root{color-scheme:light;
  --paper:#f7f5f0;--panel:#fcfcfb;--ink:#141413;--ink2:#52514e;--muted:#7a776f;--line:#e3ded4;--grid:#ebe7df;
  --shift:#f3d9a0;--return:#cfe8d6;--tip-bg:#141413;--tip-ink:#f7f5f0;
  --s1:#2a78d6;--s2:#eb6834;--s3:#1baf7a;--s4:#eda100;--s5:#e87ba4;--s6:#008300;--s7:#4a3aa7;--s8:#e34948;--sg:#8e8a84;--sv:#4a3aa7;
  --s9:#1791a3;--s10:#b23a86;--s11:#7f8a1e;--s12:#84378a;--s13:#7c4400;--s14:#8659c9;--s15:#2f6f4f;--s16:#a35d00;--good:#1a8a4e;--bad:#c23a3a}
@media (prefers-color-scheme: dark){:root:not([data-theme="light"]){color-scheme:dark;
  --paper:#1a1a19;--panel:#232322;--ink:#f2f1ec;--ink2:#c3c2b7;--muted:#9c9a91;--line:#3a3936;--grid:#2e2d2b;
  --shift:#5c4a24;--return:#2d4a36;--tip-bg:#f2f1ec;--tip-ink:#1a1a19;
  --s1:#3987e5;--s2:#d95926;--s3:#199e70;--s4:#c98500;--s5:#d55181;--s6:#3aa53a;--s7:#9085e9;--s8:#e66767;--sg:#a5a29b;--sv:#9085e9;
  --s9:#26a2b5;--s10:#db5aa9;--s11:#8e9a29;--s12:#ac5db1;--s13:#8e5500;--s14:#a985e0;--s15:#5fae82;--s16:#d98a33;--good:#4cbf7f;--bad:#e2726f}}
:root[data-theme="dark"]{color-scheme:dark;
  --paper:#1a1a19;--panel:#232322;--ink:#f2f1ec;--ink2:#c3c2b7;--muted:#9c9a91;--line:#3a3936;--grid:#2e2d2b;
  --shift:#5c4a24;--return:#2d4a36;--tip-bg:#f2f1ec;--tip-ink:#1a1a19;
  --s1:#3987e5;--s2:#d95926;--s3:#199e70;--s4:#c98500;--s5:#d55181;--s6:#3aa53a;--s7:#9085e9;--s8:#e66767;--sg:#a5a29b;--sv:#9085e9;
  --s9:#26a2b5;--s10:#db5aa9;--s11:#8e9a29;--s12:#ac5db1;--s13:#8e5500;--s14:#a985e0;--s15:#5fae82;--s16:#d98a33;--good:#4cbf7f;--bad:#e2726f}
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
.chip.open .pop{display:block}
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
.calibrow{display:flex;gap:18px;flex-wrap:wrap;align-items:flex-start}
.calibrow>svg{flex:0 0 auto;width:440px;max-width:100%;aspect-ratio:1/1;height:auto}
.calibrow>.tbl{flex:1 1 260px;min-width:230px}
#calib circle{cursor:default}
td.ece{font-weight:600}
@media (max-width:640px){h1{font-size:28px} .controls{gap:6px 12px}}
@media (prefers-reduced-motion:no-preference){.step,.chip{transition:border-color .15s}}
</style>
<div class="wrap">
<h1>Routine Shift Testbench</h1>
<p class="lead">Whether a memory <em>learns</em> a household routine, <em>notices</em> when it breaks, <em>adapts</em> to the new one, copes when the old one returns — and whether it <em>knows</em> any of that about itself.</p>

<div class="panel" id="oneminute" style="margin-block:14px 6px;background:var(--panel);border:1px solid var(--line);border-left:4px solid var(--s3);padding:14px 16px">
  <h3 style="margin-bottom:6px">In one minute</h3>
  <p style="font-size:15.5px;color:var(--ink);max-width:74ch;margin:0 0 10px">A home robot is asked where everyday things are while people are using them, and learns the truth ten minutes later; it settles into a household's routine over two weeks, then one resident is off sick for ten days and their things move, then normal life resumes.</p>
  <p style="font-size:15.5px;color:var(--ink);max-width:74ch;margin:0 0 10px">Simple counting methods learn the routine well and break the moment it changes, and what they do next depends on how much they forget: a short memory re-learns the sick routine and then breaks again when normal life returns, a memory that never forgets stays wrong throughout but is right again immediately, and one that hedges between memory lengths avoids both breaks.</p>
  <p style="font-size:15.5px;color:var(--ink);max-width:74ch;margin:0 0 10px">Five kinds of language-model memory break by about as much, and left to work it out from evidence alone they never really learn the new routine. What looks like recovery is mostly same-day correction: ask about a thing for the first time that day, before the robot has been told where it actually was, and the apparent recovery largely disappears.</p>
  <p style="font-size:15.5px;color:var(--ink);max-width:74ch;margin:0 0 10px">One sentence telling the robot what changed is worth more than a week of evidence to a plain buffer, and it is applied only to the things belonging to the person who is ill. The same sentence costs them when it is never taken back: they keep believing the old story after life returns to normal, and for the memory that looks things up by time of day that cost is still there a week later. The memory that already writes itself a nightly note of its own mistakes gains nothing measurable from being told — it was recording the same thing already.</p>
  <p style="font-size:15.5px;color:var(--ink);max-width:74ch;margin:0 0 10px">None of them knows any of this is happening: whatever the day, all five report themselves about 85% sure while the share they answer correctly falls by a quarter, so a robot deciding when to ask for help cannot tell from its own confidence that the world has changed — the counting methods, for all their simplicity, do better on that score.</p>
  <p style="font-size:15.5px;color:var(--ink2);max-width:74ch;margin:0">Two things did not work and are reported as such: a different disruption, friends over every evening, barely troubles these methods because it only moves things for part of the day; and two findings written up earlier in the night were withdrawn once more households showed them to be noise, which is why every comparison here carries the disagreement between households beside it.</p>
</div>

<div class="panel" id="gist" style="margin-block:6px 18px;border-left:4px solid var(--s1)">
  <h3 style="display:flex;justify-content:space-between;gap:12px;flex-wrap:wrap"><span>What we found</span><span class="muted" style="font-weight:400" id="gistwhen"></span></h3>
  <ul id="gistlist" style="margin:6px 0 2px;padding-left:20px;font-size:14.5px;line-height:1.5"></ul>
</div>

<div class="steps" role="group" aria-label="the story in four steps">
  <button class="step on" data-step="learn"><b>1 · Learn</b><span>Over the first two weeks every learner climbs from ~45% to 80–85%. “Last seen” never learns: it stays at ~50%.</span></button>
  <button class="step" data-step="break"><b>2 · Break</b><span>On the first sick day accuracy falls by 40 points. Things are no longer where the routine puts them.</span></button>
  <button class="step" data-step="relearn"><b>3 · Re-learn</b><span>Methods that forget the past adapt to the sick routine within days; methods that never forget stay stuck.</span></button>
  <button class="step" data-step="return"><b>4 · Break again</b><span>When normal life returns, the adaptive methods break again — and the ones that never forgot are right at once.</span></button>
</div>

<div class="controls">
  <label>households <select id="regime"><option value="household">everyone sick · households 1–10</option><option value="household_rep">everyone sick · households 11–20 (replication)</option><option value="person">one person sick · that person's things</option><option value="person2x">one person sick, twice · that person's things</option></select></label>
  <label>questions <select id="split"><option value="all">all questions</option><option value="moved">only objects that moved since the night round</option></select></label>
  <label><input type="checkbox" id="bands" checked> show ±1 sd across households</label>
  <label><input type="checkbox" id="more"> more methods</label>
</div>

<div class="legend" id="legend"></div>

<h2>Accuracy — is the answer right?</h2>
<div class="chart-wrap"><svg id="main" viewBox="0 0 1000 380" role="img" aria-label="accuracy per day"></svg><div class="tip" id="tip"></div></div>
<p class="note" id="mainnote"></p>

<h2>Confidence — what does it claim?</h2>
<p>The same lines, but plotting each method's own stated confidence in its answer instead of whether the answer was right: the top probability in its distribution over places. Toggle a method in the legend above and watch this chart and the accuracy one together — a confidence line that ignores the break in the chart above is a method that does not know it is wrong. (The two “honest sets” methods are not shown here or in the accuracy chart: they pick the never-forgets timetable's own answer, so their accuracy line would sit exactly on top of it — see “Does the method notice?” below for what they actually add, a set size and coverage.)</p>
<div class="chart-wrap"><svg id="confmain" viewBox="0 0 1000 380" role="img" aria-label="claimed confidence per day"></svg><div class="tip" id="conftip"></div></div>
<p class="note" id="confnote"></p>

<h2>Calibration — is the confidence honest, day by day?</h2>
<p>The gap, in percentage points: mean stated confidence minus accuracy, one line per method per day, pooled over households (±1 sd across households). A flat line near zero through the shift is a method whose confidence can be trusted for deciding where to look; a jump <em>up</em> at day 14 is confident-and-wrong; a line sitting below zero throughout is underconfident by definition, not by tracking.</p>
<p>Two readings, because a method can be honest about <em>level</em> without being honest about <em>tracking</em>, or the other way round. <b>As stated</b> is the method's own number. <b>Lead-day calibrated</b> fits a monotone translation from stated confidence to observed accuracy using only the lead-up days (1–13), then applies that same translation everywhere — including back onto the lead-up itself, where the gap should now sit near zero by construction. What is left after that translation, especially on days 14–16 and 24–26, is the real signal: does the method's sense of its own accuracy keep up when the routine breaks, or does the translation that worked all lead-up stop working the moment the routine does?</p>
<div class="controls" style="position:static;border:0;padding-block:0 10px">
  <label>households <select id="gapreg"><option value="household">everyone sick · households 1–10</option><option value="person">one person sick · that person's things</option><option value="partial">one person sick · everyone's things asked</option><option value="person2x">one person sick, twice</option></select></label>
  <label>confidence <select id="gapmode"><option value="raw">as stated</option><option value="leadcal">lead-day calibrated</option></select></label>
</div>
<div class="chart-wrap"><svg id="gap" viewBox="0 0 1000 320" role="img" aria-label="calibration gap per day"></svg><div class="tip" id="gaptip"></div></div>
<p class="note" id="gapnote"></p>
<div class="tbl"><table id="gaptable"></table></div>
<div class="small" id="gapconformal"></div>
<p class="note" id="gapconfnote"></p>
<h3 style="margin-top:18px">LLM arms — an answer-or-ask gate on their own stated confidence</h3>
<p class="note">Adaptive-conformal control (Gibbs &amp; Candès-style decaying step, same machinery as the honest-sets agents, retargeted at a yes/no gate instead of a set size): ask the resident instead of answering whenever the stated confidence falls below a bar that adjusts itself after every question, aiming for a 10% miss rate among the questions it DOES answer. Post-hoc on the saved logs, no new LLM calls. "Miss rate" below is only over answered questions (asking is always right, by construction — the resident knows). A gate that "tightens at the shift" raises its bar right at day 14, without being told to.</p>
<div class="tbl"><table id="askgatetable"></table></div>
<p class="note" id="askgatenote"></p>
<h3 style="margin-top:18px">LLM arms — three ways of reading its confidence, and honest sets on its own answer</h3>
<p class="note">On a bounded list of days (13 · 14 · 15 · 20 · 24 · 25 · 30 — the end of the lead-up, the shift, mid-spell, the return), three households, every question asked three ways: the plain answer with its stated confidence (<b>verbalized</b>); five answers at temperature 0.7, confidence = the share that agree with the plain one (<b>agreement</b>); and the same question as a multiple choice over the nine most likely places plus "somewhere else", confidence = the probability the model puts on the letter it picks (<b>token probability</b>, KnowNo-style). The <b>honest set</b> is built on those letter probabilities the same way as the classical honest-sets agents (online conformal, 90% target): coverage is the share of questions whose truth was in the set, size the average number of options named (out of 10). First ~20 questions are the conformal warm-up, so day 13's set is not yet meaningful. No new calls beyond this bounded list.</p>
<div class="tbl"><table id="knownotable"></table></div>
<p class="note" id="knownonote"></p>
<p class="note" style="margin-top:10px"><b>Why the counters read as underconfident even when they are usually right.</b> A timetable's probability is spread over every place it has ever seen the object at that time of day — often close to 38 candidate spots for a small object — with a smoothing floor that keeps every place above zero. On the lead-up days the 3-day timetable is right about 73% of the time, but its own top probability at answer time averages only about 41%: it is not being modest, 41% is genuinely the mixture's mass on its best guess given how many places share the rest. The lead-day calibration above learns that translation and removes it, so what is left is tracking, not level.<br><b>Why the honest sets read as underconfident too.</b> 1 divided by the set size answers "if I pointed at one member of this set at random, how likely is it right" — not "is the truth in the set." A 3-place set states 33% that way while containing the truth 9 times in 10 by design. That is a different question from calibration, so the honest-sets methods are shown below as coverage against their 90% target and set size, not as a confidence gap.</p>
<details style="margin-top:14px">
<summary style="cursor:pointer;color:var(--ink2);font-size:13.5px">Aggregate reliability diagram (claimed confidence vs. actual accuracy, pooled over all days of a stage — superseded above by the per-day gap for most purposes, kept here for the bin-level picture)</summary>
<p style="margin-top:8px">Every question, sorted into five bins by the confidence the method stated, then: on the horizontal axis, the average confidence claimed inside that bin; on the vertical axis, the share of those questions actually answered right. A method whose confidence means what it says sits on the diagonal — above it, the method is <em>underconfident</em> (righter than it claims); below, <em>overconfident</em> (wrong more often than it admits). Point size is the share of all questions that landed in that bin. ECE (expected calibration error) is the size-weighted average gap from the diagonal, in points.</p>
<div class="controls" style="position:static;border:0;padding-block:0 10px">
  <label>over <select id="calibstage"><option value="any">every day</option><option value="lead">the lead-up only</option><option value="sick">the sick spell only</option><option value="return">the return only</option></select></label>
</div>
<div class="chart-wrap"><div class="calibrow"><svg id="calib" viewBox="0 0 440 440" role="img" aria-label="claimed confidence vs actual accuracy"></svg><div class="tbl"><table id="calibtable"></table></div></div></div>
<p class="note" id="calibnote"></p>
</details>

<h2>Does the method notice?</h2>
<p>Getting the answer wrong is one thing; knowing that you are probably wrong is another. Three ways of noticing, all sitting on the same “timetable” learner.</p>
<div class="small" id="small"></div>

<h2>By stage</h2>
<p>Mean accuracy over each stage, ± the spread across households (one number per household, then the standard deviation). The bands here show how much households disagree, which is a different question from whether an average difference is real — for that, see the paired contrasts in "What we found" above, where a difference is claimed when the average is at least twice its own standard error.</p>
<div class="tbl"><table id="stagetable"></table></div>

<h2>Remembering versus adapting</h2>
<p>The return is where memory policy shows. A learner that forgets quickly adapts to the sick routine but breaks again when life returns to normal; one that never forgets stays wrong through the spell but is right at once afterwards. How much each costs depends on how long the new routine lasts. Each panel is one spell length; each row a memory length of the timetable learner (stage means ± spread across households).</p>
<div class="small" id="sweep"></div>
<p class="note" id="sweepnote"></p>

<h2>Whose routine changed?</h2>
<p>Only one resident is off sick; questions are asked about everyone's things. A method that keeps a separate record for every object cannot possibly mix the two people up — that is a property of its design, not something it figured out, so it is shown once below as a control. The real question is for methods that keep one shared piece of state for the whole household: when the sick person's things force that shared state to move, does it also move for the things of the person whose routine never changed?</p>
<div class="small" id="affected"></div>
<p class="note" id="affnote"></p>

<h2>What it costs the planner</h2>
<p>A guess is only useful if it saves searching. Post-hoc simulation from each method's own distribution: the robot searches places in order of probability until it finds the object, or — when its confidence is low — asks the resident at a fixed cost instead. Numbers from the research roster (households 1–10, household regime).</p>
<div class="panel" id="planning"></div>

<h2>The methods, in plain words</h2>
<div class="gloss" id="gloss"></div>
<p class="note" style="margin-top:14px">Regime: 32 days from a Monday; the walkthrough is day 0; days 1–13 are the lead-up, 14–23 the sick spell, 24–31 the return. The robot does one round at 03:00 and, ten minutes after every question, learns where the object actually was (“found-it feedback”). Questions are asked while the object is in use, about the everyday things the sick routine moves: book, water bottle, tablet, mug, charger, glasses, glass, razor — at most one question per object per half hour, 12–24 a day. No language-model method is in this loop. Confidence and calibration cost nothing extra to show: every method already stated a number for how sure it was on every question, in the same logs the accuracy chart is built from — nothing here was re-run.</p>
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
 {k:"tt1d", name:"timetable, 1-day memory", v:"--s8", core:false, gloss:"The timetable with a one-day half-life.", how:"Adapts fastest and shows the largest second break — and states the least honest confidence of any method here (calibration error 49 points): a single day's counts swing its stated probability to near-certainty long before its accuracy has caught up."},
 {k:"mf1d", name:"most frequent place, 1-day memory", v:"--s9", core:false, gloss:"Most-frequent place with a one-day half-life — ignores time of day, remembers only yesterday.", how:"Reacts fastest of the most-frequent family; plateaus lowest in the lead-up but shows the quickest re-learning and second break."},
 {k:"bmaobj", name:"hedge, per object", v:"--s11", core:false, gloss:"The same hedge over memory lengths, but with a separate trust vector for every object instead of one shared vector for the household.", how:"Gains a few points over the shared-vector hedge in the sick spell on objects seen often enough to move their own weights — but most objects are seen only once or twice a day, too rarely for their own weights to shift much inside a ten-day spell, so most of the gain is left on the table."},
 {k:"detectorfrozen", name:"never-forgets timetable + change alarm", v:"--s12", core:false, gloss:"The never-forgets timetable plus the same watchdog as the 3-day version: instead of a short memory forgetting on its own, the watchdog wipes most of the diary the moment it decides the routine has changed.", how:"Sounds on the first sick day even more reliably than the 3-day version (it has no natural forgetting of its own to blur the signal) — but rarely sounds again on the return: the wipe already adapted it to the sick routine, so by the time normal life comes back its recent memory is the sick spell, not the 14 lead days, and the return does not surprise it the same way."},
];
const STEP_LINES = {learn:["tt3d","ttfrozen","lastseen"], break:["tt3d","ttfrozen","mf3d","lastseen"], relearn:["tt3d","ttfrozen","detector3d","bma"], return:["tt3d","ttfrozen","detector3d","bma","lastseen"]};
const STEP_NOTE = {learn:"Lead-up (days 1–13): the timetables climb from ~45% to 80–85% as their diaries fill; last seen stays flat.",
 break:"First sick day (day 14): every learner drops by roughly 40 points — that is the size of the routine change, ~4 standard deviations across households. Most-frequent falls furthest.",
 relearn:"Inside the spell (days 14–23): the 3-day timetable is back near 85–90% within a week; the never-forgets timetable crawls; the change alarm's wipe makes the re-learning faster still; the hedge follows the short memories.",
 return:"Return (days 24–31): the adaptive methods break again (down to 55–60% and re-learn); the never-forgets timetable is right immediately; the hedge moves its trust back to it and shows no second break."};
const css = v => getComputedStyle(document.documentElement).getPropertyValue(v).trim();
const state = {regime:"household", split:"all", bands:true, more:false, on:new Set(STEP_LINES.learn), step:"learn", calibStage:"any", gapReg:"household", gapMode:"raw"};
const GAP_EXTRA_SERIES = [
 {k:"bma_person", name:"hedge over memory lengths", v:"--s14", gloss:"The hedge over memory lengths, run with a separate trust vector per resident instead of one shared vector — only meaningful when just one resident's routine actually shifts.", how:"Shown only under the “one person sick · everyone's things asked” population in the calibration-gap panel."},
 {k:"detector3d_person", name:"3-day timetable + change alarm", v:"--s15", gloss:"The change-alarm timetable with a separate diary and alarm per resident.", how:"Shown only under the “one person sick · everyone's things asked” population in the calibration-gap panel."},
 {k:"oracle72", name:"never-forgets timetable + told when", v:"--s16", gloss:"The change-alarm timetable's base, but instead of a watchdog deciding when to wipe the diary, it is simply told the day the routine changed and wipes on cue — an upper bound on what the watchdog could do with a perfect detector.", how:"Identical to the plain change-alarm agent on the lead days (nothing has been told yet); differs from day 14."},
];
function gapSeriesInfo(k){ return SERIES.find(s=>s.k===k) || GAP_EXTRA_SERIES.find(s=>s.k===k); }
const GAP_COMPANION = {bma:["bma_person"], detector3d:["detector3d_person","oracle72"]};
const GAP_STAGES_DEFAULT = [{name:"lead",a:1,b:13},{name:"sick",a:14,b:23},{name:"return",a:24,b:31}];
function gapStages(reg){ return (DATA[reg] && DATA[reg].stages) ? stagesOf(reg) : GAP_STAGES_DEFAULT; }
const $ = s => document.querySelector(s);
const MIN_N = 10;   // a day (or window) needs at least this many pooled answers before a number is drawn or printed

function daily(reg, key, split){ // -> {mean:[day->%], sd:[day->%], n:[..]} across households
  const R = DATA[reg]; const A = R.agents[key]; if(!A) return null;
  const nd = R.days; const mean=[], sd=[], nn=[];
  for(let d=1; d<nd; d++){ const vals=[]; let N=0;
    for(const hh of Object.keys(A)){ const [n,ok]=A[hh][split][d]; if(n>=3){ vals.push(100*ok/n); N+=n; } }
    if(!vals.length){mean.push(null); sd.push(null); nn.push(0); continue}
    const m = vals.reduce((a,b)=>a+b,0)/vals.length; const s = vals.length>1? Math.sqrt(vals.reduce((a,b)=>a+(b-m)**2,0)/(vals.length-1)) : 0;
    if(N<MIN_N){ mean.push(null); sd.push(null); nn.push(N); continue; }   // thin tail of an in-progress arm: keep n for the tooltip, draw nothing
    mean.push(m); sd.push(s); nn.push(N);
  } return {mean, sd, n:nn};
}
function dailyConf(reg, key, split){ // -> {mean:[day->claimed %], sd, n} across households, from sum_conf/n per household
  const R = DATA[reg]; const A = R.agents[key]; if(!A) return null;
  const nd = R.days; const mean=[], sd=[], nn=[];
  for(let d=1; d<nd; d++){ const vals=[]; let N=0;
    for(const hh of Object.keys(A)){ const [n,ok,sc]=A[hh][split][d]; if(n>=3){ vals.push(100*sc/n); N+=n; } }
    if(!vals.length){mean.push(null); sd.push(null); nn.push(0); continue}
    const m = vals.reduce((a,b)=>a+b,0)/vals.length; const s = vals.length>1? Math.sqrt(vals.reduce((a,b)=>a+(b-m)**2,0)/(vals.length-1)) : 0;
    if(N<MIN_N){ mean.push(null); sd.push(null); nn.push(N); continue; }   // thin tail of an in-progress arm: keep n for the tooltip, draw nothing
    mean.push(m); sd.push(s); nn.push(N);
  } return {mean, sd, n:nn};
}
function calibBins(reg, key, split, stage){ const C=DATA[reg].calib && DATA[reg].calib[key]; if(!C) return null; const Csp=C[split]||C["all"]; if(!Csp) return null; return Csp[stage]||null; }
function eceOf(bins){ if(!bins) return null; let nTot=0; for(const b of bins) nTot+=b[0]; if(!nTot) return null;
  let e=0; for(const [n,ok,sc] of bins){ if(!n) continue; e += (n/nTot)*Math.abs(ok/n - sc/n); } return {ece:100*e, n:nTot}; }
function pooled(reg, key, split, days){ const A=DATA[reg].agents[key]; if(!A) return null; let n=0,ok=0; for(const hh of Object.keys(A)) for(const d of days){ n+=A[hh][split][d][0]; ok+=A[hh][split][d][1]; } return n? 100*ok/n : null; }
function hhStage(reg, key, split, days){ const A=DATA[reg].agents[key]; if(!A) return null; const vals=[]; for(const hh of Object.keys(A)){ let n=0,ok=0; for(const d of days){ n+=A[hh][split][d][0]; ok+=A[hh][split][d][1]; } if(n) vals.push(100*ok/n);} const m=vals.reduce((a,b)=>a+b,0)/vals.length; const s=vals.length>1?Math.sqrt(vals.reduce((a,b)=>a+(b-m)**2,0)/(vals.length-1)):0; return {m,s,k:vals.length}; }
function stagesOf(reg){ const R=DATA[reg]; const out=[]; let cur=null; for(let d=1; d<R.days; d++){ const st=R.stages[String(d)]||"plain"; if(!cur||cur.name!==st){ cur={name:st,a:d,b:d}; out.push(cur);} else cur.b=d; } return out; }
const STAGE_LABEL = {lead:"lead-up (normal routine)", sick:"sick spell", return:"return to normal", sick2:"sick again", return2:"back again"};
const STAGE_FILL = {sick:"--shift", return:"--return", sick2:"--shift", return2:"--return"};

function renderLegend(){
  const L=$("#legend"); L.innerHTML="";
  for(const s of SERIES){ if(!s.core && !state.more) continue; if(!DATA[state.regime].agents[s.k]) continue;
    const chip=document.createElement("label"); chip.className="chip"; chip.innerHTML=`<input type="checkbox" ${state.on.has(s.k)?"checked":""} aria-label="${s.name}"><i class="sw" style="background:var(${s.v})"></i>${s.name}<span class="q" tabindex="0" aria-label="what is ${s.name}">?</span><div class="pop" role="tooltip"><b>${s.name}</b>${s.gloss}<div class="how">On this testbench: ${s.how}</div></div>`;
    chip.querySelector("input").addEventListener("change", e=>{ if(e.target.checked) state.on.add(s.k); else state.on.delete(s.k); draw(); });
    const toggleChip = e=>{ e.preventDefault(); e.stopPropagation(); const wasOpen=chip.classList.contains("open"); closeAllPops(); if(!wasOpen) chip.classList.add("open"); };
    chip.querySelector(".q").addEventListener("click", toggleChip);
    chip.querySelector(".q").addEventListener("keydown", e=>{ if(e.key==="Enter"||e.key===" ") toggleChip(e); });
    L.appendChild(chip); }
}

function renderLine(svgId, xhId, dataFn, labelSuffix){
  // shared renderer for the two per-day line charts (accuracy, confidence): stage bands, gridlines, day ticks,
  // one line + optional ±1sd band per selected method, end-of-line labels, a hidden crosshair the hover fills in.
  const reg=state.regime, R=DATA[reg], nd=R.days, W=1000,H=380,L=44,Rt=215,T=22,B=40;
  const x=d=>L+(d-1)*(W-L-Rt)/(nd-2), y=v=>T+(100-v)*(H-T-B)/100;
  const svg=$(svgId); let g="";
  for(const st of stagesOf(reg)){ const f=STAGE_FILL[st.name]; if(f) g+=`<rect x="${(x(st.a)-8).toFixed(1)}" y="${T}" width="${(x(st.b)-x(st.a)+16).toFixed(1)}" height="${H-T-B}" fill="var(${f})" opacity="0.5"/>`;
    g+=`<text class="stg" x="${((x(st.a)+x(st.b))/2).toFixed(1)}" y="${T-7}" text-anchor="middle">${STAGE_LABEL[st.name]||st.name}</text>`; }
  for(const v of [0,25,50,75,100]) g+=`<line class="grid" x1="${L}" x2="${W-Rt}" y1="${y(v).toFixed(1)}" y2="${y(v).toFixed(1)}"/><text x="${L-8}" y="${(y(v)+4).toFixed(1)}" text-anchor="end">${v}%</text>`;
  for(let d=1; d<nd; d++){ if(d%2===1) g+=`<text x="${x(d).toFixed(1)}" y="${H-B+16}" text-anchor="middle">${d}</text>`; }
  g+=`<text x="${((L+W-Rt)/2).toFixed(1)}" y="${H-6}" text-anchor="middle" class="lbl">day (weekday routine throughout; day 0 = walkthrough)</text>`;
  const shown=SERIES.filter(s=>state.on.has(s.k)&&DATA[reg].agents[s.k]); const ends=[];
  for(const s of shown){ const D=dataFn(reg,s.k,state.split); if(!D) continue; const col=`var(${s.v})`;
    if(state.bands){ const up=[],lo=[]; D.mean.forEach((m,i)=>{ if(m==null) return; up.push(`${x(i+1).toFixed(1)},${y(Math.min(100,m+D.sd[i])).toFixed(1)}`); lo.unshift(`${x(i+1).toFixed(1)},${y(Math.max(0,m-D.sd[i])).toFixed(1)}`); }); if(up.length>1) g+=`<polygon points="${up.join(" ")} ${lo.join(" ")}" fill="${col}" opacity="0.12"/>`; }
    const pts=[]; D.mean.forEach((m,i)=>{ if(m!=null) pts.push(`${x(i+1).toFixed(1)},${y(m).toFixed(1)}`); });
    g+=`<polyline fill="none" stroke="${col}" stroke-width="${s.dash?1.8:2.2}" stroke-linejoin="round" ${s.dash?'stroke-dasharray="6 4"':""} points="${pts.join(" ")}"/>`;
    const last=D.mean.map((m,i)=>[m,i]).filter(a=>a[0]!=null).pop(); if(last) ends.push({s,col,yy:y(last[0]),v:last[0]}); }
  ends.sort((a,b)=>a.yy-b.yy); let prev=-99; for(const e of ends){ let yy=Math.max(e.yy, prev+14); prev=yy; g+=`<circle cx="${(W-Rt).toFixed(1)}" cy="${e.yy.toFixed(1)}" r="3.5" fill="${e.col}"/><text class="lbl" x="${W-Rt+8}" y="${(yy+4).toFixed(1)}" style="fill:var(--ink)">${e.s.name} · ${e.v.toFixed(0)}%${labelSuffix||""}${e.s.progress?" "+e.s.progress:""}</text>`; }
  g+=`<line id="${xhId}" class="axis" x1="0" x2="0" y1="${T}" y2="${H-B}" style="display:none"/>`;
  svg.innerHTML=g; svg.dataset.geom=JSON.stringify({L,Rt,W,nd});
}
function lineHover(ev, svgId, tipId, xhId, dataFn){
  const svg=$(svgId); const geom=JSON.parse(svg.dataset.geom||"null"); if(!geom) return; const rect=svg.getBoundingClientRect(); const px=(ev.clientX-rect.left)*geom.W/rect.width;
  const d=Math.round((px-geom.L)/((geom.W-geom.L-geom.Rt)/(geom.nd-2)))+1; if(d<1||d>=geom.nd){ $(tipId).style.display="none"; $(xhId).style.display="none"; return; }
  const xx=geom.L+(d-1)*(geom.W-geom.L-geom.Rt)/(geom.nd-2); const xh=$(xhId); xh.setAttribute("x1",xx); xh.setAttribute("x2",xx); xh.style.display="";
  const R=DATA[state.regime]; const st=R.stages[String(d)]||"plain"; const i0=DAYNAMES.indexOf(R.day0);
  let rows=`<div style="margin-bottom:4px"><b>day ${d}</b> · ${DAYNAMES[(i0+d)%7]} · ${STAGE_LABEL[st]||st}</div>`;
  for(const s of SERIES){ if(!state.on.has(s.k)) continue; const D=dataFn(state.regime,s.k,state.split); if(!D) continue;
    if(D.mean[d-1]==null){ if(D.n[d-1]>0) rows+=`<div class="r"><span><i style="background:var(${s.v})"></i>${s.name}</span><span class="muted">(n=${D.n[d-1]}, too few)</span></div>`; continue; }
    rows+=`<div class="r"><span><i style="background:var(${s.v})"></i>${s.name}</span><span>${D.mean[d-1].toFixed(0)}% ±${D.sd[d-1].toFixed(0)}</span></div>`; }
  const tip=$(tipId); tip.innerHTML=rows; tip.style.display="block"; const wrap=svg.parentElement.getBoundingClientRect(); let lx=ev.clientX-wrap.left+14; if(lx+230>wrap.width) lx=ev.clientX-wrap.left-240; tip.style.left=lx+"px"; tip.style.top=(ev.clientY-wrap.top+12)+"px";
}
function draw(){
  renderLine("#main","#xh",daily);
  $("#mainnote").textContent = STEP_NOTE[state.step] + (state.split==="moved" ? " (Showing only the questions whose object had moved since the 03:00 round — the half where learning matters; 'last seen' is right on the other half almost by definition.)" : "");
  renderLine("#confmain","#confxh",dailyConf," claimed");
  $("#confnote").textContent = "Claimed confidence, same households and split as the accuracy chart above. Compare a line's shape here with its shape there: a confidence line that stays roughly flat while its accuracy line dives (the frozen timetable's does) is not tracking its own mistakes." + (state.split==="moved" ? " (Only the questions whose object had moved.)" : "");
  drawCalib();
  renderGap(); renderGapConformal(); renderAskgate(); renderKnowno();
  renderSmall(); renderTable();
}
function hover(ev){ lineHover(ev,"#main","#tip","#xh",daily); }
function hoverConf(ev){ lineHover(ev,"#confmain","#conftip","#confxh",dailyConf); }
function drawCalib(){
  const reg=state.regime, R=DATA[reg]; const svg=$("#calib");
  if(!R.calib || !Object.keys(R.calib).length){ svg.innerHTML=""; $("#calibtable").innerHTML=""; $("#calibnote").textContent="Calibration was logged on the two frozen regimes (households 1–10, and the one-person regime); this replication set has accuracy only."; return; }
  const W=440,H=440,L=40,Rr=14,T=12,B=32;
  const px=v=>L+(v/100)*(W-L-Rr), py=v=>T+(1-v/100)*(H-T-B);
  let g="";
  for(const v of [0,25,50,75,100]){ g+=`<line class="grid" x1="${L}" x2="${W-Rr}" y1="${py(v).toFixed(1)}" y2="${py(v).toFixed(1)}"/><line class="grid" x1="${px(v).toFixed(1)}" x2="${px(v).toFixed(1)}" y1="${T}" y2="${H-B}"/><text x="${L-6}" y="${(py(v)+4).toFixed(1)}" text-anchor="end">${v}</text><text x="${px(v).toFixed(1)}" y="${H-B+14}" text-anchor="middle">${v}</text>`; }
  g+=`<line x1="${px(0).toFixed(1)}" y1="${py(0).toFixed(1)}" x2="${px(100).toFixed(1)}" y2="${py(100).toFixed(1)}" stroke="var(--muted)" stroke-dasharray="3 3" stroke-width="1.3"/>`;
  g+=`<text class="lbl" x="${((L+W-Rr)/2).toFixed(1)}" y="${H-4}" text-anchor="middle">confidence claimed</text>`;
  g+=`<text class="lbl" text-anchor="middle" transform="translate(11,${(T+(H-T-B)/2).toFixed(1)}) rotate(-90)">accuracy actually seen</text>`;
  const rows=[]; const shown=SERIES.filter(s=>state.on.has(s.k)&&DATA[reg].agents[s.k]);
  for(const s of shown){ const bins=calibBins(reg,s.k,state.split,state.calibStage); if(!bins) continue;
    let nTot=0; for(const b of bins) nTot+=b[0]; if(!nTot) continue;
    const pts=[]; let dots="";
    bins.forEach((b,i)=>{ const [n,ok,sc]=b; if(n<5) return; const cx=100*sc/n, cy=100*ok/n, share=n/nTot, r=3+13*Math.sqrt(share);
      pts.push(`${px(cx).toFixed(1)},${py(cy).toFixed(1)}`);
      dots+=`<circle cx="${px(cx).toFixed(1)}" cy="${py(cy).toFixed(1)}" r="${r.toFixed(1)}" fill="var(${s.v})" fill-opacity="0.85" stroke="var(--panel)" stroke-width="1"><title>${s.name}\nstated confidence ${i*20}–${i*20+20}%: claimed ${cx.toFixed(0)}%, actually right ${cy.toFixed(0)}% of the time (${n} questions, ${(100*share).toFixed(0)}% of its answers)</title></circle>`; });
    if(pts.length>1) g+=`<polyline fill="none" stroke="var(${s.v})" stroke-width="1.6" points="${pts.join(" ")}"/>`;
    g+=dots; const E=eceOf(bins); if(E) rows.push({s,E}); }
  svg.innerHTML=g;
  rows.sort((a,b)=>a.E.ece-b.E.ece);
  let th=`<thead><tr><th>method</th><th class="num">ECE</th></tr></thead><tbody>`;
  for(const {s,E} of rows) th+=`<tr><td><i class="swatch" style="background:var(${s.v})"></i>${s.name}</td><td class="num ece" style="color:${E.ece<12?"var(--good)":E.ece>28?"var(--bad)":"inherit"}">${E.ece.toFixed(0)} pp</td></tr>`;
  $("#calibtable").innerHTML = rows.length? th+"</tbody>" : "<tr><td>No method selected in the legend above has calibration data for this regime.</td></tr>";
  const stageTxt = {any:"every day", lead:"the lead-up only", sick:"the sick spell only", return:"the return only"}[state.calibStage];
  $("#calibnote").textContent = `Over ${stageTxt}${state.split==="moved"?", objects that had moved since the night round only":""}, pooled across all ${R.hh.length} households. Above the diagonal: underconfident (righter than claimed). Below: overconfident. ECE (expected calibration error) is the size-weighted average distance from the diagonal, in percentage points — lower is more honest. (The “honest sets” methods aren't in this list — they state a set size, not a point guess; their calibration target is 90% coverage, shown in “Does the method notice?” below, not this diagonal.)`;
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
  <div class="g"><b>Honest sets (online conformal prediction)</b>Rather than one guess, name enough places that the truth is inside about 9 times in 10, and keep adjusting the bar from the robot's own hit rate — two variants shown throughout: a 2024 version whose bar nudges up or down after each answer, with the nudge shrinking over time, and a 2023 version that instead takes the size straight from the last 24 hours of evidence, weighting the newest most, so it reacts to a shift immediately rather than catching up over several days. Both run on top of the never-forgets timetable and pick that same timetable's single best guess as their point answer — they name a set of places <em>around</em> that answer, they do not change it, so their accuracy is exactly the never-forgets timetable's own accuracy. For that reason they are not shown as separate lines in the accuracy or confidence-per-day charts above (they would draw exactly on top of it); they appear instead only in "Does the method notice?" and the calibration-gap panel, as coverage against the 90% target and set size. When the routine breaks, the sets grow — the method is saying "I am no longer sure" in a way that can be checked.</div>
  <div class="g"><b>Hedge over memory lengths (Bayesian model averaging)</b>Keep several versions of the learner with different memory lengths and let recent performance decide how much to trust each. Adapts without being told, but also cancels the second break — a trade-off, not a free lunch.</div>
  <div class="g"><b>Calibration (reliability diagram, ECE)</b>Sort every answer into bins by the confidence the method stated for it, then compare the bin's average claimed confidence with the share of that bin actually answered right. A perfectly honest method sits on the diagonal in every bin. Expected calibration error (ECE) weights each bin's gap from the diagonal by how many questions landed in it and averages the result — a single number in percentage points, the lower the more honest.</div>`; }

function closeAllPops(){ document.querySelectorAll(".chip.open").forEach(c=>c.classList.remove("open")); }
document.addEventListener("click", e=>{ if(!e.target.closest(".pop")) closeAllPops(); });
document.addEventListener("keydown", e=>{ if(e.key==="Escape") closeAllPops(); });
document.querySelectorAll(".step").forEach(b=>b.addEventListener("click",()=>{ document.querySelectorAll(".step").forEach(x=>x.classList.remove("on")); b.classList.add("on"); state.step=b.dataset.step; state.on=new Set(STEP_LINES[state.step]); renderLegend(); draw(); }));
$("#regime").addEventListener("change",e=>{ state.regime=e.target.value; renderLegend(); draw(); });
$("#split").addEventListener("change",e=>{ state.split=e.target.value; draw(); });
$("#bands").addEventListener("change",e=>{ state.bands=e.target.checked; draw(); });
$("#more").addEventListener("change",e=>{ state.more=e.target.checked; renderLegend(); draw(); });
$("#main").addEventListener("mousemove",hover); $("#main").addEventListener("mouseleave",()=>{ $("#tip").style.display="none"; const xh=$("#xh"); if(xh) xh.style.display="none"; });
$("#confmain").addEventListener("mousemove",hoverConf); $("#confmain").addEventListener("mouseleave",()=>{ $("#conftip").style.display="none"; const xh=$("#confxh"); if(xh) xh.style.display="none"; });
$("#calibstage").addEventListener("change",e=>{ state.calibStage=e.target.value; drawCalib(); });
$("#gapreg").addEventListener("change",e=>{ state.gapReg=e.target.value; renderGap(); renderGapConformal(); renderAskgate(); renderKnowno(); });
$("#gapmode").addEventListener("change",e=>{ state.gapMode=e.target.value; renderGap(); });
$("#gap").addEventListener("mousemove",hoverGap); $("#gap").addEventListener("mouseleave",()=>{ $("#gaptip").style.display="none"; const xh=$("#gapxh"); if(xh) xh.style.display="none"; });
try{ const saved=localStorage.getItem("rst-regime"); if(saved && DATA[saved]) { state.regime=saved; $("#regime").value=saved; } }catch(e){}
$("#regime").addEventListener("change",e=>{ try{ localStorage.setItem("rst-regime", e.target.value); }catch(err){} });
const EXTRA = /*EXTRA*/null;
const MEM = [["timetable_hl1d","1 day"],["timetable_hl3d","3 days"],["timetable_hl7d","7 days"],["timetable","never forgets"]];
function renderSweep(){
  const host=$("#sweep"); if(!EXTRA||!EXTRA.sweep){ host.innerHTML=""; return; } host.innerHTML="";
  const order=[["5","5-day spell"],["10","10-day spell"],["20","20-day spell"],["natural10","10-day spell, natural calendar (weekends + random events)"]];
  for(const [key,title] of order){ const S=EXTRA.sweep[key]; if(!S) continue;
    const W=440,H=190,L=110,T=16,B=26,Rr=14; const x=v=>L+v*(W-L-Rr)/100; const rowH=(H-T-B)/MEM.length;
    let g=""; for(const v of [0,25,50,75,100]) g+=`<line class="grid" x1="${x(v).toFixed(1)}" x2="${x(v).toFixed(1)}" y1="${T}" y2="${H-B}"/><text x="${x(v).toFixed(1)}" y="${H-B+14}" text-anchor="middle">${v}%</text>`;
    MEM.forEach(([ag,name],i)=>{ const v=S[ag]; if(!v) return; const yy=T+i*rowH+rowH/2;
      g+=`<text x="${L-8}" y="${(yy+4).toFixed(1)}" text-anchor="end" class="lbl">${name}</text>`;
      // sick-stage accuracy (bar) and return accuracy (dot) relative to lead (tick)
      g+=`<rect x="${x(0)}" y="${(yy-6).toFixed(1)}" width="${(x(v.sick[0])-x(0)).toFixed(1)}" height="12" rx="3" fill="var(--shift)"><title>${name}: during the spell ${v.sick[0].toFixed(0)}% ± ${v.sick[1].toFixed(0)}</title></rect>`;
      g+=`<line x1="${x(Math.max(0,v.sick[0]-v.sick[1])).toFixed(1)}" x2="${x(Math.min(100,v.sick[0]+v.sick[1])).toFixed(1)}" y1="${yy.toFixed(1)}" y2="${yy.toFixed(1)}" stroke="var(--ink2)" stroke-width="1.5"/>`;
      g+=`<line x1="${x(v.lead[0]).toFixed(1)}" x2="${x(v.lead[0]).toFixed(1)}" y1="${(yy-9).toFixed(1)}" y2="${(yy+9).toFixed(1)}" stroke="var(--ink)" stroke-width="2"><title>lead-up level ${v.lead[0].toFixed(0)}%</title></line>`;
      g+=`<circle cx="${x(v.ret[0]).toFixed(1)}" cy="${yy.toFixed(1)}" r="5" fill="var(--return)" stroke="var(--ink2)"><title>${name}: after the return ${v.ret[0].toFixed(0)}% ± ${v.ret[1].toFixed(0)} (first return day: ${v.back>0?"+":""}${v.back.toFixed(0)} points)</title></circle>`; });
    host.innerHTML+=`<div class="panel"><h3>${title}</h3><p>Bar: accuracy during the spell · dot: after the return · tick: lead-up level. Hover for numbers. First-day drop on the return: ${MEM.map(([ag,n])=>S[ag]?`${n} ${S[ag].back>0?"+":""}${S[ag].back.toFixed(0)}`:"").filter(Boolean).join(" · ")}.</p><svg viewBox="0 0 ${W} ${H}" role="img" aria-label="${title}">${g}</svg></div>`; }
  $("#sweepnote").textContent="Reading: the longer the memory, the worse the spell and the better the return; the longer the spell, the more even a long memory is re-taught (7 days: return drop −10 → −17 as the spell goes from 5 to 10 days). The never-forgets learner wins the return only while the lead-up outweighs the spell. With the natural calendar (weekends and random events in every stage) the same pattern holds, a few points smaller.";
}
function pairSentence(p){
  // plain-language read of one paired-change number: which side moved more, by how much, in how many households
  const a=p.affected_change.mean, u=p.unaffected_change.mean, g=p.gap.mean, n=p.n_clear, N=p.n_total;
  if(g>=p.gap_bar) return `the sick person's things got ${g.toFixed(0)} points worse than everyone else's here (${n} of ${N} households) — everyone else's held steady.`;
  if(a>0 && g<0) return `the sick person's things got ${a.toFixed(0)} points EASIER to answer here, not harder — everyone else's barely moved (${n} of ${N} households show a ${p.gap_bar.toFixed(0)}-point-or-more gap the other way).`;
  if(g<=-p.gap_bar) return `everyone else's things got ${(-g).toFixed(0)} points worse than the sick person's here (${n} of ${N} households).`;
  return `no clear difference here — only ${n} of ${N} households show a gap of ${p.gap_bar.toFixed(0)} points or more.`;
}
function windowBarStrip(WIN,SHORT,byWindow,seriesA,seriesB,labelA,labelB,color,W,H,fmt){
  // one mini chart: for each of the 5 windows, one solid bar (seriesA) + one faint bar (seriesB); window names are
  // NOT re-labelled on this narrow axis (5 short strings collide below ~400px) — one shared sequence line under the
  // pair of charts gives the order once, and every bar still carries its own window name in its hover tooltip
  const L=32,T=14,B=10,Rr=8; const vals=WIN.map(w=>[byWindow[w][seriesA],byWindow[w][seriesB]]);
  const maxV=Math.max(fmt==="pct"?100:1,...vals.flat().map(v=>v.mean+(v.sd||0))); const scaleMax = fmt==="pct"?100:Math.max(2,Math.ceil(maxV/2)*2);
  const y=val=>T+(scaleMax-val)*(H-T-B)/scaleMax; const bw=(W-L-Rr)/WIN.length;
  let g=""; const ticks = fmt==="pct" ? [0,50,100] : [0, Math.round(scaleMax/2), scaleMax];
  for(const vv of ticks) g+=`<line class="grid" x1="${L}" x2="${W-Rr}" y1="${y(vv).toFixed(1)}" y2="${y(vv).toFixed(1)}"/><text x="${L-6}" y="${(y(vv)+4).toFixed(1)}" text-anchor="end">${vv}</text>`;
  WIN.forEach((w,i)=>{ const x0=L+i*bw+6; const a=byWindow[w][seriesA], b=byWindow[w][seriesB]; const bw2=bw/2-10;
    if(a.n) g+=`<rect x="${x0}" y="${y(a.mean).toFixed(1)}" width="${bw2.toFixed(1)}" height="${(y(0)-y(a.mean)).toFixed(1)}" rx="2" fill="var(${color})"><title>${SHORT[w]}, ${labelA}: ${a.mean.toFixed(1)}${fmt==="pct"?"%":""} ± ${a.sd.toFixed(1)} (${a.n} households)</title></rect>`;
    if(b.n) g+=`<rect x="${(x0+bw2+4).toFixed(1)}" y="${y(b.mean).toFixed(1)}" width="${bw2.toFixed(1)}" height="${(y(0)-y(b.mean)).toFixed(1)}" rx="2" fill="var(${color})" opacity="0.4"><title>${SHORT[w]}, ${labelB}: ${b.mean.toFixed(1)}${fmt==="pct"?"%":""} ± ${b.sd.toFixed(1)} (${b.n} households)</title></rect>`; });
  return `<svg viewBox="0 0 ${W} ${H}" role="img" aria-label="${labelA} vs ${labelB}, by the five moments before/during/after the shift">${g}</svg>`;
}
function spreadSentence(m,transition,label){
  const p=m.pairs[transition]; const gc=p.global_metric_change.mean, pc=p.person_metric_change.mean;
  const ga=p.global_acc_change.mean, pa=p.person_acc_change.mean;
  const accHarm = Math.abs(ga-pa)>=8 && ga<pa-8;
  const doubtSpread = Math.abs(gc)>=Math.abs(pc)*2 && Math.abs(gc)>=3;
  if(accHarm && doubtSpread) return `spreads both damage (accuracy ${ga.toFixed(0)} vs ${pa.toFixed(0)} points) and doubt (${label} ${gc>=0?"+":""}${gc.toFixed(0)} vs ${pc>=0?"+":""}${pc.toFixed(0)}) when it's shared for the whole household.`;
  if(doubtSpread) return `accuracy barely differs (${ga.toFixed(0)} vs ${pa.toFixed(0)} points) but ${label} on everyone else's things swings ${gc>=0?"+":""}${gc.toFixed(0)} when shared for the whole household, vs only ${pc>=0?"+":""}${pc.toFixed(0)} split per person — it spreads DOUBT, not damage.`;
  return `neither accuracy (${ga.toFixed(0)} vs ${pa.toFixed(0)}) nor ${label} (${gc>=0?"+":""}${gc.toFixed(0)} vs ${pc>=0?"+":""}${pc.toFixed(0)}) differs much here between sharing it and splitting it per person.`;
}
function dailyGap(reg, key, mode){
  const G = EXTRA.gap && EXTRA.gap.populations[reg]; if(!G) return null;
  const M = G.methods[key]; if(!M) return null;
  const idx = mode==="raw" ? 2 : 3; const nd = G.days; const mean=[], sd=[], nn=[];
  for(let d=1; d<nd; d++){ const vals=[]; let N=0;
    for(const hh of Object.keys(M.cells)){ const c=M.cells[hh][d]; if(!c || c[0]<3) continue; vals.push(100*(c[idx]-c[1])/c[0]); N+=c[0]; }
    if(!vals.length){ mean.push(null); sd.push(null); nn.push(0); continue; }
    const m=vals.reduce((a,b)=>a+b,0)/vals.length; const s=vals.length>1? Math.sqrt(vals.reduce((a,b)=>a+(b-m)**2,0)/(vals.length-1)):0;
    if(N<MIN_N){ mean.push(null); sd.push(null); nn.push(N); continue; }   // thin tail of an in-progress arm: keep n for the tooltip, draw nothing
    mean.push(m); sd.push(s); nn.push(N);
  } return {mean, sd, n:nn};
}
function gapSeries(){
  const reg=state.gapReg, mode=state.gapMode; const G = EXTRA.gap && EXTRA.gap.populations[reg]; if(!G) return [];
  const base = SERIES.filter(s=>state.on.has(s.k) && G.methods[s.k] && !G.methods[s.k].live);
  let out = base.map(s=>({s, key:s.k, dash:false}));
  if(reg==="partial"){ for(const s of base){ for(const ck of (GAP_COMPANION[s.k]||[])){ if(G.methods[ck]) out.push({s:gapSeriesInfo(ck), key:ck, dash:true}); } } }
  for(const key of Object.keys(G.methods)){ const M=G.methods[key]; if(!M.live) continue;
    if(mode==="leadcal" && !M.hasLeadcal) continue;   // no lead-day fit yet for this arm -- only show it in "as stated" mode
    out.push({s:{k:key, name:M.name, v:M.v, progress:M.progress}, key, dash:M.dash!==false}); }
  return out;
}
function renderGap(){
  const reg=state.gapReg, mode=state.gapMode; const G = EXTRA.gap && EXTRA.gap.populations[reg]; const svg=$("#gap");
  if(!G){ svg.innerHTML=""; $("#gapnote").textContent="No calibration-gap data for this population yet."; $("#gaptable").innerHTML=""; return; }
  const nd=G.days, W=1000,H=320,L=46,Rt=210,T=18,B=36;
  const x=d=>L+(d-1)*(W-L-Rt)/(nd-2);
  const series = gapSeries();
  const lines = series.map(e=>({...e, D: dailyGap(reg, e.key, mode)})).filter(e=>e.D);
  let ymin=-10, ymax=10;
  for(const {D} of lines){ D.mean.forEach((m,i)=>{ if(m==null) return; ymin=Math.min(ymin, m-D.sd[i]); ymax=Math.max(ymax, m+D.sd[i]); }); }
  ymin=Math.floor((ymin-4)/10)*10; ymax=Math.ceil((ymax+4)/10)*10;
  const y=v=>T+(ymax-v)*(H-T-B)/(ymax-ymin);
  let g="";
  for(const st of gapStages(reg)){ const f=STAGE_FILL[st.name]; if(f) g+=`<rect x="${(x(st.a)-8).toFixed(1)}" y="${T}" width="${(x(st.b)-x(st.a)+16).toFixed(1)}" height="${H-T-B}" fill="var(${f})" opacity="0.5"/>`;
    g+=`<text class="stg" x="${((x(st.a)+x(st.b))/2).toFixed(1)}" y="${T-6}" text-anchor="middle">${STAGE_LABEL[st.name]||st.name}</text>`; }
  const step = (ymax-ymin)>60?20:10;
  for(let v=Math.ceil(ymin/step)*step; v<=ymax; v+=step) g+=`<line class="grid" x1="${L}" x2="${W-Rt}" y1="${y(v).toFixed(1)}" y2="${y(v).toFixed(1)}"/><text x="${L-8}" y="${(y(v)+4).toFixed(1)}" text-anchor="end">${v>0?"+":""}${v}</text>`;
  g+=`<line x1="${L}" x2="${W-Rt}" y1="${y(0).toFixed(1)}" y2="${y(0).toFixed(1)}" stroke="var(--ink2)" stroke-width="1.3" stroke-dasharray="2 3"/>`;
  for(let d=1; d<nd; d++){ if(d%2===1) g+=`<text x="${x(d).toFixed(1)}" y="${H-B+16}" text-anchor="middle">${d}</text>`; }
  g+=`<text x="${((L+W-Rt)/2).toFixed(1)}" y="${H-6}" text-anchor="middle" class="lbl">day — above 0: overconfident (stated &gt; actual) · below 0: underconfident</text>`;
  const ends=[];
  for(const {s,D,dash} of lines){ const col=`var(${s.v})`;
    if(state.bands){ const up=[],lo=[]; D.mean.forEach((m,i)=>{ if(m==null) return; up.push(`${x(i+1).toFixed(1)},${y(Math.min(ymax,m+D.sd[i])).toFixed(1)}`); lo.unshift(`${x(i+1).toFixed(1)},${y(Math.max(ymin,m-D.sd[i])).toFixed(1)}`); }); if(up.length>1) g+=`<polygon points="${up.join(" ")} ${lo.join(" ")}" fill="${col}" opacity="0.1"/>`; }
    const pts=[]; D.mean.forEach((m,i)=>{ if(m!=null) pts.push(`${x(i+1).toFixed(1)},${y(m).toFixed(1)}`); });
    g+=`<polyline fill="none" stroke="${col}" stroke-width="${dash?1.6:2.2}" stroke-linejoin="round" ${dash?'stroke-dasharray="5 3"':""} points="${pts.join(" ")}"/>`;
    const last=D.mean.map((m,i)=>[m,i]).filter(a=>a[0]!=null).pop(); if(last) ends.push({s,col,yy:y(last[0]),v:last[0],dash}); }
  ends.sort((a,b)=>a.yy-b.yy); let prev=-99; for(const e of ends){ let yy=Math.max(e.yy, prev+14); prev=yy; g+=`<circle cx="${(W-Rt).toFixed(1)}" cy="${e.yy.toFixed(1)}" r="3.5" fill="${e.col}"/><text class="lbl" x="${W-Rt+8}" y="${(yy+4).toFixed(1)}" style="fill:var(--ink)">${e.s.name}${e.dash&&!e.s.progress?" (per person)":""} · ${e.v>0?"+":""}${e.v.toFixed(0)}pp${e.s.progress?" "+e.s.progress:""}</text>`; }
  g+=`<line id="gapxh" class="axis" x1="0" x2="0" y1="${T}" y2="${H-B}" style="display:none"/>`;
  svg.innerHTML=g; svg.dataset.geom=JSON.stringify({L,Rt,W,nd});

  const popTxt = reg==="household"?"everyone sick · households 1–10":reg==="person"?"one person sick · that person's things":"one person sick · everyone's things asked";
  const modeTxt = mode==="raw"? "as each method itself states it" : "after removing the lead-day-fitted level offset";
  $("#gapnote").textContent = lines.length? `Confidence ${modeTxt}, pooled over households of the "${popTxt}" population. Dashed lines (where shown) are the per-person-grouped variant of the same-colored method.` : "No method selected in the legend above has calibration-gap data for this population.";
  let th=`<thead><tr><th>method</th><th class="num">lead (1–13)</th><th class="num">days 14–16</th><th class="num">days 24–26</th></tr></thead><tbody>`;
  for(const {s,key,dash} of series){ const M=G.methods[key]; if(!M||!M.summary) continue; const sm=M.summary; const idx = mode==="raw"?"raw":"leadcal";
    const cell=w=>{ const v=sm[w] && sm[w][idx]; return v? `${v.gap>0?"+":""}${v.gap.toFixed(0)} <span class="muted">±${v.sd.toFixed(0)}</span>` : "–"; };
    th+=`<tr><td><i class="swatch" style="background:var(${s.v})"></i>${s.name}${dash?" (per person)":""}</td><td class="num">${cell("lead")}</td><td class="num">${cell("d14_16")}</td><td class="num">${cell("d24_26")}</td></tr>`; }
  $("#gaptable").innerHTML = series.length? th+"</tbody>" : "";
}
function hoverGap(ev){
  const svg=$("#gap"); const geom=JSON.parse(svg.dataset.geom||"null"); if(!geom) return; const rect=svg.getBoundingClientRect(); const px=(ev.clientX-rect.left)*geom.W/rect.width;
  const d=Math.round((px-geom.L)/((geom.W-geom.L-geom.Rt)/(geom.nd-2)))+1; const xh=$("#gapxh");
  if(d<1||d>=geom.nd){ $("#gaptip").style.display="none"; if(xh) xh.style.display="none"; return; }
  const xx=geom.L+(d-1)*(geom.W-geom.L-geom.Rt)/(geom.nd-2); xh.setAttribute("x1",xx); xh.setAttribute("x2",xx); xh.style.display="";
  let st="plain"; for(const s2 of gapStages(state.gapReg)) if(d>=s2.a&&d<=s2.b) st=s2.name;
  let rows=`<div style="margin-bottom:4px"><b>day ${d}</b> · ${STAGE_LABEL[st]||st}</div>`;
  const reg=state.gapReg, mode=state.gapMode;
  for(const {s,key} of gapSeries()){ const D=dailyGap(reg,key,mode); if(!D) continue;
    if(D.mean[d-1]==null){ if(D.n[d-1]>0) rows+=`<div class="r"><span><i style="background:var(${s.v})"></i>${s.name}</span><span class="muted">(n=${D.n[d-1]}, too few)</span></div>`; continue; }
    rows+=`<div class="r"><span><i style="background:var(${s.v})"></i>${s.name}</span><span>${D.mean[d-1]>0?"+":""}${D.mean[d-1].toFixed(0)}pp ±${D.sd[d-1].toFixed(0)}</span></div>`; }
  const tip=$("#gaptip"); tip.innerHTML=rows; tip.style.display="block"; const wrap=svg.parentElement.getBoundingClientRect(); let lx=ev.clientX-wrap.left+14; if(lx+230>wrap.width) lx=ev.clientX-wrap.left-240; tip.style.left=lx+"px"; tip.style.top=(ev.clientY-wrap.top+12)+"px";
}
function renderGapConformal(){
  const reg=state.gapReg; const G = EXTRA.gap && EXTRA.gap.populations[reg]; const host=$("#gapconformal"); host.innerHTML="";
  if(!G || !G.conformal || !Object.keys(G.conformal).length){ $("#gapconfnote").textContent=""; return; }
  const nd=G.days, W=460,H=170,L=34,T=16,B=26,Rr=10; const x=d=>L+(d-1)*(W-L-Rr)/(nd-2);
  const bands=()=>{ let g=""; for(const st of gapStages(reg)){ const f=STAGE_FILL[st.name]; if(f) g+=`<rect x="${(x(st.a)-6).toFixed(1)}" y="${T}" width="${(x(st.b)-x(st.a)+12).toFixed(1)}" height="${H-T-B}" fill="var(${f})" opacity="0.5"/>`; } return g; };
  const CONF_NAME = {conformal:["honest sets, nudging quantile","--s13"], conformal_person:["honest sets, nudging quantile, per person","--s10"], nexcp:["honest sets, weighted quantile","--s10"]};
  for(const key of Object.keys(G.conformal)){ const cells=G.conformal[key]; const [name,col] = CONF_NAME[key]||[key,"--sv"];
    const days=[...Array(nd-1).keys()].map(i=>i+1);
    const cov=days.map(d=>{ let n=0,c=0; for(const hh of Object.keys(cells)){ const cc=cells[hh][d]; if(cc){ n+=cc[0]; c+=cc[1]; } } return n? 100*c/n : null; });
    const sz=days.map(d=>{ let n=0,s=0; for(const hh of Object.keys(cells)){ const cc=cells[hh][d]; if(cc){ n+=cc[0]; s+=cc[2]; } } return n? s/n : null; });
    const yc=v=>T+(100-v)*(H-T-B)/100;
    let g=bands(); for(const v of [0,90,100]) g+=`<line class="grid" x1="${L}" x2="${W-Rr}" y1="${yc(v).toFixed(1)}" y2="${yc(v).toFixed(1)}"/><text x="${L-6}" y="${(yc(v)+4).toFixed(1)}" text-anchor="end">${v}%</text>`;
    g+=`<line x1="${L}" x2="${W-Rr}" y1="${yc(90).toFixed(1)}" y2="${yc(90).toFixed(1)}" stroke="var(--muted)" stroke-dasharray="3 3" stroke-width="1.2"/>`;
    g+=`<polyline fill="none" stroke="var(${col})" stroke-width="2" points="${days.map((d,i)=>cov[i]==null?"":`${x(d).toFixed(1)},${yc(cov[i]).toFixed(1)}`).join(" ")}"/>`;
    for(let d=1; d<nd; d+=4) g+=`<text x="${x(d).toFixed(1)}" y="${H-B+14}" text-anchor="middle">${d}</text>`;
    const szmax=Math.max(1,...sz.filter(v=>v!=null))*1.1; const ys=v=>T+(szmax-v)*(H-T-B)/szmax;
    let g2=bands(); for(const v of [0,10,20]) if(v<=szmax) g2+=`<line class="grid" x1="${L}" x2="${W-Rr}" y1="${ys(v).toFixed(1)}" y2="${ys(v).toFixed(1)}"/><text x="${L-6}" y="${(ys(v)+4).toFixed(1)}" text-anchor="end">${v}</text>`;
    g2+=`<polyline fill="none" stroke="var(${col})" stroke-width="2" points="${days.map((d,i)=>sz[i]==null?"":`${x(d).toFixed(1)},${ys(sz[i]).toFixed(1)}`).join(" ")}"/>`;
    for(let d=1; d<nd; d+=4) g2+=`<text x="${x(d).toFixed(1)}" y="${H-B+14}" text-anchor="middle">${d}</text>`;
    host.innerHTML += `<div class="panel"><h3>${name} — coverage vs. 90% target</h3><p>Not a confidence number: coverage is the share of questions whose truth was inside the named set (dashed line: the 90% target); set size is the average number of places named.</p><svg viewBox="0 0 ${W} ${H}" role="img" aria-label="${name} coverage per day">${g}</svg></div>`;
    host.innerHTML += `<div class="panel"><h3>${name} — set size</h3><p>Average number of places named per day.</p><svg viewBox="0 0 ${W} ${H}" role="img" aria-label="${name} set size per day">${g2}</svg></div>`;
  }
  $("#gapconfnote").textContent = "Coverage and set size, pooled over households, same population as the chart above.";
}
function renderAskgate(){
  const reg=state.gapReg; const arms=(EXTRA.llm_live && EXTRA.llm_live[reg]) || {}; const T=$("#askgatetable");
  const rows = Object.keys(arms).map(k=>arms[k]).filter(a=>a.askgate);
  if(!rows.length){ T.innerHTML=""; $("#askgatenote").textContent = "No LLM arm has an ask-gate computed for this population yet."; return; }
  const WL = rows[0].window_labels || WINDOWS5_JS; const wkeys = Object.keys(WL);
  let h=`<thead><tr><th>arm</th>${wkeys.map(w=>`<th>${WL[w]}<br><span class="muted">ask% / miss%</span></th>`).join("")}<th>tightens at shift?</th></tr></thead><tbody>`;
  for(const a of rows){ const g=a.askgate; const tt=g._tighten_at_shift;
    const cells = wkeys.map(w=>{ const v=g[w]; return (v && v.n>=MIN_N)? `<td class="num">${v.ask_rate}% / ${v.miss_rate==null?"–":v.miss_rate+"%"}</td>` : "<td>–</td>"; }).join("");
    h+=`<tr><td>${a.name}${a.progress?` <span class="muted">${a.progress}</span>`:""}</td>${cells}<td class="num" style="color:${tt.tightened?"var(--good)":"inherit"}">${tt.tightened?"yes":"no"} <span class="muted">(q ${tt.q_lead}→${tt.q_shift})</span></td></tr>`; }
  T.innerHTML = h + "</tbody>";
  $("#askgatenote").textContent = "q = the confidence bar the gate currently requires before it will trust the model's own answer instead of asking; it starts adapting after a 20-question warm-up per arm, so early-lead numbers are noisier than later ones.";
}
const WINDOWS5_JS = {lead:"lead (9–13)", d14_16:"14–16", d17_23:"17–23", d24_26:"24–26", d27_31:"27–31"};
function renderKnowno(){
  const reg=state.gapReg; const arms=(EXTRA.knowno_live && EXTRA.knowno_live[reg]) || {}; const T=$("#knownotable");
  const keys=Object.keys(arms); if(!keys.length){ T.innerHTML=""; $("#knownonote").textContent="No token-probability channel logged for this population yet."; return; }
  const stageOf = d => d<=13?"lead":d<=23?"sick":"return";
  let h=`<thead><tr><th>arm · day</th><th class="num">n</th><th class="num">accuracy</th><th class="num">verbalized</th><th class="num">agreement</th><th class="num">token prob.</th><th class="num">MCQ accuracy</th><th class="num">set coverage</th><th class="num">set size /10</th></tr></thead><tbody>`;
  for(const k of keys){ const a=arms[k]; const days=Object.keys(a.days).map(Number).sort((x,y)=>x-y);
    h+=`<tr><td colspan="9"><b>${a.name}</b> <span class="muted">· ${a.n_hh} household${a.n_hh===1?"":"s"}, ${a.n} questions so far</span></td></tr>`;
    for(const d of days){ const v=a.days[String(d)]; const thin=v.n<MIN_N;
      const c=x=> thin? "–" : x;
      h+=`<tr><td>day ${d} <span class="muted">${STAGE_LABEL[stageOf(d)]||stageOf(d)}</span></td><td class="num">${v.n}</td><td class="num">${c(v.acc.toFixed(0)+"%")}</td><td class="num">${c(v.verbal.toFixed(0)+"%")}</td><td class="num">${c(v.agree.toFixed(0)+"%")}</td><td class="num">${c(v.token.toFixed(0)+"%")}</td><td class="num">${c(v.mcq_acc.toFixed(0)+"%")}</td><td class="num">${c(v.coverage.toFixed(0)+"%")}</td><td class="num">${c(v.set_size.toFixed(1))}</td></tr>`; } }
  T.innerHTML=h+"</tbody>";
  $("#knownonote").textContent="Read each confidence column against the accuracy column on the same day: a channel that stays near 80–90% while accuracy drops to 30–40% on day 14 is not reading its own mistakes. Set coverage near 90% with a size that grows on the shift days is the honest-sets behaviour; a size that shrinks back by day 20 means the model's probabilities re-concentrated once the new routine settled.";
}
function renderAffected(){
  const host=$("#affected");
  if(!EXTRA||!EXTRA.affected_windows){ host.innerHTML=""; return; } host.innerHTML="";
  const EX=EXTRA.affected_windows, WIN=EX.window_order;
  const SHORT={last5lead:"before",first3sick:"sick, days 1–3",restsick:"sick, later",first3return:"back, days 1–3",restreturn:"back, later"};
  // 1. the per-object reference: one learner, as a control (it passes by construction — every object has its own record)
  const ref=EX.agents["none_tt"];
  if(ref){ const v=ref.color;
    const W=620,H=200,L=38,T=16,B=40,Rr=10; const y=val=>T+(100-val)*(H-T-B)/100; const bw=(W-L-Rr)/WIN.length;
    let g=""; for(const vv of [0,50,100]) g+=`<line class="grid" x1="${L}" x2="${W-Rr}" y1="${y(vv).toFixed(1)}" y2="${y(vv).toFixed(1)}"/><text x="${L-6}" y="${(y(vv)+4).toFixed(1)}" text-anchor="end">${vv}%</text>`;
    WIN.forEach((w,i)=>{ const x0=L+i*bw+10; const a=ref.windows[w].affected, u=ref.windows[w].unaffected; const bw2=bw/2-14;
      if(a.n) g+=`<rect x="${x0}" y="${y(a.mean).toFixed(1)}" width="${bw2.toFixed(1)}" height="${(y(0)-y(a.mean)).toFixed(1)}" rx="3" fill="var(${v})"><title>${SHORT[w]}, the sick person's things: ${a.mean.toFixed(0)}% ± ${a.sd.toFixed(0)} (${a.n} households)</title></rect><text x="${(x0+bw2/2).toFixed(1)}" y="${(y(a.mean)-4).toFixed(1)}" text-anchor="middle">${a.mean.toFixed(0)}</text>`;
      if(u.n) g+=`<rect x="${(x0+bw2+6).toFixed(1)}" y="${y(u.mean).toFixed(1)}" width="${bw2.toFixed(1)}" height="${(y(0)-y(u.mean)).toFixed(1)}" rx="3" fill="var(${v})" opacity="0.4"><title>${SHORT[w]}, everyone else's things: ${u.mean.toFixed(0)}% ± ${u.sd.toFixed(0)} (${u.n} households)</title></rect><text x="${(x0+bw2+6+bw2/2).toFixed(1)}" y="${(y(u.mean)-4).toFixed(1)}" text-anchor="middle">${u.mean.toFixed(0)}</text>`;
      g+=`<text x="${(x0+bw/2-5).toFixed(1)}" y="${H-B+16}" text-anchor="middle">${SHORT[w]}</text>`; });
    g+=`<text x="${L}" y="${H-8}" class="lbl">solid: the sick person's things · faint: everyone else's · ${ref.n_households} households</text>`;
    host.innerHTML+=`<div class="panel"><h3>Reference: ${ref.name}</h3><p><b>This one keeps a separate record for every object, so it passes by construction</b> — nothing about the sick person's things can leak into the record for anyone else's, whatever happens. It is the control, not a test.<br><b>Getting sick:</b> ${pairSentence(ref.pairs.entry)}<br><b>Coming back:</b> ${pairSentence(ref.pairs.return)}</p><svg viewBox="0 0 ${W} ${H}" role="img" aria-label="${ref.name}: the sick person's things vs everyone else's">${g}</svg></div>`; }
  // 2. the real test: methods that share one piece of state across every object — does that state leak the sick
  // person's disruption onto the things of the person whose routine never changed?
  const SS=EXTRA.shared_state;
  if(SS){ for(const key of Object.keys(SS.methods)){ const m=SS.methods[key];
    const fmt = m.metric_label.startsWith("confidence") ? "pct" : "num";
    const accSvg = windowBarStrip(WIN,SHORT,m.windows,"global_acc","person_acc","shared for the household","split per person",m.color,320,140,"pct");
    const metSvg = windowBarStrip(WIN,SHORT,m.windows,"global_metric","person_metric","shared for the household","split per person",m.color,320,140,fmt);
    host.innerHTML+=`<div class="panel" style="grid-column:span 2"><h3>${m.name}</h3>`
      +`<p>Everyone else's things — ${m.global_name} vs ${m.person_name}. `
      +`<b>Getting sick:</b> ${spreadSentence(m,"first3sick_vs_last5lead",m.metric_label)}<br>`
      +`<b>Coming back:</b> ${spreadSentence(m,"first3return_vs_restsick",m.metric_label)}</p>`
      +`<div style="display:flex;gap:16px;flex-wrap:wrap"><div><h3 style="font-size:12px">accuracy, right or wrong</h3>${accSvg}</div>`
      +`<div><h3 style="font-size:12px">${m.metric_label}</h3>${metSvg}</div></div>`
      +`<p class="lbl" style="margin-top:4px">left to right in each chart: ${WIN.map(w=>SHORT[w]).join(" · ")}<br>solid: kept for the whole household · faint: kept separately per person · ${m.n_households} households</p></div>`; }
    // a marked slot for a method with genuinely different shared state (a rolling-buffer or nightly-summary LLM
    // memory, not per-object) — appears automatically above once its logs land under a "llm_*" key in shared_state.json;
    // shown as a placeholder meanwhile so the slot is visible, not silently missing
    const OS = EXTRA.owner_split_live && EXTRA.owner_split_live.partial;
    if(OS && Object.keys(OS).length){
      const order = ["llm_naive_nomsg","llm_naive_startmsg","llm_routine7_nomsg","llm_routine7_startmsg"].filter(k=>OS[k]).concat(Object.keys(OS).filter(k=>!["llm_naive_nomsg","llm_naive_startmsg","llm_routine7_nomsg","llm_routine7_startmsg"].includes(k)));
      const cell = v => (v && v.n>=MIN_N) ? `${v.acc.toFixed(0)} <span class="muted">(${v.n})</span>` : "–";
      const conf = v => (v && v.n>=MIN_N) ? `${v.conf.toFixed(0)}` : "–";
      let h=`<div class="tbl"><table><thead><tr><th>LLM memory · message</th><th>whose things</th>${Object.keys(WINDOWS5_JS).map(w=>`<th class="num">${WINDOWS5_JS[w]}</th>`).join("")}</tr></thead><tbody>`;
      const nhh = Math.max(...order.map(k=>OS[k].n_hh));
      for(const k of order){ const a=OS[k]; const W=a.windows;
        h+=`<tr><td rowspan="3"><b>${a.name}</b><br><span class="muted">${a.n_hh} household${a.n_hh===1?"":"s"}</span></td><td>the sick person's things</td>${Object.keys(WINDOWS5_JS).map(w=>`<td class="num">${cell(W[w].sick_all)}</td>`).join("")}</tr>`;
        h+=`<tr><td>everyone else's things</td>${Object.keys(WINDOWS5_JS).map(w=>`<td class="num">${cell(W[w].others_all)}</td>`).join("")}</tr>`;
        h+=`<tr><td class="muted">everyone else's, cold questions only · stated confidence</td>${Object.keys(WINDOWS5_JS).map(w=>`<td class="num muted">${cell(W[w].others_cold)} · ${conf(W[w].others_all)}%</td>`).join("")}</tr>`; }
      h+="</tbody></table></div>";
      host.innerHTML+=`<div class="panel" style="grid-column:span 2"><h3>LLM memories — does a message about one person leak into the other person's things?</h3>`
        +`<p>Accuracy (%) on the sick resident's own things against everyone else's, per window, from the workshop session's partial-shift arms — ${nhh} households, all arms finished (n per cell in brackets; "–" = fewer than ${MIN_N}). Read the comparison between the no-message and start-message rows of the same memory: the message moves the sick resident's things and leaves the other resident's where they were. Differences are measured household by household and given as the average ± its standard error, with the spread between households beside it; an average at least twice its standard error is claimed as a difference. An earlier version of this panel, on three households, reported that the routine table with a message degraded the other resident's things — with all six households that is a wash (per household in the sick spell: −14, −10, −11, +8, +9, −12), and the claim has been withdrawn.</p>${h}</div>`;
    } else if(!Object.keys(SS.methods).some(k=>k.startsWith("llm")))
      host.innerHTML+=`<div class="panel" style="opacity:0.6"><h3>LLM memory (buffer / nightly summary)</h3><p>This method also keeps one shared record for the household rather than one per object, so it belongs in this row too. It was run: the result is the partial-shift panel beside this one, on six households, and is not repeated here.</p></div>`;
  }
  $("#affnote").textContent="Reading, top panel: each pair of bars is the same five moments — the settled week before, the first three sick days, the rest of the sick spell (re-learned), the first three days back to normal, and the rest of the return. A method that keeps a separate record per object cannot possibly leak information between the sick person's things and everyone else's — it holds up (\"held steady\") because it can do nothing else, not because it noticed anything. The sentences under it are the paired change, per household, against each household's own settled week — not just the two group averages, which can look similar even when every single household shows a real gap. Below: the three methods that DO keep one shared piece of state per household — a hedge weight, a conformal size bar, a change alarm — checked against the same method with the state kept separately per person instead. All three tell the same story: sharing it does not make the unaffected person's own answers more often wrong, but it does swing how SURE the robot sounds about their things, several times more than splitting it does — the robot spreads doubt about people whose routine never changed, not damage.";
}
function renderPlanning(){
  const host=$("#planning"); if(!EXTRA||!EXTRA.planning){ host.innerHTML="<p>The planning-cost result is in the gist above — noticing only pays for itself when it triggers a reset — and its table is in the working notes; it is missing from this build only, which means a rebuild caught the data files mid-write.</p>"; return; }
  const md=EXTRA.planning; const lines=md.split("\n").filter(l=>l.startsWith("|")); if(lines.length<3){ host.innerHTML="<p>The planning-cost table did not parse in this build; the result it carries is the one stated in the gist above.</p>"; return; }
  const NAME={none_tt:"timetable, never forgets",none_tt72:"timetable, 3-day memory",none_lastseen:"last seen",mart_tt72:"3-day timetable + change alarm",bma_tt:"hedge over memory lengths",ocp_tt:"honest sets (conformal) on the timetable"};
  const rows=lines.slice(2).map(l=>l.split("|").slice(1,-1).map(c=>c.trim()));
  let h=`<div class="tbl"><table><thead><tr><th>method</th><th>lead-up: places / rooms / share confident</th><th>sick spell</th><th>return</th><th class=num>lead cost</th><th class=num>sick cost</th><th class=num>return cost</th></tr></thead><tbody>`;
  for(const r of rows){ if(!NAME[r[0]]) continue; h+=`<tr><td>${NAME[r[0]]}</td><td>${r[1]}</td><td>${r[2]}</td><td>${r[3]}</td><td class=num>${r[4]}</td><td class=num>${r[6]}</td><td class=num>${r[8]}</td></tr>`; }
  h+=`</tbody></table></div><p>Cost per question in places-equivalents with asking costing 2 (a search visits places in probability order; "share confident" = questions answered without asking, confidence ≥ 0.6 or a set of ≤ 3 places). Read with care: a method that is simply less confident asks more everywhere, which flatters it here. The fair test fixes every method's lead-day ask rate (25% or 50%) and looks at sick days only — and then <b>only the change alarm + reset</b> is cheaper on sick days than on its own normal days (household regime: 3.31 → 2.55 at a 25% ask rate; 2.67 → 2.25 at 50%). The hedge's apparent win in the table above is that confidence-scale effect (it already asked 68% of the time on normal days) and disappears at matched rates; honest sets do not help either (the set grows only on the first sick day). Last seen is always confident, never asks and pays 12–14 places per bad guess. So noticing the break turns into fewer wasted searches only when it triggers an actual reset — a lower confidence scale alone buys nothing.</p>`;
  host.innerHTML=h;
}
function mergeLLMLive(){
  if(!EXTRA.llm_live) return;
  const palette=["--s1","--s3","--s5","--s7","--s9","--s2","--s4","--s6"]; let i=0;
  for(const pop of ["household","person","person2x"]){   // the populations with a real DATA[pop] to plug into
    if(!DATA[pop]) continue;
    for(const key of Object.keys(EXTRA.llm_live[pop]||{})){
      const arm = EXTRA.llm_live[pop][key]; const col = palette[i++ % palette.length];
      const qkey = pop+":"+key;   // population-qualified so an identical memory-kind/message key in another
                                   // population (e.g. "naive" run on both sick10_partial and sick10_owner) can
                                   // never collide in the single flat SERIES array or leak into the wrong regime
      DATA[pop].agents[qkey] = arm.cells;
      SERIES.push({k:qkey, name:arm.name, v:col, core:true, dash:!arm.complete, progress:arm.progress,
        gloss:"An LLM-strategy arm from the overnight runs" + (arm.complete?", finished":", NOT yet finished — accuracy and confidence cover only the days answered so far, and it is drawn dashed for that reason") + ".",
        how:arm.progress});
      state.on.add(qkey);
    }
  }
  if(!EXTRA.gap) return;
  let j=0;
  for(const pop of ["household","partial","person","person2x"]){
    const arms = (EXTRA.llm_live && EXTRA.llm_live[pop]) || {}; const G = EXTRA.gap.populations[pop];
    if(!G) continue;
    for(const key of Object.keys(arms)){
      const arm = arms[key]; const cells = {};
      for(const h2 of Object.keys(arm.cells)){ cells[h2] = arm.cells[h2].all; }   // gap chart has no split; flatten out of {all,moved}
      G.methods[key] = {cells, lead_map:[], summary:null, live:true, hasLeadcal:!!arm.has_leadcal,
        name:arm.name, progress:arm.progress, v:palette[j++%palette.length], dash:!arm.complete};
    }
  }
}
const BUILT = "/*BUILT*/";
function renderGist(){
  const L=$("#gistlist"); if(!L) return; $("#gistwhen").textContent = "as of " + BUILT + " — every run behind this page has finished";
  const P = (EXTRA.llm_live && EXTRA.llm_live.person) || {};
  const W = k => (P[k] && P[k].windows) || null;
  // Two families of number deliberately kept apart:
  //  acc/cold/conf  — one arm on its own households (used only for statements about that arm alone)
  //  accM/coldM     — the MATCHED windows: the same arm restricted to the households every message arm of that
  //                   memory kind ran on. Every told-vs-untold comparison uses these, because the arms do not
  //                   always cover the same households and the per-household spread is several points.
  const acc = (k,w) => { const v=W(k) && W(k)[w]; return (v && v.n>=MIN_N)? v.acc : null; };
  const cold = (k,w) => { const v=W(k) && W(k)[w]; return (v && v.n_cold>=MIN_N)? v.acc_cold : null; };
  const conf = (k,w) => { const v=W(k) && W(k)[w]; return (v && v.n>=MIN_N)? v.conf : null; };
  const WM = k => (P[k] && (P[k].windows_matched || P[k].windows)) || null;
  const accM = (k,w) => { const v=WM(k) && WM(k)[w]; return (v && v.n>=MIN_N)? v.acc : null; };
  const coldM = (k,w) => { const v=WM(k) && WM(k)[w]; return (v && v.n_cold>=MIN_N)? v.acc_cold : null; };
  // paired told-vs-untold contrast on the SAME households. Oliver's rule as of 07:25 this morning: claim a
  // difference when the average is at least twice its OWN standard error — the disagreement between households
  // divided by the square root of how many there are — and keep that disagreement beside it as a separate fact.
  // Below six households a standard error estimated from that few numbers is not worth trusting, so those arms
  // keep the older "bigger than the disagreement" floor and say how few households they rest on.
  const pv = (k,w,split) => { const p=P[k] && P[k].paired_vs_nomsg && P[k].paired_vs_nomsg[w]; return p? p[split||"all"] : null; };
  const fmtv = v => { if(!v) return "not measured";
    const m = `${v.mean>0?"+":""}${Math.abs(v.mean)<1? v.mean.toFixed(1) : v.mean.toFixed(0)}`;   // never print "+0"
    const tail = `n=${v.n_hh}, spread ±${v.sd.toFixed(0)}${v.small_n? " — few enough households that both bars are rough" : ""}`;
    return v.detected? `${m} ± ${v.se.toFixed(1)} points (${tail})`
                     : `no measurable difference (${m} ± ${v.se.toFixed(1)}, ${tail})`; };
  const bare = v => v? `${v.mean>0?"+":""}${Math.abs(v.mean)<1? v.mean.toFixed(1) : v.mean.toFixed(0)} ± ${v.se.toFixed(1)}` : "–";
  const pstr = (k,w,split) => fmtv(pv(k,w,split));
  // the retraction's own effect: telling twice vs telling once (distinct from either against never being told)
  const rv = (k,w,split) => { const p=P[k] && P[k].paired_vs_startmsg && P[k].paired_vs_startmsg[w]; return p? p[split||"all"] : null; };
  const rstr = (k,w,split) => { const v=rv(k,w,split); if(!v) return "not measured";
    if(v.detected) return fmtv(v);
    return `${v.mean>0?"+":""}${v.mean.toFixed(0)} ± ${v.se.toFixed(1)} (n=${v.n_hh}), which rules out a repair bigger than about ${(v.mean + 2*v.se).toFixed(0)} points`; };
  const nhh = k => { const v=pv(k,"d14_16"); return v? v.n_hh : (P[k] && P[k].hh_matched ? P[k].hh_matched.length : 0); };
  const hhM = k => (P[k] && P[k].hh_matched) ? (P[k].hh_matched.length===10? "all 10 households" : `households ${P[k].hh_matched.join(", ")}`) : "";
  const f = v => v==null? "…" : v.toFixed(0);
  const has = (...ks) => ks.every(k=>P[k]);
  // classical yardsticks on the same population (one person sick), pooled over the 10 households
  const DAYS = {lead:[9,10,11,12,13], s1:[14,15,16], s2:[17,18,19,20,21,22,23], r1:[24,25,26], r2:[27,28,29,30,31]};
  const cw = (k,w) => { const v=DATA.person && pooled("person",k,"all",DAYS[w]); return v==null? null : v; };
  const cconf = (k,w) => { const A=DATA.person && DATA.person.agents[k]; if(!A) return null; let n=0,sc=0; for(const hh of Object.keys(A)) for(const d of DAYS[w]){ const c=A[hh].all[d]; n+=c[0]; sc+=c[2]; } return n? 100*sc/n : null; };
  const items=[];
  // 1. everyone breaks (sizes from the data; cold = first question about an object that day)
  const memKinds=[["llm_naive_nomsg","buffer"],["llm_retrieval_nomsg","retrieval"],["llm_longcontext_nomsg","long-context"],["llm_reflect_nomsg","reflection"],["llm_routine7_nomsg","routine table"]];
  const drops = memKinds.filter(([k])=>acc(k,"lead")!=null && acc(k,"d14_16")!=null).map(([k,n])=>({n, d:acc(k,"lead")-acc(k,"d14_16"), dc:(cold(k,"lead")!=null&&cold(k,"d14_16")!=null)? cold(k,"lead")-cold(k,"d14_16") : null}));
  const learned = drops.filter(x=>acc(memKinds.find(m=>m[1]===x.n)[0],"lead")>=65);   // a memory that never learned the lead-up has nothing to lose
  const dmin = learned.length? learned.reduce((a,b)=>a.d<b.d?a:b) : null, dmax = learned.length? learned.reduce((a,b)=>a.d>b.d?a:b) : null;
  const cdrops = drops.filter(x=>x.dc!=null); const cmin = cdrops.length? Math.min(...cdrops.map(x=>x.dc)) : null, cmax = cdrops.length? Math.max(...cdrops.map(x=>x.dc)) : null;
  items.push(`<b>Every memory breaks on the first sick day — by ${dmin? f(dmin.d)+" points ("+dmin.n+")":"…"} to ${dmax? f(dmax.d)+" points ("+dmax.n+")":"…"} on all questions, and by ${cmin!=null? f(cmin)+"–"+f(cmax):"…"} points on cold questions.</b> Counters (settled lead-up → first three sick days): 3-day timetable ${f(cw("tt3d","lead"))}→${f(cw("tt3d","s1"))}%, never-forgets timetable ${f(cw("ttfrozen","lead"))}→${f(cw("ttfrozen","s1"))}%. LLM memories with no message: ${drops.map(x=>`${x.n} ${f(acc(memKinds.find(m=>m[1]===x.n)[0],"lead"))}→${f(acc(memKinds.find(m=>m[1]===x.n)[0],"d14_16"))}`).join(", ")}. The routine table hardly moves only because it never learned the lead-up (${f(acc("llm_routine7_nomsg","lead"))}%). Reflection drops least because it learned the lead-up least of the rest (${f(acc("llm_reflect_nomsg","lead"))}% where the buffer reaches ${f(acc("llm_naive_nomsg","lead"))}%); its later rise above its own lead-up (${f(acc("llm_reflect_nomsg","d17_23"))}% inside the spell) is a day-level effect — on cold questions it is ${f(cold("llm_reflect_nomsg","lead"))}→${f(cold("llm_reflect_nomsg","d14_16"))}→${f(cold("llm_reflect_nomsg","d17_23"))}%, below its lead-up — and the timetables show the same day-level rise (3-day: ${f(cw("tt3d","lead"))}→${f(cw("tt3d","s2"))}%) because the sick routine, once learned, keeps things in fewer places.`);
  // 2. re-learn vs break again
  items.push(`<b>Who re-learns inside the spell, and who breaks again when life returns.</b> The 3-day timetable re-learns to ${f(cw("tt3d","s2"))}% inside the spell and breaks again on the return (${f(cw("tt3d","r1"))}%); the never-forgets one stays stuck (${f(cw("ttfrozen","s2"))}%) and is right at once when the old routine is back (${f(cw("ttfrozen","r1"))}%). The LLM buffer with no message recovers slowly (${f(acc("llm_naive_nomsg","s1"===0?"d14_16":"d14_16"))}→${f(accM("llm_naive_nomsg","d17_23"))}→${f(acc("llm_naive_nomsg","d24_26"))}→${f(acc("llm_naive_nomsg","d27_31"))}%) and shows no second break — it breaks again on the return <em>only when it was told</em>: with the start message ${f(accM("llm_naive_startmsg","d17_23"))}% in the spell, then ${f(accM("llm_naive_startmsg","d24_26"))}% on the first days back.${has("llm_retrieval_nomsg")? ` Retrieval memory, no message: ${f(acc("llm_retrieval_nomsg","d14_16"))}→${f(acc("llm_retrieval_nomsg","d17_23"))}→${f(accM("llm_retrieval_nomsg","d24_26"))}%.`:""}${has("llm_longcontext_nomsg")? ` Long-context: ${f(acc("llm_longcontext_nomsg","d14_16"))}→${f(acc("llm_longcontext_nomsg","d17_23"))}→${f(acc("llm_longcontext_nomsg","d24_26"))}%.`:""}${has("llm_reflect_nomsg")? ` Reflection: ${f(acc("llm_reflect_nomsg","d14_16"))}→${f(acc("llm_reflect_nomsg","d17_23"))}→${f(acc("llm_reflect_nomsg","d24_26"))}%.`:""}`);
  // 3. what a sentence buys and costs
  const OS=(EXTRA.owner_split_live && EXTRA.owner_split_live.partial)||{};
  const os=(k,w,g)=>{ const v=OS[k] && OS[k].windows[w] && OS[k].windows[w][g]; return (v && v.n>=MIN_N)? v.acc : null; };
  items.push(`<b>What one sentence buys — and what it costs.</b> Each figure is the difference on the SAME household between the told and untold runs, averaged over households. Where the spread dwarfs the average, as it does on the return below, the difference is real but small — the households mostly move the same way rather than any one of them moving far. Telling the buffer "Yuki is home sick today" is worth ${pstr("llm_naive_startmsg","d14_16")} on the first three sick days and ${pstr("llm_naive_startmsg","d17_23")} through the rest of the spell; on cold questions — the first question about a thing each day, before any feedback — ${pstr("llm_naive_startmsg","d14_16","cold")} and ${pstr("llm_naive_startmsg","d17_23","cold")}.<br><br>It costs on the return: ${pstr("llm_naive_startmsg","d24_26")} on the first days back, cold ${pstr("llm_naive_startmsg","d24_26","cold")} — told once, it keeps believing the sick routine until feedback proves otherwise. Told again on the first day back, that cost is no longer measurable: with both messages the first days back come out ${pstr("llm_naive_startend","d24_26")} against never being told at all. Compare those two on the same ten households, since the retracted arm only ran there: un-retracted ${(()=>{const o=pv("llm_naive_startmsg","d24_26","all"); return o&&o.ours? `${Math.abs(o.ours.mean).toFixed(0)} points worse` : "\u2013";})()}, retracted 4 points worse \u2014 so the retraction does coincide with the cost going away. That is not the same as showing the retraction did the repairing, and when the two told arms are compared head to head we do not find it: ${rstr("llm_naive_startend","d24_26")} on all questions, ${rstr("llm_naive_startend","d24_26","cold")} on cold ones. ${(()=>{const v=rv("llm_naive_startend","d24_26","cold"); return (v&&v.ours)? `Our first ten households put that cold figure at +${v.ours.mean.toFixed(0)}; with the eight added afterwards it is +${v.mean.toFixed(0)}, so doubling the sample moved the estimate down rather than tightening it around the old one.` : "";})()}<br><br>The two halves are not the same size, and the difference matters more than either on its own. What the sentence buys on the way in is large and survives a fresh sample: ${pstr("llm_naive_startmsg","d17_23","cold")} on cold questions through the spell, where the ten households we ran first gave +36 and the eight added afterwards +30. What it costs on the way out is real but roughly a third the size, and confined to the first three days back — a week later there is ${pstr("llm_naive_startmsg","d27_31")} left of it. Both estimates came down when the sample doubled, and they came down for the same reason: our first ten households were the optimistic half of the draw, showing up once in each direction. That is one hopeful sample seen twice, not two separate surprises.<br><br>The same sentence costs a memory that looks things up by time of day for longer: retrieval is ${pstr("llm_retrieval_startmsg","d24_26")} on the first days back \u2014 a bigger number than the one we do claim, but the households disagree about it four times as much, which is the whole reason the bar is where it is \u2014 and still ${pstr("llm_retrieval_startmsg","d27_31")} behind a week later (cold ${pstr("llm_retrieval_startmsg","d27_31","cold")}) — its same-hour lookup keeps handing back the sick-day sightings after the buffer has dropped them — and the second message mostly, but not entirely, clears it: with both messages that same week comes out ${pstr("llm_retrieval_startend","d27_31","cold")} on cold questions against never being told — still large enough to measure, but ${(()=>{const a=pv("llm_retrieval_startmsg","d27_31","cold"), b=pv("llm_retrieval_startend","d27_31","cold"); return (a&&b&&b.mean)? `about a ${Math.round(Math.abs(a.mean/b.mean))===4?"quarter":Math.round(Math.abs(a.mean/b.mean))===3?"third":`${Math.round(Math.abs(a.mean/b.mean))}th`} of the ${a.mean.toFixed(0)} points` : "far less than what"})()} the un-retracted message leaves. Telling twice against telling once is, on cold questions, ${rstr("llm_retrieval_startend","d27_31","cold")}. The buffer shows no such lasting cost (${pstr("llm_naive_startmsg","d27_31")} a week after the return). The message is selective by object, for as long as it is true: where only one person is sick it moves the sick person's things and leaves the other resident's alone — the figures are in "Whose routine changed?" below, together with what happens to that selectivity once the message goes stale.`);
  // 4. confidence never moves
  const K=(EXTRA.knowno_live && EXTRA.knowno_live.person && EXTRA.knowno_live.person.llm_naive_nomsg) || null; const k14 = K && K.days["14"];
  const confs = memKinds.filter(([k])=>conf(k,"lead")!=null && conf(k,"d14_16")!=null).map(([k,n])=>`${n} ${f(conf(k,"lead"))}→${f(conf(k,"d14_16"))}%`);
  const AG=P.llm_naive_nomsg && P.llm_naive_nomsg.askgate;
  items.push(`<b>The LLM never knows when it is wrong.</b> Its stated confidence barely moves between the settled lead-up and the first sick days (${confs.join(", ")}) while its accuracy falls by 20–30 points; the counters' confidence moves with the stage (3-day timetable claims ${f(cconf("tt3d","lead"))}→${f(cconf("tt3d","s1"))}%). After a lead-day calibration that removes each method's own level, the buffer is ${P.llm_naive_nomsg && P.llm_naive_nomsg.windows.d14_16? "+"+f(P.llm_naive_nomsg.windows.d14_16.leadcal_conf - P.llm_naive_nomsg.windows.d14_16.acc) : "?"} points over-confident on the shift days. An answer-or-ask gate on that confidence has to ask ${AG && AG.d14_16? f(AG.d14_16.ask_rate) : "?"}% of the time on the shift days (vs ${AG && AG.lead? f(AG.lead.ask_rate) : "?"}% before) and still misses ${AG && AG.d14_16? f(AG.d14_16.miss_rate) : "?"}% of what it answers (target 10%).${k14 && k14.n>=MIN_N? ` Read three ways on the first sick day, the buffer is ${f(k14.acc)}% right while it says ${f(k14.verbal)}% (verbalized), ${f(k14.agree)}% (self-agreement), ${f(k14.token)}% (token probability) — none of the three channels reads the drop; an honest set on its own probabilities has to name ${k14.set_size.toFixed(1)} of 10 places to cover it ${f(k14.coverage)}% of the time.`:""}`);
  // 5. shared memory interferes
  {
    const OS=(EXTRA.owner_split_live && EXTRA.owner_split_live.partial)||{};
    const op = (k,w,g,sp) => { const p=OS[k] && OS[k].paired_vs_nomsg && OS[k].paired_vs_nomsg[w]; return p? p[`${g}_${sp}`] : null; };
    const ops = (k,w,g,sp) => fmtv(op(k,w,g,sp));
    // levels beside every contrast, from the extractor's own equal-weighted per-household means over exactly the
    // households that contrast is computed from, so a level can never move one way while its contrast moves the other
    const lvl = (k,w,g,sp) => { const v=op(k,w,g,sp); return v && v.base!=null? `${v.base.toFixed(0)}→${v.told.toFixed(0)}%` : "…"; };
    const nhh = (OS.llm_naive_startmsg && OS.llm_naive_startmsg.n_hh) || 0;
    const nOf = (k,w,g,sp) => { const v=op(k,w,g,sp); return v? v.n_hh : 0; };
    if(op("llm_naive_startmsg","d17_23","sick","all")) items.push(`<b>A message about one person moves that person\u2019s things and leaves the other resident\u2019s alone \u2014 until it goes stale.</b> In households where one resident is off sick but the robot is asked about everyone\u2019s things (${nhh} households, every arm finished), telling the buffer \u201cYuki is home sick today\u201d takes the sick resident\u2019s own things from ${lvl("llm_naive_startmsg","d14_16","sick","all")} on the first three sick days (${ops("llm_naive_startmsg","d14_16","sick","all")}) and from ${lvl("llm_naive_startmsg","d17_23","sick","all")} through the rest of the spell (${ops("llm_naive_startmsg","d17_23","sick","all")}); on cold questions the same two windows are ${lvl("llm_naive_startmsg","d14_16","sick","cold")} (${ops("llm_naive_startmsg","d14_16","sick","cold")}) and ${lvl("llm_naive_startmsg","d17_23","sick","cold")} (${ops("llm_naive_startmsg","d17_23","sick","cold")}). The other resident\u2019s things, on the same households and the same windows, go ${lvl("llm_naive_startmsg","d14_16","others","all")} and ${lvl("llm_naive_startmsg","d17_23","others","all")} \u2014 no measurable difference either time (${bare(op("llm_naive_startmsg","d14_16","others","all"))} and ${bare(op("llm_naive_startmsg","d17_23","others","all"))} points across the same six households), and none on cold questions either (${bare(op("llm_naive_startmsg","d14_16","others","cold"))} and ${bare(op("llm_naive_startmsg","d17_23","others","cold"))}, same six). The arm that shows nothing is half the finding: the sentence is applied where it belongs and, while it is true, nowhere else.<br><br>Then it stops being true. On the first three days back, with the message still standing and never retracted, the other resident\u2019s things fall ${lvl("llm_naive_startmsg","d24_26","others","all")} \u2014 ${ops("llm_naive_startmsg","d24_26","others","all")} \u2014 while the sick resident\u2019s own fall ${lvl("llm_naive_startmsg","d24_26","sick","all")}, ${ops("llm_naive_startmsg","d24_26","sick","all")}. So: while the instruction matches the world, the buffer applies it exactly where it belongs; once it is stale it costs a little beyond its target too, which is the same return cost the buffer shows on the one-person population, seen from the other side. Read the second half carefully \u2014 the leak we can actually measure is the ${Math.abs((op("llm_naive_startmsg","d24_26","others","all")||{}).mean||0).toFixed(0)}-point one onto the other resident\u2019s things, on ${nOf("llm_naive_startmsg","d24_26","others","all")} households; the estimate on the sick person\u2019s own things is larger but these ${nOf("llm_naive_startmsg","d24_26","sick","all")} households cannot separate it from zero, so nothing here says a stale message costs more away from home than at home. <br><br>On the same six households the nightly routine table behaves the same way on the other resident\u2019s things (${ops("llm_routine7_startmsg","d17_23","others","all")}) but is worse everywhere: without any message it answers the sick resident\u2019s things ${f((OS.llm_routine7_nomsg||{windows:{}}).windows.d17_23 ? OS.llm_routine7_nomsg.windows.d17_23.sick_all.acc : null)}% against the buffer\u2019s ${f((OS.llm_naive_nomsg||{windows:{}}).windows.d17_23 ? OS.llm_naive_nomsg.windows.d17_23.sick_all.acc : null)}%, and the other resident\u2019s ${f(OS.llm_routine7_nomsg.windows.d17_23.others_all.acc)}% against ${f(OS.llm_naive_nomsg.windows.d17_23.others_all.acc)}% \u2014 while its stated confidence sits between 82 and 89% in every window for both residents, message or no message.`);
  }
  // 6. noticing pays only with a reset
  items.push(`<b>Noticing only pays for itself when it triggers a reset.</b> Simulated search cost at a matched 25% ask rate (one person sick): in the sick spell the 3-day timetable searches 3.08 places per question, the same timetable with a change alarm that wipes the diary when it fires 2.48 (−20%); the hedge over memory lengths, which notices but does not reset, 3.14; the never-forgets timetable 3.66. A method that only knows it is unsure buys nothing at the planner; one that acts on it does.`);
  // 7. two spells (counters now; LLM arms when they land)
  if(DATA.person2x){
    const D2 = {lead:[9,10,11,12,13], s1a:[14,15,16], s1b:[17,18,19,20], r1b:[24,25,26,27], s2a:[28,29,30], s2b:[31,32,33,34]};
    const c2 = (k,w) => { const v=pooled("person2x",k,"all",D2[w]); return v==null? null : v; };
    const P2 = (EXTRA.llm_live && EXTRA.llm_live.person2x) || {};
    const a2 = (k,w) => { const v=P2[k] && P2[k].windows && P2[k].windows[w]; return (v && v.n>=MIN_N)? v.acc : null; };
    let llm2 = "";
    for(const [k,n] of [["llm_naive_nomsg","buffer"],["llm_retrieval_nomsg","retrieval"],["llm_naive_startmsg","buffer with the message"],["llm_retrieval_startmsg","retrieval with the message"]]){
      if(a2(k,"s1a")!=null && a2(k,"s2a")!=null) llm2 += ` ${n}: first break ${f(a2(k,"lead"))}→${f(a2(k,"s1a"))}%, second ${f(a2(k,"r1b"))}→${f(a2(k,"s2a"))}%${a2(k,"s2b")!=null? ` (re-learns to ${f(a2(k,"s1b"))} then ${f(a2(k,"s2b"))}%)`:""}.`; }
        items.push(`<b>When the same sick week comes back (days 28–34, after a week back to normal), the robot's simple learners keep the sick-day habit — it costs them almost nothing the second time.</b> First break → second break: 3-day timetable ${f(c2("tt3d","lead"))}→${f(c2("tt3d","s1a"))}% then ${f(c2("tt3d","r1b"))}→${f(c2("tt3d","s2a"))}%; 1-day timetable ${f(c2("tt1d","lead"))}→${f(c2("tt1d","s1a"))}% then ${f(c2("tt1d","r1b"))}→${f(c2("tt1d","s2a"))}%; never-forgets ${f(c2("ttfrozen","lead"))}→${f(c2("ttfrozen","s1a"))}% then ${f(c2("ttfrozen","r1b"))}→${f(c2("ttfrozen","s2a"))}%. The second spell is as different from normal life as the first (a plain "last seen" answer does no better the second time), so this is memory, not luck: these learners keep a habit for each hour of the day, and nothing during normal days ever replaces the sick-day habit at those hours — in the second spell, more than half of the questions fall in hours only the first spell ever filled, and there the 1-day learner is 97% right. Forgetting in these learners is relative within an hour of the day; a habit nothing overwrites is kept for ever. The language memories were run on the same two spells (buffer, which keeps only recent sightings, against retrieval, which looks up the same hour of the day) on three households, with the prediction written down first: retrieval would re-learn the second spell faster than the first and the buffer would not. It came out ${(()=>{const r=(EXTRA.llm_live&&EXTRA.llm_live.person2x&&EXTRA.llm_live.person2x.llm_retrieval_nomsg||{}).reuse_paired, b=(EXTRA.llm_live&&EXTRA.llm_live.person2x&&EXTRA.llm_live.person2x.llm_naive_nomsg||{}).reuse_paired; return r&&b? `${r.mean>0?"+":""}${r.mean.toFixed(0)} ± ${r.sd.toFixed(0)} points for retrieval and ${b.mean>0?"+":""}${b.mean.toFixed(0)} ± ${b.sd.toFixed(0)} for the buffer` : "not measured";})()} — neither clears the disagreement between three households, so the prediction is not supported and nothing is claimed from it. The robot's simple learners reuse the first spell; whether the language memories do is beyond what three households can tell us.`);
  }
  // 8. what actually makes a disruption break these methods (classical regimes; tools/break_cells.py reproduces
  // every number, 10 households each; both of our prior hypotheses were tested and refuted first)
  items.push(`<b>What breaks these methods is things being somewhere they usually are not — not being asked at a new hour.</b> Measure a disruption by how much of the household's stuff is out of its usual place. In a settled week about 35 in every 100 questions ask about something that is not where it normally lives. On the first three sick days that becomes 77 in 100; with friends over every evening, 51 in 100; on a holiday spent at home, 44 in 100 — and the breaks line up: 23, 11 and 2 points for the 3-day timetable. Being asked at an hour the robot has never seen before is harmless on its own: when the hour is new but the thing is in its usual place the robot is right 89–95% of the time in all three, because with nothing for that hour it falls back on where the thing normally lives, and that is normally correct. And the methods do not get worse at the questions they were already facing: the sick spell puts 41 more questions in every 100 into the kind they were always bad at, while their accuracy within each kind actually improves by 18 points.`);
  // 9. the negative result: a second kind of disruption that does not break these methods
  items.push(`<b>We tried a second kind of disruption — friends over every evening for ten days — and it does not break these methods.</b> The 3-day timetable falls 77 → 65% on the first three evenings-with-guests and is fully back inside the spell, with no drop when normal evenings return. Asking only in the guest hours makes it worse but not much: 71 → 57%, a 15-point break against the sick spell's 23. Asking only the morning after shows nothing at all (82 → 83%): whatever the guests moved is re-used or tidied away by morning. It fits the measure above — even concentrated on the guest hours, 61 in every 100 questions are about something out of its usual place against 77 in the sick spell, and the evening baseline is already 46 in 100. A disruption has to move a lot of things, for most of the day, to trouble a routine learner.`);
  // 10. reflection: the memory a message hardly helps, and the one that asks least (matched households only)
  if(pv("llm_reflect_startmsg","d14_16")){
    const g = k => { const a=P[k] && P[k].askgate; return (a && a.d14_16 && a.d14_16.n>=MIN_N)? a.d14_16.ask_rate : null; };
    const refl = pv("llm_reflect_startmsg","d14_16");
    const rup = refl.mean + 2*refl.se;   // what five households can still not rule out
    items.push(`<b>The memory that already writes its own corrections each night is the one case where we cannot say what the message does.</b> Reflection keeps a nightly note of the mistakes it made and what to check instead. Told \u201cYuki is home sick today\u201d, its first three sick days come out ${pstr("llm_reflect_startmsg","d14_16")} and its cold questions ${pstr("llm_reflect_startmsg","d14_16","cold")}, across the ${refl.n_hh} households all three of its message arms ran on \u2014 server time ran out before the other five. It is tempting to read that as "the sentence tells it something its own notes were already recording", and that may well be true, but five households cannot support it: the same figures are also consistent with a gain of up to ${rup.toFixed(0)} points \u2014 essentially the +${(pv("llm_naive_startmsg","d14_16")||{mean:0}).mean.toFixed(0)} the plain buffer gets. So what this arm establishes is only that we could not measure an effect, not that there is none \u2014 the one bullet here where absence of evidence is all we have. It is, separately, the least demanding of the four: asked to answer only when it can be wrong no more than one time in ten, it asks the resident on ${f(g("llm_reflect_nomsg"))}% of the shift-day questions where the buffer asks ${f(g("llm_naive_nomsg"))}% and retrieval ${f(g("llm_retrieval_nomsg"))}%.`);
  }

  if(pv("llm_longcontext_startmsg","d14_16")){
    const ab=(P.llm_longcontext_nomsg && P.llm_longcontext_nomsg.abandoned_hh) || [];
    const q = (k,w,sp) => bare(pv(k,w,sp));
    items.push(`<b>Long-context memory — the whole log in every prompt — was run on three households, which is too few to settle most of what we would want to ask of it.</b> It costs roughly ten times the compute of the other memories \u2014 about 10,000 to 12,000 tokens of prompt per question against 1,100 for retrieval and 1,400 to 1,500 for reflection, counted from the no-message arms\u2019 call logs (the two of us measured it separately and got 10,300 and 11,800, the spread coming from which arms were included; the multiple is seven to ten either way); its message arms were only ever affordable on three households, so the other ${ab.length} households of its no-message run were abandoned rather than finished, since they could not have improved any comparison. On three households the spread between households is itself barely measurable, so treat every figure here as indicative: telling it about the sick spell makes no measurable difference on the first three sick days (${q("llm_longcontext_startmsg","d14_16","all")} points, cold ${q("llm_longcontext_startmsg","d14_16","cold")}; every figure in this bullet is an average over three households \u00b1 its standard error), appears to help through the rest of the spell (${q("llm_longcontext_startmsg","d17_23","all")}, cold ${q("llm_longcontext_startmsg","d17_23","cold")}), and — the one pattern worth noting, because it matches retrieval on ten households — the cost of a message that is never retracted still shows a week after the return (${q("llm_longcontext_startmsg","d27_31","all")}, cold ${q("llm_longcontext_startmsg","d27_31","cold")}), while with the second message it is gone (${q("llm_longcontext_startend","d27_31","all")}). Two memories that keep everything behave the same way; a plain recency buffer does not.`);
  }


  // what this many households can resolve, measured rather than asserted: the median paired spread across our
  // ten-household comparisons (degenerate pairs — arms that are literally the same run before the return day — excluded)
  const sds = {all:[], cold:[]}, ses = {all:[], cold:[]};
  for(const k of Object.keys(P)) for(const w of Object.keys(P[k].paired_vs_nomsg||{})) for(const sp of ["all","cold"]){
    const v = P[k].paired_vs_nomsg[w][sp]; if(v && v.n_hh>=10 && v.sd>0){ sds[sp].push(v.sd); ses[sp].push(v.se); } }
  const med = a => { if(!a.length) return null; const b=a.slice().sort((x,y)=>x-y); return b[Math.floor(b.length/2)]; };
  if(sds.all.length){
    const note = document.createElement("p");
    note.className = "note"; note.style.margin = "0 0 8px";
    // The change of bar has to be visible rather than discoverable (Oliver, via the coordinator), but 350 words of
    // method must not stand between a reader and the findings. So: the change itself, and the direction it moved
    // things, in two sentences up top; the rest one click away.
    note.innerHTML = `<b>How to read these numbers — and the bar changed this morning.</b> Every comparison between two ways of running the same memory is measured household by household, never by setting one arm's overall number beside another's, and is written as <b>average ± its standard error</b> with <b>n</b> = households and <b>spread</b> = how much they disagree. Oliver asked us to move from "bigger than the spread" to "at least twice the standard error", and it is worth being plain about which way that moved things, because the name sounds stricter and the arithmetic is not: at ten households the standard error is about a third of the spread, so at six households or more anything that cleared the old bar clears the new one automatically. <b>Nothing written up overnight lost its standing, and the change could only add claims</b> — what it added is a handful of contrasts previously called "no measurable difference" that are now reported as small effects, and a detected three-point gain is described here as a small gain, not an important one. <details style="margin-top:6px"><summary style="cursor:pointer">What ten households can and cannot resolve, and the two findings withdrawn overnight</summary><div style="margin-top:6px">With ten households the smallest average we can now call is about ${f(2*med(ses.all))} points on all questions and about ${f(2*med(ses.cold))} on cold ones, where under the old bar it was about ${f(med(sds.all))} and ${f(med(sds.cold))}. Wherever a figure passes one bar and not the other, both are printed. The old floor still governs where a memory was only affordable on three or five households: a standard error estimated from that few numbers is not worth trusting, so those arms keep the spread floor and say how few households they rest on. Treat anything marked "three households" as indicative — worth reporting when it matches a pattern seen on ten, not on its own. Two findings were withdrawn overnight for failing exactly this test after first being written up on too few households: a claim that a memory shared across the household spread one person's disruption onto the other resident's things (three households; with all six it is a wash), and a two-point difference between two ways of running the reflection memory that was measured on different household sets. Both are recorded in the working notes; the numbers on this page are the ones that survived.</div></details>`;
    const box = $("#gistlist"); if(box && box.parentNode) box.parentNode.insertBefore(note, box);
  }
  // Order: the four findings that survived the spread test lead, in the order they tell the story; everything else
  // follows. Matching is on a distinctive phrase of each bullet so reordering does not depend on push order.
  // The lead group is what currently SURVIVES the spread test, not a fixed list: if a claim stops clearing when a
  // larger sample lands, its bullet drops out of the lead automatically rather than sitting at the top in weakened
  // form. The message-cost bullet leads only while the buffer's first-days-back contrast still clears.
  const LEAD = ["What one sentence buys", "The LLM never knows when it is wrong",
                "Every memory breaks on the first sick day", "the one case where we cannot say"];
  const holds = (k,w) => { const a=pv(k,w,"all"), c=pv(k,w,"cold"); return !!((a && a.detected) || (c && c.detected)); };
  const returnCostHolds = holds("llm_naive_startmsg","d24_26");
  const rank = t => {
    if(t.includes("What one sentence buys") && !returnCostHolds) return LEAD.length;   // demoted, not restated
    for(let i=0;i<LEAD.length;i++) if(t.includes(LEAD[i])) return i;
    return LEAD.length; };
  items.sort((a,b)=>rank(a)-rank(b));
  L.innerHTML = items.map(t=>`<li>${t}</li>`).join("");
}
for(const o of $("#regime").options){ if(!DATA[o.value]){ o.disabled=true; o.hidden=true; } }   // a population whose data has not been built yet is not selectable
for(const o of $("#gapreg").options){ if(!(EXTRA.gap && EXTRA.gap.populations[o.value])){ o.disabled=true; o.hidden=true; } }
mergeLLMLive();
renderGist(); renderLegend(); renderGloss(); draw(); renderSweep(); renderAffected(); renderPlanning();
</script>
'''
import datetime as _dt
open(out, "w").write(HTML.replace("/*DATA*/null", json.dumps(data, separators=(",", ":"))).replace("/*EXTRA*/null", json.dumps(extra, separators=(",", ":")))
     .replace("/*BUILT*/", _dt.datetime.now().strftime("%a %H:%M, %d %b %Y")))
print("wrote", out, os.path.getsize(out) // 1024, "KB")
