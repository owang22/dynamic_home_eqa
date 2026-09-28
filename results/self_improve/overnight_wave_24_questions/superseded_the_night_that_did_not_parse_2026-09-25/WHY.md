# The two published-MemGPT cells whose completion did not parse, kept as they first ran

Moved aside 2026-09-25, not deleted, because the accuracy numbers for `MemGPT as published` at
24 questions a day come from **reruns** of these two cells, and a rerun reported without the
original failure is selection on outcome.

| cell | the night that did not parse |
|---|---|
| `MemGPT as published` / `hh_s32_t03` | night 8 |
| `MemGPT as published` / `hh_s48_t03` | night 6 |

The call succeeded on both nights and the completion was malformed, so the night wrote nothing.
The gate held both cells, correctly. **2 of 96 nights for this arm, 2.1%, against 0 of 1,920 for
every other arm that makes a nightly call** — recorded as a reported number in
`../THE_PARSE_FAILURES.json` and printed in the compliance gate, section 0b2.

Not truncation, which was the first explanation and the wrong one: at the failing night the
block held 8,070 characters, and the same cell parsed nineteen later nights with the block at
19,898 of 20,000. The arm emits edit calls rather than rewriting the block, so its 2,600-token
budget is ample. The suspicion is the editing interface itself — this is the one arm asked to
edit a 20,000-character block by quoting substrings of it, and these three cells quoted a piece
that was not there 9, 7 and 3 times.

**If a rerun fails to parse on the same night, that is reported rather than rerun again.** Two
failures on one night would make it a property of that night's prompt rather than noise.

The frozen-block result these cells carry does not depend on the reruns: the block fills to
~19,900 of 20,000 and then refuses writes on 4, 12 and 12 nights, the archive holds 0 passages
at every point in all three cells, and on two of three households the refusals run unbroken from
night 19 or 20 to 31 — the whole recovery window.
