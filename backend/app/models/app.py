from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum



class AppCategory(str, Enum):
    health = "health"
    finance = "finance"
    productivity = "productivity"
    creative = "creative"
    education = "education"
    coding = "coding"
    other = "other"


class AppBadge(str, Enum):
    safe = "safe"
    caution = "caution"
    avoid = "avoid"
    unverified = "unverified"


# ── Shared fields (used for create + read) ──────────────────
class AppBase(SQLModel):
    name: str = Field(index=True)
    url: str = Field(unique=True)
    description: str
    category: AppCategory = AppCategory.other
    is_health: bool = False           # health apps get stricter tests
    company: Optional[str] = None
    logo_url: Optional[str] = None
    github_url: Optional[str] = None
    pricing: Optional[str] = None     # free / freemium / paid
    source: str = "manual"            # manual / producthunt / scraped


# ── DB Table ────────────────────────────────────────────────
class App(AppBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

    # Scores (updated by scoring service)
    guardian_score: Optional[float] = None   # 0-100 final
    safety_score: Optional[float] = None     # automated test score
    community_score: Optional[float] = None  # from user ratings
    harm_penalty: Optional[float] = None     # deducted for harm reports
    badge: AppBadge = AppBadge.unverified
    total_ratings: int = 0
    total_harm_reports: int = 0
    is_verified: bool = False
    last_tested: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


# ── API Schemas ──────────────────────────────────────────────
class AppCreate(AppBase):
    pass


class AppRead(AppBase):
    id: int
    guardian_score: Optional[float]
    badge: AppBadge
    total_ratings: int
    total_harm_reports: int
    is_verified: bool
    created_at: datetime


class AppSummary(SQLModel):
    """Lightweight card for directory listing."""
    id: int
    name: str
    url: str
    category: AppCategory
    is_health: bool
    guardian_score: Optional[float]
    badge: AppBadge
    total_ratings: int
    logo_url: Optional[str]

