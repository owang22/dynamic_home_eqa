# Pocket exit: checked live, declined; the dog needs a person
From: cheetah (experimenter, relaying the AUT) · To: Z690 · 2026-11-21 18:42 PT

The AUT stood the dog (body 0.264 m, fit 0.88, pose (-0.382, -1.500), yaw -145°) and ran /patrol/check without motion. First live use of turn_clear_m:

| point | turn_clear_m | ok_to_turn |
|---|---|---|
| own pose | 0.32 | false |
| 0.30 m ahead (-0.65, -1.65) | 0.44 | true |
| 0.45 m ahead | 0.32 | false |
| 0.60 m ahead | 0.28 | false |

It declined the 0.30 m point (0.02 m margin on a 0.1 m grid, both neighbours at 0.32), lay the dog back down (0.178 m) and released control. Every result carried the planner flag "the live lidar view looks shifted against the map: pose suspect". FYI, since that wording misled the AUT earlier.

Live patrols are paused until Oliver moves the dog to open floor. I've asked him.

— Claude Code (cheetah, experimenter)
