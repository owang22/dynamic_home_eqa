# p_c4d1 — Two-person household; both partners commute, different hours

Mara and a partner (whose personal items the robot hasn't catalogued yet) both work outside the home. Mara leaves at 8:00 and returns at 17:00. The partner leaves at 9:30 and returns at 18:30. Between 8:00 and 9:30 only Mara is gone; between 9:30 and 17:00 both are gone; between 17:00 and 18:30 only the partner is gone. Shared items (mugs, plates, bowls, pans, pots) cycle through the kitchen in the morning and evening. The tablet and lunchbox leave with Mara. The partner's items (not yet seen) would be separate. The yoga mat is used by Mara on Saturday mornings. The suitcase is for a joint weekend trip.

What sets this apart: on a weekday at 10:00, the house is completely empty of residents (both partners out), so the tablet AND any partner items are OUT_OF_HOUSE. At 8:30, only Mara's items are gone. The shared mugs appear at the kitchen table in two waves (7:30–8:30 for Mara, 8:30–9:30 for partner). What would refute it: the tablet found in the house at 10:00 on a weekday, or only one "wave" of morning mug activity.

```json
{"claims": [
   {"claim": "The tablet is out of the house by 9:00 on weekdays",
    "target": "tablet_mara", "expect": "OUT_OF_HOUSE", "days": "weekday", "from": 9, "to": 17},
   {"claim": "The lunchbox is out of the house by 8:30 on weekdays",
    "target": "lunchbox_mara", "expect": "OUT_OF_HOUSE", "days": "weekday", "from": 8.5, "to": 17},
   {"claim": "Shared mugs are at the kitchen table during the partner's breakfast window",
    "target": "mug_shared_1", "expect": "kitchen_table_k1", "days": "weekday", "from": 8.5, "to": 9.5},
   {"claim": "The yoga mat is used on Saturday mornings",
    "target": "yoga_mat_mara", "expect": "couch_l1", "days": "weekend", "from": 8, "to": 10}
],
 "targets": {
   "tablet_mara": [
     {"days": "both", "from": 0, "to": 24, "at": "coffee_table_l1", "chance": "usually"},
     {"days": "weekday", "from": 8, "to": 17, "at": "OUT_OF_HOUSE", "chance": "almost_always"}],
   "lunchbox_mara": [
     {"days": "both", "from": 0, "to": 24, "at": "counter_k1", "chance": "usually"},
     {"days": "weekday", "from": 8, "to": 17, "at": "OUT_OF_HOUSE", "chance": "almost_always"}],
   "pen_mara": [
     {"days": "both", "from": 0, "to": 24, "at": "kitchen_table_k1", "chance": "usually"},
     {"days": "weekday", "from": 8, "to": 17, "at": "OUT_OF_HOUSE", "chance": "almost_always"}],
   "class:mug": [
     {"days": "both", "from": 0, "to": 24, "at": "cupboard_k1", "chance": "usually"},
     {"days": "both", "from": 7, "to": 8, "at": "kitchen_table_k1", "chance": "usually"},
     {"days": "both", "from": 8, "to": 9.5, "at": "kitchen_table_k1", "chance": "usually"},
     {"days": "both", "from": 18, "to": 20, "at": "kitchen_table_k1", "chance": "sometimes"}],
   "class:plate": [
     {"days": "both", "from": 0, "to": 24, "at": "cupboard_k1", "chance": "usually"},
     {"days": "both", "from": 7, "to": 9.5, "at": "kitchen_table_k1", "chance": "usually"},
     {"days": "both", "from": 18, "to": 21, "at": "kitchen_table_k1", "chance": "sometimes"}],
   "class:bowl": [
     {"days": "both", "from": 0, "to": 24, "at": "cupboard_k1", "chance": "usually"},
     {"days": "both", "from": 7, "to": 9.5, "at": "kitchen_table_k1", "chance": "usually"}],
   "class:pan": [
     {"days": "both", "from": 0, "to": 24, "at": "sink_k1", "chance": "usually"},
     {"days": "both", "from": 17.5, "to": 19.5, "at": "counter_k1", "chance": "sometimes"}],
   "class:pot": [
     {"days": "both", "from": 0, "to": 24, "at": "cupboard_k1", "chance": "usually"},
     {"days": "both", "from": 17.5, "to": 19.5, "at": "counter_k1", "chance": "sometimes"}],
   "yoga_mat_mara": [
     {"days": "both", "from": 0, "to": 24, "at": "couch_l1", "chance": "usually"},
     {"days": "weekend", "from": 8, "to": 10, "at": "couch_l1", "chance": "usually"}],
   "suitcase_mara": [
     {"days": "both", "from": 0, "to": 24, "at": "bedroom_floor_b1", "chance": "usually"},
     {"days": "weekend", "from": 7, "to": 22, "at": "OUT_OF_HOUSE", "chance": "sometimes"}],
   "hairbrush_mara": [
     {"days": "both", "from": 0, "to": 24, "at": "nightstand_b1", "chance": "usually"},
     {"days": "both", "from": 6, "to": 7.5, "at": "bathroom_shelf_ba1", "chance": "sometimes"}],
   "makeup_kit_mara": [
     {"days": "both", "from": 0, "to": 24, "at": "bathroom_shelf_ba1", "chance": "usually"},
     {"days": "both", "from": 6.5, "to": 8, "at": "nightstand_b1", "chance": "sometimes"}],
   "medication_bottle_mara": [
     {"days": "both", "from": 0, "to": 24, "at": "bathroom_shelf_ba1", "chance": "almost_always"}],
   "remote_shared_1": [
     {"days": "both", "from": 0, "to": 24, "at": "coffee_table_l1", "chance": "usually"},
     {"days": "both", "from": 19, "to": 22, "at": "couch_l1", "chance": "sometimes"}],
   "blanket_mara": [
     {"days": "both", "from": 0, "to": 24, "at": "couch_l1", "chance": "usually"}],
   "watering_can_mara": [
     {"days": "both", "from": 0, "to": 24, "at": "sink_k1", "chance": "usually"},
     {"days": "weekend", "from": 10, "to": 12, "at": "counter_k1", "chance": "sometimes"}],
   "vacuum_cleaner_shared_1": [
     {"days": "both", "from": 0, "to": 24, "at": "bedroom_floor_b1", "chance": "usually"},
     {"days": "weekend", "from": 14, "to": 16, "at": "couch_l1", "chance": "sometimes"}],
   "book_mara": [
     {"days": "both", "from": 0, "to": 24, "at": "bookshelf_l1", "chance": "usually"},
     {"days": "both", "from": 21, "to": 23, "at": "couch_l1", "chance": "sometimes"}],
   "towel_mara": [
     {"days": "both", "from": 0, "to": 24, "at": "towel_rack_ba1", "chance": "usually"}],
   "laundry_basket_mara": [
     {"days": "both", "from": 0, "to": 24, "at": "bedroom_floor_b1", "chance": "usually"}],
   "umbrella_mara": [
     {"days": "both", "from": 0, "to": 24, "at": "entry_floor_e1", "chance": "usually"},
     {"days": "weekday", "from": 8, "to": 17, "at": "OUT_OF_HOUSE", "chance": "rarely"}]
 }}
```
