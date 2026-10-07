# The 24-questions wave: what it is for, and what its output must contain

Written before launching, so that "it finished" can be checked against a list rather than
against a clean exit. A run that looks complete because everything it did do succeeded is this
project's dominant failure mode.

## What it is for, and what it does not replace

**Resolution inside one household, not more households.** At 8 questions a day a point on a
per-day, per-home, movers-only line rests on **3.7 mover questions**, and 79 of 310 home-days
have one or two - so a 0% or a 100% day is arithmetic, not signal. The banks hold **24
answerable questions every day** and we were using a third of them.

Verified independently on the three chosen homes before launching (not taken on trust):

| home | movers | answerable/day | at 8: distinct objects / hours / mover qs | at 24: distinct objects / hours / mover qs |
|---|---|---|---|---|
| `hh_s2_t03` | 8 | 24 | 5.4 / 7.4 / **4.5** | 8.6 / 11.6 / **14.5** |
| `hh_s48_t03` | 6 | 24 | 5.7 / 6.7 / **2.9** | 9.0 / 10.3 / **9.9** |
| `hh_s32_t03` | 8 | 24 | 6.0 / 7.4 / **4.1** | 11.2 / 11.9 / **11.5** |

**The ten-home wave at 8 a day is NOT superseded.** It answers a different question: pooled
over ten homes, a day's point rests on ~37 mover questions, which is fine. What it cannot do
is show one household's curve. Both waves stand; they are never pooled.

## The two guards against the waves being mixed

1. **Its own directory** (this one), and the 8-a-day wave stays where it is.
2. **The number is recorded in three places and read back off disk.** Each cell's
   `searches.jsonl` header and `arm.json` carry `questions_per_day`; the runner refuses a cell
   whose header does not say what was asked for (the same gate the asked-object list has); and
   the first line of every report prints every distinct value found under the root, with a
   loud line if there is more than one.

## The homes, chosen to differ rather than drawn

* `hh_s2_t03` - has a dining room, 8 movers
* `hh_s48_t03` - 6 movers, all of them named in its notes
* `hh_s32_t03` - three residents, no dining room

## The arms, in the order one launcher will run them

1. `newest sighting, no model` on **all ten** homes - it makes no model calls, so more of the
   comparator costs nothing
2. `the log and notes about the routine` (ours) x 3
3. `incremental edits` (the plain control, the one-variable partner) x 3
4. `claim store told if it was right` (ACE) x 3
5. `a small working memory and an archive` (MemGPT) x 3
6. `prior only, no notes` x 3, if the night allows
7. `wholesale rewrite` x 1 (`hh_s2_t03`), last

## What the output must contain before any number is read

* **26 cells** if everything runs: 10 + 3 + 3 + 3 + 3 + 3 + 1. Fewer is fine and must be
  *named*: the cut order is MemGPT first, then ACE's third home.
* every cell: `cell.json`, `arm.json`, `notes.json` (except the no-model arm, which writes
  none), `searches.jsonl`, `looks.jsonl`, `per_day.jsonl`, `call_times.jsonl`
* every cell's header says **`questions_per_day: 24`** and
  `name_the_objects_it_will_be_quizzed_on: false`
* **no** `cell_HELD_FOR_REVIEW.json` and **no** `CRASHED.txt` anywhere; `RUNNING.lock` gone
  from every finished cell
* no night with `the_completion_did_not_parse`, and no lost call: `LOST after 2 attempts`
  must not appear in any log now that the socket bug is fixed
* at 24 a day a day's point must rest on ~10-14 mover questions per home; the report states
  the actual count per home-day, and any home-day under 5 is named rather than plotted

## The budget, measured rather than assumed

At 8 a day a model cell made 338-636 model calls, of which 32 (64 for ACE) were nightly
writes; the rest are question-time, and only those triple. So at 24 a day: about **950 calls
for ours, 1,100-1,160 for the control and ACE, 1,850 for MemGPT**. Measured throughput on this
server at the concurrency we are using was **2,800-3,400 uncached calls an hour**.

* the twelve model-arm cells (arms 2-5): **~15,100 calls, 4.5-5.5 hours**
* adding prior-only and the rewrite: **~19,600 calls, 6-7 hours**
* without MemGPT (nine cells): **~9,600 calls, 3-3.5 hours**

Longer prompts at 24 a day will lower calls-per-hour somewhat, so these are floors. **Three
hours buys nine cells, not twelve.** The cut, if one is wanted, is MemGPT.

## The ceiling test: ONE confound, and how the second candidate was measured away

