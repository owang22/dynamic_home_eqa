# What we expect, written down before anything runs

Registered 2026-09-24, before any arm has been launched. Every number below was
measured on the frozen households, which this study reads and never writes.

## The hypothesis

A robot remembers a home better when it looks where its own guesses disagree,
and edits its notes instead of rewriting them.

## The two things we are varying

**How the notes are written.** Either the model rewrites one summary of the
household from scratch each night, or it adds, revises and marks individual
claims, each claim carrying the ids of the sightings that support and contradict
it.

**Where the robot looks.** Either a schedule fixed before day 0, or the model
chooses the room.

Everything else is held identical: same model, same temperature, same
households, same traces, same number of looks, same question stream, same
retrieval budget at answer time, and prompts that differ only in the
intervention.

## The prediction that survives a null on accuracy

This is the point of pre-registering. Accuracy may come out flat. The following
is a property of the notes file itself and can be checked without the model:

> The arms that edit their notes incrementally still hold the ordinary-routine
> claim at the end of the disrupted period, and reuse it when the resident comes
> back. The arms that rewrite their notes wholesale have lost it.

Checked by `memory_notes.ordinary_routine_claims_still_present`. For the
incremental arms it is exact: claim ids persist and we check whether the claim
written during the ordinary fortnight is still readable and still names the same
place. For the wholesale-rewrite arms we can only check the newest summary text,
so we check whether the ordinary-routine wording still appears in it.

Secondary and also pre-registered: the choosing arm finds the disruption on an
earlier day than the schedule does.

## The scenario

`results/regime_search/sick10_partial/banks` — one resident off sick for ten
weekdays, with questions asked about **everyone's** things. Read-only; it belongs
to another paper.

Why not the owner-only regime we started from: there every asked object belongs
to the sick resident and nearly all of them land on the same coffee table, so one
sentence covers the whole disruption and a per-claim memory cannot beat a
wholesale rewrite by construction. Worse, its disrupted window is *easier* than
ordinary life. Both scenarios, measured the same way on the disrupted window:

| Yardstick on the disrupted window | owner-only | this scenario |
| --- | --- | --- |
| One fact for the whole house ("coffee table") | 78% | **58%** |
| Every object's own commonest place, known perfectly | 83% | **80%** |
| Room between them | 5 points | **22 points** |

Reproduced independently and to the point on 2026-09-24: 58% and 80%.

Per household here: 644 to 744 questions, 8 to 18 asked objects, of which 3 to 8
change their usual place and the rest never move — so the memory has both
revision and preservation to do.

## The sensing design

Locked 2026-09-24. Room-level looks, **one room per look, one look a day, at
13:00**. Not three rooms, not place-level, no 3am sweep.

| Measured on the frozen households | Number |
| --- | --- |
| Rooms per household | 6 to 9 (median 7) |
| Places (spots things rest in) per household | 33 to 47 |
| Share of answers sitting in a household's three commonest rooms | 84% to 100%, median 92% |
| Asked objects whose usual room differs between periods, seen in the daytime | 32 of 53 |
| The same, seen at 3am | 9 of 53, and zero in three households |
| Share of the disruption a look reveals, by hour | 17-20% midnight to 08:00; 48% at 09:00; a flat 71-75% from 10:00 to 17:00; 66% at 18:00; 24-33% late evening |
| Days for one full pass of a fixed rotation, one room a day | 6 to 9 |
| Days for one full pass, three places a day | 11 to 15, longer than the ten-day disruption |

- **Rooms, not places.** A place-level rotation cannot finish a pass inside the
  disruption, so whether a household notices depends on where the rota started.
  That is a coin flip, not an experiment.
- **One room, not three.** At three rooms a day a rotation sweeps the house every
  two to three days and a robot that chooses has nothing left to find.
- **13:00, not 3am.** The disruption is a daytime phenomenon: the sick resident
  uses their things in the living room through the working day and they are
  tidied back overnight, so the night world looks the same in both periods.
- **The fixed schedule rotates over every room, fairly.** The obvious
  alternative — rotate only the rooms that usually held things during the
  ordinary fortnight — is not fairer but rigged: the living room is in the
  settled-period top three in only **1 of 10** households, so that schedule never
  visits the room the disruption moves into in **9 of 10** households and could
  not detect the change at any budget.
