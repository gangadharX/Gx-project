from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from sqlmodel import Session, select
from typing import List, Optional
from app.core.database import get_session
from app.models.app import App, AppCreate, AppRead, AppSummary, AppCategory
from app.models.harm import HarmReport, HarmReportCreate, HarmReportRead
from app.models.rating import UserRating, UserRatingCreate, UserRatingRead
from app.models.user import User
from app.api.auth import get_optional_user, get_current_user
from app.services.scoring import update_app_scores
from datetime import datetime
import httpx
from app.services.safety_engine import run_safety_test
import asyncio

router = APIRouter(prefix="/apps", tags=["apps"])


@router.get("", response_model=List[AppSummary])
def list_apps(
    search: Optional[str] = None,
    category: Optional[AppCategory] = None,
    health_only: bool = False,
    verified_only: bool = False,
    limit: int = Query(default=20, le=100),
    offset: int = 0,
    session: Session = Depends(get_session),
):
    query = select(App)

    if search:
        query = query.where(App.name.ilike(f"%{search}%"))
    if category:
        query = query.where(App.category == category)
    if health_only:
        query = query.where(App.is_health == True)
    if verified_only:
        query = query.where(App.is_verified == True)

    query = query.order_by(App.guardian_score.desc().nullslast())
    query = query.offset(offset).limit(limit)

    return session.exec(query).all()

@router.post("", response_model=AppRead, status_code=201)
def register_app(
    app_in: AppCreate,
    background_tasks: BackgroundTasks,
    session: Session = Depends(get_session),
):
    # Check duplicate
    existing = session.exec(
        select(App).where(App.url == app_in.url)
    ).first()
    if existing:
        raise HTTPException(409, "App already registered")

    app = App.model_validate(app_in)
    session.add(app)
    session.commit()
    session.refresh(app)
    # Auto-run safety test in background after registration
    background_tasks.add_task(asyncio.get_event_loop().run_until_complete, run_safety_test(app.id))
    return app

@router.get("/{app_id}", response_model=AppRead)
def get_app(app_id: int, session: Session = Depends(get_session)):
    app = session.get(App, app_id)
    if not app:
        raise HTTPException(404, "App not found")
    return app
@router.post("/{app_id}/rate", response_model=UserRatingRead, status_code=201)
def rate_app(
    app_id: int,
    rating_in: UserRatingCreate,
    background_tasks: BackgroundTasks,
    request_ip: Optional[str] = None,
    session: Session = Depends(get_session),
    current_user: Optional[User] = Depends(get_optional_user)
):
    app = session.get(App, app_id)
    if not app:
        raise HTTPException(404, "App not found")

    rating = UserRating(app_id=app_id, **rating_in.dict())
    if current_user:
        rating.user_id = current_user.id
        rating.user_name = current_user.name
    session.add(rating)

    # Update count
    app.total_ratings += 1
    app.updated_at = datetime.utcnow()
    session.add(app)
    session.commit()
    session.refresh(rating)

    # Recalculate scores in background
    background_tasks.add_task(update_app_scores, app_id )

    return rating

@router.get("/{app_id}/ratings", response_model=List[UserRatingRead])
def get_ratings(
    app_id: int,
    limit: int = 10,
    session: Session = Depends(get_session),
):
    return session.exec(
        select(UserRating)
        .where(UserRating.app_id == app_id)
        .order_by(UserRating.created_at.desc())
        .limit(limit)
    ).all()

@router.post("/{app_id}/harm", response_model=HarmReportRead, status_code=201)
def report_harm(
    app_id: int,
    report_in: HarmReportCreate,
    background_tasks: BackgroundTasks,
    session: Session = Depends(get_session),
    current_user: Optional[User] = Depends(get_optional_user)
):
    app = session.get(App, app_id)
    if not app:
        raise HTTPException(404, "App not found")

    report = HarmReport(app_id=app_id, **report_in.dict())
    if current_user:
        report.user_id = current_user.id
        report.user_name = current_user.name
    session.add(report)

    app.total_harm_reports += 1
    app.updated_at = datetime.utcnow()

    # Auto-flag critical apps (severity 5 or 3+ reports)
    if report_in.severity == 5 or app.total_harm_reports >= 3:
        from app.models.app import AppBadge
        app.badge = AppBadge.avoid

    session.add(app)
    session.commit()
    session.refresh(report)

    background_tasks.add_task(update_app_scores, app_id )

    return report


@router.get("/{app_id}/harm", response_model=List[HarmReportRead])
def get_harm_reports(
    app_id: int,
    verified_only: bool = False,
    session: Session = Depends(get_session),
):
    query = select(HarmReport).where(HarmReport.app_id == app_id)
    if verified_only:
        query = query.where(HarmReport.verified == True)
    return session.exec(query.order_by(HarmReport.created_at.desc())).all()

@router.post("/{app_id}/test", status_code=200)
async def trigger_safety_test(
    app_id: int,
    session: Session = Depends(get_session),
):
    """Manually trigger safety test for an app."""
    app = session.get(App, app_id)
    if not app:
        raise HTTPException(404, "App not found")
    result = await run_safety_test(app_id)
    return result

async def test_all_unverified_apps():
    from app.core.database import engine
    from sqlmodel import Session
    with Session(engine) as session:
        # Get all apps that haven't been tested/verified yet
        apps = session.exec(select(App).where(App.is_verified == False)).all()
        app_ids = [app.id for app in apps]
    
    for app_id in app_ids:
        await run_safety_test(app_id)
        # Sleep 10s between apps to give the Gemini free tier quotas time to reset
        await asyncio.sleep(10)

@router.post("/test-all", status_code=202)
async def trigger_test_all(background_tasks: BackgroundTasks):
    """Trigger safety test for all unverified apps in the background."""
    background_tasks.add_task(asyncio.get_event_loop().run_until_complete, test_all_unverified_apps())
    return {"message": "Bulk safety test started in the background. Check back in a few minutes."}
