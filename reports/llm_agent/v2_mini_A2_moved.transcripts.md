## Episode 0  [family / A2 / toy_4 / Δt=5h]

**PROMPT (what the model saw):**
```
You are a household robot's decision module. Answer location questions about objects, at the level of the exact spot: answers are 'room.receptacle' labels (e.g. kitchen.counter_1 = the first counter in the kitchen; a *_tucked label is the tucked-in position at that furniture). 'elsewhere' means the object is in no listed spot (taken out of the house, or put away out of sight). Residents move objects as they live their day: think about which household activities plausibly happened in the relevant time span — meals, work or school hours, tidying, evening wind-down, weekend rhythms — and how those activities move objects of this kind. You have a memory of past observations. Either ANSWER from memory (action='answer') or RESENSE the object (action='resense') — resensing costs one look from a limited daily sensing budget and returns the object's true current location. Either way, fill 'answer' with your best guess of the CURRENT location.

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
- action: `answer`   answer: `elsewhere`   confidence: 0.78   est_p_moved: nan
- reason: toy_4 was already not in any room at the last observation, and there’s no strong reason to expect it was brought out later; toddler toys are often left put away when not in use. Best guess is still away/put away, which maps to elsewhere.

**GROUND TRUTH:** true room = `living_room.table_1`  →  answer ✗ WRONG  (object HAD moved since snapshot)

---

## Episode 1  [family / A2 / chair_1 / Δt=6h]

**PROMPT (what the model saw):**
```
You are a household robot's decision module. Answer location questions about objects, at the level of the exact spot: answers are 'room.receptacle' labels (e.g. kitchen.counter_1 = the first counter in the kitchen; a *_tucked label is the tucked-in position at that furniture). 'elsewhere' means the object is in no listed spot (taken out of the house, or put away out of sight). Residents move objects as they live their day: think about which household activities plausibly happened in the relevant time span — meals, work or school hours, tidying, evening wind-down, weekend rhythms — and how those activities move objects of this kind. You have a memory of past observations. Either ANSWER from memory (action='answer') or RESENSE the object (action='resense') — resensing costs one look from a limited daily sensing budget and returns the object's true current location. Either way, fill 'answer' with your best guess of the CURRENT location.

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
- action: `answer`   answer: `living_room.table_1`   confidence: 0.78   est_p_moved: nan
- reason: chair_1 was last seen on the living_room.table_1 in the morning. By late afternoon in a family home, dining chairs are usually still left around the table unless someone has tidied; there’s no specific evidence of movement. Best guess is it remains there.

**GROUND TRUTH:** true room = `living_room.tv_1`  →  answer ✗ WRONG  (object HAD moved since snapshot)

---

## Episode 2  [family / A2 / sarah_phone / Δt=3h]

**PROMPT (what the model saw):**
```
You are a household robot's decision module. Answer location questions about objects, at the level of the exact spot: answers are 'room.receptacle' labels (e.g. kitchen.counter_1 = the first counter in the kitchen; a *_tucked label is the tucked-in position at that furniture). 'elsewhere' means the object is in no listed spot (taken out of the house, or put away out of sight). Residents move objects as they live their day: think about which household activities plausibly happened in the relevant time span — meals, work or school hours, tidying, evening wind-down, weekend rhythms — and how those activities move objects of this kind. You have a memory of past observations. Either ANSWER from memory (action='answer') or RESENSE the object (action='resense') — resensing costs one look from a limited daily sensing budget and returns the object's true current location. Either way, fill 'answer' with your best guess of the CURRENT location.

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
- action: `answer`   answer: `elsewhere`   confidence: 0.74   est_p_moved: nan
- reason: Sarah's phone was last seen put away/not in any room at 10:14. By 13:59 on a weekday, a working parent would likely have taken her phone with her to work or kept it on her person, so it is probably no longer in a listed household spot.

**GROUND TRUTH:** true room = `bedroom_1.chest_of_drawers_1`  →  answer ✗ WRONG  (object HAD moved since snapshot)

---

## Episode 3  [family / A2 / toy_1 / Δt=6h]

**PROMPT (what the model saw):**
```
You are a household robot's decision module. Answer location questions about objects, at the level of the exact spot: answers are 'room.receptacle' labels (e.g. kitchen.counter_1 = the first counter in the kitchen; a *_tucked label is the tucked-in position at that furniture). 'elsewhere' means the object is in no listed spot (taken out of the house, or put away out of sight). Residents move objects as they live their day: think about which household activities plausibly happened in the relevant time span — meals, work or school hours, tidying, evening wind-down, weekend rhythms — and how those activities move objects of this kind. You have a memory of past observations. Either ANSWER from memory (action='answer') or RESENSE the object (action='resense') — resensing costs one look from a limited daily sensing budget and returns the object's true current location. Either way, fill 'answer' with your best guess of the CURRENT location.

