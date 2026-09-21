# p_4c9d — The 3 AM Living Room; Post-Shift TV Before the Kitchen

The 03:00 pass places the blanket on armchair_l1 and the remote on floor_l_l1, while the kitchen items are simultaneously out of their resting spots. This means Hana moves between the living room and the kitchen in the 02:00–04:00 window: she settles in the armchair with the blanket and watches TV (remote dropped on the floor), then heads to the kitchen to cook or prep. By 18:00 the blanket is back on the coffee table and the remote on the TV stand, their usual resting spots. This is distinct from p_789a, which places Hana's cooking at midnight (23:25–24:00) and does not account for the living-room evidence. It is also distinct from p_c3d4, which says the blanket stays on the coffee table all evening; here the blanket is on the armchair in the early morning, a different time and a different spot. The remote on the floor (not the TV stand) at 03:00 indicates active TV use, not storage.

What sets this apart: the blanket on armchair_l1 (not coffee_table_l1) during 02:00–05:00 on weekdays, the remote on floor_l_l1 (not tv_stand_l1) in the same window, and the co-occurrence of living-room and kitchen activity in the 03:00 pass.

What would refute it: the blanket on the coffee table at the 03:00 pass; the remote on the TV stand at 03:00; no kitchen items out of their resting spots at 03:00 (meaning no cooking was happening).

```json
{
 "claims": [
  {
   "claim": "The blanket is on the armchair at 3 AM while Hana watches TV after her shift",
   "target": "blanket_shared",
   "expect": "armchair_l1",
   "days": "weekday",
   "from": 2,
   "to": 5
  },
  {
   "claim": "The remote is on the living room floor at 3 AM during active TV use",
   "target": "remote_shared",
   "expect": "floor_l_l1",
   "days": "weekday",
   "from": 2,
   "to": 5
  },
  {
   "claim": "The blanket is back on the coffee table by 18:00 after the early-morning TV session",
   "target": "blanket_shared",
   "expect": "coffee_table_l1",
   "days": "weekday",
   "from": 17,
   "to": 19
  },
  {
   "claim": "The remote is on the TV stand by 18:00",
   "target": "remote_shared",
   "expect": "tv_stand_l1",
   "days": "weekday",
   "from": 17,
   "to": 19
  }
 ],
 "targets": {
  "blanket_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "coffee_table_l1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 2,
    "to": 5,
    "at": "armchair_l1",
    "chance": "sometimes"
   }
  ],
  "remote_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "tv_stand_l1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 2,
    "to": 5,
    "at": "floor_l_l1",
    "chance": "sometimes"
   },
   {
    "days": "both",
    "from": 21,
    "to": 23,
    "at": "coffee_table_l1",
    "chance": "sometimes"
   }
  ],
  "cushion_2_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "armchair_l1",
    "chance": "usually"
   }
  ],
  "cushion_1_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "couch_l1",
    "chance": "usually"
   }
  ]
 }
}
```
