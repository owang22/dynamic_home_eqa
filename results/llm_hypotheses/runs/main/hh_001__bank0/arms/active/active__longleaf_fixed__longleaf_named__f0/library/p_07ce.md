# p_07ce — Mara works part-time (9:00–14:00); the afternoon is for errands and gym

Mara has a part-time job (retail or admin) from 9:00 to 14:00 on weekdays. She leaves at 8:45 and is back by 14:15. After work, she goes to the gym (15:00–16:30) three times a week (Mon/Wed/Fri) or does errands. The tablet stays home (work is manual or doesn't require it). The lunchbox is packed for her pre-work breakfast or taken to work. The yoga mat is used at home on Tue/Thu/Sat mornings. The suitcase is for a weekend getaway. The watering can is used every morning at 7:30. The medication bottle is taken at 8:00 and 20:00.

What sets this apart: on a weekday at 15:30 (Mon/Wed/Fri), Mara is at the gym so the house is empty, but the tablet is still at the coffee table. On a weekday at 11:00, the lunchbox may be OUT_OF_HOUSE but the tablet is in the house. The yoga mat is on the floor at 9:00 on Tue/Thu (not Mon/Wed/Fri). What would refute it: the tablet found OUT_OF_HOUSE on a weekday, or the yoga mat on the floor at 9:00 on a Monday.

```json
{"claims": [
   {"claim": "The tablet is at the coffee table at 15:30 on Monday (Mara is at the gym, not the office)",
    "target": "tablet_mara", "expect": "coffee_table_l1", "days": "weekday", "from": 15, "to": 17},
   {"claim": "The lunchbox is out of the house during work hours on weekdays",
    "target": "lunchbox_mara", "expect": "OUT_OF_HOUSE", "days": "weekday", "from": 9, "to": 14},
   {"claim": "The yoga mat is on the floor at 9:00 on Tuesday (yoga day)",
    "target": "yoga_mat_mara", "expect": "couch_l1", "days": "weekday", "from": 9, "to": 10},
   {"claim": "The medication bottle is at the counter during the 8:00 dose window",
    "target": "medication_bottle_mara", "expect": "counter_k1", "days": "both", "from": 7.5, "to": 8.5}
],
 "targets": {
   "tablet_mara": [
     {"days": "both", "from": 0, "to": 24, "at": "coffee_table_l1", "chance": "usually"},
     {"days": "both", "from": 19, "to": 22, "at": "couch_l1", "chance": "sometimes"}],
   "lunchbox_mara": [
     {"days": "both", "from": 0, "to": 24, "at": "counter_k1", "chance": "usually"},
     {"days": "weekday", "from": 8.5, "to": 14.5, "at": "OUT_OF_HOUSE", "chance": "usually"}],
   "yoga_mat_mara": [
     {"days": "both", "from": 0, "to": 24, "at": "couch_l1", "chance": "usually"},
     {"days": "weekday", "from": 9, "to": 10, "at": "couch_l1", "chance": "sometimes"},
     {"days": "weekend", "from": 9, "to": 10, "at": "couch_l1", "chance": "usually"}],
   "medication_bottle_mara": [
     {"days": "both", "from": 0, "to": 24, "at": "bathroom_shelf_ba1", "chance": "usually"},
     {"days": "both", "from": 7.5, "to": 8.5, "at": "counter_k1", "chance": "usually"},
     {"days": "both", "from": 19.5, "to": 20.5, "at": "counter_k1", "chance": "usually"}],
   "pen_mara": [
     {"days": "both", "from": 0, "to": 24, "at": "kitchen_table_k1", "chance": "usually"},
     {"days": "weekday", "from": 8.5, "to": 14.5, "at": "OUT_OF_HOUSE", "chance": "sometimes"}],
   "suitcase_mara": [
     {"days": "both", "from": 0, "to": 24, "at": "bedroom_floor_b1", "chance": "usually"},
     {"days": "weekend", "from": 9, "to": 21, "at": "OUT_OF_HOUSE", "chance": "sometimes"}],
   "watering_can_mara": [
     {"days": "both", "from": 0, "to": 24, "at": "sink_k1", "chance": "usually"},
     {"days": "both", "from": 7, "to": 8, "at": "counter_k1", "chance": "usually"}],
   "hairbrush_mara": [
     {"days": "both", "from": 0, "to": 24, "at": "nightstand_b1", "chance": "usually"},
     {"days": "both", "from": 7, "to": 8.5, "at": "bathroom_shelf_ba1", "chance": "usually"}],
   "makeup_kit_mara": [
     {"days": "both", "from": 0, "to": 24, "at": "bathroom_shelf_ba1", "chance": "usually"},
     {"days": "both", "from": 7, "to": 8.5, "at": "nightstand_b1", "chance": "sometimes"}],
   "remote_shared_1": [
     {"days": "both", "from": 0, "to": 24, "at": "coffee_table_l1", "chance": "usually"},
     {"days": "both", "from": 19, "to": 22, "at": "couch_l1", "chance": "sometimes"}],
   "blanket_mara": [
     {"days": "both", "from": 0, "to": 24, "at": "couch_l1", "chance": "usually"}],
   "vacuum_cleaner_shared_1": [
     {"days": "both", "from": 0, "to": 24, "at": "bedroom_floor_b1", "chance": "usually"},
     {"days": "weekend", "from": 13, "to": 15, "at": "couch_l1", "chance": "sometimes"}],
   "class:mug": [
     {"days": "both", "from": 0, "to": 24, "at": "cupboard_k1", "chance": "usually"},
     {"days": "both", "from": 7, "to": 8.5, "at": "kitchen_table_k1", "chance": "usually"},
     {"days": "both", "from": 14.5, "to": 16, "at": "kitchen_table_k1", "chance": "sometimes"},
     {"days": "both", "from": 18, "to": 20, "at": "kitchen_table_k1", "chance": "sometimes"}],
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
   "book_mara": [
     {"days": "both", "from": 0, "to": 24, "at": "bookshelf_l1", "chance": "usually"},
     {"days": "both", "from": 21, "to": 23, "at": "couch_l1", "chance": "sometimes"}],
   "towel_mara": [
     {"days": "both", "from": 0, "to": 24, "at": "towel_rack_ba1", "chance": "usually"}],
   "laundry_basket_mara": [
     {"days": "both", "from": 0, "to": 24, "at": "bedroom_floor_b1", "chance": "usually"}],
   "umbrella_mara": [
     {"days": "both", "from": 0, "to": 24, "at": "entry_floor_e1", "chance": "usually"},
     {"days": "weekday", "from": 8.5, "to": 14.5, "at": "OUT_OF_HOUSE", "chance": "rarely"}]
 }}
```
