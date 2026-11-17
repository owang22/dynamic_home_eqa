#!/usr/bin/env python3
"""MCP connector for watching and supervising the Go2 from claude.ai (the "Go2 Robot" artifact).

Runs on the control PC, next to the console (http://localhost:8080), and only relays to it.
It listens on 127.0.0.1; go2_remote.sh puts a Cloudflare tunnel in front of it. The tunnel URL
plus the secret path in ~/oliver/go2_remote/secret is what you add as a claude.ai connector:
anyone with that full URL can see the robot and press its buttons, so keep it private.

Commands sent from here count as a person at the console: they take control from any agent.
"""
import base64
import fcntl
import subprocess
import io
import json
import os
import time
import urllib.error
import urllib.request
from typing import Any

from PIL import Image
from mcp.server.fastmcp import FastMCP
from mcp.server.transport_security import TransportSecuritySettings
from mcp.types import ToolAnnotations

CONSOLE = "http://127.0.0.1:8080"
CLIENT = "claude.ai remote"
WAKE = os.path.expanduser("~/oliver/go2_wake.sh")
L515 = "http://127.0.0.1:8081"   # RealSense L515 bridge page (l515_go2_pi4_bridge); may be off
HERE = os.path.dirname(os.path.abspath(__file__))
SECRET = open(os.path.join(HERE, "secret")).read().strip()
STEP = {"forward": (0.3, 0, 0), "back": (-0.3, 0, 0), "left": (0, 0.2, 0), "right": (0, -0.2, 0),
        "turn_left": (0, 0, 0.6), "turn_right": (0, 0, -0.6)}

mcp = FastMCP("Go2 Robot", host="127.0.0.1", port=8765, stateless_http=True, json_response=True,
              streamable_http_path=f"/{SECRET}/mcp",
              # Reached through the tunnel, so the Host header is the tunnel's name; the secret path guards it.
              transport_security=TransportSecuritySettings(enable_dns_rebinding_protection=False))

READ = ToolAnnotations(readOnlyHint=True, destructiveHint=False, openWorldHint=False)
WRITE = ToolAnnotations(readOnlyHint=False, destructiveHint=False, openWorldHint=False)


def get(path, timeout=5):
    with urllib.request.urlopen(CONSOLE + path, timeout=timeout) as r:
        return r.read()


def cmd(body):
    req = urllib.request.Request(CONSOLE + "/cmd", data=json.dumps({**body, "client": CLIENT, "console": True}).encode(),
                                 headers={"Content-Type": "application/json"}, method="POST")
    try:
        urllib.request.urlopen(req, timeout=5).read()
        return None
    except urllib.error.HTTPError as e:
        return f"{e.code}: {e.reason}"


def jpeg_b64(raw, width):
    img = Image.open(io.BytesIO(raw)).convert("RGB")
    if img.width > width:
        img = img.resize((width, round(img.height * width / img.width)))
    out = io.BytesIO()
    img.save(out, "JPEG", quality=72)
    return base64.b64encode(out.getvalue()).decode()


def state():
    s = json.loads(get("/state.json"))
    a = s.get("agents") or {}
    imu, st = s.get("imu"), s.get("state")
    out = {
        "t": time.time(),
        "ages": s.get("age", {}),
        "owner": a.get("owner"), "current": a.get("current"), "notes": a.get("notes", {}),
        "log": (a.get("log") or [])[-10:],
        "odom": s.get("odom"), "map_pose": s.get("map_pose"),
        "map": s.get("map"),
        "rpy": imu["rpy"] if imu else None,
        "body_height": st["body_height"] if st else None,
        "avoid": (s.get("control") or {}).get("avoid"),
        "recording": (s.get("rec") or {}).get("running"),
        # seconds with no motion, posture change or command (from the console's auto recorder; None when unknown)
        "idle_s": ((s.get("rec") or {}).get("auto_info") or {}).get("idle_s"),
        "agent_photos": a.get("photos", []),
        # {t, msg} while the console is being redeployed (driving paused); boot_id changes on every console start
        "deploying": s.get("deploying"), "boot_id": s.get("boot_id"),
    }
    try:
        out["camera_jpeg_b64"] = jpeg_b64(get("/frame.jpg"), 640)
    except (urllib.error.URLError, OSError):
        out["camera_jpeg_b64"] = None
    photos = out["agent_photos"]
    if photos:
        try:
            out["latest_agent_photo_b64"] = jpeg_b64(get(photos[-1]["url"]), 640)
        except (urllib.error.URLError, OSError):
            out["latest_agent_photo_b64"] = None
    return out


def wake_status():
    """Whether a wake (go2_wake.sh) is running now, and the end of its log."""
    running = False
    try:
        with open("/tmp/go2_wake.lock", "a") as f:
            try:
                fcntl.flock(f, fcntl.LOCK_EX | fcntl.LOCK_NB)
                fcntl.flock(f, fcntl.LOCK_UN)
            except OSError:
                running = True
    except OSError:
        pass
    try:
        with open("/tmp/go2_wake.log") as f:
            log = f.read().splitlines()[-8:]
    except OSError:
        log = []
    return {"running": running, "log": log}


def console_up():
    try:
        get("/control", timeout=2)
        return True
    except (urllib.error.URLError, OSError):
        return False


