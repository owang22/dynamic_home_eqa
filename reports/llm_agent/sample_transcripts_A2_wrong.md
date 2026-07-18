## Episode 0  [family / A2 / candle_1 / Δt=13h]

**PROMPT (what the model saw):**
```
You are a household robot's decision module. Answer location questions about objects in the house. 'elsewhere' means the object is not in any room (taken out of the house, or put away out of sight). You have a memory of past observations. You may either ANSWER from memory (action='answer') or RESENSE the object (action='resense') — resensing costs one look from a limited daily sensing budget and returns the object's true current room, so use it only when your memory is likely stale. Either way, fill 'answer' with your best guess of the CURRENT room.

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

Question: which room is candle_1 in right now? Options: bathroom_1, bathroom_2, bathroom_3, bedroom_1, bedroom_2, bedroom_3, closet, garage, kitchen, laundryroom, living_room, elsewhere
```

**MODEL RESPONSE:**
- action: `answer`   answer: `living_room`   confidence: 0.93   est_p_moved: nan
- reason: candle_1 was last seen in the living_room and there is no evidence it was moved; decorative items like candles typically stay put, so memory is likely still valid.

**GROUND TRUTH:** true room = `bedroom_3`  →  answer ✗ WRONG  (object HAD moved since snapshot)

---

## Episode 1  [roommates / A2 / casey_laptop / Δt=9h]

**PROMPT (what the model saw):**
```
You are a household robot's decision module. Answer location questions about objects in the house. 'elsewhere' means the object is not in any room (taken out of the house, or put away out of sight). You have a memory of past observations. You may either ANSWER from memory (action='answer') or RESENSE the object (action='resense') — resensing costs one look from a limited daily sensing budget and returns the object's true current room, so use it only when your memory is likely stale. Either way, fill 'answer' with your best guess of the CURRENT room.

---

Household: a shared house: three adult roommates

Your memory of the house:
- alex_headphones: not in any room (away/put away) (last seen 08:00)
- alex_keys: not in any room (away/put away) (last seen 08:00)
- alex_laptop: not in any room (away/put away) (last seen 08:00)
- alex_phone: kitchen (last seen 08:00)
- alex_wallet: not in any room (away/put away) (last seen 08:00)
- bottle_1: kitchen (last seen 08:00)
- bottle_2: not in any room (away/put away) (last seen 08:00)
- casey_headphones: not in any room (away/put away) (last seen 08:00)
- casey_laptop: not in any room (away/put away) (last seen 08:00)
- casey_phone: not in any room (away/put away) (last seen 08:00)
- casey_sunglasses: not in any room (away/put away) (last seen 08:00)
- chair_1: bedroom_2 (last seen 08:00)
- chair_10: dining (last seen 08:00)
- chair_2: dining (last seen 08:00)
- chair_3: dining (last seen 08:00)
- chair_4: dining (last seen 08:00)
- chair_5: dining (last seen 08:00)
- chair_6: dining (last seen 08:00)
- chair_7: living_room (last seen 08:00)
- chair_8: living_room (last seen 08:00)
- chair_9: dining (last seen 08:00)
- cup_1: dining_room (last seen 08:00)
- cup_2: kitchen (last seen 08:00)
- cup_3: dining_room (last seen 08:00)
- cup_4: not in any room (away/put away) (last seen 08:00)
- fridge_1: not in any room (away/put away) (last seen 08:00)
- jordan_keys: not in any room (away/put away) (last seen 08:00)
- jordan_phone: not in any room (away/put away) (last seen 08:00)
- jordan_sunglasses: not in any room (away/put away) (last seen 08:00)
- jordan_wallet: not in any room (away/put away) (last seen 08:00)
- oven_1: not in any room (away/put away) (last seen 08:00)
- potted_plant_1: living_room (last seen 08:00)
- potted_plant_10: living_room (last seen 08:00)
- potted_plant_11: living_room (last seen 08:00)
- potted_plant_12: living_room (last seen 08:00)
- potted_plant_13: living_room (last seen 08:00)
- potted_plant_14: living_room (last seen 08:00)
- potted_plant_15: living_room (last seen 08:00)
- potted_plant_16: living_room (last seen 08:00)
- potted_plant_17: living_room (last seen 08:00)
- potted_plant_2: living_room (last seen 08:00)
- potted_plant_3: living_room (last seen 08:00)
- potted_plant_4: living_room (last seen 08:00)
- potted_plant_5: living_room (last seen 08:00)
- potted_plant_6: living_room (last seen 08:00)
- potted_plant_7: living_room (last seen 08:00)
- potted_plant_8: living_room (last seen 08:00)
- potted_plant_9: living_room (last seen 08:00)
- remote_control_1: living_room (last seen 08:00)
- stool_1: kitchen (last seen 08:00)
- stool_2: kitchen (last seen 08:00)
- tv_1: not in any room (away/put away) (last seen 08:00)
- vase_1: dining_room (last seen 08:00)

Current time: 17:00

Question: which room is casey_laptop in right now? Options: bathroom_1, bathroom_2, bedroom_1, bedroom_2, dining, dining_room, kitchen, living_room, toilet, elsewhere
```

