from app.db.base import Base
from app.db.session import engine

# Import all models so Base.metadata is populated before create_all runs.
from app.models.employee import Employee  # noqa: F401
from app.models.incident_category import IncidentCategory  # noqa: F401
from app.models.incident_type import IncidentType  # noqa: F401
from app.models.incident import Incident  # noqa: F401
from app.models.phone_call import PhoneCall  # noqa: F401


def init_db() -> None:
    Base.metadata.create_all(bind=engine)
