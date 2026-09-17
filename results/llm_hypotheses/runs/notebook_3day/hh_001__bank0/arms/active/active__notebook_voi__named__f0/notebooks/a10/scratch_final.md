# a10 — scratch memory, final (retired d01 Tue 23:59 (population cap); final weight 0.1014)

d01 Tue 06:06: Looked at cupboard_k1. Found: mug_shared_1, pot_shared_1. Residents: resident_1.
- SCORE ANALYSIS: -6.55. Weight 0.101, rank 5/5. Scored above panel average (-7.11). The loss is driven by the long tail of absent items where I assigned non-zero probabilities (0.05) to ~8 objects (bowls, plates, pans, etc.) that were not in the cupboard. Even small probabilities for absent items hurt when the item is definitely elsewhere. I correctly identified mug_shared_1 and pot_shared_1 as likely candidates but underestimated the 'cleanliness' of the cupboard (i.e., it holds very few items).
- OBSERVATION: Resident_1 is in Kitchen (confirmed again). The cupboard contains only shared kitchenware (mug, pot). No personal items (mug_mara, water_bottle_mara) were found here, confirming they are on the counter (as seen at 06:06).
- KEY INSIGHT: The cupboard is a 'storage' receptacle for shared items, not a 'active' one. It holds items that are not currently in use. Since the resident is in the Kitchen, active items (mug_mara, water_bottle_mara, bowl_shared_1, plate_shared_2) are on the counter. The cupboard holds the 'reserve' shared items (mug_shared_1, pot_shared_1). This reinforces the 'Active vs. Stored' distinction: Active items are on the counter; Stored shared items are in the cupboard.
- CORRECTION: Sharpen the 'Active vs. Stored' distinction for the Kitchen.
  1. Active Kitchen Items (High P on counter_k1): mug_mara, water_bottle_mara, bowl_shared_1, plate_shared_2. (Confirmed stable).
  2. Stored Kitchen Items (High P on cupboard_k1): mug_shared_1, pot_shared_1. (Confirmed stable).
  3. Unlikely Kitchen Items (Low P on counter_k1/cupboard_k1): keys_mara, wallet_mara, jacket_mara, umbrella_mara, backpack_mara, lunchbox_mara. These belong in Entry or Bedroom. P(Kitchen) should be <0.01 unless resident is moving to Entry.
  4. Impossible Kitchen Items (Zero P on counter_k1/cupboard_k1): hairbrush_mara, makeup_kit_mara, medication_bottle_mara, towel_mara, blanket_mara, yoga_mat_mara, suitcase_mara. These are strictly Bedroom/Bathroom items. P(Kitchen) = 0.0.
- UPDATED STATE:
  1. Resident_1: In Kitchen (0.98) at 06:06.
  2. mug_mara: counter_k1 (confirmed).
  3. water_bottle_mara: counter_k1 (confirmed).
  4. bowl_shared_1: counter_k1 (confirmed).
  5. plate_shared_2: counter_k1 (confirmed).
  6. mug_shared_1: cupboard_k1 (confirmed).
  7. pot_shared_1: cupboard_k1 (confirmed).
  8. hairbrush_mara: bathroom_shelf_ba1 (0.95) - resident left Bathroom 15 mins ago.
  9. phone_mara: counter_k1 (0.15) or nightstand_b1 (0.7) or ON_PERSON (0.1).
  10. keys_mara/wallet_mara: Bedroom (0.6) or Entry (0.3) or ON_PERSON (0.1). NOT in Kitchen.
- NEXT STEPS: If asked for mug/water/bowl/plate, predict counter_k1 with high confidence. If asked for shared mug/pot, predict cupboard_k1 with high confidence. If asked for hairbrush/makeup/meds, predict Bathroom shelf/rack. If asked for keys/wallet, predict Bedroom/Entry, NOT Kitchen. Be stricter about excluding Bedroom/Bathroom items from Kitchen predictions. Assign near-zero probability to absent items in a receptacle once confirmed empty of them.
