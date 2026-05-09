from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.incident_category import IncidentCategory
from app.models.incident_type import IncidentType

# Mirrors the INSERT statements in the canonical SQL schema.
CATEGORIES = [
    {"name": "Fires", "description": "Fire-related incidents"},
    {"name": "Transportation", "description": "Transport-related incidents"},
    {"name": "Preemptive Measures", "description": "Preventive and preemptive operations"},
]

INCIDENT_TYPES_BY_CATEGORY = {
    "Fires": [
        {"name": "Forest Fire", "description": "Fire in a forested area"},
        {"name": "Field Fire", "description": "Fire in open fields or agricultural land"},
        {"name": "House Fire", "description": "Fire in a residential building"},
        {"name": "Urban Fire", "description": "Fire in an urban environment"},
    ],
    "Transportation": [
        {"name": "Patient Transportation", "description": "Transporting a patient"},
        {"name": "Hospital Transportation", "description": "Transport to or from a hospital"},
    ],
    "Preemptive Measures": [
        {"name": "Vehicle Transportation", "description": "Vehicle transport under preventive measures"},
    ],
}


def seed_categories(db: Session) -> dict[str, int]:
    """Insert missing categories and return a name → id mapping."""
    existing = {
        row.name: row.id
        for row in db.execute(select(IncidentCategory)).scalars().all()
    }

    for cat in CATEGORIES:
        if cat["name"] not in existing:
            record = IncidentCategory(**cat)
            db.add(record)
            db.flush()
            existing[record.name] = record.id

    db.commit()
    return existing


def seed_incident_types(db: Session, category_ids: dict[str, int]) -> None:
    """Insert missing incident types under their respective categories."""
    existing_names = {
        row.name
        for row in db.execute(select(IncidentType)).scalars().all()
    }

    for category_name, types in INCIDENT_TYPES_BY_CATEGORY.items():
        category_id = category_ids[category_name]
        for item in types:
            if item["name"] not in existing_names:
                db.add(IncidentType(category_id=category_id, **item))

    db.commit()


def seed_all(db: Session) -> None:
    category_ids = seed_categories(db)
    seed_incident_types(db, category_ids)
