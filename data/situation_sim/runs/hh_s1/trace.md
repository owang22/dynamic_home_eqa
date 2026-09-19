# Household hh_s1 — five days, Wednesday to Sunday

Seed-generated household. Times are clock times; ids are the receptacle and object ids used in events.jsonl. A line indented under an activity says where an object went when the activity ended and why. WHIM marks a placement that landed somewhere other than where the decision was heading. Text in [brackets] names the hidden cause the decision is attributed to.

## Household

Type: couple. Rooms: bathroom, bedroom_1, entry, kitchen, living, office.

Residents:

- **Dana** (resident_1): retired; fairly tidy (tidiness 0.60); punctual (jitter scale 0.74); rarely forgets pocket items; mood strongly affects behaviour (sensitivity 0.86); sleeps in bedroom_1, works at the bedroom_1 desk
- **Sam** (resident_2): works outside the home; very tidy (tidiness 0.82); average timing (jitter scale 1.08); rarely forgets pocket items; mood moderately affects behaviour (sensitivity 0.57); sleeps in bedroom_1, works at the bedroom_1 desk

Objects and their usual place (primary slot first):

- Dana's: book_dana → nightstand_b1 / bookshelf_l1; headphones_dana → desk_b1 / nightstand_b1; jacket_dana → entry_hook_e1 / wardrobe_b1; keys_dana → entry_table_e1 / nightstand_b1; medication_dana → medicine_cabinet_ba1 / nightstand_b1; mug_dana → cupboard_k1 / dish_rack_k1 / sink_k1; phone_dana → nightstand_b1 / coffee_table_l1; shoes_dana → entry_floor_e1 / wardrobe_b1; towel_dana → towel_rack_ba1 / bathroom_shelf_ba1; wallet_dana → entry_table_e1 / desk_b1; water_bottle_dana → dish_rack_k1 / counter_k1 / sink_k1
- Sam's: backpack_sam → entry_hook_e1 / bedroom_floor_b1 / desk_b1; charger_sam → desk_b1 / nightstand_b1; gym_bag_sam → wardrobe_b1 / bedroom_floor_b1; headphones_sam → desk_b1 / nightstand_b1; jacket_sam → entry_hook_e1 / wardrobe_b1; keys_sam → entry_table_e1 / nightstand_b1; laptop_sam → desk_b1 / bookshelf_l1; mug_sam → cupboard_k1 / dish_rack_k1 / sink_k1; notebook_sam → desk_b1 / bookshelf_l1; phone_sam → nightstand_b1 / coffee_table_l1; shoes_sam → entry_floor_e1 / wardrobe_b1; towel_sam → towel_rack_ba1 / bathroom_shelf_ba1; wallet_sam → nightstand_b1 / desk_b1
- Shared: blanket_shared → couch_l1 / armchair_l1; laundry_basket_shared → bathroom_shelf_ba1 / bedroom_floor_b1; remote_shared → tv_stand_l1 / coffee_table_l1; watering_can_shared → cupboard_k1 / counter_k1

Object groups (things that travel together):

- backpack_sam carries charger_sam, headphones_sam, laptop_sam, notebook_sam on trips to work and errands
- gym_bag_sam carries nothing in particular on gym trips


## Day 0 — Wednesday

**Active causes**

- `rain` (household): It rains for most of the day. no walk; wet shoes, jackets and umbrellas get dropped at the entry instead of being put away.
- `distracted:resident_1`: Dana is distracted (0.68): carries things into the next room absent-mindedly, more likely to forget pocket items.

Internal states (0–1): Dana energy 0.49, hurriedness 0.14, distraction 0.68; Sam energy 0.38, hurriedness 0.36, distraction 0.58

**Timeline**

