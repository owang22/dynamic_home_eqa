# p_b8c2 — The 18:30 cook: pan at half past, snacks on the counter, remote never moves

The kitchen evidence is unambiguous about timing. The pan is in the cupboard at 18:00 (one sighting) and on the counter at 19:00 (two sightings); the pot is in the cupboard at 18:00 and on the counter at the same time; the kitchen knife is in the drawer at 18:00 and on the counter at 19:00. Cooking begins at roughly 18:30, not 17:50. Before that, the kitchen is quiet. After 19:30 the pan returns to the cupboard.

The snack bowl tells a different story from the coffee-table documents. It is in the cupboard at 03:00, on the counter at 18:00 (two sightings), and on the counter at 20:00 (three sightings). It never appears on the coffee table. The TV block (roughly 19:30–22:00) is anchored by the snack bowl on the kitchen counter, not the living room. The remote, meanwhile, is on the tv_stand every single time the robot looks (4/4 sighted days, one receptacle). It does not migrate to the coffee table.

The guitar is in the bedroom at 18:00 (on the floor) and on the couch at 21:00, suggesting Marco moves it to the living room for an evening session after dinner.

This document is refuted if the pan is on the counter before 18:15, if the snack bowl is found on the coffee table during TV hours, or if the remote is sighted off the tv_stand.

```json
{
 "claims": [
  {
   "claim": "The pan is still in the cupboard at 18:00 before cooking starts",
   "target": "pan_shared",
   "expect": "cupboard_k1",
   "days": "both",
   "from": 17.5,
   "to": 18.5
  },
  {
   "claim": "The pan is on the counter during the cooking window",
   "target": "pan_shared",
   "expect": "counter_k1",
   "days": "both",
   "from": 18.5,
   "to": 19.5
  },
  {
   "claim": "The snack bowl is on the kitchen counter during evening TV",
   "target": "snack_bowl_shared",
   "expect": "counter_k1",
   "days": "both",
   "from": 19.5,
   "to": 21
  },
  {
   "claim": "The remote stays on the tv stand during evening TV",
   "target": "remote_shared",
   "expect": "tv_stand_l1",
   "days": "both",
   "from": 19.5,
   "to": 22
  },
  {
   "claim": "The kitchen knife is on the counter during the cooking window",
   "target": "kitchen_knife_shared",
   "expect": "counter_k1",
   "days": "both",
   "from": 18.5,
   "to": 19.5
  }
 ],
 "targets": {
  "pan_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 18.5,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 18.5,
    "to": 19.5,
    "at": "counter_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 19.5,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "usually"
   }
  ],
  "pot_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 18.5,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 18.5,
    "to": 19.5,
    "at": "counter_k1",
    "chance": "sometimes"
   },
   {
    "days": "both",
    "from": 19.5,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "usually"
   }
  ],
  "kitchen_knife_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 18.5,
    "at": "drawer_k_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 18.5,
    "to": 19.5,
    "at": "counter_k1",
    "chance": "sometimes"
   },
   {
    "days": "both",
    "from": 19.5,
    "to": 24,
    "at": "drawer_k_k1",
    "chance": "usually"
   }
  ],
  "snack_bowl_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 17.5,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 17.5,
    "to": 22,
    "at": "counter_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 22,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "sometimes"
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
  "guitar_marco": [
   {
    "days": "both",
    "from": 0,
    "to": 20,
    "at": "bedroom_floor_b1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 20,
    "to": 23,
    "at": "couch_l1",
    "chance": "sometimes"
   }
  ],
  "class:towel": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "towel_rack_ba1",
    "chance": "almost_always"
   }
  ]
 }
}
```
