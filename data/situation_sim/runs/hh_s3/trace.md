# Household hh_s3 — five days, Wednesday to Sunday

Seed-generated household. Times are clock times; ids are the receptacle and object ids used in events.jsonl. A line indented under an activity says where an object went when the activity ended and why. WHIM marks a placement that landed somewhere other than where the decision was heading. Text in [brackets] names the hidden cause the decision is attributed to.

## Household

Type: flatmates. Rooms: bathroom, bedroom_1, bedroom_2, bedroom_3, dining, entry, kitchen, living.

Residents:

- **Ines** (resident_1): retired; very tidy (tidiness 0.94); average timing (jitter scale 1.14); sometimes forgets pocket items; mood barely affects behaviour (sensitivity 0.40); sleeps in bedroom_1, works at the bedroom_1 desk
- **Sam** (resident_2): works outside the home; very tidy (tidiness 0.76); punctual (jitter scale 0.50); sometimes forgets pocket items; mood moderately affects behaviour (sensitivity 0.67); sleeps in bedroom_2, works at the bedroom_2 desk
- **Aisha** (resident_3): works outside the home; fairly tidy (tidiness 0.52); average timing (jitter scale 1.15); rarely forgets pocket items; mood moderately affects behaviour (sensitivity 0.53); sleeps in bedroom_3, works at the bedroom_3 desk

Objects and their usual place (primary slot first):

- Ines's: book_ines → nightstand_b1 / bookshelf_l1; glasses_ines → nightstand_b1 / desk_b1; headphones_ines → desk_b1 / nightstand_b1; jacket_ines → entry_hook_e1 / wardrobe_b1; keys_ines → entry_table_e1 / nightstand_b1; mug_ines → cupboard_k1 / dish_rack_k1 / sink_k1; phone_ines → nightstand_b1 / coffee_table_l1; shoes_ines → entry_floor_e1 / wardrobe_b1; towel_ines → towel_rack_ba1 / bathroom_shelf_ba1; umbrella_ines → entry_floor_e1 / entry_hook_e1; wallet_ines → nightstand_b1 / desk_b1; water_bottle_ines → dish_rack_k1 / counter_k1 / sink_k1
- Sam's: book_sam → nightstand_b2 / bookshelf_l1; charger_sam → desk_b2 / nightstand_b2; handbag_sam → entry_hook_e1 / bedroom_floor_b2 / desk_b2; headphones_sam → desk_b2 / nightstand_b2; jacket_sam → entry_hook_e1 / wardrobe_b2; keys_sam → entry_table_e1 / nightstand_b2; laptop_sam → desk_b2 / bookshelf_l1; mug_sam → cupboard_k1 / dish_rack_k1 / sink_k1; notebook_sam → desk_b2 / bookshelf_l1; phone_sam → nightstand_b2 / coffee_table_l1; shoes_sam → entry_floor_e1 / wardrobe_b2; towel_sam → towel_rack_ba1 / bathroom_shelf_ba1; wallet_sam → nightstand_b2 / desk_b2; water_bottle_sam → dish_rack_k1 / counter_k1 / sink_k1
- Aisha's: backpack_aisha → entry_hook_e1 / bedroom_floor_b3 / desk_b3; book_aisha → nightstand_b3 / bookshelf_l1; glasses_aisha → nightstand_b3 / desk_b3; headphones_aisha → desk_b3 / nightstand_b3; jacket_aisha → entry_hook_e1 / wardrobe_b3; keys_aisha → entry_table_e1 / nightstand_b3; laptop_aisha → desk_b3 / bookshelf_l1; lunchbox_aisha → cupboard_k1 / counter_k1 / sink_k1; mug_aisha → cupboard_k1 / dish_rack_k1 / sink_k1; notebook_aisha → desk_b3 / bookshelf_l1; phone_aisha → nightstand_b3 / coffee_table_l1; shoes_aisha → entry_floor_e1 / wardrobe_b3; towel_aisha → towel_rack_ba1 / bathroom_shelf_ba1; umbrella_aisha → entry_floor_e1 / entry_hook_e1; wallet_aisha → nightstand_b3 / desk_b3
- Shared: blanket_shared → couch_l1 / armchair_l1; laundry_basket_shared → bathroom_shelf_ba1 / bedroom_floor_b1; remote_shared → tv_stand_l1 / coffee_table_l1

Object groups (things that travel together):

- backpack_aisha carries laptop_aisha on trips to work and errands
- handbag_sam carries charger_sam, laptop_sam, notebook_sam on trips to work and errands


## Day 0 — Wednesday

**Active causes**

- `late_work:resident_2` (Sam): A long day at work; home two hours late. gets home late and hurried; the evening walk and cooking are dropped and things are dumped at the door.
- `rain` (household): It rains for most of the day. no walk; wet shoes, jackets and umbrellas get dropped at the entry instead of being put away.
- `low_energy:resident_2`: Sam has low energy (0.00): leaves things where they were used instead of putting them back.
- `running_late:resident_2`: Sam is running late all day (0.69): rushed putdowns, things dumped at the door, more whim.

Internal states (0–1): Ines energy 0.36, hurriedness 0.39, distraction 0.27; Sam energy 0.00, hurriedness 0.69, distraction 0.20; Aisha energy 0.49, hurriedness 0.33, distraction 0.51

**Timeline**