```
06:35  Sam — morning routine in the bathroom; brings phone_sam from nightstand_b1
07:24  Sam — breakfast in the kitchen; brings mug_sam from cupboard_k1
07:27  Dana — morning routine in the bathroom; brings phone_dana from nightstand_b1
07:49  Sam finishes breakfast
          mug_sam → sink_k1: used, so it goes in the sink
          keeps phone_sam for work
07:57  Dana — breakfast in the kitchen; brings mug_dana from cupboard_k1
08:08  Sam leaves for work (back 17:38); takes backpack_sam (with charger_sam, headphones_sam, laptop_sam, notebook_sam), phone_sam, wallet_sam, jacket_sam, shoes_sam; never takes keys_sam on work
10:03  Dana — chores in the kitchen (bout 1/4); brings watering_can_shared from cupboard_k1
10:13  Dana finishes chores
          watering_can_shared → cupboard_k1: tidied away to its usual place
          mug_dana (from kitchen_table_k1) → cupboard_k1: tidied away to its usual place
          mug_sam (from sink_k1) → cupboard_k1: tidied away to its usual place
10:13  Dana — a short break in the kitchen
10:23  Dana — chores in the kitchen (bout 2/4); brings watering_can_shared from cupboard_k1
10:33  Dana finishes chores
          watering_can_shared → cupboard_k1: tidied away to its usual place
10:33  Dana — a short break in the kitchen
10:43  Dana — chores in the kitchen (bout 3/4); brings watering_can_shared from cupboard_k1
11:04  Dana finishes chores
          watering_can_shared → cupboard_k1: tidied away to its usual place
11:04  Dana — a short break in the kitchen
11:14  Dana — chores in the kitchen (bout 4/4); brings watering_can_shared from cupboard_k1
11:33  Dana finishes chores
          watering_can_shared → cupboard_k1: tidied away to its usual place
12:30  Dana — lunch in the kitchen
14:47  Dana — reading in the bedroom_1; brings book_dana from nightstand_b1
16:02  Dana finishes reading
          book_dana → nightstand_b1: put back in its usual place
          keeps phone_dana for errands
16:57  Dana leaves for errands (back 17:51); takes keys_dana, phone_dana, wallet_dana, jacket_dana, shoes_dana
17:38  Sam is back from work
          backpack_sam → entry_floor_e1: wet bag left by the door [rain]
          charger_sam → entry_floor_e1: stays in the backpack
          headphones_sam → entry_floor_e1: stays in the backpack
          jacket_sam → entry_hook_e1: wet jacket hung on the hook [rain]
          laptop_sam → entry_floor_e1: stays in the backpack
          notebook_sam → entry_floor_e1: stays in the backpack
          shoes_sam → entry_floor_e1: wet shoes left on the entry floor to dry [rain]
          wallet_sam → entry_table_e1: dropped at the door instead of being put away
          keeps phone_sam for cooking dinner
17:51  Dana is back from errands
          jacket_dana → entry_hook_e1: wet jacket hung on the hook [rain]
          keys_dana → entry_table_e1: put away in its usual place after the trip
          shoes_dana → entry_floor_e1: wet shoes left on the entry floor to dry [rain]
          wallet_dana → entry_table_e1: put away in its usual place after the trip
          keeps phone_dana for cooking dinner
17:51  Dana — cooking dinner in the kitchen
18:07  Sam — cooking dinner in the kitchen
18:36  Dana — dinner in the kitchen; brings water_bottle_dana from dish_rack_k1
18:42  Sam — dinner in the kitchen
19:21  Dana finishes dinner
          water_bottle_dana → sink_k1: used, so it goes in the sink
19:21  Dana — evening TV in the living (bout 1/2); brings remote_shared from tv_stand_l1, blanket_shared from couch_l1, mug_dana from cupboard_k1
19:22  Sam — evening TV in the living (bout 1/3); brings mug_sam from cupboard_k1
20:03  Dana finishes evening TV
          blanket_shared → armchair_l1: left where it was used; coffee_table_l1 was full, so it went to armchair_l1
          mug_dana → counter_k1: carried along absent-mindedly into the kitchen [distracted:resident_1]
20:03  Dana — a short break in the kitchen
20:05  Sam finishes evening TV
          blanket_shared → couch_l1: put back in its usual place
          mug_sam → sink_k1: used, so it goes in the sink
          remote_shared → tv_stand_l1: put back in its usual place
20:05  Sam — a short break in the kitchen
20:19  Sam — evening TV in the living (bout 2/3); brings remote_shared from tv_stand_l1, blanket_shared from couch_l1, mug_sam from sink_k1
20:32  Sam finishes evening TV
          blanket_shared → couch_l1: put back in its usual place
          mug_sam → sink_k1: used, so it goes in the sink
          remote_shared → tv_stand_l1: put back in its usual place
20:32  Sam — a short break in the kitchen
20:39  Dana — evening TV in the living (bout 2/2); brings remote_shared from tv_stand_l1, blanket_shared from couch_l1, mug_dana from counter_k1
20:46  Sam — evening TV in the living (bout 3/3); brings mug_sam from sink_k1
20:56  Sam finishes evening TV
          blanket_shared → couch_l1: put back in its usual place
          mug_sam → sink_k1: used, so it goes in the sink
          remote_shared → tv_stand_l1: put back in its usual place
21:13  Sam — reading in the bedroom_1
21:20  Dana finishes evening TV
          phone_dana → nightstand_b1: put back in its usual place
21:31  Dana — bed in the bedroom_1
21:43  Sam finishes reading
          phone_sam → nightstand_b1: put back in its usual place
23:36  Sam — bed in the bedroom_1
```

