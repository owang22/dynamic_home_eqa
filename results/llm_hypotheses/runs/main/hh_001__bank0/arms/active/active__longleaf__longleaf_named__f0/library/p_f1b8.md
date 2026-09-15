# p_f1b8 — Mara is a student; at school 9:00–16:00 weekdays, library in the afternoon

Mara is a university student. She leaves for campus around 8:30 on weekdays and returns around 16:30. Her tablet, pen, and book go with her. The lunchbox is packed the night before and taken to campus. The yoga mat is used in the evening (19:00–19:30) as a wind-down. The suitcase is for a study away or weekend trip to a friend's city. The watering can is used on weekends only (she's too rushed on weekdays). The medication bottle is taken in the morning and evening at home. The hairbrush and makeup kit are used in the morning before leaving.

What sets this apart: on a weekday at 11:00, the tablet, pen, book, and lunchbox are all OUT_OF_HOUSE. The yoga mat is on the couch during the day but on the floor at 19:15. The watering can stays in the sink on weekdays. What would refute it: the tablet found in the house at 11:00 on a weekday, or the watering can at the counter on a weekday morning.

```json
{"claims": [
   {"claim": "The tablet is out of the house with Mara at school on weekdays",
    "target": "tablet_mara", "expect": "OUT_OF_HOUSE", "days": "weekday", "from": 9, "to": 16},
   {"claim": "The book is out of the house on weekdays (taken to campus)",
    "target": "book_mara", "expect": "OUT_OF_HOUSE", "days": "weekday", "from": 9, "to": 16},
   {"claim": "The yoga mat is on the floor during the evening wind-down",
    "target": "yoga_mat_mara", "expect": "couch_l1", "days": "weekday", "from": 19, "to": 19.5},
   {"claim": "The watering can stays in the sink on weekdays",
    "target": "watering_can_mara", "expect": "sink_k1", "days": "weekday", "from": 7, "to": 12}
],
 "targets": {
   "tablet_mara": [
     {"days": "both", "from": 0, "to": 24, "at": "coffee_table_l1", "chance": "usually"},
     {"days": "weekday", "from": 8.5, "to": 16.5, "at": "OUT_OF_HOUSE", "chance": "almost_always"},
     {"days": "both", "from": 17, "to": 22, "at": "desk_b1", "chance": "sometimes"}],
   "book_mara": [
     {"days": "both", "from": 0, "to": 24, "at": "bookshelf_l1", "chance": "usually"},
     {"days": "weekday", "from": 8.5, "to": 16.5, "at": "OUT_OF_HOUSE", "chance": "almost_always"}],
   "pen_mara": [
     {"days": "both", "from": 0, "to": 24, "at": "kitchen_table_k1", "chance": "usually"},
     {"days": "weekday", "from": 8.5, "to": 16.5, "at": "OUT_OF_HOUSE", "chance": "almost_always"}],
   "lunchbox_mara": [
     {"days": "both", "from": 0, "to": 24, "at": "counter_k1", "chance": "usually"},
     {"days": "weekday", "from": 8.5, "to": 16.5, "at": "OUT_OF_HOUSE", "chance": "almost_always"}],
   "yoga_mat_mara": [
     {"days": "both", "from": 0, "to": 24, "at": "couch_l1", "chance": "usually"},
     {"days": "weekday", "from": 19, "to": 19.5, "at": "couch_l1", "chance": "usually"},
     {"days": "weekend", "from": 9, "to": 10, "at": "couch_l1", "chance": "usually"}],
   "suitcase_mara": [
     {"days": "both", "from": 0, "to": 24, "at": "bedroom_floor_b1", "chance": "usually"},
     {"days": "weekend", "from": 8, "to": 22, "at": "OUT_OF_HOUSE", "chance": "sometimes"}],
   "watering_can_mara": [
     {"days": "both", "from": 0, "to": 24, "at": "sink_k1", "chance": "usually"},
     {"days": "weekend", "from": 10, "to": 12, "at": "counter_k1", "chance": "usually"}],
   "hairbrush_mara": [
     {"days": "both", "from": 0, "to": 24, "at": "nightstand_b1", "chance": "usually"},
     {"days": "both", "from": 7, "to": 8.5, "at": "bathroom_shelf_ba1", "chance": "usually"}],
   "makeup_kit_mara": [
     {"days": "both", "from": 0, "to": 24, "at": "bathroom_shelf_ba1", "chance": "usually"},
     {"days": "both", "from": 7, "to": 8.5, "at": "nightstand_b1", "chance": "sometimes"}],
   "medication_bottle_mara": [
     {"days": "both", "from": 0, "to": 24, "at": "bathroom_shelf_ba1", "chance": "almost_always"},
     {"days": "both", "from": 7.5, "to": 8.5, "at": "counter_k1", "chance": "sometimes"}],
   "remote_shared_1": [
     {"days": "both", "from": 0, "to": 24, "at": "coffee_table_l1", "chance": "usually"},
     {"days": "both", "from": 19, "to": 23, "at": "couch_l1", "chance": "sometimes"}],
   "blanket_mara": [
     {"days": "both", "from": 0, "to": 24, "at": "couch_l1", "chance": "usually"}],
   "vacuum_cleaner_shared_1": [
     {"days": "both", "from": 0, "to": 24, "at": "bedroom_floor_b1", "chance": "usually"},
     {"days": "weekend", "from": 14, "to": 16, "at": "couch_l1", "chance": "sometimes"}],
   "class:mug": [
     {"days": "both", "from": 0, "to": 24, "at": "cupboard_k1", "chance": "usually"},
     {"days": "both", "from": 7, "to": 8.5, "at": "kitchen_table_k1", "chance": "usually"},
     {"days": "both", "from": 17, "to": 19, "at": "kitchen_table_k1", "chance": "sometimes"}],
   "class:plate": [
     {"days": "both", "from": 0, "to": 24, "at": "cupboard_k1", "chance": "usually"},
     {"days": "both", "from": 7, "to": 8.5, "at": "kitchen_table_k1", "chance": "usually"},
     {"days": "both", "from": 18, "to": 21, "at": "kitchen_table_k1", "chance": "usually"}],
   "class:bowl": [
     {"days": "both", "from": 0, "to": 24, "at": "cupboard_k1", "chance": "usually"},
     {"days": "both", "from": 7, "to": 8.5, "at": "kitchen_table_k1", "chance": "usually"}],
   "class:pan": [
     {"days": "both", "from": 0, "to": 24, "at": "sink_k1", "chance": "usually"},
     {"days": "both", "from": 17, "to": 19, "at": "counter_k1", "chance": "sometimes"}],
   "class:pot": [
     {"days": "both", "from": 0, "to": 24, "at": "cupboard_k1", "chance": "usually"}],
   "towel_mara": [
     {"days": "both", "from": 0, "to": 24, "at": "towel_rack_ba1", "chance": "usually"}],
   "laundry_basket_mara": [
     {"days": "both", "from": 0, "to": 24, "at": "bedroom_floor_b1", "chance": "usually"}],
   "umbrella_mara": [
     {"days": "both", "from": 0, "to": 24, "at": "entry_floor_e1", "chance": "usually"},
     {"days": "weekday", "from": 8.5, "to": 16.5, "at": "OUT_OF_HOUSE", "chance": "rarely"}]
 }}
```