```
06:47  Sam — morning routine in the bathroom; brings phone_sam from nightstand_b2
07:12  Sam — breakfast in the kitchen; brings mug_sam from cupboard_k1
07:33  Ines — morning routine in the bathroom; brings phone_ines from nightstand_b1, glasses_ines from nightstand_b1
07:37  Sam finishes breakfast
          mug_sam → counter_k1: WHIM — was heading for sink_k1 (used, so it goes in the sink) but landed on counter_k1 instead
          keeps phone_sam for work
07:39  Aisha — morning routine in the bathroom; brings phone_aisha from nightstand_b3, glasses_aisha from nightstand_b3
08:03  Ines finishes morning routine
          glasses_ines → nightstand_b1: put back in its usual place
08:03  Ines — breakfast in the kitchen; brings mug_ines from cupboard_k1
08:04  Aisha finishes morning routine
          keeps phone_aisha for work
08:14  Sam leaves for work (back 19:44); takes handbag_sam (with charger_sam, laptop_sam, notebook_sam), keys_sam, wallet_sam, jacket_sam, shoes_sam; never takes phone_sam on work
08:14  Aisha leaves for work (back 17:44); takes backpack_aisha (with laptop_aisha), keys_aisha, phone_aisha, wallet_aisha, jacket_aisha, shoes_aisha, umbrella_aisha
08:43  Ines finishes breakfast
          mug_ines → sink_k1: used, so it goes in the sink
12:09  Ines — lunch in the kitchen
12:54  Ines — reading in the bedroom_1; brings book_ines from nightstand_b1, glasses_ines from nightstand_b1
14:09  Ines finishes reading
          book_ines → nightstand_b1: put back in its usual place
          glasses_ines → nightstand_b1: put back in its usual place
17:11  Ines — cooking dinner in the kitchen
17:44  Aisha is back from work
          backpack_aisha → entry_floor_e1: wet bag left by the door [rain]
          jacket_aisha → entry_hook_e1: wet jacket hung on the hook [rain]
          keys_aisha → entry_table_e1: put away in its usual place after the trip
          laptop_aisha → entry_floor_e1: stays in the backpack
          shoes_aisha → entry_floor_e1: wet shoes left on the entry floor to dry [rain]
          umbrella_aisha → entry_floor_e1: wet umbrella propped by the door [rain]
          wallet_aisha → nightstand_b3: put away in its usual place after the trip
          keeps phone_aisha for cooking dinner
18:11  Aisha — cooking dinner in the kitchen
18:44  Ines — dinner in the dining; brings water_bottle_ines from dish_rack_k1
19:24  Aisha — dinner in the dining
19:29  Ines finishes dinner
          water_bottle_ines → sink_k1: used, so it goes in the sink
19:44  Sam is back from work
          handbag_sam → entry_floor_e1: bag dumped by the door, home late [late_work:resident_2]
          charger_sam → entry_floor_e1: stays in the handbag
          jacket_sam → armchair_l1: WHIM — was heading for couch_l1 (jacket thrown over the couch, home late) but landed on armchair_l1 instead [late_work:resident_2]
          keys_sam → entry_table_e1: put away in its usual place after the trip
          laptop_sam → entry_floor_e1: stays in the handbag
          notebook_sam → entry_floor_e1: stays in the handbag
          shoes_sam → wardrobe_b2: wet shoes left on the entry floor to dry; entry_floor_e1 was full, so it went to wardrobe_b2 [rain]
          wallet_sam → bed_b2: WHIM — was heading for nightstand_b2 (put away in its usual place after the trip) but landed on bed_b2 instead
19:44  Sam — dinner in the dining; brings water_bottle_sam from dish_rack_k1
20:24  Sam finishes dinner
          water_bottle_sam → dish_rack_k1: WHIM — was heading for sink_k1 (used, so it goes in the sink) but landed on dish_rack_k1 instead
20:35  Ines — evening TV in the living (bout 1/4); brings remote_shared from tv_stand_l1, blanket_shared from couch_l1, mug_ines from sink_k1, glasses_ines from nightstand_b1
20:45  Ines finishes evening TV
          blanket_shared → couch_l1: put back in its usual place
          glasses_ines → nightstand_b1: put back in its usual place
          mug_ines → sink_k1: used, so it goes in the sink
          remote_shared → tv_stand_l1: put back in its usual place
20:45  Ines — a short break in the kitchen
20:54  Aisha — evening TV in the living (bout 1/2); brings remote_shared from tv_stand_l1, blanket_shared from couch_l1, mug_aisha from cupboard_k1, glasses_aisha from bathroom_shelf_ba1
20:57  Ines — evening TV in the living (bout 2/4); brings mug_ines from sink_k1, glasses_ines from nightstand_b1
21:17  Sam — evening TV in the living [shifted by late_work:resident_2]; brings mug_sam from counter_k1
21:35  Ines finishes evening TV
          blanket_shared → couch_l1: put back in its usual place
          glasses_ines → nightstand_b1: put back in its usual place
          mug_ines → sink_k1: used, so it goes in the sink
          remote_shared → tv_stand_l1: put back in its usual place
21:35  Ines — a short break in the kitchen
21:47  Aisha finishes evening TV
          glasses_aisha → nightstand_b3: put back in its usual place
          mug_aisha → sink_k1: used, so it goes in the sink
          remote_shared → coffee_table_l1: left where it was used
21:47  Ines — evening TV in the living (bout 3/4); brings blanket_shared from couch_l1, mug_ines from sink_k1, glasses_ines from nightstand_b1
21:47  Aisha — a short break in the kitchen
22:01  Aisha — evening TV in the living (bout 2/2); brings mug_aisha from sink_k1, glasses_aisha from nightstand_b3
22:03  Ines finishes evening TV
          blanket_shared → couch_l1: put back in its usual place
          glasses_ines → nightstand_b1: put back in its usual place
          mug_ines → sink_k1: used, so it goes in the sink
          remote_shared → tv_stand_l1: put back in its usual place
22:03  Ines — a short break in the kitchen
22:05  Sam finishes evening TV
          mug_sam → sink_k1: used, so it goes in the sink
          phone_sam → coffee_table_l1: left where it was used
          remote_shared → coffee_table_l1: WHIM — was heading for tv_stand_l1 (put back in its usual place) but landed on coffee_table_l1 instead
22:11  Aisha finishes evening TV
          mug_aisha → sink_k1: used, so it goes in the sink
          remote_shared → bookshelf_l1: WHIM — was heading for coffee_table_l1 (left where it was used) but landed on bookshelf_l1 instead
22:15  Ines — evening TV in the living (bout 4/4); brings remote_shared from bookshelf_l1, blanket_shared from couch_l1, mug_ines from sink_k1, glasses_ines from nightstand_b1
22:28  Sam — bed in the bedroom_2
22:29  Aisha — reading in the bedroom_3; brings book_aisha from nightstand_b3, glasses_aisha from coffee_table_l1
22:35  Ines finishes evening TV
          blanket_shared → couch_l1: put back in its usual place
          glasses_ines → nightstand_b1: put back in its usual place
          mug_ines → sink_k1: used, so it goes in the sink
          phone_ines → nightstand_b1: put back in its usual place
          remote_shared → tv_stand_l1: put back in its usual place
22:35  Ines — bed in the bedroom_1
22:59  Aisha finishes reading
          phone_aisha → bed_b3: left where it was used
22:59  Aisha — bed in the bedroom_3
```

