# p_f7b3 — Evening entertainment: snacks at the kitchen table, speaker on the couch, remote migrates at 22

The evening routine (roughly 20:00–23:00) has a specific spatial pattern. The snack bowl is on the kitchen table during TV time, not on the couch as some documents predict. The speaker moves from the bookshelf to the couch when the women settle in to watch TV or listen to music (Ines's hobby). The remote stays on the TV stand through most of the evening but ends up on the coffee table by 22:00. The blanket is on the couch during the early evening and shifts to the coffee table by 21:00. Elena's yoga mat is on the coffee table in the early morning (6–8h, for her yoga practice) and stored in the wardrobe by 18:00. The shopping bag sits in the pantry shelf most of the time but appears on the kitchen counter in the evening (19:00), suggesting grocery unpacking. This document is distinguished by placing the snack bowl at the kitchen table and the speaker on the couch during evening hours, and by the remote's late-evening migration to the coffee table.

What would refute it: If the snack bowl is found on the couch during 20–22h, or the speaker is on the bookshelf during 20–22h, or the remote is on the coffee table before 22:00, or the yoga mat is in the wardrobe at 07:00.

```json
{
 "claims": [
  {
   "claim": "The snack bowl is on the kitchen table during evening TV",
   "target": "snack_bowl_shared",
   "expect": "kitchen_table_k1",
   "days": "both",
   "from": 20,
   "to": 22
  },
  {
   "claim": "The speaker is on the couch during evening entertainment",
   "target": "speaker_shared",
   "expect": "couch_l1",
   "days": "both",
   "from": 20,
   "to": 22
  },
  {
   "claim": "The remote is on the coffee table after 22:00",
   "target": "remote_shared",
   "expect": "coffee_table_l1",
   "days": "both",
   "from": 22,
   "to": 23
  },
  {
   "claim": "Elena's yoga mat is on the coffee table in the early morning",
   "target": "yoga_mat_elena",
   "expect": "coffee_table_l1",
   "days": "both",
   "from": 6,
   "to": 8
  }
 ],
 "targets": {
  "snack_bowl_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 20,
    "to": 22.5,
    "at": "kitchen_table_k1",
    "chance": "almost_always"
   },
   {
    "days": "both",
    "from": 2,
    "to": 6,
    "at": "sink_k1",
    "chance": "sometimes"
   }
  ],
  "speaker_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "bookshelf_l1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 20,
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
    "from": 22,
    "to": 24,
    "at": "coffee_table_l1",
    "chance": "sometimes"
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
    "from": 21,
    "to": 23,
    "at": "coffee_table_l1",
    "chance": "sometimes"
   }
  ],
  "yoga_mat_elena": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "wardrobe_b1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 6,
    "to": 8,
    "at": "coffee_table_l1",
    "chance": "almost_always"
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
    "days": "both",
    "from": 18,
    "to": 20,
    "at": "counter_k1",
    "chance": "sometimes"
   }
  ]
 }
}
```
