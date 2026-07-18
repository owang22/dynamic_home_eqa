## Episode 0  [family / A3 / chair_4 / Δt=1h]

**PROMPT (what the model saw):**
```
You are a household robot's decision module. Answer location questions about objects in the house. 'elsewhere' means the object is not in any room (taken out of the house, or put away out of sight). You have a memory of past observations, possibly stale. Work step by step: (1) from the object's class and how long ago it was last seen, estimate est_p_moved — the probability it is no longer where your memory says (frequently-handled items drift within hours; furniture rarely moves); (2) decide: if est_p_moved is high enough that a wrong answer is likely, RESENSE (costs 1 of 5 remaining looks today, 10 questions today, returns the true room); if your memory is probably still right, ANSWER from it; (3) fill 'answer' with your best current guess either way, and calibrate 'confidence' to est_p_moved.

---

Household: a family home: two working parents, a teenage son, a toddler daughter

Your memory of the house:
- bowl_1: kitchen (last seen 08:00)
- bowl_2: kitchen (last seen 08:00)
- bowl_3: kitchen (last seen 08:00)
- bowl_4: kitchen (last seen 08:00)
- candle_1: living_room (last seen 08:00)
- chair_1: living_room (last seen 08:00)
- chair_2: living_room (last seen 08:00)
- chair_3: living_room (last seen 08:00)
- chair_4: living_room (last seen 08:00)
- david_keys: kitchen (last seen 08:00)
- david_phone: not in any room (away/put away) (last seen 08:00)
- david_wallet: not in any room (away/put away) (last seen 08:00)
- fridge_1: not in any room (away/put away) (last seen 08:00)
- leo_headphones: not in any room (away/put away) (last seen 08:00)
- leo_laptop: not in any room (away/put away) (last seen 08:00)
- leo_phone: bedroom_2 (last seen 08:00)
- mia_backpack: not in any room (away/put away) (last seen 08:00)
- newspaper_1: living_room (last seen 08:00)
- newspaper_2: living_room (last seen 08:00)
- potted_plant_1: living_room (last seen 08:00)
- potted_plant_2: living_room (last seen 08:00)
- potted_plant_3: living_room (last seen 08:00)
- potted_plant_4: living_room (last seen 08:00)
- potted_plant_5: living_room (last seen 08:00)
- potted_plant_6: living_room (last seen 08:00)
- remote_control_1: living_room (last seen 08:00)
- remote_control_2: living_room (last seen 08:00)
- sarah_keys: not in any room (away/put away) (last seen 08:00)
- sarah_laptop: not in any room (away/put away) (last seen 08:00)
- sarah_phone: not in any room (away/put away) (last seen 08:00)
- sarah_wallet: not in any room (away/put away) (last seen 08:00)
- stool_1: kitchen (last seen 08:00)
- stool_2: kitchen (last seen 08:00)
- stool_3: kitchen (last seen 08:00)
- teapot_1: kitchen (last seen 08:00)
- toy_1: not in any room (away/put away) (last seen 08:00)
- toy_2: living_room (last seen 08:00)
- toy_3: not in any room (away/put away) (last seen 08:00)
- toy_4: not in any room (away/put away) (last seen 08:00)
- tv_1: not in any room (away/put away) (last seen 08:00)
- vase_1: living_room (last seen 08:00)
- wardrobe_1: not in any room (away/put away) (last seen 08:00)

Current time: 09:00

Question: which room is chair_4 in right now? Options: bathroom_1, bathroom_2, bathroom_3, bedroom_1, bedroom_2, bedroom_3, closet, garage, kitchen, laundryroom, living_room, elsewhere
```

**MODEL RESPONSE:**
- action: `answer`   answer: `living_room`   confidence: 0.95   est_p_moved: 0.05
- reason: chair_4 is a piece of furniture and was last seen in the living_room just 1 hour ago. Furniture is very unlikely to move on its own, and there’s no indication it was relocated, so the memory is probably still correct.

