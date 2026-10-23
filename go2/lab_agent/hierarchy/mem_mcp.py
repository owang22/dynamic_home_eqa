"""Memory-only lab tools as an MCP server named "lab", for running the big model (claude -p) in replay.

Same tool names and texts as server.py, but over a frozen memory (memtools.Memory) and with no console access:
status and list_places come from the saved places and the memory, the moving tools do not exist, locate uses the
27B for sightings and skips the route check. Configured by environment (bigmodel.py writes the MCP config):
  HIER_INDEX  index file   HIER_K  line prefix (optional)   HIER_NOW  epoch seconds of the turn
  HIER_VLM_URL  default http://127.0.0.1:8300/v1   HIER_DOG_STATUS  optional status text from the logs
"""
from __future__ import annotations

import io
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from mcp.server.fastmcp import FastMCP, Image  # noqa: E402

from memtools import Memory  # noqa: E402

mcp = FastMCP("lab")
MEM = Memory.from_index(Path(os.environ["HIER_INDEX"]), int(os.environ["HIER_K"]) if os.environ.get("HIER_K") else None,
                        float(os.environ["HIER_NOW"]) if os.environ.get("HIER_NOW") else None)
_VLM = None


def vlm():
    global _VLM
    if _VLM is None:
        from llm import LLM
        _VLM = LLM(os.environ.get("HIER_VLM_URL", "http://127.0.0.1:8300/v1"))
    return _VLM


def small(jpg, width=960):
    from PIL import Image as PI
    im = PI.open(io.BytesIO(jpg))
    if im.width > width:
        im = im.resize((width, round(im.height * width / im.width)))
    b = io.BytesIO()
    im.convert("RGB").save(b, "JPEG", quality=85)
    return Image(data=b.getvalue(), format="jpeg")


def guard(fn):
    import functools

    @functools.wraps(fn)
    def run(*a, **k):
        try:
            return fn(*a, **k)
        except Exception as e:  # noqa: BLE001
            return f"ERROR: {type(e).__name__}: {e}"
    return run


@mcp.tool()
@guard
def status() -> str:
    """Is the console up, is the dog lined up with the map, where is it, who has control, and how big the memory is."""
    return MEM.status(os.environ.get("HIER_DOG_STATUS"))


@mcp.tool()
@guard
def list_places() -> str:
    """The lab's saved places (ids to use with go_to), each with its standing spot and what it looks at."""
    return MEM.list_places()


@mcp.tool()
@guard
def search_memory(query: str, since: str = "", until: str = "", place: str = "", limit: int = 12) -> str:
    """Search everything the dog has seen. query: words such as 'grey backpack' or 'person'. since/until:
    'HH:MM' (today), 'YYYY-MM-DD HH:MM', or 'today'. place: a place id (pictures taken nearest to it).
    Returns matching pictures (best match first) with time, place, pose and the matched object. The descriptions
    were written by a smaller model and can be wrong: look at the pictures (show_pictures) before answering."""
    return MEM.search_memory(query, since, until, place, limit)


@mcp.tool()
@guard
def show_pictures(ids: list[str]) -> list:
    """Look at remembered pictures (up to 6 ids from search_memory or people_seen), with their full descriptions."""
    out = []
    for i in ids[:6]:
        txt, jpgs = MEM.show_pictures([i])
        out.append(txt)
        out += [small(j) for _, j in jpgs]
    return out


@mcp.tool()
@guard
def people_seen(since: str = "today", until: str = "") -> str:
    """How many people the pictures show, over time: one line per picture with anyone in it, plus a count of
    pictures taken per hour (so 'no people' can be told apart from 'no pictures')."""
    return MEM.people_seen(since, until)


@mcp.tool()
@guard
def locate(thing: str, ids: list[str]) -> str:
    """Where a thing is on the map, from pictures that show it (ids you have looked at and confirmed). The local
    vision model finds it in each picture; each sighting is a line from the camera pose; two or more lines from
    different directions give a position."""
    return MEM.locate(thing, ids, vlm())


if __name__ == "__main__":
    mcp.run()