## Day 1 — Thursday

**Active causes**

- `sick_day:resident_2` (Sam): Off sick, resting on the couch all day. no work or trips out; laptop, mug, medication, book and blanket all migrate to the couch and coffee table.
- `distracted:resident_2`: Sam is distracted (0.72): carries things into the next room absent-mindedly, more likely to forget pocket items.
- `low_energy:resident_1`: Ines has low energy (0.30): leaves things where they were used instead of putting them back.
- `low_energy:resident_2`: Sam has low energy (0.00): leaves things where they were used instead of putting them back.

Internal states (0–1): Ines energy 0.30, hurriedness 0.09, distraction 0.21; Sam energy 0.00, hurriedness 0.13, distraction 0.72; Aisha energy 0.30, hurriedness 0.60, distraction 0.27

**Timeline**

```
06:31  Aisha — morning routine in the bathroom; brings phone_aisha from bed_b3, glasses_aisha from bed_b3
06:56  Aisha finishes morning routine
          glasses_aisha → nightstand_b3: put back in its usual place
07:16  Sam — morning routine in the bathroom; brings phone_sam from coffee_table_l1
07:33  Ines — morning routine in the bathroom; brings phone_ines from nightstand_b1, glasses_ines from nightstand_b1
07:41  Sam — breakfast in the kitchen; brings mug_sam from sink_k1
07:50  Aisha — breakfast in the kitchen; brings mug_aisha from sink_k1
08:03  Ines finishes morning routine
          glasses_ines → nightstand_b1: put back in its usual place
08:03  Ines — breakfast in the kitchen; brings mug_ines from sink_k1
08:15  Aisha finishes breakfast
          mug_aisha → counter_k1: WHIM — was heading for sink_k1 (used, so it goes in the sink) but landed on counter_k1 instead
          keeps phone_aisha for work
08:16  Aisha leaves for work (back 17:46); takes backpack_aisha (with laptop_aisha), keys_aisha, phone_aisha, wallet_aisha, jacket_aisha, shoes_aisha
08:43  Ines finishes breakfast
          mug_ines → sink_k1: WHIM — was heading for kitchen_table_k1 (left where it was used, too tired to put it away) but landed on sink_k1 instead [low_energy:resident_1]
09:39  Sam — resting on the couch in the living (bout 1/4) [because of sick_day:resident_2]; brings laptop_sam from entry_floor_e1, charger_sam from entry_floor_e1, headphones_sam from desk_b2, mug_sam from kitchen_table_k1, book_sam from nightstand_b2, blanket_shared from couch_l1, water_bottle_sam from dish_rack_k1
10:04  Sam finishes resting on the couch
          blanket_shared → couch_l1: blanket stays on the couch [sick_day:resident_2]
          book_sam → couch_l1: book dropped on the couch [sick_day:resident_2]
          charger_sam → nightstand_b2: charger stays plugged in by the couch; coffee_table_l1 was full, so it went to nightstand_b2 [sick_day:resident_2]
          headphones_sam → couch_l1: headphones left on the couch [sick_day:resident_2]
          water_bottle_sam → sink_k1: used, so it goes in the sink [sick_day:resident_2]
10:04  Sam — a short break in the kitchen [because of sick_day:resident_2]
10:52  Sam — resting on the couch in the living (bout 2/4) [because of sick_day:resident_2]; brings charger_sam from nightstand_b2, headphones_sam from couch_l1, book_sam from couch_l1, blanket_shared from couch_l1, water_bottle_sam from sink_k1
11:05  Sam finishes resting on the couch
          blanket_shared → couch_l1: blanket stays on the couch [sick_day:resident_2]
          book_sam → couch_l1: book dropped on the couch [sick_day:resident_2]
          charger_sam → bedroom_floor_b2: WHIM — was heading for nightstand_b2 (charger stays plugged in by the couch; coffee_table_l1 was full, so it went to nightstand_b2) but landed on bedroom_floor_b2 instead [sick_day:resident_2]
          headphones_sam → armchair_l1: WHIM — was heading for couch_l1 (headphones left on the couch) but landed on armchair_l1 instead [sick_day:resident_2]
          water_bottle_sam → sink_k1: used, so it goes in the sink [sick_day:resident_2]
11:05  Sam — a short break in the kitchen [because of sick_day:resident_2]
11:53  Sam — resting on the couch in the living (bout 3/4) [because of sick_day:resident_2]; brings charger_sam from bedroom_floor_b2, headphones_sam from armchair_l1, book_sam from couch_l1, blanket_shared from couch_l1, water_bottle_sam from sink_k1
12:29  Ines — lunch in the kitchen
13:14  Ines — reading in the bedroom_1; brings book_ines from nightstand_b1, glasses_ines from nightstand_b1
14:29  Ines finishes reading
          book_ines → nightstand_b1: put back in its usual place
          glasses_ines → nightstand_b1: put back in its usual place
          keeps phone_ines for errands
14:29  Ines leaves for errands (back 15:59); takes keys_ines, phone_ines, jacket_ines, shoes_ines; never takes wallet_ines on errands
15:59  Ines is back from errands
          jacket_ines → entry_hook_e1: put away in its usual place after the trip
          keys_ines → entry_table_e1: put away in its usual place after the trip
          shoes_ines → entry_floor_e1: put away in its usual place after the trip
          keeps phone_ines for cooking dinner
16:38  Sam finishes resting on the couch
          blanket_shared → couch_l1: blanket stays on the couch [sick_day:resident_2]
          book_sam → bookshelf_l1: WHIM — was heading for couch_l1 (book dropped on the couch) but landed on bookshelf_l1 instead [sick_day:resident_2]
          charger_sam → nightstand_b2: charger stays plugged in by the couch; coffee_table_l1 was full, so it went to nightstand_b2 [sick_day:resident_2]
          headphones_sam → couch_l1: headphones left on the couch [sick_day:resident_2]
          water_bottle_sam → tv_stand_l1: WHIM — was heading for coffee_table_l1 (left where it was used, too tired to put it away) but landed on tv_stand_l1 instead [low_energy:resident_2, sick_day:resident_2]
16:38  Sam — a short break in the kitchen [because of sick_day:resident_2]
16:55  Ines — cooking dinner in the kitchen
17:26  Sam — resting on the couch in the living (bout 4/4) [because of sick_day:resident_2]; brings charger_sam from nightstand_b2, headphones_sam from couch_l1, book_sam from bookshelf_l1, blanket_shared from couch_l1, water_bottle_sam from tv_stand_l1
17:37  Sam finishes resting on the couch
          blanket_shared → couch_l1: blanket stays on the couch [sick_day:resident_2]
          book_sam → couch_l1: book dropped on the couch [sick_day:resident_2]
          charger_sam → nightstand_b2: charger stays plugged in by the couch; coffee_table_l1 was full, so it went to nightstand_b2 [sick_day:resident_2]
          headphones_sam → couch_l1: headphones left on the couch [sick_day:resident_2]
          water_bottle_sam → sink_k1: used, so it goes in the sink [sick_day:resident_2]
17:45  Ines — dinner in the dining; brings water_bottle_ines from sink_k1
17:46  Aisha is back from work
          backpack_aisha → entry_hook_e1: put away in its usual place after the trip
          laptop_aisha → entry_hook_e1: stays in the backpack
          keeps jacket_aisha, keys_aisha, phone_aisha, shoes_aisha, wallet_aisha for a walk
17:46  Aisha leaves for a walk (back 18:21); takes keys_aisha, phone_aisha, wallet_aisha, jacket_aisha, shoes_aisha, headphones_aisha
18:21  Aisha is back from a walk
          headphones_aisha → desk_b3: put away in its usual place after the trip
          jacket_aisha → entry_hook_e1: put away in its usual place after the trip
          keys_aisha → entry_hook_e1: WHIM — was heading for entry_table_e1 (put away in its usual place after the trip) but landed on entry_hook_e1 instead
          shoes_aisha → entry_floor_e1: put away in its usual place after the trip
          wallet_aisha → nightstand_b3: put away in its usual place after the trip
          keeps phone_aisha for cooking dinner
18:21  Aisha — cooking dinner in the kitchen
18:27  Sam — cooking dinner in the kitchen
18:30  Ines finishes dinner
          water_bottle_ines → counter_k1: WHIM — was heading for sink_k1 (used, so it goes in the sink) but landed on counter_k1 instead
18:56  Aisha — dinner in the dining
19:20  Ines — evening TV in the living (bout 1/3); brings remote_shared from tv_stand_l1, blanket_shared from couch_l1, mug_ines from sink_k1, glasses_ines from nightstand_b1
19:35  Sam — dinner in the dining; brings water_bottle_sam from sink_k1
19:41  Ines finishes evening TV
          blanket_shared → couch_l1: put back in its usual place
          glasses_ines → nightstand_b1: put back in its usual place
          mug_ines → sink_k1: used, so it goes in the sink
19:41  Ines — a short break in the kitchen
19:59  Ines — evening TV in the living (bout 2/3); brings blanket_shared from couch_l1, mug_ines from sink_k1, glasses_ines from nightstand_b1
20:15  Sam finishes dinner
          water_bottle_sam → sink_k1: used, so it goes in the sink
20:28  Sam — evening TV in the living
20:40  Ines finishes evening TV
          blanket_shared → couch_l1: put back in its usual place
          glasses_ines → desk_b1: left where it was used, too tired to put it away; coffee_table_l1 was full, so it went to desk_b1 [low_energy:resident_1]
          mug_ines → sink_k1: used, so it goes in the sink
20:40  Ines — a short break in the kitchen
20:58  Ines — evening TV in the living (bout 3/3); brings blanket_shared from couch_l1, mug_ines from sink_k1, glasses_ines from desk_b1
21:19  Ines finishes evening TV
          blanket_shared → couch_l1: put back in its usual place
          glasses_ines → bedroom_floor_b1: WHIM — was heading for nightstand_b1 (put back in its usual place) but landed on bedroom_floor_b1 instead
          mug_ines → sink_k1: used, so it goes in the sink
          phone_ines → nightstand_b1: put back in its usual place
          remote_shared → tv_stand_l1: put back in its usual place
21:50  Aisha — evening TV in the living (bout 1/3); brings remote_shared from tv_stand_l1, blanket_shared from couch_l1, mug_aisha from counter_k1, glasses_aisha from nightstand_b3
22:03  Sam finishes evening TV
          blanket_shared → armchair_l1: left where it was used, too tired to put it away; coffee_table_l1 was full, so it went to armchair_l1 [low_energy:resident_2]
          mug_sam → dish_rack_k1: left where it was used; coffee_table_l1 was full, so it went to dish_rack_k1
          remote_shared → tv_stand_l1: put back in its usual place
22:15  Aisha finishes evening TV
          blanket_shared → coffee_table_l1: left where it was used
          glasses_aisha → nightstand_b3: put back in its usual place
          mug_aisha → sink_k1: used, so it goes in the sink
22:15  Aisha — a short break in the kitchen
22:18  Sam — reading in the bedroom_2; brings book_sam from couch_l1
22:29  Aisha — evening TV in the living (bout 2/3); brings remote_shared from tv_stand_l1, mug_aisha from sink_k1, glasses_aisha from nightstand_b3
22:48  Sam finishes reading
          book_sam → nightstand_b2: put back in its usual place
          phone_sam → nightstand_b2: put back in its usual place
22:48  Sam — bed in the bedroom_2
22:55  Aisha finishes evening TV
          blanket_shared → couch_l1: put back in its usual place
          glasses_aisha → nightstand_b3: put back in its usual place
          remote_shared → tv_stand_l1: put back in its usual place
22:55  Aisha — a short break in the kitchen
23:09  Aisha — evening TV in the living (bout 3/3); brings remote_shared from tv_stand_l1, blanket_shared from couch_l1, glasses_aisha from nightstand_b3
23:16  Ines — bed in the bedroom_1
23:24  Aisha finishes evening TV
          blanket_shared → couch_l1: put back in its usual place
          glasses_aisha → nightstand_b3: put back in its usual place
          mug_aisha → sink_k1: used, so it goes in the sink
          phone_aisha → nightstand_b3: put back in its usual place
23:25  Aisha — bed in the bedroom_3
```

