# p_4e7a — Hana's Tablet Stays Home; Midnight Kitchen Cook

Hana works afternoon-to-night shifts, home in the morning and out from roughly 13:40 to 23:00 on weekdays. In the morning she sits at desk_b1 with her notebook for a work or study block, but her tablet is not a work device — it is a bedside charger that stays on nightstand_b1 all day and all night. She leaves for work without it, and it is still there when she comes home. When she walks in at 23:00 she goes straight to the kitchen and cooks a late meal; the resident sightings place her in the kitchen at 00:00, 02:00, 04:00, and 06:00 on day 1, which is consistent with a long midnight cooking-and-eating session. This document sets itself apart from p_b8c2 and p_a1b2 (which put the tablet at the desk) and from p_c3d4 (which puts the tablet out of the house with her): the tablet never leaves nightstand_b1.

What would refute this document: a sighting of tablet_hana at desk_b1 or OUT_OF_HOUSE during her weekday shift; a look at nightstand_b1 during 14–22 h that finds the tablet missing; a resident look showing Hana in the bedroom or living room at 00:00–06:00 instead of the kitchen.

```json
{
 "claims": [
  {
   "claim": "Hana's tablet stays on her nightstand while she is at work",
   "target": "tablet_hana",
   "expect": "nightstand_b1",
   "days": "weekday",
   "from": 14,
   "to": 22
  },
  {
   "claim": "The pan is on the kitchen counter during Hana's midnight cook",
   "target": "pan_shared",
   "expect": "counter_k1",
   "days": "weekday",
   "from": 23.5,
   "to": 24
  },
  {
   "claim": "Hana's notebook is at her desk during her morning work block",
   "target": "notebook_hana",
   "expect": "desk_b1",
   "days": "weekday",
   "from": 8,
   "to": 12
  }
 ],
 "targets": {
  "tablet_hana": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "nightstand_b1",
    "chance": "almost_always"
   }
  ],
  "notebook_hana": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "desk_b1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 7,
    "to": 13,
    "at": "desk_b1",
    "chance": "almost_always"
   }
  ],
  "pan_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "counter_k1",
    "chance": "usually"
   }
  ],
  "kitchen_knife_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "counter_k1",
    "chance": "usually"
   }
  ],
  "pot_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "counter_k1",
    "chance": "usually"
   }
  ],
  "guitar_hana": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "bedroom_floor_b1",
    "chance": "almost_always"
   }
  ],
  "camera_priya": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "bookshelf_l1",
    "chance": "almost_always"
   }
  ],
  "yoga_mat_priya": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "wardrobe_b2",
    "chance": "almost_always"
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
  ],
  "class:skincare": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "bathroom_shelf_ba1",
    "chance": "almost_always"
   }
  ],
  "class:bowl": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "almost_always"
   }
  ]
 }
}
```