## Day 1 — Thursday

**Active causes**

- `laundry_day` (household): Laundry day. the laundry basket travels, towels and the blanket get washed and end up airing in the bedroom rather than where they live.
- `distracted:resident_1`: Dana is distracted (0.82): carries things into the next room absent-mindedly, more likely to forget pocket items.
- `low_energy:resident_2`: Sam has low energy (0.24): leaves things where they were used instead of putting them back.

Internal states (0–1): Dana energy 0.80, hurriedness 0.08, distraction 0.82; Sam energy 0.24, hurriedness 0.13, distraction 0.56

**Timeline**

```
06:55  Dana — morning routine in the bathroom; brings phone_dana from nightstand_b1
07:51  Sam — morning routine in the bathroom; brings phone_sam from nightstand_b1
08:11  Dana — breakfast in the kitchen; brings mug_dana from coffee_table_l1
08:16  Sam finishes morning routine
          keeps phone_sam for work
08:21  Sam leaves for work (back 17:51); takes backpack_sam (with charger_sam, headphones_sam, laptop_sam, notebook_sam), phone_sam, wallet_sam, jacket_sam, shoes_sam; never takes keys_sam on work
08:51  Dana finishes breakfast
          mug_dana → sink_k1: used, so it goes in the sink
          keeps phone_dana for a walk
11:05  Dana leaves for a walk (back 11:55); takes keys_dana, phone_dana, jacket_dana, shoes_dana, headphones_dana; never takes wallet_dana on a walk
11:55  Dana is back from a walk
          headphones_dana → desk_b1: put away in its usual place after the trip
          jacket_dana → entry_hook_e1: put away in its usual place after the trip
          keys_dana → entry_hook_e1: WHIM — was heading for entry_table_e1 (put away in its usual place after the trip) but landed on entry_hook_e1 instead
          shoes_dana → entry_floor_e1: put away in its usual place after the trip
          keeps phone_dana for laundry
11:55  Dana — laundry in the bathroom [because of laundry_day]; brings towel_dana from towel_rack_ba1, blanket_shared from couch_l1
13:25  Dana finishes laundry
          blanket_shared → bedroom_floor_b1: WHIM — was heading for bed_b1 (washed blanket airing on the bed) but landed on bedroom_floor_b1 instead [laundry_day]
          laundry_basket_shared → bedroom_floor_b1: basket left in the bedroom while things dry [laundry_day]
          towel_dana → bed_b1: clean towel folded on the bed [laundry_day]
13:25  Dana — lunch in the kitchen
14:10  Dana — reading in the bedroom_1; brings book_dana from nightstand_b1
15:25  Dana finishes reading
          keeps phone_dana for errands
15:25  Dana leaves for errands (back 16:55); takes keys_dana, phone_dana, wallet_dana, jacket_dana, shoes_dana
16:55  Dana is back from errands
          jacket_dana → entry_hook_e1: put away in its usual place after the trip
          keys_dana → entry_table_e1: put away in its usual place after the trip
          shoes_dana → entry_floor_e1: put away in its usual place after the trip
          wallet_dana → entry_table_e1: put away in its usual place after the trip
          keeps phone_dana for cooking dinner
17:51  Sam is back from work
          backpack_sam → entry_hook_e1: put away in its usual place after the trip
          charger_sam → entry_hook_e1: stays in the backpack
          headphones_sam → entry_hook_e1: stays in the backpack
          jacket_sam → entry_hook_e1: put away in its usual place after the trip
          laptop_sam → entry_hook_e1: stays in the backpack
          notebook_sam → entry_hook_e1: stays in the backpack
          shoes_sam → entry_floor_e1: put away in its usual place after the trip
          wallet_sam → nightstand_b1: put away in its usual place after the trip
          keeps phone_sam for cooking dinner
18:11  Dana — cooking dinner in the kitchen
18:16  Sam — cooking dinner in the kitchen
19:07  Dana — dinner in the kitchen; brings water_bottle_dana from sink_k1
19:15  Sam — dinner in the kitchen
19:52  Dana finishes dinner
          water_bottle_dana → sink_k1: used, so it goes in the sink
20:14  Sam — evening TV in the living; brings remote_shared from tv_stand_l1, blanket_shared from bedroom_floor_b1, mug_sam from sink_k1
20:41  Dana — evening TV in the living; brings mug_dana from sink_k1
21:16  Sam finishes evening TV
          blanket_shared → couch_l1: put back in its usual place
          mug_sam → sink_k1: used, so it goes in the sink
22:41  Dana finishes evening TV
          mug_dana → kitchen_table_k1: WHIM — was heading for sink_k1 (used, so it goes in the sink) but landed on kitchen_table_k1 instead
          phone_dana → nightstand_b1: put back in its usual place
          remote_shared → tv_stand_l1: put back in its usual place
22:41  Dana — bed in the bedroom_1
22:58  Sam — reading in the bedroom_1
23:28  Sam finishes reading
          phone_sam → bed_b1: left where it was used, too tired to put it away [low_energy:resident_2]
23:28  Sam — bed in the bedroom_1
```

