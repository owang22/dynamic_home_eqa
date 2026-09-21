# p_c4d9 — Omar's tablet: nightstand overnight, kitchen table mid-morning, chair in the evening

Omar's tablet follows a strict three-stop daily migration. Overnight (00:00–07:00) it rests on the bedroom nightstand, where he charges it while he sleeps. In the morning, when he is home before his 1:40 departure, he uses it at the kitchen table (roughly 09:00–13:00) — browsing, music, or light work. Once he leaves for his afternoon-to-night shift, the tablet stays at the kitchen chair (14:00–23:00); it is his "home base" chair where he leaves things when he steps out. On weekends the pattern shifts: the tablet stays at the kitchen table or chair all day since he is home.

This document is distinguished by its precise three-receptacle migration. It predicts the tablet at the nightstand at 03:00 (not the kitchen table, not the chair), at the kitchen table at 10:00 (not the chair, not the nightstand), and at the kitchen chair at 18:00 (not the kitchen table, not the nightstand). The kitchen table claim for 10:00 is the one most at risk: if he is gaming or in the living room, the tablet might be elsewhere.

Refuted if: the tablet is at the kitchen chair at 03:00 (wrong overnight spot); at the nightstand at 10:00 (he should be using it at the table); at the kitchen table at 18:00 (he is at work, it should be at the chair).

```json
{
 "claims": [
  {
   "claim": "Omar's tablet is at the bedroom nightstand at 03:00 on a weekday (overnight resting spot)",
   "target": "tablet_omar",
   "expect": "nightstand_b1",
   "days": "weekday",
   "from": 2,
   "to": 6
  },
  {
   "claim": "Omar's tablet is at the kitchen table at 10:00 on a weekday (mid-morning use while he is home)",
   "target": "tablet_omar",
   "expect": "kitchen_table_k1",
   "days": "weekday",
   "from": 9.5,
   "to": 12.5
  },
  {
   "claim": "Omar's tablet is at the kitchen chair at 18:00 on a weekday (he is at work, tablet rests in the chair)",
   "target": "tablet_omar",
   "expect": "chair_k1",
   "days": "weekday",
   "from": 15,
   "to": 22
  }
 ],
 "targets": {
  "tablet_omar": [
   {
    "days": "weekday",
    "from": 0,
    "to": 7,
    "at": "nightstand_b1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 9,
    "to": 13,
    "at": "kitchen_table_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 14,
    "to": 23,
    "at": "chair_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 0,
    "to": 8,
    "at": "nightstand_b1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 8,
    "to": 24,
    "at": "kitchen_table_k1",
    "chance": "sometimes"
   }
  ],
  "class:towel": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "towel_rack_ba1",
    "chance": "usually"
   }
  ],
  "class:toiletry_bag": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "bathroom_shelf_ba1",
    "chance": "usually"
   }
  ]
 }
}
```
