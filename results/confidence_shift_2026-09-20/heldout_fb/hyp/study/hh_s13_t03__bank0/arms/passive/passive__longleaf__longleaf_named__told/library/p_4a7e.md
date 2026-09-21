# p_4a7e — Weekend 9:00 Breakfast and 12:00 Hana Shower

On weekends the kitchen wakes at 9:00, not 7:00. Both residents have a slow breakfast together: Priya's bowl and mug are at the kitchen table at 9:00 (bowl_priya sighted there 3 times, mug_priya 2 times), and Hana's bowl and mug are there too (bowl_hana at 9:00 and 10:00, mug_hana at 9:00). By 10:00 the mugs are heading to the dish rack. Then Hana showers around 12:00 — her towel is at the bathroom shelf 7 times at the 12:00 weekend pass, the single strongest single-hour towel signal in the entire log. The towel goes back to the rack by 13:00.

What sets this apart: p_9b2d captures the 9:00 brunch window but its bowl_priya claim (for 3, against 5) is being diluted by the 10:00 pass where the bowl is back in the cupboard. This document narrows the bowl window to 9–10 and adds the 12:00 shower, which no other document addresses. p_e5f0 says "Hana sleeps in until 10:00" but places brunch at 11:00–13:00, which is too late for the 9:00 bowl and mug sightings.

What would refute it: if bowl_priya is at the cupboard at 9:00 on multiple weekend mornings, or if towel_hana is at the towel rack (not the shelf) at 12:00 on a weekend.

```json
{
 "claims": [
  {
   "claim": "Priya's bowl is on the kitchen table at 9:00 on a weekend for breakfast",
   "target": "bowl_priya",
   "expect": "kitchen_table_k1",
   "days": "weekend",
   "from": 9,
   "to": 10
  },
  {
   "claim": "Hana's towel is on the bathroom shelf at 12:00 on a weekend because she is in the shower",
   "target": "towel_hana",
   "expect": "bathroom_shelf_ba1",
   "days": "weekend",
   "from": 11,
   "to": 13
  },
  {
   "claim": "Priya's mug is on the kitchen table at 9:00 on a weekend for morning tea",
   "target": "mug_priya",
   "expect": "kitchen_table_k1",
   "days": "weekend",
   "from": 9,
   "to": 10
  }
 ],
 "targets": {
  "bowl_priya": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 7,
    "to": 9,
    "at": "kitchen_table_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 9,
    "to": 10,
    "at": "kitchen_table_k1",
    "chance": "usually"
   }
  ],
  "bowl_hana": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 9,
    "to": 11,
    "at": "kitchen_table_k1",
    "chance": "usually"
   }
  ],
  "mug_priya": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 7,
    "to": 9,
    "at": "kitchen_table_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 9,
    "to": 10,
    "at": "kitchen_table_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 21,
    "to": 23,
    "at": "coffee_table_l1",
    "chance": "usually"
   }
  ],
  "mug_hana": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 9,
    "to": 10,
    "at": "kitchen_table_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 20,
    "to": 22,
    "at": "coffee_table_l1",
    "chance": "sometimes"
   }
  ],
  "towel_hana": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "towel_rack_ba1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 7,
    "to": 10,
    "at": "bathroom_shelf_ba1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 11,
    "to": 13,
    "at": "bathroom_shelf_ba1",
    "chance": "almost_always"
   }
  ]
 }
}
```
