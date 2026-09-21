# p_8c3f — Priya's weekday afternoon: the living room, 12 to 17

On weekdays Elena is at work from about 8 to 17:30, leaving Priya with the house from mid-morning through the late afternoon. After her morning walk (around 10–11), she settles into the living room. Her mug, which sat at the kitchen table during breakfast (7–8), moves to the coffee table by mid-afternoon (14–15). Her reading glasses, which rested on the nightstand overnight and were in the bathroom at 7, are set on the coffee table from about 15:00 onward; she does not wear them (the ON_PERSON block in p_a1b2 and p_4c7d failed). Around 16:00–17:00 the vacuum cleaner is in the living room, suggesting she vacuums then. The shopping bag is on the kitchen counter from 12:00 to 15:00, likely groceries from a midday errand or being packed for one.

What would refute this: finding the mug at the kitchen table after 15:00 on a weekday, finding the glasses on the nightstand after 15:00, or finding the vacuum at the entry floor during 16–17.

```json
{
 "claims": [
  {
   "claim": "Priya's mug is at the kitchen table at 12:00 on a weekday",
   "target": "mug_priya",
   "expect": "kitchen_table_k1",
   "days": "weekday",
   "from": 12,
   "to": 14
  },
  {
   "claim": "Priya's glasses are on the coffee table at 15:00 on a weekday",
   "target": "glasses_priya",
   "expect": "coffee_table_l1",
   "days": "weekday",
   "from": 15,
   "to": 17
  },
  {
   "claim": "The vacuum cleaner is in the living room at 16:30 on a weekday",
   "target": "vacuum_cleaner_shared",
   "expect": "floor_l_l1",
   "days": "weekday",
   "from": 16,
   "to": 17
  }
 ],
 "targets": {
  "mug_priya": [
   {
    "days": "weekday",
    "from": 12,
    "to": 14,
    "at": "kitchen_table_k1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 14,
    "to": 17,
    "at": "coffee_table_l1",
    "chance": "sometimes"
   }
  ],
  "glasses_priya": [
   {
    "days": "weekday",
    "from": 15,
    "to": 18,
    "at": "coffee_table_l1",
    "chance": "usually"
   }
  ],
  "vacuum_cleaner_shared": [
   {
    "days": "weekday",
    "from": 16,
    "to": 17,
    "at": "floor_l_l1",
    "chance": "rarely"
   }
  ],
  "shopping_bag_shared": [
   {
    "days": "weekday",
    "from": 12,
    "to": 15,
    "at": "counter_k1",
    "chance": "sometimes"
   }
  ]
 }
}
```
