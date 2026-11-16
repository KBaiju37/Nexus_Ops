from datetime import datetime

from pydantic import BaseModel, Field


class IncidentPatch(BaseModel):
    status: str | None = Field(default=None, max_length=30)
    severity: str | None = Field(default=None, max_length=20)
    diagnosis: str | None = Field(default=None)
    recommended_resolution: str | None = Field(default=None)


class IncidentRead(BaseModel):
    id: int
    deployment_id: int
    severity: str
    error_logs: str
    root_cause_category: str
    diagnosis: str
    recommended_resolution: str
    status: str
    created_at: datetime
    ml_category: str | None = None
    ml_confidence: float | None = None

    class Config:
        from_attributes = True
