# p_c5e8 — Both jackets end up at the shoe rack overnight

The mixture predicts both jackets as ON_PERSON at 03:00, but nobody is wearing a jacket at three in the morning. The 03:00 passes show each jacket at entry_hook_e1 (2×) and shoe_rack_e1 (1×). The hook is the primary overnight spot, but on at least one occasion each jacket was draped over the shoe rack instead — a small, consistent secondary dump. Yuki's jacket is at the entry hook at 18:00 (just arrived home), confirming the hook is where it goes when she walks in. Omar's jacket follows the same pattern: hook during the day, occasionally shoe rack overnight.

This document differs from the plain statistical model (which predicts ON_PERSON for both jackets at 03:00) and from any existing hypothesis that does not mention the shoe rack as a jacket location. It is a narrow correction: the hook remains the dominant spot; the shoe rack is a secondary, sometimes-used resting place.

What would refute it: four or more 03:00 passes that find each jacket at the entry hook with zero at the shoe rack, eliminating the secondary-dump pattern.

```json
{
 "claims": [
  {
   "claim": "Omar's jacket is at the shoe rack at 03:00 on a weekday (draped over it instead of the hook)",
   "target": "jacket_omar",
   "expect": "shoe_rack_e1",
   "days": "weekday",
   "from": 2,
   "to": 6
  },
  {
   "claim": "Yuki's jacket is at the shoe rack at 03:00 on a weekday (draped over it instead of the hook)",
   "target": "jacket_yuki",
   "expect": "shoe_rack_e1",
   "days": "weekday",
   "from": 2,
   "to": 6
  },
  {
   "claim": "Yuki's jacket is at the entry hook at 18:00 on a weekday (just arrived home)",
   "target": "jacket_yuki",
   "expect": "entry_hook_e1",
   "days": "weekday",
   "from": 17.5,
   "to": 19
  }
 ],
 "targets": {
  "jacket_omar": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_hook_e1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 0,
    "to": 7,
    "at": "shoe_rack_e1",
    "chance": "sometimes"
   }
  ],
  "jacket_yuki": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_hook_e1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 0,
    "to": 7,
    "at": "shoe_rack_e1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 17,
    "to": 19,
    "at": "entry_hook_e1",
    "chance": "usually"
   }
  ]
 }
}
```
