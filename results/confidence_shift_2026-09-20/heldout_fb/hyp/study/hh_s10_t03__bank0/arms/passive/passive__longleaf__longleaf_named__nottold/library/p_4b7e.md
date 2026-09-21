# p_4b7e — Weekend overnight: thorough cleanup shifts resting spots

On weekends both Yuki and Omar are home all day, and their evening routine ends with a more thorough cleanup than on weekdays. Dishes are washed and placed on the drying rack rather than left soaking in the sink. The pan is put away in the drawer (not merely returned to the cupboard). The spatula goes to the pantry shelf. Omar folds his scarf into the wardrobe instead of leaving it draped on the entry hook. Yuki takes her journal to the bed—she reads before sleeping on weekends. Yuki's phone is at the nightstand, charging overnight. Omar's glasses end up at the bedroom desk, where he was working on something in the evening. Omar's razor is on the bathroom shelf (used during his weekend morning routine, not left at the sink). The snack bowl is in the kitchen sink, left dirty from the evening. The water bottle is at the dish rack (washed and set to dry).

What sets this apart from the weekday overnight documents (p_d41f, p_8c2e): those predict the sink for dirty dishes and the cupboard for the pan. On weekends the cleanup is more complete—dishes are on the rack, the pan is in the drawer, the spatula is in the pantry. The scarf goes to the wardrobe, not the hook. The journal goes to the bed, not the nightstand. These are weekend-specific resting positions that the weekday models do not capture.

What would refute this: If on a weekend morning (02:00–07:00) the pan is found in the cupboard rather than the drawer, or the glasses are at the nightstand rather than the desk, or the scarf is at the entry hook rather than the wardrobe, or the glasses (drinking) are in the sink rather than the dish rack, or the journal is at the nightstand rather than the bed.

```json
{
 "claims": [
  {
   "claim": "Omar's glasses are at the bedroom desk at 03:00 on a weekend (left there after evening desk work)",
   "target": "glasses_omar",
   "expect": "desk_b1",
   "days": "weekend",
   "from": 2,
   "to": 6
  },
  {
   "claim": "Yuki's journal is at the bed at 03:00 on a weekend (she reads in bed before sleeping)",
   "target": "journal_yuki",
   "expect": "bed_b1",
   "days": "weekend",
   "from": 2,
   "to": 6
  },
  {
   "claim": "Omar's drinking glass is on the dish rack at 03:00 on a weekend (washed and dried, not left in the sink)",
   "target": "glass_omar",
   "expect": "dish_rack_k1",
   "days": "weekend",
   "from": 2,
   "to": 6
  },
  {
   "claim": "The shared pan is in the kitchen drawer at 03:00 on a weekend (put away properly, not just in the cupboard)",
   "target": "pan_shared",
   "expect": "drawer_k_k1",
   "days": "weekend",
   "from": 2,
   "to": 6
  },
  {
   "claim": "Omar's scarf is in the wardrobe at 03:00 on a weekend (folded away, not left on the entry hook)",
   "target": "scarf_omar",
   "expect": "wardrobe_b1",
   "days": "weekend",
   "from": 2,
   "to": 6
  }
 ],
 "targets": {
  "glasses_omar": [
   {
    "days": "weekend",
    "from": 0,
    "to": 8,
    "at": "desk_b1",
    "chance": "usually"
   }
  ],
  "journal_yuki": [
   {
    "days": "weekend",
    "from": 0,
    "to": 8,
    "at": "bed_b1",
    "chance": "usually"
   }
  ],
  "phone_yuki": [
   {
    "days": "weekend",
    "from": 0,
    "to": 8,
    "at": "nightstand_b1",
    "chance": "usually"
   }
  ],
  "scarf_omar": [
   {
    "days": "weekend",
    "from": 0,
    "to": 8,
    "at": "wardrobe_b1",
    "chance": "usually"
   }
  ],
  "glass_omar": [
   {
    "days": "weekend",
    "from": 0,
    "to": 8,
    "at": "dish_rack_k1",
    "chance": "usually"
   }
  ],
  "glass_yuki": [
   {
    "days": "weekend",
    "from": 0,
    "to": 8,
    "at": "dish_rack_k1",
    "chance": "usually"
   }
  ],
  "pan_shared": [
   {
    "days": "weekend",
    "from": 0,
    "to": 8,
    "at": "drawer_k_k1",
    "chance": "usually"
   }
  ],
  "spatula_shared": [
   {
    "days": "weekend",
    "from": 0,
    "to": 8,
    "at": "pantry_shelf_k1",
    "chance": "usually"
   }
  ],
  "snack_bowl_shared": [
   {
    "days": "weekend",
    "from": 0,
    "to": 8,
    "at": "sink_k1",
    "chance": "usually"
   }
  ],
  "razor_omar": [
   {
    "days": "weekend",
    "from": 0,
    "to": 8,
    "at": "bathroom_shelf_ba1",
    "chance": "usually"
   }
  ],
  "water_bottle_yuki": [
   {
    "days": "weekend",
    "from": 0,
    "to": 8,
    "at": "dish_rack_k1",
    "chance": "usually"
   }
  ],
  "mug_yuki": [
   {
    "days": "weekend",
    "from": 0,
    "to": 8,
    "at": "sink_k1",
    "chance": "usually"
   }
  ],
  "tablet_omar": [
   {
    "days": "weekend",
    "from": 0,
    "to": 8,
    "at": "nightstand_b1",
    "chance": "usually"
   }
  ],
  "controller_omar": [
   {
    "days": "weekend",
    "from": 0,
    "to": 8,
    "at": "tv_stand_l1",
    "chance": "usually"
   }
  ],
  "blanket_shared": [
   {
    "days": "weekend",
    "from": 0,
    "to": 8,
    "at": "couch_l1",
    "chance": "usually"
   }
  ]
 }
}
```
