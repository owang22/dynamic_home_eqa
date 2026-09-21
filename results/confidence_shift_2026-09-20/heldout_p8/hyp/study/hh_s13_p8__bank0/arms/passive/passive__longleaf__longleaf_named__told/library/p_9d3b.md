# p_9d3b — Hana's Evening at the Desk: No Hook Dump

Hana does not dump her things at the entry hook when she comes home. The evidence is clear: seven empty looks each for the laptop, water bottle, and pen at the entry hook during 18-22h on weekdays. Instead, she hangs her jacket and handbag at the hook (those stay there all evening), but takes the laptop to desk_b1 in her bedroom. The water bottle goes to the kitchen counter where she fills it. The pen goes with the laptop to the desk.

In the evening Hana works or browses at desk_b1 from about 18:00 to 21:00. On Wednesday with guests she might skip the desk work and go straight to the living room, leaving the laptop closed on the desk. The jacket and handbag stay at the entry hook. During work hours (8:00-17:30) the jacket, handbag, keys, and laptop are out of the house with her.

What sets this apart: the laptop is at desk_b1 (not entry_hook_e1) at 20:00, the water bottle is at counter_k1 (not entry_hook_e1), the pen is at desk_b1 (not entry_hook_e1). This directly contradicts p_d3e8 (The Entry Mess, which put all three at the entry hook 18-22h and accumulated 7+7+7 against).

What would refute it: if the laptop is sighted at the entry hook at 20:00, or if the water bottle is at the entry hook, or if the pen is at the entry hook.

```json
{
 "claims": [
  {
   "claim": "Hana's laptop is at desk_b1 at 20:00 on a weekday",
   "target": "laptop_hana",
   "expect": "desk_b1",
   "days": "weekday",
   "from": 18,
   "to": 22
  },
  {
   "claim": "Hana's water bottle is at the kitchen counter at 20:00 on a weekday",
   "target": "water_bottle_hana",
   "expect": "counter_k1",
   "days": "weekday",
   "from": 18,
   "to": 22
  },
  {
   "claim": "Hana's pen is at desk_b1 at 20:00 on a weekday",
   "target": "pen_hana",
   "expect": "desk_b1",
   "days": "weekday",
   "from": 18,
   "to": 22
  },
  {
   "claim": "Hana's jacket is out of the house at noon on a weekday",
   "target": "jacket_hana",
   "expect": "OUT_OF_HOUSE",
   "days": "weekday",
   "from": 8,
   "to": 17.5
  }
 ],
 "targets": {
  "laptop_hana": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_hook_e1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 8,
    "to": 17.5,
    "at": "OUT_OF_HOUSE",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 18,
    "to": 22,
    "at": "desk_b1",
    "chance": "usually"
   }
  ],
  "water_bottle_hana": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_hook_e1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 8,
    "to": 17.5,
    "at": "OUT_OF_HOUSE",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 18,
    "to": 22,
    "at": "counter_k1",
    "chance": "usually"
   }
  ],
  "pen_hana": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_hook_e1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 8,
    "to": 17.5,
    "at": "OUT_OF_HOUSE",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 18,
    "to": 22,
    "at": "desk_b1",
    "chance": "usually"
   }
  ],
  "jacket_hana": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_hook_e1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 8,
    "to": 17.5,
    "at": "OUT_OF_HOUSE",
    "chance": "usually"
   }
  ],
  "handbag_hana": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_hook_e1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 8,
    "to": 17.5,
    "at": "OUT_OF_HOUSE",
    "chance": "usually"
   }
  ]
 }
}
```
