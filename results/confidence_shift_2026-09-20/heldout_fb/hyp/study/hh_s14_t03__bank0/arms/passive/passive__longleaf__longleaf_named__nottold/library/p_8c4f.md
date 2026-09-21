# p_8c4f — Marco's Morning at Home: Shower, Journal at the Desk, Vitamins at the Counter

Marco wakes around 6:30 on weekdays. His glasses start the night on the nightstand; he takes them into the shower around 8:30 (bathroom shelf) and then sets them on the coffee table while he gets ready. His journal is at the bedroom desk from the early morning through the midday writing session (03:00 and 12:00 sightings both at desk_b1; 9–17 h looks at the desk find it 2-for-2). It moves to the nightstand by 18:00, after his writing is done. His vitamins bottle stays at the kitchen counter all day — he takes a dose in the morning and another in the evening; it never leaves the house (9–17 h looks at the counter find it 2, empty 6, but the empties are likely at moments the bottle is briefly in his hand). His phone moves from the nightstand (sleeping, 0–7 h) to the coffee table (waking, 7–13 h) before he grabs it and leaves at 13:40. His water bottle sits at the coffee table during the day (sightings at 14:00, 16:00, 18:00).

This document differs from p_b7c2 and p_8e2f, which send the journal OUT with Marco or park it at the nightstand during the day. The evidence (desk_b1 at 12:00, 9–17 h looks 2-for-2) says the journal stays at the desk. It also differs from p_e4c8, which covers only the 11:30–13:30 window; here the journal is at the desk from 06:00 onward.

Refutation: if the journal is found at the nightstand or OUT during 9:00–14:00 on a weekday, the desk block fails. If the vitamins are found OUT or at a non-counter receptacle during 9:00–14:00, the counter block is wrong. If the glasses are not on the bathroom shelf during 8:30–9:30, the shower block is wrong.

```json
{
 "claims": [
  {
   "claim": "Marco's glasses are on the bathroom shelf during his weekday morning shower",
   "target": "glasses_marco",
   "expect": "bathroom_shelf_ba1",
   "days": "weekday",
   "from": 8.5,
   "to": 9.5
  },
  {
   "claim": "Marco's journal is at the bedroom desk during his weekday morning writing",
   "target": "journal_marco",
   "expect": "desk_b1",
   "days": "weekday",
   "from": 9,
   "to": 14
  },
  {
   "claim": "Marco's vitamins are at the kitchen counter during his weekday morning",
   "target": "vitamins_marco",
   "expect": "counter_k1",
   "days": "weekday",
   "from": 9,
   "to": 14
  },
  {
   "claim": "Marco's phone is at the coffee table during his weekday morning preparation",
   "target": "phone_marco",
   "expect": "coffee_table_l1",
   "days": "weekday",
   "from": 8,
   "to": 12
  }
 ],
 "targets": {
  "glasses_marco": [
   {
    "days": "weekday",
    "from": 0,
    "to": 8,
    "at": "nightstand_b1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 8,
    "to": 9.5,
    "at": "bathroom_shelf_ba1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 9.5,
    "to": 13,
    "at": "coffee_table_l1",
    "chance": "sometimes"
   }
  ],
  "journal_marco": [
   {
    "days": "weekday",
    "from": 0,
    "to": 17,
    "at": "desk_b1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 17,
    "to": 24,
    "at": "nightstand_b1",
    "chance": "sometimes"
   }
  ],
  "vitamins_marco": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "counter_k1",
    "chance": "usually"
   }
  ],
  "phone_marco": [
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
    "to": 13,
    "at": "coffee_table_l1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 14,
    "to": 23,
    "at": "OUT_OF_HOUSE",
    "chance": "almost_always"
   }
  ],
  "water_bottle_marco": [
   {
    "days": "weekday",
    "from": 7,
    "to": 23,
    "at": "coffee_table_l1",
    "chance": "sometimes"
   }
  ]
 }
}
```