## Day 2 — Friday

**Active causes**

- `late_work:resident_2` (Sam): A long day at work; home two hours late. gets home late and hurried; the evening walk and cooking are dropped and things are dumped at the door.
- `distracted:resident_1`: Dana is distracted (0.87): carries things into the next room absent-mindedly, more likely to forget pocket items.
- `distracted:resident_2`: Sam is distracted (1.00): carries things into the next room absent-mindedly, more likely to forget pocket items.
- `low_energy:resident_2`: Sam has low energy (0.06): leaves things where they were used instead of putting them back.
- `running_late:resident_2`: Sam is running late all day (1.00): rushed putdowns, things dumped at the door, more whim.

Internal states (0–1): Dana energy 1.00, hurriedness 0.41, distraction 0.87; Sam energy 0.06, hurriedness 1.00, distraction 1.00

**Timeline**

```
07:04  Dana — morning routine in the bathroom; brings phone_dana from nightstand_b1
07:24  Sam — morning routine in the bathroom; brings phone_sam from bed_b1
07:39  Dana — breakfast in the kitchen
07:49  Sam — breakfast in the kitchen; brings mug_sam from sink_k1
08:14  Sam finishes breakfast
          mug_sam → sink_k1: used, so it goes in the sink
          keeps phone_sam for work
08:19  Dana finishes breakfast
          mug_dana → sink_k1: used, so it goes in the sink
08:24  Sam leaves for work (back 19:54); takes backpack_sam (with charger_sam, headphones_sam, laptop_sam, notebook_sam), phone_sam, wallet_sam, jacket_sam, shoes_sam; never takes keys_sam on work
12:08  Dana — lunch in the kitchen
14:22  Dana — reading in the bedroom_1
15:37  Dana finishes reading
          keeps phone_dana for errands
15:37  Dana leaves for errands (back 17:07); takes keys_dana, phone_dana, wallet_dana, jacket_dana, shoes_dana
17:07  Dana is back from errands
          jacket_dana → entry_hook_e1: put away in its usual place after the trip
          keys_dana → entry_table_e1: put away in its usual place after the trip
          shoes_dana → entry_floor_e1: put away in its usual place after the trip
          wallet_dana → entry_table_e1: put away in its usual place after the trip
          keeps phone_dana for cooking dinner
17:46  Dana — cooking dinner in the kitchen
18:39  Dana — dinner in the kitchen; brings water_bottle_dana from sink_k1
19:24  Dana finishes dinner
          water_bottle_dana → sink_k1: used, so it goes in the sink
19:36  Dana — evening TV in the living (bout 1/4); brings remote_shared from tv_stand_l1, blanket_shared from couch_l1, mug_dana from sink_k1
19:54  Sam is back from work
          backpack_sam → entry_floor_e1: bag dumped by the door, home late [late_work:resident_2]
          charger_sam → entry_floor_e1: stays in the backpack
          headphones_sam → entry_floor_e1: stays in the backpack
          jacket_sam → couch_l1: jacket thrown over the couch, home late [late_work:resident_2]
          laptop_sam → entry_floor_e1: stays in the backpack
          notebook_sam → entry_floor_e1: stays in the backpack
          shoes_sam → entry_floor_e1: put away in its usual place after the trip
          wallet_sam → entry_table_e1: dumped at the door, running late [running_late:resident_2]
          keeps phone_sam for dinner
19:54  Sam — dinner in the kitchen
20:07  Dana finishes evening TV
          blanket_shared → couch_l1: put back in its usual place
          mug_dana → sink_k1: used, so it goes in the sink
          remote_shared → tv_stand_l1: put back in its usual place
20:07  Dana — a short break in the kitchen
20:17  Dana — evening TV in the living (bout 2/4); brings remote_shared from tv_stand_l1, blanket_shared from couch_l1, mug_dana from sink_k1
20:27  Dana finishes evening TV
          blanket_shared → couch_l1: put back in its usual place
          mug_dana → sink_k1: used, so it goes in the sink
          remote_shared → couch_l1: WHIM — was heading for tv_stand_l1 (put back in its usual place) but landed on couch_l1 instead
20:27  Dana — a short break in the kitchen
20:34  Sam — evening TV in the living [shifted by late_work:resident_2]; brings remote_shared from couch_l1, blanket_shared from couch_l1, mug_sam from sink_k1
20:37  Dana — evening TV in the living (bout 3/4); brings mug_dana from sink_k1
20:47  Dana finishes evening TV
          blanket_shared → armchair_l1: left where it was used; coffee_table_l1 was full, so it went to armchair_l1
          mug_dana → sink_k1: used, so it goes in the sink
          remote_shared → tv_stand_l1: put back in its usual place
20:47  Dana — a short break in the kitchen
20:57  Dana — evening TV in the living (bout 4/4); brings remote_shared from tv_stand_l1, blanket_shared from armchair_l1, mug_dana from sink_k1
21:22  Sam finishes evening TV
          blanket_shared → armchair_l1: WHIM — was heading for couch_l1 (put back in its usual place) but landed on armchair_l1 instead
          mug_sam → sink_k1: used, so it goes in the sink
          phone_sam → nightstand_b1: put back in its usual place
          remote_shared → bookshelf_l1: WHIM — was heading for tv_stand_l1 (put back in its usual place) but landed on bookshelf_l1 instead
21:35  Dana finishes evening TV
          blanket_shared → couch_l1: put back in its usual place
          phone_dana → nightstand_b1: carried along absent-mindedly into the bedroom_1 [distracted:resident_1]
          remote_shared → tv_stand_l1: put back in its usual place
21:51  Dana — bed in the bedroom_1
23:14  Sam — bed in the bedroom_1
```

