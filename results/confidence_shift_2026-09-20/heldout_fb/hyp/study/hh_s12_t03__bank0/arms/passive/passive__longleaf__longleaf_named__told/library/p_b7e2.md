# p_b7e2 — Priya's weekday afternoon: vacuum at 12 and 16:30, guitar on the couch, glasses at the coffee table

Priya's weekday afternoon is a structured sequence. She vacuums the living room at midday (the robot sees the vacuum on floor_l_l1 at 12:00 on three separate weekday passes) and again in the late afternoon (16:00–17:00). Between and after vacuuming, she practises guitar on the couch (sightings at couch_l1 at 13:00 on three weekday passes, versus bedroom_floor_b1 at 03:00 and 18:00). Her reading glasses move to the coffee table in the mid-afternoon (15:00–16:00 sightings) and return to the nightstand around 18:00. The shopping bag sits at the kitchen counter during her 12:00–15:00 errand-prep window (seven weekday sightings at counter_k1 in that span).

This document differs from p_8c1a (retired) by placing the vacuum at 12:00 and 16:30 rather than 16:00–17:00 only, and by adding the guitar-on-couch and glasses-at-coffee-table windows. It differs from p_b8e2 (weight 0.005) by extending the guitar window and adding the glasses block. It differs from p_3a7c (retired, yoga morning) by focusing exclusively on the afternoon.

What would refute this document: the vacuum at entry_floor_e1 during 12:00–13:00 or 16:00–17:30 on a weekday; the guitar at bedroom_floor_b1 at 13:00–15:00 on a weekday; the glasses at the nightstand during 15:00–17:00 on a weekday.

```json
{
 "claims": [
  {
   "claim": "The vacuum is on the living-room floor during Priya's midday cleaning at 12:00 on a weekday",
   "target": "vacuum_cleaner_shared",
   "expect": "floor_l_l1",
   "days": "weekday",
   "from": 12,
   "to": 13
  },
  {
   "claim": "Priya's guitar is on the couch during her mid-afternoon practice at 14:00 on a weekday",
   "target": "guitar_priya",
   "expect": "couch_l1",
   "days": "weekday",
   "from": 13,
   "to": 16
  },
  {
   "claim": "Priya's glasses are on the coffee table at 15:30 on a weekday",
   "target": "glasses_priya",
   "expect": "coffee_table_l1",
   "days": "weekday",
   "from": 15,
   "to": 16.5
  },
  {
   "claim": "The shopping bag is at the kitchen counter during Priya's midday errand window at 13:00 on a weekday",
   "target": "shopping_bag_shared",
   "expect": "counter_k1",
   "days": "weekday",
   "from": 12,
   "to": 15
  },
  {
   "claim": "The vacuum is on the living-room floor during Priya's late-afternoon cleaning at 16:30 on a weekday",
   "target": "vacuum_cleaner_shared",
   "expect": "floor_l_l1",
   "days": "weekday",
   "from": 16,
   "to": 17.5
  }
 ],
 "targets": {
  "vacuum_cleaner_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_floor_e1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 11.5,
    "to": 13,
    "at": "floor_l_l1",
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
    "days": "weekend",
    "from": 10.5,
    "to": 12,
    "at": "floor_l_l1",
    "chance": "sometimes"
   }
  ],
  "guitar_priya": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "bedroom_floor_b1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 12.5,
    "to": 16.5,
    "at": "couch_l1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 18,
    "to": 22,
    "at": "floor_l_l1",
    "chance": "sometimes"
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
    "days": "weekday",
    "from": 14.5,
    "to": 17,
    "at": "coffee_table_l1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 20.5,
    "to": 23,
    "at": "coffee_table_l1",
    "chance": "usually"
   }
  ],
  "shopping_bag_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "pantry_shelf_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 11.5,
    "to": 15.5,
    "at": "counter_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 11.5,
    "to": 14,
    "at": "counter_k1",
    "chance": "sometimes"
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
    "from": 6.5,
    "to": 9,
    "at": "kitchen_table_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 19.5,
    "to": 22,
    "at": "coffee_table_l1",
    "chance": "sometimes"
   }
  ]
 }
}
```
