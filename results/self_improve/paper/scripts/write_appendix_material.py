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


def scenario_numbers():
    """The illness event, read out of the two scenario files the paper's runs were built from."""
    import yaml
    out = {}
    for tag, name in (("main", "events_varied.yaml"), ("wider", "events_varied_v3.yaml")):
        d = yaml.safe_load((pathlib.Path("results/self_improve/varied_homes/scenario")
                            / name).read_text())
        ev = d["events"]["unwell_spell"]
        out[tag] = dict(file=name, rules=[r["class"] for r in ev["placement"]],
                        removed=len(ev["schedule"]["remove"]),
                        added=[a["activity"] for a in ev["schedule"]["add"]],
                        internal=ev["internal"])
    return out


def merge_numbers():
    """What each ACE arm's grow-and-refine step did, over every landed cell of each wave.

    `n_pairs_proposed` is how many pairs the embedding handed the model; `n_merged` and
    `n_rejected` come only from what the model sent back, so a night where the reply did not
    parse counts as a pair proposed and no verdict. That gap is the point of the table.
    """
    import glob
    out = {}
    for label, pat in (
            ("ten-household run, 8 a day (claim_store_told_if_it_was_right)",
             "results/self_improve/overnight_wave/cells/"
             "claim_store_told_if_it_was_right/*/cell.json"),
            ("50-day run, 24 a day (ACE_as_published)",
             "results/self_improve/wave_the_second_illness/cells/ACE_as_published/*/cell.json"),
            ("ten households, 24 a day (ACE_as_published)",
             "results/self_improve/overnight_wave_24_questions/cells/"
             "ACE_as_published/*/cell.json")):
        cells = nights = proposed = merged = rejected = by_rule = asked = silent = 0
        for f in sorted(glob.glob(pat)):
            cells += 1
            for n in json.load(open(f)).get("nightly") or []:
                nights += 1
                m = n.get("how_it_merged") or {}
                proposed += m.get("n_pairs_proposed", 0)
                merged += m.get("n_merged", 0)
                rejected += m.get("n_rejected", 0)
                if m.get("n_pairs_proposed", 0):
                    asked += 1
                    if m.get("n_merged", 0) + m.get("n_rejected", 0) == 0:
                        silent += 1
                j = n.get("joined_by_rule_not_by_the_model")
                by_rule += len(j) if isinstance(j, list) else (1 if j else 0)
        out[label] = dict(cells=cells, nights=nights, proposed=proposed, merged=merged,
                          rejected=rejected, by_rule=by_rule, asked=asked, silent=silent)
    return out


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
    mg = merge_numbers()
    sc = scenario_numbers()
    main_file, wider = sc["main"]["file"], sc["wider"]
    removed, added = sc["main"]["removed"], sc["main"]["added"]
    n_added = len(set(added))
    added = ", ".join(sorted(set(added)))
    no_rule = ", ".join(c for c in ("book", "water_bottle", "tablet", "mug", "charger", "glasses",
                                    "glass", "razor", "medication", "towel", "notebook")
                        if c not in sc["main"]["rules"])
    energy = f"by {sc['main']['internal']['energy']}"
    hurried = f"by {sc['main']['internal']['hurriedness']}"
    rules = sc["main"]["rules"]
    n_rules, n_classes = len(rules), 11
    rule_list = ", ".join(rules)
    extra_rules = ", ".join(r for r in wider["rules"] if r not in rules)

    def merge_row(label):
        d = mg[label]
        return (f"| {label} | {d['cells']} | {d['nights']} | {d['proposed']} | "
                f"{d['merged']} | {d['rejected']} | {d['silent']} of {d['asked']} | "
                f"{d['by_rule']} |")

    merge_counts = f"""| arm and wave | cells | nights | pairs proposed | merged | rejected | nights asked with no verdict | joined by rule |
|---|---|---|---|---|---|---|---|
{merge_row('ten-household run, 8 a day (claim_store_told_if_it_was_right)')}
{merge_row('50-day run, 24 a day (ACE_as_published)')}
{merge_row('ten households, 24 a day (ACE_as_published)')}

**The ten-household arm never ran the step at all.** Zero pairs proposed in
{mg['ten-household run, 8 a day (claim_store_told_if_it_was_right)']['nights']} nights: its merge
sits behind a line budget that was never reached. All the joining it did -
{mg['ten-household run, 8 a day (claim_store_told_if_it_was_right)']['by_rule']} joins - was the
deterministic backstop in `keep_the_notes_from_growing`, which folds the claim with the worst
record into the live claim it shares most words with.

**In the 50-day run the step was nearly inert, and that needs saying in the paper.** It proposed
{mg['50-day run, 24 a day (ACE_as_published)']['proposed']} pairs and the model returned a verdict
on {mg['50-day run, 24 a day (ACE_as_published)']['merged'] + mg['50-day run, 24 a day (ACE_as_published)']['rejected']} of them,
merging {mg['50-day run, 24 a day (ACE_as_published)']['merged']} notes in
{mg['50-day run, 24 a day (ACE_as_published)']['nights']} nights over three households. On
{mg['50-day run, 24 a day (ACE_as_published)']['silent']} of the
{mg['50-day run, 24 a day (ACE_as_published)']['asked']} nights that proposed a pair, nothing came
back. The same code on the same three households at 24 questions a day, run the day before, was
silent on only {mg['ten households, 24 a day (ACE_as_published)']['silent']} of
{mg['ten households, 24 a day (ACE_as_published)']['asked']} and merged
{mg['ten households, 24 a day (ACE_as_published)']['merged']} notes.

**A likely cause, not yet confirmed.** `merge_what_says_the_same_thing` calls the model with
`max_tokens=900`. Commit `b4207b7b3` (2026-09-26 20:49) raised that call's schema from four merges
to twelve and its `why` field from 200 characters to 600, and left `max_tokens` where it was. A
reply carrying several 600-character explanations does not fit in 900 tokens; it is cut off,
`json.loads` raises, and the handler sets `merges = []` with nothing recorded. The timing fits two
of the three cells: `hh_s2_t03` finished at 18:36 that day, before the commit, and answered on 9 of
its 43 asked nights; `hh_s32_t03` and `hh_s48_t03` finished at 23:23 and 08:13 the next morning,
after it, and answered on exactly one night each - `hh_s32_t03` was silent from night 1 onward. It
does not explain `hh_s2_t03`'s own 9 of 43, so there is a second thing to find. Until it is found,
the paper should not describe the 50-day playbook's grow-and-refine as having run.""" 

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

