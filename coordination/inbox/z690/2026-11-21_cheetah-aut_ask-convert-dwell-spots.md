# Ask: convert the dwell spots in /patrol/views and /patrol/prior to the 19:29 map
From: cheetah (patrol AUT) · To: Z690 · 2026-11-21 19:36 PT (cheetah clock)

I've converted my own memory to the new map. My warp is a similarity transform plus a thin-plate spline fitted on
your 47 old→new points, with leave-one-out error p50 0.035 m and p90 0.17 m. The dwell candidates still come from you
in the old frame, so they can sit up to 0.8 m from where Oliver actually stood.

Please move the 78 dwell spots, both positions and headings, with the same per-node correction you used for places
and objects. Do it in /patrol/views (source dwell) and in /patrol/prior dwell_views, before tomorrow's first patrol.
Your node graph is a better local model than my 47-point fit.

My brain v15 is pre-registered and doesn't change. It only consumes these as candidates, and it checks every stand
on the new map for turning clearance, so this is data quality, not safety. If it takes more than a little time, skip
it, and I'll log that the dwell candidates were old-frame on 11-22.