## Day 2 — Friday

**Active causes**

- `late_work:resident_2` (Sam): A long day at work; home two hours late. gets home late and hurried; the evening walk and cooking are dropped and things are dumped at the door.
- `late_work:resident_3` (Aisha): A long day at work; home two hours late. gets home late and hurried; the evening walk and cooking are dropped and things are dumped at the door.
- `low_energy:resident_2`: Sam has low energy (0.11): leaves things where they were used instead of putting them back.
- `low_energy:resident_3`: Aisha has low energy (0.09): leaves things where they were used instead of putting them back.

Internal states (0–1): Ines energy 0.56, hurriedness 0.00, distraction 0.51; Sam energy 0.11, hurriedness 0.67, distraction 0.53; Aisha energy 0.09, hurriedness 0.63, distraction 0.00

**Timeline**

```
06:13  Aisha — morning routine in the bathroom; brings phone_aisha from nightstand_b3, glasses_aisha from nightstand_b3
06:38  Aisha finishes morning routine
          glasses_aisha → desk_b3: WHIM — was heading for nightstand_b3 (put back in its usual place) but landed on desk_b3 instead
          keeps phone_aisha for work
06:46  Ines — morning routine in the bathroom; brings phone_ines from nightstand_b1, glasses_ines from bedroom_floor_b1
07:01  Sam — morning routine in the bathroom; brings phone_sam from nightstand_b2
07:16  Ines finishes morning routine
          glasses_ines → nightstand_b1: put back in its usual place
07:20  Ines — breakfast in the kitchen; brings mug_ines from sink_k1
07:34  Sam — breakfast in the kitchen; brings mug_sam from dish_rack_k1
07:59  Sam finishes breakfast
          mug_sam → sink_k1: used, so it goes in the sink
          keeps phone_sam for work
08:00  Ines finishes breakfast
          mug_ines → sink_k1: used, so it goes in the sink
08:03  Aisha leaves for work (back 19:33); takes backpack_aisha (with laptop_aisha), keys_aisha, phone_aisha, wallet_aisha, jacket_aisha, shoes_aisha
08:11  Sam leaves for work (back 19:41); takes handbag_sam (with charger_sam, laptop_sam, notebook_sam), keys_sam, wallet_sam, jacket_sam, shoes_sam; never takes phone_sam on work
13:16  Ines — lunch in the kitchen
14:01  Ines — reading in the bedroom_1; brings book_ines from nightstand_b1, glasses_ines from nightstand_b1
15:16  Ines finishes reading
          book_ines → nightstand_b1: put back in its usual place
          glasses_ines → nightstand_b1: put back in its usual place
          keeps phone_ines for errands
16:04  Ines leaves for errands (back 17:34); takes keys_ines, phone_ines, jacket_ines, shoes_ines; never takes wallet_ines on errands
17:34  Ines is back from errands
          jacket_ines → entry_hook_e1: put away in its usual place after the trip
          keys_ines → entry_table_e1: put away in its usual place after the trip
          shoes_ines → entry_floor_e1: put away in its usual place after the trip
          keeps phone_ines for cooking dinner
17:34  Ines — cooking dinner in the kitchen
18:22  Ines — dinner in the dining; brings water_bottle_ines from counter_k1
19:07  Ines finishes dinner
          water_bottle_ines → counter_k1: used, so it goes in the sink; sink_k1 was full, so it went to counter_k1
19:33  Aisha is back from work
          backpack_aisha → entry_floor_e1: bag dumped by the door, home late [late_work:resident_3]
          jacket_aisha → couch_l1: jacket thrown over the couch, home late [late_work:resident_3]
          keys_aisha → entry_table_e1: put away in its usual place after the trip
          laptop_aisha → entry_floor_e1: stays in the backpack
          shoes_aisha → entry_floor_e1: put away in its usual place after the trip
          wallet_aisha → nightstand_b3: put away in its usual place after the trip
          keeps phone_aisha for dinner
19:33  Aisha — dinner in the dining
19:41  Sam is back from work
          handbag_sam → entry_floor_e1: bag dumped by the door, home late [late_work:resident_2]
          charger_sam → entry_floor_e1: stays in the handbag
          jacket_sam → couch_l1: jacket thrown over the couch, home late [late_work:resident_2]
          keys_sam → entry_hook_e1: WHIM — was heading for entry_table_e1 (put away in its usual place after the trip) but landed on entry_hook_e1 instead
          laptop_sam → entry_floor_e1: stays in the handbag
          notebook_sam → entry_floor_e1: stays in the handbag
          shoes_sam → wardrobe_b2: put away in its usual place after the trip; entry_floor_e1 was full, so it went to wardrobe_b2
          wallet_sam → nightstand_b2: put away in its usual place after the trip
19:41  Sam — dinner in the dining; brings water_bottle_sam from sink_k1
20:13  Aisha — evening TV in the living [shifted by late_work:resident_3]; brings blanket_shared from couch_l1, mug_aisha from sink_k1, glasses_aisha from desk_b3
20:21  Sam finishes dinner
          water_bottle_sam → sink_k1: used, so it goes in the sink
20:55  Sam — evening TV in the living (bout 1/2) [shifted by late_work:resident_2]; brings mug_sam from sink_k1
21:01  Aisha finishes evening TV
          blanket_shared → armchair_l1: left where it was used, too tired to put it away; coffee_table_l1 was full, so it went to armchair_l1 [low_energy:resident_3]
          glasses_aisha → desk_b3: left where it was used; coffee_table_l1 was full, so it went to desk_b3
          phone_aisha → nightstand_b3: put back in its usual place
          remote_shared → couch_l1: WHIM — was heading for tv_stand_l1 (put back in its usual place) but landed on couch_l1 instead
21:08  Sam finishes evening TV
          remote_shared → tv_stand_l1: put back in its usual place
21:08  Sam — a short break in the kitchen
21:21  Ines — evening TV in the living; brings remote_shared from tv_stand_l1, blanket_shared from armchair_l1, mug_ines from sink_k1, glasses_ines from nightstand_b1
21:22  Sam — evening TV in the living (bout 2/2) [shifted by late_work:resident_2]
21:42  Sam finishes evening TV
          blanket_shared → armchair_l1: left where it was used, too tired to put it away; coffee_table_l1 was full, so it went to armchair_l1 [low_energy:resident_2]
          mug_sam → sink_k1: used, so it goes in the sink
          phone_sam → bedroom_floor_b2: WHIM — was heading for nightstand_b2 (put back in its usual place) but landed on bedroom_floor_b2 instead
          remote_shared → tv_stand_l1: put back in its usual place
22:05  Sam — bed in the bedroom_2
22:12  Aisha — bed in the bedroom_3
23:21  Ines finishes evening TV
          blanket_shared → couch_l1: put back in its usual place
          glasses_ines → nightstand_b1: put back in its usual place
          mug_ines → sink_k1: used, so it goes in the sink
          phone_ines → nightstand_b1: put back in its usual place
23:21  Ines — bed in the bedroom_1
```

