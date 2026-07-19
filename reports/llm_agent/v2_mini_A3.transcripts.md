## Episode 0  [family / A3 / remote_control_1 / Δt=26h]

**PROMPT (what the model saw):**
```
You are a household robot's decision module. Answer location questions about objects, at the level of the exact spot: answers are 'room.receptacle' labels (e.g. kitchen.counter_1 = the first counter in the kitchen; a *_tucked label is the tucked-in position at that furniture). 'elsewhere' means the object is in no listed spot (taken out of the house, or put away out of sight). Residents move objects as they live their day: think about which household activities plausibly happened in the relevant time span — meals, work or school hours, tidying, evening wind-down, weekend rhythms — and how those activities move objects of this kind. You have a memory of past observations, possibly stale. Work step by step: (1) from the object's kind, when it was last seen, the current time, and the household activities likely to have occurred in between, estimate est_p_moved — the probability it is no longer at the remembered spot; (2) if est_p_moved is high enough that a wrong answer is likely, RESENSE (costs 1 of 5 remaining looks today, 10 questions today); otherwise ANSWER from memory; (3) fill 'answer' with your best guess either way and calibrate 'confidence'.

---

Household: a family home: two working parents, a teenage son, a toddler daughter

Your memory of the house:
- bowl_1: kitchen.counter_1 (last seen Monday 16:00)
- bowl_2: kitchen.counter_1 (last seen Monday 16:00)
- bowl_3: kitchen.counter_1 (last seen Monday 16:00)
- bowl_4: kitchen.counter_1 (last seen Monday 16:00)
- candle_1: bedroom_3.chest_of_drawers_1 (last seen Monday 16:00)
- chair_1: living_room.table_1 (last seen Monday 16:00)
- chair_2: living_room.table_1 (last seen Monday 16:00)
- chair_3: living_room.table_1 (last seen Monday 16:00)
- chair_4: living_room.table_1 (last seen Monday 16:00)
- david_keys: not in any room (away/put away) (last seen Monday 16:00)
- david_phone: not in any room (away/put away) (last seen Monday 16:00)
- david_wallet: not in any room (away/put away) (last seen Monday 16:00)
- fridge_1: fridge (last seen Monday 16:00)
- leo_headphones: not in any room (away/put away) (last seen Monday 16:00)
- leo_laptop: not in any room (away/put away) (last seen Monday 16:00)
- leo_phone: not in any room (away/put away) (last seen Monday 16:00)
- mia_backpack: not in any room (away/put away) (last seen Monday 16:00)
- newspaper_1: kitchen.counter_1 (last seen Monday 16:00)
- newspaper_2: living_room.table_1 (last seen Monday 16:00)
- potted_plant_1: living_room.corner (last seen Monday 16:00)
- potted_plant_2: living_room.corner (last seen Monday 16:00)
- potted_plant_3: living_room.corner (last seen Monday 16:00)
- potted_plant_4: living_room.corner (last seen Monday 16:00)
- potted_plant_5: living_room.corner (last seen Monday 16:00)
- potted_plant_6: living_room.corner (last seen Monday 16:00)
- remote_control_1: living_room.table_1 (last seen Monday 16:00)
- remote_control_2: living_room.table_1 (last seen Monday 16:00)
- sarah_keys: not in any room (away/put away) (last seen Monday 16:00)
- sarah_laptop: not in any room (away/put away) (last seen Monday 16:00)
- sarah_phone: not in any room (away/put away) (last seen Monday 16:00)
- sarah_wallet: not in any room (away/put away) (last seen Monday 16:00)
- stool_1: kitchen.counter_1 (last seen Monday 16:00)
- stool_2: kitchen.counter_1 (last seen Monday 16:00)
- stool_3: kitchen.counter_1 (last seen Monday 16:00)
- teapot_1: kitchen.counter_1 (last seen Monday 16:00)
- toy_1: living_room.table_1 (last seen Monday 16:00)
- toy_2: living_room.table_1 (last seen Monday 16:00)
- toy_3: living_room.table_1 (last seen Monday 16:00)
- toy_4: living_room.table_1 (last seen Monday 16:00)
- tv_1: tv (last seen Monday 16:00)
- vase_1: living_room.table_1 (last seen Monday 16:00)
- wardrobe_1: wardrobe (last seen Monday 16:00)

Current time: Tuesday 18:00

Question: where is remote_control_1 right now? Answer with one of the location labels, or 'elsewhere'.
```

**MODEL RESPONSE:**
- action: `resense`   answer: `living_room.table_1`   confidence: 0.34   est_p_moved: 0.78
- reason: A remote control is a high-use living room item and was last seen on the living room table yesterday afternoon. Over a full day in a family home, it is very likely to have been moved to the couch, TV area, or left elsewhere after evening use and tidying. The exact table spot is not reliable without 

**GROUND TRUTH:** true room = `living_room.table_1`  →  answer ✓ correct

---

## Episode 1  [family / A3 / teapot_1 / Δt=2h]

