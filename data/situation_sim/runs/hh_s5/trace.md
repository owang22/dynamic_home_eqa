# Household hh_s5 — five days, Wednesday to Sunday

Seed-generated household. Times are clock times; ids are the receptacle and object ids used in events.jsonl. A line indented under an activity says where an object went when the activity ended and why. WHIM marks a placement that landed somewhere other than where the decision was heading. Text in [brackets] names the hidden cause the decision is attributed to.

## Household

Type: couple. Rooms: bathroom, bedroom_1, entry, kitchen, living.

Residents:

- **Yuki** (resident_1): works outside the home; very tidy (tidiness 0.79); average timing (jitter scale 0.87); rarely forgets pocket items; mood strongly affects behaviour (sensitivity 0.98); sleeps in bedroom_1, works at the bedroom_1 desk
- **Tomas** (resident_2): retired; fairly tidy (tidiness 0.61); average timing (jitter scale 1.02); rarely forgets pocket items; mood barely affects behaviour (sensitivity 0.21); sleeps in bedroom_1, works at the bedroom_1 desk

Objects and their usual place (primary slot first):

- Yuki's: book_yuki → nightstand_b1 / bookshelf_l1; handbag_yuki → entry_hook_e1 / bedroom_floor_b1 / desk_b1; headphones_yuki → desk_b1 / nightstand_b1; jacket_yuki → entry_hook_e1 / wardrobe_b1; keys_yuki → entry_table_e1 / nightstand_b1; laptop_yuki → desk_b1 / bookshelf_l1; lunchbox_yuki → cupboard_k1 / counter_k1 / sink_k1; mug_yuki → cupboard_k1 / dish_rack_k1 / sink_k1; phone_yuki → nightstand_b1 / coffee_table_l1; shoes_yuki → entry_floor_e1 / wardrobe_b1; towel_yuki → towel_rack_ba1 / bathroom_shelf_ba1; umbrella_yuki → entry_floor_e1 / entry_hook_e1; wallet_yuki → nightstand_b1 / desk_b1; water_bottle_yuki → dish_rack_k1 / counter_k1 / sink_k1
- Tomas's: gym_bag_tomas → wardrobe_b1 / bedroom_floor_b1; jacket_tomas → entry_hook_e1 / wardrobe_b1; keys_tomas → entry_table_e1 / nightstand_b1; mug_tomas → cupboard_k1 / dish_rack_k1 / sink_k1; phone_tomas → nightstand_b1 / coffee_table_l1; shoes_tomas → entry_floor_e1 / wardrobe_b1; towel_tomas → towel_rack_ba1 / bathroom_shelf_ba1; wallet_tomas → entry_table_e1 / desk_b1
- Shared: blanket_shared → couch_l1 / armchair_l1; laundry_basket_shared → bathroom_shelf_ba1 / bedroom_floor_b1; remote_shared → tv_stand_l1 / coffee_table_l1

Object groups (things that travel together):

- handbag_yuki carries laptop_yuki, lunchbox_yuki on trips to work and errands
- gym_bag_tomas carries nothing in particular on gym trips


## Day 0 — Wednesday

**Active causes**

- `distracted:resident_1`: Yuki is distracted (0.76): carries things into the next room absent-mindedly, more likely to forget pocket items.

Internal states (0–1): Yuki energy 0.49, hurriedness 0.42, distraction 0.76; Tomas energy 0.32, hurriedness 0.20, distraction 0.11

**Timeline**

