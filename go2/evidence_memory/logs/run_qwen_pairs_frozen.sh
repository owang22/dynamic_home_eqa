#!/bin/bash
cd /home/oliver/robot/dynamic_home_eqa/go2/evidence_memory
until curl -s 127.0.0.1:8300/v1/models > /dev/null; do sleep 10; done
python answer.py --height 1.0 --arms Ep2,Ep3 --workers 12
echo QWEN PAIRS DONE
