# p_8c5a — Ines stays home for lunch at the kitchen table; pen and laptop stay in the office

Ines does not leave the house for lunch on weekdays. Her pen (pen_ines) remains at the office desk (desk_o1) throughout the midday window (12:00–14:00), confirming she is still in the office room or at least did not take her pen with her. Her glass (glass_ines) is at the kitchen table (kitchen_table_k1) at 12:00–13:00, indicating she eats lunch at the kitchen table. Her water bottle (water_bottle_ines) is at the kitchen sink (sink_k1) at 14:00, where she refills it after lunch before returning to the desk.

Her laptop (laptop_ines) is at the desk at 10:00 (before lunch) and at 16:00–17:00 (after lunch), but is not on the desk during the 12:00–15:00 window — it is on her lap, at the kitchen table, or on the office floor. Her mug (mug_ines) is at the desk during the afternoon work block (14:00–17:00) and at the kitchen table in the morning (07:00).

This directly contradicts p_c9d4, which claims Ines's laptop and keys are OUT_OF_HOUSE at midday. The pen-at-desk evidence (4 finds at desk_o1 during 9–17 h, including the midday window) and the glass-at-kitchen-table sightings (12:00, 13:00) support staying home.

What sets this apart: p_c9d4 predicts Ines is out 12–14 h; this document predicts she is in the kitchen at the table 12–13 h with her pen still on the desk. p_a3f7 and p_d1e5 do not specify midday behaviour.

Refutation: if pen_ines is found OUT_OF_HOUSE or at the kitchen table at 12:00–14:00 on multiple weekdays, the "stays home" claim fails. If glass_ines is at the sink (not the kitchen table) at 12:00–13:00, the lunch-at-the-table prediction fails. If laptop_ines is at the desk at 13:00, the "laptop off-desk during lunch" prediction fails.

```json
{
 "claims": [
  {
   "claim": "Ines's pen is on the office desk at 13:00 on weekdays",
   "target": "pen_ines",
   "expect": "desk_o1",
   "days": "weekday",
   "from": 12,
   "to": 14
  },
  {
   "claim": "Ines's glass is at the kitchen table at 12:30 on weekdays",
   "target": "glass_ines",
   "expect": "kitchen_table_k1",
   "days": "weekday",
   "from": 12,
   "to": 13.5
  },
  {
   "claim": "Ines's water bottle is at the kitchen sink at 14:00 on weekdays",
   "target": "water_bottle_ines",
   "expect": "sink_k1",
   "days": "weekday",
   "from": 14,
   "to": 15
  },
  {
   "claim": "Ines's keys are on the entry table at 13:00 on weekdays",
   "target": "keys_ines",
   "expect": "entry_table_e1",
   "days": "weekday",
   "from": 12,
   "to": 14
  }
 ],
 "targets": {
  "pen_ines": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "desk_o1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 12,
    "to": 14,
    "at": "desk_o1",
    "chance": "usually"
   }
  ],
  "glass_ines": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "sink_k1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 12,
    "to": 13.5,
    "at": "kitchen_table_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 19,
    "to": 21,
    "at": "kitchen_table_k1",
    "chance": "usually"
   }
  ],
  "water_bottle_ines": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "dish_rack_k1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 9,
    "to": 17.5,
    "at": "desk_o1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 14,
    "to": 15,
    "at": "sink_k1",
    "chance": "sometimes"
   },
   {
    "days": "both",
    "from": 19,
    "to": 21,
    "at": "kitchen_table_k1",
    "chance": "sometimes"
   }
  ],
  "laptop_ines": [
   {
    "days": "weekday",
    "from": 10,
    "to": 11,
    "at": "desk_o1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 12,
    "to": 15,
    "at": "floor_o_o1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 16,
    "to": 17.5,
    "at": "desk_o1",
    "chance": "usually"
   }
  ],
  "mug_ines": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "sometimes"
   },
   {
    "days": "both",
    "from": 7,
    "to": 8.5,
    "at": "kitchen_table_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 14,
    "to": 17.5,
    "at": "desk_o1",
    "chance": "usually"
   }
  ],
  "keys_ines": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_table_e1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 12,
    "to": 14,
    "at": "entry_table_e1",
    "chance": "usually"
   }
  ]
 }
}
```
