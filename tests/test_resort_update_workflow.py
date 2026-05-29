import json


def _seed_test_resorts(tmp_path):
    seed_path = tmp_path / "seed_resorts.json"
    live_path = tmp_path / "live_resorts.json"
    pending_path = tmp_path / "pending_updates.json"
    seed_data = [
        {
            "id": 1,
            "name": "River Valley",
            "category": "Adventure Resort",
            "city": "Dandeli",
            "location": "Dandeli",
            "price": 5000,
            "rating": 4.5,
            "amenities": ["pool", "wifi"],
            "activities_onsite": ["rafting"],
            "activities_nearby": ["bird watching"],
            "family_friendly": True,
            "available_rooms": 10,
            "occupied_rooms": 2,
            "special_offer": "None",
            "availability_status": "open",
            "owner_id": "owner-001",
        }
    ]
    seed_path.write_text(json.dumps(seed_data), encoding="utf-8")
    live_path.write_text(json.dumps(seed_data), encoding="utf-8")
    pending_path.write_text("[]", encoding="utf-8")
    return seed_path, live_path, pending_path


def test_submit_and_approve_resort_update(test_client, monkeypatch, tmp_path):
    from travel_tools import resort_update_store
    from travel_tools.search_engine import load_all_documents

    seed_path, live_path, pending_path = _seed_test_resorts(tmp_path)
    monkeypatch.setattr(resort_update_store, "SEED_RESORTS_PATH", seed_path)
    monkeypatch.setattr(resort_update_store, "LIVE_RESORTS_PATH", live_path)
    monkeypatch.setattr(resort_update_store, "PENDING_UPDATES_PATH", pending_path)

    submit_response = test_client.post(
        "/resorts/updates",
        json={
            "resort_id": "1",
            "owner_id": "owner-001",
            "changes": {
                "available_rooms": 6,
                "occupied_rooms": 4,
                "special_offer": "20% off weekend stay",
                "availability_status": "limited"
            },
        },
    )
    assert submit_response.status_code == 200
    payload = submit_response.json()
    assert payload["status"] == "pending"
    assert payload["resort_id"] == "1"

    pending_response = test_client.get("/resorts/updates?status=pending")
    assert pending_response.status_code == 200
    assert len(pending_response.json()) == 1

    approve_response = test_client.post(
        f"/resorts/updates/{payload['id']}/approve",
        json={"reviewer_id": "admin-001", "review_notes": "Approved for weekend promotion"},
    )
    assert approve_response.status_code == 200
    approved = approve_response.json()
    assert approved["status"] == "approved"
    assert approved["reviewer_id"] == "admin-001"

    published_response = test_client.get("/resorts")
    assert published_response.status_code == 200
    published = published_response.json()
    resort = next(item for item in published if str(item["id"]) == "1")
    assert resort["available_rooms"] == 6
    assert resort["occupied_rooms"] == 4
    assert resort["special_offer"] == "20% off weekend stay"
    assert resort["availability_status"] == "limited"

    docs = load_all_documents()
    doc = next(item for item in docs if item["metadata"]["id"] == 1)
    assert doc["metadata"]["available_rooms"] == 6
    assert doc["metadata"]["occupied_rooms"] == 4
    assert doc["metadata"]["special_offer"] == "20% off weekend stay"
    assert doc["metadata"]["availability_status"] == "limited"


def test_owner_cannot_update_unowned_resort(test_client, monkeypatch, tmp_path):
    from travel_tools import resort_update_store

    seed_path, live_path, pending_path = _seed_test_resorts(tmp_path)
    monkeypatch.setattr(resort_update_store, "SEED_RESORTS_PATH", seed_path)
    monkeypatch.setattr(resort_update_store, "LIVE_RESORTS_PATH", live_path)
    monkeypatch.setattr(resort_update_store, "PENDING_UPDATES_PATH", pending_path)

    response = test_client.post(
        "/resorts/updates",
        json={
            "request_type": "update",
            "resort_id": "1",
            "owner_id": "owner-999",
            "changes": {"available_rooms": 1},
        },
    )

    assert response.status_code == 403


def test_submit_and_approve_new_resort(test_client, monkeypatch, tmp_path):
    from travel_tools import resort_update_store

    seed_path, live_path, pending_path = _seed_test_resorts(tmp_path)
    monkeypatch.setattr(resort_update_store, "SEED_RESORTS_PATH", seed_path)
    monkeypatch.setattr(resort_update_store, "LIVE_RESORTS_PATH", live_path)
    monkeypatch.setattr(resort_update_store, "PENDING_UPDATES_PATH", pending_path)

    submit_response = test_client.post(
        "/resorts/updates",
        json={
            "request_type": "create",
            "owner_id": "owner-002",
            "changes": {
                "name": "Kali River Hideaway",
                "category": "Eco Resort",
                "city": "Dandeli",
                "location": "Ganeshgudi Road",
                "price": 4200,
                "amenities": ["wifi", "restaurant"],
                "available_rooms": 8,
            },
        },
    )
    assert submit_response.status_code == 200
    pending = submit_response.json()
    assert pending["request_type"] == "create"
    assert pending["status"] == "pending"

    diff_response = test_client.get(f"/resorts/updates/{pending['id']}/diff")
    assert diff_response.status_code == 200
    assert diff_response.json()["before"] is None

    approve_response = test_client.post(
        f"/resorts/updates/{pending['id']}/approve",
        json={"reviewer_id": "admin-001"},
    )
    assert approve_response.status_code == 200
    approved = approve_response.json()
    assert approved["status"] == "approved"

    owner_resorts_response = test_client.get("/owners/owner-002/resorts")
    assert owner_resorts_response.status_code == 200
    owner_resorts = owner_resorts_response.json()
    assert len(owner_resorts) == 1
    assert owner_resorts[0]["name"] == "Kali River Hideaway"
    assert owner_resorts[0]["owner_id"] == "owner-002"
