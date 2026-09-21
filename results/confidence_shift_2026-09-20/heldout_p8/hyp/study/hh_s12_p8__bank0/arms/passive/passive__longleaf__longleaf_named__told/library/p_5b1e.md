# p_5b1e — Priya's afternoon errand: items shift to the entry floor

When Priya heads out for her weekday afternoon errands (roughly 13–16 h), her sunglasses, keys, and wallet migrate from the entry table to the entry floor. The 16:00 passes show the sunglasses on entry_floor_e1 three times — the single most-missed prediction in the current mixture. She sets them down while pulling on her coat and shoes, and they stay on the floor until she returns. Her water bottle is the variable: sometimes she takes it (it is missing from the dish rack during the errand window), sometimes it stays. Her keys and wallet remain at the entry table because she needs them to come back in, but the sunglasses — which she does not need until she is outside in the sun — end up on the floor. This document is distinct from p_7890 (which focuses on the dog and Priya being out) by making the entry-floor placement of the sunglasses a specific, testable prediction.

What would refute it: if the sunglasses are at the entry table during the 14–16 h window on most looks (meaning she keeps them on the table even when out), or if the water bottle is consistently at the dish rack during errands (meaning she never takes it).

```json
{
 "claims": [
  {
   "claim": "Priya's sunglasses are on the entry floor during her weekday afternoon errands",
   "target": "sunglasses_priya",
   "expect": "entry_floor_e1",
   "days": "weekday",
   "from": 14,
   "to": 16
  },
  {
   "claim": "Priya's water bottle is at the dish rack during her afternoon errands (she does not always take it)",
   "target": "water_bottle_priya",
   "expect": "dish_rack_k1",
   "days": "weekday",
   "from": 14,
   "to": 16
  },
  {
   "claim": "Priya's keys remain at the entry table during her afternoon errands",
   "target": "keys_priya",
   "expect": "entry_table_e1",
   "days": "weekday",
   "from": 14,
   "to": 16
  },
  {
   "claim": "Priya's sunglasses are at the entry table in the evening after she returns",
   "target": "sunglasses_priya",
   "expect": "entry_table_e1",
   "days": "both",
   "from": 18,
   "to": 22
  }
 ],
 "targets": {
  "sunglasses_priya": [
   {
    "days": "both",
    "from": 0,
    "to": 13,
    "at": "entry_table_e1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 13,
    "to": 16,
    "at": "entry_floor_e1",
    "chance": "sometimes"
   },
   {
    "days": "both",
    "from": 16,
    "to": 24,
    "at": "entry_table_e1",
    "chance": "usually"
   }
  ],
  "keys_priya": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_table_e1",
    "chance": "usually"
   }
  ],
  "wallet_priya": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_table_e1",
    "chance": "usually"
   }
  ],
  "water_bottle_priya": [
   {
    "days": "both",
    "from": 0,
    "to": 13,
    "at": "dish_rack_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 13,
    "to": 16,
    "at": "OUT_OF_HOUSE",
    "chance": "sometimes"
   },
   {
    "days": "both",
    "from": 16,
    "to": 24,
    "at": "dish_rack_k1",
    "chance": "usually"
   }
  ]
 }
}
```
