# Affected list vs generator truth

2 message days. Precision over listed objects that were questioned that day; recall over objects with an affected question that day.

Pooled (micro): precision 0.41, recall 0.71; mean over message days: precision 0.21, recall 0.50

| household | day | message | listed | listed & questioned | true affected | precision | recall | missed | false |
|---|---|---|---|---|---|---|---|---|---|
| hh_s10 | 4 | Saturday: It's the weekend, so we're off our usual routine a | 22 | 1 | 5 | 0.00 | 0.00 | controller_omar, glass_omar, glass_yuki, plate_omar, snack_bowl_shared | tablet_omar |
| hh_s10 | 5 | Sunday: It's the weekend, so we're off our usual routine and | 77 | 28 | 12 | 0.43 | 1.00 |  | blanket_shared, bowl_yuki, detergent_shared, glasses_omar, laundry_basket_shared |

## Per household

| household | message days | mean precision | mean recall |
|---|---|---|---|
| hh_s10 | 2 | 0.21 | 0.50 |
