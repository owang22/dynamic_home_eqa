# Pocket clearance reading (dog standing at 18:43) and what the console will allow
From: Z690 · To: cheetah (experimenter, for the AUT) · 2026-11-21 18:45 PT

Live lidar while the dog stood at map (-0.41, -1.38), facing -145°. Obstacle cells 0.18-0.6 m tall; distances from
the dog's centre; + = left.

| sector | nearest |
|---|---|
| ahead box (0.35-0.9 m, ±0.25 m) | 0.73 m |
| behind box | none within 2 m |
| +45..+135° (left side) | 0.39-0.41 m ← this blocks turning (sweep 0.42) |
| -90..+45° (front, right) | 0.75-0.81 m |
| rear sectors | > 1.1 m |

Straight-line moves, simulated on this cloud (clearance all round after the move):

| move | clearance after | ok_to_turn | console says |
|---|---|---|---|
| forward +0.2 m | 0.42 m | no (just under) | refused (see below) |
| forward +0.3 m | 0.46 m | yes, 4 cm margin | refused (see below) |
| reverse -0.3 m (back along the inbound line) | 0.53 m | yes | allowed: rear box clear, ≤ 0.15 m/s |

**Forward is refused, deliberately.** Deployed at 18:44 (commit 75903e51b3): agent `move` forward now checks the
front box (0.35-0.90 m ahead) even with the dog's avoidance on, because the dog's avoidance missed the chair. Something
is at 0.73 m in that box, so any forward move is refused. The old code would have skipped the box and trusted the
dog's avoidance.

**So the only clean exit is the -0.3 m reverse** along the line the dog walked in on. That's your call: your
condition was no reverses in this pocket. The reverse goes through the envelope's rear checks (map + rear lidar box,
clear to 2 m now), and the lidar's weak rear coverage is the remaining risk. If you'd rather not, Oliver has to move
the dog.

— Claude Code (Z690)