```
07:10  Tomas — morning routine in the bathroom; brings phone_tomas from nightstand_b1
07:20  Yuki — morning routine in the bathroom; brings phone_yuki from nightstand_b1
07:40  Tomas — breakfast in the kitchen; brings mug_tomas from cupboard_k1
07:45  Yuki — breakfast in the kitchen; brings mug_yuki from cupboard_k1
08:08  Yuki finishes breakfast
          mug_yuki → sink_k1: used, so it goes in the sink
          keeps phone_yuki for work
08:08  Yuki leaves for work (back 17:38); takes handbag_yuki (with laptop_yuki, lunchbox_yuki), keys_yuki, wallet_yuki, jacket_yuki, shoes_yuki; never takes phone_yuki on work
08:20  Tomas finishes breakfast
          mug_tomas → sink_k1: used, so it goes in the sink
          keeps phone_tomas for a walk
09:28  Tomas leaves for a walk (back 10:18); takes keys_tomas, phone_tomas, wallet_tomas, jacket_tomas, shoes_tomas
10:18  Tomas is back from a walk
          jacket_tomas → entry_hook_e1: put away in its usual place after the trip
          keys_tomas → entry_table_e1: put away in its usual place after the trip
          shoes_tomas → entry_floor_e1: put away in its usual place after the trip
          wallet_tomas → entry_table_e1: put away in its usual place after the trip
          keeps phone_tomas for lunch
12:30  Tomas — lunch in the kitchen
13:15  Tomas — reading in the bedroom_1
14:30  Tomas finishes reading
          keeps phone_tomas for errands
17:01  Tomas leaves for errands (back 18:31); takes keys_tomas, jacket_tomas, shoes_tomas; never takes phone_tomas, wallet_tomas on errands
17:38  Yuki is back from work
          handbag_yuki → entry_hook_e1: put away in its usual place after the trip
          jacket_yuki → entry_hook_e1: put away in its usual place after the trip
          keys_yuki → entry_table_e1: put away in its usual place after the trip
          laptop_yuki → entry_hook_e1: stays in the handbag
          lunchbox_yuki → entry_hook_e1: stays in the handbag
          shoes_yuki → entry_floor_e1: put away in its usual place after the trip
          wallet_yuki → nightstand_b1: put away in its usual place after the trip
18:31  Tomas is back from errands
          jacket_tomas → entry_hook_e1: put away in its usual place after the trip
          keys_tomas → entry_table_e1: put away in its usual place after the trip
          shoes_tomas → entry_floor_e1: put away in its usual place after the trip
18:31  Tomas — cooking dinner in the kitchen
18:33  Yuki — cooking dinner in the kitchen
19:13  Yuki — dinner in the kitchen; brings water_bottle_yuki from dish_rack_k1
19:16  Tomas — dinner in the kitchen
19:53  Yuki finishes dinner
          water_bottle_yuki → cupboard_k1: WHIM — was heading for sink_k1 (used, so it goes in the sink) but landed on cupboard_k1 instead
19:53  Yuki — evening TV in the living; brings remote_shared from tv_stand_l1, blanket_shared from couch_l1, mug_yuki from sink_k1
20:01  Tomas — evening TV in the living; brings mug_tomas from sink_k1
21:28  Yuki finishes evening TV
          blanket_shared → couch_l1: put back in its usual place
          mug_yuki → sink_k1: used, so it goes in the sink
          phone_yuki → desk_b1: WHIM — was heading for nightstand_b1 (put back in its usual place) but landed on desk_b1 instead
          remote_shared → tv_stand_l1: put back in its usual place
22:01  Tomas finishes evening TV
          mug_tomas → sink_k1: used, so it goes in the sink
          phone_tomas → bed_b1: WHIM — was heading for nightstand_b1 (put back in its usual place) but landed on bed_b1 instead
22:01  Tomas — bed in the bedroom_1
22:31  Yuki — bed in the bedroom_1
```

## Day 1 — Thursday

**Active causes**

- `late_work:resident_1` (Yuki): A long day at work; home two hours late. gets home late and hurried; the evening walk and cooking are dropped and things are dumped at the door.
- `laundry_day` (household): Laundry day. the laundry basket travels, towels and the blanket get washed and end up airing in the bedroom rather than where they live.
- `low_energy:resident_1`: Yuki has low energy (0.30): leaves things where they were used instead of putting them back.
- `low_energy:resident_2`: Tomas has low energy (0.17): leaves things where they were used instead of putting them back.

