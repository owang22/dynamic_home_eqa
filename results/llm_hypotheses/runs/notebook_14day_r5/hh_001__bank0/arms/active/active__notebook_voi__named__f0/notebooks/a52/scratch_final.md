# a52 — scratch memory, final (retired d06 Sun 08:45 (population cap); final weight 0.0769)

d04-d05 Morning Patterns (05:00-08:00):
1. Stable Anchors (High Confidence): bathroom_shelf_ba1 (hairbrush_mara, makeup_kit_mara, medication_bottle_mara), nightstand_b1 (phone_mara), desk_b1 (laptop_mara), sink_k1 (watering_can_mara), cupboard_k1 (mug_shared_1). These remain static even when resident_1 is present or absent. No drift observed for these items.
2. Transient/Drifting Items: pot_shared_1 drifts from cupboard_k1 to dish_rack_k1 or counter_k1 after 06:00. headphones_mara and mug_mara drift from cupboard_k1 to counter_k1 or ON_PERSON. lunchbox_mara and water_bottle_mara appear on counter_k1 as staging items. plate_shared_2 is transient on counter_k1, often absent by 07:47.
3. Exit Items: entry_hook_e1 is NOT a stable anchor for backpack_mara, jacket_mara, or charger_mara in the morning. These are removed by resident_1 before 06:50. Predict ON_PERSON or bedroom locations, not entry_hook_e1, after 06:00.
4. Counter_k1 Dynamics: High-traffic staging area. Items appear and disappear rapidly. Not a home for objects. Check here for mug_mara, lunchbox_mara, water_bottle_mara, and pot_shared_1 (or dish_rack_k1) if time > 06:00 and resident_1 is present.
5. Non-Kitchen/Bathroom Drift: bookshelf_l1 is not a stable anchor for book_mara, notebook_mara, or headphones_mara during the morning window. These items likely drift to desk_b1, counter_k1, or ON_PERSON.

Key Contradictions Resolved:
- medication_bottle_mara does NOT drift to counter_k1 (d04 05:23, d05 07:13).
- pot_shared_1 is not a stable cupboard anchor (d04 06:11, d05 07:47).
- entry_hook_e1 is invalid for exit items in the morning (d05 06:50).

d06 Sun 07:50: bookshelf_l1 empty; nobody present. Confirms bookshelf_l1 is not a stable anchor for book_mara, notebook_mara, or headphones_mara during the morning window. These items likely drift to desk_b1, counter_k1, or ON_PERSON. No contradiction to existing beliefs; reinforces transient nature of non-kitchen/bathroom items.
d06 Sun 07:50: d06 07:50 desk_b1: laptop_mara only. Confirms desk_b1 is a stable anchor for laptop_mara, not a drift zone for notebook_mara, pen_mara, or book_mara. Reinforces that non-kitchen items do not cluster at desk_b1 in the morning.
d06 Sun 07:50: d06 Sun 07:50: bed_b1 empty; nobody present. Confirms bed_b1 is not a morning anchor for blanket_mara, yoga_mat_mara, or exit items when resident is absent. Reinforces that bedroom items drift or remain in storage (closet/desk) rather than on the bed during this window.
d06 Sun 08:44: d06 Sun 08:44: bedroom_floor_b1 contains laundry_basket_mara, suitcase_mara, vacuum_cleaner_shared_1. No residents. Confirms bedroom_floor_b1 is a storage zone for bulky items, not a drift zone for small personal items (yoga_mat, blanket) or exit items (jacket, backpack). My forecast of small items here was wrong; they remain in storage or on person.
d06 Sun 08:44: d06 Sun 08:44: bed_b1 empty; nobody present. Confirms bed_b1 is not a morning anchor for blanket_mara, yoga_mat_mara, or exit items when resident is absent. Reinforces that bedroom items drift or remain in storage (closet/desk) rather than on the bed during this window.
d06 Sun 08:45: d06 Sun 08:45: bedroom_floor_b1 holds laundry_basket_mara, suitcase_mara, vacuum_cleaner_shared_1; nobody present. Confirms floor is for bulky storage only. Small items (yoga_mat, blanket) and exit gear (backpack, jacket) are NOT here. My low probs for absences were correct; high probs for bulky items were correct. No belief change.
d06 Sun 08:45: d06 Sun 08:45: entry_hook_e1 contains jacket_mara; nobody present. Contradicts belief that entry_hook_e1 is invalid for exit items in morning (d05 06:50). Jacket remains here even when resident is absent. Suggests entry_hook_e1 is a stable anchor for jacket_mara, not a transient staging area. My low probability (0.05) for jacket_mara was a significant error.
