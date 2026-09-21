# p_c9f1 — Weekend evening: no 19:00 cooking; serving dish at the table 20:00–22:00; remote stays at the TV stand

On weekends the kitchen does not fire up at 19:00. The pan stays in the cupboard, the spatula only appears at the counter at 20:00 (a single sighting, perhaps a quick reheat or garnish), and the recipe book lingers at the pantry shelf until 20:00. Instead of individual plates and glasses being set, the shared serving dish is placed at the dining table from 20:00 through 22:00 (four weekend sightings across three hours), suggesting a family-style or lighter meal. Marco's water bottle is at the dish rack at 20:00 on weekends, not the dining table. The remote never migrates: it is at the TV stand at 23:00 on weekends, unlike the weekday pattern where it ends up on the floor or coffee table. The blanket does move to the coffee table from 21:00 onward on weekends, consistent with a wind-down that starts a bit earlier than on weekdays.

What sets this apart from p_b7e3 (the weekday cooking fork): this document is the weekend complement. It predicts the pan in the cupboard at 19:00 on a Saturday, the serving dish at the dining table at 20:00–22:00 on weekends, and the remote at the TV stand at 23:00 on weekends. What would refute it: the pan on the counter at 19:00 on a Saturday, the remote on the floor at 22:00 on a Sunday, or the serving dish still in the cupboard at 21:00 on a weekend.

```json
{
 "claims": [
  {
   "claim": "The pan remains in the cupboard at 19:00 on weekends (no weekend cooking at that hour)",
   "target": "pan_shared",
   "expect": "cupboard_k1",
   "days": "weekend",
   "from": 18.5,
   "to": 19.5
  },
  {
   "claim": "The serving dish is at the dining table during the weekend evening meal",
   "target": "serving_dish_shared",
   "expect": "dining_table_d1",
   "days": "weekend",
   "from": 20,
   "to": 22
  },
  {
   "claim": "The remote remains at the TV stand at 23:00 on weekends",
   "target": "remote_shared",
   "expect": "tv_stand_l1",
   "days": "weekend",
   "from": 22.5,
   "to": 24
  },
  {
   "claim": "Marco's water bottle is at the dish rack at 20:00 on weekends, not the dining table",
   "target": "water_bottle_marco",
   "expect": "dish_rack_k1",
   "days": "weekend",
   "from": 19.5,
   "to": 21
  }
 ],
 "targets": {
  "pan_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "almost_always"
   }
  ],
  "serving_dish_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 20,
    "to": 22,
    "at": "dining_table_d1",
    "chance": "usually"
   }
  ],
  "remote_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "tv_stand_l1",
    "chance": "almost_always"
   }
  ],
  "water_bottle_marco": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "dish_rack_k1",
    "chance": "usually"
   }
  ],
  "spatula_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "drawer_k_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 19.5,
    "to": 21,
    "at": "counter_k1",
    "chance": "rarely"
   }
  ],
  "class:blanket": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "couch_l1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 21,
    "to": 23.5,
    "at": "coffee_table_l1",
    "chance": "usually"
   }
  ]
 }
}
```