**MODEL RESPONSE:**
- action: `answer`   answer: `elsewhere`   confidence: 0.92   est_p_moved: nan
- reason: casey_laptop was last seen away/put away and there is no newer observation suggesting it has been placed in a room since 08:00. The safest current guess is elsewhere, and resensing is likely unnecessary for an item typically kept put away.

**GROUND TRUTH:** true room = `living_room`  →  answer ✗ WRONG  (object HAD moved since snapshot)

---

## Episode 2  [roommates / A2 / casey_laptop / Δt=13h]

**PROMPT (what the model saw):**
```
You are a household robot's decision module. Answer location questions about objects in the house. 'elsewhere' means the object is not in any room (taken out of the house, or put away out of sight). You have a memory of past observations. You may either ANSWER from memory (action='answer') or RESENSE the object (action='resense') — resensing costs one look from a limited daily sensing budget and returns the object's true current room, so use it only when your memory is likely stale. Either way, fill 'answer' with your best guess of the CURRENT room.

---

Household: a shared house: three adult roommates

Your memory of the house:
- alex_headphones: not in any room (away/put away) (last seen 08:00)
- alex_keys: not in any room (away/put away) (last seen 08:00)
- alex_laptop: not in any room (away/put away) (last seen 08:00)
- alex_phone: kitchen (last seen 08:00)
- alex_wallet: not in any room (away/put away) (last seen 08:00)
- bottle_1: kitchen (last seen 08:00)
- bottle_2: not in any room (away/put away) (last seen 08:00)
- casey_headphones: not in any room (away/put away) (last seen 08:00)
- casey_laptop: not in any room (away/put away) (last seen 08:00)
- casey_phone: not in any room (away/put away) (last seen 08:00)
- casey_sunglasses: not in any room (away/put away) (last seen 08:00)
- chair_1: bedroom_2 (last seen 08:00)
- chair_10: dining (last seen 08:00)
- chair_2: dining (last seen 08:00)
- chair_3: dining (last seen 08:00)
- chair_4: dining (last seen 08:00)
- chair_5: dining (last seen 08:00)
- chair_6: dining (last seen 08:00)
- chair_7: living_room (last seen 08:00)
- chair_8: living_room (last seen 08:00)
- chair_9: dining (last seen 08:00)
- cup_1: dining_room (last seen 08:00)
- cup_2: kitchen (last seen 08:00)
- cup_3: dining_room (last seen 08:00)
- cup_4: not in any room (away/put away) (last seen 08:00)
- fridge_1: not in any room (away/put away) (last seen 08:00)
- jordan_keys: not in any room (away/put away) (last seen 08:00)
- jordan_phone: not in any room (away/put away) (last seen 08:00)
- jordan_sunglasses: not in any room (away/put away) (last seen 08:00)
- jordan_wallet: not in any room (away/put away) (last seen 08:00)
- oven_1: not in any room (away/put away) (last seen 08:00)
- potted_plant_1: living_room (last seen 08:00)
- potted_plant_10: living_room (last seen 08:00)
- potted_plant_11: living_room (last seen 08:00)
- potted_plant_12: living_room (last seen 08:00)
- potted_plant_13: living_room (last seen 08:00)
- potted_plant_14: living_room (last seen 08:00)
- potted_plant_15: living_room (last seen 08:00)
- potted_plant_16: living_room (last seen 08:00)
- potted_plant_17: living_room (last seen 08:00)
- potted_plant_2: living_room (last seen 08:00)
- potted_plant_3: living_room (last seen 08:00)
- potted_plant_4: living_room (last seen 08:00)
- potted_plant_5: living_room (last seen 08:00)
- potted_plant_6: living_room (last seen 08:00)
- potted_plant_7: living_room (last seen 08:00)
- potted_plant_8: living_room (last seen 08:00)
- potted_plant_9: living_room (last seen 08:00)
- remote_control_1: living_room (last seen 08:00)
- stool_1: kitchen (last seen 08:00)
- stool_2: kitchen (last seen 08:00)
- tv_1: not in any room (away/put away) (last seen 08:00)
- vase_1: dining_room (last seen 08:00)

Current time: 21:00

Question: which room is casey_laptop in right now? Options: bathroom_1, bathroom_2, bedroom_1, bedroom_2, dining, dining_room, kitchen, living_room, toilet, elsewhere
```