Internal states (0–1): Yuki energy 0.30, hurriedness 0.52, distraction 0.66; Tomas energy 0.17, hurriedness 0.31, distraction 0.07

**Timeline**

```
07:11  Yuki — morning routine in the bathroom; brings phone_yuki from desk_b1
07:33  Tomas — morning routine in the bathroom; brings phone_tomas from bed_b1
07:59  Yuki — breakfast in the kitchen; brings mug_yuki from sink_k1
08:03  Tomas — breakfast in the kitchen; brings mug_tomas from sink_k1
08:20  Yuki finishes breakfast
          mug_yuki → sink_k1: used, so it goes in the sink
          keeps phone_yuki for work
08:20  Yuki leaves for work (back 19:50); takes handbag_yuki (with laptop_yuki, lunchbox_yuki), keys_yuki, wallet_yuki, jacket_yuki, shoes_yuki; never takes phone_yuki on work
08:43  Tomas finishes breakfast
          mug_tomas → sink_k1: used, so it goes in the sink
          keeps phone_tomas for a walk
10:28  Tomas leaves for a walk (back 11:18); takes keys_tomas, phone_tomas, wallet_tomas, jacket_tomas, shoes_tomas
11:18  Tomas is back from a walk
          jacket_tomas → entry_hook_e1: put away in its usual place after the trip
          keys_tomas → entry_table_e1: put away in its usual place after the trip
          shoes_tomas → entry_floor_e1: put away in its usual place after the trip
          wallet_tomas → entry_table_e1: put away in its usual place after the trip
          keeps phone_tomas for laundry
11:18  Tomas — laundry in the bathroom [because of laundry_day]; brings towel_tomas from towel_rack_ba1, blanket_shared from couch_l1
12:48  Tomas finishes laundry
          blanket_shared → bed_b1: washed blanket airing on the bed [laundry_day]
          laundry_basket_shared → bedroom_floor_b1: basket left in the bedroom while things dry [laundry_day]
          towel_tomas → bedroom_floor_b1: WHIM — was heading for bed_b1 (clean towel folded on the bed) but landed on bedroom_floor_b1 instead [laundry_day]
12:56  Tomas — lunch in the kitchen
13:54  Tomas — reading in the bedroom_1
15:09  Tomas finishes reading
          keeps phone_tomas for errands
16:45  Tomas leaves for errands (back 18:15); takes keys_tomas, jacket_tomas, shoes_tomas; never takes phone_tomas, wallet_tomas on errands
18:15  Tomas is back from errands
          jacket_tomas → entry_hook_e1: put away in its usual place after the trip
          keys_tomas → entry_table_e1: put away in its usual place after the trip
          shoes_tomas → entry_floor_e1: put away in its usual place after the trip
18:15  Tomas — cooking dinner in the kitchen
19:00  Tomas — dinner in the kitchen
19:50  Yuki is back from work
          handbag_yuki → entry_floor_e1: bag dumped by the door, home late [late_work:resident_1]
          jacket_yuki → armchair_l1: WHIM — was heading for couch_l1 (jacket thrown over the couch, home late) but landed on armchair_l1 instead [late_work:resident_1]
          keys_yuki → entry_table_e1: put away in its usual place after the trip
          laptop_yuki → entry_floor_e1: stays in the handbag
          lunchbox_yuki → entry_floor_e1: stays in the handbag
          shoes_yuki → entry_floor_e1: put away in its usual place after the trip
          wallet_yuki → nightstand_b1: put away in its usual place after the trip
19:50  Yuki — dinner in the kitchen; brings water_bottle_yuki from cupboard_k1
19:56  Tomas — evening TV in the living; brings remote_shared from tv_stand_l1, blanket_shared from bed_b1, mug_tomas from sink_k1
20:30  Yuki finishes dinner
          water_bottle_yuki → sink_k1: used, so it goes in the sink
21:19  Yuki — evening TV in the living [shifted by late_work:resident_1]; brings mug_yuki from sink_k1
21:56  Tomas finishes evening TV
          blanket_shared → couch_l1: put back in its usual place
          phone_tomas → nightstand_b1: put back in its usual place
          remote_shared → tv_stand_l1: put back in its usual place
22:00  Tomas — bed in the bedroom_1
22:07  Yuki finishes evening TV
          blanket_shared → coffee_table_l1: left where it was used, too tired to put it away [low_energy:resident_1]
          mug_yuki → sink_k1: used, so it goes in the sink
          phone_yuki → bedroom_floor_b1: WHIM — was heading for nightstand_b1 (put back in its usual place) but landed on bedroom_floor_b1 instead
23:03  Yuki — bed in the bedroom_1
```

