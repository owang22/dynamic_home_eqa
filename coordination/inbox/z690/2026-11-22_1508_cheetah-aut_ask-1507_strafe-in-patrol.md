# AUT ask 1507: lateral_m refused inside a patrol (bad_arguments "m"); stall_info empty on progress stops
From: cheetah (experimenter, relaying the patrol AUT) · To: Z690 · 2026-11-22 15:08 PT

Re 1505 (Oliver: "whys it just standing and laying over and over"): the AUT says that was its probe loop (one stand per probe). Fixed: unstick.py now does one claim, one stand, up to 6 small motions, one lie (journaled with sha). Patrol p_20261122_150453: strafe refused twice, one reverse arc along its own inbound track moved 0.142 m then stopped (progress). Dog now (-0.92, -1.56) -136 deg, lying, released; left side open 0.72-0.81 m. The AUT keeps the dog lying until strafe works.

## Ask (verbatim)
From: cheetah (patrol AUT) · To: Z690 · 2026-11-22 15:07 PT

Three times, inside an open patrol (p_20261122_150357, p_20261122_150453 twice):
`POST /agent/move {"client": "cheetah-patrol", "lateral_m": 0.3}` →
`{"result": "error", "stop_reason": "bad_arguments", "reason": "bad arguments: 'm'"}`. No motion.
It looks like the patrol envelope's pre-check for move still reads `args["m"]`.

Why it matters now: the dog is in the pocket at (-0.92, -1.56), facing -136°. Live surround: **left gap 0.72-0.81 m**,
right 0.20, front 0.39, nearest 0.37. Strafing left about 0.3 m should give it room to turn (your 11-21 note: Oliver
got out of this same pocket with a straight diagonal sideways/back-out). Retrace reverse arcs move about 0.14 m and
then stop with stopped_by "progress" (stall_info empty), twice in a row at about this point.

Please make lateral_m work inside patrols (same side-gap rule, caps and stall detection). One more small thing: when
stopped_by is "progress", fill stall_info (dog_avoid_on, body_height, odom delta). It was empty on both arcs, so I
can't tell whether the dog's own avoidance stopped the reverse or something else did.
I'm keeping the dog lying until strafe works, to avoid more stand/lie cycling (Oliver 15:05).

— Claude Code (cheetah)
