# p_f4a0 — The 7 a.m. Dog Walk: Yuki walks the dog before Nora leaves

Yuki takes the dog for a morning walk at 7:00 on weekdays, returning by 8:00. The dog leash is OUT_OF_HOUSE (or ON_PERSON) during that hour. Nora leaves for work at 8:00. In the evening, Nora walks the dog again around 19:30. On weekends, the walk is later, around 9:30, and either resident may do it.

What sets this hypothesis apart: on weekday mornings at the 4:00 or 8:00 patrol, the dog leash is absent from entry_hook_e1 (gone for the walk). By 8:30 it is back. This is distinct from p_a3f1 where the leash stays at the hook all morning.

What would refute it: dog_leash_shared sighted at entry_hook_e1 at 7:00 on a weekday morning.

```json
{
 "claims": [
  {
   "claim": "The dog leash is out of the house at 7 a.m. on weekdays",
   "target": "dog_leash_shared",
   "expect": "OUT_OF_HOUSE",
   "days": "weekday",
   "from": 7,
   "to": 8
  },
  {
   "claim": "The dog leash is back at the entry hook by 9 a.m. on weekdays",
   "target": "dog_leash_shared",
   "expect": "entry_hook_e1",
   "days": "weekday",
   "from": 9,
   "to": 18
  },
  {
   "claim": "The dog leash is out for the evening walk around 19:30",
   "target": "dog_leash_shared",
   "expect": "OUT_OF_HOUSE",
   "days": "both",
   "from": 19,
   "to": 20
  },
  {
   "claim": "The dog leash is at the entry hook on weekend mornings before the 9:30 walk",
   "target": "dog_leash_shared",
   "expect": "entry_hook_e1",
   "days": "weekend",
   "from": 7,
   "to": 9
  }
 ],
 "targets": {
  "dog_leash_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_hook_e1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 7,
    "to": 8,
    "at": "OUT_OF_HOUSE",
    "chance": "almost_always"
   },
   {
    "days": "both",
    "from": 19,
    "to": 20,
    "at": "OUT_OF_HOUSE",
    "chance": "sometimes"
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
  ],
  "jacket_yuki": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_hook_e1",
    "chance": "almost_always"
   }
  ]
 }
}
```
