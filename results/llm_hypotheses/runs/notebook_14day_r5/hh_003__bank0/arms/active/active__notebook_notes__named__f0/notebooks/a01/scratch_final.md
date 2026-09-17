# a01 — scratch memory, final (live at the end; final weight 0.9653)

AM (06:00-08:00) kitchen migration is dominant for shared/volatile items, but personal items cluster on counter_k1 or sink_k1, not bedrooms. Counter_k1 holds a static cluster (chargers, mugs, phones, water bottles, lunchboxes) that persists from pre-dawn through midday. Sink_k1 holds shared cookware (bowl, pan, pot, plate); plate_shared_1 is volatile, often moving from cupboard to sink. Cupboard_k1 is rarely used for AM storage.

Resident presence in kitchen is low pre-dawn (05:00-07:00), often 'nobody present,' but items remain static. Marisol is inconsistent: sometimes in bedroom_1 (holding phone, glasses on nightstand), sometimes in kitchen. Nico is volatile; his items migrate to kitchen surfaces, but he is often in bedroom_3 pre-dawn. Talia’s items show strong kitchen affinity.

Key Adjustments:
1. Do not assume personal items are in bedrooms or on persons during AM; they are on kitchen surfaces.
2. Nico’s daily carry items (headphones, phone, keys) are NOT on desk_b3. Desk is not a storage spot for his items. Likely in bedroom_3 receptacles (nightstand/bed) or on person. Prior for desk_b3 -> 0.05.
3. Marisol’s keys are rarely on nightstand_b1 (prior -> 0.01); glasses are stable there (prior -> 0.60). Phone is often on person (prior -> 0.40) or counter_k1 (prior -> 0.05).
4. Plate_shared_1 is volatile; sink_k1 prior -> 0.50, cupboard_k1 -> 0.10.
5. Static cluster on counter_k1 is highly stable; high priors (0.60-0.80) for items like charger_marisol, lunchboxes, water bottles are validated. Low priors cause heavy penalties.
6. Misplacements are common on kitchen surfaces. Bedroom receptacles are typically empty for personal items during AM.

d13 Sun 05:13: d13 Sun 05:13 desk_b3: empty; resident_3 present. Nico's personal items (headphones, phone, keys) are NOT on desk_b3. Score -1.49 due to over-prioritizing desk. Adjust: Nico items on desk_b3 -> 0.05; likely in bedroom_3 receptacles (nightstand/bed) or on person. Desk is not a storage spot for Nico's daily carry items.
d13 Sun 07:15: d13 Sun 07:15 counter_k1: charger_marisol, lunchbox_nico, lunchbox_talia, mug_marisol, notebook_marisol, pan_shared_1, water_bottle_marisol, water_bottle_nico. No phones. Static cluster holds; notebook_marisol and pan_shared_1 present. Adjust priors: notebook_marisol 0.60, pan_shared_1 0.40, phones 0.05.
d13 Sun 07:15: d13 Sun 07:15 nightstand_b1: empty; resident_1 present. Marisol's glasses (prior 0.60) absent. Score -1.45. Adjust: glasses_marisol on nightstand_b1 -> 0.10. Bedroom receptacles are often empty for personal items during AM, even for 'stable' items like glasses. Marisol is present but not holding/using them there.
d13 Sun 07:15: d13 Sun 07:15: resident_1 (Marisol) in bedroom_1 holding phone_marisol. Confirms phone is often on person during AM (prior 0.45 was reasonable, but absence of other items like keys/glasses on person was costly). Adjust: phone_marisol on person -> 0.50; keys_marisol on person -> 0.05; glasses_marisol on person -> 0.05. Bedroom receptacles remain empty for these items.
d13 Sun 07:15: d13 Sun 07:15 counter_k1: charger_marisol, lunchbox_nico, lunchbox_talia, mug_marisol, notebook_marisol, pan_shared_1, water_bottle_marisol, water_bottle_nico; nobody present. Static cluster confirmed. Score -3.33 due to overconfidence (0.75) on stable items and under-prioritizing pan_shared_1 (0.45 vs actual). Adjust: stable cluster priors to 0.90; pan_shared_1 to 0.60. Bedroom emptiness persists.
d13 Sun 07:15: d13 Sun 07:15 sink_k1: plate_shared_1, pot_shared_1; nobody present. Bowl and pan absent (pan on counter_k1). Score -3.20. Adjust: sink_k1 priors for bowl_shared_1 -> 0.10, pan_shared_1 -> 0.05, plate_shared_1 -> 0.60, pot_shared_1 -> 0.60. Sink holds only shared cookware, not personal items.
