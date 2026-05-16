from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum


class HarmCategory(str, Enum):
    wrong_medical = "wrong_medical_advice"
    dangerous_suggestion = "dangerous_suggestion"
    manipulation = "manipulation"
    privacy = "privacy_violation"
    bias = "bias_discrimination"
    self_harm = "self_harm_facilitation"
    misinformation = "misinformation"
    other = "other"


class HarmReport(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    app_id: int = Field(foreign_key="app.id", index=True)

    severity: int = Field(ge=1, le=5)        # 1=minor 5=life-threatening
    category: HarmCategory
    description: str = Field(max_length=2000)

    # Optionally capture exact interaction
    prompt_used: Optional[str] = None        # what user asked the app
    app_response: Optional[str] = None       # what app said (the harm)

    user_id: Optional[int] = Field(default=None, foreign_key="user.id", index=True)
    user_name: Optional[str] = None

    # Moderation
    verified: bool = False                   # your team marks this
    rejected: bool = False
    user_ip: Optional[str] = None

    created_at: datetime = Field(default_factory=datetime.utcnow)


class HarmReportCreate(SQLModel):
    severity: int = Field(ge=1, le=5)
    category: HarmCategory
    description: str
    prompt_used: Optional[str] = None
    app_response: Optional[str] = None

class HarmReportRead(HarmReportCreate):
    id: int
    app_id: int
    verified: bool
    created_at: datetime
    user_id: Optional[int] = None
    user_name: Optional[str] = None


