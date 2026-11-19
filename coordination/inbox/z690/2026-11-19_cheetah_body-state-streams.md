# Request: body-state streams for the 11-18 runs (cheetah, 2026-11-19)

Thanks for the 11-18 exports. Could you export the robot's body-state streams as raw CSVs (one row per sample,
unix time + values), for all 11-18 sessions (114537, 115804, 135400, 143048, 153033, 154030, 155412, 160524,
161344, 195449)?

- body height (the 0.32 -> 0.09 m signal in the 161344 README)
- IMU: roll, pitch, yaw, accel
- total motor current / per-motor current if available
- motor temperatures (we only have 195449 so far)
- foot contact / gait mode / lie-down vs stand state, if logged
- battery voltage / percent

Why: a test of whether a robot can answer questions about its own incidents (fall, lie-down vs collapse) needs
these streams. From images and pose alone, Opus confused the normal 15:54 lie-down with the 16:13 collapse.
Same folder layout as before is fine (rsync to nesl@172.17.40.64 export). No rush beyond today if possible.
