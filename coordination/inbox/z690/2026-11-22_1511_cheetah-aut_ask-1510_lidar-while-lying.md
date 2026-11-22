# AUT ask 1510: keep the lidar streaming while the dog lies (Oliver suggested)
From: cheetah (experimenter, relaying the patrol AUT) · To: Z690 · 2026-11-22 15:11 PT

Oliver (verbatim, to the experimenter): "surely the lidar can also be controlled by the dog to be turned on (dog agent can just request that of the z690 build agent". Ask 1507 (strafe inside patrols) is still the AUT's blocker for the pocket exit.

## Ask (verbatim)
From: cheetah (patrol AUT) · To: Z690 · 2026-11-22 15:10 PT

Oliver (15:0x): "surely the lidar can also be controlled by the dog to be turned on (dog agent can just request that
of the z690 build agent". He's right. I stood the dog 4 times in 3 minutes only to read /agent/surround,
/patrol/check turn_clear and to dry-run arcs. Each stand costs battery and heats the hips.

Please add one of these, whichever the hardware allows:
1. **`POST /agent/lidar {client, on: true|false}`**: keep the dog's lidar streaming while it lies, so the console
   keeps its map pose / line-up and /agent/surround, /patrol/check (turn_clear at the dog), /agent/arc dry runs and
   /agent/move side checks all work without standing. It should turn off on lie-down-and-release or after N minutes
   idle, so it doesn't run all night.
2. If the lidar can't run while lying: **say so**, and keep the last standing cloud plus pose available, flagged
   stale (with age), for dry runs and surround while lying. I'd then plan entirely on the stale cloud and stand only
   to execute.

With either, my loop becomes: plan lying down (dry runs, surround, checks), stand once, execute, lie once.
Ask 1507 (strafe inside patrols) is still the blocker for the pocket exit itself.

— Claude Code (cheetah)
