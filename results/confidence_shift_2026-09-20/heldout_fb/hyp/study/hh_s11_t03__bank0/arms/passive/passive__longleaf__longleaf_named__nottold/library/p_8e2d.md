# p_8e2d — Priya's 15:00 Afternoon Yoga; Mat on the Living Room Floor

Priya is retired and keeps a flexible daily rhythm. The robot's passes place her yoga mat on floor_l_l1 at 15:00 on weekdays (two sightings) and at 20:00 on weekends (one sighting). In the pre-dawn passes the mat is in wardrobe_b2 (three sightings at 03:00 on weekdays, two on weekends), and by 18:00 on weekdays it is back in wardrobe_b2. This rules out the 06:00 morning-yoga hypothesis (p_c9d4) and instead places the session in the mid-afternoon on weekdays and the early evening on weekends. Priya's morning walk (weekday 07:00–09:00) takes her out with the dog leash and keys, but the yoga mat stays in the wardrobe until the afternoon session.

This document is distinguished from p_c9d4 (morning yoga at 06:00 — no sightings support that window) and from p_a3f7 (which places the mat in wardrobe_b2 all week, ignoring the 15:00 floor sightings). The key prediction: the mat is on the living room floor at 15:00 on a weekday, not at 06:00.

What would refute it: a weekday sighting of yoga_mat_priya on floor_l_l1 before 13:00, or a weekday sighting at 15:00 that finds the mat in wardrobe_b2.

```json
{
 "claims": [
  {
   "claim": "Priya's yoga mat is on the living room floor during her weekday afternoon yoga session",
   "target": "yoga_mat_priya",
   "expect": "floor_l_l1",
   "days": "weekday",
   "from": 14,
   "to": 17
  },
  {
   "claim": "Priya's yoga mat is on the living room floor during her weekend evening yoga session",
   "target": "yoga_mat_priya",
   "expect": "floor_l_l1",
   "days": "weekend",
   "from": 19,
   "to": 21
  },
  {
   "claim": "Priya's yoga mat is in the wardrobe before her weekday yoga session",
   "target": "yoga_mat_priya",
   "expect": "wardrobe_b2",
   "days": "weekday",
   "from": 7,
   "to": 14
  },
  {
   "claim": "The dog leash is out of the house during Priya's weekday morning walk",
   "target": "dog_leash_shared",
   "expect": "OUT_OF_HOUSE",
   "days": "weekday",
   "from": 7,
   "to": 9
  }
 ],
 "targets": {
  "yoga_mat_priya": [
   {
    "days": "both",
    "from": 0,
    "to": 14,
    "at": "wardrobe_b2",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 14,
    "to": 17,
    "at": "floor_l_l1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 17,
    "to": 24,
    "at": "wardrobe_b2",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 14,
    "to": 19,
    "at": "wardrobe_b2",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 19,
    "to": 21,
    "at": "floor_l_l1",
    "chance": "sometimes"
   },
   {
    "days": "weekend",
    "from": 21,
    "to": 24,
    "at": "wardrobe_b2",
    "chance": "usually"
   }
  ],
  "keys_priya": [
   {
    "days": "both",
    "from": 0,
    "to": 7,
    "at": "entry_table_e1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 7,
    "to": 9,
    "at": "OUT_OF_HOUSE",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 9,
    "to": 14,
    "at": "entry_table_e1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 14,
    "to": 17,
    "at": "OUT_OF_HOUSE",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 17,
    "to": 24,
    "at": "entry_table_e1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 7,
    "to": 9,
    "at": "OUT_OF_HOUSE",
    "chance": "sometimes"
   },
   {
    "days": "weekend",
    "from": 9,
    "to": 24,
    "at": "entry_table_e1",
    "chance": "usually"
   }
  ],
  "dog_leash_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 7,
    "at": "entry_hook_e1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 7,
    "to": 9,
    "at": "OUT_OF_HOUSE",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 9,
    "to": 24,
    "at": "entry_hook_e1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 7,
    "to": 9,
    "at": "OUT_OF_HOUSE",
    "chance": "sometimes"
   },
   {
    "days": "weekend",
    "from": 9,
    "to": 24,
    "at": "entry_hook_e1",
    "chance": "usually"
   }
  ],
  "jacket_priya": [
   {
    "days": "both",
    "from": 0,
    "to": 7,
    "at": "entry_hook_e1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 7,
    "to": 9,
    "at": "OUT_OF_HOUSE",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 9,
    "to": 14,
    "at": "entry_hook_e1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 14,
    "to": 17,
    "at": "OUT_OF_HOUSE",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 17,
    "to": 24,
    "at": "entry_hook_e1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 7,
    "to": 9,
    "at": "OUT_OF_HOUSE",
    "chance": "sometimes"
   },
   {
    "days": "weekend",
    "from": 9,
    "to": 24,
    "at": "entry_hook_e1",
    "chance": "usually"
   }
  ],
  "class:dog_bowl": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "floor_k_k1",
    "chance": "almost_always"
   }
  ],
  "class:skincare": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "bathroom_shelf_ba1",
    "chance": "almost_always"
   }
  ]
 }
}
```
