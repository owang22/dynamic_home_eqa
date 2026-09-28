# Superseded, not deleted: the partial cells run under the 8-line budget

These 14 cells were launched at 19:51 on 2026-09-24 and stopped by me at 19:59, after
the coordinator's correction arrived: **remove the memory length limit entirely, in
writing and in reading.** They were running with `read_budget_lines = 8` at answer time,
which is the confound the correction removes, so every number they would have produced
was uninterpretable for the question being asked. None of them reached `cell.json`.

Nothing here was deleted. The look streams and the partial notes are intact, and the
prompt cache they warmed is what makes the relaunch cheap: the room-choice prompts and
the nightly note-writing prompts are **byte-identical** under the correction (the
claim-store writing prompt never mentioned a budget, and the chooser was always shown
all of the notes), so those calls replay from cache. Only the fallback answer prompt
changed, because that is the one place the 8-line window was applied.
