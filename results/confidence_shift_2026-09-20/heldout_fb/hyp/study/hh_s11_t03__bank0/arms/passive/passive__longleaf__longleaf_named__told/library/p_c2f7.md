# p_c2f7 — Guest Evening Revised; Snacks Arrive at 21:00, Blanket Already on the Couch (fork of p_4e8c)

The parent p_4e8c correctly places the blanket on the couch and the remote in active use during the guest evening, but its snack-bowl claim (coffee_table_l1, 19:00–21:00) has gone against 3 times since the last call. The sightings show the snack bowl at counter_k1 at 19:00 (x3) and only at coffee_table_l1 at 21:00 (x1). The guests arrive around 18:00, but the snack bowl does not migrate to the coffee table until the TV-and-snacking phase at 21:00, after the initial socialising and any light dinner. The blanket, by contrast, is already on the couch by 19:00 (sighting confirms) and does not need to "move" from the coffee table—it lives there.

What changed from the parent: the snack_bowl_shared block at coffee_table_l1 shifts from 18:00–22:00 to 20:00–23:00 (matching the 21:00 sighting). The blanket block at couch_l1 is extended to 18:00–23:00 (the 19:00 couch sighting supports this, and the blanket's default is the couch per the aggregate evidence). The remote block at floor_l_l1 is narrowed to 20:00–22:00 (the 03:00 floor sightings are from the early-morning post-shift TV, not the guest evening; the 18:00 TV-stand sighting means the remote is still resting when guests arrive).

This document is refuted if the snack bowl is at coffee_table_l1 at 19:00, or if the blanket is at coffee_table_l1 at 19:00–21:00, or if the remote is at floor_l_l1 at 18:00.

```json
{
 "claims": [
  {
   "claim": "The blanket is on the couch during the guest evening, not the coffee table",
   "target": "blanket_shared",
   "expect": "couch_l1",
   "days": "both",
   "from": 18,
   "to": 22
  },
  {
   "claim": "The snack bowl is still on the kitchen counter at 19:00 during the guest evening, not yet on the coffee table",
   "target": "snack_bowl_shared",
   "expect": "counter_k1",
   "days": "both",
   "from": 18,
   "to": 20
  },
  {
   "claim": "The snack bowl moves to the coffee table by 21:00 for the guest TV-and-snacking phase",
   "target": "snack_bowl_shared",
   "expect": "coffee_table_l1",
   "days": "both",
   "from": 21,
   "to": 23
  },
  {
   "claim": "The remote is on the TV stand at 18:00 when guests arrive, not yet in active use",
   "target": "remote_shared",
   "expect": "tv_stand_l1",
   "days": "both",
   "from": 18,
   "to": 20
  }
 ],
 "targets": {
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
    "from": 18,
    "to": 23,
    "at": "couch_l1",
    "chance": "almost_always"
   }
  ],
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
    "from": 20,
    "to": 22,
    "at": "floor_l_l1",
    "chance": "sometimes"
   }
  ],
  "snack_bowl_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "counter_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 20,
    "to": 23,
    "at": "coffee_table_l1",
    "chance": "sometimes"
   }
  ],
  "dog_toy_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "floor_l_l1",
    "chance": "usually"
   }
  ],
  "glass_priya": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "sink_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 18,
    "to": 21,
    "at": "dining_table_d1",
    "chance": "sometimes"
   },
   {
    "days": "both",
    "from": 21,
    "to": 23,
    "at": "counter_k1",
    "chance": "sometimes"
   }
  ],
  "cushion_1_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "couch_l1",
    "chance": "almost_always"
   }
  ],
  "cushion_2_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "armchair_l1",
    "chance": "almost_always"
   }
  ]
 }
}
```
