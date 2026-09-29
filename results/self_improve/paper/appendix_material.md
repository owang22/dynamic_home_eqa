# Appendix material

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

> HOW THIS DIFFERS FROM THE REAL ACE, checked against github.com/ace-agent/ace rather than
> against the paper's prose, by the research agent. The shape is faithful; several load-bearing
> specifics are not, and they diverge in BOTH directions:
> 
>   - their Reflector loops up to three rounds and only when the answer was wrong, stopping
>     early on a correct one. Ours is one unconditional call every night. This is the clearest
>     divergence and it is the reason this arm is "inspired by ACE's three-role division"
>     rather than "ACE's Reflector".
>   - their grow-and-refine groups by real sentence embeddings (all-mpnet-base-v2, cosine at
>     0.90) and then has an LLM author the merged text. Ours is the mirror image: word overlap
>     for the grouping, and a deterministic concatenation for the merge with no model involved.
>     The paper's "lightweight, non-LLM logic" describes their grouping step only, not the
>     merge. Both halves differ, and in opposite directions, so they are named separately.
>   - their bullets carry no condition field at all. `holds_under` - the thing that lets a
>     claim say "true only under this routine" - is this study's own addition to the format and
>     must not be presented as ACE's.
>   - their released code defines ADD, UPDATE, MERGE and DELETE but executes only ADD; the rest
>     are unused in the shipped batched workflow. Ours actually runs revise, attach-evidence
>     and join. That is a point in this arm's favour rather than a shortfall, and it is stated
>     because a reader who checks the repository would otherwise find the gap themselves.
>   - their DELETE removes a bullet's content outright. Ours never deletes, which was already
>     recorded below and the real code confirms rather than changes.
> 
> Three differences from the paper, all deliberate and all to be stated in the write-up:
>   - the paper's Generator is a reasoning model producing trajectories; here it is
>     the robot's own room choices and answers, which is the task this study has.
>   - the paper scores its playbook lines on a benchmark with a known answer key. Here
>     the outcome is whether the first room opened held the object, which is the
>     measure the study reports, so the feedback is honest: nothing in it tells the
>     robot a place it has not seen.
>   - the paper dedups by comparing sentence vectors. Here the model is asked to fold,
>     with a deterministic backstop below when it does not and the notes are over the
>     line it has been given.

### The grouper

`grouping_by_meaning.pairs_worth_asking_about` proposes at most **4 pairs a night** (`HOW_MANY_PAIRS_TO_PROPOSE = 4`). It ranks every
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

> MemGPT the way MemGPT is built: one block of free text, plus an archive it must search.
> 
> Our first MemGPT arm kept numbered notes in both tiers, which is a claim store with a size
> limit rather than MemGPT. Their core memory is ONE BLOCK OF FREE TEXT, and the model edits it
> by naming a piece of the text and what to put in its place; their archive holds separate
> passages that are only ever reached by searching. That shape is what this module adds, and it
> is the difference that made the earlier arm an imitation.
> 
> The four things their agent can actually do, and the four things here:
> 
>   core_memory_append      add a line to the end of the block
>   core_memory_replace     name an exact piece of the block and what replaces it. Naming a
>                           piece that is not there FAILS, as theirs does - it is a substring
>                           match, not a fuzzy one, and the failure is reported to the model.
>   archival_memory_insert  put a passage in the archive
>   archival_memory_search  ask the archive for passages, a page at a time
> 
> Sizes are theirs: `letta/constants.py` puts the persona and human blocks at 20,000 characters
> each. A write that would overflow is refused and the refusal is handed back, which is a
> faithful reading of the paper's prose - the research agent could not reach an enforcement
> point in the code, so that is stated as a reading rather than as a match.
> 
> Two departures that remain, both disclosed rather than fixed. Moving something from the block
> to the archive is two calls for them (insert, then replace with nothing) and two here as well,
> so that one is faithful. But their archive search is interactive across turns - page one, then
> the model asks for page two - and a nightly write here is one call, so pages are offered by
> asking for more in the same reply rather than in a later turn.

### Block sizes, and which run used which

