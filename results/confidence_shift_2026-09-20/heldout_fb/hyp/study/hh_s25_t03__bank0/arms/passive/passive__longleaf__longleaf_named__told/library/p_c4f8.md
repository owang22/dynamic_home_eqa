# p_c4f8 — Evening wind-down: remote migrates TV stand to coffee table to floor; blanket and snacks follow

The evening TV routine is a three-stage migration that the sightings confirm clearly. The remote rests at tv_stand_l1 from the time the residents get up until about 20:30 (sightings at 03:00 and 18:00). At 21:00 it is at coffee_table_l1 (active viewing, one of the residents holding it or setting it on the table). By 22:00 it has dropped to floor_l_l1 (TV winding down, remote tossed aside). On weekends the remote stays at tv_stand_l1 longer (sighting at 23:00 still at tv_stand), suggesting a later or shorter TV session.

The blanket follows a similar but offset pattern: it is on couch_l1 throughout the day (03:00, 14:00, 18:00 on weekdays; 16:00 on weekends) and migrates to coffee_table_l1 in the evening (22:00 on weekdays, 21:00 and 23:00 on weekends). The snack bowl is at sink_k1 or cupboard_k1 at rest and appears at coffee_table_l1 during the 21:00–22:30 TV window (sightings at 21:00 and 22:00×3 on weekdays).

What sets this apart from p_8a6b and p_9f4a: I place the remote at coffee_table_l1 specifically at 21:00 (the active viewing hour) and at floor_l_l1 at 22:00+ (post-TV), rather than a broad 20:30–22:30 coffee_table window. The blanket moves to the coffee table at 21:00+ on weekends (not 20:00), matching the weekend 21:00 and 23:00 sightings.

What would refute this: the remote at tv_stand_l1 at 21:30 on a weekday (it should be at the coffee table), or the blanket on the couch at 22:30 on a weekend (it should be on the coffee table).

```json
{
 "claims": [
  {
   "claim": "The remote is on the coffee table during the active evening TV window on weekdays",
   "target": "remote_shared",
   "expect": "coffee_table_l1",
   "days": "weekday",
   "from": 20.5,
   "to": 22
  },
  {
   "claim": "The remote is on the living room floor after TV ends on weekdays",
   "target": "remote_shared",
   "expect": "floor_l_l1",
   "days": "weekday",
   "from": 22,
   "to": 23.5
  },
  {
   "claim": "The blanket is on the coffee table during weekend evenings",
   "target": "blanket_shared",
   "expect": "coffee_table_l1",
   "days": "weekend",
   "from": 21,
   "to": 23.5
  },
  {
   "claim": "The snack bowl is on the coffee table during the evening TV window",
   "target": "snack_bowl_shared",
   "expect": "coffee_table_l1",
   "days": "both",
   "from": 21,
   "to": 22.5
  }
 ],
 "targets": {
  "class:remote": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "tv_stand_l1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 20.5,
    "to": 22,
    "at": "coffee_table_l1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 22,
    "to": 23.5,
    "at": "floor_l_l1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 20.5,
    "to": 22.5,
    "at": "coffee_table_l1",
    "chance": "sometimes"
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
    "days": "weekday",
    "from": 21.5,
    "to": 23.5,
    "at": "coffee_table_l1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 21,
    "to": 23.5,
    "at": "coffee_table_l1",
    "chance": "usually"
   }
  ],
  "class:snack_bowl": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "sink_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 20.5,
    "to": 22.5,
    "at": "coffee_table_l1",
    "chance": "usually"
   }
  ],
  "class:cushion": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "couch_l1",
    "chance": "usually"
   }
  ],
  "class:tissue_box": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "coffee_table_l1",
    "chance": "usually"
   }
  ],
  "class:candle": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "coffee_table_l1",
    "chance": "usually"
   }
  ],
  "class:lamp": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "side_table_l1",
    "chance": "usually"
   }
  ],
  "class:board_game": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "bookshelf_l1",
    "chance": "usually"
   }
  ],
  "glasses_omar": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "nightstand_b1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 20.5,
    "to": 22.5,
    "at": "armchair_l1",
    "chance": "sometimes"
   }
  ],
  "glasses_marco": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "nightstand_b1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 22,
    "to": 23.5,
    "at": "coffee_table_l1",
    "chance": "sometimes"
   }
  ]
 }
}
```
