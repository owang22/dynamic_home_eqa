# p_7a4b — Evening coffee table: remote, blanket, mugs, and glasses settle by 20:30

The living room becomes the evening hub. After dinner is cleared (by 21:30 on weekdays), both residents drift to the couch. The remote moves from the TV stand to the coffee table at 20:00 (confirmed ×1 at 20:00, ×4 at 22:00). Both mugs (Elena's and Priya's) are on the coffee table from 20:00 through 23:00. Priya's glasses (eyewear) are set on the coffee table from 21:00 to 22:30. The blanket is pulled from the couch to the coffee table at 22:00 (×3). At 19:00 the blanket is briefly on the armchair (someone reading before TV). The remote makes a brief return to the TV stand at 21:00 (×1) before settling back on the coffee table at 22:00.

What sets this apart: it predicts the coffee table as the dominant evening receptacle for the remote, both mugs, the blanket, and Priya's glasses simultaneously from 21:00 to 23:00. Documents that put the remote on the TV stand at 22:00, or the mugs at the dining table, or the glasses ON_PERSON, will be contradicted.

Refutation: if the remote is on the TV stand at 22:00 on a weekday (×4 sightings say coffee table), or if mug_elena is at the dining table at 21:00 (sightings say coffee table), or if the blanket is on the couch at 22:00 (sightings say coffee table ×3).

```json
{
 "claims": [
  {
   "claim": "The remote is on the coffee table at 22:00 on a weekday",
   "target": "remote_shared",
   "expect": "coffee_table_l1",
   "days": "weekday",
   "from": 21.5,
   "to": 23
  },
  {
   "claim": "Elena's mug is on the coffee table at 21:00 on a weekday",
   "target": "mug_elena",
   "expect": "coffee_table_l1",
   "days": "weekday",
   "from": 20,
   "to": 22
  },
  {
   "claim": "The blanket is on the coffee table at 22:00 on a weekday",
   "target": "blanket_shared",
   "expect": "coffee_table_l1",
   "days": "weekday",
   "from": 21.5,
   "to": 23
  },
  {
   "claim": "Priya's glasses are on the coffee table at 21:30 on a weekday",
   "target": "glasses_priya",
   "expect": "coffee_table_l1",
   "days": "weekday",
   "from": 21,
   "to": 22.5
  }
 ],
 "targets": {
  "remote_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "tv_stand_l1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 14,
    "to": 16,
    "at": "coffee_table_l1",
    "chance": "sometimes"
   },
   {
    "days": "both",
    "from": 20,
    "to": 23.5,
    "at": "coffee_table_l1",
    "chance": "usually"
   }
  ],
  "mug_elena": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "sink_k1",
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
    "from": 18,
    "to": 23.5,
    "at": "coffee_table_l1",
    "chance": "usually"
   }
  ],
  "mug_priya": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
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
    "from": 14,
    "to": 16,
    "at": "coffee_table_l1",
    "chance": "sometimes"
   },
   {
    "days": "both",
    "from": 20,
    "to": 23,
    "at": "coffee_table_l1",
    "chance": "usually"
   }
  ],
  "blanket_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "couch_l1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 13,
    "to": 15,
    "at": "coffee_table_l1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 19,
    "to": 20,
    "at": "armchair_l1",
    "chance": "sometimes"
   },
   {
    "days": "both",
    "from": 22,
    "to": 23.5,
    "at": "coffee_table_l1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 3,
    "to": 9,
    "at": "armchair_l1",
    "chance": "usually"
   }
  ],
  "glasses_priya": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "nightstand_b1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 7,
    "to": 8,
    "at": "bathroom_shelf_ba1",
    "chance": "sometimes"
   },
   {
    "days": "both",
    "from": 15,
    "to": 18,
    "at": "coffee_table_l1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 20,
    "to": 23,
    "at": "coffee_table_l1",
    "chance": "usually"
   }
  ],
  "fruit_bowl_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "kitchen_table_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 20,
    "to": 23,
    "at": "coffee_table_l1",
    "chance": "sometimes"
   }
  ]
 }
}
```
