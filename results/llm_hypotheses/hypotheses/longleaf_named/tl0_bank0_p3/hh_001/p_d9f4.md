# p_d9f4 — Mara works evening shifts (16:00–00:00); the house is lively in the morning

Mara is a nurse or works in hospitality. On weekdays she sleeps in until around 13:00, does errands and cooking in the afternoon, and leaves for her shift at 16:00, returning around 00:00. The house is active in the morning (10:00–14:00) when she's up and about. The tablet stays at home (she doesn't bring it to work). The lunchbox is packed the night before for her pre-shift meal and sits on the counter. The yoga mat is used in the morning (10:00–11:00) before she fully wakes up. The suitcase is for a work trip (she's on call for out-of-town shifts). The medication bottle is taken with her in the evening.

What sets this apart: on a weekday at 12:00, Mara is home and the tablet is at the coffee table, the yoga mat may be on the floor, and the lunchbox is on the counter. At 18:00, the medication bottle is OUT_OF_HOUSE. The house is empty 16:00–00:00 on weekdays. What would refute it: the tablet found OUT_OF_HOUSE on a weekday, or the medication bottle found on the bathroom shelf at 20:00 on a weekday.

```json
{"claims": [
   {"claim": "The tablet is at the coffee table at noon on weekdays (Mara is home)",
    "target": "tablet_mara", "expect": "coffee_table_l1", "days": "weekday", "from": 11, "to": 15},
   {"claim": "The medication bottle is out of the house during evening shift hours",
    "target": "medication_bottle_mara", "expect": "OUT_OF_HOUSE", "days": "weekday", "from": 16, "to": 23},
   {"claim": "The yoga mat is in use in the morning on weekdays",
    "target": "yoga_mat_mara", "expect": "couch_l1", "days": "weekday", "from": 10, "to": 11},
   {"claim": "The lunchbox is on the counter at noon on weekdays",
    "target": "lunchbox_mara", "expect": "counter_k1", "days": "weekday", "from": 10, "to": 15}
],
 "targets": {
   "tablet_mara": [
     {"days": "both", "from": 0, "to": 24, "at": "coffee_table_l1", "chance": "usually"},
     {"days": "weekday", "from": 10, "to": 15, "at": "coffee_table_l1", "chance": "usually"}],
   "medication_bottle_mara": [
     {"days": "both", "from": 0, "to": 24, "at": "bathroom_shelf_ba1", "chance": "usually"},
     {"days": "weekday", "from": 16, "to": 23.5, "at": "OUT_OF_HOUSE", "chance": "almost_always"}],
   "yoga_mat_mara": [
     {"days": "both", "from": 0, "to": 24, "at": "couch_l1", "chance": "usually"},
     {"days": "weekday", "from": 10, "to": 11, "at": "couch_l1", "chance": "usually"}],
   "lunchbox_mara": [
     {"days": "both", "from": 0, "to": 24, "at": "counter_k1", "chance": "usually"},
     {"days": "weekday", "from": 15.5, "to": 17, "at": "OUT_OF_HOUSE", "chance": "sometimes"}],
   "suitcase_mara": [
     {"days": "both", "from": 0, "to": 24, "at": "bedroom_floor_b1", "chance": "usually"},
     {"days": "both", "from": 15, "to": 23, "at": "OUT_OF_HOUSE", "chance": "rarely"}],
   "hairbrush_mara": [
     {"days": "both", "from": 0, "to": 24, "at": "nightstand_b1", "chance": "usually"},
     {"days": "both", "from": 10, "to": 12, "at": "bathroom_shelf_ba1", "chance": "sometimes"}],
   "makeup_kit_mara": [
     {"days": "both", "from": 0, "to": 24, "at": "bathroom_shelf_ba1", "chance": "usually"},
     {"days": "weekday", "from": 14, "to": 16, "at": "nightstand_b1", "chance": "sometimes"}],
   "pen_mara": [
     {"days": "both", "from": 0, "to": 24, "at": "kitchen_table_k1", "chance": "usually"},
     {"days": "weekday", "from": 16, "to": 23, "at": "OUT_OF_HOUSE", "chance": "sometimes"}],
   "remote_shared_1": [
     {"days": "both", "from": 0, "to": 24, "at": "coffee_table_l1", "chance": "usually"},
     {"days": "both", "from": 10, "to": 14, "at": "couch_l1", "chance": "sometimes"}],
   "blanket_mara": [
     {"days": "both", "from": 0, "to": 24, "at": "couch_l1", "chance": "usually"},
     {"days": "both", "from": 13, "to": 16, "at": "bed_b1", "chance": "sometimes"}],
   "watering_can_mara": [
     {"days": "both", "from": 0, "to": 24, "at": "sink_k1", "chance": "usually"},
     {"days": "both", "from": 10, "to": 12, "at": "counter_k1", "chance": "sometimes"}],
   "vacuum_cleaner_shared_1": [
     {"days": "both", "from": 0, "to": 24, "at": "bedroom_floor_b1", "chance": "usually"},
     {"days": "weekend", "from": 11, "to": 13, "at": "couch_l1", "chance": "sometimes"}],
   "class:mug": [
     {"days": "both", "from": 0, "to": 24, "at": "cupboard_k1", "chance": "usually"},
     {"days": "both", "from": 10, "to": 13, "at": "kitchen_table_k1", "chance": "usually"},
     {"days": "both", "from": 15, "to": 17, "at": "counter_k1", "chance": "sometimes"}],
   "class:plate": [
     {"days": "both", "from": 0, "to": 24, "at": "cupboard_k1", "chance": "usually"},
     {"days": "both", "from": 10, "to": 13, "at": "kitchen_table_k1", "chance": "usually"},
     {"days": "both", "from": 15, "to": 17, "at": "counter_k1", "chance": "sometimes"}],
   "class:bowl": [
     {"days": "both", "from": 0, "to": 24, "at": "cupboard_k1", "chance": "usually"},
     {"days": "both", "from": 10, "to": 13, "at": "kitchen_table_k1", "chance": "usually"}],
   "class:pan": [
     {"days": "both", "from": 0, "to": 24, "at": "sink_k1", "chance": "usually"},
     {"days": "both", "from": 15, "to": 17, "at": "counter_k1", "chance": "sometimes"}],
   "class:pot": [
     {"days": "both", "from": 0, "to": 24, "at": "cupboard_k1", "chance": "usually"}],
   "book_mara": [
     {"days": "both", "from": 0, "to": 24, "at": "bookshelf_l1", "chance": "usually"},
     {"days": "both", "from": 13, "to": 16, "at": "bed_b1", "chance": "sometimes"}],
   "towel_mara": [
     {"days": "both", "from": 0, "to": 24, "at": "towel_rack_ba1", "chance": "usually"}],
   "laundry_basket_mara": [
     {"days": "both", "from": 0, "to": 24, "at": "bedroom_floor_b1", "chance": "usually"}],
   "umbrella_mara": [
     {"days": "both", "from": 0, "to": 24, "at": "entry_floor_e1", "chance": "usually"},
     {"days": "weekday", "from": 16, "to": 23, "at": "OUT_OF_HOUSE", "chance": "rarely"}]
 }}
```
