# Every failed call in this wave was one bug. It is fixed and the cells were rerun.

**This is not a caveat on any number.** It used to be: this file held an exclusion rule naming
four cells and the days to drop. There is no exclusion rule now, because the cause was found
and the affected cells were rerun rather than annotated. Nothing in the accuracy section refers
to it. The fault is recorded here because it is worth recording.

## The bug

`baselines/patrol/llm.py`, `LLMClient._post`, built its connection with

```python
timeout=min(600.0, self.DEADLINE_S)        # DEADLINE_S = 900
```

Two limits on one quantity. The smaller one was the real one, and nobody chose it: a watchdog
thread exists to bound a call at 900 seconds, and the socket gave up three hundred seconds
before it. Now `timeout=self.DEADLINE_S`; the watchdog still shuts the socket at 900, so a
genuinely lost request is still bounded and nothing can wait longer than it could before.

## What made it unambiguous

**24 failed calls across the wave, and every single one was `TimeoutError: timed out` at
exactly 600 seconds, on both attempts:**

```
llm call failed (1/2, 600s in): TimeoutError: timed out
llm call failed (2/2, 1202s in): TimeoutError: timed out
llm call LOST after 2 attempts (1206s): falling back for this question
```

Not a server error, not a schema rejection, nothing content-related. The generation was still
running. Exactly 600 on every one of 24 is a constant in our own code, not a property of the
server or of the prompts.

## The five cells, and what each lost

| cell | what was lost | when |
|---|---|---|
| `claim store told if it was right` / `hh_s123_t03` | a nightly write | night 15 |
| `claim store told if it was right` / `hh_s151_t03` | three nightly writes | nights 8, 9, 11 |
| `claim store told if it was right` / `hh_s32_t03` | a nightly write | night 29 |
| `claim store told if it was right` / `hh_s2_t03` | **an answer-step call** | one question on day 3 |
| `incremental edits` / `hh_s63_t03` | a nightly write | night 16 |

All five were moved to `superseded_ran_under_the_600s_socket_2026-09-25/` — not deleted — and
rerun under the fixed socket. Because the prompt cache is keyed on the request, a rerun replays
every night up to its first loss and regenerates from there.

## The part worth remembering: a failed-night flag did not find all of it

`hh_s2_t03` lost an **answer-step** call, not a nightly write. It therefore carried no
`model_call_failed` night anywhere, no gate ever saw it, and the audit that produced the old
four-cell table — which read that flag — reported it clean. It was found by grepping the run
logs for `LOST after 2 attempts`, the only place an answer-step loss is recorded. The old table
in this file was not just too cautious, it was **incomplete**, and in the direction that
matters: a question answered by fallback goes straight into the accuracy numbers, where a lost
nightly write only thins the notes.

Where a measurement can be lost in two places, an audit that reads one of them will report
clean.

## What the old exclusion rule got right, kept for the record

The exclusion was "drop day N+1, not day N", and the reason stands: the nightly write happens
at the *end* of day N, after that day's questions are answered, so a night-N failure cannot
reach day N's answers. It is written down here in case a lost call ever has to be tolerated
rather than rerun.
