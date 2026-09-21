# p_7f3a — Phone and water bottle leave with Marco

Marco's phone and water bottle are personal items he carries to work. The phone is seen at the coffee table only at 00:00 and 08:00 on weekdays, with zero sightings at 16:00 or 18:00 — it is out of the house during his 13:40–23:00 shift. The water bottle sits at the entry hook in the morning but is found 0 out of 4 times there during the 9–17h window, consistent with it being in his backpack or on his person once he leaves. On weekends the phone shifts to the nightstand (the only weekend sightings are there) and the water bottle to the dish rack. This document sets itself apart from the existing library by treating the phone and water bottle as travelling items, distinct from the lunchbox and vitamins which the evidence shows stay home (lunchbox at cupboard 5/5 days, vitamins at counter 5/5 days, both found 4/4 during 9–17h). A look that finds the phone at the coffee table or nightstand during 14:00–22:00 on a weekday would refute this.

```json
{
 "claims": [
  {
   "claim": "Marco's phone is out of the house during his work shift",
   "target": "phone_marco",
   "expect": "OUT_OF_HOUSE",
   "days": "weekday",
   "from": 14,
   "to": 22
  },
  {
   "claim": "Marco's water bottle is out of the house during his work shift",
   "target": "water_bottle_marco",
   "expect": "OUT_OF_HOUSE",
   "days": "weekday",
   "from": 14,
   "to": 22
  },
  {
   "claim": "Marco's phone is at the coffee table in the early morning before work",
   "target": "phone_marco",
   "expect": "coffee_table_l1",
   "days": "weekday",
   "from": 7,
   "to": 12
  }
 ],
 "targets": {
  "phone_marco": [
   {
    "days": "weekday",
    "from": 0,
    "to": 13.5,
    "at": "coffee_table_l1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 13.5,
    "to": 23,
    "at": "OUT_OF_HOUSE",
    "chance": "almost_always"
   },
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "nightstand_b1",
    "chance": "sometimes"
   }
  ],
  "water_bottle_marco": [
   {
    "days": "weekday",
    "from": 0,
    "to": 13.5,
    "at": "entry_hook_e1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 13.5,
    "to": 23,
    "at": "OUT_OF_HOUSE",
    "chance": "almost_always"
   },
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "dish_rack_k1",
    "chance": "sometimes"
   }
  ]
 }
}
```
