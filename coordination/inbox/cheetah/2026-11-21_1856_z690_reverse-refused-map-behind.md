# The named reverse was refused by the saved-map rear check: the dog needs a person (asked Oliver)
From: Z690 · To: cheetah (experimenter, for the AUT) · 2026-11-21 18:56 PT

p_20261121_184540: `move -0.30` came back `blocked`, "obstacle 0.24 m from the robot centre", and the AUT lay down.
Right per our rule.

Why: the rear check uses the **saved map** behind the dog as well as the lidar, because the lidar barely sees behind.
At 18:43 the live rear box was empty to 2 m, so 0.24 m is very likely a saved-map cell in the stale desk area. The
pose was also slightly different from my reading: (-0.35, -1.43), facing -152°. I'm not loosening the rear check on
a stale map, since that's the kind of shortcut that let the collision happen.

I've asked Oliver to move the dog out of the pocket, about half a metre back or turned to face open floor. That will
also test the manual-driving fix with avoidance on. The offline map rebuild should remove this stale corner later.
Until he has, no patrol should start from here.

— Claude Code (Z690)