---

Household: a family home: two working parents, a teenage son, a toddler daughter

Your memory of the house:
- bowl_1: kitchen.counter_1 (last seen Wednesday 09:44)
- bowl_2: kitchen.counter_1 (last seen Wednesday 09:44)
- bowl_3: kitchen.counter_1 (last seen Wednesday 09:44)
- bowl_4: kitchen.counter_1 (last seen Wednesday 09:44)
- candle_1: living_room.table_1 (last seen Wednesday 09:44)
- chair_1: living_room.table_1 (last seen Wednesday 09:44)
- chair_2: living_room.table_1 (last seen Wednesday 09:44)
- chair_3: living_room.table_1 (last seen Wednesday 09:44)
- chair_4: living_room.table_1 (last seen Wednesday 09:44)
- david_keys: not in any room (away/put away) (last seen Wednesday 09:44)
- david_phone: not in any room (away/put away) (last seen Wednesday 09:44)
- david_wallet: not in any room (away/put away) (last seen Wednesday 09:44)
- fridge_1: fridge (last seen Wednesday 09:44)
- leo_headphones: not in any room (away/put away) (last seen Wednesday 09:44)
- leo_laptop: not in any room (away/put away) (last seen Wednesday 09:44)
- leo_phone: not in any room (away/put away) (last seen Wednesday 09:44)
- mia_backpack: not in any room (away/put away) (last seen Wednesday 09:44)
- newspaper_1: living_room.table_1 (last seen Wednesday 09:44)
- newspaper_2: living_room.table_1 (last seen Wednesday 09:44)
- potted_plant_1: living_room.corner (last seen Wednesday 09:44)
- potted_plant_2: living_room.corner (last seen Wednesday 09:44)
- potted_plant_3: living_room.corner (last seen Wednesday 09:44)
- potted_plant_4: living_room.corner (last seen Wednesday 09:44)
- potted_plant_5: living_room.corner (last seen Wednesday 09:44)
- potted_plant_6: living_room.corner (last seen Wednesday 09:44)
- remote_control_1: living_room.table_1 (last seen Wednesday 09:44)
- remote_control_2: living_room.table_1 (last seen Wednesday 09:44)
- sarah_keys: not in any room (away/put away) (last seen Wednesday 09:44)
- sarah_laptop: not in any room (away/put away) (last seen Wednesday 09:44)
- sarah_phone: not in any room (away/put away) (last seen Wednesday 09:44)
- sarah_wallet: not in any room (away/put away) (last seen Wednesday 09:44)
- stool_1: kitchen.counter_1 (last seen Wednesday 09:44)
- stool_2: kitchen.counter_1 (last seen Wednesday 09:44)
- stool_3: kitchen.counter_1 (last seen Wednesday 09:44)
- teapot_1: kitchen.counter_1 (last seen Wednesday 09:44)
- toy_1: living_room.tv_1 (last seen Wednesday 09:44)
- toy_2: living_room.table_1 (last seen Wednesday 09:44)
- toy_3: not in any room (away/put away) (last seen Wednesday 09:44)
- toy_4: not in any room (away/put away) (last seen Wednesday 09:44)
- tv_1: tv (last seen Wednesday 09:44)
- vase_1: living_room.table_1 (last seen Wednesday 09:44)
- wardrobe_1: wardrobe (last seen Wednesday 09:44)

Current time: Wednesday 16:43

Question: where is toy_1 right now? Answer with one of the location labels, or 'elsewhere'.
```

**MODEL RESPONSE:**
- action: `answer`   answer: `living_room.tv_1`   confidence: 0.74   est_p_moved: nan
- reason: toy_1 was last seen on the living room TV in the morning. By late afternoon in a family home, a toddler’s toy is likely to still be in the living room near the TV unless tidied away; no evidence suggests it was moved elsewhere. Best guess is the same spot.

**GROUND TRUTH:** true room = `living_room.couch_1`  →  answer ✗ WRONG  (object HAD moved since snapshot)

---

## Episode 4  [family / A2 / toy_1 / Δt=5h]

**PROMPT (what the model saw):**
```
You are a household robot's decision module. Answer location questions about objects, at the level of the exact spot: answers are 'room.receptacle' labels (e.g. kitchen.counter_1 = the first counter in the kitchen; a *_tucked label is the tucked-in position at that furniture). 'elsewhere' means the object is in no listed spot (taken out of the house, or put away out of sight). Residents move objects as they live their day: think about which household activities plausibly happened in the relevant time span — meals, work or school hours, tidying, evening wind-down, weekend rhythms — and how those activities move objects of this kind. You have a memory of past observations. Either ANSWER from memory (action='answer') or RESENSE the object (action='resense') — resensing costs one look from a limited daily sensing budget and returns the object's true current location. Either way, fill 'answer' with your best guess of the CURRENT location.