**MODEL RESPONSE:**
- action: `answer`   answer: `elsewhere`   confidence: 0.86   est_p_moved: nan
- reason: casey_laptop was last seen away/put away and there is no newer observation; laptops are commonly kept out of rooms when not in use, so the best current guess is elsewhere. Memory may be stale, but not enough to justify a resense for this. 

**GROUND TRUTH:** true room = `living_room`  →  answer ✗ WRONG  (object HAD moved since snapshot)

---

## Episode 3  [roommates / A2 / cup_1 / Δt=4h]

**PROMPT (what the model saw):**
```
You are a household robot's decision module. Answer location questions about objects in the house. 'elsewhere' means the object is not in any room (taken out of the house, or put away out of sight). You have a memory of past observations. You may either ANSWER from memory (action='answer') or RESENSE the object (action='resense') — resensing costs one look from a limited daily sensing budget and returns the object's true current room, so use it only when your memory is likely stale. Either way, fill 'answer' with your best guess of the CURRENT room.

---

Household: a shared house: three adult roommates

Your memory of the house:
- alex_headphones: not in any room (away/put away) (last seen 08:00)
- alex_keys: not in any room (away/put away) (last seen 08:00)
- alex_laptop: not in any room (away/put away) (last seen 08:00)
- alex_phone: kitchen (last seen 08:00)
- alex_wallet: not in any room (away/put away) (last seen 08:00)
- bottle_1: kitchen (last seen 08:00)
- bottle_2: not in any room (away/put away) (last seen 08:00)
- casey_headphones: not in any room (away/put away) (last seen 08:00)
- casey_laptop: not in any room (away/put away) (last seen 08:00)
- casey_phone: not in any room (away/put away) (last seen 08:00)
- casey_sunglasses: not in any room (away/put away) (last seen 08:00)
- chair_1: bedroom_2 (last seen 08:00)
- chair_10: dining (last seen 08:00)
- chair_2: dining (last seen 08:00)
- chair_3: dining (last seen 08:00)
- chair_4: dining (last seen 08:00)
- chair_5: dining (last seen 08:00)
- chair_6: dining (last seen 08:00)
- chair_7: living_room (last seen 08:00)
- chair_8: living_room (last seen 08:00)
- chair_9: dining (last seen 08:00)
- cup_1: dining_room (last seen 08:00)
- cup_2: kitchen (last seen 08:00)
- cup_3: dining_room (last seen 08:00)
- cup_4: not in any room (away/put away) (last seen 08:00)
- fridge_1: not in any room (away/put away) (last seen 08:00)
- jordan_keys: not in any room (away/put away) (last seen 08:00)
- jordan_phone: not in any room (away/put away) (last seen 08:00)
- jordan_sunglasses: not in any room (away/put away) (last seen 08:00)
- jordan_wallet: not in any room (away/put away) (last seen 08:00)
- oven_1: not in any room (away/put away) (last seen 08:00)
- potted_plant_1: living_room (last seen 08:00)
- potted_plant_10: living_room (last seen 08:00)
- potted_plant_11: living_room (last seen 08:00)
- potted_plant_12: living_room (last seen 08:00)
- potted_plant_13: living_room (last seen 08:00)
- potted_plant_14: living_room (last seen 08:00)
- potted_plant_15: living_room (last seen 08:00)
- potted_plant_16: living_room (last seen 08:00)
- potted_plant_17: living_room (last seen 08:00)
- potted_plant_2: living_room (last seen 08:00)
- potted_plant_3: living_room (last seen 08:00)
- potted_plant_4: living_room (last seen 08:00)
- potted_plant_5: living_room (last seen 08:00)
- potted_plant_6: living_room (last seen 08:00)
- potted_plant_7: living_room (last seen 08:00)
- potted_plant_8: living_room (last seen 08:00)
- potted_plant_9: living_room (last seen 08:00)
- remote_control_1: living_room (last seen 08:00)
- stool_1: kitchen (last seen 08:00)
- stool_2: kitchen (last seen 08:00)
- tv_1: not in any room (away/put away) (last seen 08:00)
- vase_1: dining_room (last seen 08:00)

Current time: 12:00

Question: which room is cup_1 in right now? Options: bathroom_1, bathroom_2, bedroom_1, bedroom_2, dining, dining_room, kitchen, living_room, toilet, elsewhere
```

