# p_2f7a — Blanket Migration: Couch at Night, Coffee Table Midday, Couch Again by Evening

The shared blanket rests on the living room couch overnight and in the early morning. During the weekday midday (roughly 09:30–14:30) it is pulled to the coffee table, where it sits while the residents relax, read, or watch TV. By 17:00–18:00 it is returned to the couch for the evening. On weekends, with both residents home all day, the blanket spends more time on the coffee table (from late morning through the evening).

The 03:00 pass finds it on the couch (x3), the 08:00 pass on the couch (x1), the 10:00 and 13:00 passes on the coffee table (x1 each), and the 18:00 pass back on the couch (x1). This is a clean daily migration. The hypothesis differs from p_d5f8, which places the blanket on the coffee table only on weekends from 10:00–14:00; the weekday midday sightings show the same pattern occurs on weekdays too.

What would refute this: a weekday pass at 11:00 or 13:00 finding the blanket still on the couch, or a pass at 03:00 finding it on the coffee table.

```json
{
 "claims": [
  {
   "claim": "The blanket is on the coffee table at 11:00 on a weekday",
   "target": "blanket_shared",
   "expect": "coffee_table_l1",
   "days": "weekday",
   "from": 10,
   "to": 13
  },
  {
   "claim": "The blanket is on the couch at 03:00 overnight",
   "target": "blanket_shared",
   "expect": "couch_l1",
   "days": "both",
   "from": 2,
   "to": 5
  },
  {
   "claim": "The blanket is back on the couch at 18:00 on a weekday",
   "target": "blanket_shared",
   "expect": "couch_l1",
   "days": "weekday",
   "from": 17,
   "to": 19
  },
  {
   "claim": "The blanket is on the coffee table at 13:00 on a weekday",
   "target": "blanket_shared",
   "expect": "coffee_table_l1",
   "days": "weekday",
   "from": 12,
   "to": 14
  }
 ],
 "targets": {
  "blanket_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 9.5,
    "at": "couch_l1",
    "chance": "almost_always"
   },
   {
    "days": "weekday",
    "from": 9.5,
    "to": 14.5,
    "at": "coffee_table_l1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 14.5,
    "to": 24,
    "at": "couch_l1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 9.5,
    "to": 20,
    "at": "coffee_table_l1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 20,
    "to": 24,
    "at": "couch_l1",
    "chance": "sometimes"
   }
  ]
 }
}
```
