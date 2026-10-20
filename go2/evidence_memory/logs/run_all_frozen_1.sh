#!/bin/bash
# Full answer runs, 2026-10-19: every arm at 1.0 m, then at 0.4 m. Resumable through the call cache.
cd /home/oliver/robot/dynamic_home_eqa/go2/evidence_memory
python answer.py --height 1.0 --arms O,A,F,B,D,C,E --workers 20
python answer.py --height 0.4 --arms O,A,F,B,D,C,E --workers 20
echo ALL DONE
