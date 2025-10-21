from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class ProjectBase(BaseModel):
    name: str = Field(..., example="Motion Capture Demo")
    description: Optional[str] = Field(None, example="3D motion reconstruction project")
    is_active: bool = True


class ProjectCreate(ProjectBase):
    pass


class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None


class ProjectRead(ProjectBase):
    id: int
    owner_id: int
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        orm_mode = True
