# a08 — scratch memory, final (retired d01 Tue 05:38 (population cap); final weight 0.0980)

d01 Tue 05:38: Looked at bathroom_shelf_ba1. Found: hairbrush_mara, makeup_kit_mara, medication_bottle_mara. Residents: resident_1.
- MAJOR CORRECTION: My previous belief that hairbrush_mara is an 'active' item rarely on the shelf was WRONG. It is a 'stored' item on the shelf, just like makeup and meds. The 05:34 absence from the rack did not imply absence from the shelf; it implied it was on the shelf all along (or moved there quickly).
- Score Analysis: -3.47. I assigned 0.05 to hairbrush_mara (actual: present). Log(0.05) = -3.0. This single error dominated the score. I assigned 0.95 to makeup/meds (correct). The penalty for the hairbrush was severe because I explicitly lowered its probability based on the 'active use' hypothesis.
- Revised Model for Bathroom Items:
  - bathroom_shelf_ba1 is the primary storage for: makeup_kit_mara, medication_bottle_mara, hairbrush_mara.
  - towel_rack_ba1 is the primary storage for: towel_mara.
  - These items are rarely ON_PERSON or on the floor unless the resident is actively using them (e.g., brushing hair *right now*). At 05:38, resident is present, but hairbrush is on shelf. This suggests 'grooming' might be a quick task or the resident is just in the room, not necessarily mid-brush.
- Current State (05:38):
  - Resident_1: Bathroom (1.0).
  - hairbrush_mara: bathroom_shelf_ba1 (1.0).
  - makeup_kit_mara: bathroom_shelf_ba1 (1.0).
  - medication_bottle_mara: bathroom_shelf_ba1 (1.0).
  - towel_mara: towel_rack_ba1 (1.0).
- Movement Prediction:
  - Resident is in Bathroom. Next likely move: Kitchen (breakfast) or Bedroom (finish getting ready).
  - If moving to Kitchen, likely carries: phone_mara, water_bottle_mara, keys_mara (if leaving soon), wallet_mara.
  - Electronics (laptop, tablet) likely remain in Bedroom or Living.
- Lesson: Do not over-apply 'active use' heuristics to small personal items. If an item has a designated 'home' receptacle (shelf, rack, drawer), it is there 90%+ of the time unless the resident is explicitly observed using it. The 'active' state is a transient exception, not the default. I will revert hairbrush_mara to 'Stored' category with high probability on shelf.
