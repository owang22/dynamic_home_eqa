#!/usr/bin/env bash
# Talk to the lab agent (Opus on Oliver's Max plan) in this terminal. It has only the lab tools in server.py.
#   bash go2/lab_agent/chat.sh            # new conversation
#   bash go2/lab_agent/chat.sh --resume   # pick an earlier one
cd "$(dirname "$0")"
exec claude --model opus \
  --mcp-config mcp.json --strict-mcp-config \
  --tools "" --allowedTools "mcp__lab__*" \
  --append-system-prompt-file SYSTEM.md \
  --disable-slash-commands "$@"
