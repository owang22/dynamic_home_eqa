# p_3b8a — Mara works in healthcare (rotating shifts); the schedule is irregular

Mara is a nurse or doctor on rotating shifts. Some weeks she works days (7:00–15:00), other weeks nights (19:00–07:00), and some weeks weekends. The model here assumes a "day shift" week: she leaves at 6:45 and returns at 15:15. The tablet stays home (hospital provides its own devices). The medication bottle is taken at 7:00 before leaving. The lunchbox is packed the night before and taken to work. The yoga mat is used on days off (weekends or the 2 days off per week). The suitcase is for on-call overnights (rare). The watering can is used on days off only. The hairbrush and makeup kit are used in the morning before leaving.

What sets this apart: on a weekday at 10:00 (day-shift week), the tablet is in the house but the lunchbox is OUT_OF_HOUSE. At 16:00, Mara is home and the tablet is at the coffee table. On a "night shift" week (not modeled here but the pattern would flip), the tablet would be in the house at 10:00 AND the lunchbox would be in the house. What would refute it: the tablet found OUT_OF_HOUSE on a weekday, or the lunchbox found in the house at 10:00 on a weekday.

```json
{"claims": [
   {"claim": "The tablet is in the house at 10:00 on weekdays (hospital provides its own tech)",
    "target": "tablet_mara", "expect": "coffee_table_l1", "days": "weekday", "from": 9, "to": 16},
   {"claim": "The lunchbox is out of the house during work hours on weekdays",
    "target": "lunchbox_mara", "expect": "OUT_OF_HOUSE", "days": "weekday", "from": 7, "to": 15},
   {"claim": "The medication bottle is at the counter during the 7:00 morning dose",
    "target": "medication_bottle_mara", "expect": "counter_k1", "days": "weekday", "from": 6.5, "to": 7.5},
   {"claim": "The yoga mat is on the floor on Saturday (day off)",
    "target": "yoga_mat_mara", "expect": "couch_l1", "days": "weekend", "from": 10, "to": 11}
],
 "targets": {
   "tablet_mara": [
     {"days": "both", "from": 0, "to": 24, "at": "coffee_table_l1", "chance": "usually"},
     {"days": "both", "from": 19, "to": 22, "at": "couch_l1", "chance": "sometimes"}],
   "lunchbox_mara": [
     {"days": "both", "from": 0, "to": 24, "at": "counter_k1", "chance": "usually"},
     {"days": "weekday", "from": 6.5, "to": 15.5, "at": "OUT_OF_HOUSE", "chance": "almost_always"}],
   "medication_bottle_mara": [
     {"days": "both", "from": 0, "to": 24, "at": "bathroom_shelf_ba1", "chance": "usually"},
     {"days": "weekday", "from": 6.5, "to": 7.5, "at": "counter_k1", "chance": "usually"},
     {"days": "weekday", "from": 15, "to": 16, "at": "counter_k1", "chance": "sometimes"}],
   "yoga_mat_mara": [
     {"days": "both", "from": 0, "to": 24, "at": "couch_l1", "chance": "usually"},
     {"days": "weekend", "from": 10, "to": 11, "at": "couch_l1", "chance": "usually"}],
   "suitcase_mara": [
     {"days": "both", "from": 0, "to": 24, "at": "bedroom_floor_b1", "chance": "usually"},
     {"days": "both", "from": 0, "to": 24, "at": "OUT_OF_HOUSE", "chance": "rarely"}],
   "hairbrush_mara": [
     {"days": "both", "from": 0, "to": 24, "at": "nightstand_b1", "chance": "usually"},
     {"days": "weekday", "from": 6, "to": 7.5, "at": "bathroom_shelf_ba1", "chance": "usually"}],
   "makeup_kit_mara": [
     {"days": "both", "from": 0, "to": 24, "at": "bathroom_shelf_ba1", "chance": "usually"},
     {"days": "weekday", "from": 6, "to": 7.5, "at": "nightstand_b1", "chance": "sometimes"}],
   "pen_mara": [
     {"days": "both", "from": 0, "to": 24, "at": "kitchen_table_k1", "chance": "usually"},
     {"days": "weekday", "from": 6.5, "to": 15.5, "at": "OUT_OF_HOUSE", "chance": "sometimes"}],
   "watering_can_mara": [
     {"days": "both", "from": 0, "to": 24, "at": "sink_k1", "chance": "usually"},
     {"days": "weekend", "from": 10, "to": 12, "at": "counter_k1", "chance": "usually"}],
   "remote_shared_1": [
     {"days": "both", "from": 0, "to": 24, "at": "coffee_table_l1", "chance": "usually"},
     {"days": "both", "from": 16, "to": 22, "at": "couch_l1", "chance": "sometimes"}],
   "blanket_mara": [
     {"days": "both", "from": 0, "to": 24, "at": "couch_l1", "chance": "usually"}],
   "vacuum_cleaner_shared_1": [
     {"days": "both", "from": 0, "to": 24, "at": "bedroom_floor_b1", "chance": "usually"},
     {"days": "weekend", "from": 13, "to": 15, "at": "couch_l1", "chance": "sometimes"}],
   "class:mug": [
     {"days": "both", "from": 0, "to": 24, "at": "cupboard_k1", "chance": "usually"},
     {"days": "both", "from": 6.5, "to": 7.5, "at": "kitchen_table_k1", "chance": "usually"},
     {"days": "both", "from": 16, "to": 18, "at": "kitchen_table_k1", "chance": "sometimes"},
     {"days": "both", "from": 19, "to": 21, "at": "kitchen_table_k1", "chance": "usually"}],
   "class:plate": [
     {"days": "both", "from": 0, "to": 24, "at": "cupboard_k1", "chance": "usually"},
     {"days": "both", "from": 6.5, "to": 7.5, "at": "kitchen_table_k1", "chance": "usually"},
     {"days": "both", "from": 19, "to": 21, "at": "kitchen_table_k1", "chance": "usually"}],
   "class:bowl": [
     {"days": "both", "from": 0, "to": 24, "at": "cupboard_k1", "chance": "usually"},
     {"days": "both", "from": 6.5, "to": 7.5, "at": "kitchen_table_k1", "chance": "usually"}],
   "class:pan": [
     {"days": "both", "from": 0, "to": 24, "at": "sink_k1", "chance": "usually"},
     {"days": "both", "from": 17, "to": 19, "at": "counter_k1", "chance": "sometimes"}],
   "class:pot": [
     {"days": "both", "from": 0, "to": 24, "at": "cupboard_k1", "chance": "usually"}],
   "book_mara": [
     {"days": "both", "from": 0, "to": 24, "at": "bookshelf_l1", "chance": "usually"},
     {"days": "both", "from": 21, "to": 23, "at": "couch_l1", "chance": "sometimes"}],
   "towel_mara": [
     {"days": "both", "from": 0, "to": 24, "at": "towel_rack_ba1", "chance": "usually"}],
   "laundry_basket_mara": [
     {"days": "both", "from": 0, "to": 24, "at": "bedroom_floor_b1", "chance": "usually"}],
   "umbrella_mara": [
     {"days": "both", "from": 0, "to": 24, "at": "entry_floor_e1", "chance": "usually"},
     {"days": "weekday", "from": 6.5, "to": 15.5, "at": "OUT_OF_HOUSE", "chance": "rarely"}]
 }}
```
