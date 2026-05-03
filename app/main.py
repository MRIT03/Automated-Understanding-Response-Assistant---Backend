from __future__ import annotations

import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import api_router
from app.core.config import settings
from app.db.init_db import init_db

from app.services.tcp_server import start_tcp_server
from app.services.offline_tcp_server import start_offline_tcp_server


@asynccontextmanager
async def lifespan(_: FastAPI):
    if settings.auto_create_tables:
        init_db()

    print("[APP] Starting live TCP server task", flush=True)
    live_tcp_task = asyncio.create_task(start_tcp_server())

    print("[APP] Starting offline TCP server task", flush=True)
    offline_tcp_task = asyncio.create_task(start_offline_tcp_server())

    yield

    print("[APP] Stopping TCP server tasks", flush=True)

    live_tcp_task.cancel()
    offline_tcp_task.cancel()

    try:
        await live_tcp_task
    except asyncio.CancelledError:
        pass

    try:
        await offline_tcp_task
    except asyncio.CancelledError:
        pass


app = FastAPI(title=settings.app_name, debug=settings.debug, lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allow_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix=settings.api_v1_prefix)