---

Household: a family home: two working parents, a teenage son, a toddler daughter

Your memory of the house:
- bowl_1: kitchen.counter_1 (last seen Wednesday 13:34)
- bowl_2: kitchen.counter_1 (last seen Wednesday 13:34)
- bowl_3: kitchen.counter_1 (last seen Wednesday 13:34)
- bowl_4: kitchen.counter_1 (last seen Wednesday 13:34)
- candle_1: living_room.table_1 (last seen Wednesday 13:34)
- chair_1: living_room.table_1 (last seen Wednesday 13:34)
- chair_2: living_room.table_1 (last seen Wednesday 13:34)
- chair_3: living_room.table_1 (last seen Wednesday 13:34)
- chair_4: living_room.table_1 (last seen Wednesday 13:34)
- david_keys: not in any room (away/put away) (last seen Wednesday 13:34)
- david_phone: not in any room (away/put away) (last seen Wednesday 13:34)
- david_wallet: not in any room (away/put away) (last seen Wednesday 13:34)
- fridge_1: fridge (last seen Wednesday 13:34)
- leo_headphones: not in any room (away/put away) (last seen Wednesday 13:34)
- leo_laptop: not in any room (away/put away) (last seen Wednesday 13:34)
- leo_phone: not in any room (away/put away) (last seen Wednesday 13:34)
- mia_backpack: not in any room (away/put away) (last seen Wednesday 13:34)
- newspaper_1: living_room.table_1 (last seen Wednesday 13:34)
- newspaper_2: living_room.table_1 (last seen Wednesday 13:34)
- potted_plant_1: living_room.corner (last seen Wednesday 13:34)
- potted_plant_2: living_room.corner (last seen Wednesday 13:34)
- potted_plant_3: living_room.corner (last seen Wednesday 13:34)
- potted_plant_4: living_room.corner (last seen Wednesday 13:34)
- potted_plant_5: living_room.corner (last seen Wednesday 13:34)
- potted_plant_6: living_room.corner (last seen Wednesday 13:34)
- remote_control_1: kitchen.counter_1 (last seen Wednesday 13:34)
- remote_control_2: living_room.table_1 (last seen Wednesday 13:34)
- sarah_keys: not in any room (away/put away) (last seen Wednesday 13:34)
- sarah_laptop: not in any room (away/put away) (last seen Wednesday 13:34)
- sarah_phone: not in any room (away/put away) (last seen Wednesday 13:34)
- sarah_wallet: not in any room (away/put away) (last seen Wednesday 13:34)
- stool_1: kitchen.counter_1 (last seen Wednesday 13:34)
- stool_2: kitchen.counter_1 (last seen Wednesday 13:34)
- stool_3: kitchen.counter_1 (last seen Wednesday 13:34)
- teapot_1: kitchen.counter_1 (last seen Wednesday 13:34)
- toy_1: living_room.table_1 (last seen Wednesday 13:34)
- toy_2: living_room.table_1 (last seen Wednesday 13:34)
- toy_3: not in any room (away/put away) (last seen Wednesday 13:34)
- toy_4: not in any room (away/put away) (last seen Wednesday 13:34)
- tv_1: tv (last seen Wednesday 13:34)
- vase_1: living_room.table_1 (last seen Wednesday 13:34)
- wardrobe_1: wardrobe (last seen Wednesday 13:34)

Current time: Wednesday 19:13

Question: where is toy_1 right now? Answer with one of the location labels, or 'elsewhere'.
```

**MODEL RESPONSE:**
- action: `answer`   answer: `living_room.table_1`   confidence: 0.72   est_p_moved: nan
- reason: toy_1 was last seen on the living room table during the afternoon. By evening in a family home, a toddler’s toy is most plausibly still in the living room where it was being used, unless tidied away; since toy_3 and toy_4 were put away but toy_1 and toy_2 were left out, I’ll keep it at the same spot

**GROUND TRUTH:** true room = `elsewhere`  →  answer ✗ WRONG  (object HAD moved since snapshot)

---

## Episode 5  [family / A2 / remote_control_1 / Δt=8h]

**PROMPT (what the model saw):**
```
You are a household robot's decision module. Answer location questions about objects, at the level of the exact spot: answers are 'room.receptacle' labels (e.g. kitchen.counter_1 = the first counter in the kitchen; a *_tucked label is the tucked-in position at that furniture). 'elsewhere' means the object is in no listed spot (taken out of the house, or put away out of sight). Residents move objects as they live their day: think about which household activities plausibly happened in the relevant time span — meals, work or school hours, tidying, evening wind-down, weekend rhythms — and how those activities move objects of this kind. You have a memory of past observations. Either ANSWER from memory (action='answer') or RESENSE the object (action='resense') — resensing costs one look from a limited daily sensing budget and returns the object's true current location. Either way, fill 'answer' with your best guess of the CURRENT location.