**PROMPT (what the model saw):**
```
You are a household robot's decision module. Answer location questions about objects, at the level of the exact spot: answers are 'room.receptacle' labels (e.g. kitchen.counter_1 = the first counter in the kitchen; a *_tucked label is the tucked-in position at that furniture). 'elsewhere' means the object is in no listed spot (taken out of the house, or put away out of sight). Residents move objects as they live their day: think about which household activities plausibly happened in the relevant time span — meals, work or school hours, tidying, evening wind-down, weekend rhythms — and how those activities move objects of this kind. You have a memory of past observations, possibly stale. Work step by step: (1) from the object's kind, when it was last seen, the current time, and the household activities likely to have occurred in between, estimate est_p_moved — the probability it is no longer at the remembered spot; (2) if est_p_moved is high enough that a wrong answer is likely, RESENSE (costs 1 of 5 remaining looks today, 10 questions today); otherwise ANSWER from memory; (3) fill 'answer' with your best guess either way and calibrate 'confidence'.

---

Household: a family home: two working parents, a teenage son, a toddler daughter

Your memory of the house:
- bowl_1: not in any room (away/put away) (last seen Monday 19:00)
- bowl_2: kitchen.counter_1 (last seen Monday 19:00)
- bowl_3: kitchen.counter_1 (last seen Monday 19:00)
- bowl_4: kitchen.counter_1 (last seen Monday 19:00)
- candle_1: bedroom_3.chest_of_drawers_1 (last seen Monday 19:00)
- chair_1: living_room.table_1 (last seen Monday 19:00)
- chair_2: living_room.table_1 (last seen Monday 19:00)
- chair_3: living_room.table_1 (last seen Monday 19:00)
- chair_4: living_room.table_1 (last seen Monday 19:00)
- david_keys: not in any room (away/put away) (last seen Monday 19:00)
- david_phone: not in any room (away/put away) (last seen Monday 19:00)
- david_wallet: not in any room (away/put away) (last seen Monday 19:00)
- fridge_1: fridge (last seen Monday 19:00)
- leo_headphones: not in any room (away/put away) (last seen Monday 19:00)
- leo_laptop: not in any room (away/put away) (last seen Monday 19:00)
- leo_phone: not in any room (away/put away) (last seen Monday 19:00)
- mia_backpack: not in any room (away/put away) (last seen Monday 19:00)
- newspaper_1: kitchen.counter_1 (last seen Monday 19:00)
- newspaper_2: living_room.table_1 (last seen Monday 19:00)
- potted_plant_1: living_room.corner (last seen Monday 19:00)
- potted_plant_2: living_room.corner (last seen Monday 19:00)
- potted_plant_3: living_room.corner (last seen Monday 19:00)
- potted_plant_4: living_room.corner (last seen Monday 19:00)
- potted_plant_5: living_room.corner (last seen Monday 19:00)
- potted_plant_6: living_room.corner (last seen Monday 19:00)
- remote_control_1: living_room.table_1 (last seen Monday 19:00)
- remote_control_2: living_room.table_1 (last seen Monday 19:00)
- sarah_keys: not in any room (away/put away) (last seen Monday 19:00)
- sarah_laptop: not in any room (away/put away) (last seen Monday 19:00)
- sarah_phone: not in any room (away/put away) (last seen Monday 19:00)
- sarah_wallet: not in any room (away/put away) (last seen Monday 19:00)
- stool_1: kitchen.counter_1 (last seen Monday 19:00)
- stool_2: kitchen.counter_1 (last seen Monday 19:00)
- stool_3: kitchen.counter_1 (last seen Monday 19:00)
- teapot_1: kitchen.counter_1 (last seen Monday 19:00)
- toy_1: living_room.table_1 (last seen Monday 19:00)
- toy_2: living_room.table_1 (last seen Monday 19:00)
- toy_3: living_room.table_1 (last seen Monday 19:00)
- toy_4: living_room.table_1 (last seen Monday 19:00)
- tv_1: tv (last seen Monday 19:00)
- vase_1: living_room.table_1 (last seen Monday 19:00)
- wardrobe_1: wardrobe (last seen Monday 19:00)

Current time: Monday 21:00

Question: where is teapot_1 right now? Answer with one of the location labels, or 'elsewhere'.
```

**MODEL RESPONSE:**
- action: `answer`   answer: `kitchen.counter_1`   confidence: 0.86   est_p_moved: 0.18
- reason: Teapot was last seen on the kitchen counter during dinner time. Two hours later on a Monday evening, it is still very likely to remain in the kitchen after cleanup or tea/coffee use, and teapots are not commonly moved far from the counter. No strong reason to suspect relocation.

**GROUND TRUTH:** true room = `kitchen.counter_1`  →  answer ✓ correct

---

## Episode 2  [family / A3 / toy_4 / Δt=5h]

