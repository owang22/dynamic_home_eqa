# Household hh_s2 — five days, Wednesday to Sunday

Seed-generated household. Times are clock times; ids are the receptacle and object ids used in events.jsonl. A line indented under an activity says where an object went when the activity ended and why. WHIM marks a placement that landed somewhere other than where the decision was heading. Text in [brackets] names the hidden cause the decision is attributed to.

## Household

Type: couple. Rooms: bathroom, bedroom_1, dining, entry, kitchen, living, office.

Residents:

- **Priya** (resident_1): works outside the home; very tidy (tidiness 0.78); punctual (jitter scale 0.69); sometimes forgets pocket items; mood strongly affects behaviour (sensitivity 0.93); sleeps in bedroom_1, works at the bedroom_1 desk
- **Ines** (resident_2): works outside the home; untidy (tidiness 0.40); average timing (jitter scale 0.95); sometimes forgets pocket items; mood moderately affects behaviour (sensitivity 0.42); sleeps in bedroom_1, works at the bedroom_1 desk

Objects and their usual place (primary slot first):

- Priya's: book_priya → nightstand_b1 / bookshelf_l1; charger_priya → desk_b1 / nightstand_b1; glasses_priya → nightstand_b1 / desk_b1; handbag_priya → entry_hook_e1 / bedroom_floor_b1 / desk_b1; jacket_priya → entry_hook_e1 / wardrobe_b1; keys_priya → entry_table_e1 / nightstand_b1; laptop_priya → desk_b1 / bookshelf_l1; medication_priya → medicine_cabinet_ba1 / nightstand_b1; mug_priya → cupboard_k1 / dish_rack_k1 / sink_k1; notebook_priya → desk_b1 / bookshelf_l1; phone_priya → nightstand_b1 / coffee_table_l1; shoes_priya → entry_floor_e1 / wardrobe_b1; towel_priya → towel_rack_ba1 / bathroom_shelf_ba1; wallet_priya → nightstand_b1 / desk_b1; water_bottle_priya → dish_rack_k1 / counter_k1 / sink_k1
- Ines's: backpack_ines → entry_hook_e1 / bedroom_floor_b1 / desk_b1; book_ines → nightstand_b1 / bookshelf_l1; glasses_ines → nightstand_b1 / desk_b1; headphones_ines → desk_b1 / nightstand_b1; jacket_ines → entry_hook_e1 / wardrobe_b1; keys_ines → entry_table_e1 / nightstand_b1; laptop_ines → desk_b1 / bookshelf_l1; medication_ines → medicine_cabinet_ba1 / nightstand_b1; mug_ines → cupboard_k1 / dish_rack_k1 / sink_k1; phone_ines → nightstand_b1 / coffee_table_l1; shoes_ines → entry_floor_e1 / wardrobe_b1; towel_ines → towel_rack_ba1 / bathroom_shelf_ba1; wallet_ines → nightstand_b1 / desk_b1; water_bottle_ines → dish_rack_k1 / counter_k1 / sink_k1
- Shared: blanket_shared → couch_l1 / armchair_l1; laundry_basket_shared → bathroom_shelf_ba1 / bedroom_floor_b1; remote_shared → tv_stand_l1 / coffee_table_l1

Object groups (things that travel together):

- backpack_ines carries headphones_ines, laptop_ines on trips to work and errands
- handbag_priya carries charger_priya, laptop_priya, notebook_priya, water_bottle_priya on trips to work and errands


## Day 0 — Wednesday

**Active causes**

- `late_work:resident_2` (Ines): A long day at work; home two hours late. gets home late and hurried; the evening walk and cooking are dropped and things are dumped at the door.
- `rain` (household): It rains for most of the day. no walk; wet shoes, jackets and umbrellas get dropped at the entry instead of being put away.
- `low_energy:resident_2`: Ines has low energy (0.00): leaves things where they were used instead of putting them back.

Internal states (0–1): Priya energy 0.69, hurriedness 0.31, distraction 0.13; Ines energy 0.00, hurriedness 0.60, distraction 0.50

**Timeline**