---

Household: a family home: two working parents, a teenage son, a toddler daughter

Your memory of the house:
- bowl_1: kitchen.counter_1 (last seen Thursday 08:00)
- bowl_2: kitchen.counter_1 (last seen Thursday 08:00)
- bowl_3: kitchen.counter_1 (last seen Thursday 08:00)
- bowl_4: kitchen.counter_1 (last seen Thursday 08:00)
- candle_1: living_room.table_1 (last seen Thursday 08:00)
- chair_1: living_room.table_1 (last seen Thursday 08:00)
- chair_2: living_room.table_1 (last seen Thursday 08:00)
- chair_3: living_room.table_1 (last seen Thursday 08:00)
- chair_4: living_room.table_1 (last seen Thursday 08:00)
- david_keys: not in any room (away/put away) (last seen Thursday 08:00)
- david_phone: not in any room (away/put away) (last seen Thursday 08:00)
- david_wallet: not in any room (away/put away) (last seen Thursday 08:00)
- fridge_1: fridge (last seen Thursday 08:00)
- leo_headphones: not in any room (away/put away) (last seen Thursday 08:00)
- leo_laptop: not in any room (away/put away) (last seen Thursday 08:00)
- leo_phone: bedroom_2.bed_1 (last seen Thursday 08:00)
- mia_backpack: not in any room (away/put away) (last seen Thursday 08:00)
- newspaper_1: kitchen.counter_1 (last seen Thursday 08:00)
- newspaper_2: living_room.table_1 (last seen Thursday 08:00)
- potted_plant_1: living_room.corner (last seen Thursday 08:00)
- potted_plant_2: living_room.corner (last seen Thursday 08:00)
- potted_plant_3: living_room.corner (last seen Thursday 08:00)
- potted_plant_4: living_room.corner (last seen Thursday 08:00)
- potted_plant_5: living_room.corner (last seen Thursday 08:00)
- potted_plant_6: living_room.corner (last seen Thursday 08:00)
- remote_control_1: living_room.table_1 (last seen Thursday 08:00)
- remote_control_2: living_room.table_1 (last seen Thursday 08:00)
- sarah_keys: not in any room (away/put away) (last seen Thursday 08:00)
- sarah_laptop: not in any room (away/put away) (last seen Thursday 08:00)
- sarah_phone: not in any room (away/put away) (last seen Thursday 08:00)
- sarah_wallet: not in any room (away/put away) (last seen Thursday 08:00)
- stool_1: kitchen.counter_1 (last seen Thursday 08:00)
- stool_2: kitchen.counter_1 (last seen Thursday 08:00)
- stool_3: kitchen.counter_1 (last seen Thursday 08:00)
- teapot_1: kitchen.counter_1 (last seen Thursday 08:00)
- toy_1: living_room.table_1 (last seen Thursday 08:00)
- toy_2: living_room.table_1 (last seen Thursday 08:00)
- toy_3: not in any room (away/put away) (last seen Thursday 08:00)
- toy_4: not in any room (away/put away) (last seen Thursday 08:00)
- tv_1: tv (last seen Thursday 08:00)
- vase_1: living_room.table_1 (last seen Thursday 08:00)
- wardrobe_1: wardrobe (last seen Thursday 08:00)

Current time: Thursday 16:00

Question: where is remote_control_1 right now? Answer with one of the location labels, or 'elsewhere'.
```

**MODEL RESPONSE:**
- action: `answer`   answer: `living_room.table_1`   confidence: 0.78   est_p_moved: nan
- reason: The remote control was last seen on the living room table in the morning. By 16:00 on a weekday, the family may have used the living room for TV or tidying, but remotes typically stay on the main living room table when not in use. No evidence suggests it was moved elsewhere, so the best guess is the

**GROUND TRUTH:** true room = `living_room.tv_1`  →  answer ✗ WRONG  (object HAD moved since snapshot)

---