**The brief's parenthetical needs correcting.** The 1,200-character block and the
20,000-character block are not the ten-household run and the three-household run. They are two
different arms in two different waves:

- `WORKING_MEMORY_CHARACTERS = 20000` is MemGPT's own number, from `letta/constants.py`, where `CORE_MEMORY_PERSONA_CHAR_LIMIT` and
  `CORE_MEMORY_HUMAN_CHAR_LIMIT` are both 20,000. This is the arm called **MemGPT as published**,
  and it ran in `overnight_wave_24_questions` and `wave_reasons_first`.
- `A_DELIBERATELY_TIGHT_WORKING_MEMORY = 1200` is a sixteenth of that, anchored on this study's own summary length. It is the arm called **a small working memory
  and an archive**, and it ran on the ten households in `overnight_wave`. The paper must call this
  the tight variant and never MemGPT.
- **The three-household 50-day run has no MemGPT arm of any size.** Its cells are
  `last seen`, `the log and notes`, `incremental edits`, `ACE as published` and
  `ours told the night before`.

Counted from the cells' own nightly records - the cap is recovered by dividing the characters held
by the share of the block reported, so these are the caps that were actually in force, not the
constants as they stand today:

| arm and wave | cells | nights | cap recovered | median characters held | largest | refused writes |
|---|---|---|---|---|---|---|
| tight variant, 1,200 | 10 | 320 | 1200 | 779 | 1168 | refused because working memory was full: 2 |
| MemGPT as published, 24 questions a day | 1 | 32 | 20000 | 12018 | 19967 | refused because the block was full: 4, refused because the piece was not there: 9 |
| MemGPT as published, the reason-first wave | 3 | 96 | 20000 | 11494 | 19972 | refused because the block was full: 9, refused because the piece was not there: 11 |

### Substring-replacement edits

`replace_part_of_the_block` is an exact substring match, as theirs is. The piece named must appear
in the block character for character; if it does not, nothing is replaced and the model is handed
back:

> that piece is not in your block, character for character, so nothing was replaced. Quote it
> exactly as it appears.

### Archive search on the asked object

The archive is reached only by searching, at two moments. At night the writer may call
`search the archive`, which returns 5 passages a page with the page count,
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

==============================================================================
NIGHTLY UPDATE - system prompt (hh_s2_t03, night 1, the claim store)
==============================================================================
You help a home robot keep notes about where a household's things are kept. Nobody tells the robot the right answer; everything it knows comes from looking. Answer with JSON only.

==============================================================================
NIGHTLY UPDATE - user prompt (hh_s2_t03, night 1)
==============================================================================
This is a real home. Two people live in it, and from the names on their things they are called Ines and Tomas.

They are real people with real lives. They have habits and preferences. They make mistakes. They leave a thing wherever they happened to be standing. Their habits change when something in their life changes.

So working out where a thing is really means working out what the person who owns it was doing. A thing is where somebody left it.

There are many kinds of thing worth working out about people, and far more than anything written here could list. Two examples only, so you know the sort of thing: somebody might always take a cup with them when they move rooms, or somebody might be in a different room on a Saturday. Do not treat those two as the list. Look at what you actually saw and work out what is going on in this home.

You can see the people when you walk into a room, and your record names them.

It is the end of day 1.

The rooms of this home and the spots in each:
- balcony: balcony_floor_y1, balcony_table_y1
- bathroom: bathroom_shelf_ba1, medicine_cabinet_ba1, sink_ba_ba1, towel_rack_ba1
- bedroom_1: bed_b1, bedroom_floor_b1, desk_b1, dresser_b1, nightstand_b1, wardrobe_b1
- dining: chair_d_d1, dining_table_d1, sideboard_d1
- entry: entry_floor_e1, entry_hook_e1, entry_table_e1, shoe_rack_e1
- kitchen: chair_k1, counter_k1, cupboard_k1, dish_rack_k1, drawer_k_k1, floor_k_k1, kitchen_table_k1, pantry_shelf_k1, sink_k1
- living: armchair_l1, bookshelf_l1, coffee_table_l1, couch_l1, floor_l_l1, side_table_l1, tv_stand_l1
- office: desk_o1, floor_o_o1, office_chair_o1, office_shelf_o1
- storage: storage_floor_s1, storage_shelf_s1

