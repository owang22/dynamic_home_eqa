#!/bin/bash
# Opus runs on the Max plan before the Oct 22 reset (approved 2026-10-19 ~15:30). Frozen copy.
cd /home/oliver/robot/dynamic_home_eqa/go2/evidence_memory
python opus.py --height 0.4 --arms D --workers 6                      # all 122 at 0.4 m (61 already cached)
python opus.py --height 1.0 --arms Ep,Ep2,Ep3 --workers 6             # importance vs random pairs, 3 draws, Opus
OPUS_RERUN=1 python opus.py --height 1.0 --arms D --workers 6 --tag _rerun   # Opus rerun noise floor
python opus_write.py --height 1.0 --workers 6                         # Opus writes the notes
python opus.py --height 1.0 --arms D,C --workers 6 --memory out/memory_1.0_opuswriter.json --tag _opuswriter
echo OPUS BIG DONE
