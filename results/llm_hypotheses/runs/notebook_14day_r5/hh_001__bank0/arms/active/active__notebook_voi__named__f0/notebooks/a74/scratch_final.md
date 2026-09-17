# a74 — scratch memory, final (retired d09 Wed 06:11 (population cap); final weight 0.0367)

d04-d09 Patterns:
1. Static Anchors (High Confidence): bathroom_shelf_ba1 (hairbrush_mara, makeup_kit_mara, medication_bottle_mara), towel_rack_ba1 (towel_mara), desk_b1 (laptop_mara), sink_k1 (watering_can_mara), cupboard_k1 (mug_shared_1), entry_table_e1 (wallet_mara), bedroom_floor_b1 (laundry_basket_mara, suitcase_mara, vacuum_cleaner_shared_1). Reliable regardless of resident presence or time.
2. Nightstand Volatility: nightstand_b1 is NOT a stable anchor. Contents vary daily (d08: glasses/phone/water; d09: phone only). book_mara location is unpredictable (nightstand, desk, ON_PERSON). Do not assume small items are present when resident is absent.
3. Kitchen Staging (counter_k1): HIGHLY VARIABLE day-to-day. Do not assume 'core items' are present. Observed contents fluctuate significantly (d08: lunchbox/mug/pan/tablet; d09: mug/tablet only). Predict mug_mara and tablet_mara with moderate confidence (0.6-0.7) if resident present >06:00. Assign low probability (<0.3) to lunchbox_mara, pen_mara, pan_shared_1, pot_shared_1, water_bottle_mara, headphones_mara, plate_shared_2, charger_mara, phone_mara unless specific daily evidence suggests otherwise. Avoid overconfidence in specific item presence.
4. Dish Rack (dish_rack_k1): Transient spot for recently used shared items (e.g., mug_shared_1, pot_shared_1). Not a storage location for pan_shared_1, bowl_shared_1, or plates.
5. Exit Items: entry_hook_e1 is a valid anchor for jacket_mara in pre-06:00 windows. Post-06:00, predict ON_PERSON or bedroom/bed_b1. entry_table_e1 holds wallet_mara pre-06:00.
6. Non-Kitchen Drift: bookshelf_l1 is empty in morning windows. bed_b1 is empty when resident is absent. bedroom_floor_b1 holds only bulky items; small personal items do not drift here when resident is away.

Key Contradictions Resolved:
- medication_bottle_mara does NOT drift to counter_k1.
- pot_shared_1 is not a stable cupboard anchor after 06:00.
- entry_hook_e1 is valid for jacket_mara in mornings.
- book_mara is at nightstand_b1, not desk_b1.
- bedroom_floor_b1 holds only bulky storage items, not small personal items.

d09 Wed 06:08: d09 Wed 06:08: counter_k1 holds mug_mara, tablet_mara; resident_1 present. Confirms d09 pattern: lunchbox/pen/pan absent. Score -1.40 (above panel avg -2.22). Weight 0.061, rank 5/5. Kitchen staging remains highly variable; avoid overconfidence in 'core' items beyond mug/tablet.
d09 Wed 06:08: d09 Wed 06:08 sink_k1: lunchbox_mara, plate_shared_1, watering_can_mara. Confirms watering_can_mara anchor. Reveals lunchbox_mara and plate_shared_1 are transient sink items, not counter_k1 anchors. Do not assume lunchbox is at counter_k1; check sink_k1 first. Score -8.33 (above avg).
d09 Wed 06:11: d09 Wed 06:11 counter_k1: mug_mara, tablet_mara; resident_1 present. Confirms moderate confidence (0.85) for these two items. All other predicted items (lunchbox, pen, pan, water_bottle, phone, headphones) absent. Score -0.90, rank 4/5. Weight 0.162. Kitchen staging remains highly variable; avoid overconfidence in 'core' items beyond mug/tablet.
d09 Wed 06:11: d09 Wed 06:11: dish_rack_k1 holds mug_shared_1, pot_shared_1. Confirms transient nature of shared items. My low priors (0.15/0.10) were too low; actual presence was certain. Update: If resident_1 is in kitchen, assign high confidence (0.8+) to mug_shared_1 and pot_shared_1 in dish_rack_k1. Do not treat as empty.
