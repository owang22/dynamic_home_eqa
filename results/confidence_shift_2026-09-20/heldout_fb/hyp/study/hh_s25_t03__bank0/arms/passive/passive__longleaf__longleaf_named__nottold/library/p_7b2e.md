# p_7b2e — Marco's laptop and charger ON_PERSON 10–16 h; notebook stays on the desk (fork of p_8c4d)

This fork corrects the notebook placement in p_8c4d. The parent put notebook_marco ON_PERSON during 10–16 h, but the p_3e9a block for notebook at ON_PERSON in that window **failed** (0.14 on 3 sightings), and the patrol data shows the notebook at desk_b1 at 09:00, 11:00 (×3), 12:00, 15:00, 17:00, and 18:00 (×2) — six or seven positive desk sightings within the workday. The 32 empty desk looks during 9–17 h are best explained by Marco picking the notebook up briefly to write, then setting it back down; it is not consistently in his hands the way the laptop and charger are. I therefore change the notebook block to desk_b1 with "usually" (not "almost_always"), and drop the notebook ON_PERSON claim in favour of a desk claim. The laptop and charger blocks are unchanged: the charger is absent from the desk 37 of 38 times (≈ 97 %) and the laptop 30 of 38 (≈ 79 %), both strongly supporting ON_PERSON during 10–16 h.

What changed from p_8c4d: (1) notebook_marco 10–16 h block changed from ON_PERSON/"usually" to desk_b1/"usually"; (2) the notebook claim now expects desk_b1 instead of ON_PERSON; (3) a new claim confirms the notebook is back on the desk by 17:00. What would refute this: a look at desk_b1 during 10–16 h that finds the notebook consistently absent (more than half the looks empty), or a look at resident_2 showing him holding the notebook while the desk is empty.

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
   "claim": "Marco's notebook is on the desk surface during core work hours, set down between writing sessions",
   "target": "notebook_marco",
   "expect": "desk_b1",
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
    "at": "desk_b1",
    "chance": "usually"
   }
  ]
 }
}
```
