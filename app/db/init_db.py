from app.db.base import Base
from app.db.session import engine
from app.models.call import Call
from app.models.dispatcher import Dispatcher
from app.models.incident import Incident
from app.models.incident_type import IncidentType


def init_db() -> None:
    Base.metadata.create_all(bind=engine)
