# a60 — scratch memory, final (retired d07 Mon 23:59 (population cap); final weight 0.0000)

d06-d07: counter_k1 is the primary static storage for Marisol's essentials (charger, mug, water_bottle, notebook) and shared items (lunchbox_talia, dog_leash). High persistence (>0.80) from 05:00-10:00. Phones (nico, talia) frequently present pre-dawn (05:00-08:00) but volatile post-10:00; phone_marisol often absent after 10:00. Residents in kitchen carry nothing (no-carry rule confirmed d05-d07).

dish_rack_k1 clusters shared dishes (bowl_shared_1, mug_talia), not counter_k1.

kitchen_table_k1 is a stable overnight drop zone for personal items (backpacks, laptops, notebooks, pens) from 05:00-08:00, not just mid-morning volatile. Priors for these items pre-dawn should be >0.80. Bedroom floor (bedroom_floor_b1) is rarely used for storage when residents are absent; items likely in nightstand_b1 or kitchen.

d07 Mon 06:10: kitchen_table_k1 held backpack_nico, laptop_talia, notebook_marisol, pen_marisol; no residents. Confirms table is a stable overnight drop zone for personal items, not just mid-morning volatile. My priors (0.65) were too low; raise to >0.80 for these specific items pre-dawn. Phone_talia absent (0.15), consistent with counter_k1 pattern.
d07 Mon 06:11: d07 06:11 kitchen_table_k1: backpack_nico, laptop_talia, notebook_marisol, pen_marisol present; phone_talia, backpack_talia, notebook_talia, pen_talia absent. Confirms table is stable pre-dawn drop zone for specific personal items (p>0.80) but not a general catch-all; shared/other personal items remain elsewhere. My 0.30-0.40 priors for absent items were too high, causing score penalty.
