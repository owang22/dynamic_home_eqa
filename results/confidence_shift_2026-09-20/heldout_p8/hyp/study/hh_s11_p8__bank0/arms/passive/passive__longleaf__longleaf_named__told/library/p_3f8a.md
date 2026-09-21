# p_3f8a — Sick Day Friday; Friends in the Evening

Hana is home sick on this Friday. She does not leave for her afternoon shift; instead she rests in her bed through the morning and midday, then drifts into the living room in the afternoon where she picks up her guitar and plays while she recovers. Her going-out kit—handbag, jacket, keys, shoes, water bottle—stays at the entry because she never puts it on. Priya keeps her normal rhythm: a morning walk (leash and keys out 7–9), afternoon errands (jacket on, out 14–16), and then home. The evening is the big departure: friends arrive around 18:00. Priya sets the table with the serving dish and extra plates, the puzzle box comes down from the bookshelf for a round of board games, the snack bowl is out on the coffee table, and the blanket migrates from the armchair to the couch where the guests pile in. The remote moves to the coffee table for active group TV. Hana's tablet stays on her bed all day—she is not working, not at the desk, not out of the house.

What sets this document apart: (1) the guitar leaves the bedroom in the afternoon, something no other document predicts; (2) the puzzle box is on the dining table on a weekday evening, which only p_e5f6 approaches (and only on weekends); (3) the serving dish is at the dining table in the evening, matching the mixture's worst-object evidence (predicted cupboard_k1, actually dining_table_d1); (4) Hana's handbag and jacket remain at the entry through the evening hours when the normal documents expect them out of the house with her.

This document is refuted if: the guitar is found in bedroom_floor_b1 during 14–20h on this Friday; the puzzle box is still on the bookshelf at 19:00; the serving dish is in the sink or cupboard during 17–21h; or Hana's handbag/jacket are seen out of the house (meaning she went out despite being "sick").

```json
{
 "claims": [
  {
   "claim": "Hana's guitar is at the armchair in the living room during her sick afternoon",
   "target": "guitar_hana",
   "expect": "armchair_l1",
   "days": "weekday",
   "from": 14,
   "to": 20
  },
  {
   "claim": "The puzzle box is on the dining table for board games with the evening guests",
   "target": "puzzle_box_shared",
   "expect": "dining_table_d1",
   "days": "weekday",
   "from": 18,
   "to": 22
  },
  {
   "claim": "The serving dish is on the dining table while dinner is served to the guests",
   "target": "serving_dish_shared",
   "expect": "dining_table_d1",
   "days": "weekday",
   "from": 17,
   "to": 21
  },
  {
   "claim": "Hana's tablet stays on her bed all day because she is resting and not working",
   "target": "tablet_hana",
   "expect": "bed_b1",
   "days": "weekday",
   "from": 9,
   "to": 15
  },
  {
   "claim": "Hana's handbag remains on the entry floor in the evening because she did not go out",
   "target": "handbag_hana",
   "expect": "entry_floor_e1",
   "days": "weekday",
   "from": 16,
   "to": 22
  }
 ],
 "targets": {
  "guitar_hana": [
   {
    "days": "weekday",
    "from": 0,
    "to": 14,
    "at": "bedroom_floor_b1",
    "chance": "almost_always"
   },
   {
    "days": "weekday",
    "from": 14,
    "to": 22,
    "at": "armchair_l1",
    "chance": "sometimes"
   }
  ],
  "puzzle_box_shared": [
   {
    "days": "weekday",
    "from": 0,
    "to": 17,
    "at": "bookshelf_l1",
    "chance": "almost_always"
   },
   {
    "days": "weekday",
    "from": 17,
    "to": 23,
    "at": "dining_table_d1",
    "chance": "sometimes"
   }
  ],
  "serving_dish_shared": [
   {
    "days": "weekday",
    "from": 0,
    "to": 16,
    "at": "sink_k1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 16,
    "to": 22,
    "at": "dining_table_d1",
    "chance": "usually"
   }
  ],
  "snack_bowl_shared": [
   {
    "days": "weekday",
    "from": 0,
    "to": 17,
    "at": "cupboard_k1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 17,
    "to": 23,
    "at": "coffee_table_l1",
    "chance": "usually"
   }
  ],
  "tablet_hana": [
   {
    "days": "weekday",
    "from": 0,
    "to": 24,
    "at": "bed_b1",
    "chance": "usually"
   }
  ],
  "phone_hana": [
   {
    "days": "weekday",
    "from": 0,
    "to": 24,
    "at": "bed_b1",
    "chance": "sometimes"
   }
  ],
  "handbag_hana": [
   {
    "days": "weekday",
    "from": 0,
    "to": 24,
    "at": "entry_floor_e1",
    "chance": "almost_always"
   }
  ],
  "jacket_hana": [
   {
    "days": "weekday",
    "from": 0,
    "to": 24,
    "at": "entry_hook_e1",
    "chance": "almost_always"
   }
  ],
  "keys_hana": [
   {
    "days": "weekday",
    "from": 0,
    "to": 24,
    "at": "entry_table_e1",
    "chance": "almost_always"
   }
  ],
  "blanket_shared": [
   {
    "days": "weekday",
    "from": 0,
    "to": 17,
    "at": "armchair_l1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 17,
    "to": 23,
    "at": "couch_l1",
    "chance": "sometimes"
   }
  ],
  "remote_shared": [
   {
    "days": "weekday",
    "from": 0,
    "to": 17,
    "at": "floor_l_l1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 17,
    "to": 23,
    "at": "coffee_table_l1",
    "chance": "sometimes"
   }
  ]
 }
}
```
