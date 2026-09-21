# p_7c2e — The Guitar Rests: Never Played, Weekend Couch Migration

The guitar has never been seen ON_PERSON in any patrol pass across six days. On weekdays it is at bedroom_floor_b1 at both the 03:00 and 18:00 passes, with no intermediate sightings to suggest movement. On weekends the 16:00 pass finds it at couch_l1 on two occasions (and at bedroom_floor_b1 once), indicating a mid-afternoon relocation to the living room where it simply rests — perhaps propped against the couch while Hana reads or naps. By the 22:00 pass it is back in the bedroom.

This hypothesis directly contradicts p_b1c6 ("Guitar is the Evening Anchor, 19–21 daily") and p_c4f1 (its fork), which predict ON_PERSON sightings during the 19:00–21:00 window. The absence of any ON_PERSON sighting across 6 days is strong evidence against evening playing. It also contradicts p_c9d4's claim of the guitar at coffee_table_l1 at 22:00.

What would refute this: any ON_PERSON sighting of the guitar, or a sighting at coffee_table_l1 on a weekday evening.

```json
{
 "claims": [
  {
   "claim": "The guitar is on the bedroom floor at 18:30 on a weekday (not being played)",
   "target": "guitar_hana",
   "expect": "bedroom_floor_b1",
   "days": "weekday",
   "from": 18,
   "to": 20
  },
  {
   "claim": "The guitar is on the couch at 16:00 on a Saturday (resting, not played)",
   "target": "guitar_hana",
   "expect": "couch_l1",
   "days": "weekend",
   "from": 15,
   "to": 17
  },
  {
   "claim": "The guitar is on the bedroom floor at 22:00 on a weekday",
   "target": "guitar_hana",
   "expect": "bedroom_floor_b1",
   "days": "weekday",
   "from": 21,
   "to": 23
  },
  {
   "claim": "The guitar is on the bedroom floor at 09:00 on a weekday (never moved during the day)",
   "target": "guitar_hana",
   "expect": "bedroom_floor_b1",
   "days": "weekday",
   "from": 8,
   "to": 17
  }
 ],
 "targets": {
  "guitar_hana": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "bedroom_floor_b1",
    "chance": "almost_always"
   },
   {
    "days": "weekend",
    "from": 14,
    "to": 18,
    "at": "couch_l1",
    "chance": "sometimes"
   },
   {
    "days": "weekend",
    "from": 19,
    "to": 24,
    "at": "bedroom_floor_b1",
    "chance": "usually"
   }
  ]
 }
}
```
