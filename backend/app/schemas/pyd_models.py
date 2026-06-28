from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


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
    description: Optional[str] = None
    intent: str
    selector: str
    parameters: Optional[str] = None
    action_type: str
    api_url: Optional[str] = None
    api_method: Optional[str] = None
    confidence_score: float
    assertions: Optional[str] = None

    class Config:
        from_attributes = True

class WorkflowResponse(BaseModel):
    id: str
    project_id: str
    name: str
    description: Optional[str] = None
    steps: str

    class Config:
        from_attributes = True

class WorkflowStepUpdate(BaseModel):
    action: str
    source_page: str
    target_page: str

class WorkflowUpdate(BaseModel):
    name: str
    description: Optional[str] = None
    steps: List[WorkflowStepUpdate]

class ActionUpdate(BaseModel):
    description: Optional[str] = None
    selector: Optional[str] = None
    parameters: Optional[str] = None
    assertions: Optional[str] = None

class PlaygroundExecuteRequest(BaseModel):
    project_id: str
    action_id: str
    parameters: dict = {}
