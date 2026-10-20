#!/bin/bash
# after the audit, 2026-10-19 14:45 (frozen copy): fair pairs control, and reruns for the noise floor
cd /home/oliver/robot/dynamic_home_eqa/go2/evidence_memory
python answer.py --height 1.0 --arms Ep --workers 12
EM_RERUN=1 python answer.py --height 1.0 --arms A,Bf --workers 12 --tag _rerun
python answer.py --height 0.4 --arms Ep --workers 12
echo AUDIT RUNS DONE
