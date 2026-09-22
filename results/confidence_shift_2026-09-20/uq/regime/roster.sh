#!/bin/bash
# roster.sh <regime> <hh list...>: run the UQ roster on results/regime_search/<regime>/banks -> uq/regime/<regime>/<agent>/
# (existing logs are moved to <agent>/old_<timestamp>/, never deleted)
set -u
R=$1; shift
ROOT=/home/oliver/robot/dynamic_home_eqa
OUT=$ROOT/results/confidence_shift_2026-09-20/uq/regime/$R
cd $ROOT/src
declare -A AG
AG[none_mf]="--agent none --base mostfreq"
AG[none_tt]="--agent none --base timetable"
AG[none_tt72]="--agent none --base timetable --half-life 72"
AG[none_tt24]="--agent none --base timetable --half-life 24"
AG[mon_tt24]="--agent martingale --base timetable --half-life 24 --factor 1.0"
AG[ocp_tt]="--agent ocp --base timetable"
AG[ocp_tt72]="--agent ocp --base timetable --half-life 72"
AG[ocp_tt_norel]="--agent ocp --base timetable --tau 0"
AG[mon_tt]="--agent martingale --base timetable --factor 1.0"
AG[mon_tt72]="--agent martingale --base timetable --half-life 72 --factor 1.0"
AG[mart_tt]="--agent martingale --base timetable --factor 0.1"
AG[mart_tt72]="--agent martingale --base timetable --half-life 72 --factor 0.1"
AG[monw_tt]="--agent martingale --base timetable --factor 1.0 --window 96"
AG[monw_tt72]="--agent martingale --base timetable --half-life 72 --factor 1.0 --window 96"
AG[monw_tt24]="--agent martingale --base timetable --half-life 24 --factor 1.0 --window 96"
AG[martw_tt72]="--agent martingale --base timetable --half-life 72 --factor 0.1 --window 96"
AG[bma_tt]="--agent bma --base timetable"
AG[bma_obj]="--agent bma --base timetable --per-object"
AG[nexcp_tt]="--agent nexcp --base timetable"
AG[nexcp_tt72]="--agent nexcp --base timetable --tau-w 72"
AG[nexcp_tt_unw]="--agent nexcp --base timetable --tau-w 0"
for hh in "$@"; do
  for ag in ${AGENTS:-none_mf none_tt none_tt72 none_tt24 mon_tt24 ocp_tt ocp_tt_norel mon_tt mon_tt72 mart_tt mart_tt72 bma_tt nexcp_tt nexcp_tt72 nexcp_tt_unw}; do
    o=$OUT/$ag/${hh}_t03.jsonl
    if [ -e "$o" ]; then mkdir -p $OUT/$ag/old_$(date +%H%M); mv $o ${o%.jsonl}.side.json $OUT/$ag/old_$(date +%H%M)/ 2>/dev/null; fi
    python3 -m baselines.patrol.uq_agents --bank $ROOT/results/regime_search/$R/banks/${hh}_t03.jsonl --out $o ${AG[$ag]} 2>&1 | sed "s/^/[$R $ag] /"
  done
done
