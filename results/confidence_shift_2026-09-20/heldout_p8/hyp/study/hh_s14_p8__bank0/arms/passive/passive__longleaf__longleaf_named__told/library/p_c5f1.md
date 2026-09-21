# p_c5f1 — Guitar: bedroom floor is home, couch is a midday visit

Yuki's guitar lives on the bedroom floor. During the weekday midday (roughly 12:00–17:00) she carries it to the living room couch while she's settled in for a nap or casual playing, but by 18:00 it is back on the bedroom floor for her evening practice. The 18:00 weekday patrol confirms this: the guitar is on the bedroom floor and nowhere else. On weekends the split is more even because she's home all day and moves it back and forth. The per-object data shows bedroom_floor_b1 as the primary location (4/7 days) and the 18:00 pass shows it exclusively there. What distinguishes this document from the "guitar on couch" predictions that keep failing is the 18:00+ weekday window: the guitar is on the bedroom floor, not the couch. If the robot finds the guitar on the couch at 18:00 or 20:00 on a weekday, this document is wrong.

```json
{
 "claims": [
  {
   "claim": "The guitar is on the bedroom floor at 18:00 on a weekday, not the couch",
   "target": "guitar_yuki",
   "expect": "bedroom_floor_b1",
   "days": "weekday",
   "from": 18,
   "to": 22
  },
  {
   "claim": "The guitar is on the bedroom floor in the weekday early morning",
   "target": "guitar_yuki",
   "expect": "bedroom_floor_b1",
   "days": "weekday",
   "from": 0,
   "to": 8
  },
  {
   "claim": "The guitar is on the couch during the weekday midday while Yuki is in the living room",
   "target": "guitar_yuki",
   "expect": "couch_l1",
   "days": "weekday",
   "from": 13,
   "to": 17
  }
 ],
 "targets": {
  "guitar_yuki": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "bedroom_floor_b1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 12,
    "to": 17,
    "at": "couch_l1",
    "chance": "sometimes"
   },
   {
    "days": "weekend",
    "from": 14,
    "to": 18,
    "at": "couch_l1",
    "chance": "sometimes"
   }
  ]
 }
}
```