**PROMPT (what the model saw):**
```
You are a household robot's decision module. Answer location questions about objects, at the level of the exact spot: answers are 'room.receptacle' labels (e.g. kitchen.counter_1 = the first counter in the kitchen; a *_tucked label is the tucked-in position at that furniture). 'elsewhere' means the object is in no listed spot (taken out of the house, or put away out of sight). Residents move objects as they live their day: think about which household activities plausibly happened in the relevant time span — meals, work or school hours, tidying, evening wind-down, weekend rhythms — and how those activities move objects of this kind. You have a memory of past observations, possibly stale. Work step by step: (1) from the object's kind, when it was last seen, the current time, and the household activities likely to have occurred in between, estimate est_p_moved — the probability it is no longer at the remembered spot; (2) if est_p_moved is high enough that a wrong answer is likely, RESENSE (costs 1 of 5 remaining looks today, 10 questions today); otherwise ANSWER from memory; (3) fill 'answer' with your best guess either way and calibrate 'confidence'.

---

Household: a family home: two working parents, a teenage son, a toddler daughter

Your memory of the house:
- bowl_1: kitchen.counter_1 (last seen Monday 14:16)
- bowl_2: kitchen.counter_1 (last seen Monday 14:16)
- bowl_3: kitchen.counter_1 (last seen Monday 14:16)
- bowl_4: kitchen.counter_1 (last seen Monday 14:16)
- candle_1: bedroom_3.chest_of_drawers_1 (last seen Monday 14:16)
- chair_1: living_room.table_1 (last seen Monday 14:16)
- chair_2: living_room.table_1 (last seen Monday 14:16)
- chair_3: living_room.table_1 (last seen Monday 14:16)
- chair_4: living_room.table_1 (last seen Monday 14:16)
- david_keys: not in any room (away/put away) (last seen Monday 14:16)
- david_phone: not in any room (away/put away) (last seen Monday 14:16)
- david_wallet: not in any room (away/put away) (last seen Monday 14:16)
- fridge_1: fridge (last seen Monday 14:16)
- leo_headphones: not in any room (away/put away) (last seen Monday 14:16)
- leo_laptop: not in any room (away/put away) (last seen Monday 14:16)
- leo_phone: not in any room (away/put away) (last seen Monday 14:16)
- mia_backpack: not in any room (away/put away) (last seen Monday 14:16)
- newspaper_1: kitchen.counter_1 (last seen Monday 14:16)
- newspaper_2: living_room.table_1 (last seen Monday 14:16)
- potted_plant_1: living_room.corner (last seen Monday 14:16)
- potted_plant_2: living_room.corner (last seen Monday 14:16)
- potted_plant_3: living_room.corner (last seen Monday 14:16)
- potted_plant_4: living_room.corner (last seen Monday 14:16)
- potted_plant_5: living_room.corner (last seen Monday 14:16)
- potted_plant_6: living_room.corner (last seen Monday 14:16)
- remote_control_1: living_room.table_1 (last seen Monday 14:16)
- remote_control_2: living_room.table_1 (last seen Monday 14:16)
- sarah_keys: not in any room (away/put away) (last seen Monday 14:16)
- sarah_laptop: not in any room (away/put away) (last seen Monday 14:16)
- sarah_phone: not in any room (away/put away) (last seen Monday 14:16)
- sarah_wallet: not in any room (away/put away) (last seen Monday 14:16)
- stool_1: kitchen.counter_1 (last seen Monday 14:16)
- stool_2: kitchen.counter_1 (last seen Monday 14:16)
- stool_3: kitchen.counter_1 (last seen Monday 14:16)
- teapot_1: kitchen.counter_1 (last seen Monday 14:16)
- toy_1: living_room.table_1 (last seen Monday 14:16)
- toy_2: living_room.table_1 (last seen Monday 14:16)
- toy_3: living_room.table_1 (last seen Monday 14:16)
- toy_4: not in any room (away/put away) (last seen Monday 14:16)
- tv_1: tv (last seen Monday 14:16)
- vase_1: living_room.table_1 (last seen Monday 14:16)
- wardrobe_1: wardrobe (last seen Monday 14:16)

Current time: Monday 20:06

Question: where is toy_4 right now? Answer with one of the location labels, or 'elsewhere'.
```

**MODEL RESPONSE:**
- action: `answer`   answer: `elsewhere`   confidence: 0.78   est_p_moved: 0.25
- reason: toy_4 was last seen already put away/out of any room at Monday 14:16. Over ~6 hours, a toy is likely to have been brought into the living room for play by the toddler or tidied back out of sight, but since it was already not in a listed spot and there is no stronger evidence of a new location, the m

**GROUND TRUTH:** true room = `living_room.table_1`  →  answer ✗ WRONG  (object HAD moved since snapshot)

---

## Episode 3  [family / A3 / toy_3 / Δt=5h]

