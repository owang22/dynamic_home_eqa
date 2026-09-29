#!/usr/bin/env python3
"""Builds results/self_improve/paper/appendix_material.md.

Every verbatim block is pulled out of the file it lives in by line range, and every prompt is
rendered by the builder that sends it, so the appendix cannot drift from the code the way a
pasted quotation does. Re-run it after any change to the two method modules or the prompts.

    PYTHONPATH=src python3 results/self_improve/paper/scripts/write_appendix_material.py
"""
import contextlib
import io
import json
import pathlib
import sys

sys.path.insert(0, "src")
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

OUT = pathlib.Path("results/self_improve/paper/appendix_material.md")
SRC = pathlib.Path("src/self_improve")


def quote(path, first, last):
    """Lines first..last of a file, one-indexed and inclusive, exactly as they stand."""
    lines = pathlib.Path(path).read_text().splitlines()
    block = "\n".join(lines[first - 1:last])
    # a module header quoted from line 1 arrives wrapped in its own triple quotes
    return block.removeprefix('"""').removesuffix('"""').strip("\n")


def rendered_prompts():
    import the_prompts_verbatim
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        the_prompts_verbatim.main()
    return buf.getvalue()


def memgpt_numbers():
    """Block cap, nights and refusals, counted from the landed cells themselves."""
    import glob
    out = {}
    for label, pat, capkey, sharekey, refusals, archive in (
            ("tight variant, 1,200",
             "results/self_improve/overnight_wave/cells/"
             "a_small_working_memory_and_an_archive/*/cell.json",
             "characters_in_working_memory", "share_of_working_memory_used",
             ("refused_because_working_memory_was_full",), "n_notes_in_the_archive"),
            ("MemGPT as published, 24 questions a day",
             "results/self_improve/overnight_wave_24_questions/cells/"
             "MemGPT_as_published/*/cell.json",
             "characters_in_the_block", "share_of_the_block_used",
             ("refused_because_the_block_was_full",
              "refused_because_the_piece_was_not_there"), "n_passages_in_the_archive"),
            ("MemGPT as published, the reason-first wave",
             "results/self_improve/wave_reasons_first/cells/"
             "MemGPT_as_published/*/cell.json",
             "characters_in_the_block", "share_of_the_block_used",
             ("refused_because_the_block_was_full",
              "refused_because_the_piece_was_not_there"), "n_passages_in_the_archive")):
        caps, nights, cells, chars = set(), 0, 0, []
        counts = {k: 0 for k in refusals}
        archives = []
        for f in sorted(glob.glob(pat)):
            cells += 1
            for n in json.load(open(f)).get("nightly") or []:
                nights += 1
                c, s = n.get(capkey), n.get(sharekey)
                if c and s:
                    caps.add(round(c / s))
                if c:
                    chars.append(c)
                for k in refusals:
                    counts[k] += len(n.get(k) or [])
                archives.append(n.get(archive, 0))
        out[label] = dict(cells=cells, nights=nights, caps=sorted(caps), refusals=counts,
                          chars=chars, archive_max=max(archives) if archives else 0)
    return out


