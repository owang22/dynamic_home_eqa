#!/bin/bash
# waits for the one-person chain (run_chain_person.sh) to finish, then launches the two-spells chain
cd "$(dirname "$0")" || exit 1
while pgrep -f "^bash run_chain_person.sh" >/dev/null; do sleep 60; done
echo "$(date +%H:%M) queue: one-person chain finished, launching person2x" >> chain_progress.log
bash run_chain_person2x.sh
