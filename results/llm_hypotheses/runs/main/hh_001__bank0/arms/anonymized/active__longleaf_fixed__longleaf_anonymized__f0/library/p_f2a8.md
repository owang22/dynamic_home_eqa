# p_f2a8 — Retired couple; slow pace, objects barely move

Two retired adults live here. They wake around 07:30, are at home all day, and go to bed around 21:30. The walkthrough at 15:08 caught them in their usual afternoon routine: reading in the living room (receptacle_10, receptacle_20), perhaps tending to the kitchen (receptacle_4, receptacle_18, receptacle_19). Almost nothing leaves the house: they take short walks but leave keys and bags inside. The objects are extremely stable: the bathroom items (class_12, class_24, class_28) never move. The kitchen items (class_4) are on the counter from 08:00 to 20:00 (they snack and cook throughout the day). The bedroom (receptacle_8, receptacle_13) items are undisturbed.

What sets this apart: on ALL days (weekday and weekend), object_2, object_35, and object_3 are IN the house at all times. The kitchen objects (class_4) are at receptacle_4 for a long stretch (08:00–20:00) rather than short morning/evening windows. The living room (receptacle_10) is occupied with objects from 09:00 to 21:00. What would refute it: object_2 or object_35 found OUT_OF_HOUSE at any time, or the kitchen objects at receptacle_18 during 10:00–18:00 on any day.

```json
{"claims": [
   {"claim": "object_2 (keys) is always in the house because the retired couple rarely goes far",
    "target": "object_2", "expect": "receptacle_11", "days": "both", "from": 0, "to": 24},
   {"claim": "object_4 (kitchen item) is on the counter for most of the day",
    "target": "object_4", "expect": "receptacle_4", "days": "both", "from": 8, "to": 20},
   {"claim": "object_26 (living room item) is in the living room during afternoon reading",
    "target": "object_26", "expect": "receptacle_10", "days": "both", "from": 9, "to": 21},
   {"claim": "object_13 (bathroom item) is at the bathroom sink at all hours",
    "target": "object_13", "expect": "receptacle_6", "days": "both", "from": 0, "to": 24}
 ],
 "targets": {
   "object_2": [
     {"days": "both", "from": 0, "to": 24, "at": "receptacle_11", "chance": "almost_always"}
   ],
   "object_4": [
     {"days": "both", "from": 8, "to": 20, "at": "receptacle_4", "chance": "almost_always"},
     {"days": "both", "from": 0, "to": 24, "at": "receptacle_18", "chance": "usually"}
   ],
   "object_26": [
     {"days": "both", "from": 9, "to": 21, "at": "receptacle_10", "chance": "almost_always"}
   ],
   "object_13": [
     {"days": "both", "from": 0, "to": 24, "at": "receptacle_6", "chance": "almost_always"}
   ]
 }
}
```
