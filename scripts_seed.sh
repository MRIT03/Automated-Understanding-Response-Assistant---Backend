#!/usr/bin/env bash
python - <<'PY'
from app.db.session import SessionLocal
from app.db.seed_data import seed_incident_types

with SessionLocal() as db:
    seed_incident_types(db)
    print('Seeded incident types.')
PY
