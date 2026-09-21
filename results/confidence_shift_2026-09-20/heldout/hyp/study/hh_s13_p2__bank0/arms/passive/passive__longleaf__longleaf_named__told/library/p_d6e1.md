# p_d6e1 — Priya's Phone: Carried All Day, Never at the Nightstand After 8 AM

Priya's phone is at nightstand_b2 during the night (00:00–08:00 sightings confirm this on every day of the log) but is never found there during the working day. The weekday 9–17h statistics are stark: 0 finds, 16 empty looks. On weekends the phone reappears at the nightstand at 12:00 (one sighting) but is absent at 10:00, 14:00, 16:00, 18:00, 20:00, and 22:00. The only receptacle the phone is ever seen at is nightstand_b2, so when it is not there, it must be ON_PERSON (Priya is home most of the day) or OUT_OF_HOUSE (on her walk or errand).

This hypothesis predicts that the phone is ON_PERSON from about 8:00 to 22:00 on weekdays and from about 8:00 to 11:00 and 13:00 to 22:00 on weekends. It is set apart from p_9c2f (which has a claim that the phone is ON_PERSON at 14:00 on weekdays — consistent, but p_9c2f does not make the full 0-8/22-24 nightstand claim) and from p_d5e7 (the bedroom fortress, which would put the phone at the nightstand all day).

This document is refuted if a look at nightstand_b2 between 10:00 and 18:00 on a weekday finds the phone there.

```json
{
 "claims": [
  {
   "claim": "Priya's phone is on her person at 10 AM on a weekday because she carries it while doing morning activities",
   "target": "phone_priya",
   "expect": "ON_PERSON",
   "days": "weekday",
   "from": 9,
   "to": 11
  },
  {
   "claim": "Priya's phone is on her person at 2 PM on a weekday because she is at home but not at the nightstand",
   "target": "phone_priya",
   "expect": "ON_PERSON",
   "days": "weekday",
   "from": 13,
   "to": 15
  },
  {
   "claim": "Priya's phone is at the nightstand at 6 AM on a weekday because it is charging overnight",
   "target": "phone_priya",
   "expect": "nightstand_b2",
   "days": "weekday",
   "from": 5,
   "to": 7
  },
  {
   "claim": "Priya's phone is on her person at 3 PM on a Saturday because she is at home but not resting at the nightstand",
   "target": "phone_priya",
   "expect": "ON_PERSON",
   "days": "weekend",
   "from": 14,
   "to": 16
  }
 ],
 "targets": {
  "phone_priya": [
   {
    "days": "both",
    "from": 0,
    "to": 8,
    "at": "nightstand_b2",
    "chance": "almost_always"
   },
   {
    "days": "weekday",
    "from": 8,
    "to": 22,
    "at": "ON_PERSON",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 8,
    "to": 11,
    "at": "ON_PERSON",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 11,
    "to": 13,
    "at": "nightstand_b2",
    "chance": "sometimes"
   },
   {
    "days": "weekend",
    "from": 13,
    "to": 22,
    "at": "ON_PERSON",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 22,
    "to": 24,
    "at": "nightstand_b2",
    "chance": "almost_always"
   }
  ]
 }
}
```
