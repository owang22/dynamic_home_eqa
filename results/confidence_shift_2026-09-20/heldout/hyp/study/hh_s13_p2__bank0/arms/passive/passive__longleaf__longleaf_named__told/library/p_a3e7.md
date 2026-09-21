# p_a3e7 — Weekend Living Room Takeover: Remote, Blanket, and Board Game Out All Day

On weekends the living room becomes the single gravitational center of the house, and the objects that orbit it never go back to their weekday resting spots. The remote is on the coffee table from the moment the residents wake until the last patrol at 22:00 — every single weekend sighting in the log (all twelve hours, both Saturday and Sunday) puts it at coffee_table_l1, never at the TV stand. The blanket is on the armchair for the full waking day (00:00–20:00 sightings all at armchair_l1) and only shifts to the coffee table at 22:00, when the evening settles in. The board game is out on the coffee table all day, every hour, both weekend days — it is never put back on the bookshelf on a Saturday or Sunday. The tissue box, candle, and coasters are also fixed to the coffee table all day.

This hypothesis is set apart from p_9b6e (which puts the remote at tv_stand_l1 and the blanket at couch_l1 in the afternoon) and from p_c9d4 (which puts the remote on the couch at 22:00 on weekdays). The weekend remote is NOT at the TV stand; it is at the coffee table because the residents are sitting in the living room all day, not standing at the TV. The blanket is on the armchair, not the couch — it is draped over the chair where Priya reads or where Hana lounges, not pulled over the couch for a TV session.

This document is refuted if a weekend look at 10:00–16:00 finds the remote at tv_stand_l1, the blanket at couch_l1, or the board game at bookshelf_l1.

```json
{
 "claims": [
  {
   "claim": "The remote is on the coffee table at noon on a Saturday because the residents are in the living room all day",
   "target": "remote_shared",
   "expect": "coffee_table_l1",
   "days": "weekend",
   "from": 11,
   "to": 14
  },
  {
   "claim": "The blanket is on the armchair at 2 PM on a Saturday because it is draped over the chair for lounging, not pulled over the couch",
   "target": "blanket_shared",
   "expect": "armchair_l1",
   "days": "weekend",
   "from": 13,
   "to": 16
  },
  {
   "claim": "The board game is on the coffee table at 10 AM on a Saturday because it is left out all day on weekends",
   "target": "board_game_shared",
   "expect": "coffee_table_l1",
   "days": "weekend",
   "from": 9,
   "to": 12
  },
  {
   "claim": "The remote is on the coffee table at 8 PM on a Saturday, not at the TV stand",
   "target": "remote_shared",
   "expect": "coffee_table_l1",
   "days": "weekend",
   "from": 19,
   "to": 22
  }
 ],
 "targets": {
  "remote_shared": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "coffee_table_l1",
    "chance": "almost_always"
   }
  ],
  "blanket_shared": [
   {
    "days": "weekend",
    "from": 0,
    "to": 21,
    "at": "armchair_l1",
    "chance": "almost_always"
   },
   {
    "days": "weekend",
    "from": 21,
    "to": 24,
    "at": "coffee_table_l1",
    "chance": "usually"
   }
  ],
  "board_game_shared": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "coffee_table_l1",
    "chance": "almost_always"
   }
  ],
  "tissue_box_shared": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "coffee_table_l1",
    "chance": "almost_always"
   }
  ],
  "candle_shared": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "coffee_table_l1",
    "chance": "almost_always"
   }
  ],
  "coasters_shared": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "coffee_table_l1",
    "chance": "almost_always"
   }
  ]
 }
}
```
