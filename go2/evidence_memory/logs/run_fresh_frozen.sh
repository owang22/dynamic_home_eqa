#!/bin/bash
# fresh-look arms, 2026-10-19 13:22 (frozen copy)
cd /home/oliver/robot/dynamic_home_eqa/go2/evidence_memory
python answer.py --height 1.0 --arms Cf,Bf,Df --workers 12
python answer.py --height 0.4 --arms Cf,Bf,Df --workers 12
echo FRESH DONE
