#!/usr/bin/env bash
# One-button wake for the Go2 Remote page (called by go2_remote/go2_mcp.py, tool go2_wake).
# Reconnects the driver and console the way run_go2_keys.sh does (it restarts the driver only when no data
# arrives), then starts the RealSense L515 bridge if its Pi is on the network. Restarting the driver restarts
# the go2_test container, which also stops the L515 receiver, so the bridge is always (re)started after.
# Log: /tmp/go2_wake.log. Only one wake runs at a time.
HERE=$(dirname "$(readlink -f "$0")")
exec 9>/tmp/go2_wake.run.lock   # 11-23: renamed; an L515 tunnel from 11-21 holds the old lock file forever
flock -n 9 || { echo "wake already running"; exit 0; }
{
  echo "=== wake $(date '+%F %T')"
  unset DISPLAY WAYLAND_DISPLAY          # don't open a browser on the control PC
  timeout 240 "$HERE/run_go2_keys.sh" </dev/null 2>&1 | grep -v -E 'TTY|keyboard control|Press x'
  if ping -c1 -W2 172.17.29.72 >/dev/null 2>&1; then
    echo "L515 Pi is up; waking its sender and starting the bridge"
    timeout 20 ssh -o BatchMode=yes -o ConnectTimeout=5 khang@172.17.29.72 'sudo systemctl start l515-sender' 2>&1 | tail -1
    timeout 120 bash "$HERE/l515_go2_pi4_bridge/scripts/run_pc.sh" </dev/null 9>&- 2>&1 | tail -4
  else
    echo "L515 Pi (172.17.29.72) not on the network; skipping the L515 bridge"
  fi
  echo "=== done $(date '+%F %T')"
} >> /tmp/go2_wake.log 2>&1
