from enum import Enum


class PriorityLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class IncidentStatus(str, Enum):
    REPORTED = "reported"
    DISPATCHED = "dispatched"
    EN_ROUTE = "en_route"
    ON_SCENE = "on_scene"
    CONTAINED = "contained"
    RESOLVED = "resolved"
    CLOSED = "closed"


class CallStatus(str, Enum):
    RECEIVED = "received"
    TRIAGED = "triaged"
    DISPATCHED = "dispatched"
    CLOSED = "closed"
    CANCELLED = "cancelled"
