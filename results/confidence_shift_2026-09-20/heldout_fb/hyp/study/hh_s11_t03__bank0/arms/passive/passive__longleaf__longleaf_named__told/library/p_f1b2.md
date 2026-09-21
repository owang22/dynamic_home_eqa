# p_f1b2 — Weekend Evening; Guitar to the Couch, Yoga to the Floor, Blanket to the Bed

On weekends the evening routine reshuffles the living room. Hana, off work, moves her guitar from the bedroom floor to the couch around 20:00 to play while she watches TV or chats with Priya (two weekend 21:00 sightings at couch_l1 versus one at bedroom_floor_b1). Priya unrolls her yoga mat on the living room floor around 19:30–20:00 for her evening session (one weekend 20:00 sighting at floor_l_l1), then rolls it back up and returns it to wardrobe_b2 by 21:00. The shared blanket, which on weekend mornings is on Hana's bed (two 03:00, one 07:00, one 08:00 sightings at bed_b1), migrates to the coffee table by 20:00 for the evening TV session (three weekend 20:00 sightings at coffee_table_l1).

This document differs from p_4b6f, which covers the same weekend evening but also claims the guitar stays in the bedroom on weekdays (a claim that is true but not distinctive here). It differs from p_5b9c, which places the yoga mat on the floor from 19:00 to 21:00 on weekends; here the window is 19.5–21:00 to avoid conflict with the 19:00 pass where the mat is still in the wardrobe. It also differs from p_e7a3, which places the blanket on bed_b1 from 0:00 to 9:00 on weekends (matching the morning evidence) but does not specify the 20:00 coffee-table migration.

The document would be refuted if the guitar is consistently in the bedroom at the 21:00 weekend pass (no couch sightings), or if the yoga mat is found in the wardrobe at the 20:00 weekend pass (no floor sighting), or if the blanket is on the couch rather than the bed at the 03:00 weekend pass.

```json
{
 "claims": [
  {
   "claim": "Hana's guitar is on the couch at the 21:00 weekend pass",
   "target": "guitar_hana",
   "expect": "couch_l1",
   "days": "weekend",
   "from": 20,
   "to": 23
  },
  {
   "claim": "Priya's yoga mat is on the living room floor at the 20:00 weekend pass",
   "target": "yoga_mat_priya",
   "expect": "floor_l_l1",
   "days": "weekend",
   "from": 19.5,
   "to": 21
  },
  {
   "claim": "The blanket is on Hana's bed at the 03:00 weekend pass",
   "target": "blanket_shared",
   "expect": "bed_b1",
   "days": "weekend",
   "from": 0,
   "to": 3
  },
  {
   "claim": "Hana's guitar stays in her bedroom at the 03:00 weekday pass",
   "target": "guitar_hana",
   "expect": "bedroom_floor_b1",
   "days": "weekday",
   "from": 0,
   "to": 3
  }
 ],
 "targets": {
  "guitar_hana": [
   {
    "days": "weekday",
    "from": 0,
    "to": 24,
    "at": "bedroom_floor_b1",
    "chance": "almost_always"
   },
   {
    "days": "weekend",
    "from": 0,
    "to": 20,
    "at": "bedroom_floor_b1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 20,
    "to": 24,
    "at": "couch_l1",
    "chance": "sometimes"
   }
  ],
  "yoga_mat_priya": [
   {
    "days": "weekend",
    "from": 0,
    "to": 19.5,
    "at": "wardrobe_b2",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 19.5,
    "to": 21,
    "at": "floor_l_l1",
    "chance": "sometimes"
   },
   {
    "days": "weekend",
    "from": 21,
    "to": 24,
    "at": "wardrobe_b2",
    "chance": "usually"
   }
  ],
  "blanket_shared": [
   {
    "days": "weekend",
    "from": 0,
    "to": 9,
    "at": "bed_b1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 9,
    "to": 19,
    "at": "couch_l1",
    "chance": "sometimes"
   },
   {
    "days": "weekend",
    "from": 19,
    "to": 24,
    "at": "coffee_table_l1",
    "chance": "sometimes"
   }
  ]
 }
}
```