## Day 3 — Saturday

**Active causes**

- `sick_day:resident_1` (Ines): Off sick, resting on the couch all day. no work or trips out; laptop, mug, medication, book and blanket all migrate to the couch and coffee table.
- `low_energy:resident_2`: Sam has low energy (0.17): leaves things where they were used instead of putting them back.
- `low_energy:resident_3`: Aisha has low energy (0.16): leaves things where they were used instead of putting them back.
- `running_late:resident_2`: Sam is running late all day (0.73): rushed putdowns, things dumped at the door, more whim.
- `running_late:resident_3`: Aisha is running late all day (0.88): rushed putdowns, things dumped at the door, more whim.

Internal states (0–1): Ines energy 0.38, hurriedness 0.00, distraction 0.32; Sam energy 0.17, hurriedness 0.73, distraction 0.00; Aisha energy 0.16, hurriedness 0.88, distraction 0.12

**Timeline**

```
07:54  Ines — morning routine in the bathroom; brings phone_ines from nightstand_b1, glasses_ines from nightstand_b1
08:24  Ines finishes morning routine
          glasses_ines → nightstand_b1: put back in its usual place
08:24  Ines — breakfast in the kitchen; brings mug_ines from sink_k1
08:39  Aisha — morning routine in the bathroom; brings phone_aisha from nightstand_b3, glasses_aisha from desk_b3
09:04  Aisha finishes morning routine
          glasses_aisha → nightstand_b3: put back in its usual place
09:04  Aisha — breakfast in the kitchen; brings mug_aisha from coffee_table_l1
09:09  Ines — resting on the couch in the living (bout 1/2) [because of sick_day:resident_1]; brings headphones_ines from desk_b1, glasses_ines from nightstand_b1, mug_ines from kitchen_table_k1, book_ines from nightstand_b1, blanket_shared from couch_l1, water_bottle_ines from counter_k1
09:12  Sam — morning routine in the bathroom; brings phone_sam from bedroom_floor_b2
09:37  Sam — breakfast in the kitchen; brings mug_sam from sink_k1
09:39  Aisha — chores in the kitchen
10:12  Sam finishes breakfast
          mug_sam → counter_k1: WHIM — was heading for sink_k1 (used, so it goes in the sink) but landed on counter_k1 instead
10:46  Ines finishes resting on the couch
          blanket_shared → couch_l1: blanket stays on the couch [sick_day:resident_1]
          book_ines → bookshelf_l1: book dropped on the couch; couch_l1 was full, so it went to bookshelf_l1 [sick_day:resident_1]
          glasses_ines → desk_b1: glasses left on the coffee table; coffee_table_l1 was full, so it went to desk_b1 [sick_day:resident_1]
          headphones_ines → nightstand_b1: headphones left on the couch; couch_l1 was full, so it went to nightstand_b1 [sick_day:resident_1]
          water_bottle_ines → sink_k1: used, so it goes in the sink [sick_day:resident_1]
10:46  Ines — a short break in the kitchen [because of sick_day:resident_1]
10:59  Aisha finishes chores
          mug_aisha (from kitchen_table_k1) → cupboard_k1: tidied away to its usual place
          mug_sam (from counter_k1) → cupboard_k1: tidied away to its usual place
          water_bottle_ines (from sink_k1) → dish_rack_k1: tidied away to its usual place
          water_bottle_sam (from sink_k1) → kitchen_table_k1: WHIM — was heading for dish_rack_k1 (tidied away to its usual place) but landed on kitchen_table_k1 instead
          keeps phone_aisha for errands
10:59  Aisha leaves for errands (back 12:59); takes backpack_aisha, keys_aisha, phone_aisha, jacket_aisha, shoes_aisha; never takes wallet_aisha on errands
11:13  Sam — chores in the kitchen (bout 1/3)
11:36  Sam finishes chores
          water_bottle_sam (from kitchen_table_k1) → dish_rack_k1: tidied away to its usual place
11:36  Sam — a short break in the kitchen
11:46  Sam — chores in the kitchen (bout 2/3)
11:56  Sam — a short break in the kitchen
12:06  Sam — chores in the kitchen (bout 3/3)
12:59  Aisha is back from errands
          backpack_aisha → entry_floor_e1: dropped at the door instead of being put away
          jacket_aisha → entry_hook_e1: put away in its usual place after the trip
          keys_aisha → entry_table_e1: put away in its usual place after the trip
          shoes_aisha → entry_floor_e1: put away in its usual place after the trip
          keeps phone_aisha for lunch
13:10  Ines — resting on the couch in the living (bout 2/2) [because of sick_day:resident_1]; brings headphones_ines from nightstand_b1, glasses_ines from desk_b1, book_ines from bookshelf_l1, blanket_shared from couch_l1, water_bottle_ines from dish_rack_k1
14:02  Sam — lunch in the kitchen
14:34  Aisha — lunch in the kitchen
14:42  Sam finishes lunch
          keeps phone_sam for the gym
16:41  Sam leaves for the gym (back 18:01); takes keys_sam, wallet_sam, jacket_sam, shoes_sam; never takes phone_sam on the gym
17:08  Ines finishes resting on the couch
          blanket_shared → couch_l1: blanket stays on the couch [sick_day:resident_1]
          headphones_ines → couch_l1: headphones left on the couch [sick_day:resident_1]
          mug_ines → dish_rack_k1: tea mug stays by the couch; coffee_table_l1 was full, so it went to dish_rack_k1 [sick_day:resident_1]
          water_bottle_ines → sink_k1: used, so it goes in the sink [sick_day:resident_1]
17:09  Ines — reading in the bedroom_1; brings book_ines from coffee_table_l1, glasses_ines from coffee_table_l1
17:20  Aisha — reading in the bedroom_3; brings glasses_aisha from nightstand_b3
18:01  Sam is back from the gym
          jacket_sam → entry_hook_e1: put away in its usual place after the trip
          keys_sam → entry_table_e1: put away in its usual place after the trip
          shoes_sam → wardrobe_b2: put away in its usual place after the trip; entry_floor_e1 was full, so it went to wardrobe_b2
          wallet_sam → bed_b2: WHIM — was heading for nightstand_b2 (put away in its usual place after the trip) but landed on bed_b2 instead
18:10  Sam — cooking dinner in the kitchen
18:20  Aisha finishes reading
          book_aisha → nightstand_b3: put back in its usual place
18:39  Ines finishes reading
          book_ines → nightstand_b1: put back in its usual place
          glasses_ines → nightstand_b1: put back in its usual place
18:39  Ines — cooking dinner in the kitchen
18:41  Aisha — cooking dinner in the kitchen
18:52  Sam — dinner in the dining; brings water_bottle_sam from dish_rack_k1
19:31  Aisha — dinner in the dining
20:01  Sam — evening TV in the living; brings remote_shared from tv_stand_l1, blanket_shared from couch_l1, mug_sam from cupboard_k1
20:19  Ines — dinner in the dining; brings water_bottle_ines from sink_k1
21:09  Ines finishes dinner
          water_bottle_ines → sink_k1: used, so it goes in the sink
21:09  Ines — evening TV in the living (bout 1/2); brings mug_ines from dish_rack_k1, glasses_ines from nightstand_b1
21:21  Ines finishes evening TV
          blanket_shared → couch_l1: put back in its usual place
          glasses_ines → nightstand_b1: put back in its usual place
          mug_ines → sink_k1: used, so it goes in the sink
          remote_shared → tv_stand_l1: put back in its usual place
21:21  Ines — a short break in the kitchen
21:39  Ines — evening TV in the living (bout 2/2); brings remote_shared from tv_stand_l1, blanket_shared from couch_l1, mug_ines from sink_k1, glasses_ines from nightstand_b1
21:51  Sam finishes evening TV
          blanket_shared → couch_l1: put back in its usual place
          mug_sam → sink_k1: used, so it goes in the sink
          phone_sam → nightstand_b2: put back in its usual place
          remote_shared → tv_stand_l1: put back in its usual place
22:06  Aisha — evening TV in the living (bout 1/3); brings remote_shared from tv_stand_l1, blanket_shared from couch_l1, mug_aisha from cupboard_k1, glasses_aisha from bed_b3
22:33  Aisha finishes evening TV
          blanket_shared → armchair_l1: WHIM — was heading for couch_l1 (put back in its usual place) but landed on armchair_l1 instead
          glasses_aisha → desk_b3: left where it was used; coffee_table_l1 was full, so it went to desk_b3
          mug_aisha → dish_rack_k1: left where it was used; coffee_table_l1 was full, so it went to dish_rack_k1
22:33  Aisha — a short break in the kitchen
22:43  Ines finishes evening TV
          blanket_shared → couch_l1: put back in its usual place
          glasses_ines → nightstand_b1: put back in its usual place
          mug_ines → sink_k1: used, so it goes in the sink
          phone_ines → nightstand_b1: put back in its usual place
          remote_shared → tv_stand_l1: put back in its usual place
22:49  Aisha — evening TV in the living (bout 2/3); brings remote_shared from tv_stand_l1, blanket_shared from couch_l1, mug_aisha from dish_rack_k1, glasses_aisha from desk_b3
22:59  Aisha finishes evening TV
          blanket_shared → armchair_l1: WHIM — was heading for couch_l1 (put back in its usual place) but landed on armchair_l1 instead
22:59  Aisha — a short break in the kitchen
23:03  Sam — bed in the bedroom_2
23:09  Ines — bed in the bedroom_1
23:15  Aisha — evening TV in the living (bout 3/3); brings blanket_shared from armchair_l1
23:56  Aisha finishes evening TV
          blanket_shared → armchair_l1: left where it was used; coffee_table_l1 was full, so it went to armchair_l1
          mug_aisha → sink_k1: used, so it goes in the sink
          phone_aisha → nightstand_b3: put back in its usual place
23:56  Aisha — bed in the bedroom_3
```