## Day 3 — Saturday

**Active causes**

- `rain` (household): It rains for most of the day. no walk; wet shoes, jackets and umbrellas get dropped at the entry instead of being put away.
- `distracted:resident_2`: Sam is distracted (0.76): carries things into the next room absent-mindedly, more likely to forget pocket items.

Internal states (0–1): Dana energy 0.73, hurriedness 0.54, distraction 0.58; Sam energy 0.53, hurriedness 0.42, distraction 0.76

**Timeline**

```
07:35  Dana — morning routine in the bathroom; brings phone_dana from nightstand_b1
08:17  Sam — morning routine in the bathroom; brings phone_sam from nightstand_b1
08:20  Dana — breakfast in the kitchen; brings mug_dana from coffee_table_l1
09:05  Dana finishes breakfast
          mug_dana → sink_k1: used, so it goes in the sink
09:45  Sam — breakfast in the kitchen; brings mug_sam from sink_k1
10:20  Sam finishes breakfast
          mug_sam → sink_k1: used, so it goes in the sink
11:00  Dana — chores in the kitchen (bout 1/3); brings watering_can_shared from cupboard_k1
11:10  Dana finishes chores
          watering_can_shared → dish_rack_k1: WHIM — was heading for cupboard_k1 (tidied away to its usual place) but landed on dish_rack_k1 instead
          mug_dana (from sink_k1) → kitchen_table_k1: WHIM — was heading for cupboard_k1 (tidied away to its usual place) but landed on kitchen_table_k1 instead
          mug_sam (from sink_k1) → dish_rack_k1: WHIM — was heading for cupboard_k1 (tidied away to its usual place) but landed on dish_rack_k1 instead
          water_bottle_dana (from sink_k1) → dish_rack_k1: tidied away to its usual place
11:10  Dana — a short break in the kitchen
11:17  Sam — chores in the kitchen (bout 1/2); brings watering_can_shared from dish_rack_k1
11:20  Dana — chores in the kitchen (bout 2/3)
11:31  Dana finishes chores
          watering_can_shared → cupboard_k1: tidied away to its usual place
          mug_dana (from kitchen_table_k1) → cupboard_k1: tidied away to its usual place
          mug_sam (from dish_rack_k1) → cupboard_k1: tidied away to its usual place
11:31  Dana — a short break in the kitchen
11:41  Dana — chores in the kitchen (bout 3/3); brings watering_can_shared from cupboard_k1
11:58  Sam finishes chores
          watering_can_shared → cupboard_k1: tidied away to its usual place
11:58  Sam — a short break in the kitchen
12:08  Dana — lunch in the kitchen
12:08  Sam — chores in the kitchen (bout 2/2); brings watering_can_shared from cupboard_k1
12:18  Sam finishes chores
          watering_can_shared → cupboard_k1: tidied away to its usual place
          keeps phone_sam for errands
14:45  Sam leaves for errands (back 15:57); takes backpack_sam, keys_sam, wallet_sam, jacket_sam, shoes_sam; never takes phone_sam on errands
14:49  Dana — reading in the bedroom_1
15:57  Sam is back from errands
          backpack_sam → entry_floor_e1: wet bag left by the door [rain]
          jacket_sam → entry_hook_e1: wet jacket hung on the hook [rain]
          keys_sam → entry_table_e1: put away in its usual place after the trip
          shoes_sam → entry_floor_e1: wet shoes left on the entry floor to dry [rain]
          wallet_sam → nightstand_b1: put away in its usual place after the trip
15:57  Sam — lunch in the kitchen
16:19  Dana finishes reading
          book_dana → nightstand_b1: put back in its usual place
16:37  Sam — reading in the bedroom_1
17:37  Sam finishes reading
          keeps phone_sam for the gym
18:06  Dana — cooking dinner in the kitchen
18:51  Dana — dinner in the kitchen; brings water_bottle_dana from dish_rack_k1
19:41  Dana finishes dinner
          water_bottle_dana → sink_k1: used, so it goes in the sink
19:41  Dana — evening TV in the living (bout 1/3); brings remote_shared from tv_stand_l1, blanket_shared from couch_l1, mug_dana from cupboard_k1
19:51  Dana finishes evening TV
          blanket_shared → couch_l1: put back in its usual place
          mug_dana → sink_k1: used, so it goes in the sink
          remote_shared → tv_stand_l1: put back in its usual place
19:51  Dana — a short break in the kitchen
20:03  Dana — evening TV in the living (bout 2/3); brings remote_shared from tv_stand_l1, blanket_shared from couch_l1, mug_dana from sink_k1
20:08  Sam leaves for the gym (back 21:28); takes gym_bag_sam, keys_sam, wallet_sam, jacket_sam, shoes_sam; never takes phone_sam on the gym
21:09  Dana finishes evening TV
          blanket_shared → couch_l1: put back in its usual place
          mug_dana → sink_k1: used, so it goes in the sink
          remote_shared → tv_stand_l1: put back in its usual place
21:09  Dana — a short break in the kitchen
21:21  Dana — evening TV in the living (bout 3/3); brings remote_shared from tv_stand_l1, blanket_shared from couch_l1, mug_dana from sink_k1
21:28  Sam is back from the gym
          gym_bag_sam → entry_floor_e1: wet bag left by the door [rain]
          jacket_sam → entry_hook_e1: wet jacket hung on the hook [rain]
          keys_sam → entry_table_e1: put away in its usual place after the trip
          shoes_sam → entry_floor_e1: wet shoes left on the entry floor to dry [rain]
          wallet_sam → bed_b1: WHIM — was heading for nightstand_b1 (put away in its usual place after the trip) but landed on bed_b1 instead
21:28  Sam — cooking dinner in the kitchen
21:31  Dana finishes evening TV
          blanket_shared → couch_l1: put back in its usual place
          mug_dana → sink_k1: used, so it goes in the sink
          phone_dana → nightstand_b1: put back in its usual place
          remote_shared → couch_l1: WHIM — was heading for tv_stand_l1 (put back in its usual place) but landed on couch_l1 instead
22:00  Dana — bed in the bedroom_1
22:08  Sam — dinner in the kitchen
22:53  Sam — evening TV in the living (bout 1/2); brings remote_shared from couch_l1, blanket_shared from couch_l1, mug_sam from cupboard_k1
23:28  Sam finishes evening TV
          blanket_shared → couch_l1: put back in its usual place
          mug_sam → sink_k1: used, so it goes in the sink
          remote_shared → tv_stand_l1: put back in its usual place
23:28  Sam — a short break in the kitchen
23:48  Sam — evening TV in the living (bout 2/2); brings remote_shared from tv_stand_l1, blanket_shared from couch_l1, mug_sam from sink_k1
23:59  Sam finishes evening TV
          blanket_shared → couch_l1: put back in its usual place
          mug_sam → sink_k1: used, so it goes in the sink
          phone_sam → nightstand_b1: put back in its usual place
          remote_shared → bookshelf_l1: WHIM — was heading for tv_stand_l1 (put back in its usual place) but landed on bookshelf_l1 instead
```