```
06:05  Ines — morning routine in the bathroom; brings phone_ines from nightstand_b1, glasses_ines from nightstand_b1
06:30  Ines finishes morning routine
          glasses_ines → bed_b1: put back in its usual place; nightstand_b1 was full, so it went to bed_b1
06:38  Priya — morning routine in the bathroom; brings phone_priya from nightstand_b1, glasses_priya from nightstand_b1
07:03  Priya finishes morning routine
          glasses_priya → bed_b1: put back in its usual place; nightstand_b1 was full, so it went to bed_b1
07:32  Priya — breakfast in the kitchen; brings mug_priya from cupboard_k1
07:50  Ines — breakfast in the kitchen; brings mug_ines from cupboard_k1
07:57  Priya finishes breakfast
          mug_priya → sink_k1: used, so it goes in the sink
          keeps phone_priya for work
08:11  Priya leaves for work (back 17:41); takes handbag_priya (with charger_priya, laptop_priya, notebook_priya, water_bottle_priya), keys_priya, phone_priya, wallet_priya, jacket_priya, shoes_priya
08:15  Ines finishes breakfast
          keeps phone_ines for work
08:21  Ines leaves for work (back 19:51); takes backpack_ines (with headphones_ines, laptop_ines), keys_ines, phone_ines, wallet_ines, jacket_ines, shoes_ines
17:41  Priya is back from work
          handbag_priya → entry_floor_e1: wet bag left by the door [rain]
          charger_priya → entry_floor_e1: stays in the handbag
          jacket_priya → entry_hook_e1: wet jacket hung on the hook [rain]
          keys_priya → entry_table_e1: put away in its usual place after the trip
          laptop_priya → entry_floor_e1: stays in the handbag
          notebook_priya → entry_floor_e1: stays in the handbag
          shoes_priya → entry_floor_e1: wet shoes left on the entry floor to dry [rain]
          wallet_priya → nightstand_b1: put away in its usual place after the trip
          water_bottle_priya → entry_floor_e1: stays in the handbag
          keeps phone_priya for cooking dinner
18:05  Priya — cooking dinner in the kitchen
19:03  Priya — dinner in the dining; brings water_bottle_priya from entry_floor_e1
19:43  Priya finishes dinner
          water_bottle_priya → sink_k1: used, so it goes in the sink
19:51  Ines is back from work
          backpack_ines → entry_floor_e1: bag dumped by the door, home late [late_work:resident_2]
          headphones_ines → entry_floor_e1: stays in the backpack
          jacket_ines → armchair_l1: WHIM — was heading for couch_l1 (jacket thrown over the couch, home late) but landed on armchair_l1 instead [late_work:resident_2]
          keys_ines → entry_table_e1: put away in its usual place after the trip
          laptop_ines → entry_floor_e1: stays in the backpack
          shoes_ines → entry_floor_e1: wet shoes left on the entry floor to dry [rain]
          wallet_ines → nightstand_b1: put away in its usual place after the trip
          keeps phone_ines for dinner
19:51  Ines — dinner in the dining; brings water_bottle_ines from dish_rack_k1
20:12  Priya — evening TV in the living (bout 1/2); brings remote_shared from tv_stand_l1, blanket_shared from couch_l1, mug_priya from sink_k1, glasses_priya from bed_b1
20:31  Ines finishes dinner
          water_bottle_ines → sink_k1: used, so it goes in the sink
20:31  Ines — evening TV in the living (bout 1/2) [shifted by late_work:resident_2]; brings mug_ines from kitchen_table_k1, glasses_ines from bed_b1
20:48  Ines finishes evening TV
          blanket_shared → couch_l1: put back in its usual place
          glasses_ines → desk_b1: left where it was used; coffee_table_l1 was full, so it went to desk_b1
          mug_ines → dish_rack_k1: left where it was used; coffee_table_l1 was full, so it went to dish_rack_k1
          remote_shared → tv_stand_l1: put back in its usual place
20:48  Ines — a short break in the kitchen
20:57  Priya finishes evening TV
          blanket_shared → coffee_table_l1: left where it was used
          glasses_priya → desk_b1: put back in its usual place; nightstand_b1 was full, so it went to desk_b1
          mug_priya → sink_k1: used, so it goes in the sink
20:57  Priya — a short break in the kitchen
21:02  Ines — evening TV in the living (bout 2/2) [shifted by late_work:resident_2]; brings remote_shared from tv_stand_l1, mug_ines from dish_rack_k1, glasses_ines from desk_b1
21:11  Priya — evening TV in the living (bout 2/2); brings mug_priya from sink_k1, glasses_priya from desk_b1
21:18  Ines finishes evening TV
          blanket_shared → armchair_l1: left where it was used; coffee_table_l1 was full, so it went to armchair_l1
          glasses_ines → desk_b1: left where it was used; coffee_table_l1 was full, so it went to desk_b1
          mug_ines → sink_k1: used, so it goes in the sink
          phone_ines → coffee_table_l1: left where it was used
          remote_shared → bookshelf_l1: left where it was used; coffee_table_l1 was full, so it went to bookshelf_l1
21:31  Priya finishes evening TV
          blanket_shared → couch_l1: put back in its usual place
          mug_priya → sink_k1: used, so it goes in the sink
          remote_shared → tv_stand_l1: put back in its usual place
21:47  Priya — reading in the bedroom_1; brings book_priya from nightstand_b1, glasses_priya from coffee_table_l1
22:17  Priya finishes reading
          glasses_priya → nightstand_b1: put back in its usual place
          phone_priya → coffee_table_l1: put back in its usual place; nightstand_b1 was full, so it went to coffee_table_l1
22:41  Priya — bed in the bedroom_1
22:48  Ines — bed in the bedroom_1
```

## Day 1 — Thursday

**Active causes**

- `late_work:resident_1` (Priya): A long day at work; home two hours late. gets home late and hurried; the evening walk and cooking are dropped and things are dumped at the door.
- `late_work:resident_2` (Ines): A long day at work; home two hours late. gets home late and hurried; the evening walk and cooking are dropped and things are dumped at the door.
- `low_energy:resident_2`: Ines has low energy (0.06): leaves things where they were used instead of putting them back.
- `running_late:resident_2`: Ines is running late all day (0.74): rushed putdowns, things dumped at the door, more whim.

