# Affected list vs generator truth

72 message days. Precision over listed objects that were questioned that day; recall over objects with an affected question that day.

Pooled (micro): precision 0.47, recall 0.63; mean over message days: precision 0.46, recall 0.63

| household | day | message | listed | listed & questioned | true affected | precision | recall | missed | false |
|---|---|---|---|---|---|---|---|---|---|
| hh_s10 | 4 | Saturday: It's the weekend, so we're off our usual routine a | 20 | 11 | 4 | 0.36 | 1.00 |  | blanket_shared, glass_yuki, laundry_basket_shared, mug_omar, mug_yuki, remote_sh |
| hh_s10 | 5 | Sunday: It's the weekend, so we're off our usual routine and | 19 | 10 | 12 | 0.70 | 0.58 | duster_shared, pan_shared, phone_omar, spatula_shared, water_bottle_yuki | blanket_shared, bowl_yuki, mug_omar |
| hh_s11 | 3 | Friday: We have friends coming over this evening. Hana is ho | 20 | 11 | 11 | 0.82 | 0.82 | cutting_board_shared, dog_bowl_shared | glass_priya, plate_priya |
| hh_s11 | 4 | Saturday: It's the weekend, so we're off our usual routine a | 20 | 7 | 4 | 0.29 | 0.50 | phone_hana, phone_priya | blanket_shared, dog_bowl_shared, magazine_priya, plate_hana, yoga_mat_priya |
| hh_s11 | 5 | Sunday: It's the weekend, so we're off our usual routine and | 20 | 4 | 2 | 0.25 | 0.50 | phone_priya | snack_bowl_shared, tablet_hana, tablet_priya |
| hh_s11 | 7 | Tuesday: We have friends coming over this evening. | 20 | 9 | 9 | 0.67 | 0.67 | duster_shared, phone_hana, phone_priya | cutting_board_shared, plate_hana, plate_priya |
| hh_s12 | 4 | Saturday: It's the weekend, so we're off our usual routine a | 20 | 8 | 10 | 0.88 | 0.70 | board_game_shared, glasses_priya, vacuum_cleaner_shared | plate_priya |
| hh_s12 | 5 | Sunday: It's the weekend, so we're off our usual routine and | 20 | 9 | 8 | 0.67 | 0.75 | duster_shared, glasses_priya | bowl_priya, glass_priya, plate_priya |
| hh_s12 | 7 | Tuesday: We have friends coming over this evening. | 20 | 14 | 8 | 0.43 | 0.75 | glasses_priya, phone_priya | blanket_shared, bowl_priya, cutting_board_shared, pan_shared, plate_elena, plate |
| hh_s13 | 1 | Wednesday: We have friends coming over this evening. | 20 | 6 | 7 | 0.67 | 0.57 | board_game_shared, kitchen_knife_shared, recipe_book_shared | blanket_shared, book_priya |
| hh_s13 | 2 | Thursday: We have friends coming over this evening. | 20 | 7 | 8 | 0.57 | 0.50 | board_game_shared, charger_hana, phone_hana, phone_priya | blanket_shared, glass_priya, plate_hana |
| hh_s13 | 4 | Saturday: It's the weekend, so we're off our usual routine a | 20 | 5 | 4 | 0.60 | 0.75 | phone_priya | blanket_shared, snack_bowl_shared |
| hh_s13 | 5 | Sunday: It's the weekend, so we're off our usual routine and | 20 | 8 | 4 | 0.38 | 0.75 | mug_priya | glass_hana, guitar_hana, mug_hana, puzzle_box_shared, snack_bowl_shared |
| hh_s14 | 2 | Thursday: We have friends coming over this evening. | 20 | 10 | 5 | 0.40 | 0.80 | board_game_shared | blanket_shared, bowl_yuki, glass_marco, phone_yuki, plate_marco, plate_yuki |
| hh_s14 | 3 | Friday: Marco is home sick today. | 20 | 9 | 6 | 0.56 | 0.83 | blanket_shared | bowl_marco, mug_marco, towel_marco, vitamins_marco |
| hh_s14 | 4 | Saturday: It's the weekend, so we're off our usual routine a | 20 | 7 | 7 | 0.14 | 0.14 | cutting_board_shared, pan_shared, plate_yuki, pot_shared, serving_dish_shared, w | blanket_shared, dog_bowl_shared, mug_marco, snack_bowl_shared, spatula_shared, y |
| hh_s14 | 5 | Sunday: It's the weekend, so we're off our usual routine and | 20 | 8 | 8 | 0.12 | 0.12 | blanket_shared, glasses_marco, mug_marco, pan_shared, phone_yuki, remote_shared, | baking_tray_shared, dog_bowl_shared, dog_food_bag_shared, dog_toy_shared, kitche |
| hh_s14 | 6 | Monday: Marco is home sick today. | 20 | 8 | 4 | 0.38 | 0.75 | blanket_shared | bowl_marco, glasses_marco, mug_marco, towel_marco, vitamins_marco |
| hh_s15 | 1 | Wednesday: Omar is home sick today. | 20 | 9 | 3 | 0.33 | 1.00 |  | blanket_shared, charger_felix, glass_omar, remote_shared, snack_bowl_shared, vit |
| hh_s15 | 2 | Thursday: Omar is home sick today. | 20 | 5 | 5 | 0.60 | 0.60 | blanket_shared, book_omar | journal_omar, notebook_felix |
| hh_s15 | 3 | Friday: We have friends coming over this evening. | 20 | 13 | 6 | 0.38 | 0.83 | phone_yuki | bowl_felix, bowl_yuki, cutting_board_shared, glass_felix, pan_shared, plate_feli |
| hh_s15 | 4 | Saturday: It's the weekend, so we're off our usual routine a | 20 | 9 | 6 | 0.22 | 0.33 | blanket_shared, glass_omar, plate_omar, towel_felix | baking_tray_shared, journal_omar, laundry_basket_shared, mug_omar, recipe_book_s |
| hh_s15 | 5 | Sunday: It's the weekend, so we're off our usual routine and | 20 | 5 | 11 | 0.80 | 0.36 | glass_felix, glass_yuki, glasses_yuki, mug_yuki, phone_yuki, plate_yuki, snack_b | bowl_omar |
| hh_s16 | 4 | Saturday: It's the weekend, so we're off our usual routine a | 20 | 9 | 9 | 0.56 | 0.56 | book_nora, charger_marco, phone_marco, plate_marco | headphones_elena, meditation_cushion_nora, tablet_marco, yoga_mat_marco |
| hh_s16 | 5 | Sunday: It's the weekend, so we're off our usual routine and | 20 | 9 | 11 | 0.56 | 0.45 | cutting_board_shared, glass_elena, mug_elena, recipe_book_shared, tablet_elena,  | blanket_shared, bowl_nora, mug_nora, plate_nora |
| hh_s16 | 6 | Monday: We have friends coming over this evening. | 20 | 8 | 5 | 0.38 | 0.60 | charger_marco, mug_elena | blanket_shared, glass_marco, headphones_elena, laptop_elena, water_bottle_nora |
| hh_s17 | 2 | Thursday: Dana is home sick today. | 20 | 7 | 6 | 0.86 | 1.00 |  | towel_dana |
| hh_s17 | 4 | Saturday: It's the weekend, so we're off our usual routine a | 20 | 3 | 2 | 0.00 | 0.00 | charger_dana, water_bottle_dana | book_sam, glasses_sam, mug_dana |
| hh_s17 | 5 | Sunday: It's the weekend, so we're off our usual routine and | 20 | 6 | 2 | 0.17 | 0.50 | towel_dana | bowl_dana, glass_dana, mug_dana, plate_dana, remote_shared |
| hh_s17 | 6 | Monday: Dana is home sick today. | 20 | 8 | 8 | 0.88 | 0.88 | blanket_shared | snack_bowl_shared |
| hh_s17 | 7 | Tuesday: Sam is home sick today. | 20 | 11 | 7 | 0.55 | 0.86 | phone_sam | detergent_shared, laundry_basket_shared, snack_bowl_shared, towel_sam, vacuum_cl |
| hh_s18 | 4 | Saturday: It's the weekend, so we're off our usual routine a | 20 | 10 | 4 | 0.40 | 1.00 |  | charger_ines, glass_ines, mug_elena, mug_ines, phone_ines, plate_ines |
| hh_s18 | 5 | Sunday: It's the weekend, so we're off our usual routine and | 20 | 11 | 4 | 0.27 | 0.75 | towel_ines | blanket_shared, laundry_basket_shared, mug_elena, remote_shared, snack_bowl_shar |
| hh_s19 | 2 | Thursday: Omar is home sick today. | 20 | 9 | 7 | 0.67 | 0.86 | book_omar | snack_bowl_shared, towel_omar, vitamins_omar |
| hh_s19 | 3 | Friday: Marco is home sick today. | 20 | 8 | 2 | 0.25 | 1.00 |  | blanket_shared, headphones_omar, mug_marco, plate_marco, snack_bowl_shared, towe |
| hh_s19 | 4 | Saturday: It's the weekend, so we're off our usual routine a | 20 | 9 | 6 | 0.44 | 0.67 | phone_omar, towel_omar | blanket_shared, charger_marco, glass_marco, plate_omar, snack_bowl_shared |
| hh_s19 | 5 | Sunday: It's the weekend, so we're off our usual routine and | 20 | 7 | 4 | 0.43 | 0.75 | duster_shared | charger_marco, hair_dryer_marco, towel_marco, vitamins_marco |
| hh_s20 | 1 | Wednesday: Aisha is home sick today. | 20 | 8 | 4 | 0.38 | 0.75 | blanket_shared | dog_bowl_shared, dog_food_bag_shared, dog_toy_shared, glass_aisha, mug_aisha |
| hh_s20 | 3 | Friday: Hana is home sick today. | 20 | 8 | 8 | 0.75 | 0.75 | glass_hana, plate_hana | skincare_hana, towel_hana |
| hh_s20 | 4 | Saturday: It's the weekend, so we're off our usual routine a | 20 | 6 | 5 | 0.33 | 0.40 | duster_shared, towel_hana, water_bottle_aisha | book_aisha, guitar_aisha, tablet_aisha, watering_can_shared |
| hh_s20 | 5 | Sunday: It's the weekend, so we're off our usual routine and | 20 | 12 | 8 | 0.50 | 0.75 | glasses_hana, shopping_bag_shared | blanket_shared, bowl_aisha, glass_hana, mug_aisha, plate_hana, water_bottle_hana |
| hh_s21 | 4 | Saturday: It's the weekend, so we're off our usual routine a | 20 | 11 | 6 | 0.09 | 0.17 | phone_dana, plate_dana, plate_felix, towel_dana, towel_felix | blanket_shared, dog_bowl_shared, dog_toy_shared, laundry_basket_shared, mixing_b |
| hh_s21 | 5 | Sunday: It's the weekend, so we're off our usual routine and | 20 | 11 | 12 | 0.45 | 0.42 | baking_tray_shared, glasses_dana, mixing_bowl_shared, phone_dana, phone_felix, t | blanket_shared, bowl_dana, dog_bowl_shared, dog_toy_shared, plate_dana, plate_fe |
| hh_s22 | 3 | Friday: Sam is home sick today. | 20 | 8 | 8 | 0.62 | 0.62 | blanket_shared, book_sam, charger_sam | plate_sam, skincare_sam, towel_sam |
| hh_s22 | 4 | Saturday: It's the weekend, so we're off our usual routine a | 16 | 3 | 12 | 0.33 | 0.08 | blanket_shared, glass_sam, glass_tomas, glass_yuki, kitchen_knife_shared, phone_ | headphones_sam, yoga_mat_tomas |
| hh_s22 | 5 | Sunday: It's the weekend, so we're off our usual routine and | 17 | 6 | 9 | 0.50 | 0.33 | charger_sam, glass_sam, glass_tomas, phone_yuki, plate_sam, pot_shared | mug_sam, snack_bowl_shared, yoga_mat_tomas |
| hh_s23 | 4 | Saturday: It's the weekend, so we're off our usual routine a | 20 | 7 | 2 | 0.14 | 0.50 | towel_zara | glass_aisha, glasses_aisha, mug_aisha, skincare_aisha, tablet_aisha, towel_aisha |
| hh_s23 | 5 | Sunday: It's the weekend, so we're off our usual routine and | 20 | 7 | 5 | 0.14 | 0.20 | cutting_board_shared, glass_aisha, kitchen_knife_shared, towel_zara | blanket_shared, charger_zara, guitar_zara, sketchbook_zara, snack_bowl_shared, w |
| hh_s23 | 6 | Monday: We have friends coming over this evening. | 20 | 13 | 6 | 0.46 | 1.00 |  | blanket_shared, bowl_aisha, laptop_zara, notebook_zara, plate_aisha, plate_zara, |
| hh_s23 | 7 | Tuesday: Zara is home sick today. | 20 | 13 | 8 | 0.46 | 0.75 | book_zara, tablet_zara | bowl_zara, glass_zara, plate_zara, razor_zara, skincare_zara, towel_zara, vitami |
| hh_s24 | 1 | Wednesday: Dana is home sick today. | 20 | 12 | 9 | 0.75 | 1.00 |  | skincare_dana, towel_dana, vitamins_dana |
| hh_s24 | 2 | Thursday: We have friends coming over this evening. | 20 | 10 | 4 | 0.30 | 0.75 | serving_dish_shared | blanket_shared, glass_dana, mug_leo, plate_dana, plate_leo, water_bottle_dana, w |
| hh_s24 | 4 | Saturday: It's the weekend, so we're off our usual routine a | 20 | 8 | 7 | 0.75 | 0.86 | towel_leo | bowl_dana, mug_dana |
| hh_s24 | 5 | Sunday: It's the weekend, so we're off our usual routine and | 20 | 4 | 1 | 0.00 | 0.00 | towel_leo | charger_dana, journal_leo, mug_leo, phone_leo |
| hh_s24 | 6 | Monday: Leo is home sick today. | 20 | 12 | 8 | 0.58 | 0.88 | charger_leo | headphones_dana, remote_shared, skincare_leo, snack_bowl_shared, vitamins_leo |
| hh_s25 | 1 | Wednesday: Omar is home sick today. | 20 | 9 | 6 | 0.56 | 0.83 | charger_omar | blanket_shared, remote_shared, vitamins_omar, water_bottle_marco |
| hh_s25 | 4 | Saturday: It's the weekend, so we're off our usual routine a | 20 | 7 | 3 | 0.00 | 0.00 | phone_omar, towel_marco, towel_omar | blanket_shared, meditation_cushion_marco, mug_marco, mug_omar, remote_shared, sn |
| hh_s25 | 5 | Sunday: It's the weekend, so we're off our usual routine and | 20 | 15 | 0 | 0.00 | - |  | blanket_shared, book_marco, bowl_marco, bowl_omar, glass_marco, glass_omar, head |
| hh_s26 | 2 | Thursday: Leo is home sick today. | 20 | 10 | 7 | 0.50 | 0.71 | charger_leo, phone_leo | dog_bowl_shared, dog_food_bag_shared, dog_toy_shared, remote_shared, snack_bowl_ |
| hh_s26 | 3 | Friday: Kwame is home sick today. | 20 | 10 | 6 | 0.60 | 1.00 |  | book_kwame, glasses_sam, skincare_leo, towel_kwame |
| hh_s26 | 4 | Saturday: It's the weekend, so we're off our usual routine a | 20 | 9 | 8 | 0.56 | 0.62 | charger_kwame, phone_kwame, snack_bowl_shared | blanket_shared, mug_leo, mug_sam, plate_leo |
| hh_s26 | 5 | Sunday: It's the weekend, so we're off our usual routine and | 20 | 5 | 10 | 0.80 | 0.40 | glass_leo, glass_sam, plate_kwame, toolbox_shared, towel_leo, water_bottle_kwame | mug_sam |
| hh_s26 | 6 | Monday: We have friends coming over this evening. | 20 | 8 | 6 | 0.62 | 0.83 | phone_leo | glass_kwame, plate_sam, water_bottle_leo |
| hh_s27 | 4 | Saturday: It's the weekend, so we're off our usual routine a | 20 | 13 | 8 | 0.46 | 0.75 | glasses_elena, pot_shared | dog_bowl_shared, glass_tomas, guitar_tomas, laundry_basket_shared, plate_tomas,  |
| hh_s27 | 5 | Sunday: It's the weekend, so we're off our usual routine and | 20 | 8 | 6 | 0.38 | 0.50 | glasses_elena, recipe_book_shared, serving_dish_shared | blanket_shared, book_elena, mug_elena, snack_bowl_shared, tablet_elena |
| hh_s28 | 2 | Thursday: Hana is home sick today. | 20 | 8 | 3 | 0.25 | 0.67 | blanket_shared | glasses_hana, hair_dryer_hana, razor_hana, skincare_hana, toiletry_bag_hana, tow |
| hh_s28 | 4 | Saturday: It's the weekend, so we're off our usual routine a | 20 | 7 | 6 | 0.43 | 0.50 | duster_shared, phone_elena, towel_elena | blanket_shared, glasses_hana, mug_hana, remote_shared |
| hh_s28 | 5 | Sunday: It's the weekend, so we're off our usual routine and | 20 | 6 | 5 | 0.33 | 0.40 | plate_elena, plate_hana, towel_elena | controller_elena, headset_elena, mug_elena, mug_hana |
| hh_s28 | 7 | Tuesday: We have friends coming over this evening. | 20 | 9 | 5 | 0.33 | 0.60 | serving_dish_shared, spatula_shared | blanket_shared, glass_elena, laptop_elena, mug_hana, plate_hana, water_bottle_el |
| hh_s29 | 4 | Saturday: It's the weekend, so we're off our usual routine a | 20 | 9 | 7 | 0.56 | 0.71 | tablet_kwame, towel_nora | bowl_kwame, glass_nora, headphones_kwame, plate_nora |
| hh_s29 | 5 | Sunday: It's the weekend, so we're off our usual routine and | 20 | 9 | 14 | 0.89 | 0.57 | baking_tray_shared, charger_nora, mixing_bowl_shared, phone_kwame, phone_nora, t | plate_kwame |
| hh_s29 | 7 | Tuesday: Nora is home sick today. | 20 | 8 | 6 | 0.75 | 1.00 |  | remote_shared, snack_bowl_shared |

