#!/usr/bin/env bash
# Remote access for claude.ai: the Go2 connector (go2_mcp.py) behind a Cloudflare quick tunnel.
#   ./go2_remote.sh start    start both and print the connector URL to add in claude.ai
#   ./go2_remote.sh stop     stop both (the robot is then unreachable from outside the lab)
#   ./go2_remote.sh status   show whether they run, and the current URL
# The tunnel URL changes every time it starts; update the connector in claude.ai when it does.
# Keep the URL private: anyone who has it can see the robot and press its buttons.
set -u
HERE=$(dirname "$(readlink -f "$0")")
CF="$HERE/../bin/cloudflared"
LOG="$HERE/logs"; mkdir -p "$LOG"
[ -s "$HERE/secret" ] || { (umask 077; head -c 24 /dev/urandom | base64 | tr -d '/+=' > "$HERE/secret"); }
url() { grep -o 'https://[a-z0-9-]*\.trycloudflare\.com' "$LOG/tunnel.log" 2>/dev/null | tail -1; }

case "${1:-}" in
start)
    pgrep -f go2_mcp.py >/dev/null || nohup "$HERE/venv/bin/python" "$HERE/go2_mcp.py" > "$LOG/mcp.log" 2>&1 &
    if ! pgrep -f "cloudflared tunnel" >/dev/null; then
        nohup "$CF" tunnel --no-autoupdate --url http://127.0.0.1:8765 > "$LOG/tunnel.log" 2>&1 &
    fi
    for _ in $(seq 30); do [ -n "$(url)" ] && break; sleep 1; done
    [ -n "$(url)" ] || { echo "Tunnel did not come up; see $LOG/tunnel.log"; exit 1; }
    echo "Connector URL (add in claude.ai > Settings > Connectors > Add custom connector, name: Go2 Robot):"
    echo "  $(url)/$(cat "$HERE/secret")/mcp" ;;
stop)
    pkill -f "cloudflared tunnel"; pkill -f go2_mcp.py; echo "Stopped." ;;
status)
    pgrep -f go2_mcp.py >/dev/null && echo "connector: running" || echo "connector: stopped"
    pgrep -f "cloudflared tunnel" >/dev/null && echo "tunnel: running  $(url)/$(cat "$HERE/secret")/mcp" || echo "tunnel: stopped" ;;
*)
    sed -n '2,8p' "$0"; exit 1 ;;
esac