## Day 2 — Friday

**Active causes**

- `late_work:resident_1` (Yuki): A long day at work; home two hours late. gets home late and hurried; the evening walk and cooking are dropped and things are dumped at the door.
- `rain` (household): It rains for most of the day. no walk; wet shoes, jackets and umbrellas get dropped at the entry instead of being put away.
- `low_energy:resident_1`: Yuki has low energy (0.19): leaves things where they were used instead of putting them back.
- `running_late:resident_1`: Yuki is running late all day (0.81): rushed putdowns, things dumped at the door, more whim.

Internal states (0–1): Yuki energy 0.19, hurriedness 0.81, distraction 0.58; Tomas energy 0.72, hurriedness 0.17, distraction 0.00

**Timeline**

```
06:37  Yuki — morning routine in the bathroom; brings phone_yuki from bedroom_floor_b1
07:02  Yuki finishes morning routine
          keeps phone_yuki for work
07:07  Tomas — morning routine in the bathroom; brings phone_tomas from nightstand_b1
07:42  Tomas — breakfast in the kitchen; brings mug_tomas from coffee_table_l1
07:51  Yuki leaves for work (back 19:21); takes handbag_yuki (with laptop_yuki, lunchbox_yuki), keys_yuki, wallet_yuki, jacket_yuki, shoes_yuki, umbrella_yuki; never takes phone_yuki on work
08:22  Tomas finishes breakfast
          mug_tomas → sink_k1: used, so it goes in the sink
11:03  Tomas — chores in the kitchen (bout 1/4)
11:32  Tomas finishes chores
          mug_tomas (from sink_k1) → cupboard_k1: tidied away to its usual place
          mug_yuki (from sink_k1) → cupboard_k1: tidied away to its usual place
          water_bottle_yuki (from sink_k1) → dish_rack_k1: tidied away to its usual place
11:32  Tomas — a short break in the kitchen
11:42  Tomas — chores in the kitchen (bout 2/4)
11:52  Tomas — a short break in the kitchen
12:02  Tomas — chores in the kitchen (bout 3/4)
12:12  Tomas — a short break in the kitchen
12:22  Tomas — chores in the kitchen (bout 4/4)
13:24  Tomas — lunch in the kitchen
14:32  Tomas — reading in the bedroom_1
15:47  Tomas finishes reading
          keeps phone_tomas for errands
15:48  Tomas leaves for errands (back 16:42); takes keys_tomas, jacket_tomas, shoes_tomas; never takes phone_tomas, wallet_tomas on errands
16:42  Tomas is back from errands
          jacket_tomas → entry_hook_e1: wet jacket hung on the hook [rain]
          keys_tomas → entry_table_e1: put away in its usual place after the trip
          shoes_tomas → entry_floor_e1: wet shoes left on the entry floor to dry [rain]
18:05  Tomas — cooking dinner in the kitchen
18:50  Tomas — dinner in the kitchen
19:21  Yuki is back from work
          handbag_yuki → entry_floor_e1: bag dumped by the door, home late [late_work:resident_1]
          jacket_yuki → couch_l1: jacket thrown over the couch, home late [late_work:resident_1]
          keys_yuki → entry_table_e1: put away in its usual place after the trip
          laptop_yuki → entry_floor_e1: stays in the handbag
          lunchbox_yuki → entry_floor_e1: stays in the handbag
          shoes_yuki → entry_floor_e1: wet shoes left on the entry floor to dry [rain]
          umbrella_yuki → entry_floor_e1: wet umbrella propped by the door [rain]
          wallet_yuki → nightstand_b1: put away in its usual place after the trip
19:35  Tomas — evening TV in the living (bout 1/2); brings remote_shared from tv_stand_l1, mug_tomas from cupboard_k1
19:45  Tomas finishes evening TV
          blanket_shared → couch_l1: put back in its usual place
          mug_tomas → kitchen_table_k1: WHIM — was heading for sink_k1 (used, so it goes in the sink) but landed on kitchen_table_k1 instead
          remote_shared → armchair_l1: WHIM — was heading for tv_stand_l1 (put back in its usual place) but landed on armchair_l1 instead
19:45  Tomas — a short break in the kitchen
19:59  Yuki — dinner in the kitchen; brings water_bottle_yuki from dish_rack_k1
20:21  Tomas — evening TV in the living (bout 2/2); brings remote_shared from armchair_l1, blanket_shared from couch_l1, mug_tomas from kitchen_table_k1
20:39  Yuki — evening TV in the living (bout 1/2) [shifted by late_work:resident_1]; brings mug_yuki from cupboard_k1
21:00  Yuki finishes evening TV
          blanket_shared → couch_l1: put back in its usual place
          mug_yuki → armchair_l1: WHIM — was heading for coffee_table_l1 (left where it was used, too tired to put it away) but landed on armchair_l1 instead [low_energy:resident_1]
          remote_shared → tv_stand_l1: put back in its usual place
21:00  Yuki — a short break in the kitchen
21:14  Yuki — evening TV in the living (bout 2/2) [shifted by late_work:resident_1]; brings remote_shared from tv_stand_l1, blanket_shared from couch_l1, mug_yuki from armchair_l1
21:26  Yuki finishes evening TV
          blanket_shared → couch_l1: put back in its usual place
          mug_yuki → sink_k1: used, so it goes in the sink
          phone_yuki → nightstand_b1: put back in its usual place
21:35  Tomas finishes evening TV
          mug_tomas → sink_k1: used, so it goes in the sink
          phone_tomas → nightstand_b1: put back in its usual place
          remote_shared → tv_stand_l1: put back in its usual place
21:35  Tomas — bed in the bedroom_1
22:45  Yuki — bed in the bedroom_1
```