Internal states (0–1): Priya energy 0.60, hurriedness 0.15, distraction 0.34; Ines energy 0.06, hurriedness 0.74, distraction 0.24

**Timeline**

```
06:59  Ines — morning routine in the bathroom; brings phone_ines from coffee_table_l1, glasses_ines from desk_b1
07:17  Priya — morning routine in the bathroom; brings phone_priya from coffee_table_l1, glasses_priya from nightstand_b1
07:24  Ines — breakfast in the kitchen; brings mug_ines from sink_k1
07:42  Priya finishes morning routine
          glasses_priya → bedroom_floor_b1: WHIM — was heading for nightstand_b1 (put back in its usual place) but landed on bedroom_floor_b1 instead
07:49  Ines finishes breakfast
          mug_ines → sink_k1: used, so it goes in the sink
          keeps phone_ines for work
07:55  Priya — breakfast in the kitchen; brings mug_priya from sink_k1
08:06  Ines leaves for work (back 19:36); takes backpack_ines (with headphones_ines, laptop_ines), keys_ines, phone_ines, wallet_ines, jacket_ines, shoes_ines
08:13  Priya finishes breakfast
          mug_priya → sink_k1: used, so it goes in the sink
          keeps phone_priya for work
08:13  Priya leaves for work (back 19:43); takes handbag_priya (with charger_priya, laptop_priya, notebook_priya, water_bottle_priya), keys_priya, phone_priya, wallet_priya, jacket_priya, shoes_priya
19:36  Ines is back from work
          backpack_ines → entry_floor_e1: bag dumped by the door, home late [late_work:resident_2]
          headphones_ines → entry_floor_e1: stays in the backpack
          jacket_ines → couch_l1: jacket thrown over the couch, home late [late_work:resident_2]
          keys_ines → entry_table_e1: put away in its usual place after the trip
          laptop_ines → entry_floor_e1: stays in the backpack
          shoes_ines → entry_floor_e1: put away in its usual place after the trip
          wallet_ines → desk_b1: WHIM — was heading for nightstand_b1 (put away in its usual place after the trip) but landed on desk_b1 instead
          keeps phone_ines for dinner
19:36  Ines — dinner in the dining; brings water_bottle_ines from sink_k1
19:43  Priya is back from work
          handbag_priya → entry_floor_e1: bag dumped by the door, home late [late_work:resident_1]
          charger_priya → entry_floor_e1: stays in the handbag
          jacket_priya → couch_l1: jacket thrown over the couch, home late [late_work:resident_1]
          keys_priya → entry_table_e1: put away in its usual place after the trip
          laptop_priya → entry_floor_e1: stays in the handbag
          notebook_priya → entry_floor_e1: stays in the handbag
          shoes_priya → entry_floor_e1: put away in its usual place after the trip
          wallet_priya → nightstand_b1: put away in its usual place after the trip
          keeps phone_priya, water_bottle_priya for dinner
19:43  Priya — dinner in the dining; brings water_bottle_priya from ON_PERSON
20:16  Ines finishes dinner
          water_bottle_ines → sink_k1: used, so it goes in the sink
20:23  Priya — evening TV in the living [shifted by late_work:resident_1]; brings remote_shared from tv_stand_l1, blanket_shared from couch_l1, mug_priya from sink_k1, glasses_priya from bedroom_floor_b1
20:53  Ines — evening TV in the living (bout 1/2) [shifted by late_work:resident_2]; brings mug_ines from sink_k1, glasses_ines from bathroom_shelf_ba1
21:07  Ines finishes evening TV
          blanket_shared → couch_l1: put back in its usual place
          glasses_ines → desk_b1: left where it was used; coffee_table_l1 was full, so it went to desk_b1
          mug_ines → sink_k1: used, so it goes in the sink
21:07  Ines — a short break in the kitchen
21:11  Priya finishes evening TV
          mug_priya → sink_k1: used, so it goes in the sink
          phone_priya → nightstand_b1: put back in its usual place
          remote_shared → tv_stand_l1: put back in its usual place
21:21  Ines — evening TV in the living (bout 2/2) [shifted by late_work:resident_2]; brings remote_shared from tv_stand_l1, blanket_shared from couch_l1, mug_ines from sink_k1, glasses_ines from desk_b1
21:40  Ines finishes evening TV
          blanket_shared → couch_l1: put back in its usual place
          glasses_ines → nightstand_b1: put back in its usual place
          phone_ines → coffee_table_l1: left where it was used
          remote_shared → bookshelf_l1: WHIM — was heading for armchair_l1 (left where it was used, too tired to put it away; coffee_table_l1 was full, so it went to armchair_l1) but landed on bookshelf_l1 instead [low_energy:resident_2]
22:35  Ines — bed in the bedroom_1
22:40  Priya — bed in the bedroom_1
```

## Day 2 — Friday

**Active causes**

- `guest_visit` (household): Friends come over for the evening. the living room is tidied beforehand, dinner is late, and the couch is taken by guests all evening.
- `distracted:resident_1`: Priya is distracted (0.76): carries things into the next room absent-mindedly, more likely to forget pocket items.
- `running_late:resident_2`: Ines is running late all day (0.92): rushed putdowns, things dumped at the door, more whim.

