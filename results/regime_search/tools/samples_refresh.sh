#!/bin/bash
# Rebuild everything the sampling run feeds, every 5 minutes while it is in flight.
# Order matters: both extractors must write story_extra.json BEFORE the page is built from it, or the page
# ships a five-minute-old copy of the data it claims to show. That drift is what left story.html stale for
# forty minutes on 22 Sept while the chart beside it was current.
cd ~/robot/dynamic_home_eqa/results/regime_search || exit 1
while true; do
  python3 tools/samples_chart.py  >> tools/samples_refresh.log 2>&1   # the conformal figure (its own PNG)
  python3 tools/samples_extra.py  >> tools/samples_refresh.log 2>&1   # samples_live -> the panel library
  python3 tools/deferral_extra.py >> tools/samples_refresh.log 2>&1   # deferral_live
  python3 tools/story_page.py     >> tools/samples_refresh.log 2>&1   # the page, last
  echo "$(date +%H:%M) refreshed" >> tools/samples_refresh.log
  sleep 300
done
