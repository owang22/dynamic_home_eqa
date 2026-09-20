#!/bin/sh
# Classical sweep: fast beliefs everywhere (resumes), then the Perpetua pair on 8 h/4 h, then 2 h/1 h.
cd /home/oliver/robot/dynamic_home_eqa/src
R=../results/overnight_2026-09-20
FAST="last_observation most_frequent timetable markov1 periodic_persistence smoothed_recency hierarchy_backoff daytype_mixture"
python3 -m baselines.patrol.sweep --runs ../data/situation_sim/week8 --seeds 0-19 --patrol-hours 1 2 4 8 --looks off voi top --beliefs $FAST --out $R --workers 12 2>&1 | tee -a $R/classical_sweep3.log
python3 -m baselines.patrol.sweep --runs ../data/situation_sim/week8 --seeds 0-19 --patrol-hours 8 4 --looks off voi top --beliefs perpetua perpetua_star --suffix _perpetua --out $R --workers 12 2>&1 | tee -a $R/classical_sweep3.log
python3 -m baselines.patrol.sweep --runs ../data/situation_sim/week8 --seeds 0-19 --patrol-hours 2 1 --looks off voi top --beliefs perpetua perpetua_star --suffix _perpetua --out $R --workers 12 2>&1 | tee -a $R/classical_sweep3.log
echo "CLASSICAL QUEUE DONE $(date)" | tee -a $R/classical_sweep3.log
