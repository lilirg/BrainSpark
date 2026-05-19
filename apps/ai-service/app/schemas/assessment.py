from pydantic import BaseModel
from typing import List, Dict, Any
from datetime import datetime


class AssessmentEvent(BaseModel):
    event_type: str
    dimension: str  # memory, attention, logic, creativity, observation, imagination
    score: float
    timestamp: datetime


class AssessmentRequest(BaseModel):
    student_id: str
    events: List[AssessmentEvent]


class DimensionScore(BaseModel):
    dimension: str
    score: float
    level: str  # 优秀/良好/中等/待提升


class AssessmentResponse(BaseModel):
    student_id: str
    dimensions: List[DimensionScore]
    overall_score: float
    suggestions: List[str]
    generated_at: datetime = datetime.now()