#!/bin/bash
# regenerate the sampling-uncertainty chart every 10 minutes while the run is in flight
cd ~/robot/dynamic_home_eqa/results/regime_search || exit 1
while true; do
  python3 tools/samples_chart.py >> tools/samples_refresh.log 2>&1
  echo "$(date +%H:%M) refreshed" >> tools/samples_refresh.log
  sleep 300
done
