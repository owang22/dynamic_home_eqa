# Folds: `ACE as published` against our claim store, and what a fold does to the record

**Read each fold's own revision snapshot, matched on its recorded reason.** An earlier count
took the first snapshot at the fold's timestamp, which on a night when the model had already
merged something itself gave the wording from before the MODEL's merge - and made six of the
backstop's folds look cross-object. Corrected below. The guard has no hole.

| arm | who folded | folds | merged DIFFERENT objects | shared an object | matcher's limit | could not classify |
|---|---|---|---|---|---|---|
| `ACE as published` (still running) | the model, UNGUARDED | 26 | **16 (62%)** | 4 | 4 | 2 |
| our claim store | the model, UNGUARDED | 85 | **7 (8%)** | 42 | 3 | 33 |
| our claim store | the backstop, guarded | 22 | **0 (0%)** | 22 | 0 | 0 |

**The guarded path never merges across objects: 22 of 22 share one.** The unguarded path -
the model's `join two claims`, which both arms use and neither guards - is where every
cross-object merge comes from. So the ablation is not guarded against unguarded; it is how
often each model ASKS for a bad merge on the same unguarded path.

## What a fold does to the record it leaves behind

`Notes.fold_one_claim_into_another` does `keep.times_it_helped += folded.times_it_helped` and
the same for `times_it_misled`. Nothing separates inherited credit afterwards, and ACE's
reflection step reads exactly those tallies to decide which notes to trust. In the published
ACE cells:

| cell | live claims | of those, absorbed another | share | 'times it helped' held by them |
|---|---|---|---|---|
| hh_s2_t03 | 15 | 2 | 13% | **49 of 79 (62%)** |
| hh_s32_t03 | 20 | 4 | 20% | **10 of 46 (22%)** |
| hh_s48_t03 | 41 | 8 | 20% | **19 of 44 (43%)** |

A minority of claims hold most of the credit, and it is the minority whose record is not its
own. Our own arm has two cells of the same shape: `hh_s123_t03`, 21 of 22 live claims
absorbed another and 100% of the credit sits in them, and `hh_s32_t03`, 28% of claims
holding 83%.

## Every fold, with both wordings as the fold saw them

### ACE_as_published / hh_s2_t03 day 8 — claim_0013 into claim_0007, by the model — **matcher limit**

* folded in: Ines's water bottle is on the dining table in the evening (19:00+).
  * objects: ['water_bottle_ines']
* survived: Ines's glass, plate, and water bottle are on the dining table in the evening (approx 19:00-20:00).
  * objects: ['glass_ines']
* recorded reason: claim_0013 is a subset of claim_0007. Both state the water bottle is on the dining table in the evening. claim_0007 adds more items but does not contradict claim_0013.

### ACE_as_published / hh_s2_t03 day 13 — claim_0012 into claim_0010, by the model — **CROSS-OBJECT**

* folded in: Tomas's mug is on the office desk during the day. In the evening (20:00+), it moves to the dining table. Check office for day, dining for evening.
  * objects: ['mug_tomas']
* survived: Tomas's water bottle is on the office desk during the day. In the evening (20:00+), it moves to the dining table. Check office for day, dining for evening.
  * objects: ['water_bottle_tomas']
* recorded reason: Both notes describe the same objects (water bottle and mug) following the exact same location pattern (office desk by day, dining table by evening) under the same condition. They are effectively the '

### ACE_as_published / hh_s2_t03 day 15 — claim_0010 into claim_0008, by the model — **CROSS-OBJECT**

* folded in: Tomas's water bottle is on the bedroom_1 nightstand in the evening (13:00+). It may move to the bed. Check nightstand first, then bed.
  * objects: ['water_bottle_tomas']
* survived: Tomas's glass is in the bedroom_1 nightstand in the evening (13:00+). It is not in the dining room or kitchen during this time. Check bedroom_1 first.
  * objects: ['glass_tomas']
* recorded reason: Both notes describe the location of Tomas's glass in the bedroom_1 nightstand during the evening (13:00+). Although claim_0010 mentions a 'water bottle', in the context of household object tracking, a

### ACE_as_published / hh_s2_t03 day 17 — claim_0009 into claim_0007, by the model — **CROSS-OBJECT**

* folded in: Ines's mug is on the dining table in the morning (08:00-10:00). In the evening (21:00+), it is put away in the kitchen cupboard. Check dining for morning, kitchen for late evening.
  * objects: ['mug_ines']
* survived: Ines's glass, plate, and water bottle are on the dining table in the evening (20:00+). During the day (12:00-13:00) they are also on the dining table. In the late evening (21:00+), they are put away in the kitchen cupboard/dish rack. Check:
  * objects: ['glass_ines']
* recorded reason: Both notes describe the location of Ines's items on the dining table and their storage in the kitchen cupboard/dish rack in the late evening. claim_0007 covers the glass, plate, and water bottle; c

### ACE_as_published / hh_s2_t03 day 17 — claim_0019 into claim_0007, by the model — **matcher limit**

* folded in: Ines's water bottle is on the dining table in the evening (20:00+). In the late evening (21:00+), it is put away in the kitchen dish rack. Check dining for early evening, kitchen for late evening.
  * objects: ['water_bottle_ines']
* survived: Ines's glass, plate, and water bottle are on the dining table in the evening (20:00+). During the day (12:00-13:00) they are also on the dining table. In the late evening (21:00+), they are put away in the kitchen cupboard/dish rack. Check:
  * objects: ['glass_ines']
* recorded reason: claim_0019 is a subset of claim_0007. claim_0007 already states that the water bottle is on the dining table in the evening and put away in the kitchen dish rack in the late evening. claim_0019 adds a

### ACE_as_published / hh_s2_t03 day 18 — claim_0007 into claim_0002, by the model — **unclassifiable**

* folded in: Ines's glass, plate, water bottle, and mug are on the dining table in the morning (08:00-10:00), midday (12:00-13:00), and evening (20:00+). In the late evening (21:00+), they are put away in the kitchen cupboard/dish rack. Check dining for
  * objects: ['glass_ines']
* survived: Ines is in the dining room around midday (12:00-13:00) and in the evening (20:00-21:00). She is in the living room with Tomas at 21:09. Check dining for midday/early evening, living for late evening.
  * objects: none recognised
* recorded reason: Both notes describe Ines's location and the location of her dining items during overlapping time periods (midday and evening).

### ACE_as_published / hh_s2_t03 day 18 — claim_0017 into claim_0008, by the model — **CROSS-OBJECT**

* folded in: Ines's headphones are on the bedroom_1 wardrobe in the evening (13:00+). Check bedroom_1 wardrobe first. Do NOT check desk.
  * objects: ['headphones_ines']
* survived: Tomas's glass is in the bedroom_1 nightstand and his gym bag is in the bedroom_1 wardrobe in the evening (13:00+). Check bedroom_1 first.
  * objects: ['glass_tomas']
* recorded reason: Both notes describe the location of specific items in the bedroom_1 during the evening (13:00+).

### ACE_as_published / hh_s2_t03 day 18 — claim_0020 into claim_0008, by the model — **matcher limit**

* folded in: Tomas's gym bag is in the bedroom_1 wardrobe in the evening (13:00+). Check bedroom_1 wardrobe first.
  * objects: ['gym_bag_tomas']
* survived: Tomas's glass is in the bedroom_1 nightstand and his gym bag is in the bedroom_1 wardrobe in the evening (13:00+). Check bedroom_1 first.
  * objects: ['glass_tomas']
* recorded reason: Both describe the location of Tomas's personal items in the bedroom_1 during the evening (13:00+).

### ACE_as_published / hh_s32_t03 day 3 — claim_0015 into claim_0014, by the model — **CROSS-OBJECT**

* folded in: Leo's charger, mug, and water bottle are taken from the office desk to the kitchen in the evening. They return to the office desk by late night.
  * objects: ['charger_leo']
* survived: Leo's phone is often in the kitchen in the evening, while his other personal items stay in bedroom_1.
  * objects: ['phone_leo']
* recorded reason: Both notes describe the location of Leo's personal items in the evening. Claim 0014 states his phone is in the kitchen and other items are in bedroom_1. Claim 0015 states his charger, mug, and water b

### ACE_as_published / hh_s32_t03 day 4 — claim_0016 into claim_0011, by the model — **CROSS-OBJECT**

* folded in: Leo's pen is usually on the office desk. It was seen on the office floor at 15:58 but returned to the desk by 16:54.
  * objects: ['pen_leo']
* survived: Leo's laptop is usually on the office desk, but was seen on the office floor at 15:30. It returned to the desk by 15:46.
  * objects: ['laptop_leo']
* recorded reason: Both notes describe the same pattern of behavior for Leo's personal items (laptop and pen) in the office: they are usually on the desk but were observed on the floor at specific times and returned. M-

### ACE_as_published / hh_s32_t03 day 4 — claim_0017 into claim_0012, by the model — **CROSS-OBJECT**

* folded in: Aisha's water bottle appears in the kitchen in the evening (20:05, 22:48). It is not present in the kitchen during the day.
  * objects: ['water_bottle_aisha']
* survived: Aisha's tablet is kept on the nightstand in bedroom_3 in the evening. It was in the kitchen during the day.
  * objects: ['tablet_aisha']
* recorded reason: Both notes describe the location of Aisha's personal items (tablet and water bottle) in the evening, specifically noting their presence in the kitchen or bedroom_3 during that time, contrasting with/

### ACE_as_published / hh_s32_t03 day 12 — claim_0011 into claim_0001, by the model — **unclassifiable**

* folded in: Leo's pen is usually on the office desk. It was seen on the office floor at 22:01 and 22:02. It may fall off the desk late at night. Check floor if not on desk.
  * objects: ['pen_leo']
