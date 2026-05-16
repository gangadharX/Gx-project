"""Incident feed API endpoints."""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select, func
from typing import List, Optional
from app.core.database import get_session
from app.models.incident import (
    Incident, IncidentCreate, IncidentRead,
    IncidentSeverity, IncidentCategory, IncidentStatus,
)
from app.models.user import User
from app.api.auth import get_optional_user

router = APIRouter(prefix="/incidents", tags=["incidents"])


@router.get("", response_model=List[IncidentRead])
def list_incidents(
    severity: Optional[IncidentSeverity] = None,
    category: Optional[IncidentCategory] = None,
    region: Optional[str] = None,
    search: Optional[str] = None,
    limit: int = Query(default=30, le=100),
    offset: int = 0,
    session: Session = Depends(get_session),
):
    """Public feed — latest verified incidents."""
    query = select(Incident).where(Incident.is_public == True)

    if severity:
        query = query.where(Incident.severity == severity)
    if category:
        query = query.where(Incident.category == category)
    if region:
        query = query.where(Incident.region == region)
    if search:
        query = query.where(
            Incident.title.ilike(f"%{search}%") |
            Incident.app_name.ilike(f"%{search}%") |
            Incident.description.ilike(f"%{search}%")
        )

    query = query.order_by(Incident.created_at.desc())
    query = query.offset(offset).limit(limit)
    return session.exec(query).all()


@router.get("/stats")
def incident_stats(session: Session = Depends(get_session)):
    """Quick stats for the feed header."""
    total = session.exec(
        select(func.count(Incident.id)).where(Incident.is_public == True)
    ).one()
    critical = session.exec(
        select(func.count(Incident.id)).where(
            Incident.is_public == True,
            Incident.severity == IncidentSeverity.critical,
        )
    ).one()
    apps_named = session.exec(
        select(func.count(func.distinct(Incident.app_name)))
    ).one()
    return {
        "total_incidents": total,
        "critical_incidents": critical,
        "apps_named": apps_named,
    }


@router.get("/{incident_id}", response_model=IncidentRead)
def get_incident(incident_id: int, session: Session = Depends(get_session)):
    incident = session.get(Incident, incident_id)
    if not incident or not incident.is_public:
        raise HTTPException(404, "Incident not found")
    return incident



@router.post("", response_model=IncidentRead, status_code=201)
def report_incident(
    data: IncidentCreate,
    session: Session = Depends(get_session),
    current_user: Optional[User] = Depends(get_optional_user)
):
    """Submit a new incident report."""
    incident = Incident.model_validate(data)
    if current_user:
        incident.user_id = current_user.id
        incident.user_name = current_user.name
    session.add(incident)
    session.commit()
    session.refresh(incident)
    return incident
