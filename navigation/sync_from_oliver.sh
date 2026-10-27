#!/usr/bin/env bash
# Copy the control PC's live console code (~/oliver, what run_go2_keys.sh deploys into the go2_test container)
# into this folder. Code only: no maps, recordings, camera frames, logs, venvs or the remote connector's secret.
#   ./sync_from_oliver.sh          then review `git status` / `git diff` and commit
set -euo pipefail
SRC=${1:-$HOME/oliver}
cd "$(dirname "$0")"
FILES="go2_dashboard.py go2_agent.py go2_nav.py go2_mapper.py go2_trail.py go2_markers.py go2_examples.py go2_history.py go2_marker_table.py
       go2_label.py go2_tidy.py go2_floor.py go2_straighten.py go2_keys.py
       go2_map.sh go2_goto.sh go2_claude.sh run_go2_keys.sh patch_driver_battery.sh watch_notes.sh
       go2_claude/go2_tools_mcp.py go2_claude/mcp.json go2_claude/prompt.md go2_claude/show.py
       go2_remote/go2_mcp.py go2_remote/go2_remote.html go2_remote/go2_remote.sh
       markers/make_markers.py"
for f in $FILES; do
    if [ -f "$SRC/$f" ]; then mkdir -p "$(dirname "$f")"; cp -p "$SRC/$f" "$f"; else echo "missing: $SRC/$f"; fi
done
for f in "$SRC"/patch_driver_*.sh; do [ -f "$f" ] && cp -p "$f" .; done
echo "synced from $SRC"