**GROUND TRUTH:** true room = `living_room`  →  answer ✓ correct

---

## Episode 1  [family / A3 / chair_4 / Δt=4h]

**PROMPT (what the model saw):**
```
You are a household robot's decision module. Answer location questions about objects in the house. 'elsewhere' means the object is not in any room (taken out of the house, or put away out of sight). You have a memory of past observations, possibly stale. Work step by step: (1) from the object's class and how long ago it was last seen, estimate est_p_moved — the probability it is no longer where your memory says (frequently-handled items drift within hours; furniture rarely moves); (2) decide: if est_p_moved is high enough that a wrong answer is likely, RESENSE (costs 1 of 5 remaining looks today, 10 questions today, returns the true room); if your memory is probably still right, ANSWER from it; (3) fill 'answer' with your best current guess either way, and calibrate 'confidence' to est_p_moved.

---

Household: a family home: two working parents, a teenage son, a toddler daughter

Your memory of the house:
- bowl_1: kitchen (last seen 08:00)
- bowl_2: kitchen (last seen 08:00)
- bowl_3: kitchen (last seen 08:00)
- bowl_4: kitchen (last seen 08:00)
- candle_1: living_room (last seen 08:00)
- chair_1: living_room (last seen 08:00)
- chair_2: living_room (last seen 08:00)
- chair_3: living_room (last seen 08:00)
- chair_4: living_room (last seen 08:00)
- david_keys: kitchen (last seen 08:00)
- david_phone: not in any room (away/put away) (last seen 08:00)
- david_wallet: not in any room (away/put away) (last seen 08:00)
- fridge_1: not in any room (away/put away) (last seen 08:00)
- leo_headphones: not in any room (away/put away) (last seen 08:00)
- leo_laptop: not in any room (away/put away) (last seen 08:00)
- leo_phone: bedroom_2 (last seen 08:00)
- mia_backpack: not in any room (away/put away) (last seen 08:00)
- newspaper_1: living_room (last seen 08:00)
- newspaper_2: living_room (last seen 08:00)
- potted_plant_1: living_room (last seen 08:00)
- potted_plant_2: living_room (last seen 08:00)
- potted_plant_3: living_room (last seen 08:00)
- potted_plant_4: living_room (last seen 08:00)
- potted_plant_5: living_room (last seen 08:00)
- potted_plant_6: living_room (last seen 08:00)
- remote_control_1: living_room (last seen 08:00)
- remote_control_2: living_room (last seen 08:00)
- sarah_keys: not in any room (away/put away) (last seen 08:00)
- sarah_laptop: not in any room (away/put away) (last seen 08:00)
- sarah_phone: not in any room (away/put away) (last seen 08:00)
- sarah_wallet: not in any room (away/put away) (last seen 08:00)
- stool_1: kitchen (last seen 08:00)
- stool_2: kitchen (last seen 08:00)
- stool_3: kitchen (last seen 08:00)
- teapot_1: kitchen (last seen 08:00)
- toy_1: not in any room (away/put away) (last seen 08:00)
- toy_2: living_room (last seen 08:00)
- toy_3: not in any room (away/put away) (last seen 08:00)
- toy_4: not in any room (away/put away) (last seen 08:00)
- tv_1: not in any room (away/put away) (last seen 08:00)
- vase_1: living_room (last seen 08:00)
- wardrobe_1: not in any room (away/put away) (last seen 08:00)

Current time: 12:00

Question: which room is chair_4 in right now? Options: bathroom_1, bathroom_2, bathroom_3, bedroom_1, bedroom_2, bedroom_3, closet, garage, kitchen, laundryroom, living_room, elsewhere
```

**MODEL RESPONSE:**
- action: `answer`   answer: `living_room`   confidence: 0.92   est_p_moved: 0.08
- reason: chair_4 is a piece of furniture, which rarely moves. It was last seen in the living_room at 08:00, and only 4 hours have passed, so the memory is likely still correct.

**GROUND TRUTH:** true room = `living_room`  →  answer ✓ correct

