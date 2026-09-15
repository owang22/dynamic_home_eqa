# p_2e6f — Couple; Mara works from home, partner is the commuter

Two residents: Mara (works from home, 9:00–17:00) and a partner (commutes to office, 8:00–17:30). The partner's personal items aren't catalogued yet. Mara's tablet stays at the desk or coffee table all day. The partner's mugs and plates appear at the kitchen table in the morning (7:30–8:30) and evening (18:00–19:30). The lunchbox is Mara's (she packs a lunch for herself, eaten at the kitchen table at 12:30). The yoga mat is used by Mara on Saturday mornings. The suitcase is for the partner's work trips (a few days, once a month). The watering can is used by Mara every morning at 7:00. The vacuum is used by the partner on Saturday afternoons.

What sets this apart: on a weekday at 10:00, the tablet is in the house (Mara is working from home) but the partner is gone. The partner's items (mugs, plates) are in the cupboard, not at the table. At 7:45, the partner's mug is at the kitchen table. The lunchbox is on the kitchen table at 12:30 (not out of the house). What would refute it: the tablet found OUT_OF_HOUSE on a weekday, or the lunchbox found OUT_OF_HOUSE on a weekday.

```json
{"claims": [
   {"claim": "The tablet is at the desk or coffee table on weekday mornings (Mara works from home)",
    "target": "tablet_mara", "expect": "desk_b1", "days": "weekday", "from": 9, "to": 12},
   {"claim": "The lunchbox is at the kitchen table at lunchtime (Mara eats at home)",
    "target": "lunchbox_mara", "expect": "kitchen_table_k1", "days": "both", "from": 12, "to": 13.5},
   {"claim": "The partner's mug is at the kitchen table during the morning breakfast window",
    "target": "mug_shared_1", "expect": "kitchen_table_k1", "days": "weekday", "from": 7.5, "to": 8.5},
   {"claim": "The yoga mat is on the floor on Saturday morning",
    "target": "yoga_mat_mara", "expect": "couch_l1", "days": "weekend", "from": 9, "to": 10}
],
 "targets": {
   "tablet_mara": [
     {"days": "both", "from": 0, "to": 24, "at": "coffee_table_l1", "chance": "usually"},
     {"days": "weekday", "from": 9, "to": 17, "at": "desk_b1", "chance": "usually"},
     {"days": "both", "from": 19, "to": 22, "at": "couch_l1", "chance": "sometimes"}],
   "lunchbox_mara": [
     {"days": "both", "from": 0, "to": 24, "at": "counter_k1", "chance": "usually"},
     {"days": "both", "from": 12, "to": 13.5, "at": "kitchen_table_k1", "chance": "usually"},
     {"days": "both", "from": 13.5, "to": 15, "at": "sink_k1", "chance": "sometimes"}],
   "class:mug": [
     {"days": "both", "from": 0, "to": 24, "at": "cupboard_k1", "chance": "usually"},
     {"days": "both", "from": 7, "to": 8.5, "at": "kitchen_table_k1", "chance": "usually"},
     {"days": "both", "from": 12, "to": 13.5, "at": "kitchen_table_k1", "chance": "sometimes"},
     {"days": "both", "from": 18, "to": 20, "at": "kitchen_table_k1", "chance": "usually"}],
   "class:plate": [
     {"days": "both", "from": 0, "to": 24, "at": "cupboard_k1", "chance": "usually"},
     {"days": "both", "from": 7, "to": 8.5, "at": "kitchen_table_k1", "chance": "usually"},
     {"days": "both", "from": 12, "to": 13.5, "at": "kitchen_table_k1", "chance": "sometimes"},
     {"days": "both", "from": 18, "to": 21, "at": "kitchen_table_k1", "chance": "usually"}],
   "class:bowl": [
     {"days": "both", "from": 0, "to": 24, "at": "cupboard_k1", "chance": "usually"},
     {"days": "both", "from": 7, "to": 8.5, "at": "kitchen_table_k1", "chance": "usually"},
     {"days": "both", "from": 18, "to": 20, "at": "kitchen_table_k1", "chance": "sometimes"}],
   "class:pan": [
     {"days": "both", "from": 0, "to": 24, "at": "sink_k1", "chance": "usually"},
     {"days": "both", "from": 17.5, "to": 19.5, "at": "counter_k1", "chance": "sometimes"}],
   "class:pot": [
     {"days": "both", "from": 0, "to": 24, "at": "cupboard_k1", "chance": "usually"},
     {"days": "both", "from": 17.5, "to": 19.5, "at": "counter_k1", "chance": "sometimes"}],
   "yoga_mat_mara": [
     {"days": "both", "from": 0, "to": 24, "at": "couch_l1", "chance": "usually"},
     {"days": "weekend", "from": 9, "to": 10, "at": "couch_l1", "chance": "usually"}],
   "suitcase_mara": [
     {"days": "both", "from": 0, "to": 24, "at": "bedroom_floor_b1", "chance": "usually"},
     {"days": "both", "from": 0, "to": 24, "at": "OUT_OF_HOUSE", "chance": "rarely"}],
   "watering_can_mara": [
     {"days": "both", "from": 0, "to": 24, "at": "sink_k1", "chance": "usually"},
     {"days": "both", "from": 7, "to": 8, "at": "counter_k1", "chance": "usually"}],
   "hairbrush_mara": [
     {"days": "both", "from": 0, "to": 24, "at": "nightstand_b1", "chance": "usually"},
     {"days": "both", "from": 7, "to": 8.5, "at": "bathroom_shelf_ba1", "chance": "usually"}],
   "makeup_kit_mara": [
     {"days": "both", "from": 0, "to": 24, "at": "bathroom_shelf_ba1", "chance": "usually"},
     {"days": "both", "from": 7, "to": 8.5, "at": "nightstand_b1", "chance": "sometimes"}],
   "medication_bottle_mara": [
     {"days": "both", "from": 0, "to": 24, "at": "bathroom_shelf_ba1", "chance": "almost_always"},
     {"days": "both", "from": 7.5, "to": 8.5, "at": "counter_k1", "chance": "sometimes"}],
   "pen_mara": [
     {"days": "both", "from": 0, "to": 24, "at": "kitchen_table_k1", "chance": "usually"},
     {"days": "weekday", "from": 9, "to": 17, "at": "desk_b1", "chance": "sometimes"}],
   "remote_shared_1": [
     {"days": "both", "from": 0, "to": 24, "at": "coffee_table_l1", "chance": "usually"},
     {"days": "both", "from": 19, "to": 22, "at": "couch_l1", "chance": "sometimes"}],
   "blanket_mara": [
     {"days": "both", "from": 0, "to": 24, "at": "couch_l1", "chance": "usually"}],
   "vacuum_cleaner_shared_1": [
     {"days": "both", "from": 0, "to": 24, "at": "bedroom_floor_b1", "chance": "usually"},
     {"days": "weekend", "from": 14, "to": 16, "at": "couch_l1", "chance": "usually"}],
   "book_mara": [
     {"days": "both", "from": 0, "to": 24, "at": "bookshelf_l1", "chance": "usually"},
     {"days": "both", "from": 21, "to": 23, "at": "couch_l1", "chance": "sometimes"}],
   "towel_mara": [
     {"days": "both", "from": 0, "to": 24, "at": "towel_rack_ba1", "chance": "usually"}],
   "laundry_basket_mara": [
     {"days": "both", "from": 0, "to": 24, "at": "bedroom_floor_b1", "chance": "usually"}],
   "umbrella_mara": [
     {"days": "both", "from": 0, "to": 24, "at": "entry_floor_e1", "chance": "usually"}]
 }}
```
