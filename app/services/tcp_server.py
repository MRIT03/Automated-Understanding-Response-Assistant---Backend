import asyncio
import json
import logging
from typing import Any

from app.services.transcript_store import transcript_store

logger = logging.getLogger("whisper_tcp")
logger.setLevel(logging.INFO)

HOST = "0.0.0.0"
PORT = 5001


async def process_transcript(event: dict[str, Any]):
    text = event.get("text", "").strip()

    if not text:
        return

    payload = {
        "type": "transcript",
        "text": text,
        "start": event.get("start"),
        "end": event.get("end"),
        "is_final": True,
    }

    await transcript_store.add(payload)

    print(f"[TCP] Clean transcript: {payload}", flush=True)
    logger.info(f"Clean transcript: {payload}")


async def handle_client(reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
    addr = writer.get_extra_info("peername")

    print(f"[TCP] Bridge connected from {addr}", flush=True)
    logger.info(f"Bridge connected from {addr}")

    try:
        while True:
            line = await reader.readline()

            if not line:
                print("[TCP] Empty line / connection closed", flush=True)
                break

            raw = line.decode("utf-8").strip()

            print(f"[TCP] Raw received: {raw}", flush=True)

            if not raw:
                continue

            if not raw.startswith("{"):
                print(f"[TCP] Ignored non-JSON: {raw}", flush=True)
                continue

            try:
                event = json.loads(raw)
            except json.JSONDecodeError as e:
                print(f"[TCP] Invalid JSON ignored: {e} | {raw}", flush=True)
                continue

            if "text" not in event:
                print(f"[TCP] JSON without text ignored: {event}", flush=True)
                continue

            await process_transcript(event)

    finally:
        print(f"[TCP] Bridge disconnected from {addr}", flush=True)
        logger.info(f"Bridge disconnected from {addr}")
        writer.close()
        await writer.wait_closed()


async def start_tcp_server():
    print(f"[TCP] Starting TCP server on {HOST}:{PORT}", flush=True)

    server = await asyncio.start_server(handle_client, HOST, PORT)

    print(f"[TCP] Listening on {HOST}:{PORT}", flush=True)

    async with server:
        await server.serve_forever()