def main() -> int:
    from self_improve.grouping_by_meaning import HOW_MANY_PAIRS_TO_PROPOSE
    from self_improve.memory_notes import (A_DELIBERATELY_TIGHT_WORKING_MEMORY,
                                           WORKING_MEMORY_CHARACTERS)
    from self_improve.write_the_notes_memgpt_as_published import HOW_MANY_PASSAGES_A_PAGE
    m = memgpt_numbers()

    def row(label):
        d = m[label]
        chars = sorted(d["chars"])
        median = chars[len(chars) // 2] if chars else 0
        refused = ", ".join(f"{k.replace('_', ' ')}: {v}" for k, v in d["refusals"].items())
        return (f"| {label} | {d['cells']} | {d['nights']} | "
                f"{', '.join(str(c) for c in d['caps'])} | {median} | {max(chars or [0])} | "
                f"{refused} |")

    text = f"""# Appendix material

Everything here is generated. `write_appendix_material.py` pulls each verbatim block out of the
file it lives in by line range and renders each prompt with the builder that sends it, so nothing
in this document is a transcription. Re-run it after any change to the method modules or prompts:

    PYTHONPATH=src python3 results/self_improve/paper/scripts/write_appendix_material.py

---

## 1. Differences from ACE

The paragraph should quote the header of `src/self_improve/write_the_notes_told_if_right.py`. The
brief asked for lines 34 to 56; line 34 starts mid-sentence, so the block below is lines **33 to
65**, which is the whole of the two lists - the differences from the released code, and the
differences from the paper.

> {quote(SRC / 'write_the_notes_told_if_right.py', 33, 65).replace(chr(10), chr(10) + '> ')}

### The grouper

`grouping_by_meaning.pairs_worth_asking_about` proposes at most **{HOW_MANY_PAIRS_TO_PROPOSE} pairs a night** (`HOW_MANY_PAIRS_TO_PROPOSE = {HOW_MANY_PAIRS_TO_PROPOSE}`). It ranks every
eligible pair by the cosine of two mean-pooled Llama-3.2-1B vectors, most alike first, and hands
the top four to the model, which decides for each whether the two notes say one thing. The
embedding never decides a merge on its own - there is no similarity threshold - for the reason in
that module's header: measured on this machine, unrelated sentences already score 0.83 to 0.88 on
this model, so ACE's 0.90 does not transfer to it.

**One thing to state carefully.** That function's docstring says two rules make a pair eligible:
the same condition, and the same object. The code enforces only the first - it compares
`holds_under` and nothing else - and the caller in `write_the_notes_told_if_right.py` passes every
live claim. So the appendix should say pairs are restricted to notes holding under the same
condition, and not claim an object restriction. What keeps one object's two routines apart is the
condition test plus the sentence in the merge prompt: *"Two notes about the same object at
different times of day are NOT the same note."*

---

## 2. Differences from MemGPT

> {quote(SRC / 'write_the_notes_memgpt_as_published.py', 1, 28).replace(chr(10), chr(10) + '> ')}

### Block sizes, and which run used which

**The brief's parenthetical needs correcting.** The 1,200-character block and the
20,000-character block are not the ten-household run and the three-household run. They are two
different arms in two different waves:

- `WORKING_MEMORY_CHARACTERS = {WORKING_MEMORY_CHARACTERS}` is MemGPT's own number, from `letta/constants.py`, where `CORE_MEMORY_PERSONA_CHAR_LIMIT` and
  `CORE_MEMORY_HUMAN_CHAR_LIMIT` are both 20,000. This is the arm called **MemGPT as published**,
  and it ran in `overnight_wave_24_questions` and `wave_reasons_first`.
- `A_DELIBERATELY_TIGHT_WORKING_MEMORY = {A_DELIBERATELY_TIGHT_WORKING_MEMORY}` is a sixteenth of that, anchored on this study's own summary length. It is the arm called **a small working memory
  and an archive**, and it ran on the ten households in `overnight_wave`. The paper must call this
  the tight variant and never MemGPT.
- **The three-household 50-day run has no MemGPT arm of any size.** Its cells are
  `last-seen`, `the log and notes`, `incremental edits`, `ACE as published` and
  `ours told the night before`.

Counted from the cells' own nightly records - the cap is recovered by dividing the characters held
by the share of the block reported, so these are the caps that were actually in force, not the
constants as they stand today:

| arm and wave | cells | nights | cap recovered | median characters held | largest | refused writes |
|---|---|---|---|---|---|---|
{row('tight variant, 1,200')}
{row('MemGPT as published, 24 questions a day')}
{row('MemGPT as published, the reason-first wave')}

### Substring-replacement edits

`replace_part_of_the_block` is an exact substring match, as theirs is. The piece named must appear
in the block character for character; if it does not, nothing is replaced and the model is handed
back:

> that piece is not in your block, character for character, so nothing was replaced. Quote it
> exactly as it appears.

### Archive search on the asked object

The archive is reached only by searching, at two moments. At night the writer may call
`search the archive`, which returns {HOW_MANY_PASSAGES_A_PAGE} passages a page with the page count,
and asks for the next page in the same reply rather than in a later turn - their search is
interactive across turns and a nightly write here is one call. At answer time
`memory_notes.what_the_robot_can_read` shows the block in full and searches the archive for **the
object the question asks about**, which is the only way an archived passage ever reaches a prompt.
The search is word overlap, not vectors, and it skips anything already in the block.

### Refused writes on overflow

A write that would take the block past its cap is refused and the refusal is handed back, both for
an append and for a replacement that grows the text. The wording the model receives, with the real
numbers substituted:

> your block holds 19967 of 20000 characters, so there is no room for 768 more. Move something to
> the archive first, or replace a piece of the block instead of adding to it.

This is a reading of the paper's prose rather than a match to their code: the research agent could
not reach an enforcement point in the released source, and that is stated as a reading.

---

## 3. Prompts

Rendered by the builders themselves, on household `hh_s2_t03`, night 1, with that cell's own
looks read back from `looks.jsonl`. Night 1 is used because it is the one night whose inputs
reproduce exactly - the notes are empty, so nothing has to be rewound, and the cells keep only the
end state of the memory. The edit allowance the renderer computes, 51, is the number that cell
recorded for night 1, which is the check that this is the prompt that was sent.

Both calls go to `Qwen/Qwen3.8-27B` at temperature 0, seed 0, with `enable_thinking` false and the
schema enforced by the server as a JSON schema response format.

```
{rendered_prompts()}
```
"""
    OUT.write_text(text)
    print(f"wrote {OUT}  ({len(text.splitlines())} lines)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
