"""The viewer path: spatial configs and traces.json registration, so a
revamp_v2 household replays in the same topdown viewer as revamp_v1."""
from __future__ import annotations

import json
import os
import shutil
import socket
import pathlib

import yaml

from revamp_v2_helpers import REPO, mini_program

import make_viewer_configs as mvc


def _household(tmp_path, program=None):
    hh = tmp_path / "hh1"
    hh.mkdir()
    program = program or mini_program()
    # the viewer maps symbolic rooms onto real scene regions
    program["receptacles"] = [
        {"id": "couch_l1", "room": "living"},
        {"id": "counter_k1", "room": "kitchen"},
        {"id": "bed_b1", "room": "bedroom"},
        {"id": "entry_floor_e1", "room": "entry"},
        {"id": "entry_hook_e1", "room": "entry"},
    ]
    (hh / "routine_program.yaml").write_text(yaml.safe_dump(program))
    return hh


def test_config_covers_every_receptacle_with_a_relation(tmp_path, monkeypatch):
    monkeypatch.setattr(mvc, "VIZ", tmp_path / "viz")
    (tmp_path / "viz" / "configs").mkdir(parents=True)
    hh = _household(tmp_path)
    cfg = yaml.safe_load(mvc.make_config(hh).read_text())
    program = yaml.safe_load((hh / "routine_program.yaml").read_text())
    assert set(cfg["receptacles"]) == {r["id"] for r in program["receptacles"]}
    assert all(len(r["anchor"]) == 2 for r in cfg["receptacles"].values())
    # placement semantics: floors are floors, hooks are hooks
    assert cfg["receptacles"]["entry_floor_e1"]["relation"] == "floor"
    assert cfg["receptacles"]["entry_hook_e1"]["relation"] == "hook"
    assert cfg["receptacles"]["couch_l1"]["relation"] == "on_surface"
    # spatialize.py reads receptacles+placements from this file
    assert cfg["schedule_spec"].endswith("expanded_motions.yaml")
    # a household outside the repo still gets a resolvable (absolute) path
    assert pathlib.Path(cfg["schedule_spec"]).is_absolute()
    assert set(cfg["room_map"]) == {"living", "kitchen", "bedroom", "entry"}


def test_unmapped_room_fails_loudly(tmp_path, monkeypatch):
    monkeypatch.setattr(mvc, "VIZ", tmp_path / "viz")
    (tmp_path / "viz" / "configs").mkdir(parents=True)
    program = mini_program()
    hh = _household(tmp_path, program)
    p = yaml.safe_load((hh / "routine_program.yaml").read_text())
    p["receptacles"].append({"id": "shed_x1", "room": "boathouse"})
    (hh / "routine_program.yaml").write_text(yaml.safe_dump(p))
    try:
        mvc.make_config(hh)
        assert False, "expected an assertion for an unmapped room"
    except AssertionError as e:
        assert "boathouse" in str(e)


def test_serve_discovers_every_built_timeline():
    """The viewer's dropdown is rebuilt from disk by serve.py, so a freshly
    built household appears without anyone editing a manifest — and a
    deleted one stops being offered."""
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "viewer_serve", REPO / "visualization" / "serve.py")
    serve = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(serve)

    n = serve.refresh_manifest()
    manifest = json.loads((REPO / "visualization" / "traces.json").read_text())
    rows = manifest["traces"]
    assert len(rows) == n
    built = sorted(REPO.glob(
        "profiles/revamp_v2/*/*/hh*/timeline_seed0/trace.json"))
    listed = {r["trace"] for r in rows}
    for path in built:
        assert "/" + str(path.relative_to(REPO)) in listed
    # every row points at a file that exists, and reads as a household
    for r in rows:
        assert (REPO / r["trace"].lstrip("/")).exists()
        assert "·" in r["label"]          # "hh_004 · college_roommates · ..."
    # revamp_v2 households come first, in natural order (hh2 before hh10)
    v2 = [r["trace"] for r in rows if "revamp_v2" in r["trace"]]
    assert v2 == [r["trace"] for r in rows[:len(v2)]]
    # Natural household order holds WITHIN each method/model source; the
    # numbering restarts when the source changes, because the dropdown
    # groups by source and each group lists hh1..hh10.
    by_source: dict[str, list[int]] = {}
    for u in v2:
        src = "/".join(u.split("/")[2:5])       # revamp_v2/<method>/<slug>
        by_source.setdefault(src, []).append(
            int("".join(c for c in u.split("/hh")[-1].split("/")[0]
                        if c.isdigit())))
    for src, nums in by_source.items():
        assert nums == sorted(nums), f"{src} out of order: {nums}"


def _load_serve():
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "viewer_serve", REPO / "visualization" / "serve.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_dropdown_follows_disk_without_a_restart(tmp_path):
    """The list is rebuilt per request, so a household that finishes while
    the viewer is open appears on the next poll — no restart, no manifest
    editing."""
    serve = _load_serve()
    before = {r["trace"] for r in serve.build_rows()}
    live = (REPO / "profiles" / "revamp_v2" / "_pytest_live" / "hh1"
            / "timeline_seed0")
    live.mkdir(parents=True)
    try:
        (live / "trace.json").write_text(json.dumps({
            "household": "hh_live", "days": 21, "seed": 0,
            "objects": {"mug_1": {"class": "mug", "segments": []}},
            "residents": {"resident_1": []}}))
        after = {r["trace"] for r in serve.build_rows()}
        assert after - before == {
            "/profiles/revamp_v2/_pytest_live/hh1/timeline_seed0/trace.json"}
    finally:
        shutil.rmtree(REPO / "profiles" / "revamp_v2" / "_pytest_live")
    # ...and it disappears again once the files are gone
    assert {r["trace"] for r in serve.build_rows()} == before


def test_port_holder_identifies_a_listener():
    """Restarting means finding a detached server nobody's shell owns; the
    takeover path depends on spotting it by pid via /proc."""
    serve = _load_serve()
    assert serve._port_holder("127.0.0.1", 1) is None      # nothing listens
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        s.listen(1)
        port = s.getsockname()[1]
        holder = serve._port_holder("127.0.0.1", port)
    assert holder is not None and holder[0] == os.getpid()


def test_every_row_names_the_set_it_came_from():
    """Each set numbers its households hh1..hh10, so a flat dropdown shows
    three rows called hh_001 with nothing to tell them apart. The source
    field is what the viewer's first picker groups on."""
    serve = _load_serve()
    rows = serve.build_rows()
    assert rows and all(r.get("source") for r in rows)
    for r in rows:
        if "/revamp_v2/" in r["trace"]:
            # profiles/revamp_v2/<method>/<model-slug>/hhN/...: the method
            # (rule_based / freeform / ...) is the discriminator now — the
            # same model builds the same household under several methods.
            parts = r["trace"].split("/")
            assert r["source"] == f"{parts[3]} · {parts[4]}"
        elif r["trace"].startswith("/casas/"):
            assert r["source"] == "casas (real ADLs)"
    # two households sharing a number must differ by source
    by_household = {}
    for r in rows:
        by_household.setdefault(r["label"].split(" · ")[0], set()).add(r["source"])
    for household, sources in by_household.items():
        assert len(sources) == len([r for r in rows
                                    if r["label"].startswith(household + " ")]), \
            f"{household} appears twice within one source"