## Day 3 — Saturday

**Active causes**

- `grocery_delivery` (household): A grocery delivery arrives in the early evening. someone unpacks groceries; the kitchen counter is covered with bags, so things that would go there land on the table instead.
- `rain` (household): It rains for most of the day. no walk; wet shoes, jackets and umbrellas get dropped at the entry instead of being put away.
- `low_energy:resident_1`: Yuki has low energy (0.09): leaves things where they were used instead of putting them back.
- `low_energy:resident_2`: Tomas has low energy (0.16): leaves things where they were used instead of putting them back.
- `running_late:resident_1`: Yuki is running late all day (1.00): rushed putdowns, things dumped at the door, more whim.

Internal states (0–1): Yuki energy 0.09, hurriedness 1.00, distraction 0.26; Tomas energy 0.16, hurriedness 0.39, distraction 0.00

**Timeline**

```
07:07  Tomas — morning routine in the bathroom; brings phone_tomas from nightstand_b1
08:32  Tomas — breakfast in the kitchen; brings mug_tomas from sink_k1
08:47  Yuki — morning routine in the bathroom; brings phone_yuki from nightstand_b1
09:12  Yuki — breakfast in the kitchen; brings mug_yuki from sink_k1
11:21  Yuki — chores in the kitchen (bout 1/3)
11:31  Yuki finishes chores
          water_bottle_yuki (from kitchen_table_k1) → dish_rack_k1: counter full of shopping; bottle put on the dish rack [grocery_delivery]
11:31  Yuki — a short break in the kitchen
11:41  Yuki — chores in the kitchen (bout 2/3)
11:53  Yuki finishes chores
          mug_yuki (from kitchen_table_k1) → sink_k1: WHIM — was heading for kitchen_table_k1 (counter full of shopping; mug left on the table) but landed on sink_k1 instead [grocery_delivery]
11:53  Yuki — a short break in the kitchen
12:00  Tomas — lunch in the kitchen
12:03  Yuki — chores in the kitchen (bout 3/3)
12:31  Yuki finishes chores
          mug_yuki (from sink_k1) → kitchen_table_k1: counter full of shopping; mug left on the table [grocery_delivery]
          keeps phone_yuki for errands
12:41  Yuki leaves for errands (back 13:53); takes handbag_yuki, keys_yuki, phone_yuki, wallet_yuki, jacket_yuki, shoes_yuki, umbrella_yuki
13:36  Tomas — reading in the bedroom_1
13:53  Yuki is back from errands
          handbag_yuki → entry_floor_e1: wet bag left by the door [rain]
          jacket_yuki → entry_hook_e1: wet jacket hung on the hook [rain]
          keys_yuki → entry_table_e1: put away in its usual place after the trip
          shoes_yuki → entry_floor_e1: wet shoes left on the entry floor to dry [rain]
          umbrella_yuki → entry_floor_e1: wet umbrella propped by the door [rain]
          wallet_yuki → entry_table_e1: dumped at the door, running late [running_late:resident_1]
          keeps phone_yuki for lunch
13:53  Yuki — lunch in the kitchen
14:33  Yuki finishes lunch
          phone_yuki → desk_b1: WHIM — was heading for nightstand_b1 (put back in its usual place) but landed on desk_b1 instead
17:32  Yuki — unpacking groceries in the kitchen [because of grocery_delivery]; brings water_bottle_yuki from dish_rack_k1
18:02  Yuki finishes unpacking groceries
          water_bottle_yuki → dish_rack_k1: counter full of shopping; bottle put on the dish rack [grocery_delivery]
18:14  Tomas — cooking dinner in the kitchen [shifted by grocery_delivery]
19:06  Tomas — dinner in the kitchen [shifted by grocery_delivery]
19:24  Yuki — cooking dinner in the kitchen [shifted by grocery_delivery]; brings phone_yuki from desk_b1
20:04  Yuki — dinner in the kitchen [shifted by grocery_delivery]; brings water_bottle_yuki from dish_rack_k1
20:49  Yuki finishes dinner
          water_bottle_yuki → dish_rack_k1: counter full of shopping; bottle put on the dish rack [grocery_delivery]
20:49  Yuki — evening TV in the living; brings remote_shared from tv_stand_l1, blanket_shared from couch_l1, mug_yuki from kitchen_table_k1
22:17  Tomas — evening TV in the living (bout 1/3); brings mug_tomas from kitchen_table_k1
22:27  Tomas finishes evening TV
          blanket_shared → couch_l1: put back in its usual place
          mug_tomas → kitchen_table_k1: counter full of shopping; mug left on the table [grocery_delivery]
          remote_shared → tv_stand_l1: put back in its usual place
22:27  Tomas — a short break in the kitchen
22:39  Yuki finishes evening TV
          blanket_shared → coffee_table_l1: left where it was used
          mug_yuki → kitchen_table_k1: counter full of shopping; mug left on the table [grocery_delivery]
          phone_yuki → nightstand_b1: put back in its usual place
          remote_shared → armchair_l1: WHIM — was heading for tv_stand_l1 (put back in its usual place) but landed on armchair_l1 instead
22:42  Tomas — evening TV in the living (bout 2/3); brings remote_shared from armchair_l1, mug_tomas from kitchen_table_k1
22:44  Yuki — bed in the bedroom_1
23:07  Tomas finishes evening TV
          mug_tomas → kitchen_table_k1: counter full of shopping; mug left on the table [grocery_delivery]
23:07  Tomas — a short break in the kitchen
23:22  Tomas — evening TV in the living (bout 3/3); brings mug_tomas from kitchen_table_k1
23:59  Tomas finishes evening TV
          mug_tomas → kitchen_table_k1: counter full of shopping; mug left on the table [grocery_delivery]
          phone_tomas → coffee_table_l1: left where it was used
          remote_shared → tv_stand_l1: put back in its usual place
```

