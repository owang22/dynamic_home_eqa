# p_4c9e — Mara is a freelance artist/creative; irregular hours, home-based, social evenings

Mara is a freelance illustrator or writer. She works from home but her hours are irregular: sometimes she starts at 10:00, sometimes at 14:00, sometimes in the evening. She's home most of the day but may go out for coffee, to a gallery, or to meet clients. The tablet is her work tool and moves between the desk, kitchen table, and couch throughout the day. The lunchbox is used sporadically (she often eats out or skips lunch). The yoga mat is rolled out whenever she needs a break (irregular, 15–30 min sessions). The suitcase is for a client visit or conference (1–2 times a month). The watering can is used when she remembers (irregular). The medication bottle is taken at roughly 8:00 and 20:00 but not rigidly.

What sets this apart: the tablet's location is highly variable within a single day (desk in the morning, kitchen table at lunch, couch in the evening). The lunchbox is often on the counter for days (not used daily). The yoga mat appears on the floor at unpredictable times. The suitcase is out of the house on irregular days (not just weekends). What would refute it: the tablet found in the same location (desk) for 6+ consecutive hours on a weekday, or the lunchbox found at the kitchen table at the same time every day.

```json
{"claims": [
   {"claim": "The tablet is at the desk in the late morning (irregular work start)",
    "target": "tablet_mara", "expect": "desk_b1", "days": "weekday", "from": 10, "to": 14},
   {"claim": "The lunchbox is on the counter for extended periods (not used daily)",
    "target": "lunchbox_mara", "expect": "counter_k1", "days": "both", "from": 0, "to": 24},
   {"claim": "The yoga mat is on the floor at an irregular midday break",
    "target": "yoga_mat_mara", "expect": "couch_l1", "days": "both", "from": 13, "to": 15},
   {"claim": "The suitcase is out of the house for a client visit or conference",
    "target": "suitcase_mara", "expect": "OUT_OF_HOUSE", "days": "both", "from": 0, "to": 24}
],
 "targets": {
   "tablet_mara": [
     {"days": "both", "from": 0, "to": 24, "at": "coffee_table_l1", "chance": "sometimes"},
     {"days": "both", "from": 9, "to": 14, "at": "desk_b1", "chance": "sometimes"},
     {"days": "both", "from": 14, "to": 17, "at": "kitchen_table_k1", "chance": "sometimes"},
     {"days": "both", "from": 19, "to": 23, "at": "couch_l1", "chance": "sometimes"}],
   "lunchbox_mara": [
     {"days": "both", "from": 0, "to": 24, "at": "counter_k1", "chance": "usually"},
     {"days": "both", "from": 12, "to": 14, "at": "kitchen_table_k1", "chance": "rarely"}],
   "yoga_mat_mara": [
     {"days": "both", "from": 0, "to": 24, "at": "couch_l1", "chance": "usually"},
     {"days": "both", "from": 13, "to": 15, "at": "couch_l1", "chance": "sometimes"},
     {"days": "both", "from": 18, "to": 20, "at": "couch_l1", "chance": "sometimes"}],
   "suitcase_mara": [
     {"days": "both", "from": 0, "to": 24, "at": "bedroom_floor_b1", "chance": "usually"},
     {"days": "both", "from": 0, "to": 24, "at": "OUT_OF_HOUSE", "chance": "rarely"}],
   "watering_can_mara": [
     {"days": "both", "from": 0, "to": 24, "at": "sink_k1", "chance": "usually"},
     {"days": "both", "from": 10, "to": 12, "at": "counter_k1", "chance": "rarely"}],
   "hairbrush_mara": [
     {"days": "both", "from": 0, "to": 24, "at": "nightstand_b1", "chance": "usually"},
     {"days": "both", "from": 8, "to": 10, "at": "bathroom_shelf_ba1", "chance": "sometimes"}],
   "makeup_kit_mara": [
     {"days": "both", "from": 0, "to": 24, "at": "bathroom_shelf_ba1", "chance": "usually"},
     {"days": "both", "from": 9, "to": 11, "at": "nightstand_b1", "chance": "sometimes"}],
   "medication_bottle_mara": [
     {"days": "both", "from": 0, "to": 24, "at": "bathroom_shelf_ba1", "chance": "usually"},
     {"days": "both", "from": 7.5, "to": 9, "at": "counter_k1", "chance": "sometimes"},
     {"days": "both", "from": 19.5, "to": 21, "at": "counter_k1", "chance": "sometimes"}],
   "pen_mara": [
     {"days": "both", "from": 0, "to": 24, "at": "kitchen_table_k1", "chance": "sometimes"},
     {"days": "both", "from": 9, "to": 14, "at": "desk_b1", "chance": "sometimes"},
     {"days": "both", "from": 19, "to": 23, "at": "couch_l1", "chance": "sometimes"}],
   "remote_shared_1": [
     {"days": "both", "from": 0, "to": 24, "at": "coffee_table_l1", "chance": "usually"},
     {"days": "both", "from": 19, "to": 23, "at": "couch_l1", "chance": "sometimes"}],
   "blanket_mara": [
     {"days": "both", "from": 0, "to": 24, "at": "couch_l1", "chance": "usually"}],
   "vacuum_cleaner_shared_1": [
     {"days": "both", "from": 0, "to": 24, "at": "bedroom_floor_b1", "chance": "usually"},
     {"days": "weekend", "from": 11, "to": 13, "at": "couch_l1", "chance": "rarely"}],
   "class:mug": [
     {"days": "both", "from": 0, "to": 24, "at": "cupboard_k1", "chance": "usually"},
     {"days": "both", "from": 8, "to": 10, "at": "kitchen_table_k1", "chance": "sometimes"},
     {"days": "both", "from": 14, "to": 16, "at": "desk_b1", "chance": "sometimes"},
     {"days": "both", "from": 18, "to": 20, "at": "kitchen_table_k1", "chance": "sometimes"}],
   "class:plate": [
     {"days": "both", "from": 0, "to": 24, "at": "cupboard_k1", "chance": "usually"},
     {"days": "both", "from": 12, "to": 14, "at": "kitchen_table_k1", "chance": "sometimes"},
     {"days": "both", "from": 18, "to": 21, "at": "kitchen_table_k1", "chance": "sometimes"}],
   "class:bowl": [
     {"days": "both", "from": 0, "to": 24, "at": "cupboard_k1", "chance": "usually"},
     {"days": "both", "from": 8, "to": 10, "at": "kitchen_table_k1", "chance": "sometimes"}],
   "class:pan": [
     {"days": "both", "from": 0, "to": 24, "at": "sink_k1", "chance": "usually"}],
   "class:pot": [
     {"days": "both", "from": 0, "to": 24, "at": "cupboard_k1", "chance": "usually"}],
   "book_mara": [
     {"days": "both", "from": 0, "to": 24, "at": "bookshelf_l1", "chance": "usually"},
     {"days": "both", "from": 9, "to": 14, "at": "desk_b1", "chance": "sometimes"},
     {"days": "both", "from": 21, "to": 23, "at": "couch_l1", "chance": "sometimes"}],
   "towel_mara": [
     {"days": "both", "from": 0, "to": 24, "at": "towel_rack_ba1", "chance": "usually"}],
   "laundry_basket_mara": [
     {"days": "both", "from": 0, "to": 24, "at": "bedroom_floor_b1", "chance": "usually"}],
   "umbrella_mara": [
     {"days": "both", "from": 0, "to": 24, "at": "entry_floor_e1", "chance": "usually"},
     {"days": "both", "from": 10, "to": 16, "at": "OUT_OF_HOUSE", "chance": "rarely"}]
 }}
```
