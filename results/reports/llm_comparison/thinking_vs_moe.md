# LLM option evaluation — Qwen3-32B guided (baseline) vs thinking mode; MoE arm blocked

8 frozen contexts (6 displacement, 2 judge), byte-identical inputs per arm, built with the
real pipeline prompt/schema code from the Part-A generation results. Temperature 0.7,
seeds fixed per context. Thinking mode: no guided decoding (grammar would suppress the
think block), Qwen3 chat-template thinking enabled, max_tokens 12288 (vs 2048 guided).

## Arm 3 (large Qwen MoE) — BLOCKED, reported rather than substituted

- Verified candidate: `Qwen/Qwen3-Next-80B-A3B-Thinking-FP8` — 82.1 GB FP8 safetensors
  (bf16 variant ~160 GB, does not fit 97.9 GB), `Qwen3NextForCausalLM` IS in the installed
  vLLM 0.10.2 registry, ungated. Downloaded successfully (11.9 min).
- Engine load FAILS on vLLM 0.10.2: `ValueError: Detected some but not all shards of
  model.layers.0.linear_attn.in_proj are quantized.` — the FP8 checkpoint deliberately
  leaves the hybrid linear-attention projections unquantized, and 0.10.2's fused-layer
  quant check can't handle the mix for this arch. Fixed in later vLLM, which CANNOT be
  installed here: vLLM >=0.11 requires Python >=3.10 syntax, and this env is pinned to
  Python 3.9 by habitat-sim's newest available prebuilt binaries. Chain: habitat-sim ->
  py3.9 -> vllm<=0.10.2 -> no Qwen3-Next-FP8.
- Other Qwen MoE options under this constraint: Qwen3-235B-A22B (no fit at any supported
  quant), Qwen3-30B-A3B (loads fine, but SMALLER than the 32B dense baseline — not the
  'largest MoE that fits'). Decision needed: accept 30B-A3B as a below-baseline MoE data
  point, run bf16 Qwen3-Next on multi-GPU/other hardware, or drop Arm 3.

## Headline numbers

| arm | load | VRAM after load | total gen time (8 calls) | mean s/call | JSON valid (strict) | valid after fence-strip |
|---|---|---|---|---|---|---|
| 32B guided (baseline) | 53.6s | 89472 MiB | 83s | 10s | 8/8 | 8/8 |
| 32B thinking | 43.8s | 89472 MiB | 1261s | 92s | 7/8 | 8/8 |

(Guided total includes zero retries; thinking total includes 3 retry attempts on the one
strict-parse failure. Thinking is ~15x slower per call — reasoning tokens dominate.)

## Schema discipline WITHOUT guided decoding (the important caveat)

