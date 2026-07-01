from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class SchoolSettingUpsert(BaseModel):
    value: str = Field(min_length=1)
    description: str | None = None


class SchoolSettingRead(BaseModel):
    id: int
    key: str
    value: str
    description: str | None = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