**PROMPT (what the model saw):**
```
You are a household robot's decision module. Answer location questions about objects, at the level of the exact spot: answers are 'room.receptacle' labels (e.g. kitchen.counter_1 = the first counter in the kitchen; a *_tucked label is the tucked-in position at that furniture). 'elsewhere' means the object is in no listed spot (taken out of the house, or put away out of sight). Residents move objects as they live their day: think about which household activities plausibly happened in the relevant time span — meals, work or school hours, tidying, evening wind-down, weekend rhythms — and how those activities move objects of this kind. You have a memory of past observations, possibly stale. Work step by step: (1) from the object's kind, when it was last seen, the current time, and the household activities likely to have occurred in between, estimate est_p_moved — the probability it is no longer at the remembered spot; (2) if est_p_moved is high enough that a wrong answer is likely, RESENSE (costs 1 of 5 remaining looks today, 10 questions today); otherwise ANSWER from memory; (3) fill 'answer' with your best guess either way and calibrate 'confidence'.

---

Household: a family home: two working parents, a teenage son, a toddler daughter

Your memory of the house:
- bowl_1: kitchen.counter_1 (last seen Monday 08:33)
- bowl_2: kitchen.counter_1 (last seen Monday 08:33)
- bowl_3: kitchen.counter_1 (last seen Monday 08:33)
- bowl_4: kitchen.counter_1 (last seen Monday 08:33)
- candle_1: living_room.table_1 (last seen Monday 08:33)
- chair_1: living_room.table_1 (last seen Monday 08:33)
- chair_2: living_room.table_1 (last seen Monday 08:33)
- chair_3: living_room.table_1 (last seen Monday 08:33)
- chair_4: living_room.table_1 (last seen Monday 08:33)
- david_keys: not in any room (away/put away) (last seen Monday 08:33)
- david_phone: not in any room (away/put away) (last seen Monday 08:33)
- david_wallet: not in any room (away/put away) (last seen Monday 08:33)
- fridge_1: fridge (last seen Monday 08:33)
- leo_headphones: not in any room (away/put away) (last seen Monday 08:33)
- leo_laptop: not in any room (away/put away) (last seen Monday 08:33)
- leo_phone: not in any room (away/put away) (last seen Monday 08:33)
- mia_backpack: not in any room (away/put away) (last seen Monday 08:33)
- newspaper_1: kitchen.counter_1 (last seen Monday 08:33)
- newspaper_2: living_room.table_1 (last seen Monday 08:33)
- potted_plant_1: living_room.corner (last seen Monday 08:33)
- potted_plant_2: living_room.corner (last seen Monday 08:33)
- potted_plant_3: living_room.corner (last seen Monday 08:33)
- potted_plant_4: living_room.corner (last seen Monday 08:33)
- potted_plant_5: living_room.corner (last seen Monday 08:33)
- potted_plant_6: living_room.corner (last seen Monday 08:33)
- remote_control_1: living_room.table_1 (last seen Monday 08:33)
- remote_control_2: living_room.table_1 (last seen Monday 08:33)
- sarah_keys: not in any room (away/put away) (last seen Monday 08:33)
- sarah_laptop: not in any room (away/put away) (last seen Monday 08:33)
- sarah_phone: not in any room (away/put away) (last seen Monday 08:33)
- sarah_wallet: not in any room (away/put away) (last seen Monday 08:33)
- stool_1: kitchen.counter_1 (last seen Monday 08:33)
- stool_2: kitchen.counter_1 (last seen Monday 08:33)
- stool_3: kitchen.counter_1 (last seen Monday 08:33)
- teapot_1: kitchen.counter_1 (last seen Monday 08:33)
- toy_1: living_room.table_1 (last seen Monday 08:33)
- toy_2: living_room.table_1 (last seen Monday 08:33)
- toy_3: not in any room (away/put away) (last seen Monday 08:33)
- toy_4: not in any room (away/put away) (last seen Monday 08:33)
- tv_1: tv (last seen Monday 08:33)
- vase_1: living_room.table_1 (last seen Monday 08:33)
- wardrobe_1: wardrobe (last seen Monday 08:33)

Current time: Monday 14:04

Question: where is toy_3 right now? Answer with one of the location labels, or 'elsewhere'.
```

**MODEL RESPONSE:**
- action: `answer`   answer: `elsewhere`   confidence: 0.58   est_p_moved: 0.62
- reason: toy_3 was last seen put away/not in any room at 08:33. By 14:04 on a Monday, a toddler toy is fairly likely to have been brought out into the living room or another common area during daytime play, but it could also still be put away. Since its last state was already away/put away, the chance it has

**GROUND TRUTH:** true room = `living_room.table_1`  →  answer ✗ WRONG  (object HAD moved since snapshot)

---

## Episode 4  [family / A3 / leo_headphones / Δt=2h]

