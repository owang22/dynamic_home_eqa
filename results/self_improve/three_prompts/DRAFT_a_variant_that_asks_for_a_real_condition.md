# Draft: a variant that asks for a real condition. NOT LAUNCHED.

Brought for review, not run. Nothing in `three_prompts.ARMS` refers to it and no code path
can reach it; the prompt text below exists only in this file.

## What it is fixing

Measured on 2026-09-24 over **270 claims** in the claim-store arms: **96.3% record
`holds_under` as exactly `"current"`**, 3.7% record `"set aside for now"` — which is a
*standing* value written into the wrong field — and **not one claim names a routine, a time
or a condition.**

`holds_under` is the only field that can say *when* a claim holds. So the rival-beliefs
variant cannot be doing what its own rationale says it does. Its rationale is the existing
prompt's sentence:

> A claim about one routine does not have to be undone to write a claim about another.

But when that variant keeps both beliefs, **both carry the condition `"current"`**. The
reader is handed two contradictory claims about the same object with nothing to choose
between them. Keeping the loser cannot help, and if reachability rises while accuracy does
not, this is the mechanism rather than a surprise.

That makes `rival_beliefs` a test of a prompt we did not intend to write: it asks for two
claims and gets two claims, and the thing that would make two claims useful was never
asked for.

## The proposed prompt addition

One block, appended after the existing edit instructions, in the same place and the same
style as `KEEP_RIVAL_BELIEFS`. A pure addition, so it can be attributed.

```
Every claim has to say WHEN it holds, in its own words, and "current" is not an
answer. Say what has to be true of the household for the claim to be right: which
part of the day, which days, whether someone is at home or out, whether anything
unusual is going on. If you do not know when it holds, say that instead.

Two claims about the same thing may both be worth keeping, but only if their
conditions differ. If you cannot say what tells them apart, you have not learned
two things -- you have changed your mind, and you should say which one holds now.
```

The second paragraph is what makes this more than a tidier field: it makes the condition
the *reason* for keeping a rival rather than a label attached afterwards.

## How it would be run, and what would decide it

Two arms, because the point is whether the condition is what makes rivals useful:

| arm | what it is |
|---|---|
| `real_condition` | the unchanged prompt plus the block above |
| `rival_and_condition` | `rival_beliefs` plus the block above |

Against the existing `control` and `rival_beliefs` on the same ten homes, everything else
identical, so the four arms form a 2x2 and the interaction is the question.

**Compliance first, and it has a clear threshold.** The share of claims whose `holds_under`
names a routine rather than `"current"`, `"not said"` or a standing value. The control
baseline is **0 of 270**. If the share does not move off zero, the variant failed and no
outcome from it means anything — the same rule the rival-beliefs gate was held to.

A second compliance measure, which is the one that matters for the 2x2: **among pairs of
claims about the same object that are both readable, the share whose conditions differ.**
Under `rival_beliefs` today that share is 0 by construction, because every condition is
`"current"`. If `rival_and_condition` does not move it, the interaction cannot exist.

**Then the outcomes**, the same four end-to-end measures as everything else, paired within
home, clustered on home, and judged against the rerun noise floor in
`the_rerun_noise_floor.json` — 1.9 points on first-room-right, 1.5 on shelf accuracy — not
against a standard error alone.

## Three reasons to be sceptical before spending the GPU

1. **It may just relabel.** The model may write a condition because it was asked and have
   it carry no information — `"when the resident is at home"` on every claim is `"current"`
   with more words. The compliance measure would pass and nothing would change. Guard: count
   *distinct* conditions per home and per object, not just non-`"current"` ones.
2. **The reader may ignore it.** Even a good condition only helps if the answer step uses
   it. The answer prompt shows `holds_under` already, so nothing needs to change — but the
   existing evidence that the model names a room it has just searched and found empty is not
   encouraging about its use of what it is shown.
3. **It costs tokens in the same place the edit budget already binds.** See below.

## A thing that must be settled before this or anything else is read

**The new edit allowance binds on the first night.** Two edits per asked-about object gives
22 for `hh_s2_t03`. On night 1 that cell saw **47 distinct objects** and offered **exactly
22 edits** — the cap, exactly. So `2 x asked_objects` is not "a number that cannot bind"
now that the quiz list is off: with the list gone the writer describes what it saw, and what
it saw is the house, not the quiz. The natural denominator is objects observed, not objects
asked about.

That matters for this draft because a condition on every claim makes each edit longer, so
the same allowance buys fewer facts. **Any 2x2 built on top of a cap that binds is partly a
test of the cap.** I have not changed the allowance — it is the coordinator's number and the
rationale was explicit — but it should be decided before this variant runs.
