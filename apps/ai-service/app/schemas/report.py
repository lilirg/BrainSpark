from pydantic import BaseModel
from typing import List, Dict, Any
from datetime import datetime


class ReportRequest(BaseModel):
    student_id: str
    assessment: Dict[str, Any]
    context: str = ""


class ReportResponse(BaseModel):
    student_id: str
    report: str
    generated_at: datetime = datetime.now()
    version: str = "1.0"


class TrainingPlan(BaseModel):
    plan_id: str
    student_id: str
    objectives: List[str]
    schedule: List[Dict[str, Any]]
    duration_weeks: int