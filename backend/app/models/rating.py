from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime


class UserRatingBase(SQLModel):
    # 5 structured dimensions — each 1 to 5 stars
    accuracy: int = Field(ge=1, le=5)        # Did it give correct info?
    safety: int = Field(ge=1, le=5)          # Did it feel safe?
    helpfulness: int = Field(ge=1, le=5)     # Did it actually help?
    transparency: int = Field(ge=1, le=5)    # Clear about limitations?
    trust: int = Field(ge=1, le=5)           # Safe for vulnerable users?

    review: Optional[str] = Field(default=None, max_length=1000)
    use_case: Optional[str] = None           # "health advice" / "work" etc.
    used_for_health: bool = False


class UserRating(UserRatingBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    app_id: int = Field(foreign_key="app.id", index=True)
    user_id: Optional[int] = Field(default=None, foreign_key="users.id", index=True)
    user_name: Optional[str] = None
    user_ip: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

    @property
    def average(self) -> float:
        return (self.accuracy + self.safety + self.helpfulness +
                self.transparency + self.trust) / 5


class UserRatingCreate(UserRatingBase):
    pass


class UserRatingRead(UserRatingBase):
    id: int
    app_id: int
    created_at: datetime
