# p_e7b4 — The work kit that stays: journal at desk, lunchbox at cupboard, vitamins at counter

Marco leaves for his afternoon-to-night shift around 13:40, but three items never go with him. His journal stays at the desk (he journals in the morning and evening, not at work). His lunchbox stays in the kitchen cupboard (he packs it the night before and it rests there all day; he grabs it on the way out but the cupboard is where it's found by the robot). His vitamins stay on the kitchen counter (she reminds him to take them in the morning; the bottle sits on the counter all day). The per-object evidence is unambiguous: journal at desk_b1 on 5/7 days with 4/4 weekday afternoon looks confirming it; lunchbox at cupboard_k1 on 7/7 days with 4/4 weekday afternoon looks; vitamins at counter_k1 on 7/7 days with 4/4 weekday afternoon looks. What Marco *does* take is his phone, water bottle, keys, wallet, backpack, and jacket — those are the items showing empty looks at their resting spots during 14:00–22:00. This document is distinguished from the "full kit travels" documents by insisting these three items are in the house all day. If the robot finds the journal at the nightstand, the lunchbox out of the house, or the vitamins out of the house during the weekday 14:00–22:00 window, this document is refuted.

```json
{
 "claims": [
  {
   "claim": "Marco's journal is at the desk during his work shift, not out of the house",
   "target": "journal_marco",
   "expect": "desk_b1",
   "days": "weekday",
   "from": 14,
   "to": 22
  },
  {
   "claim": "Marco's lunchbox is in the kitchen cupboard during his work shift",
   "target": "lunchbox_marco",
   "expect": "cupboard_k1",
   "days": "weekday",
   "from": 14,
   "to": 22
  },
  {
   "claim": "Marco's vitamins are on the kitchen counter during his work shift",
   "target": "vitamins_marco",
   "expect": "counter_k1",
   "days": "weekday",
   "from": 14,
   "to": 22
  },
  {
   "claim": "Marco's phone is out of the house during his work shift",
   "target": "phone_marco",
   "expect": "OUT_OF_HOUSE",
   "days": "weekday",
   "from": 14,
   "to": 22
  }
 ],
 "targets": {
  "journal_marco": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "desk_b1",
    "chance": "almost_always"
   }
  ],
  "lunchbox_marco": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "almost_always"
   }
  ],
  "vitamins_marco": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "counter_k1",
    "chance": "almost_always"
   }
  ],
  "phone_marco": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "coffee_table_l1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 14,
    "to": 22,
    "at": "OUT_OF_HOUSE",
    "chance": "usually"
   }
  ],
  "water_bottle_marco": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "dish_rack_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 14,
    "to": 22,
    "at": "OUT_OF_HOUSE",
    "chance": "usually"
   }
  ],
  "keys_marco": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_table_e1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 14,
    "to": 22,
    "at": "OUT_OF_HOUSE",
    "chance": "sometimes"
   }
  ],
  "wallet_marco": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_table_e1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 14,
    "to": 22,
    "at": "OUT_OF_HOUSE",
    "chance": "sometimes"
   }
  ],
  "backpack_marco": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_hook_e1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 14,
    "to": 22,
    "at": "OUT_OF_HOUSE",
    "chance": "sometimes"
   }
  ],
  "jacket_marco": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_hook_e1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 14,
    "to": 22,
    "at": "OUT_OF_HOUSE",
    "chance": "usually"
   }
  ]
 }
}
```