**PROMPT (what the model saw):**
```
You are a household robot's decision module. Answer location questions about objects, at the level of the exact spot: answers are 'room.receptacle' labels (e.g. kitchen.counter_1 = the first counter in the kitchen; a *_tucked label is the tucked-in position at that furniture). 'elsewhere' means the object is in no listed spot (taken out of the house, or put away out of sight). Residents move objects as they live their day: think about which household activities plausibly happened in the relevant time span — meals, work or school hours, tidying, evening wind-down, weekend rhythms — and how those activities move objects of this kind. You have a memory of past observations, possibly stale. Work step by step: (1) from the object's kind, when it was last seen, the current time, and the household activities likely to have occurred in between, estimate est_p_moved — the probability it is no longer at the remembered spot; (2) if est_p_moved is high enough that a wrong answer is likely, RESENSE (costs 1 of 5 remaining looks today, 10 questions today); otherwise ANSWER from memory; (3) fill 'answer' with your best guess either way and calibrate 'confidence'.

---

Household: a family home: two working parents, a teenage son, a toddler daughter

Your memory of the house:
- bowl_1: kitchen.counter_1 (last seen Tuesday 16:00)
- bowl_2: kitchen.counter_1 (last seen Tuesday 16:00)
- bowl_3: kitchen.counter_1 (last seen Tuesday 16:00)
- bowl_4: kitchen.counter_1 (last seen Tuesday 16:00)
- candle_1: living_room.table_1 (last seen Tuesday 16:00)
- chair_1: living_room.tv_1 (last seen Tuesday 16:00)
- chair_2: living_room.table_1 (last seen Tuesday 16:00)
- chair_3: living_room.table_1 (last seen Tuesday 16:00)
- chair_4: living_room.table_1 (last seen Tuesday 16:00)
- david_keys: not in any room (away/put away) (last seen Tuesday 16:00)
- david_phone: not in any room (away/put away) (last seen Tuesday 16:00)
- david_wallet: not in any room (away/put away) (last seen Tuesday 16:00)
- fridge_1: fridge (last seen Tuesday 16:00)
- leo_headphones: not in any room (away/put away) (last seen Tuesday 16:00)
- leo_laptop: not in any room (away/put away) (last seen Tuesday 16:00)
- leo_phone: kitchen.counter_1 (last seen Tuesday 16:00)
- mia_backpack: not in any room (away/put away) (last seen Tuesday 16:00)
- newspaper_1: bedroom_3.chest_of_drawers_1 (last seen Tuesday 16:00)
- newspaper_2: living_room.table_1 (last seen Tuesday 16:00)
- potted_plant_1: living_room.corner (last seen Tuesday 16:00)
- potted_plant_2: living_room.corner (last seen Tuesday 16:00)
- potted_plant_3: living_room.corner (last seen Tuesday 16:00)
- potted_plant_4: living_room.corner (last seen Tuesday 16:00)
- potted_plant_5: living_room.corner (last seen Tuesday 16:00)
- potted_plant_6: living_room.corner (last seen Tuesday 16:00)
- remote_control_1: living_room.table_1 (last seen Tuesday 16:00)
- remote_control_2: living_room.table_1 (last seen Tuesday 16:00)
- sarah_keys: not in any room (away/put away) (last seen Tuesday 16:00)
- sarah_laptop: not in any room (away/put away) (last seen Tuesday 16:00)
- sarah_phone: bedroom_1.chest_of_drawers_1 (last seen Tuesday 16:00)
- sarah_wallet: not in any room (away/put away) (last seen Tuesday 16:00)
- stool_1: kitchen.counter_1 (last seen Tuesday 16:00)
- stool_2: kitchen.counter_1 (last seen Tuesday 16:00)
- stool_3: kitchen.counter_1 (last seen Tuesday 16:00)
- teapot_1: kitchen.counter_1 (last seen Tuesday 16:00)
- toy_1: living_room.table_1 (last seen Tuesday 16:00)
- toy_2: living_room.table_1 (last seen Tuesday 16:00)
- toy_3: not in any room (away/put away) (last seen Tuesday 16:00)
- toy_4: not in any room (away/put away) (last seen Tuesday 16:00)
- tv_1: tv (last seen Tuesday 16:00)
- vase_1: living_room.table_1 (last seen Tuesday 16:00)
- wardrobe_1: wardrobe (last seen Tuesday 16:00)

Current time: Tuesday 18:00

Question: where is leo_headphones right now? Answer with one of the location labels, or 'elsewhere'.
```

**MODEL RESPONSE:**
- action: `answer`   answer: `elsewhere`   confidence: 0.65   est_p_moved: 0.35
- reason: Leo’s headphones were last seen put away/out of any room at Tuesday 16:00. Over just 2 hours in a family home, headphones are somewhat likely to be taken out for homework, gaming, or music, but they also often stay put when not in use. Since the last known state is already away/put away, the chance,

**GROUND TRUTH:** true room = `elsewhere`  →  answer ✓ correct

---

## Episode 5  [family / A3 / newspaper_1 / Δt=8h]

