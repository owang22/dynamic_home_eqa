"""Search for one thing, with the robot brain (robot_brain/, a separate HTTP service) choosing where to look.

    ros2 run go2_patrol search --ros-args -p question:="where is the red mug?"

The brain answers /ask with a plan of position ids. The robot walks to the first, photographs it,
and sends the picture to /look. The brain says whether the thing is in it, and which position to
try next. A position that cannot be reached or photographed is reported to /feedback, which also
names the next one. The search ends when the thing is found, the plan runs out, max_looks is
reached, or the brain names a position that is not in the positions file.

Writes  <out_root>/<YYYY-MM-DD>/<HHMMSS>_<question>/look_<n>_<id>.jpg  and search.json, which is
rewritten after every look.
"""
from __future__ import annotations

import datetime
import re
import sys
from pathlib import Path

import rclpy
import rclpy.signals

from .common import load_positions, now_iso, write_json_atomic
from .patrol import Patrol


class Search(Patrol):
    def __init__(self):
        super().__init__()
        self.declare_parameter("question", "")
        self.declare_parameter("brain_url", "http://127.0.0.1:8400")
        self.declare_parameter("brain_client_dir", "/brain")   # robot_brain/ mounted read-only
        self.declare_parameter("max_looks", 8)
        self.declare_parameter("return_to_dock", False)        # default: stay where the search ended
        for k in ("question", "brain_url", "brain_client_dir", "max_looks", "return_to_dock"):
            self.cfg[k] = self.get_parameter(k).value

    def run(self) -> int:
        q = self.cfg["question"].strip()
        if not q:
            self.get_logger().error("give the question: -p question:='where is the red mug?'")
            return 2
        sys.path.insert(0, self.cfg["brain_client_dir"])
        from client import Brain, BrainError  # robot_brain/client.py, standard library only

        positions = {p["id"]: p for p in load_positions(self.cfg["positions_file"])}
        started = datetime.datetime.now().astimezone()
        slug = re.sub(r"[^a-z0-9]+", "_", q.lower()).strip("_")[:40]
        out = Path(self.cfg["out_root"]) / started.strftime("%Y-%m-%d") / f"{started.strftime('%H%M%S')}_{slug}"
        out.mkdir(parents=True, exist_ok=True)
        log = {"question": q, "started": started.isoformat(timespec="seconds"), "finished": None,
               "ended_because": None, "found_at": None, "settings": self.cfg, "ask": None, "looks": []}
        logf = out / "search.json"

        def finish(why: str, code: int) -> int:
            log["ended_because"], log["finished"] = why, now_iso()
            write_json_atomic(logf, log)
            self.get_logger().info(f"search ended: {why}; log in {logf}")
            return code

        brain = Brain(self.cfg["brain_url"], timeout=120)
        try:
            health = brain.health()
        except Exception as e:  # noqa: BLE001 - URLError, BrainError, refused connection
            return finish(f"robot brain not answering at {self.cfg['brain_url']}: {e}", 2)
        if not health.get("model_up"):
            return finish("robot brain is up but its vision model is not (start robot_brain/serve_vlm.sh)", 2)
        if not health.get("places"):
            return finish("robot brain knows no places yet (record positions, and start it with --positions)", 2)
        if not self.nav.wait_for_server(timeout_sec=30.0):
            return finish("nav2 is not running (no navigate_to_pose server after 30 s)", 2)

        try:
            s = brain.ask(q)
            log["ask"] = s
            write_json_atomic(logf, log)
            session = s["session"]
            place = s["plan"][0] if s.get("plan") else None
            self.get_logger().info(f"plan: {s.get('plan')} ({s.get('answer_type')}: {s.get('why', '')[:120]})")
            why = "the brain's plan is used up"
            while place:
                if len(log["looks"]) >= int(self.cfg["max_looks"]):
                    why = f"max_looks ({self.cfg['max_looks']}) reached"
                    break
                if place not in positions:
                    brain.feedback(f"unknown place {place}: not in the robot's positions file", session=session)
                    why = f"the brain named {place}, which is not in the positions file"
                    break
                n = len(log["looks"]) + 1
                rec = self.visit(positions[place], out / f"look_{n:02d}_{place}.jpg")
                rec["look"] = n
                log["looks"].append(rec)
                if rec["result"] != "photographed":
                    r = brain.feedback(f"could not reach or photograph {place}: {rec['result']}",
                                       session=session, place=place, failed=True)
                else:
                    r = brain.look(session, place, image_bytes=(out / rec["picture"]).read_bytes(), time=rec["taken"])
                rec["brain"] = r
                write_json_atomic(logf, log)
                if r.get("found"):
                    log["found_at"] = place
                    why = f"found at {place}"
                    break
                place = None if r.get("done") else r.get("next_place")
        except KeyboardInterrupt:
            why = "stopped by the operator (Ctrl+C)" + self.cancel_active_goal()
        except BrainError as e:
            why = f"robot brain error: {e}"
        except OSError as e:  # the brain went away mid-search
            why = f"robot brain not answering: {e}"

        dock = positions.get(self.cfg["dock_id"])
        if self.cfg["return_to_dock"] and dock and not why.startswith("stopped"):
            outcome, secs = self.go_to(dock)
            log["return_to_dock"] = {"outcome": outcome, "seconds": round(secs, 1)}
        return finish(why, 0 if log["found_at"] else 1)


def main():
    rclpy.init(signal_handler_options=rclpy.signals.SignalHandlerOptions.NO)
    node = Search()
    try:
        code = node.run()
    finally:
        node.destroy_node()
        rclpy.try_shutdown()
    raise SystemExit(code)


if __name__ == "__main__":
    main()
