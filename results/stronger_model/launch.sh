#!/bin/bash
# One stronger-model cell per argument: "<backend-args>|<arm>|<household>". Frozen while running:
# copy to launch_<n>.sh before editing (bash reads a running script by byte offset).
cd /home/oliver/robot/dynamic_home_eqa
export PYTHONPATH=src
LOGS=results/stronger_model/logs
for spec in "$@"; do
  IFS='|' read -r bargs arm hh <<< "$spec"
  safe="$(echo "$bargs $arm $hh" | tr ' ,/' '___' | tr -s '_')"
  ( exec python3 -m stronger_model.run_cell $bargs --arm "$arm" --household "$hh" > "$LOGS/$safe.log" 2>&1 ) &
  echo "$! $spec" >> "$LOGS/pids.txt"
  sleep 2
done
wait
