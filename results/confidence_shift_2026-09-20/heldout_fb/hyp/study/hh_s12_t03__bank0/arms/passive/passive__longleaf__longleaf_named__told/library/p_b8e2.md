# p_b8e2 — Priya's weekday afternoon: vacuum at noon and 4, guitar on the couch

Priya's weekday afternoon is a working one, not a resting one. Around 12:00 she pulls the vacuum from the entry and cleans the living room (the robot finds it on the living-room floor at 12:00, three sightings). By 13:00 she's sat on the couch with her guitar for a mid-afternoon practice session — the guitar is on the couch at 13:00 (three sightings), not on the bedroom floor. She goes out for errands in this window (the shopping bag is at the kitchen counter from 12:00 to 15:00). In the late afternoon, 16:00–17:30, she vacuums the living room again (the vacuum is on the floor at 16:00 and 17:00). By 18:00 the guitar is back on the bedroom floor and the vacuum is back at the entry.

What sets this apart from p_7ef3 and p_b9e5 (guitar at bedroom_floor_b1 midday): the guitar is on the COUCH at 13:00, not the bedroom floor. The "worst objects" list confirms the mixture predicted bedroom_floor_b1 but found couch_l1 twice on day 6 at 13:00. What sets it apart from p_8c1a (vacuum 16–17:30 only): the vacuum is also out at 12:00–13:00, a second cleaning session. What sets it apart from p_3a7c (retired, yoga morning / guitar afternoon): the yoga mat stays in the wardrobe all day; there is no mat-out window in the evidence.

This is refuted if the guitar is consistently on the bedroom floor at 13:00, or if the vacuum is at the entry at 12:00 (no midday cleaning), or if the yoga mat is on the living-room floor in the morning.

```json
{
 "claims": [
  {
   "claim": "The vacuum is on the living-room floor during Priya's midday cleaning at 12:00",
   "target": "vacuum_cleaner_shared",
   "expect": "floor_l_l1",
   "days": "weekday",
   "from": 12,
   "to": 13
  },
  {
   "claim": "Priya's guitar is on the couch during her mid-afternoon practice at 13:00",
   "target": "guitar_priya",
   "expect": "couch_l1",
   "days": "weekday",
   "from": 12,
   "to": 16
  },
  {
   "claim": "The vacuum is on the living-room floor during Priya's late-afternoon cleaning at 16:30",
   "target": "vacuum_cleaner_shared",
   "expect": "floor_l_l1",
   "days": "weekday",
   "from": 16,
   "to": 17.5
  },
  {
   "claim": "The shopping bag is at the kitchen counter during Priya's midday errand window",
   "target": "shopping_bag_shared",
   "expect": "counter_k1",
   "days": "weekday",
   "from": 12,
   "to": 15
  }
 ],
 "targets": {
  "vacuum_cleaner_shared": [
   {
    "days": "weekday",
    "from": 0,
    "to": 12,
    "at": "entry_floor_e1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 12,
    "to": 13,
    "at": "floor_l_l1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 13,
    "to": 16,
    "at": "entry_floor_e1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 16,
    "to": 17.5,
    "at": "floor_l_l1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 17.5,
    "to": 24,
    "at": "entry_floor_e1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 0,
    "to": 11,
    "at": "entry_floor_e1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 11,
    "to": 12,
    "at": "floor_l_l1",
    "chance": "sometimes"
   },
   {
    "days": "weekend",
    "from": 12,
    "to": 24,
    "at": "entry_floor_e1",
    "chance": "usually"
   }
  ],
  "guitar_priya": [
   {
    "days": "weekday",
    "from": 0,
    "to": 12,
    "at": "bedroom_floor_b1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 12,
    "to": 16,
    "at": "couch_l1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 16,
    "to": 24,
    "at": "bedroom_floor_b1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 0,
    "to": 14,
    "at": "bedroom_floor_b1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 14,
    "to": 18,
    "at": "floor_l_l1",
    "chance": "sometimes"
   },
   {
    "days": "weekend",
    "from": 18,
    "to": 24,
    "at": "bedroom_floor_b1",
    "chance": "usually"
   }
  ],
  "shopping_bag_shared": [
   {
    "days": "weekday",
    "from": 0,
    "to": 12,
    "at": "pantry_shelf_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 12,
    "to": 15,
    "at": "counter_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 15,
    "to": 24,
    "at": "pantry_shelf_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 0,
    "to": 12,
    "at": "pantry_shelf_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 12,
    "to": 15,
    "at": "counter_k1",
    "chance": "sometimes"
   },
   {
    "days": "weekend",
    "from": 15,
    "to": 24,
    "at": "pantry_shelf_k1",
    "chance": "usually"
   }
  ],
  "mug_priya": [
   {
    "days": "both",
    "from": 0,
    "to": 7,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 7,
    "to": 9,
    "at": "kitchen_table_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 9,
    "to": 14,
    "at": "kitchen_table_k1",
    "chance": "sometimes"
   },
   {
    "days": "both",
    "from": 14,
    "to": 21,
    "at": "coffee_table_l1",
    "chance": "sometimes"
   },
   {
    "days": "both",
    "from": 21,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "usually"
   }
  ],
  "yoga_mat_priya": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "wardrobe_b1",
    "chance": "usually"
   }
  ]
 }
}
```
