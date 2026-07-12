"""
Smoke test for webapp/realism_eval/app.py against a small fixture item
pool + a temp SQLite DB — no real render job output, no habitat_sim, no
network. Exercises the full request cycle: start -> items -> save a
response -> progress reflects it -> invalid rubric values are rejected.
"""
from __future__ import annotations

import importlib
import json
import sys

import pytest

# Fully crossed on purpose: 2 profiles x 2 change_types x 4 items/cell =
# 16 items, so every joint-quota cell the app can generate (change_type
# is the only quota axis now — see app.py's SAMPLING_DISTRIBUTIONS) has
# real candidates — a quota-infeasibility ValueError here would be a
# fixture bug, not app behavior under test (that failure mode is covered
# directly by sampling.py's own unit tests, not this smoke test).
FIXTURE_ITEMS = []
_i = 0
for profile in ("p1", "p2"):
    for change_type in ("location", "state"):
        for _ in range(4):
            FIXTURE_ITEMS.append({
                "item_id": f"item_{_i}", "png": f"item_{_i}.png", "json": f"item_{_i}.json",
                "label": f"obj_{_i}", "category": "book", "change_type": change_type,
                "t_hours": 6.0, "t_clock": "06:00", "reason": "test", "mover": "Test",
                "scene_id": "S1", "profile": profile, "day": 0,
                "household_id": "S1_p1", "folder": "f1",
                "from": "a", "to": "b",
            })
            _i += 1


@pytest.fixture()
def client(tmp_path, monkeypatch):
    media_dir = tmp_path / "media"
    media_dir.mkdir()
    (media_dir / "render_manifest.json").write_text(json.dumps(FIXTURE_ITEMS))
    for it in FIXTURE_ITEMS:
        (media_dir / it["json"]).write_text(json.dumps({
            "caption": it,
            "automatic_signals": {
                "after_supported": True, "after_embedded": False,
                "degenerate_viewpoint": False, "before_status": "ok", "after_status": "ok",
                "deterministic_plausibility_confidence": 1.0,
                "llm_self_graded_realism_day_mean": 0.7,
            },
        }))
        (media_dir / it["png"]).write_bytes(b"\x89PNG\r\n\x1a\n")

    monkeypatch.setenv("REALISM_MEDIA_DIR", str(media_dir))
    monkeypatch.setenv("REALISM_DATA_DIR", str(tmp_path / "data"))

    for mod in list(sys.modules):
        if mod.startswith("dynamic_home_eqa.webapp"):
            del sys.modules[mod]

    import dynamic_home_eqa.webapp.realism_eval.app as app_module
    importlib.reload(app_module)
    app_module.TOTAL_ITEMS = 8

    from fastapi.testclient import TestClient
    return TestClient(app_module.app), app_module


