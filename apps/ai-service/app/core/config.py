"""
AI 服务配置
"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # 服务配置
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = True

    # Milvus 配置
    MILVUS_HOST: str = "localhost"
    MILVUS_PORT: int = 19530

    # LLM 配置
    LLM_PROVIDER: str = "openai"
    LLM_API_KEY: Optional[str] = None
    LLM_MODEL: str = "gpt-4"
    LLM_TEMPERATURE: float = 0.7
    LLM_MAX_TOKENS: int = 2048

    # 知识库配置
    KNOWLEDGE_COLLECTION: str = "brainspark_knowledge"
    EMBEDDING_DIMENSION: int = 768
    TOP_K_RESULTS: int = 5

    # 报告配置
    REPORT_OUTPUT_DIR: str = "./reports"
    MAX_REPORT_LENGTH: int = 5000

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()