**PROMPT (what the model saw):**
```
You are a household robot's decision module. Answer location questions about objects, at the level of the exact spot: answers are 'room.receptacle' labels (e.g. kitchen.counter_1 = the first counter in the kitchen; a *_tucked label is the tucked-in position at that furniture). 'elsewhere' means the object is in no listed spot (taken out of the house, or put away out of sight). Residents move objects as they live their day: think about which household activities plausibly happened in the relevant time span — meals, work or school hours, tidying, evening wind-down, weekend rhythms — and how those activities move objects of this kind. You have a memory of past observations, possibly stale. Work step by step: (1) from the object's kind, when it was last seen, the current time, and the household activities likely to have occurred in between, estimate est_p_moved — the probability it is no longer at the remembered spot; (2) if est_p_moved is high enough that a wrong answer is likely, RESENSE (costs 1 of 5 remaining looks today, 10 questions today); otherwise ANSWER from memory; (3) fill 'answer' with your best guess either way and calibrate 'confidence'.

---

Household: a family home: two working parents, a teenage son, a toddler daughter

Your memory of the house:
- bowl_1: kitchen.counter_1 (last seen Tuesday 13:00)
- bowl_2: kitchen.counter_1 (last seen Tuesday 13:00)
- bowl_3: kitchen.counter_1 (last seen Tuesday 13:00)
- bowl_4: kitchen.counter_1 (last seen Tuesday 13:00)
- candle_1: living_room.table_1 (last seen Tuesday 13:00)
- chair_1: living_room.tv_1 (last seen Tuesday 13:00)
- chair_2: living_room.table_1 (last seen Tuesday 13:00)
- chair_3: living_room.table_1 (last seen Tuesday 13:00)
- chair_4: living_room.table_1 (last seen Tuesday 13:00)
- david_keys: not in any room (away/put away) (last seen Tuesday 13:00)
- david_phone: not in any room (away/put away) (last seen Tuesday 13:00)
- david_wallet: not in any room (away/put away) (last seen Tuesday 13:00)
- fridge_1: fridge (last seen Tuesday 13:00)
- leo_headphones: not in any room (away/put away) (last seen Tuesday 13:00)
- leo_laptop: not in any room (away/put away) (last seen Tuesday 13:00)
- leo_phone: kitchen.counter_1 (last seen Tuesday 13:00)
- mia_backpack: not in any room (away/put away) (last seen Tuesday 13:00)
- newspaper_1: bedroom_3.chest_of_drawers_1 (last seen Tuesday 13:00)
- newspaper_2: living_room.table_1 (last seen Tuesday 13:00)
- potted_plant_1: living_room.corner (last seen Tuesday 13:00)
- potted_plant_2: living_room.corner (last seen Tuesday 13:00)
- potted_plant_3: living_room.corner (last seen Tuesday 13:00)
- potted_plant_4: living_room.corner (last seen Tuesday 13:00)
- potted_plant_5: living_room.corner (last seen Tuesday 13:00)
- potted_plant_6: living_room.corner (last seen Tuesday 13:00)
- remote_control_1: living_room.table_1 (last seen Tuesday 13:00)
- remote_control_2: living_room.table_1 (last seen Tuesday 13:00)
- sarah_keys: not in any room (away/put away) (last seen Tuesday 13:00)
- sarah_laptop: not in any room (away/put away) (last seen Tuesday 13:00)
- sarah_phone: bedroom_1.chest_of_drawers_1 (last seen Tuesday 13:00)
- sarah_wallet: not in any room (away/put away) (last seen Tuesday 13:00)
- stool_1: kitchen.counter_1 (last seen Tuesday 13:00)
- stool_2: kitchen.counter_1 (last seen Tuesday 13:00)
- stool_3: kitchen.counter_1 (last seen Tuesday 13:00)
- teapot_1: kitchen.counter_1 (last seen Tuesday 13:00)
- toy_1: living_room.table_1 (last seen Tuesday 13:00)
- toy_2: living_room.table_1 (last seen Tuesday 13:00)
- toy_3: not in any room (away/put away) (last seen Tuesday 13:00)
- toy_4: not in any room (away/put away) (last seen Tuesday 13:00)
- tv_1: tv (last seen Tuesday 13:00)
- vase_1: living_room.table_1 (last seen Tuesday 13:00)
- wardrobe_1: wardrobe (last seen Tuesday 13:00)

Current time: Tuesday 21:00

Question: where is newspaper_1 right now? Answer with one of the location labels, or 'elsewhere'.
```

**MODEL RESPONSE:**
- action: `answer`   answer: `bedroom_3.chest_of_drawers_1`   confidence: 0.65   est_p_moved: 0.35
- reason: newspaper_1 was last seen on bedroom_3.chest_of_drawers_1 at Tuesday 13:00. By Tuesday 21:00, a newspaper is somewhat likely to have been read and left elsewhere, but it is also plausible it stayed put in a bedroom drawer/chest area during the day. Since this is a relatively low-mobility item and no

**GROUND TRUTH:** true room = `bedroom_3.chest_of_drawers_1`  →  answer ✓ correct

---

## Episode 6  [family / A3 / chair_1 / Δt=6h]

