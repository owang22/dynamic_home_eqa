# p_5e1b — Priya's glasses: bathroom by 7, coffee table from 15, nightstand by 23

Priya does not wear her reading glasses during the day. The ON_PERSON blocks in p_a1b2 and p_4c7d failed (0.11 on 4 sightings). Instead, the glasses follow a fixed path: they rest on the nightstand overnight, move to the bathroom shelf for her 7:00 morning routine, then—after she finishes her walk and settles in the living room—land on the coffee table from about 15:00 through the evening. They return to the nightstand after 23:00 when she goes to bed.

What sets this apart from p_c5d7 (which also says "never worn"): p_c5d7 places them on the nightstand "by day" and its 23:00 claim scored for 1, against 4. The evidence shows the glasses are on the coffee table, not the nightstand, from 15:00 through 22:00. The nightstand is their resting spot only before 07:00 and after 23:00. The bathroom shelf window is narrow (07:00–08:00) and confirmed on both weekdays and weekends.

Refutation: if the glasses are sighted ON_PERSON on more than 2 occasions, or if they are on the nightstand at 16:00 or 21:00 on 3+ weekday evenings, the coffee-table-afternoon pattern is wrong.

```json
{
 "claims": [
  {
   "claim": "Priya's glasses are on the bathroom shelf at 07:00 on a weekday",
   "target": "glasses_priya",
   "expect": "bathroom_shelf_ba1",
   "days": "weekday",
   "from": 6.5,
   "to": 7.5
  },
  {
   "claim": "Priya's glasses are on the coffee table at 15:00 on a weekday",
   "target": "glasses_priya",
   "expect": "coffee_table_l1",
   "days": "weekday",
   "from": 14,
   "to": 17
  },
  {
   "claim": "Priya's glasses are on the coffee table at 21:00 on a weekday",
   "target": "glasses_priya",
   "expect": "coffee_table_l1",
   "days": "weekday",
   "from": 20.5,
   "to": 22.5
  },
  {
   "claim": "Priya's glasses are on the nightstand at 03:00 on a weekday",
   "target": "glasses_priya",
   "expect": "nightstand_b1",
   "days": "weekday",
   "from": 2,
   "to": 6
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
    "days": "both",
    "from": 6.5,
    "to": 8,
    "at": "bathroom_shelf_ba1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 14,
    "to": 22.5,
    "at": "coffee_table_l1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 14,
    "to": 22.5,
    "at": "coffee_table_l1",
    "chance": "sometimes"
   }
  ]
 }
}
```
