from __future__ import annotations

from datetime import datetime
from pydantic import BaseModel, ConfigDict, field_validator
import bleach

from ..models import NotificationType

class NotificationRead(BaseModel):
    id: int
    user_id: int
    title: str
    message: str
    type: str

    @field_validator('title', 'message')
    @classmethod
    def sanitize_html(cls, v: str) -> str:
        return bleach.clean(v, strip=True, tags=[])

class NotificationUpdate(BaseModel):
    is_read: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