@mcp.tool(annotations=READ, structured_output=True)
def go2_snapshot() -> dict[str, Any]:
    """Live state of the robot dog: who has control (agent or person) and what it is doing, pose on
    the map, recent agent tool calls, the front camera now (640 px JPEG, base64) and the agents'
    latest photo."""
    if not console_up():
        return {"error": "console_down", "t": time.time(), "wake": wake_status()}
    return {**state(), "wake": wake_status()}


@mcp.tool(annotations=READ, structured_output=True)
def go2_map() -> dict[str, Any]:
    """The lab map (PNG, base64; 5 cm per pixel, north up) with its placement and the saved places."""
    if not console_up():
        return {"error": "console_down"}
    s = json.loads(get("/state.json"))
    try:
        png = base64.b64encode(get("/map.png")).decode()
    except urllib.error.HTTPError:
        png = None
    return {"map": s.get("map"), "map_pose": s.get("map_pose"), "png_b64": png,
            "places": json.loads(get("/places"))}


@mcp.tool(annotations=READ, structured_output=True)
def go2_agent_photo(photo_id: str) -> dict[str, Any]:
    """One photo an agent took, full size (base64 JPEG)."""
    return {"id": photo_id, "jpeg_b64": base64.b64encode(get(f"/agent/photos/{photo_id}.jpg")).decode()}


@mcp.tool(annotations=READ, structured_output=True)
def go2_l515() -> dict[str, Any]:
    """The RealSense L515 depth camera on the dog, when its bridge is running: the latest colour frame and a
    colour-coded depth frame (640 px JPEGs, base64), with frame times. online is false when the bridge is off."""
    out = {"t": time.time(), "online": False, "color_jpeg_b64": None, "depth_jpeg_b64": None, "frame_t": {}}
    try:
        cam = json.loads(urllib.request.urlopen(L515 + "/status.json", timeout=3).read()).get("camera")
    except (urllib.error.URLError, OSError, ValueError):
        return out
    out["online"], out["camera"] = True, cam
    for kind in ("color", "depth"):
        try:
            with urllib.request.urlopen(f"{L515}/{kind}.jpg", timeout=3) as r:
                if r.status == 200:
                    out[f"{kind}_jpeg_b64"] = jpeg_b64(r.read(), 640)
                    out["frame_t"][kind] = float(r.headers.get("X-Frame-T") or 0) or None
        except (urllib.error.URLError, OSError, ValueError):
            pass
    return out


@mcp.tool(annotations=WRITE, structured_output=True)
def go2_wake() -> dict[str, Any]:
    """Wake everything with one button: reconnect the dog's driver and the console if they have no data (as
    run_go2_keys.sh does), and start the RealSense L515 bridge if its Pi is on. Does not move the dog or take
    control. Runs in the background for up to a few minutes; watch wake.log in go2_snapshot."""
    st = wake_status()
    if st["running"]:
        return {"started": False, "reason": "a wake is already running", "wake": st, "t": time.time()}
    subprocess.Popen([WAKE], stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                     start_new_session=True)
    time.sleep(1)
    return {"started": True, "wake": wake_status(), "t": time.time()}


@mcp.tool(annotations=WRITE, structured_output=True)
def go2_stop() -> dict[str, Any]:
    """Stop the dog now and abort any agent tool. Does not take control."""
    return {"error": cmd({"action": "stop"}), **state()}


@mcp.tool(annotations=WRITE, structured_output=True)
def go2_take_over() -> dict[str, Any]:
    """A person takes control: stops the dog, aborts any agent tool and locks agents out until hand back."""
    return {"error": cmd({"takeover": True}), **state()}


@mcp.tool(annotations=WRITE, structured_output=True)
def go2_hand_back() -> dict[str, Any]:
    """End a person's takeover so agents can claim the dog again."""
    return {"error": cmd({"handback": True}), **state()}


@mcp.tool(annotations=WRITE, structured_output=True)
def go2_step(direction: str, seconds: float = 1.0) -> dict[str, Any]:
    """Drive briefly as a person (takes control from any agent). direction: forward, back, left,
    right, turn_left or turn_right. seconds: 0.2 to 2 (forward 1 s is about 0.3 m; turn 1 s about 35 degrees).
    Returns the new state with a fresh camera frame."""
    if direction not in STEP:
        return {"error": f"direction must be one of {', '.join(STEP)}"}
    secs = max(0.2, min(2.0, float(seconds)))
    end, err = time.monotonic() + secs, None
    while time.monotonic() < end and not err:
        err = cmd({"move": list(STEP[direction])})
        time.sleep(0.1)
    cmd({"action": "stop"})
    time.sleep(0.8)   # let it settle so the frame is sharp
    return {"error": err, **state()}


@mcp.tool(annotations=WRITE, structured_output=True)
def go2_posture(posture: str) -> dict[str, Any]:
    """Stand up or lie down (takes control from any agent). posture: stand or lie."""
    if posture not in ("stand", "lie"):
        return {"error": "posture must be stand or lie"}
    err = cmd({"action": posture})
    time.sleep(1.5)
    return {"error": err, **state()}


if __name__ == "__main__":
    mcp.run(transport="streamable-http")
