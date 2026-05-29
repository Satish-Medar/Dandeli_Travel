# Manages published resort data and owner approval workflows.
# File: travel_tools/resort_update_store.py

import json
import uuid
from copy import deepcopy
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
SEED_RESORTS_PATH = BASE_DIR / "data" / "json_files" / "resorts.json"
LIVE_RESORTS_PATH = BASE_DIR / "data" / "local_live_resorts.json"
PENDING_UPDATES_PATH = BASE_DIR / "data" / "local_pending_resort_updates.json"
CREATE_REQUIRED_FIELDS = ["name", "category", "city", "location", "price"]
PROTECTED_UPDATE_FIELDS = {"id", "owner_id", "last_approved_update_id", "last_approved_by"}


def utc_now() -> str:
    return datetime.utcnow().replace(microsecond=0).isoformat(timespec="seconds") + "Z"


def _ensure_parent(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def _read_json(path: Path, fallback):
    if not path.exists():
        return deepcopy(fallback)
    try:
        content = path.read_text(encoding="utf-8")
        data = json.loads(content)
        return data if data is not None else deepcopy(fallback)
    except (OSError, json.JSONDecodeError):
        return deepcopy(fallback)


def _write_json(path: Path, data) -> None:
    _ensure_parent(path)
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")


def load_seed_resorts() -> list[dict]:
    return _read_json(SEED_RESORTS_PATH, [])


def load_live_resorts() -> list[dict]:
    live_resorts = _read_json(LIVE_RESORTS_PATH, None)
    if live_resorts:
        return deepcopy(live_resorts)

    seed_resorts = load_seed_resorts()
    _write_json(LIVE_RESORTS_PATH, seed_resorts)
    return deepcopy(seed_resorts)


def save_live_resorts(resorts: list[dict]) -> None:
    _write_json(LIVE_RESORTS_PATH, resorts)


def load_pending_updates() -> list[dict]:
    return _read_json(PENDING_UPDATES_PATH, [])


def save_pending_updates(updates: list[dict]) -> None:
    _write_json(PENDING_UPDATES_PATH, updates)


def _normalize_owner_id(owner_id: str) -> str:
    cleaned = str(owner_id or "").strip()
    if not cleaned:
        raise ValueError("Owner ID is required")
    return cleaned


def _find_resort(resorts: list[dict], resort_id: str) -> dict | None:
    return next((item for item in resorts if str(item.get("id")) == str(resort_id)), None)


def _assert_owner_can_update(resort: dict, owner_id: str) -> None:
    assigned_owner = str(resort.get("owner_id") or "").strip()
    if not assigned_owner:
        raise PermissionError(
            "This resort is not assigned to an owner yet. Ask an admin to assign ownership before updates are allowed."
        )
    if assigned_owner != owner_id:
        raise PermissionError("You can only update resorts that belong to your owner account")


def _clean_update_changes(changes: dict) -> dict:
    return {key: value for key, value in changes.items() if key not in PROTECTED_UPDATE_FIELDS}


def _next_resort_id(resorts: list[dict]) -> int:
    numeric_ids = []
    for resort in resorts:
        try:
            numeric_ids.append(int(resort.get("id")))
        except (TypeError, ValueError):
            continue
    return (max(numeric_ids) if numeric_ids else 0) + 1


def _merge_nested_values(existing, new_value):
    if isinstance(existing, dict) and isinstance(new_value, dict):
        merged = deepcopy(existing)
        for key, value in new_value.items():
            if key in merged and isinstance(merged[key], (dict, list)) and isinstance(value, (dict, list)):
                merged[key] = _merge_nested_values(merged[key], value)
            else:
                merged[key] = deepcopy(value)
        return merged
    if isinstance(existing, list) and isinstance(new_value, list):
        return deepcopy(new_value)
    return deepcopy(new_value)


def create_pending_update(
    resort_id: str | None,
    owner_id: str,
    changes: dict,
    submitted_by: str | None = None,
    request_type: str = "update",
) -> dict:
    request_type = str(request_type or "update").strip().lower()
    owner_id = _normalize_owner_id(owner_id)
    if not changes:
        raise ValueError("At least one change must be provided")
    if request_type not in {"create", "update"}:
        raise ValueError("Request type must be create or update")

    live_resorts = load_live_resorts()
    if request_type == "update":
        if not resort_id:
            raise ValueError("Resort ID is required for updates")
        resort = _find_resort(live_resorts, resort_id)
        if resort is None:
            raise KeyError(f"Resort {resort_id} not found")
        _assert_owner_can_update(resort, owner_id)
        changes = _clean_update_changes(changes)
        if not changes:
            raise ValueError("No editable changes were provided")
    else:
        missing_fields = [field for field in CREATE_REQUIRED_FIELDS if not changes.get(field)]
        if missing_fields:
            raise ValueError(f"New resorts require: {', '.join(missing_fields)}")
        resort_id = f"new-{uuid.uuid4().hex[:8]}"
        changes = deepcopy(changes)
        changes["owner_id"] = owner_id

    updates = load_pending_updates()
    update = {
        "id": str(uuid.uuid4()),
        "resort_id": str(resort_id),
        "owner_id": owner_id,
        "submitted_by": submitted_by or owner_id,
        "request_type": request_type,
        "status": "pending",
        "changes": deepcopy(changes),
        "submitted_at": utc_now(),
        "updated_at": utc_now(),
        "reviewer_id": None,
        "reviewed_at": None,
        "review_notes": None,
    }
    updates.append(update)
    save_pending_updates(updates)
    return deepcopy(update)


def list_pending_updates(status: str | None = None, owner_id: str | None = None) -> list[dict]:
    updates = load_pending_updates()
    if status:
        updates = [item for item in updates if item.get("status") == status]
    if owner_id:
        updates = [item for item in updates if str(item.get("owner_id")) == str(owner_id)]
    return sorted(updates, key=lambda item: item.get("submitted_at", ""), reverse=True)


def list_owner_resorts(owner_id: str) -> list[dict]:
    owner_id = _normalize_owner_id(owner_id)
    return [resort for resort in load_live_resorts() if str(resort.get("owner_id") or "").strip() == owner_id]


def diff_resort_update(update_id: str) -> dict:
    updates = load_pending_updates()
    update = next((u for u in updates if str(u.get("id")) == str(update_id)), None)
    if not update:
        raise KeyError(f"Pending update {update_id} not found")

    if update.get("request_type") == "create":
        after = deepcopy(update["changes"])
        after.setdefault("id", "(assigned on approval)")
        return {"before": None, "after": after, "changes": deepcopy(update["changes"])}

    live_resorts = load_live_resorts()
    resort = _find_resort(live_resorts, update["resort_id"])
    if resort is None:
        raise KeyError(f"Resort {update['resort_id']} not found")
    before = deepcopy(resort)
    after = _merge_nested_values(resort, update["changes"])
    return {"before": before, "after": after, "changes": deepcopy(update["changes"])}


def approve_pending_update(update_id: str, reviewer_id: str, review_notes: str | None = None) -> dict:
    updates = load_pending_updates()
    for index, update in enumerate(updates):
        if str(update.get("id")) == str(update_id):
            if update.get("status") != "pending":
                raise ValueError(f"Update {update_id} is already {update['status']}")

            live_resorts = load_live_resorts()
            if update.get("request_type") == "create":
                merged_resort = deepcopy(update["changes"])
                merged_resort["id"] = _next_resort_id(live_resorts)
                merged_resort["owner_id"] = update["owner_id"]
                merged_resort["created_at"] = utc_now()
                merged_resort["updated_at"] = utc_now()
                merged_resort["last_approved_update_id"] = update["id"]
                merged_resort["last_approved_by"] = reviewer_id
                live_resorts.append(merged_resort)
                update["resort_id"] = str(merged_resort["id"])
                save_live_resorts(live_resorts)
            else:
                resort = _find_resort(live_resorts, update["resort_id"])
                if resort is None:
                    raise KeyError(f"Resort {update['resort_id']} not found")
                _assert_owner_can_update(resort, update["owner_id"])

                merged_resort = _merge_nested_values(resort, update["changes"])
                merged_resort["updated_at"] = utc_now()
                merged_resort["last_approved_update_id"] = update["id"]
                merged_resort["last_approved_by"] = reviewer_id

                updated_resorts = []
                for item in live_resorts:
                    if str(item.get("id")) == str(resort["id"]):
                        updated_resorts.append(merged_resort)
                    else:
                        updated_resorts.append(item)
                save_live_resorts(updated_resorts)

            update["status"] = "approved"
            update["reviewer_id"] = reviewer_id
            update["reviewed_at"] = utc_now()
            update["review_notes"] = review_notes
            update["updated_at"] = utc_now()
            updates[index] = update
            save_pending_updates(updates)
            return deepcopy(update)
    raise KeyError(f"Pending update {update_id} not found")


def reject_pending_update(update_id: str, reviewer_id: str, review_notes: str | None = None) -> dict:
    updates = load_pending_updates()
    for index, update in enumerate(updates):
        if str(update.get("id")) == str(update_id):
            if update.get("status") != "pending":
                raise ValueError(f"Update {update_id} is already {update['status']}")
            update["status"] = "rejected"
            update["reviewer_id"] = reviewer_id
            update["reviewed_at"] = utc_now()
            update["review_notes"] = review_notes
            update["updated_at"] = utc_now()
            updates[index] = update
            save_pending_updates(updates)
            return deepcopy(update)
    raise KeyError(f"Pending update {update_id} not found")