Somebody will ask you where a thing in this home is. Nobody has said which things, so it could be any of them.

WHAT YOU SAW TODAY. Each look lists everything that was in the room at that moment, so anything not listed was not there:

Day 1 at 07:17, the robot looked in: bathroom.
It found:
  - towel_ines on the towel rack in the bathroom  [sighting_0007]
  - towel_tomas on the towel rack in the bathroom  [sighting_0008]
People there: Tomas.

Day 1 at 09:22, the robot looked in: kitchen.
It found:
  - glass_ines on the cupboard in the kitchen  [sighting_0016]
  - glass_tomas on the cupboard in the kitchen  [sighting_0017]
  - water_bottle_ines on the dish rack in the kitchen  [sighting_0022]
NOT FOUND:
  - kitchen: towel_ines, towel_tomas

Day 1 at 09:22, the robot looked in: living.
It found none of the things it is asked about.
NOT FOUND:
  - living: glass_ines, glass_tomas, towel_ines, towel_tomas, water_bottle_ines

Day 1 at 09:22, the robot looked in: bathroom.
It found:
  - towel_ines on the towel rack in the bathroom  [sighting_0047]
  - towel_tomas on the towel rack in the bathroom  [sighting_0048]
NOT FOUND:
  - bathroom: glass_ines, glass_tomas, water_bottle_ines

Day 1 at 11:17, the robot looked in: bathroom.
It found:
  - towel_ines on the towel rack in the bathroom  [sighting_0055]
  - towel_tomas on the towel rack in the bathroom  [sighting_0056]
NOT FOUND:
  - bathroom: glass_ines, glass_tomas, water_bottle_ines

Day 1 at 12:41, the robot looked in: bathroom.
It found:
  - towel_ines on the towel rack in the bathroom  [sighting_0063]
  - towel_tomas on the towel rack in the bathroom  [sighting_0064]
NOT FOUND:
  - bathroom: glass_ines, glass_tomas, water_bottle_ines

Day 1 at 14:16, the robot looked in: kitchen.
It found:
  - glass_ines on the sink in the kitchen  [sighting_0082]
  - glass_tomas on the sink in the kitchen  [sighting_0083]
  - mug_ines on the kitchen table in the kitchen  [sighting_0078]
NOT FOUND:
  - kitchen: towel_ines, towel_tomas, water_bottle_ines

Day 1 at 14:16, the robot looked in: living.
It found none of the things it is asked about.
NOT FOUND:
  - living: glass_ines, glass_tomas, mug_ines, towel_ines, towel_tomas, water_bottle_ines

Day 1 at 14:16, the robot looked in: bathroom.
It found:
  - towel_ines on the towel rack in the bathroom  [sighting_0103]
  - towel_tomas on the towel rack in the bathroom  [sighting_0104]
NOT FOUND:
  - bathroom: glass_ines, glass_tomas, mug_ines, water_bottle_ines

Day 1 at 15:27, the robot looked in: office.
It found:
  - mug_tomas on the desk in the office  [sighting_0107]
  - notebook_tomas on the desk in the office  [sighting_0108]
NOT FOUND:
  - office: glass_ines, glass_tomas, mug_ines, towel_ines, towel_tomas, water_bottle_ines

Day 1 at 18:16, the robot looked in: bathroom.
It found:
  - towel_ines on the towel rack in the bathroom  [sighting_0117]
  - towel_tomas on the towel rack in the bathroom  [sighting_0118]
NOT FOUND:
  - bathroom: glass_ines, glass_tomas, mug_ines, mug_tomas, notebook_tomas, water_bottle_ines

Day 1 at 20:15, the robot looked in: kitchen.
It found:
  - glass_ines on the sink in the kitchen  [sighting_0134]
  - mug_ines on the kitchen table in the kitchen  [sighting_0125]
  - mug_tomas on the kitchen table in the kitchen  [sighting_0126]
NOT FOUND:
  - kitchen: glass_tomas, notebook_tomas, towel_ines, towel_tomas, water_bottle_ines
People there: Tomas, Ines.

