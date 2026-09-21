# p_9d2c — Weekend Evening Living Room; Blanket on the Coffee Table, Guitar on the Couch

On weekend evenings the living room fills with the day's activities converging. The blanket, which spent the morning on bed_b1 while Hana slept in (seen at 03:00, 07:00, and 08:00), moves to coffee_table_l1 by 20:00 (three sightings at 20:00, one still at bed_b1). Hana plays guitar on couch_l1 from roughly 20:00 to 23:00 (two sightings at 21:00, one still at bedroom_floor_b1). Priya unrolls her yoga mat on floor_l_l1 around 20:00 (one sighting). The duster, set down on the coffee table during the afternoon dusting, is still there at 19:00 (two sightings). The vacuum, after being used on the floor, is at coffee_table_l1 at 17:00.

This document corrects p_4e7a, which placed the blanket at couch_l1 during weekend guitar playing and was contradicted six times (0 for, 6 against). The blanket is on the coffee table, not the couch, during the weekend evening. It also extends p_5e2a and p_d5a9 by adding the duster and vacuum at the coffee table as part of the same evening scene.

On weekdays the blanket follows a different pattern: armchair_l1 in the early morning after Hana's shift (03:00, two sightings), couch_l1 through the afternoon (07:00, 16:00, 17:00, 18:00, 19:00), and coffee_table_l1 at 14:00 and 17:00. The guitar stays at bedroom_floor_b1 all weekday.

What would refute this document: if the blanket is found on the couch during the weekend 19–22 h window, or if the guitar is in the bedroom during that window on a weekend evening.

```json
{
 "claims": [
  {
   "claim": "The blanket is on the coffee table during the weekend evening",
   "target": "blanket_shared",
   "expect": "coffee_table_l1",
   "days": "weekend",
   "from": 19,
   "to": 22
  },
  {
   "claim": "Hana plays guitar on the couch during the weekend evening",
   "target": "guitar_hana",
   "expect": "couch_l1",
   "days": "weekend",
   "from": 20,
   "to": 23
  },
  {
   "claim": "Priya's yoga mat is on the living room floor during the weekend evening",
   "target": "yoga_mat_priya",
   "expect": "floor_l_l1",
   "days": "weekend",
   "from": 19,
   "to": 21
  },
  {
   "claim": "The duster is on the coffee table during the weekend evening after dusting",
   "target": "duster_shared",
   "expect": "coffee_table_l1",
   "days": "weekend",
   "from": 17,
   "to": 20
  }
 ],
 "targets": {
  "blanket_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "couch_l1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 2,
    "to": 5,
    "at": "armchair_l1",
    "chance": "sometimes"
   },
   {
    "days": "weekend",
    "from": 2,
    "to": 9,
    "at": "bed_b1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 19,
    "to": 22,
    "at": "coffee_table_l1",
    "chance": "usually"
   }
  ],
  "guitar_hana": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "bedroom_floor_b1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 19,
    "to": 23,
    "at": "couch_l1",
    "chance": "usually"
   }
  ],
  "yoga_mat_priya": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "wardrobe_b2",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 19,
    "to": 21,
    "at": "floor_l_l1",
    "chance": "sometimes"
   }
  ],
  "duster_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "storage_shelf_s1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 16,
    "to": 21,
    "at": "coffee_table_l1",
    "chance": "usually"
   }
  ]
 }
}
```