Internal states (0–1): Priya energy 0.50, hurriedness 0.36, distraction 0.76; Ines energy 0.60, hurriedness 0.92, distraction 0.16

**Timeline**

```
06:37  Ines — morning routine in the bathroom; brings phone_ines from coffee_table_l1, glasses_ines from nightstand_b1
07:02  Ines finishes morning routine
          glasses_ines → nightstand_b1: put back in its usual place
07:21  Priya — morning routine in the bathroom; brings phone_priya from nightstand_b1, glasses_priya from coffee_table_l1
07:25  Ines — breakfast in the kitchen; brings mug_ines from coffee_table_l1
07:46  Priya finishes morning routine
          glasses_priya → desk_b1: WHIM — was heading for nightstand_b1 (put back in its usual place) but landed on desk_b1 instead
          keeps phone_priya for work
07:50  Ines finishes breakfast
          mug_ines → sink_k1: used, so it goes in the sink
          keeps phone_ines for work
08:14  Priya leaves for work (back 17:44); takes handbag_priya (with charger_priya, laptop_priya, notebook_priya, water_bottle_priya), keys_priya, phone_priya, wallet_priya, jacket_priya, shoes_priya
08:20  Ines leaves for work (back 17:50); takes backpack_ines (with headphones_ines, laptop_ines), keys_ines, phone_ines, wallet_ines, jacket_ines, shoes_ines
17:44  Priya is back from work
          handbag_priya → entry_hook_e1: put away in its usual place after the trip
          charger_priya → entry_hook_e1: stays in the handbag
          jacket_priya → entry_hook_e1: put away in its usual place after the trip
          keys_priya → entry_table_e1: put away in its usual place after the trip
          laptop_priya → entry_hook_e1: stays in the handbag
          notebook_priya → entry_hook_e1: stays in the handbag
          phone_priya → nightstand_b1: put away in its usual place after the trip
          shoes_priya → entry_floor_e1: put away in its usual place after the trip
          wallet_priya → entry_table_e1: dropped at the door instead of being put away
          water_bottle_priya → entry_hook_e1: stays in the handbag
17:44  Priya — tidying up in the living [because of guest_visit]
17:50  Ines is back from work
          backpack_ines → entry_floor_e1: dumped at the door, running late [running_late:resident_2]
          headphones_ines → entry_floor_e1: stays in the backpack
          jacket_ines → entry_hook_e1: put away in its usual place after the trip
          keys_ines → entry_table_e1: put away in its usual place after the trip
          laptop_ines → entry_floor_e1: stays in the backpack
          phone_ines → entry_table_e1: dropped at the door instead of being put away
          shoes_ines → entry_floor_e1: put away in its usual place after the trip
          wallet_ines → nightstand_b1: put away in its usual place after the trip
17:50  Ines — tidying up in the living [because of guest_visit]
18:14  Priya finishes tidying up
          backpack_ines (from entry_floor_e1) → entry_hook_e1: tidied away to its usual place [guest_visit]
          charger_priya (from entry_hook_e1) → desk_b1: tidied away to its usual place [guest_visit]
          headphones_ines (from entry_floor_e1) → desk_b1: tidied away to its usual place [guest_visit]
          laptop_ines (from entry_floor_e1) → desk_b1: cleared away before the guests [guest_visit]
          laptop_priya (from entry_hook_e1) → bookshelf_l1: cleared away before the guests; desk_b1 was full, so it went to bookshelf_l1 [guest_visit]
          mug_ines (from sink_k1) → counter_k1: WHIM — was heading for cupboard_k1 (tidied away to its usual place) but landed on counter_k1 instead [guest_visit]
          mug_priya (from sink_k1) → cupboard_k1: tidied away to its usual place [guest_visit]
          notebook_priya (from entry_hook_e1) → bookshelf_l1: tidied away to its usual place; desk_b1 was full, so it went to bookshelf_l1 [guest_visit]
          phone_ines (from entry_table_e1) → coffee_table_l1: tidied away to its usual place; nightstand_b1 was full, so it went to coffee_table_l1 [guest_visit]
          remote_shared (from bookshelf_l1) → couch_l1: WHIM — was heading for tv_stand_l1 (tidied away to its usual place) but landed on couch_l1 instead [guest_visit]
          wallet_priya (from entry_table_e1) → bed_b1: tidied away to its usual place; nightstand_b1 was full, so it went to bed_b1 [guest_visit]
          water_bottle_ines (from sink_k1) → counter_k1: WHIM — was heading for dish_rack_k1 (tidied away to its usual place) but landed on counter_k1 instead [guest_visit]
          water_bottle_priya (from entry_hook_e1) → dish_rack_k1: tidied away to its usual place [guest_visit]
18:14  Priya leaves for a walk (back 18:49); takes keys_priya, phone_priya, wallet_priya, jacket_priya, shoes_priya
18:20  Ines finishes tidying up
          mug_ines (from counter_k1) → kitchen_table_k1: WHIM — was heading for cupboard_k1 (tidied away to its usual place) but landed on kitchen_table_k1 instead [guest_visit]
          phone_ines (from coffee_table_l1) → nightstand_b1: tidied away to its usual place [guest_visit]
          remote_shared (from couch_l1) → tv_stand_l1: tidied away to its usual place [guest_visit]
          water_bottle_ines (from counter_k1) → dish_rack_k1: tidied away to its usual place [guest_visit]
18:49  Priya is back from a walk
          jacket_priya → entry_hook_e1: put away in its usual place after the trip
          keys_priya → entry_table_e1: put away in its usual place after the trip
          shoes_priya → entry_floor_e1: put away in its usual place after the trip
          wallet_priya → entry_table_e1: dropped at the door instead of being put away
          keeps phone_priya for cooking dinner
19:02  Ines leaves for a walk (back 19:37); takes keys_ines, phone_ines, wallet_ines, jacket_ines, shoes_ines, headphones_ines
19:36  Priya — cooking dinner in the kitchen [shifted by guest_visit]
19:37  Ines is back from a walk
          headphones_ines → entry_table_e1: dropped at the door instead of being put away
          jacket_ines → entry_hook_e1: put away in its usual place after the trip
          keys_ines → entry_table_e1: put away in its usual place after the trip
          shoes_ines → entry_floor_e1: put away in its usual place after the trip
          wallet_ines → nightstand_b1: put away in its usual place after the trip
          keeps phone_ines for cooking dinner
19:37  Ines — cooking dinner in the kitchen [shifted by guest_visit]
20:11  Priya — dinner in the dining [shifted by guest_visit]; brings water_bottle_priya from dish_rack_k1
20:12  Ines — dinner in the dining [shifted by guest_visit]; brings water_bottle_ines from dish_rack_k1
20:51  Priya finishes dinner
          water_bottle_priya → sink_k1: used, so it goes in the sink
20:51  Priya — hosting the guests in the living [because of guest_visit]; brings mug_priya from cupboard_k1
20:52  Ines — hosting the guests in the living [because of guest_visit]; brings mug_ines from kitchen_table_k1
22:51  Priya finishes hosting the guests
          mug_priya → sink_k1: mugs collected into the sink after the guests [guest_visit]
          phone_priya → bedroom_floor_b1: WHIM — was heading for nightstand_b1 (put back in its usual place) but landed on bedroom_floor_b1 instead [guest_visit]
22:52  Ines finishes hosting the guests
          mug_ines → sink_k1: mugs collected into the sink after the guests [guest_visit]
          phone_ines → nightstand_b1: put back in its usual place [guest_visit]
22:55  Priya — bed in the bedroom_1
22:56  Ines — bed in the bedroom_1
```

