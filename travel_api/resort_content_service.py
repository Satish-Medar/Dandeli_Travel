from travel_tools.resort_update_store import diff_resort_update
def get_resort_update_diff(update_id: str) -> dict:
    return diff_resort_update(update_id)
# Business logic for resort updates and approvals.
# File: travel_api/resort_content_service.py

from travel_tools.resort_update_store import approve_pending_update, create_pending_update, list_owner_resorts, list_pending_updates, load_live_resorts, reject_pending_update
from travel_tools.search_engine import invalidate_search_cache
from travel_tools.vectorstore_provider import reset_vectorstore


def submit_resort_update(payload: dict) -> dict:
    return create_pending_update(
        resort_id=payload.get("resort_id"),
        owner_id=payload["owner_id"],
        changes=payload["changes"],
        submitted_by=payload.get("submitted_by"),
        request_type=payload.get("request_type", "update"),
    )


def fetch_resort_updates(status: str | None = None, owner_id: str | None = None) -> list[dict]:
    return list_pending_updates(status=status, owner_id=owner_id)


def approve_resort_update(update_id: str, reviewer_id: str, review_notes: str | None = None) -> dict:
    approved_update = approve_pending_update(update_id, reviewer_id, review_notes)
    invalidate_search_cache()
    reset_vectorstore()
    return approved_update


def reject_resort_update(update_id: str, reviewer_id: str, review_notes: str | None = None) -> dict:
    rejected_update = reject_pending_update(update_id, reviewer_id, review_notes)
    invalidate_search_cache()
    reset_vectorstore()
    return rejected_update


def fetch_live_resorts() -> list[dict]:
    return load_live_resorts()


def fetch_owner_resorts(owner_id: str) -> list[dict]:
    return list_owner_resorts(owner_id)
