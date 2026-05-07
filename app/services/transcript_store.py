from __future__ import annotations

import asyncio
from datetime import datetime, timezone
from typing import Any


class TranscriptStore:
    """Small in-memory store for live transcript chunks.

    This keeps the latest TCP transcript data available to the FastAPI layer.
    It is intentionally simple and resets when the backend restarts.
    """

    def __init__(self) -> None:
        self._lock = asyncio.Lock()
        self._items: list[dict[str, Any]] = []

    async def add(self, payload: dict[str, Any]) -> dict[str, Any]:
        async with self._lock:
            item = {
                "id": len(self._items) + 1,
                "type": payload.get("type", "transcript"),
                "text": payload.get("text", ""),
                "start": payload.get("start"),
                "end": payload.get("end"),
                "is_final": payload.get("is_final", True),
                "received_at": datetime.now(timezone.utc).isoformat(),
            }
            self._items.append(item)
            return item

    async def get_all(self) -> list[dict[str, Any]]:
        async with self._lock:
            return list(self._items)

    async def get_latest(self) -> dict[str, Any] | None:
        async with self._lock:
            if not self._items:
                return None
            return dict(self._items[-1])

    async def clear(self) -> None:
        async with self._lock:
            self._items.clear()


transcript_store = TranscriptStore()