---

## Episode 2  [family / A3 / chair_4 / Δt=9h]

**PROMPT (what the model saw):**
```
You are a household robot's decision module. Answer location questions about objects in the house. 'elsewhere' means the object is not in any room (taken out of the house, or put away out of sight). You have a memory of past observations, possibly stale. Work step by step: (1) from the object's class and how long ago it was last seen, estimate est_p_moved — the probability it is no longer where your memory says (frequently-handled items drift within hours; furniture rarely moves); (2) decide: if est_p_moved is high enough that a wrong answer is likely, RESENSE (costs 1 of 5 remaining looks today, 10 questions today, returns the true room); if your memory is probably still right, ANSWER from it; (3) fill 'answer' with your best current guess either way, and calibrate 'confidence' to est_p_moved.

---

Household: a family home: two working parents, a teenage son, a toddler daughter

Your memory of the house:
- bowl_1: kitchen (last seen 08:00)
- bowl_2: kitchen (last seen 08:00)
- bowl_3: kitchen (last seen 08:00)
- bowl_4: kitchen (last seen 08:00)
- candle_1: living_room (last seen 08:00)
- chair_1: living_room (last seen 08:00)
- chair_2: living_room (last seen 08:00)
- chair_3: living_room (last seen 08:00)
- chair_4: living_room (last seen 08:00)
- david_keys: kitchen (last seen 08:00)
- david_phone: not in any room (away/put away) (last seen 08:00)
- david_wallet: not in any room (away/put away) (last seen 08:00)
- fridge_1: not in any room (away/put away) (last seen 08:00)
- leo_headphones: not in any room (away/put away) (last seen 08:00)
- leo_laptop: not in any room (away/put away) (last seen 08:00)
- leo_phone: bedroom_2 (last seen 08:00)
- mia_backpack: not in any room (away/put away) (last seen 08:00)
- newspaper_1: living_room (last seen 08:00)
- newspaper_2: living_room (last seen 08:00)
- potted_plant_1: living_room (last seen 08:00)
- potted_plant_2: living_room (last seen 08:00)
- potted_plant_3: living_room (last seen 08:00)
- potted_plant_4: living_room (last seen 08:00)
- potted_plant_5: living_room (last seen 08:00)
- potted_plant_6: living_room (last seen 08:00)
- remote_control_1: living_room (last seen 08:00)
- remote_control_2: living_room (last seen 08:00)
- sarah_keys: not in any room (away/put away) (last seen 08:00)
- sarah_laptop: not in any room (away/put away) (last seen 08:00)
- sarah_phone: not in any room (away/put away) (last seen 08:00)
- sarah_wallet: not in any room (away/put away) (last seen 08:00)
- stool_1: kitchen (last seen 08:00)
- stool_2: kitchen (last seen 08:00)
- stool_3: kitchen (last seen 08:00)
- teapot_1: kitchen (last seen 08:00)
- toy_1: not in any room (away/put away) (last seen 08:00)
- toy_2: living_room (last seen 08:00)
- toy_3: not in any room (away/put away) (last seen 08:00)
- toy_4: not in any room (away/put away) (last seen 08:00)
- tv_1: not in any room (away/put away) (last seen 08:00)
- vase_1: living_room (last seen 08:00)
- wardrobe_1: not in any room (away/put away) (last seen 08:00)

Current time: 17:00

Question: which room is chair_4 in right now? Options: bathroom_1, bathroom_2, bathroom_3, bedroom_1, bedroom_2, bedroom_3, closet, garage, kitchen, laundryroom, living_room, elsewhere
```

**MODEL RESPONSE:**
- action: `answer`   answer: `living_room`   confidence: 0.92   est_p_moved: 0.08
- reason: chair_4 is a piece of furniture, which rarely moves. It was last seen in the living_room at 08:00, and only 9 hours have passed, so the memory is likely still correct.

**GROUND TRUTH:** true room = `living_room`  →  answer ✓ correct

