from datetime import datetime

from pydantic import BaseModel, Field


class DeploymentCreate(BaseModel):
    application_id: int
    version: str = Field(..., min_length=1, max_length=80)
    scenario: str = Field(..., min_length=2, max_length=40)


class DeploymentRead(BaseModel):
    id: int
    application_id: int
    version: str
    scenario: str
    status: str
    started_at: datetime
    completed_at: datetime | None = None
    logs: str
    failure_reason: str | None = None
    incident_id: int | None = None

    class Config:
        from_attributes = True