## Day 4 — Sunday

**Active causes**

- `rain` (household): It rains for most of the day. no walk; wet shoes, jackets and umbrellas get dropped at the entry instead of being put away.
- `distracted:resident_1`: Ines is distracted (0.74): carries things into the next room absent-mindedly, more likely to forget pocket items.
- `low_energy:resident_3`: Aisha has low energy (0.04): leaves things where they were used instead of putting them back.

Internal states (0–1): Ines energy 0.50, hurriedness 0.22, distraction 0.74; Sam energy 0.34, hurriedness 0.52, distraction 0.37; Aisha energy 0.04, hurriedness 0.56, distraction 0.10

**Timeline**

```
08:32  Ines — morning routine in the bathroom; brings phone_ines from nightstand_b1, glasses_ines from nightstand_b1
08:45  Aisha — morning routine in the bathroom; brings phone_aisha from nightstand_b3, glasses_aisha from coffee_table_l1
08:58  Sam — morning routine in the bathroom; brings phone_sam from nightstand_b2
09:02  Ines finishes morning routine
          glasses_ines → bed_b1: WHIM — was heading for nightstand_b1 (put back in its usual place) but landed on bed_b1 instead
09:02  Ines — breakfast in the kitchen; brings mug_ines from sink_k1
09:10  Aisha finishes morning routine
          glasses_aisha → medicine_cabinet_ba1: WHIM — was heading for bathroom_shelf_ba1 (left where it was used, too tired to put it away) but landed on medicine_cabinet_ba1 instead [low_energy:resident_3]
09:10  Aisha — breakfast in the kitchen; brings mug_aisha from sink_k1
09:23  Sam — breakfast in the kitchen; brings mug_sam from sink_k1
09:45  Aisha finishes breakfast
          mug_aisha → dish_rack_k1: WHIM — was heading for sink_k1 (used, so it goes in the sink) but landed on dish_rack_k1 instead
09:45  Aisha — chores in the kitchen
09:47  Ines finishes breakfast
          mug_ines → sink_k1: used, so it goes in the sink
09:58  Sam finishes breakfast
          mug_sam → sink_k1: used, so it goes in the sink
10:55  Sam — chores in the kitchen (bout 1/4)
11:05  Sam finishes chores
          mug_aisha (from dish_rack_k1) → cupboard_k1: tidied away to its usual place
          mug_ines (from sink_k1) → cupboard_k1: tidied away to its usual place
          mug_sam (from sink_k1) → cupboard_k1: tidied away to its usual place
          water_bottle_ines (from sink_k1) → dish_rack_k1: tidied away to its usual place
11:05  Aisha finishes chores
          keeps phone_aisha for errands
11:05  Sam — a short break in the kitchen
11:15  Sam — chores in the kitchen (bout 2/4)
11:25  Sam — a short break in the kitchen
11:31  Ines — chores in the kitchen (bout 1/3)
11:35  Sam — chores in the kitchen (bout 3/4)
11:50  Ines — a short break in the kitchen
11:55  Sam — a short break in the kitchen
12:00  Ines — chores in the kitchen (bout 2/3)
12:05  Sam — chores in the kitchen (bout 4/4)
12:10  Ines — a short break in the kitchen
12:20  Ines — chores in the kitchen (bout 3/3)
12:31  Ines — lunch in the kitchen
13:21  Aisha leaves for errands (back 14:33); takes backpack_aisha, keys_aisha, phone_aisha, jacket_aisha, shoes_aisha, umbrella_aisha; never takes wallet_aisha on errands
13:46  Ines — reading in the bedroom_1; brings book_ines from nightstand_b1
14:33  Aisha is back from errands
          backpack_aisha → entry_hook_e1: WHIM — was heading for entry_floor_e1 (wet bag left by the door) but landed on entry_hook_e1 instead [rain]
          jacket_aisha → entry_hook_e1: wet jacket hung on the hook [rain]
          keys_aisha → entry_table_e1: put away in its usual place after the trip
          shoes_aisha → entry_floor_e1: wet shoes left on the entry floor to dry [rain]
          umbrella_aisha → entry_floor_e1: wet umbrella propped by the door [rain]
          keeps phone_aisha for lunch
14:33  Sam — lunch in the kitchen
14:33  Aisha — lunch in the kitchen
15:16  Ines finishes reading
          book_ines → nightstand_b1: put back in its usual place
          glasses_ines → nightstand_b1: put back in its usual place
17:16  Ines — cooking dinner in the kitchen
18:22  Aisha — cooking dinner in the kitchen
18:31  Ines — dinner in the dining; brings water_bottle_ines from dish_rack_k1
18:57  Sam — cooking dinner in the kitchen
19:21  Ines finishes dinner
          water_bottle_ines → sink_k1: used, so it goes in the sink
19:37  Sam — dinner in the dining
20:05  Aisha — dinner in the dining
20:22  Sam finishes dinner
          water_bottle_sam → sink_k1: used, so it goes in the sink
20:22  Sam — evening TV in the living; brings blanket_shared from armchair_l1, mug_sam from cupboard_k1
20:50  Aisha — evening TV in the living (bout 1/2); brings mug_aisha from cupboard_k1, glasses_aisha from medicine_cabinet_ba1
21:36  Ines — evening TV in the living (bout 1/2); brings mug_ines from cupboard_k1, glasses_ines from nightstand_b1
21:46  Ines finishes evening TV
          blanket_shared → couch_l1: put back in its usual place
          glasses_ines → nightstand_b1: put back in its usual place
          mug_ines → sink_k1: used, so it goes in the sink
          remote_shared → tv_stand_l1: put back in its usual place
21:46  Aisha finishes evening TV
          blanket_shared → armchair_l1: WHIM — was heading for couch_l1 (put back in its usual place) but landed on armchair_l1 instead
          glasses_aisha → nightstand_b3: put back in its usual place
          mug_aisha → sink_k1: used, so it goes in the sink
21:46  Ines — a short break in the kitchen
21:46  Aisha — a short break in the kitchen
22:12  Sam finishes evening TV
          blanket_shared → couch_l1: put back in its usual place
          mug_sam → dish_rack_k1: used, so it goes in the sink; sink_k1 was full, so it went to dish_rack_k1
          phone_sam → nightstand_b2: put back in its usual place
22:19  Aisha — evening TV in the living (bout 2/2); brings remote_shared from tv_stand_l1, blanket_shared from couch_l1, mug_aisha from sink_k1, glasses_aisha from nightstand_b3
22:22  Ines — evening TV in the living (bout 2/2); brings mug_ines from sink_k1, glasses_ines from nightstand_b1
22:31  Sam — bed in the bedroom_2
22:39  Aisha finishes evening TV
          blanket_shared → couch_l1: WHIM — was heading for armchair_l1 (left where it was used, too tired to put it away; coffee_table_l1 was full, so it went to armchair_l1) but landed on couch_l1 instead [low_energy:resident_3]
          glasses_aisha → nightstand_b3: put back in its usual place
          mug_aisha → dish_rack_k1: left where it was used, too tired to put it away; coffee_table_l1 was full, so it went to dish_rack_k1 [low_energy:resident_3]
          phone_aisha → coffee_table_l1: left where it was used
          remote_shared → armchair_l1: left where it was used; coffee_table_l1 was full, so it went to armchair_l1
22:40  Aisha — bed in the bedroom_3
23:36  Ines finishes evening TV
          glasses_ines → nightstand_b1: put back in its usual place
          mug_ines → sink_k1: used, so it goes in the sink
          phone_ines → coffee_table_l1: left where it was used
          remote_shared → tv_stand_l1: put back in its usual place
23:36  Ines — bed in the bedroom_1
```
