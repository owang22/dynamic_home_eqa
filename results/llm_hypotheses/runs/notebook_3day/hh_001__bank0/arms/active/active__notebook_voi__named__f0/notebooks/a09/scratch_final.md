# a09 — scratch memory, final (retired d01 Tue 23:59 (population cap); final weight 0.0679)

d01 Tue 05:58: Looked at counter_k1. Found: lunchbox_mara, mug_mara, notebook_mara, pen_mara. Residents: resident_1.
- OBSERVATION: Resident moved from Bathroom to Kitchen. Counter holds 'work/school' items (lunchbox, notebook, pen) and a mug. 
- SCORE ANALYSIS: Score -17.25. Worst in panel. 
- ERROR ANALYSIS: 
1. I assigned 0.00 to lunchbox, notebook, pen, mug. These were present. log(0.00) is undefined, effectively -inf, but the system likely floors it or I missed the 'long tail' implication. Actually, looking at my forecast, I explicitly set them to 0.00. This is a catastrophic failure of the 'static/mobile' model. I assumed these were in the bedroom or on person, but they are on the kitchen counter.
2. I assigned 0.25 to phone, 0.20 to charger. Both absent. log(0.75)+log(0.80) = -0.29 -0.22 = -0.51. Not the main killer.
3. The main killer is the 0.00s on present items. I failed to account for 'preparation' items being staged in the kitchen.
- LESSON: The 'Kitchen Counter' is a staging area for morning departure items (lunchbox, notebook, pen, mug). My belief that these are 'bedroom' or 'on person' items is wrong for the 05:00-09:00 window. They are likely placed on the counter while the resident is in the bathroom/bedroom.
- ADJUSTMENT: 
1. Raise prior for lunchbox, notebook, pen, mug on counter_k1 during morning hours (05:00-09:00).
2. Lower prior for phone/charger on counter_k1. They are likely still in bedroom or on person (though person was in bathroom, maybe they left them on nightstand/desk? Nightstand was empty. Desk? Unknown).
3. Resident is in Kitchen. This suggests they are finishing up morning routine or eating breakfast.
- CURRENT STATE: Resident in Kitchen. Carrying wallet (from 05:40). Counter has lunchbox, mug, notebook, pen. Phone/Charger location still unknown (not on person, not on nightstand, not on counter). Likely on desk_b1 or in bedroom.
- STRATEGY: Next look should probably be desk_b1 to find phone/charger, or entry_table_e1 to check keys/jacket status. But budget is limited (8 looks). I have used 3 (bathroom_shelf, nightstand, resident, counter). Wait, 4 looks. 4 left.
- PRIORITY: Find phone/charger. If they are on desk_b1, that's a high-value target. If they are OUT_OF_HOUSE, that's also a high-value target (but resident is in house). So desk_b1 is the best bet for phone/charger.
