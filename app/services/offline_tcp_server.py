import asyncio
import json
from typing import Any

HOST = "0.0.0.0"
PORT = 5002


async def process_offline_transcript(event: dict[str, Any]):
    text = event.get("text", "").strip()

    if not text:
        return

    payload = {
        "type": "offline_transcript",
        "text": text,
        "audio_path": event.get("audio_path"),
        "segment_id": event.get("segment_id"),
    }

    print(f"[OFFLINE TCP] Final transcript: {payload}", flush=True)

    # Later:
    # await save_final_transcript(payload)
    # await broadcast_final_to_frontend(payload)
    # await send_to_agent(payload)


async def handle_offline_client(
    reader: asyncio.StreamReader,
    writer: asyncio.StreamWriter,
):
    addr = writer.get_extra_info("peername")
    print(f"[OFFLINE TCP] Bridge connected from {addr}", flush=True)

    try:
        while True:
            line = await reader.readline()

            if not line:
                break

            raw = line.decode("utf-8").strip()

            if not raw:
                continue

            print(f"[OFFLINE TCP] Raw received: {raw}", flush=True)

            try:
                event = json.loads(raw)
            except json.JSONDecodeError as e:
                print(f"[OFFLINE TCP] Invalid JSON ignored: {e}", flush=True)
                continue

            if event.get("type") != "offline_transcript":
                print(f"[OFFLINE TCP] Ignored wrong event type: {event}", flush=True)
                continue

            await process_offline_transcript(event)

    finally:
        print(f"[OFFLINE TCP] Bridge disconnected from {addr}", flush=True)
        writer.close()
        await writer.wait_closed()


async def start_offline_tcp_server():
    print(f"[OFFLINE TCP] Starting server on {HOST}:{PORT}", flush=True)

    server = await asyncio.start_server(handle_offline_client, HOST, PORT)

    print(f"[OFFLINE TCP] Listening on {HOST}:{PORT}", flush=True)

    async with server:
        await server.serve_forever()