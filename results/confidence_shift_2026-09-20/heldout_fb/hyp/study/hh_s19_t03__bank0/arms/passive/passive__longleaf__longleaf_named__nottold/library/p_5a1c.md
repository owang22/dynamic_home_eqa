# p_5a1c — The evening wind-down: guitar from the wardrobe, TV on the couch, 21:00 ironing in Omar's room

The evening has three overlapping threads. First, Marco's guitar is in the wardrobe at 03:00 but on the bedroom floor by 18:00, so he takes it out around 17:30–18:00 for evening practice (his hobby). Second, Omar's headphones are at desk_o1 at 14:00 but on the couch by 18:00, and his book is on the couch at 18:00 (nightstand at 03:00), so the couch is the evening relaxation spot for both residents. Third, the iron and ironing board are in storage at 03:00, 09:00, and 18:00, but at bed_b2 (Omar's room) at 21:00 — Omar irons in the late evening, around 20:30–22:00, after dinner and TV.

This document sets itself apart from p_789a (which keeps the guitar in the bedroom during TV but does not specify the wardrobe-to-floor transition) and from p_1e9b (which focuses on running shoes rather than the ironing routine). The ironing-at-21:00 prediction is unique to this document; no other document places the iron in bedroom_2.

What would refute this: the iron still in storage at 21:00 on a weekday, or the guitar still in the wardrobe at 19:00 (meaning Marco does not practice in the evening).

```json
{
 "claims": [
  {
   "claim": "The guitar is on the bedroom floor during the evening",
   "target": "guitar_marco",
   "expect": "bedroom_floor_b1",
   "days": "both",
   "from": 18,
   "to": 22
  },
  {
   "claim": "The iron is in Omar's bedroom during the late-evening ironing session",
   "target": "iron_shared",
   "expect": "bed_b2",
   "days": "both",
   "from": 20.5,
   "to": 22.5
  },
  {
   "claim": "Omar's headphones are on the couch during evening relaxation",
   "target": "headphones_omar",
   "expect": "couch_l1",
   "days": "both",
   "from": 18,
   "to": 22
  },
  {
   "claim": "The ironing board is in Omar's bedroom during the late-evening ironing session",
   "target": "ironing_board_shared",
   "expect": "bed_b2",
   "days": "both",
   "from": 20.5,
   "to": 22.5
  },
  {
   "claim": "The guitar is in the wardrobe overnight",
   "target": "guitar_marco",
   "expect": "wardrobe_b1",
   "days": "both",
   "from": 2,
   "to": 5
  }
 ],
 "targets": {
  "guitar_marco": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "wardrobe_b1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 17.5,
    "to": 23,
    "at": "bedroom_floor_b1",
    "chance": "usually"
   }
  ],
  "iron_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "storage_shelf_s1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 20,
    "to": 23,
    "at": "bed_b2",
    "chance": "usually"
   }
  ],
  "ironing_board_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "storage_floor_s1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 20,
    "to": 23,
    "at": "bed_b2",
    "chance": "usually"
   }
  ],
  "headphones_omar": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "desk_o1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 9,
    "to": 16,
    "at": "desk_o1",
    "chance": "almost_always"
   },
   {
    "days": "both",
    "from": 17,
    "to": 23,
    "at": "couch_l1",
    "chance": "usually"
   }
  ],
  "book_omar": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "nightstand_b2",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 17,
    "to": 23,
    "at": "couch_l1",
    "chance": "sometimes"
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
    "from": 19.5,
    "to": 22.5,
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
   }
  ]
 }
}
```
