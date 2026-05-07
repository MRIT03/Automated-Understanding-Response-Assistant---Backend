from __future__ import annotations

from fastapi import APIRouter

from app.services.transcript_store import transcript_store

router = APIRouter()


@router.get("/live")
async def get_live_transcript():
    """Return the current live transcript assembled from TCP chunks."""
    items = await transcript_store.get_all()
    latest = items[-1] if items else None

    return {
        "count": len(items),
        "latest": latest,
        "text": " ".join(item["text"] for item in items if item.get("text")),
        "items": items,
    }


@router.delete("/live")
async def clear_live_transcript():
    """Clear the live transcript displayed by the frontend."""
    await transcript_store.clear()
    return {"ok": True}
