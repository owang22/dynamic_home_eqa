# p_e2b7 — Shopping bag: pantry overnight, counter 16:00–18:00 on weekends after midday errands

The shopping bag rests at the pantry shelf overnight (five sightings at 03:00 across weekdays and weekends). On weekends, after the residents' midday errands, the bag appears on the kitchen counter from 16:00 through 18:00 (eight sightings across three hours), indicating that groceries are unpacked at the counter in the late afternoon. By 19:00 the bag is back at the pantry shelf (one weekday sighting at 19:00 on the counter, but the overnight pattern is pantry). On weekdays the bag is at the pantry shelf at 18:00 and 19:00, with no counter sightings, because the residents are at their desks and do not do errands.

What sets this apart from the other documents: no other document in the library tracks the shopping bag or the weekend grocery-unpacking routine. What would refute it: the bag on the counter at 16:00 on a weekday, or the bag at the counter at 03:00 on any day.

```json
{
 "claims": [
  {
   "claim": "The shopping bag is on the kitchen counter during the weekend grocery-unpacking window",
   "target": "shopping_bag_shared",
   "expect": "counter_k1",
   "days": "weekend",
   "from": 16,
   "to": 18
  },
  {
   "claim": "The shopping bag is at the pantry shelf overnight",
   "target": "shopping_bag_shared",
   "expect": "pantry_shelf_k1",
   "days": "both",
   "from": 0,
   "to": 7
  },
  {
   "claim": "The shopping bag is at the pantry shelf at 18:00 on weekdays (no weekday errands)",
   "target": "shopping_bag_shared",
   "expect": "pantry_shelf_k1",
   "days": "weekday",
   "from": 17.5,
   "to": 19
  }
 ],
 "targets": {
  "shopping_bag_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "pantry_shelf_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 16,
    "to": 18,
    "at": "counter_k1",
    "chance": "usually"
   }
  ]
 }
}
```
