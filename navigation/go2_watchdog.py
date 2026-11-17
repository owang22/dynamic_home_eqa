#!/usr/bin/env python3
"""Go2 power watchdog: a small, AI-free loop that decides whether the dog is on, off, or on without data, and acts.

Every 3 s:
  dog "on"          the console has odometry newer than 10 s.
  dog "no_data"     the dog answers ping but the console has no fresh data (or is down): after 15 s, run
                    go2_wake.sh (reconnect driver + console, start the L515), at most once per 3 min.
  dog "off"         no fresh data and no ping: after 30 s, put the L515 to sleep (stop its sender on the Pi;
                    the Pi itself stays on so it can be woken again).
When the dog is "on" and the L515 is not streaming but its Pi answers, the L515 is woken (sender + bridge).
Never sends motion. State: /tmp/go2_watchdog.json (the console shows it). Log: ~/oliver/logs/go2_watchdog.log.
"""
import json
import os
import subprocess
import time
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
DOG, PI = "172.17.39.82", "khang@172.17.29.72"
PI_IP = PI.split("@")[1]
CONSOLE = "http://127.0.0.1:8080/state.json"
STALE_S, OFF_AFTER_S, WAKE_AFTER_S, WAKE_COOLDOWN_S, L515_COOLDOWN_S = 10, 30, 15, 180, 120
STATUS = "/tmp/go2_watchdog.json"
LOG = os.path.join(HERE, "logs", "go2_watchdog.log")


def log(msg):
    os.makedirs(os.path.dirname(LOG), exist_ok=True)
    with open(LOG, "a") as f:
        f.write(time.strftime("%F %T ") + msg + "\n")


def ping(host):
    return subprocess.run(["ping", "-c1", "-W1", host], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode == 0


def console():
    try:
        return json.loads(urllib.request.urlopen(CONSOLE, timeout=2).read())
    except Exception:
        return None


def pi(cmd):
    r = subprocess.run(["ssh", "-o", "BatchMode=yes", "-o", "ConnectTimeout=4", PI, cmd],
                       stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, timeout=20)
    return r.returncode, r.stdout.strip()[-200:]


def main():
    since = {"state": None, "t": time.time()}
    last_wake = last_l515 = 0.0
    l515_asleep = False
    last_action = None
    log("watchdog started")
    while True:
        now = time.time()
        st = console()
        odom_age = ((st or {}).get("age") or {}).get("odom")
        fresh = odom_age is not None and odom_age < STALE_S
        reach = fresh or ping(DOG)
        state = "on" if fresh else "no_data" if reach else "off"
        if state != since["state"]:
            log(f"dog {since['state']} -> {state} (odom age {odom_age})")
            since = {"state": state, "t": now}
        held = now - since["t"]
        l515_on = bool(((st or {}).get("l515") or {}).get("online"))
        action = None

        if state == "no_data" and held >= WAKE_AFTER_S and now - last_wake >= WAKE_COOLDOWN_S:
            action, last_wake, l515_asleep = "wake", now, False
            log("dog answers but no data: running go2_wake.sh")
            subprocess.Popen([os.path.join(HERE, "go2_wake.sh")], stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL,
                             stderr=subprocess.DEVNULL, start_new_session=True)
        elif state == "off" and held >= OFF_AFTER_S and not l515_asleep:
            l515_asleep = True
            if ping(PI_IP):
                code, out = pi("sudo systemctl stop l515-sender")
                action = "l515_sleep"
                log(f"dog off {held:.0f} s: L515 sender stopped (rc {code}) {out}")
            else:
                log("dog off: L515 Pi not reachable, nothing to put to sleep")
        elif state == "on" and not l515_on and now - last_l515 >= L515_COOLDOWN_S and ping(PI_IP):
            last_l515, l515_asleep, action = now, False, "l515_wake"
            code, out = pi("sudo systemctl start l515-sender")
            log(f"dog on, L515 not streaming: sender start rc {code} {out}; starting bridge")
            subprocess.Popen(["bash", os.path.join(HERE, "l515_go2_pi4_bridge", "scripts", "run_pc.sh")],
                             stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                             start_new_session=True)

        if action:
            last_action = f"{action} at {time.strftime('%H:%M:%S')}"
        status = {"t": round(now, 1), "dog": state, "for_s": round(held), "odom_age_s": odom_age,
                  "console_up": st is not None, "l515_online": l515_on, "l515_asleep": l515_asleep,
                  "last_action": last_action,
                  "last_wake_t": round(last_wake, 1) or None}
        try:   # shown in the console header (POST /watchdog, localhost only)
            urllib.request.urlopen(urllib.request.Request("http://127.0.0.1:8080/watchdog", data=json.dumps(status).encode(),
                                   headers={"Content-Type": "application/json"}, method="POST"), timeout=2).read()
        except Exception:
            pass
        tmp = STATUS + ".tmp"
        with open(tmp, "w") as f:
            json.dump(status, f)
        os.replace(tmp, STATUS)
        time.sleep(3)


if __name__ == "__main__":
    main()
