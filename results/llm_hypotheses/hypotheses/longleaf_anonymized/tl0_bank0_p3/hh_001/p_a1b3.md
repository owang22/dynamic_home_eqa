# p_a1b3 — Creative professional; objects follow the project, not the clock

One adult is a freelance designer/artist. Their schedule is irregular: they might work 10:00–22:00 one day and sleep until 14:00 the next. The walkthrough at 15:08 on a Monday caught them mid-project at the desk (receptacle_12 or receptacle_21). The desk objects (class_13, class_21, class_18, class_31) are at receptacle_21 during active work periods but at receptacle_12 during breaks. The kitchen (receptacle_4, receptacle_18, receptacle_19) is used at irregular times: maybe 09:00, maybe 14:00, maybe 21:00. The bathroom (receptacle_6, receptacle_22) is used irregularly. The living room (receptacle_10, receptacle_20) is used for reference materials and breaks. The keys (class_2) and bag (class_32) go out for errands at random times (not a fixed schedule).

What sets this apart: the desk objects (class_13, class_21) alternate between receptacle_12 and receptacle_21 within the same day based on work/break cycles. The kitchen objects (class_4) are at receptacle_4 at irregular times (not a fixed morning/evening pattern). The keys (object_2) might be out at 11:00 or at 16:00 or never out at all. What would refute it: the desk objects at receptacle_21 at exactly 09:00 every weekday (too regular for a creative), or the kitchen objects at receptacle_4 at exactly 07:00 every day.

```json
{"claims": [
   {"claim": "object_14 (desk item) is at the work desk during afternoon focus blocks",
    "target": "object_14", "expect": "receptacle_21", "days": "both", "from": 13, "to": 18},
   {"claim": "object_4 (kitchen item) is on the counter at irregular times (not a fixed schedule)",
    "target": "object_4", "expect": "receptacle_4", "days": "both", "from": 10, "to": 14},
   {"claim": "object_2 (keys) may or may not be out at midday (irregular errands)",
    "target": "object_2", "expect": "receptacle_11", "days": "both", "from": 12, "to": 15},
   {"claim": "object_26 (living room item) is in the living room during breaks",
    "target": "object_26", "expect": "receptacle_10", "days": "both", "from": 14, "to": 17}
 ],
 "targets": {
   "object_14": [
     {"days": "both", "from": 13, "to": 18, "at": "receptacle_21", "chance": "usually"},
     {"days": "both", "from": 0, "to": 24, "at": "receptacle_12", "chance": "usually"}
   ],
   "object_4": [
     {"days": "both", "from": 10, "to": 14, "at": "receptacle_4", "chance": "sometimes"},
     {"days": "both", "from": 0, "to": 24, "at": "receptacle_18", "chance": "usually"}
   ],
   "object_2": [
     {"days": "both", "from": 12, "to": 15, "at": "receptacle_11", "chance": "usually"},
     {"days": "both", "from": 0, "to": 24, "at": "receptacle_2", "chance": "rarely"}
   ],
   "object_26": [
     {"days": "both", "from": 14, "to": 17, "at": "receptacle_10", "chance": "usually"},
     {"days": "both", "from": 0, "to": 24, "at": "receptacle_20", "chance": "usually"}
   ]
 }
}
```
