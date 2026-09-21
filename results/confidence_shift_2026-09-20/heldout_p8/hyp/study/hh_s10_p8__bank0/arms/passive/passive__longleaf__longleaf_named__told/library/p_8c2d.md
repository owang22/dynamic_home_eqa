# p_8c2d — Remote on the side table until evening; kitchen tools rest at the sink, not in hands

The remote lives on the side table for most of the day and moves to the TV stand only when evening viewing begins. The four weekday passes show it at side_table_l1 at 00:00, 08:00, and 16:00, and at tv_stand_l1 at 18:00. The mixture's worst-object list flags two errors where it predicted tv_stand_l1 but the remote was actually at side_table_l1 at 00:00. This document corrects that by keeping the remote at the side table from 00:00 to 18:00.

The second correction targets the mixture's habit of predicting kitchen objects as ON_PERSON during 9–17h on weekdays. Both residents are at work during this window (Yuki 8:00–17:30, Omar 1:40–23:00), so no one is in the kitchen to hold a pan, plate, or glass. The per-object evidence confirms: the pan, spatula, knife, and Yuki's plate and mug are at sink_k1; Omar's glass is at counter_k1; Omar's mug is at kitchen_table_k1. These are resting positions, not in-use positions. The 16:00 pass shows Omar's glass at kitchen_table_k1 and his plate at dish_rack_k1, suggesting a mid-afternoon tidy or dish run by Yuki before she leaves.

What sets this apart from the other documents: the explicit side-table window for the remote (0–18h) and the rejection of ON_PERSON for kitchen objects during 9–17h. Refutation: finding the remote at tv_stand_l1 before 17:00, or any kitchen object ON_PERSON during 9–17h on a weekday.

```json
{
 "claims": [
  {
   "claim": "The remote is on the side table at 10:00 on a weekday because evening TV has not started yet",
   "target": "remote_shared",
   "expect": "side_table_l1",
   "days": "weekday",
   "from": 8,
   "to": 16
  },
  {
   "claim": "The pan is at the kitchen sink at 14:00 on a weekday because no one is home to cook",
   "target": "pan_shared",
   "expect": "sink_k1",
   "days": "weekday",
   "from": 9,
   "to": 17
  },
  {
   "claim": "Omar's glass is on the kitchen counter at 10:00 on a weekday, resting from the morning",
   "target": "glass_omar",
   "expect": "counter_k1",
   "days": "weekday",
   "from": 8,
   "to": 16
  }
 ],
 "targets": {
  "remote_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 18,
    "at": "side_table_l1",
    "chance": "almost_always"
   },
   {
    "days": "both",
    "from": 18,
    "to": 24,
    "at": "tv_stand_l1",
    "chance": "usually"
   }
  ],
  "class:pan": [
   {
    "days": "weekday",
    "from": 9,
    "to": 17,
    "at": "sink_k1",
    "chance": "usually"
   }
  ],
  "class:spatula": [
   {
    "days": "weekday",
    "from": 9,
    "to": 17,
    "at": "sink_k1",
    "chance": "usually"
   }
  ],
  "class:kitchen_knife": [
   {
    "days": "weekday",
    "from": 9,
    "to": 17,
    "at": "sink_k1",
    "chance": "usually"
   }
  ],
  "class:plate": [
   {
    "days": "weekday",
    "from": 9,
    "to": 17,
    "at": "sink_k1",
    "chance": "sometimes"
   }
  ],
  "class:mug": [
   {
    "days": "weekday",
    "from": 9,
    "to": 17,
    "at": "sink_k1",
    "chance": "sometimes"
   }
  ],
  "glass_omar": [
   {
    "days": "weekday",
    "from": 0,
    "to": 16,
    "at": "counter_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 16,
    "to": 18,
    "at": "kitchen_table_k1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 18,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "sometimes"
   }
  ],
  "class:toiletry_bag": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "bathroom_shelf_ba1",
    "chance": "almost_always"
   }
  ],
  "class:book": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "nightstand_b1",
    "chance": "almost_always"
   }
  ]
 }
}
```
