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
/* ONE COLOUR PER METHOD, defined once and read by every chart, legend, bar and swatch. Four focus methods get the
   four strong hues; everything else is muted grey. Colour never means anything but identity - no green-for-good or
   red-for-bad overloading anywhere (that overloading produced a real bug on 22 Sept: costs drawn in a variable
   whose name suggested red and whose value was dark green, so position said loss and colour said win).
   Both sets validated: four categorical hues, CVD separation, chroma floor, lightness band and contrast all pass
   against their own surface. Light worst adjacent pair dE 8.4 protan; dark 8.3 deutan. */
:root{
  --m-ttfrozen:#2a78d6; --m-tt3d:#eb6834; --m-perpetua:#199e70; --m-longcontext:#7a3aa7;
  --m-muted:#9a9a93;
}
@media (prefers-color-scheme: dark){ :root:not([data-theme="light"]){
  --m-ttfrozen:#1671f0; --m-tt3d:#b75c1c; --m-perpetua:#258d61; --m-longcontext:#ad32d6;
  --m-muted:#6f736d;
}}
:root[data-theme="dark"]{
  --m-ttfrozen:#1671f0; --m-tt3d:#b75c1c; --m-perpetua:#258d61; --m-longcontext:#ad32d6;
  --m-muted:#6f736d;
}
li.fx{margin:0 0 4px;list-style:none;margin-left:-20px}
details.finding{border-left:2px solid var(--line);padding-left:10px}
details.finding[open]{border-left-color:var(--s1)}
details.finding summary{cursor:pointer;font-weight:650;color:var(--ink);line-height:1.45;padding:2px 0}
details.finding summary::marker{color:var(--muted)}
details.finding .fbody{padding:4px 0 8px;color:var(--ink2)}
.allfind{display:inline-flex;align-items:center;gap:7px;font-size:12.5px;color:var(--muted);cursor:pointer;margin:0 0 8px}
.resultblock{border-top:2px solid var(--rule);padding-top:18px;margin:0 0 34px}
.rtitle{font-family:inherit;font-size:20px;line-height:1.3;margin:0 0 6px;max-width:66ch;font-weight:700;text-wrap:balance}
.rblurb{font-size:15px;color:var(--ink2);max-width:70ch;margin:0 0 18px}
details.morec{margin-top:10px;border-left:2px solid var(--line);padding-left:12px}
details.morec summary{cursor:pointer;color:var(--muted);font-size:13px;padding:4px 0}
details.morec[open]{border-left-color:var(--s1)}
.claimlist{max-width:78ch;padding-left:1.35em;margin:10px 0 22px}
.claimlist li{margin:0 0 7px;font-size:15.5px;line-height:1.5}
.claimlist a{color:var(--ink);text-decoration:none;border-bottom:1px solid var(--line)}
.claimlist a:hover{border-bottom-color:var(--s1)}
.claim{border-top:1px solid var(--line);padding-top:16px;margin:0 0 26px;scroll-margin-top:12px}
.claim h3{display:flex;gap:10px;align-items:baseline;font-size:17px;line-height:1.4;margin:0 0 4px;max-width:74ch;font-weight:650}
.claim .cnum{flex:0 0 auto;font-size:13px;color:#fff;background:var(--s1);border-radius:50%;width:22px;height:22px;display:inline-flex;align-items:center;justify-content:center;font-weight:700}
.claim .cmeta{margin:0 0 10px;font-size:12px;color:var(--muted)}
.claim .cbody{max-width:620px}
.claim .cbody svg{width:100%;height:auto;display:block}
.claim .cnums{margin-top:8px;font-size:12.5px}
.claim .cnums summary{cursor:pointer;color:var(--muted)}
.claim .cnums table{margin-top:8px;max-width:680px}
.claim .pcap{margin:0 0 8px;font-size:13.5px;color:var(--ink2);max-width:66ch}
.claim .pmeta{margin:6px 0 0;font-size:11.5px;color:var(--muted)}
.claim .cbody svg{max-width:100%}
.csupport{margin-top:14px;padding-top:10px;border-top:1px dashed var(--line);max-width:620px}
.csuphead{margin:0 0 6px;font-size:12.5px;color:var(--muted);font-weight:600}
.panelgrid{display:grid;grid-template-columns:repeat(auto-fit,minmax(330px,1fr));gap:14px;margin:12px 0 22px}
.panelgrid .pnl{margin:0;padding:12px 14px 10px}
.pnl h3{margin:0 0 4px;font-size:15px}
.pnl .pcap{margin:0 0 8px;font-size:13px;color:var(--ink2);max-width:60ch}
.pnl svg{width:100%;height:auto;display:block}
.pnl .pmeta{margin:6px 0 0;font-size:11.5px;color:var(--muted);line-height:1.45}
.plegend{display:flex;flex-wrap:wrap;gap:4px 12px;margin:0 0 6px}
.plegend .pl{display:inline-flex;align-items:center;gap:5px;font-size:12px;color:var(--ink2)}
.plegend .pl i{width:14px;height:3px;border-radius:2px;display:inline-block}
.panelpick{display:flex;flex-wrap:wrap;gap:8px 20px;margin:8px 0 4px;font-size:12.5px}
.pgroup{display:flex;flex-direction:column;gap:2px}
.pgroup b{font-size:11px;text-transform:uppercase;letter-spacing:.04em;color:var(--muted)}
.pchip{display:flex;align-items:center;gap:6px;color:var(--ink2);cursor:pointer}
@media (max-width:700px){ .panelgrid{grid-template-columns:1fr} }
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

<!-- THE ONE-MINUTE SUMMARY IS HAND-WRITTEN, AND ITS FIGURES ARE TYPED ON PURPOSE.
     Everything else on this page computes its numbers from story_data.json / story_extra.json. This block does
     not, by design: it is prose meant to be read first, and it was written against runs that have all finished,
     so the figures cannot drift underneath it. The typed figures are:
       ~45% to 80-85%   lead-up climb of the timetables          (see panel A / claim 1)
       "about 85% sure" the LLM memories' stated confidence      (see panel K / claim 4)
       "by a quarter"   their accuracy fall at the shift         (see claim 3's numbers table)
       70% and 41%      the 3-day timetable's hand-over and wrong-when-answered rates on the first sick
                        days                                     (see claim 6; EXTRA.deferral_live.memories.tt3d.per_day)
     IF ANY ARM IS EVER RE-RUN, re-check these four against the charts named beside them before publishing.
     Do not add new figures here without adding them to this list. (Convention agreed 22 Sept: the risk is not
     typed numbers as such, it is typed numbers that LOOK computed -- see uq/problems_found.md 11:35.) -->
<div class="panel" id="oneminute" style="margin-block:14px 6px;background:var(--panel);border:1px solid var(--line);border-left:4px solid var(--s3);padding:14px 16px">
  <h3 style="margin-bottom:6px">In one minute</h3>
  <p style="font-size:15.5px;color:var(--ink);max-width:74ch;margin:0 0 10px">A home robot is asked where everyday things are while people are using them, and learns the truth ten minutes later; it settles into a household's routine over two weeks, then one resident is off sick for ten days and their things move, then normal life resumes.</p>
  <p style="font-size:15.5px;color:var(--ink);max-width:74ch;margin:0 0 10px">Simple counting methods learn the routine well and break the moment it changes, and what they do next depends on how much they forget: a short memory re-learns the sick routine and then breaks again when normal life returns, a memory that never forgets stays wrong throughout but is right again immediately, and one that hedges between memory lengths avoids both breaks.</p>
  <p style="font-size:15.5px;color:var(--ink);max-width:74ch;margin:0 0 10px">Five kinds of language-model memory break by about as much, and left to work it out from evidence alone they never really learn the new routine. What looks like recovery is mostly same-day correction: ask about a thing for the first time that day, before the robot has been told where it actually was, and the apparent recovery largely disappears.</p>
  <p style="font-size:15.5px;color:var(--ink);max-width:74ch;margin:0 0 10px">One sentence telling the robot what changed is worth more than a week of evidence to a plain buffer, and it is applied only to the things belonging to the person who is ill. The same sentence costs them when it is never taken back: they keep believing the old story after life returns to normal, and for the memory that looks things up by time of day that cost is still there a week later. The memory that already writes itself a nightly note of its own mistakes gains nothing measurable from being told — it was recording the same thing already.</p>
  <p style="font-size:15.5px;color:var(--ink);max-width:74ch;margin:0 0 10px">None of them knows any of this is happening: whatever the day, all five report themselves about 85% sure while the share they answer correctly falls by a quarter, so a robot deciding when to ask for help cannot tell from its own confidence that the world has changed. The counting methods' confidence does move with the stage, which looks like an advantage until it is priced: put through the same answer-or-ask gate, the 3-day timetable is the <em>worst</em> of them all on the first sick days, handing back 70% of the questions and still getting 41% of the rest wrong. Only once it has re-learned the new routine does it become the one method that keeps its promise.</p>
  <p style="font-size:15.5px;color:var(--ink2);max-width:74ch;margin:0">Two things did not work and are reported as such: a different disruption, friends over every evening, barely troubles these methods because it only moves things for part of the day; and two findings written up earlier in the night were withdrawn once more households showed them to be noise, which is why every comparison here carries the disagreement between households beside it.</p>
</div>

<h2>What we found</h2>
<p style="max-width:74ch">Three results. Each opens with what it says and the one graph that shows it; the supporting results and all the numbers are folded underneath. Scroll once and open nothing and you have the three statements and the three graphs.</p>
<ol class="claimlist" id="claimlist"></ol>
<div id="claimgraphs"></div>

<div class="panel" id="gist" style="margin-block:6px 18px;border-left:4px solid var(--s1)">
  <h3 style="display:flex;justify-content:space-between;gap:12px;flex-wrap:wrap"><span>Every finding, in full</span><span class="muted" style="font-weight:400" id="gistwhen"></span></h3>
  <p class="note" style="margin:0 0 4px">The claims above, each with the numbers and the caveats behind it. Every one is closed; open the ones you want, or all of them at once.</p>
  <label class="allfind"><input type="checkbox" id="findall"> show the numbers behind each finding</label>
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

<h2>The rest of the panels</h2>
<p>The library: every panel we built, including the ones above. Each is at most four lines and answers one question. The day axis, the shaded sick spell and the scale are the same in every one, so two panels can be read side by side. The shaded band around each line is ±1 standard error across households — the same bar the comparisons in “What we found” are judged on; the spread between households is in the hover.</p>
<div class="controls" id="panelcontrols">
  <label>questions <select id="psplit"><option value="all">all questions</option><option value="cold">cold questions (first about a thing that day)</option><option value="moved">only objects that moved since the night round</option></select></label>
  <label>show <select id="pflavour"><option value="acc">accuracy</option><option value="conf">stated confidence</option></select></label>
  <button type="button" id="pall">show every panel</button>
  <button type="button" id="pdef">back to the four</button>
</div>
<div id="panelpick" class="panelpick"></div>
<div id="panelgrid" class="panelgrid"></div>

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
<div id="gatecharts"></div>
<details style="margin-top:6px"><summary class="muted" style="cursor:pointer;font-size:12.5px">the same numbers as a table (reference version)</summary>
<div class="tbl"><table id="askgatetable"></table></div>
<p class="note" id="askgatenote"></p></details>
<h3 style="margin-top:18px">What one sentence is worth, every comparison at once</h3>
<p class="note">Every told-vs-untold contrast on the page, in two pictures. Each is a paired measurement: the difference on the SAME household between the two runs, averaged over the households both arms covered. The older grid of numbers is still below, behind the disclosure, as the reference version.</p>
<div id="effectschart"></div>

<h3 style="margin-top:18px">LLM arms — two ways of reading its confidence, and sets on its own answer</h3>
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

function daily(reg, key, split){ // -> {mean, sd, n, k:[households contributing that day]} across households
  const R = DATA[reg]; const A = R.agents[key]; if(!A) return null;
  const nd = R.days; const mean=[], sd=[], nn=[], kk=[];
  for(let d=1; d<nd; d++){ const vals=[]; let N=0;
    for(const hh of Object.keys(A)){ const [n,ok]=A[hh][split][d]; if(n>=3){ vals.push(100*ok/n); N+=n; } }
    if(!vals.length){mean.push(null); sd.push(null); nn.push(0); kk.push(0); continue}
    const m = vals.reduce((a,b)=>a+b,0)/vals.length; const s = vals.length>1? Math.sqrt(vals.reduce((a,b)=>a+(b-m)**2,0)/(vals.length-1)) : 0;
    if(N<MIN_N){ mean.push(null); sd.push(null); nn.push(N); kk.push(vals.length); continue; }   // thin tail: keep n for the tooltip, draw nothing
    mean.push(m); sd.push(s); nn.push(N); kk.push(vals.length);
  } return {mean, sd, n:nn, k:kk};
}
function dailyConf(reg, key, split){ // -> {mean, sd, n, k} across households, from sum_conf/n per household
  const R = DATA[reg]; const A = R.agents[key]; if(!A) return null;
  const nd = R.days; const mean=[], sd=[], nn=[], kk=[];
  for(let d=1; d<nd; d++){ const vals=[]; let N=0;
    for(const hh of Object.keys(A)){ const [n,ok,sc]=A[hh][split][d]; if(n>=3){ vals.push(100*sc/n); N+=n; } }
    if(!vals.length){mean.push(null); sd.push(null); nn.push(0); kk.push(0); continue}
    const m = vals.reduce((a,b)=>a+b,0)/vals.length; const s = vals.length>1? Math.sqrt(vals.reduce((a,b)=>a+(b-m)**2,0)/(vals.length-1)) : 0;
    if(N<MIN_N){ mean.push(null); sd.push(null); nn.push(N); kk.push(vals.length); continue; }   // thin tail: keep n for the tooltip, draw nothing
    mean.push(m); sd.push(s); nn.push(N); kk.push(vals.length);
  } return {mean, sd, n:nn, k:kk};
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
  renderGap(); renderGapConformal(); renderAskgate(); renderGate(); renderEffects(); renderKnowno();
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
$("#gapreg").addEventListener("change",e=>{ state.gapReg=e.target.value; renderGap(); renderGapConformal(); renderAskgate(); renderGate(); renderKnowno(); });
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
  const idx = mode==="raw" ? 2 : 3; const nd = G.days; const mean=[], sd=[], nn=[], kk=[];
  for(let d=1; d<nd; d++){ const vals=[]; let N=0;
    for(const hh of Object.keys(M.cells)){ const c=M.cells[hh][d]; if(!c || c[0]<3) continue; vals.push(100*(c[idx]-c[1])/c[0]); N+=c[0]; }
    if(!vals.length){ mean.push(null); sd.push(null); nn.push(0); kk.push(0); continue; }
    const m=vals.reduce((a,b)=>a+b,0)/vals.length; const s=vals.length>1? Math.sqrt(vals.reduce((a,b)=>a+(b-m)**2,0)/(vals.length-1)):0;
    if(N<MIN_N){ mean.push(null); sd.push(null); nn.push(N); kk.push(vals.length); continue; }   // thin tail: keep n for the tooltip, draw nothing
    mean.push(m); sd.push(s); nn.push(N); kk.push(vals.length);
  } return {mean, sd, n:nn, k:kk};
}
function gapSeries(){
  const reg=state.gapReg, mode=state.gapMode; const G = EXTRA.gap && EXTRA.gap.populations[reg]; if(!G) return [];
  const base = SERIES.filter(s=>state.on.has(s.k) && G.methods[s.k] && !G.methods[s.k].live);
  let out = base.map(s=>({s, key:s.k, dash:false}));
  if(reg==="partial"){ for(const s of base){ for(const ck of (GAP_COMPANION[s.k]||[])){ if(G.methods[ck]) out.push({s:gapSeriesInfo(ck), key:ck, dash:false}); } } }
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
// ---------------------------------------------------------------------------------------------------------------
// Small-multiple panels. Each is at most four lines and answers one question. Bands are +-1 STANDARD ERROR across
// households (sd/sqrt(k)), matching the bar the paired contrasts are judged on; the per-day sd is kept in the hover.
// The day axis, the sick-spell shading and the y range are identical in every panel so they can be read side by side.
// The four methods the page is a comparison between. Everything else is secondary: muted, thinner, and off by
// default. A method keeps its colour whether it appears in one chart or ten.
const FOCUS = ["ttfrozen", "tt3d", "perpetua", "longcontext"];
const METHOD_COLOR = {
  ttfrozen:"--m-ttfrozen", tt3d:"--m-tt3d", perpetua:"--m-perpetua", longcontext:"--m-longcontext",
};
// a line names its method; the colour follows from that and nothing picks its own
function methodOf(key){
  const k = String(key).split(":").pop().replace(/^llm_/, "").replace(/_(nomsg|startmsg|startend)$/, "");
  return k;
}
function colorFor(key){ return METHOD_COLOR[methodOf(key)] || "--m-muted"; }
function isFocus(key){ return FOCUS.includes(methodOf(key)); }
const PANEL_SPLIT_LABEL = {all:"all questions", cold:"cold questions — the first question about a thing each day, before that day's feedback", moved:"only objects that had moved since the night round"};
const PANELS = [
  {id:"A", group:"The simple learners", title:"How much should a simple learner forget?", pop:"person",
   cap:"Learn, break, re-learn, break again — and the longer the memory, the BIGGER the first break and the smaller the second: never-forgets drops 31 points and is right again at once, the 1-day memory drops 14 and breaks a second time.",
   lines:[{key:"ttfrozen", label:"never forgets"},{key:"tt3d", label:"3-day memory"},{key:"tt1d", label:"1-day memory"},{key:"lastseen", label:"last seen"}]},
  {id:"C", group:"The LLM memories", title:"LLM memories, nobody tells them anything", pop:"person",
   cap:"Every memory breaks on the first sick day. On cold questions — the honest measure — the buffer and retrieval are still more than 30 points below their own lead-up after a week of the new routine.",
   note:"Long-context is not here: it ran on 3 households, a different sample.",
   lines:[{key:"person:llm_naive_nomsg", label:"buffer"},{key:"person:llm_retrieval_nomsg", label:"retrieval"},{key:"person:llm_reflect_nomsg", label:"reflection"},{key:"person:llm_routine7_nomsg", label:"nightly routine table"}]},
  {id:"C2", group:"The LLM memories", title:"What looks like recovery, and what is actually re-learned", pop:"person",
   cap:"Each colour is one memory, twice: solid = scored on every question, dashed = scored only on the first question about a thing each day. The gap between the two is same-day correction — the robot is told where the thing was ten minutes after each question, and the later questions ride on that. Inside the sick spell the upper line climbs back toward its old level while the lower one does not: the buffer answers 66% of all questions but only 41% of cold ones, against a lead-up of 75% — and retrieval 64% against 43%, from a lead-up of 79%. Solid and dashed are distinguishable without colour, so the pairing survives a greyscale print.",
   lines:[{key:"person:llm_naive_nomsg", label:"buffer — every question", split:"all", col:"--s1"},{key:"person:llm_naive_nomsg", label:"buffer — cold questions only", split:"cold", col:"--s1", tint:true},{key:"person:llm_retrieval_nomsg", label:"retrieval — every question", split:"all", col:"--s5"},{key:"person:llm_retrieval_nomsg", label:"retrieval — cold questions only", split:"cold", col:"--s5", tint:true}]},
  {id:"E", group:"What a message does", title:"What a message does to a plain buffer", pop:"person",
   cap:"One sentence buys back most of the break — and costs on the first days back, unless it is retracted.",
   lines:[{key:"person:llm_naive_nomsg", label:"no message"},{key:"person:llm_naive_startmsg", label:"start message"},{key:"person:llm_naive_startend", label:"start + end messages"}]},
  {id:"F", group:"What a message does", title:"What a message does to retrieval", pop:"person",
   cap:"The same sentence, on the memory that looks things up by the same time of day. It buys as much as it does for the buffer — and its cost outlasts the buffer's by a week, because the same-hour lookup keeps handing back sick-day sightings after a recency buffer has dropped them.",
   lines:[{key:"person:llm_retrieval_nomsg", label:"no message"},{key:"person:llm_retrieval_startmsg", label:"start message"},{key:"person:llm_retrieval_startend", label:"start + end messages"}]},
  {id:"G", group:"What a message does", title:"What a message does to the nightly routine table", pop:"person",
   cap:"The same three arms on the memory that rewrites a routine table each night. It gains least of the three, because it learned the lead-up least.",
   lines:[{key:"person:llm_routine7_nomsg", label:"no message"},{key:"person:llm_routine7_startmsg", label:"start message"},{key:"person:llm_routine7_startend", label:"start + end messages"}]},
  {id:"H", group:"Special populations", title:"Whose things does the message move?", pop:"partial", stagesFrom:"person",
   cap:"One resident is off sick; the robot is asked about everyone's things. Colour is whose things the question was about, and the dashed line is the same run told \u201cYuki is home sick today\u201d. On the sick resident's things the two lines separate the moment the message arrives. On the other resident's they stay together — until the return, when the message is stale and nobody has taken it back.",
   lines:[{src:"owner", key:"llm_naive_nomsg", group:"sick", label:"sick resident's things, no message", col:"--s1"},
          {src:"owner", key:"llm_naive_startmsg", group:"sick", label:"sick resident's things, told", col:"--s1", tint:true},
          {src:"owner", key:"llm_naive_nomsg", group:"others", label:"other resident's things, no message", col:"--s5"},
          {src:"owner", key:"llm_naive_startmsg", group:"others", label:"other resident's things, told", col:"--s5", tint:true}]},
  {id:"ACC4", group:"The four we compare", title:"How often each of the four is right", pop:"person",
   cap:"The four methods the rest of this page compares, on accuracy alone. Perpetua* sits below both timetables through the settled fortnight \u2014 it is the weakest forecaster of the four \u2014 which is the half of the next claim a reader has to be able to see rather than take on trust.",
   lines:[{key:"ttfrozen", label:"never-forgets timetable"},
          {key:"tt3d", label:"3-day timetable"},
          {key:"perpetua", label:"Perpetua*"},
          {key:"person:llm_longcontext_nomsg", label:"long-context (3 households)"}]},
  {id:"L", group:"The LLM memories", title:"Given ten days of the new routine, who learns it?", pop:"person",
   cap:"From the first sick days to the end of the spell, every method is living in the new routine and getting corrected on every question. The counter learns it. The language memories barely move.",
   lines:[{key:"tt3d", label:"3-day timetable"},
          {key:"person:llm_naive_nomsg", label:"recency buffer"},
          {key:"person:llm_retrieval_nomsg", label:"retrieval"},
          {key:"person:llm_reflect_nomsg", label:"reflection"}]},
  {id:"D", group:"The LLM memories", title:"Long-context memory on its own", pop:"person",
   cap:"The whole log in every prompt, on three households — too few to settle most questions, and about ten times the compute per question of the others. Shown on its own because it is a different sample from every other LLM panel and must not be read beside them.",
   note:"3 households only — indicative, not settled.",
   lines:[{key:"person:llm_longcontext_nomsg", label:"no message"},{key:"person:llm_longcontext_startmsg", label:"start message"},{key:"person:llm_longcontext_startend", label:"start + end messages"}]},
  {id:"B", group:"The simple learners", title:"One representative per family", pop:"person",
   cap:"Four different ways of counting. The time-of-day timetable is the only one that really learns this routine. Periodic persistence looks unbreakable only because it never learned much to break: it sits below every timetable in the lead-up and takes a 7-point break where the 3-day timetable takes 23 — but on cold questions it falls to 23% against that timetable's 47%. A caution about all-questions views generally: switch the control above to cold questions and its flatness disappears.",
   lines:[{key:"tt3d", label:"timetable, 3-day"},{key:"mf3d", label:"most frequent, 3-day"},{key:"periodic", label:"periodic persistence"},{key:"perpetua", label:"Perpetua*"}]},
  {id:"I", group:"Special populations", title:"When the same week comes back", pop:"person2x",
   cap:"Two sick spells with a normal week between them. The second break costs these learners almost nothing: nothing during normal days ever overwrites the sick-day habit at those hours.",
   lines:[{key:"tt3d", label:"timetable, 3-day"},{key:"tt1d", label:"timetable, 1-day"},{key:"ttfrozen", label:"never forgets"}]},
  {id:"J", group:"The simple learners", title:"Does anything notice?", pop:"person",
   cap:"A learner that resets when it detects a change recovers inside the spell and again on the return; one that only hedges does neither as sharply.",
   lines:[{key:"tt3d", label:"3-day timetable"},{key:"detector3d", label:"3-day + change alarm, with reset"},{key:"bma", label:"hedge over memory lengths"},{key:"ttfrozen", label:"never forgets"}]},
  {id:"K", group:"The LLM memories", title:"Confidence, flat against moving", pop:"person", flavour:"conf",
   cap:"The three LLM memories claim the same confidence through the break; the counter's tracks the stage.",
   lines:[{key:"person:llm_naive_nomsg", label:"buffer"},{key:"person:llm_retrieval_nomsg", label:"retrieval"},{key:"person:llm_routine7_nomsg", label:"nightly routine table"},{key:"tt3d", label:"3-day timetable"}]},
];
const PANEL_DEFAULT = ["A","C","E","K"];
const panelState = {on:new Set(PANEL_DEFAULT), split:"all", flavour:"acc"};

function cellsOf(p, line){           // -> {cells:{hh:{split:[[n,ok,sum_conf],..]}}, nd} for one line of one panel
  if(line.src==="owner"){
    const A = (EXTRA.owner_split_live && EXTRA.owner_split_live[p.pop] && EXTRA.owner_split_live[p.pop][line.key]) || null;
    if(!A || !A.cells_by_group) return null;
    return {cells:A.cells_by_group[line.group], nd:A.n_days};
  }
  const R = DATA[p.pop]; if(!R || !R.agents[line.key]) return null;
  return {cells:R.agents[line.key], nd:R.days};
}
function panelSeries(p, line, flavour, split){   // -> {mean, se, sd, n, k} per day, or null
  const C = cellsOf(p, line); if(!C) return null;
  if(line.split) split = line.split;              // a line that pins its own split (the cold-gap panel)
  const mean=[], se=[], sd=[], nn=[], kk=[];
  for(let d=1; d<C.nd; d++){
    const vals=[]; let N=0;
    for(const hh of Object.keys(C.cells)){
      const row = C.cells[hh][split] || C.cells[hh]["all"]; const c = row && row[d];
      if(!c || c[0]<3) continue;
      vals.push(flavour==="conf" ? 100*c[2]/c[0] : 100*c[1]/c[0]); N+=c[0];
    }
    if(!vals.length || N<MIN_N){ mean.push(null); se.push(null); sd.push(null); nn.push(N); kk.push(vals.length); continue; }
    const m = vals.reduce((a,b)=>a+b,0)/vals.length;
    const sdv = vals.length>1 ? Math.sqrt(vals.reduce((a,b)=>a+(b-m)**2,0)/(vals.length-1)) : 0;
    mean.push(m); sd.push(sdv); se.push(vals.length>1? sdv/Math.sqrt(vals.length) : 0); nn.push(N); kk.push(vals.length);
  }
  return {mean, se, sd, n:nn, k:kk};
}
function panelHH(p){                 // households behind the panel, for its caption
  let best=0; for(const line of p.lines){ const C=cellsOf(p,line); if(C) best=Math.max(best, Object.keys(C.cells).length); } return best;
}
const POP_LABEL = {person:"one person sick, that person's things", person2x:"one person sick, twice", household:"everyone sick", partial:"one person sick, everyone's things asked"};

function drawPanel(p){
  const flavour = p.flavour || panelState.flavour;
  const split = panelState.split;
  const W=400, H=232, L=32, Rr=10, T=10, B=26;
  const nd = (()=>{ const C=cellsOf(p,p.lines[0]); return C? C.nd : 32; })();
  const x = d => L + (d-1)*(W-L-Rr)/Math.max(1,(nd-2));
  const y = v => T + (100-v)*(H-T-B)/100;
  let g = "";
  // Stage shading, from the population's own stage map so two-spell panels shade both spells. The owner-split
  // population ("partial") has no DATA entry of its own -- it is extracted per arm, not per regime -- but it runs
  // the SAME 32-day calendar as "person", so it borrows that stage map. Without this the panel silently loses its
  // shading and stops being readable beside the others.
  const R = DATA[p.pop] || DATA[p.stagesFrom || "person"];
  if(R && R.stages){ let cur=null;
    for(let d=1; d<nd; d++){ const st=R.stages[String(d)]||"plain";
      if(!cur||cur.name!==st){ if(cur) g+=stageRect(cur); cur={name:st,a:d,b:d}; } else cur.b=d; }
    if(cur) g+=stageRect(cur);
  }
  function stageRect(c){ const f=STAGE_FILL[c.name]; if(!f) return "";
    return `<rect x="${x(c.a).toFixed(1)}" y="${T}" width="${(x(c.b+1)-x(c.a)).toFixed(1)}" height="${H-T-B}" fill="var(${f})" opacity="0.5"/>`; }
  for(const v of [0,25,50,75,100]) g += `<line x1="${L}" y1="${y(v).toFixed(1)}" x2="${W-Rr}" y2="${y(v).toFixed(1)}" stroke="var(--line)" stroke-width="1"/><text x="${L-5}" y="${(y(v)+3.5).toFixed(1)}" text-anchor="end" font-size="9" fill="var(--muted)">${v}</text>`;
  for(const d of [1,7,14,21,28,35,41].filter(d=>d<nd)) g += `<text x="${x(d).toFixed(1)}" y="${H-9}" text-anchor="middle" font-size="9" fill="var(--muted)">${d}</text>`;
  const cols = ["--s1","--s3","--s5","--s7"];
  const drawn = [];
  p.lines.forEach((line,i)=>{
    const S = panelSeries(p, line, flavour, split); if(!S) return;
    const col = line.col || colorFor(line.key);
    const focus = line.col ? true : isFocus(line.key);
    // A pair of lines about the SAME method (all questions against cold, say) is distinguished by lightness on
    // one hue, never by a dash: dashes on this page mean "annotation", not "identity".
    const tint = !!line.tint;
    let band="", path="", pen=false;
    for(let j=0;j<S.mean.length;j++){ const d=j+1; if(S.mean[j]==null){ pen=false; continue; }
      path += (pen? " L ":" M ") + x(d).toFixed(1) + " " + y(S.mean[j]).toFixed(1); pen=true; }
    // +-1 standard error ribbon, drawn as a closed polygon over each unbroken run
    let run=[];
    const flush=()=>{ if(run.length>1){ const up=run.map(([d,m,e])=>`${x(d).toFixed(1)},${y(Math.min(100,m+e)).toFixed(1)}`);
        const dn=run.slice().reverse().map(([d,m,e])=>`${x(d).toFixed(1)},${y(Math.max(0,m-e)).toFixed(1)}`);
        band += `<polygon points="${up.concat(dn).join(" ")}" fill="var(${col})" opacity="0.13"/>`; } run=[]; };
    for(let j=0;j<S.mean.length;j++){ if(S.mean[j]==null){ flush(); continue; } run.push([j+1,S.mean[j],S.se[j]||0]); }
    flush();
    g += band + `<path d="${path}" fill="none" stroke="var(${col})" stroke-width="${focus?2.4:1.4}" stroke-linejoin="round" opacity="${tint?0.45:(focus?1:0.75)}"/>`;
    drawn.push({label:line.label, col, S, tint});
  });
  const legend = drawn.map(d=>`<span class="pl"><i style="background:var(${d.col});opacity:${d.tint?0.45:1}"></i>${d.label}</span>`).join("");
  const hh = panelHH(p);
  const missing = p.lines.length - drawn.length;
  return `<div class="panel pnl" data-pid="${p.id}">
    <h3>${p.title}</h3>
    <p class="pcap">${p.cap}</p>
    <div class="plegend">${legend}</div>
    <svg viewBox="0 0 ${W} ${H}" role="img" aria-label="${p.title}" data-pid="${p.id}"></svg>
    <p class="pmeta">${flavour==="conf"?"Stated confidence":"Accuracy"}, ${PANEL_SPLIT_LABEL[split]} · ${hh} household${hh===1?"":"s"} · ${POP_LABEL[p.pop]||p.pop} · shaded band = ±1 standard error across households${p.note? " · "+p.note : ""}${missing? ` · <b>${missing} line(s) have no data in this split</b>`:""}</p>
  </div>`.replace("></svg>", `>${g}</svg>`);
}
// ---------------------------------------------------------------------------------------------------------------
// The numbered series at the top of the page: a claim, its graph, the numbers behind it, in that order, repeated.
// Every claim states a result in one sentence and carries no plus-or-minus figures; the numbers sit behind a
// CLOSED disclosure under its own graph. A reader who opens nothing still gets every claim and sees it shown.
// Three results, in the order they matter. Each claim names the result it belongs to and whether it is that
// result's lead graph - the one thing visible before a reader opens anything.
const RESULTS = [
  {id:"lost", title:"When the routine changes, the robot cannot tell that it is lost",
   blurb:"It answers on regardless. The signal it would use to decide when to hand a question over stops working at exactly the moment the world stops matching what it learned."},
  {id:"learn", title:"These memories learn a household routine and break when it changes",
   blurb:"The counters climb back over the following days. The language memories, given the same ten days of the new routine and corrected on every question, barely move."},
  {id:"told", title:"One sentence of explanation is worth more than a week of corrections",
   blurb:"And a sentence nobody retracts costs you: the robot goes on believing it after it stops being true."},
];
const CLAIMS = [
  {n:1, panel:"A", result:"learn", lead:true, text:"Every method learns the household routine and breaks the day it changes — and how much it forgets decides what happens next."},
  {n:2, panel:"L", result:"learn", text:"Given ten days of the new routine to learn from, the counter learns it and the language memories barely move."},
  {n:3, panel:"E", result:"told", lead:true, text:"One sentence telling the robot what changed is worth more than a week of evidence — and costs it when nobody takes the sentence back."},
  {n:4, panel:"F", result:"told", text:"That sentence costs a memory that looks things up by time of day far longer than it costs a plain buffer."},
  {n:5, panel:"K", also:"channels", result:"lost", text:"What the robot needs in order to know when to hand a question over is not in these confidence numbers — even a bar chosen with hindsight does no better."},
  {n:6, custom:"defer", result:"lost", lead:true, text:"Every method knows when to ask for help while nothing is changing \u2014 and stops knowing at the one moment it needs to."},
  {n:7, custom:"perpetua", result:"lost", text:"One method keeps its judgement through the change. It is the least accurate of the three \u2014 being right and knowing when you are wrong turn out to be separable."},
];
const WIN5 = [["lead","lead-up 9–13"],["d14_16","first sick days 14–16"],["d17_23","rest of spell 17–23"],["d24_26","first days back 24–26"],["d27_31","rest of return 27–31"]];
const WIN5_DAYS = {lead:[9,10,11,12,13], d14_16:[14,15,16], d17_23:[17,18,19,20,21,22,23], d24_26:[24,25,26], d27_31:[27,28,29,30,31]};

function claimNumbers(p, split, flavour){
  const head = `<tr><th>line</th>` + WIN5.map(([,l])=>`<th class="num">${l}</th>`).join("") + `</tr>`;
  let rows = "";
  for(const line of p.lines){
    const C = cellsOf(p, line); if(!C) continue;
    const val = w => { let n=0, ok=0, sc=0;
      for(const hh of Object.keys(C.cells)){ const arr=C.cells[hh][split]||C.cells[hh]["all"];
        for(const d of WIN5_DAYS[w]){ const c=arr&&arr[d]; if(!c) continue; n+=c[0]; ok+=c[1]; sc+=c[2]; } }
      return n>=MIN_N ? (flavour==="conf"? 100*sc/n : 100*ok/n) : null; };
    rows += `<tr><td>${line.label}</td>` + WIN5.map(([w])=>{ const v=val(w); return `<td class="num">${v==null?"–":v.toFixed(0)}</td>`; }).join("") + `</tr>`;
  }
  return `<table>${head}${rows}</table>`;
}
// Claim 7's graph: search cost, at a MATCHED lead-day ask rate. Matching is the whole point -- the hedge's raw
// advantage was a confidence-scale confound (it asked 68% of the time on lead days), so an unmatched comparison
// says nothing. Order puts "notices and resets" next to "notices but does not act", because that pair is the claim.
const PLAN_ORDER = [
  {k:"none_tt72", label:"3-day timetable", sub:"does not notice"},
  {k:"mart_tt72", label:"3-day + change alarm", sub:"notices AND resets"},
  {k:"bma_tt",    label:"hedge over memory lengths",        sub:"notices, does not act"},
  {k:"none_tt",   label:"never-forgets timetable",          sub:"does not notice"},
];
function drawPlanningBars(){
  const P = EXTRA.planning_matched; if(!P) return "";
  const rows = PLAN_ORDER.map(o=>({...o, v:(P.rows[o.k]||{}).sick, lead:(P.rows[o.k]||{}).lead})).filter(r=>r.v!=null);
  if(!rows.length) return "";
  const W=600, rowH=46, T=16, L=200, H=T+rows.length*rowH+34;
  const max = Math.max(...rows.map(r=>r.v))*1.15;
  const x = v => L + v*(W-L-16)/max;
  let g="";
  for(const t of [0,1,2,3]){ if(t>max) continue;
    g += `<line x1="${x(t).toFixed(1)}" y1="${T-4}" x2="${x(t).toFixed(1)}" y2="${T+rows.length*rowH}" stroke="var(--line)" stroke-width="1"/>`
      +  `<text x="${x(t).toFixed(1)}" y="${T+rows.length*rowH+14}" text-anchor="middle" font-size="10" fill="var(--muted)">${t}</text>`; }
  rows.forEach((r,i)=>{
    const y0 = T + i*rowH + 7, bh = 20;
    const best = r.k==="mart_tt72";
    g += `<text x="${L-10}" y="${(y0+9).toFixed(1)}" text-anchor="end" font-size="11.5" fill="var(--ink)">${r.label}</text>`
      +  `<text x="${L-10}" y="${(y0+22).toFixed(1)}" text-anchor="end" font-size="10" fill="var(--muted)">${r.sub}</text>`
      +  `<rect x="${L}" y="${y0}" width="${(x(r.v)-L).toFixed(1)}" height="${bh}" rx="3" fill="var(${best?'--s3':'--s1'})" opacity="${best?1:0.55}"/>`
      +  `<text x="${(x(r.v)+6).toFixed(1)}" y="${(y0+14).toFixed(1)}" font-size="11.5" font-weight="${best?700:400}" fill="var(--ink)">${r.v.toFixed(2)}</text>`;
  });
  g += `<text x="${L}" y="${H-5}" font-size="10.5" fill="var(--muted)">places searched per question during the sick spell (lower is better)</text>`;
  return `<svg viewBox="0 0 ${W} ${H}" role="img" aria-label="search cost per method at a matched ask rate">${g}</svg>`;
}
// Claim 4, shown a second way: on a bounded list of days the same questions are asked three ways, and the three
// confidence channels are drawn against what the answer actually was. Accuracy is the heavy dark line; the three
// claims are the light ones. The point is the day-14 scissor -- accuracy halves, nothing it says about itself moves.
// Sampled days only (13/14/15/20/24/25/30), so points are marked and the axis is the same as every other panel.
function drawChannels(){
  const A = EXTRA.knowno_live && EXTRA.knowno_live.person && EXTRA.knowno_live.person.llm_naive_nomsg;
  if(!A || !A.days) return "";
  const days = Object.keys(A.days).map(Number).sort((a,b)=>a-b).filter(d=>A.days[String(d)].n>=MIN_N);
  if(days.length<3) return "";
  const W=400,H=232,L=32,Rr=10,T=10,B=26, nd=32;
  const x = d => L + (d-1)*(W-L-Rr)/(nd-2), y = v => T + (100-v)*(H-T-B)/100;
  let g="";
  const R=DATA.person;
  if(R&&R.stages){ let cur=null;
    const rect=c=>{const f=STAGE_FILL[c.name]; return f?`<rect x="${x(c.a).toFixed(1)}" y="${T}" width="${(x(c.b+1)-x(c.a)).toFixed(1)}" height="${H-T-B}" fill="var(${f})" opacity="0.5"/>`:"";};
    for(let d=1;d<nd;d++){const st=R.stages[String(d)]||"plain"; if(!cur||cur.name!==st){ if(cur) g+=rect(cur); cur={name:st,a:d,b:d}; } else cur.b=d;}
    if(cur) g+=rect(cur); }
  for(const v of [0,25,50,75,100]) g+=`<line x1="${L}" y1="${y(v).toFixed(1)}" x2="${W-Rr}" y2="${y(v).toFixed(1)}" stroke="var(--line)" stroke-width="1"/><text x="${L-5}" y="${(y(v)+3.5).toFixed(1)}" text-anchor="end" font-size="9" fill="var(--muted)">${v}</text>`;
  for(const d of [1,7,14,21,28]) g+=`<text x="${x(d).toFixed(1)}" y="${H-9}" text-anchor="middle" font-size="9" fill="var(--muted)">${d}</text>`;
  // The multiple-choice channel that used to be a fourth line here has been WITHDRAWN, not corrected: it offered
  // nine spots plus "somewhere else" and the model took the catch-all on 1480 of 1480 questions, so its number was
  // P(catch-all), mean 0.756. See uq/problems_found.md, 22 Sept.
  const SER=[{f:"verbal",label:"what it says when asked outright",col:"--s5",w:1.6},
             {f:"agree",label:"how often five samples agree",col:"--s7",w:1.6},
             {f:"acc",label:"how often it is actually right",col:"--s1",w:3}];
  const drawn=[];
  for(const sp of SER){
    let d0="", pts="";
    days.forEach((d,i)=>{ const v=A.days[String(d)][sp.f]; if(v==null) return;
      d0 += (i?" L ":" M ")+x(d).toFixed(1)+" "+y(v).toFixed(1);
      pts += `<circle cx="${x(d).toFixed(1)}" cy="${y(v).toFixed(1)}" r="${sp.w>2?3:2.4}" fill="var(${sp.col})"/>`; });
    g += `<path d="${d0}" fill="none" stroke="var(${sp.col})" stroke-width="${sp.w}" stroke-linejoin="round"/>`+pts;
    drawn.push(sp);
  }
  const legend = drawn.map(d=>`<span class="pl"><i style="background:var(${d.col});height:${d.w>2?4:3}px"></i>${d.label}</span>`).join("");
  return `<div class="csupport"><p class="csuphead">The same claim a second way: three ways of asking it how sure it is, against whether it was right</p>
    <p class="pcap">On a bounded list of days (13, 14, 15, 20, 24, 25, 30) the same questions are put two ways: asked outright, and asked five times at temperature 0.7 and scored on how often the answers agree. On the first sick day the heavy line halves, from ${A.days["13"].acc.toFixed(0)}% to ${A.days["14"].acc.toFixed(0)}%, and neither channel moves with it — they read ${A.days["14"].verbal.toFixed(0)}% and ${A.days["14"].agree.toFixed(0)}%. Self-agreement is the worse of the two: the model is most consistent exactly where it is most wrong. A third channel, a multiple choice scored on the letter's probability, has been withdrawn — it was measuring the probability of a catch-all &ldquo;somewhere else&rdquo; option that the model chose on every one of 1480 questions.</p>
    <div class="plegend">${legend}</div>
    <svg viewBox="0 0 ${W} ${H}" role="img" aria-label="three confidence channels against accuracy">${g}</svg>
    <p class="pmeta">${A.n_hh} households · buffer, no message · points are the sampled days only</p></div>`;
}
// The answer-or-ask gate, replacing its table. Two charts: how often it has to ask, and how often it is still
// wrong on what it does answer, with the 10% target it was set drawn as a reference. Plotted over the five
// windows rather than per day, because the gate is a sequential procedure whose rate over a single day would be
// a handful of decisions; the window is the resolution the number is computed at.
const GATE_ARMS = [
  {k:"llm_naive_nomsg", label:"buffer", col:"--m-muted"},
  {k:"llm_retrieval_nomsg", label:"retrieval", col:"--m-muted"},
  {k:"llm_reflect_nomsg", label:"reflection", col:"--m-muted"},
  {k:"llm_routine7_nomsg", label:"nightly routine table", col:"--m-muted"},
  {k:"tt3d", label:"3-day timetable", col:"--m-tt3d", classical:true},
];
function drawGate(field, target, yMax){
  const P = (EXTRA.llm_live && EXTRA.llm_live.person) || {};
  const ws = WIN5.map(([w])=>w);
  const C = EXTRA.classical_askgate || {};
  const series = GATE_ARMS.map(a=>({...a, vals: ws.map(w=>{ const src = a.classical? C[a.k] : P[a.k]; const G=(src||{}).askgate;
                                                            const v=G && G[w] && G[w][field]; return v==null? null : v; })}))
                          .filter(a=>a.vals.some(v=>v!=null));
  if(!series.length) return "";
  // fit the axis to the data instead of always drawing 0-100: the miss rates all sit under 30, and an axis three
  // times taller than the data hides exactly the differences the chart exists to show
  const top = yMax || Math.min(100, Math.max(25, Math.ceil(Math.max(...series.flatMap(a=>a.vals.filter(v=>v!=null)), target||0)/10)*10 + 10));
  const W=420,H=200,L=34,Rr=22,T=12,B=30;   // Rr leaves room for the last x label's half-width
  const x = i => L + i*(W-L-Rr)/(ws.length-1), y = v => T + (top-v)*(H-T-B)/top;
  const ticks = top<=40 ? [0,10,20,30,40].filter(t=>t<=top) : [0,25,50,75,100].filter(t=>t<=top);
  let g="";
  for(const v of ticks) g+=`<line x1="${L}" y1="${y(v).toFixed(1)}" x2="${W-Rr}" y2="${y(v).toFixed(1)}" stroke="var(--line)"/><text x="${L-5}" y="${(y(v)+3.5).toFixed(1)}" text-anchor="end" font-size="9" fill="var(--muted)">${v}</text>`;
  ["lead","14–16","17–23","24–26","27–31"].forEach((lab,i)=>
    g+=`<text x="${x(i).toFixed(1)}" y="${H-12}" text-anchor="middle" font-size="9" fill="var(--muted)">${lab}</text>`);
  if(target!=null){
    g+=`<line x1="${L}" y1="${y(target).toFixed(1)}" x2="${W-Rr}" y2="${y(target).toFixed(1)}" stroke="var(--ink2)" stroke-width="1.5" stroke-dasharray="5 4"/>`
     + `<text x="${L+3}" y="${(y(target)+11).toFixed(1)}" font-size="9.5" fill="var(--ink2)">${target}% target</text>`;
  }
  for(const a of series){
    let d="", pts="", pen=false;
    a.vals.forEach((v,i)=>{ if(v==null){ pen=false; return; }
      d += (pen?" L ":" M ")+x(i).toFixed(1)+" "+y(v).toFixed(1); pen=true;
      pts += `<circle cx="${x(i).toFixed(1)}" cy="${y(v).toFixed(1)}" r="2.6" fill="var(${a.col})"/>`; });
    g += `<path d="${d}" fill="none" stroke="var(${a.col})" stroke-width="${a.classical?2.8:2}" stroke-linejoin="round"/>`+pts;
  }
  const legend = series.map(a=>`<span class="pl"><i style="background:var(${a.col});height:${a.classical?4:3}px"></i>${a.label}</span>`).join("");
  return `<div class="plegend">${legend}</div><svg viewBox="0 0 ${W} ${H}" role="img" aria-label="ask gate ${field}">${g}</svg>`;
}
function renderGate(){
  const host=$("#gatecharts"); if(!host) return;
  const a=drawGate("ask_rate",null,100), b=drawGate("miss_rate",10);
  if(!a && !b){ host.innerHTML=""; return; }
  host.innerHTML = `<div class="panelgrid">
    <div class="panel pnl"><h3>How often it has to ask for help</h3>
      <p class="pcap">Each memory is allowed to answer only when it can be wrong no more than one time in ten; when its own stated confidence is too low it asks the resident instead. This is the share of questions it hands back.</p>${a}
      <p class="pmeta">Adaptive-conformal gate on each method's own stated confidence, target 10% wrong among what it answers · 10 households · no-message arms · plotted over the five windows, not per day, because the gate is a sequential procedure and a single day is only a handful of decisions — the window is the resolution the number is computed at</p></div>
    <div class="panel pnl"><h3>And how often it is wrong anyway</h3>
      <p class="pcap">Of the questions it did answer, the share it got wrong. The dashed line is the 10% it promised. Nearly every method sits above it in every window, furthest on the first sick days — the confidence the gate reads was not good enough to keep the promise. The counter is the surprise: its confidence <em>does</em> track the stage, but put through the same gate it is the worst of the lot at the break, missing 43% while asking 70% of the time. Tracking the stage and being usable at the moment it changes are not the same thing.</p>${b}
      <p class="pmeta">Same arms and windows · a point above the dashed line is a broken promise</p></div></div>`;
}
// The paired told-vs-untold contrasts as an effects chart instead of a grid of numbers. One row per comparison:
// a dot at the effect, a bar through it for +-1 standard error, a rule at zero. A bar that crosses zero is not a
// detected effect, and the reader sees that without doing arithmetic. Rows grouped by memory, n at the end.
const EFF_MEMS = [["naive","buffer"],["retrieval","retrieval"],["routine7","nightly routine table"],["reflect","reflection"],["longcontext","long-context"]];
function drawEffects(split){
  const P = (EXTRA.llm_live && EXTRA.llm_live.person) || {};
  const rows = [];
  for(const [mem,label] of EFF_MEMS){
    const arm = P[`llm_${mem}_startmsg`]; if(!arm || !arm.paired_vs_nomsg) continue;
    const group = [];
    for(const [w,wl] of WIN5.slice(1)){
      const v = arm.paired_vs_nomsg[w] && arm.paired_vs_nomsg[w][split];
      if(v) group.push({label:wl, v});
    }
    if(group.length) rows.push({mem:label, group});
  }
  if(!rows.length) return "";
  const all = rows.flatMap(r=>r.group.map(g=>g.v));
  const lim = Math.max(...all.map(v=>Math.abs(v.mean)+2*(v.se||0)), 10);
  const nRows = rows.reduce((a,r)=>a+r.group.length,0);
  const W=470, L=190, Rr=44, T=22, rowH=17, headH=15, H=T+nRows*rowH+rows.length*(headH+6)+18;
  const x = v => L + (v+lim)*(W-L-Rr)/(2*lim);
  let g="", yy=T;
  const step = lim>60? 40 : lim>30? 20 : 10;
  const ticks2 = []; for(let t=-Math.floor(lim/step)*step; t<=lim; t+=step) ticks2.push(t);
  for(const t of ticks2){
    g += `<line x1="${x(t).toFixed(1)}" y1="${T-8}" x2="${x(t).toFixed(1)}" y2="${H-16}" stroke="var(${t===0?'--ink2':'--line'})" stroke-width="${t===0?1.5:1}"/>`
      +  `<text x="${x(t).toFixed(1)}" y="${T-12}" text-anchor="middle" font-size="9" fill="var(--muted)">${t>0?"+":""}${t}</text>`;
  }
  for(const r of rows){
    g += `<text x="6" y="${(yy+10).toFixed(1)}" font-size="10.5" font-weight="650" fill="var(--ink)">${r.mem}</text>`;
    yy += headH;
    for(const it of r.group){
      const v=it.v, se=v.se||0, det=v.detected;
      const col = det ? (v.mean>0? "--s3" : "--s8") : "--muted";
      g += `<text x="${L-8}" y="${(yy+9).toFixed(1)}" text-anchor="end" font-size="9.5" fill="var(--muted)">${it.label}</text>`
        +  `<line x1="${x(v.mean-se).toFixed(1)}" y1="${(yy+5.5).toFixed(1)}" x2="${x(v.mean+se).toFixed(1)}" y2="${(yy+5.5).toFixed(1)}" stroke="var(${col})" stroke-width="2.5" stroke-linecap="round"/>`
        +  `<circle cx="${x(v.mean).toFixed(1)}" cy="${(yy+5.5).toFixed(1)}" r="3.4" fill="var(${col})"/>`
        +  `<text x="${W-Rr+6}" y="${(yy+9).toFixed(1)}" font-size="9" fill="var(--muted)">n=${v.n_hh}${v.small_n?"*":""}</text>`;
      yy += rowH;
    }
    yy += 6;
  }
  return `<svg viewBox="0 0 ${W} ${H}" role="img" aria-label="paired effects, ${split} questions">${g}</svg>`;
}
function renderEffects(){
  const host=$("#effectschart"); if(!host) return;
  const a=drawEffects("all"), b=drawEffects("cold");
  if(!a && !b){ host.innerHTML=""; return; }
  host.innerHTML = `<div class="panelgrid">
    <div class="panel pnl"><h3>What the message is worth — every question</h3>
      <p class="pcap">Each row is one memory in one window: the dot is the average difference the message makes on a household, the bar through it is ±1 standard error, and the rule is zero. A bar that touches the rule is not a detected effect. Green is a gain, red a cost, grey not detected.</p>${a}
      <p class="pmeta">Told minus not told, measured household by household on the households both arms ran · n at the end of each row · * = fewer than six households, where the older “bigger than the spread” bar still governs</p></div>
    <div class="panel pnl"><h3>And on cold questions</h3>
      <p class="pcap">The same contrasts on the first question about a thing each day, before that day’s feedback — the honest memory measure. The effects are larger here in both directions, so <b>this chart’s scale is wider than the one beside it</b>: read the numbers on the axis, not the dot positions, when comparing the two.</p>${b}
      <p class="pmeta">Same arms, same households, cold questions only</p></div></div>`;
}
// Claim 6's graphs: can the robot tell when to hand the question over? Per DAY, not per window, because the claim
// is about the moment the routine changes and a five-day window averages that moment away. Both families on one
// axis. Data from deferral_live, which owns only its own key and never touches llm_live.
// Long-context leads: it is the language memory this work is about. Beside it one representative per counter
// family rather than three timetables. Different sample sizes - long-context is 3 households, the counters 10 -
// so the long-context line is genuinely jumpier; that is honest and it is not smoothed.
const DEFER_LINES = [
  {k:"longcontext", label:"long-context (3 households)"},
  {k:"tt3d", label:"3-day timetable"},
  {k:"ttfrozen", label:"never-forgets timetable"},
  {k:"perpetua", label:"Perpetua*"},
].map(l => ({...l, col: colorFor(l.k)}));
function drawDefer(field, target){
  const M = (EXTRA.deferral_live && EXTRA.deferral_live.memories) || {};
  const series = DEFER_LINES.map(L=>{
    const pd = (M[L.k]||{}).per_day || {};
    const pts = Object.keys(pd).map(Number).sort((a,b)=>a-b)
      .filter(d=>pd[String(d)][field]!=null).map(d=>[d, pd[String(d)][field]]);
    return {...L, pts};
  }).filter(x=>x.pts.length>3);
  if(!series.length) return "";
  const all = series.flatMap(x=>x.pts.map(p=>p[1]));
  const top = Math.min(100, Math.max(40, Math.ceil(Math.max(...all)/10)*10+10));
  const W=470,H=210,L=34,Rr=14,T=12,B=28, nd=32;
  const x = d => L + (d-1)*(W-L-Rr)/(nd-2), y = v => T + (top-v)*(H-T-B)/top;
  let g="";
  const R=DATA.person;
  if(R&&R.stages){ let cur=null;
    const rect=c=>{const f=STAGE_FILL[c.name]; return f?`<rect x="${x(c.a).toFixed(1)}" y="${T}" width="${(x(c.b+1)-x(c.a)).toFixed(1)}" height="${H-T-B}" fill="var(${f})" opacity="0.5"/>`:"";};
    for(let d=1;d<nd;d++){const st=R.stages[String(d)]||"plain"; if(!cur||cur.name!==st){ if(cur) g+=rect(cur); cur={name:st,a:d,b:d};} else cur.b=d;}
    if(cur) g+=rect(cur); }
  const ticks=[0,25,50,75,100].filter(t=>t<=top);
  for(const v of ticks) g+=`<line x1="${L}" y1="${y(v).toFixed(1)}" x2="${W-Rr}" y2="${y(v).toFixed(1)}" stroke="var(--line)"/><text x="${L-5}" y="${(y(v)+3.5).toFixed(1)}" text-anchor="end" font-size="9" fill="var(--muted)">${v}</text>`;
  for(const d of [1,7,14,21,28]) g+=`<text x="${x(d).toFixed(1)}" y="${H-9}" text-anchor="middle" font-size="9" fill="var(--muted)">${d}</text>`;
  if(target!=null){
    g+=`<line x1="${L}" y1="${y(target).toFixed(1)}" x2="${W-Rr}" y2="${y(target).toFixed(1)}" stroke="var(--ink2)" stroke-width="1.5" stroke-dasharray="5 4"/>`
     + `<text x="${(W-Rr-2).toFixed(1)}" y="${(y(target)+10).toFixed(1)}" text-anchor="end" font-size="9" fill="var(--ink2)">promised: wrong 1 time in 10</text>`;
  }
  for(const sp of series){
    let d0="",pen=false;
    for(const [d,v] of sp.pts){ d0 += (pen?" L ":" M ")+x(d).toFixed(1)+" "+y(v).toFixed(1); pen=true; }
    g += `<path d="${d0}" fill="none" stroke="var(${sp.col})" stroke-width="2.4" stroke-linejoin="round"/>`;
  }
  const legend = series.map(a=>`<span class="pl"><i style="background:var(${a.col})"></i>${a.label}</span>`).join("");
  return `<div class="plegend">${legend}</div><svg viewBox="0 0 ${W} ${H}" role="img" aria-label="deferral ${field}">${g}</svg>`;
}
function deferBlock(){
  const a=drawDefer("hand_over",null), b=drawDefer("wrong_when_answered",10);
  if(!a&&!b) return "";
  const M=(EXTRA.deferral_live&&EXTRA.deferral_live.memories)||{};
  const at=(k,f)=>{const pd=(M[k]||{}).per_day||{}; const v=[14,15,16].map(d=>pd[String(d)]&&pd[String(d)][f]).filter(x=>x!=null); return v.length? (v.reduce((p,c)=>p+c,0)/v.length).toFixed(0) : "\u2013";};
  return `<div class="panelgrid" style="margin-top:4px">
   <div class="panel pnl"><h3>How often it hands the question over</h3>
     <p class="pcap">The robot answers only when its own confidence clears a bar it keeps adjusting as the resident's corrections come in, aiming to be wrong at most one time in ten on the answers it keeps. This is the share it hands back instead \u2014 go and look, or ask.</p>${a}
     <p class="pmeta">On the first sick days: long-context hands over ${at("longcontext","hand_over")}%, the 3-day timetable ${at("tt3d","hand_over")}%, never-forgets ${at("ttfrozen","hand_over")}%, Perpetua* ${at("perpetua","hand_over")}% \u00b7 counters on 10 households, long-context on 3, so its line is the jumpier one \u00b7 no message</p></div>
   <div class="panel pnl"><h3>And how often it is wrong on what it keeps</h3>
     <p class="pcap">Of the questions it chose to answer, the share it got wrong. The dashed line is the promise. Every method breaks it, and it breaks worst exactly where the routine changes.</p>${b}
     <p class="pmeta">On the first sick days: long-context ${at("longcontext","wrong_when_answered")}%, the 3-day timetable ${at("tt3d","wrong_when_answered")}%, never-forgets ${at("ttfrozen","wrong_when_answered")}%, Perpetua* ${at("perpetua","wrong_when_answered")}% \u00b7 against a promise of 10%</p></div></div>`;
}
function renderClaims(){
  const list=$("#claimlist"), host=$("#claimgraphs"); if(!list||!host) return;
  list.innerHTML = RESULTS.map((r,i)=>{
    const lead = CLAIMS.find(c=>c.result===r.id && c.lead);
    return `<li><a href="#result-${r.id}"><b>${r.title}.</b> ${r.blurb}</a></li>`;
  }).join("");
  const one = c => renderOneClaim(c);
  host.innerHTML = RESULTS.map(r=>{
    const mine = CLAIMS.filter(c=>c.result===r.id);
    const lead = mine.find(c=>c.lead) || mine[0];
    const rest = mine.filter(c=>c!==lead);
    return `<section class="resultblock" id="result-${r.id}">
      <h2 class="rtitle">${r.title}</h2>
      <p class="rblurb">${r.blurb}</p>
      ${one(lead)}
      ${rest.length? `<details class="morec"><summary>${rest.length} more result${rest.length===1?"":"s"} behind this one</summary>${rest.map(one).join("")}</details>` : ""}
    </section>`;
  }).join("");
}
function renderOneClaim(c){
  return (function(){
    if(c.custom==="perpetua"){
      const M=(EXTRA.deferral_live&&EXTRA.deferral_live.memories)||{};
      const P=M.perpetua||{}, TF=M.ttfrozen||{}, T3=M.tt3d||{};
      const eh=(m,w)=>(m.edge_by_household||{})[w]||null;
      const av=(m,w)=>(m.answered_vs_handed||{})[w]||null;
      const ps=eh(P,"d14_16"), pl=eh(P,"lead"), ts=eh(TF,"d14_16"), t3=eh(T3,"d14_16");
      if(!ps) return "";
      const d=(m,w)=>{const x=(m.per_day)||{}; const v=[14,15,16].map(k=>x[String(k)]&&x[String(k)][w]).filter(y=>y!=null); return v.length?(v.reduce((a,b)=>a+b,0)/v.length).toFixed(0):"–";};
      return `<section class="claim" id="claim${c.n}">
        <h3><span class="cnum">${c.n}</span>${c.text}</h3>
        <p class="cmeta">10 households · one person sick · same gate, same target, same days as the figure above</p>
        <div class="cbody">
          ${(()=>{const q=PANELS.find(x=>x.id==="ACC4"); if(!q) return "";
            const saved=panelState.split; panelState.split="all"; let inner=drawPanel(q); panelState.split=saved;
            return inner.replace(/^<div class="panel pnl"[^>]*>/,"").replace(/<\/div>\s*$/,"")
                        .replace(/<h3>.*?<\/h3>/,"")
                        .replace(/<p class="pmeta">.*?<\/p>/,`<p class="pmeta">Accuracy only, all questions, 10 households (long-context 3). The confidence result is the figure above this one; this is the same four methods on whether they are right.</p>`);})()}
          <p class="pcap" style="max-width:74ch">Perpetua* is on the figure above as the fourth line. <b>It is the least accurate of the three in the settled fortnight \u2014 69% against the timetables' 80 and 81 \u2014 so this is not a better method that also happens to have better uncertainty. It is a worse forecaster whose confidence keeps meaning something when the others' stops.</b> It does not keep the one-in-ten promise either — on the first sick days it still hands back ${d(P,"hand_over")}% of questions and is wrong on ${d(P,"wrong_when_answered")}% of the rest. What it does is keep <em>knowing which of its answers to trust</em> while the routine changes. The questions it answers are ${ps.mean.toFixed(0)} points more accurate than the ones it hands over, measured inside each household and then averaged — <b>and all ${ps.kept_sign} of the ${ps.n_hh} households keep that sign</b>, the smallest being ${ps.per_hh[0]} points. In the settled fortnight the same figure is ${pl? pl.mean.toFixed(0) : "–"}, so the separation does not merely survive the disruption, it widens.</p>
          <p class="pcap" style="max-width:74ch">Beside it, over the same days: the never-forgets timetable is <b>${ts? ts.mean.toFixed(0) : "–"}</b> and keeps the sign in only ${ts? ts.kept_sign : "–"} of ${ts? ts.n_hh : "–"} households, and the 3-day timetable is ${t3? t3.mean.toFixed(0) : "–"} in ${t3? t3.kept_sign : "–"} of ${t3? t3.n_hh : "–"}. So this is not a counter-versus-language-model story. Two counters lose their judgement at the shift and one keeps it.</p>
          <p class="pcap" style="max-width:74ch"><b>What it does differently, in one sentence you can check against the method.</b> A timetable's confidence comes from how <em>regular</em> the past was — how tightly its sightings cluster in a two-hour slot. Perpetua* instead models each object-and-place as something that persists until a survival time runs out, so its confidence comes from how <em>old</em> its evidence is. When a routine changes, the past was at its most regular precisely where things have now moved, which is why a timetable ends up confident and wrong. Evidence, by contrast, goes stale at the same rate whatever the world is doing.</p>
          <p class="pcap" style="max-width:74ch"><b>The mechanism predicted something we had not looked at, and it held.</b> If regularity-based confidence goes wrong when the world moves away from the pattern a method currently holds, then which moment breaks a method should depend on what it remembers \u2014 and a method whose confidence tracks evidence age should never break at all. Measured on the two-spell households, across five windows nobody had examined: Perpetua* holds its separation at every one of them (+28, +37, +29, +29, +36, keeping the sign in 9 or 10 households each time). The never-forgets timetable inverts at the first sick onset but <em>not</em> the second, because by then it holds both routines at once and is no longer surprised. The 3-day timetable inverts at both onsets and slightly harder the second time, because it keeps forgetting and re-learning and so is surprised every time. Neither inverts on a return: a return leaves its evidence mixed rather than regular, so it is unconfident rather than confidently wrong \u2014 which is the failure behaving as the mechanism says it should.</p>
          <p class="pmeta">Edge = accuracy of the questions the gate answers minus accuracy of the ones it hands over, computed inside each household and then averaged, ± its standard error. Perpetua* ${ps.mean.toFixed(1)} ± ${ps.se.toFixed(1)} across ${ps.n_hh} households, spread between them ±${ps.sd.toFixed(0)}. The two-spell figures come from a separate population of 10 households.</p>
        </div>
        <details class="cnums"><summary>the numbers behind this claim</summary>
          <table><tr><th>method</th><th class="num">edge, settled</th><th class="num">edge, first sick days</th><th class="num">households keeping the sign</th><th class="num">own accuracy at the shift</th></tr>
          ${["perpetua","tt3d","ttfrozen"].map(k=>{const m=M[k]||{}; const a=eh(m,"lead"), b=eh(m,"d14_16"), q=av(m,"d14_16");
            return `<tr><td>${m.name||k}</td><td class="num">${a? (a.mean>0?"+":"")+a.mean.toFixed(0):"–"}</td><td class="num">${b? (b.mean>0?"+":"")+b.mean.toFixed(0):"–"}</td><td class="num">${b? b.kept_sign+" of "+b.n_hh : "–"}</td><td class="num">${q? (100*0+ (q.answered_acc*q.n_answered+q.handed_acc*q.n_handed)/(q.n_answered+q.n_handed)).toFixed(0)+"%" : "–"}</td></tr>`;}).join("")}
          </table><p class="note" style="margin:8px 0 0">Perpetua* is the least accurate of the three in the settled fortnight, so this is not a case of a better method also having better uncertainty — it is a worse forecaster whose confidence keeps meaning something when the others' stops.</p></details>
      </section>`;
    }
    if(c.custom==="defer"){
      const M=(EXTRA.deferral_live&&EXTRA.deferral_live.memories)||{};
      const n_hh = 10;
      return `<section class="claim" id="claim${c.n}">
        <h3><span class="cnum">${c.n}</span>${c.text}</h3>
        <p class="cmeta">${n_hh} households (long-context 3) \u00b7 one person sick \u00b7 every method gated on its own confidence, aiming to be wrong at most one time in ten</p>
        <p class="pcap" style="max-width:74ch">Through the settled fortnight every method sits close to the promise it made. The gate works while the world is stable. It breaks precisely at the change \u2014 so the failure is not that these methods cannot do uncertainty, it is that the one moment the robot needs to know it is lost is the moment the signal stops working.${(()=>{const M=(EXTRA.deferral_live&&EXTRA.deferral_live.memories)||{};
          const av=M.ttfrozen&&M.ttfrozen.answered_vs_handed, sh=av&&av.d14_16, ld=av&&av.lead;
          return (sh&&ld&&sh.inverted)? ` And for one method the signal does not merely stop \u2014 it reverses. Through the settled fortnight the never-forgets timetable answers the questions it gets ${ld.answered_acc.toFixed(0)}% right and hands over ones it would have got ${ld.handed_acc.toFixed(0)}% right, which is a gate doing its job. On the first sick days that turns round: it answers the ones it gets <b>${sh.answered_acc.toFixed(0)}%</b> right and hands over ones it would have got <b>${sh.handed_acc.toFixed(0)}%</b> right. It would do better answering the questions it just refused. A memory that never forgets is surest exactly where the old routine was most regular, which is exactly where the new one has moved things.` : "";})()}</p>
        <div class="cbody">${deferBlock()}</div>
        <details class="cnums"><summary>the numbers behind this graph</summary>
        <table><tr><th>method</th><th class="num">hands over</th><th class="num">wrong on what it keeps</th><th class="num">best fixed bar, with hindsight</th><th class="num">what better calibration would buy</th></tr>
        ${Object.keys(M).map(k=>{const m=M[k]; const pd=m.per_day||{};
          const av=f=>{const v=[14,15,16].map(d=>pd[String(d)]&&pd[String(d)][f]).filter(x=>x!=null); return v.length?(v.reduce((p,c)=>p+c,0)/v.length).toFixed(0)+"%":"\u2013";};
          const dc=(m.decomposition||{}).d14_16;
          const hs = !dc||dc.miss_hindsight==null? "\u2013" : `${dc.miss_hindsight.toFixed(0)}%` + (dc.separable===false? " *" : "");
          const gp = !dc||dc.gap==null? "\u2013" : `${dc.gap>0?"":"+"}${(-dc.gap).toFixed(0)} points`;
          return `<tr><td>${m.name}</td><td class="num">${av("hand_over")}</td><td class="num">${av("wrong_when_answered")}</td><td class="num">${hs}</td><td class="num">${gp}</td></tr>`;}).join("")}
        </table><p class="note" style="margin:8px 0 0">First three sick days, against a promise of being wrong at most 10% of the time. The hindsight column is the best a single fixed bar could have done on those days if it had been chosen knowing the answers, at the same rate of handing questions over &mdash; an upper bound nobody can reach in deployment. The last column is what that hindsight would have bought; a negative figure means the bar the robot actually adjusts, which moves day to day, already beat any single fixed one. <b>*</b> marks a memory whose confidence values are too tied together for a bar to separate them at all.</p></details>
      </section>`;
    }
    if(c.custom==="planning"){
      const P = EXTRA.planning_matched; if(!P) return "";
      const r = P.rows["mart_tt72"], b = P.rows["bma_tt"];
      const sup = PANELS.find(x=>x.id===c.under);
      let supHtml = "";
      if(sup){ const saved=panelState.split; panelState.split="all"; let inner=drawPanel(sup); panelState.split=saved;
        inner = inner.replace(/^<div class="panel pnl"[^>]*>/,"").replace(/<\/div>\s*$/,"").replace(/<h3>.*?<\/h3>/,"")
                     .replace(/<p class="pmeta">.*?<\/p>/, `<p class="pmeta">Shaded band = ±1 standard error across households</p>`);
        supHtml = `<div class="csupport"><p class="csuphead">And the accuracy behind it — the reset is what makes the saving</p>${inner}</div>`; }
      return `<section class="claim" id="claim${c.n}">
        <h3><span class="cnum">${c.n}</span>${c.text}</h3>
        <p class="cmeta">10 households · ${P.regime} · simulated search cost, every method held to the same ${P.matched_ask}% ask rate on lead days</p>
        <div class="cbody">
          <p class="pcap">Each method answers, or asks the resident instead when it is unsure. The thresholds are set so all four ask on ${P.matched_ask}% of lead-day questions, then held fixed — without that matching the comparison is meaningless, because a method that simply asks more often looks cheaper. Only the one that notices <em>and</em> wipes its diary gets cheaper during the spell (${r.lead.toFixed(2)} → ${r.sick.toFixed(2)}); the hedge notices and does not act, and gets dearer (${b.lead.toFixed(2)} → ${b.sick.toFixed(2)}).</p>
          ${drawPlanningBars()}
        </div>
        ${supHtml}
        <details class="cnums"><summary>the numbers behind this graph</summary>
          <table><tr><th>method</th><th class="num">lead-up</th><th class="num">sick spell</th><th class="num">return</th><th class="num">ask rate, lead → spell</th></tr>
          ${PLAN_ORDER.map(o=>{const v=P.rows[o.k]; return v? `<tr><td>${o.label}</td><td class="num">${v.lead.toFixed(2)}</td><td class="num">${v.sick.toFixed(2)}</td><td class="num">${v.return.toFixed(2)}</td><td class="num">${v.lead_ask} → ${v.sick_ask}</td></tr>`:"";}).join("")}
          </table><p class="note" style="margin:8px 0 0">Places searched per question. Source: ${P.source}.</p></details>
      </section>`;
    }
    const p = PANELS.find(x=>x.id===c.panel); if(!p) return "";
    const split = c.split || "all", flavour = p.flavour || "acc";
    const saved = panelState.split; panelState.split = split;   // each graph is drawn in the split its claim needs
    const svg = drawPanel(p);
    panelState.split = saved;
    const hh = panelHH(p);
    let inner = svg.replace(/^<div class="panel pnl"[^>]*>/, "").replace(/<\/div>\s*$/, "");
    inner = inner.replace(/<h3>.*?<\/h3>/, "");                                  // the claim is the heading
    inner = inner.replace(/<p class="pmeta">.*?<\/p>/, `<p class="pmeta">Shaded band = ±1 standard error across households${p.note? " · "+p.note : ""}</p>`);
    return `<section class="claim" id="claim${c.n}">
      <h3><span class="cnum">${c.n}</span>${c.text}</h3>
      <p class="cmeta">${hh} household${hh===1?"":"s"} · ${POP_LABEL[p.pop]||p.pop} · ${flavour==="conf"?"stated confidence":"accuracy"}, ${p.lines.some(l=>l.split)? "all questions and cold questions together — cold is the first question about a thing each day, before that day's feedback" : (split==="cold"?"cold questions — the first question about a thing each day, before that day's feedback":"all questions")}</p>
      <div class="cbody">${inner}</div>
      ${c.also==="channels"? drawChannels() : ""}
      <details class="cnums"><summary>the numbers behind this graph</summary>${claimNumbers(p, split, flavour)}</details>
    </section>`;
  })();
}
function renderPanels(){
  const host=$("#panelgrid"); if(!host) return;
  const list = PANELS.filter(p=>panelState.on.has(p.id));
  host.innerHTML = list.length? list.map(drawPanel).join("") : `<p class="note">No panel selected — pick one above.</p>`;
}
function renderPanelPicker(){
  const host=$("#panelpick"); if(!host) return;
  const groups={};
  for(const p of PANELS){ (groups[p.group]=groups[p.group]||[]).push(p); }
  host.innerHTML = Object.keys(groups).map(gname=>
    `<div class="pgroup"><b>${gname}</b>${groups[gname].map(p=>
      `<label class="pchip"><input type="checkbox" data-pid="${p.id}"${panelState.on.has(p.id)?" checked":""}> ${p.title}</label>`).join("")}</div>`).join("");
  host.querySelectorAll("input[data-pid]").forEach(el=>el.addEventListener("change", e=>{
    const id=e.target.dataset.pid; if(e.target.checked) panelState.on.add(id); else panelState.on.delete(id); renderPanels(); }));
}
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
  // paired told-vs-untold contrast on the SAME households. The bar, changed by THIS SESSION at 07:25 (Oliver set the
  // 1-sd rule; he has not ruled on this one, and the note on the page says so): claim a
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
  const nd = v => v? `(${v.mean>0?"+":""}${Math.abs(v.mean)<1? v.mean.toFixed(1):v.mean.toFixed(0)} ± ${v.se.toFixed(1)}, n=${v.n_hh}, spread ±${v.sd.toFixed(0)})` : "";
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
  items.push(`<b>What one sentence buys — and what it costs.</b> Telling the buffer "Yuki is home sick today" is worth ${pstr("llm_naive_startmsg","d14_16")} on the first three sick days and ${pstr("llm_naive_startmsg","d17_23")} through the rest of the spell; on cold questions — the first question about a thing each day, before any feedback — ${pstr("llm_naive_startmsg","d14_16","cold")} and ${pstr("llm_naive_startmsg","d17_23","cold")}.<br><br>It costs on the return: ${pstr("llm_naive_startmsg","d24_26")} on the first days back, cold ${pstr("llm_naive_startmsg","d24_26","cold")} — told once, it keeps believing the sick routine until feedback proves otherwise. Told again on the first day back, that cost is no longer measurable: with both messages the first days back show no measurable difference against never being told at all ${nd(pv("llm_naive_startend","d24_26","all"))}. Compare those two on the same ten households, since the retracted arm only ran there: un-retracted ${(()=>{const o=pv("llm_naive_startmsg","d24_26","all"); return o&&o.ours? `${Math.abs(o.ours.mean).toFixed(0)} points worse` : "\u2013";})()}, retracted 4 points worse \u2014 so the retraction does coincide with the cost going away. That is not the same as showing the retraction did the repairing, and when the two told arms are compared head to head we do not find it: ${rstr("llm_naive_startend","d24_26")} on all questions, ${rstr("llm_naive_startend","d24_26","cold")} on cold ones. ${(()=>{const v=rv("llm_naive_startend","d24_26","cold"); return (v&&v.ours)? `Our first ten households put that cold figure at +${v.ours.mean.toFixed(0)}; with the eight added afterwards it is +${v.mean.toFixed(0)}, so doubling the sample moved the estimate down rather than tightening it around the old one.` : "";})()}<br><br>The two halves are not the same size, and the difference matters more than either on its own. What the sentence buys on the way in is large and survives a fresh sample: ${pstr("llm_naive_startmsg","d17_23","cold")} on cold questions through the spell, where the ten households we ran first gave +36 and the eight added afterwards +30. What it costs on the way out is real but roughly a third the size, and confined to the first three days back — a week later there is ${pstr("llm_naive_startmsg","d27_31")} left of it. Both estimates came down when the sample doubled, and they came down for the same reason: our first ten households were the optimistic half of the draw, showing up once in each direction. That is one hopeful sample seen twice, not two separate surprises.<br><br>The same sentence costs a memory that looks things up by time of day for longer: retrieval shows no measurable difference on the first days back ${nd(pv("llm_retrieval_startmsg","d24_26","all"))} \u2014 a bigger number than the one we do claim, but the households disagree about it four times as much, which is the whole reason the bar is where it is \u2014 and still ${pstr("llm_retrieval_startmsg","d27_31")} behind a week later (cold ${pstr("llm_retrieval_startmsg","d27_31","cold")}) — its same-hour lookup keeps handing back the sick-day sightings after the buffer has dropped them — and the second message mostly, but not entirely, clears it: with both messages that same week comes out ${pstr("llm_retrieval_startend","d27_31","cold")} on cold questions against never being told — still large enough to measure, but ${(()=>{const a=pv("llm_retrieval_startmsg","d27_31","cold"), b=pv("llm_retrieval_startend","d27_31","cold"); return (a&&b&&b.mean)? `about a ${Math.round(Math.abs(a.mean/b.mean))===4?"quarter":Math.round(Math.abs(a.mean/b.mean))===3?"third":`${Math.round(Math.abs(a.mean/b.mean))}th`} of the ${a.mean.toFixed(0)} points` : "far less than what"})()} the un-retracted message leaves. Telling twice against telling once is, on cold questions, ${rstr("llm_retrieval_startend","d27_31","cold")}. The buffer shows no such lasting cost a week after the return ${nd(pv("llm_naive_startmsg","d27_31","all"))}. The message is selective by object, for as long as it is true: where only one person is sick it moves the sick person's things and leaves the other resident's alone — the figures are in "Whose routine changed?" below, together with what happens to that selectivity once the message goes stale.`);
  // 4. confidence never moves
  const K=(EXTRA.knowno_live && EXTRA.knowno_live.person && EXTRA.knowno_live.person.llm_naive_nomsg) || null; const k14 = K && K.days["14"];
  const confs = memKinds.filter(([k])=>conf(k,"lead")!=null && conf(k,"d14_16")!=null).map(([k,n])=>`${n} ${f(conf(k,"lead"))}→${f(conf(k,"d14_16"))}%`);
  const AG=P.llm_naive_nomsg && P.llm_naive_nomsg.askgate;
  {
    const DF = (EXTRA.deferral_live && EXTRA.deferral_live.memories) || {};
    const dec = (m,w) => (DF[m] && DF[m].decomposition && DF[m].decomposition[w]) || null;
    const tied = m => { const d=dec(m,"d14_16"); return d && d.separable===false; };
    const r = m => { const d=dec(m,"d14_16"); return d? d : {}; };
    const rng = f => { const v=Object.keys(DF).map(k=>r(k)[f]).filter(x=>x!=null);
                       return v.length? `${Math.min(...v).toFixed(0)}% to ${Math.max(...v).toFixed(0)}%` : "\u2013"; };
    const nTied = Object.keys(DF).filter(tied).length;
    items.push(`<b>The information is not in the number.</b> Not &ldquo;the bar is in the wrong place&rdquo; and not &ldquo;it needs recalibrating&rdquo; \u2014 there is nothing in these confidence values to put a bar on. The stated number barely shifts between the settled fortnight and the first sick days (${confs.join(", ")}) while accuracy falls by 20\u201330 points. The obvious reply is that the bar is simply in the wrong place and better calibration would fix it. It would not. <br><br>Let the robot answer only when its confidence clears a bar it keeps adjusting from the resident's corrections, aiming to be wrong at most one time in ten. On the first sick days it ends up wrong on ${rng("miss_achieved")} of what it chooses to answer. Now hand it the answers and let it pick the single best fixed bar for those days with full hindsight, at the same rate of handing questions over: ${rng("miss_hindsight")}. Every method lands within ${(()=>{const v=Object.keys(DF).map(k=>r(k).gap).filter(x=>x!=null).map(Math.abs); return v.length? Math.max(...v).toFixed(0) : "3";})()} points of where it already was. <br><br>So the scalar itself is the problem, not the threshold on it. On ${nTied} of the ${Object.keys(DF).length} memories the confidence values are too tied together for any bar to separate them at all \u2014 long-context is the extreme, stating near-certainty on almost everything (median ${(DF.longcontext&&DF.longcontext.discrimination&&DF.longcontext.discrimination.lead||{}).median}, ${(DF.longcontext&&DF.longcontext.discrimination&&DF.longcontext.discrimination.lead||{}).n_above} of ${(DF.longcontext&&DF.longcontext.discrimination&&DF.longcontext.discrimination.lead||{}).n} questions above it in the settled week), so for that memory no bar exists, with hindsight or without. The counter fails the other way round: its confidence <em>does</em> move with the stage (3-day timetable ${f(cconf("tt3d","lead"))}\u2192${f(cconf("tt3d","s1"))}%), and it is still the worst of the lot here, wrong on ${(r("tt3d").miss_achieved||0).toFixed(0)}% of what it keeps while handing back ${(r("tt3d").ask_rate||0).toFixed(0)}%.`);
  }

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
    if(op("llm_naive_startmsg","d17_23","sick","all")) items.push(`<b>A message about one person moves that person\u2019s things and leaves the other resident\u2019s alone \u2014 until it goes stale.</b> In households where one resident is off sick but the robot is asked about everyone\u2019s things (${nhh} households, every arm finished), telling the buffer \u201cYuki is home sick today\u201d takes the sick resident\u2019s own things from ${lvl("llm_naive_startmsg","d14_16","sick","all")} on the first three sick days (${ops("llm_naive_startmsg","d14_16","sick","all")}) and from ${lvl("llm_naive_startmsg","d17_23","sick","all")} through the rest of the spell (${ops("llm_naive_startmsg","d17_23","sick","all")}); on cold questions the same two windows are ${lvl("llm_naive_startmsg","d14_16","sick","cold")} (${ops("llm_naive_startmsg","d14_16","sick","cold")}) and ${lvl("llm_naive_startmsg","d17_23","sick","cold")} (${ops("llm_naive_startmsg","d17_23","sick","cold")}). The other resident\u2019s things, on the same households and the same windows, go ${lvl("llm_naive_startmsg","d14_16","others","all")} and ${lvl("llm_naive_startmsg","d17_23","others","all")} \u2014 no measurable difference either time (${bare(op("llm_naive_startmsg","d14_16","others","all"))} and ${bare(op("llm_naive_startmsg","d17_23","others","all"))} points across the same six households), and none on cold questions either (${bare(op("llm_naive_startmsg","d14_16","others","cold"))} and ${bare(op("llm_naive_startmsg","d17_23","others","cold"))}, same six). The arm that shows nothing is half the finding: the sentence is applied where it belongs and, while it is true, nowhere else.<br><br>Then it stops being true. On the first three days back, with the message still standing and never retracted, the other resident\u2019s things fall ${lvl("llm_naive_startmsg","d24_26","others","all")} \u2014 ${ops("llm_naive_startmsg","d24_26","others","all")} \u2014 while the sick resident\u2019s own fall ${lvl("llm_naive_startmsg","d24_26","sick","all")}, which six households cannot separate from zero ${nd(op("llm_naive_startmsg","d24_26","sick","all"))}. So: while the instruction matches the world, the buffer applies it exactly where it belongs; once it is stale it costs a little beyond its target too, which is the same return cost the buffer shows on the one-person population, seen from the other side. Read the second half carefully \u2014 the leak we can actually measure is the ${Math.abs((op("llm_naive_startmsg","d24_26","others","all")||{}).mean||0).toFixed(0)}-point one onto the other resident\u2019s things, on ${nOf("llm_naive_startmsg","d24_26","others","all")} households; the estimate on the sick person\u2019s own things is larger but these ${nOf("llm_naive_startmsg","d24_26","sick","all")} households cannot separate it from zero, so nothing here says a stale message costs more away from home than at home. <br><br>On the same six households the nightly routine table also leaves the other resident\u2019s things alone ${nd(op("llm_routine7_startmsg","d17_23","others","all"))} but is worse everywhere: without any message it answers the sick resident\u2019s things ${f((OS.llm_routine7_nomsg||{windows:{}}).windows.d17_23 ? OS.llm_routine7_nomsg.windows.d17_23.sick_all.acc : null)}% against the buffer\u2019s ${f((OS.llm_naive_nomsg||{windows:{}}).windows.d17_23 ? OS.llm_naive_nomsg.windows.d17_23.sick_all.acc : null)}%, and the other resident\u2019s ${f(OS.llm_routine7_nomsg.windows.d17_23.others_all.acc)}% against ${f(OS.llm_naive_nomsg.windows.d17_23.others_all.acc)}% \u2014 while its stated confidence sits between 82 and 89% in every window for both residents, message or no message.`);
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
    items.push(`<b>The memory that already writes its own corrections each night is the one case where we cannot say what the message does.</b> Reflection keeps a nightly note of the mistakes it made and what to check instead. Told \u201cYuki is home sick today\u201d, its first three sick days show no measurable difference ${nd(pv("llm_reflect_startmsg","d14_16","all"))} and neither do its cold questions ${nd(pv("llm_reflect_startmsg","d14_16","cold"))}, across the ${refl.n_hh} households all three of its message arms ran on \u2014 server time ran out before the other five. It is tempting to read that as "the sentence tells it something its own notes were already recording", and that may well be true, but five households cannot support it: the same figures are also consistent with a gain of up to ${rup.toFixed(0)} points \u2014 essentially the +${(pv("llm_naive_startmsg","d14_16")||{mean:0}).mean.toFixed(0)} the plain buffer gets. So what this arm establishes is only that we could not measure an effect, not that there is none \u2014 the one bullet here where absence of evidence is all we have. It is, separately, the least demanding of the four: asked to answer only when it can be wrong no more than one time in ten, it asks the resident on ${f(g("llm_reflect_nomsg"))}% of the shift-day questions where the buffer asks ${f(g("llm_naive_nomsg"))}% and retrieval ${f(g("llm_retrieval_nomsg"))}%.`);
  }

  if(pv("llm_longcontext_startmsg","d14_16")){
    const ab=(P.llm_longcontext_nomsg && P.llm_longcontext_nomsg.abandoned_hh) || [];
    const q = (k,w,sp) => bare(pv(k,w,sp));
    items.push(`<b>Long-context memory — the whole log in every prompt — was run on three households, which is too few to settle most of what we would want to ask of it.</b> It costs roughly ten times the compute of the other memories \u2014 about 10,000 to 12,000 tokens of prompt per question against 1,100 for retrieval and 1,400 to 1,500 for reflection, counted from the no-message arms\u2019 call logs; its message arms were only ever affordable on three households, so the other ${ab.length} households of its no-message run were abandoned rather than finished, since they could not have improved any comparison. On three households the spread between households is itself barely measurable, so treat every figure here as indicative: telling it about the sick spell makes no measurable difference on the first three sick days (${q("llm_longcontext_startmsg","d14_16","all")} points, cold ${q("llm_longcontext_startmsg","d14_16","cold")}; every figure in this bullet is an average over three households \u00b1 its standard error), appears to help through the rest of the spell (${q("llm_longcontext_startmsg","d17_23","all")}, cold ${q("llm_longcontext_startmsg","d17_23","cold")}), and — the one pattern worth noting, because it matches retrieval on ten households — the cost of a message that is never retracted still shows a week after the return (${q("llm_longcontext_startmsg","d27_31","all")}, cold ${q("llm_longcontext_startmsg","d27_31","cold")}), while with the second message it is gone (${q("llm_longcontext_startend","d27_31","all")}). Two memories that keep everything behave the same way; a plain recency buffer does not.`);
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
    // Our own change of bar has to be visible rather than discoverable -- it is not his decision yet -- but 350 words of
    // method must not stand between a reader and the findings. So: the change itself, and the direction it moved
    // things, in two sentences up top; the rest one click away.
    note.innerHTML = `<b>How to read these numbers — and the bar changed this morning.</b> Every comparison between two ways of running the same memory is measured household by household, never by setting one arm's overall number beside another's, and is written as <b>average ± its standard error</b> with <b>n</b> = households and <b>spread</b> = how much they disagree. Each figure is the difference on the same household between the told and untold runs, averaged over households; where the spread dwarfs the average — as it does on the buffer's return cost — the difference is real but small, meaning the households mostly move the same way rather than any one of them moving far. The bar we ran on overnight was Oliver's: claim an effect only when the average beats the disagreement between households. <b>We changed the primary bar this morning</b>, to the conventional one — the average must be at least twice its own standard error — and it is flagged here rather than left to be discovered, because it is our change and not yet his ruling; both bars are printed wherever they disagree, so the rule he set can still be applied by eye. It is worth being plain about which way it moved things, because the name sounds stricter and the arithmetic is not: at ten households the standard error is about a third of the spread, so at six households or more anything that cleared the old bar clears the new one automatically. <b>Nothing written up overnight lost its standing, and the change could only add claims</b> — what it added is a handful of contrasts previously called "no measurable difference" that are now reported as small effects, and a detected three-point gain is described here as a small gain, not an important one. <details style="margin-top:6px"><summary style="cursor:pointer">What ten households can and cannot resolve, and the two findings withdrawn overnight</summary><div style="margin-top:6px">With ten households the smallest average we can now call is about ${f(2*med(ses.all))} points on all questions and about ${f(2*med(ses.cold))} on cold ones, where under the old bar it was about ${f(med(sds.all))} and ${f(med(sds.cold))}. Wherever a figure passes one bar and not the other, both are printed. The old floor still governs where a memory was only affordable on three or five households: a standard error estimated from that few numbers is not worth trusting, so those arms keep the spread floor and say how few households they rest on. Treat anything marked "three households" as indicative — worth reporting when it matches a pattern seen on ten, not on its own. Two findings were withdrawn overnight for failing exactly this test after first being written up on too few households: a claim that a memory shared across the household spread one person's disruption onto the other resident's things (three households; with all six it is a wash), and a two-point difference between two ways of running the reflection memory that was measured on different household sets. Both are recorded in the working notes; the numbers on this page are the ones that survived.</div></details>`;
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
  L.innerHTML = items.map(t=>{
    const m = t.match(/^\s*<b>([\s\S]*?)<\/b>([\s\S]*)$/);
    if(!m) return `<li>${t}</li>`;
    return `<li class="fx"><details class="finding"><summary>${m[1]}</summary><div class="fbody">${m[2]}</div></details></li>`;
  }).join("");
}
for(const o of $("#regime").options){ if(!DATA[o.value]){ o.disabled=true; o.hidden=true; } }   // a population whose data has not been built yet is not selectable
for(const o of $("#gapreg").options){ if(!(EXTRA.gap && EXTRA.gap.populations[o.value])){ o.disabled=true; o.hidden=true; } }
mergeLLMLive();
$("#psplit").addEventListener("change", e=>{ panelState.split=e.target.value; renderPanels(); });
$("#pflavour").addEventListener("change", e=>{ panelState.flavour=e.target.value; renderPanels(); });
$("#pall").addEventListener("click", ()=>{ for(const p of PANELS) panelState.on.add(p.id); renderPanelPicker(); renderPanels(); });
$("#pdef").addEventListener("click", ()=>{ panelState.on=new Set(PANEL_DEFAULT); renderPanelPicker(); renderPanels(); });
renderPanelPicker(); renderPanels(); renderClaims();
$("#findall").addEventListener("change", e=>{
  for(const d of document.querySelectorAll("details.finding")) d.open = e.target.checked; });
renderGist(); renderLegend(); renderGloss(); draw(); renderSweep(); renderAffected(); renderPlanning();
</script>
'''
import datetime as _dt
open(out, "w").write(HTML.replace("/*DATA*/null", json.dumps(data, separators=(",", ":"))).replace("/*EXTRA*/null", json.dumps(extra, separators=(",", ":")))
     .replace("/*BUILT*/", _dt.datetime.now().strftime("%a %H:%M, %d %b %Y")))
print("wrote", out, os.path.getsize(out) // 1024, "KB")
