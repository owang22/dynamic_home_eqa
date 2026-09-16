# notebook mixture — active__notebook_mixture__named__f0

## calls (n / seconds) per call type per day
| day | initial | question_forecast | look_forecast | follow_up | fork | review | total |
|---|---|---|---|---|---|---|---|
| d00 | 1 / 195s | 131 / 1225s | 14 / 181s | 14 / 394s | 0 / 0s | 1 / 45s | 161 / 2041s |
| d01 | 0 / 0s | 168 / 1627s | 0 / 0s | 0 / 0s | 0 / 0s | 1 / 37s | 169 / 1664s |
| d02 | 0 / 0s | 192 / 1659s | 0 / 0s | 0 / 0s | 0 / 0s | 1 / 32s | 193 / 1690s |

## population
size at the start of each day: d00=0, d01=7, d02=8
- end of d00 review: 6 agents, candidate a02
- end of d01 review: 7 agents, candidate a02
- end of d02 review: 8 agents, candidate a02
- births 4, forks 5 (rejected 0), retirements 0, reviews failed 0, scratch truncations 0, invalid forecasts 19
- final weights: a04 0.990, a01 0.008, a05 0.001, a03 0.000, a06 0.000, a07 0.000, a02 0.000, a08 0.000, a09 0.000

## looks
3 looks; budget ran out at: d00 never, d01 never, d02 never
receptacle looks 3, person looks 0; 3 looks found something

## accuracy (exact, queried objects)
- d00: 12/24 = 0.50
- d01: 9/24 = 0.38
- d02: 16/24 = 0.67
- all: 37/72 = 0.51

## example fork: a02 -> a05
**why:** The previous beliefs were too generic and spread probability too thin. The look at counter_k1 revealed a specific cluster of items (lunchbox, mug, water bottle) that were not sufficiently prioritized. The new beliefs explicitly group items by room and time of day, and assign higher probabilities to the 'kitchen personal items' cluster on the counter. This should improve forecast accuracy for kitchen looks.

### parent a02 beliefs
BELIEFS: The household is disorganized. Objects are left where they are used. 1. **General Rule:** If an object is used in Room X, it stays in Room X until moved again. 2. **Kitchen:** Mugs, plates, bowls, pans, and pots are often left on counter_k1 or kitchen_table_k1 after use. Dish_rack_k1 is used sporadically. Cupboard_k1 is rarely used for storage. 3. **Living Room:** Remote_shared_1 is on couch_l1, armchair_l1, or coffee_table_l1. Books and notebooks are on couch_l1 or coffee_table_l1. Blanket_mara is on couch_l1 or bed_b1. 4. **Bedroom:** Phone, charger, glasses, and laptop are on bed_b1 or nightstand_b1. Clothes (jacket, backpack) are on bedroom_floor_b1 or desk_b1. 5. **Bathroom:** Towel_mara is on towel_rack_ba1 or bathroom_shelf_ba1. Makeup and medication are on bathroom_shelf_ba1 or counter (if present, but only shelf/rack listed). 6. **Entry:** Keys, wallet, and jacket are often on entry_table_e1 or entry_floor_e1. Umbrella is in entry_floor_e1. 7. **Movement:** Objects move between rooms based on resident activity. If resident is in living room, phone and tablet are likely there. If in bedroom, they are there. 8. **Uncertainty:** High probability of objects being in 'last used' location. 9. **Laundry:** Laundry_basket_mara is in bedroom or living room, often full. 10. **Yoga Mat:** Yoga_mat_mara is in living room or bedroom, often unrolled. 11. **Vacuum:** Vacuum_cleaner_shared_1 is in living room or entry, often in use. 12. **Suitcase:** Suitcase_mara is in bedroom or living room, often open. 13. **Watering Can:** Watering_can_mara is in kitchen or entry, often used. 14. **Backpack:** Backpack_mara is in entry or bedroom, often open. 15. **Hairbrush:** Hairbrush_mara is in bathroom or bedroom, often on floor. 16. **Headphones:** Headphones_mara are in bedroom or living room, often on couch. 17. **Pen:** Pen_mara is in bedroom or living room, often on table. 18. **Lunchbox:** Lunchbox_mara is in kitchen or OUT_OF_HOUSE, often dirty. 19. **Blanket:** Blanket_mara is on couch_l1 or bed_b1, often crumpled. 20. **Pan/Pot:** Pan_shared_1 and pot_shared_1 are on counter_k1 or kitchen_table_k1, often dirty. 21. **Plate/Bowl:** Plate_shared_1/2 and Bowl_shared_1/2 are on kitchen_table_k1 or counter_k1, often dirty. 22. **Charger:** Charger_mara is with phone or on bed_b1. 23. **Glasses:** Glasses_mara are ON_PERSON or on bed_b1. 24. **Jacket:** Jacket_mara is ON_PERSON or on bedroom_floor_b1. 25. **Keys:** Keys_mara are ON_PERSON or on entry_table_e1. 26. **Laptop:** Laptop_mara is on desk_b1 or couch_l1. 27. **Laundry Basket:** Laundry_basket_mara is in bedroom or living room. 28. **Lunchbox:** Lunchbox_mara is in kitchen or OUT_OF_HOUSE. 29. **Makeup Kit:** Makeup_kit_mara is in bathroom or bedroom. 30. **Medication Bottle:** Medication_bottle_mara is in bathroom or bedroom. 31. **Mug:** Mug_mara is in kitchen. 32. **Notebook:** Notebook_mara is in bedroom or living room. 33. **Pan:** Pan_shared_1 is in kitchen. 34. **Pen:** Pen_mara is in bedroom or living room. 35. **Phone:** Phone_mara is ON_PERSON or in bedroom/living room. 36. **Plate:** Plate_shared_1/2 is in kitchen. 37. **Pot:** Pot_shared_1 is in kitchen. 38. **Remote:** Remote_shared_1 is in living room. 39. **Suitcase:** Suitcase_mara is in bedroom or living room. 40. **Tablet:** Tablet_mara is in bedroom or living room. 41. **Towel:** Towel_mara is in bathroom. 42. **Umbrella:** Umbrella_mara is in entry. 43. **Vacuum:** Vacuum_cleaner_shared_1 is in entry or living room. 44. **Wallet:** Wallet_mara is ON_PERSON or in entry. 45. **Water Bottle:** Water_bottle_mara is in kitchen or ON_PERSON. 46. **Watering Can:** Watering_can_mara is in kitchen or entry. 47. **Yoga Mat:** Yoga_mat_mara is in bedroom or living room.

