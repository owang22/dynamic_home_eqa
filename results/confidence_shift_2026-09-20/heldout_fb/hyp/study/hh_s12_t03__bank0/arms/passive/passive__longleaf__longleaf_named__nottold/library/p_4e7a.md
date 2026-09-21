# p_4e7a — Elena's evening: the coffee table is her desk

Elena comes home from work around 17:30–18:00 on weekdays. Rather than going to the bedroom desk or the office, she sets her laptop and charger on the coffee table in the living room, where she can check email or browse while having a drink with Priya. The notebook and pen remain at desk_b1, where they were packed in the morning or where they rested overnight. This is distinct from p_f8a6, which places the laptop at desk_b1 on Tuesday midday, and p_c3d4, which places it at desk_o1 on Monday and Wednesday mornings. The 18:00 weekday passes are unambiguous: laptop at coffee_table_l1, charger at coffee_table_l1, notebook at desk_b1, pen at desk_b1.

What would refute this: finding the laptop at desk_b1 or desk_o1 during the 18–23h weekday window, or finding the charger at desk_b1 in that window.

```json
{
 "claims": [
  {
   "claim": "Elena's laptop is on the coffee table at 18:00 on a weekday evening",
   "target": "laptop_elena",
   "expect": "coffee_table_l1",
   "days": "weekday",
   "from": 18,
   "to": 20
  },
  {
   "claim": "Elena's charger is on the coffee table at 18:00 on a weekday evening",
   "target": "charger_elena",
   "expect": "coffee_table_l1",
   "days": "weekday",
   "from": 18,
   "to": 20
  },
  {
   "claim": "Elena's notebook stays at the bedroom desk at 18:00 on a weekday",
   "target": "notebook_elena",
   "expect": "desk_b1",
   "days": "weekday",
   "from": 18,
   "to": 20
  }
 ],
 "targets": {
  "laptop_elena": [
   {
    "days": "weekday",
    "from": 18,
    "to": 23,
    "at": "coffee_table_l1",
    "chance": "usually"
   }
  ],
  "charger_elena": [
   {
    "days": "weekday",
    "from": 18,
    "to": 23,
    "at": "coffee_table_l1",
    "chance": "usually"
   }
  ],
  "notebook_elena": [
   {
    "days": "weekday",
    "from": 18,
    "to": 23,
    "at": "desk_b1",
    "chance": "usually"
   }
  ],
  "pen_elena": [
   {
    "days": "weekday",
    "from": 18,
    "to": 23,
    "at": "desk_b1",
    "chance": "usually"
   }
  ]
 }
}
```
