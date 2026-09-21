# p_8c1e — Evening entertainment revised: coffee-table snacks, bed yoga mat (fork of p_f7b3)

Fork of p_f7b3. Two corrections based on the latest claim tallies and the "worst objects" list:

1. **Snack bowl moved from kitchen_table (20–22h) to coffee_table (22–23h).** The parent's kitchen_table claim scored for 1, against 3. The 23:00 pass caught the snack bowl at coffee_table twice; the 21:00 pass was split three ways (kitchen_table, cupboard, coffee_table). The kitchen_table is where it is *brought out* around 20:00, but by the time the women are settled watching TV (22:00+) it has migrated to the coffee table alongside the remote and blanket.

2. **Yoga mat moved from coffee_table (6–8h) to bed_b1 (6–8h).** The parent's coffee_table claim scored for 1, against 2. The "worst objects" list explicitly flags: "yoga_mat_elena: predicted coffee_table_l1, actually bed_b1 — 2x." The 03:00 and 07:00 passes both caught the mat at bed_b1 (x1 each) alongside coffee_table and floor_l_l1. The bed is the more reliable early-morning location; the mat is unrolled on the floor for the actual practice (7:00–7:45) but stored at the bedside.

The speaker-on-couch claim (for 3, against 0) and the remote-on-coffee-table-after-22 claim (for 3, against 2) are retained unchanged — they are the strongest claims in the parent.

```json
{
 "claims": [
  {
   "claim": "The snack bowl is on the coffee table at 23:00",
   "target": "snack_bowl_shared",
   "expect": "coffee_table_l1",
   "days": "both",
   "from": 22,
   "to": 23
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
   "claim": "Elena's yoga mat is at the bed in the early morning",
   "target": "yoga_mat_elena",
   "expect": "bed_b1",
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
    "to": 21,
    "at": "kitchen_table_k1",
    "chance": "sometimes"
   },
   {
    "days": "both",
    "from": 22,
    "to": 23,
    "at": "coffee_table_l1",
    "chance": "usually"
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
    "from": 21,
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
    "from": 21,
    "to": 23,
    "at": "coffee_table_l1",
    "chance": "usually"
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
    "at": "bed_b1",
    "chance": "sometimes"
   },
   {
    "days": "both",
    "from": 7,
    "to": 7.75,
    "at": "floor_l_l1",
    "chance": "sometimes"
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
    "from": 19,
    "to": 20,
    "at": "counter_k1",
    "chance": "sometimes"
   }
  ]
 }
}
```