**MODEL RESPONSE:**
- action: `answer`   answer: `dining_room`   confidence: 0.93   est_p_moved: nan
- reason: cup_1 was last seen in the dining_room at 08:00, and there is no newer information suggesting it moved. It is a stable household item, so memory is likely still valid.

**GROUND TRUTH:** true room = `living_room`  →  answer ✗ WRONG  (object HAD moved since snapshot)

---

## Episode 4  [roommates / A2 / cup_1 / Δt=9h]

**PROMPT (what the model saw):**
```
You are a household robot's decision module. Answer location questions about objects in the house. 'elsewhere' means the object is not in any room (taken out of the house, or put away out of sight). You have a memory of past observations. You may either ANSWER from memory (action='answer') or RESENSE the object (action='resense') — resensing costs one look from a limited daily sensing budget and returns the object's true current room, so use it only when your memory is likely stale. Either way, fill 'answer' with your best guess of the CURRENT room.

---

Household: a shared house: three adult roommates

Your memory of the house:
- alex_headphones: not in any room (away/put away) (last seen 08:00)
- alex_keys: not in any room (away/put away) (last seen 08:00)
- alex_laptop: not in any room (away/put away) (last seen 08:00)
- alex_phone: kitchen (last seen 08:00)
- alex_wallet: not in any room (away/put away) (last seen 08:00)
- bottle_1: kitchen (last seen 08:00)
- bottle_2: not in any room (away/put away) (last seen 08:00)
- casey_headphones: not in any room (away/put away) (last seen 08:00)
- casey_laptop: not in any room (away/put away) (last seen 08:00)
- casey_phone: not in any room (away/put away) (last seen 08:00)
- casey_sunglasses: not in any room (away/put away) (last seen 08:00)
- chair_1: bedroom_2 (last seen 08:00)
- chair_10: dining (last seen 08:00)
- chair_2: dining (last seen 08:00)
- chair_3: dining (last seen 08:00)
- chair_4: dining (last seen 08:00)
- chair_5: dining (last seen 08:00)
- chair_6: dining (last seen 08:00)
- chair_7: living_room (last seen 08:00)
- chair_8: living_room (last seen 08:00)
- chair_9: dining (last seen 08:00)
- cup_1: dining_room (last seen 08:00)
- cup_2: kitchen (last seen 08:00)
- cup_3: dining_room (last seen 08:00)
- cup_4: not in any room (away/put away) (last seen 08:00)
- fridge_1: not in any room (away/put away) (last seen 08:00)
- jordan_keys: not in any room (away/put away) (last seen 08:00)
- jordan_phone: not in any room (away/put away) (last seen 08:00)
- jordan_sunglasses: not in any room (away/put away) (last seen 08:00)
- jordan_wallet: not in any room (away/put away) (last seen 08:00)
- oven_1: not in any room (away/put away) (last seen 08:00)
- potted_plant_1: living_room (last seen 08:00)
- potted_plant_10: living_room (last seen 08:00)
- potted_plant_11: living_room (last seen 08:00)
- potted_plant_12: living_room (last seen 08:00)
- potted_plant_13: living_room (last seen 08:00)
- potted_plant_14: living_room (last seen 08:00)
- potted_plant_15: living_room (last seen 08:00)
- potted_plant_16: living_room (last seen 08:00)
- potted_plant_17: living_room (last seen 08:00)
- potted_plant_2: living_room (last seen 08:00)
- potted_plant_3: living_room (last seen 08:00)
- potted_plant_4: living_room (last seen 08:00)
- potted_plant_5: living_room (last seen 08:00)
- potted_plant_6: living_room (last seen 08:00)
- potted_plant_7: living_room (last seen 08:00)
- potted_plant_8: living_room (last seen 08:00)
- potted_plant_9: living_room (last seen 08:00)
- remote_control_1: living_room (last seen 08:00)
- stool_1: kitchen (last seen 08:00)
- stool_2: kitchen (last seen 08:00)
- tv_1: not in any room (away/put away) (last seen 08:00)
- vase_1: dining_room (last seen 08:00)

Current time: 17:00

Question: which room is cup_1 in right now? Options: bathroom_1, bathroom_2, bedroom_1, bedroom_2, dining, dining_room, kitchen, living_room, toilet, elsewhere
```

