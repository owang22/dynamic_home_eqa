# p_8e2b — Hana's Weekend: Entry Hook Is Home

On weekends Hana is home all day but she does not go to her desk. Her laptop and pen, which she sets down at the entry hook when she comes home from work on a Friday evening, simply stay there through Saturday and Sunday. Every weekend patrol (00:00, 08:00, 16:00) finds both the laptop and the pen at the entry_hook_e1, twice each. On weekday mornings, by contrast, the laptop and pen are at desk_b1 (00:00 and 08:00 passes confirm), because she uses them before leaving for work. The charger, however, stays at desk_b1 on weekends (00:00, 08:00, 16:00 all desk_b1 x2) because it is plugged in and does not travel with her. The guitar is on the bedroom floor every single day, every single pass — 7 out of 7 sighted days, 17 sightings, one receptacle.

This document differs from p_7f3a, which places the laptop at desk_b1 on Saturday morning, and from p_9e4a, which focuses on weekday morning desk placement. The key distinction is that on weekends the laptop and pen are at the entry hook, not the desk, while the charger remains at the desk. The guitar's immovability is a shared anchor with p_a3f1 and p_b1c6 but is stated here as a weekend-specific confirmation.

This hypothesis is refuted if the laptop or pen is found at desk_b1 on a weekend day, or if the charger is found at the entry hook on a weekend, or if the guitar is seen anywhere other than the bedroom floor.

```json
{
 "claims": [
  {
   "claim": "Hana's laptop is at the entry hook on a Saturday morning because she is home and not at work",
   "target": "laptop_hana",
   "expect": "entry_hook_e1",
   "days": "weekend",
   "from": 7,
   "to": 12
  },
  {
   "claim": "Hana's pen is at the entry hook on a Saturday afternoon",
   "target": "pen_hana",
   "expect": "entry_hook_e1",
   "days": "weekend",
   "from": 12,
   "to": 18
  },
  {
   "claim": "Hana's charger is at desk_b1 on a Saturday afternoon, not at the entry hook",
   "target": "charger_hana",
   "expect": "desk_b1",
   "days": "weekend",
   "from": 12,
   "to": 18
  },
  {
   "claim": "The guitar stays on the bedroom floor on a Saturday afternoon",
   "target": "guitar_hana",
   "expect": "bedroom_floor_b1",
   "days": "weekend",
   "from": 14,
   "to": 18
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
    "from": 6,
    "to": 8,
    "at": "desk_b1",
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
    "from": 6,
    "to": 8,
    "at": "desk_b1",
    "chance": "usually"
   }
  ],
  "charger_hana": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "desk_b1",
    "chance": "usually"
   }
  ],
  "guitar_hana": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "bedroom_floor_b1",
    "chance": "almost_always"
   }
  ]
 }
}
```