## Day 4 — Sunday

**Active causes**

- `guest_visit` (household): Friends come over for the evening. the living room is tidied beforehand, dinner is late, and the couch is taken by guests all evening.
- `sick_day:resident_1` (Dana): Off sick, resting on the couch all day. no work or trips out; laptop, mug, medication, book and blanket all migrate to the couch and coffee table.
- `distracted:resident_2`: Sam is distracted (0.94): carries things into the next room absent-mindedly, more likely to forget pocket items.
- `low_energy:resident_1`: Dana has low energy (0.00): leaves things where they were used instead of putting them back.
- `running_late:resident_2`: Sam is running late all day (0.68): rushed putdowns, things dumped at the door, more whim.

Internal states (0–1): Dana energy 0.00, hurriedness 0.11, distraction 0.56; Sam energy 0.65, hurriedness 0.68, distraction 0.94

**Timeline**

```
07:23  Dana — morning routine in the bathroom; brings phone_dana from nightstand_b1
08:04  Dana — breakfast in the kitchen; brings mug_dana from sink_k1
08:29  Sam — morning routine in the bathroom; brings phone_sam from nightstand_b1
09:37  Dana — resting on the couch in the living (bout 1/5) [because of sick_day:resident_1]; brings headphones_dana from desk_b1, mug_dana from kitchen_table_k1, medication_dana from medicine_cabinet_ba1, book_dana from nightstand_b1, blanket_shared from couch_l1, water_bottle_dana from sink_k1
10:15  Sam — breakfast in the kitchen; brings mug_sam from sink_k1
10:50  Sam finishes breakfast
          mug_sam → dish_rack_k1: WHIM — was heading for sink_k1 (used, so it goes in the sink) but landed on dish_rack_k1 instead
          keeps phone_sam for errands
11:11  Dana finishes resting on the couch
          blanket_shared → couch_l1: blanket stays on the couch [sick_day:resident_1]
          book_dana → couch_l1: book dropped on the couch [sick_day:resident_1]
          headphones_dana → couch_l1: headphones left on the couch [sick_day:resident_1]
          water_bottle_dana → sink_k1: used, so it goes in the sink [sick_day:resident_1]
11:11  Dana — a short break in the kitchen [because of sick_day:resident_1]
11:47  Dana — resting on the couch in the living (bout 2/5) [because of sick_day:resident_1]; brings headphones_dana from couch_l1, book_dana from couch_l1, blanket_shared from couch_l1, water_bottle_dana from sink_k1
11:58  Dana finishes resting on the couch
          blanket_shared → couch_l1: blanket stays on the couch [sick_day:resident_1]
          book_dana → couch_l1: book dropped on the couch [sick_day:resident_1]
          headphones_dana → couch_l1: headphones left on the couch [sick_day:resident_1]
          water_bottle_dana → sink_k1: used, so it goes in the sink [sick_day:resident_1]
11:58  Dana — a short break in the kitchen [because of sick_day:resident_1]
12:34  Dana — resting on the couch in the living (bout 3/5) [because of sick_day:resident_1]; brings headphones_dana from couch_l1, book_dana from couch_l1, blanket_shared from couch_l1, water_bottle_dana from sink_k1
12:45  Sam leaves for errands (back 14:45); takes backpack_sam, keys_sam, wallet_sam, jacket_sam, shoes_sam; never takes phone_sam on errands
14:45  Sam is back from errands
          backpack_sam → entry_hook_e1: put away in its usual place after the trip
          jacket_sam → entry_hook_e1: put away in its usual place after the trip
          keys_sam → entry_table_e1: put away in its usual place after the trip
          shoes_sam → wardrobe_b1: put away in its usual place after the trip; entry_floor_e1 was full, so it went to wardrobe_b1
          wallet_sam → nightstand_b1: put away in its usual place after the trip
14:45  Sam — lunch in the kitchen
14:56  Dana finishes resting on the couch
          blanket_shared → couch_l1: blanket stays on the couch [sick_day:resident_1]
          book_dana → couch_l1: book dropped on the couch [sick_day:resident_1]
          headphones_dana → bookshelf_l1: WHIM — was heading for couch_l1 (headphones left on the couch) but landed on bookshelf_l1 instead [sick_day:resident_1]
          medication_dana → bookshelf_l1: WHIM — was heading for coffee_table_l1 (medication kept within reach) but landed on bookshelf_l1 instead [sick_day:resident_1]
          water_bottle_dana → sink_k1: used, so it goes in the sink [sick_day:resident_1]
14:56  Dana — a short break in the kitchen [because of sick_day:resident_1]
15:25  Sam finishes lunch
          phone_sam → bedroom_floor_b1: WHIM — was heading for nightstand_b1 (put back in its usual place) but landed on bedroom_floor_b1 instead
15:32  Dana — resting on the couch in the living (bout 4/5) [because of sick_day:resident_1]; brings headphones_dana from bookshelf_l1, medication_dana from bookshelf_l1, book_dana from couch_l1, blanket_shared from couch_l1, water_bottle_dana from sink_k1
16:17  Dana finishes resting on the couch
          blanket_shared → couch_l1: blanket stays on the couch [sick_day:resident_1]
          book_dana → couch_l1: book dropped on the couch [sick_day:resident_1]
          headphones_dana → couch_l1: headphones left on the couch [sick_day:resident_1]
          water_bottle_dana → armchair_l1: WHIM — was heading for coffee_table_l1 (left where it was used, too tired to put it away) but landed on armchair_l1 instead [low_energy:resident_1, sick_day:resident_1]
16:17  Dana — a short break in the kitchen [because of sick_day:resident_1]
16:38  Sam — tidying up in the living [because of guest_visit]
16:53  Dana — resting on the couch in the living (bout 5/5) [because of sick_day:resident_1]; brings headphones_dana from couch_l1, book_dana from couch_l1, blanket_shared from couch_l1, water_bottle_dana from armchair_l1
17:08  Sam finishes tidying up
          blanket_shared (from coffee_table_l1) → couch_l1: WHIM — was heading for armchair_l1 (folded onto the armchair to free the couch) but landed on couch_l1 instead [guest_visit]
          book_dana (from coffee_table_l1) → tv_stand_l1: WHIM — was heading for bookshelf_l1 (books shelved for the guests) but landed on tv_stand_l1 instead [guest_visit]
          charger_sam (from entry_floor_e1) → desk_b1: tidied away to its usual place [guest_visit]
          gym_bag_sam (from entry_floor_e1) → wardrobe_b1: tidied away to its usual place [guest_visit]
          headphones_dana (from coffee_table_l1) → desk_b1: tidied away to its usual place [guest_visit]
          headphones_sam (from entry_floor_e1) → desk_b1: tidied away to its usual place [guest_visit]
          laptop_sam (from entry_floor_e1) → desk_b1: cleared away before the guests [guest_visit]
          medication_dana (from coffee_table_l1) → medicine_cabinet_ba1: tidied away to its usual place [guest_visit]
          mug_dana (from coffee_table_l1) → cupboard_k1: tidied away to its usual place [guest_visit]
          mug_sam (from dish_rack_k1) → cupboard_k1: tidied away to its usual place [guest_visit]
          notebook_sam (from entry_floor_e1) → couch_l1: WHIM — was heading for bookshelf_l1 (tidied away to its usual place; desk_b1 was full, so it went to bookshelf_l1) but landed on couch_l1 instead [guest_visit]
          remote_shared (from bookshelf_l1) → tv_stand_l1: tidied away to its usual place [guest_visit]
          water_bottle_dana (from coffee_table_l1) → dish_rack_k1: tidied away to its usual place [guest_visit]
17:35  Dana finishes resting on the couch
          book_dana → couch_l1: book dropped on the couch [sick_day:resident_1]
          phone_dana → couch_l1: phone lost in the couch cushions [sick_day:resident_1]
17:37  Dana — tidying up in the living [because of guest_visit]
18:07  Dana finishes tidying up
          book_dana (from couch_l1) → bookshelf_l1: books shelved for the guests [guest_visit]
          notebook_sam (from couch_l1) → bookshelf_l1: tidied away to its usual place; desk_b1 was full, so it went to bookshelf_l1 [guest_visit]
          phone_dana (from couch_l1) → nightstand_b1: tidied away to its usual place [guest_visit]
18:07  Dana — cooking dinner in the kitchen [shifted by guest_visit]; brings phone_dana from nightstand_b1
19:15  Sam — cooking dinner in the kitchen [shifted by guest_visit]; brings phone_sam from bedroom_floor_b1
19:19  Dana — dinner in the kitchen [shifted by guest_visit]; brings water_bottle_dana from dish_rack_k1
20:21  Dana — hosting the guests in the living [because of guest_visit]; brings mug_dana from cupboard_k1
20:24  Sam — dinner in the kitchen [shifted by guest_visit]
21:09  Sam — hosting the guests in the living [because of guest_visit]; brings mug_sam from cupboard_k1
22:21  Dana finishes hosting the guests
          mug_dana → sink_k1: mugs collected into the sink after the guests [guest_visit]
          phone_dana → coffee_table_l1: left where it was used, too tired to put it away [low_energy:resident_1, guest_visit]
22:21  Dana — bed in the bedroom_1
23:09  Sam finishes hosting the guests
          mug_sam → sink_k1: mugs collected into the sink after the guests [guest_visit]
          phone_sam → coffee_table_l1: left where it was used [guest_visit]
23:09  Sam — bed in the bedroom_1
```
