"""First contact with the Go2: is it reachable, does it need a key, and can we get one picture.

Run on a computer whose Wi-Fi is joined to the dog (its own hotspot, or the same network as it).
Close the Unitree phone app first: the dog accepts only one controller at a time.

    pip install unitree_webrtc_connect opencv-python-headless
    python check_connection.py                      # dog's own hotspot (address 192.168.12.1)
    python check_connection.py --ip 192.168.1.57    # dog joined to another network
    GO2_AES_KEY=<32 hex> python check_connection.py # firmware 1.1.15 or later

Stops at the first step that fails and says what to try. Nothing is sent that moves the dog.
"""
from __future__ import annotations

import argparse
import asyncio
import base64
import datetime
import json
import os
import socket
import sys
from pathlib import Path

AP_IP = "192.168.12.1"


def port_open(ip: str, port: int, timeout: float = 2.0) -> bool:
    try:
        with socket.create_connection((ip, port), timeout=timeout):
            return True
    except OSError:
        return False


def step1_reachable(ip: str) -> int:
    print(f"1. Reaching {ip} ...")
    if port_open(ip, 9991):
        print("   ok: the dog answers on port 9991 (current firmware's connection port)")
        return 9991
    if port_open(ip, 8081):
        print("   ok: the dog answers on port 8081 (firmware older than 1.1.11)")
        return 8081
    print("   FAILED: nothing answers at this address.")
    print("   - Is this computer's Wi-Fi joined to the dog's network?  (ip -br addr: look for 192.168.12.x)")
    print("   - Is the dog switched on and fully started (about 1 minute after power-on)?")
    print("   - If the dog joined another Wi-Fi network, its address is in the app:"
          " Device -> Data -> Automatic Machine Inspection -> STA Network: wlan0")
    sys.exit(1)


def step2_key_needed(ip: str) -> bool:
    """con_notify is the first message of the phone app's handshake; its data2 field says which
    encryption the firmware uses (2 = shared key, firmware below 1.1.15; 3 = per-dog key)."""
    import requests
    print("2. Asking which handshake the firmware uses ...")
    try:
        r = requests.post(f"http://{ip}:9991/con_notify", timeout=5)
        r.raise_for_status()
        data2 = json.loads(base64.b64decode(r.text)).get("data2")
    except Exception as e:  # noqa: BLE001 - report whatever went wrong
        print(f"   could not read the reply ({e}); carrying on")
        return False
    if data2 == 3:
        print("   data2=3: firmware 1.1.15 or later. A per-dog key is needed (GO2_AES_KEY).")
        print("   Get it once with: unitree-fetch-aes-key --email <the dog's account> --device-type Go2")
        return True
    print(f"   data2={data2}: firmware below 1.1.15. No key needed; the lab repo's driver will work as is.")
    return False


async def step3_connect_and_photograph(ip: str, key: str | None, out: Path) -> None:
    import cv2
    from unitree_webrtc_connect.constants import RTC_TOPIC
    from unitree_webrtc_connect.webrtc_driver import UnitreeWebRTCConnection, WebRTCConnectionMethod

    print("3. Opening the same connection the phone app uses ...")
    method = WebRTCConnectionMethod.LocalAP if ip == AP_IP else WebRTCConnectionMethod.LocalSTA
    kwargs = {"aes_128_key": key} if key else {}
    conn = (UnitreeWebRTCConnection(method, **kwargs) if method == WebRTCConnectionMethod.LocalAP
            else UnitreeWebRTCConnection(method, ip=ip, **kwargs))
    try:
        await asyncio.wait_for(conn.connect(), timeout=40)
    except Exception as e:  # noqa: BLE001
        print(f"   FAILED: {type(e).__name__}: {e}")
        print("   - Close the Unitree app on every phone (one controller at a time), wait 20 s, retry.")
        print("   - If it says the key is required or rejected, fetch the key (step 2).")
        sys.exit(1)
    print("   ok: connected")

    state: dict = {}
    conn.datachannel.pub_sub.subscribe(RTC_TOPIC["LOW_STATE"], lambda m: state.update(low=m.get("data", {})))
    conn.datachannel.pub_sub.subscribe(RTC_TOPIC["LF_SPORT_MOD_STATE"], lambda m: state.update(sport=m.get("data", {})))

    print("4. Waiting for a camera picture ...")
    frames: list = []

    async def on_track(track):
        while len(frames) < 30:  # skip the first frames, which can be grey while the stream starts
            frames.append(await track.recv())

    conn.video.add_track_callback(on_track)
    conn.video.switchVideoChannel(True)
    for _ in range(150):
        if len(frames) >= 30:
            break
        await asyncio.sleep(0.1)
    if not frames:
        print("   FAILED: connected, but no video arrived in 15 s.")
        sys.exit(1)
    img = frames[-1].to_ndarray(format="bgr24")
    out.mkdir(parents=True, exist_ok=True)
    stamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    path = out / f"first_picture_{stamp}.jpg"
    cv2.imwrite(str(path), img, [cv2.IMWRITE_JPEG_QUALITY, 92])
    print(f"   ok: {img.shape[1]}x{img.shape[0]} picture saved to {path}")

    low, sport = state.get("low", {}), state.get("sport", {})
    bms = low.get("bms_state", {}) if isinstance(low, dict) else {}
    print("5. Robot state")
    print(f"   battery: {bms.get('soc', '?')}%   battery firmware {bms.get('version_high', '?')}.{bms.get('version_low', '?')}")
    if isinstance(sport, dict) and sport:
        print(f"   body height: {sport.get('body_height', '?')} m   mode: {sport.get('mode', '?')}")
    (out / f"first_state_{stamp}.json").write_text(json.dumps(
        {"ip": ip, "time": stamp, "picture": path.name, "low_state": low, "sport_state": sport}, indent=1, default=str))
    await conn.disconnect()


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--ip", default=os.environ.get("ROBOT_IP", AP_IP))
    ap.add_argument("--out", default=str(Path(__file__).resolve().parent / "data" / "checks"))
    args = ap.parse_args()
    key = os.environ.get("GO2_AES_KEY") or None

    port = step1_reachable(args.ip)
    needs_key = step2_key_needed(args.ip) if port == 9991 else False
    if needs_key and not key:
        print("\nStopping before connecting: set GO2_AES_KEY and run again.")
        sys.exit(2)
    asyncio.run(step3_connect_and_photograph(args.ip, key, Path(args.out)))
    print("\nAll steps passed.")


if __name__ == "__main__":
    main()