## Per household

| household | message days | mean precision | mean recall |
|---|---|---|---|
| hh_s10 | 2 | 0.53 | 0.79 |
| hh_s11 | 4 | 0.51 | 0.62 |
| hh_s12 | 3 | 0.66 | 0.73 |
| hh_s13 | 4 | 0.55 | 0.64 |
| hh_s14 | 5 | 0.32 | 0.53 |
| hh_s15 | 5 | 0.47 | 0.63 |
| hh_s16 | 3 | 0.50 | 0.54 |
| hh_s17 | 5 | 0.49 | 0.65 |
| hh_s18 | 2 | 0.34 | 0.88 |
| hh_s19 | 4 | 0.45 | 0.82 |
| hh_s20 | 4 | 0.49 | 0.66 |
| hh_s21 | 2 | 0.27 | 0.29 |
| hh_s22 | 3 | 0.49 | 0.35 |
| hh_s23 | 4 | 0.30 | 0.61 |
| hh_s24 | 5 | 0.48 | 0.70 |
| hh_s25 | 3 | 0.19 | 0.42 |
| hh_s26 | 5 | 0.62 | 0.71 |
| hh_s27 | 2 | 0.42 | 0.62 |
| hh_s28 | 4 | 0.34 | 0.54 |
| hh_s29 | 3 | 0.73 | 0.76 |