**PROMPT (what the model saw):**
```
You are a household robot's decision module. Answer location questions about objects, at the level of the exact spot: answers are 'room.receptacle' labels (e.g. kitchen.counter_1 = the first counter in the kitchen; a *_tucked label is the tucked-in position at that furniture). 'elsewhere' means the object is in no listed spot (taken out of the house, or put away out of sight). Residents move objects as they live their day: think about which household activities plausibly happened in the relevant time span — meals, work or school hours, tidying, evening wind-down, weekend rhythms — and how those activities move objects of this kind. You have a memory of past observations, possibly stale. Work step by step: (1) from the object's kind, when it was last seen, the current time, and the household activities likely to have occurred in between, estimate est_p_moved — the probability it is no longer at the remembered spot; (2) if est_p_moved is high enough that a wrong answer is likely, RESENSE (costs 1 of 5 remaining looks today, 10 questions today); otherwise ANSWER from memory; (3) fill 'answer' with your best guess either way and calibrate 'confidence'.

---

Household: a family home: two working parents, a teenage son, a toddler daughter

Your memory of the house:
- bowl_1: kitchen.counter_1 (last seen Tuesday 10:02)
- bowl_2: kitchen.counter_1 (last seen Tuesday 10:02)
- bowl_3: kitchen.counter_1 (last seen Tuesday 10:02)
- bowl_4: kitchen.counter_1 (last seen Tuesday 10:02)
- candle_1: living_room.table_1 (last seen Tuesday 10:02)
- chair_1: living_room.table_1 (last seen Tuesday 10:02)
- chair_2: living_room.table_1 (last seen Tuesday 10:02)
- chair_3: living_room.table_1 (last seen Tuesday 10:02)
- chair_4: living_room.table_1 (last seen Tuesday 10:02)
- david_keys: not in any room (away/put away) (last seen Tuesday 10:02)
- david_phone: not in any room (away/put away) (last seen Tuesday 10:02)
- david_wallet: not in any room (away/put away) (last seen Tuesday 10:02)
- fridge_1: fridge (last seen Tuesday 10:02)
- leo_headphones: not in any room (away/put away) (last seen Tuesday 10:02)
- leo_laptop: not in any room (away/put away) (last seen Tuesday 10:02)
- leo_phone: kitchen.counter_1 (last seen Tuesday 10:02)
- mia_backpack: not in any room (away/put away) (last seen Tuesday 10:02)
- newspaper_1: kitchen.counter_1 (last seen Tuesday 10:02)
- newspaper_2: living_room.table_1 (last seen Tuesday 10:02)
- potted_plant_1: living_room.corner (last seen Tuesday 10:02)
- potted_plant_2: living_room.corner (last seen Tuesday 10:02)
- potted_plant_3: living_room.corner (last seen Tuesday 10:02)
- potted_plant_4: living_room.corner (last seen Tuesday 10:02)
- potted_plant_5: living_room.corner (last seen Tuesday 10:02)
- potted_plant_6: living_room.corner (last seen Tuesday 10:02)
- remote_control_1: living_room.table_1 (last seen Tuesday 10:02)
- remote_control_2: living_room.table_1 (last seen Tuesday 10:02)
- sarah_keys: not in any room (away/put away) (last seen Tuesday 10:02)
- sarah_laptop: not in any room (away/put away) (last seen Tuesday 10:02)
- sarah_phone: not in any room (away/put away) (last seen Tuesday 10:02)
- sarah_wallet: not in any room (away/put away) (last seen Tuesday 10:02)
- stool_1: kitchen.counter_1 (last seen Tuesday 10:02)
- stool_2: kitchen.counter_1 (last seen Tuesday 10:02)
- stool_3: kitchen.counter_1 (last seen Tuesday 10:02)
- teapot_1: kitchen.counter_1 (last seen Tuesday 10:02)
- toy_1: living_room.table_1 (last seen Tuesday 10:02)
- toy_2: living_room.table_1 (last seen Tuesday 10:02)
- toy_3: not in any room (away/put away) (last seen Tuesday 10:02)
- toy_4: not in any room (away/put away) (last seen Tuesday 10:02)
- tv_1: tv (last seen Tuesday 10:02)
- vase_1: living_room.table_1 (last seen Tuesday 10:02)
- wardrobe_1: wardrobe (last seen Tuesday 10:02)

Current time: Tuesday 16:17

Question: where is chair_1 right now? Answer with one of the location labels, or 'elsewhere'.
```

**MODEL RESPONSE:**
- action: `answer`   answer: `living_room.table_1`   confidence: 0.58   est_p_moved: 0.62
- reason: chair_1 was last seen on the living room table in the morning. By late afternoon in a family home, dining/living chairs are often still left around the table unless tidied, but they are also commonly moved for meals, cleaning, or kids' play. Since this is a movable furniture item and several hours (

**GROUND TRUTH:** true room = `living_room.tv_1`  →  answer ✗ WRONG  (object HAD moved since snapshot)

---

## Episode 7  [family / A3 / sarah_phone / Δt=3h]

