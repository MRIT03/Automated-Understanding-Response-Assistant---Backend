from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.incident_type import IncidentType
from app.models.enums import PriorityLevel

DEFAULT_INCIDENT_TYPES = [
    {
        "code": "FIRE_STRUCTURE",
        "name": "Structure Fire",
        "category": "fire",
        "description": "Residential or commercial building fire.",
        "default_priority": PriorityLevel.CRITICAL,
    },
    {
        "code": "FIRE_VEHICLE",
        "name": "Vehicle Fire",
        "category": "fire",
        "description": "Fire involving a car, truck, bus, or other vehicle.",
        "default_priority": PriorityLevel.HIGH,
    },
    {
        "code": "EMS_TRANSPORT",
        "name": "Ambulance Transport",
        "category": "ems",
        "description": "Medical transport request requiring ambulance support.",
        "default_priority": PriorityLevel.HIGH,
    },
    {
        "code": "RESCUE_TECH",
        "name": "Technical Rescue",
        "category": "rescue",
        "description": "Complex rescue such as confined space, collapse, or high-angle rescue.",
        "default_priority": PriorityLevel.CRITICAL,
    },
    {
        "code": "RESCUE_WATER",
        "name": "Water Rescue",
        "category": "rescue",
        "description": "Rescue involving rivers, sea, flooding, or submerged vehicles.",
        "default_priority": PriorityLevel.CRITICAL,
    },
]


def seed_incident_types(db: Session) -> None:
    existing_codes = {row[0] for row in db.execute(select(IncidentType.code)).all()}
    for item in DEFAULT_INCIDENT_TYPES:
        if item["code"] not in existing_codes:
            db.add(IncidentType(**item))
    db.commit()
