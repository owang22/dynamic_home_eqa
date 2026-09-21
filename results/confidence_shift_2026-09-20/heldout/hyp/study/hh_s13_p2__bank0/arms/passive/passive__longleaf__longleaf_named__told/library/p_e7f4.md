# p_e7f4 — Weekend Mugs and Water Bottle: Kitchen Rest, Not the Living Room

On weekends the mugs and water bottle follow a quieter path than on weekdays. Priya's mug is at the dish rack overnight (00:00–08:00, washed from the previous evening), appears at the kitchen table at 10:00 (breakfast), and then goes to the cupboard from 12:00 to 22:00 — it is not carried to the living room for an evening drink. Hana's mug is at the cupboard all day, briefly at the counter at 10:00 (making coffee), and at the coffee table at 22:00 (a single evening sighting). The water bottle is at the dish rack all day on weekends, with a single sink sighting at 20:00 (rinsing).

This is set apart from p_9b6e (which puts Priya's mug at the kitchen table 10–13h for brunch — the data shows it there only at 10:00, then in the cupboard) and from p_d1f8 (which puts Priya's mug on the coffee table at 22:00 on weekdays — on weekends it is in the cupboard at 22:00). The weekend evening is calmer: the mugs go back to the cupboard, not to the living room.

This document is refuted if a weekend look at 14:00–20:00 finds Priya's mug at the coffee table or kitchen table, or the water bottle at the entry hook.

```json
{
 "claims": [
  {
   "claim": "Priya's mug is in the cupboard at 2 PM on a Saturday because breakfast is over and she does not carry it to the living room on weekends",
   "target": "mug_priya",
   "expect": "cupboard_k1",
   "days": "weekend",
   "from": 13,
   "to": 16
  },
  {
   "claim": "Hana's water bottle is at the dish rack at 2 PM on a Saturday because she does not take it out on weekends",
   "target": "water_bottle_hana",
   "expect": "dish_rack_k1",
   "days": "weekend",
   "from": 13,
   "to": 16
  },
  {
   "claim": "Priya's mug is in the cupboard at 10 PM on a Saturday, not at the coffee table",
   "target": "mug_priya",
   "expect": "cupboard_k1",
   "days": "weekend",
   "from": 21,
   "to": 23
  },
  {
   "claim": "Hana's mug is in the cupboard at 4 PM on a Saturday because she is not in the kitchen",
   "target": "mug_hana",
   "expect": "cupboard_k1",
   "days": "weekend",
   "from": 14,
   "to": 17
  }
 ],
 "targets": {
  "mug_priya": [
   {
    "days": "weekend",
    "from": 0,
    "to": 9,
    "at": "dish_rack_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 9,
    "to": 11,
    "at": "kitchen_table_k1",
    "chance": "sometimes"
   },
   {
    "days": "weekend",
    "from": 11,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "usually"
   }
  ],
  "mug_hana": [
   {
    "days": "weekend",
    "from": 0,
    "to": 10,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 10,
    "to": 11,
    "at": "counter_k1",
    "chance": "sometimes"
   },
   {
    "days": "weekend",
    "from": 11,
    "to": 22,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 22,
    "to": 24,
    "at": "coffee_table_l1",
    "chance": "sometimes"
   }
  ],
  "water_bottle_hana": [
   {
    "days": "weekend",
    "from": 0,
    "to": 20,
    "at": "dish_rack_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 20,
    "to": 21,
    "at": "sink_k1",
    "chance": "sometimes"
   },
   {
    "days": "weekend",
    "from": 21,
    "to": 24,
    "at": "dish_rack_k1",
    "chance": "usually"
   }
  ]
 }
}
```
