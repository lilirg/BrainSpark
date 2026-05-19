from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.schemas.assessment import AssessmentRequest, AssessmentResponse
from app.schemas.report import ReportRequest, ReportResponse
from app.analysis.analyzer import CognitiveAnalyzer
from app.rag.vector_store import MilvusVectorStore
import uuid

app = FastAPI(title=settings.APP_NAME, version=settings.VERSION)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

cognitive_analyzer = CognitiveAnalyzer()
vector_store = MilvusVectorStore()


@app.get("/health")
async def health_check():
    return {"status": "ok", "service": "ai-service", "version": settings.VERSION}


@app.post("/api/v1/assessments/analyze", response_model=AssessmentResponse)
async def analyze_assessment(request: AssessmentRequest):
    """分析测评数据，生成认知维度评分"""
    try:
        result = cognitive_analyzer.analyze(request.events)
        return AssessmentResponse(
            student_id=request.student_id,
            dimensions=result,
            suggestions=cognitive_analyzer.generate_suggestions(result)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/reports/generate", response_model=ReportResponse)
async def generate_report(request: ReportRequest):
    """基于 RAG 生成 AI 报告"""
    try:
        # 检索相关教育知识
        context = await vector_store.similarity_search(request.context, k=3)
        
        # 调用 LLM 生成报告
        report = await cognitive_analyzer.generate_report(
            assessment_data=request.assessment,
            knowledge_context=context
        )
        
        return ReportResponse(
            student_id=request.student_id,
            report=report
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/knowledge/index")
async def index_knowledge(docs: list[dict]):
    """索引教育知识到 Milvus"""
    try:
        ids = await vector_store.add_documents(docs)
        return {"indexed": len(ids), "ids": ids}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8001, reload=settings.DEBUG)