from fastapi import APIRouter

from app.api.v1.endpoints import assistant, calls, dispatchers, health, incident_types, incidents

api_router = APIRouter()
api_router.include_router(health.router, tags=["health"])
api_router.include_router(dispatchers.router, prefix="/dispatchers", tags=["dispatchers"])
api_router.include_router(incident_types.router, prefix="/incident-types", tags=["incident-types"])
api_router.include_router(incidents.router, prefix="/incidents", tags=["incidents"])
api_router.include_router(calls.router, prefix="/calls", tags=["calls"])
api_router.include_router(assistant.router, prefix="/assistant", tags=["assistant"])
