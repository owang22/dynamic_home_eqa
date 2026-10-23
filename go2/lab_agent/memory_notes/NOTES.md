# Memory work, overnight 2026-10-23 (no dog)

Brief: embeddings + fused search, synonym map, object instances, where_is, report. Survey: research_2026-10-22/research_memory.md s.5.

## Log
- 00:20 SigLIP ViT-SO400M-14-384 weights found in ~/.cache/huggingface (open_clip safetensors only). The text
  tokenizer (timm/ViT-B-16-SigLIP) was not cached; fetched its 3 files (2.4 MB) with curl into
  go2/data/models/siglip_tokenizer (HF reachable). Model needs mean/std 0.5 + squash resize set by hand when loaded
  from a file (open_clip's defaults are the OpenAI ones otherwise).
- 00:25 embeddings.py: 3 views per picture (squashed full + left/right squares), 1107 pictures in 38 s on GPU,
  +1.9 GB GPU. Store: go2/data/lab_agent/embeddings/{views.npy, ids.json}.
- 00:35 Synonym map (CANON/KIND/CLUTTER in memory.py) from the 162 object names. SigLIP text-embedding
  neighbours of the names were used as suggestions only (they also pair key~keyboard 0.88, rug~floor), the map
  itself is by hand. Checked by eye: "bin" = small white waste bins under desks (-> trash can); "appliance" black
  on floor = mostly the black water cooler (not merged: it is a description error, not a synonym).
- 00:50 Search eval protocol: 40 queries (chat questions + lab objects). Candidate pool per query = union of the
  top 20 of word search (old), word search + synonyms, image search, fused (RRF) -> 21-57 pictures per query, all
  opened by me on contact sheets (scratchpad mem/sheets) and labelled relevant if the thing is visibly there.
  recall@k = relevant in top k / min(k, n relevant) (pool-relative). "red screwdriver" dropped (none in the pool,
  as the chat found).
- 01:15 Dev split = first 14 labelled queries. RRF (k=60) fusion was WORSE than images alone (0.67/0.71 vs
  0.79/0.74 r@5/r@10): word scores tie a lot and are often junk (water cooler: words find "water bottle"), and
  RRF gives them equal say. Tried on dev: RRF with image weight 2/3, k=10; score boost cos + b*(word/best word)
  with b=.01/.02/.04. Picked boost b=0.02 (dev 0.80/0.77). Fixed before labelling the 25 test queries.
- 02:10 Labels done: 39 queries labelled, 35 with at least one relevant picture (dropped as none/unsure: red
  screwdriver, robot arm, open door, speaker, red bottle). Files: memory_notes/search_eval/ (labels.json with a
  note per query, pools.json, evalr.py, variants.py, eval_final.txt).
- Results (recall@5 / recall@10, mean over queries; pool-relative):

  | search | dev 15 (tuned on) | test 20 | all 35 |
  |---|---|---|---|
  | words, 2026-10-22 search | 0.67/0.63 | 0.67/0.65 | 0.67/0.64 |
  | words + synonyms | 0.67/0.63 | 0.67/0.64 | 0.67/0.64 |
  | SigLIP pictures only | 0.80/0.74 | 0.60/0.55 | 0.69/0.63 |
  | RRF (k=60) | 0.69/0.72 | 0.73/0.71 | 0.71/0.72 |
  | boost b=0.02 (chosen on dev before test labels) | 0.81/0.78 | 0.70/0.65 | 0.75/0.71 |
  | boost b=0.05 (plateau 0.04-0.06 over all 35; now the default) | 0.76/0.77 | 0.81/0.78 | 0.79/0.78 |

  Honest reading: the pre-registered b=0.02 only gained +0.03 r@5 on the test split. b=0.05 was picked after
  seeing all labels, so its 0.79/0.78 is optimistic; b in 0.04-0.06 all give 0.78-0.79/0.77-0.78, so it is a
  plateau, not a spike. The gain is real where the description missed the thing (computer tower with lights
  0.00 -> 1.00, conference table 0.20 -> 1.00, microwave 0.00 -> 0.80, blue tape 0.20 -> 0.60, checked shirt
  0.00 -> 0.60). Pictures-only loses on small or edge-cut things (printer, plant, phone, TV, cup, whiteboard),
  which the words still find; the fusion keeps most of those.
- Synonyms change nothing measurable on these queries (the queries use the common name). "black bag" got worse
  with synonyms on word search (r@10 0.40 -> 0.30): "bag" now also matches every black backpack, score ties are
  broken by time, and several tied pictures show the backpack too small to count. Tie noise, not a wrong merge.
  The synonym map matters for instances (task 3), where "office chair"/"chair", "bin"/"trash can" split groups.
- Pool caveat: the pools are the union of the top 20 of these same systems, so recall is relative to what some
  system found; things no system found are missing from both numerator and denominator.

## Object instances (memory_instances.py)
- 02:30 Ranging: Qwen asked once per picture for the distance to each non-clutter object. First prompt (all
  objects in one list, no reasons) gave every object in a picture the same distance (1.6/1.7 m) and once an empty
  list: kept as instances/ranges_v1_sameval.jsonl, not used. Second prompt: one field per object with a short
  "where" before "metres" and the hint that lower in the picture = closer; distances now differ per object.
  896 pictures have at least one tracked object; ~12 s per picture, 4 at a time, shared vLLM.
- Describer recall per kind (hand labels; share of labelled-visible pictures whose description names that kind):
  backpack 1.00 (68), sofa 1.00, case 1.00, jacket 0.97, tripod 0.97, bucket 0.97, extinguisher 0.96, computer
  tower 0.95, printer 0.94, laptop 0.91, vacuum 0.90, trash can 0.87, TV 0.85, fridge 0.82, phone 0.67, shoe 0.62,
  microwave 0.62, water cooler 0.47, whiteboard 0.47, podium 0.24, tape 0.12. Upper bounds (pools partly from word
  search). Used as DESCRIBE_RECALL: a miss counts for little where the describer often leaves the thing out.
- Route length for where_is: computed on the saved map (/map.png + /state.json, nav_proto.Grid + choose_stand,
  plain path length), NOT the console's /nav/plan: tonight's allowed list does not include /nav/plan and I could
  not check on the control PC that it has no side effects. locate() still uses /nav/plan (unchanged).
- Distance check (partial, 270 pictures): for instances whose position comes from sight lines crossing (3+
  sightings), Qwen's distance / camera-to-crossing distance: median 1.24 (IQR 0.98-1.61) on good poses (28),
  1.27 (1.05-1.49) on pre-fix poses (163). So Qwen guesses about 25% long, +-25%. Not corrected (the crossings
  come from the same groups, so the check is not independent).
- 03:00 Full ranging pass: 896 pictures, 0 failed, ~25 min. Sightings: 2,309 (non-clutter objects with a
  distance; 8,550 clutter rows skipped).

### Grouping: what was tried, and hand checks (contact sheets: scratchpad mem/ic*, map + pictures per instance)
| version | instances | hand check of ~50 random instances with >= 2 pictures |
|---|---|---|
| v1: one greedy pass over all days, join 1.0 m + 0.35 x distance, colour must match | 475 | 21 checked: 14 pure, 7 mixed (stopped early) |
| v2: + robust crossing, distances x0.8, join 1.5 m, big furniture 2.0 m with no colour gate | 400 | 53: 23 pure, 1 mostly, 21 mixed, 8 unsure |
| v3 (kept): v2 but grouped **within one day**, then linked across days | 542 (393 chains) | 51: 27 pure, 5 mostly (one stray picture), 11 mixed, 8 unsure |
  Purity among judgeable instances: v2 24/45 = 53%, v3 32/43 = 74%. Pictures in pure/mostly-pure instances, v3:
  381 of 477 judgeable (80%).
- Tried and dropped: SigLIP crop embeddings around each object's `across` as a grouping gate (same blue bucket:
  median similarity 0.90; same-name-and-colour pairs > 4 m apart: 0.74-0.80; overlapping). As a gate it split the
  bucket into 4 (was 3) and the sofa into 6; as a far-merge rule it changed nothing. Crops at a guessed `across`
  are too loose. Copy of that version: scratchpad mem/memory_instances_with_crops.py.
