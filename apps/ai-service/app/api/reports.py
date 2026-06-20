"""
报告生成 API
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Dict, Optional, List
from datetime import datetime
import json
import os

router = APIRouter(prefix="/reports", tags=["reports"])


class GenerateReportRequest(BaseModel):
    student_id: str = Field(..., description="学生ID")
    student_name: str = Field(..., description="学生姓名")
    student_age: int = Field(..., ge=6, le=18, description="学生年龄")
    assessment_results: List[Dict] = Field(..., description="测评结果列表")
    report_type: str = Field("ASSESSMENT", description="报告类型")


class ReportResponse(BaseModel):
    report_id: str
    title: str
    content: Dict
    generated_at: str
    pdf_url: Optional[str] = None


@router.post("/generate", response_model=ReportResponse)
async def generate_report(request: GenerateReportRequest):
    """生成测评报告"""
    try:
        # 计算综合得分
        overall_scores = []
        dimensions_summary = {}

        for result in request.assessment_results:
            if "overall_score" in result:
                overall_scores.append(result["overall_score"])
            for dim in result.get("dimensions", []):
                code = dim.get("code")
                if code:
                    if code not in dimensions_summary:
                        dimensions_summary[code] = []
                    dimensions_summary[code].append(dim)

        avg_score = (
            sum(overall_scores) / len(overall_scores)
            if overall_scores
            else 0
        )

        # 生成报告内容
        report_content = {
            "student_info": {
                "name": request.student_name,
                "age": request.student_age,
                "id": request.student_id,
            },
            "summary": {
                "total_assessments": len(request.assessment_results),
                "average_score": round(avg_score, 1),
                "assessment_date": datetime.utcnow().isoformat(),
            },
            "dimensions": [],
            "recommendations": [],
            "trends": [],
        }

        # 汇总各维度
        for code, dims in dimensions_summary.items():
            scores = [d.get("score", 0) for d in dims]
            levels = [d.get("level", "AVERAGE") for d in dims]
            latest = dims[-1] if dims else {}

            report_content["dimensions"].append({
                "code": code,
                "name": latest.get("name", code),
                "current_score": scores[-1] if scores else 0,
                "average_score": round(sum(scores) / len(scores), 1) if scores else 0,
                "current_level": levels[-1] if levels else "AVERAGE",
                "description": latest.get("description", ""),
                "suggestion": latest.get("suggestion", ""),
            })

        # 生成建议
        for dim in report_content["dimensions"]:
            if dim["current_level"] in ("LOW", "VERY_LOW"):
                report_content["recommendations"].append({
                    "dimension": dim["name"],
                    "priority": "high" if dim["current_level"] == "VERY_LOW" else "medium",
                    "suggestion": dim["suggestion"],
                })

        report = ReportResponse(
            report_id=f"rpt_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
            title=f"{request.student_name}的认知测评报告",
            content=report_content,
            generated_at=datetime.utcnow().isoformat(),
        )

        return report

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"报告生成失败: {str(e)}")