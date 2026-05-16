from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime


class GuardianScore(SQLModel, table=True):
    """Full GUARDIAN test result — one row per test run."""
    id: Optional[int] = Field(default=None, primary_key=True)
    app_id: int = Field(foreign_key="app.id", index=True)

    # 8 dimension scores (0-100 each)
    user_safety: float = 0
    non_deception: float = 0
    adversarial: float = 0
    fairness: float = 0
    transparency: float = 0
    robustness: float = 0
    governance: float = 0
    incident_response: float = 0

    # Aggregates
    final_score: float = 0
    critical_failures: int = 0

    # Standards compliance flags
    eu_ai_act: bool = False
    nist_rmf: bool = False
    un_guidelines: bool = False
    oecd: bool = False

    # Generated public report
    report_summary: Optional[str] = None
    test_version: str = "GUARDIAN-v1.0"
    tested_at: datetime = Field(default_factory=datetime.utcnow)


class GuardianScoreRead(SQLModel):
    user_safety: float
    non_deception: float
    adversarial: float
    fairness: float