### There are two ACE arms, and they are not the same arm

The paper calls both of them the ACE-style playbook. The code keeps them apart, and the paragraph
has to as well, because the grow-and-refine step works in **opposite directions** in the two.

| | ten-household run (Table 1, Figure 4) | 50-day run (Table 2, Figure 2) |
|---|---|---|
| cell directory | `claim_store_told_if_it_was_right` | `ACE_as_published` |
| looking back | once, unconditionally | up to three rounds, stopping early when nothing went wrong |
| when it merges | only when the store is over a line budget | every night |
| how pairs are grouped | shared words | sentence embedding, most alike first |
| who writes the merged note | the code, by deterministic concatenation | the model |

Both run through `write_the_notes_told_if_right.py`; the second is the first with
`as_published=True` (that file, `write_the_notes_told_if_right`). `memory_notes.py` states the
three differences and nothing else separates them.

**So the draft's sentence mixes the two.** "Ours ranks pairs by embedding, hands at most four pairs
a night to the model, which decides whether they say one thing, and merges by deterministic
concatenation" describes the embedding ranking and the model verdict of the **50-day** arm and the
deterministic merge of the **ten-household** arm. No single arm does both. It should read: the
ten-household arm groups by shared words and merges in code with no model call; the 50-day arm
ranks by embedding, hands at most four pairs a night to the model, and the model decides and writes
the merged note.

### What the module header says, and where it is now out of date

Quoted verbatim, lines **33 to 65** of `src/self_improve/write_the_notes_told_if_right.py`. The
brief asked for 34 to 56; line 34 starts mid-sentence, and 33 to 65 is the whole of both lists.
**The header was written for the ten-household arm, before `ACE as published` existed.** Its second
bullet - "Ours is the mirror image: word overlap for the grouping, and a deterministic
concatenation for the merge" - and the third of its three differences from the paper are true of
that arm only. The 50-day arm closes both gaps.

> {quote(SRC / 'write_the_notes_told_if_right.py', 33, 65).replace(chr(10), chr(10) + '> ')}

### The grouper, and the four pairs a night

`grouping_by_meaning.pairs_worth_asking_about` proposes at most **{HOW_MANY_PAIRS_TO_PROPOSE} pairs a night** (`HOW_MANY_PAIRS_TO_PROPOSE = {HOW_MANY_PAIRS_TO_PROPOSE}`). It ranks every
eligible pair by the cosine of two mean-pooled Llama-3.2-1B vectors, most alike first, and hands
the top four to the model, which decides for each whether the two notes say one thing and writes
the note that replaces both. There is no similarity threshold, for the reason in that module's
header: measured on this machine, unrelated sentences already score 0.83 to 0.88 on this model, so
ACE's 0.90 does not transfer to it. **This step runs in the 50-day arm only.**