- **The rota order is a seed, chosen and recorded per household.** When a full
  pass takes longer than the thing being detected, the order carries the result.

Two budgets, kept separate: three curation looks per asked object across the
whole study (about 36, so roughly one a day), and up to three places checked when
answering one question. The second is the headline search cost and is reported
apart from accuracy.

## The freeze points

The primary measurement freezes each arm's notes and answers with no further
looking, so that "the memory is better" is separated from "the policy searches
better". Every question in the window is used; nothing is held out, because with
the post-question truth removed a question teaches the robot nothing.

| Freeze point | Notes through | Questions | What it can show |
| --- | --- | --- | --- |
| before anything changed | day 13 | days 14-23 | the control: every arm has the same information and they should agree |
| did it learn the new routine | day 23 | days 14-23 | revision. Floor 34%, ceiling 80%: 46 points of room |
| did it keep the old routine | day 23 | days 24-31 | preservation, where the prediction lives. Keeping the ordinary routine is worth about 68% and is within 2 points of this window's own oracle; replacing it with the disrupted routine is worth about 45%. Predicted gap: about 23 points |

240 questions per household at the first two, 164 to 192 at the third. We also
report, separately, the score on the subset a settled memory gets wrong (40-87%
of the disrupted window, 19-51% of the return window) — those are the only
questions that can separate the arms.

## The exclusion rule, and a disagreement about it

Stated before any run: **drop any household where fewer than two asked objects
change their usual place when the resident falls ill.**

Which households that drops depends on a choice that had not been made explicit,
and the two answers differ:

- measured **over daytime hours** (the hours a look could happen): no household
  has fewer than three movers, so the rule drops **nobody**;
- measured **at question times**: s4 has one mover and every other household has
  three or more, so the rule drops **s4**.

In s4 six of thirteen asked objects change their usual daytime place — the
disruption plainly happened — but the question stream does not sample those
objects at the hours they have moved. So excluding s4 excludes it because the
*measurement* cannot see the event, not because the event did not happen.

Our recommendation, and the reason: **keep s4, and measure the rule over daytime
hours.** Excluding on the question-times measure selects households where the
outcome variable moves, which inflates whatever the survivors show. And s4 is the
household whose movers are *most* heterogeneous — five distinct destinations, only
33% of movers on the commonest one, against 100% on one destination in s2 and s9
— so it is the household best suited to the memory factor, not the worst. Both
counts are recorded per household in `which_objects_moved.json` either way, so
the choice stays visible.

## Null risks, stated in advance

1. **The disruption may still be one sentence long.** Even here, 4 of 10
   households send 83-100% of their movers to the same destination. The memory
   factor is strongest in s1, s3 and s4 (5 destinations each) and close to
   unfalsifiable in s2 and s9 (1 destination each). We will report the memory
   factor against the number of distinct destinations per household.
2. **The control freeze point is a null by construction** — a useful check, not a
   place an effect can live.
3. **Only 8 to 18 objects are asked about per household.** 644 to 744 questions
   are not that many independent facts; the effective sample is about 48 moved
   objects across ten households. A per-question binomial interval would be about
   four times too narrow, so intervals cluster on the household, and on the
   object within the household.
4. **The choosing arm's advantage is close to a step function per household.**
   The disruption concentrates into one room, so an arm that finds it once has
   found all of it. With ten households that means high variance on the paired
   difference.
5. **The return is not clean.** Of the objects that move, only 20% to 100% per
   household (mean 61%) go back to where they were; the rest stay put or end up
   somewhere third, and some objects that never moved have a different commonest
   place in the return window from ordinary drift anyway. "Did the memory revert
   correctly" is contaminated at roughly the 40% level, worse than the 20%
   assumed. It is measured and reported, never treated as binary.
6. **The first household will flatter.** Effects in this project have shrunk by
   half or more every time households were added. No result will be reported from
   fewer than all the included households.
7. **A cache hit is not agreement.** Generation on this server is not
   deterministic: the same notes rerun on the same data change 3 to 5% of their
   answers. Two arms whose outputs match because one was served from the
   prompt-hash cache have not been shown to agree. Differences below 5% are noise.

## How results will be reported

Per household, then combined: paired differences with standard errors and n,
clustered on the household and on the object within the household, never on the
question. Never a pooled number mixing household sets. We say what we measured
before we say what it means.
