# p_9c3d — Weekend overnight resting spots differ from weekday

On weekends the overnight and early-morning resting places shift for several personal items. Yuki's journal moves from the nightstand (where it sits all day on weekdays) to the bed itself, where it stays for the entire weekend — she journals in bed in the morning rather than at the desk. Omar's reading glasses, which rest at the nightstand on weekdays, move to the bedroom desk on weekends (consistent with the desk-work pattern). Omar's scarf, which hangs at the entry hook on weekdays (he grabs it to leave), stays in the wardrobe on weekends because he is not commuting. Both glasses (drinking) rest in the dish rack overnight on weekends rather than at the sink, suggesting they were washed and dried after the weekend's earlier meal. Omar's wallet drops to the entry floor on weekends (he is home, sets it down on the floor by the door rather than the table). Yuki's phone rests at the nightstand on weekend nights rather than the coffee table.

This document is distinct from the weekday documents because it captures the *overnight* weekend pattern: the items are not in transit, not at the entry hook in a "just got home" state, but in their relaxed weekend resting positions. The key differentiator is that on weekends there is no 8:00 or 13:30 departure, so the "entry dump" pattern does not apply; items settle into their true resting spots.

This document is refuted if, on a weekend morning (before 12:00), the journal is at the nightstand, the glasses are at the nightstand, or the scarf is at the entry hook.

```json
{
 "claims": [
  {
   "claim": "Yuki's journal is on the bed all day on weekends, not the nightstand",
   "target": "journal_yuki",
   "expect": "bed_b1",
   "days": "weekend",
   "from": 0,
   "to": 24
  },
  {
   "claim": "Omar's scarf is in the wardrobe on weekends, not the entry hook",
   "target": "scarf_omar",
   "expect": "wardrobe_b1",
   "days": "weekend",
   "from": 0,
   "to": 24
  },
  {
   "claim": "Yuki's drinking glass is in the dish rack on weekend mornings",
   "target": "glass_yuki",
   "expect": "dish_rack_k1",
   "days": "weekend",
   "from": 0,
   "to": 12
  },
  {
   "claim": "Omar's wallet is on the entry floor on weekend mornings",
   "target": "wallet_omar",
   "expect": "entry_floor_e1",
   "days": "weekend",
   "from": 0,
   "to": 12
  }
 ],
 "targets": {
  "journal_yuki": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "bed_b1",
    "chance": "almost_always"
   }
  ],
  "glasses_omar": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "desk_b1",
    "chance": "almost_always"
   }
  ],
  "scarf_omar": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "wardrobe_b1",
    "chance": "almost_always"
   }
  ],
  "glass_omar": [
   {
    "days": "weekend",
    "from": 0,
    "to": 12,
    "at": "dish_rack_k1",
    "chance": "almost_always"
   },
   {
    "days": "weekend",
    "from": 12,
    "to": 24,
    "at": "kitchen_table_k1",
    "chance": "sometimes"
   }
  ],
  "glass_yuki": [
   {
    "days": "weekend",
    "from": 0,
    "to": 12,
    "at": "dish_rack_k1",
    "chance": "almost_always"
   },
   {
    "days": "weekend",
    "from": 12,
    "to": 24,
    "at": "kitchen_table_k1",
    "chance": "sometimes"
   }
  ],
  "wallet_omar": [
   {
    "days": "weekend",
    "from": 0,
    "to": 12,
    "at": "entry_floor_e1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 12,
    "to": 24,
    "at": "entry_table_e1",
    "chance": "sometimes"
   }
  ],
  "phone_yuki": [
   {
    "days": "weekend",
    "from": 0,
    "to": 12,
    "at": "nightstand_b1",
    "chance": "usually"
   }
  ]
 }
}
```