---

## Episode 3  [family / A3 / chair_4 / Δt=13h]

**PROMPT (what the model saw):**
```
You are a household robot's decision module. Answer location questions about objects in the house. 'elsewhere' means the object is not in any room (taken out of the house, or put away out of sight). You have a memory of past observations, possibly stale. Work step by step: (1) from the object's class and how long ago it was last seen, estimate est_p_moved — the probability it is no longer where your memory says (frequently-handled items drift within hours; furniture rarely moves); (2) decide: if est_p_moved is high enough that a wrong answer is likely, RESENSE (costs 1 of 5 remaining looks today, 10 questions today, returns the true room); if your memory is probably still right, ANSWER from it; (3) fill 'answer' with your best current guess either way, and calibrate 'confidence' to est_p_moved.

---

Household: a family home: two working parents, a teenage son, a toddler daughter

Your memory of the house:
- bowl_1: kitchen (last seen 08:00)
- bowl_2: kitchen (last seen 08:00)
- bowl_3: kitchen (last seen 08:00)
- bowl_4: kitchen (last seen 08:00)
- candle_1: living_room (last seen 08:00)
- chair_1: living_room (last seen 08:00)
- chair_2: living_room (last seen 08:00)
- chair_3: living_room (last seen 08:00)
- chair_4: living_room (last seen 08:00)
- david_keys: kitchen (last seen 08:00)
- david_phone: not in any room (away/put away) (last seen 08:00)
- david_wallet: not in any room (away/put away) (last seen 08:00)
- fridge_1: not in any room (away/put away) (last seen 08:00)
- leo_headphones: not in any room (away/put away) (last seen 08:00)
- leo_laptop: not in any room (away/put away) (last seen 08:00)
- leo_phone: bedroom_2 (last seen 08:00)
- mia_backpack: not in any room (away/put away) (last seen 08:00)
- newspaper_1: living_room (last seen 08:00)
- newspaper_2: living_room (last seen 08:00)
- potted_plant_1: living_room (last seen 08:00)
- potted_plant_2: living_room (last seen 08:00)
- potted_plant_3: living_room (last seen 08:00)
- potted_plant_4: living_room (last seen 08:00)
- potted_plant_5: living_room (last seen 08:00)
- potted_plant_6: living_room (last seen 08:00)
- remote_control_1: living_room (last seen 08:00)
- remote_control_2: living_room (last seen 08:00)
- sarah_keys: not in any room (away/put away) (last seen 08:00)
- sarah_laptop: not in any room (away/put away) (last seen 08:00)
- sarah_phone: not in any room (away/put away) (last seen 08:00)
- sarah_wallet: not in any room (away/put away) (last seen 08:00)
- stool_1: kitchen (last seen 08:00)
- stool_2: kitchen (last seen 08:00)
- stool_3: kitchen (last seen 08:00)
- teapot_1: kitchen (last seen 08:00)
- toy_1: not in any room (away/put away) (last seen 08:00)
- toy_2: living_room (last seen 08:00)
- toy_3: not in any room (away/put away) (last seen 08:00)
- toy_4: not in any room (away/put away) (last seen 08:00)
- tv_1: not in any room (away/put away) (last seen 08:00)
- vase_1: living_room (last seen 08:00)
- wardrobe_1: not in any room (away/put away) (last seen 08:00)

Current time: 21:00

Question: which room is chair_4 in right now? Options: bathroom_1, bathroom_2, bathroom_3, bedroom_1, bedroom_2, bedroom_3, closet, garage, kitchen, laundryroom, living_room, elsewhere
```

**MODEL RESPONSE:**
- action: `answer`   answer: `living_room`   confidence: 0.95   est_p_moved: 0.05
- reason: chair_4 is a piece of furniture in the living room, and furniture is very unlikely to have moved since 08:00. The memory is probably still correct, so no resense needed.

**GROUND TRUTH:** true room = `living_room`  →  answer ✓ correct

---

