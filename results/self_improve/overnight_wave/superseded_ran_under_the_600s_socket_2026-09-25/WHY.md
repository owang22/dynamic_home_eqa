# Moved aside 2026-09-25 ~11:30: run under a 600-second socket timeout, being rerun

These five cells each lost at least one model call to the same bug, and nothing else. In
`baselines/patrol/llm.py` the connection was built with `timeout=min(600.0, self.DEADLINE_S)`
while `DEADLINE_S` is 900: two limits on one quantity, and the smaller one — which nobody
chose — was the real one. Every lost call in this wave failed at **exactly 600 seconds on both
attempts** with `TimeoutError: timed out`. Not a server error, not a schema rejection, nothing
content-related: the generation was still running and the socket gave up.

`timeout=self.DEADLINE_S` now. The watchdog thread still shuts the socket at 900, so a
genuinely lost request is still bounded and nothing can wait longer than it could before.

## What each moved cell lost

| cell | what the loss was | nights or day affected |
|---|---|---|
| `claim store told if it was right` / `hh_s123_t03` | nightly write | night 15 |
| `claim store told if it was right` / `hh_s151_t03` | nightly write | nights 8, 9, 11 |
| `claim store told if it was right` / `hh_s32_t03` | nightly write | night 29 |
| `claim store told if it was right` / `hh_s2_t03` | **an answer-step call on day 3** | one question answered by fallback |
| `incremental edits` / `hh_s63_t03` | nightly write | night 16 |

`hh_s2_t03` is the one to notice: its loss was a *question* call, not a nightly write, so it
carries no `model_call_failed` night and no gate ever saw it. An audit of `model_call_failed`
alone would have reported this cell clean. The losses were found by grepping the logs for
`LOST after 2 attempts`, which is the only place an answer-step loss is recorded.

Nothing here is deleted; the reruns land in `../cells/` and these copies stay for comparison.
Because the prompt cache is keyed on the request, a rerun replays every night up to its first
loss and only regenerates from there: `hh_s32_t03` (night 29) is nearly free, `hh_s151_t03`
(night 8) is most of a cell.

There is no exclusion rule and no permanent content deficit. `../THE_FAILED_NIGHTS_were_one_bug.md` is kept
as a record of the fault, not as a caveat on the numbers.

## A second, unrelated fault found while moving these: one MemGPT cell had crashed

`a small working memory and an archive / hh_s19_t03` (partial run kept beside these, under
`..._crashed_on_the_render_assert`) died at day 3 with

    AssertionError: ... the note-writing prompt did NOT go through the search-driven day
    renderer, so what the model was shown is not what this module claims.

It had. The guard in `search_driven.run_one_cell` required the day-render counter to increase
by **exactly one** per night, and this arm renders **twice** on a night when a write is refused
for want of room and it is given a second go — through the same renderer, with the same text.
So the one arm whose defining feature is an overflow refusal could not survive its first
refusal. Now `>= 1`, which is the fault the guard exists to catch (a writer that builds the day
itself leaves the counter unmoved); the count is recorded per night as
`n_times_the_day_was_rendered_for_the_writer`. Checked all three ways before trusting it:
renders once passes, renders twice passes, renders never still raises.

Two related things it exposed, both now fixed:

* `RUNNING.lock` was removed only by the gate, never on success or on a crash, so it meant
  "was started" while its name says "is running". Three MemGPT cells showed as running at
  11:30 when two had finished and this one had been dead for thirteen minutes.
* a crash left nothing on disk at all. It now writes `CRASHED.txt`, so a directory listing
  distinguishes crashed from held-by-a-gate from finished.

**A second cell died the same way**: `a small working memory and an archive / hh_s151_t03`, at
day 20, with the identical AssertionError. Two of the arm's ten cells, on their first night
with a refused write, which is the strongest evidence that the double render is this arm's
retry and not something stranger. Both were relaunched after the guard was corrected. It also
shows what the leftover lock cost: with the lock meaning "was started", nothing in the wave's
own status distinguished these two dead cells from two slow ones.