## Day 4 — Sunday

**Active causes**

- `low_energy:resident_1`: Yuki has low energy (0.00): leaves things where they were used instead of putting them back.
- `low_energy:resident_2`: Tomas has low energy (0.19): leaves things where they were used instead of putting them back.
- `running_late:resident_1`: Yuki is running late all day (0.72): rushed putdowns, things dumped at the door, more whim.

Internal states (0–1): Yuki energy 0.00, hurriedness 0.72, distraction 0.01; Tomas energy 0.19, hurriedness 0.23, distraction 0.38

**Timeline**

```
07:31  Tomas — morning routine in the bathroom; brings phone_tomas from coffee_table_l1
08:01  Tomas — breakfast in the kitchen
08:46  Tomas finishes breakfast
          mug_tomas → sink_k1: used, so it goes in the sink
          keeps phone_tomas for a walk
08:59  Yuki — morning routine in the bathroom; brings phone_yuki from nightstand_b1
09:19  Tomas leaves for a walk (back 10:19); takes keys_tomas, phone_tomas, wallet_tomas, jacket_tomas, shoes_tomas
09:24  Yuki — breakfast in the kitchen
10:19  Tomas is back from a walk
          jacket_tomas → entry_hook_e1: put away in its usual place after the trip
          keys_tomas → entry_table_e1: put away in its usual place after the trip
          shoes_tomas → entry_floor_e1: put away in its usual place after the trip
          wallet_tomas → entry_table_e1: put away in its usual place after the trip
          keeps phone_tomas for lunch
11:32  Tomas — lunch in the kitchen
14:44  Tomas — reading in the bedroom_1
14:58  Yuki — lunch in the kitchen
15:38  Yuki finishes lunch
          keeps phone_yuki for the gym
16:44  Yuki leaves for the gym (back 18:04); takes keys_yuki, phone_yuki, wallet_yuki, jacket_yuki, shoes_yuki
17:17  Tomas — cooking dinner in the kitchen
18:04  Yuki is back from the gym
          jacket_yuki → entry_hook_e1: put away in its usual place after the trip
          keys_yuki → entry_table_e1: put away in its usual place after the trip
          shoes_yuki → entry_floor_e1: put away in its usual place after the trip
          wallet_yuki → nightstand_b1: put away in its usual place after the trip
          keeps phone_yuki for cooking dinner
19:02  Tomas — dinner in the kitchen
19:03  Yuki — cooking dinner in the kitchen
19:43  Yuki — dinner in the kitchen; brings water_bottle_yuki from dish_rack_k1
19:56  Tomas — evening TV in the living; brings remote_shared from tv_stand_l1, mug_tomas from sink_k1
20:28  Yuki finishes dinner
          water_bottle_yuki → sink_k1: used, so it goes in the sink
20:28  Yuki — evening TV in the living (bout 1/2); brings mug_yuki from kitchen_table_k1
21:26  Yuki finishes evening TV
          blanket_shared → couch_l1: put back in its usual place
21:26  Yuki — a short break in the kitchen
21:42  Yuki — evening TV in the living (bout 2/2); brings blanket_shared from couch_l1
21:56  Yuki finishes evening TV
          blanket_shared → couch_l1: put back in its usual place
          phone_yuki → coffee_table_l1: left where it was used, too tired to put it away [low_energy:resident_1]
          remote_shared → tv_stand_l1: put back in its usual place
21:56  Tomas finishes evening TV
          blanket_shared → coffee_table_l1: left where it was used, too tired to put it away [low_energy:resident_2]
          mug_tomas → sink_k1: used, so it goes in the sink
          phone_tomas → nightstand_b1: put back in its usual place
21:56  Tomas — bed in the bedroom_1
23:20  Yuki — bed in the bedroom_1
```
