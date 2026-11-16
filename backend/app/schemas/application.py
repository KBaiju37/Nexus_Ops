from datetime import datetime

from pydantic import BaseModel, Field


class ApplicationBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=200)
    description: str = Field(default="", max_length=1000)
    repository_url: str | None = Field(default=None, max_length=500)
    environment: str = Field(default="dev", max_length=50)


class ApplicationCreate(ApplicationBase):
    pass


class ApplicationRead(ApplicationBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
