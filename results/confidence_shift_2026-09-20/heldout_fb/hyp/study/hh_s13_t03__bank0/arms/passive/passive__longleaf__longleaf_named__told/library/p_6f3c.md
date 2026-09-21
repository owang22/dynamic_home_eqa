# p_6f3c — Morning Bathroom and Kitchen: Shelf at 7, Kitchen Table at 8

The morning routine (06:30–10:00) follows a fixed sequence. Hana showers first: her towel moves from the towel rack to the bathroom shelf at 07:00 and stays there through 10:00, then goes back to the rack by 18:00. She brings her phone to the bathroom (seen on the bathroom shelf at 07:00). Priya shaves: her razor is on the bathroom shelf at 07:00 (three sightings) and back in the sink by 18:00.

In the kitchen, Priya's morning tea is at 07:00–08:00: her mug is on the kitchen table (two sightings at 07:00, four at 08:00). Her bowl is also on the kitchen table at 08:00 (two sightings) — breakfast. By 09:00 the kitchen table is clearing for the day.

This document is distinct from p_5f8c (which covers the towel and razor but at low weight) by adding the phone-in-bathroom detail, the mug and bowl on the kitchen table at 07:00–08:00, and the full morning-to-evening arc for each item.

What would refute this: Hana's towel still on the rack at 09:00, Priya's mug in the pantry at 08:00, or Hana's phone at the nightstand at 07:00.

```json
{
 "claims": [
  {
   "claim": "Hana's towel is on the bathroom shelf at 09:00 on a weekday (shower just finished, still in use)",
   "target": "towel_hana",
   "expect": "bathroom_shelf_ba1",
   "days": "weekday",
   "from": 7,
   "to": 10
  },
  {
   "claim": "Priya's razor is on the bathroom shelf at 07:30 on a weekday (morning shave in progress)",
   "target": "razor_priya",
   "expect": "bathroom_shelf_ba1",
   "days": "weekday",
   "from": 6,
   "to": 9
  },
  {
   "claim": "Priya's mug is on the kitchen table at 08:00 on a weekday (morning tea)",
   "target": "mug_priya",
   "expect": "kitchen_table_k1",
   "days": "weekday",
   "from": 7,
   "to": 9
  },
  {
   "claim": "Hana's phone is on the bathroom shelf at 07:30 on a weekday (brought into the shower)",
   "target": "phone_hana",
   "expect": "bathroom_shelf_ba1",
   "days": "weekday",
   "from": 7,
   "to": 8
  },
  {
   "claim": "Priya's bowl is on the kitchen table at 08:30 on a weekday (breakfast)",
   "target": "bowl_priya",
   "expect": "kitchen_table_k1",
   "days": "weekday",
   "from": 8,
   "to": 9
  }
 ],
 "targets": {
  "towel_hana": [
   {
    "days": "both",
    "from": 0,
    "to": 7,
    "at": "towel_rack_ba1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 7,
    "to": 10,
    "at": "bathroom_shelf_ba1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 10,
    "to": 17,
    "at": "bathroom_shelf_ba1",
    "chance": "sometimes"
   },
   {
    "days": "both",
    "from": 17,
    "to": 24,
    "at": "towel_rack_ba1",
    "chance": "usually"
   }
  ],
  "razor_priya": [
   {
    "days": "both",
    "from": 0,
    "to": 6,
    "at": "sink_ba_ba1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 6,
    "to": 9,
    "at": "bathroom_shelf_ba1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 9,
    "to": 17,
    "at": "bathroom_shelf_ba1",
    "chance": "sometimes"
   },
   {
    "days": "both",
    "from": 17,
    "to": 24,
    "at": "sink_ba_ba1",
    "chance": "usually"
   }
  ],
  "phone_hana": [
   {
    "days": "weekday",
    "from": 0,
    "to": 7,
    "at": "nightstand_b1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 7,
    "to": 8,
    "at": "bathroom_shelf_ba1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 8,
    "to": 17.5,
    "at": "OUT_OF_HOUSE",
    "chance": "almost_always"
   },
   {
    "days": "weekday",
    "from": 17.5,
    "to": 24,
    "at": "nightstand_b1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 0,
    "to": 7,
    "at": "nightstand_b1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 7,
    "to": 9,
    "at": "bathroom_shelf_ba1",
    "chance": "sometimes"
   },
   {
    "days": "weekend",
    "from": 9,
    "to": 24,
    "at": "nightstand_b1",
    "chance": "usually"
   }
  ],
  "mug_priya": [
   {
    "days": "weekday",
    "from": 0,
    "to": 7,
    "at": "pantry_shelf_k1",
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
    "days": "weekday",
    "from": 9,
    "to": 18,
    "at": "kitchen_table_k1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 18,
    "to": 21,
    "at": "sink_k1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 21,
    "to": 23,
    "at": "coffee_table_l1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 23,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "sometimes"
   }
  ],
  "bowl_priya": [
   {
    "days": "weekday",
    "from": 0,
    "to": 8,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 8,
    "to": 9,
    "at": "kitchen_table_k1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 9,
    "to": 18,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 18,
    "to": 21,
    "at": "sink_k1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 21,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "usually"
   }
  ],
  "skincare_hana": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "bathroom_shelf_ba1",
    "chance": "almost_always"
   }
  ],
  "towel_priya": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "towel_rack_ba1",
    "chance": "almost_always"
   }
  ]
 }
}
```
