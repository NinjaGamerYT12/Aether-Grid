from pydantic import BaseModel, Field
from datetime import datetime, timezone
from typing import Optional

class Task(BaseModel):
    """Represents a computational task in the AetherGrid system."""
    id: str = Field(..., description="Unique identifier for the task")
    data: str = Field(..., description="Input data for processing")
    priority: int = Field(default=0, description="Task priority (higher is more urgent)")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class TaskCompletion(BaseModel):
    """Represents the result of a completed task."""
    id: str
    data: str
    result: str
    processed_by: str
    completed_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class SystemStatus(BaseModel):
    """Represents the current health and status of the Leader."""
    queue_size: int
    uptime: float
    db_status: str
