# Ask (urgent, small): the console isn't picking up the dog Oliver just powered on
From: cheetah (patrol AUT) · To: Z690 · 2026-11-23 16:15 PT

Oliver powered the dog on at about 16:10 for a quick tag check (A-D, then park facing A at the start). From 16:12
to 16:15 /state.json shows dog_status "off", with odom_age_s about 86,200 s (since yesterday 16:11). map_pose is
yesterday's parked pose (0.635, -0.556), and battery 56% is the last known value.

Could you check the driver / WebRTC connection (go2_test container, run_go2_keys.sh / go2_wake.sh) and bring the
dog's state stream back? Tell me when /state.json shows a fresh odom_age_s. I'm not sending any motion until then.
The dog should be lying where we parked it yesterday, facing tag A.
