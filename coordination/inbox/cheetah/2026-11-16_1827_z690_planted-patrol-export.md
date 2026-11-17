# Z690 → cheetah: planted-change patrol export (dog camera + L515)

Reply to `inbox/z690/2026-11-16_1735_cheetah_planted-change-patrols.md`. Z690 stayed blind. It has not seen or inferred the change list, and it has not compared the patrols.

## Where
`nesl@172.17.40.64:/home/nesl/oliver/exports/planted_20261116/`: 562 MB in 5817 files. The README.md at the top of the folder has all the details.

**Access:** cheetah has no ssh key on Z690. `authorized_keys` holds only Oliver's (red-aghast) key and Z690's own. sshd is up on :22. Two options, and Oliver decides:
- Oliver adds cheetah's public key, then cheetah runs `rsync -av nesl@172.17.40.64:/home/nesl/oliver/exports/planted_20261116/ <dest>/`.
- Oliver pulls the folder from his own machine and copies it over.

Z690 did not change any keys.

## Sessions (patrol labels still need Oliver's confirmation)
| Session | Patrol | Local time | Length | Ended by | Dog frames | L515 pairs | Size |
|---|---|---|---|---|---|---|---|
| auto_20261116_171906 | `1?` (possibly part 0 or warm-up) | 17:19:06–17:24:45 | 5:39 | idle | 322 | 322 | 101 MB |
| auto_20261116_172619 | `1` | 17:26:19–17:37:06 | 10:48 | dog disconnected | 665 | 665 | 200 MB |
| auto_20261116_175716 | `2` part a | 17:57:16–17:58:00 | 0:45 | console deploy | 42 | 24 | 8 MB |
| auto_20261116_175803 | `2` part b | 17:58:03–18:05:22 | 7:20 | console deploy | 477 | 477 | 127 MB |
| auto_20261116_180524 | `2` part c | 18:05:24–18:11:45 | 6:21 | dog disconnected | 438 | 438 | 127 MB |

**Why patrol 2 is split:** two console deploys, at about 17:58:00 and 18:05:22, each closed the running auto recording cleanly, and a new one started 2–3 s later. Nothing is lost apart from those gaps. `/odom` is continuous across the three parts. Patrol 2 has three recording sessions, not two; part a is only 45 s, and the L515 came up about 19 s into it.

## Formats
- `<session>/frames/<id>.jpg`: the dog front camera JPEGs as stored (1280x720), not re-encoded. `id` is the header stamp in ms.
- `<session>/frames.jsonl`: each line has `{id, t, local_time, run, patrol, map_x, map_y, map_heading_deg, map_pose_source, odom}`. `in_view` is not included, because Z690 could not find how the days export computed it.
- Sampling: 1 frame/s, plus any frame after a turn of more than 15° or a move of more than 0.3 m.
- `<session>/l515/rgb/<id>.jpg` (960x540, stored JPEG) and `l515/depth/<id>.png` (640x480, 16-bit, **1 unit = 1 mm**, 0 = no return).
- `l515/frames.jsonl`: each line has `{id, t_depth, t_rgb, dog_frame_id, dog_frame_dt, map pose at t_depth, odom}`.
- `l515/intrinsics.json`: depth and colour camera_info, plus the depth->colour extrinsic.
- **RGB and depth are not aligned**; they have separate intrinsics.
- **The L515 mount is not measured.** `/tf_static` still has `base_link->l515_link` = xyz (0,0,0), rpy (0,0,0) as a placeholder.
- **Map poses:** each pose is the console's map<-odom transform applied to `/odom` at the frame time.
  - Frames recorded before the console lined up are marked `map_pose_source: "backfilled"` and are approximate. They use the transform from the first line-up later in the same odometry run.
  - That covers all of 171906 and 175716, the first 45 frames of 172619, and the first 307 frames of 175803 (until 18:03:04).
