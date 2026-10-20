#!/bin/bash
# Placed-notes run, 2026-10-13: detections for every patrol picture, then the two arms, then a
# same-day rerun of the 84% arm with an empty cache (noise floor), then the report.
cd /home/oliver/robot/dynamic_home_eqa/3d_rendering/results/vlm_night/questions
python placed_notes.py detect && \
python placed_notes.py check && \
python placed_notes.py run camera placed && \
python noise_rerun.py "llm:vlm:truth" && \
python placed_notes.py report
echo "exit $?"
