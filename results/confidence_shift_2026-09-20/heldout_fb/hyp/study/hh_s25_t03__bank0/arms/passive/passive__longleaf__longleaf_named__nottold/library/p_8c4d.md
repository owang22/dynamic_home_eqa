# p_8c4d — Marco's laptop and charger are ON_PERSON during core work (10–16 h); notebook mostly in hand (fork of p_7f2a)

This fork narrows the ON_PERSON window from 9–17 h to 10–16 h and adjusts the chance labels to match the accumulated evidence. The parent p_7f2a placed all three items ON_PERSON for the full 9–17 h block; the sightings show the laptop at desk_b1 at 09:00 and 17:00 (he sets it down when he sits and when he packs up), so the "in-hand" window is really 10–16 h. Within that window the charger is absent from the desk 37 of 38 times (≈ 97 %), the laptop is absent 30 of 38 (≈ 79 %), and the notebook is absent 32 of 38 (≈ 84 %). I therefore label the charger "almost_always" ON_PERSON, and the laptop and notebook "usually" ON_PERSON. The parent stays at its own weight; this fork competes on the tighter window and the calibrated chances.

What changed and why: (1) time window 9→10 and 17→16 to exclude the sit-down and pack-up moments when the laptop is confirmed on the desk; (2) charger chance raised to "almost_always" because only 1 of 38 looks found it on the desk; (3) a new claim targets the charger specifically in the 10–16 h window where the evidence is strongest. What would refute this document: a look at resident_2 (Marco) during 10–16 h showing he is not holding the charger, or the charger sighted at a third receptacle (not desk_b1, not ON_PERSON) in that window.

```json
{
 "claims": [
  {
   "claim": "Marco's charger is in his hands (plugged into the laptop on his lap) during core work hours",
   "target": "charger_marco",
   "expect": "ON_PERSON",
   "days": "weekday",
   "from": 10,
   "to": 16
  },
  {
   "claim": "Marco's laptop is in his hands on his lap during core work hours, not resting on the desk surface",
   "target": "laptop_marco",
   "expect": "ON_PERSON",
   "days": "weekday",
   "from": 10,
   "to": 16
  },
  {
   "claim": "Marco's notebook is in his hands or on his lap during core work hours",
   "target": "notebook_marco",
   "expect": "ON_PERSON",
   "days": "weekday",
   "from": 10,
   "to": 16
  },
  {
   "claim": "Marco's laptop is back on the desk surface by 17:00 after he finishes work",
   "target": "laptop_marco",
   "expect": "desk_b1",
   "days": "weekday",
   "from": 17,
   "to": 19
  }
 ],
 "targets": {
  "laptop_marco": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "desk_b1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 10,
    "to": 16,
    "at": "ON_PERSON",
    "chance": "usually"
   }
  ],
  "charger_marco": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "desk_b1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 10,
    "to": 16,
    "at": "ON_PERSON",
    "chance": "almost_always"
   }
  ],
  "notebook_marco": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "desk_b1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 10,
    "to": 16,
    "at": "ON_PERSON",
    "chance": "usually"
   }
  ]
 }
}
```
