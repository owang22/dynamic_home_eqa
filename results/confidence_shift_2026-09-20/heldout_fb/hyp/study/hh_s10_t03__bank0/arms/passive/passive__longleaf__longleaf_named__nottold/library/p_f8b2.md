# p_f8b2 — Omar's tablet: nightstand overnight, kitchen table 09–13, kitchen chair 14–22

Omar's tablet follows a three-stage weekday migration. Overnight and in the early morning (03:00: nightstand 2×, chair 1×, dresser 1×; 09:00: nightstand 2×, kitchen_table 1×) it rests at the bedroom nightstand. By 10:00 it has moved to the kitchen table (10:00: kitchen_table 2×), where Omar uses it for his morning routine—perhaps checking messages, reading, or light work—before his 13:40 departure. Once he leaves for his afternoon-to-night shift, the tablet is at the kitchen chair (18:00: chair_k1 1×), where it stays while he's at work. On weekends the tablet simply sleeps at the nightstand (03:00: nightstand 2×; 23:00: nightstand 1×) with no midday migration.

This differs from p_e5f6, which placed the tablet at the kitchen chair during 07–13h (refuted: 0 for, 5 against), and from p_3e91, which put it at the kitchen table 10–12h (2 for, 6 against—partially supported but the window may be too narrow). The key distinction here is the 13:00–14:00 transition from kitchen table to kitchen chair, coinciding with Omar's departure for work.

```json
{
 "claims": [
  {
   "claim": "Omar's tablet is at the bedroom nightstand at 04:00 on a weekday (overnight resting spot)",
   "target": "tablet_omar",
   "expect": "nightstand_b1",
   "days": "weekday",
   "from": 3,
   "to": 7
  },
  {
   "claim": "Omar's tablet is at the kitchen table at 10:30 on a weekday (morning use before his shift)",
   "target": "tablet_omar",
   "expect": "kitchen_table_k1",
   "days": "weekday",
   "from": 10,
   "to": 12
  },
  {
   "claim": "Omar's tablet is at the kitchen chair at 18:00 on a weekday (he is at work, tablet left in kitchen)",
   "target": "tablet_omar",
   "expect": "chair_k1",
   "days": "weekday",
   "from": 14,
   "to": 22
  }
 ],
 "targets": {
  "tablet_omar": [
   {
    "days": "weekday",
    "from": 0,
    "to": 9,
    "at": "nightstand_b1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 9,
    "to": 13,
    "at": "kitchen_table_k1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 13,
    "to": 23,
    "at": "chair_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "nightstand_b1",
    "chance": "usually"
   }
  ]
 }
}
```
