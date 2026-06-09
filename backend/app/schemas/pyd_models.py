from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

class ProjectCreate(BaseModel):
    name: str
    root_url: str

class ProjectResponse(BaseModel):
    id: str
    name: str
    root_url: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class CrawlResponse(BaseModel):
    id: str
    project_id: str
    status: str
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    error_message: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True

class ActionResponse(BaseModel):
    id: str
    project_id: str
    name: str
    description: Optional[str]
    intent: str
    selector: str
    parameters: Optional[str]
    action_type: str
    api_url: Optional[str]
    api_method: Optional[str]
    confidence_score: float

    class Config:
        from_attributes = True

class WorkflowResponse(BaseModel):
    id: str
    project_id: str
    name: str
    description: Optional[str]
    steps: str

    class Config:
        from_attributes = True