**MODEL RESPONSE:**
- action: `answer`   answer: `dining_room`   confidence: 0.86   est_p_moved: nan
- reason: cup_1 was last seen in the dining_room at 08:00, and there is no evidence it has moved since then. Tableware often stays where it was placed, so memory is likely still valid.

**GROUND TRUTH:** true room = `living_room`  →  answer ✗ WRONG  (object HAD moved since snapshot)

---

## Episode 5  [roommates / A2 / cup_1 / Δt=13h]

**PROMPT (what the model saw):**
```
You are a household robot's decision module. Answer location questions about objects in the house. 'elsewhere' means the object is not in any room (taken out of the house, or put away out of sight). You have a memory of past observations. You may either ANSWER from memory (action='answer') or RESENSE the object (action='resense') — resensing costs one look from a limited daily sensing budget and returns the object's true current room, so use it only when your memory is likely stale. Either way, fill 'answer' with your best guess of the CURRENT room.

---

Household: a shared house: three adult roommates

Your memory of the house:
- alex_headphones: not in any room (away/put away) (last seen 08:00)
- alex_keys: not in any room (away/put away) (last seen 08:00)
- alex_laptop: not in any room (away/put away) (last seen 08:00)
- alex_phone: kitchen (last seen 08:00)
- alex_wallet: not in any room (away/put away) (last seen 08:00)
- bottle_1: kitchen (last seen 08:00)
- bottle_2: not in any room (away/put away) (last seen 08:00)
- casey_headphones: not in any room (away/put away) (last seen 08:00)
- casey_laptop: not in any room (away/put away) (last seen 08:00)
- casey_phone: not in any room (away/put away) (last seen 08:00)
- casey_sunglasses: not in any room (away/put away) (last seen 08:00)
- chair_1: bedroom_2 (last seen 08:00)
- chair_10: dining (last seen 08:00)
- chair_2: dining (last seen 08:00)
- chair_3: dining (last seen 08:00)
- chair_4: dining (last seen 08:00)
- chair_5: dining (last seen 08:00)
- chair_6: dining (last seen 08:00)
- chair_7: living_room (last seen 08:00)
- chair_8: living_room (last seen 08:00)
- chair_9: dining (last seen 08:00)
- cup_1: dining_room (last seen 08:00)
- cup_2: kitchen (last seen 08:00)
- cup_3: dining_room (last seen 08:00)
- cup_4: not in any room (away/put away) (last seen 08:00)
- fridge_1: not in any room (away/put away) (last seen 08:00)
- jordan_keys: not in any room (away/put away) (last seen 08:00)
- jordan_phone: not in any room (away/put away) (last seen 08:00)
- jordan_sunglasses: not in any room (away/put away) (last seen 08:00)
- jordan_wallet: not in any room (away/put away) (last seen 08:00)
- oven_1: not in any room (away/put away) (last seen 08:00)
- potted_plant_1: living_room (last seen 08:00)
- potted_plant_10: living_room (last seen 08:00)
- potted_plant_11: living_room (last seen 08:00)
- potted_plant_12: living_room (last seen 08:00)
- potted_plant_13: living_room (last seen 08:00)
- potted_plant_14: living_room (last seen 08:00)
- potted_plant_15: living_room (last seen 08:00)
- potted_plant_16: living_room (last seen 08:00)
- potted_plant_17: living_room (last seen 08:00)
- potted_plant_2: living_room (last seen 08:00)
- potted_plant_3: living_room (last seen 08:00)
- potted_plant_4: living_room (last seen 08:00)
- potted_plant_5: living_room (last seen 08:00)
- potted_plant_6: living_room (last seen 08:00)
- potted_plant_7: living_room (last seen 08:00)
- potted_plant_8: living_room (last seen 08:00)
- potted_plant_9: living_room (last seen 08:00)
- remote_control_1: living_room (last seen 08:00)
- stool_1: kitchen (last seen 08:00)
- stool_2: kitchen (last seen 08:00)
- tv_1: not in any room (away/put away) (last seen 08:00)
- vase_1: dining_room (last seen 08:00)

Current time: 21:00

Question: which room is cup_1 in right now? Options: bathroom_1, bathroom_2, bedroom_1, bedroom_2, dining, dining_room, kitchen, living_room, toilet, elsewhere
```

**MODEL RESPONSE:**
- action: `answer`   answer: `dining_room`   confidence: 0.86   est_p_moved: nan
- reason: cup_1 was last seen in the dining_room at 08:00, and there is no newer information suggesting it moved. This is a relatively stable household object, so memory is likely still valid.

**GROUND TRUTH:** true room = `living_room`  →  answer ✗ WRONG  (object HAD moved since snapshot)

---
