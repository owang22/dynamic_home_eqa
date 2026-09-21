# p_d6a1 — Priya's weekday: desk_b1 mornings, kitchen midday, guitar afternoon

This document models Priya's full weekday arc in detail, which several existing documents only partially capture.

Morning (6:00–9:00): Priya is in the bedroom, then moves to the kitchen for breakfast. Her glasses, headphones, and pen are at desk_b1. Her glass is at the sink or desk. She has her morning walk (the dog leash is at the entry hook; the dog toy stays on the living room floor — the dog is not walked, it stays in). Her water bottle is at the dish rack or pantry shelf.

Midday (9:00–15:00): Priya is at desk_b1 working or reading. Her glasses are at desk_b1 (seen there at 08:00, 10:00, 12:00, 14:00, 16:00). Her headphones are at desk_b1. Her pen is at desk_b1. Her glass is at desk_b1 (seen there 00:00–10:00). Her water bottle shifts to the kitchen sink (seen at sink_k1 at 10:00, 12:00, 14:00, 16:00). She is in the kitchen at 14:00 per the resident sighting.

Afternoon (15:00–18:00): Priya may do errands, but the evidence shows her water bottle still at the sink at 16:00, so she is home. Her guitar is on the bedroom floor all day (found 6/6 during 9–17h). She does not take the guitar out.

Evening (18:00–22:00): Priya is in the kitchen (seen at 18:00, 20:00) or the living room. Her glasses return to the nightstand (seen at 18:00, 20:00, 22:00). Her water bottle is at the dish rack or dining table.

What sets this hypothesis apart: Priya is **home** during the entire weekday (no out-of-house blocks for her personal items); her workspace is desk_b1 specifically; her water bottle is at the sink midday (not out); the guitar never leaves the bedroom floor.

Refutation: if Priya's glasses, headphones, or pen are found out of the house on a weekday; if the guitar is found off the bedroom floor during 9–17h; if the water bottle is found out of the house during 10–16h on a weekday.

```json
{
 "claims": [
  {
   "claim": "Priya's glasses are at desk_b1 during weekday midday",
   "target": "glasses_priya",
   "expect": "desk_b1",
   "days": "weekday",
   "from": 10,
   "to": 16
  },
  {
   "claim": "Priya's guitar is on the bedroom floor during weekday midday",
   "target": "guitar_priya",
   "expect": "bedroom_floor_b1",
   "days": "weekday",
   "from": 10,
   "to": 16
  },
  {
   "claim": "Priya's water bottle is at the kitchen sink during weekday midday",
   "target": "water_bottle_priya",
   "expect": "sink_k1",
   "days": "weekday",
   "from": 11,
   "to": 16
  },
  {
   "claim": "Priya's headphones are at desk_b1 during weekday midday",
   "target": "headphones_priya",
   "expect": "desk_b1",
   "days": "weekday",
   "from": 10,
   "to": 16
  }
 ],
 "targets": {
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
    "from": 8,
    "to": 17,
    "at": "desk_b1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 19,
    "to": 23,
    "at": "nightstand_b1",
    "chance": "almost_always"
   }
  ],
  "headphones_priya": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "desk_b1",
    "chance": "almost_always"
   }
  ],
  "pen_priya": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "desk_b1",
    "chance": "almost_always"
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
    "days": "weekday",
    "from": 8,
    "to": 17,
    "at": "desk_b1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 20,
    "to": 22,
    "at": "dining_table_d1",
    "chance": "sometimes"
   }
  ],
  "guitar_priya": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "bedroom_floor_b1",
    "chance": "almost_always"
   }
  ],
  "water_bottle_priya": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "dish_rack_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 10,
    "to": 17,
    "at": "sink_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 20,
    "to": 22,
    "at": "dining_table_d1",
    "chance": "sometimes"
   }
  ],
  "book_priya": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "nightstand_b1",
    "chance": "almost_always"
   }
  ],
  "phone_priya": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "nightstand_b1",
    "chance": "usually"
   }
  ],
  "yoga_mat_priya": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "wardrobe_b1",
    "chance": "almost_always"
   }
  ],
  "sunglasses_priya": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_table_e1",
    "chance": "usually"
   }
  ],
  "keys_priya": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_table_e1",
    "chance": "usually"
   }
  ],
  "wallet_priya": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_table_e1",
    "chance": "usually"
   }
  ],
  "shoes_priya": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "shoe_rack_e1",
    "chance": "almost_always"
   }
  ],
  "jacket_priya": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_hook_e1",
    "chance": "usually"
   }
  ]
 }
}
```