class TestRealismWebappSmoke:
    def test_start_creates_participant(self, client):
        c, _mod = client
        r = c.post("/api/start", json={"name": "Ada"})
        assert r.status_code == 200
        assert r.json()["participant_id"] == "ada"

    def test_items_returns_assigned_pool(self, client):
        c, mod = client
        c.post("/api/start", json={"name": "Ada"})
        r = c.get("/api/items/ada")
        assert r.status_code == 200
        body = r.json()
        assert body["dataset_version"] == mod.DATASET_VERSION
        assert len(body["items"]) == mod.TOTAL_ITEMS
        # every returned item id must be a real pool item
        ids = {it["item_id"] for it in body["items"]}
        assert ids.issubset({it["item_id"] for it in FIXTURE_ITEMS})

    def test_shared_assignment_is_identical_across_participants(self, client):
        c, _mod = client
        c.post("/api/start", json={"name": "Ada"})
        c.post("/api/start", json={"name": "Bob"})
        items_a = [it["item_id"] for it in c.get("/api/items/ada").json()["items"]]
        items_b = [it["item_id"] for it in c.get("/api/items/bob").json()["items"]]
        assert items_a == items_b  # ASSIGNMENT_MODE = "shared"

    def test_save_and_read_back_response(self, client):
        c, _mod = client
        c.post("/api/start", json={"name": "Ada"})
        item_id = c.get("/api/items/ada").json()["items"][0]["item_id"]
        r = c.post("/api/response", json={
            "participant_id": "ada", "item_id": item_id,
            "placement": "resting_naturally", "behavior": "plausible", "visibility": "clearly_visible",
            "issues": ["floating"], "comment": "looks fine", "time_spent_sec": 4.2,
        })
        assert r.status_code == 200

        progress = c.get("/api/progress/ada").json()
        assert item_id in progress
        assert progress[item_id]["placement"] == "resting_naturally"
        assert progress[item_id]["issues"] == ["floating"]
        # automatic signals were frozen into storage, not left null
        assert progress[item_id]["deterministic_plausibility_confidence"] == 1.0
        assert progress[item_id]["before_status"] == "ok"
        assert progress[item_id]["after_status"] == "ok"

    def test_upsert_overwrites_prior_response_for_same_item(self, client):
        c, _mod = client
        c.post("/api/start", json={"name": "Ada"})
        item_id = c.get("/api/items/ada").json()["items"][0]["item_id"]
        base = {
            "participant_id": "ada", "item_id": item_id,
            "placement": "resting_naturally", "behavior": "plausible", "visibility": "clearly_visible",
            "issues": [], "comment": "", "time_spent_sec": 1.0,
        }
        c.post("/api/response", json=base)
        c.post("/api/response", json={**base, "placement": "clearly_wrong"})
        progress = c.get("/api/progress/ada").json()
        assert progress[item_id]["placement"] == "clearly_wrong"

    def test_invalid_placement_rejected(self, client):
        c, _mod = client
        c.post("/api/start", json={"name": "Ada"})
        item_id = c.get("/api/items/ada").json()["items"][0]["item_id"]
        r = c.post("/api/response", json={
            "participant_id": "ada", "item_id": item_id,
            "placement": "bogus_value", "behavior": "plausible", "visibility": "clearly_visible",
        })
        assert r.status_code == 400

    def test_invalid_issue_rejected(self, client):
        c, _mod = client
        c.post("/api/start", json={"name": "Ada"})
        item_id = c.get("/api/items/ada").json()["items"][0]["item_id"]
        r = c.post("/api/response", json={
            "participant_id": "ada", "item_id": item_id,
            "placement": "resting_naturally", "behavior": "plausible", "visibility": "clearly_visible",
            "issues": ["not_a_real_issue"],
        })
        assert r.status_code == 400

    def test_not_applicable_accepted_for_state_item(self, client):
        c, _mod = client
        c.post("/api/start", json={"name": "Ada"})
        items = c.get("/api/items/ada").json()["items"]
        state_item = next(it for it in items if it["change_type"] == "state")
        r = c.post("/api/response", json={
            "participant_id": "ada", "item_id": state_item["item_id"],
            "placement": "not_applicable", "behavior": "plausible", "visibility": "not_applicable",
        })
        assert r.status_code == 200
        progress = c.get("/api/progress/ada").json()
        assert progress[state_item["item_id"]]["placement"] == "not_applicable"

    def test_not_applicable_rejected_for_location_item(self, client):
        c, _mod = client
        c.post("/api/start", json={"name": "Ada"})
        items = c.get("/api/items/ada").json()["items"]
        location_item = next(it for it in items if it["change_type"] == "location")
        r = c.post("/api/response", json={
            "participant_id": "ada", "item_id": location_item["item_id"],
            "placement": "not_applicable", "behavior": "plausible", "visibility": "clearly_visible",
        })
        assert r.status_code == 400

    def test_unknown_item_id_rejected(self, client):
        c, _mod = client
        c.post("/api/start", json={"name": "Ada"})
        r = c.post("/api/response", json={
            "participant_id": "ada", "item_id": "does_not_exist",
            "placement": "resting_naturally", "behavior": "plausible", "visibility": "clearly_visible",
        })
        assert r.status_code == 404

    def test_static_and_media_are_mounted(self, client):
        c, _mod = client
        r = c.get("/")
        assert r.status_code == 200
        assert "Realism Eval" in r.text
        r2 = c.get("/media/item_0.png")
        assert r2.status_code == 200