## Episode 4  [family / A3 / remote_control_2 / Δt=1h]

**PROMPT (what the model saw):**
```
You are a household robot's decision module. Answer location questions about objects in the house. 'elsewhere' means the object is not in any room (taken out of the house, or put away out of sight). You have a memory of past observations, possibly stale. Work step by step: (1) from the object's class and how long ago it was last seen, estimate est_p_moved — the probability it is no longer where your memory says (frequently-handled items drift within hours; furniture rarely moves); (2) decide: if est_p_moved is high enough that a wrong answer is likely, RESENSE (costs 1 of 5 remaining looks today, 10 questions today, returns the true room); if your memory is probably still right, ANSWER from it; (3) fill 'answer' with your best current guess either way, and calibrate 'confidence' to est_p_moved.

---

Household: a family home: two working parents, a teenage son, a toddler daughter

Your memory of the house:
- bowl_1: kitchen (last seen 08:00)
- bowl_2: kitchen (last seen 08:00)
- bowl_3: kitchen (last seen 08:00)
- bowl_4: kitchen (last seen 08:00)
- candle_1: living_room (last seen 08:00)
- chair_1: living_room (last seen 08:00)
- chair_2: living_room (last seen 08:00)
- chair_3: living_room (last seen 08:00)
- chair_4: living_room (last seen 08:00)
- david_keys: kitchen (last seen 08:00)
- david_phone: not in any room (away/put away) (last seen 08:00)
- david_wallet: not in any room (away/put away) (last seen 08:00)
- fridge_1: not in any room (away/put away) (last seen 08:00)
- leo_headphones: not in any room (away/put away) (last seen 08:00)
- leo_laptop: not in any room (away/put away) (last seen 08:00)
- leo_phone: bedroom_2 (last seen 08:00)
- mia_backpack: not in any room (away/put away) (last seen 08:00)
- newspaper_1: living_room (last seen 08:00)
- newspaper_2: living_room (last seen 08:00)
- potted_plant_1: living_room (last seen 08:00)
- potted_plant_2: living_room (last seen 08:00)
- potted_plant_3: living_room (last seen 08:00)
- potted_plant_4: living_room (last seen 08:00)
- potted_plant_5: living_room (last seen 08:00)
- potted_plant_6: living_room (last seen 08:00)
- remote_control_1: living_room (last seen 08:00)
- remote_control_2: living_room (last seen 08:00)
- sarah_keys: not in any room (away/put away) (last seen 08:00)
- sarah_laptop: not in any room (away/put away) (last seen 08:00)
- sarah_phone: not in any room (away/put away) (last seen 08:00)
- sarah_wallet: not in any room (away/put away) (last seen 08:00)
- stool_1: kitchen (last seen 08:00)
- stool_2: kitchen (last seen 08:00)
- stool_3: kitchen (last seen 08:00)
- teapot_1: kitchen (last seen 08:00)
- toy_1: not in any room (away/put away) (last seen 08:00)
- toy_2: living_room (last seen 08:00)
- toy_3: not in any room (away/put away) (last seen 08:00)
- toy_4: not in any room (away/put away) (last seen 08:00)
- tv_1: not in any room (away/put away) (last seen 08:00)
- vase_1: living_room (last seen 08:00)
- wardrobe_1: not in any room (away/put away) (last seen 08:00)

Current time: 09:00

Question: which room is remote_control_2 in right now? Options: bathroom_1, bathroom_2, bathroom_3, bedroom_1, bedroom_2, bedroom_3, closet, garage, kitchen, laundryroom, living_room, elsewhere
```

**MODEL RESPONSE:**
- action: `answer`   answer: `living_room`   confidence: 0.82   est_p_moved: 0.18
- reason: remote_control_2 is a frequently handled household item, but it was last seen only 1 hour ago in the living room. Remotes usually stay near the TV/sofa area and are less likely to move far within an hour, so the memory is probably still सही

**GROUND TRUTH:** true room = `living_room`  →  answer ✓ correct

---

