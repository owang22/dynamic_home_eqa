# p_2f7d — Marco's glasses: on the desk during work, nightstand in the evening, coffee table late at night

Marco's glasses follow a three-zone path. Overnight and in the early morning (0–7 h) they rest on the nightstand, confirmed by sightings at nightstand_b1 at 03:00 (×2). During work hours (9–17 h) they are on the desk at desk_b1, sighted at 09:00 and 11:00 (×2). This contradicts p_7a3c, which places them ON_PERSON (on his face) during 9–17 h; the patrol data shows them on the desk surface, not in his hands. In the evening (18–21 h) they return to the nightstand (sighted at 18:00 and 21:00). Late at night (22–24 h) they end up on the coffee table, presumably after he takes them off while watching TV (sighted at 22:00 and 23:00). The 9–17 h window has only 1 look at the nightstand (empty), consistent with the glasses being at the desk, not the nightstand, during work.

What would refute this: a look at desk_b1 at 12:00 on a weekday that finds no glasses; or a look at the nightstand at 14:00 that finds them (meaning they were set down mid-afternoon, not kept at the desk).

```json
{
 "claims": [
  {
   "claim": "Marco's glasses are on the desk surface during weekday work hours",
   "target": "glasses_marco",
   "expect": "desk_b1",
   "days": "weekday",
   "from": 9,
   "to": 17
  },
  {
   "claim": "Marco's glasses are on the nightstand during the evening wind-down",
   "target": "glasses_marco",
   "expect": "nightstand_b1",
   "days": "both",
   "from": 18,
   "to": 21.5
  },
  {
   "claim": "Marco's glasses are on the coffee table during late-night TV",
   "target": "glasses_marco",
   "expect": "coffee_table_l1",
   "days": "both",
   "from": 22,
   "to": 24
  }
 ],
 "targets": {
  "glasses_marco": [
   {
    "days": "both",
    "from": 0,
    "to": 7,
    "at": "nightstand_b1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 9,
    "to": 17,
    "at": "desk_b1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 18,
    "to": 21.5,
    "at": "nightstand_b1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 22,
    "to": 24,
    "at": "coffee_table_l1",
    "chance": "usually"
   }
  ]
 }
}
```
