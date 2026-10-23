# Problems found in the camera-relocalization study (2026-10-23, offline)

## P1. No tilted pictures exist: `look` has no effect on the stored photo

- 1107 / 1109 pictures are look_deg 0. Photo `p1792710742_11` (look 16) has the same framing as `p1792710737_10`
  (look 0, same spot, 5 s earlier), to within a few pixels (`figs/task1_tilt_pair_0_vs_16.jpg`). The look -5
  photo `p1792711082_3` is likewise level.
- Likely cause: `photo` waits until the dog is still, and `look` springs back to level after ~0.5 s (README).
  So the look is over before the picture is taken. The index then stores the requested look_deg, not the
  actual tilt.
- Consequence: a "ceiling survey at max tilt" cannot be recorded with the current agent API. Options:
  - a console change: `photo {look_deg}` that holds the pitch while it grabs the frame, or grab `/frame.jpg`
    during the hold;
  - recording frames continuously from the 10 Hz stream while repeating `look`.
  - Also, record the actual pitch (from the IMU rpy) with each picture rather than the requested one.

## P2. Stored trail frames are 640x360, not 1280x720

The calibration has to be scaled by 0.5 (`vcommon.K_for`). Some agent photos are 1280x720. Mixed sizes are
handled here; anchors.py works in picture fractions, so it is unaffected.

## P3. The 720p calibration's focal length does not fit the stored frames (effective HFOV ~79 deg, not 73)

- Image rotations computed with the calibrated K come out at **0.878x** the odom yaw change, over 250 pairs of
  consecutive trail frames (1-4 s apart).
- Odom yaw itself is right. Over 31 same-spot pairs one full turn apart, odom = 360 deg + image residual
  within **+1.8 %** (`yaw_scale_check.py`).
- Scaling fx, fy by 0.90 (at 1280x720: fx ~ 778) makes the slope 1.003 and lowers the median error from 2.8 to
  1.9 deg (`scratch_fx_sweep.py`).
- Candidate causes:
  - the console's stream is not the image the yaml was calibrated on (a different crop/scale on the way to
    the 640x360 trail frames);
  - or the distortion coefficients are off.
- Consequences:
  - `HFOV = 73.0` in `lab_agent/memory.py` and `console/anchors.py` (bearings from 'across' fractions) is about
    8 % narrow. Bearings near the frame edge are off by up to ~3 deg.
  - Any metric use of the camera needs a fresh checkerboard calibration on frames grabbed the same way as the
    trail (`/frame.jpg`).

## P4. Console poses disagree with what the pictures show

Seen in `pose_consistency.py`, `yaw_audit.py`, `pos_audit.py`. Details in NOTES section 2.

- **Yaw:** per-picture console yaw error (from rotation averaging over 852 verified pairs, residual 0.5 deg) is
  median 8-12 deg, p90 22-24 deg.
  - 10-20 12:2x-12:3x: off by 90-128 deg, with no jump event logged.
  - 10-22 sessions disagree by 15-30 deg with each other.
- **10-19 shift:** 10-19 (after 16:54) is shifted ~0.75 m (dx -0.57, dy +0.50) relative to 10-20 and 10-22 for
  the same views. Either the map frame or the 10-19 localization differs.
- **10-22 after 16:24:38:** after the three 'hand?' events at 16:24 (1.8 m / 57 deg), the pictures say the
  poses are 1.5-3 m off. Identical pictures are posed 2-3 m apart from 10-20 pictures of the same view.
- **Event-log trust filter misses these:** the jump detector does not flag slow or relocalization-induced
  offsets. The camera does: verified matches against older pictures are a cheap pose audit.

## P5. Shared VLM servers went down at 01:50 (not caused by a code change here)

- Both vLLM servers stopped answering at ~01:50:14. Our tmux sessions `vlm`/`vlm8b` are gone, and another user's
  vLLM (gaofeng, Qwen3.6-35B-A3B, port 8036, util 0.81) holds the GPU since 01:50.
- My probe was running at concurrency 2 (within the limit). 214 / 372 requests failed with HTTP 500 /
  connection refused. Those cache files were moved to `cache/vlm_27b_errors_v1/`, and the invalid first eval to
  `results/v1_vlm_with_errors/`.
- I did not restart anything. Rerun later with
  `python3 vlm_probe.py --model 27b --split x_22v20,x_20v22`: it skips cached pictures.

## P6. The event-log trust filter is not enough for ground truth

The 5 s jump window plus turn-rate gate passes pictures whose console pose is off by up to 128 deg or 3 m (P4).
Any evaluation that uses console poses as truth should add the image audit (`yaw_audit.py`, `pos_audit.py`)
or cut the segments after hand placements.