Day 1 at 20:15, the robot looked in: living.
It found none of the things it is asked about.
NOT FOUND:
  - living: glass_ines, glass_tomas, mug_ines, mug_tomas, notebook_tomas, towel_ines, towel_tomas, water_bottle_ines

Day 1 at 20:15, the robot looked in: bathroom.
It found:
  - towel_ines on the towel rack in the bathroom  [sighting_0157]
  - towel_tomas on the towel rack in the bathroom  [sighting_0158]
NOT FOUND:
  - bathroom: glass_ines, glass_tomas, mug_ines, mug_tomas, notebook_tomas, water_bottle_ines

YOUR MEMORY AS IT STANDS:

(nothing written yet)

YOUR MEMORY is a list of separate notes, each with its own number. It carries over from yesterday exactly as it was. Tonight you change it by writing edits: you can add a note, revise a note by its number, or attach today's sightings to a note as evidence for it or against it.

Write the edits tonight calls for. Revising a note keeps what it said before, so nothing you write is ever lost.

It may help to think about what was surprising or important in what you saw today, and why it happened. What you write down is your own thinking, not a copy of what you saw.

It may help to say when something you write is true, if it is only true at some times. That is what lets you choose between two things you have written that disagree. Write the condition itself, not the date you happened to see it: what has to be the case for it to be true.

It may help to write down what you would expect to see if something you believe turned out to be wrong.

When something you believed stops being true, make your best judgement on whether to keep it, change it, or set it aside. Setting it aside is its own thing to do, separate from changing what it says: it means the note is not true at the moment, and it stays in your memory so you can bring it back. Changing the words of a note leaves it standing. It may help to record what made you decide.

You can point at any sighting using the number in square brackets beside it.

Each note is cut off after 240 characters, so keep one idea to a note.

==============================================================================
NIGHTLY UPDATE - output schema (the allowance this night was 51 edits)
==============================================================================
{
  "type": "object",
  "properties": {
    "edits": {
      "type": "array",
      "maxItems": 51,
      "items": {
        "type": "object",
        "properties": {
          "why": {
            "type": "string",
            "maxLength": 600
          },
          "action": {
            "type": "string",
            "enum": [
              "add",
              "revise",
              "record evidence",
              "set a note aside",
              "bring a note back"
            ]
          },
          "claim_id": {
            "type": [
              "string",
              "null"
            ]
          },
          "statement": {
            "type": [
              "string",
              "null"
            ],
            "maxLength": 240
          },
          "holds_under": {
            "type": [
              "string",
              "null"
            ],
            "maxLength": 120
          },
          "status": {
            "type": [
              "string",
              "null"
            ],
            "enum": [
              "provisional",
              "established",
              null
            ]
          },
          "supporting_observation_ids": {
            "type": "array",
            "items": {
              "type": "string"
            },
            "maxItems": 6
          },
          "contradicting_observation_ids": {
            "type": "array",
            "items": {
              "type": "string"
            },
            "maxItems": 6
          }
        },
        "required": [
          "why",
          "action",
          "claim_id",
          "statement",
          "holds_under",
          "status",
          "supporting_observation_ids",
          "contradicting_observation_ids"
        ],
        "additionalProperties": false
      }
    }
  },
  "required": [
    "edits"
  ],
  "additionalProperties": false
}

==============================================================================
ROOM CHOICE - system prompt
==============================================================================
You help a home robot decide where to look in a house. Nobody tells the robot where anything is; looking is the only way it learns. Answer with JSON only.

==============================================================================
ROOM CHOICE - user prompt (hh_s2_t03, day 1, empty notes)
==============================================================================
It is day 1. You may look in ONE room, at 09:00.

Below is every room in this house and what your notes currently predict would be found in it. Choose the ONE room whose contents your notes are least able to predict - and then say what looking there would settle. Name two claims that cannot both be right, say which of the things you are asked about you would find in that room if the first one holds, which you would find if the second holds, and what you would change in your notes either way.

A room your notes say nothing about is a room you cannot predict at all. Things move: if something is missing from where your notes put it, it is somewhere your notes are not looking.

