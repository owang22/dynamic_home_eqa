# p_9c1b — Weekend rest: no overnight pack, work items stay in the bedroom

On weekdays Elena stages her laptop, notebook, and pen at the entry hook overnight (the p_3a7c pattern). On weekends there is no commute, so this staging does not happen. The laptop rests at the coffee table all day, the notebook and pen stay at the bedroom desk, and the charger remains plugged in at the bedroom desk. The helmet stays at the entry hook (she does not cycle to work on weekends, though she might cycle for fun later). This document is the weekend complement to p_3a7c: where p_3a7c says "entry hook overnight, out during work," this says "coffee table / desk all day, nothing out."

What would refute it: if the laptop is at the entry hook overnight on Saturday (she packed for a Monday-commute-starts-Sunday routine), or if the notebook is at the entry hook (staged for a Sunday work session), or if the charger is at the coffee table all day (unplugged and mobile).

```json
{
 "claims": [
  {
   "claim": "Elena's laptop is at the coffee table overnight on a weekend (no overnight packing)",
   "target": "laptop_elena",
   "expect": "coffee_table_l1",
   "days": "weekend",
   "from": 0,
   "to": 7
  },
  {
   "claim": "Elena's notebook is at the bedroom desk overnight on a weekend (not staged at the entry hook)",
   "target": "notebook_elena",
   "expect": "desk_b1",
   "days": "weekend",
   "from": 0,
   "to": 7
  },
  {
   "claim": "Elena's charger is at the bedroom desk on a weekend afternoon (plugged in, no commute)",
   "target": "charger_elena",
   "expect": "desk_b1",
   "days": "weekend",
   "from": 10,
   "to": 16
  },
  {
   "claim": "Elena's helmet is at the entry hook on a weekend (no cycling to work)",
   "target": "helmet_elena",
   "expect": "entry_hook_e1",
   "days": "weekend",
   "from": 9,
   "to": 17
  }
 ],
 "targets": {
  "laptop_elena": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "coffee_table_l1",
    "chance": "usually"
   }
  ],
  "notebook_elena": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "desk_b1",
    "chance": "usually"
   }
  ],
  "pen_elena": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "desk_b1",
    "chance": "usually"
   }
  ],
  "charger_elena": [
   {
    "days": "weekend",
    "from": 0,
    "to": 18,
    "at": "desk_b1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 18,
    "to": 24,
    "at": "coffee_table_l1",
    "chance": "sometimes"
   }
  ],
  "helmet_elena": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "entry_hook_e1",
    "chance": "usually"
   }
  ],
  "phone_elena": [
   {
    "days": "weekend",
    "from": 0,
    "to": 7,
    "at": "nightstand_b1",
    "chance": "usually"
   }
  ]
 }
}
```
