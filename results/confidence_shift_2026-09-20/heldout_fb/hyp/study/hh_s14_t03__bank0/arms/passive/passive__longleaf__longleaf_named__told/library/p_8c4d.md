# p_8c4d — Weekend Baking: Kitchen Counter Active, Both Home All Day

With both residents home all day, the kitchen sees significantly more activity than on weekdays. Marco bakes in the morning (his stated hobby), pulling the baking tray, mixing bowl, spatula, and kitchen knife onto the counter for a 9:00–12:00 session. Yuki may do a shorter afternoon session (16:00–19:00). Between sessions, the baking tools return to the pantry shelf (tray, bowl) or the drawer (spatula, knife). This contrasts with the weekday documents where only one person is home and baking windows are shorter or absent.

What sets this apart: on weekdays, p_d1e6 and p_5a3d place baking at 7:00–8:30 or 10:00–12:00 with only one resident present. Here both are home, the morning session is longer, and there is a second afternoon session. The counter is the active surface; the pantry shelf and drawer are resting spots.

This is refuted if the baking tray or mixing bowl is found on the pantry shelf during the 9:00–12:00 window (meaning no morning baking), or if the spatula is in the drawer during a window where both residents are in the kitchen.

```json
{
 "claims": [
  {
   "claim": "The baking tray is on the kitchen counter during Marco's weekend morning baking session",
   "target": "baking_tray_shared",
   "expect": "counter_k1",
   "days": "weekend",
   "from": 9,
   "to": 12
  },
  {
   "claim": "The mixing bowl is on the kitchen counter during Marco's weekend morning baking session",
   "target": "mixing_bowl_shared",
   "expect": "counter_k1",
   "days": "weekend",
   "from": 9,
   "to": 12
  },
  {
   "claim": "The spatula is on the kitchen counter during Yuki's weekend afternoon baking",
   "target": "spatula_shared",
   "expect": "counter_k1",
   "days": "weekend",
   "from": 16,
   "to": 19
  },
  {
   "claim": "The kitchen knife is in the drawer between baking sessions on the weekend",
   "target": "kitchen_knife_shared",
   "expect": "drawer_k_k1",
   "days": "weekend",
   "from": 12,
   "to": 16
  }
 ],
 "targets": {
  "baking_tray_shared": [
   {
    "days": "weekend",
    "from": 0,
    "to": 9,
    "at": "pantry_shelf_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 9,
    "to": 12,
    "at": "counter_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 12,
    "to": 16,
    "at": "pantry_shelf_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 16,
    "to": 19,
    "at": "counter_k1",
    "chance": "sometimes"
   },
   {
    "days": "weekend",
    "from": 19,
    "to": 24,
    "at": "pantry_shelf_k1",
    "chance": "usually"
   }
  ],
  "mixing_bowl_shared": [
   {
    "days": "weekend",
    "from": 0,
    "to": 9,
    "at": "pantry_shelf_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 9,
    "to": 12,
    "at": "counter_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 12,
    "to": 16,
    "at": "pantry_shelf_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 16,
    "to": 19,
    "at": "counter_k1",
    "chance": "sometimes"
   },
   {
    "days": "weekend",
    "from": 19,
    "to": 24,
    "at": "pantry_shelf_k1",
    "chance": "usually"
   }
  ],
  "spatula_shared": [
   {
    "days": "weekend",
    "from": 0,
    "to": 9,
    "at": "drawer_k_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 9,
    "to": 12,
    "at": "counter_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 12,
    "to": 16,
    "at": "drawer_k_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 16,
    "to": 19,
    "at": "counter_k1",
    "chance": "sometimes"
   },
   {
    "days": "weekend",
    "from": 19,
    "to": 24,
    "at": "drawer_k_k1",
    "chance": "usually"
   }
  ],
  "kitchen_knife_shared": [
   {
    "days": "weekend",
    "from": 0,
    "to": 9,
    "at": "drawer_k_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 9,
    "to": 12,
    "at": "counter_k1",
    "chance": "sometimes"
   },
   {
    "days": "weekend",
    "from": 12,
    "to": 16,
    "at": "drawer_k_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 16,
    "to": 19,
    "at": "counter_k1",
    "chance": "sometimes"
   },
   {
    "days": "weekend",
    "from": 19,
    "to": 24,
    "at": "drawer_k_k1",
    "chance": "usually"
   }
  ],
  "cutting_board_shared": [
   {
    "days": "weekend",
    "from": 9,
    "to": 12,
    "at": "counter_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 16,
    "to": 19,
    "at": "counter_k1",
    "chance": "sometimes"
   }
  ]
 }
}
```
