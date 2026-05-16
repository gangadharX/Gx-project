"""AI Harm Incident model — public feed of real AI harm events."""
from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime, date
from enum import Enum


class IncidentSeverity(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"
    critical = "critical"


class IncidentCategory(str, Enum):
    medical = "medical_harm"
    financial = "financial_harm"
    privacy = "privacy_breach"
    discrimination = "discrimination"
    misinformation = "misinformation"
    manipulation = "manipulation"
    child_safety = "child_safety"
    mental_health = "mental_health"
    legal = "legal_harm"
    other = "other"


class IncidentStatus(str, Enum):
    reported = "reported"
    verified = "verified"
    investigating = "investigating"
    resolved = "resolved"


class Incident(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    app_id: Optional[int] = Field(default=None, foreign_key="app.id", index=True)

    # Core info
    app_name: str = Field(index=True)
    title: str
    description: str = Field(max_length=5000)
    severity: IncidentSeverity
    category: IncidentCategory

    # Details
    affected_users: Optional[str] = None        # "patients", "children", "students"
    region: Optional[str] = None                 # "EU", "US", "India", etc.
    source_url: Optional[str] = None             # news article / proof
    source_name: Optional[str] = None            # "Reuters", "user report"
    evidence_summary: Optional[str] = None       # brief evidence

    # Moderation
    status: IncidentStatus = IncidentStatus.reported
    verified_by: Optional[str] = None
    is_public: bool = True

    user_id: Optional[int] = Field(default=None, foreign_key="user.id", index=True)
    user_name: Optional[str] = None

    # Dates
    incident_date: Optional[date] = None         # when it happened
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class IncidentCreate(SQLModel):
    app_name: str
    title: str
    description: str
    severity: IncidentSeverity
    category: IncidentCategory
    affected_users: Optional[str] = None
    region: Optional[str] = None
    source_url: Optional[str] = None
    source_name: Optional[str] = None
    incident_date: Optional[date] = None
    app_id: Optional[int] = None


class IncidentRead(SQLModel):
    id: int
    app_name: str
    title: str
    description: str
    severity: IncidentSeverity
    category: IncidentCategory
    affected_users: Optional[str]
    region: Optional[str]
    source_url: Optional[str]
    source_name: Optional[str]
    status: IncidentStatus
    incident_date: Optional[date]
    created_at: datetime
    user_id: Optional[int] = None
    user_name: Optional[str] = None
