# p_1a4d — Mara travels frequently; the suitcase is never truly "stored"

Mara is a frequent traveler (consultant, sales, or family obligations). The suitcase is packed and unpacked roughly every 2–3 weeks. When she's away (1–4 days at a time), most of her personal items (tablet, laptop-equivalent, medication, makeup, hairbrush) go with her. The house is empty for those days. The yoga mat stays on the couch (she doesn't pack it). The watering can is used by a neighbor or automated (stays in sink). The lunchbox is only used when she's home. The remote and blanket stay in the living room.

What sets this apart: the suitcase is OUT_OF_HOUSE on many days (not just weekends). When the suitcase is out, the tablet, medication, and hairbrush are also out. The house can be empty for 2–3 days at a stretch. What would refute it: the suitcase found on the bedroom floor for 5+ consecutive days, or the tablet found in the house while the suitcase is out.

```json
{"claims": [
   {"claim": "The suitcase is out of the house on a regular cycle (not just weekends)",
    "target": "suitcase_mara", "expect": "OUT_OF_HOUSE", "days": "both", "from": 0, "to": 24},
   {"claim": "The tablet travels with Mara when she's away",
    "target": "tablet_mara", "expect": "OUT_OF_HOUSE", "days": "both", "from": 0, "to": 24},
   {"claim": "The medication bottle travels with Mara",
    "target": "medication_bottle_mara", "expect": "OUT_OF_HOUSE", "days": "both", "from": 0, "to": 24},
   {"claim": "The yoga mat stays on the couch even when Mara is traveling",
    "target": "yoga_mat_mara", "expect": "couch_l1", "days": "both", "from": 0, "to": 24}
],
 "targets": {
   "suitcase_mara": [
     {"days": "both", "from": 0, "to": 24, "at": "bedroom_floor_b1", "chance": "sometimes"},
     {"days": "both", "from": 0, "to": 24, "at": "OUT_OF_HOUSE", "chance": "sometimes"}],
   "tablet_mara": [
     {"days": "both", "from": 0, "to": 24, "at": "coffee_table_l1", "chance": "sometimes"},
     {"days": "both", "from": 0, "to": 24, "at": "OUT_OF_HOUSE", "chance": "sometimes"}],
   "medication_bottle_mara": [
     {"days": "both", "from": 0, "to": 24, "at": "bathroom_shelf_ba1", "chance": "sometimes"},
     {"days": "both", "from": 0, "to": 24, "at": "OUT_OF_HOUSE", "chance": "sometimes"}],
   "hairbrush_mara": [
     {"days": "both", "from": 0, "to": 24, "at": "nightstand_b1", "chance": "sometimes"},
     {"days": "both", "from": 0, "to": 24, "at": "OUT_OF_HOUSE", "chance": "sometimes"}],
   "makeup_kit_mara": [
     {"days": "both", "from": 0, "to": 24, "at": "bathroom_shelf_ba1", "chance": "sometimes"},
     {"days": "both", "from": 0, "to": 24, "at": "OUT_OF_HOUSE", "chance": "sometimes"}],
   "lunchbox_mara": [
     {"days": "both", "from": 0, "to": 24, "at": "counter_k1", "chance": "usually"}],
   "yoga_mat_mara": [
     {"days": "both", "from": 0, "to": 24, "at": "couch_l1", "chance": "almost_always"}],
   "watering_can_mara": [
     {"days": "both", "from": 0, "to": 24, "at": "sink_k1", "chance": "usually"}],
   "pen_mara": [
     {"days": "both", "from": 0, "to": 24, "at": "kitchen_table_k1", "chance": "sometimes"},
     {"days": "both", "from": 0, "to": 24, "at": "OUT_OF_HOUSE", "chance": "sometimes"}],
   "remote_shared_1": [
     {"days": "both", "from": 0, "to": 24, "at": "coffee_table_l1", "chance": "usually"}],
   "blanket_mara": [
     {"days": "both", "from": 0, "to": 24, "at": "couch_l1", "chance": "usually"}],
   "vacuum_cleaner_shared_1": [
     {"days": "both", "from": 0, "to": 24, "at": "bedroom_floor_b1", "chance": "usually"}],
   "class:mug": [
     {"days": "both", "from": 0, "to": 24, "at": "cupboard_k1", "chance": "usually"}],
   "class:plate": [
     {"days": "both", "from": 0, "to": 24, "at": "cupboard_k1", "chance": "usually"}],
   "class:bowl": [
     {"days": "both", "from": 0, "to": 24, "at": "cupboard_k1", "chance": "usually"}],
   "class:pan": [
     {"days": "both", "from": 0, "to": 24, "at": "sink_k1", "chance": "usually"}],
   "class:pot": [
     {"days": "both", "from": 0, "to": 24, "at": "cupboard_k1", "chance": "usually"}],
   "book_mara": [
     {"days": "both", "from": 0, "to": 24, "at": "bookshelf_l1", "chance": "usually"}],
   "towel_mara": [
     {"days": "both", "from": 0, "to": 24, "at": "towel_rack_ba1", "chance": "usually"}],
   "laundry_basket_mara": [
     {"days": "both", "from": 0, "to": 24, "at": "bedroom_floor_b1", "chance": "usually"}],
   "umbrella_mara": [
     {"days": "both", "from": 0, "to": 24, "at": "entry_floor_e1", "chance": "usually"},
     {"days": "both", "from": 0, "to": 24, "at": "OUT_OF_HOUSE", "chance": "rarely"}]
 }}
```