`ours, allowance derived` differs from our flat-16 arm in **the number of notes it may write in a
night**, and in nothing else that bound.

`max_tokens` is `300 + 260 * slots`, so the token budget moves with the slot count as
arithmetic - one knob expressed twice, not two independent changes. And the token half never
bound, which was measured rather than argued:

* on the **26 nights** the flat-16 arm sat exactly at its cap at 24 questions a day, the new and
  changed note text came to a **median of 1,998 characters and at most 3,726** counting statement
  text alone, or a median of 3,142 and at most 6,193 counting the JSON the completion has to
  carry around it. The budget is 4,460 tokens, roughly 17,840 characters. **So the biggest night
  used between 21% and 35% of the budget while the slot count was full.** The higher figure is
  the one to quote, because it counts everything the model had to emit.
* the thing that would have to be true otherwise: a completion cut off by `max_tokens` cannot be
  valid JSON, and would be recorded as `the_completion_did_not_parse`. Our arm has **0 of 416
  nights** across both waves.

So a difference between the flat-16 cells and the derived-allowance cells is attributable to
**slots**. The `300 + 260 * cap` arithmetic stays in the write-up because it is real, stated as
*the budget was measured not to bind* rather than as an open confound.

An earlier version of this note listed the read-to-write ratio as a third thing that moved. It
is not: prompt size barely differs between the two arms (67,856 characters against 61,473), so
the ratio moves only because its denominator did.

## The read-to-write table, which earns its place on one line

Prompt tokens (characters / 4) against the same nightly call's output allowance, 24 a day:

| arm | prompt chars | max_tokens | read : write |
|---|---|---|---|
| `MemGPT as published` | 79,151 | 2,600 | **7.6x** |
| `the log and notes` (flat 16) | 67,856 | 4,460 | 3.8x |
| `incremental edits` | 73,312 | 14,248 | 1.3x |
| `claim store told if it was right` | 62,619 | 12,456 | 1.3x |
| `ACE as published` | 67,793 | 14,197 | 1.2x |
| `prior only, no notes` | 84,550 | 18,175 | 1.2x |
| `ours, allowance derived` | 61,473 | 13,492 | 1.1x |

**`MemGPT as published` reads about 19,800 tokens to emit at most 2,600, every night, while the
archive that exists to relieve that cost holds 0 passages at every point in all three cells.**
That is a cost result, it needs no accuracy number, and it is the strongest form of the
frozen-block finding.

# THIS WAVE IS CLOSED. It is the answer-first ablation.

**Closed 2026-09-25 19:2x. It was not abandoned and it is not half a wave.** Every cell in this
directory chose rooms with a schema that asks for the answer before the reasoning, and that is
now the thing it measures.

`choice_schema` in `search_driven.py` declares its properties in the order `{"room", "why"}`.
The server enforces the schema while generating, so the order is not a suggestion: the model
must emit the room first. Every call this project makes also sets
`chat_template_kwargs: {"enable_thinking": False}`, so there is no hidden deliberation channel
either. Checked in the raw completions rather than inferred from the schema:
**2,206 of 2,206 cached room-choice completions emit `room` first, then `why`** (the
coordinator's count, on this wave's calls). Counted again across the whole project cache -
every completion whose object has exactly the keys `room` and `why` - it is
**55,613 of 55,613, 100.0%**. The model
commits to a room with zero tokens of deliberation and then writes a justification for a
decision already made.

One file over, the ANSWERING schema is `{reasoning, location, confidence}`, reasoning required
first, which is right. The two were never compared.

**Why it matters beyond readability.** Every arm that chooses rooms from its notes gets one
forward pass with no room to think, while the no-model rule needs none. "A free rule beats three
published memory designs" is a great deal less surprising if the memory designs were never
allowed to reason before acting. Our arm uses the same chooser and still leads, so this does not
explain the whole gap - but it is exactly the flaw that would squash the differences between
arms toward the cheapest one.

**From now on:** reasoning comes before the decision, and the 240-character clip on explanations
goes (it cut 30.7% of all explanations, 14,308 of 46,537). The successor wave runs the same
design - 24 questions a day, the same three households - in its own directory, so the pair is a
clean ablation: **does letting a memory reason before it acts change which memory wins?**

**Moved to the successor wave rather than run here:** the `wholesale rewrite` cell, the two
`MemGPT as published` reruns, and the six told-it cells (`ours, told the night before` and
`ours, told on the first night`). They are absent from this wave by decision, not by failure.
