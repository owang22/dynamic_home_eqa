# p_5d0f — Mara works weekends only (retail/food service); weekdays are free

Mara works at a restaurant or shop that's open only on weekends (or she's a weekend contractor). On weekdays she's home from 7:00 to 23:00. On weekends she leaves at 8:00 and returns at 20:00 (or later on Saturday). The tablet is used at home on weekdays (browsing, email, entertainment). The lunchbox is for weekend work (packed Friday night, used Saturday/Sunday). The yoga mat is used on weekday mornings (8:00–8:30) as a daily ritual. The watering can is used every weekday morning at 7:30. The suitcase is for a mid-week day trip (rare, 1–2x per month). The medication bottle is taken at 8:00 and 20:00 on weekdays, and at 8:00 on weekends (before leaving).

What sets this apart: on a weekday at 14:00, the tablet is in the house, the lunchbox is on the counter (not used), and the yoga mat is on the couch (already put away from morning use). On a Saturday at 12:00, the lunchbox is OUT_OF_HOUSE and the tablet may be at home or with her. The yoga mat is on the floor at 8:15 on a Tuesday. What would refute it: the lunchbox found OUT_OF_HOUSE on a Wednesday, or the yoga mat on the couch at 8:15 on a Tuesday.

```json
{"claims": [
   {"claim": "The lunchbox is on the counter on a Wednesday (not used on weekdays)",
    "target": "lunchbox_mara", "expect": "counter_k1", "days": "weekday", "from": 10, "to": 18},
   {"claim": "The yoga mat is on the floor during the weekday morning routine",
    "target": "yoga_mat_mara", "expect": "couch_l1", "days": "weekday", "from": 8, "to": 8.5},
   {"claim": "The tablet is at the coffee table on a weekday afternoon",
    "target": "tablet_mara", "expect": "coffee_table_l1", "days": "weekday", "from": 13, "to": 17},
   {"claim": "The lunchbox is out of the house on a Saturday (weekend work)",
    "target": "lunchbox_mara", "expect": "OUT_OF_HOUSE", "days": "weekend", "from": 8, "to": 20}
],
 "targets": {
   "tablet_mara": [
     {"days": "both", "from": 0, "to": 24, "at": "coffee_table_l1", "chance": "usually"},
     {"days": "both", "from": 7, "to": 10, "at": "kitchen_table_k1", "chance": "sometimes"},
     {"days": "both", "from": 19, "to": 22, "at": "couch_l1", "chance": "sometimes"}],
   "lunchbox_mara": [
     {"days": "both", "from": 0, "to": 24, "at": "counter_k1", "chance": "usually"},
     {"days": "weekend", "from": 7.5, "to": 20.5, "at": "OUT_OF_HOUSE", "chance": "usually"}],
   "yoga_mat_mara": [
     {"days": "both", "from": 0, "to": 24, "at": "couch_l1", "chance": "usually"},
     {"days": "weekday", "from": 8, "to": 8.5, "at": "couch_l1", "chance": "usually"},
     {"days": "weekend", "from": 21, "to": 22, "at": "couch_l1", "chance": "sometimes"}],
   "watering_can_mara": [
     {"days": "both", "from": 0, "to": 24, "at": "sink_k1", "chance": "usually"},
     {"days": "weekday", "from": 7, "to": 8, "at": "counter_k1", "chance": "usually"}],
   "suitcase_mara": [
     {"days": "both", "from": 0, "to": 24, "at": "bedroom_floor_b1", "chance": "usually"},
     {"days": "both", "from": 0, "to": 24, "at": "OUT_OF_HOUSE", "chance": "rarely"}],
   "hairbrush_mara": [
     {"days": "both", "from": 0, "to": 24, "at": "nightstand_b1", "chance": "usually"},
     {"days": "both", "from": 7, "to": 8.5, "at": "bathroom_shelf_ba1", "chance": "usually"}],
   "makeup_kit_mara": [
     {"days": "both", "from": 0, "to": 24, "at": "bathroom_shelf_ba1", "chance": "usually"},
     {"days": "weekend", "from": 7, "to": 8.5, "at": "nightstand_b1", "chance": "sometimes"}],
   "medication_bottle_mara": [
     {"days": "both", "from": 0, "to": 24, "at": "bathroom_shelf_ba1", "chance": "usually"},
     {"days": "both", "from": 7.5, "to": 8.5, "at": "counter_k1", "chance": "usually"},
     {"days": "weekday", "from": 19.5, "to": 20.5, "at": "counter_k1", "chance": "usually"}],
   "pen_mara": [
     {"days": "both", "from": 0, "to": 24, "at": "kitchen_table_k1", "chance": "usually"},
     {"days": "weekend", "from": 8, "to": 20, "at": "OUT_OF_HOUSE", "chance": "sometimes"}],
   "remote_shared_1": [
     {"days": "both", "from": 0, "to": 24, "at": "coffee_table_l1", "chance": "usually"},
     {"days": "both", "from": 19, "to": 22, "at": "couch_l1", "chance": "sometimes"}],
   "blanket_mara": [
     {"days": "both", "from": 0, "to": 24, "at": "couch_l1", "chance": "usually"}],
   "vacuum_cleaner_shared_1": [
     {"days": "both", "from": 0, "to": 24, "at": "bedroom_floor_b1", "chance": "usually"},
     {"days": "weekday", "from": 14, "to": 16, "at": "couch_l1", "chance": "sometimes"}],
   "class:mug": [
     {"days": "both", "from": 0, "to": 24, "at": "cupboard_k1", "chance": "usually"},
     {"days": "both", "from": 7, "to": 9, "at": "kitchen_table_k1", "chance": "usually"},
     {"days": "both", "from": 12, "to": 14, "at": "kitchen_table_k1", "chance": "sometimes"},
     {"days": "both", "from": 18, "to": 21, "at": "kitchen_table_k1", "chance": "usually"}],
   "class:plate": [
     {"days": "both", "from": 0, "to": 24, "at": "cupboard_k1", "chance": "usually"},
     {"days": "both", "from": 7, "to": 9, "at": "kitchen_table_k1", "chance": "usually"},
     {"days": "both", "from": 12, "to": 14, "at": "kitchen_table_k1", "chance": "sometimes"},
     {"days": "both", "from": 18, "to": 21, "at": "kitchen_table_k1", "chance": "usually"}],
   "class:bowl": [
     {"days": "both", "from": 0, "to": 24, "at": "cupboard_k1", "chance": "usually"},
     {"days": "both", "from": 7, "to": 9, "at": "kitchen_table_k1", "chance": "usually"}],
   "class:pan": [
     {"days": "both", "from": 0, "to": 24, "at": "sink_k1", "chance": "usually"},
     {"days": "both", "from": 17, "to": 19, "at": "counter_k1", "chance": "sometimes"}],
   "class:pot": [
     {"days": "both", "from": 0, "to": 24, "at": "cupboard_k1", "chance": "usually"}],
   "book_mara": [
     {"days": "both", "from": 0, "to": 24, "at": "bookshelf_l1", "chance": "usually"},
     {"days": "both", "from": 14, "to": 17, "at": "couch_l1", "chance": "sometimes"},
     {"days": "both", "from": 21, "to": 23, "at": "couch_l1", "chance": "sometimes"}],
   "towel_mara": [
     {"days": "both", "from": 0, "to": 24, "at": "towel_rack_ba1", "chance": "usually"}],
   "laundry_basket_mara": [
     {"days": "both", "from": 0, "to": 24, "at": "bedroom_floor_b1", "chance": "usually"}],
   "umbrella_mara": [
     {"days": "both", "from": 0, "to": 24, "at": "entry_floor_e1", "chance": "usually"},
     {"days": "weekend", "from": 8, "to": 20, "at": "OUT_OF_HOUSE", "chance": "rarely"}]
 }}
```
