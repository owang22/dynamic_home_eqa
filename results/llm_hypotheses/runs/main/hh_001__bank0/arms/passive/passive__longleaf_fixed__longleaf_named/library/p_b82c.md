# p_b82c — Mara commutes to an office; the house is empty 8:30–17:30 on weekdays

Mara works a standard office job. She leaves the house around 8:30 on weekdays and returns around 17:30. Her tablet, pen, and lunchbox go with her. The umbrella stays at the entry unless it's raining, in which case it leaves with her. The hairbrush and makeup kit are used in the morning before she leaves and then sit on the nightstand or bathroom shelf until the next morning. The yoga mat stays rolled on the couch during the week (she only exercises weekends). The suitcase is packed for a weekend trip she takes every other Saturday.

What sets this apart: on a weekday at 12:00, the tablet, pen, and lunchbox are OUT_OF_HOUSE, and the house is otherwise still. The yoga mat is on the couch all week. What would refute it: the tablet found at the coffee table or desk between 9:00 and 16:00 on a weekday.

```json
{"claims": [
   {"claim": "The tablet is out of the house with Mara on weekday work hours",
    "target": "tablet_mara", "expect": "OUT_OF_HOUSE", "days": "weekday", "from": 9, "to": 17},
   {"claim": "The lunchbox leaves the house with Mara for work on weekdays",
    "target": "lunchbox_mara", "expect": "OUT_OF_HOUSE", "days": "weekday", "from": 8.5, "to": 17.5},
   {"claim": "The yoga mat stays rolled on the couch all week",
    "target": "yoga_mat_mara", "expect": "couch_l1", "days": "weekday", "from": 0, "to": 24},
   {"claim": "The pen is out of the house on weekday work hours",
   "target": "pen_mara", "expect": "OUT_OF_HOUSE", "days": "weekday", "from": 9, "to": 17}
],
 "targets": {
   "tablet_mara": [
     {"days": "both", "from": 0, "to": 24, "at": "coffee_table_l1", "chance": "usually"},
     {"days": "weekday", "from": 8.5, "to": 17.5, "at": "OUT_OF_HOUSE", "chance": "almost_always"}],
   "pen_mara": [
     {"days": "both", "from": 0, "to": 24, "at": "kitchen_table_k1", "chance": "usually"},
     {"days": "weekday", "from": 8.5, "to": 17.5, "at": "OUT_OF_HOUSE", "chance": "almost_always"}],
   "lunchbox_mara": [
     {"days": "both", "from": 0, "to": 24, "at": "counter_k1", "chance": "usually"},
     {"days": "weekday", "from": 8.5, "to": 17.5, "at": "OUT_OF_HOUSE", "chance": "almost_always"}],
   "umbrella_mara": [
     {"days": "both", "from": 0, "to": 24, "at": "entry_floor_e1", "chance": "usually"},
     {"days": "weekday", "from": 8.5, "to": 17.5, "at": "OUT_OF_HOUSE", "chance": "rarely"}],
   "yoga_mat_mara": [
     {"days": "both", "from": 0, "to": 24, "at": "couch_l1", "chance": "usually"},
     {"days": "weekend", "from": 9, "to": 11, "at": "couch_l1", "chance": "usually"}],
   "suitcase_mara": [
     {"days": "both", "from": 0, "to": 24, "at": "bedroom_floor_b1", "chance": "usually"},
     {"days": "weekend", "from": 8, "to": 22, "at": "OUT_OF_HOUSE", "chance": "sometimes"}],
   "hairbrush_mara": [
     {"days": "both", "from": 0, "to": 24, "at": "nightstand_b1", "chance": "usually"},
     {"days": "both", "from": 6, "to": 8, "at": "bathroom_shelf_ba1", "chance": "sometimes"}],
   "makeup_kit_mara": [
     {"days": "both", "from": 0, "to": 24, "at": "bathroom_shelf_ba1", "chance": "usually"},
     {"days": "both", "from": 6.5, "to": 8.5, "at": "nightstand_b1", "chance": "sometimes"}],
   "medication_bottle_mara": [
     {"days": "both", "from": 0, "to": 24, "at": "bathroom_shelf_ba1", "chance": "almost_always"}],
   "remote_shared_1": [
     {"days": "both", "from": 0, "to": 24, "at": "coffee_table_l1", "chance": "usually"},
     {"days": "weekday", "from": 18, "to": 22, "at": "armchair_l1", "chance": "sometimes"}],
   "blanket_mara": [
     {"days": "both", "from": 0, "to": 24, "at": "couch_l1", "chance": "usually"}],
   "watering_can_mara": [
     {"days": "both", "from": 0, "to": 24, "at": "sink_k1", "chance": "usually"},
     {"days": "weekend", "from": 9, "to": 11, "at": "counter_k1", "chance": "sometimes"}],
   "vacuum_cleaner_shared_1": [
     {"days": "both", "from": 0, "to": 24, "at": "bedroom_floor_b1", "chance": "usually"},
     {"days": "weekend", "from": 14, "to": 16, "at": "couch_l1", "chance": "sometimes"}],
   "class:mug": [
     {"days": "both", "from": 0, "to": 24, "at": "cupboard_k1", "chance": "usually"},
     {"days": "both", "from": 7, "to": 8.5, "at": "counter_k1", "chance": "usually"},
     {"days": "weekday", "from": 8.5, "to": 17.5, "at": "cupboard_k1", "chance": "usually"}],
   "class:plate": [
     {"days": "both", "from": 0, "to": 24, "at": "cupboard_k1", "chance": "usually"},
     {"days": "both", "from": 18, "to": 21, "at": "counter_k1", "chance": "sometimes"}],
   "class:bowl": [
     {"days": "both", "from": 0, "to": 24, "at": "cupboard_k1", "chance": "usually"},
     {"days": "both", "from": 7, "to": 9, "at": "kitchen_table_k1", "chance": "usually"}],
   "class:pan": [
     {"days": "both", "from": 0, "to": 24, "at": "sink_k1", "chance": "usually"}],
   "class:pot": [
     {"days": "both", "from": 0, "to": 24, "at": "cupboard_k1", "chance": "usually"}],
   "book_mara": [
     {"days": "both", "from": 0, "to": 24, "at": "bookshelf_l1", "chance": "usually"},
     {"days": "both", "from": 21, "to": 23, "at": "couch_l1", "chance": "sometimes"}],
   "towel_mara": [
     {"days": "both", "from": 0, "to": 24, "at": "towel_rack_ba1", "chance": "usually"}],
   "laundry_basket_mara": [
     {"days": "both", "from": 0, "to": 24, "at": "bedroom_floor_b1", "chance": "usually"}]
 }}
```
