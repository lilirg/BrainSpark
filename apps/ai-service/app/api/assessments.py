"""
测评分析 API
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Dict, Optional, List
from app.analysis.analyzer import CognitiveAnalyzer

router = APIRouter(prefix="/assessments", tags=["assessments"])
analyzer = CognitiveAnalyzer()


class AnalyzeRequest(BaseModel):
    assessment_type: str = Field(..., description="测评类型")
    raw_scores: Dict[str, float] = Field(..., description="原始分数")
    student_age: int = Field(..., ge=6, le=18, description="学生年龄")
    student_id: Optional[str] = None
    metadata: Optional[Dict] = None


class AnalyzeResponse(BaseModel):
    assessment_type: str
    student_age: int
    age_group: str
    overall_score: float
    dimensions: List[Dict]
    analyzed_at: str


@router.post("/analyze", response_model=AnalyzeResponse)
async def analyze_assessment(request: AnalyzeRequest):
    """分析测评结果"""
    try:
        result = analyzer.analyze_assessment(
            assessment_type=request.assessment_type,
            raw_scores=request.raw_scores,
            student_age=request.student_age,
            metadata={
                **(request.metadata or {}),
                "student_id": request.student_id,
            },
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"分析失败: {str(e)}")


class CompareRequest(BaseModel):
    analysis_result: Dict


@router.post("/compare")
async def compare_with_norm(request: CompareRequest):
    """与常模对比"""
    try:
        result = analyzer.compare_with_norm(request.analysis_result)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"对比失败: {str(e)}")