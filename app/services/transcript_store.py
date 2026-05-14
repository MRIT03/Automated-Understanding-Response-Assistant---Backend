from __future__ import annotations

import asyncio
from datetime import datetime, timezone
from typing import Any


class TranscriptStore:
    """In-memory store for live transcript chunks.

    Each item carries the call_id from the bridge so the rest of the system
    can correlate live chunks with the post-call offline transcript.
    """

    def __init__(self) -> None:
        self._lock = asyncio.Lock()
        self._items: list[dict[str, Any]] = []

    async def add(self, payload: dict[str, Any]) -> dict[str, Any]:
        async with self._lock:
            item = {
                "id": len(self._items) + 1,
                "call_id": payload.get("call_id"),
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
            return dict(self._items[-1]) if self._items else None

    async def clear(self) -> None:
        async with self._lock:
            self._items.clear()


transcript_store = TranscriptStore()
