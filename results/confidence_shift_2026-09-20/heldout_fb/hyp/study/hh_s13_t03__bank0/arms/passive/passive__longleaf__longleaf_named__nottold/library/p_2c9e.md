# p_2c9e — The Snack Bowl's Day: Sink, Counter, Coffee Table

The snack bowl follows a clear three-stop daily arc that no single existing document captures in full. Overnight it sits in the kitchen sink (03:00 sighting). During the workday it is absent from the counter — five empty looks at counter_k1 between 9 and 17 confirm it is stored away, most likely in the cupboard or back in the sink. At 18:00 it reappears on the kitchen counter, where it stays through 19:00 (four sightings across those two passes). By 21:00 it has migrated to the coffee table for the evening TV session (two sightings).

This is distinct from p_c9d4 and p_7e4a, which focus on the late-night TV window and the 21–23h coffee-table placement. This document adds the daytime storage (cupboard, 9–17h) and the 18–20h counter window as the "filling and staging" phase before the bowl moves to the living room. If the snack bowl is found on the counter at noon, or on the coffee table before 20:00, this hypothesis is weakened.

```json
{
 "claims": [
  {
   "claim": "The snack bowl is on the kitchen counter at 19:00 on a weekday",
   "target": "snack_bowl_shared",
   "expect": "counter_k1",
   "days": "weekday",
   "from": 18,
   "to": 20
  },
  {
   "claim": "The snack bowl is on the coffee table at 21:00 on a weekday",
   "target": "snack_bowl_shared",
   "expect": "coffee_table_l1",
   "days": "weekday",
   "from": 20.5,
   "to": 22
  },
  {
   "claim": "The snack bowl is in the sink at 03:00 on a weekday",
   "target": "snack_bowl_shared",
   "expect": "sink_k1",
   "days": "weekday",
   "from": 2,
   "to": 5
  }
 ],
 "targets": {
  "snack_bowl_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "sink_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 9,
    "to": 17,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 17.5,
    "to": 20,
    "at": "counter_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 20,
    "to": 23,
    "at": "coffee_table_l1",
    "chance": "usually"
   }
  ]
 }
}
```