Expecting to find NOTHING is a real answer: if one claim puts the mug on the desk, then that claim predicts an empty living room, and an empty list is how you say so. What matters is that the two lists are not the same - if both claims predict the same things in the room you pick, looking there cannot tell you which is right and the look is wasted.

The rooms of this home and the spots in each:
- balcony: balcony_floor_y1, balcony_table_y1
- bathroom: bathroom_shelf_ba1, medicine_cabinet_ba1, sink_ba_ba1, towel_rack_ba1
- bedroom_1: bed_b1, bedroom_floor_b1, desk_b1, dresser_b1, nightstand_b1, wardrobe_b1
- dining: chair_d_d1, dining_table_d1, sideboard_d1
- entry: entry_floor_e1, entry_hook_e1, entry_table_e1, shoe_rack_e1
- kitchen: chair_k1, counter_k1, cupboard_k1, dish_rack_k1, drawer_k_k1, floor_k_k1, kitchen_table_k1, pantry_shelf_k1, sink_k1
- living: armchair_l1, bookshelf_l1, coffee_table_l1, couch_l1, floor_l_l1, side_table_l1, tv_stand_l1
- office: desk_o1, floor_o_o1, office_chair_o1, office_shelf_o1
- storage: storage_floor_s1, storage_shelf_s1

The things you are asked about: book_tomas, charger_tomas, glass_ines, glass_tomas, mug_ines, mug_tomas, notebook_tomas, towel_ines, towel_tomas, water_bottle_ines, water_bottle_tomas

What your notes predict for each room:
- balcony: your notes say nothing about this room
- bathroom: your notes say nothing about this room
- bedroom_1: your notes say nothing about this room
- dining: your notes say nothing about this room
- entry: your notes say nothing about this room
- kitchen: your notes say nothing about this room
- living: your notes say nothing about this room
- office: your notes say nothing about this room
- storage: your notes say nothing about this room

Your notes:

(nothing written yet)

==============================================================================
ROOM CHOICE - output schema
==============================================================================
{
  "type": "object",
  "properties": {
    "room": {
      "type": "string",
      "enum": [
        "balcony",
        "bathroom",
        "bedroom_1",
        "dining",
        "entry",
        "kitchen",
        "living",
        "office",
        "storage"
      ]
    },
    "first_claim_id": {
      "type": [
        "string",
        "null"
      ]
    },
    "first_claim": {
      "type": "string",
      "maxLength": 240
    },
    "second_claim_id": {
      "type": [
        "string",
        "null"
      ]
    },
    "second_claim": {
      "type": "string",
      "maxLength": 240
    },
    "objects_expected_if_the_first_claim_holds": {
      "type": "array",
      "items": {
        "type": "string"
      },
      "maxItems": 12
    },
    "objects_expected_if_the_second_claim_holds": {
      "type": "array",
      "items": {
        "type": "string"
      },
      "maxItems": 12
    },
    "what_i_would_change_if_the_first_claim_holds": {
      "type": "string",
      "maxLength": 240
    },
    "what_i_would_change_if_the_second_claim_holds": {
      "type": "string",
      "maxLength": 240
    },
    "reasoning": {
      "type": "string",
      "maxLength": 400
    }
  },
  "required": [
    "room",
    "first_claim_id",
    "first_claim",
    "second_claim_id",
    "second_claim",
    "objects_expected_if_the_first_claim_holds",
    "objects_expected_if_the_second_claim_holds",
    "what_i_would_change_if_the_first_claim_holds",
    "what_i_would_change_if_the_second_claim_holds",
    "reasoning"
  ],
  "additionalProperties": false
}

==============================================================================
HOW ONE EXISTING NOTE IS SHOWN BACK (from the landed claim store, day 31)
==============================================================================
[claim_0001] Bathroom items (towels, detergent, hair dryer, soap, toothbrush holder, toiletry bag) are static on their usual spots.
    when it is true: Always
    6 sighting(s) support it | 0 argue against it | written or last changed on day 31 | provisional

[claim_0002] Tomas works in the office during the day. His laptop, mouse, pen, notebook, charger, and water bottle are on the office desk.
    when it is true: When Tomas is working in the office
    4 sighting(s) support it | 0 argue against it | written or last changed on day 29 | provisional


```
