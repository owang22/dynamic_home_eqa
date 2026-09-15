# p_a3e7 — Mara works from home; the couch is her evening sanctuary

One adult, Mara, lives alone. She works from the kitchen table or the desk in the bedroom, roughly 9:00–17:00 on weekdays, and never leaves the house during working hours. In the evenings she stretches on the yoga mat unrolled on the living-room floor, then curls up on the couch with the tablet and remote. The suitcase stays on the bedroom floor indefinitely (a packed bag she's been meaning to use for a trip that keeps getting postponed). The watering can lives in the sink overnight and gets carried to the plants on the counter or windowsill each morning. The lunchbox is packed the night before and sits on the counter until she eats it around 12:30, after which it goes to the sink to be washed.

What sets this hypothesis apart: the tablet and remote are on the coffee table at 15:00 on weekdays (she's home), and the yoga mat is on the floor (not the couch) between 18:00 and 20:00 on weekdays. The lunchbox is OUT_OF_HOUSE never. What would refute it: the tablet or remote found OUT_OF_HOUSE on a weekday afternoon, or the yoga mat still on the couch at 19:00 on a weekday.

```json
{"claims": [
   {"claim": "Mara is home at the coffee table with the tablet on weekday afternoons",
    "target": "tablet_mara", "expect": "coffee_table_l1", "days": "weekday", "from": 13, "to": 17},
   {"claim": "The yoga mat is unrolled on the living room floor during evening stretch time",
    "target": "yoga_mat_mara", "expect": "couch_l1", "days": "weekday", "from": 18, "to": 20},
   {"claim": "The lunchbox never leaves the house",
    "target": "lunchbox_mara", "expect": "counter_k1", "days": "both", "from": 0, "to": 24},
   {"claim": "The remote is on the coffee table in the evening while she watches TV",
    "target": "remote_shared_1", "expect": "coffee_table_l1", "days": "both", "from": 19, "to": 22}
],
 "targets": {
   "tablet_mara": [
     {"days": "both", "from": 0, "to": 24, "at": "coffee_table_l1", "chance": "usually"},
     {"days": "weekday", "from": 9, "to": 12, "at": "desk_b1", "chance": "sometimes"}],
   "remote_shared_1": [
     {"days": "both", "from": 0, "to": 24, "at": "coffee_table_l1", "chance": "usually"}],
   "yoga_mat_mara": [
     {"days": "both", "from": 0, "to": 24, "at": "couch_l1", "chance": "usually"},
     {"days": "weekday", "from": 18, "to": 20, "at": "couch_l1", "chance": "usually"}],
   "lunchbox_mara": [
     {"days": "both", "from": 0, "to": 24, "at": "counter_k1", "chance": "usually"},
     {"days": "both", "from": 12, "to": 14, "at": "sink_k1", "chance": "sometimes"}],
   "watering_can_mara": [
     {"days": "both", "from": 0, "to": 24, "at": "sink_k1", "chance": "usually"},
     {"days": "both", "from": 7, "to": 9, "at": "counter_k1", "chance": "sometimes"}],
   "suitcase_mara": [
     {"days": "both", "from": 0, "to": 24, "at": "bedroom_floor_b1", "chance": "almost_always"}],
   "blanket_mara": [
     {"days": "both", "from": 0, "to": 24, "at": "couch_l1", "chance": "usually"},
     {"days": "both", "from": 20, "to": 23, "at": "couch_l1", "chance": "almost_always"}],
   "hairbrush_mara": [
     {"days": "both", "from": 0, "to": 24, "at": "nightstand_b1", "chance": "usually"},
     {"days": "both", "from": 6, "to": 8, "at": "bathroom_shelf_ba1", "chance": "sometimes"}],
   "makeup_kit_mara": [
     {"days": "both", "from": 0, "to": 24, "at": "bathroom_shelf_ba1", "chance": "usually"},
     {"days": "both", "from": 6.5, "to": 8, "at": "nightstand_b1", "chance": "sometimes"}],
   "medication_bottle_mara": [
     {"days": "both", "from": 0, "to": 24, "at": "bathroom_shelf_ba1", "chance": "almost_always"}],
   "pen_mara": [
     {"days": "both", "from": 0, "to": 24, "at": "kitchen_table_k1", "chance": "usually"},
     {"days": "weekday", "from": 9, "to": 17, "at": "desk_b1", "chance": "sometimes"}],
   "umbrella_mara": [
     {"days": "both", "from": 0, "to": 24, "at": "entry_floor_e1", "chance": "usually"}],
   "vacuum_cleaner_shared_1": [
     {"days": "both", "from": 0, "to": 24, "at": "bedroom_floor_b1", "chance": "usually"},
     {"days": "weekend", "from": 10, "to": 12, "at": "couch_l1", "chance": "sometimes"}],
   "class:mug": [
     {"days": "both", "from": 0, "to": 24, "at": "cupboard_k1", "chance": "usually"},
     {"days": "both", "from": 7, "to": 9, "at": "counter_k1", "chance": "usually"},
     {"days": "both", "from": 12, "to": 14, "at": "kitchen_table_k1", "chance": "sometimes"}],
   "class:plate": [
     {"days": "both", "from": 0, "to": 24, "at": "cupboard_k1", "chance": "usually"},
     {"days": "both", "from": 12, "to": 14, "at": "kitchen_table_k1", "chance": "sometimes"},
     {"days": "both", "from": 18, "to": 21, "at": "counter_k1", "chance": "sometimes"}],
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
     {"days": "both", "from": 21, "to": 23, "at": "couch_l1", "chance": "sometimes"}],
   "towel_mara": [
     {"days": "both", "from": 0, "to": 24, "at": "towel_rack_ba1", "chance": "usually"}],
   "laundry_basket_mara": [
     {"days": "both", "from": 0, "to": 24, "at": "bedroom_floor_b1", "chance": "usually"}]
 }}
```
