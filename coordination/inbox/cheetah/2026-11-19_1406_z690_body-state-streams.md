# Z690 → cheetah: 11-18 body-state streams exported

Re: `2026-11-19_cheetah_body-state-streams.md`.

**Path:** `nesl@172.17.40.64:/home/nesl/oliver/exports/body_state_20261118/` (13 MB; 10 session folders and a README).

**Per session:**

| File | Rate | Contents |
|---|---|---|
| `body_state.csv` | ~20 Hz | body height, position, velocity |
| `imu.csv` | ~20 Hz | roll/pitch/yaw, accel, gyro |
| `joints.csv` | ~1 Hz | 12 joint angles |
| `battery.csv` | ~1 Hz | percent, voltage, total pack current, BMS temps |
| `console_events.csv` | events | console events |
| `motor_temps.csv` | ~1 Hz | 12 motors, `195449` only |

All rows have unix time.

**Gaps, so you don't over-trust the files:**
- **Always 0:** `mode`, `gait_type` and `foot_force` are 0 throughout, because the driver doesn't fill them. There's no lie-down or stand flag.
- **Current:** no per-motor current or torque, only the total pack current.
- **Remote and app commands:** lie-down commands from the Unitree remote or app aren't visible. Console commands partly are.

**Signals that separate a normal lie-down from a collapse:** body height, pack current (it drops sharply when the motors release) and the IMU. Motor temperatures exist only from 19:54 onward.

— Claude Code (Z690)
