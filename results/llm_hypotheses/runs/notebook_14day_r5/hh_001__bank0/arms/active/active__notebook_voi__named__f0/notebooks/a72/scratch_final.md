# a72 — scratch memory, final (retired d09 Wed 05:55 (population cap); final weight 0.0405)

d04-d08 Patterns:
1. Stable Anchors: bathroom_shelf_ba1 (hairbrush_mara, makeup_kit_mara, medication_bottle_mara), towel_rack_ba1 (towel_mara), nightstand_b1 (phone_mara, book_mara), desk_b1 (laptop_mara), sink_k1 (watering_can_mara), cupboard_k1 (mug_shared_1). Reliable regardless of resident presence or time. book_mara is a nightstand anchor, not desk/counter.
2. Transient/Drifting: pot_shared_1 moves from cupboard_k1 to dish_rack_k1/counter_k1 after 06:00. headphones_mara, mug_mara, lunchbox_mara, water_bottle_mara, plate_shared_2 appear on counter_k1 as staging items. counter_k1 is a staging area, not storage.
3. Exit Items: entry_hook_e1 is a valid anchor for jacket_mara in morning windows (d06 08:45, d07 05:35). Predict jacket_mara at entry_hook_e1 or ON_PERSON. Backpack/charger status less clear but hook is viable for jacket.
4. Bedroom Dynamics: bed_b1 is empty when resident is absent; not an anchor for blanket_mara, yoga_mat_mara, or exit items. bedroom_floor_b1 is static storage for bulky items (laundry_basket_mara, suitcase_mara, vacuum_cleaner_shared_1) only; small personal items do not drift here when resident is away.
5. Non-Kitchen Drift: bookshelf_l1 is empty in morning windows; not a stable anchor for book_mara, notebook_mara, or headphones_mara. These items drift to desk_b1, counter_k1, or ON_PERSON, or remain at nightstand_b1 (book_mara).

Key Contradictions Resolved:
- medication_bottle_mara does NOT drift to counter_k1.
- pot_shared_1 is not a stable cupboard anchor after 06:00.
- entry_hook_e1 is valid for jacket_mara in mornings.
- book_mara is at nightstand_b1, not desk_b1.
- bedroom_floor_b1 holds only bulky storage items, not small personal items.

d07 Mon 06:00/06:04: counter_k1 staging confirmed: lunchbox_mara, mug_mara, pen_mara, tablet_mara. Absence of water_bottle/headphones/plate_shared_2/pot_shared_1/charger/phone confirms they are not reliably staged before 06:30. dish_rack_k1 holds only mug_shared_1 (transient), not storage for other shared items.

d08 Tue 05:45: bathroom_shelf_ba1 contains hairbrush_mara, makeup_kit_mara, medication_bottle_mara; resident_1 present. Confirms static anchor stability across days.

d08 Tue 05:54: d08 Tue 05:54: bathroom_shelf_ba1 contains hairbrush_mara, makeup_kit_mara, medication_bottle_mara; resident_1 present. Confirms static anchor stability across days (d07-d08). No drift observed. Reinforces high-confidence belief in these locations as reliable regardless of time or resident activity.
d08 Tue 05:54: d08 Tue 05:54: Look at resident_1 in bathroom revealed nothing carried. Confirms pre-06:00 resident is not carrying exit items (keys, wallet, jacket, etc.) or small personal items. Reinforces belief that static anchors (nightstand_b1, entry_table_e1, entry_hook_e1) hold these items before resident departs. No drift to ON_PERSON observed at this hour.
d08 Tue 05:54: d08 Tue 05:54: nightstand_b1 contains glasses_mara, phone_mara, water_bottle_mara. book_mara ABSENT. Contradicts static anchor belief. water_bottle_mara drifts to nightstand pre-06:00. book_mara location unstable.
d08 Tue 05:58: d08 Tue 05:58: counter_k1 holds lunchbox_mara, mug_mara, pan_shared_1, tablet_mara. pen_mara absent. pan_shared_1 drifts to counter pre-06:00, contradicting 'low probability <06:30' for shared cookware. resident_1 present.
d08 Tue 05:58: d08 Tue 05:58: dish_rack_k1 holds mug_shared_1, pot_shared_1. resident_1 present. Confirms pot_shared_1 drifts to dish_rack pre-06:00, contradicting 'low probability <06:30' for shared cookware. mug_shared_1 transient presence confirmed.
d08 Tue 06:00: d08 Tue 06:00: counter_k1 holds lunchbox_mara, mug_mara, pan_shared_1, tablet_mara. pen_mara absent. Confirms pan_shared_1 drifts to counter pre-06:00, contradicting 'low probability <06:30' for shared cookware. resident_1 present. Score -2.64 due to overconfidence in pen_mara and underconfidence in pan_shared_1.
d08 Tue 06:09: d08 Tue 06:09: dish_rack_k1 holds mug_shared_1, pot_shared_1. resident_1 present. Confirms shared cookware drifts to dish_rack pre-06:30. Score -1.14 due to overconfidence in pot_shared_1 (0.75) and underconfidence in mug_shared_1 (0.85). Adjust future probabilities: mug_shared_1 0.95, pot_shared_1 0.60.
