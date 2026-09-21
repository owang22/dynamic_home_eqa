# p_e7c4 — The 22:00 coffee table: snacks, remote, and blanket migrate at night

The evening entertainment routine in this house is a migration, not a static arrangement. During the day the remote sits on the TV stand, the blanket on the couch, and the snack bowl in the kitchen (cupboard, counter, or sink). After 20:00 the residents gather in the living room and the objects follow: the blanket and remote move to the coffee table, the snack bowl comes out of the cupboard and lands on the coffee table by 22:00, and the speaker is already on the couch. The 21:00 patrol catches the migration in progress (the snack bowl is split across four receptacles), but by 22:00–23:00 the coffee table is the anchor. On weekends the migration is later and less complete: at 21:00 the remote is still on the TV stand and the snack bowl in the cupboard.

What sets this apart: p_a3f7 puts the snack bowl on the couch (0 for, 12 against); p_7d4e puts it on the kitchen table (1 for, 17 against); p_6d3b and p_8a3e put it on the coffee table but with windows that are too narrow or too early. This document places it at coffee_table_l1 specifically from 22:00, matching the two 23:00 weekday sightings and the weekend 22:00 sighting.

What would refute it: a look at coffee_table_l1 during 22–23 h that finds the snack bowl, remote, or blanket elsewhere (couch, kitchen table, TV stand), or a look at the kitchen cupboard at 22:00 that still finds the snack bowl there.

```json
{
 "claims": [
  {
   "claim": "The snack bowl is on the coffee table during late-evening TV",
   "target": "snack_bowl_shared",
   "expect": "coffee_table_l1",
   "days": "both",
   "from": 22,
   "to": 23
  },
  {
   "claim": "The remote is on the coffee table during the weekday evening TV window",
   "target": "remote_shared",
   "expect": "coffee_table_l1",
   "days": "weekday",
   "from": 21.5,
   "to": 23
  },
  {
   "claim": "The blanket is on the coffee table during the weekday evening TV window",
   "target": "blanket_shared",
   "expect": "coffee_table_l1",
   "days": "weekday",
   "from": 21.5,
   "to": 23
  },
  {
   "claim": "The speaker is on the couch during evening entertainment",
   "target": "speaker_shared",
   "expect": "couch_l1",
   "days": "both",
   "from": 20.5,
   "to": 22.5
  },
  {
   "claim": "Ines's water bottle is at the kitchen table during dinner",
   "target": "water_bottle_ines",
   "expect": "kitchen_table_k1",
   "days": "both",
   "from": 18.5,
   "to": 20
  }
 ],
 "targets": {
  "snack_bowl_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 21,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 22,
    "to": 23.5,
    "at": "coffee_table_l1",
    "chance": "usually"
   }
  ],
  "remote_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 20,
    "at": "tv_stand_l1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 21,
    "to": 23,
    "at": "coffee_table_l1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 21,
    "to": 23,
    "at": "tv_stand_l1",
    "chance": "sometimes"
   }
  ],
  "blanket_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 20,
    "at": "couch_l1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 21,
    "to": 23,
    "at": "coffee_table_l1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 21,
    "to": 23,
    "at": "couch_l1",
    "chance": "sometimes"
   }
  ],
  "speaker_shared": [
   {
    "days": "both",
    "from": 20,
    "to": 23,
    "at": "couch_l1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "couch_l1",
    "chance": "usually"
   }
  ],
  "mug_elena": [
   {
    "days": "both",
    "from": 0,
    "to": 18,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 19,
    "to": 21,
    "at": "kitchen_table_k1",
    "chance": "sometimes"
   }
  ],
  "water_bottle_elena": [
   {
    "days": "both",
    "from": 18.5,
    "to": 20,
    "at": "kitchen_table_k1",
    "chance": "sometimes"
   },
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "dish_rack_k1",
    "chance": "usually"
   }
  ],
  "water_bottle_ines": [
   {
    "days": "both",
    "from": 18.5,
    "to": 20,
    "at": "kitchen_table_k1",
    "chance": "sometimes"
   },
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "dish_rack_k1",
    "chance": "usually"
   }
  ],
  "glass_ines": [
   {
    "days": "both",
    "from": 18,
    "to": 21,
    "at": "kitchen_table_k1",
    "chance": "sometimes"
   },
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "sink_k1",
    "chance": "usually"
   }
  ],
  "glass_elena": [
   {
    "days": "both",
    "from": 19,
    "to": 21,
    "at": "kitchen_table_k1",
    "chance": "sometimes"
   },
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "sink_k1",
    "chance": "usually"
   }
  ]
 }
}
```