* survived: Leo works in the office. His desk holds laptop, charger, headphones, notebook, pen, and plant. Mug and water bottle are on the desk from ~09:36 to ~18:00. At night (22:59), charger, mug, water bottle, and laptop are gone from the desk; only
  * objects: none recognised
* recorded reason: Both notes describe the state of Leo's office desk and the location of his items (specifically the pen and other objects) during the day and at night. Claim 0011 adds specific detail about the pen's '

### ACE_as_published / hh_s32_t03 day 14 — claim_0023 into claim_0019, by the model — **CROSS-OBJECT**

* folded in: Leo's water bottle is on the office desk during the day. In the evening (after 13:00), it moves to bedroom_1 on the nightstand. It is not in the office or kitchen at night. Leo's glass is in the kitchen cupboard during the day. In the eveni
  * objects: ['glass_leo', 'water_bottle_leo']
* survived: Leo's charger is on the office desk during the day. In the evening (after 13:00), it moves to bedroom_1 on the bed. It is not in the office at night.
  * objects: ['charger_leo']
* recorded reason: Both notes describe the same object (Leo's charger/water bottle) moving from the office to bedroom_1 in the evening, with the same time threshold (13:00) and similar exclusion constraints. The '

### ACE_as_published / hh_s32_t03 day 14 — claim_0024 into claim_0023, by the model — **shared**

* folded in: Leo's glass is in the kitchen cupboard during the day. In the evening (after 13:00), it moves to bedroom_1 on the desk. It is not in the kitchen at night.
  * objects: ['glass_leo']
* survived: Leo's water bottle is on the office desk during the day. In the evening (after 13:00), it moves to bedroom_1 on the nightstand. It is not in the office or kitchen at night. Leo's glass is in the kitchen cupboard during the day. In the eveni
  * objects: ['glass_leo', 'water_bottle_leo']
* recorded reason: Both notes describe the same object (Leo's water bottle/glass) moving from the office/kitchen to bedroom_1 in the evening, with the same time threshold (13:00) and similar exclusion constraints. The '

### ACE_as_published / hh_s48_t03 day 2 — claim_0007 into claim_0006, by the model — **CROSS-OBJECT**

* folded in: Priya's plate is in the kitchen cupboard in the morning, but moves to the dining table by evening.
  * objects: ['plate_priya']
* survived: Priya's glass is in the kitchen cupboard in the morning, but moves to the dining table by evening.
  * objects: ['glass_priya']
* recorded reason: Both notes describe the same movement pattern for Priya's tableware (glass and plate) from the kitchen cupboard to the dining table between morning and evening.

### ACE_as_published / hh_s48_t03 day 2 — claim_0047 into claim_0046, by the model — **CROSS-OBJECT**

* folded in: Priya's glass and plate are in the kitchen cupboard in the late evening (seen at 20:59).
  * objects: ['glass_priya']
* survived: Priya's water bottle is in the kitchen dish rack in the late evening (seen at 20:59).
  * objects: ['water_bottle_priya']
* recorded reason: Both notes describe the location of Priya's items in the kitchen at the same time (20:59). Although the items and specific locations differ, they are part of the same observation of the kitchen state.

### ACE_as_published / hh_s48_t03 day 2 — claim_0049 into claim_0048, by the model — **CROSS-OBJECT**

* folded in: Marco's plate is in the kitchen cupboard in the late evening (seen at 20:59).
  * objects: ['plate_marco']
* survived: Marco's glass is in the kitchen cupboard in the late evening (seen at 20:59).
  * objects: ['glass_marco']
* recorded reason: Both notes describe the location of Marco's tableware (glass and plate) in the same place (kitchen cupboard) at the same time (20:59). They are distinct objects but can be combined into a single note.

### ACE_as_published / hh_s48_t03 day 2 — claim_0050 into claim_0047, by the model — **matcher limit**

* folded in: Priya's plate is in the kitchen cupboard in the late evening (seen at 20:59).
  * objects: ['plate_priya']
* survived: Priya's glass and plate are in the kitchen cupboard in the late evening (seen at 20:59).
  * objects: ['glass_priya']
* recorded reason: Both notes describe the location of Priya's tableware (glass and plate) in the same place (kitchen cupboard) at the same time (20:59). They are distinct objects but can be combined into a single note.

### ACE_as_published / hh_s48_t03 day 3 — claim_0003 into claim_0002, by the model — **CROSS-OBJECT**

* folded in: Marco's glass is in the kitchen cupboard in the morning and late evening. It moves to the dining table in the mid-evening (approx 15:00-20:00).
  * objects: ['glass_marco']
* survived: Marco's water bottle is in the kitchen dish rack in the morning and late evening. It moves to the dining table in the mid-evening (approx 19:00-20:00).
  * objects: ['water_bottle_marco']
* recorded reason: Both notes describe the same object (Marco's water bottle) moving from a kitchen location to the dining table in the mid-evening. The specific time window and starting location in claim_0003 are less/

### ACE_as_published / hh_s48_t03 day 4 — claim_0046 into claim_0005, by the model — **shared**

* folded in: Priya's water bottle is in the kitchen dish rack in the morning. It moves to the dining table by late evening (20:13).
  * objects: ['water_bottle_priya']
* survived: Priya's water bottle is in the kitchen dish rack in the morning. It moves to the dining table by late evening (20:13).
  * objects: ['water_bottle_priya']
* recorded reason: The text of both notes is identical.

### ACE_as_published / hh_s48_t03 day 4 — claim_0052 into claim_0039, by the model — **shared**

* folded in: Marco's skincare is on the bedroom_1 desk in the morning. It is not in the bathroom in the morning.
  * objects: ['skincare_marco']
* survived: Marco's skincare is on the bedroom_1 desk in the morning. It is not in the bathroom in the morning.
  * objects: ['skincare_marco']
* recorded reason: The text of both notes is identical.

### ACE_as_published / hh_s48_t03 day 5 — claim_0045 into claim_0002, by the model — **shared**

* folded in: Marco's water bottle is on the dining table in the evening.
  * objects: ['water_bottle_marco']
* survived: Marco's water bottle is on the dining table in the evening.
  * objects: ['water_bottle_marco']
* recorded reason: The text of both notes is identical.

### ACE_as_published / hh_s48_t03 day 7 — claim_0024 into claim_0016, by the model — **CROSS-OBJECT**

* folded in: Priya's notebook is on the entry floor in the evening.
  * objects: ['notebook_priya']
* survived: Priya's backpack is on the entry floor in the evening.
  * objects: ['backpack_priya']
* recorded reason: Both notes describe the same object (Priya's backpack) being in the same location (entry floor) at the same time (evening).

### ACE_as_published / hh_s48_t03 day 7 — claim_0034 into claim_0032, by the model — **CROSS-OBJECT**

* folded in: The shared spatula is in the kitchen drawer in the morning. It moves to the kitchen sink in the evening.
  * objects: ['spatula_shared']
* survived: The shared kitchen knife is in the kitchen drawer in the morning. It moves to the kitchen counter in the evening.
  * objects: ['kitchen_knife_shared']
* recorded reason: Both notes describe the same object (the shared kitchen knife) having the same location in the morning (kitchen drawer) and the same location in the evening (kitchen counter).

### ACE_as_published / hh_s48_t03 day 7 — claim_0048 into claim_0004, by the model — **CROSS-OBJECT**

* folded in: Marco's glass is in the kitchen cupboard in the morning. It moves to the dining table in the evening.
  * objects: ['glass_marco']
* survived: Marco's plate is in the kitchen cupboard in the morning. It moves to the dining table in the evening.
  * objects: ['plate_marco']
* recorded reason: Both notes describe the same object (Marco's plate) having the same location in the morning (kitchen cupboard) and the same location in the evening (dining table).

### ACE_as_published / hh_s48_t03 day 7 — claim_0051 into claim_0033, by the model — **CROSS-OBJECT**

* folded in: The shared serving dish is in the kitchen cupboard in the morning. It moves to the dining table in the evening.
  * objects: ['serving_dish_shared']
* survived: The shared pan is in the kitchen cupboard in the morning. It moves to the kitchen sink in the evening.
  * objects: ['pan_shared']
* recorded reason: Both notes describe the same object (the shared pan) having the same location in the morning (kitchen cupboard) and the same location in the evening (kitchen sink).

### claim_store_told_if_it_was_right / hh_s123_t03 day 11 — claim_0007 into claim_0003, by the model — **shared**

* folded in: Priya's water bottle is on the kitchen dish rack. Duplicate of claim_0019.
  * objects: ['water_bottle_priya']
* survived: Priya's water bottle is on the kitchen dish rack. Duplicate of claim_0019.
  * objects: ['water_bottle_priya']
* recorded reason: Merging duplicates to reduce clutter.

### claim_store_told_if_it_was_right / hh_s123_t03 day 11 — claim_0016 into claim_0009, by the model — **CROSS-OBJECT**

* folded in: Sam's vitamins are on the kitchen counter. Duplicate of claim_0034.
  * objects: ['vitamins_sam']
* survived: Priya's water bottle is on the kitchen dish rack. Duplicate of claim_0019.
  * objects: ['water_bottle_priya']
* recorded reason: Merging duplicates to reduce clutter.

### claim_store_told_if_it_was_right / hh_s123_t03 day 11 — claim_0018 into claim_0017, by the model — **unclassifiable**

* folded in: The dog food bag is on the kitchen pantry shelf. Duplicate of claim_0005.
  * objects: none recognised
* survived: Sam's plate is on the kitchen table. Duplicate of claim_0015.
  * objects: ['plate_sam']
* recorded reason: Merging duplicates to reduce clutter.

### claim_store_told_if_it_was_right / hh_s123_t03 day 12 — claim_0004 into claim_0039, by the backstop rule — **shared**

* folded in: Sam's mug is not on the kitchen cupboard. It was on the table at 08:38 and the sink at 20:14. It is likely in the bedroom or entry when not in the kitchen.
  * objects: ['mug_sam']
* survived: Priya's mug is on the kitchen cupboard. Sam's mug is on the kitchen cupboard. They have been there consistently.
  * objects: ['mug_priya', 'mug_sam']
* recorded reason: folded by the code, not by the model: the notes were over the line they were given, this claim had the worst record, and the two are claimed under the same routine

### claim_store_told_if_it_was_right / hh_s123_t03 day 15 — claim_0039 into claim_0076, by the backstop rule — **shared**

* folded in: Sam's mug and plate are on the kitchen cupboard when not in use. Sam's mug moves to the office desk when he is working. [sighting_2222, sighting_2246]
  * objects: ['mug_sam']
* survived: Sam's mug is on the kitchen cupboard. [sighting_2148]
  * objects: ['mug_sam']
* recorded reason: folded by the code, not by the model: the notes were over the line they were given, this claim had the worst record, and the two are claimed under the same routine

### claim_store_told_if_it_was_right / hh_s123_t03 day 16 — claim_0076 into claim_0075, by the backstop rule — **shared**

* folded in: Sam's mug is on the kitchen cupboard. [sighting_2148]. Also: Sam's mug and plate are on the kitchen cupboard when not in use. Sam's mug moves to the office desk when he is working. [sighting_2222, sighting_2246]
  * objects: ['mug_sam']
* survived: Priya's mug is on the kitchen cupboard. Sam's mug is on the kitchen sink. Sam's mug moves to the office desk when he is working.
  * objects: ['mug_priya', 'mug_sam']
* recorded reason: folded by the code, not by the model: the notes were over the line they were given, this claim had the worst record, and the two are claimed under the same routine

### claim_store_told_if_it_was_right / hh_s123_t03 day 17 — claim_0001 into claim_0013, by the model — **shared**

* folded in: Priya's razor is on the bathroom sink. Priya's towel is on the bathroom shelf. They are in their resting places. [sighting_2108, sighting_2106, sighting_2266, sighting_2264]
  * objects: ['razor_priya', 'towel_priya']
* survived: Priya's razor is on the bathroom sink. Priya's towel is on the bathroom shelf. These are their consistent resting places.
  * objects: ['razor_priya', 'towel_priya']
* recorded reason: Merged duplicate notes. Corrected razor location to shelf and towel to rack based on consistent sightings today.

### claim_store_told_if_it_was_right / hh_s123_t03 day 17 — claim_0002 into claim_0020, by the model — **shared**

* folded in: Sam's razor is on the bathroom sink. Sam's towel is on the bathroom towel rack. They have been there consistently.
  * objects: ['razor_sam', 'towel_sam']
* survived: Sam's razor is on the bathroom sink. Sam's towel is on the towel rack. These are their consistent resting places.
  * objects: ['razor_sam', 'towel_sam']
* recorded reason: Merged duplicate notes. Confirmed locations based on consistent sightings today.

### claim_store_told_if_it_was_right / hh_s123_t03 day 17 — claim_0003 into claim_0037, by the model — **CROSS-OBJECT**

* folded in: Priya's water bottle is on the kitchen dish rack. Duplicate of claim_0019.
  * objects: ['water_bottle_priya']
* survived: Priya's bowl is on the kitchen sink. Sam's bowl is on the kitchen cupboard. [sighting_2158, sighting_2147]
  * objects: ['bowl_priya', 'bowl_sam']
* recorded reason: Merged duplicate notes. Locations confirmed today.

### claim_store_told_if_it_was_right / hh_s123_t03 day 17 — claim_0008 into claim_0044, by the model — **unclassifiable**

* folded in: Sam is in the bathroom in the morning. He was there at 07:47 on Day 9.
  * objects: none recognised
* survived: Priya is in the living room in the morning. She was there at 07:15.
  * objects: none recognised
* recorded reason: Merged duplicate notes. Priya seen in bathroom, not living room, this morning. Sam not seen in bathroom.

### claim_store_told_if_it_was_right / hh_s123_t03 day 17 — claim_0009 into claim_0036, by the model — **shared**

* folded in: Sam's vitamins are on the kitchen counter. They have been there consistently.
  * objects: ['vitamins_sam']
* survived: Plant pot 2 and Sam's vitamins are on the kitchen counter.
  * objects: ['vitamins_sam']
* recorded reason: Merged duplicate notes. Locations confirmed today.

### claim_store_told_if_it_was_right / hh_s123_t03 day 17 — claim_0011 into claim_0025, by the model — **unclassifiable**

* folded in: The pot is on the kitchen cupboard. It has been there consistently.
  * objects: none recognised
* survived: The pan and pot are on the kitchen cupboard.
  * objects: none recognised
* recorded reason: Merged duplicate notes. Locations confirmed today.

### claim_store_told_if_it_was_right / hh_s123_t03 day 17 — claim_0014 into claim_0075, by the model — **CROSS-OBJECT**

* folded in: Priya's glass is on the bedroom_1 nightstand. Sam's glass is on the kitchen table. Sam's glass was seen on the sink in the past, but has moved to the table.
  * objects: ['glass_priya', 'glass_sam']
* survived: Priya's mug is on the kitchen cupboard. Sam's mug is on the kitchen sink. Sam's mug moves to the office desk when he is working. Also: Sam's mug is on the kitchen cupboard. [sighting_2148]. Also: Sam's mug and plate are on the kitchen cupboard when not in use. Sam's mug moves to the office desk when he is working. [sighting_2222, sighting_2246]
  * objects: ['mug_priya', 'mug_sam']
* recorded reason: Merged duplicate notes. Corrected Sam's glass to table and Priya's mug to coffee table based on today's sightings.

### claim_store_told_if_it_was_right / hh_s123_t03 day 17 — claim_0015 into claim_0017, by the model — **shared**

* folded in: Sam's plate is on the kitchen cupboard. It was on the sink at 18:03 and table at 20:14, but moved to the cupboard by 22:09. The cupboard is its resting place.
  * objects: ['plate_sam']
* survived: Sam's plate is on the kitchen cupboard. It was on the table at 20:13 but moved to the cupboard by 21:43. The cupboard is its resting place.
  * objects: ['plate_sam']
* recorded reason: Merged duplicate notes. Plate seen on table today.

### claim_store_told_if_it_was_right / hh_s123_t03 day 17 — claim_0021 into claim_0010, by the model — **unclassifiable**

* folded in: Priya's glass is on the kitchen cupboard. It was on the sink at 18:03 and 20:14, but moved to the cupboard by 22:09. The cupboard is its resting place.
  * objects: ['glass_priya']
* survived: Priya's and Sam's plates are on the kitchen sink during the day. They move to the cupboard at night. [sighting_2160, sighting_2161]
  * objects: none recognised
* recorded reason: Merged duplicate notes. Corrected Priya's plate to couch. Glass not seen today.

### claim_store_told_if_it_was_right / hh_s123_t03 day 17 — claim_0023 into claim_0006, by the model — **unclassifiable**

* folded in: Sam is in the kitchen in the afternoon. He was there at 14:35 and 19:22 on Day 9.
  * objects: none recognised
* survived: Sam is in the kitchen in the afternoon and evening. Priya is in the kitchen in the evening. [sighting_1940, sighting_1982, sighting_2004, sighting_2050]
  * objects: none recognised
* recorded reason: Merged duplicate notes. Sam seen in kitchen today.

### claim_store_told_if_it_was_right / hh_s123_t03 day 17 — claim_0026 into claim_0027, by the model — **unclassifiable**

* folded in: The spatula is on the kitchen drawer. It has been there consistently.
  * objects: none recognised
* survived: The kitchen knife and spatula are in the kitchen drawer.
  * objects: none recognised
* recorded reason: Merged duplicate notes. Locations confirmed today.

### claim_store_told_if_it_was_right / hh_s123_t03 day 17 — claim_0028 into claim_0005, by the model — **unclassifiable**

* folded in: The dog bowl is on the kitchen floor. It has been there consistently.
  * objects: none recognised
* survived: The dog bowl is on the kitchen floor. The dog food bag is on the pantry shelf.
  * objects: none recognised
* recorded reason: Merged duplicate notes. Corrected dog food bag to floor based on today's sightings (was pantry in old note).

### claim_store_told_if_it_was_right / hh_s123_t03 day 17 — claim_0029 into claim_0012, by the model — **unclassifiable**

* folded in: Fruit bowl is on the kitchen table. Shopping bag is on the pantry shelf. [sighting_2154, sighting_2157]
  * objects: none recognised
* survived: The cutting board is on the kitchen counter. The recipe book and shopping bag are on the pantry shelf. The fruit bowl is on the kitchen table.
  * objects: none recognised
* recorded reason: Merged duplicate notes. Locations confirmed today.

### claim_store_told_if_it_was_right / hh_s123_t03 day 17 — claim_0030 into claim_0024, by the model — **unclassifiable**

* folded in: The shopping bag is on the kitchen pantry shelf. The recipe book is on the kitchen pantry shelf.
  * objects: none recognised
* survived: The recipe book is on the kitchen chair. The shopping bag is on the kitchen pantry shelf.
  * objects: none recognised
* recorded reason: Merged duplicate notes. Corrected recipe book to pantry shelf based on today's sightings (was chair in old note).

### claim_store_told_if_it_was_right / hh_s123_t03 day 17 — claim_0032 into claim_0031, by the model — **unclassifiable**

* folded in: The knife block is on the kitchen counter. It has been there consistently.
  * objects: none recognised
* survived: The kettle and knife block are on the kitchen counter.
  * objects: none recognised
* recorded reason: Merged duplicate notes. Locations confirmed today.

### claim_store_told_if_it_was_right / hh_s123_t03 day 17 — claim_0035 into claim_0033, by the model — **unclassifiable**

* folded in: The wall clock is on the kitchen counter. It has been there consistently.
  * objects: none recognised
* survived: The toaster and wall clock are on the kitchen counter.
  * objects: none recognised
* recorded reason: Merged duplicate notes. Locations confirmed today.

### claim_store_told_if_it_was_right / hh_s123_t03 day 17 — claim_0038 into claim_0034, by the model — **CROSS-OBJECT**

* folded in: Sam's bowl is on the kitchen cupboard. It has been there consistently.
  * objects: ['bowl_sam']
* survived: Sam's vitamins are on the kitchen counter. It has been there consistently.
  * objects: ['vitamins_sam']
* recorded reason: Merged duplicate notes. Locations confirmed today.

### claim_store_told_if_it_was_right / hh_s123_t03 day 17 — claim_0043 into claim_0040, by the model — **shared**

* folded in: Sam's book is on the kitchen table. It was there at 07:15 but not at 14:53.
  * objects: ['book_sam']
* survived: Sam's book is on the kitchen table during the day. It is not in the kitchen in the evening.
  * objects: ['book_sam']
* recorded reason: Merged duplicate notes. Not seen today.

### claim_store_told_if_it_was_right / hh_s123_t03 day 17 — claim_0045 into claim_0022, by the model — **unclassifiable**

* folded in: Sam is in the kitchen in the morning. Priya is in the bathroom in the morning. [sighting_1940, sighting_1911]
  * objects: none recognised
* survived: Priya is in the bathroom in the early morning. Sam is in the bathroom in the morning. [sighting_1911, sighting_1914]
  * objects: none recognised
* recorded reason: Merged duplicate notes. Priya seen in bathroom this morning.

### claim_store_told_if_it_was_right / hh_s123_t03 day 17 — claim_0046 into claim_0041, by the model — **shared**

* folded in: Sam's textbook is on the office desk. The first aid kit is on the bathroom medicine cabinet. Priya's towel is on the bathroom shelf. They are in their current spots.
  * objects: ['textbook_sam', 'towel_priya']
* survived: First aid kit is on the bathroom medicine cabinet. Sam's textbook is on the office desk.
  * objects: ['textbook_sam']
* recorded reason: Merged duplicate notes. First aid kit location confirmed. Textbook not seen today but assumed stable.

### claim_store_told_if_it_was_right / hh_s123_t03 day 17 — claim_0047 into claim_0042, by the model — **shared**

* folded in: Priya's phone is on the kitchen table. It appeared at 20:14 and was gone by 22:09. It is likely in the living room or bedroom when not in use.
  * objects: ['phone_priya']
* survived: Priya's phone is not consistently in one spot. It was not seen in the kitchen or living room today. [sighting_2050, sighting_2072]
  * objects: ['phone_priya']
* recorded reason: Merged duplicate notes. Phone not seen today.

### claim_store_told_if_it_was_right / hh_s123_t03 day 17 — claim_0053 into claim_0049, by the model — **unclassifiable**

* folded in: Remote is on the coffee table in the living room. [sighting_2214]
  * objects: none recognised
* survived: Priya's mug and the remote are on the coffee table in the living room in the evening.
  * objects: ['mug_priya']
* recorded reason: Merged duplicate notes. Locations confirmed today.

### claim_store_told_if_it_was_right / hh_s123_t03 day 17 — claim_0055 into claim_0067, by the model — **unclassifiable**

* folded in: Plant pot 3 is on the office desk. [sighting_2224]
  * objects: none recognised
* survived: Sam's book is not in the kitchen or living room in the evening. [sighting_2160, sighting_2213]
  * objects: ['book_sam']
* recorded reason: Merged duplicate notes. Not seen today.

### claim_store_told_if_it_was_right / hh_s123_t03 day 17 — claim_0059 into claim_0058, by the model — **unclassifiable**

* folded in: Dog toy is on the living room floor. [sighting_2171]
  * objects: none recognised
* survived: Candle, lamp, and plant pot 1 are in the living room (coffee table/side table). [sighting_2167, sighting_2172, sighting_2173]
  * objects: none recognised
* recorded reason: Merged duplicate notes. Locations confirmed today.

### claim_store_told_if_it_was_right / hh_s123_t03 day 17 — claim_0060 into claim_0054, by the model — **unclassifiable**

* folded in: Picture frame and vase are on the bookshelf in the living room. [sighting_2164, sighting_2166]
  * objects: none recognised
* survived: Sam's camera, magazine, and speaker are on the bookshelf/coffee table in the living room. [sighting_2163, sighting_2168, sighting_2165]
  * objects: ['camera_sam']
* recorded reason: Merged duplicate notes. Locations confirmed today.

### claim_store_told_if_it_was_right / hh_s123_t03 day 17 — claim_0061 into claim_0057, by the model — **unclassifiable**

* folded in: Cushions are on the couch and armchair in the living room. [sighting_2170, sighting_2162]
  * objects: none recognised
* survived: Blanket is on the couch in the living room. [sighting_2169]
  * objects: none recognised
* recorded reason: Merged duplicate notes. Locations confirmed today.

### claim_store_told_if_it_was_right / hh_s123_t03 day 17 — claim_0063 into claim_0062, by the model — **unclassifiable**

* folded in: Laundry basket is on the bathroom shelf. [sighting_2103]
  * objects: none recognised
* survived: Priya's hair dryer and the laundry basket are on the bathroom shelf.
  * objects: ['hair_dryer_priya']
* recorded reason: Merged duplicate notes. Locations confirmed today.

### claim_store_told_if_it_was_right / hh_s123_t03 day 17 — claim_0065 into claim_0064, by the model — **unclassifiable**

* folded in: Sam's skincare is on the bathroom medicine cabinet. It was on the shelf earlier in the day but moved to the cabinet by 08:55.
  * objects: ['skincare_sam']
* survived: The soap dispenser and toothbrush holder are on the bathroom sink.
  * objects: none recognised
* recorded reason: Merged duplicate notes. Corrected Sam's skincare to shelf based on today's sightings (was cabinet in old note).

### claim_store_told_if_it_was_right / hh_s123_t03 day 17 — claim_0066 into claim_0051, by the model — **unclassifiable**

* folded in: Priya's phone is not in the kitchen or living room in the evening. [sighting_2160, sighting_2213]
  * objects: ['phone_priya']
* survived: Priya is in the living room in the evening. [sighting_2213, sighting_2254]
  * objects: none recognised
* recorded reason: Merged duplicate notes. Priya seen in living room. Phone not seen.

### claim_store_told_if_it_was_right / hh_s123_t03 day 17 — claim_0068 into claim_0019, by the model — **shared**

* folded in: Priya's water bottle is on the nightstand in bedroom_1.
  * objects: ['water_bottle_priya']
* survived: Priya's water bottle is on the bedroom_1 nightstand. It was previously noted on the kitchen dish rack, but the nightstand is its current resting place.
  * objects: ['water_bottle_priya']
* recorded reason: Merged duplicate notes. Location confirmed today.

### claim_store_told_if_it_was_right / hh_s123_t03 day 17 — claim_0070 into claim_0075, by the backstop rule — **shared**

* folded in: Sam's glass is on the kitchen sink. [sighting_2159]
  * objects: ['glass_sam']
* survived: Priya's mug is on the coffee table in the evening. Sam's mug is on the kitchen sink. Sam's glass is on the kitchen table.
  * objects: ['glass_sam', 'mug_priya', 'mug_sam']
* recorded reason: folded by the code, not by the model: the notes were over the line they were given, this claim had the worst record, and the two are claimed under the same routine

### claim_store_told_if_it_was_right / hh_s123_t03 day 17 — claim_0072 into claim_0071, by the model — **shared**

* folded in: Sam's bowl is on the kitchen cupboard.
  * objects: ['bowl_sam']
* survived: Priya's bowl is on the kitchen sink. Sam's bowl is on the kitchen cupboard.
  * objects: ['bowl_priya', 'bowl_sam']
* recorded reason: Merged duplicate notes. Locations confirmed today.

### claim_store_told_if_it_was_right / hh_s123_t03 day 17 — claim_0074 into claim_0073, by the model — **shared**

* folded in: Sam's plate is on the kitchen table. It moves to the cupboard when not in use.
  * objects: ['plate_sam']
* survived: Priya's plate is on the kitchen table. Sam's plate is on the kitchen table. They are currently in use or recently used.
  * objects: ['plate_priya', 'plate_sam']
* recorded reason: Merged duplicate notes. Updated Priya's plate location to couch based on evening sighting. Sam's plate on table.

### claim_store_told_if_it_was_right / hh_s123_t03 day 17 — claim_0077 into claim_0048, by the model — **shared**

* folded in: Priya's charger is on the bed in bedroom_1. [sighting_2133]
  * objects: ['charger_priya']
* survived: Priya's charger is on the bed in bedroom_1.
  * objects: ['charger_priya']
* recorded reason: Merged duplicate notes. Location confirmed today.

### claim_store_told_if_it_was_right / hh_s123_t03 day 17 — claim_0078 into claim_0052, by the model — **shared**

* folded in: Priya's pencil case is on the bedroom floor. [sighting_2134]
  * objects: ['pencil_case_priya']
* survived: Priya's pencil case is on the bedroom_1 floor. Her sketchbook is on the desk.
  * objects: ['pencil_case_priya']
* recorded reason: Merged duplicate notes. Locations confirmed today.

### claim_store_told_if_it_was_right / hh_s123_t03 day 17 — claim_0080 into claim_0079, by the model — **CROSS-OBJECT**

* folded in: Priya's water bottle is on the nightstand in bedroom_1. [sighting_2137]
  * objects: ['water_bottle_priya']
* survived: Priya's sketchbook is on the desk in bedroom_1. [sighting_2135]
  * objects: ['sketchbook_priya']
* recorded reason: Merged duplicate notes. Locations confirmed today.

### claim_store_told_if_it_was_right / hh_s123_t03 day 17 — claim_0081 into claim_0069, by the model — **shared**

* folded in: Priya's glass is on the nightstand in bedroom_1. [sighting_2136]
  * objects: ['glass_priya']
* survived: Priya's glass is on the nightstand in bedroom_1.
  * objects: ['glass_priya']
* recorded reason: Merged duplicate notes. Location confirmed today.

### claim_store_told_if_it_was_right / hh_s123_t03 day 17 — claim_0082 into claim_0056, by the model — **shared**

* folded in: Priya's gym bag is on the wardrobe in bedroom_1. [sighting_2138]
  * objects: ['gym_bag_priya']
* survived: Priya's gym bag and the iron are on the wardrobe in bedroom_1.
  * objects: ['gym_bag_priya']
* recorded reason: Merged duplicate notes. Locations confirmed today.

### claim_store_told_if_it_was_right / hh_s123_t03 day 17 — claim_0084 into claim_0083, by the model — **unclassifiable**

* folded in: Blanket is on the bed in bedroom_1. [sighting_2132]
  * objects: none recognised
* survived: The iron is on the wardrobe in bedroom_1. The blanket is on the bed in bedroom_1.
  * objects: none recognised
* recorded reason: Merged duplicate notes. Locations confirmed today.

### claim_store_told_if_it_was_right / hh_s123_t03 day 17 — claim_0086 into claim_0085, by the model — **matcher limit**

* folded in: Sam's laptop is on the desk in the office. [sighting_2221]
  * objects: ['laptop_sam']
* survived: Sam's headphones and laptop are on the desk in the office.
  * objects: ['headphones_sam']
* recorded reason: Merged duplicate notes. Not seen today, assumed stable.

### claim_store_told_if_it_was_right / hh_s123_t03 day 17 — claim_0088 into claim_0087, by the model — **matcher limit**

* folded in: Sam's textbook is on the desk in the office. [sighting_2225]
  * objects: ['textbook_sam']
* survived: Sam's pen and textbook are on the desk in the office.
  * objects: ['pen_sam']
* recorded reason: Merged duplicate notes. Not seen today, assumed stable.

### claim_store_told_if_it_was_right / hh_s123_t03 day 17 — claim_0089 into claim_0050, by the model — **unclassifiable**

* folded in: Plant pot 3 is on the desk in the office.
  * objects: none recognised
* survived: Sam is in the office in the evening. His laptop, headphones, pen, and textbook are on the desk.
  * objects: none recognised
* recorded reason: Merged duplicate notes. Not seen today, assumed stable.

### claim_store_told_if_it_was_right / hh_s123_t03 day 23 — claim_0067 into claim_0087, by the backstop rule — **shared**

* folded in: Sam's book is not in the kitchen or living room in the evening. Plant pot 3 is on the office desk.
  * objects: ['book_sam']
* survived: Evening: Sam's book in bedroom_2. Sam's pen/textbook not seen in office (only headphones/laptop/mug/plant3). Plant pot 3 on office desk.
  * objects: ['book_sam', 'pen_sam']
* recorded reason: folded by the code, not by the model: the notes were over the line they were given, this claim had the worst record, and the two are claimed under the same routine

### claim_store_told_if_it_was_right / hh_s123_t03 day 25 — claim_0087 into claim_0075, by the backstop rule — **shared**

* folded in: Evening: Sam's book in bedroom_2. Sam's pen/textbook not seen in office (only headphones/laptop/mug/plant3). Plant pot 3 on office desk. Also: Sam's book is not in the kitchen or living room in the evening. Plant pot 3 is on the office desk
  * objects: ['book_sam', 'pen_sam']
* survived: Evening: Sam's book in bedroom_2. Sam's pen/textbook not seen in office (only headphones/laptop/mug/plant3). Plant pot 3 on office desk. Also: Sam's book is not in the kitchen or living room in the evening. Plant pot 3 is on the office desk
  * objects: ['book_sam', 'pen_sam']
* recorded reason: folded by the code, not by the model: the notes were over the line they were given, this claim had the worst record, and the two are claimed under the same routine

### claim_store_told_if_it_was_right / hh_s123_t03 day 31 — claim_0006 into claim_0005, by the model — **unclassifiable**

* folded in: Dog bowl on pantry shelf. Dog food bag on kitchen floor. Sam in kitchen/office in afternoon/evening.
  * objects: none recognised
* survived: Dog bowl on kitchen floor. Dog food bag on pantry shelf. Sam is often in kitchen or office in afternoon/evening.
  * objects: none recognised
* recorded reason: Merging duplicate notes about dog items and Sam's location.

### claim_store_told_if_it_was_right / hh_s123_t03 day 31 — claim_0024 into claim_0012, by the model — **unclassifiable**

* folded in: Recipe book and shopping bag on counter (day) or pantry shelf (evening). Cutting board on sink (day) or counter (evening). Fruit bowl on kitchen table.
  * objects: none recognised
* survived: Recipe book on kitchen counter. Shopping bag on pantry shelf. Cutting board: dish rack (day) or counter (evening). Fruit bowl on kitchen table.
  * objects: none recognised
* recorded reason: Merging duplicate notes about kitchen items.

### claim_store_told_if_it_was_right / hh_s123_t03 day 31 — claim_0027 into claim_0025, by the model — **unclassifiable**

* folded in: Kitchen knife and spatula on sink (day) or drawer (evening). Pan and pot on sink (day) or cupboard (evening).
  * objects: none recognised
* survived: Kitchen knife and spatula on drawer. Pan and pot on kitchen cupboard. These locations are stable.
  * objects: none recognised
* recorded reason: Merging duplicate notes about kitchen utensils.

### claim_store_told_if_it_was_right / hh_s123_t03 day 31 — claim_0031 into claim_0036, by the model — **shared**

* folded in: Kettle, knife block, toaster, wall clock, plant pot 2, and Sam's vitamins on kitchen counter.
  * objects: ['vitamins_sam']
* survived: Kettle, knife block, toaster, wall clock, plant pot 2, and Sam's vitamins are on the kitchen counter. Stable.
  * objects: ['vitamins_sam']
* recorded reason: Merging duplicate notes about kitchen counter items.

### claim_store_told_if_it_was_right / hh_s123_t03 day 31 — claim_0033 into claim_0017, by the model — **shared**

* folded in: Sam's plate on kitchen table. Toaster and wall clock on kitchen counter.
  * objects: ['plate_sam']
* survived: Sam's plate: kitchen table (day) or kitchen cupboard (evening). Toaster and wall clock on kitchen counter.
  * objects: ['plate_sam']
* recorded reason: Merging duplicate notes about Sam's plate and kitchen counter items.

### claim_store_told_if_it_was_right / hh_s123_t03 day 31 — claim_0034 into claim_0041, by the model — **shared**

* folded in: Sam's vitamins are on the kitchen counter. Sam's bowl is on the kitchen cupboard.
  * objects: ['bowl_sam', 'vitamins_sam']
* survived: First aid kit on bathroom medicine cabinet. Sam's vitamins on kitchen counter. Sam's bowl on kitchen cupboard. Priya's bowl on kitchen cupboard.
  * objects: ['bowl_priya', 'bowl_sam', 'vitamins_sam']
* recorded reason: Merging duplicate notes about first aid kit, vitamins, and bowls.

### claim_store_told_if_it_was_right / hh_s123_t03 day 31 — claim_0044 into claim_0022, by the model — **unclassifiable**

* folded in: Morning: Priya in bedroom_1/bathroom. Sam in bathroom/office.
  * objects: none recognised
* survived: Morning: Priya in bedroom_1 or bathroom. Sam in bathroom or office. This pattern holds for early morning sightings.
  * objects: none recognised
* recorded reason: Merging duplicate notes about morning locations.

### claim_store_told_if_it_was_right / hh_s123_t03 day 31 — claim_0049 into claim_0091, by the model — **unclassifiable**

* folded in: Evening: Cushion 1 on couch, cushion 2 on armchair. Blanket on coffee table. Remote on TV stand. These living room items are stable in the evening.
  * objects: none recognised
* survived: Priya's and Sam's towels are on the towel rack. Evening: Cushion 1 on couch, cushion 2 on armchair. Blanket on coffee table. Remote on TV stand.
  * objects: none recognised
* recorded reason: Merging duplicate notes about evening living room items.

### claim_store_told_if_it_was_right / hh_s123_t03 day 31 — claim_0051 into claim_0050, by the model — **shared**

* folded in: Evening: Sam in office/kitchen. Priya in kitchen/living. Priya's phone not in kitchen/living.
  * objects: ['phone_priya']
* survived: Evening: Sam in office/kitchen. Priya in bedroom_1/kitchen. Priya's phone not in kitchen/living. Sam's book moves to bedroom_2.
  * objects: ['book_sam', 'phone_priya']
* recorded reason: Merging duplicate notes about evening locations.

### claim_store_told_if_it_was_right / hh_s123_t03 day 31 — claim_0054 into claim_0057, by the model — **unclassifiable**

* folded in: Living room: Camera/speaker/vase/frame on bookshelf. Magazine/candle/blanket on coffee table. Lamp/plant1 on side table. Dog toy on floor. Cushions on couch/armchair.
  * objects: none recognised
* survived: Living room: Camera/speaker/vase/frame on bookshelf. Magazine/candle/blanket on coffee table. Lamp/plant1 on side table. Dog toy on floor. Cushions on couch/armchair.
  * objects: none recognised
* recorded reason: Merging duplicate notes about living room layout.

### claim_store_told_if_it_was_right / hh_s123_t03 day 31 — claim_0056 into claim_0058, by the model — **unclassifiable**

* folded in: The iron is on the wardrobe in bedroom_1. The blanket is on the bed in bedroom_1. These locations are stable.
  * objects: none recognised
* survived: Iron on wardrobe in bedroom_1. Blanket on bed in bedroom_1. Living room items stable.
  * objects: none recognised
* recorded reason: Merging duplicate notes about bedroom_1 items.

### claim_store_told_if_it_was_right / hh_s123_t03 day 31 — claim_0062 into claim_0013, by the model — **shared**

* folded in: Priya's razor and hair dryer on bathroom shelf. Priya's towel on towel rack. Laundry basket on shelf. First aid kit on medicine cabinet.
  * objects: ['razor_priya', 'towel_priya']
* survived: Priya's razor, hair dryer, and laundry basket are on the bathroom shelf. Priya's towel is on the towel rack. First aid kit is on the medicine cabinet. Stable.
  * objects: ['razor_priya', 'towel_priya']
* recorded reason: Merging duplicate notes about Priya's bathroom items.

### claim_store_told_if_it_was_right / hh_s123_t03 day 31 — claim_0064 into claim_0020, by the model — **shared**

* folded in: Sam's razor on sink, towel on rack, skincare on shelf. Soap/toothbrush on sink.
  * objects: ['razor_sam']
* survived: Sam's razor is on the sink. Sam's skincare is on the shelf. Sam's towel is on the towel rack. Soap and toothbrush holder on sink. First aid kit on medicine cabinet.
  * objects: ['razor_sam', 'skincare_sam', 'towel_sam']
* recorded reason: Merging duplicate notes about Sam's bathroom items. Note: Sam's razor is on shelf, not sink as previously thought in claim_0020.

### claim_store_told_if_it_was_right / hh_s123_t03 day 31 — claim_0069 into claim_0010, by the model — **shared**

* folded in: Priya's glass: bedroom_1 nightstand (morning) or kitchen table (evening). Plate: kitchen pantry shelf (day) or kitchen table (evening).
  * objects: ['glass_priya']
* survived: Priya's glass: kitchen table (day) or kitchen cupboard (evening). Plate: kitchen table (day) or kitchen cupboard (evening).
  * objects: ['glass_priya']
* recorded reason: Merging duplicate notes about Priya's glass and plate.

### claim_store_told_if_it_was_right / hh_s123_t03 day 31 — claim_0071 into claim_0037, by the model — **shared**

* folded in: Priya's bowl on kitchen cupboard. Sam's bowl on kitchen cupboard.
  * objects: ['bowl_priya', 'bowl_sam']
* survived: Priya's bowl and Sam's bowl are on the kitchen cupboard. Stable.
  * objects: ['bowl_priya', 'bowl_sam']
* recorded reason: Merging duplicate notes about bowls.

### claim_store_told_if_it_was_right / hh_s123_t03 day 31 — claim_0073 into claim_0083, by the model — **shared**

* folded in: Priya's plate on kitchen cupboard (day) or kitchen table (evening). Sam's plate on kitchen cupboard. First aid kit on bathroom medicine cabinet. Sam's vitamins on kitchen counter.
  * objects: ['plate_priya', 'plate_sam', 'vitamins_sam']
* survived: Iron on wardrobe in bedroom_1. Priya's plate on kitchen cupboard (evening). Sam's plate on kitchen cupboard (evening). First aid kit on bathroom med cab. Sam's vitamins on kitchen counter.
  * objects: ['plate_priya', 'plate_sam', 'vitamins_sam']
* recorded reason: Merging duplicate notes about iron, plates, first aid kit, and vitamins.

### claim_store_told_if_it_was_right / hh_s123_t03 day 31 — claim_0075 into claim_0040, by the model — **shared**

* folded in: Evening: Sam's book in bedroom_2. Sam's pen/textbook on office desk. Plant pot 3 on office desk. Priya's plate on kitchen cupboard. Sam's plate on kitchen cupboard.
  * objects: ['book_sam', 'pen_sam', 'plate_priya', 'plate_sam']
* survived: Sam's book: kitchen table (day), bedroom_2 bed (evening). Sam's mug: kitchen table (day), office desk (evening). Plant pot 3: office desk. In the evening, Sam's book is not in the kitchen or living room.
  * objects: ['book_sam', 'mug_sam']
* recorded reason: Merging notes about Sam's book, mug, and plant pot 3.

### claim_store_told_if_it_was_right / hh_s123_t03 day 31 — claim_0079 into claim_0048, by the model — **CROSS-OBJECT**

* folded in: Priya's pencil case, sketchbook, and water bottle are on the bedroom_1 desk in the evening.
  * objects: ['pencil_case_priya']
* survived: Priya's water bottle: bedroom_1 desk (evening) or kitchen table (day). Charger: bedroom_1 desk (evening).
  * objects: ['water_bottle_priya']
* recorded reason: Merging notes about Priya's water bottle, charger, and desk items.

### claim_store_told_if_it_was_right / hh_s123_t03 day 31 — claim_0085 into claim_0042, by the model — **shared**

* folded in: Evening: Sam's headphones, laptop, pen, textbook, and mug on office desk. Plant pot 3 on office desk.
  * objects: ['headphones_sam']
* survived: Evening: Sam's headphones, laptop, pen, textbook, and plant pot 3 are on the office desk. Mug is on kitchen sink.
  * objects: ['headphones_sam']
* recorded reason: Merging duplicate notes about Sam's office items.

### claim_store_told_if_it_was_right / hh_s123_t03 day 31 — claim_0090 into claim_0075, by the model — **shared**

* folded in: Evening: Sam's book in bedroom_2. Sam's pen/textbook on office desk. Plant pot 3 on office desk. Priya's plate on kitchen cupboard. Sam's plate on kitchen cupboard.
  * objects: ['book_sam', 'pen_sam', 'plate_priya', 'plate_sam']
* survived: Evening: Sam's book in bedroom_2. Sam's pen/textbook on office desk. Plant pot 3 on office desk. Priya's plate on kitchen cupboard. Sam's plate on kitchen cupboard.
  * objects: ['book_sam', 'pen_sam', 'plate_priya', 'plate_sam']
* recorded reason: Merging duplicate notes about evening item locations.

### claim_store_told_if_it_was_right / hh_s123_t03 day 31 — claim_0092 into claim_0052, by the model — **CROSS-OBJECT**

* folded in: Priya's mug is on the bedroom_1 desk in the evening.
  * objects: ['mug_priya']
* survived: Priya's pencil case on bedroom_1 floor. Sketchbook on desk. Water bottle on nightstand (morning) or kitchen sink (afternoon).
  * objects: ['pencil_case_priya']
* recorded reason: Merging notes about Priya's desk items and water bottle.

### claim_store_told_if_it_was_right / hh_s151_t03 day 10 — claim_0030 into claim_0029, by the backstop rule — **shared**

* folded in: Felix's glass is in the kitchen cupboard. It was on the sink in the morning but moved to the cupboard by 22:59.
  * objects: ['glass_felix']
* survived: Felix's glass is not in the kitchen cupboard. It is likely in the bedroom or office.
  * objects: ['glass_felix']
* recorded reason: folded by the code, not by the model: the notes were over the line they were given, this claim had the worst record, and the two are claimed under the same routine

### claim_store_told_if_it_was_right / hh_s151_t03 day 15 — claim_0011 into claim_0053, by the backstop rule — **shared**

* folded in: Felix's water bottle is not in the kitchen. It is likely in the bedroom or office. Also: Felix's water bottle is in the kitchen dish rack. It was absent from the kitchen earlier in the day.
  * objects: ['water_bottle_felix']
* survived: Felix's water bottle is on the bedroom_1 nightstand.
  * objects: ['water_bottle_felix']
* recorded reason: folded by the code, not by the model: the notes were over the line they were given, this claim had the worst record, and the two are claimed under the same routine

### claim_store_told_if_it_was_right / hh_s151_t03 day 15 — claim_0019 into claim_0011, by the backstop rule — **shared**

* folded in: Felix's water bottle is in the kitchen dish rack. It was absent from the kitchen earlier in the day.
  * objects: ['water_bottle_felix']
* survived: Felix's water bottle is not in the kitchen. It is likely in the bedroom or office. Also: Felix's water bottle is in the kitchen dish rack. It was absent from the kitchen earlier in the day.
  * objects: ['water_bottle_felix']
* recorded reason: folded by the code, not by the model: the notes were over the line they were given, this claim had the worst record, and the two are claimed under the same routine

### claim_store_told_if_it_was_right / hh_s151_t03 day 18 — claim_0053 into claim_0051, by the backstop rule — **shared**

* folded in: Felix's water bottle is not in the kitchen during the day. In the evening, it is on the kitchen dish rack. Dana's water bottle is not in the kitchen; it is in bedroom_1 (nightstand).
  * objects: ['water_bottle_dana', 'water_bottle_felix']
* survived: Dana's water bottle is not in the kitchen. Felix's water bottle is not in the kitchen during the day, but on the kitchen sink in the evening.
  * objects: ['water_bottle_dana', 'water_bottle_felix']
* recorded reason: folded by the code, not by the model: the notes were over the line they were given, this claim had the worst record, and the two are claimed under the same routine

### claim_store_told_if_it_was_right / hh_s151_t03 day 23 — claim_0051 into claim_0010, by the backstop rule — **shared**

* folded in: Dana's water bottle is on the bedroom_1 nightstand. Felix's water bottle is not in the kitchen.
  * objects: ['water_bottle_dana', 'water_bottle_felix']
* survived: Dana's water bottle is on the bedroom_1 nightstand. Felix's water bottle is not in the kitchen. It is likely in the bathroom or bedroom_2.
  * objects: ['water_bottle_dana', 'water_bottle_felix']
* recorded reason: folded by the code, not by the model: the notes were over the line they were given, this claim had the worst record, and the two are claimed under the same routine

### claim_store_told_if_it_was_right / hh_s151_t03 day 27 — claim_0010 into claim_0018, by the backstop rule — **shared**

* folded in: Dana's water bottle is highly mobile. Last seen in kitchen dish rack [sighting_4069]. Not on entry floor today. Do not rely on static location.
  * objects: ['water_bottle_dana']
* survived: Dana's water bottle location is unknown. It is not in the kitchen or living room.
  * objects: ['water_bottle_dana']
* recorded reason: folded by the code, not by the model: the notes were over the line they were given, this claim had the worst record, and the two are claimed under the same routine

### claim_store_told_if_it_was_right / hh_s32_t03 day 13 — claim_0023 into claim_0007, by the model — **shared**

* folded in: Leo's water bottle is on the office desk during the day. It was present at 09:27, 10:22, 11:38, 16:18, and 17:02 on Day 8.
  * objects: ['water_bottle_leo']
* survived: Leo's water bottle is on the office desk during the day. It was seen there at 10:50, 11:50, 14:19, and 17:12 on Day 12. In the evening, it moves to the kitchen table.
  * objects: ['water_bottle_leo']
* recorded reason: Merged duplicate notes about Leo's water bottle daytime location. Both were correct and consistent.

### claim_store_told_if_it_was_right / hh_s32_t03 day 13 — claim_0069 into claim_0022, by the model — **shared**

* folded in: Leo's charger is on the office desk during the day. It was seen there at 09:05, 09:46, 10:39, and 15:56 on Day 11. [sighting_1584] [sighting_1645] [sighting_1653] [sighting_1693]
  * objects: ['charger_leo']
* survived: Leo's charger is on the office desk during the day. It was on the desk at 09:27, 10:22, 11:38, 16:18, and 17:02 on Day 8.
  * objects: ['charger_leo']
* recorded reason: Merged duplicate notes about Leo's charger location. Both were correct and consistent.

### claim_store_told_if_it_was_right / hh_s32_t03 day 13 — claim_0070 into claim_0020, by the model — **shared**

* folded in: Leo's headphones are on the office desk during the day. They were seen there at 09:05, 09:46, 10:39, and 15:56 on Day 11. [sighting_1585] [sighting_1646] [sighting_1654] [sighting_1694]
  * objects: ['headphones_leo']
* survived: Leo's headphones are on the office desk during the day. They were on the desk at 09:27, 10:22, 11:38, 16:18, and 17:02 on Day 8.
  * objects: ['headphones_leo']
* recorded reason: Merged duplicate notes about Leo's headphones location. Both were correct and consistent.

### claim_store_told_if_it_was_right / hh_s32_t03 day 13 — claim_0071 into claim_0021, by the model — **shared**

* folded in: Leo's laptop is on the office desk during the day. It was seen there at 09:05, 09:46, 10:39, and 15:56 on Day 11. [sighting_1586] [sighting_1647] [sighting_1655] [sighting_1695]
  * objects: ['laptop_leo']
* survived: Leo's laptop is on the office desk during the day. It was on the desk at 09:27, 10:22, 11:38, 16:18, and 17:02 on Day 8.
  * objects: ['laptop_leo']
* recorded reason: Merged duplicate notes about Leo's laptop location. Both were correct and consistent.

### claim_store_told_if_it_was_right / hh_s32_t03 day 13 — claim_0072 into claim_0017, by the model — **shared**

* folded in: Leo's mug is on the office desk during the day. It was seen there at 11:10, 13:31, and 17:27 on Day 9.
  * objects: ['mug_leo']
* survived: Leo's mug is on the office desk during the day. It was seen there at 09:46, 10:39, and 15:56 on Day 11. [sighting_1648] [sighting_1656] [sighting_1696]
  * objects: ['mug_leo']
* recorded reason: Merged duplicate notes about Leo's mug location. Both were correct and consistent.

### claim_store_told_if_it_was_right / hh_s32_t03 day 13 — claim_0073 into claim_0019, by the model — **shared**

* folded in: Leo's notebook is on the office desk during the day. It was seen there at 11:10, 13:31, and 17:27 on Day 9.
  * objects: ['notebook_leo']
* survived: Leo's notebook is on the office desk during the day. It was seen there at 09:05, 09:46, 10:39, and 15:56 on Day 11. [sighting_1587] [sighting_1649] [sighting_1657] [sighting_1697]
  * objects: ['notebook_leo']
* recorded reason: Merged duplicate notes about Leo's notebook location. Both were correct and consistent.

### claim_store_told_if_it_was_right / hh_s32_t03 day 13 — claim_0074 into claim_0018, by the model — **shared**

* folded in: Leo's pen is on the office desk during the day. It was seen there at 09:05, 09:46, 10:39, and 15:56 on Day 11. [sighting_1588] [sighting_1650] [sighting_1658] [sighting_1698]
  * objects: ['pen_leo']
* survived: Leo's pen is on the office desk during the day. It was on the desk at 09:27, 10:22, 11:38, 16:18, and 17:02 on Day 8.
  * objects: ['pen_leo']
* recorded reason: Merged duplicate notes about Leo's pen location. Both were correct and consistent.

### claim_store_told_if_it_was_right / hh_s32_t03 day 13 — claim_0077 into claim_0016, by the model — **unclassifiable**

* folded in: Plant pot 3 is on the office desk. It was seen there at 09:05, 09:46, 10:39, and 15:56 on Day 11. [sighting_1589] [sighting_1651] [sighting_1659] [sighting_1699]
  * objects: none recognised
* survived: Plant pot 3 is on the office desk. It was present at 09:27, 10:22, 11:38, 16:18, and 17:02 on Day 8.
  * objects: none recognised
* recorded reason: Merged duplicate notes about Plant pot 3 location. Both were correct and consistent.

### claim_store_told_if_it_was_right / hh_s32_t03 day 13 — claim_0078 into claim_0013, by the model — **unclassifiable**

* folded in: The first aid kit is in the bathroom medicine cabinet. It was seen there at 07:07 and 09:27 on Day 11. [sighting_1578] [sighting_1631]
  * objects: none recognised
* survived: The first aid kit is in the bathroom medicine cabinet. It was present at 08:05, 18:53, and 20:25 on Day 8.
  * objects: none recognised
* recorded reason: Merged duplicate notes about first aid kit location. Both were correct and consistent.

### claim_store_told_if_it_was_right / hh_s32_t03 day 13 — claim_0079 into claim_0014, by the model — **unclassifiable**

* folded in: The soap dispenser and toothbrush holder are on the bathroom sink. They were seen there at 07:07 and 09:27 on Day 11. [sighting_1579] [sighting_1580] [sighting_1632] [sighting_1633]
  * objects: none recognised
* survived: The soap dispenser and toothbrush holder are on the bathroom sink. They were present at 08:05, 18:53, and 20:25 on Day 8.
  * objects: none recognised
* recorded reason: Merged duplicate notes about bathroom sink items. Both were correct and consistent.

### claim_store_told_if_it_was_right / hh_s32_t03 day 13 — claim_0080 into claim_0015, by the model — **unclassifiable**

* folded in: The laundry basket is on the bathroom shelf. It was seen there at 07:07 and 09:27 on Day 11. [sighting_1574] [sighting_1626]
  * objects: none recognised
* survived: The laundry basket is on the bathroom shelf. It was present at 08:05, 18:53, and 20:25 on Day 8.
  * objects: none recognised
* recorded reason: Merged duplicate notes about laundry basket location. Both were correct and consistent.

### claim_store_told_if_it_was_right / hh_s32_t03 day 13 — claim_0081 into claim_0012, by the model — **shared**

* folded in: Aisha's towel is on the bathroom shelf. It was seen there at 07:25, 07:57, and 09:00 on Day 12. It moved from the rack to the shelf sometime after Day 9.
  * objects: ['towel_aisha']
* survived: Aisha's towel is on the bathroom shelf. It moved from the rack to the shelf between 07:07 and 09:27 on Day 11. [sighting_1581] [sighting_1630]
  * objects: ['towel_aisha']
* recorded reason: Merged duplicate notes about Aisha's towel location. Both were correct and consistent.

### claim_store_told_if_it_was_right / hh_s32_t03 day 13 — claim_0082 into claim_0011, by the model — **shared**

* folded in: Elena's towel is on the bathroom towel rack. It was seen there at 08:52 and 12:34 on Day 9.
  * objects: ['towel_elena']
* survived: Elena's towel is on the bathroom towel rack. It was seen there at 07:07 and 09:27 on Day 11. [sighting_1582] [sighting_1634]
  * objects: ['towel_elena']
* recorded reason: Merged duplicate notes about Elena's towel location. Both were correct and consistent.

### claim_store_told_if_it_was_right / hh_s32_t03 day 13 — claim_0083 into claim_0010, by the model — **shared**

* folded in: Leo's towel is on the bathroom towel rack. It was seen there at 08:52 and 12:34 on Day 9.
  * objects: ['towel_leo']
* survived: Leo's towel is on the bathroom towel rack. It was seen there at 07:07 and 09:27 on Day 11. [sighting_1583] [sighting_1635]
  * objects: ['towel_leo']
* recorded reason: Merged duplicate notes about Leo's towel location. Both were correct and consistent.

### claim_store_told_if_it_was_right / hh_s32_t03 day 13 — claim_0085 into claim_0084, by the model — **matcher limit**

* folded in: Elena's toiletry bag is on the bathroom shelf. It was seen there at 08:52 and 12:34 on Day 9.
  * objects: ['toiletry_bag_elena']
* survived: Elena's hair dryer and toiletry bag are on the bathroom shelf. They were seen there at 07:07 and 09:27 on Day 11. [sighting_1573] [sighting_1577] [sighting_1625] [sighting_1629]
  * objects: ['hair_dryer_elena']
* recorded reason: Merged duplicate notes about Elena's bathroom shelf items. Both were correct and consistent.

### claim_store_told_if_it_was_right / hh_s32_t03 day 13 — claim_0086 into claim_0003, by the model — **shared**

* folded in: Aisha's skincare is on the bathroom shelf. It was seen there at 08:52 and 12:34 on Day 9.
  * objects: ['skincare_aisha']
* survived: Aisha's skincare is on the bathroom shelf. It was seen there at 07:07 and 09:27 on Day 11. [sighting_1575] [sighting_1627]
  * objects: ['skincare_aisha']
* recorded reason: Merged duplicate notes about Aisha's skincare location. Both were correct and consistent.

### claim_store_told_if_it_was_right / hh_s32_t03 day 16 — claim_0057 into claim_0017, by the model — **shared**

* folded in: Leo's mug is on the kitchen sink in the morning. In the evening it moves to the living room coffee table.
  * objects: ['mug_leo']
* survived: Leo's mug is on the kitchen sink in the morning. In the evening it moves to the living room coffee table.
  * objects: ['mug_leo']
* recorded reason: Merged duplicate claims. Corrected morning location from 'sink' to 'counter' based on Day 16 sightings.

### claim_store_told_if_it_was_right / hh_s32_t03 day 19 — claim_0060 into claim_0065, by the backstop rule — **shared**

* folded in: The cutting board, kitchen knife, and glass_leo are on the kitchen sink. This was seen on Day 9. On Day 19, glass_leo was in bedroom_1.
  * objects: ['glass_leo']
* survived: Aisha's glass is on the kitchen table in the evening. The cutting board, kitchen knife, and glass_leo are on the kitchen sink in the evening. Note: glass_leo was seen on bedroom_1 nightstand on Day 18, suggesting it moves to the bedroom at
  * objects: ['glass_aisha', 'glass_leo']
* recorded reason: folded by the code, not by the model: the notes were over the line they were given, this claim had the worst record, and the two are claimed under the same routine

### claim_store_told_if_it_was_right / hh_s32_t03 day 19 — claim_0076 into claim_0022, by the backstop rule — **shared**

* folded in: Leo's charger is on the bedroom_1 bed. It is not on the office desk.
  * objects: ['charger_leo']
* survived: Leo's charger is on the bedroom_1 bed. It was seen there on Day 19. Previous claims about the floor or office desk are incorrect.
  * objects: ['charger_leo']
* recorded reason: folded by the code, not by the model: the notes were over the line they were given, this claim had the worst record, and the two are claimed under the same routine

### claim_store_told_if_it_was_right / hh_s32_t03 day 20 — claim_0065 into claim_0027, by the backstop rule — **shared**

* folded in: Aisha's glass is on the kitchen table. The cutting board is on the kitchen dish rack. The kitchen knife is on the kitchen cupboard. Leo's glass is on the bedroom_1 nightstand. Seen Day 20 at 19:44 [sighting_2920, 2915, 2912] and 18:39 [s
  * objects: ['glass_aisha', 'glass_leo']
* survived: Aisha's glass is on the kitchen table. Elena's glass is on the kitchen table in the evening. Both seen on Day 20 at 19:44 [sighting_2920, sighting_2921].
  * objects: ['glass_aisha', 'glass_elena']
* recorded reason: folded by the code, not by the model: the notes were over the line they were given, this claim had the worst record, and the two are claimed under the same routine

### claim_store_told_if_it_was_right / hh_s32_t03 day 22 — claim_0067 into claim_0007, by the model — **shared**

* folded in: Leo's water bottle is on the bedroom_1 nightstand.
  * objects: ['water_bottle_leo']
* survived: Leo's water bottle is on the bedroom_1 nightstand. Seen Day 21 [sighting_2981].
  * objects: ['water_bottle_leo']
* recorded reason: Merged duplicate notes about Leo's water bottle.

### claim_store_told_if_it_was_right / hh_s32_t03 day 22 — claim_0075 into claim_0004, by the model — **shared**

* folded in: Leo's water bottle is on the bedroom_1 nightstand. The snack bowl is on the kitchen cupboard.
  * objects: ['water_bottle_leo']
* survived: The snack bowl is on the kitchen sink. Leo's water bottle is on the bedroom_1 nightstand. Seen Day 21 [sighting_2965, 2981].
  * objects: ['water_bottle_leo']
* recorded reason: Merged notes to reduce count. Snack bowl location from Day 21, bottle from Day 22.

### claim_store_told_if_it_was_right / hh_s32_t03 day 23 — claim_0016 into claim_0068, by the backstop rule — **shared**

* folded in: Plant pot 3 is on the office desk. Elena's notebook is on the bedroom_2 desk. Seen Day 20 at 18:39 [sighting_2901, 2895].
  * objects: ['notebook_elena']
* survived: Leo's tablet is on the living room side table. Plant pot 3 is on the office desk. Elena's notebook is on the bedroom_2 desk. Seen Day 21 [sighting_2999]. Also: Plant pot 3 is on the office desk. Elena's notebook is on the bedroom_2 desk. Seen Day 20 at 18:39 [sighting_2901, 2895].
  * objects: ['notebook_elena', 'tablet_leo']
* recorded reason: folded by the code, not by the model: the notes were over the line they were given, this claim had the worst record, and the two are claimed under the same routine

### claim_store_told_if_it_was_right / hh_s32_t03 day 23 — claim_0022 into claim_0017, by the backstop rule — **shared**

* folded in: Leo's charger is on the bedroom_1 bed. Seen Day 21 [sighting_2977].
  * objects: ['charger_leo']
* survived: Leo's charger is on the bedroom_1 bed. His tablet is on the living room side table. His mug is on the living room coffee table.
  * objects: ['charger_leo']
* recorded reason: folded by the code, not by the model: the notes were over the line they were given, this claim had the worst record, and the two are claimed under the same routine

### claim_store_told_if_it_was_right / hh_s32_t03 day 23 — claim_0066 into claim_0006, by the backstop rule — **shared**

* folded in: Aisha's water bottle is on the kitchen dish rack. Seen Day 21 [sighting_2953].
  * objects: ['water_bottle_aisha']
* survived: Aisha's water bottle is on the kitchen table. Seen Day 23 [sighting_3217, 3249].
  * objects: ['water_bottle_aisha']
* recorded reason: folded by the code, not by the model: the notes were over the line they were given, this claim had the worst record, and the two are claimed under the same routine

### claim_store_told_if_it_was_right / hh_s32_t03 day 23 — claim_0068 into claim_0008, by the backstop rule — **shared**

* folded in: Leo's tablet is on the living room side table. Plant pot 3 is on the office desk. Elena's notebook is on the bedroom_2 desk. Seen Day 21 [sighting_2999]. Also: Plant pot 3 is on the office desk. Elena's notebook is on the bedroom_2 desk. Seen Day 20 at 18:39 [sighting_2901, 2895].
  * objects: ['notebook_elena', 'tablet_leo']
* survived: Leo's tablet is on the living room side table. The dog toy is on the living room floor. The picture frame, board game, Aisha's camera, and Elena's camera are on the living room bookshelf.
  * objects: ['camera_aisha', 'camera_elena', 'tablet_leo']
* recorded reason: folded by the code, not by the model: the notes were over the line they were given, this claim had the worst record, and the two are claimed under the same routine

### claim_store_told_if_it_was_right / hh_s32_t03 day 24 — claim_0006 into claim_0027, by the backstop rule — **shared**

* folded in: Aisha's water bottle is on the kitchen table. Elena's notebook is not in bedroom_2. It was on the desk_b2 on Day 22 but is missing on Day 23. Likely in bedroom_3 or office. Seen Day 23 [sighting_3217, 3249].
  * objects: ['notebook_elena', 'water_bottle_aisha']
* survived: Aisha's glass is on the kitchen cupboard. Elena's glass is on the kitchen sink. Aisha's water bottle is not seen in the kitchen. Seen Day 24 [sighting_3309, 3377].
  * objects: ['glass_aisha', 'glass_elena', 'water_bottle_aisha']
* recorded reason: folded by the code, not by the model: the notes were over the line they were given, this claim had the worst record, and the two are claimed under the same routine

### claim_store_told_if_it_was_right / hh_s32_t03 day 24 — claim_0025 into claim_0006, by the backstop rule — **shared**

* folded in: Elena's notebook is not in bedroom_2. It was on the desk_b2 on Day 22 but is missing on Day 23. Likely in bedroom_3 or office.
  * objects: ['notebook_elena']
* survived: Aisha's water bottle is on the kitchen table. Elena's notebook is not in bedroom_2. It was on the desk_b2 on Day 22 but is missing on Day 23. Likely in bedroom_3 or office. Seen Day 23 [sighting_3217, 3249].
  * objects: ['notebook_elena', 'water_bottle_aisha']
* recorded reason: folded by the code, not by the model: the notes were over the line they were given, this claim had the worst record, and the two are claimed under the same routine

### claim_store_told_if_it_was_right / hh_s32_t03 day 28 — claim_0027 into claim_0028, by the backstop rule — **shared**

* folded in: Aisha's glass is on the kitchen table in the evening. Aisha's water bottle is on the kitchen table in the evening. Elena's notebook is not in bedroom_2.
  * objects: ['glass_aisha', 'notebook_elena', 'water_bottle_aisha']
* survived: Aisha's water bottle is on the kitchen table in the evening. Elena's phone is not seen in the kitchen.
  * objects: ['phone_elena', 'water_bottle_aisha']
* recorded reason: folded by the code, not by the model: the notes were over the line they were given, this claim had the worst record, and the two are claimed under the same routine

### claim_store_told_if_it_was_right / hh_s48_t03 day 6 — claim_0010 into claim_0013, by the model — **shared**

* folded in: Marco's water bottle is on the dining table in the evening. It appeared in dining at 20:05.
  * objects: ['water_bottle_marco']
* survived: Marco's water bottle is on the dining table in the evening. It was not in the kitchen at 15:05 on Day 5, but appeared in dining at 19:45.
  * objects: ['water_bottle_marco']
* recorded reason: Merged claim_0010 into claim_0013 to reduce redundancy. Both described the same behavior. The new sighting at 20:18 confirms the location.