The single strict failure (32B thinking, morning_jog@outdoor) is not a truncation: the
model wrapped valid-ish JSON in a ```json fence, renamed `reason` to `behavioural_reason`,
and invented the anchor `outdoor.potted_plant_3` — a label that exists in NO census view
(potted plants are not anchors). Guided decoding makes all three impossible; thinking mode
as wired here trades that guarantee for reasoning. Any production use of thinking mode
needs either (a) post-validation + retry against the census (the pipeline's grounding
gate already provides most of this), or (b) a vLLM version whose reasoning parser applies
the grammar AFTER the think block — not available under the py3.9 constraint.

## Per-context outputs

### 1. 102343992/sleeping@bedroom/John

**32B guided** — 14.0s, 287 tokens

- phone **on_top bedroom_1.bed_1** — User likely places phone on the bed while sleeping to have it nearby for alarms or late-night use.
- keys **inside bedroom_1.bed_1** — Keys may be placed under the pillow or on the bed while sleeping for easy access in the morning.
- wallet **inside bedroom_1.bed_1** — Wallet is likely placed under the pillow or on the bed for security and easy access.
- book **on_top bedroom_1.bed_1** — A book might be left on the bed during or after reading before sleeping.

**32B thinking** — 107.0s, 2478 tokens, think 10303 chars

- (no proposals)

<details><summary>think excerpt</summary>

> Okay, let's tackle this problem. The user wants me to propose object displacements for John, the father, during his sleeping activity. The room is the bedroom, and the household tidiness is 0.8, which is pretty high. So, the occupants are likely to keep things organized, but there might be a few small items moved around.  First, I need to look at the scene inventory. In the bedroom, there's a stool. The other items in the bedroom aren't listed, but the inventory includes a stool, which is in the bedroom. The activity is sleeping, so I should think about what someone might do before going to bed.  Possible actions could involve moving items to or from the bed. Let's check the inventory categories. The objects that might be moved could be the phone, keys, wallet, maybe a book, or laptop. But the user is sleeping, so perhaps they're putting these items on the bed or a surface nearby.  Looki...

</details>

### 2. 102343992/morning_jog@outdoor/John

**32B guided** — 3.9s, 91 tokens

- keys **near outdoor.trashcan_1** — placing keys near a trashcan while going for a jog

**32B thinking** — 81.6s, 1922 tokens, think 7022 chars, strict-parse FAILED (fence-stripped below)

- (no proposals)

<details><summary>think excerpt</summary>

> Okay, let's tackle this query. The user wants me to propose object displacements for John's morning jog activity from 8 to 9 AM. The current room is outdoor, and the household tidiness is 0.8, which is pretty tidy.   First, I need to look at the scene inventory. The outdoor room has potted_plant×6 and chair×2. Other rooms have various items, but since John is in the outdoor room, all target anchors must be there. The activity is a morning jog, so likely John is preparing to go out.  Looking at the objects, the keys, wallet, and phone are probably on his person, but maybe he left them somewhere. Since he's in the outdoor room, maybe he placed them near the door or on a chair. The chair is in the outdoor room, so moving a chair might not make sense unless he's adjusting it. But chairs are floor objects, so only proximity relations. Wait, the rules say chairs and stools can't be placed on s...

</details>

### 3. 102343992/showering@bathroom/John

**32B guided** — 1.5s, 35 tokens

- (no proposals)

**32B thinking** — 143.2s, 3365 tokens, think 14542 chars

- (no proposals)

<details><summary>think excerpt</summary>

> Okay, let's tackle this problem. The user wants me to propose object displacements for John (father) during his showering activity from 9.0h to 9.5h. The current room is the bathroom, and the household tidiness is 0.8, which is pretty high.  First, I need to look at the scene inventory. The categories present are potted_plant, book, chair, tv, wardrobe, fridge, stool, phone, wallet, keys, and laptop. But since John is in the bathroom, I need to check which of these objects are in the bathroom or could plausibly be moved there. However, the "by room" section doesn't list the bathroom, so maybe the inventory is only for the current room? Wait, the user mentioned that the target_anchor entries must be in the current room (bathroom), but the objects being moved could be from elsewhere. So the objects in the scene inventory are for the entire house, but the movement is into the bathroom.  Wai...

</details>

### 4. 102344049/waking_up@bedroom/Emily

**32B guided** — 1.0s, 23 tokens

- (no proposals)

**32B thinking** — 75.0s, 1770 tokens, think 5391 chars

- (no proposals)

<details><summary>think excerpt</summary>

> Okay, let's tackle this query. The user wants me to propose object displacements caused by Emily waking up in the bedroom. First, I need to consider the activity: waking up in the morning. Common actions during this time might include getting out of bed, maybe sitting on a chair or stool, perhaps turning on a light (like a lamp or candle), or organizing personal items.  Looking at the scene inventory for the bedroom, there's a potted_plant and a wardrobe. But the user mentioned that the occupant is in the bedroom, and the target anchors are only those in that room. Wait, the scene inventory by room shows the bedroom has potted_plant×1 and wardrobe×1. However, the overall inventory includes more items like bowls, chairs, stools, etc., but those might be in other rooms. However, the note says the object being moved doesn't have to be in the same room as the destination. So Emily could be b...

</details>

### 5. 102344049/light_snack@kitchen/Emily

**32B guided** — 18.1s, 428 tokens

- bowl **on_top kitchen.counter_1** — Emily might place a bowl on the counter to hold snacks while she prepares them.
- candle **on_top kitchen.counter_1** — Candles are often used during snack times for ambiance.
- phone **on_top kitchen.counter_1** — Emily might place her phone on the counter while she eats to stay connected.
- stool **next_to kitchen.counter_1** — Emily might move a stool next to the counter for seating while she eats her snack.
- book **on_top kitchen.counter_1** — A book could be placed on the counter for entertainment during the snack time.
- vase **on_top kitchen.counter_1** — A vase might be placed on the counter to add a decorative touch while having a snack.
- stool **next_to kitchen.counter_1** — Emily might move another stool next to the counter for additional seating.

**32B thinking** — 123.4s, 2903 tokens, think 11249 chars

- (no proposals)

<details><summary>think excerpt</summary>

> Okay, let's start by understanding the problem. Emily is in the kitchen, and it's time for a light snack between 7.2 to 7.5 hours, which I assume is around 7:12 AM to 7:30 AM. The activity is a light snack, so I need to think about what objects she might move during this time.  First, the room is the kitchen, and the inventory includes several items. The key here is to focus on objects that are in the kitchen or that she could bring into the kitchen. The target anchors are specific instances like kitchen.counter_2 or kitchen.stool_1.   Looking at the inventory, the kitchen has stools and a potted plant. The other rooms have chairs, potted plants, etc., but since Emily is in the kitchen, the destinations must be within the kitchen's anchors. The available anchors in the kitchen are the stools and the potted plant. Wait, but the potted plant is a plant, not a surface. So the main surfaces ...

</details>

### 6. 102344049/organizing_workspace@office/Emily

**32B guided** — 20.9s, 493 tokens

- book **on_top none** — No suitable anchor for books in the office room.
- potted_plant **next_to none** — No suitable anchor for potted plants in the office room.
- chair **next_to none** — No suitable anchor for chairs in the office room.
- stool **next_to none** — No suitable anchor for stools in the office room.
- candle **on_top none** — No suitable anchor for candles in the office room.
- bowl **on_top none** — No suitable anchor for bowls in the office room.
- vase **on_top none** — No suitable anchor for vases in the office room.
- phone **on_top none** — No suitable anchor for phones in the office room.
- wallet **on_top none** — No suitable anchor for wallets in the office room.
- keys **on_top none** — No suitable anchor for keys in the office room.

**32B thinking** — 137.1s, 3222 tokens, think 12963 chars

- (no proposals)

<details><summary>think excerpt</summary>

> Okay, let's tackle this. The activity is organizing the workspace, which is in the office. Emily is the occupant, and the household is very tidy. I need to propose object displacements based on the inventory and room info.  First, the current room is the office, so all target anchors must be in there. The scene inventory lists objects in different rooms. The office's inventory isn't directly given, but the activity is there, so objects in the office would be relevant. Wait, the "By room" section lists bedroom, kitchen, living_room. The office isn't there, so maybe the office's objects are in the main inventory? The main inventory includes bowl, potted_plant, chair, etc. But the objects in the office would be those not assigned to other rooms. Hmm, maybe the office has the laptop (since organizing workspace often involves a laptop), books, perhaps some bowls or vases for decoration. Since...

</details>

### 7. 102343992/judge:decorating/John (8 candidates)

**32B guided** — 23.2s, 546 tokens

- [0] potted_plant on_top tv.table_1 -> **0.95** A potted plant on the TV stand is a common and plausible decorative choice. Given the activity of de
- [1] chair next_to tv.tv_1 -> **0.9** Placing a chair next to the TV is a logical choice for additional seating during any activity, inclu
- [2] book inside tv.table_1 -> **0.85** Placing a book inside the TV stand to organize and display reading material is a reasonable choice, 
- [3] laptop on_top tv.table_1 -> **0.6** While using a laptop for organizing decor ideas is a plausible reason, placing it on the TV stand du
- [4] phone on_top tv.table_1 -> **0.8** Placing a phone on the TV stand for easy access during decorating makes sense. It's a convenient loc
- [5] wallet on_top tv.table_1 -> **0.5** Placing a wallet on the TV stand for quick access during decorating seems slightly implausible. Whil
- [6] keys on_top tv.table_1 -> **0.45** Putting keys on the TV stand during decorating is somewhat implausible. Keys are usually placed in m
- [7] potted_plant on_top tv.table_1 -> **0.95** Adding another potted plant to the TV stand to enhance the room's aesthetics is a very plausible and

**32B thinking** — 32.3s, 764 tokens, think 3049 chars

*(schema drift: index->score dict instead of the scores array)*
- [0] potted_plant on_top tv.table_1 -> **0.9** 
- [1] chair next_to tv.tv_1 -> **0.85** 
- [2] book inside tv.table_1 -> **0.7** 
- [3] laptop on_top tv.table_1 -> **0.75** 
- [4] phone on_top tv.table_1 -> **0.8** 
- [5] wallet on_top tv.table_1 -> **0.3** 
- [6] keys on_top tv.table_1 -> **0.2** 
- [7] potted_plant on_top tv.table_1 -> **0.5** 

<details><summary>think excerpt</summary>

> Okay, let's tackle this query step by step. The user wants me to evaluate the behavioral plausibility of each candidate object placement in the context of decorating, with occupant John and a household tidiness of 0.8.   First, I need to understand the scenario. The activity is decorating, so the placements should make sense in that context. The household is quite tidy (0.8/1.0), so any clutter or misplaced items might be less plausible.  Starting with candidate [0]: potted plant on the TV stand. The reason given is to enhance decor with a natural touch. Since the activity is decorating, adding a plant makes sense. In a tidy household, this would be intentional, so the score should be high. Maybe 0.9.  Candidate [1]: chair next to TV. The reason is for additional seating during decorating. It's logical to have a chair nearby for seating, especially when working on the TV area. Even in a ...

</details>

### 8. 102344049/judge:morning_routine/Emily (11 candidates)

**32B guided** — 0.4s, 7 tokens

- [0] bowl on_top bedroom_1.bed_1 -> **—** 
- [1] phone on_top bedroom_1.bed_1 -> **—** 
- [2] wallet on_top bedroom_1.bed_1 -> **—** 
- [3] candle on_top bedroom_1.bed_1 -> **—** 
- [4] book on_top bedroom_1.bed_1 -> **—** 
- [5] stool next_to bedroom_1.bed_1 -> **—** 
- [6] potted_plant on_top bedroom_1.bed_1 -> **—** 
- [7] potted_plant on_top bedroom_1.bed_1 -> **—** 
- [8] potted_plant on_top bedroom_1.bed_1 -> **—** 
- [9] wardrobe on_top bedroom_1.bed_1 -> **—** 
- [10] laptop on_top bedroom_1.bed_1 -> **—** 

**32B thinking** — 34.3s, 811 tokens, think 2911 chars

*(schema drift: index->score dict instead of the scores array)*
- [0] bowl on_top bedroom_1.bed_1 -> **0.6** 
- [1] phone on_top bedroom_1.bed_1 -> **0.9** 
- [2] wallet on_top bedroom_1.bed_1 -> **0.5** 
- [3] candle on_top bedroom_1.bed_1 -> **0.3** 
- [4] book on_top bedroom_1.bed_1 -> **0.8** 
- [5] stool next_to bedroom_1.bed_1 -> **0.75** 
- [6] potted_plant on_top bedroom_1.bed_1 -> **0.2** 
- [7] potted_plant on_top bedroom_1.bed_1 -> **0.2** 
- [8] potted_plant on_top bedroom_1.bed_1 -> **0.2** 
- [9] wardrobe on_top bedroom_1.bed_1 -> **0.0** 
- [10] laptop on_top bedroom_1.bed_1 -> **0.7** 

<details><summary>think excerpt</summary>

> Okay, let's tackle this step by step. The user wants me to evaluate each candidate's placement in Emily's bedroom during her morning routine, considering the household's high tidiness (0.9/1.0). Since the household is very tidy, we can expect that any object here should have a clear and plausible reason related to the morning routine, and not just be left there by accident.  Starting with candidate [0], the bowl on the bed. Morning routines often involve eating, maybe cereal or something, but in a very tidy household, would someone keep a bowl on the bed? It's possible if she's eating in bed, but that's not common in a tidy home. The reason given is plausible, but maybe a bit on the edge. I might give it a mid score, like 0.6.  Candidate [1] is the phone on the bed. Checking the phone is definitely a common morning activity. Placing it on the bed for convenience makes sense. Even in a ti...

</details>