## Day 3 — Saturday

**Active causes**

- `laundry_day` (household): Laundry day. the laundry basket travels, towels and the blanket get washed and end up airing in the bedroom rather than where they live.
- `sick_day:resident_1` (Priya): Off sick, resting on the couch all day. no work or trips out; laptop, mug, medication, book and blanket all migrate to the couch and coffee table.
- `low_energy:resident_1`: Priya has low energy (0.17): leaves things where they were used instead of putting them back.
- `running_late:resident_2`: Ines is running late all day (0.85): rushed putdowns, things dumped at the door, more whim.

Internal states (0–1): Priya energy 0.17, hurriedness 0.00, distraction 0.60; Ines energy 0.36, hurriedness 0.85, distraction 0.29

**Timeline**

```
08:32  Priya — morning routine in the bathroom; brings phone_priya from bedroom_floor_b1, glasses_priya from desk_b1
08:40  Ines — morning routine in the bathroom; brings phone_ines from nightstand_b1, glasses_ines from nightstand_b1
08:57  Priya — breakfast in the kitchen; brings mug_priya from sink_k1
09:05  Ines finishes morning routine
          glasses_ines → nightstand_b1: put back in its usual place
09:16  Ines — breakfast in the kitchen; brings mug_ines from sink_k1
09:51  Ines finishes breakfast
          keeps phone_ines for errands
10:22  Priya — resting on the couch in the living (bout 1/2) [because of sick_day:resident_1]; brings laptop_priya from bookshelf_l1, charger_priya from desk_b1, glasses_priya from bathroom_shelf_ba1, mug_priya from kitchen_table_k1, medication_priya from medicine_cabinet_ba1, book_priya from bed_b1, blanket_shared from couch_l1, water_bottle_priya from sink_k1
10:38  Priya finishes resting on the couch
          blanket_shared → couch_l1: blanket stays on the couch [sick_day:resident_1]
          book_priya → couch_l1: book dropped on the couch [sick_day:resident_1]
          charger_priya → nightstand_b1: charger stays plugged in by the couch; coffee_table_l1 was full, so it went to nightstand_b1 [sick_day:resident_1]
          glasses_priya → desk_b1: glasses left on the coffee table; coffee_table_l1 was full, so it went to desk_b1 [sick_day:resident_1]
          laptop_priya → bookshelf_l1: left on the coffee table between naps; coffee_table_l1 was full, so it went to bookshelf_l1 [sick_day:resident_1]
          water_bottle_priya → sink_k1: used, so it goes in the sink [sick_day:resident_1]
10:38  Priya — a short break in the kitchen [because of sick_day:resident_1]
11:50  Priya — resting on the couch in the living (bout 2/2) [because of sick_day:resident_1]; brings laptop_priya from bookshelf_l1, charger_priya from nightstand_b1, glasses_priya from desk_b1, book_priya from couch_l1, blanket_shared from couch_l1, water_bottle_priya from sink_k1
12:44  Ines leaves for errands (back 14:44); takes backpack_ines, keys_ines, phone_ines, wallet_ines, jacket_ines, shoes_ines
14:44  Ines is back from errands
          backpack_ines → entry_floor_e1: dropped at the door instead of being put away
          jacket_ines → entry_hook_e1: put away in its usual place after the trip
          keys_ines → entry_table_e1: put away in its usual place after the trip
          shoes_ines → entry_floor_e1: put away in its usual place after the trip
          wallet_ines → nightstand_b1: put away in its usual place after the trip
          keeps phone_ines for lunch
14:44  Ines — lunch in the kitchen
15:24  Ines — reading in the bedroom_1; brings book_ines from nightstand_b1, glasses_ines from nightstand_b1
16:24  Ines finishes reading
          book_ines → nightstand_b1: put back in its usual place
          glasses_ines → nightstand_b1: put back in its usual place
17:09  Priya finishes resting on the couch
          book_priya → couch_l1: book dropped on the couch [sick_day:resident_1]
          charger_priya → nightstand_b1: charger stays plugged in by the couch; coffee_table_l1 was full, so it went to nightstand_b1 [sick_day:resident_1]
          glasses_priya → desk_b1: glasses left on the coffee table; coffee_table_l1 was full, so it went to desk_b1 [sick_day:resident_1]
          laptop_priya → bookshelf_l1: left on the coffee table between naps; coffee_table_l1 was full, so it went to bookshelf_l1 [sick_day:resident_1]
          medication_priya → armchair_l1: medication kept within reach; coffee_table_l1 was full, so it went to armchair_l1 [sick_day:resident_1]
          water_bottle_priya → couch_l1: WHIM — was heading for coffee_table_l1 (left where it was used) but landed on couch_l1 instead [sick_day:resident_1]
18:22  Priya — laundry in the bathroom (bout 1/3) [because of laundry_day]; brings towel_priya from towel_rack_ba1, blanket_shared from coffee_table_l1
18:34  Priya finishes laundry
          blanket_shared → bed_b1: washed blanket airing on the bed [laundry_day]
          laundry_basket_shared → bedroom_floor_b1: basket left in the bedroom while things dry [laundry_day]
          towel_priya → bed_b1: clean towel folded on the bed [laundry_day]
18:34  Priya — a short break in the kitchen [because of laundry_day]
18:44  Priya — laundry in the bathroom (bout 2/3) [because of laundry_day]; brings laundry_basket_shared from bedroom_floor_b1, towel_priya from bed_b1, blanket_shared from bed_b1
18:56  Priya finishes laundry
          blanket_shared → wardrobe_b1: WHIM — was heading for bed_b1 (washed blanket airing on the bed) but landed on wardrobe_b1 instead [laundry_day]
          laundry_basket_shared → bedroom_floor_b1: basket left in the bedroom while things dry [laundry_day]
          towel_priya → bed_b1: clean towel folded on the bed [laundry_day]
18:56  Priya — a short break in the kitchen [because of laundry_day]
18:58  Ines — cooking dinner in the kitchen
19:06  Priya — laundry in the bathroom (bout 3/3) [because of laundry_day]; brings laundry_basket_shared from bedroom_floor_b1, towel_priya from bed_b1, blanket_shared from wardrobe_b1
19:38  Ines — dinner in the dining
19:40  Priya finishes laundry
          blanket_shared → bed_b1: washed blanket airing on the bed [laundry_day]
          laundry_basket_shared → bedroom_floor_b1: basket left in the bedroom while things dry [laundry_day]
          towel_priya → bed_b1: clean towel folded on the bed [laundry_day]
19:52  Priya — reading in the bedroom_1; brings book_priya from couch_l1, glasses_priya from desk_b1
20:23  Ines — evening TV in the living (bout 1/2); brings remote_shared from tv_stand_l1, blanket_shared from bed_b1, mug_ines from kitchen_table_k1, glasses_ines from nightstand_b1
20:49  Ines finishes evening TV
          blanket_shared → armchair_l1: left where it was used; coffee_table_l1 was full, so it went to armchair_l1
          glasses_ines → bedroom_floor_b1: WHIM — was heading for nightstand_b1 (put back in its usual place) but landed on bedroom_floor_b1 instead
          mug_ines → sink_k1: used, so it goes in the sink
          remote_shared → tv_stand_l1: put back in its usual place
20:49  Ines — a short break in the kitchen
20:52  Priya finishes reading
          book_priya → nightstand_b1: put back in its usual place
          glasses_priya → desk_b1: put back in its usual place; nightstand_b1 was full, so it went to desk_b1
20:52  Priya — cooking dinner in the kitchen
21:22  Ines — evening TV in the living (bout 2/2); brings remote_shared from tv_stand_l1, blanket_shared from armchair_l1, mug_ines from sink_k1, glasses_ines from bedroom_floor_b1
21:32  Priya — dinner in the dining; brings water_bottle_priya from couch_l1
22:12  Ines finishes evening TV
          blanket_shared → armchair_l1: WHIM — was heading for couch_l1 (put back in its usual place) but landed on armchair_l1 instead
          glasses_ines → desk_b1: put back in its usual place; nightstand_b1 was full, so it went to desk_b1
          mug_ines → counter_k1: WHIM — was heading for sink_k1 (used, so it goes in the sink) but landed on counter_k1 instead
          phone_ines → coffee_table_l1: put back in its usual place; nightstand_b1 was full, so it went to coffee_table_l1
          remote_shared → tv_stand_l1: put back in its usual place
22:17  Priya finishes dinner
          water_bottle_priya → sink_k1: used, so it goes in the sink
22:17  Priya — evening TV in the living; brings remote_shared from tv_stand_l1, blanket_shared from armchair_l1, glasses_priya from desk_b1
22:48  Ines — bed in the bedroom_1
23:59  Priya finishes evening TV
          blanket_shared → armchair_l1: left where it was used; coffee_table_l1 was full, so it went to armchair_l1
          glasses_priya → desk_b1: put back in its usual place; nightstand_b1 was full, so it went to desk_b1
          mug_priya → sink_k1: used, so it goes in the sink
          phone_priya → coffee_table_l1: put back in its usual place; nightstand_b1 was full, so it went to coffee_table_l1
          remote_shared → tv_stand_l1: put back in its usual place
```

