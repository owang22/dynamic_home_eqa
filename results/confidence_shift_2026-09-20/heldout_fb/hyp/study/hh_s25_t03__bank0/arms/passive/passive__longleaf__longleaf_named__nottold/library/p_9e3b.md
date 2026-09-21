# p_9e3b — Marco's water bottle: desk in the morning, in his hand through the afternoon, kitchen and dining in the evening

Marco's water bottle traces a clear five-stop path through the day. Overnight (0–7 h) it rests in the dish rack or the sink after being washed. In the early morning (8–11 h) it is at his desk, confirmed by sightings at desk_b1 at 08:00, 09:00 (×3), 10:00, and 11:00 (×2). During the core afternoon work block (12–17 h) the bottle disappears from the desk: 32 of 38 looks at desk_b1 during 9–17 h find it absent, and the 6 positive finds are all in the 8–11 h range. The most likely explanation is that he holds it in his hand while working (ON_PERSON), sipping throughout the afternoon. The 23 "weak for" tallies on p_f4b8's ON_PERSON claim (empty looks at desk_b1) support this. By 18:00 the bottle is back in the kitchen at the dish rack; at 19:00 it is in the sink (being washed); and at 20:00 it is at the dining table for dinner (×2 sightings). On weekends the pattern is similar but the desk window may be shorter since he sleeps in.

What would refute this: a look at desk_b1 at 14:00 on a weekday that finds the water bottle there; or a look at the dish rack at 13:00 that finds the bottle (meaning it was set down in the kitchen, not held).

```json
{
 "claims": [
  {
   "claim": "Marco's water bottle is at his desk in the early morning before core work",
   "target": "water_bottle_marco",
   "expect": "desk_b1",
   "days": "weekday",
   "from": 8,
   "to": 11
  },
  {
   "claim": "Marco's water bottle is in his hand during the afternoon work block, not on the desk",
   "target": "water_bottle_marco",
   "expect": "ON_PERSON",
   "days": "weekday",
   "from": 12,
   "to": 17
  },
  {
   "claim": "Marco's water bottle is at the dining table during dinner",
   "target": "water_bottle_marco",
   "expect": "dining_table_d1",
   "days": "both",
   "from": 20,
   "to": 21
  }
 ],
 "targets": {
  "water_bottle_marco": [
   {
    "days": "both",
    "from": 0,
    "to": 7,
    "at": "dish_rack_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 8,
    "to": 11,
    "at": "desk_b1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 12,
    "to": 17,
    "at": "ON_PERSON",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 17.5,
    "to": 19,
    "at": "dish_rack_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 19,
    "to": 20,
    "at": "sink_k1",
    "chance": "sometimes"
   },
   {
    "days": "both",
    "from": 20,
    "to": 21.5,
    "at": "dining_table_d1",
    "chance": "usually"
   }
  ]
 }
}
```
