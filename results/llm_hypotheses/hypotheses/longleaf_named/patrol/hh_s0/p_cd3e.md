# p_cd3e — The Umbrella and Weather: Outdoor gear depends on the forecast

The umbrella, jacket, hat, scarf, and shoes at the entry are weather-dependent. On dry, mild days (which we cannot predict precisely), the jacket and scarf may be folded into the wardrobe or left off the hook. On rainy or cold days, they are at the entry hook. The umbrella is on the entry floor when it has been used. This hypothesis assumes a mixed-weather week: the umbrella is used 2–3 times per week, and the jacket is worn 3–4 times.

What sets this hypothesis apart: the entry hook is NOT always fully stocked. On some weekday mornings, the scarf or hat may be absent (folded away in a drawer or wardrobe). The umbrella may be at the entry floor or OUT_OF_HOUSE on rainy days. This introduces variability that the "always at the hook" hypotheses (p_a3f1, p_b7c2) do not have.

What would refute it: the entry hook sighted with ALL of jacket, hat, scarf, AND shoes present at 8:00 on five consecutive weekday mornings (suggesting they never come off).

```json
{
 "claims": [
  {
   "claim": "Yuki's jacket is at the entry hook on most weekday mornings",
   "target": "jacket_yuki",
   "expect": "entry_hook_e1",
   "days": "weekday",
   "from": 7,
   "to": 9
  },
  {
   "claim": "Yuki's scarf is at the entry hook on most weekday mornings",
   "target": "scarf_yuki",
   "expect": "entry_hook_e1",
   "days": "weekday",
   "from": 7,
   "to": 9
  },
  {
   "claim": "Yuki's umbrella is on the entry floor after use",
   "target": "umbrella_yuki",
   "expect": "entry_floor_e1",
   "days": "both",
   "from": 17,
   "to": 22
  },
  {
   "claim": "Yuki's hat is at the entry hook on most weekday evenings",
   "target": "hat_yuki",
   "expect": "entry_hook_e1",
   "days": "weekday",
   "from": 17,
   "to": 22
  }
 ],
 "targets": {
  "jacket_yuki": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_hook_e1",
    "chance": "usually"
   }
  ],
  "hat_yuki": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_hook_e1",
    "chance": "usually"
   }
  ],
  "scarf_yuki": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_hook_e1",
    "chance": "usually"
   }
  ],
  "shoes_yuki": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_hook_e1",
    "chance": "usually"
   }
  ],
  "umbrella_yuki": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_floor_e1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 8,
    "to": 17,
    "at": "OUT_OF_HOUSE",
    "chance": "rarely"
   }
  ],
  "keys_yuki": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_table_e1",
    "chance": "almost_always"
   }
  ]
 }
}
```
