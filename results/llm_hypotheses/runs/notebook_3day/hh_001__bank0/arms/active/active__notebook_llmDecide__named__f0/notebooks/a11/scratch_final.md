# a11 — scratch memory, final (live at the end; final weight 0.9482)

d02 04:05 entry_hook_e1: backpack_mara, charger_mara, jacket_mara present. No resident. Keys_mara absent.
d02 05:49 nightstand_b1: phone_mara present. No resident.
d02 06:01 counter_k1: bowl_shared_1, medication_bottle_mara, mug_mara present. resident_1 present.
d02 06:01 sink_k1: lunchbox_mara, plate_shared_1, watering_can_mara present. resident_1 present.
d02 06:04 counter_k1: bowl_shared_1, medication_bottle_mara, mug_mara present. resident_1 present.
d02 06:04 sink_k1: lunchbox_mara, plate_shared_1, watering_can_mara present. resident_1 present.
d02 06:05 counter_k1: bowl_shared_1, medication_bottle_mara, mug_mara present. resident_1 present. (Confirmed stability over 4 mins).

Analysis:
1. Resident_1 is consistently in the kitchen (seen at counter and sink 06:01-06:05). Morning routine: Bedroom -> Kitchen.
2. Counter_k1 contents are stable: bowl_shared_1, medication_bottle_mara, mug_mara. This confirms medication_bottle_mara migrates to the kitchen for morning ingestion, deviating from its static bathroom_shelf home base.
3. Sink_k1 is a multi-use staging zone, not just for wet items. It holds lunchbox_mara and plate_shared_1, suggesting prep or dirty item staging.
4. Keys_mara remains unlocated. Not on counter or sink. Given resident_1 is in the kitchen, ON_PERSON is a strong candidate (pocket/bag). If resident_1 leaves, check entry_hook.
5. Water_bottle_mara was predicted at 0.10 but absent from counter. It might be in the fridge (not a look target) or ON_PERSON.
6. Jacket_mara at entry_hook suggests preparation to leave or recent return. If resident_1 is in kitchen, they may be finishing up before heading out.

Next Steps:
- Look at resident_1 to check for keys_mara, wallet_mara, water_bottle_mara.
- If resident_1 is carrying keys, that resolves the keys mystery.
- Monitor entry_hook later for keys if resident leaves.
- Note: The 'Zoned Stasis' model needs adjustment: sink_k1 is a multi-use staging zone, not just for wet items. medication_bottle_mara is not static in the bathroom.
