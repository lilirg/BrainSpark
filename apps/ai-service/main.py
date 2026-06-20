"""
BrainSpark AI 服务入口
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import router as api_router
from app.core.config import settings

app = FastAPI(
    title="BrainSpark AI Service",
    description="认知测评分析与 AI 报告生成服务",
    version="1.0.0",
)

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(api_router)


@app.get("/health")
async def health_check():
    """健康检查"""
    return {
        "status": "ok",
        "service": "brainspark-ai",
        "version": "1.0.0",
    }


@app.get("/")
async def root():
    """根路径"""
    return {
        "service": "BrainSpark AI Service",
        "version": "1.0.0",
        "docs": "/docs",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
    )