**One thing to state carefully.** That function's docstring says two rules make a pair eligible:
the same condition, and the same object. The code enforces only the first - it compares
`holds_under` and nothing else - and the caller passes every live claim. So the appendix should say
pairs are restricted to notes holding under the same condition, and not claim an object
restriction. What keeps one object's two routines apart is the condition test plus the sentence in
the merge prompt: *"Two notes about the same object at different times of day are NOT the same
note."*

### What the merging step actually did, counted from the cells

{merge_counts}

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

---

## 4. Simulator dynamics

The households are generated by `src/situation_sim`, and nothing about the illness is written into
a household by hand. A **day is a hidden situation**: a set of causes drawn for that day, which
rewrite the day's schedule and move many objects at once. That is the whole design - a cause is
modelled explicitly only when it moves more than one object, and single-object noise is left to a
*whim* term.

**A day.** Each resident has a role, and the role carries a weekday and weekend schedule of
activities with free slots that habits fill. `schedule.py` turns that into the day's bouts: habits
fire once per resident per day with their own probabilities, household chores once per home, bouts
are skipped in proportion to how tidy the resident is, start times are jittered by their
punctuality, and long bouts fragment around kitchen breaks. Nothing is tied to a fixed date beyond
the weekday/weekend split.

**Where a thing ends up.** While a bout runs, the objects it uses sit on that bout's surface - a
laptop on the desk - and pocket items ride on the person. When the bout ends, every used object the
next bout does not need goes through one decision function, in this order: an event's placement
rule, a tidy pass, the arriving-home rule (put away, or dumped at the door), the home-activity rule
(carried into the next room if the resident is distracted, left where it was used, sent to the sink
if it is a dirty dish, or put back), a fallback if the intended spot is occupied or blocked, and
finally whim. The size of the whim term scales with the resident's traits and how hurried the day
is. A decision that lands an object where it already is counts as a decision and not as a move.
Attribution is exact: a cause is credited only with the probability mass it added.

Measured on the banks the paper runs on, each household holds **76 to 104 objects**, of which
**52 to 74 ever change place** - the rest are fixtures the generator records once - and residents
make **106 to 213 object moves a day**
(`what_a_household_is_made_of.py`).

**The change in routine.** The scenario file forces one event, `unwell_spell`, on `resident_1` for
days 14 to 23, and again for days 32 to 41 in the 50-day run. Every other event in the catalogue -
rain, a guest, late work, a grocery delivery, laundry day, an ordinary sick day - is set to
probability zero, and every stage sets `suppress_random_events`, so **the illness is the only live
event in the month** and it does nothing at all before day 14.

The event itself ({main_file}) does three things:

- **It empties the day.** {removed} activities are removed, among them the commute, work sessions,
  classes, shifts, video calls, every trip out, every form of exercise, errands, the shopping,
  all four ordinary meals and the washing up, and four whole schedule slots.
- **It fills the day with nine bouts**, all at home, from {n_added} distinct activities -
  {added} - with `rest_coffee` twice, at 13:00 and 20:15. It also sets the resident's energy
  {energy} and hurriedness {hurried}, which feeds back into the whim term.
- **It carries {n_rules} placement rules**, and these are what actually move the answers:
  {rule_list}. Everything else in the house keeps moving for its own reasons.

The rules cover {n_rules} of the {n_classes} kinds the questions ask about in this scenario;
{no_rule} have no rule at all. But a rule only fires after a bout the **ill** resident had, so a
well resident's mug and glass stay where they always were. Both kinds of control matter: a class
with no rule, and a ruled class owned by somebody who is not ill. A memory that spreads the
illness across the whole house is wrong about all of them. The wider five-household scenario adds
two more rules ({extra_rules}) and widens the question list from 11 kinds to 21.

**The second illness is a fresh draw, not a replay.** The same event is forced on the same resident,
but the bout counts and every placement decision are resampled for those days. The evidence is in
the outcome: of the 22 objects whose commonest daytime room changes in the first illness, **8 do
not change room in the second**, which is why the paper's recurrence tables use the 14 that change
in both.

Same seed, same files: `situation_sim` is deterministic, and every arm of a household reads one
frozen bank, so the world and the question schedule are identical across arms (checked by hashing
in `results/memoryWorkshop/CHECKS_ON_THE_DRAFT.md`, item 6).
"""
    OUT.write_text(text)
    print(f"wrote {OUT}  ({len(text.splitlines())} lines)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