## Episode 5  [family / A3 / remote_control_2 / Δt=4h]

**PROMPT (what the model saw):**
```
You are a household robot's decision module. Answer location questions about objects in the house. 'elsewhere' means the object is not in any room (taken out of the house, or put away out of sight). You have a memory of past observations, possibly stale. Work step by step: (1) from the object's class and how long ago it was last seen, estimate est_p_moved — the probability it is no longer where your memory says (frequently-handled items drift within hours; furniture rarely moves); (2) decide: if est_p_moved is high enough that a wrong answer is likely, RESENSE (costs 1 of 5 remaining looks today, 10 questions today, returns the true room); if your memory is probably still right, ANSWER from it; (3) fill 'answer' with your best current guess either way, and calibrate 'confidence' to est_p_moved.

---

Household: a family home: two working parents, a teenage son, a toddler daughter

Your memory of the house:
- bowl_1: kitchen (last seen 08:00)
- bowl_2: kitchen (last seen 08:00)
- bowl_3: kitchen (last seen 08:00)
- bowl_4: kitchen (last seen 08:00)
- candle_1: living_room (last seen 08:00)
- chair_1: living_room (last seen 08:00)
- chair_2: living_room (last seen 08:00)
- chair_3: living_room (last seen 08:00)
- chair_4: living_room (last seen 08:00)
- david_keys: kitchen (last seen 08:00)
- david_phone: not in any room (away/put away) (last seen 08:00)
- david_wallet: not in any room (away/put away) (last seen 08:00)
- fridge_1: not in any room (away/put away) (last seen 08:00)
- leo_headphones: not in any room (away/put away) (last seen 08:00)
- leo_laptop: not in any room (away/put away) (last seen 08:00)
- leo_phone: bedroom_2 (last seen 08:00)
- mia_backpack: not in any room (away/put away) (last seen 08:00)
- newspaper_1: living_room (last seen 08:00)
- newspaper_2: living_room (last seen 08:00)
- potted_plant_1: living_room (last seen 08:00)
- potted_plant_2: living_room (last seen 08:00)
- potted_plant_3: living_room (last seen 08:00)
- potted_plant_4: living_room (last seen 08:00)
- potted_plant_5: living_room (last seen 08:00)
- potted_plant_6: living_room (last seen 08:00)
- remote_control_1: living_room (last seen 08:00)
- remote_control_2: living_room (last seen 08:00)
- sarah_keys: not in any room (away/put away) (last seen 08:00)
- sarah_laptop: not in any room (away/put away) (last seen 08:00)
- sarah_phone: not in any room (away/put away) (last seen 08:00)
- sarah_wallet: not in any room (away/put away) (last seen 08:00)
- stool_1: kitchen (last seen 08:00)
- stool_2: kitchen (last seen 08:00)
- stool_3: kitchen (last seen 08:00)
- teapot_1: kitchen (last seen 08:00)
- toy_1: not in any room (away/put away) (last seen 08:00)
- toy_2: living_room (last seen 08:00)
- toy_3: not in any room (away/put away) (last seen 08:00)
- toy_4: not in any room (away/put away) (last seen 08:00)
- tv_1: not in any room (away/put away) (last seen 08:00)
- vase_1: living_room (last seen 08:00)
- wardrobe_1: not in any room (away/put away) (last seen 08:00)

Current time: 12:00

Question: which room is remote_control_2 in right now? Options: bathroom_1, bathroom_2, bathroom_3, bedroom_1, bedroom_2, bedroom_3, closet, garage, kitchen, laundryroom, living_room, elsewhere
```

**MODEL RESPONSE:**
- action: `answer`   answer: `living_room`   confidence: 0.65   est_p_moved: 0.35
- reason: remote controls are frequently handled, but this one was last seen in the living room only 4 hours ago. It may have been moved, but the living room is still the most likely location. The chance of drift is moderate, not high enough to force

**GROUND TRUTH:** true room = `living_room`  →  answer ✓ correct

---