## Day 4 — Sunday

**Active causes**

- `grocery_delivery` (household): A grocery delivery arrives in the early evening. someone unpacks groceries; the kitchen counter is covered with bags, so things that would go there land on the table instead.
- `low_energy:resident_2`: Ines has low energy (0.15): leaves things where they were used instead of putting them back.
- `running_late:resident_2`: Ines is running late all day (0.83): rushed putdowns, things dumped at the door, more whim.

Internal states (0–1): Priya energy 0.37, hurriedness 0.29, distraction 0.26; Ines energy 0.15, hurriedness 0.83, distraction 0.10

**Timeline**

```
08:22  Priya — morning routine in the bathroom; brings phone_priya from coffee_table_l1, glasses_priya from desk_b1
08:47  Priya finishes morning routine
          glasses_priya → desk_b1: put back in its usual place; nightstand_b1 was full, so it went to desk_b1
09:20  Ines — morning routine in the bathroom; brings phone_ines from coffee_table_l1, glasses_ines from desk_b1
09:38  Priya — breakfast in the kitchen; brings mug_priya from sink_k1
09:45  Ines finishes morning routine
          glasses_ines → desk_b1: put back in its usual place; nightstand_b1 was full, so it went to desk_b1
09:45  Ines — breakfast in the kitchen; brings mug_ines from counter_k1
10:20  Ines — chores in the kitchen (bout 1/4)
10:30  Ines finishes chores
          water_bottle_priya (from sink_k1) → dish_rack_k1: counter full of shopping; bottle put on the dish rack [grocery_delivery]
10:30  Ines — a short break in the kitchen
10:32  Priya — chores in the kitchen (bout 1/4)
10:40  Ines — chores in the kitchen (bout 2/4)
10:43  Priya finishes chores
          mug_priya (from kitchen_table_k1) → counter_k1: WHIM — was heading for kitchen_table_k1 (counter full of shopping; mug left on the table) but landed on counter_k1 instead [grocery_delivery]
10:43  Priya — a short break in the kitchen
10:53  Priya — chores in the kitchen (bout 2/4)
10:58  Ines finishes chores
          mug_priya (from counter_k1) → kitchen_table_k1: counter full of shopping; mug left on the table [grocery_delivery]
10:58  Ines — a short break in the kitchen
11:08  Priya finishes chores
          mug_ines (from kitchen_table_k1) → sink_k1: WHIM — was heading for kitchen_table_k1 (counter full of shopping; mug left on the table) but landed on sink_k1 instead [grocery_delivery]
11:08  Priya — a short break in the kitchen
11:08  Ines — chores in the kitchen (bout 3/4)
11:18  Ines finishes chores
          mug_ines (from sink_k1) → cupboard_k1: WHIM — was heading for kitchen_table_k1 (counter full of shopping; mug left on the table) but landed on cupboard_k1 instead [grocery_delivery]
11:18  Priya — chores in the kitchen (bout 3/4)
11:18  Ines — a short break in the kitchen
11:28  Ines — chores in the kitchen (bout 4/4)
11:30  Priya — a short break in the kitchen
11:40  Ines finishes chores
          keeps phone_ines for errands
11:40  Priya — chores in the kitchen (bout 4/4)
13:55  Priya — lunch in the kitchen
15:58  Priya — reading in the bedroom_1; brings book_priya from nightstand_b1, glasses_priya from desk_b1
16:56  Ines leaves for errands (back 18:56); takes backpack_ines, keys_ines, phone_ines, wallet_ines, jacket_ines, shoes_ines
16:58  Priya finishes reading
          book_priya → nightstand_b1: put back in its usual place
          glasses_priya → nightstand_b1: put back in its usual place
          keeps phone_priya for the gym
16:58  Priya leaves for the gym (back 18:18); takes keys_priya, phone_priya, wallet_priya, jacket_priya, shoes_priya
18:18  Priya is back from the gym
          jacket_priya → entry_hook_e1: put away in its usual place after the trip
          keys_priya → entry_table_e1: put away in its usual place after the trip
          phone_priya → coffee_table_l1: put away in its usual place after the trip; nightstand_b1 was full, so it went to coffee_table_l1
          shoes_priya → entry_floor_e1: put away in its usual place after the trip
          wallet_priya → desk_b1: put away in its usual place after the trip; nightstand_b1 was full, so it went to desk_b1
18:28  Priya — unpacking groceries in the kitchen [because of grocery_delivery]; brings water_bottle_priya from dish_rack_k1
18:56  Ines is back from errands
          backpack_ines → entry_floor_e1: dumped at the door, running late [running_late:resident_2]
          jacket_ines → entry_hook_e1: put away in its usual place after the trip
          keys_ines → entry_table_e1: put away in its usual place after the trip
          shoes_ines → entry_floor_e1: put away in its usual place after the trip
          wallet_ines → bed_b1: WHIM — was heading for desk_b1 (put away in its usual place after the trip; nightstand_b1 was full, so it went to desk_b1) but landed on bed_b1 instead
          keeps phone_ines for lunch
18:56  Ines — lunch in the kitchen
18:58  Priya finishes unpacking groceries
          water_bottle_priya → dish_rack_k1: counter full of shopping; bottle put on the dish rack [grocery_delivery]
18:58  Priya — cooking dinner in the kitchen [shifted by grocery_delivery]; brings phone_priya from coffee_table_l1
19:36  Ines — reading in the bedroom_1; brings book_ines from nightstand_b1, glasses_ines from desk_b1
20:00  Priya — dinner in the dining [shifted by grocery_delivery]; brings water_bottle_priya from dish_rack_k1
20:36  Ines finishes reading
          book_ines → nightstand_b1: put back in its usual place
          glasses_ines → desk_b1: left where it was used; bed_b1 was full, so it went to desk_b1
          keeps phone_ines for the gym
20:36  Ines leaves for the gym (back 21:56); takes phone_ines, jacket_ines, shoes_ines; never takes keys_ines, wallet_ines on the gym
20:45  Priya finishes dinner
          water_bottle_priya → dish_rack_k1: counter full of shopping; bottle put on the dish rack [grocery_delivery]
20:45  Priya — evening TV in the living; brings remote_shared from tv_stand_l1, blanket_shared from armchair_l1, mug_priya from kitchen_table_k1, glasses_priya from nightstand_b1
21:56  Ines is back from the gym
          jacket_ines → entry_hook_e1: put away in its usual place after the trip
          shoes_ines → entry_floor_e1: put away in its usual place after the trip
          keeps phone_ines for cooking dinner
21:56  Ines — cooking dinner in the kitchen [shifted by grocery_delivery]
22:35  Priya finishes evening TV
          blanket_shared → couch_l1: put back in its usual place
          glasses_priya → bedroom_floor_b1: WHIM — was heading for nightstand_b1 (put back in its usual place) but landed on bedroom_floor_b1 instead
          mug_priya → kitchen_table_k1: counter full of shopping; mug left on the table [grocery_delivery]
          phone_priya → nightstand_b1: put back in its usual place
          remote_shared → bookshelf_l1: WHIM — was heading for tv_stand_l1 (put back in its usual place) but landed on bookshelf_l1 instead
22:36  Ines — dinner in the dining [shifted by grocery_delivery]
23:21  Ines finishes dinner
          water_bottle_ines → dish_rack_k1: counter full of shopping; bottle put on the dish rack [grocery_delivery]
23:21  Ines — evening TV in the living (bout 1/2); brings remote_shared from bookshelf_l1, blanket_shared from couch_l1, mug_ines from cupboard_k1, glasses_ines from desk_b1
23:22  Priya — bed in the bedroom_1
23:31  Ines finishes evening TV
          blanket_shared → armchair_l1: left where it was used; coffee_table_l1 was full, so it went to armchair_l1
          mug_ines → kitchen_table_k1: counter full of shopping; mug left on the table [grocery_delivery]
          remote_shared → tv_stand_l1: put back in its usual place
23:31  Ines — a short break in the kitchen
23:42  Ines — evening TV in the living (bout 2/2); brings remote_shared from tv_stand_l1, blanket_shared from armchair_l1, mug_ines from kitchen_table_k1
23:59  Ines finishes evening TV
          blanket_shared → couch_l1: put back in its usual place
          glasses_ines → bed_b1: WHIM — was heading for desk_b1 (put back in its usual place; nightstand_b1 was full, so it went to desk_b1) but landed on bed_b1 instead
          mug_ines → kitchen_table_k1: counter full of shopping; mug left on the table [grocery_delivery]
          phone_ines → bookshelf_l1: WHIM — was heading for coffee_table_l1 (left where it was used) but landed on bookshelf_l1 instead
          remote_shared → tv_stand_l1: put back in its usual place
```