### child a05 beliefs
BELIEFS: The household is disorganized with a strong 'last used location' bias. Objects cluster in the room where they are actively used. 

1. **Kitchen Counter (counter_k1):** High probability for: mug_mara, water_bottle_mara, lunchbox_mara, pan_shared_1, pot_shared_1, plate_shared_1/2, bowl_shared_1/2. These items are frequently left here after use or while being prepared. Resident_1 is often here in the morning.
2. **Kitchen Sink/Dish Rack:** High probability for dirty dishes (plates, bowls, pans) if not on counter. 
3. **Living Room:** Remote_shared_1, blanket_mara, headphones_mara, laptop_mara, tablet_mara, book_mara, notebook_mara. These are leisure/work items. 
4. **Bedroom:** Phone_mara, charger_mara, glasses_mara, jacket_mara, backpack_mara, hairbrush_mara, makeup_kit_mara, medication_bottle_mara, towel_mara (if brought in), laundry_basket_mara, yoga_mat_mara. 
5. **Entry:** Keys_mara, wallet_mara, umbrella_mara, jacket_mara (if going out), backpack_mara (if going out). 
6. **Bathroom:** Towel_mara, hairbrush_mara, makeup_kit_mara, medication_bottle_mara. 
7. **Movement Patterns:** 
   - Morning (06:00-09:00): Resident_1 likely in Kitchen or Bathroom. Kitchen counter will have mugs, water bottles, lunchboxes. Bathroom will have towels, makeup, medication.
   - Daytime: Resident_1 likely in Living Room or Bedroom. Phone/tablet/laptop move with resident.
   - Evening: Resident_1 likely in Living Room. Remote, blanket, headphones likely there.
8. **ON_PERSON:** Keys, wallet, phone, glasses, jacket, water bottle (sometimes) are often ON_PERSON when resident is moving between rooms or going out.
9. **OUT_OF_HOUSE:** Lunchbox, umbrella, jacket, backpack, keys, wallet are likely OUT_OF_HOUSE if resident is out. 
10. **Specific Object Rules:** 
   - Lunchbox_mara: Kitchen (counter/sink) or OUT_OF_HOUSE.
   - Water_bottle_mara: Kitchen (counter) or ON_PERSON.
   - Mug_mara: Kitchen (counter) or Living Room (coffee table).
   - Phone_mara: ON_PERSON, Bedroom (bed/nightstand), or Living Room (couch/table).
   - Keys_mara: ON_PERSON or Entry (table/floor).
   - Jacket_mara: ON_PERSON, Entry (hook/floor), or Bedroom (floor/desk).
   - Blanket_mara: Living Room (couch) or Bedroom (bed).
   - Remote_shared_1: Living Room (couch/armchair/coffee table).
   - Laptop_mara: Bedroom (desk) or Living Room (couch/table).
   - Tablet_mara: Bedroom (bed) or Living Room (couch/table).
   - Headphones_mara: Bedroom (bed/desk) or Living Room (couch).
   - Hairbrush_mara: Bathroom (shelf) or Bedroom (floor/desk).
   - Makeup_kit_mara: Bathroom (shelf) or Bedroom (desk).
   - Medication_bottle_mara: Bathroom (shelf) or Bedroom (nightstand).
   - Towel_mara: Bathroom (rack/shelf) or Bedroom (floor).
   - Yoga_mat_mara: Living Room (floor) or Bedroom (floor).
   - Vacuum_cleaner_shared_1: Living Room (corner) or Entry.
   - Suitcase_mara: Bedroom (floor) or Living Room (floor).
   - Watering_can_mara: Kitchen (counter) or Entry (floor).
   - Backpack_mara: Entry (floor/table) or Bedroom (floor/desk).
   - Umbrella_mara: Entry (floor/table).
   - Pen_mara: Bedroom (desk) or Living Room (table).
   - Book_mara: Living Room (couch/table) or Bedroom (bed).
   - Notebook_mara: Bedroom (desk) or Living Room (table).

