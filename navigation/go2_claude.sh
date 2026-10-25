#!/usr/bin/env bash
# Give the robot dog a task and let a Claude agent do it, using your Claude plan (Claude Code login).
#   ./go2_claude.sh "go to the sofa and tell me what is on it"
#   GO2_MODEL=sonnet ./go2_claude.sh "..."      (default: opus)
# The agent only has the robot tools in go2_claude/go2_tools_mcp.py. Watch it on the console
# (http://localhost:8080); Take over or STOP there always wins.
set -euo pipefail
HERE=$(dirname "$(readlink -f "$0")")
[ $# -ge 1 ] || { echo "usage: $0 \"task for the robot\""; exit 1; }
curl -sf -o /dev/null http://localhost:8080/ || { echo "The console isn't running: start it with run_go2_keys.sh"; exit 1; }
cd "$HERE/go2_claude"
claude -p "$*" --model "${GO2_MODEL:-opus}" \
    --mcp-config "$HERE/go2_claude/mcp.json" --strict-mcp-config \
    --allowedTools "mcp__go2__*" --disallowedTools "Bash,Edit,Write,WebFetch,WebSearch,Task,NotebookEdit" \
    --append-system-prompt "$(cat "$HERE/go2_claude/prompt.md")" \
    --output-format stream-json --verbose | python3 "$HERE/go2_claude/show.py"