- Fragmentation of single static things (hand-labelled pictures; instances -> share in largest), cross-day
  grouping: join 1.0: bucket 3 (0.71), sofa 5 (0.65), case 2; join 1.5 + big 2.0 no-colour: bucket 2, sofa 3
  (0.91), case 1; join 2.0: bucket 1 but 343 instances (more mixing). File: instance_eval/grouping_result.txt.
- Error cases seen (v2/v3 sheets):
  - **Different days** were the main source of mixing in v2 (the backpack at Oliver's desk Thu merged with a black
    one at desk_gaofeng Mon; red-lit tower + white glass tower; tripods 3 m apart). Map poses differ between walks
    by 1-2 m: the same grey-white backpack on the black tower is at (2.85, 0.15) at Thu 16:13 and (0.27, 1.95) at
    Thu 16:36 (two instances, 3 m apart, same day). Per-day grouping fixes the cross-day mixing but not this.
  - **Describer naming**: the grey-white backpack on the tower is called "jacket" on Tue (jacket_298/364 mix it
    with the cream hoodie); the black water cooler "computer tower"; the mop pad at the tripod foot "mop".
  - **Many-of-a-kind in one place**: 4 towers on the long cabinet, a shelf of bottles (one picture lists 14-16
    bottles or shoes across the top edge), 2 extinguishers side by side: kept as one or split arbitrarily.
  - **Far / small**: laptops on far desk tops, bottles on far shelves, "robot" on far shelves: 8 of 51 unsure.
  - **Worn things**: shoes and jackets on people (shoe_305/359 = two people's shoes) become instances.
  - **Scrambled frame** t1792710643153 produced a "black bag" instance.
- Compression (v3): 2,309 sightings -> 542 instances -> 393 chains. Pictures per instance: median 2, mean 4.3;
  258 singletons, 199 with >= 3 pictures. backpack: 208 pictures -> 33 instances / 20 chains (12 with >= 3
  pictures); bucket: 160 -> 8 / 6; tripod 190 -> 15 / 7; sofa 57 -> 5 / 3; computer tower 278 -> 33 / 15;
  bottle 97 -> 84 / 68 (bottles do not group). Position: 113 instances from sight-line crossings, 429 from
  Qwen distance guesses; median uncertainty +-0.64 m.

### P(still there): prequential check (instance_eval/prequential.py, prequential_result.txt)
- No staged moves exist, so P(still there) cannot be checked against real moves. Proxy: for each instance and
  each later picture whose pose/FOV covers its position, predict from what was known before that picture, then
  check whether the picture shows it (one of its sightings, or the description names that kind + colour).
  This mixes real moves with describer misses and pose error, so it measures "will the next look see it".
- 12,915 pairs, 22% shown. AUC: persistence model 0.826, misses only 0.845, time decay only 0.815; Brier: model
  0.496, misses only 0.139, constant 0.170. After 0/1/2/3+ misses the next covering picture shows it 62/17/9/2%.
- **Time decay hurts ranking on this data**: scaling all half-lives x0.3..x100 gives AUC 0.825-0.827; no decay
  at all 0.840. Over these 3 days, things the dog saw mostly stayed (the bucket, sofa, extinguishers, the grey
  backpack Mon->Tue) and "not seen again" is explained by misses, not time. The half-lives are kept (the model
  must decay for questions about now after days of no looking), but they are guesses with no support here.
- Calibration of a miss: static things (sofa, extinguisher, printer, TV, fridge, bookshelf, vacuum) are named in
  only 44% of same-day pictures that cover them by geometry, 7-12% on a later day (recall ~0.9 when plainly
  visible) -> COVER_TRUE 0.45 same day, 0.15 later day. So geometry-based "covered" is right less than half the
  time: pose error and occlusion dominate. Misses within one 10-minute visit count once.
- Static-thing sanity check: 2 of 37 static instances end with P(still there) < 0.3 (false "gone").
- 03:30 Added MAX_PER_PICTURE = 4 (a picture listing more of one kind is an edge artefact; 67 sightings dropped).
  Final: 2,242 sightings -> 478 instances -> 339 chains; median 2, mean 4.7 pictures per instance, 197
  singletons. bottle 84 -> 40 instances. Prequential AUC moved 0.826 -> 0.816 (model), misses-only 0.845 -> 0.838:
  fewer easy "bottle shelf" pairs; same ordering of models. The hand checks above were on the build before this
  cap (bottle_72 and shoe_2 were the instances it affects).

## Summary (01:25)
Improved:
- Search recall@5/@10 over 35 hand-labelled queries: old word search 0.67/0.64 -> fused 0.79/0.78 (weight picked
  after seeing labels; the pre-registered weight gave 0.75/0.71, and 0.70/0.65 on the 20 held-out queries vs
  0.67/0.65 for words). Big gains where the description missed the thing (lit tower 0 -> 1.0, conference table
  0.2 -> 1.0, microwave 0 -> 0.8, blue tape 0.2 -> 0.6). Losses vs words: printer, plant, phone, TV.
- where_is: chain-level answers with last seen, P(still there), misses, suggestion and walk length on the saved
  map. Grouping purity ~74% (hand check, 43 judgeable of 51).
Not improved / open:
- Synonyms: no measurable change in search (0.67 -> 0.67).
- P(still there): time decay gives no ranking gain on 3 days without staged moves (no-decay AUC 0.840 vs 0.826).
  Needs staged moves to validate (survey 5.3 item 5).
- Positions: limited by map poses (up to ~3 m between passes on Thu) and Qwen distances (+25% bias, +-25%).
- Not done: L3 summaries, people grouping, crop-level detection (an open-vocabulary detector would give real
  boxes instead of `across` guesses), auto-ranging in web.py's watch loop.