**PROMPT (what the model saw):**
```
You are a household robot's decision module. Answer location questions about objects, at the level of the exact spot: answers are 'room.receptacle' labels (e.g. kitchen.counter_1 = the first counter in the kitchen; a *_tucked label is the tucked-in position at that furniture). 'elsewhere' means the object is in no listed spot (taken out of the house, or put away out of sight). Residents move objects as they live their day: think about which household activities plausibly happened in the relevant time span — meals, work or school hours, tidying, evening wind-down, weekend rhythms — and how those activities move objects of this kind. You have a memory of past observations, possibly stale. Work step by step: (1) from the object's kind, when it was last seen, the current time, and the household activities likely to have occurred in between, estimate est_p_moved — the probability it is no longer at the remembered spot; (2) if est_p_moved is high enough that a wrong answer is likely, RESENSE (costs 1 of 5 remaining looks today, 10 questions today); otherwise ANSWER from memory; (3) fill 'answer' with your best guess either way and calibrate 'confidence'.

---

Household: a family home: two working parents, a teenage son, a toddler daughter

Your memory of the house:
- bowl_1: kitchen.counter_1 (last seen Tuesday 10:14)
- bowl_2: kitchen.counter_1 (last seen Tuesday 10:14)
- bowl_3: kitchen.counter_1 (last seen Tuesday 10:14)
- bowl_4: kitchen.counter_1 (last seen Tuesday 10:14)
- candle_1: living_room.table_1 (last seen Tuesday 10:14)
- chair_1: living_room.table_1 (last seen Tuesday 10:14)
- chair_2: living_room.table_1 (last seen Tuesday 10:14)
- chair_3: living_room.table_1 (last seen Tuesday 10:14)
- chair_4: living_room.table_1 (last seen Tuesday 10:14)
- david_keys: not in any room (away/put away) (last seen Tuesday 10:14)
- david_phone: not in any room (away/put away) (last seen Tuesday 10:14)
- david_wallet: not in any room (away/put away) (last seen Tuesday 10:14)
- fridge_1: fridge (last seen Tuesday 10:14)
- leo_headphones: not in any room (away/put away) (last seen Tuesday 10:14)
- leo_laptop: not in any room (away/put away) (last seen Tuesday 10:14)
- leo_phone: kitchen.counter_1 (last seen Tuesday 10:14)
- mia_backpack: not in any room (away/put away) (last seen Tuesday 10:14)
- newspaper_1: kitchen.counter_1 (last seen Tuesday 10:14)
- newspaper_2: living_room.table_1 (last seen Tuesday 10:14)
- potted_plant_1: living_room.corner (last seen Tuesday 10:14)
- potted_plant_2: living_room.corner (last seen Tuesday 10:14)
- potted_plant_3: living_room.corner (last seen Tuesday 10:14)
- potted_plant_4: living_room.corner (last seen Tuesday 10:14)
- potted_plant_5: living_room.corner (last seen Tuesday 10:14)
- potted_plant_6: living_room.corner (last seen Tuesday 10:14)
- remote_control_1: living_room.table_1 (last seen Tuesday 10:14)
- remote_control_2: living_room.table_1 (last seen Tuesday 10:14)
- sarah_keys: not in any room (away/put away) (last seen Tuesday 10:14)
- sarah_laptop: not in any room (away/put away) (last seen Tuesday 10:14)
- sarah_phone: not in any room (away/put away) (last seen Tuesday 10:14)
- sarah_wallet: not in any room (away/put away) (last seen Tuesday 10:14)
- stool_1: kitchen.counter_1 (last seen Tuesday 10:14)
- stool_2: kitchen.counter_1 (last seen Tuesday 10:14)
- stool_3: kitchen.counter_1 (last seen Tuesday 10:14)
- teapot_1: kitchen.counter_1 (last seen Tuesday 10:14)
- toy_1: living_room.table_1 (last seen Tuesday 10:14)
- toy_2: living_room.table_1 (last seen Tuesday 10:14)
- toy_3: not in any room (away/put away) (last seen Tuesday 10:14)
- toy_4: not in any room (away/put away) (last seen Tuesday 10:14)
- tv_1: tv (last seen Tuesday 10:14)
- vase_1: living_room.table_1 (last seen Tuesday 10:14)
- wardrobe_1: wardrobe (last seen Tuesday 10:14)

Current time: Tuesday 13:59

Question: where is sarah_phone right now? Answer with one of the location labels, or 'elsewhere'.
```

**MODEL RESPONSE:**
- action: `resense`   answer: `elsewhere`   confidence: 0.34   est_p_moved: 0.72
- reason: Sarah_phone was last seen put away/not in any room at 10:14. By 13:59 on a weekday, a working parent is likely to have taken her phone out for commuting, work calls, or errands, so the chance it has moved from the remembered hidden state is fairly high. Since the exact current spot is uncertain and,

**GROUND TRUTH:** true room = `bedroom_1.chest_of_drawers_1`  →  answer ✗ WRONG  (object HAD moved since snapshot)

---
