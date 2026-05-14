from fastapi import APIRouter

from app.api.v1.endpoints import (
    assistant,
    employees,
    health,
    incident_categories,
    incident_types,
    incidents,
    phone_calls,
    transcripts,
    settings
)

api_router = APIRouter()
api_router.include_router(health.router, tags=["health"])
api_router.include_router(employees.router, prefix="/employees", tags=["employees"])
api_router.include_router(incident_categories.router, prefix="/incident-categories", tags=["incident-categories"])
api_router.include_router(incident_types.router, prefix="/incident-types", tags=["incident-types"])
api_router.include_router(incidents.router, prefix="/incidents", tags=["incidents"])
api_router.include_router(phone_calls.router, prefix="/phone-calls", tags=["phone-calls"])
api_router.include_router(assistant.router, prefix="/assistant", tags=["assistant"])
api_router.include_router(transcripts.router, prefix="/transcripts", tags=["transcripts"])


api_router.include_router(
    settings.router,
    prefix="/settings",
    tags=["settings"],
)
